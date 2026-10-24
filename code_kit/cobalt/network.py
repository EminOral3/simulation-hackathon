"""Strong-tie network between personas (family, friends, coworkers): frozen with the persona set.
Homophily (same_group_share), preferential attachment (degree + 1, like sim_core.ba_graph) and extra ties
for opinion leaders. Every tie carries a relation label the persona reads in its prompt."""
from __future__ import annotations

import random

RELATIONS = {
    frozenset(["students"]): ["classmate", "roommate", "friend from school"],
    frozenset(["students", "everyday customers"]): ["older cousin", "sibling", "friend"],
    frozenset(["students", "paycheck customers"]): ["sibling", "cousin", "friend"],
    frozenset(["students", "savers with large balances"]): ["older sibling", "cousin"],
    frozenset(["students", "small business owners with a Cobalt card reader"]): ["part-time boss", "family friend"],
    frozenset(["paycheck customers", "everyday customers"]): ["coworker", "friend", "neighbor"],
    frozenset(["paycheck customers"]): ["coworker", "friend", "sibling"],
    frozenset(["everyday customers"]): ["friend", "neighbor", "coworker", "partner's friend"],
    frozenset(["savers with large balances"]): ["former colleague", "friend", "college friend"],
    frozenset(["savers with large balances", "everyday customers"]): ["friend", "sibling", "former colleague"],
    frozenset(["savers with large balances", "paycheck customers"]): ["sibling", "friend"],
    frozenset(["small business owners with a Cobalt card reader"]): ["fellow business owner", "friend from the market"],
    frozenset(["small business owners with a Cobalt card reader", "everyday customers"]): ["regular customer", "friend"],
    frozenset(["small business owners with a Cobalt card reader", "paycheck customers"]): ["regular customer", "cousin"],
    frozenset(["small business owners with a Cobalt card reader", "savers with large balances"]): ["friend", "accountant friend"],
}


def build(p: dict, people: list[dict]) -> dict[str, list[dict]]:
    cfg = p["network"]
    rng = random.Random(cfg["graph_seed"])
    ids = [f["id"] for f in people]
    by = {f["id"]: f for f in people}
    target = {}
    for f in people:
        t = rng.randint(cfg["ties_min"], cfg["ties_max"])
        if f["opinion_role"].startswith("lead"):
            t += cfg["leader_extra_ties"]
        target[f["id"]] = t
    edges: dict[str, dict[str, str]] = {i: {} for i in ids}
    order = ids[:]
    rng.shuffle(order)
    for _ in range(3):  # a few passes so late nodes still find partners
        for a in order:
            while len(edges[a]) < target[a]:
                cands = [b for b in ids if b != a and b not in edges[a] and len(edges[b]) < target[b] + 1]
                if not cands:
                    break
                ga = by[a]["group"]
                w = [(cfg["same_group_share"] if by[b]["group"] == ga else (1 - cfg["same_group_share"]) / 4)
                     * (1 + len(edges[b])) * (1.5 if by[b]["opinion_role"].startswith("lead") else 1.0) for b in cands]
                b = rng.choices(cands, weights=w, k=1)[0]
                key = frozenset([ga, by[b]["group"]])
                rel = rng.choice(RELATIONS.get(key, ["friend"]))
                edges[a][b] = rel
                edges[b][a] = rel
    return {a: [{"id": b, "relation": r, "cobalt": True} for b, r in sorted(edges[a].items())] for a in ids}
