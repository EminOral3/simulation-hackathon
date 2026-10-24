"""Persona set: distribution first, story second (docs/talp_db/docs/theory/03_PERSONA_DESIGN.md).

1. Slots and weights come unchanged from persona_design.json (DOE: 2^4 / 2^(4-1) per group, clones).
2. Code samples every schema field consistently with the slot's axis levels (rules below; seed fixed).
3. The LLM writes only the backstory from those fields; a second call checks it against the fields;
   sensitive-word and near-duplicate scans trigger rewrites.
4. The set is frozen in data/personas/<timestamp>_<label>/ and never overwritten.

    python -m code_kit.cobalt.personas build [--live] [--label v1] [--set personas.story_model=experiment]
"""
from __future__ import annotations

import argparse
import asyncio
import json
import random
import re
from datetime import datetime
from pathlib import Path

from . import agent, config, network
from . import params as P
from .llm import LLM

FIRST_NAMES = [  # common US first names, assigned at random, independent of every attribute
    "Maya", "Jordan", "Ethan", "Priya", "Marcus", "Olivia", "Diego", "Hannah", "Tyler", "Aisha", "Ryan", "Sofia",
    "Kevin", "Grace", "Andre", "Emily", "Luis", "Chloe", "Brandon", "Mei", "Caleb", "Jasmine", "Nathan", "Lauren",
    "Omar", "Rachel", "Derek", "Natalie", "Isaac", "Vanessa", "Connor", "Brianna", "Mateo", "Kayla", "Austin",
    "Leah", "Jamal", "Megan", "Trevor", "Alicia", "Noah", "Danielle", "Raj", "Samantha", "Elijah", "Tessa",
    "Victor", "Morgan", "Malik", "Hailey", "Gabriel", "Nina", "Cody", "Erin", "Wes", "Camila", "Darius", "Paige",
    "Adrian", "Kendra", "Sean", "Lucia", "Brett", "Imani", "Felix", "Zoe", "Jared", "Rosa", "Quinn", "Taylor",
    "Devin", "Alexis", "Riley", "Casey", "Avery", "Jamie", "Dana", "Robin"]
LAST_INITIALS = list("ABCDEFGHJKLMNOPRSTVW")
STATES = [("California", 12), ("Texas", 9), ("Florida", 7), ("New York", 6), ("Illinois", 4), ("Pennsylvania", 4),
          ("Ohio", 3), ("Georgia", 3), ("North Carolina", 3), ("Michigan", 3), ("New Jersey", 3), ("Virginia", 3),
          ("Washington", 3), ("Arizona", 2), ("Massachusetts", 2), ("Colorado", 2), ("Tennessee", 2), ("Oregon", 1),
          ("Minnesota", 2), ("Maryland", 2)]  # VARSAYIM: rough population weights
CITIES = {"California": ["Los Angeles", "San Diego", "Sacramento", "Oakland"], "Texas": ["Austin", "Houston", "Dallas", "San Antonio"],
          "Florida": ["Miami", "Tampa", "Orlando"], "New York": ["New York City", "Buffalo"], "Illinois": ["Chicago"],
          "Pennsylvania": ["Philadelphia", "Pittsburgh"], "Ohio": ["Columbus", "Cleveland"], "Georgia": ["Atlanta"],
          "North Carolina": ["Charlotte", "Raleigh"], "Michigan": ["Detroit", "Grand Rapids"], "New Jersey": ["Newark", "Jersey City"],
          "Virginia": ["Richmond", "Arlington"], "Washington": ["Seattle", "Tacoma"], "Arizona": ["Phoenix", "Tucson"],
          "Massachusetts": ["Boston"], "Colorado": ["Denver"], "Tennessee": ["Nashville", "Memphis"], "Oregon": ["Portland"],
          "Minnesota": ["Minneapolis"], "Maryland": ["Baltimore"]}
OCCUPATIONS = {
    "everyday customers": ["office administrator", "retail store manager", "nurse", "software tester", "marketing coordinator",
                           "warehouse supervisor", "dental hygienist", "insurance claims adjuster", "barista and part-time student",
                           "rideshare driver", "elementary school teacher", "HR assistant", "graphic designer"],
    "paycheck customers": ["call center agent", "registered nurse", "logistics coordinator", "pharmacy technician", "IT support specialist",
                           "line cook", "bank teller at a big bank", "postal worker", "medical assistant", "sales associate",
                           "accountant", "electrician apprentice", "federal agency program analyst"],
    "savers with large balances": ["software engineer", "physician resident", "product manager", "attorney", "financial analyst",
                                   "dentist", "management consultant", "data scientist", "small landlord", "pharmacist"],
    "small business owners with a Cobalt card reader": ["food truck owner", "hair salon owner", "coffee cart owner", "florist",
                                                        "mobile car detailer", "personal trainer", "bakery owner", "craft market seller",
                                                        "tattoo studio owner", "phone repair shop owner"],
    "students": ["undergraduate student", "community college student", "graduate student", "nursing student", "engineering student"],
}
NEWS = ["family group chat", "Facebook", "X", "Instagram", "TikTok", "Reddit", "YouTube", "podcasts", "local TV news",
        "cable news", "coworkers", "neighbors"]
SOCIAL = {"Facebook", "X", "Instagram", "TikTok", "Reddit", "YouTube"}
OTHER_BANKS = ["Chase", "Bank of America", "Wells Fargo", "Citi", "a local credit union", "Capital One", "an online savings bank"]
DETAILS = ["iPhone user", "Android user", "drinks oat-milk lattes", "has a dog", "night owl", "morning runner",
           "follows the local football team", "plays video games", "has a cat", "loves cooking shows"]


def pick(rng, items, weights=None):
    return rng.choices(items, weights=weights, k=1)[0]


def yes(rng, p):
    return "yes" if rng.random() < p else "no"


def fill_fields(slot: dict, rng: random.Random, name: str) -> dict:
    """Sample all schema fields consistently with the slot's axis levels. Rules = VARSAYIM, listed in TEAM_DOC."""
    g, L = slot["group"], slot["design_levels"]
    fragile = L.get("fragility") in ("paycheck to paycheck", "thin cash flow")
    info = L.get("info_style", pick(rng, ["believes rumors, follows others", "checks facts"], [0.3, 0.7]))
    vocal = L.get("voice", "").startswith("vocal")
    f: dict = {"id": slot["id"], "group": g, "name": name, "design_levels": L,
               "weight_customers": slot["weight_customers"], "clone_of": slot["clone_of"]}
    state = pick(rng, [s for s, _ in STATES], [w for _, w in STATES])
    f["location"] = f"{pick(rng, ['the city of', 'a suburb of'], [0.55, 0.45])} {pick(rng, CITIES[state])}, {state}"
    f["age"] = rng.randint(19, 24) if g == "students" else int(min(40, max(22, rng.gauss(31, 5))))
    f["occupation"] = pick(rng, OCCUPATIONS[g])
    hh = ["lives alone", "lives with a partner", "lives with roommates", "married, one young child",
          "single parent of one child", "lives with parents"]
    hw = ([0.1, 0.05, 0.5, 0, 0, 0.35] if g == "students" else
          [0.25, 0.25, 0.2, 0.12, 0.06, 0.12] if f["age"] < 30 else [0.25, 0.3, 0.05, 0.28, 0.1, 0.02])
    f["household"] = pick(rng, hh, hw)
    f["customer_since"] = str(rng.randint(2019, 2025))
    f["detail"] = pick(rng, DETAILS)

    # money and relationship
    if g == "savers with large balances":
        over = L["fdic_exposure"].startswith("over")
        f["balance_band"] = pick(rng, ["250k+", "50-250k"], [0.6, 0.4]) if over else pick(rng, ["10-50k", "50-250k"], [0.75, 0.25])
        f["knows_fdic_limit"] = pick(rng, ["no", "unsure"]) if over and f["balance_band"] != "250k+" else (
            pick(rng, ["yes", "unsure"], [0.4, 0.6]) if over else "yes")
        f["moves_money_for_rate"] = "yes" if L["rate_seeking"].startswith("moves") else "no"
        f["household_income_band"] = pick(rng, ["75-150k", "150k+"], [0.5, 0.5])
        f["lives_paycheck_to_paycheck"] = "no"
        f["cobalt_role"] = pick(rng, ["main bank", "second bank"], [0.4, 0.6])
        f["paycheck_into_cobalt"] = yes(rng, 0.25)
    else:
        f["lives_paycheck_to_paycheck"] = "yes" if fragile else ("no" if "fragility" in L else yes(rng, 0.4))
        p2p = f["lives_paycheck_to_paycheck"] == "yes"
        f["balance_band"] = pick(rng, ["<1k", "1-10k"], [0.6, 0.4]) if p2p else pick(rng, ["1-10k", "10-50k"], [0.75, 0.25])
        if g == "students":
            f["balance_band"] = pick(rng, ["<1k", "1-10k"], [0.75, 0.25])
        f["household_income_band"] = (pick(rng, ["<35k", "35-75k"], [0.5, 0.5]) if p2p else pick(rng, ["35-75k", "75-150k"], [0.6, 0.4]))
        if g == "students":
            f["household_income_band"] = "<35k"
        f["moves_money_for_rate"] = yes(rng, 0.25)
        f["knows_fdic_limit"] = pick(rng, ["yes", "no", "unsure"], [0.4, 0.3, 0.3])
        role = L.get("bank_role")
        f["cobalt_role"] = ("main bank" if role == "Cobalt is main bank" else "second bank" if role
                            else pick(rng, ["main bank", "second bank"], [0.5, 0.5]))
        f["paycheck_into_cobalt"] = "yes" if g == "paycheck customers" else (
            "no" if g == "students" else yes(rng, 0.15 if f["cobalt_role"] == "main bank" else 0.03))
    if g == "paycheck customers":
        f["cobalt_role"] = "main bank" if L["bank_role"] == "Cobalt is main bank" else "second bank"
    f["n_banks"] = "1" if (f["cobalt_role"] == "main bank" and rng.random() < 0.15) else pick(rng, ["2", "3+"], [0.7, 0.3])
    f["other_bank"] = "none" if f["n_banks"] == "1" else pick(rng, OTHER_BANKS)
    f["payday"] = (pick(rng, ["every other Friday (next one: Friday, December 11)", "15th and last day of the month"], [0.6, 0.4])
                   if f["paycheck_into_cobalt"] == "yes" else "not paid into Cobalt")
    f["autopays"] = str(rng.randint(2, 6) if f["cobalt_role"] == "main bank" else rng.randint(0, 2))

    # risk and trust
    f["fraud_or_phishing_victim"] = ("yes" if L.get("fraud_history", "").startswith("past") else
                                     "no" if "fraud_history" in L else yes(rng, 0.21))  # SHED 2024 anchor [KISMEN]
    f["sms_from_bank_reaction"] = pick(rng, ["clicks links", "checks in app first", "ignores"],
                                       [0.15, 0.55, 0.30] if info.startswith("checks") else [0.35, 0.40, 0.25])
    f["financial_literacy"] = (pick(rng, ["medium", "high"], [0.4, 0.6]) if g == "savers with large balances"
                               else pick(rng, ["low", "medium", "high"], [0.3, 0.5, 0.2]))
    f["rumor_style"] = "believe and pass them on" if info.startswith("believes") else "check before believing"

    # behaviour and channels
    if g == "students":
        f["uses_p2p"] = "daily" if L["p2p_dependence"].startswith("relies") else "rarely"
        f["who_pays"] = "parents send money" if L["who_pays"].startswith("parents") else "my own part-time income"
    else:
        f["uses_p2p"] = pick(rng, ["daily", "weekly", "rarely"], [0.25, 0.45, 0.30])
    f["checks_app_daily"] = yes(rng, 0.6 if f["cobalt_role"] == "main bank" else 0.3)
    f["preferred_support_channel"] = pick(rng, ["app chat", "phone"], [0.65, 0.35])
    k = rng.randint(1, 3)
    pool = NEWS if f["age"] > 26 else NEWS[:7]
    f["news_sources"] = rng.sample(pool, k)
    f["social_channels"] = [s for s in f["news_sources"] if s in SOCIAL]
    f["voice_propensity"] = ("vocal: I complain, post and write reviews" if vocal else "quiet: I rarely complain in public")
    f["opinion_role"] = "lead (people ask me)" if rng.random() < (0.4 if vocal else 0.18) else "follow (I ask others)"
    f["patience"] = pick(rng, ["low", "medium", "high"], [0.3, 0.45, 0.25])
    f["forgiveness"] = pick(rng, ["low", "medium", "high"], [0.25, 0.5, 0.25])
    if g == "small business owners with a Cobalt card reader":
        big = L["ticket_size"].startswith("typical sale over")
        f["business"] = (f"{f['occupation']}; typical card sale {'about $120-300' if big else 'about $15-60'}; "
                         f"busiest on weekends; {'thin cash flow' if fragile else 'some cash cushion'}")
    sc = []
    if f["paycheck_into_cobalt"] == "yes":
        sc.append("my paycheck is deposited here")
    if int(f["autopays"]) >= 2:
        sc.append(f"{f['autopays']} bills are on autopay from here")
    if g == "small business owners with a Cobalt card reader":
        sc.append("my card reader pays out into Cobalt")
    if f["n_banks"] == "1":
        sc.append("I have no other bank account yet")
    f["switch_cost"] = ("; ".join(sc) + ".") if sc else "not much: I already have another bank and nothing important runs through Cobalt."
    return f


def fields_text(f: dict) -> str:
    return agent.facts(f) + f"\n- Name: {f['name']}\n- Customer group: {f['group']}"


SENSITIVE = re.compile(r"\b(black|white|latino|latina|hispanic|asian|christian|muslim|jewish|church|mosque|religio\w*|"
                       r"disab\w*|diabet\w*|cancer|depress\w*|democrat\w*|republican\w*|immigra\w*|undocumented|visa)\b", re.I)


def trigrams(text: str) -> set:
    w = re.findall(r"[a-z']+", text.lower())
    return {" ".join(w[i:i + 3]) for i in range(len(w) - 2)}


def jaccard(a: set, b: set) -> float:
    return len(a & b) / max(1, len(a | b))


async def write_stories(p: dict, llm: LLM, people: list[dict], model: str) -> tuple[list[dict], list[dict]]:
    calls, report = [], []
    seed = p["personas"]["story_seed"]

    async def one(f, attempt):
        ft = fields_text(f)
        c = await llm.ask(call_id=f"gen-story-{f['id']}-a{attempt}", persona=f["id"], week=0, kind="story",
                          prompt=agent.story_prompt(ft), seed=seed + attempt, schema=agent.Story, mock=agent.mock_story, model=model)
        story = (c.parsed or {}).get("story", "").strip()
        k = await llm.ask(call_id=f"gen-check-{f['id']}-a{attempt}", persona=f["id"], week=0, kind="story_check",
                          prompt=agent.check_prompt(ft, story), seed=seed, schema=agent.StoryCheck, mock=agent.mock_check, model=model)
        calls.extend([c, k])
        chk = k.parsed or {"contradiction": True, "fields": ["unparsed"], "stereotype_or_sensitive": False}
        return story, chk

    async def build(f):
        for attempt in range(p["personas"]["max_rewrites"] + 1):
            story, chk = await one(f, attempt)
            bad_words = SENSITIVE.findall(story)
            ok = story and not chk["contradiction"] and not chk["stereotype_or_sensitive"] and not bad_words
            if ok or attempt == p["personas"]["max_rewrites"]:
                f["narrative"] = story
                report.append({"id": f["id"], "attempts": attempt + 1, "ok": bool(ok), "check": chk, "sensitive_words": bad_words})
                return

    await asyncio.gather(*(build(f) for f in people))
    # near-duplicate scan (clones share axis levels): rewrite the later one once
    grams = {f["id"]: trigrams(f["narrative"]) for f in people}
    redo = []
    for i, a in enumerate(people):
        for b in people[i + 1:]:
            if jaccard(grams[a["id"]], grams[b["id"]]) > p["personas"]["similarity_max"]:
                redo.append(b)
    for f in {x["id"]: x for x in redo}.values():
        story, chk = await one(f, 9)
        f["narrative"] = story
        report.append({"id": f["id"], "rewritten_for_similarity": True, "check": chk})
    return calls, report


def build_fields(p: dict) -> list[dict]:
    slots = config.data(p, "design")["slots"]
    priors = config.data(p, "priors")["groups"]
    rng = random.Random(p["personas"]["sample_seed"])
    names = rng.sample([f"{n} {rng.choice(LAST_INITIALS)}." for n in FIRST_NAMES], len(slots))
    people = []
    for slot, name in zip(slots, names):
        f = fill_fields(slot, random.Random(f"{p['personas']['sample_seed']}|{slot['id']}"), name)
        f["active_share"] = priors[slot["group"]]["active_share"]
        f["w_active"] = round(slot["weight_customers"] * f["active_share"], 3)
        people.append(f)
    return people


async def build_set(p: dict, live: bool, label: str) -> Path:
    model = P.model_id(p, p["personas"]["story_model"])
    llm = LLM(p, live=live, model=model)
    people = build_fields(p)
    calls, report = await write_stories(p, llm, people, model)
    ties = network.build(p, people)
    for f in people:
        f["ties"] = ties[f["id"]]
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = P.path(p, "personas_dir") / f"{ts}_{label}{'' if live else '_mock'}"
    out.mkdir(parents=True, exist_ok=False)
    with (out / "personas.jsonl").open("w") as fh:
        for f in people:
            fh.write(json.dumps(f, ensure_ascii=False) + "\n")
    with (out / "gen_calls.jsonl").open("w") as fh:
        for c in calls:
            fh.write(json.dumps(c.record(), ensure_ascii=False) + "\n")
    (out / "quality.json").write_text(json.dumps({"model": llm.model_label, "n": len(people),
                                                  "ok": sum(r.get("ok", True) for r in report), "report": report}, indent=1))
    (out / "network.json").write_text(json.dumps(ties, indent=1))
    print(f"persona set -> {out}  ({len(people)} personas, {llm.stats.calls} calls, failed {llm.stats.failed})")
    return out


def resolve_set(p: dict, name: str | None = None) -> Path:
    base = P.path(p, "personas_dir")
    name = name or p["personas"]["persona_set"]
    if name != "latest":
        return base / name
    sets = sorted(d for d in base.iterdir() if (d / "personas.jsonl").exists()) if base.exists() else []
    if not sets:
        raise FileNotFoundError(f"no persona set in {base}; run: python -m code_kit.cobalt.personas build")
    live = [d for d in sets if not d.name.endswith("_mock")]
    return (live or sets)[-1]


def load_set(p: dict, name: str | None = None) -> tuple[Path, list[dict], list[dict]]:
    d = resolve_set(p, name)
    people = [json.loads(l) for l in (d / "personas.jsonl").read_text().splitlines() if l.strip()]
    gen = [json.loads(l) for l in (d / "gen_calls.jsonl").read_text().splitlines() if l.strip()] if (d / "gen_calls.jsonl").exists() else []
    return d, people, gen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "show"])
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--label", default="v1")
    ap.add_argument("--params", action="append", default=[])
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--id")
    a = ap.parse_args()
    p = P.load(a.params, a.set)
    if a.cmd == "build":
        asyncio.run(build_set(p, a.live, a.label))
    else:
        d, people, _ = load_set(p)
        for f in people:
            if not a.id or f["id"] == a.id:
                print(f"{f['id']} {f['name']} | {f['group']} | w={f['w_active']} | {f['design_levels']}\n  {f.get('narrative', '')}\n")


if __name__ == "__main__":
    main()
