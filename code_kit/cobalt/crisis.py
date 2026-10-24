"""Crisis library glue (docs/talp_db/docs/crises/CRISIS_PLAYBOOK.md). Classifies dashboard announcements
into archetypes, produces world-feed items for exposed personas and checks results against sanity bounds.
calibration_anchors and real-case outcomes never reach a persona prompt."""
from __future__ import annotations

import json
import random
from functools import lru_cache

from . import config
from . import params as P


def load_announcements(p: dict, surprises: bool) -> list[dict]:
    items = json.loads(P.path(p, "announcements").read_text())["items"]
    return [a for a in items if surprises or not a.get("surprise", True)]


def archetypes(p: dict) -> dict:
    return {a["id"]: a for a in config.data(p, "crisis_kb")["archetypes"]}


@lru_cache(maxsize=1)
def library() -> dict:
    return json.loads((P.PKG / "data" / "surprise_library.json").read_text())


@lru_cache(maxsize=1)
def lib_index() -> dict:
    return {a["id"]: a for a in library()["archetypes"]}


def cls_of(archetype_id: str) -> str:
    a = lib_index().get(archetype_id)
    return a["cls"] if a else "trust"


SEVERITY = {"low": 0.6, "base": 1.0, "high": 1.5}


def classify(p: dict, text: str) -> list[str]:
    lo = text.lower()
    scored = sorted(((sum(s.lower() in lo for s in a["signals"]), aid) for aid, a in archetypes(p).items()), reverse=True)
    return [aid for s, aid in scored[:2] if s > 0]


def reading(p: dict, ann: dict) -> dict:
    ids = ann.get("archetypes") or classify(p, ann["text"])
    return {"archetypes": ids, "severity": ann.get("severity", "base")}


def world_items(p: dict, archetype_id: str, rng: random.Random, k: int = 2) -> list[str]:
    a = archetypes(p).get(archetype_id)
    items = a.get("world_feed_templates", []) if a else library()["feed_templates"].get(cls_of(archetype_id), [])
    out = []
    for t in rng.sample(items, min(k, len(items))):
        kind, _, body = t.replace("USD ", "$").partition(":")
        out.append(f"{kind}: {body.strip().strip(chr(39))}" if body and kind in ("News", "Social", "Rival ad") else t)
    return out


def affects(p: dict, archetype_id: str, persona: dict) -> bool:
    """Rough match between an archetype's key attributes and a persona (used for exposure)."""
    a = archetypes(p).get(archetype_id, {})
    keys = " ".join(a.get("key_attributes", []) + a.get("most_affected", [])).lower()
    if not a:  # library-only (good) archetypes
        c = cls_of(archetype_id)
        return (c == "pos_rate" and persona.get("moves_money_for_rate") == "yes") or (
            c == "rival_trouble" and persona.get("n_banks") != "1") or c == "pos_trust"
    g = persona["group"].split(" ")[0]
    hits = [g in keys,
            persona.get("lives_paycheck_to_paycheck") == "yes" and "paycheck" in keys,
            persona.get("uses_p2p") == "daily" and "peer" in keys,
            persona.get("fraud_or_phishing_victim") == "yes" and ("fraud" in keys or "phishing" in keys),
            persona.get("moves_money_for_rate") == "yes" and "rate" in keys,
            persona.get("knows_fdic_limit") != "yes" and "fdic" in keys]
    return any(hits)


def sanity_check(p: dict, weekly_active: list[float], deposits_pct: float) -> list[str]:
    s, warn = p["sanity"], []
    prev = 100.0
    for w, a in enumerate(weekly_active, 1):
        if prev - a > s["weekly_active_loss_max_pct"]:
            warn.append(f"week {w}: active fell {prev - a:.2f} points in one week (> {s['weekly_active_loss_max_pct']})")
        prev = a
    if weekly_active and 100 - weekly_active[-1] > s["total_active_loss_max_pct"]:
        warn.append(f"10-week active loss {100 - weekly_active[-1]:.2f}% (> {s['total_active_loss_max_pct']}); TSB 2018 lost ~1.5%/year")
    if 100 - deposits_pct > s["deposit_outflow_max_pct"]:
        warn.append(f"deposit outflow {100 - deposits_pct:.2f}% (> {s['deposit_outflow_max_pct']})")
    return warn
