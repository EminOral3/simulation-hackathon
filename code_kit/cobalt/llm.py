"""LLM access for personas: Gemini on Vertex AI (API key) or a mock, with a content-addressed disk cache
keyed by (model, seed, prompt) and a log of every call in the challenge's calls.jsonl shape.

The cache makes re-runs incremental: after a late announcement only the weeks whose prompts changed are
sent again. The key is read from TALP_KEY, else VERTEX_AI_KEY (also from the repo .env); never written out.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import params as P


def load_env():
    env = P.ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def api_key() -> str:
    load_env()
    key = os.environ.get("TALP_KEY") or os.environ.get("VERTEX_AI_KEY")
    if not key:
        raise RuntimeError("set TALP_KEY (or VERTEX_AI_KEY in .env)")
    return key


@dataclass
class Call:
    id: str
    persona: str | None
    week: int
    prompt: str
    response: str
    model: str
    kind: str
    cached: bool = False
    seconds: float = 0.0
    parsed: dict | None = None

    def record(self) -> dict:
        return {"id": self.id, "persona": self.persona, "week": self.week, "prompt": self.prompt,
                "response": self.response, "model": self.model, "kind": self.kind, "cached": self.cached}


@dataclass
class Stats:
    calls: int = 0
    cached: int = 0
    failed: int = 0
    seconds: float = 0.0


class LLM:
    """One per process; shared by concurrent runs (one semaphore = one concurrency budget)."""

    def __init__(self, p: dict, live: bool | None = None, model: str | None = None):
        self.p = p
        self.live = p["llm"]["provider"] == "gemini" if live is None else live
        self.model = model or P.model_id(p)
        self.sem = asyncio.Semaphore(p["llm"]["concurrency"])
        self.cache_dir = P.path(p, "outputs") / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._client = None
        self.stats = Stats()

    @property
    def model_label(self) -> str:
        return self.model if self.live else f"mock({self.model})"

    def client(self):
        if self._client is None:
            from google import genai
            from google.genai import types
            self._client = genai.Client(
                vertexai=True, api_key=api_key(),
                http_options=types.HttpOptions(retry_options=types.HttpRetryOptions(attempts=self.p["llm"]["retries"]),
                                               timeout=int(self.p["llm"]["timeout_s"] * 1000)))
        return self._client

    def _key(self, model: str, seed: int, prompt: str) -> Path:
        h = hashlib.sha256(f"{model}\x00{seed}\x00{prompt}".encode()).hexdigest()
        return self.cache_dir / h[:2] / f"{h}.json"

    async def _gemini(self, model: str, prompt: str, seed: int, schema) -> str:
        from google.genai import types
        cfg = dict(temperature=self.p["llm"]["temperature"], seed=seed,
                   max_output_tokens=self.p["llm"]["max_output_tokens"])
        if schema is not None:
            cfg.update(response_mime_type="application/json", response_schema=schema)
        if model in self.p["llm"]["no_thinking_models"]:
            cfg["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
        else:
            cfg["thinking_config"] = types.ThinkingConfig(thinking_level=self.p["llm"]["thinking_level"])
        r = await self.client().aio.models.generate_content(model=model, contents=prompt,
                                                            config=types.GenerateContentConfig(**cfg))
        return r.text or ""

    async def ask(self, *, call_id: str, persona: str | None, week: int, kind: str, prompt: str, seed: int,
                  schema=None, mock: Callable[[str, random.Random], dict] | None = None,
                  model: str | None = None) -> Call:
        """Returns a Call with .parsed (dict) when schema is given. Re-asks on unparsable JSON."""
        model = model or self.model
        label = model if self.live else f"mock({model})"
        text, parsed, cached, t0 = "", None, False, time.perf_counter()
        attempts = self.p["llm"]["parse_retries"] + 1
        sent = prompt
        for attempt in range(attempts):
            sent = prompt if attempt == 0 else prompt + "\n\nReturn only valid JSON that matches the schema."
            ck = self._key(label, seed, sent)
            if self.p["llm"]["cache"] and ck.exists():
                text, cached = json.loads(ck.read_text())["response"], True
            else:
                async with self.sem:
                    if self.live:
                        try:
                            text = await self._gemini(model, sent, seed, schema)
                        except Exception as e:  # network / quota: re-ask, then give up on this call
                            text = ""
                            last_err = repr(e)[:300]
                            await asyncio.sleep(1.0 + attempt)
                    else:
                        rng = random.Random(f"{seed}|{sent}")
                        text = json.dumps(mock(sent, rng) if mock else {"text": "ok"})
                if text and self.p["llm"]["cache"]:
                    ck.parent.mkdir(parents=True, exist_ok=True)
                    ck.write_text(json.dumps({"model": label, "seed": seed, "response": text}))
            if schema is None:
                break
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    break
                parsed = None
            except (json.JSONDecodeError, TypeError):
                parsed = None
        dt = time.perf_counter() - t0
        self.stats.calls += 1
        self.stats.cached += cached
        self.stats.seconds += dt
        if schema is not None and parsed is None:
            self.stats.failed += 1
        return Call(id=call_id if attempt == 0 else f"{call_id}-r{attempt}", persona=persona, week=week,
                    prompt=sent, response=text, model=label, kind=kind, cached=cached, seconds=dt, parsed=parsed)
