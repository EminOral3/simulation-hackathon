"""Run an experiment grid (variants x seeds) concurrently under one concurrency budget. Every run still goes to its
own timestamped folder; the experiment folder holds summary.csv (+ per-variant means) and points to those runs.

Spec (TOML), e.g. code_kit/cobalt/params/experiments/e11_network.toml:
    name = "e11_network"
    seeds = [1, 2]
    [[variant]]
    label = "full"            # type defaults to "plan", decisions to "plan"
    [[variant]]
    label = "no-ties"
    set = ["network.enabled_ties=false"]

    python -m code_kit.cobalt.experiments code_kit/cobalt/params/experiments/e11_network.toml [--live] [--model final]
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import tomllib
from datetime import datetime
from pathlib import Path

import numpy as np

from . import params as P
from .llm import LLM
from .run import run_one

GOALS = ["goal_1", "goal_2", "goal_3", "goal_3b"]


async def run_grid(spec: dict, base_params: list[str], base_sets: list[str], live: bool, quiet: bool) -> Path:
    shared_sem = None
    jobs = []
    for v in spec["variant"]:
        sets = base_sets + v.get("set", [])
        p = P.load(base_params + v.get("params", []), sets)
        for seed in v.get("seeds", spec.get("seeds", [1])):
            llm = LLM(p, live=live)
            if shared_sem is None:
                shared_sem = llm.sem
            llm.sem = shared_sem
            jobs.append((v, seed, p, llm))
    p0 = jobs[0][2]
    exp_dir = P.path(p0, "outputs") / "experiments" / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_{spec['name']}"
    exp_dir.mkdir(parents=True, exist_ok=False)
    (exp_dir / "spec.json").write_text(json.dumps({"spec": spec, "params": base_params, "set": base_sets, "live": live}, indent=1))

    async def one(v, seed, p, llm):
        label = f"{spec['name']}-{v['label']}"
        try:
            out = await run_one(p, llm, run_type=v.get("type", "plan"), seed=seed,
                                decisions_file=v.get("decisions", "plan"), label=label,
                                probe=v.get("probe", False), persona_set=v.get("persona_set"), quiet=quiet,
                                n_personas=v.get("personas"), weeks=v.get("weeks", 10))
            m = json.loads((out / "metrics.json").read_text())
            return {"variant": v["label"], "type": v.get("type", "plan"), "seed": seed, "folder": out.name,
                    **{k: m.get(k) for k in GOALS}, **{f"{k}_ci95": m.get(f"{k}_ci95") for k in GOALS},
                    "overrun": m.get("overrun"), "warnings": len(m.get("sanity_warnings", []))}
        except Exception as e:
            return {"variant": v["label"], "seed": seed, "error": repr(e)[:300]}

    rows = await asyncio.gather(*(one(*j) for j in jobs))
    fields = ["variant", "type", "seed", *GOALS, *[f"{k}_ci95" for k in GOALS], "overrun", "warnings", "folder", "error"]
    with (exp_dir / "summary.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    means = []
    for v in spec["variant"]:
        rs = [r for r in rows if r["variant"] == v["label"] and "error" not in r]
        if rs:
            means.append({"variant": v["label"], "n_seeds": len(rs),
                          **{k: round(float(np.mean([r[k] for r in rs])), 3) for k in GOALS},
                          **{f"{k}_range": [round(min(r[k] for r in rs), 3), round(max(r[k] for r in rs), 3)] for k in GOALS}})
    (exp_dir / "means.json").write_text(json.dumps(means, indent=1))
    print(f"\n{exp_dir}")
    print(f"{'variant':22s} {'n':>2s} {'goal_1':>8s} {'goal_2':>8s} {'goal_3':>7s} {'goal_3b':>8s}")
    for m in means:
        print(f"{m['variant']:22s} {m['n_seeds']:>2d} {m['goal_1']:8.2f} {m['goal_2']:8.2f} {m['goal_3']:7.2f} {m['goal_3b']:8.0f}")
    for r in rows:
        if "error" in r:
            print("ERROR", r)
    return exp_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--model")
    ap.add_argument("--seeds", help="override, e.g. 1,2,3")
    ap.add_argument("--params", action="append", default=[])
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--confirm-top", type=int, default=0,
                    help="screen every variant with the first seed only, then run the other seeds for the K best "
                         "(ranked by goal_1 + goal_2); cuts grid cost roughly in half")
    a = ap.parse_args()
    path = Path(a.spec)
    if not path.exists():
        path = P.PKG / "params" / "experiments" / (a.spec if a.spec.endswith(".toml") else f"{a.spec}.toml")
    spec = tomllib.loads(path.read_text())
    if a.seeds:
        spec["seeds"] = [int(x) for x in a.seeds.split(",")]
        for v in spec["variant"]:
            v.pop("seeds", None)
    sets = list(a.set) + ([f'llm.model="{a.model}"'] if a.model else [])
    if not a.confirm_top:
        asyncio.run(run_grid(spec, a.params, sets, a.live, quiet=not a.verbose))
        return
    seeds_of = {v["label"]: v.get("seeds", spec.get("seeds", [1])) for v in spec["variant"]}
    first = dict(spec, name=f"{spec['name']}_screen", variant=[dict(v, seeds=seeds_of[v["label"]][:1]) for v in spec["variant"]])
    d1 = asyncio.run(run_grid(first, a.params, sets, a.live, quiet=not a.verbose))
    means = {m["variant"]: m["goal_1"] + m["goal_2"] for m in json.loads((d1 / "means.json").read_text())}
    keep = sorted(means, key=lambda k: -means[k])[: a.confirm_top]
    rest = [dict(v, seeds=seeds_of[v["label"]][1:]) for v in spec["variant"]
            if v["label"] in keep and len(seeds_of[v["label"]]) > 1]
    if not rest:
        rest = [dict(v, seeds=[seeds_of[v["label"]][0] + 1]) for v in spec["variant"] if v["label"] in keep]
    print(f"\nconfirming top {len(rest)}: {[v['label'] for v in rest]}")
    asyncio.run(run_grid(dict(spec, name=f"{spec['name']}_confirm", variant=rest), a.params, sets, a.live,
                         quiet=not a.verbose))


if __name__ == "__main__":
    main()
