"""Main chart: goal tracker, plan vs no decision, weekly, seed range as a band, targets and crisis weeks marked.
Small multiples (one panel per goal, one axis each). Saves PNG + CSV to outputs/reports/<timestamp>_<name>/.

    python -m code_kit.cobalt.report --plan <run> <run> --nodecision <run> <run> [--name final]
    python -m code_kit.cobalt.report --auto --model gemini-3.5-flash-lite --label e0
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from . import params as P
from .ask_persona import load_run

INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
SERIES = {"plan": ("#2a78d6", "Our plan"), "nodecision": ("#eb6834", "No decision")}
PANELS = [("active_pct", "Active customers, % of Nov 2", 98, "≥ 98"),
          ("deposits_pct", "Deposits, % of Nov 2", 97, "≥ 97"),
          ("rating", "App Store rating", 4.3, "≥ 4.3"),
          ("cfpb_month", "CFPB complaints, last 30 days", 240, "≤ 240")]


def series(dirs, key, metrics_file="metrics.json"):
    rows = [json.loads((d / metrics_file).read_text())["weekly"][key] for d in dirs]
    return np.array(rows, float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", nargs="*", default=[])
    ap.add_argument("--nodecision", nargs="*", default=[])
    ap.add_argument("--auto", action="store_true")
    ap.add_argument("--model", default="")
    ap.add_argument("--label", default="")
    ap.add_argument("--name", default="goal_tracker")
    ap.add_argument("--metrics-version", choices=["v1", "v2"], default="v1")
    a = ap.parse_args()
    metrics_file = "metrics_v2.json" if a.metrics_version == "v2" else "metrics.json"
    p = P.load()
    groups = {"plan": [load_run(p, r) for r in a.plan], "nodecision": [load_run(p, r) for r in a.nodecision]}
    if a.auto:
        rows = list(csv.DictReader((P.path(p, "outputs") / "index.csv").open()))
        rows = [r for r in rows if r["status"] == "ok" and a.model in r["model"] and a.label in r["label"]]
        for typ in groups:
            groups[typ] = [P.path(p, "outputs") / "runs" / r["folder"] for r in rows if r["type"] == typ][-2:]
    surprise_weeks = set()
    if a.metrics_version == "v2":
        global PANELS
        versions = set()
        PANELS = [("active_pct", "28-day status proxy (not app usage)", 98, "≥ 98"),
                  PANELS[1], PANELS[2],
                  ("cfpb_month", "CFPB proxy, 28-day windows (see evidence)", 240, "≤ 240")]
        for d in groups["plan"] + groups["nodecision"]:
            metric = json.loads((d / metrics_file).read_text())
            versions.add(metric["metrics_version"])
            if not metric["validity"]["valid"]:
                raise ValueError(f"invalid v2 run: {d}")
            if not metric["cfpb_evidence"]["measurable"]:
                print(f"CFPB unmeasurable: {d.name}; numeric curve is a proxy, not a confirmed pass")
        if len(versions) > 1:
            raise ValueError("cannot mix different metrics versions in one comparison")
    for d in groups["plan"] + groups["nodecision"]:
        for x in json.loads((d / "announcements.snapshot.json").read_text()):
            if x.get("surprise", True):
                surprise_weeks.add(x["week"])
    decisions = json.loads((groups["plan"][0] / "run.json").read_text())["decisions"] if groups["plan"] else []

    plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                         "ytick.color": INK2, "font.family": "DejaVu Sans"})
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.6), facecolor=SURF)
    weeks = np.arange(1, 11)
    out_rows = []
    for ax, (key, title, target, tlabel) in zip(axes, PANELS):
        ends = {t: series(d, key, metrics_file).mean(0)[-1] for t, d in groups.items() if d}
        ax.set_facecolor(SURF)
        ax.axvspan(5.5, 6.5, color="#efeee9", zorder=0)
        for w in surprise_weeks:
            ax.axvline(w - 0.5, color=INK2, lw=0.8, ls=":", zorder=1)
        for d in decisions:
            ax.axvline(d["week"] - 0.5, color=SERIES["plan"][0], lw=0.8, ls="--", alpha=0.6, zorder=1)
        ax.axhline(target, color=INK2, lw=1, ls=(0, (4, 3)), zorder=1)
        for typ, dirs in groups.items():
            if not dirs:
                continue
            col, name = SERIES[typ]
            y = series(dirs, key, metrics_file)
            mean = y.mean(0)
            if len(y) > 1:
                ax.fill_between(weeks, y.min(0), y.max(0), color=col, alpha=0.18, lw=0, zorder=2)
            ax.plot(weeks, mean, color=col, lw=2, zorder=3, solid_capstyle="round")
            ax.plot(weeks[-1], mean[-1], "o", ms=6, color=col, mec=SURF, mew=2, zorder=4)
            dy = 0
            if len(ends) == 2:
                other = [v for t, v in ends.items() if t != typ][0]
                dy = 6 if mean[-1] >= other else -6
            ax.annotate(f"{mean[-1]:.1f}" if key != "rating" else f"{mean[-1]:.2f}", (weeks[-1], mean[-1]),
                        xytext=(6, dy), textcoords="offset points", va="center", color=INK, fontsize=8.5)
            for w, v in zip(weeks, mean):
                out_rows.append({"panel": key, "series": typ, "week": int(w), "mean": round(float(v), 3),
                                 "min": round(float(y[:, w - 1].min()), 3), "max": round(float(y[:, w - 1].max()), 3),
                                 "n_runs": len(y)})
        ax.text(10.4, target, tlabel, color=INK2, fontsize=7.5, va="bottom", ha="right")
        ax.set_title(title, color=INK, fontsize=10, loc="left")
        ax.set_xticks(weeks)
        ax.set_xlim(0.7, 10.9)
        ax.grid(axis="y", color=GRID, lw=0.6)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_xlabel("week")
    axes[0].text(6, axes[0].get_ylim()[0], "migration", ha="center", va="bottom", fontsize=7.5, color=INK2)
    handles = [plt.Line2D([], [], color=SERIES[t][0], lw=2, label=f"{SERIES[t][1]} (n={len(groups[t])} runs, band = range)")
               for t in groups if groups[t]]
    handles += [plt.Line2D([], [], color=INK2, lw=1, ls=(0, (4, 3)), label="board target"),
                plt.Line2D([], [], color=SERIES["plan"][0], lw=0.8, ls="--", label="our decisions take effect"),
                plt.Line2D([], [], color=INK2, lw=0.8, ls=":", label="surprise announced")]
    fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False, fontsize=8, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    out = P.path(p, "outputs") / "reports" / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_{a.name}"
    out.mkdir(parents=True, exist_ok=False)
    fig.savefig(out / f"{a.name}.png", dpi=180, facecolor=SURF)
    with (out / f"{a.name}.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0]))
        w.writeheader()
        w.writerows(out_rows)
    (out / "sources.json").write_text(json.dumps({t: [d.name for d in v] for t, v in groups.items()}, indent=1))
    print(out / f"{a.name}.png")


if __name__ == "__main__":
    main()
