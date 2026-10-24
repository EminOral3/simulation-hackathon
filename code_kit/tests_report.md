# tests_report.md — 24 Ekim 2026, Python 3.14.4 (venv), numpy/scipy/pandas/sklearn/simpy/streamlit/langgraph

## Çalıştı (otomatik, `pytest`: 16 test geçti, ≈3 sn)
- data_sampling: IPF marjinallere yakınsıyor (<1e-3), sentetik marjinaller doğru (±0.02).
- decision_models: 3 strateji (verbal / multi_sample / logprobs) mock ile; fiyat duyarlılığı yönü; disk cache isabeti (ikinci koşuda 0 çağrı); retry (%50 hata enjeksiyonunda tamamlanıyor); vazgeçince düzgün uniform; logprobs desteği yoksa multi_sample'a düşüş; RuleModel; MLModel (sklearn) yönü doğru.
- sim_core: DES M/M/c Wq, analitik değerle %95 aralık (±0.05 tolerans) içinde; sabırsız müşteri terk oranı >0; kaskad monoton; Bass uç değeri; SD (SI modeli) kütle korunumu.
- validation: JSD, ordinal W1, insan tavanı, madde korelasyonu, yön uyumu, bootstrap CI, mod çöküşü (çökmüş > çeşitli), ECE, PPI (yanlı sentetik ortalamayı düzeltiyor), DR (yanlış sonuç modeli + doğru propensity ile).
- roi: MC yüzdelikleri sıralı, tornado sıralı, 3 senaryo.
- app_stub: `compute_view` mantığı; Streamlit `AppTest` ile tam script çalıştırıldı: istisna yok, 4 metrik + uyarı rozetleri render oldu.
- langgraph_adapter: simulate→validate grafiği çalıştı (`ainvoke`).

## Çalışmadı / test edilmedi
- **AnthropicProvider: TEST EDİLMEDİ** (anahtar/paket yok).
- Streamlit'in tarayıcıda görsel doğrulaması yapılmadı (yalnız AppTest).
- MCI eşiği: mock çıktısında 0.94 (persona yok sayıldığı için). Gerçek LLM'de değeri bilinmiyor → eşik kalibrasyonsuz.
- PPI güven aralığı testi tek tohumla; kapsama (coverage) simülasyonu yapılmadı → "%95" iddiası doğrulanmadı.
- Ölçek/performans: yalnız ≤300 persona mock; gerçek gecikme/rate-limit altında davranış bilinmiyor.
- Python 3.11 hedefi: 3.14'te test edildi; 3.11'de çalıştırılmadı (kod 3.11 sözdizimini aşmıyor, ama doğrulanmadı).

## Canlı OpenAI kontrolü (24 Ekim, `live_check.py`, gpt-4o-mini, 2 fiyat × 6 persona, çok küçük n)
Çalıştı: 3 strateji da uçtan uca; logprobs (tek harf token) gerçekten döndü; disk cache/retry yolu çalıştı.
Canlıda bulunan 2 hata (mock'ta görünmüyordu, düzeltildi):
1. Prompt'taki `OPT[...]` mock işaretleyicisini model yankılıyordu → seçenekler artık harf etiketli (A/B), Al/Alma ilk-token çakışması da bitti.
2. `predict()` her çağrıda yeni event loop açıyor, `AsyncOpenAI` ilk loop'a bağlı kalıyordu → %50 hata; sağlayıcılar loop değişince istemciyi yeniden kuruyor (hata 0'a indi).
Sonuç (P(Al), fiyat 20 → 100): verbal 0.70 → 0.70 (duyarlılık yok), multi_sample 0.57 → 0.47, logprobs 0.58 → 0.34. **n=6 persona; bu bir bağlantı testidir, geçerlilik kanıtı değil.** Gerçek doğruluk, çeşitlilik (MCI), maliyet ölçülmedi. Konum yanlılığı (A/B sırası) test edilmedi.

## Model değişikliği: gpt-6-luna (24 Ekim)
`OpenAIProvider` varsayılanı `gpt-6-luna`. Canlıda bulunan 3 uyumsuzluk, düzeltildi: (1) `max_tokens` reddediliyor → `max_completion_tokens`; (2) `temperature=0.0` reddediliyor (yalnız 1) → parametre yalnız 1.0'da gönderilir; (3) `logprobs` reddediliyor → `supports_logprobs=False`, `logprobs` stratejisi otomatik `multi_sample`'a düşer. Bu hatalar her çağrıda düştüğü için ilk denemede sonuçlar sessizce uniform (0.5) çıktı: `stats['gave_up']` ve `fallback_*` sayaçlarına bakmadan canlı sonuç yorumlanmamalı.
Deneme (`live_check.py`, 2 fiyat × 6 persona, n çok küçük; P(Al) fiyat 20 → 100): verbal 0.52 → 0.42, multi_sample 0.70 → 0.27, logprobs-isteği (multi_sample'a düştü) 0.75 → 0.23. Yalnız "çalışıyor" kontrolüdür; doğruluk/maliyet/MCI ölçülmedi. Yukarıdaki gpt-4o-mini sonuçları tarihçedir, güncel model değildir.

## Model değişikliği: gemini-3.7-flash (24 Ekim)
Varsayılan LLM `GeminiProvider` (Vertex AI REST, anahtar `VERTEX_AI_KEY`). Canlıda bulunan: düşünme kapatılamıyor (`thinkingLevel=minimal` 400, `thinkingBudget=0` etkisiz) ve düşünme token'ları `maxOutputTokens`'tan yer; pay verilmezse yanıt boş (`MAX_TOKENS`) döner → `thinkingLevel=low` + `max_tokens+1024`. `live_check.py` sonucu aşağıda.
`live_check.py` (2 fiyat × 6 persona, çok küçük n, P(Al) fiyat 20 / 100): verbal 0.73/0.54 (8.7 sn) · multi_sample 0.90/0.57 (19.9 sn) · logprobs→multi_sample'a düştü 0.90/0.70 (184 sn, 2 hata, `gave_up` yok). Fiyat yönü doğru; n çok küçük, doğruluk iddiası yok. Logprobs yolu yavaş: canlıda `multi_sample` veya `verbal` kullan.
