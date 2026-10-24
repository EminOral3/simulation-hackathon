"""Recalculate recorded runs only; writes metrics_v2.json without modifying v1 or calling an LLM."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

from . import metrics_v2
from . import params as P


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def recalculate(folder, *, bootstrap=False, force=False):
    folder = Path(folder)
    target = folder / "metrics_v2.json"
    if target.exists() and not force:
        raise FileExistsError(f"{target} exists; --force only replaces the v2 sidecar")
    p = P.load()
    snapshot = folder / "params.resolved.json"
    if snapshot.exists():
        p = P.merge(p, read_json(snapshot))
    people, weekly = read_jsonl(folder / "personas.jsonl"), read_jsonl(folder / "weekly.jsonl")
    run = read_json(folder / "run.json")
    meta = read_json(folder / "meta.json") if (folder / "meta.json").exists() else {}
    result = metrics_v2.evaluate(p, people, weekly, run=run, meta=meta, bootstrap=bootstrap)
    # Keep actual originally reported values as well as v1 recomputation for audit.
    if (folder / "metrics.json").exists():
        old = read_json(folder / "metrics.json")
        result["original_saved_values"] = {k: old.get(k) for k in metrics_v2.GOALS}
        result["overrun"] = old.get("overrun", meta.get("overrun"))
    def fingerprint(obj):
        return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()
    result["comparison_signature"] = {
        "seed": run.get("seed"), "model": run.get("model"),
        "source_commit": meta.get("git", {}).get("commit"),
        "personas": fingerprint(people),
        "announcements": fingerprint(read_json(folder / "announcements.snapshot.json"))
            if (folder / "announcements.snapshot.json").exists() else None,
        "metric_settings": fingerprint({**p["metrics"], "base_weeks": [1, 2]}),
        "v2_settings": fingerprint(p["metrics_v2"]),
        "world_settings": fingerprint(p["world"]),
        "network_settings": fingerprint(p["network"]),
        "support_settings": fingerprint(p["support"]),
        "actual_overrun": result.get("overrun"),
    }
    target.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    return result


def summary_row(folder, m):
    return {"run": folder.name, "type": m["source_run"]["type"], "seed": m["source_run"]["seed"],
            "model": m["source_run"]["model"], "metrics_version": m["metrics_version"],
            **{k: m.get(k) for k in metrics_v2.GOALS},
            **{k + "_v1": m.get("original_saved_values", {}).get(k) for k in metrics_v2.GOALS},
            **{k + "_met": m.get("met", {}).get(k) for k in metrics_v2.GOALS},
            "all_targets_met": m["all_targets_met"], "assessment": m["assessment"],
            "valid": m["validity"]["valid"], "missing_rows": m["validity"]["missing_rows"],
            "unparsed_rows": m["validity"]["unparsed_rows"],
            "cfpb_raw_events": m.get("cfpb_evidence", {}).get("raw_events"),
            "cfpb_measurable": m.get("cfpb_evidence", {}).get("measurable"),
            "total_cost_usd": m["budget"]["total_cost_usd"],
            "remaining_budget_usd": m["budget"]["remaining_budget_usd"],
            "budget_feasible": m["budget"]["feasible"]}


def paired_deltas(items):
    controls = [(d, m) for d, m in items if m["source_run"]["type"] == "nodecision" and m["validity"]["valid"]]
    rows = []
    for folder, m in items:
        if m["source_run"]["type"] == "nodecision" or not m["validity"]["valid"]:
            continue
        signature = m["comparison_signature"]
        if any(signature[k] is None for k in ("seed", "model", "source_commit", "announcements")):
            continue
        # Never silently select the most flattering control if several are available.
        for d, control in controls:
            if control["comparison_signature"] != signature:
                continue
            row = {"plan": folder.name, "control": d.name, "seed": signature["seed"],
                   "model": signature["model"], "source_commit": signature["source_commit"]}
            for key in metrics_v2.GOALS:
                row["delta_" + key] = m[key] - control[key]
            row["plan_all_targets_met"] = m["all_targets_met"]
            row["control_all_targets_met"] = control["all_targets_met"]
            row["cfpb_measurable"] = m["cfpb_evidence"]["measurable"] and control["cfpb_evidence"]["measurable"]
            rows.append(row)
    return rows


def write_csv(path, rows):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+", help="run directories, or a directory whose direct children are runs")
    ap.add_argument("--bootstrap", action="store_true", help="offline resampling only; default: no intervals")
    ap.add_argument("--force", action="store_true", help="replace metrics_v2.json only; v1 remains untouched")
    ap.add_argument("--out", type=Path, help="new summary directory")
    a = ap.parse_args()
    folders = []
    for arg in a.paths:
        path = Path(arg)
        folders.extend([path] if (path / "run.json").exists()
                       else sorted(d for d in path.iterdir() if d.is_dir() and (d / "run.json").exists()))
    folders = list(dict.fromkeys(d.resolve() for d in folders))
    if not folders:
        raise SystemExit("no recorded runs found")
    out = a.out or P.path(P.load(), "outputs") / "reports" / (
        datetime.now().strftime("%Y%m%d-%H%M%S") + "_metrics_v2")
    out.mkdir(parents=True, exist_ok=False)
    items, errors = [], []
    for folder in folders:
        try:
            m = recalculate(folder, bootstrap=a.bootstrap, force=a.force)
            items.append((folder, m))
        except Exception as exc:
            errors.append({"run": str(folder), "error": f"{type(exc).__name__}: {exc}"})
    write_csv(out / "summary.csv", [summary_row(d, m) for d, m in items])
    pairs = paired_deltas(items)
    write_csv(out / "paired_deltas.csv", pairs)
    group_rows, sensitivity = [], []
    for folder, m in items:
        group_rows.extend({"run": folder.name, "group": g, **v} for g, v in m.get("groups", {}).items())
        sensitivity.extend({"run": folder.name, "exit_conversion": c, **v}
                           for c, v in m.get("sensitivity", {}).items())
    write_csv(out / "groups.csv", group_rows)
    write_csv(out / "exit_sensitivity.csv", sensitivity)
    (out / "errors.json").write_text(json.dumps(errors, indent=2), encoding="utf-8")
    notes = (
        "# Offline metrics v2 re-evaluation\n\n"
        f"Recorded runs: {len(folders)}; evaluated: {len(items)}; read/write errors: {len(errors)}.\n"
        f"Valid recorded runs: {sum(m['validity']['valid'] for _, m in items)}; matched plan/control pairs: {len(pairs)}.\n\n"
        "No API calls or simulation runs. Original files were not overwritten.\n"
        "summary.csv shows original v1 and revised values. Blank target verdict means unknown, not pass.\n"
        "G1 is a 28-day relationship-status proxy, not actual 30-day application usage.\n"
        "CFPB numeric output remains a proxy; see raw event counts and measurability.\n"
        "paired_deltas.csv only matches equal seed/model/source commit/personas/announcements/metric settings.\n"
        "Different treatments can still change LLM sampling behavior; these are model comparisons, not real-world causal proof.\n"
        "exit_sensitivity.csv compares 0.69 and 1.0 on the same recorded behavior.\n"
    )
    (out / "README.md").write_text(notes, encoding="utf-8")
    print(f"Evaluated {len(items)} recorded runs; errors {len(errors)}; summary {out}")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
