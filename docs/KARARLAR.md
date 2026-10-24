# KARARLAR — proje düzeyi kararlar (değiştirilmedikçe geçerli)

## K1. LLM modeli: `gemini-3.7-flash` (Vertex AI) — 24 Ekim 2026, Tolga (önceki: `gpt-6-luna`, OpenAI)
- **Karar:** Projede LLM gereken her yerde (kod varsayılanları, denemeler, demo) `gemini-3.7-flash` kullanılır. Kullanıcı açıkça değiştirmedikçe başka model seçilmez.
- **Uygulama:** `code_kit/decision_models.py` → `GeminiProvider(model="gemini-3.7-flash")`; `code_kit/live_check.py` ve `app_stub.py` (canlı mod) aynı. Anahtar: kök `.env` içinde `VERTEX_AI_KEY` (`load_env()` okur; gitignore'da).
- **Modelin bilinen kısıtları (canlı test, 24 Ekim):** `logprobs` kullanılmıyor (strateji otomatik `multi_sample`); düşünme kapatılamıyor ve düşünme token'ları `maxOutputTokens`'tan yer → `thinkingLevel=low` + 1024 pay. Kodda ele alındı.
- **Değişirse:** `GeminiProvider` varsayılanını, `live_check.py`'yi, `app_stub.py`'yi ve bu dosyayı güncelle. `OpenAIProvider` (gpt-6-luna) ve `AnthropicProvider` varsayılanı (`claude-sonnet-5-5`) yedek olarak duruyor, canlı test edilmedi.
- **Not:** Bu karar demo/prod dışı sunum içeriğini de etkiler: slayt/Q&A'de "hangi LLM" sorusuna cevap `gemini-3.7-flash`; model hakkında bu oturumda ölçülmüş doğruluk/maliyet verisi yok.

- **Güncelleme (24 Ekim, case sonrası, Tolga):** Cobalt simülasyonunda **deneyler `gemini-3.5-flash-lite`** (≈1 sn, düşünme yok, çok koşu/seed için); **persona üretimi ve teslim edilen 5 koşu `gemini-3.7-flash`**. İki model arasındaki tutarlılık E10 deneyiyle kontrol edilir. B planı: 16:30'da 3.7 ile 5 koşu 15 dk'yı aşıyorsa final koşular lite ile yapılır (TEAM_DOC'ta gerekçe). Anahtar: önce `TALP_KEY` env, yoksa `.env → VERTEX_AI_KEY`. Ayrıntı: `docs/07_COBALT_PLAN.md`.

## K2. Dosya yapısı (kullanıcı değiştirdi, 24 Ekim)
`code_kit/` (kod, testler, README, tests_report.md) · `docs/` (00–07 dokümanları, KARARLAR.md, `talp_db/`) · kök: `CLAUDE.md`, `README.md`, `.env`, `.venv/`.

## K3. Case: Cobalt Bank, çözüm planı — 24 Ekim 2026, Tolga
- **Şirket:** Cobalt Bank (`talp-hackathon-participants/yeni-case-5-sirket/10-cobalt-bank.md`).
- **Geçerli plan:** `docs/07_COBALT_PLAN.md` (onaylı). Kaynak sırası: dossier/challenge > `docs/talp_db/` > tahmin.
- **Personalar:** `docs/talp_db/data/theory/persona_design.json` tasarımına göre 75 persona (DOE 2^4 / 2^(4−1) + klon). Alanları kod örnekler, hikâyeyi LLM yazar. İki turlu haftalık etkileşim (DM, soru/cevap, kamusal feed).
- **Kod:** `code_kit/cobalt/`. Parametreler tek dosyada (`params/default.toml`) + `--params` / `--set` override katmanları.
- **Koşu kayıtları:** her koşu `outputs/runs/<YYYYMMDD-HHMMSS>_<ad>/` altında; hiçbir sonuç üzerine yazılmaz; `outputs/index.csv` append-only. Teslim paketi seçilen koşuları kopyalayarak kurulur.
