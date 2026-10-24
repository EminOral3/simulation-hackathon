"""Live board question to one persona, using everything that happened to it in a saved run.

    python -m code_kit.cobalt.ask_persona --run <run_dir or folder name> --persona P17 "Why did you stay?" [--live] [--model final]
    python -m code_kit.cobalt.ask_persona --run <run_dir> --list              # who is in the run, how they ended
    python -m code_kit.cobalt.ask_persona --run <run_dir> --persona Chloe      # timeline only (no question)
"""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from . import agent
from . import params as P
from .llm import LLM


def load_run(p: dict, run: str) -> Path:
    d = Path(run)
    if not d.exists():
        d = P.path(p, "outputs") / "runs" / run
    if not d.exists():
        cands = sorted((P.path(p, "outputs") / "runs").glob(f"*{run}*"))
        if not cands:
            raise SystemExit(f"run not found: {run}")
        d = cands[-1]
    return d


def jl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()] if path.exists() else []


def find(people: list[dict], key: str) -> dict:
    for f in people:
        if f["id"].lower() == key.lower() or f["name"].lower().startswith(key.lower()):
            return f
    raise SystemExit(f"persona not found: {key}")


def timeline(d: Path, f: dict, names: dict) -> tuple[str, dict]:
    weekly = [r for r in jl(d / "weekly.jsonl") if r["persona"] == f["id"]]
    calls = {c["id"]: c for c in jl(d / "calls.jsonl") if c.get("persona") == f["id"]}
    inter = [x for x in jl(d / "interactions.jsonl") if f["id"] in (x.get("from"), x.get("to"))]
    state = {"notes": [], "relations": {}}
    lines = []
    for r in sorted(weekly, key=lambda r: r["week"]):
        try:
            note = json.loads(calls[r["call"]]["response"]).get("memory_note", "")
        except Exception:
            note = ""
        state["notes"].append((r["week"], note, r["status"], r["money"]))
        lines.append(f"week {r['week']:2d}: {r['status']:11s} money {r['money']:10s} trust {r.get('trust')}  {note}")
    for x in inter[-8:]:
        other = x.get("to") if x.get("from") == f["id"] else x.get("from")
        if other and x["type"] in ("dm", "reply"):
            state["relations"][names.get(other, other)] = x["text"][:160]
    msgs = [f"  w{x['week']} {x['type']:8s} {names.get(x.get('from'), '')} -> {names.get(x.get('to'), x.get('channel', ''))}: {x['text'][:140]}"
            for x in inter]
    return "\n".join(lines) + ("\n\nconversations:\n" + "\n".join(msgs[-12:]) if msgs else ""), state


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?")
    ap.add_argument("--run", required=True)
    ap.add_argument("--persona")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--model", default=None)
    ap.add_argument("--params", action="append", default=[])
    ap.add_argument("--set", action="append", default=[])
    a = ap.parse_args()
    p = P.load(a.params, a.set)
    d = load_run(p, a.run)
    people = jl(d / "personas.jsonl")
    names = {f["id"]: f["name"] for f in people}
    if a.list or not a.persona:
        last = {r["persona"]: r for r in jl(d / "weekly.jsonl") if r["week"] == 10}
        for f in people:
            r = last.get(f["id"], {})
            print(f"{f['id']} {f['name']:12s} {f['group'][:28]:28s} start {f['cobalt_role']:11s} -> {r.get('status', '?'):11s} money {r.get('money', '?')}")
        return
    f = find(people, a.persona)
    tl, state = timeline(d, f, names)
    print(f"== {f['id']} {f['name']} ({f['group']})\n{f.get('narrative', '')}\n\n{tl}\n")
    if not a.question:
        return
    run = json.loads((d / "run.json").read_text())
    model = a.model or (run["model"] if not run["model"].startswith("mock") else None)
    llm = LLM(p, live=a.live, model=P.model_id(p, model) if model in ("experiment", "final") else model)
    ties = f.get("ties", [])
    prompt = agent.ask_prompt(agent.persona_block(f, ties, names), agent.history_block(state), a.question)
    c = asyncio.run(llm.ask(call_id=f"ask-{f['id']}", persona=f["id"], week=11, kind="ask", prompt=prompt,
                            seed=run.get("seed", 1), schema=agent.Answer, mock=agent.mock_answer))
    print(f"Q: {a.question}\n{f['name']}: {(c.parsed or {}).get('answer', c.response)}")


if __name__ == "__main__":
    main()
