# DEVAM NOTU — Cobalt simülasyonu (code_kit/cobalt)

Plan: `docs/07_COBALT_PLAN.md`. Bütün komutlar repo kökünden: `.venv/bin/python -m code_kit.cobalt.<modül>`. `--live` yoksa mock çalışır (API'ye gitmez).

## Durum (24 Ekim, 12:47)
- Uçtan uca hat çalışıyor: mock 5 koşu → `package.py` → `check.py` "Nothing to fix." (klasör + zip).
- Canlı persona seti: `data/personas/20261024-123642_v2` (75 persona, hikâyeler gemini-3.7-flash, kalite kapısı 75/75).
- Canlı lite koşu: 75 persona × 10 hafta ≈ 1.300 çağrı, tek koşu ≈ 3–5 dk (paralel koşularda daha uzun).
- Testler: `.venv/bin/python -m pytest -q code_kit/cobalt/tests` (7 test, ~7 sn, API yok).

## İlk deney sonuçları (lite, 2 seed; yalnız bilinen kriz, sürpriz yok)
- E1 (`outputs/experiments/20261024-124356_e1_k1`): nodecision aktif 92.0 / mevduat 93.6 (iki hedef de tutmuyor); plan 98.6 / 101.1. K1 varyantları arası farklar seed gürültüsü içinde; sağlam bulgu: "herhangi bir K1 >> karar yok". K2 (yeni paraya boost) mevduatı ~+3 puan artırıyor (plan 101.1 vs k1-only 98.3).
- Seed 2'de migration uzaması kötü çekildi → kayıplar büyüyor: belirsizliğin ana kaynağı uzama süresi.
- E11 plan altında (`..._e11_network`): ağ açık/kapalı farkı küçük (aktif 99.8 vs 98.7); plan krizi yumuşattığı için yayılacak öfke az.
- E11b nodecision altında (`..._e11b_network_nodecision`): ağ açık 93.95 / 93.2, kapalı 94.0 / 94.3 → hedef düzeyinde etkileşim etkisi 2 seed'le gürültü içinde. Mikro düzeyde akran etkisi var (aşağıda) ama toplamı doğrudan deneyim + kuyruk belirliyor. Daha çok seed ve söylenti tipi sürprizde (A07) yeniden ölçülmeli.
- nodecision e0 analizi: olumsuz DM alanların %9.2'si ertesi hafta harekete geçti, almayanların %4.2'si; başta 74/75 "kalırım" dedi, %12'si çıktı (say-do).
- Not: E1 sonrası metrik/prompt değişti (CFPB smoothing, güven kelimeyle). Karşılaştırmalar aynı kod sürümüyle yeniden koşulmalı.

## Sık komutlar
| İş | Komut |
|---|---|
| Tek koşu (lite) | `run --type plan --seed 1 --decisions plan --live --label deneme` |
| Teslim modeli | `... --model final` (gemini-3.7-flash) |
| Parametre değiştir | `... --set network.enabled_feed=false --set metrics.k_rating=1.5` veya `--params dosya.toml` |
| Parametreleri gör | `params --show [--set ...]` |
| Deney ızgarası | `experiments e1_k1 --live` (spec: `params/experiments/*.toml`) |
| Persona seti üret | `personas build --live --label v3` (eski setler silinmez; `personas.persona_set` seçer, varsayılan en yeni canlı set) |
| Persona listesi | `personas show [--id P17]` |
| Canlı soru | `ask_persona --run <klasör parçası> --persona P17 "soru" --live` · `--list` ile kim ne durumda |
| Analiz | `analysis <run> [<run_seed2>]` → kalite (S, entropi, ters kodlu, say-do), DOE etkileri, akran etkisi, kaskadlar |
| Ana grafik | `report --plan <r1> <r2> --nodecision <r1> <r2> --name final` |
| Paket | `package --auto --model gemini-3.7-flash` (ya da slot slot `--plan_1 <dir>` ...) |

## Kayıt düzeni (hiçbir şey üzerine yazılmaz)
- Koşular: `outputs/runs/<YYYYMMDD-HHMMSS>_<type>_s<seed>_<model>_<label>/` (+ `params.resolved.json`, `meta.json`, `interactions.jsonl`, `queue.jsonl`, `log.txt`).
- Kayıt defteri: `outputs/index.csv` (append-only). Deneyler: `outputs/experiments/<ts>_<ad>/summary.csv`, `means.json`.
- Paketler: `outputs/submissions/<ts>_<team>/` (koşular kopyalanır). Grafikler: `outputs/reports/<ts>_<ad>/`.
- LLM cache: `outputs/cache/` (anahtar = model + seed + prompt). Aynı koşu tekrarlanırsa cache'ten gelir; geç duyuruda yalnız değişen haftalar yeniden sorulur.

## Duyuru geldiğinde (Gürkan, her :00 / :30)
1. `docs/talp_db/data/crises/announcements.json` → `items`'a ekle: `{"week": N, "surprise": true, "source": "dashboard", "text": "<aynen>", "archetypes": [], "severity": "base", "update_of": null, "reading": "<bizim okumamız>"}`. `archetypes` boşsa sınıflandırıcı seçer; `crisis_kb.json` id'leriyle elle de verilebilir.
2. Okumayı TEAM_DOC'a yaz.
3. Deneyleri yeniden koş (cache sayesinde yalnız N. haftadan sonrası yeni).

## Karar kilitleme
- Karar dosyası: `params/decisions/<ad>.json` → `{"decisions": [...kilitlenen hali...], "filters": {"1": {"groups": [...], "where": {"lives_paycheck_to_paycheck": "yes"}}}}`. Aksiyon adları/seviyeleri `docs/talp_db/data/crises/decision_menu.json` etiketleriyle aynı olmalı; `budget_check` menü/bütçe/600 karakter/3 satır why denetler.
- Teslimdeki karar dosyası `params/decisions/plan.json` (dashboard'da kilitlenenle birebir aynı olmalı).

## Bilinen sınırlar / yapılacaklar
- Kural tabanlı baz (E8) ve hafızasız varyant (E9) henüz kodlanmadı.
- `support` ve `metrics` parametrelerinin çoğu VARSAYIM; duyarlılık için `--set` ile deney koş.
- `team` parametresi `team-NN`: paketlemeden önce `--set run.team="team-07"` gibi gerçek numarayı ver.
