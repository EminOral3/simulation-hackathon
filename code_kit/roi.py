"""Monte Carlo ROI + tornado. Parametre = (düşük, baz, yüksek) üçgen dağılım; hepsi VARSAYIM etiketli olmalı."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class Param:
    name: str
    low: float
    base: float
    high: float
    assumption: str = "VARSAYIM"  # kaynağı/etiket: "VARSAYIM" | "VERİ" | "VEKİL"

    def sample(self, rng, n):
        return rng.triangular(self.low, self.base, self.high, n)


def monte_carlo_roi(params: list[Param], formula, n: int = 10000, seed: int = 0) -> dict:
    """formula(**{param_adı: dizi}) -> net değer dizisi (vektörleştirilmiş). ROI aralığı + P(net>0)."""
    rng = np.random.default_rng(seed)
    draws = {p.name: p.sample(rng, n) for p in params}
    v = np.asarray(formula(**draws), float)
    return {"p5": float(np.percentile(v, 5)), "p50": float(np.percentile(v, 50)), "p95": float(np.percentile(v, 95)),
            "mean": float(v.mean()), "prob_positive": float((v > 0).mean()), "samples": v}


def scenarios(params: list[Param], formula) -> dict:
    """Düşük/baz/yüksek: hepsi-düşük, hepsi-baz, hepsi-yüksek. (Parametre yönü formülde 'iyi' olmayabilir -> tornado'ya bak.)"""
    return {k: float(formula(**{p.name: getattr(p, k) for p in params})) for k in ("low", "base", "high")}


def tornado(params: list[Param], formula) -> list[dict]:
    """Tek parametre düşük/yüksek, diğerleri baz. Etki genişliğine göre azalan sıralı."""
    base = {p.name: p.base for p in params}
    b = float(formula(**base)); rows = []
    for p in params:
        lo = float(formula(**{**base, p.name: p.low})); hi = float(formula(**{**base, p.name: p.high}))
        rows.append({"param": p.name, "at_low": lo, "at_high": hi, "swing": abs(hi - lo), "base": b,
                     "assumption": p.assumption})
    return sorted(rows, key=lambda r: -r["swing"])
