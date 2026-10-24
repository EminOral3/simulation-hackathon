"""Analysis of saved runs: persona quality, design (DOE) main effects, interaction effects, cascades.

    python -m code_kit.cobalt.analysis <run_dir> [<run_dir_seed2>]     # writes analysis.json next to the first run
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from .ask_persona import jl, load_run
from . import params as P

EXIT = {"main bank": 0, "second bank": 0, "dormant": 1, "left": 1}


def entropy(counts: Counter, k: int) -> float:
    n = sum(counts.values())
    if n == 0:
        return 0.0
    ps = np.array([c / n for c in counts.values() if c])
    return float(-(ps * np.log(ps)).sum() / np.log(k))


def persona_quality(d: Path, d2: Path | None) -> dict:
    people = jl(d / "personas.jsonl")
    weekly = jl(d / "weekly.jsonl")
    probe = jl(d / "probe.jsonl")
    out = {}
    # mode collapse: status entropy within group, week 10, and share of the most common answer
    end = [r for r in weekly if r["week"] == 10]
    grp = {f["id"]: f["group"] for f in people}
    by = defaultdict(Counter)
    for r in end:
        by[grp[r["persona"]]][(r["status"], r["money"])] += 1
    out["end_state_entropy_by_group"] = {g: round(entropy(c, 12), 3) for g, c in by.items()}
    out["modal_share_by_group"] = {g: round(max(c.values()) / sum(c.values()), 3) for g, c in by.items()}
    if probe:
        start = defaultdict(dict)
        for r in probe:
            start[(r["persona"], r["when"])][r["question"]] = r["score"]
        rows = [v for (pid, w), v in start.items() if w == "start" and len(v) == 8]
        X = np.array([[v[q] for q in ["1a", "1b", "2a", "2b", "3a", "3b", "4a", "4b"]] for v in rows], float)
        if len(X):
            # S (Costa & Vicente): spread between personas, averaged over questions
            out["S_between_personas"] = round(float(X.std(0).mean()), 3)
            # reverse-coded consistency: 2a vs 2b and 4a vs 4b should be negatively related
            out["corr_2a_2b"] = round(float(np.corrcoef(X[:, 2], X[:, 3])[0, 1]), 3) if X[:, 2].std() and X[:, 3].std() else None
            out["corr_4a_4b"] = round(float(np.corrcoef(X[:, 6], X[:, 7])[0, 1]), 3) if X[:, 6].std() and X[:, 7].std() else None
            out["corr_1a_1b"] = round(float(np.corrcoef(X[:, 0], X[:, 1])[0, 1]), 3) if X[:, 0].std() and X[:, 1].std() else None
        # say-do: stated intention to stay (start) vs actual exit by week 10
        say = {pid: (v["2a"] + (6 - v["2b"])) / 2 for (pid, w), v in start.items() if w == "start" and "2a" in v and "2b" in v}
        did = {r["persona"]: EXIT[r["status"]] for r in end}
        hi = [did[p] for p, s in say.items() if s >= 4 and p in did]
        lo = [did[p] for p, s in say.items() if s < 4 and p in did]
        out["say_do"] = {"exit_rate_if_said_stay": round(float(np.mean(hi)), 3) if hi else None, "n_said_stay": len(hi),
                         "exit_rate_if_said_unsure_or_leave": round(float(np.mean(lo)), 3) if lo else None, "n_other": len(lo)}
        ends = {(r["persona"]): r for r in probe if r["when"] == "end" and r["question"] == "2b"}
        thinking = sum(1 for r in ends.values() if r["score"] >= 4)
        out["say_do"]["end_thinking_of_leaving_share"] = round(thinking / max(1, len(ends)), 3) if ends else None
        out["say_do"]["end_exit_share"] = round(float(np.mean(list(did.values()))), 3) if did else None
    # R: same persona across seeds (status agreement per persona-week)
    if d2:
        w2 = {(r["persona"], r["week"]): r["status"] for r in jl(d2 / "weekly.jsonl")}
        agree = [r["status"] == w2.get((r["persona"], r["week"])) for r in weekly if (r["persona"], r["week"]) in w2]
        out["seed_status_agreement"] = round(float(np.mean(agree)), 3) if agree else None
    return out


def doe_effects(d: Path) -> dict:
    """Main effect of each design axis level on exit (dormant/left), money moved and negative reviews, per group."""
    people = {f["id"]: f for f in jl(d / "personas.jsonl")}
    weekly = jl(d / "weekly.jsonl")
    per = defaultdict(lambda: {"exit": 0, "moved": 0, "neg": 0, "voice": 0})
    for r in weekly:
        x = per[r["persona"]]
        x["exit"] = max(x["exit"], EXIT[r["status"]])
        x["moved"] = max(x["moved"], {"kept": 0, "moved some": 0.3, "moved most": 0.8}[r["money"]])
        x["neg"] = max(x["neg"], int(1 <= r.get("review_stars", 0) <= 2))
        x["voice"] = max(x["voice"], int(bool(r.get("cfpb")) or "complained in app" in r.get("actions", []) or 1 <= r.get("review_stars", 0) <= 2))
    out = {}
    for g in sorted({f["group"] for f in people.values()}):
        ids = [i for i, f in people.items() if f["group"] == g]
        axes = people[ids[0]]["design_levels"].keys()
        res = {}
        for ax in axes:
            levels = sorted({people[i]["design_levels"][ax] for i in ids})
            res[ax] = {lv: {k: round(float(np.mean([per[i][k] for i in ids if people[i]["design_levels"][ax] == lv])), 3)
                            for k in ("exit", "moved", "voice")} for lv in levels}
        out[g] = res
    return out


def interaction_effects(d: Path) -> dict:
    """Peer effect: did a persona move money / exit the week after a tie sent a negative DM or post?"""
    weekly = {(r["persona"], r["week"]): r for r in jl(d / "weekly.jsonl")}
    inter = jl(d / "interactions.jsonl")
    neg_words = ("moving", "moved", "switch", "leaving", "left", "furious", "worst", "done with", "pull", "close", "waited", "hours")
    exposed = defaultdict(set)
    for x in inter:
        if x["type"] in ("dm", "reply") and any(w in x["text"].lower() for w in neg_words):
            exposed[x["to"]].add(x["week"])
    def change(pid, w):
        a, b = weekly.get((pid, w)), weekly.get((pid, w + 1))
        return bool(b and (b["money"] != "kept" or (a and EXIT[b["status"]] > EXIT[a["status"]])))
    exp_rate = [change(pid, w) for pid, ws in exposed.items() for w in ws if w < 10]
    all_pairs = {(r[0], r[1]) for r in weekly}
    unexp = [change(pid, w) for pid, w in all_pairs if w < 10 and w >= 5 and w not in exposed.get(pid, set())]
    counts = Counter(x["type"] for x in inter)
    return {"interactions": dict(counts),
            "acted_next_week_after_negative_message": round(float(np.mean(exp_rate)), 3) if exp_rate else None,
            "n_exposed": len(exp_rate),
            "acted_next_week_otherwise_w5_10": round(float(np.mean(unexp)), 3) if unexp else None,
            "n_unexposed": len(unexp)}


def cascades(d: Path, k: int = 3) -> list[dict]:
    """Chains: a negative message/post -> recipient moves money or exits within 2 weeks."""
    people = {f["id"]: f["name"] for f in jl(d / "personas.jsonl")}
    weekly = {(r["persona"], r["week"]): r for r in jl(d / "weekly.jsonl")}
    out = []
    for x in jl(d / "interactions.jsonl"):
        if x["type"] not in ("dm", "reply") or not x.get("to"):
            continue
        for dw in (0, 1, 2):
            r = weekly.get((x["to"], x["week"] + dw))
            if r and (r["money"] != "kept" or r["status"] in ("dormant", "left")):
                out.append({"week": x["week"], "from": people[x["from"]], "to": people[x["to"]], "text": x["text"][:200],
                            "then": f"week {r['week']}: {r['status']}, money {r['money']}"})
                break
    return out[:k * 5]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    p = P.load()
    d = load_run(p, a.runs[0])
    d2 = load_run(p, a.runs[1]) if len(a.runs) > 1 else None
    res = {"run": d.name, "persona_quality": persona_quality(d, d2), "doe_effects": doe_effects(d),
           "interaction": interaction_effects(d), "cascades": cascades(d)}
    out = d / "analysis.json"
    if out.exists():
        out = d / f"analysis_{len(list(d.glob('analysis*.json')))}.json"
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(json.dumps({k: res[k] for k in ("persona_quality", "interaction")}, indent=1))
    for c in res["cascades"][:5]:
        print(f"w{c['week']} {c['from']} -> {c['to']}: {c['text'][:100]} || {c['then']}")
    print(out)


if __name__ == "__main__":
    main()
