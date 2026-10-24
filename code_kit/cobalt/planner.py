"""Weekly planner: given the current week, the decisions already in effect and the surprises announced so far,
screen every remaining decision (action combination x target x week) against many future-surprise scenarios
(bad and good) with the fast surrogate simulator, then check the best plans with the real LLM personas.

    python -m code_kit.cobalt.planner --week 3 [--locked locked.json] [--overrun known-level] [--validate] [--live]

--week N   : the company week now running (0 = before 13:00). Decisions for weeks <= N are fixed; new or replaced
             decisions can start at week N+1 at the earliest (challenge rule).
--locked   : decision file (same format as params/decisions/*.json) with what is locked on the dashboard now.
             Decisions with week <= N are kept as given; later ones are treated as replaceable and re-optimized
             (they are still reported for comparison).
Surprises so far are read from paths.announcements (the dashboard log), only weeks <= N.

Output: outputs/planner/<timestamp>_w<N>/report.md (+ candidates.csv, scenarios.json).
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import itertools
import json
import random
import time
from datetime import datetime
from pathlib import Path

import numpy as np

from . import config, crisis, messages, personas
from . import params as P
from .fastsim import FastWorld, all_met, utility
from .surrogate import Model, latest

GOALS = ["goal_1", "goal_2", "goal_3", "goal_3b"]


# ----------------------------------------------------------------------------- inputs
STOP = {"that", "this", "they", "them", "their", "from", "with", "some", "have", "were", "week", "known", "cobalt",
        "customers", "customer", "said", "says", "report", "reports", "reported", "which", "about", "more", "than"}


def _stem(w: str) -> str:
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[: -len(suf)]
    return w


def _words(t: str) -> set:
    import re
    return {_stem(w) for w in re.findall(r"[a-z]+", t.lower()) if len(w) > 3 and w not in STOP}


def classify_any(p: dict, text: str) -> tuple[str, str]:
    """Best library archetype (bad or good) by word overlap with its texts, plus crisis_kb signal hits."""
    tw = _words(text)
    kb = {a["id"]: a for a in config.data(p, "crisis_kb")["archetypes"]}
    best, score_ = None, -1.0
    for a in crisis.library()["archetypes"]:
        sim = max(len(tw & _words(x)) / max(1, len(tw | _words(x))) for x in a["texts"])
        sim += 0.05 * sum(s_.lower() in text.lower() for s_ in kb.get(a["id"], {}).get("signals", []))
        if sim > score_:
            best, score_ = a["id"], sim
    return best, f"auto (similarity {score_:.2f})"


def classify_llm(p: dict, text: str, live: bool) -> tuple[str, str, str]:
    """Analyst-side reading of a dashboard announcement: archetype (bad or good), severity. One lite call."""
    from pydantic import BaseModel
    from typing import Literal
    from .llm import LLM
    lib = crisis.library()["archetypes"]
    ids = [a["id"] for a in lib]

    class Reading(BaseModel):
        archetype: Literal[tuple(ids)]
        severity: Literal["low", "base", "high"]
        reason: str
    menu = "\n".join(f"- {a['id']} ({a['polarity']} for Cobalt): {a['texts'][0]}" for a in lib)
    prompt = (f"You classify news for Cobalt Bank, a US digital bank. Pick the archetype that best matches the "
              f"announcement, judging whether it is bad or good for Cobalt, and its severity for Cobalt's customers.\n"
              f"ARCHETYPES:\n{menu}\n\nANNOUNCEMENT: {text}\nAnswer as JSON.")
    if not live:
        aid, how = classify_any(p, text)
        return aid, "base", how
    llm = LLM(p, live=True, model=P.model_id(p, "experiment"))
    c = asyncio.run(llm.ask(call_id="classify", persona=None, week=0, kind="classify", prompt=prompt, seed=1,
                            schema=Reading))
    if not c.parsed:
        aid, how = classify_any(p, text)
        return aid, "base", how
    return c.parsed["archetype"], c.parsed["severity"], f"LLM: {c.parsed['reason'][:100]}"


def observed_surprises(p: dict, week: int, live: bool = False) -> list[dict]:
    """Announcements so far. Our reading in announcements.json ('archetypes', 'severity') wins; otherwise auto."""
    out = []
    for a in crisis.load_announcements(p, True):
        if not a.get("surprise", True) or a["week"] > week:
            continue
        sev = a.get("severity", "base")
        if a.get("archetypes"):
            aid, how = a["archetypes"][0], "our reading"
        else:
            aid, sev, how = classify_llm(p, a["text"], live)
        out.append({"week": a["week"], "archetype": aid, "severity": sev, "observed": True,
                    "how": how, "text": a["text"][:120]})
    return out


def scenarios(p: dict, week: int, observed: list[dict]) -> list[dict]:
    """Scenario = observed surprises + sampled future ones. Always includes 'no further surprise'."""
    o = p["optimize"]
    rng = random.Random(o["scenario_seed"] + week)
    lib = crisis.library()["archetypes"]
    good = [a for a in lib if a["polarity"] == "good"]
    bad = [a for a in lib if a["polarity"] == "bad"]
    future = list(range(week + 1, 11))
    out = [{"name": "no further surprise", "surprises": list(observed)}]
    for i in range(o["n_random_scenarios"]):
        sx = list(observed)
        names = []
        for _ in range(rng.randint(1, o["max_future_surprises"])):
            if not future:
                break
            a = rng.choice(good if rng.random() < o["p_good"] else bad)
            ws = [w for w in a["weeks"] if w in future] or future
            w = rng.choice(ws)
            sev = rng.choice(["low", "base", "base", "high"])
            sx.append({"week": w, "archetype": a["id"], "severity": sev})
            names.append(f"{a['id'].split('_', 1)[1]}@w{w}({sev})")
        out.append({"name": " + ".join(names) or "no further surprise", "surprises": sx})
    return out


def playbook_scenarios(p: dict, week: int, observed: list[dict]) -> list[dict]:
    """One scenario per library archetype at its first plausible future week: 'what if X happens next?'."""
    out = []
    for a in crisis.library()["archetypes"]:
        ws = [w for w in a["weeks"] if w > week]
        if ws:
            out.append({"name": f"{a['polarity']}: {a['id']} in week {ws[0]}", "archetype": a["id"], "week": ws[0],
                        "surprises": observed + [{"week": ws[0], "archetype": a["id"], "severity": "base"}]})
    return out


def fixed_and_open(p: dict, locked_file: str | None, week: int, people: list[dict]):
    decisions, filters = config.load_decisions(p, locked_file) if locked_file else ([], {})
    fixed, replaceable = [], []
    for i, d in enumerate(decisions, 1):
        d = dict(d)
        d["_mask"] = np.array([config.in_target(f, filters.get(str(i))) for f in people])
        (fixed if d["week"] <= week else replaceable).append(d)
    return fixed, replaceable


# ----------------------------------------------------------------------------- evaluation
class Evaluator:
    def __init__(self, p, fw: FastWorld, scen: list[dict], overruns: list[tuple[int, float]], reps: int):
        self.p, self.fw, self.scen, self.overruns, self.reps = p, fw, scen, overruns, reps
        self.calls = 0

    def run(self, plans: list[list[dict]], scen: list[dict] | None = None, chunk: int = 300) -> dict:
        scen = scen or self.scen
        n = len(plans)
        acc = {k: np.zeros((n, len(scen))) for k in GOALS + ["u", "met"]}
        for s_i, s in enumerate(scen):
            for ov, wov in self.overruns:
                for r in range(self.reps):
                    rep = 1000 * s_i + 10 * ov + r
                    for c0 in range(0, n, chunk):
                        g = self.fw.simulate(plans[c0:c0 + chunk], s["surprises"], ov, rep)
                        sl = slice(c0, c0 + chunk)
                        wt = wov / self.reps
                        for k in GOALS:
                            acc[k][sl, s_i] += wt * g[k]
                        acc["u"][sl, s_i] += wt * utility(self.p, g)
                        acc["met"][sl, s_i] += wt * all_met(g)
                        self.calls += 1
        return acc


def plan_cost(plan: list[dict], p: dict) -> int:
    return sum(config.decision_cost(p, d) for d in plan)


def score(acc: dict, plans: list[list[dict]], p: dict) -> np.ndarray:
    cost = np.array([sum(config.decision_cost(p, d) for d in pl if not d.get("_fixed")) for pl in plans]) / 1e6
    return acc["u"].mean(1) - p["optimize"]["w_cost_per_musd"] * cost


def redundant(p: dict, a: dict, b: dict) -> bool:
    """Same action in both decisions while the first is still running (permanent or overlapping weeks): money wasted."""
    first, second = sorted([a, b], key=lambda d: d["week"])
    for x in first["actions"]:
        spec = config.action_spec(p, x["action"])
        if any(y["action"] == x["action"] for y in second["actions"]):
            if spec.get("permanent") or second["week"] < first["week"] + spec.get("duration_weeks", 99):
                return True
    return False


def describe(d: dict) -> str:
    acts = "; ".join(f"{a['action'].split(',')[0]} [{a['level']}]" for a in d["actions"])
    return f"w{d['week']} | {d['target']} | {acts}"


# ----------------------------------------------------------------------------- search
def search(p, ev: Evaluator, fixed: list[dict], earliest: int, budget_left: int, t_end: float, log) -> tuple:
    o = p["optimize"]
    n_open = 2 - len(fixed)
    fixed = [dict(d, _fixed=True) for d in fixed]
    base_plan = [fixed]
    if n_open == 0:
        acc = ev.run(base_plan)
        return base_plan, acc, {}
    weeks = list(range(earliest, 11))
    # stage A: every single action-level x target x week
    singles = []
    for w in weeks:
        for o_ in messages.actions_menu(p):
            if o_[0] == "offline_limit" and w > 6:
                continue
            if o_[3] > budget_left:
                continue
            for t in o["targets"]:
                if o_[0] in ("extra_support", "offline_limit", "early_pay") and t != "everyone":
                    continue  # company-wide actions: target does not change them
                singles.append(messages.decision((o_,), w, t))
    plans = [fixed + [d] for d in singles]
    screen = ev.scen[: o["screen_scenarios"]]
    reps0, ev.reps = ev.reps, 1
    log(f"stage A: {len(plans)} single-action decisions x {len(screen)} screening scenarios")
    accA = ev.run(plans, screen)
    sA = score(accA, plans, p)
    # stage B: per week, the best K distinct actions (each with its best target) combined 2-3 at a time
    best_by_week: dict[int, list] = {}
    for i in np.argsort(-sA):
        d = singles[i]
        lst = best_by_week.setdefault(d["week"], [])
        aid = d["actions"][0]["action"]
        if len(lst) < o["top_singletons_per_week"] and all(x["actions"][0]["action"] != aid for x in lst):
            lst.append(d)
    menu = {(o_[1], o_[2]): o_ for o_ in messages.actions_menu(p)}
    combos = []
    seen = set()
    for w, lst in best_by_week.items():
        for k in (2, 3):
            for group in itertools.combinations(lst, k):
                c = tuple(menu[(x["actions"][0]["action"], x["actions"][0]["level"])] for x in group)
                if messages.cost(c) > budget_left:
                    continue
                for t in {group[0]["target"], "everyone"}:
                    key = (w, t, tuple(sorted((x[0], x[2]) for x in c)))
                    if key not in seen:
                        seen.add(key)
                        combos.append(messages.decision(c, w, t))
    if time.time() < t_end and combos:
        plansB = [fixed + [d] for d in combos]
        log(f"stage B: {len(plansB)} multi-action decisions")
        accB = ev.run(plansB, screen)
        sB = score(accB, plansB, p)
        cand = [(sA[i], singles[i]) for i in range(len(singles))] + [(sB[i], combos[i]) for i in range(len(combos))]
    else:
        cand = [(sA[i], singles[i]) for i in range(len(singles))]
    cand.sort(key=lambda x: -x[0])
    top = [d for _, d in cand[: o["top_decisions"]]]
    if n_open == 1:
        final = [fixed + [d] for d in top]
    else:
        # stage C: pairs of decisions within the remaining budget (and each pair once)
        final = []
        for i, a in enumerate(top):
            for b in top[i:]:
                if a is b and len(top) > 1:
                    continue
                if config.decision_cost(p, a) + config.decision_cost(p, b) > budget_left:
                    continue
                if redundant(p, a, b):
                    continue
                final.append(sorted([a, b], key=lambda d: d["week"]))
        # keep single-decision plans too (the second one can be a cheap placeholder later)
        final += [[d] for d in top[:10]]
        log(f"stage C: {len(final)} two-decision plans")
    ev.reps = reps0
    log(f"stage C: full evaluation of {len(final)} plans x {len(ev.scen)} scenarios x {ev.reps} reps")
    accC = ev.run(final)
    return final, accC, {"singles": len(singles), "combos": len(combos)}


# ----------------------------------------------------------------------------- report
def table_row(i, pl, acc, j, p, fixed_n):
    g = {k: acc[k][j].mean() for k in GOALS}
    worst = acc["u"][j].min()
    return (f"| {i} | " + "<br>".join(describe(d) for d in pl[fixed_n:]) +
            f" | ${plan_cost(pl[fixed_n:], p)/1e6:.2f}M | {g['goal_1']:.1f} | {g['goal_2']:.1f} | {g['goal_3']:.2f} | "
            f"{g['goal_3b']:.0f} | {acc['met'][j].mean():.0%} | {acc['u'][j].mean():.2f} | {worst:.2f} |")


def write_report(out: Path, ctx: dict, final, accC, scen, play, nodec, p, fixed, extra):
    s = score(accC, final, p)
    order = np.argsort(-s)
    fn = len(fixed)
    L = [f"# Planner report: week {ctx['week']} (earliest new decision: week {ctx['earliest']})", "",
         f"Generated {ctx['time']} in {ctx['seconds']:.0f}s. Surrogate `{ctx['model']}` "
         f"(heldout log-loss vs base rate in meta). **Screening only: the hand-in runs are LLM runs.**", "",
         "## Inputs", f"- Fixed decisions (week <= {ctx['week']}): " + ("; ".join(describe(d) for d in fixed) or "none"),
         f"- Budget left: ${ctx['budget_left']/1e6:.2f}M",
         "- Surprises observed: " + ("; ".join(f"w{s_['week']} {s_['archetype']} ({s_['severity']}, {s_['how']})" for s_ in ctx["observed"]) or "none"),
         f"- Surrogate fidelity (run level, held-out LLM runs): {ctx['fidelity']}",
         f"- Migration overrun: {ctx['overrun_note']}",
         f"- Scenarios: {len(scen)} (no further surprise + random bad/good mixes), {ctx['reps']} reps each; "
         f"searched {extra.get('singles', 0)} single-action and {extra.get('combos', 0)} multi-action decisions, "
         f"{len(final)} final plans.", "",
         "## No decision (business as usual from here)",
         f"goal_1 {nodec['goal_1']:.1f} · goal_2 {nodec['goal_2']:.1f} · goal_3 {nodec['goal_3']:.2f} · goal_3b {nodec['goal_3b']:.0f} · "
         f"P(all goals) {nodec['met']:.0%}", "",
         "## Best plans (mean over scenarios; worst = lowest scenario utility)",
         "| # | remaining decision(s) | cost | active % | deposits % | rating | CFPB/mo | P(all) | utility | worst |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for i, j in enumerate(order[:10], 1):
        L.append(table_row(i, final[j], accC, j, p, fn))
    # timing: best plan by the week of the next decision
    L += ["", "## When to act: best plan whose next decision starts in week w",
          "| week | best plan | utility | P(all) |", "|---|---|---|---|"]
    by_w = {}
    for j in order:
        w = min(d["week"] for d in final[j][fn:]) if final[j][fn:] else None
        if w is not None and w not in by_w:
            by_w[w] = j
    for w in sorted(by_w):
        j = by_w[w]
        L.append(f"| {w} | " + "<br>".join(describe(d) for d in final[j][fn:]) + f" | {accC['u'][j].mean():.2f} | {accC['met'][j].mean():.0%} |")
    # robustness per scenario for the top plan
    j0 = order[0]
    L += ["", "## Top plan per scenario", "| scenario | active % | deposits % | rating | CFPB | all goals |", "|---|---|---|---|---|---|"]
    for si, sc in enumerate(scen):
        L.append(f"| {sc['name']} | {accC['goal_1'][j0, si]:.1f} | {accC['goal_2'][j0, si]:.1f} | {accC['goal_3'][j0, si]:.2f} | "
                 f"{accC['goal_3b'][j0, si]:.0f} | {accC['met'][j0, si]:.0%} |")
    if play:
        L += ["", "## Playbook: if this surprise is announced next, best response among the shortlisted plans",
              "(a decision answering a surprise of week N can start in week N+1)", "",
              "| if announced | best plan | utility | vs top plan |", "|---|---|---|---|"]
        for row in play:
            L.append(f"| {row['name']} | {row['plan']} | {row['u']:.2f} | {row['delta']:+.2f} |")
    if ctx.get("validation"):
        L += ["", "## LLM check (real personas, lite, 1 seed, current announcements)",
              "| plan | surrogate active/deposits | LLM active/deposits | LLM rating | LLM CFPB | run |", "|---|---|---|---|---|---|"]
        for v in ctx["validation"]:
            L.append(f"| {v['name']} | {v['sur']} | {v['llm']} | {v['rating']} | {v['cfpb']} | `{v['run']}` |")
    L += ["", "## Notes",
          "- Utility: per goal weight x clip((value - target)/tol, -3, 1), weights and tolerances in params [optimize].",
          "- The surrogate learned from LLM runs; it extrapolates poorly to surprise types and actions it rarely saw. "
          "Treat ranks, not decimals. Confirm the chosen plan with LLM runs before locking.",
          "- Candidate messages are composed from factual snippets (messages.py); edit the wording before locking, "
          "keep the facts."]
    (out / "report.md").write_text("\n".join(L) + "\n")


def save_candidates(out: Path, final, accC, p, fixed_n):
    s = score(accC, final, p)
    order = np.argsort(-s)
    with (out / "candidates.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["rank", "plan", "cost", *GOALS, "p_all", "utility", "worst"])
        for i, j in enumerate(order, 1):
            w.writerow([i, " || ".join(describe(d) for d in final[j][fixed_n:]), plan_cost(final[j][fixed_n:], p),
                        *[round(accC[k][j].mean(), 3) for k in GOALS], round(accC["met"][j].mean(), 3),
                        round(accC["u"][j].mean(), 3), round(accC["u"][j].min(), 3)])
    for i, j in enumerate(order[:5], 1):
        plan = [{k: v for k, v in d.items() if not k.startswith("_")} for d in final[j]]
        filters = {str(k + 1): messages.TARGETS.get(d["target"], {}) for k, d in enumerate(plan)}
        (out / f"plan_rank{i}.json").write_text(json.dumps({"decisions": plan, "filters": filters}, indent=1, ensure_ascii=False))


async def validate(p, out: Path, ranked_files: list[Path], live: bool, log) -> list[dict]:
    from .llm import LLM
    from .run import run_one
    llm = LLM(p, live=live, model=P.model_id(p, "experiment"))
    jobs = [("no-decision", None)] + [(f.stem, f) for f in ranked_files]

    async def one(name, f):
        d = await run_one(p, llm, run_type="nodecision" if f is None else "plan", seed=1,
                          decisions_file=str(f) if f else None, label=f"planner-{name}", probe=False, quiet=True)
        m = json.loads((d / "metrics.json").read_text())
        return {"name": name, "run": d.name, "llm": f"{m['goal_1']:.1f} / {m['goal_2']:.1f}",
                "rating": f"{m['goal_3']:.2f}", "cfpb": f"{m['goal_3b']:.0f}"}
    log(f"LLM check: {len(jobs)} runs")
    return await asyncio.gather(*(one(n, f) for n, f in jobs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", type=int, required=True, help="company week now running (0 = before 13:00)")
    ap.add_argument("--locked", help="decision file with what is locked now")
    ap.add_argument("--overrun", choices=["on time", "a few hours late", "into Monday"],
                    help="known migration outcome (after week 6)")
    ap.add_argument("--validate", action="store_true", help="LLM-check the top plans (needs --live for real LLM)")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--surrogate")
    ap.add_argument("--params", action="append", default=[])
    ap.add_argument("--set", action="append", default=[])
    a = ap.parse_args()
    p = P.load(a.params, a.set)
    o = p["optimize"]
    t0 = time.time()
    out = P.path(p, "outputs") / "planner" / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_w{a.week}"
    out.mkdir(parents=True, exist_ok=False)
    logf = (out / "log.txt").open("w")

    def log(m):
        line = f"[{time.time() - t0:5.0f}s] {m}"
        print(line, flush=True)
        logf.write(line + "\n")

    _, people, _ = personas.load_set(p)
    mpath = Path(a.surrogate) if a.surrogate else latest(p)
    fw = FastWorld(p, people, Model.load(mpath))
    earliest = a.week + 1
    fixed, replaceable = fixed_and_open(p, a.locked, a.week, people)
    budget_left = config.data(p, "menu")["budget_usd"] - sum(config.decision_cost(p, d) for d in fixed)
    obs = observed_surprises(p, a.week, a.live)
    scen = scenarios(p, a.week, obs)
    levels = p["world"]["overrun_levels"]
    if a.overrun:
        overruns, note = [(levels.index(a.overrun), 1.0)], f"known: {a.overrun}"
    elif a.week >= 7:
        log("WARNING: week >= 7 but --overrun not given; still averaging over overrun levels")
        overruns, note = list(enumerate(o["overrun_weights"])), "unknown (averaged)"
    else:
        overruns, note = list(enumerate(o["overrun_weights"])), "unknown (averaged over on time / few hours / into Monday)"
    ev = Evaluator(p, fw, scen, overruns, o["reps"])
    # time check on a small batch, then shrink scenarios if needed
    tt = time.time()
    ev.run([[]], scen[:1])
    per_scen_plan = (time.time() - tt)
    log(f"surrogate {mpath.parent.name}; {len(people)} personas; fixed {len(fixed)}, budget left ${budget_left:,}; "
        f"{len(obs)} surprises observed; {len(scen)} scenarios; one plan-scenario batch {per_scen_plan:.2f}s")
    t_end = t0 + o["time_budget_s"]
    final, accC, extra = search(p, ev, fixed, earliest, budget_left, t_end, log)
    fixed_n = len(fixed)
    nod = ev.run([[dict(d, _fixed=True) for d in fixed]])
    nodec = {k: nod[k][0].mean() for k in GOALS + ["met"]}
    # playbook: the shortlisted plans under single-surprise scenarios
    s = score(accC, final, p)
    order = np.argsort(-s)
    short = [final[j] for j in order[:25]]
    play = []
    if time.time() < t0 + o["time_budget_s"] * 1.4:
        pbs = playbook_scenarios(p, a.week, obs)
        accP = ev.run(short, pbs)
        for si, sc in enumerate(pbs):
            # a response to a surprise can only start the week after it; keep plans whose open decisions fit
            ok = [k for k, pl in enumerate(short) if all(d["week"] > sc["week"] or d.get("_fixed") or d["week"] <= a.week + 1
                                                         for d in pl)]
            k = max(ok or range(len(short)), key=lambda k: accP["u"][k, si])
            play.append({"name": sc["name"], "plan": "<br>".join(describe(d) for d in short[k][fixed_n:]),
                         "u": accP["u"][k, si], "delta": accP["u"][k, si] - accP["u"][0, si]})
    save_candidates(out, final, accC, p, fixed_n)
    fid = "no check yet (python -m code_kit.cobalt.surrogate_check)"
    checks = sorted((P.path(p, "outputs") / "surrogate").glob("check_*.json"))
    if checks and checks[-1].stat().st_mtime > mpath.stat().st_mtime:
        c = json.loads(checks[-1].read_text())
        fid = "; ".join(f"{g} MAE {c[g]['mae']:.2f} r {c[g]['corr'] or 0:.2f}" for g in GOALS) + \
            ". CFPB is not informative when r < 0.3: judge it by the LLM check."
    elif checks:
        fid = "last check is older than this surrogate; rerun surrogate_check"
    ctx = {"week": a.week, "earliest": earliest, "fidelity": fid, "time": datetime.now().strftime("%H:%M:%S"), "seconds": time.time() - t0,
           "model": mpath.parent.name, "budget_left": budget_left, "observed": obs, "overrun_note": note, "reps": o["reps"]}
    if replaceable:
        log("replaceable locked decisions (re-optimized): " + "; ".join(describe(d) for d in replaceable))
        ev2 = ev.run([[dict(d, _fixed=True) for d in fixed] + replaceable])
        ctx["current_lock"] = {k: ev2[k][0].mean() for k in GOALS + ["u", "met"]}
    if a.validate:
        files = [out / f"plan_rank{i}.json" for i in range(1, o["validate_top"] + 1) if (out / f"plan_rank{i}.json").exists()]
        val = asyncio.run(validate(p, out, files, a.live, log))
        sur = {"no-decision": f"{nodec['goal_1']:.1f} / {nodec['goal_2']:.1f}"}
        for i, j in enumerate(order[: o["validate_top"]], 1):
            sur[f"plan_rank{i}"] = f"{accC['goal_1'][j].mean():.1f} / {accC['goal_2'][j].mean():.1f}"
        for v in val:
            v["sur"] = sur.get(v["name"], "")
        ctx["validation"] = val
    ctx["seconds"] = time.time() - t0
    write_report(out, ctx, final, accC, scen, play, nodec, p, fixed, extra)
    if "current_lock" in ctx:
        c = ctx["current_lock"]
        with (out / "report.md").open("a") as fh:
            fh.write(f"\n## Currently locked (replaceable) plan\nutility {c['u']:.2f}, P(all) {c['met']:.0%}, "
                     f"active {c['goal_1']:.1f}, deposits {c['goal_2']:.1f}\n")
    (out / "scenarios.json").write_text(json.dumps({"scenarios": scen, "observed": obs}, indent=1))
    log(f"done in {time.time() - t0:.0f}s -> {out / 'report.md'}")


if __name__ == "__main__":
    main()
