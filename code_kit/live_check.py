"""Canlı OpenAI kontrolü: 3 strateji, küçük n. Anahtarı yazdırmaz."""
import sys, time
import decision_models as dm, validation as v
model = sys.argv[1] if len(sys.argv) > 1 else "gpt-6-luna"
prov = dm.OpenAIProvider(model)
ctx = lambda price, seg: {"persona": {"yas": seg, "gelir": "orta"}, "stimulus": f"Aylık abonelik fiyatı price={price} TL.", "options": ["Al", "Alma"]}
for strat in ("verbal", "multi_sample", "logprobs"):
    m = dm.LLMPersonaModel(prov, strat, n_samples=4, concurrency=8)
    t = time.time()
    try:
        r = {p: dm.aggregate([ctx(p, s) for s in ("genc", "yasli")] * 3, m.predict([ctx(p, s) for s in ("genc", "yasli")] * 3))["Al"] for p in (20, 100)}
        print(strat, {k: round(x, 3) for k, x in r.items()}, f"{time.time()-t:.1f}s", dict(m.stats))
    except Exception as e:
        print(strat, "HATA", type(e).__name__, str(e)[:200])
