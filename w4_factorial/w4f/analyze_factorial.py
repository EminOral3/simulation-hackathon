"""2^4 factorial effects + Lenth PSE. Usage: python analyze_factorial.py runs_exp factorial_design.json"""
import json, sys, os, itertools, statistics as st
root, D = sys.argv[1], json.load(open(sys.argv[2]))
F = ["A_week", "B_boost", "C_support", "D_message"]
goals = ["goal_1", "goal_2", "goal_3", "goal_3b"]
rows = []
for run, lv in D["runs"].items():
    vals = []
    for s in (1, 2, 3):
        p = os.path.join(root, f"{run}__REAL__s{s}", "metrics.json")
        if os.path.exists(p): vals.append(json.load(open(p)))
    if vals: rows.append((lv, {g: st.mean(v[g] for v in vals) for g in goals}))
print(f"runs found: {len(rows)}/16")
if len(rows) < 16: print("incomplete design: effects below use available runs (aliasing possible)")
terms = [c for k in range(1, 5) for c in itertools.combinations(F, k)]
for g in goals:
    eff = {}
    for t in terms:
        plus = [y[g] for lv, y in rows if all(True for _ in [0]) and eval("*".join(str(lv[f]) for f in t)) == 1]
        minus = [y[g] for lv, y in rows if eval("*".join(str(lv[f]) for f in t)) == -1]
        if plus and minus: eff["x".join(f.split("_")[0] for f in t)] = st.mean(plus) - st.mean(minus)
    a = [abs(v) for v in eff.values()]
    if not a or max(a) == 0:
        print(f"\n== {g}: no variation =="); continue
    s0 = 1.5 * st.median(a); trim = [x for x in a if x < 2.5 * s0] or a; pse = 1.5 * st.median(trim)
    me = 2.57 * pse  # Lenth margin of error, m=15 contrasts, ~95%
    print(f"\n== {g}  (Lenth PSE={pse:.3f}, ME={me:.3f}; |effect|>ME = real) ==")
    for k, v in sorted(eff.items(), key=lambda kv: -abs(kv[1])):
        print(f"{k:12s} {v:+8.3f} {'*' if abs(v) > me else ''}")
