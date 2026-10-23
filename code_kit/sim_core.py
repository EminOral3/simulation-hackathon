"""Simülasyon çekirdeği: Monte Carlo, SimPy DES + M/M/c analitik sağlama, ağ kaskadı/Bass, stok-akış (SD)."""
from __future__ import annotations
import math
from typing import Callable

import numpy as np


# ---------------------------------------------------------------- Monte Carlo
def monte_carlo(model: Callable[[np.random.Generator], float], n: int = 5000, seed: int = 0) -> np.ndarray:
    """model(rng)->skaler çıktı. n tekrar. Aralık için `validation.bootstrap_ci` veya np.percentile."""
    rng = np.random.default_rng(seed)
    return np.array([model(rng) for _ in range(n)])


def summarize(x: np.ndarray, qs=(5, 50, 95)) -> dict:
    return {"mean": float(np.mean(x)), **{f"p{q}": float(np.percentile(x, q)) for q in qs}}


# ---------------------------------------------------------------- DES (SimPy)
def erlang_c(c: int, lam: float, mu: float) -> float:
    """P(bekleme) M/M/c. Kararlılık: lam < c*mu."""
    a = lam / mu
    rho = a / c
    if rho >= 1:
        return 1.0
    s = sum(a ** k / math.factorial(k) for k in range(c))
    top = a ** c / (math.factorial(c) * (1 - rho))
    return top / (s + top)


def mmc_analytic(c: int, lam: float, mu: float) -> dict:
    """M/M/c kapalı form: Wq (ort. bekleme), Lq, rho, P(wait)."""
    rho = lam / (c * mu)
    if rho >= 1:
        return {"rho": rho, "stable": False}
    pw = erlang_c(c, lam, mu)
    wq = pw / (c * mu - lam)
    return {"rho": rho, "p_wait": pw, "Wq": wq, "Lq": lam * wq, "W": wq + 1 / mu, "stable": True}


def simulate_queue(c: int, lam: float, mu: float, horizon: float = 5000.0, warmup: float = 500.0,
                   seed: int = 0, service: Callable | None = None, patience: Callable | None = None) -> dict:
    """SimPy çok sunuculu kuyruk. service(rng)->süre (varsayılan Exp(mu)); patience(rng)->sabır (None: yok;
    sabır dolunca müşteri terk eder = abandonment/churn analojisi)."""
    import simpy
    rng = np.random.default_rng(seed)
    env = simpy.Environment()
    srv = simpy.Resource(env, capacity=c)
    waits, abandoned, served = [], [0], [0]
    service = service or (lambda r: r.exponential(1 / mu))

    def customer(env):
        t0 = env.now
        with srv.request() as req:
            if patience is None:
                yield req
            else:
                res = yield req | env.timeout(patience(rng))
                if req not in res:
                    if t0 > warmup:
                        abandoned[0] += 1
                    return
            if t0 > warmup:
                waits.append(env.now - t0)
            yield env.timeout(service(rng))
            if t0 > warmup:
                served[0] += 1

    def arrivals(env):
        while True:
            yield env.timeout(rng.exponential(1 / lam))
            env.process(customer(env))

    env.process(arrivals(env))
    env.run(until=horizon)
    w = np.array(waits) if waits else np.array([0.0])
    tot = served[0] + abandoned[0]
    return {"Wq": float(w.mean()), "p95_wait": float(np.percentile(w, 95)), "served": served[0],
            "abandon_rate": abandoned[0] / tot if tot else 0.0}


def replicate_queue(reps: int = 20, **kw) -> dict:
    """Bağımsız replikasyonlar -> ortalama ve %95 t-aralığı (Wq)."""
    from scipy import stats
    xs = np.array([simulate_queue(seed=s, **kw)["Wq"] for s in range(reps)])
    h = stats.t.ppf(0.975, reps - 1) * xs.std(ddof=1) / math.sqrt(reps)
    return {"Wq_mean": float(xs.mean()), "ci_low": float(xs.mean() - h), "ci_high": float(xs.mean() + h)}


# ---------------------------------------------------------------- ağ kaskadı / Bass
def er_graph(n: int, avg_deg: float, seed: int = 0) -> list[list[int]]:
    rng = np.random.default_rng(seed)
    p = avg_deg / (n - 1)
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in np.nonzero(rng.random(n - i - 1) < p)[0] + i + 1:
            adj[i].append(int(j)); adj[int(j)].append(i)
    return adj


def ba_graph(n: int, m: int = 3, seed: int = 0) -> list[list[int]]:
    """Barabasi-Albert (heavy-tail; influencer yapısı)."""
    rng = np.random.default_rng(seed)
    adj = [[] for _ in range(n)]
    targets = list(range(m)); repeated = []
    for v in range(m, n):
        for t in set(targets):
            adj[v].append(t); adj[t].append(v)
        repeated += list(set(targets)) + [v] * m
        targets = [repeated[i] for i in rng.integers(0, len(repeated), m)]
    return adj


def cascade(adj, seeds: list[int], p: float = 0.1, threshold: float | None = None,
            q_bass: float = 0.0, p_bass: float = 0.0, steps: int = 50, seed: int = 0) -> np.ndarray:
    """Tek iskelet, üç mod:
    - Bağımsız kaskad (IC) : threshold=None -> her aktif komşu p ile bulaştırır (SIR benzeri, tek atış).
    - Eşik modeli          : threshold=θ -> aktif komşu oranı ≥ θ ise aktifleşir.
    - Bass                 : p_bass (dış etki/reklam) + q_bass*oran (ağ etkisi) her adımda ek aktifleşme olasılığı.
    Dönüş: adım başına kümülatif aktif sayısı."""
    rng = np.random.default_rng(seed)
    n = len(adj)
    active = np.zeros(n, bool); active[seeds] = True
    frontier = set(seeds)
    hist = [active.sum()]
    for _ in range(steps):
        new = set()
        if threshold is None:
            for u in frontier:  # IC: her yeni aktif bir kez dener
                for v in adj[u]:
                    if not active[v] and rng.random() < p:
                        new.add(v)
        else:
            for v in range(n):
                if not active[v] and adj[v]:
                    if active[adj[v]].mean() >= threshold:
                        new.add(v)
        if p_bass or q_bass:
            for v in np.nonzero(~active)[0]:
                frac = active[adj[v]].mean() if adj[v] else 0.0
                if rng.random() < p_bass + q_bass * frac:
                    new.add(int(v))
        for v in new:
            active[v] = True
        frontier = new
        hist.append(active.sum())
        if not new and threshold is not None and not (p_bass or q_bass):
            break
    return np.array(hist)


def bass_curve(m: float, p: float, q: float, T: int = 50) -> np.ndarray:
    """Klasik Bass (ODE, Euler dt=1): dN = (p + q N/m)(m - N). Ağsız referans."""
    N = np.zeros(T + 1)
    for t in range(T):
        N[t + 1] = N[t] + (p + q * N[t] / m) * (m - N[t])
    return N


# ---------------------------------------------------------------- stok-akış (SD)
def stock_flow(stocks0: dict[str, float], flows: dict[str, Callable[[dict, float], float]],
               links: dict[str, dict[str, float]], T: float = 50.0, dt: float = 0.25) -> dict[str, np.ndarray]:
    """Euler entegrasyonu. flows: {akış_adı: f(stocks, t)->hız}. links: {akış: {stok: +1 (giriş) | -1 (çıkış)}}.
    Örnek: nüfus-adopsiyon, envanter, birikim. Geri besleme f içinde stoklara bakarak kurulur."""
    steps = int(T / dt)
    st = dict(stocks0)
    out = {k: [v] for k, v in st.items()}
    for i in range(steps):
        t = i * dt
        rates = {f: fn(st, t) for f, fn in flows.items()}
        for f, r in rates.items():
            for s, sign in links[f].items():
                st[s] += sign * r * dt
        for k in st:
            out[k].append(st[k])
    return {k: np.array(v) for k, v in out.items()}
