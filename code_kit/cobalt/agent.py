"""Persona prompts and output schemas: backstory, consistency check, round A (notice and talk),
round B (decide), check-in probe, live Q&A. Mock generators let the whole pipeline run offline."""
from __future__ import annotations

import random
import re
from typing import Literal

from pydantic import BaseModel, Field

STATUS = Literal["main bank", "second bank", "dormant", "left"]
MONEY = Literal["kept", "moved some", "moved most"]
ACTIONS = ["complained in app", "called support", "posted review", "filed CFPB complaint", "posted on social media",
           "told friends", "asked a friend", "moved money", "added money", "disputed a card charge",
           "used another bank more", "switched to a rival", "waited", "nothing"]
ACTION = Literal[tuple(ACTIONS)]


# ----------------------------------------------------------------------------- schemas
class Story(BaseModel):
    story: str


class StoryCheck(BaseModel):
    contradiction: bool
    fields: list[str]
    stereotype_or_sensitive: bool


class Post(BaseModel):
    channel: str = Field(description="one of your social channels, or 'none'")
    text: str


class Msg(BaseModel):
    to: str = Field(description="first name of one of the people you talk to")
    text: str


class RoundA(BaseModel):
    feelings: str
    public_post: Post
    messages: list[Msg]
    question: Msg
    leaning: str


class Review(BaseModel):
    stars: int = Field(description="0 = no review this week, else 1-5")
    text: str


class RoundB(BaseModel):
    thoughts: str
    actions: list[ACTION]
    app_store_review: Review
    contacted_support: bool
    support_reason: str
    cfpb_complaint: bool
    card_dispute: bool
    money: MONEY
    added_money: Literal["none", "some", "a lot"]
    trust_feeling: int = Field(description="1-5")
    replies: list[Msg]
    memory_note: str
    status: STATUS


class Probe(BaseModel):
    q1a: int
    q1b: int
    q2a: int
    q2b: int
    q3a: int
    q3b: int
    q4a: int
    q4b: int


class Answer(BaseModel):
    answer: str


# ----------------------------------------------------------------------------- persona block
FIELD_LABELS = [
    ("age", "Age"), ("location", "Lives in"), ("occupation", "Work"), ("household", "Household"),
    ("household_income_band", "Household income"), ("customer_since", "Cobalt customer since"),
    ("cobalt_role", "Cobalt is my"), ("n_banks", "Number of banks I use"), ("other_bank", "Other bank"),
    ("balance_band", "Money I keep at Cobalt"), ("paycheck_into_cobalt", "Paycheck deposited into Cobalt"),
    ("payday", "Payday"), ("autopays", "Bills on autopay from Cobalt"),
    ("lives_paycheck_to_paycheck", "Live paycheck to paycheck"), ("moves_money_for_rate", "Move money for a better rate"),
    ("knows_fdic_limit", "Know the FDIC insurance limit ($250,000)"), ("fraud_or_phishing_victim", "Past fraud or phishing victim"),
    ("sms_from_bank_reaction", "When a bank texts me"), ("financial_literacy", "Financial know-how"),
    ("uses_p2p", "Use peer-to-peer payment apps"), ("checks_app_daily", "Check the Cobalt app every day"),
    ("preferred_support_channel", "Preferred support channel"), ("news_sources", "Where I hear news"),
    ("opinion_role", "Among friends I"), ("rumor_style", "With rumors I"), ("voice_propensity", "When unhappy I am"),
    ("patience", "Patience"), ("forgiveness", "Tendency to forgive"), ("business", "My business"),
    ("who_pays", "Who funds my account"), ("detail", "A detail about me"),
]


def facts(persona: dict) -> str:
    lines = []
    for k, label in FIELD_LABELS:
        v = persona.get(k)
        if v in (None, "", []):
            continue
        if isinstance(v, list):
            v = ", ".join(v)
        lines.append(f"- {label}: {v}")
    return "\n".join(lines)


def persona_block(persona: dict, ties: list[dict], names: dict) -> str:
    t = "\n".join(f"- {names[x['id']]} ({x['relation']}{', also banks with Cobalt' if x.get('cobalt') else ''})"
                  for x in ties) or "- (nobody in particular)"
    return (f"You are {persona['name']}, a real person and a customer of Cobalt Bank, a US digital bank with no "
            f"branches (promise: \"Banking with no surprises\"). You are one of its "
            f"{persona['group']}. Speak and decide as yourself, in the first person, consistent with your facts "
            f"and history. You are not an assistant.\n\n"
            f"FACTS ABOUT YOU (never contradict these):\n{facts(persona)}\n\n"
            f"YOUR STORY:\n{persona['narrative']}\n\n"
            f"PEOPLE YOU TALK TO ABOUT MONEY:\n{t}\n")


def history_block(state: dict) -> str:
    if not state["notes"]:
        return "YOUR NOTES FROM PAST WEEKS: none yet (this is the first week).\n"
    rows = [f"- Week {w}: {n} [Cobalt: {s}; money that week: {m}]" for w, n, s, m in state["notes"]]
    rel = "\n".join(f"- {k}: {v}" for k, v in state["relations"].items())
    return ("YOUR NOTES FROM PAST WEEKS (written by you):\n" + "\n".join(rows) +
            (f"\n\nWHAT PEOPLE TOLD YOU RECENTLY:\n{rel}" if rel else "") + "\n")


def situation_block(persona: dict, state: dict) -> str:
    moved = {0.0: "none", 0.3: "some", 0.8: "most"}.get(state["out_level"], "some")
    feel = {1: "very negative", 2: "negative", 3: "mixed", 4: "positive", 5: "very positive"}.get(state["trust"], "mixed")
    return (f"WHERE YOU STAND NOW: Cobalt is your {state['status']}. Money you have moved out of Cobalt since "
            f"November: {moved}. Your feeling about Cobalt right now: {feel}.\n"
            f"Switching banks is real work for you: {persona['switch_cost']}\n")


def week_block(week: int, dates: str, season: str, seen: list[str]) -> str:
    body = "\n".join(f"- {s}" for s in seen) if seen else "- Nothing unusual about Cobalt this week."
    return f"THIS WEEK: week {week} of 10 ({dates}, 2026). {season}\nWHAT YOU SAW, HEARD OR EXPERIENCED:\n{body}\n"


def round_a_prompt(pb: str, hb: str, sb: str, wb: str, channels: list[str], inbox: list[str]) -> str:
    ib = "\n".join(f"- {x}" for x in inbox) if inbox else "- No messages."
    ch = ", ".join(channels) if channels else "none"
    return (f"{pb}\n{hb}\n{sb}\n{wb}\nMESSAGES FROM PEOPLE YOU KNOW (since last week):\n{ib}\n\n"
            f"STEP 1 OF 2 THIS WEEK: react and talk. You have not decided anything yet.\n"
            f"- feelings: one or two sentences, in your own voice.\n"
            f"- public_post: only if you would really post; channel must be one of: {ch}; otherwise channel 'none' and empty text.\n"
            f"- messages: 0-2 short private messages to people you talk to (use their first name), only if you would.\n"
            f"- question: ask one of them something, or to='none'.\n"
            f"- leaning: what you are inclined to do about Cobalt this week and why, one sentence.\n"
            f"Most weeks most people do not post or message. Answer as JSON.")


def round_b_prompt(pb: str, hb: str, sb: str, wb: str, a_out: dict | None, heard: list[str], feed: list[str],
                   questions: list[str]) -> str:
    mine = (f"YOUR FIRST REACTION THIS WEEK: {a_out.get('feelings', '')} Leaning: {a_out.get('leaning', '')}\n"
            if a_out else "")
    hb2 = "\n".join(f"- {x}" for x in heard) if heard else "- Nobody messaged you."
    fd = "\n".join(f"- {x}" for x in feed) if feed else "- Nothing about Cobalt in your feeds."
    q = "\n".join(f"- {x}" for x in questions) if questions else "- None."
    return (f"{pb}\n{hb}\n{sb}\n{wb}\n{mine}\nPRIVATE MESSAGES TO YOU THIS WEEK:\n{hb2}\n\n"
            f"POSTS YOU SAW ON SOCIAL MEDIA THIS WEEK:\n{fd}\n\nQUESTIONS PEOPLE ASKED YOU:\n{q}\n\n"
            f"STEP 2 OF 2: decide what you actually do this week, as the real you would (doing nothing is fine).\n"
            f"- actions: everything you did this week (choose from the list).\n"
            f"- app_store_review: stars 0 if you did not write one.\n"
            f"- money: what you did with your money at Cobalt this week: kept, moved some, or moved most.\n"
            f"- added_money: whether you moved money INTO Cobalt this week.\n"
            f"- replies: answer the questions people asked you (first name in 'to'), else empty.\n"
            f"- memory_note: at most 60 words in the first person: what happened to you, how you feel about Cobalt, what you plan (no scores).\n"
            f"- status: where Cobalt stands for you at the end of this week. main bank = most of your everyday money "
            f"runs through Cobalt; second bank = you still use it, but another bank comes first; dormant = the account "
            f"is open but you stopped using it; left = you closed the account or moved everything out for good.\n"
            f"Answer as JSON.")


PROBE_QUESTIONS = {
    "1a": "How much do you trust {company}? 1 = not at all, 5 = completely.",
    "1b": "\"I can count on {company} to treat me right.\" 1 = strongly disagree, 5 = strongly agree.",
    "2a": "How likely are you to keep using {company} over the next three months? 1 = very unlikely, 5 = very likely.",
    "2b": "\"I am thinking about leaving {company}.\" 1 = strongly disagree, 5 = strongly agree.",
    "3a": "How likely are you to recommend {company} to a friend or colleague? 1 = very unlikely, 5 = very likely.",
    "3b": "If a friend asked you about {company} today, what would you tell them? 1 = stay away, 5 = go for it.",
    "4a": "How fairly has {company} treated you? 1 = very unfairly, 5 = very fairly.",
    "4b": "\"{company} takes advantage of people like me.\" 1 = strongly disagree, 5 = strongly agree.",
}


def probe_prompt(pb: str, hb: str, company: str, when: str) -> str:
    qs = "\n".join(f"q{k}: {v.format(company=company)}" for k, v in PROBE_QUESTIONS.items())
    t = "before November 2" if when == "start" else "after January 10"
    return (f"{pb}\n{hb}\nIt is {t}, 2026. A short customer check-in. Answer each question with a whole number "
            f"from 1 to 5, honestly, as yourself. Read each scale carefully: some are worded the other way round.\n"
            f"{qs}\nAnswer as JSON with keys q1a ... q4b.")


def story_prompt(fields_text: str) -> str:
    return ("Write a 4-6 sentence first-person backstory for this Cobalt Bank customer (Cobalt is a US digital bank). "
            "Use ONLY these facts and do not invent other facts that matter for money. Do not list the facts and do "
            "not repeat trait words such as 'patience', 'forgive', 'vocal' or 'financial know-how': show one or two of "
            "them through a concrete everyday detail instead. Do not predict what you would do in a future crisis. "
            "Do not mention race, religion, health, politics or immigration status; avoid stereotypes. Sound like a "
            "real person talking, not an ad or a profile.\n"
            f"FACTS:\n{fields_text}\n"
            "Include: why you opened Cobalt, one past money or bank experience (small and ordinary is fine), and how "
            "money fits into your week. Answer as JSON: {\"story\": \"...\"}.")


def check_prompt(fields_text: str, story: str) -> str:
    return ("Compare a customer backstory with the customer's facts.\n"
            f"FACTS:\n{fields_text}\n\nBACKSTORY:\n{story}\n\n"
            "contradiction: does the backstory contradict any fact? fields: which fact names (empty if none). "
            "stereotype_or_sensitive: does it mention race, religion, health, politics, immigration status, or use "
            "stereotyped wording? Answer as JSON.")


def ask_prompt(pb: str, hb: str, question: str) -> str:
    return (f"{pb}\n{hb}\nIt is January 2026, after the ten weeks above. Someone from Cobalt's board asks you a "
            f"question. Answer in the first person, in 2-5 sentences, as yourself, using what actually happened to "
            f"you. If you do not know something, say so.\nQUESTION: {question}\nAnswer as JSON: {{\"answer\": \"...\"}}.")


# ----------------------------------------------------------------------------- mocks (offline)
def _has(prompt: str, *words) -> bool:
    lo = prompt.split("WHAT YOU SAW, HEARD OR EXPERIENCED:")[-1].lower()  # this week only, not persona facts
    return any(w in lo for w in words)


def mock_story(prompt: str, rng: random.Random) -> dict:
    job = re.search(r"- Work: (.+)", prompt)
    return {"story": f"I opened Cobalt because the app was simple. I work as {job.group(1) if job else 'an employee'}. "
                     f"Once a bank froze my card for a day and I had to borrow cash. If I could not reach my money "
                     f"for a weekend I would {rng.choice(['use my other card', 'wait it out', 'call support'])}."}


def mock_check(prompt: str, rng: random.Random) -> dict:
    return {"contradiction": False, "fields": [], "stereotype_or_sensitive": False}


def _names(prompt: str) -> list[str]:
    block = prompt.split("PEOPLE YOU TALK TO ABOUT MONEY:")[-1].split("\n\n")[0]
    return re.findall(r"^- (\w+)", block, flags=re.M)


def mock_round_a(prompt: str, rng: random.Random) -> dict:
    bad = _has(prompt, "read-only", "declined", "failed", "waited about", "rumor", "phishing", "outage", "delay")
    names = _names(prompt)
    ch = re.search(r"channel must be one of: ([^;]+);", prompt)
    chans = [c.strip() for c in ch.group(1).split(",")] if ch and ch.group(1).strip() != "none" else []
    post = {"channel": "none", "text": ""}
    if chans and rng.random() < (0.5 if bad else 0.1):
        post = {"channel": rng.choice(chans), "text": "Cobalt app is read-only again, can't move my money." if bad
                else "Cobalt has been fine for me."}
    msgs = [{"to": rng.choice(names), "text": "Are you having trouble with Cobalt too?"}] if names and bad and rng.random() < 0.6 else []
    q = {"to": rng.choice(names), "text": "Are you moving your money?"} if names and rng.random() < 0.3 else {"to": "none", "text": ""}
    return {"feelings": "Annoyed." if bad else "Fine.", "public_post": post, "messages": msgs, "question": q,
            "leaning": "Thinking about moving some money." if bad else "Nothing to do."}


def mock_round_b(prompt: str, rng: random.Random) -> dict:
    bad = _has(prompt, "read-only", "declined", "failed", "waited about", "rumor", "phishing", "outage", "delay")
    cur = re.search(r"Cobalt is your (main bank|second bank|dormant|left)", prompt)
    status = cur.group(1) if cur else "main bank"
    money, actions, stars = "kept", ["nothing"], 0
    if bad and rng.random() < 0.35:
        money = rng.choice(["moved some", "moved some", "moved most"])
        actions = ["moved money", "complained in app"]
        if rng.random() < 0.25:
            stars = rng.choice([1, 2])
        if rng.random() < 0.08:
            status = rng.choice(["second bank", "dormant"])
    names = re.findall(r"QUESTIONS PEOPLE ASKED YOU:\n- (\w+)", prompt)
    return {"thoughts": "Mock thoughts.", "actions": actions, "app_store_review": {"stars": stars, "text": "" if not stars else "Bad week."},
            "contacted_support": bad and rng.random() < 0.3, "support_reason": "", "cfpb_complaint": bad and rng.random() < 0.02,
            "card_dispute": rng.random() < 0.02, "money": money, "added_money": "some" if _has(prompt, "boost") and rng.random() < 0.3 else "none",
            "trust_feeling": 2 if bad else 4, "replies": [{"to": n, "text": "Not yet."} for n in names[:1]],
            "memory_note": "Mock week note.", "status": status}


def mock_probe(prompt: str, rng: random.Random) -> dict:
    hi = rng.choice([3, 4, 4, 5])
    return {f"q{k}": (6 - hi if k in ("2b", "4b") else hi) for k in PROBE_QUESTIONS}


def mock_answer(prompt: str, rng: random.Random) -> dict:
    return {"answer": "It was a stressful weekend, but I mostly stayed."}
