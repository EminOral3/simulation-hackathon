"""Uydurma iki case ile uçtan uca prova. Çıktı 01_DRY_RUN.md'ye elle aktarılır."""
import time, warnings, numpy as np
warnings.filterwarnings("ignore")
import data_sampling as ds, decision_models as dm, sim_core as sc, validation as v, roi

def A():
    print("=== CASE A: persona/fiyat (UYDURMA) ===")
    truth = ds.synth_choice_data(20000, seed=1)           # gerçek model bilinir
    hist = truth.sample(1500, random_state=0)             # 'tarihsel veri'
    prices = [30, 50, 70, 90]
    seg = {"genc": .4, "orta": .4, "yasli": .2}
    def true_p(pr):  return float(truth.assign(price=pr).pipe(lambda d: 1/(1+np.exp(-(d.segment.map({"genc":1.0,"orta":1.5,"yasli":.5}) + d.segment.map({"genc":1.3,"orta":1.0,"yasli":.7})*-0.04*pr + 2.0)))).mean())
    mk = lambda pr, segname: {"persona": {"segment": segname}, "stimulus": f"price={pr}", "options": ["Al","Alma"]}
    pop = ds.synth_population(300, {"segment": seg}, seed=3)
    def ctxs(pr): return [mk(pr, s) for s in pop.segment]
    # (1) LLM'siz baz: MLModel
    t=time.time()
    tr = hist.sample(800, random_state=1)
    cs = [mk(r.price, r.segment) for r in tr.itertuples()]; ch = ["Al" if b else "Alma" for b in tr.buy]
    def f(c,o):  # her seçenek için ayrı katsayı: satır başına P(seçildi|x) öğrenilsin
        pr=float(c["stimulus"].split("=")[1]); s=c["persona"]["segment"]; ind=float(o=="Al")
        return {"p_al":pr*ind,"g_al":(s=="genc")*ind,"y_al":(s=="yasli")*ind,"b_al":ind,
                "p_alma":pr*(1-ind),"g_alma":(s=="genc")*(1-ind),"y_alma":(s=="yasli")*(1-ind),"b_alma":1-ind}
    ml = dm.MLModel(f).fit(cs, ch)
    base = [dm.aggregate(ctxs(p), ml.predict(ctxs(p)))["Al"] for p in prices]; t_ml=time.time()-t
    # (2) LLM persona (MOCK)
    t=time.time()
    llm = dm.LLMPersonaModel(dm.MockProvider(fail_rate=0.05, latency=0.002), "multi_sample", n_samples=6, retries=4, backoff=0.01, concurrency=16)
    out = [dm.aggregate(ctxs(p), llm.predict(ctxs(p)))["Al"] for p in prices]; t_llm=time.time()-t
    tp = [true_p(p) for p in prices]
    print("fiyat      ", prices); print("gercek     ", np.round(tp,3)); print("ML baz     ", np.round(base,3)); print("LLM(mock)  ", np.round(out,3))
    print("MAE ML %.3f | MAE LLM(mock) %.3f"%(np.mean(np.abs(np.array(base)-tp)), np.mean(np.abs(np.array(out)-tp))))
    print("JSD@50 ML %.4f LLM %.4f"%(v.jsd([tp[1],1-tp[1]],[base[1],1-base[1]]), v.jsd([tp[1],1-tp[1]],[out[1],1-out[1]])))
    print("yon uyumu (fiyat artinca P(Al) duser?) ML", bool(np.all(np.diff(base)<0)), "LLM", bool(np.all(np.diff(out)<0)))
    D = np.array([[d["Al"],d["Alma"]] for d in llm.predict(ctxs(50))]); print("MCI(mock,p=50)", round(v.mode_collapse_index(D)["mci"],2))
    print("sure: ML %.2fs | LLM(mock) %.2fs | cagri/hata/vazgecme:"%(t_ml,t_llm), dict(llm.stats))
    # ROI
    P=[roi.Param("lift",.005,.02,.05),roi.Param("cost",3e4,8e4,2e5),roi.Param("base_rev",8e6,1.2e7,1.6e7)]
    r=roi.monte_carlo_roi(P, lambda lift,cost,base_rev: lift*base_rev-cost)
    print("ROI(VARSAYIM) p5/p50/p95: %.0f / %.0f / %.0f  P(>0)=%.2f"%(r["p5"],r["p50"],r["p95"],r["prob_positive"]))
    print("tornado:", [(x["param"], round(x["swing"])) for x in roi.tornado(P, lambda lift,cost,base_rev: lift*base_rev-cost)])

def B():
    print("\n=== CASE B: kapasite/kuyruk (UYDURMA cagri merkezi) ===")
    lam, mu = 4.8, 1.0   # dk basina varis, hizmet orani (ort 1 dk)
    for c in (5,6,7,8):
        a = sc.mmc_analytic(c, lam, mu)
        if not a["stable"]: print(f"c={c}: kararsiz (rho={a['rho']:.2f})"); continue
        t=time.time(); r = sc.replicate_queue(reps=20, c=c, lam=lam, mu=mu, horizon=3000, warmup=300); dt=time.time()-t
        ab = sc.simulate_queue(c, lam, mu, horizon=3000, warmup=300, patience=lambda rg: rg.exponential(3))["abandon_rate"]
        print(f"c={c} rho={a['rho']:.2f} Wq analitik={a['Wq']:.3f} DES={r['Wq_mean']:.3f} [{r['ci_low']:.3f},{r['ci_high']:.3f}] terk(sabir~3dk)={ab:.3f}  ({dt:.1f}s)")
    # baz coz: min c ile Wq<=0.5 dk
    sol = next(c for c in range(5,20) if sc.mmc_analytic(c,lam,mu).get("Wq",9)<=0.5); print("Baz cozum (analitik): hedef Wq<=0.5 dk icin min c =", sol)
    # hibrit: heterojen hizmet suresi (gercek: iki cagri turu) -> M/G/c, analitik formul yok, DES gerekli
    mix = lambda r: r.exponential(0.6) if r.random()<.7 else r.exponential(2.0)   # ort 0.42+0.6=1.02
    for c in (6,7):
        r = sc.replicate_queue(reps=20, c=c, lam=lam, mu=1.0, horizon=3000, warmup=300, service=mix)
        print(f"heterojen hizmet c={c}: Wq={r['Wq_mean']:.3f} [{r['ci_low']:.3f},{r['ci_high']:.3f}]  (M/M/c ayni ort. icin {sc.mmc_analytic(c,lam,1/1.02)['Wq']:.3f})")
    # 'LLM'li' varyant: bilet metnini tur siniflandirma (MOCK; kural tabanli ile karsilastir)
    rng=np.random.default_rng(0); texts=[("fatura itiraz" if rng.random()<.3 else "sifre sifirla") for _ in range(500)]
    rule=lambda t: "uzun" if "itiraz" in t else "kisa"
    class Cls(dm.MockProvider):
        async def complete(self,prompt,**kw):
            import re; t=re.search(r"stim=(.*)",prompt).group(1); lab=rule(t)
            return dm.Completion(lab if np.random.random()>.08 else ("kisa" if lab=="uzun" else "uzun"))
    m=dm.LLMPersonaModel(Cls(), "multi_sample", n_samples=1, concurrency=32)
    t=time.time(); ds_=m.predict([{"persona":{}, "stimulus":"stim="+x, "options":["kisa","uzun"]} for x in texts]); dt=time.time()-t
    acc=np.mean([("uzun" if d["uzun"]>d["kisa"] else "kisa")==rule(x) for d,x in zip(ds_,texts)])
    print(f"LLM(mock) siniflandirma uyumu kural tabanliyla: {acc:.3f} ({dt:.2f}s). Mock %8 gurultu enjekte eder -> bu bir BORU HATTI testi, LLM basari kaniti DEGIL.")

if __name__=="__main__":
    A(); B()
