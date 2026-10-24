"""Decision candidates: targets, action combinations within the menu and budget, and the company message.
Messages are composed from factual snippets (one per menu action), so no candidate says anything the action
does not deliver (red line: no false or misleading statement)."""
from __future__ import annotations

import itertools

from . import config

TARGETS = {
    "everyone": {},
    "paycheck customers": {"groups": ["paycheck customers"]},
    "savers with large balances": {"groups": ["savers with large balances"]},
    "small business owners with a Cobalt card reader": {"groups": ["small business owners with a Cobalt card reader"]},
    "students": {"groups": ["students"]},
    "customers who live paycheck to paycheck": {"where": {"lives_paycheck_to_paycheck": "yes"}},
}
SNIPPET = {
    "savings_boost": "For the next 4 weeks, Cobalt savings earn an extra {lv} on balances up to $50,000.",
    "savings_boost_new_money": "For the next 4 weeks, new money you add to Cobalt savings earns an extra {lv}, on balances up to $50,000.",
    "instant_dispute_credit": "For the next 8 weeks, if you dispute a card charge we credit up to $100 right away.",
    "free_instant_transfers": "Instant transfers to other banks are free for the next {lv}.",
    "debit_cashback": "For 4 weeks your Cobalt debit card earns {lv} cash back.",
    "goodwill_credit": "We are adding a {lv} credit to your account to thank you for your patience.",
    "early_pay": "Paychecks paid into Cobalt can now show up to 2 days early.",
    "zero_interest_advance": "If you need it, you can get a zero-interest advance of up to $500, repaid from your next deposit.",
    "extra_support": "We have added {lv} support staff for the coming weeks.",
    "security_pack": "You can order a free new card at any time, and we now send an alert for every card payment.",
    "offline_limit": "During the system move, card payments work offline up to $250 each (raised from $100).",
}
MIGRATION = ("On Sat Dec 12, 00:00 to Sun Dec 13, about 12:00 Central, we move to a new banking system: your balance "
             "stays visible, but transfers, P2P payments and new cards pause. It may run some hours longer; we will post "
             "updates in the app.")
AFTER = "Thank you for your patience in recent weeks."
CHANNELS = ["push", "email", "in_app"]


def actions_menu(p: dict) -> list[tuple[str, str, str, int]]:
    """(id, label, level, cost) for every menu action-level."""
    out = []
    for a in config.data(p, "menu")["actions"]:
        for lv, cost in a["levels"].items():
            out.append((a["id"], a["label"], lv, cost))
    return out


def combos(p: dict, week: int, budget: int, max_actions: int = 3) -> list[tuple]:
    """All 1-3 action combinations (distinct actions) affordable within budget, valid for the week."""
    opts = [o for o in actions_menu(p) if not (o[0] == "offline_limit" and week > 6)]
    out = []
    for k in range(1, max_actions + 1):
        for c in itertools.combinations(opts, k):
            if len({o[0] for o in c}) < k:
                continue
            cost = sum(o[3] for o in c)
            if cost <= budget:
                out.append(c)
    return out


def message(combo: tuple, week: int) -> str:
    parts = [MIGRATION if week <= 6 else AFTER]
    for aid, label, lv, cost in combo:
        if aid == "early_pay" and week <= 6:
            parts.append("Paychecks paid into Cobalt can now show up to 2 days early, so Friday Dec 11 pay may arrive by Wed Dec 9.")
            continue
        parts.append(SNIPPET[aid].format(lv=lv.replace("+", "").replace(" each", "")))
    msg = " ".join(parts)
    if len(msg) > 600 and week <= 6:
        msg = " ".join(parts[1:])
    return msg[:600]


def decision(combo: tuple, week: int, target: str) -> dict:
    labels = [o[1] for o in combo]
    return {
        "week": week, "target": target,
        "actions": [{"action": o[1], "level": o[2]} for o in combo],
        "message": message(combo, week), "channels": CHANNELS,
        "why": "\n".join([f"Chosen by the optimizer for week {week} ({target}).",
                          f"Actions: {', '.join(labels)}.",
                          f"Cost ${sum(o[3] for o in combo):,} of the $4M budget."]),
    }


def cost(combo: tuple) -> int:
    return sum(o[3] for o in combo)
