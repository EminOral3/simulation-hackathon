"""Weekly loop: world -> round A (notice and talk) -> routing (DMs, questions, public posts) -> round B
(decide) -> state, support queue. Writes the challenge's run files plus our own logs."""
from __future__ import annotations

import asyncio
import json
import random
from pathlib import Path

from . import agent, config, crisis, metrics, support_queue, world
from .llm import LLM

PROBE_KEYS = ["1a", "1b", "2a", "2b", "3a", "3b", "4a", "4b"]


NEG_WORDS = ("moving", "moved", "switch", "leaving", "left", "furious", "worst", "done with", "pull", "close",
             "waited", "hours", "scam", "angry", "frustrat", "annoy", "ridiculous", "unacceptable", "terrible", "not safe",
             "trouble", "locked", "declined", "failed", "can't", "cannot", "stuck", "late")


def is_negative(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in NEG_WORDS)


def sent_negative(a: dict | None) -> bool:
    if not a:
        return False
    texts = [m.get("text", "") for m in a.get("messages") or []] + [(a.get("public_post") or {}).get("text", "")]
    return any(is_negative(t) for t in texts if t)


COBALT_WORDS = ("cobalt", "bank", "money", "account", "card", "charge", "rate", "savings", "switch", "move", "moving",
                "support", "app", "paycheck", "transfer", "deposit", "upgrade", "fee", "fraud", "scam")


def about_cobalt(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in COBALT_WORDS)


def first_name(full: str) -> str:
    return full.split()[0]


class Sim:
    def __init__(self, p: dict, llm: LLM, people: list[dict], *, run_type: str, seed: int, decisions: list,
                 filters: dict, announcements: list, probe: bool = True, weeks: int = 10, log=print):
        self.p, self.llm, self.people, self.seed = p, llm, people, seed
        self.run_type, self.probe, self.weeks, self.log = run_type, probe, weeks, log
        self.by_id = {f["id"]: f for f in people}
        self.names = {f["id"]: f["name"] for f in people}
        self.ctx = world.Ctx(p=p, seed=seed, decisions=decisions, filters=filters, announcements=announcements,
                             overrun=world.draw_overrun(p, seed))
        net = p["network"]
        self.ties = {f["id"]: (f.get("ties", []) if net["enabled_ties"] else []) for f in people}
        self.state = {f["id"]: {"status": f["cobalt_role"], "trust": 4, "out_level": 0.0, "notes": [], "relations": {},
                                "inbox_a": [], "support_last": None, "disputes": []} for f in people}
        self.calls: list = []
        self.weekly: list[dict] = []
        self.probes: list[dict] = []
        self.interactions: list[dict] = []
        self.queue: list[dict] = []

    # ------------------------------------------------------------------ helpers
    def pb(self, f):
        b = self.p["budget"]
        return agent.persona_block(f, self.ties[f["id"]], self.names, compact=b["lean_prompts"] and b["compact_facts"])

    def resolve(self, sender: str, to: str) -> str | None:
        to = (to or "").strip().split()[0].strip(".,").lower() if to else ""
        for t in self.ties[sender]:
            if first_name(self.names[t["id"]]).lower() == to:
                return t["id"]
        return None

    def relation(self, a: str, b: str) -> str:
        for t in self.ties[a]:
            if t["id"] == b:
                return t["relation"]
        return ""

    async def ask(self, **kw):
        c = await self.llm.ask(seed=self.seed, **kw)
        self.calls.append(c)
        return c

    # ------------------------------------------------------------------ probe
    async def run_probe(self, when: str):
        week = 0 if when == "start" else 11
        company = self.p["run"]["company_name"]

        async def one(f):
            c = await self.ask(call_id=f"w{week:02d}-probe-{f['id']}", persona=f["id"], week=week, kind="probe",
                               prompt=agent.probe_prompt(self.pb(f), agent.history_block(self.state[f["id"]]) if when == "end" else "",
                                                         company, when),
                               schema=agent.Probe, mock=agent.mock_probe)
            for k in PROBE_KEYS:
                v = (c.parsed or {}).get(f"q{k}")
                if isinstance(v, int) and 1 <= v <= 5:
                    self.probes.append({"persona": f["id"], "when": when, "question": k, "score": v, "call": c.id})
        await asyncio.gather(*(one(f) for f in self.people))

    # ------------------------------------------------------------------ week
    async def week(self, w: int):
        p = self.p
        b = p["budget"]
        lean, brief = b["lean_prompts"], b["lean_prompts"] and b["brief_outputs"]
        seen, new, fx, sal = {}, {}, {}, {}
        for f in self.people:
            seen[f["id"]], new[f["id"]], fx[f["id"]], sal[f["id"]] = world.week_inputs(self.ctx, f, self.state[f["id"]], w)
        blocks, blocks_a = {}, {}
        for f in self.people:
            s = self.state[f["id"]]
            hb = (agent.history_block(s, b["history_full_weeks"], b["relations_max"]) if lean else agent.history_block(s))
            hb_a = agent.history_block(s, b["history_full_weeks_round_a"], b["relations_max"]) if lean else hb
            blocks_a[f["id"]] = hb_a
            blocks[f["id"]] = (self.pb(f), hb, agent.situation_block(f, s),
                               agent.week_block(w, config.WEEK_DATES[w], config.SEASON.get(w, ""), seen[f["id"]]))

        # round A: only personas with something new (or messages waiting)
        a_out: dict[str, dict] = {}

        async def round_a(f):
            pid = f["id"]
            c = await self.ask(call_id=f"w{w:02d}-a-{pid}", persona=pid, week=w, kind="round_a",
                               prompt=agent.round_a_prompt(blocks[pid][0], blocks_a[pid], *blocks[pid][2:], f.get("social_channels", []) if p["network"]["enabled_feed"] else [],
                                                           self.state[pid]["inbox_a"], brief=brief),
                               schema=agent.RoundA, mock=agent.mock_round_a)
            a_out[pid] = c.parsed or {}
        def wants_round_a(pid):
            if not p["turns"]["round_a_skip_if_quiet"]:
                return True
            inbox = self.state[pid]["inbox_a"]
            if lean and b["round_a_salient_only"]:  # skip small talk and offers that are merely still running
                return sal[pid] or any(about_cobalt(x) for x in inbox)
            return new[pid] or bool(inbox)
        act = [f for f in self.people if wants_round_a(f["id"])]
        await asyncio.gather(*(round_a(f) for f in act))

        # routing
        heard = {f["id"]: [] for f in self.people}
        questions = {f["id"]: [] for f in self.people}
        posts = []
        for pid, out in a_out.items():
            me = self.names[pid]
            if p["network"]["enabled_ties"]:
                for m in (out.get("messages") or [])[: p["network"]["dm_max"]]:
                    to = self.resolve(pid, m.get("to", ""))
                    if to and m.get("text", "").strip():
                        heard[to].append(f"{me} ({self.relation(to, pid)}): {m['text'].strip()}")
                        self.interactions.append({"week": w, "type": "dm", "from": pid, "to": to, "text": m["text"].strip()})
                q = out.get("question") or {}
                to = self.resolve(pid, q.get("to", ""))
                if to and q.get("text", "").strip():
                    questions[to].append(f"{me} ({self.relation(to, pid)}) asks: {q['text'].strip()}")
                    self.interactions.append({"week": w, "type": "question", "from": pid, "to": to, "text": q["text"].strip()})
            post = out.get("public_post") or {}
            ch = (post.get("channel") or "none").strip()
            if p["network"]["enabled_feed"] and ch.lower() != "none" and post.get("text", "").strip():
                posts.append({"from": pid, "channel": ch, "text": post["text"].strip(), "w": self.by_id[pid]["w_active"]})
                self.interactions.append({"week": w, "type": "post", "from": pid, "channel": ch, "text": post["text"].strip()})
        feeds = {}
        for f in self.people:
            mine = {c.lower() for c in f.get("social_channels", [])}
            cand = [x for x in posts if x["from"] != f["id"] and x["channel"].lower() in mine]
            rng = random.Random(f"{self.seed}|{w}|{f['id']}|feed")
            cand.sort(key=lambda x: x["w"] * (1 + rng.random()), reverse=True)
            tie_ids = {t["id"] for t in self.ties[f["id"]]}
            feeds[f["id"]] = [f"{x['channel']}, {self.names[x['from']]}{' (' + self.relation(f['id'], x['from']) + ')' if x['from'] in tie_ids else ''}: "
                              f"{x['text']}" for x in cand[: p["network"]["feed_size"]]]

        # round B: everyone decides
        b_out: dict[str, tuple] = {}

        async def round_b(f):
            pid = f["id"]
            c = await self.ask(call_id=f"w{w:02d}-b-{pid}", persona=pid, week=w, kind="round_b",
                               prompt=agent.round_b_prompt(*blocks[pid], a_out.get(pid), heard[pid], feeds[pid], questions[pid],
                                                           brief=brief, memory_words=b["memory_words"] if brief else 60),
                               schema=agent.RoundB, mock=agent.mock_round_b)
            b_out[pid] = (c, c.parsed or {})
        await asyncio.gather(*(round_b(f) for f in self.people))

        # state update
        out_map = {"kept": 0.0, "moved some": 0.3, "moved most": 0.8}
        for f in self.people:
            pid = f["id"]
            s = self.state[pid]
            s["inbox_a"] = []
        contacts_w = 0.0
        prev = {f["id"]: self.state[f["id"]]["status"] for f in self.people}
        prev_trust = {f["id"]: self.state[f["id"]]["trust"] for f in self.people}
        for f in self.people:
            pid = f["id"]
            c, o = b_out[pid]
            s = self.state[pid]
            status = o.get("status") if o.get("status") in config.STATUSES else s["status"]
            money = o.get("money") if o.get("money") in config.MONEY else "kept"
            s["status"] = status
            s["out_level"] = max(s["out_level"], out_map[money])
            s["trust"] = o.get("trust_feeling") if isinstance(o.get("trust_feeling"), int) else s["trust"]
            s["notes"].append((w, (o.get("memory_note") or "").strip()[:500], status, money))
            if o.get("contacted_support"):
                contacts_w += f["w_active"]
            if o.get("card_dispute"):
                s["disputes"].append(w)
            for r in (o.get("replies") or [])[: p["turns"]["max_replies"]]:
                to = self.resolve(pid, r.get("to", ""))
                if to and r.get("text", "").strip() and p["network"]["enabled_ties"]:
                    self.state[to]["inbox_a"].append(f"{self.names[pid]} replied: {r['text'].strip()}")
                    self.state[to]["relations"][self.names[pid]] = r["text"].strip()[:160]
                    self.interactions.append({"week": w, "type": "reply", "from": pid, "to": to, "text": r["text"].strip()})
            for line in heard[pid]:
                who = line.split(" (")[0]
                s["relations"][who] = line.split(": ", 1)[-1][:160]
            review = o.get("app_store_review") or {}
            self.weekly.append({
                "persona": pid, "week": w, "status": status, "call": c.id, "money": money,
                "added_money": o.get("added_money", "none"), "actions": o.get("actions", []),
                "review_stars": review.get("stars", 0) if isinstance(review.get("stars"), int) else 0,
                "review_text": review.get("text", ""), "cfpb": bool(o.get("cfpb_complaint")),
                "contacted_support": bool(o.get("contacted_support")), "card_dispute": bool(o.get("card_dispute")),
                "trust": s["trust"], "round_a": pid in a_out, "dms_in": len(heard[pid]), "feed_seen": len(feeds[pid]),
                "parsed": bool(c.parsed), "fx": fx[pid], "prev_status": prev[pid], "prev_trust": prev_trust[pid],
                "peer_neg": sum(is_negative(x) for x in heard[pid]), "feed_neg": sum(is_negative(x) for x in feeds[pid]),
                "sent_neg": int(sent_negative(a_out.get(pid)))})
        total_w = sum(f["w_active"] for f in self.people)
        share = contacts_w / total_w
        if w == 1:
            self.contact_baseline = share  # week 1 is business as usual: the queue is anchored to it
        q = support_queue.week_wait(p["support"], share, config.extra_agents(p, self.ctx.decisions, w),
                                    getattr(self, "contact_baseline", None))
        q["week"] = w
        self.queue.append(q)
        for f in self.people:
            if b_out[f["id"]][1].get("contacted_support"):
                r = random.Random(f"{self.seed}|{w}|{f['id']}|support")
                self.state[f["id"]]["support_last"] = {"week": w, "wait_min": q["wait_min"] * r.uniform(0.6, 1.5),
                                                       "resolved": r.random() < q["p_resolved"]}
        n_a = len(a_out)
        self.log(f"  week {w}: round A {n_a}, DMs {sum(len(v) for v in heard.values())}, posts {len(posts)}, "
                 f"wait {q['wait_min']} min, active {sum(self.state[x]['status'] in ('main bank', 'second bank') for x in self.state)}/{len(self.people)}")

    async def run(self):
        if self.probe:
            await self.run_probe("start")
        for w in range(1, self.weeks + 1):
            await self.week(w)
        if self.probe and self.weeks == 10:
            await self.run_probe("end")


def write_outputs(sim: Sim, out: Path, run_json: dict, gen_calls: list[dict], extra: dict):
    def jl(name, rows):
        with (out / name).open("w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    (out / "run.json").write_text(json.dumps(run_json, indent=1, ensure_ascii=False))
    jl("personas.jsonl", sim.people)
    jl("calls.jsonl", gen_calls + [c.record() for c in sim.calls])
    jl("weekly.jsonl", sim.weekly)
    jl("interactions.jsonl", sim.interactions)
    jl("queue.jsonl", sim.queue)
    if sim.probes:
        jl("probe.jsonl", sim.probes)
    m = metrics.compute(sim.p, sim.people, sim.weekly) if sim.weeks == 10 else {}
    m.update({"overrun": sim.ctx.overrun, **extra})
    (out / "metrics.json").write_text(json.dumps(m, indent=1, ensure_ascii=False))
    return m
