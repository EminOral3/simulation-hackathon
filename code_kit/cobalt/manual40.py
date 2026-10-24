"""Offline adapter for the opt-in assistant-authored 40-person reference panel."""
from __future__ import annotations

import copy
from collections import Counter

from . import config, network


def adapt(source: dict, p: dict) -> list[dict]:
    """Preserve the source profiles and add engine fields; no API or simulation."""
    rows = source["personas"]
    if len(rows) != 40 or len({f["id"] for f in rows}) != 40:
        raise ValueError("manual40 requires exactly 40 unique source personas")
    counts = Counter(f["group"] for f in rows)
    priors = config.data(p, "priors")["groups"]
    if set(counts) != set(priors) or any(n != 8 for n in counts.values()):
        raise ValueError("manual40 requires 8 source personas per dossier group")
    people = []
    for original in rows:
        f = copy.deepcopy(original)
        f["reference_source"] = copy.deepcopy(original)
        group = f["group"]
        gp = priors[group]
        f["weight_customers"] = gp["customers"] / counts[group]
        f["active_share"] = gp["active_share"]
        f["w_active"] = f["weight_customers"] * f["active_share"]
        f["location"] = f["state_city_type"]
        f["clone_of"] = None
        f["opinion_role"] = "lead (people ask me)" if original["opinion_role"] == "leads" else "follow (I ask others)"
        f["rumor_style"] = "believe and pass them on" if original["rumor_style"] == "believes" else "check before believing"
        vocal = original["voice_propensity"] == "vocal"
        f["voice_propensity"] = "vocal: I complain, post and write reviews" if vocal else "quiet: I rarely complain in public"
        f["social_channels"] = [x for x in f["news_sources"] if x in {"Facebook", "X", "Instagram", "TikTok", "Reddit", "YouTube"}]
        # Explicit adapter assumptions, not observations or new biography generation.
        f["checks_app_daily"] = "yes" if f["cobalt_role"] == "main bank" else "no"
        f["autopays"] = "2" if f["cobalt_role"] == "main bank" else "0"
        f["other_bank"] = "none" if f["n_banks"] == "1" else "another bank (not specified)"
        if f["paycheck_into_cobalt"] != "yes":
            f["payday"] = "not paid into Cobalt"
        elif original["payday"] == "Friday biweekly":
            f["payday"] = "every other Friday (next one: Friday, December 11)"
        elif original["payday"] == "semi-monthly 15th/last":
            f["payday"] = "15th and last day of the month"
        constraints = []
        if f["paycheck_into_cobalt"] == "yes":
            constraints.append("my paycheck is deposited here")
        if f["autopays"] == "2":
            constraints.append("2 bills on autopay (adapter assumption)")
        if f["n_banks"] == "1":
            constraints.append("I have no other bank account")
        if group == "small business owners with a Cobalt card reader":
            amount = f["typical_sale_usd"]
            # world.py recognizes this exact ticket-category token.
            band = "120-300" if amount > 100 else "15-60"
            f["business"] = (
                f"{f['occupation']}; typical card sale amount USD {amount}; "
                f"engine ticket category {band}; "
                f"{'thin cash flow' if f['lives_paycheck_to_paycheck'] == 'yes' else 'some cash cushion'}"
            )
            constraints.append("my card reader pays out into Cobalt")
        f["switch_cost"] = "; ".join(constraints) if constraints else "I already have another bank account."
        # Descriptive groupings only: this panel is not a factorial design.
        f["design_levels"] = {
            "bank_role": f["cobalt_role"],
            "fragility": f["lives_paycheck_to_paycheck"],
            "voice": original["voice_propensity"],
            "info_style": original["rumor_style"],
        }
        f["provenance"]["runtime_adapter"] = "manual40_v1"
        f["provenance"]["population_weights"] = "ASSUMPTION: equal within each group using existing priors"
        f["provenance"]["adapter_assumptions"] = [
            "checks_app_daily inferred from bank role, not observed",
            "autopays is 2 for main bank, otherwise 0; not observed",
            "initial dynamic state follows unchanged engine, not source dynamic fields",
        ]
        people.append(f)
    ties = network.build(p, people)
    for f in people:
        f["ties"] = ties[f["id"]]
    return people
