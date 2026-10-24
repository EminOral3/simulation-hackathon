"""Run one simulation into a new timestamped folder (never overwrites) and append it to outputs/index.csv.

    python -m code_kit.cobalt.run --type plan --seed 1 --decisions plan [--live] [--model final]
        [--params x.toml] [--set network.enabled_feed=false] [--label e11] [--personas 12] [--weeks 3] [--no-probe]
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

from . import config, crisis, personas
from . import params as P
from .engine import Sim, write_outputs
from .llm import LLM

TYPES = ("plan", "nodecision", "plan_nosurprises")
INDEX_FIELDS = ["timestamp", "folder", "type", "seed", "model", "label", "persona_set", "n_personas", "weeks",
                "params_hash", "decisions_hash", "announcements_hash", "goal_1", "goal_2", "goal_3", "goal_3b",
                "calls", "cached", "failed", "seconds", "status"]


def git_info() -> dict:
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=P.ROOT, capture_output=True, text=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=P.ROOT, capture_output=True, text=True).stdout.strip())
        return {"commit": commit, "dirty": dirty}
    except Exception:
        return {}


def new_run_dir(p: dict, run_type: str, seed: int, model: str, label: str) -> Path:
    base = P.path(p, "outputs") / "runs"
    base.mkdir(parents=True, exist_ok=True)
    short = model.replace("gemini-", "g").replace("-flash-lite", "lite").replace("-flash", "f").replace("mock(", "mock-").rstrip(")")
    stem = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_{run_type}_s{seed}_{short}" + (f"_{label}" if label else "")
    for k in range(1, 100):
        d = base / (stem if k == 1 else f"{stem}-{k}")
        try:
            d.mkdir(exist_ok=False)
            return d
        except FileExistsError:
            continue
    raise RuntimeError("could not create a unique run folder")


def append_index(p: dict, row: dict):
    f = P.path(p, "outputs") / "index.csv"
    new = not f.exists()
    with f.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=INDEX_FIELDS, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerow(row)


async def run_one(p: dict, llm: LLM, *, run_type: str, seed: int, decisions_file: str | None, label: str = "",
                  n_personas: int | None = None, weeks: int = 10, probe: bool = True, persona_set: str | None = None,
                  quiet: bool = False) -> Path:
    if run_type not in TYPES:
        raise ValueError(f"type must be one of {TYPES}")
    decisions, filters = ([], {}) if run_type == "nodecision" else config.load_decisions(p, decisions_file)
    cost = config.budget_check(p, decisions)
    surprises = p["world"]["surprises"] and run_type != "plan_nosurprises"
    anns = crisis.load_announcements(p, surprises)
    set_dir, people, gen = personas.load_set(p, persona_set)
    if n_personas:
        by_group: dict[str, list] = {}
        for f in people:
            by_group.setdefault(f["group"], []).append(f)
        k = max(4, n_personas // len(by_group))
        people = [f for g in by_group.values() for f in g[:k]]
        keep = {f["id"] for f in people}
        people = [{**f, "ties": [t for t in f.get("ties", []) if t["id"] in keep]} for f in people]
        gen = [c for c in gen if c.get("persona") in keep]
    out = new_run_dir(p, run_type, seed, llm.model_label, label)
    log_lines = []

    def log(msg):
        log_lines.append(msg)
        if not quiet:
            print(f"[{out.name}] {msg}", flush=True)

    t0 = time.time()
    stats0 = (llm.stats.calls, llm.stats.cached, llm.stats.failed)
    tok0 = dict(llm.stats.tokens)
    status = "ok"
    sim = Sim(p, llm, people, run_type=run_type, seed=seed, decisions=decisions, filters=filters, announcements=anns,
              probe=probe, weeks=weeks, log=log)
    log(f"start: {len(people)} personas, model {llm.model_label}, overrun '{sim.ctx.overrun}', "
        f"{len(anns)} announcements, cost ${cost['total_usd']:,}")
    meta = {"started": datetime.now().isoformat(timespec="seconds"), "persona_set": set_dir.name, "git": git_info(),
            "cost": cost, "surprises": surprises, "label": label, "weeks": weeks}
    (out / "params.resolved.json").write_text(json.dumps(p, indent=1, ensure_ascii=False))
    (out / "decisions.json").write_text(json.dumps({"decisions": decisions, "filters": filters}, indent=1, ensure_ascii=False))
    (out / "announcements.snapshot.json").write_text(json.dumps(anns, indent=1, ensure_ascii=False))
    m = {}
    try:
        await sim.run()
    except Exception as e:
        status = "failed"
        log(f"FAILED: {e!r}")
        raise
    finally:
        run_json = {"company": p["run"]["company"], "type": run_type, "seed": seed, "model": llm.model_label,
                    "decisions": decisions}
        if sim.weekly or status == "ok":
            m = write_outputs(sim, out, run_json, gen, {"queue": sim.queue})
            if weeks < 10 or n_personas:
                status = "partial" if status == "ok" else status
        calls = llm.stats.calls - stats0[0]
        cached = llm.stats.cached - stats0[1]
        failed = llm.stats.failed - stats0[2]
        meta.update({"finished": datetime.now().isoformat(timespec="seconds"), "seconds": round(time.time() - t0, 1),
                     "calls": calls, "cached": cached, "failed_parses": failed, "status": status,
                     "tokens": {k: v - tok0.get(k, 0) for k, v in llm.stats.tokens.items()},  # shared LLM: approximate under concurrency
                     "hashes": {"params": P.digest(p), "decisions": P.digest(decisions), "announcements": P.digest(anns)}})
        (out / "meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
        (out / "log.txt").write_text("\n".join(log_lines) + "\n")
        append_index(p, {"timestamp": meta["started"], "folder": out.name, "type": run_type, "seed": seed,
                         "model": llm.model_label, "label": label, "persona_set": set_dir.name, "n_personas": len(people),
                         "weeks": weeks, "params_hash": meta["hashes"]["params"], "decisions_hash": meta["hashes"]["decisions"],
                         "announcements_hash": meta["hashes"]["announcements"],
                         **{k: round(m[k], 3) for k in ("goal_1", "goal_2", "goal_3", "goal_3b") if k in m},
                         "calls": calls, "cached": cached, "failed": failed, "seconds": meta["seconds"], "status": status})
    if m.get("goal_1") is not None:
        log(f"done in {meta['seconds']}s: goal_1 {m['goal_1']:.2f} {m['goal_1_ci95']}, goal_2 {m['goal_2']:.2f}, "
            f"goal_3 {m['goal_3']:.2f}, goal_3b {m['goal_3b']:.0f}; calls {calls} (cached {cached}, failed {failed})")
        for wmsg in m.get("sanity_warnings", []):
            log(f"SANITY: {wmsg}")
    return out


def add_common(ap: argparse.ArgumentParser):
    ap.add_argument("--live", action="store_true", help="use Gemini (default: mock)")
    ap.add_argument("--model", help="experiment | final | explicit model id")
    ap.add_argument("--params", action="append", default=[])
    ap.add_argument("--set", action="append", default=[])


def setup(a) -> tuple[dict, LLM]:
    sets = list(a.set)
    if a.model:
        sets.append(f'llm.model="{a.model}"')
    p = P.load(a.params, sets)
    return p, LLM(p, live=a.live)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", required=True, choices=TYPES)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--decisions", default="plan")
    ap.add_argument("--label", default="")
    ap.add_argument("--personas", type=int)
    ap.add_argument("--weeks", type=int, default=10)
    ap.add_argument("--no-probe", action="store_true")
    ap.add_argument("--persona-set")
    add_common(ap)
    a = ap.parse_args()
    p, llm = setup(a)
    out = asyncio.run(run_one(p, llm, run_type=a.type, seed=a.seed, decisions_file=a.decisions, label=a.label,
                              n_personas=a.personas, weeks=a.weeks, probe=not a.no_probe, persona_set=a.persona_set))
    print(out)


if __name__ == "__main__":
    main()
