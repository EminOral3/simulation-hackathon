"""Support queue feedback: persona contacts this week -> Erlang-C wait -> what contacting personas
experience next week. Erlang C via the Erlang-B recursion (sim_core.erlang_c uses factorials and overflows
at c = 180). Above capacity a fluid approximation: the backlog grows over the overload hours."""
from __future__ import annotations


def erlang_c(c: int, a: float) -> float:
    if a >= c:
        return 1.0
    b = 1.0
    for k in range(1, c + 1):
        b = a * b / (k + a * b)
    return c * b / (c - a * (1 - b))


def wait_min(c: int, lam: float, mu: float, cfg: dict) -> float:
    """Mean wait in minutes; lam, mu per minute."""
    a = lam / mu
    if a < c * 0.999:
        return min(cfg["max_wait_min"], erlang_c(c, a) / (c * mu - lam))
    over = lam / (c * mu) - 1
    return min(cfg["max_wait_min"], max(cfg["target_wait_min"] * 3, over * cfg["peak_hours"] * 60 / 2))


def base_lambda(cfg: dict) -> float:
    """Arrival rate (per minute) that gives the dossier's normal wait with the base staff."""
    c, mu = max(1, round(cfg["base_agents"] * cfg["on_duty_share"])), 1 / cfg["aht_min"]
    lo, hi = 0.0, c * mu * 0.99999
    for _ in range(80):
        mid = (lo + hi) / 2
        if wait_min(c, mid, mu, cfg) < cfg["target_wait_min"]:
            lo = mid
        else:
            hi = mid
    return lo


def week_wait(cfg: dict, contact_share: float, extra_agents: int, baseline_share: float | None = None) -> dict:
    """baseline_share: the run's own contact share in its BAU week (anchor-and-ratio); falls back to the param."""
    lam0 = base_lambda(cfg)
    base = max(cfg["base_contact_share"], baseline_share or 0.0)
    lam = lam0 * contact_share / base
    c = max(1, round((cfg["base_agents"] + extra_agents) * cfg["on_duty_share"]))
    w = wait_min(c, lam, 1 / cfg["aht_min"], cfg)
    resolved = cfg["resolved_fast"] if w < 15 else cfg["resolved_mid"] if w < 60 else cfg["resolved_slow"]
    return {"wait_min": round(w, 1), "agents": c, "load": round(lam / (c / cfg["aht_min"]), 3),
            "contact_share": round(contact_share, 4), "p_resolved": resolved}
