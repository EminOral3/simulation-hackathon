"""Training design for the surrogate: random decision plans x random surprise scenarios (bad and good),
run with the real LLM personas. Writes decision/announcement files and an experiment spec.

    python -m code_kit.cobalt.trainset --n 32 --seed 5    -> params/experiments/train_<seed>.toml
"""
from __future__ import annotations

import argparse
import json
import random

from . import crisis, messages
from . import params as P

MIGRATION_ITEM = {"week": 6, "surprise": False, "source": "dossier", "text": "Cobalt moves to a new core banking system Saturday, December 12, 00:00 to Sunday, December 13, 12:00 (Central Time).", "archetypes": ["A01_migration_overrun"], "severity": "base", "update_of": None}


def random_plan(p, rng, budget=4_000_000):
    plan = []
    left = budget
    for _ in range(2):
        week = rng.randint(1, 10)
        cs = messages.combos(p, week, left)
        if not cs:
            break
        c = rng.choice(cs)
        left -= messages.cost(c)
        plan.append(messages.decision(c, week, rng.choice(list(messages.TARGETS))))
    return plan


def random_surprises(rng, observed=()):
    lib = crisis.library()["archetypes"]
    items = [dict(MIGRATION_ITEM)] + [dict(x) for x in observed]
    for _ in range(rng.choice([0, 1, 1, 2, 2, 3])):
        a = rng.choice(lib)
        week = rng.choice(a["weeks"] if rng.random() < 0.7 else list(range(2, 11)))
        items.append({"week": week, "surprise": True, "source": "synthetic", "text": rng.choice(a["texts"]),
                      "archetypes": [a["id"]], "severity": rng.choice(["low", "base", "base", "high"]), "update_of": None})
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--seed", type=int, default=5)
    a = ap.parse_args()
    p = P.load()
    rng = random.Random(a.seed)
    tdir = P.PKG / "params" / "train" / f"set{a.seed}"
    tdir.mkdir(parents=True, exist_ok=False)
    lines = [f'# surrogate training design, seed {a.seed}', f'name = "train{a.seed}"', 'seeds = [1]']
    for i in range(a.n):
        plan = [] if rng.random() < 0.2 else random_plan(p, rng)
        anns = random_surprises(rng)
        (tdir / f"dec_{i:02d}.json").write_text(json.dumps({"decisions": plan, "filters": {str(k + 1): messages.TARGETS[d["target"]] for k, d in enumerate(plan)}}, indent=1))
        (tdir / f"ann_{i:02d}.json").write_text(json.dumps({"items": anns}, indent=1))
        rel = tdir.relative_to(P.ROOT)
        lines += ["[[variant]]", f'label = "t{i:02d}"', f'type = "{"plan" if plan else "nodecision"}"',
                  f'decisions = "{rel}/dec_{i:02d}.json"' if plan else 'decisions = "none"',
                  f'seeds = [{rng.randint(1, 50)}]',
                  f'set = ["paths.announcements=\\"{rel}/ann_{i:02d}.json\\""]']
    spec = P.PKG / "params" / "experiments" / f"train_{a.seed}.toml"
    spec.write_text("\n".join(lines) + "\n")
    print(spec)


if __name__ == "__main__":
    main()
