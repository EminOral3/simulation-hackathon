"""32 K2 variants around F08 (week 6, everyone; K1 = A1 fixed): levels x messages x channels."""
import copy, json, sys
sys.path.insert(0, ".")
from code_kit.cobalt import params as P, config
p = P.load()
base = json.load(open("code_kit/cobalt/params/decisions/w4f/w4f_F08.json"))
K1, FILT = base["decisions"][0], base["filters"]
BOOST = "Savings rate boost for 4 weeks, balances up to $50,000"
NEWM = "Savings boost on new money only, 4 weeks"
SUP = "Extra support staff for 4 weeks"
OFF = "Offline card limit during migration $100 -> $250"
CASH = "Debit card cash back for 4 weeks"

def acts(boost=None, newm=None, sup=None, off=False, cash=None):
    a = []
    if boost: a.append({"action": BOOST, "level": f"+{boost} points"})
    if newm: a.append({"action": NEWM, "level": f"+{newm} points"})
    if sup: a.append({"action": SUP, "level": f"+{sup}"})
    if off: a.append({"action": OFF, "level": "on"})
    if cash: a.append({"action": CASH, "level": cash})
    return a

def facts(a):
    f = {}
    for x in a:
        if x["action"] == BOOST: f["rate"] = f"For the next 4 weeks we add {x['level'].strip('+').replace(' points','')} percentage points to savings rates on balances up to $50,000; then the standard rate returns."
        if x["action"] == NEWM: f["rate"] = f"For the next 4 weeks, new money you add to savings earns an extra {x['level'].strip('+').replace(' points','')} percentage points, on balances up to $50,000; then the standard rate returns."
        if x["action"] == SUP: f["sup"] = f"We have added {x['level'].strip('+')} more support staff."
        if x["action"] == OFF: f["off"] = "During the upgrade, cards work offline up to $250 per payment (normally $100)."
        if x["action"] == CASH: f["cash"] = f"For 4 weeks your debit card earns {x['level'].replace(', up to', ' cash back, up to')}."
    return f

CHARGES = ("Update on the small charges: our card processor confirmed a fault that charged some payments twice on Nov 16-17, "
           "and some cards saw fraud test charges. Cobalt's systems were not breached; disputed charges are credited at once.")
UPG = "Our upgrade runs Sat Dec 12, 12:00 AM to about noon Sun Dec 13 (CT), maybe longer; balances stay visible, transfers and P2P pause."
FDIC = "Deposits stay FDIC-insured up to the standard limit."

def message(style, a):
    f = facts(a)
    extra = " ".join(f[k] for k in ("off", "cash") if k in f)
    cap = "offline up to $250" if "off" in f else "offline up to $100"
    if style == "full":
        parts = [CHARGES, UPG, f.get("off", ""), f.get("rate", ""), f.get("cash", ""), f.get("sup", ""), FDIC]
    elif style == "short":
        parts = ["Thank you for banking with us.", f.get("rate", ""), f.get("cash", ""), f.get("sup", ""), FDIC]
    elif style == "migration":
        parts = ["This weekend, Sat Dec 12 12:00 AM to about noon Sun Dec 13 (CT), we move to a new system; it may run some hours longer and we will post updates in the app.",
                 f"Your balance stays visible. Transfers, P2P payments and new cards pause; cards work {cap} per payment.",
                 "If you need to move money or pay someone, do it before Friday night.", f.get("rate", ""), f.get("cash", ""), f.get("sup", "")]
    elif style == "security":
        parts = ["The small card charges came from a processor fault on Nov 16-17 and fraud test charges on cards stolen elsewhere; Cobalt's systems were not breached.",
                 "Dispute any charge you do not recognize; we credit it at once. We never text links or ask for codes.",
                 UPG, f.get("off", ""), f.get("rate", ""), f.get("cash", ""), f.get("sup", "")]
    elif style == "rate":
        parts = [f.get("rate", ""), f.get("cash", ""), FDIC, UPG, f.get("off", ""), f.get("sup", "")]
    elif style == "apology":
        parts = ["We are sorry for the worry the small card charges caused. The cause is confirmed: a processor fault and fraud test charges; our systems were not breached.",
                 "Our upgrade on Dec 12-13 pauses transfers and P2P for about 36 hours, maybe longer; balances stay visible.",
                 f.get("off", ""), f.get("rate", ""), f.get("cash", ""), f.get("sup", "")]
    msg = " ".join(x for x in parts if x)
    for cut in (" (normally $100)", " " + FDIC, " Your balance stays visible."):
        if len(msg) > 600:
            msg = msg.replace(cut, "")
    if len(msg) > 600:
        msg = msg.replace("; then the standard rate returns.", ", ending after 4 weeks.")
    assert len(msg) <= 600, (style, len(msg), msg)
    return msg

CH = {"std": ["push", "email", "in_app"], "sms": ["push", "email", "in_app", "text_message_all"],
      "ceo": ["push", "email", "in_app", "ceo_video"]}
L = {  # level sets (all week 6, everyone)
    "L01": acts(boost="0.5", sup=150),            # = F08
    "L02": acts(boost="0.25", sup=150),
    "L03": acts(boost="0.75", sup=50),
    "L04": acts(boost="0.5", sup=50),
    "L05": acts(boost="0.5", sup=150, off=True),
    "L06": acts(boost="0.75", sup=50, off=True),
    "L07": acts(boost="0.5", sup=50, off=True),
    "L08": acts(boost="0.25", sup=150, off=True),
    "L09": acts(newm="0.75", sup=150, off=True),
    "L10": acts(newm="0.5", sup=150, off=True),
    "L11": acts(boost="0.25", sup=150, cash="1%, up to $5"),
    "L12": acts(boost="0.25", sup=50, cash="1%, up to $5"),
    "L13": acts(boost="0.75", off=True),
    "L14": acts(newm="0.75", sup=50, cash="1%, up to $5"),
}
designs = [(k, "full", "std") for k in L]                                      # 14 level variants
designs += [("L01", s, "std") for s in ("short", "migration", "security", "rate", "apology")]   # 5 messages on F08
designs += [("L01", "full", "sms"), ("L01", "full", "ceo"), ("L01", "migration", "sms")]       # 3 channels
designs += [("L05", s, "std") for s in ("short", "migration", "security", "rate", "apology")]   # 5 on F08+offline
designs += [("L03", s, "std") for s in ("migration", "rate")]                                  # 2 on boost .75
designs += [("L06", "migration", "std"), ("L09", "rate", "std"), ("L13", "migration", "std")]  # 3
assert len(designs) == 32, len(designs)
rows = []
for i, (lk, style, ch) in enumerate(designs, 1):
    k2 = {"week": 6, "target": "everyone", "actions": copy.deepcopy(L[lk]), "message": message(style, L[lk]), "channels": CH[ch]}
    cost = config.decision_cost(p, k2)
    k2["why"] = "\n".join([f"Tuning run T{i:02d} around F08: level set {lk}, message '{style}', channels '{ch}'.",
                           "Week 6 lands before the upgrade; the 4-week boost ends Jan 3, before the board measures.",
                           f"Costs ${cost/1e6:.2f}M (total ${(cost + config.decision_cost(p, K1))/1e6:.2f}M of $4M); statements are confirmed facts."])
    plan = [K1, k2]
    tot = config.budget_check(p, plan)["total_usd"]
    d = {"decisions": plan, "filters": FILT, "design": {"code": f"T{i:02d}", "levels": lk, "message": style, "channels": ch}}
    for path in (f"w4_tuning/decisions/dec_w4t_T{i:02d}.json", f"code_kit/cobalt/params/decisions/w4t/w4t_T{i:02d}.json"):
        json.dump(d, open(path, "w"), indent=1, ensure_ascii=False)
    rows.append((f"T{i:02d}", lk, style, ch, tot, len(k2["message"]), " + ".join(f"{a['action'].split(',')[0].split(' for ')[0]} {a['level']}" for a in k2["actions"])))
with open("w4_tuning/README_w4t.md", "w") as fh:
    fh.write("# F08 ince ayarı: 32 K2 varyantı (6. hafta, herkese; K1 = A1)\n\n| kod | seviye seti | mesaj | kanal | toplam | karakter | aksiyonlar |\n|---|---|---|---|---|---|---|\n")
    for r in rows:
        fh.write(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | ${r[4]/1e6:.2f}M | {r[5]} | {r[6]} |\n")
for r in rows: print(*r[:6])
names = [r[0] for r in rows]
for seed in (1, 2):
    T = [f'# F08 tuning seed {seed}', f'name = "w4t_s{seed}"', f'seeds = [{seed}]']
    for n in names: T += ['[[variant]]', f'label = "{n}"', f'decisions = "w4t/w4t_{n}.json"']
    open(f"code_kit/cobalt/params/experiments/w4t_s{seed}.toml", "w").write("\n".join(T) + "\n")
