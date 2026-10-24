# KARARLAR — proje düzeyi kararlar (değiştirilmedikçe geçerli)

## K1. LLM modeli: `gemini-3.7-flash` (Vertex AI) — 24 Ekim 2026, Tolga (önceki: `gpt-6-luna`, OpenAI)
- **Karar:** Projede LLM gereken her yerde (kod varsayılanları, denemeler, demo) `gemini-3.7-flash` kullanılır. Kullanıcı açıkça değiştirmedikçe başka model seçilmez.
- **Uygulama:** `code_kit/decision_models.py` → `GeminiProvider(model="gemini-3.7-flash")`; `code_kit/live_check.py` ve `app_stub.py` (canlı mod) aynı. Anahtar: kök `.env` içinde `VERTEX_AI_KEY` (`load_env()` okur; gitignore'da).
- **Modelin bilinen kısıtları (canlı test, 24 Ekim):** `logprobs` kullanılmıyor (strateji otomatik `multi_sample`); düşünme kapatılamıyor ve düşünme token'ları `maxOutputTokens`'tan yer → `thinkingLevel=low` + 1024 pay. Kodda ele alındı.
- **Değişirse:** `GeminiProvider` varsayılanını, `live_check.py`'yi, `app_stub.py`'yi ve bu dosyayı güncelle. `OpenAIProvider` (gpt-6-luna) ve `AnthropicProvider` varsayılanı (`claude-sonnet-5-5`) yedek olarak duruyor, canlı test edilmedi.
- **Not:** Bu karar demo/prod dışı sunum içeriğini de etkiler: slayt/Q&A'de "hangi LLM" sorusuna cevap `gemini-3.7-flash`; model hakkında bu oturumda ölçülmüş doğruluk/maliyet verisi yok.

## K2. Dosya yapısı (kullanıcı değiştirdi, 24 Ekim)
`code_kit/` (kod, testler, README, tests_report.md) · `docs/` (00–06 dokümanları, KARARLAR.md) · kök: `CLAUDE.md`, `README.md`, `.env`, `.venv/`.
