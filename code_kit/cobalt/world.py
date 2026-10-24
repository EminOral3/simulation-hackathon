"""What each persona sees, hears and experiences in a week (deterministic, seeded). The LLM decides what
they do about it. All randomness is keyed by (seed, week, persona, purpose), so plan_k and nodecision_k
share the same shocks (common random numbers) and differ only through the decisions."""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from . import config, crisis

BAU_EMAIL = ("Email from Cobalt Bank (December 5): \"On Saturday, December 12 at 00:00 until Sunday, December 13 at "
             "12:00 Central Time we move to a new core banking system. During this time the app is read-only: you can "
             "see your balances, but transfers, peer-to-peer payments and new cards are not available. Card payments "
             "work offline up to $100 per payment.\"")
OVERRUN_TEXT = {
    "on time": "The app came back on Sunday around noon, as announced.",
    "a few hours late": "The app came back a few hours later than the announced Sunday noon.",
    "into Monday": "Transfers only worked again on Monday morning, almost a day later than announced.",
}
HOLDING_MIGRATION = ("Cobalt Bank on social media: \"Our system upgrade took longer than planned. Everything is working "
                     "again. We are sorry for the trouble.\"")
HOLDING_GENERIC = ("Cobalt Bank on social media: \"We are aware of reports about this and are looking into it. We will "
                   "share updates here.\"")
RIVALS = ["online bank Brightline", "online bank Northstar Savings", "fintech Pocketwise"]  # fictional


@dataclass
class Ctx:
    p: dict
    seed: int
    decisions: list
    filters: dict
    announcements: list
    overrun: str = "on time"
    received: dict = field(default_factory=dict)      # (persona, decision) -> week received
    bau_email_seen: set = field(default_factory=set)

    def rng(self, *key) -> random.Random:
        return random.Random("|".join(map(str, (self.seed,) + key)))


def draw_overrun(p: dict, seed: int, announcements: list | None = None) -> str:
    """The migration outcome: known from the dashboard once announced (same in every run), else drawn per seed."""
    for a in announcements or []:
        if a.get("known_outcome"):
            return a["known_outcome"]
    rng = random.Random(f"{seed}|overrun")
    return rng.choices(p["world"]["overrun_levels"], weights=p["world"]["overrun_probs"], k=1)[0]


def _reach(ctx: Ctx, persona: dict, channels: list[str], rng: random.Random) -> list[str]:
    w = ctx.p["world"]
    got = []
    for ch in channels:
        c = ch.lower()
        if "push" in c:
            pr = w["reach_push"]
        elif "email" in c:
            pr = w["reach_email"]
        elif "app" in c:
            pr = w["reach_in_app_daily"] if persona.get("checks_app_daily") == "yes" else w["reach_in_app_other"]
        elif "text" in c or "sms" in c:
            pr = w["reach_sms"]
        elif "video" in c or "ceo" in c:
            pr = w["reach_ceo_video"]
        else:
            pr = 0.3
        if rng.random() < pr:
            got.append(ch)
    return got


def _news_exposure(ctx: Ctx, persona: dict, severity: str, affected: bool) -> float:
    w = ctx.p["world"]
    pr = w["news_exposure_base"] + w["news_exposure_per_source"] * len(persona.get("news_sources", []))
    if severity == "high":
        pr += w["news_exposure_high_severity"]
    if affected:
        pr += 0.25
    return min(0.95, pr)


def week_inputs(ctx: Ctx, persona: dict, state: dict, week: int) -> tuple[list[str], bool, dict, bool]:
    """(lines the persona sees this week, whether anything new happened, structured features for the surrogate,
    whether something salient happened: news, a new company message, a personal experience; not a rival ad alone
    or an offer that is merely still running)."""
    pid, p, seen, new = persona["id"], ctx.p, [], False
    sal = False
    fx: dict[str, float] = {}
    eff = config.active_effects(p, ctx.decisions, ctx.filters, persona, week)

    # company decision messages: word for word, only to the target, from their week on
    for i, d in enumerate(ctx.decisions, 1):
        if week < d["week"] or not config.in_target(persona, ctx.filters.get(str(i))):
            continue
        key = (pid, i)
        if key not in ctx.received:
            got = _reach(ctx, persona, d["channels"], ctx.rng(week, pid, "msg", i))
            if got:
                ctx.received[key] = week
                seen.append(f"Message from Cobalt Bank this week (via {', '.join(got)}): \"{d['message']}\"")
                new = True
                sal = True
                fx["msg_new"] = 1.0
                if "Dec 12" in d["message"] or "new banking system" in d["message"]:
                    fx["msg_mig"] = 1.0
        else:
            b = p["budget"]
            if b["lean_prompts"] and week - ctx.received[key] >= b["inbox_full_weeks"]:
                head = d["message"][: b["inbox_reminder_chars"]].rsplit(" ", 1)[0]
                seen.append(f"Cobalt's message from week {ctx.received[key]} is still in your inbox; it began: \"{head} ...\"")
            else:
                seen.append(f"Message from Cobalt Bank you received in week {ctx.received[key]} (still in your inbox): "
                            f"\"{d['message']}\"")
            fx["msg_inbox"] = 1.0

    # business as usual: migration email 7 days before (week 5), in-app banner in week 6 for those who missed it
    if week == 5 and ctx.rng(week, pid, "bau").random() < p["world"]["reach_email"] + 0.15:
        ctx.bau_email_seen.add(pid)
        seen.append(BAU_EMAIL)
        new = True
        sal = True
        fx["bau_email"] = 1.0
    if week == 6 and pid not in ctx.bau_email_seen:
        seen.append("In-app banner on Friday: \"This weekend the app will be read-only while we move to a new system.\"")

    # the known crisis: the switch happens at the end of week 6
    if week == 6:
        new = True
        sal = True
        fx["migration"] = 1.0
        fx["overrun"] = float(p["world"]["overrun_levels"].index(ctx.overrun))
        seen.append("Saturday December 12 00:00 to Sunday December 13 (Central Time): the Cobalt app was read-only "
                    "(balances visible, no transfers, no peer-to-peer payments, no new cards). " +
                    next((a["text"] for a in ctx.announcements if a.get("known_outcome")), OVERRUN_TEXT[ctx.overrun]))
        r = ctx.rng(week, pid, "migration")
        cap = 250 if "offline_limit" in eff else 100
        if persona.get("uses_p2p") in ("daily", "weekly") and r.random() < p["world"]["p2p_fail_prob"]:
            seen.append("On Saturday you tried to send money with a peer-to-peer app from your Cobalt account and it failed.")
            fx["p2p_fail"] = 1.0
        if r.random() < p["world"]["big_purchase_prob"]:
            amount = r.choice([85, 140, 180, 240, 320])
            if amount > cap:
                seen.append(f"On Saturday a ${amount} card payment was declined because of the ${cap} offline limit.")
                fx["card_declined"] = 1.0
            else:
                seen.append(f"On Saturday a ${amount} card payment went through offline.")
        if "business" in persona:
            if "120-300" in persona["business"]:
                seen.append(f"At your card reader on Saturday, customers' payments over ${cap} were declined; "
                            f"{'a few' if cap == 250 else 'several'} sales were lost or paid in cash.")
                fx["biz_declined"] = 0.5 if cap == 250 else 1.0
            else:
                seen.append("Your card reader kept working offline for your small sales over the weekend.")
        if "Friday" in persona.get("payday", ""):
            if "early_pay" in eff:
                seen.append("Thanks to early pay, your paycheck showed up on Wednesday, December 9, before the switch.")
                fx["early_pay_helped"] = 1.0
            else:
                seen.append("Your paycheck arrived on Friday, December 11, the day before the switch; you could not "
                            "move it or pay anyone from it over the weekend.")
                fx["paycheck_trapped"] = 1.0
    if week == 7 and ctx.overrun != "on time" and p["world"]["holding_statement"] and persona.get("social_channels"):
        seen.append(HOLDING_MIGRATION)
        fx["holding"] = 1.0

    # announcements (surprises and their updates): verbatim news to exposed personas, plus world-feed items
    for a in ctx.announcements:
        if a["week"] != week or not a.get("surprise", True):
            continue
        rd = crisis.reading(p, a)
        affected = any(crisis.affects(p, x, persona) for x in rd["archetypes"])
        r = ctx.rng(week, pid, "news", a["text"][:40])
        if r.random() < _news_exposure(ctx, persona, rd["severity"], affected):
            seen.append(f"News: {a['text']}")
            sev = crisis.SEVERITY.get(rd["severity"], 1.0)
            for x in rd["archetypes"][:1]:
                k = f"sx_{crisis.cls_of(x)}"
                fx[k] = max(fx.get(k, 0.0), sev)
            if affected:
                fx["sx_affected"] = 1.0
            for x in rd["archetypes"][:1]:
                seen.extend(crisis.world_items(p, x, r, k=1 if not affected else 2, real=a.get("source") == "dashboard"))
            if p["world"]["holding_statement"] and persona.get("social_channels"):
                seen.append(HOLDING_GENERIC)
            new = True
            sal = True

    # personal experience of a surprise: by its known incidence (affected_share) or an explicit match, not by exposure
    for a in ctx.announcements:
        ev = a.get("personal_event")
        if a["week"] != week or not a.get("surprise", True) or not ev:
            continue
        m = a.get("personal_match") or {}
        if m:
            hit = all(v.lower() in str(persona.get(k, "")).lower() for k, v in m.items())
        else:
            hit = ctx.rng(week, pid, "personal", a["text"][:40]).random() < a.get("affected_share", p["world"]["personal_event_share"])
        if hit:
            seen.append(ev)
            fx["sx_affected"] = 1.0
            new = True
            sal = True

    # rivals know the migration date
    if week in p["world"]["rival_campaign_weeks"]:
        r = ctx.rng(week, pid, "rival")
        pr = p["world"]["rival_exposure"] + (0.3 if persona.get("moves_money_for_rate") == "yes" else 0)
        if r.random() < pr:
            rival = r.choice(RIVALS)
            line = f"Ad from {rival}: savings rate {p['world']['rival_rate_gap']} points above Cobalt's, \"switch in 5 minutes\"."
            seen.append(line)
            new = True
            fx["rival_ad"] = 1.0

    # decision effects the persona can feel
    first = lambda k: eff[k]["since"] == week
    for k in eff:
        fx[f"eff_{k}"] = 1.0
    if "savings_boost" in eff or "savings_boost_new_money" in eff:
        k = "savings_boost" if "savings_boost" in eff else "savings_boost_new_money"
        scope = "on balances up to $50,000" if k == "savings_boost" else "on new money you add, up to $50,000"
        seen.append(f"Cobalt savings boost is on: {eff[k]['level']} {scope} for 4 weeks.")
        new |= first(k)
    if "debit_cashback" in eff:
        seen.append(f"Your Cobalt debit card gives cash back this month ({eff['debit_cashback']['level']}).")
        new |= first("debit_cashback")
    if "goodwill_credit" in eff and first("goodwill_credit"):
        seen.append(f"You received a {eff['goodwill_credit']['level'].replace(' each', '')} goodwill credit from Cobalt.")
        new = True
        sal = True
    if "zero_interest_advance" in eff and persona.get("lives_paycheck_to_paycheck") == "yes":
        seen.append("Cobalt offers you a zero-interest advance of up to $500, repaid from your next deposit.")
        new |= first("zero_interest_advance")
    if "free_instant_transfers" in eff:
        seen.append("Instant transfers from Cobalt to other banks are free right now (normally 1.5%, up to $15).")
    if "instant_dispute_credit" in eff and first("instant_dispute_credit"):
        seen.append("Cobalt now credits disputed card charges at once, up to $100.")
    if "security_pack" in eff and first("security_pack"):
        seen.append("Cobalt: free new card on request, and an alert for every card payment.")
        new = True
        sal = True
    if "early_pay" in eff and persona.get("paycheck_into_cobalt") == "yes" and first("early_pay"):
        seen.append("Early pay is on: your paycheck now shows up to 2 days early.")
        new = True
        sal = True

    # last week's support contact and open disputes
    sup = state.get("support_last")
    if sup and sup["week"] == week - 1:
        seen.append(f"You contacted Cobalt support last week ({persona['preferred_support_channel']}): you waited "
                    f"about {sup['wait_min']:.0f} minutes and your issue was {'resolved' if sup['resolved'] else 'not resolved'}.")
        new = True
        sal = True
        fx["sup_wait"] = float(sup["wait_min"])
        fx["sup_unresolved"] = 0.0 if sup["resolved"] else 1.0
    for dw in list(state.get("disputes", [])):
        if "instant_dispute_credit" in eff or week - dw >= 2:
            seen.append(f"Cobalt gave you a credit for the card charge you disputed in week {dw}.")
            state["disputes"].remove(dw)
            new = True
            sal = True
            fx["dispute_credited"] = 1.0
    return seen, new, fx, sal
