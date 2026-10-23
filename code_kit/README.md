# code_kit — yöntemden bağımsız modüller

Kurulum (proje kökünde): `python -m venv .venv && .venv/bin/pip install -r code_kit/requirements.txt openai` · Test: `cd code_kit && ../.venv/bin/python -m pytest -q` (≈3 sn, API gerekmez)

## Arayüz
`DecisionModel.predict(contexts) -> list[Dist]`; context = `{"persona": {...}, "stimulus": str, "options": [str]}`.
`LLMPersonaModel`, `RuleModel`, `MLModel` aynı arayüzdür → bir satırla değişir. LLM sağlayıcısı: `MockProvider | AnthropicProvider | OpenAIProvider`.

## Case geldiğinde hangi dosyalar değişir
| Case tipi | Değişecek | Dokunma |
|---|---|---|
| Persona / fiyat / reklam | `data_sampling` (marjinaller, vekil yükle), `app_stub` (OPTIONS, make_contexts, real_dist), `decision_models.build_prompt` (prompt dili) | `validation`, `sim_core` |
| Kapasite / kuyruk | `sim_core.simulate_queue` parametreleri/dağılımları (`service`, `patience`), `roi` formülü, `app_stub` (KPI'lar: Wq, abandon) | `decision_models` (LLM yok) |
| Churn | `decision_models.MLModel` + `feature_fn`; `sim_core.simulate_queue(patience=...)` (terk analojisi); `validation.ece` | LLM sağlayıcıları |
| Yayılım / kriz | `sim_core.cascade/er_graph/ba_graph`, gerçek ağ varsa kendi `adj` listesi | |
| Sürdürülebilirlik / regülasyon | `sim_core.stock_flow`, `sim_core.monte_carlo`, `roi` | |
| Her case | `roi.Param` listesi + formül; `app_stub.JSD_WARN/MCI_WARN` eşikleri (gerçek veriyle kalibre et) | |

## Bilinen sınırlar
- `MLModel` kullanımı: `feature_fn` her seçenek için ayrı katsayı üretmeli (örnek: `dry_run.py`); aksi halde seçenekler arası normalizasyon yanlı çıkar.
- Eşikler (JSD_WARN, MCI_WARN, MCI ölçeği) **sezgiseldir**; gerçek veriyle kalibre edilmedi.
- `MockProvider` persona özniteliklerini kullanmaz (yalnız `price=` ipucu) → mock'ta mod çöküşü uyarısı doğal olarak çıkar.
- Anthropic adaptörü **canlı test edilmedi**; OpenAI adaptörü gpt-6-luna ile canlı denendi (küçük n).
- Anthropic'te logprobs yok varsayılır; `strategy="logprobs"` otomatik `multi_sample`'a düşer (istatistik: `model.stats`).
- `synth_population` kolonları bağımsız varsayar (copula yalnız kaba).
- PPI/DR: ortalama için temel formül; çoklu parametre/regresyon için genişletilmedi.

- **Varsayılan LLM: `gpt-6-luna` (bkz. `docs/KARARLAR.md`).** gpt-6-luna: `logprobs` yok (strateji otomatik multi_sample'a düşer), `temperature` yalnız 1, `max_tokens` yerine `max_completion_tokens`.
- Anahtar: proje kökündeki `.env` içinde `OPENAI_KEY` (veya `OPENAI_API_KEY`); `load_env()` otomatik okur. Canlı kontrol: `python live_check.py [model]`.
- Seçenekler prompt'ta harf etiketli sunulur; sıra yanlılığı için seçenek sırasını karıştırma henüz yok.
