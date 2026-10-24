"""Vectorized fast simulator: the world mechanics of world.py in numpy, personas driven by the surrogate,
the same persona network (DMs, feed) and support queue. One call simulates B plans against one scenario with
common random numbers (all plans share the same draws), so differences come from the decisions only."""
from __future__ import annotations

import numpy as np

from . import config, crisis, messages, metrics as M, support_queue
from .surrogate import FX, HEADS, INT_T, NAMES, NO_PEER_HEADS, Model, STATIC, build, static_matrix

EFF_IDS = ["savings_boost", "savings_boost_new_money", "instant_dispute_credit", "free_instant_transfers",
           "debit_cashback", "goodwill_credit", "early_pay", "zero_interest_advance", "extra_support",
           "security_pack", "offline_limit"]
FXI = {k: i for i, k in enumerate(FX)}
SI = {k: i for i, k in enumerate(STATIC)}


def _softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(-1, keepdims=True)


class FastWorld:
    def __init__(self, p: dict, people: list[dict], model: Model):
        self.p, self.people, self.model = p, people, model
        self.N = len(people)
        self.S = static_matrix(people)
        # stacked weights of every head (sent_neg sees no peer columns), and the peer-only columns
        cols, Ws, bs, k = {n: i for i, n in enumerate(NAMES)}, [], [], 0
        self.sl = {}
        for h in HEADS:
            Wh = model.W[h] * (model.peer_mask[:, None] if h in NO_PEER_HEADS else 1.0)
            Ws.append(Wh)
            bs.append(model.b[h])
            self.sl[h] = slice(k, k + Wh.shape[1])
            k += Wh.shape[1]
        self.Wall = np.concatenate(Ws, 1).astype(np.float32)
        self.ball = np.concatenate(bs).astype(np.float32)
        peer_cols = [cols["peer_neg"], cols["feed_neg"]] + [cols[f"peer_neg*{t}"] for t in INT_T]
        self.Wpeer = self.Wall[peer_cols]
        self.Tpeer = self.S[:, [STATIC.index(t) for t in INT_T]]
        ids = {f["id"]: i for i, f in enumerate(people)}
        A = np.zeros((self.N, self.N), np.float32)
        for i, f in enumerate(people):
            for t in f.get("ties", []):
                if t["id"] in ids:
                    A[i, ids[t["id"]]] = 1.0
        deg = np.maximum(A.sum(1), 1)
        self.dm = A * np.minimum(1.0, p["network"]["dm_max"] / deg)[None, :]  # dm[i, j]: expected DMs i gets per negative j
        ch = [{c.lower() for c in f.get("social_channels", [])} for f in people]
        self.V = np.array([[1.0 if i != j and ch[i] & ch[j] else 0.0 for j in range(self.N)] for i in range(self.N)], np.float32)
        self.q_post = 0.3  # VARSAYIM: share of negative senders whose message is a public post
        w = p["world"]
        self.app = np.array([w["reach_in_app_daily"] if f.get("checks_app_daily") == "yes" else w["reach_in_app_other"]
                             for f in people], np.float32)
        self.reach = 1 - (1 - w["reach_push"]) * (1 - w["reach_email"]) * (1 - self.app)
        self.nsrc = np.array([len(f.get("news_sources", [])) for f in people], np.float32)
        self.w = np.array([f["w_active"] for f in people], np.float64)
        self.dep, self.dormant = M._deposit_weights(p, people)
        self.masks = {t: np.array([config.in_target(f, flt) for f in people]) for t, flt in messages.TARGETS.items()}
        self.lib = crisis.lib_index()
        self.affected = {a: np.array([crisis.affects(p, a, f) for f in people]) for a in self.lib}
        self.status0 = np.array([0 if f["cobalt_role"] == "main bank" else 1 for f in people])
        # support wait lookup: load ratio x agent level
        cfg = p["support"]
        self.ratios = np.linspace(0, 25, 501)
        self.wait_tab = {extra: np.array([support_queue.week_wait(cfg, r * cfg["base_contact_share"], extra)["wait_min"]
                                          for r in self.ratios]) for extra in (0, 50, 150, 200, 300)}

    # ------------------------------------------------------------------ plan arrays
    def plan_arrays(self, plans: list[list[dict]]):
        B, N = len(plans), self.N
        eff = np.zeros((B, 11, N, len(EFF_IDS)), bool)
        dw = np.zeros((B, 2), int)
        T = np.zeros((B, 2, N), bool)
        mig = np.zeros((B, 2), bool)
        extra = np.zeros((B, 11), int)
        weeks = np.arange(11)
        for b, plan in enumerate(plans):
            for k, d in enumerate(plan[:2]):
                mask = d.get("_mask")
                if mask is None:
                    mask = self.masks.get(d["target"], self.masks["everyone"])
                dw[b, k] = d["week"]
                T[b, k] = mask
                mig[b, k] = "new banking system" in d["message"] or "Dec 12" in d["message"]
                for act in d["actions"]:
                    spec = config.action_spec(self.p, act["action"])
                    e = EFF_IDS.index(spec["id"])
                    dur = None if spec.get("permanent") else spec.get("duration_weeks")
                    on = (weeks >= d["week"]) & ((weeks < d["week"] + dur) if dur else True)
                    if spec["id"] in ("extra_support", "offline_limit"):
                        eff[b, on, :, e] = True
                        if spec["id"] == "extra_support":
                            extra[b, on] += int(config.level_key(spec, act["level"]).replace("+", ""))
                    else:
                        eff[b, on, :, e] |= mask[None, :]
        return eff, dw, T, mig, extra

    def wait(self, ratio: np.ndarray, extra: np.ndarray) -> np.ndarray:
        out = np.empty_like(ratio)
        for e in np.unique(extra):
            key = min(self.wait_tab, key=lambda k: abs(k - e))
            sel = extra == e
            out[sel] = np.interp(ratio[sel], self.ratios, self.wait_tab[key])
        return out

    # ------------------------------------------------------------------ simulate
    def simulate(self, plans: list[list[dict]], surprises: list[dict], overrun: int, rep: int,
                 enabled_ties: bool = True, enabled_feed: bool = True) -> dict:
        p, N, B = self.p, self.N, len(plans)
        wp = p["world"]
        rng = np.random.default_rng(10_000 * rep + 17)
        eff, dw, T, mig, extra = self.plan_arrays(plans)
        status = np.broadcast_to(self.status0, (B, N)).copy()
        trust = np.full((B, N), 4)
        received = np.zeros((B, 2, N), bool)
        sup_prev = np.zeros((B, N), bool)
        wait_prev = np.zeros(B)
        hist = {k: np.zeros((B, N, 10), np.int8) for k in ("status", "money", "added", "neg", "cfpb", "support")}
        bau = rng.random(N) < wp["reach_email"] + 0.15
        base_share = None
        S = self.S
        fragile, social = S[:, SI["fragile"]] > 0, S[:, SI["social"]] > 0
        for w in range(1, 11):
            fx = np.zeros((B, N, len(FX)), np.float32)
            u_msg = rng.random((2, N))
            new_any = np.zeros((B, N), bool)
            for k in range(2):
                live = (dw[:, k:k + 1] > 0) & (w >= dw[:, k:k + 1]) & T[:, k]
                new = live & ~received[:, k] & (u_msg[k] < self.reach)[None, :]
                fx[..., FXI["msg_inbox"]] = np.maximum(fx[..., FXI["msg_inbox"]], received[:, k] & live)
                fx[..., FXI["msg_mig"]] = np.maximum(fx[..., FXI["msg_mig"]], new & mig[:, k:k + 1])
                received[:, k] |= new
                new_any |= new
            fx[..., FXI["msg_new"]] = new_any
            if w == 5:
                fx[..., FXI["bau_email"]] = bau
            if w == 6:
                fx[..., FXI["migration"]] = 1
                fx[..., FXI["overrun"]] = overrun
                u = rng.random((4, N))
                fx[..., FXI["p2p_fail"]] = (S[:, SI["p2p_heavy"]] > 0) & (u[0] < wp["p2p_fail_prob"])
                off = eff[:, 6, 0, EFF_IDS.index("offline_limit")]
                amount = np.array([85, 140, 180, 240, 320])[(u[1] * 5).astype(int)]
                big = u[2] < wp["big_purchase_prob"]
                fx[..., FXI["card_declined"]] = big[None, :] & (amount[None, :] > np.where(off, 250, 100)[:, None])
                fx[..., FXI["biz_declined"]] = (S[:, SI["big_ticket"]] > 0)[None, :] * np.where(off, 0.5, 1.0)[:, None]
                fri = (S[:, SI["paycheck_friday"]] > 0)[None, :]
                ep = eff[:, 6, :, EFF_IDS.index("early_pay")]
                fx[..., FXI["early_pay_helped"]] = fri & ep
                fx[..., FXI["paycheck_trapped"]] = fri & ~ep
            if w == 7 and overrun > 0:
                fx[..., FXI["holding"]] = social
            for s in surprises:
                if s["week"] != w:
                    continue
                aid = s["archetype"]
                aff = self.affected.get(aid, np.zeros(N, bool))
                sev = crisis.SEVERITY.get(s.get("severity", "base"), 1.0)
                pr = np.minimum(0.95, wp["news_exposure_base"] + wp["news_exposure_per_source"] * self.nsrc
                                + (wp["news_exposure_high_severity"] if s.get("severity") == "high" else 0) + 0.25 * aff)
                seen = rng.random(N) < pr
                k = FXI[f"sx_{crisis.cls_of(aid)}"]
                fx[..., k] = np.maximum(fx[..., k], seen * sev)
                fx[..., FXI["sx_affected"]] = np.maximum(fx[..., FXI["sx_affected"]], seen & aff)
            if w in wp["rival_campaign_weeks"]:
                fx[..., FXI["rival_ad"]] = rng.random(N) < wp["rival_exposure"] + 0.3 * S[:, SI["rate_seeker"]]
            for e, name in enumerate(EFF_IDS):
                fx[..., FXI[f"eff_{name}"]] = eff[:, w, :, e]
            if w > 1:
                jit = 0.6 + 0.9 * rng.random(N)
                fx[..., FXI["sup_wait"]] = sup_prev * wait_prev[:, None] * jit[None, :]
                p_res = np.where(wait_prev < 15, p["support"]["resolved_fast"],
                                 np.where(wait_prev < 60, p["support"]["resolved_mid"], p["support"]["resolved_slow"]))
                fx[..., FXI["sup_unresolved"]] = sup_prev & (rng.random(N)[None, :] > p_res[:, None])
            state = np.zeros((B, N, 6), np.float32)
            state[np.arange(B)[:, None], np.arange(N)[None, :], status] = 1
            state[..., 4] = trust / 5.0
            state[..., 5] = w / 10.0
            # all heads in one matmul; peer messages add a small separate term (round A happens before them)
            Z = build(S, state, fx, np.zeros((B, N, 2), np.float32)) @ self.Wall + self.ball
            zs = Z[..., self.sl["sent_neg"]]
            u0 = rng.random(N)
            sent = np.log(u0 / (1 - u0))[None, :] < zs[..., 1] - zs[..., 0]
            peer = np.zeros((B, N, 2), np.float32)
            if enabled_ties:
                peer[..., 0] = sent.astype(np.float32) @ self.dm.T
            if enabled_feed:
                peer[..., 1] = (sent.astype(np.float32) * self.q_post) @ self.V.T
            pn = np.minimum(peer[..., 0], 3) / 3.0
            Xp = np.concatenate([pn[..., None], (np.minimum(peer[..., 1], 4) / 4.0)[..., None],
                                 pn[..., None] * self.Tpeer[None, :, :]], -1)
            Z = Z + Xp @ self.Wpeer
            draws = rng.random((7, N))
            lu = np.log(draws / (1 - draws))

            def sample(head, k):
                z = Z[..., self.sl[head]]
                if z.shape[-1] == 2:  # binary: class 1 iff logit(u) < z1 - z0 (same law as the softmax draw)
                    return (lu[k][None, :] < z[..., 1] - z[..., 0]).astype(np.int8)
                c = np.cumsum(np.exp(np.clip(z, -30, 30)), -1)
                return (draws[k][None, :, None] * c[..., -1:] > c[..., :-1]).sum(-1)
            st = sample("status", 0)
            mo = sample("money", 1)
            ad = sample("added", 2)
            ng = sample("neg_review", 3)
            cf = sample("cfpb", 4)
            sp = sample("support", 5)
            tr = sample("trust", 6) + 1
            status, trust = st, tr
            for key, val in (("status", st), ("money", mo), ("added", ad), ("neg", ng), ("cfpb", cf), ("support", sp)):
                hist[key][..., w - 1] = val
            share = (sp * self.w[None, :]).sum(1) / self.w.sum()
            if base_share is None:
                base_share = np.maximum(p["support"]["base_contact_share"], share)
            ratio = share / base_share
            wait_prev = self.wait(ratio, extra[:, w])
            sup_prev = sp.astype(bool)
        return self.metrics(hist)

    # ------------------------------------------------------------------ metrics (same formulas as metrics.py)
    def metrics(self, h: dict) -> dict:
        m = self.p["metrics"]
        w = self.w
        c = m["exit_conversion"]
        active = (h["status"] <= 1) + (1 - c) * (h["status"] > 1)
        act = 100 * (active * w[None, :, None]).sum(1) / w.sum()
        out = np.array([m["out_kept"], m["out_some"], m["out_most"]])[h["money"]]
        out = np.where(h["status"] == 3, np.maximum(out, m["out_left"]), out)
        out_cum = c * np.maximum.accumulate(out, axis=2)
        inflow = np.array([0.0, m["in_some"], m["in_a_lot"]])[h["added"]]
        b0, b1 = m["base_weeks"]
        in_week = (self.dep[None, :, None] * inflow).sum(1)
        in_net = np.cumsum(in_week - in_week[:, b0 - 1:b1].mean(1, keepdims=True), 1)
        total0 = self.dep.sum() + self.dormant
        dep = 100 * ((self.dep[None, :, None] * (1 - out_cum)).sum(1) + in_net + self.dormant) / total0

        def rate(x):
            return (x * w[None, :, None]).sum(1) / w.sum()
        neg, cf = rate(h["neg"]), rate(h["cfpb"])
        neg_base = np.maximum(m["rate_floor"] / 5, neg[:, b0 - 1:b1].mean(1))
        w0, w1 = m["rating_window"]
        rating = np.minimum(5.0, m["rating_base"] - m["k_rating"] * (neg[:, w0 - 1:w1].mean(1) - neg_base))
        eps = m["rate_floor"]
        monthly = np.stack([cf[:, max(0, i - 3):i + 1].mean(1) for i in range(10)], 1)
        cfpb = m["cfpb_usual"] * (monthly + eps) / (cf[:, b0 - 1:b1].mean(1, keepdims=True) + eps)
        return {"goal_1": act[:, -1], "goal_2": dep[:, -1], "goal_3": rating, "goal_3b": cfpb.max(1),
                "active_weekly": act, "deposits_weekly": dep}


def utility(p: dict, g: dict) -> np.ndarray:
    o = p["optimize"]
    parts = [o["w_goal_1"] * np.clip((g["goal_1"] - 98) / o["tol_goal_1"], -3, 1),
             o["w_goal_2"] * np.clip((g["goal_2"] - 97) / o["tol_goal_2"], -3, 1),
             o["w_goal_3"] * np.clip((g["goal_3"] - 4.3) / o["tol_goal_3"], -3, 1),
             o["w_goal_3b"] * np.clip((240 - g["goal_3b"]) / o["tol_goal_3b"], -3, 1)]
    return sum(parts)


def all_met(g: dict) -> np.ndarray:
    return (g["goal_1"] >= 98) & (g["goal_2"] >= 97) & (g["goal_3"] >= 4.3) & (g["goal_3b"] <= 240)
