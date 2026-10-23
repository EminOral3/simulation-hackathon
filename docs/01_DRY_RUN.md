# 01_DRY_RUN — iki UYDURMA case, çekirdek uçtan uca (kod: `02_CODE_KIT/dry_run.py`)

**Önemli sınırlama:** "LLM" = `MockProvider`. Mock gerçek insan/LLM davranışı üretmez; bu koşu **boru hattı, hata/süre ve arayüz** testidir. "LLM'li çözüm gerçek çözümden iyi/kötü" sonucu **çıkarılamaz**. Gerçek LLM ile karşılaştırma bu fazda yapılmadı.

## Case A — Persona / fiyat (uydurma)
Karar: ürün fiyatı hangisi olsun (30/50/70/90)? "Gerçek" = bilinen lojistik üretici model (sentetik, `synth_choice_data`); tarihsel veri = 1500 gözlem; 800'ü eğitim.

| Fiyat | Gerçek P(Al) | LLM'siz baz (MLModel, lojistik) | LLM persona (MOCK) |
|---|---|---|---|
| 30 | 0.855 | 0.821 | 0.632 |
| 50 | 0.716 | 0.697 | 0.608 |
| 70 | 0.531 | 0.536 | 0.481 |
| 90 | 0.351 | 0.367 | 0.467 |
| **MAE** | – | **0.019** | 0.124 |
| JSD@50 | – | 0.0003 | 0.0094 |

- Yön (fiyat↑ → P(Al)↓): ikisinde de doğru. Mod çöküşü indeksi (mock, p=50): 0.48 (eşik sezgisel).
- **LLM kapısı sonucu (bu uydurma case için):** tablo verisi var ve model yapısı basit → **ajansız**. "LLM'siz baz çözüm lojistik regresyon, 0.019 MAE; LLM'in ek değeri bu case'te ölçülemedi (mock)." Gerçek bir case'te LLM yalnız tarihsel veri yoksa/metin varsa anlamlı.
- ROI (tüm parametreler VARSAYIM): net değer p5/p50/p95 = 10 261 / 182 971 / 420 031; P(>0)=0.96. Tornado: en çok `lift` (swing 540 000), sonra `cost` (170 000), `base_rev` (160 000).

**Süre/hata:** MLModel eğit+tahmin 0.39 sn. LLM(mock): 4 fiyat × 300 persona × 6 örnek = 9000 çağrı, **1.83 sn** (concurrency 16, 2 ms sahte gecikme). Enjekte edilen %5 hatadan 486 hata oluştu, hepsi retry ile kurtarıldı (`gave_up`=0). **Gerçek gecikme ve rate-limit altında bu süre geçerli değil.**

## Case B — Kapasite / kuyruk (uydurma çağrı merkezi, λ=4.8/dk, μ=1/dk)
| Ajan sayısı c | ρ | Wq analitik (M/M/c) | Wq DES, 20 rep, %95 aralık | Terk oranı (sabır~Exp(3 dk)) |
|---|---|---|---|---|
| 5 | 0.96 | 4.508 | 4.209 [3.495, 4.923] | 0.116 |
| 6 | 0.80 | 0.431 | 0.439 [0.418, 0.461] | 0.059 |
| 7 | 0.69 | 0.127 | 0.126 [0.118, 0.134] | 0.023 |
| 8 | 0.60 | 0.044 | 0.042 [0.039, 0.046] | 0.010 |

- DES, analitik değeri aralık içinde yakalıyor (sağlama geçti; c=5'te ρ→1 olduğundan aralık geniş).
- Baz çözüm (analitik): Wq ≤ 0.5 dk için **min c = 6**.
- **DES'in asıl değeri:** iki tip çağrı (%70 kısa/%30 uzun, ort ≈1.02 dk) ile hizmet süresi heterojen → M/M/c yanlış: c=6'da DES Wq=0.692 [0.613, 0.770] vs M/M/c 0.509 → **c=6 hedefi tutmuyor, c=7 gerekiyor** (0.198 vs 0.145). Analitik baz sessizce yanlış karar verirdi.
- LLM kapısı: **ajansız**. Hibrit denemesi (bilet metni → çağrı türü, mock sınıflandırıcı): kural tabanlıyla uyum 0.922, ama %8 gürültüyü mock'a ben koydum → **bu LLM başarısının kanıtı değil**, yalnız bağlantının çalıştığının kanıtı. Gerçek LLM'in değeri, kuralın yakalayamadığı serbest metinde olabilir; test edilmedi.

**Süre:** 20 replikasyon × 3000 dk ≈ 3.3 sn/konfigürasyon (SimPy, tek çekirdek). Hata yok.

## Dry-run sırasında bulunan hata
İlk koşuda MLModel baz çözümü MAE 0.105 verdi. Sebep modelleme: "Alma" satırında tüm özellikler 0 olduğu için seçenekler arası normalizasyon olasılığı bozuyordu. Özellikleri seçenek bazında ayırınca MAE 0.019'a indi. **Ders:** `MLModel` için `feature_fn` her seçeneğe özel katsayı vermeli (README'ye eklendi). Kütüphane kodu değişmedi; bu bir kullanım tuzağı.

## Bu fazda yapamadıklarım
1. Gerçek LLM (Anthropic/OpenAI) çağrısı; gerçek gecikme, rate-limit, maliyet, mod çöküşü ölçümü.
2. LLM'li vs. LLM'siz çözümün **anlamlı** kıyası (mock bilgi taşımıyor).
3. İnsan verisiyle doğrulama (split-half tavanı, madde korelasyonu gerçek ankette denenmedi).
4. PPI/DR'ın gerçek yanlı sentetik veride kapsama (coverage) testi.
5. Streamlit'in tarayıcıda uçtan uca demosu (yalnız AppTest) ve demo kaydı.
6. Python 3.11'de test (3.14'te koştu).
7. Tek dry-run koşusu; tohum duyarlılığı raporlanmadı (Case A LLM sütunu mock rastgeleliğiyle koşular arası değişir).
