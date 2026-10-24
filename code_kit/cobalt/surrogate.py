"""Surrogate (emulator) of the LLM personas: learns persona-week behaviour from saved LLM runs
(what the persona saw -> what it did) so the optimizer can screen thousands of plans x scenarios in minutes.
The hand-in runs are always the LLM; this model only ranks candidates, and its fidelity is reported.

One feature builder serves training (from logged runs) and the vectorized fast simulator (fastsim.py).

    python -m code_kit.cobalt.surrogate fit [--min-time 20261024-1300]   -> outputs/surrogate/<ts>/model.npz
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np

from . import params as P

STATUSES = ["main bank", "second bank", "dormant", "left"]
MONEY = ["kept", "moved some", "moved most"]
ADDED = ["none", "some", "a lot"]
GROUPS = ["everyday customers", "paycheck customers", "savers with large balances",
          "small business owners with a Cobalt card reader", "students"]
STATIC = [f"g{i}" for i in range(5)] + ["fragile", "vocal", "rumor", "rate_seeker", "p2p_heavy", "paycheck_friday",
                                        "paycheck_in", "bal_hi", "bal_lo", "single_bank", "leader", "role_main",
                                        "fdic_unsure", "fraud_victim", "sms_clicks", "patience_low", "forgive_low",
                                        "social", "checks_daily", "big_ticket"]
FX = ["msg_new", "msg_inbox", "msg_mig", "bau_email", "migration", "overrun", "p2p_fail", "card_declined",
      "biz_declined", "early_pay_helped", "paycheck_trapped", "holding", "sx_access", "sx_trust", "sx_paycheck",
      "sx_fraud", "sx_rate", "sx_support", "sx_merchant", "sx_app", "sx_rival_trouble", "sx_pos_trust", "sx_pos_rate",
      "sx_affected", "rival_ad", "eff_savings_boost", "eff_savings_boost_new_money", "eff_instant_dispute_credit",
      "eff_free_instant_transfers", "eff_debit_cashback", "eff_goodwill_credit", "eff_early_pay",
      "eff_zero_interest_advance", "eff_extra_support", "eff_security_pack", "eff_offline_limit", "sup_wait",
      "sup_unresolved", "dispute_credited"]
STATE = ["st_main", "st_second", "st_dormant", "st_left", "trust_prev", "week"]
PEER = ["peer_neg", "feed_neg"]
INT_E = ["migration", "overrun", "sx_trust", "sx_access", "sx_rate", "sx_paycheck", "sx_fraud", "sx_pos_trust",
         "sx_pos_rate", "sx_rival_trouble", "rival_ad", "eff_savings_boost", "eff_savings_boost_new_money",
         "eff_debit_cashback", "eff_goodwill_credit", "msg_new", "sup_unresolved", "peer_neg", "paycheck_trapped",
         "sup_wait"]
INT_T = ["fragile", "vocal", "rumor", "rate_seeker", "bal_hi", "role_main", "fdic_unsure", "patience_low"]
NAMES = STATIC + STATE + FX + PEER + [f"{e}*{t}" for e in INT_E for t in INT_T]
HEADS = {"status": STATUSES, "money": MONEY, "added": ADDED, "neg_review": [0, 1], "support": [0, 1],
         "cfpb": [0, 1], "trust": [1, 2, 3, 4, 5], "sent_neg": [0, 1]}
NO_PEER_HEADS = {"sent_neg"}  # round A happens before this week's peer messages


def static_row(f: dict) -> list[float]:
    g = [1.0 if f["group"] == x else 0.0 for x in GROUPS]
    return g + [
        f.get("lives_paycheck_to_paycheck") == "yes", f.get("voice_propensity", "").startswith("vocal"),
        f.get("rumor_style", "").startswith("believe"), f.get("moves_money_for_rate") == "yes",
        f.get("uses_p2p") in ("daily", "weekly"), "Friday" in f.get("payday", ""), f.get("paycheck_into_cobalt") == "yes",
        f.get("balance_band") in ("50-250k", "250k+"), f.get("balance_band") == "<1k", f.get("n_banks") == "1",
        f.get("opinion_role", "").startswith("lead"), f.get("cobalt_role") == "main bank",
        f.get("knows_fdic_limit") != "yes", f.get("fraud_or_phishing_victim") == "yes",
        f.get("sms_from_bank_reaction") == "clicks links", f.get("patience") == "low", f.get("forgiveness") == "low",
        bool(f.get("social_channels")), f.get("checks_app_daily") == "yes", "120-300" in f.get("business", "")]


def static_matrix(people: list[dict]) -> np.ndarray:
    return np.array([static_row(f) for f in people], np.float32)


def build(static: np.ndarray, state: np.ndarray, fx: np.ndarray, peer: np.ndarray) -> np.ndarray:
    """static (..,N,|STATIC|), state (..,N,|STATE|), fx (..,N,|FX|) raw, peer (..,N,2) raw -> (..,N,|NAMES|)."""
    fx = fx.copy()
    iw = FX.index("sup_wait")
    fx[..., iw] = np.log1p(fx[..., iw]) / 5.0
    peer = np.stack([np.minimum(peer[..., 0], 3) / 3.0, np.minimum(peer[..., 1], 4) / 4.0], -1)
    static = np.broadcast_to(static, fx.shape[:-1] + (static.shape[-1],))
    base = np.concatenate([static, state, fx, peer], -1)
    idx = {n: i for i, n in enumerate(STATIC + STATE + FX + PEER)}
    E = base[..., [idx[e] for e in INT_E]]
    T = base[..., [idx[t] for t in INT_T]]
    inter = (E[..., :, None] * T[..., None, :]).reshape(E.shape[:-1] + (len(INT_E) * len(INT_T),))
    return np.concatenate([base, inter], -1).astype(np.float32)


def state_row(prev_status: str, prev_trust: int, week: int) -> list[float]:
    return [prev_status == s for s in STATUSES] + [prev_trust / 5.0, week / 10.0]


# ----------------------------------------------------------------------------- dataset from LLM runs
def run_dirs(p: dict, min_time: str = "", models: str = "") -> list[Path]:
    rows = list(csv.DictReader((P.path(p, "outputs") / "index.csv").open()))
    out = []
    for r in rows:
        if r["status"] not in ("ok",) or r["folder"] < min_time or (models and models not in r["model"]) or "mock" in r["model"]:
            continue
        d = P.path(p, "outputs") / "runs" / r["folder"]
        first = (d / "weekly.jsonl").open().readline() if (d / "weekly.jsonl").exists() else ""
        if '"fx"' in first:
            out.append(d)
    return out


def dataset(dirs: list[Path]) -> dict:
    X, Y, G = [], {h: [] for h in HEADS}, []
    for gi, d in enumerate(dirs):
        people = {json.loads(l)["id"]: json.loads(l) for l in (d / "personas.jsonl").read_text().splitlines() if l.strip()}
        stat = {pid: static_row(f) for pid, f in people.items()}
        for line in (d / "weekly.jsonl").read_text().splitlines():
            r = json.loads(line)
            if not r.get("parsed", True):
                continue
            fx = np.array([[r["fx"].get(k, 0.0) for k in FX]], np.float32)
            x = build(np.array([stat[r["persona"]]], np.float32),
                      np.array([state_row(r["prev_status"], r["prev_trust"], r["week"])], np.float32), fx,
                      np.array([[r.get("peer_neg", 0), r.get("feed_neg", 0)]], np.float32))[0]
            X.append(x)
            G.append(gi)
            Y["status"].append(STATUSES.index(r["status"]))
            Y["money"].append(MONEY.index(r["money"]))
            Y["added"].append(ADDED.index(r.get("added_money", "none")) if r.get("added_money", "none") in ADDED else 0)
            Y["neg_review"].append(int(1 <= r.get("review_stars", 0) <= 2))
            Y["support"].append(int(r.get("contacted_support", False)))
            Y["cfpb"].append(int(r.get("cfpb", False)))
            Y["trust"].append(min(5, max(1, int(r.get("trust", 4)))) - 1)
            Y["sent_neg"].append(int(r.get("sent_neg", 0)))
    return {"X": np.array(X, np.float32), "Y": {h: np.array(v) for h, v in Y.items()}, "groups": np.array(G),
            "dirs": [d.name for d in dirs]}


class Model:
    """Multinomial logistic heads with plain numpy prediction (softmax(X W + b))."""

    def __init__(self, W: dict, b: dict, meta: dict):
        self.W, self.b, self.meta = W, b, meta
        self.peer_mask = np.array([n not in PEER and not any(n.startswith(pp + "*") for pp in PEER) for n in NAMES], np.float32)

    def proba(self, head: str, X: np.ndarray) -> np.ndarray:
        Xh = X * self.peer_mask if head in NO_PEER_HEADS else X
        z = Xh @ self.W[head] + self.b[head]
        z -= z.max(-1, keepdims=True)
        e = np.exp(z)
        return e / e.sum(-1, keepdims=True)

    def save(self, path: Path):
        np.savez(path, **{f"W_{h}": w for h, w in self.W.items()}, **{f"b_{h}": v for h, v in self.b.items()},
                 meta=json.dumps(self.meta))

    @classmethod
    def load(cls, path: Path) -> "Model":
        z = np.load(path, allow_pickle=False)
        W = {k[2:]: z[k] for k in z.files if k.startswith("W_")}
        b = {k[2:]: z[k] for k in z.files if k.startswith("b_")}
        return cls(W, b, json.loads(str(z["meta"])))


def fit(ds: dict, C: float = 0.5) -> Model:
    from sklearn.linear_model import LogisticRegression
    X = ds["X"]
    W, b, meta = {}, {}, {"n_rows": int(len(X)), "runs": ds["dirs"], "heads": {}}
    mask = np.array([n not in PEER and not any(n.startswith(pp + "*") for pp in PEER) for n in NAMES], np.float32)
    for h, classes in HEADS.items():
        y = ds["Y"][h]
        K = len(classes)
        counts = np.bincount(y, minlength=K)
        Xh = X * mask if h in NO_PEER_HEADS else X
        present = np.where(counts > 0)[0]
        Wh = np.zeros((X.shape[1], K), np.float32)
        bh = np.full(K, -20.0, np.float32)
        if len(present) == 1:
            bh[present[0]] = 0.0
        else:
            m = LogisticRegression(C=C, max_iter=400)
            m.fit(Xh, y)
            coef = m.coef_ if len(present) > 2 else np.vstack([-m.coef_[0] / 2, m.coef_[0] / 2])
            icpt = m.intercept_ if len(present) > 2 else np.array([-m.intercept_[0] / 2, m.intercept_[0] / 2])
            for j, c in enumerate(m.classes_):
                Wh[:, c] = coef[j]
                bh[c] = icpt[j]
        W[h], b[h] = Wh, bh
        meta["heads"][h] = {"counts": counts.tolist()}
    return Model(W, b, meta)


def heldout_check(ds: dict, C: float = 0.5, k: int = 4) -> dict:
    """Run-level k-fold: log-loss of the surrogate vs a base-rate model per head (persona-week level)."""
    groups = ds["groups"]
    ug = np.unique(groups)
    out = {h: {"surrogate": [], "base_rate": []} for h in HEADS}
    for fold in range(k):
        test_g = ug[fold::k]
        te = np.isin(groups, test_g)
        sub = {"X": ds["X"][~te], "Y": {h: v[~te] for h, v in ds["Y"].items()}, "dirs": []}
        m = fit(sub, C)
        for h, classes in HEADS.items():
            y = ds["Y"][h][te]
            if not len(y):
                continue
            pr = np.clip(m.proba(h, ds["X"][te]), 1e-6, 1)
            base = np.bincount(sub["Y"][h], minlength=len(classes)) + 0.5
            base = base / base.sum()
            out[h]["surrogate"].append(float(-np.log(pr[np.arange(len(y)), y]).mean()))
            out[h]["base_rate"].append(float(-np.log(base[y]).mean()))
    return {h: {kk: round(float(np.mean(v)), 4) for kk, v in d.items() if v} for h, d in out.items()}


def latest(p: dict) -> Path:
    base = P.path(p, "outputs") / "surrogate"
    ds = sorted(d for d in base.iterdir() if (d / "model.npz").exists())
    if not ds:
        raise FileNotFoundError("no surrogate yet: python -m code_kit.cobalt.surrogate fit")
    return ds[-1] / "model.npz"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fit"])
    ap.add_argument("--min-time", default="")
    ap.add_argument("--models", default="", help="substring filter on run model, e.g. gemini-3.5-flash-lite")
    ap.add_argument("--C", type=float, default=0.5)
    ap.add_argument("--no-check", action="store_true")
    a = ap.parse_args()
    p = P.load()
    dirs = run_dirs(p, a.min_time, a.models)
    ds = dataset(dirs)
    print(f"{len(dirs)} runs, {len(ds['X'])} persona-weeks, {ds['X'].shape[1]} features")
    m = fit(ds, a.C)
    if not a.no_check and len(dirs) >= 4:
        m.meta["heldout_logloss"] = heldout_check(ds, a.C)
        for h, v in m.meta["heldout_logloss"].items():
            print(f"  {h:10s} surrogate {v.get('surrogate')}  base-rate {v.get('base_rate')}")
    out = P.path(p, "outputs") / "surrogate" / datetime.now().strftime("%Y%m%d-%H%M%S")
    out.mkdir(parents=True, exist_ok=False)
    m.save(out / "model.npz")
    (out / "meta.json").write_text(json.dumps(m.meta, indent=1))
    print(out / "model.npz")


if __name__ == "__main__":
    main()
