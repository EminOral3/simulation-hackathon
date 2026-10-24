"""Live "ask a persona" for the board: one persona answers in its own voice, only from what it lived through
in a saved run (personas.jsonl + weekly.jsonl + calls.jsonl). Read-only on the run folder.

    python tools/ask_persona.py --list                    # id, group, profile, week-10 status, money, crises
    python tools/ask_persona.py --suggest                 # 3 candidates for the live question
    python tools/ask_persona.py --timeline P07            # what the persona knows, as plain text
    python tools/ask_persona.py --persona P07             # interactive: type a question, Enter; "exit" to quit
    python tools/ask_persona.py --prerecord               # 6 backup answers for the 3 suggested -> tools/prerecorded.json
    python tools/ask_persona.py --vs P07                  # plan_1 and nodecision_1 side by side, week by week
    [--run runs/plan_1] [--compare runs/plan_2] [--other runs/nodecision_1] [--model gemini-3.5-flash-lite] [--fallback tools/prerecorded.json] [--offline]

Key: TALP_KEY, else VERTEX_AI_KEY (env or repo .env), read via code_kit.cobalt.llm.api_key. Needs `pip install google-genai`.
On any API error or timeout the closest prerecorded answer for that persona is shown, marked "(cached)".
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import shutil
import sys
import textwrap
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(ROOT))

from code_kit.cobalt import agent, config  # noqa: E402
from code_kit.cobalt import params as P  # noqa: E402
from code_kit.cobalt.llm import api_key  # noqa: E402
from pydantic import BaseModel  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
os.system("")  # turns on ANSI colors in the Windows console

YELLOW = "\033[93m"
GRAY, RESET ="\033[90m", "\033[0m"
TIMEOUT_S, RETRIES, TEMPERATURE, SEED, MAX_WORDS = 15, 1, 0.7, 7, 80
SYSTEM = ("You are {name}, a Cobalt Bank customer. Stay in character, first person, plain spoken. Answer only from "
          "your own story and timeline. If asked about something you did not experience or do not know, say so. "
          "Never mention being simulated or an AI. Max 80 words.")
PRERECORD_QUESTIONS = [
    "How did you feel when you saw the unknown charges?",
    "What did you think of Cobalt's message about the upgrade?",
    "Did the December 12-13 upgrade affect you?",
    "Did you move any money? Why?",
    "Would you recommend Cobalt to a friend today?",
    "What would make you leave Cobalt?",
]

# what counts as a crisis the persona lived through, read from the lines in its own weekly prompt
CRISES = {
    "card charges": ("card charge", "card charges", "test charges", "charged some payments twice"),
    "core banking switch": ("read-only", "core banking switch"),
    "government shutdown": ("government shutdown", "federal agency", "federal workers"),
}
# directly affected: (pattern in the persona's own lines, weight, reason)
DIRECT = [
    ("card charge you do not recognize", 3, "saw an unknown charge on own card"),
    ("you work for a federal agency", 3, "federal worker, paycheck at risk in the shutdown"),
    ("paycheck arrived on friday", 2, "paycheck stuck during the switch"),
    ("payment was declined", 2, "card declined during the switch"),
    ("peer-to-peer app from your cobalt account and it failed", 1, "P2P payment failed during the switch"),
]


# ----------------------------------------------------------------------------- run data
def jl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def resolve_run(run: str) -> Path:
    """runs/plan_1 as given, else under the repo, else the newest package or run folder with that name."""
    for d in (Path(run), ROOT / run):
        if (d / "weekly.jsonl").exists():
            return d
    name = Path(run).name
    out = P.path(P.load(), "outputs")
    cands = sorted((out / "submissions").glob(f"*/runs/{name}")) + sorted((out / "runs").glob(f"*{name}*"))
    cands = [c for c in cands if (c / "weekly.jsonl").exists()]
    if not cands:
        raise SystemExit(f"run not found: {run} (give --run <folder with personas.jsonl, weekly.jsonl, calls.jsonl>)")
    return cands[-1]


def week_lines(prompt: str) -> list[str]:
    """The persona's 'WHAT YOU SAW, HEARD OR EXPERIENCED' lines from its round-B prompt for that week."""
    if "WHAT YOU SAW, HEARD OR EXPERIENCED:" not in prompt:
        return []
    body = prompt.split("WHAT YOU SAW, HEARD OR EXPERIENCED:", 1)[1]
    body = re.split(r"\n(?:YOUR FIRST REACTION THIS WEEK|PRIVATE MESSAGES TO YOU THIS WEEK)", body, maxsplit=1)[0]
    out = []
    for line in body.splitlines():
        line = line.strip()[2:].strip() if line.strip().startswith("- ") else ""
        # an old message still in the inbox is not news; the week it arrived carries it word for word
        if line and not line.startswith("Nothing unusual") and "still in your inbox" not in line:
            out.append(line)
    return out


def first_sentences(text: str, n: int = 2) -> str:
    parts = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    return " ".join(parts[:n]).strip()


class Run:
    def __init__(self, d: Path):
        self.dir = d
        self.people = jl(d / "personas.jsonl")
        self.by_id = {f["id"]: f for f in self.people}
        weekly = jl(d / "weekly.jsonl")
        need = {r["call"] for r in weekly}
        self.calls = {}
        with (d / "calls.jsonl").open(encoding="utf-8") as fh:
            for l in fh:
                if l.strip():
                    c = json.loads(l)
                    if c["id"] in need:
                        self.calls[c["id"]] = c
        self.weekly: dict[str, list[dict]] = {}
        self._weeks: dict[str, list[dict]] = {}
        for r in sorted(weekly, key=lambda r: r["week"]):
            self.weekly.setdefault(r["persona"], []).append(r)

    def find(self, key: str) -> dict:
        for f in self.people:
            if f["id"].lower() == key.lower() or f["name"].lower().startswith(key.lower()):
                return f
        raise SystemExit(f"persona not found: {key}")

    def weeks(self, pid: str) -> list[dict]:
        """One entry per week: status, money, memory note, what the persona saw, 1-2 sentences of its answer."""
        if pid in self._weeks:
            return self._weeks[pid]
        rows, before = [], set()
        for r in self.weekly.get(pid, []):
            c = self.calls.get(r["call"], {})
            try:
                resp = json.loads(c.get("response") or "{}")
            except json.JSONDecodeError:
                resp = {}
            seen = week_lines(c.get("prompt", ""))
            new = [l for l in seen if l not in before]  # an offer still running is shown in its first week only
            before = set(seen)
            rows.append({"week": r["week"], "status": r["status"], "money": r.get("money", "?"),
                         "added": r.get("added_money", "none"), "note": (resp.get("memory_note") or "").strip(),
                         "said": first_sentences(resp.get("thoughts", "")),
                         "seen": new})
        self._weeks[pid] = rows
        return rows

    def last(self, pid: str) -> dict:
        w = self.weekly.get(pid, [])
        return w[-1] if w else {}

    def crises(self, pid: str) -> list[str]:
        text = " ".join(l for w in self.weeks(pid) for l in w["seen"]).lower()
        return [k for k, pats in CRISES.items() if any(p in text for p in pats)]

    def direct(self, pid: str) -> tuple[int, list[str]]:
        f = self.by_id[pid]
        text = " ".join(l for w in self.weeks(pid) for l in w["seen"]).lower()
        score, why = 0, []
        for pat, s, reason in DIRECT:
            if pat in text:
                score, why = score + s, why + [reason]
        if f.get("balance_band") in ("50-250k", "250k+"):
            score, why = score + 1, why + [f"large saver ({f['balance_band']})"]
        if f.get("paycheck_into_cobalt") == "yes":
            score, why = score + 1, why + ["paycheck goes into Cobalt"]
        return score, why


def profile(f: dict) -> str:
    return f"{f.get('age', '?')}, {f.get('occupation', '?')}, keeps {f.get('balance_band', '?')}"


def timeline_text(run: Run, f: dict) -> str:
    out = [f"{f['id']} {f['name']}: {f['group']}", f"Profile: {profile(f)}; Cobalt was my {f.get('cobalt_role')} on Nov 2.",
           f"Story: {f.get('narrative', '')}", "", "Timeline (now: end of week 10, Sunday January 10):"]
    for w in run.weeks(f["id"]):
        added = f", added {w['added']}" if w["added"] not in ("none", None) else ""
        out.append(f"\nWeek {w['week']} ({config.WEEK_DATES[w['week']]}): Cobalt = {w['status']}; money {w['money']}{added}")
        for line in w["seen"]:
            out.append(f"  - {line}")
        if w["said"]:
            out.append(f"  I thought: {w['said']}")
        if w["note"]:
            out.append(f"  My note: {w['note']}")
    return "\n".join(out)


def context(run: Run, f: dict) -> str:
    return (f"FACTS ABOUT YOU:\n{agent.facts(f)}\n\n" + timeline_text(run, f) +
            "\n\nIt is now Sunday, January 10, the end of week 10. You know only what is above. Lines starting with "
            "'News:' and posts by Cobalt on social media are things you read about other customers; only lines that "
            "say 'you' happened to you yourself.")


# ----------------------------------------------------------------------------- LLM
class Answer(BaseModel):
    answer: str
    weeks: list[int]


def model_id(name: str | None) -> str:
    p = P.load()
    return name or p["llm"]["model_experiment"]  # fast model, thinking off (llm.no_thinking_models)


_client = None


def client():
    global _client
    if _client is None:
        from google import genai
        from google.genai import types
        _client = genai.Client(vertexai=True, api_key=api_key(),
                               http_options=types.HttpOptions(timeout=TIMEOUT_S * 1000,
                                                              retry_options=types.HttpRetryOptions(attempts=1)))
    return _client


async def ask_live(model: str, f: dict, ctx: str, question: str) -> dict:
    from google.genai import types
    cfg = types.GenerateContentConfig(
        system_instruction=SYSTEM.format(name=f["name"]), temperature=TEMPERATURE, seed=SEED, max_output_tokens=400,
        response_mime_type="application/json", response_schema=Answer,
        thinking_config=types.ThinkingConfig(thinking_budget=0))
    prompt = (f"{ctx}\n\nA member of Cobalt's board asks you: {question}\n"
              f"Return JSON: answer (max {MAX_WORDS} words, in character) and weeks (the week numbers your answer "
              f"draws on; empty if none).")
    err = None
    for _ in range(RETRIES + 1):
        try:
            r = await asyncio.wait_for(client().aio.models.generate_content(model=model, contents=prompt, config=cfg),
                                       TIMEOUT_S)
            d = json.loads(r.text)
            return {"answer": d["answer"].strip(), "weeks": sorted({int(x) for x in d.get("weeks", []) if 1 <= int(x) <= 10})}
        except Exception as e:  # timeout, network, quota, bad JSON: one retry, then the caller falls back
            err = e
    raise RuntimeError(repr(err)[:200])


def words(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", s.lower())) - {"the", "a", "you", "did", "do", "what", "of", "to", "your", "any"}


def cached(fallback: Path, pid: str, question: str) -> dict | None:
    if not fallback.exists():
        return None
    rows = json.loads(fallback.read_text(encoding="utf-8")).get("personas", {}).get(pid, [])
    if not rows:
        return None
    q = words(question)
    best = max(rows, key=lambda r: len(q & words(r["question"])) / (len(q | words(r["question"])) or 1))
    return {**best, "cached": True}


def log(rec: dict):
    with (TOOLS / "live_log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


async def answer(a, run: Run, f: dict, ctx: str, question: str) -> dict:
    t0 = time.perf_counter()
    res, err = None, None
    if not a.offline:
        try:
            res = {**await ask_live(model_id(a.model), f, ctx, question), "cached": False}
        except Exception as e:
            err = str(e)
    if res is None:
        res = cached(Path(a.fallback), f["id"], question) or {"answer": "(no answer: API unavailable and no cached "
                                                                        "answer for this persona)", "weeks": [], "cached": True}
    res["seconds"] = round(time.perf_counter() - t0, 2)
    log({"time": datetime.now().isoformat(timespec="seconds"), "run": str(run.dir), "persona": f["id"],
         "question": question, "answer": res["answer"], "weeks": res.get("weeks", []), "cached": res["cached"],
         "seconds": res["seconds"], **({"error": err} if err else {})})
    return res


def show(f: dict, res: dict):
    tag = " (cached)" if res["cached"] else ""
    weeks = ", ".join(map(str, res.get("weeks") or [])) or "none"
    print(f"\n{f['name']}: {res['answer']}{tag}")
    print(f"{GRAY}based on weeks: {weeks} · {res['seconds']}s{RESET}\n")


# ----------------------------------------------------------------------------- commands
def cmd_list(run: Run):
    print(f"{'id':4s} {'group':30s} {'profile':44s} {'w10 status':12s} {'money':11s} crises")
    for f in run.people:
        r = run.last(f["id"])
        print(f"{f['id']:4s} {f['group'][:30]:30s} {profile(f)[:44]:44s} {r.get('status', '?'):12s} "
              f"{r.get('money', '?'):11s} {len(run.crises(f['id']))}")


def suggest(run: Run, compare: Run | None) -> list[tuple[dict, str]]:
    ids = [f["id"] for f in run.people]
    note_len = {i: sum(len(w["note"]) for w in run.weeks(i)) for i in ids}
    picks: list[tuple[dict, str]] = []

    def take(order, why):
        for i in order:
            if i not in {f["id"] for f, _ in picks}:
                picks.append((run.by_id[i], why(i)))
                return

    take(sorted(ids, key=lambda i: -note_len[i]),
         lambda i: f"richest memory: {note_len[i]} characters of weekly notes")
    direct = {i: run.direct(i) for i in ids}
    take(sorted([i for i in ids if direct[i][0] > 0], key=lambda i: (-direct[i][0], -note_len[i])),
         lambda i: "directly hit: " + "; ".join(direct[i][1]))
    if compare is not None:
        same = [i for i in ids if run.last(i).get("status") and run.last(i).get("status") == compare.last(i).get("status")]
        # prefer someone whose story moved (status changed since Nov 2) so the answer has something to tell
        same.sort(key=lambda i: (run.last(i)["status"] == run.by_id[i].get("cobalt_role"), -note_len[i]))
        take(same, lambda i: f"consistent: week-10 status '{run.last(i)['status']}' in both {run.dir.name} and "
                             f"{compare.dir.name} (started as {run.by_id[i].get('cobalt_role')})")
    else:
        take(sorted(ids, key=lambda i: (-len(run.crises(i)), -note_len[i])),
             lambda i: f"lived through {len(run.crises(i))} crises: {', '.join(run.crises(i))} (no plan_2 to compare)")
    return picks


def cmd_suggest(run: Run, compare: Run | None):
    for f, why in suggest(run, compare):
        r = run.last(f["id"])
        print(f"{f['id']} {f['name']} ({f['group']}; w10 {r.get('status')}, money {r.get('money')}): {why}")


async def cmd_prerecord(a, run: Run, compare: Run | None):
    picks = [f for f, _ in suggest(run, compare)]
    model = model_id(a.model)

    async def one(f, q):
        try:
            return f["id"], q, await ask_live(model, f, context(run, f), q)
        except Exception as e:
            print(f"  failed {f['id']}: {q} -> {e}")
            return f["id"], q, None
    res = await asyncio.gather(*(one(f, q) for f in picks for q in PRERECORD_QUESTIONS))
    out = {"run": str(run.dir), "model": model, "created": datetime.now().isoformat(timespec="seconds"), "personas": {}}
    for pid, q, r in res:
        if r:
            out["personas"].setdefault(pid, []).append({"question": q, **r})
    path = Path(a.fallback)
    n = sum(len(v) for v in out["personas"].values())
    if not n:  # keep an existing backup rather than overwrite it with nothing
        raise SystemExit(f"no answers (API unavailable?); {path} left unchanged")
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{n}/{len(res)} answers -> {path}")


def week_cell(w: dict | None, other: dict | None, width: int, clip: int = 180) -> list[str]:
    """One week of one run as wrapped lines for a column; long messages are clipped (--timeline shows them whole).
    '+' marks a line the other run's persona did not see that week."""
    if w is None:
        return ["(no data)"]
    head = f"Cobalt = {w['status']}; money {w['money']}" + (f", added {w['added']}" if w["added"] not in ("none", None) else "")
    theirs = set(other["seen"]) if other else set()
    items = [f"{'-' if l in theirs else '+'} {l if len(l) <= clip else l[:clip].rsplit(' ', 1)[0] + ' ...'}"
             for l in w["seen"]]
    if w["note"]:
        items.append(f"Note: {w['note'][:clip]}")
    out = textwrap.wrap(head, width)
    for it in items:
        out += textwrap.wrap(it, width, subsequent_indent="  ")
    return out


def cmd_vs(left: Run, right: Run, f: dict):
    width = max(100, shutil.get_terminal_size((160, 40)).columns)
    col = (width - 3) // 2
    lw = {w["week"]: w for w in left.weeks(f["id"])}
    rw = {w["week"]: w for w in right.weeks(f["id"])}
    print(f"{f['id']} {f['name']}: {f['group']}; started as {f.get('cobalt_role')}")
    print(f"{left.dir.name:<{col}} | {right.dir.name}")
    differs = []
    for k in range(1, 11):
        a, b = lw.get(k), rw.get(k)
        diff = bool(a and b and (a["status"], a["money"], a["added"]) != (b["status"], b["money"], b["added"]))
        if diff:
            differs.append(k)
        title = f"Week {k} ({config.WEEK_DATES[k]})" + ("  <- status or money differs" if diff else "")
        print(f"\n{YELLOW if diff else ''}{title}{RESET if diff else ''}\n{'-' * col}-+-{'-' * col}")
        l, r = week_cell(a, b, col), week_cell(b, a, col)
        for i in range(max(len(l), len(r))):
            x, y = (l[i] if i < len(l) else ""), (r[i] if i < len(r) else "")
            print(f"{x:<{col}} | {y}")
    end = lambda run: run.last(f["id"])
    print(f"\nWeek 10: {left.dir.name} {end(left).get('status')}, money {end(left).get('money')} | "
          f"{right.dir.name} {end(right).get('status')}, money {end(right).get('money')}")
    print(f"Status or money differs in weeks: {', '.join(map(str, differs)) or 'none'}")


def cmd_persona(a, run: Run, f: dict):
    ctx = context(run, f)
    r = run.last(f["id"])
    print(f"== {f['id']} {f['name']} ({f['group']}); week 10: {r.get('status')}, money {r.get('money')}")
    print("Ask in English. Type 'exit' to quit.\n")
    while True:
        try:
            q = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in ("exit", "quit"):
            break
        if q:
            show(f, asyncio.run(answer(a, run, f, ctx, q)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", default="runs/plan_1")
    ap.add_argument("--compare", help="run for the consistency pick (default: plan_2 next to --run)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true")
    g.add_argument("--suggest", action="store_true")
    g.add_argument("--timeline", metavar="ID")
    g.add_argument("--persona", metavar="ID")
    g.add_argument("--prerecord", action="store_true")
    g.add_argument("--vs", metavar="ID", help="--run and --other side by side for one persona")
    ap.add_argument("--other", help="right-hand run for --vs (default: nodecision_1 next to --run)")
    ap.add_argument("--model", help="default: llm.model_experiment (fast, thinking off)")
    ap.add_argument("--fallback", default=str(TOOLS / "prerecorded.json"))
    ap.add_argument("--offline", action="store_true", help="never call the API; answer from --fallback")
    a = ap.parse_args()

    run = Run(resolve_run(a.run))
    cmp_dir = Path(a.compare) if a.compare else run.dir.parent / "plan_2"
    compare = Run(resolve_run(str(cmp_dir))) if (a.compare or (cmp_dir / "weekly.jsonl").exists()) and cmp_dir != run.dir else None
    if a.list:
        cmd_list(run)
    elif a.suggest:
        cmd_suggest(run, compare)
    elif a.timeline:
        print(timeline_text(run, run.find(a.timeline)))
    elif a.vs:
        other = Run(resolve_run(a.other or str(run.dir.parent / "nodecision_1")))
        cmd_vs(run, other, run.find(a.vs))
    elif a.prerecord:
        asyncio.run(cmd_prerecord(a, run, compare))
    else:
        cmd_persona(a, run, run.find(a.persona))


if __name__ == "__main__":
    main()
