"""Run-level fidelity of the surrogate: k-fold over LLM runs. Each held-out run (its decisions, its announcements,
its migration overrun) is replayed with the fast simulator trained without it; predicted vs LLM goals.

    python -m code_kit.cobalt.surrogate_check [--min-time 20261024-1320] [--k 4] [--reps 8]
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime

import numpy as np

from . import config
from . import params as P
from .fastsim import FastWorld
from .surrogate import dataset, fit, run_dirs

GOALS = ["goal_1", "goal_2", "goal_3", "goal_3b"]


def replay_inputs(p, d, people):
    dec = json.loads((d / "decisions.json").read_text())
    plan = []
    for i, x in enumerate(dec["decisions"], 1):
        x = dict(x)
        x["_mask"] = np.array([config.in_target(f, dec.get("filters", {}).get(str(i))) for f in people])
        plan.append(x)
    sx = []
    for a in json.loads((d / "announcements.snapshot.json").read_text()):
        if a.get("surprise", True):
            sx.append({"week": a["week"], "archetype": (a.get("archetypes") or ["A10_regulatory_or_media_probe"])[0],
                       "severity": a.get("severity", "base")})
    m = json.loads((d / "metrics.json").read_text())
    ov = p["world"]["overrun_levels"].index(m.get("overrun", "on time"))
    return plan, sx, ov, m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-time", default="20261024-1320")
    ap.add_argument("--models", default="")
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--reps", type=int, default=8)
    ap.add_argument("--C", type=float, default=0.5)
    a = ap.parse_args()
    p = P.load()
    dirs = run_dirs(p, a.min_time, a.models)
    ds = dataset(dirs)
    rows = []
    for fold in range(a.k):
        test = set(range(fold, len(dirs), a.k))
        tr = ~np.isin(ds["groups"], list(test))
        m = fit({"X": ds["X"][tr], "Y": {h: v[tr] for h, v in ds["Y"].items()}, "dirs": []}, a.C)
        for gi in sorted(test):
            d = dirs[gi]
            people = [json.loads(l) for l in (d / "personas.jsonl").read_text().splitlines() if l.strip()]
            fw = FastWorld(p, people, m)
            plan, sx, ov, llm = replay_inputs(p, d, people)
            preds = [fw.simulate([plan], sx, ov, rep) for rep in range(a.reps)]
            row = {"run": d.name}
            for g in GOALS:
                v = np.array([x[g][0] for x in preds])
                row[f"{g}_llm"], row[f"{g}_sur"], row[f"{g}_sur_sd"] = llm[g], float(v.mean()), float(v.std())
            rows.append(row)
            print(f"{d.name[-28:]:28s} active LLM {row['goal_1_llm']:6.1f} sur {row['goal_1_sur']:6.1f} | "
                  f"deposits LLM {row['goal_2_llm']:6.1f} sur {row['goal_2_sur']:6.1f}", flush=True)
    out = {"rows": rows}
    for g in GOALS:
        x = np.array([r[f"{g}_llm"] for r in rows])
        y = np.array([r[f"{g}_sur"] for r in rows])
        ok = x.std() > 0 and y.std() > 0
        out[g] = {"mae": float(np.abs(x - y).mean()), "bias": float((y - x).mean()),
                  "corr": float(np.corrcoef(x, y)[0, 1]) if ok else None,
                  "rank_corr": float(np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0, 1]) if ok else None}
        print(f"{g}: MAE {out[g]['mae']:.2f}  bias {out[g]['bias']:+.2f}  r {out[g]['corr']}  rank r {out[g]['rank_corr']}")
    dst = P.path(p, "outputs") / "surrogate" / f"check_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    dst.write_text(json.dumps(out, indent=1))
    print(dst)


if __name__ == "__main__":
    main()
