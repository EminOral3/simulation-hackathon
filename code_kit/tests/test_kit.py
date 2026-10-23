import sys, pathlib, math
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pytest
import data_sampling as ds, decision_models as dm, sim_core as sc, validation as v, roi


def test_ipf_matches_margins():
    df = ds.synth_population(2000, {"a": {"x": .7, "y": .3}, "b": {"u": .5, "v": .5}}, seed=1)
    w = ds.ipf(df, {"a": {"x": .5, "y": .5}, "b": {"u": .3, "v": .7}})
    assert abs(w[df.a == "x"].sum() / w.sum() - .5) < 1e-3
    assert abs(w[df.b == "u"].sum() / w.sum() - .3) < 1e-3


def test_synth_marginals():
    df = ds.synth_population(20000, {"a": {"x": .7, "y": .3}}, seed=2)
    assert abs((df.a == "x").mean() - .7) < .02


def ctxs(price, n=20):
    return [{"persona": {"i": i}, "stimulus": f"price={price}", "options": ["Al", "Alma"]} for i in range(n)]


@pytest.mark.parametrize("strategy", ["verbal", "multi_sample", "logprobs"])
def test_llm_model_mock_strategies(strategy, tmp_path):
    m = dm.LLMPersonaModel(dm.MockProvider(), strategy=strategy, n_samples=6, cache=dm.DiskCache(str(tmp_path)))
    out = m.predict(ctxs(30))
    assert len(out) == 20 and all(abs(sum(d.values()) - 1) < 1e-6 for d in out)


def test_price_sensitivity_and_cache(tmp_path):
    c = dm.DiskCache(str(tmp_path))
    m = dm.LLMPersonaModel(dm.MockProvider(), "verbal", cache=c)
    lo = dm.aggregate(ctxs(20), m.predict(ctxs(20)))["Al"]
    hi = dm.aggregate(ctxs(90), m.predict(ctxs(90)))["Al"]
    assert lo > hi
    m2 = dm.LLMPersonaModel(dm.MockProvider(), "verbal", cache=c); m2.predict(ctxs(20))
    assert m2.stats["cache_hit"] > 0 and m2.stats["calls"] == 0


def test_retry_recovers_and_gives_up():
    m = dm.LLMPersonaModel(dm.MockProvider(fail_rate=0.5), "verbal", retries=6, backoff=0.001)
    m.predict(ctxs(40, 10)); assert m.stats["errors"] > 0
    bad = dm.LLMPersonaModel(dm.MockProvider(fail_rate=1.0), "verbal", retries=1, backoff=0.001)
    out = bad.predict(ctxs(40, 3)); assert out[0] == {"Al": .5, "Alma": .5} and bad.stats["gave_up"] == 3


def test_logprobs_fallback_when_unsupported():
    p = dm.MockProvider(); p.supports_logprobs = False
    m = dm.LLMPersonaModel(p, "logprobs", n_samples=3); m.predict(ctxs(30, 2))
    assert m.stats["fallback_logprobs"] == 2


def test_rule_and_ml():
    r = dm.RuleModel(lambda c, o: -0.05 * float(c["stimulus"].split("=")[1]) if o == "Al" else 0)
    d = r.predict(ctxs(10, 1))[0]; assert d["Al"] > r.predict(ctxs(90, 1))[0]["Al"]
    rng = np.random.default_rng(0); cs, ch = [], []
    for _ in range(300):
        pr = rng.uniform(10, 100); cs.append({"persona": {}, "stimulus": f"price={pr}", "options": ["Al", "Alma"]})
        ch.append("Al" if rng.random() < 1 / (1 + math.exp(0.05 * (pr - 50))) else "Alma")
    f = lambda c, o: {"p": float(c["stimulus"].split("=")[1]) * (o == "Al"), "is_al": float(o == "Al")}
    ml = dm.MLModel(f).fit(cs, ch)
    assert ml.predict(ctxs(10, 1))[0]["Al"] > ml.predict(ctxs(95, 1))[0]["Al"]


def test_mmc_matches_des():
    a = sc.mmc_analytic(3, 2.4, 1.0)
    r = sc.replicate_queue(reps=12, c=3, lam=2.4, mu=1.0, horizon=4000, warmup=400)
    assert r["ci_low"] - 0.05 <= a["Wq"] <= r["ci_high"] + 0.05


def test_abandonment_and_cascade_and_sd():
    assert sc.simulate_queue(1, 1.2, 1.0, horizon=2000, patience=lambda r: r.exponential(2))["abandon_rate"] > 0
    g = sc.ba_graph(500, 3)
    h = sc.cascade(g, [0, 1, 2], p=.2, steps=30); assert h[-1] > h[0] and np.all(np.diff(h) >= 0)
    assert sc.cascade(g, [], p_bass=.02, q_bass=.3, steps=30)[-1] > 0
    b = sc.bass_curve(1000, .03, .4); assert 900 < b[-1] <= 1000
    o = sc.stock_flow({"S": 99., "I": 1.}, {"inf": lambda s, t: .3 * s["S"] * s["I"] / 100},
                      {"inf": {"S": -1, "I": 1}}, T=60)
    assert o["I"][-1] > 90 and abs(o["S"][-1] + o["I"][-1] - 100) < 1e-6


def test_validation_metrics():
    assert v.jsd([.5, .5], [.5, .5]) < 1e-9 and 0 < v.jsd([.9, .1], [.1, .9]) <= 1
    assert v.wasserstein_ordinal([1, 0, 0], [0, 0, 1]) == 2
    rng = np.random.default_rng(0); X = rng.normal(size=(500, 5)) + np.arange(5)
    assert v.human_ceiling(X)["split_half_r"] > .9
    assert v.item_correlation(X, X + rng.normal(0, .01, X.shape))["pearson"] > .9
    assert v.effect_direction_agreement([1, -1, 2], [.5, -.2, 1])["sign_agree"] == 1
    m, lo, hi = v.bootstrap_ci(rng.normal(5, 1, 300)); assert lo < 5 < hi
    col = np.tile([.95, .05], (50, 1)); div = rng.dirichlet([.3, .3], 50)
    assert v.mode_collapse_index(col)["mci"] > v.mode_collapse_index(div)["mci"]
    p = rng.random(5000); y = (rng.random(5000) < p).astype(int)
    assert v.ece(p, y) < .05 and v.ece(np.full(5000, .9), y) > .2


def test_ppi_fixes_bias():
    rng = np.random.default_rng(1); truth = rng.normal(.4, 1, 20000)
    pred = truth + .3 + rng.normal(0, .5, 20000)            # sentetik yanlı
    est = v.ppi_mean(truth[:200], pred[:200], pred[200:])
    assert abs(est["naive_synth_mean"] - .4) > .25 and abs(est["estimate"] - .4) < .2
    assert est["ci"][0] < .4 < est["ci"][1] or abs(est["estimate"] - .4) < .15


def test_dr_mean():
    rng = np.random.default_rng(2); n = 20000; x = rng.normal(size=n); y = 2 * x + rng.normal(size=n) + 1
    pi = 1 / (1 + np.exp(-x)); a = (rng.random(n) < pi).astype(int)
    assert abs(v.doubly_robust_mean(y, a, np.zeros(n), pi) - 1) < .15   # model yanlış (0), propensity doğru


def test_roi():
    P = [roi.Param("lift", .01, .03, .06), roi.Param("cost", 5e4, 1e5, 2e5), roi.Param("base", 1e7, 1.5e7, 2e7)]
    f = lambda lift, cost, base: lift * base - cost
    r = roi.monte_carlo_roi(P, f, n=4000); assert r["p5"] < r["p50"] < r["p95"]
    t = roi.tornado(P, f); assert t[0]["swing"] >= t[-1]["swing"] and set(roi.scenarios(P, f)) == {"low", "base", "high"}


def test_app_logic(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    import app_stub
    out = app_stub.compute_view(40, live=False, n=30)
    assert 0 < out["agg"]["Al"] < 1 and any("MOCK" in w for w in out["warnings"])
