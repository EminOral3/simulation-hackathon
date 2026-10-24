"""Persona behaviour -> board goals (docs/talp_db/data/theory/metric_spec.json). Ratios against
November 2, weights w_active (customers each persona stands for); dormant customers' deposits held fixed.
CI: bootstrap over personas, stratified by group (group totals preserved)."""
from __future__ import annotations

import numpy as np

from . import config, crisis


def _deposit_weights(p: dict, people: list[dict]) -> tuple[np.ndarray, float]:
    """Deposits held by each persona's customers: balance-band midpoint x w_active, scaled per group so the
    active share of the group's deposits matches population_priors. Returns (dep, fixed dormant deposits)."""
    mids = {"<1k": 500, "1-10k": 4000, "10-50k": 25000, "50-250k": 110000, "250k+": 400000}
    priors = config.data(p, "priors")
    dep = np.zeros(len(people))
    dormant = 0.0
    for g, gp in priors["groups"].items():
        idx = [i for i, f in enumerate(people) if f["group"] == g]
        raw = np.array([mids[people[i]["balance_band"]] * people[i]["w_active"] for i in idx], float)
        held_active = gp["deposits_usd"] * gp["active_share"]
        dormant += gp["deposits_usd"] - held_active
        if raw.sum() > 0:
            dep[idx] = raw / raw.sum() * held_active
    return dep, dormant


def _arrays(people: list[dict], weekly: list[dict]):
    ids = [f["id"] for f in people]
    pos = {pid: i for i, pid in enumerate(ids)}
    n, W = len(ids), 10
    st = np.full((n, W), "main bank", dtype=object)
    money = np.full((n, W), "kept", dtype=object)
    added = np.full((n, W), "none", dtype=object)
    neg = np.zeros((n, W))
    cfpb = np.zeros((n, W))
    sup = np.zeros((n, W))
    compl = np.zeros((n, W))
    for r in weekly:
        i, w = pos[r["persona"]], r["week"] - 1
        st[i, w], money[i, w], added[i, w] = r["status"], r["money"], r.get("added_money", "none")
        neg[i, w] = 1.0 if 1 <= r.get("review_stars", 0) <= 2 else 0.0
        cfpb[i, w] = float(bool(r.get("cfpb")))
        sup[i, w] = float(bool(r.get("contacted_support")))
        compl[i, w] = float("complained in app" in r.get("actions", []) or bool(r.get("cfpb")))
    return st, money, added, neg, cfpb, sup, compl


def goals(p: dict, people: list[dict], weekly: list[dict], idx: np.ndarray | None = None) -> dict:
    m = p["metrics"]
    st, money, added, neg, cfpb, sup, compl = _arrays(people, weekly)
    w = np.array([f["w_active"] for f in people], float)
    dep, dormant = _deposit_weights(p, people)
    if idx is not None:  # bootstrap resample, group totals preserved
        groups = np.array([f["group"] for f in people])
        scale = np.zeros(len(people))
        dscale = np.zeros(len(people))
        for g in set(groups):
            gi = np.where(groups == g)[0]
            take = idx[np.isin(idx, gi)]
            cnt = np.bincount(take, minlength=len(people))[gi]
            scale[gi] = cnt * w[gi].sum() / max(1e-9, (cnt * w[gi]).sum())
            dscale[gi] = cnt * dep[gi].sum() / max(1e-9, (cnt * dep[gi]).sum())
        w, dep = w * scale, dep * dscale
    # say-do: a persona's exit (status or money moved) stands for exit_conversion of its customers (VARSAYIM)
    c = m["exit_conversion"]
    active = np.isin(st, ["main bank", "second bank"]) + (1 - c) * ~np.isin(st, ["main bank", "second bank"])
    weekly_active = 100 * (w[:, None] * active).sum(0) / w.sum()

    out_map = {"kept": m["out_kept"], "moved some": m["out_some"], "moved most": m["out_most"]}
    out = np.vectorize(out_map.get)(money).astype(float)
    out = np.where(st == "left", np.maximum(out, m["out_left"]), out)
    out_cum = c * np.maximum.accumulate(out, axis=1)
    inflow = np.vectorize({"none": 0.0, "some": m["in_some"], "a lot": m["in_a_lot"]}.get)(added).astype(float)
    b0, b1 = m["base_weeks"]
    # business-as-usual deposits and withdrawals balance out: count only inflow above the baseline weeks' rate
    in_week = (dep[:, None] * inflow).sum(0)
    in_net_cum = np.cumsum(in_week - in_week[b0 - 1:b1].mean())
    total0 = dep.sum() + dormant
    weekly_dep = 100 * ((dep[:, None] * (1 - out_cum)).sum(0) + in_net_cum + dormant) / total0

    def rate(x):
        return (w[:, None] * x).sum(0) / w.sum()

    neg_r, cfpb_r, sup_r, compl_r = rate(neg), rate(cfpb), rate(sup), rate(compl)
    neg_base = max(m["rate_floor"] / 5, neg_r[b0 - 1:b1].mean())
    w0, w1 = m["rating_window"]
    rating = m["rating_base"] - m["k_rating"] * (neg_r[w0 - 1:w1].mean() - neg_base)
    weekly_rating = m["rating_base"] - m["k_rating"] * (np.array([neg_r[max(0, i - 3):i + 1].mean() for i in range(10)]) - neg_base)
    # anchor-and-ratio with additive smoothing: no complaints in the run = the usual monthly number
    eps = m["rate_floor"]
    cfpb_base = cfpb_r[b0 - 1:b1].mean() + eps
    monthly = np.array([cfpb_r[max(0, i - 3):i + 1].mean() for i in range(10)])
    cfpb_month = m["cfpb_usual"] * (monthly + eps) / cfpb_base
    compl_base = compl_r[b0 - 1:b1].mean() + eps
    return {
        "goal_1": float(weekly_active[-1]), "goal_2": float(weekly_dep[-1]),
        "goal_3": float(min(5.0, rating)), "goal_3b": float(cfpb_month.max()),
        "weekly": {"active_pct": weekly_active.round(3).tolist(), "deposits_pct": weekly_dep.round(3).tolist(),
                   "rating": np.minimum(5, weekly_rating).round(3).tolist(), "cfpb_month": cfpb_month.round(1).tolist(),
                   "neg_review_rate": neg_r.round(4).tolist(), "cfpb_rate": cfpb_r.round(4).tolist(),
                   "support_contact_rate": sup_r.round(4).tolist(),
                   "complaints_month": (m["complaints_usual"] * (np.array([compl_r[max(0, i - 3):i + 1].mean() for i in range(10)]) + eps)
                                        / compl_base).round(0).tolist()},
    }


def compute(p: dict, people: list[dict], weekly: list[dict]) -> dict:
    g = goals(p, people, weekly)
    rng = np.random.default_rng(p["metrics"]["bootstrap_seed"])
    n = len(people)
    boots = {k: [] for k in ("goal_1", "goal_2", "goal_3", "goal_3b")}
    for _ in range(p["metrics"]["bootstrap_n"]):
        gb = goals(p, people, weekly, idx=rng.integers(0, n, n))
        for k in boots:
            boots[k].append(gb[k])
    for k, v in boots.items():
        g[f"{k}_ci95"] = [round(float(np.percentile(v, 2.5)), 3), round(float(np.percentile(v, 97.5)), 3)]
    g["units"] = {"goal_1": "% of November 2 customers active in the last 30 days",
                  "goal_2": "% of November 2 deposits",
                  "goal_3": "App Store rating (stars) on January 10",
                  "goal_3b": "CFPB complaints in the worst 30-day window (usual = 120 per month)"}
    g["targets"] = {"goal_1": ">= 98", "goal_2": ">= 97", "goal_3": ">= 4.3", "goal_3b": "<= 240"}
    g["met"] = {"goal_1": g["goal_1"] >= 98, "goal_2": g["goal_2"] >= 97, "goal_3": g["goal_3"] >= 4.3, "goal_3b": g["goal_3b"] <= 240}
    g["sanity_warnings"] = crisis.sanity_check(p, g["weekly"]["active_pct"], g["goal_2"])
    g["assumptions"] = {k: p["metrics"][k] for k in ("out_some", "out_most", "out_left", "in_some", "in_a_lot", "k_rating",
                                                     "exit_conversion")}
    g["ci_method"] = f"bootstrap over personas stratified by group, n={p['metrics']['bootstrap_n']} (one seed)"
    return g
