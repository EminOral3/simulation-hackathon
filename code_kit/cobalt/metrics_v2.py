"""Versioned, offline board metrics. No LLM calls or changes to persona behavior.

Four board goals remain fixed; G3 has two outputs and G4 is the budget constraint.
v1 metrics.json is preserved. This module evaluates complete recorded behavior only.
"""
from __future__ import annotations

import copy
import hashlib
import math
from collections import Counter
from pathlib import Path

import numpy as np

from . import config, metrics as legacy
from . import params as P

VERSION = "cobalt-metrics-v2.0"
GOALS = ("goal_1", "goal_2", "goal_3", "goal_3b")
TARGETS = {"goal_1": ">= 98", "goal_2": ">= 97", "goal_3": ">= 4.3", "goal_3b": "<= 240"}
STATUSES = {"main bank", "second bank", "dormant", "left"}
MONEY = {"kept", "moved some", "moved most"}


def validate_records(people, weekly, meta=None):
    """Reject gaps and bad values before legacy array defaults can hide them."""
    ids = [f.get("id") for f in people]
    errors = []
    if not ids or any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        errors.append("empty, missing or duplicate persona IDs")
    for f in people:
        w = f.get("w_active")
        if isinstance(w, bool) or not isinstance(w, (int, float)) or not math.isfinite(w) or w <= 0:
            errors.append("invalid positive active weight")
    expected = {(i, w) for i in ids for w in range(1, 11)}
    keys = Counter()
    unparsed = bad = 0
    for r in weekly:
        key = (r.get("persona"), r.get("week"))
        if type(r.get("week")) is not int or key not in expected:
            bad += 1
            continue
        keys[key] += 1
        if r.get("parsed") is not True:
            unparsed += 1
        if (r.get("status") not in STATUSES or r.get("money") not in MONEY
                or r.get("added_money", "none") not in {"none", "some", "a lot"}
                or type(r.get("review_stars", 0)) is not int
                or not 0 <= r.get("review_stars", 0) <= 5
                or type(r.get("cfpb")) is not bool):
            bad += 1
    missing = len(expected - set(keys))
    duplicates = sum(n - 1 for n in keys.values() if n > 1)
    failed = int((meta or {}).get("failed_parses", 0))
    if missing:
        errors.append("missing persona-weeks")
    if duplicates:
        errors.append("duplicate persona-weeks")
    if bad:
        errors.append("invalid weekly fields or unknown persona/week")
    if unparsed or failed:
        errors.append("unparsed model responses")
    if meta and meta.get("status") not in (None, "ok"):
        errors.append("run status is not ok")
    return {"valid": not errors, "errors": sorted(set(errors)), "expected_rows": len(expected),
            "actual_rows": len(weekly), "missing_rows": missing, "duplicate_rows": duplicates,
            "bad_rows": bad, "unparsed_rows": unparsed, "failed_parses": failed}


def _budget(p, run):
    decisions = run.get("decisions", [])
    count = len(decisions) if isinstance(decisions, list) else None
    try:
        cost = config.budget_check(p, decisions)
        feasible, error = True, None
    except (ValueError, KeyError, TypeError) as exc:
        cost = {"total_usd": None, "budget_usd": config.data(p, "menu")["budget_usd"]}
        feasible, error = False, str(exc)
    total, limit = cost["total_usd"], cost["budget_usd"]
    return {"total_cost_usd": total, "budget_usd": limit,
            "remaining_budget_usd": None if total is None else limit - total,
            "budget_utilization_pct": None if total is None else 100 * total / limit,
            "feasible": feasible, "error": error, "decision_count": count,
            "final_decision_count_valid": count == 2,
            "scope": "CFO menu/cost/message checks; dashboard timing and truthfulness need separate review"}


def _active_flags(st, window=4, exclude_closed=False):
    """At each week, any active relationship status in the trailing <=4 weeks.

    This is NOT observed app usage. Closing now does not erase prior recorded activity.
    The relationship-preserving variant can additionally exclude currently closed accounts.
    """
    active = np.isin(st, ["main bank", "second bank"])
    history = np.stack([active[:, max(0, t - window + 1):t + 1].any(axis=1) for t in range(10)], axis=1)
    if exclude_closed:
        history &= st != "left"
    return history


def _weighted_active(flags, weights, conversion):
    return 100 * (weights[:, None] * (flags + (1 - conversion) * ~flags)).sum(axis=0) / weights.sum()


def _g1_resample_ci(flags, people, conversion, n, seed):
    """Diagnostic resampling interval, not a real-population confidence guarantee."""
    if n <= 0:
        return None
    rng = np.random.default_rng(seed)
    w = np.array([f["w_active"] for f in people], float)
    groups = np.array([f["group"] for f in people])
    values = []
    # Same empirical resampling/normalization convention as v1; label it accurately.
    for _ in range(n):
        idx = rng.integers(0, len(people), len(people))
        counts = np.bincount(idx, minlength=len(people))
        ws = np.zeros(len(people))
        for g in set(groups):
            mask = groups == g
            raw = counts[mask] * w[mask]
            if raw.sum() == 0:
                # A missing group is not imputed as zero activity.
                break
            ws[mask] = raw * w[mask].sum() / raw.sum()
        else:
            values.append(float(_weighted_active(flags, ws, conversion)[-1]))
    return np.percentile(values, [2.5, 97.5]).round(3).tolist() if values else None


def _group_results(p, people, weekly, flags):
    st, money, added, neg, cf, _, _ = legacy._arrays(people, weekly)
    w = np.array([f["w_active"] for f in people], float)
    dep, _ = legacy._deposit_weights(p, people)
    m = p["metrics"]
    c = m["exit_conversion"]
    out = np.vectorize({"kept": m["out_kept"], "moved some": m["out_some"], "moved most": m["out_most"]}.get)(money).astype(float)
    out = np.where(st == "left", np.maximum(out, m["out_left"]), out)
    out = c * np.maximum.accumulate(out, axis=1)
    incoming = np.vectorize({"none": 0., "some": m["in_some"], "a lot": m["in_a_lot"]}.get)(added).astype(float)
    b0, b1 = m["base_weeks"]
    priors = config.data(p, "priors")["groups"]
    results = {}
    for group in sorted({f["group"] for f in people}):
        ix = np.array([i for i, f in enumerate(people) if f["group"] == group])
        initial = priors[group]["deposits_usd"]
        fixed = initial - dep[ix].sum()
        inflows = (dep[ix, None] * incoming[ix]).sum(axis=0)
        net_in = (inflows - inflows[b0 - 1:b1].mean()).sum()
        final = float((dep[ix] * (1 - out[ix, -1])).sum() + fixed + net_in)
        results[group] = {
            "n_personas": len(ix), "active_weight": float(w[ix].sum()),
            "active_proxy_28d_pct": float(_weighted_active(flags[ix], w[ix], c)[-1]),
            "initial_deposits_usd": initial, "ending_deposits_usd": final,
            "deposit_retention_pct": 100 * final / initial,
            "net_deposit_loss_usd": initial - final,
            "cfpb_raw_events": int(cf[ix].sum()),
            "negative_review_persona_weeks": int(neg[ix].sum())}
    return results


def evaluate(p, people, weekly, *, run=None, meta=None, bootstrap=True, current_prompt_hash=None):
    """Evaluate recorded outcomes. Retain numeric CFPB proxy but separate measurability."""
    run, meta = run or {"decisions": []}, meta or {}
    cfg = p["metrics_v2"]
    result = {"metrics_version": VERSION,
              "overrun": meta.get("overrun"),
              "metric_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "source_run": {"seed": run.get("seed"), "model": run.get("model"), "type": run.get("type"),
                             "git": meta.get("git"), "persona_set": meta.get("persona_set"),
                             "prompt_sha256": current_prompt_hash or meta.get("prompt_sha256"),
                             "prompt_version_note": "unknown for historical runs unless originally recorded"},
              "targets": TARGETS, "budget": _budget(p, run),
              "validity": validate_records(people, weekly, meta)}
    if not result["validity"]["valid"]:
        result.update({k: None for k in GOALS})
        result.update({"met": {k: None for k in GOALS}, "all_targets_met": None,
                       "assessment": "invalid_recorded_run"})
        return result
    q = copy.deepcopy(p)
    # Identical uncontaminated calendar definition for every evaluated run.
    q["metrics"]["base_weeks"] = list(cfg["base_weeks"])
    if q["metrics"]["base_weeks"] != [1, 2]:
        raise ValueError("metrics v2 clean reference must be weeks 1-2 for this case")
    if bootstrap and q["metrics"]["bootstrap_n"] > 0:
        base = legacy.compute(q, people, weekly)
    else:
        base = legacy.goals(q, people, weekly)
    original = legacy.goals(p, people, weekly)
    result.update(base)
    st, money, added, neg, cf, _, _ = legacy._arrays(people, weekly)
    w = np.array([f["w_active"] for f in people], float)
    flags = _active_flags(st, exclude_closed=cfg["exclude_closed"])
    c = q["metrics"]["exit_conversion"]
    rolling = _weighted_active(flags, w, c)
    relation = _weighted_active(_active_flags(st, exclude_closed=True), w, c)
    result["goal_1"] = float(rolling[-1])
    result["goal_1_ci95"] = _g1_resample_ci(flags, people, c,
        q["metrics"]["bootstrap_n"] if bootstrap else 0, q["metrics"]["bootstrap_seed"])
    result["weekly"]["active_pct"] = rolling.round(3).tolist()
    result["active_proxy"] = {"window_days": 28, "observed_app_usage": False,
                             "exclude_closed": cfg["exclude_closed"],
                             "end_week_relationship_pct": original["goal_1"],
                             "relationship_preserving_28d_pct": float(relation[-1]),
                             "initial_active_weight": float(w.sum()),
                             "scope": "initial active cohort; inactive-customer reactivation not modeled"}
    # Original stochastic/model assumptions remain explicit.
    result["assumptions"] = {k: q["metrics"][k] for k in
        ("out_some", "out_most", "out_left", "in_some", "in_a_lot", "k_rating", "exit_conversion")}
    result["assumptions"]["base_weeks"] = [1, 2]
    result["assumptions"]["goal_2"] = "maximum cumulative outflow level, not a sum of repeated statements"
    raw_count = int(cf.sum())
    base_raw = int(cf[:, :2].sum())
    measurable = bool(cfg["cfpb_calibration_validated"] and raw_count >= cfg["cfpb_min_events"]
                      and base_raw >= cfg["cfpb_min_base_events"])
    result["cfpb_evidence"] = {
        "raw_events": raw_count, "base_raw_events": base_raw,
        "raw_event_definition": "persona-weeks with cfpb=true; old logs cannot deduplicate the same complaint across weeks",
        "persona_weeks": len(weekly), "measurable": measurable,
        "numeric_value_is_proxy": True, "window_days": 28,
        "calibration_validated": cfg["cfpb_calibration_validated"],
        "min_events": cfg["cfpb_min_events"], "min_base_events": cfg["cfpb_min_base_events"],
        "threshold_note": "operational screening thresholds, not statistical validity guarantees",
        "reason": None if measurable else "sparse events and/or no validated population calibration",
        "baseline": "same weeks 1-2 definition, per-run proxy with additive smoothing; not a calibrated shared rate"}
    numeric = {"goal_1": result["goal_1"] >= 98, "goal_2": result["goal_2"] >= 97,
               "goal_3": result["goal_3"] >= 4.3, "goal_3b": result["goal_3b"] <= 240}
    result["numeric_threshold_met"] = numeric
    result["met"] = {**numeric, "goal_3b": numeric["goal_3b"] if measurable else None}
    statuses = list(result["met"].values()) + [result["budget"]["feasible"]]
    result["all_targets_met"] = False if False in statuses else (None if None in statuses else True)
    result["assessment"] = "fails_known_target" if result["all_targets_met"] is False else (
        "indeterminate" if result["all_targets_met"] is None else "all_targets_met_in_model")
    result["units"] = {"goal_1": "% of initial active cohort: 28-day relationship-status proxy, not observed 30-day app usage",
                       "goal_2": "% of November 2 deposits", "goal_3": "App Store score proxy, not a review-stock reconstruction",
                       "goal_3b": "CFPB monthly proxy from rolling 28-day windows; measurability flagged separately"}
    result["ci_method"] = ("diagnostic percentile resampling interval over model personas, pooled draws with group-weight "
                           "renormalization; not classical stratified bootstrap; network dependence ignored; "
                           "not validated 95% coverage for real customers")
    result["legacy_values"] = {k: original[k] for k in GOALS}
    result["sensitivity"] = {}
    for conversion in sorted({0.69, 1.0, c}):
        alt = copy.deepcopy(q)
        alt["metrics"]["exit_conversion"] = conversion
        values = legacy.goals(alt, people, weekly)
        values["goal_1"] = float(_weighted_active(flags, w, conversion)[-1])
        result["sensitivity"][str(conversion)] = {k: values[k] for k in GOALS}
    result["groups"] = _group_results(q, people, weekly, flags)
    return result
