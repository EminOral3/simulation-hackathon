# KARARLAR — proje düzeyi kararlar (değiştirilmedikçe geçerli)

## K1. LLM modeli: `gpt-6-luna` (OpenAI) — 24 Ekim 2026, Tolga
- **Karar:** Projede LLM gereken her yerde (kod varsayılanları, denemeler, demo) `gpt-6-luna` kullanılır. Kullanıcı açıkça değiştirmedikçe başka model seçilmez.
- **Uygulama:** `code_kit/decision_models.py` → `OpenAIProvider(model="gpt-6-luna")`; `code_kit/live_check.py` varsayılanı aynı. Anahtar: kök `.env` içinde `OPENAI_KEY` (`load_env()` okur; gitignore'da).
- **Modelin bilinen kısıtları (canlı test, 24 Ekim):** `logprobs` desteklenmiyor (strateji otomatik `multi_sample`); `temperature` yalnız 1 (0.0 reddedilir); `max_tokens` yerine `max_completion_tokens`. Kodda ele alındı.
- **Değişirse:** `OpenAIProvider` varsayılanını, `live_check.py`'yi ve bu dosyayı güncelle; `supports_logprobs` kuralını (`model.startswith("gpt-6")`) gözden geçir. `AnthropicProvider` varsayılanı (`claude-sonnet-5-5`) yedek olarak duruyor, canlı test edilmedi.
- **Not:** Bu karar demo/prod dışı sunum içeriğini de etkiler: slayt/Q&A'de "hangi LLM" sorusuna cevap `gpt-6-luna`; model hakkında bu oturumda ölçülmüş doğruluk/maliyet verisi yok.

## K2. Dosya yapısı (kullanıcı değiştirdi, 24 Ekim)
`code_kit/` (kod, testler, README, tests_report.md) · `docs/` (00–06 dokümanları, KARARLAR.md) · kök: `CLAUDE.md`, `README.md`, `.env`, `.venv/`.
