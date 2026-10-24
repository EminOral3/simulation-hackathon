"""Loads docs/talp_db data, validates decisions against the menu and budget, and answers
'which decision effects are active for this persona in this week'."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from . import params as P

WEEK_DATES = {1: "Nov 2-8", 2: "Nov 9-15", 3: "Nov 16-22", 4: "Nov 23-29", 5: "Nov 30-Dec 6",
              6: "Dec 7-13", 7: "Dec 14-20", 8: "Dec 21-27", 9: "Dec 28-Jan 3", 10: "Jan 4-10"}
SEASON = {4: "It is Thanksgiving and Black Friday week.", 5: "Cyber Monday week; holiday shopping is under way.",
          6: "Holiday shopping season.", 7: "Last full week before Christmas.", 8: "Christmas week.",
          9: "New Year week; card bills and New Year resolutions.", 10: "First full week of January."}
STATUSES = ["main bank", "second bank", "dormant", "left"]
MONEY = ["kept", "moved some", "moved most"]


def _json(p: dict, rel: str):
    return json.loads((P.path(p, "talp_db") / rel).read_text())


@lru_cache(maxsize=None)
def _cached(talp_db: str, rel: str):
    return json.loads((Path(talp_db) / rel).read_text())


def data(p: dict, name: str):
    rel = {"priors": "data/theory/population_priors.json", "design": "data/theory/persona_design.json",
           "schema": "data/theory/persona_schema.json", "metric_spec": "data/theory/metric_spec.json",
           "crisis_kb": "data/crises/crisis_kb.json", "menu": "data/crises/decision_menu.json"}[name]
    return _cached(str(P.path(p, "talp_db")), rel)


# ----------------------------------------------------------------------------- decisions
class DecisionError(ValueError):
    pass


def load_decisions(p: dict, file: str | None) -> tuple[list[dict], dict]:
    """Decision file: {"decisions": [... exactly as locked ...], "filters": {"1": {...}, "2": {...}}}.
    filters (ours, not part of the locked decision): {"groups": [...], "where": {field: value or [values]}}."""
    if not file or file == "none":
        return [], {}
    path = Path(file)
    if not path.exists():
        path = P.path(p, "decisions_dir") / file
    if not path.exists() and not str(file).endswith(".json"):
        path = P.path(p, "decisions_dir") / f"{file}.json"
    d = json.loads(path.read_text())
    return d["decisions"], d.get("filters", {})


def _norm(label: str) -> str:
    return label.lower().replace("→", "->").replace("–", "-").strip()


def _menu_index(p: dict) -> dict:
    return {_norm(a["label"]): a for a in data(p, "menu")["actions"]}


def level_key(spec: dict, level: str) -> str:
    """Menu level for a level as written on the dashboard ('+150 staff' -> '+150', 'Enable' -> 'on')."""
    if level in spec["levels"]:
        return level
    lv = level.strip().lower()
    if lv in ("enable", "enabled") and "on" in spec["levels"]:
        return "on"
    for k in sorted(spec["levels"], key=len, reverse=True):
        if lv.startswith(k.lower()):
            return k
    raise DecisionError(f"level {level!r} not in menu for {spec['label']!r}: {list(spec['levels'])}")


def action_spec(p: dict, label: str) -> dict:
    a = _menu_index(p).get(_norm(label))
    if a is None:
        raise DecisionError(f"action not in menu: {label!r}")
    return a


def decision_cost(p: dict, dec: dict) -> int:
    menu = data(p, "menu")
    cost = 0
    for act in dec["actions"]:
        spec = action_spec(p, act["action"])
        cost += spec["levels"][level_key(spec, act["level"])]
    for ch in dec.get("channels", []):
        key = ch.lower().replace(" ", "_").replace("-", "_")
        if key in ("sms", "text", "text_message"):
            key = "text_message_all"
        if key in ("in_app_message", "inapp"):
            key = "in_app"
        if key not in menu["channels"]:
            raise DecisionError(f"unknown channel {ch!r}; use {list(menu['channels'])}")
        cost += menu["channels"][key]
    return cost


def budget_check(p: dict, decisions: list[dict]) -> dict:
    """Raises DecisionError when a board would not approve the decision set. Returns cost summary."""
    if len(decisions) > 2:  # the hand-in needs exactly 2 (check.py); experiments may test one
        raise DecisionError(f"at most 2 decisions, got {len(decisions)}")
    total = 0
    per = []
    for i, d in enumerate(decisions, 1):
        if not (isinstance(d.get("week"), int) and 1 <= d["week"] <= 10):
            raise DecisionError(f"decision {i}: week must be 1-10")
        if not 1 <= len(d.get("actions", [])) <= 3:
            raise DecisionError(f"decision {i}: 1 to 3 actions")
        msg = d.get("message", "")
        if not msg.strip() or len(msg) > 600:
            raise DecisionError(f"decision {i}: message must be 1-600 characters (is {len(msg)})")
        why = d.get("why", "")
        lines = why if isinstance(why, list) else [l for l in str(why).split("\n") if l.strip()]
        if len(lines) != 3:
            raise DecisionError(f"decision {i}: 'why' must be exactly three lines")
        if not d.get("target") or not d.get("channels"):
            raise DecisionError(f"decision {i}: needs target and channels")
        c = decision_cost(p, d)
        per.append(c)
        total += c
    budget = data(p, "menu")["budget_usd"]
    if total > budget:
        raise DecisionError(f"total cost ${total:,} exceeds budget ${budget:,}")
    return {"total_usd": total, "per_decision_usd": per, "budget_usd": budget}


def in_target(persona: dict, flt: dict | None) -> bool:
    if not flt:
        return True
    if flt.get("groups") and persona["group"] not in flt["groups"]:
        return False
    for k, v in (flt.get("where") or {}).items():
        val = persona.get(k, persona.get("design_levels", {}).get(k))
        if isinstance(v, list):
            if val not in v:
                return False
        elif val != v:
            return False
    return True


def active_effects(p: dict, decisions: list[dict], filters: dict, persona: dict, week: int) -> dict:
    """{action_id: {"level": ..., "since": week_started, "decision": i}} for actions reaching this persona now.
    Capacity-type actions (extra support) are company-wide and returned regardless of target."""
    out = {}
    for i, d in enumerate(decisions, 1):
        if week < d["week"]:
            continue
        targeted = in_target(persona, filters.get(str(i)))
        for act in d["actions"]:
            spec = action_spec(p, act["action"])
            dur = spec.get("duration_weeks")
            if spec.get("permanent"):
                dur = None
            if dur is not None and week >= d["week"] + dur:
                continue
            if spec["id"] in ("extra_support", "offline_limit") or targeted:
                out[spec["id"]] = {"level": level_key(spec, act["level"]), "since": d["week"], "decision": i}
    return out


def extra_agents(p: dict, decisions: list[dict], week: int) -> int:
    n = 0
    for d in decisions:
        if week < d["week"]:
            continue
        for act in d["actions"]:
            spec = action_spec(p, act["action"])
            if spec["id"] == "extra_support" and week < d["week"] + spec.get("duration_weeks", 4):
                n += int(level_key(spec, act["level"]).replace("+", ""))
    return n
