"""Streamlit iskeleti.  Çalıştır:  streamlit run app_stub.py
Case'te DEĞİŞECEK yerler: `OPTIONS`, `make_contexts`, `real_dist` (gerçek/vekil), KPI formülü. Mantık `compute_view`'da (UI'sız test edilir)."""
from __future__ import annotations
import numpy as np

from decision_models import LLMPersonaModel, MockProvider, DiskCache, aggregate
from data_sampling import synth_population
from validation import jsd, mode_collapse_index, bootstrap_ci

OPTIONS = ["Al", "Alma"]                       # CASE: değiştir
JSD_WARN, MCI_WARN = 0.05, 0.6                 # sezgisel eşikler; gerçek veriyle kalibre et


def make_contexts(price: float, n: int, seed: int = 0):
    pop = synth_population(n, {"yas": {"genc": .4, "orta": .4, "yasli": .2}, "gelir": {"dusuk": .5, "yuksek": .5}}, seed)
    return [{"persona": r, "stimulus": f"Ürün fiyatı price={price:.0f} TL", "options": OPTIONS}
            for r in pop.to_dict("records")]


def real_dist(price: float) -> dict:           # CASE: gerçek/vekil dağılımı yükle. Burada VARSAYIM.
    p = float(np.clip(0.9 - price / 120, 0.02, 0.98)); return {"Al": p, "Alma": 1 - p}


def compute_view(price: float, live: bool, n: int = 60, seed: int = 0, provider=None) -> dict:
    prov = provider or (None if live else MockProvider(seed=seed))
    if prov is None:
        from decision_models import AnthropicProvider; prov = AnthropicProvider()
    model = LLMPersonaModel(prov, strategy="verbal" if live else "multi_sample", n_samples=4, cache=DiskCache(".llm_cache"))
    ctx = make_contexts(price, n, seed)
    ds = model.predict(ctx)
    agg = aggregate(ctx, ds)
    real = real_dist(price)
    D = np.array([[d[o] for o in OPTIONS] for d in ds])
    _, lo, hi = bootstrap_ci(D[:, 0], seed=seed)
    j = jsd([real[o] for o in OPTIONS], [agg[o] for o in OPTIONS])
    mci = mode_collapse_index(D)["mci"]
    warn = []
    if j > JSD_WARN: warn.append(f"JSD={j:.3f} > {JSD_WARN}: gerçek dağılımdan uzak")
    if mci > MCI_WARN: warn.append(f"Mod çöküşü indeksi={mci:.2f}: persona çeşitliliği düşük")
    if not live: warn.append("MOCK mod: sayılar gerçek davranış DEĞİL")
    return {"agg": agg, "real": real, "ci": (lo, hi), "jsd": j, "mci": mci, "warnings": warn,
            "revenue_index": price * agg["Al"], "stats": dict(model.stats)}


def main():
    import streamlit as st
    st.set_page_config(page_title="Simülasyon Demo", layout="wide")
    live = st.sidebar.toggle("Canlı LLM (kapalı = mock)", value=False)
    price = st.sidebar.slider("What-if: fiyat", 20, 120, 60)
    n = st.sidebar.slider("Persona sayısı", 20, 300, 60)
    v = compute_view(price, live, n)
    st.title("Simülasyon Demo"); st.caption("Veri kaynağı: VARSAYIM/VEKİL (case'te güncelle)")
    for w in v["warnings"]:
        st.warning("⚠ GÜVENME UYARISI — " + w)
    if not v["warnings"]:
        st.success("Doğrulama eşikleri içinde (eşikler sezgisel)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("P(Al) sentetik", f"{v['agg']['Al']:.2f}", f"CI {v['ci'][0]:.2f}–{v['ci'][1]:.2f}")
    c2.metric("P(Al) gerçek/vekil", f"{v['real']['Al']:.2f}")
    c3.metric("JSD", f"{v['jsd']:.3f}")
    c4.metric("Gelir endeksi", f"{v['revenue_index']:.1f}")
    import pandas as pd
    st.bar_chart(pd.DataFrame({"gerçek/vekil": v["real"], "sentetik": v["agg"]}))
    st.caption(f"Sentetik P(Al) %95 bootstrap bandı: [{v['ci'][0]:.2f}, {v['ci'][1]:.2f}]  ·  çağrı istatistikleri: {v['stats']}")


if __name__ == "__main__":
    main()
