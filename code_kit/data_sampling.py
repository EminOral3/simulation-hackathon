"""Veri katmanı: CSV örnekleme, IPF/raking, sentetik üretim, vekil veri yükleyici.
Bağımlılık: numpy, pandas. Tüm sentetik/vekil çıktılar `attrs['provenance']` ile etiketlenir."""
from __future__ import annotations
import numpy as np
import pandas as pd


def sample_csv(path: str, n: int | None = None, frac: float | None = None,
               stratify: str | None = None, seed: int = 0, **read_kw) -> pd.DataFrame:
    """CSV'den (opsiyonel katmanlı) örnekleme."""
    df = pd.read_csv(path, **read_kw)
    if n is None and frac is None:
        return df
    if stratify:
        f = frac if frac is not None else n / len(df)
        out = df.groupby(stratify, group_keys=False).apply(
            lambda g: g.sample(frac=min(1.0, f), random_state=seed))
        return out.reset_index(drop=True)
    return df.sample(n=n, frac=frac, random_state=seed).reset_index(drop=True)


def ipf(df: pd.DataFrame, margins: dict[str, dict], weights: pd.Series | None = None,
        max_iter: int = 100, tol: float = 1e-6) -> pd.Series:
    """Iterative proportional fitting (raking). margins: {kolon: {kategori: hedef_oran}}.
    Dönüş: toplamı len(df) olan satır ağırlıkları."""
    w = np.ones(len(df)) if weights is None else weights.to_numpy(float).copy()
    n = len(df)
    for _ in range(max_iter):
        maxdiff = 0.0
        for col, target in margins.items():
            tot = sum(target.values())
            cur = pd.Series(w).groupby(df[col].to_numpy()).sum() / w.sum()
            for cat, tgt in target.items():
                c = cur.get(cat, 0.0)
                if c <= 0:
                    continue  # hücrede örnek yok: ağırlıklandırılamaz
                ratio = (tgt / tot) / c
                w[(df[col] == cat).to_numpy()] *= ratio
                maxdiff = max(maxdiff, abs(ratio - 1))
        if maxdiff < tol:
            break
    w = w / w.sum() * n
    return pd.Series(w, index=df.index, name="weight")


def synth_population(n: int, margins: dict[str, dict], seed: int = 0,
                     corr_pairs: dict | None = None) -> pd.DataFrame:
    """Marjinallerden bağımsız sentetik popülasyon (varsayım: kolonlar bağımsız).
    corr_pairs ile {(a,b): rho} Gauss-copula ile bağımlılık eklenebilir (ordinal olmayan için kaba)."""
    rng = np.random.default_rng(seed)
    cols = list(margins)
    z = rng.standard_normal((n, len(cols)))
    if corr_pairs:
        C = np.eye(len(cols))
        for (a, b), r in corr_pairs.items():
            i, j = cols.index(a), cols.index(b)
            C[i, j] = C[j, i] = r
        z = z @ np.linalg.cholesky(C).T
    from scipy.stats import norm
    u = norm.cdf(z)
    data = {}
    for k, col in enumerate(cols):
        cats = list(margins[col]); p = np.array([margins[col][c] for c in cats], float)
        cum = np.cumsum(p / p.sum())
        data[col] = np.array(cats, dtype=object)[np.minimum(np.searchsorted(cum, u[:, k]), len(cats) - 1)]
    df = pd.DataFrame(data)
    df.attrs["provenance"] = "SENTETİK (varsayım: marjinaller verildi)"
    return df


def synth_choice_data(n: int, seed: int = 0, price_beta: float = -0.04,
                      segments: dict | None = None) -> pd.DataFrame:
    """Fiyat-tercih arketipi için sentetik veri: segment, fiyat, satın alma (lojistik gerçek model)."""
    rng = np.random.default_rng(seed)
    segments = segments or {"genc": 0.4, "orta": 0.4, "yasli": 0.2}
    seg = rng.choice(list(segments), n, p=np.array(list(segments.values())) / sum(segments.values()))
    base = {"genc": 1.0, "orta": 1.5, "yasli": 0.5}
    sens = {"genc": 1.3, "orta": 1.0, "yasli": 0.7}
    price = rng.uniform(20, 100, n)
    util = np.array([base.get(s, 1.0) for s in seg]) + np.array([sens.get(s, 1.0) for s in seg]) * price_beta * price + 2.0
    p = 1 / (1 + np.exp(-util))
    df = pd.DataFrame({"segment": seg, "price": price, "buy": (rng.random(n) < p).astype(int), "true_p": p})
    df.attrs["provenance"] = "SENTETİK (gerçek lojistik model bilinir; validasyon için)"
    return df


def load_proxy(path: str, label: str, column_map: dict | None = None, **read_kw) -> pd.DataFrame:
    """Vekil veri yükleyici: kolonları standart isimlere eşler ve provenance etiketler."""
    df = pd.read_csv(path, **read_kw)
    if column_map:
        df = df.rename(columns=column_map)
    df.attrs["provenance"] = f"VEKİL: {label} (gerçek case verisi değil)"
    return df
