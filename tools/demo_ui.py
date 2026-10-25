"""Web UI over tools/ask_persona.py: tabs Demo (two runs side by side), Personas, Ask. Same data and answers as the CLI.
    .venv/bin/python tools/demo_ui.py [--run DIR] [--other DIR] [--vs P21] [--port 8765] [--offline]
Open http://localhost:8765."""
import argparse
import asyncio
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import ask_persona as ap  # same folder

ROOT = ap.ROOT
SUB = ROOT / "code_kit/cobalt/outputs/submissions/20261024-174556_team-04/submission/runs"
LEFT = RIGHT = ARGS = None


HEADS = {"WHAT YOU SAW, HEARD OR EXPERIENCED:": "events", "YOUR FIRST REACTION THIS WEEK:": "reaction",
         "PRIVATE MESSAGES TO YOU THIS WEEK:": "dms", "POSTS YOU SAW ON SOCIAL MEDIA THIS WEEK:": "posts",
         "QUESTIONS PEOPLE ASKED YOU:": "questions"}
INTER = {}  # id(run) -> list of interactions


def sections(prompt):
    """Split a round-B prompt into the blocks the persona was shown; lists for bullet blocks."""
    out = {v: [] for v in HEADS.values()}
    out["reaction"] = ""
    pat = "(" + "|".join(re.escape(h) for h in HEADS) + ")"
    parts = re.split(pat, prompt.split("STEP 2 OF 2")[0])
    for head, body in zip(parts[1::2], parts[2::2]):
        k = HEADS[head]
        if k == "reaction":
            out[k] = body.strip()
        else:
            out[k] = [l.strip()[2:].strip() for l in body.splitlines() if l.strip().startswith("- ")]
    return out


def detail(run, pid, w):
    """Everything the persona saw, felt and did in one week of one run."""
    c = run.calls.get(next((r["call"] for r in run.weekly.get(pid, []) if r["week"] == w["week"]), ""), {})
    try:
        resp = json.loads(c.get("response") or "{}")
    except json.JSONDecodeError:
        resp = {}
    row = next((r for r in run.weekly[pid] if r["week"] == w["week"]), {})
    sec = sections(c.get("prompt", ""))
    sec["events"] = [{"text": t, "new": t in w["seen"]} for t in sec["events"]
                     if not t.startswith("Nothing unusual")]
    name = lambda i: run.by_id[i]["name"] if i in run.by_id else i
    mine = [i for i in INTER.get(id(run), []) if i["week"] == w["week"]]
    sent = [{"type": i["type"], "to": name(i["to"]) if i.get("to") else i.get("channel", ""), "text": i["text"]}
            for i in mine if i["from"] == pid]
    replies_in = [{"from": name(i["from"]), "text": i["text"]} for i in mine if i.get("to") == pid and i["type"] == "reply"]
    rv = resp.get("app_store_review") or {}
    return {**sec, "thoughts": resp.get("thoughts", ""), "actions": resp.get("actions") or [],
            "review": {"stars": rv.get("stars", 0), "text": rv.get("text", "")} if rv.get("stars") else None,
            "support": resp.get("support_reason") if resp.get("contacted_support") else None,
            "cfpb": bool(resp.get("cfpb_complaint")), "dispute": bool(resp.get("card_dispute")),
            "trust": row.get("trust"), "prev_trust": row.get("prev_trust"), "sent": sent, "replies_in": replies_in,
            "replies_out": [{"to": r.get("to"), "text": r.get("text")} for r in resp.get("replies") or []]}


def week(w, run=None, pid=None):
    if not w:
        return None
    return {**{k: w[k] for k in ("status", "money", "added", "note", "said", "seen")}, **detail(run, pid, w)}


def person(f):
    return {"id": f["id"], "name": f["name"], "group": f["group"], "profile": ap.profile(f),
            "role": f.get("cobalt_role"), "story": f.get("narrative", "")}


def people():
    rows = []
    for f in LEFT.people:
        a = LEFT.last(f["id"])
        b = RIGHT.last(f["id"]) if f["id"] in RIGHT.by_id else {}
        rows.append({**person(f), "status": a.get("status"), "money": a.get("money"),
                     "other_status": b.get("status"), "other_money": b.get("money"), "crises": len(LEFT.crises(f["id"]))})
    return rows


def vs(pid):
    f = LEFT.find(pid)
    lw = {w["week"]: w for w in LEFT.weeks(f["id"])}
    rw = {w["week"]: w for w in RIGHT.weeks(f["id"])}
    out = []
    for k in range(1, 11):
        a, b = lw.get(k), rw.get(k)
        diff = bool(a and b and (a["status"], a["money"], a["added"]) != (b["status"], b["money"], b["added"]))
        sa, sb = set(a["seen"]) if a else set(), set(b["seen"]) if b else set()
        out.append({"week": k, "dates": ap.config.WEEK_DATES[k], "differs": diff, "left": week(a, LEFT, f["id"]), "right": week(b, RIGHT, f["id"]),
                    "only_left": [l for l in (a["seen"] if a else []) if l not in sb],
                    "only_right": [l for l in (b["seen"] if b else []) if l not in sa]})
    end = lambda run: {"name": run.dir.name, "end": run.last(f["id"]).get("status"), "money": run.last(f["id"]).get("money")}
    return {"person": person(f), "weeks": out, "left": end(LEFT), "right": end(RIGHT)}


def ask(pid, question):
    f = LEFT.find(pid)
    res = asyncio.run(ap.answer(ARGS, LEFT, f, ap.context(LEFT, f), question))
    return {"person": person(f), "answer": res["answer"], "weeks": res.get("weeks") or [], "seconds": res["seconds"],
            "source": "record" if res.get("source") == "record" else "cached" if res["cached"] else "live"}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, body, ctype="application/json", code=200):
        b = (body if isinstance(body, str) else json.dumps(body)).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        try:
            if u.path == "/":
                self.send((ROOT / "tools/demo_ui.html").read_text(encoding="utf-8"), "text/html")
            elif u.path == "/api/config":
                self.send({"vs": ARGS.vs, "left": LEFT.dir.name, "right": RIGHT.dir.name, "questions": ap.PRERECORD_QUESTIONS})
            elif u.path == "/api/people":
                self.send(people())
            elif u.path == "/api/vs":
                self.send(vs(q.get("id", [ARGS.vs])[0]))
            else:
                self.send({"error": "not found"}, code=404)
        except SystemExit as e:
            self.send({"error": str(e)}, code=404)

    def do_POST(self):
        if self.path != "/api/ask":
            return self.send({"error": "not found"}, code=404)
        d = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        try:
            self.send(ask(d["id"].strip(), d["q"].strip()))
        except SystemExit as e:
            self.send({"error": str(e)}, code=404)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--run", default=str(SUB / "plan_1"))
    p.add_argument("--other", default=str(SUB / "nodecision_1"))
    p.add_argument("--vs", default="P21")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--model")
    p.add_argument("--fallback", default=str(ap.TOOLS / "prerecorded.json"))
    p.add_argument("--offline", action="store_true")
    ARGS = p.parse_args()
    LEFT, RIGHT = ap.Run(ap.resolve_run(ARGS.run)), ap.Run(ap.resolve_run(ARGS.other))
    for r in (LEFT, RIGHT):
        INTER[id(r)] = ap.jl(r.dir / "interactions.jsonl")
    print(f"http://localhost:{ARGS.port}  {LEFT.dir.name} vs {RIGHT.dir.name}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", ARGS.port), H).serve_forever()
