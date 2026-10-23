"""Doğrulama araçları. Hepsi saf numpy/scipy. Dağılımlar: 1-B olasılık vektörü (kategorik) veya örnek dizisi."""
from __future__ import annotations
import numpy as np
from scipy import stats
from scipy.spatial.distance import jensenshannon


def jsd(p, q) -> float:
    """Jensen-Shannon DİVERJANSI (log2; 0..1). (scipy mesafe değil, karesi.)"""
    p, q = np.asarray(p, float), np.asarray(q, float)
    return float(jensenshannon(p / p.sum(), q / q.sum(), base=2) ** 2)


def wasserstein(x, y) -> float:
    """1-B Wasserstein; x,y örnek dizileri (ordinal için seviye değerleri)."""
    return float(stats.wasserstein_distance(x, y))


def wasserstein_ordinal(p, q) -> float:
    """Sıralı kategorilerde (0..K-1) olasılık vektörleri arası W1."""
    p, q = np.asarray(p, float), np.asarray(q, float)
    return float(np.abs(np.cumsum(p / p.sum()) - np.cumsum(q / q.sum())).sum())


def item_correlation(A, B) -> dict:
    """Madde (kolon) çiftleri arası korelasyon matrisi benzerliği: iki matrisin üst-üçgen Pearson/Spearman'ı.
    A,B: (n, k) örnek matrisleri (gerçek vs sentetik)."""
    iu = np.triu_indices(np.asarray(A).shape[1], 1)
    ca, cb = np.corrcoef(np.asarray(A).T)[iu], np.corrcoef(np.asarray(B).T)[iu]
    return {"pearson": float(stats.pearsonr(ca, cb)[0]), "spearman": float(stats.spearmanr(ca, cb)[0])}


def human_ceiling(X, n_splits: int = 200, seed: int = 0, stat=lambda a: a.mean(axis=0)) -> dict:
    """İnsan tavanı: gerçek veriyi rastgele ikiye böl, iki yarının istatistiklerinin korelasyonu (Spearman-Brown düzeltmeli).
    Sentetik, bu tavanı aşamaz; sentetik-insan korelasyonu bununla karşılaştırılmalıdır. X: (n, k)."""
    X = np.asarray(X, float); rng = np.random.default_rng(seed); r = []
    for _ in range(n_splits):
        idx = rng.permutation(len(X)); h = len(X) // 2
        r.append(np.corrcoef(stat(X[idx[:h]]), stat(X[idx[h:]]))[0, 1])
    r = np.array(r); rm = float(np.nanmean(r))
    return {"split_half_r": rm, "spearman_brown": float(2 * rm / (1 + rm)), "sd": float(np.nanstd(r))}


def effect_direction_agreement(real_effects, synth_effects) -> dict:
    """Etki yön uyumu: aynı işaret oranı + (varsa) büyüklük korelasyonu. Etkiler: tedavi-kontrol farkları vektörü."""
    a, b = np.asarray(real_effects, float), np.asarray(synth_effects, float)
    out = {"sign_agree": float(np.mean(np.sign(a) == np.sign(b))), "n": len(a)}
    if len(a) > 2:
        out["magnitude_r"] = float(np.corrcoef(a, b)[0, 1])
    return out


def subgroup_table(df, group_col: str, real_col: str, synth_col: str):
    """Alt grup tablosu: grup başına n, gerçek ort, sentetik ort, mutlak hata, işaret-yanlılık."""
    import pandas as pd
    g = df.groupby(group_col).agg(n=(real_col, "size"), real=(real_col, "mean"), synth=(synth_col, "mean"))
    g["abs_err"] = (g["synth"] - g["real"]).abs()
    g["bias"] = g["synth"] - g["real"]
    return g.reset_index()


def bootstrap_ci(x, stat=np.mean, n_boot: int = 2000, alpha: float = 0.05, seed: int = 0) -> tuple:
    """Yüzdelik bootstrap güven aralığı -> (tahmin, alt, üst)."""
    x = np.asarray(x); rng = np.random.default_rng(seed)
    bs = np.array([stat(x[rng.integers(0, len(x), len(x))]) for _ in range(n_boot)])
    return float(stat(x)), float(np.percentile(bs, 100 * alpha / 2)), float(np.percentile(bs, 100 * (1 - alpha / 2)))


def mode_collapse_index(dists) -> dict:
    """Mod çöküşü: (a) birey dağılımları arası ortalama çift JSD düşükse persona çeşitliliği yok;
    (b) ortalama normalize entropi. dists: (n_birey, K). MCI = 1 - (ort. çift JSD / maks=1) ; 1'e yakın = çökmüş."""
    D = np.asarray(dists, float); D = D / D.sum(1, keepdims=True)
    m = D.mean(0)
    mean_jsd_to_center = float(np.mean([jsd(d, m) for d in D]))
    H = -(D * np.log(D + 1e-12)).sum(1) / np.log(D.shape[1])
    return {"mci": float(1 - min(1.0, mean_jsd_to_center * 4)),  # ölçek: 0.25 JSD ≈ tam çeşitlilik (sezgisel eşik)
            "mean_jsd_to_center": mean_jsd_to_center, "mean_norm_entropy": float(H.mean()),
            "note": "MCI eşiği sezgiseldir; gerçek veriyle kalibre edilmeden mutlak yorumlama."}


def ece(probs, outcomes, n_bins: int = 10) -> float:
    """Expected Calibration Error (ikili olay). probs: tahmin P(y=1)."""
    p, y = np.asarray(probs, float), np.asarray(outcomes, float)
    bins = np.minimum((p * n_bins).astype(int), n_bins - 1); e = 0.0
    for b in range(n_bins):
        m = bins == b
        if m.any():
            e += m.mean() * abs(p[m].mean() - y[m].mean())
    return float(e)


def ppi_mean(y_labeled, f_labeled, f_unlabeled, alpha: float = 0.05) -> dict:
    """Prediction-powered inference (ortalama): θ = mean(f_unl) + mean(y_lab - f_lab) (rectifier).
    Az sayıda gerçek etiket + çok sayıda sentetik tahmin. Aralık: normal yaklaşım. (Angelopoulos vd. fikri; formül ortalama için temel hal.)"""
    y, fl, fu = map(lambda a: np.asarray(a, float), (y_labeled, f_labeled, f_unlabeled))
    n, N = len(y), len(fu); rect = y - fl
    theta = fu.mean() + rect.mean()
    se = np.sqrt(fu.var(ddof=1) / N + rect.var(ddof=1) / n)
    z = stats.norm.ppf(1 - alpha / 2)
    return {"estimate": float(theta), "ci": (float(theta - z * se), float(theta + z * se)),
            "naive_synth_mean": float(fu.mean()), "rectifier": float(rect.mean())}


def doubly_robust_mean(y, a_observed, pred_y, propensity) -> float:
    """Doubly-robust ortalama (eksik gözlem): μ = mean(pred) + mean( a/π * (y - pred) ).
    a_observed∈{0,1} gerçek etiketin gözlendiği; y yalnız a=1 için anlamlı. propensity=π(x)=P(a=1|x)."""
    y, a, m, pi = map(lambda v: np.asarray(v, float), (y, a_observed, pred_y, propensity))
    return float(np.mean(m + a / np.clip(pi, 1e-3, None) * (np.where(a == 1, y, 0) - m)))
