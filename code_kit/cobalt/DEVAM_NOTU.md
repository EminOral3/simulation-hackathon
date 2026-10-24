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

## Haftalık planlayıcı (her hafta başında, < 10 dk)
Her yarım saatte, yeni hafta başlar başlamaz (duyuru `announcements.json`'a girildikten sonra):
```
.venv/bin/python -m code_kit.cobalt.planner --week N --locked locked.json --live --validate [--overrun "on time"]
```
- `--week N`: şu an koşan şirket haftası (13:00 öncesi 0). Haftası ≤ N olan kararlar sabit kabul edilir; yeni/değişen karar en erken N+1'de başlar.
- `--locked`: dashboard'da şu an kilitli olanlar (`params/decisions/` formatı). Haftası > N olanlar yeniden optimize edilir, raporda "currently locked" satırıyla karşılaştırılır.
- Gelen sürprizler `announcements.json`'dan okunur. `archetypes` boşsa duyuru bir lite LLM çağrısıyla kütüphanedeki (`data/surprise_library.json`, 14 kötü + 5 iyi) arketiplere sınıflandırılır; raporda "LLM:" ya da "our reading" yazar.
- 6. hafta bittikten sonra migration'ın nasıl bittiğini `--overrun` ile ver (`on time` / `a few hours late` / `into Monday`).
- Ne yapar: (A) tek aksiyon × hedef × hafta, ~750 karar, 5 senaryoda eleme → (B) her haftanın en iyi 6 aksiyonunun 2'li/3'lü kombinasyonları → (C) en iyi 40 kararın çiftleri, 13 senaryo (sürprizsiz + rastgele iyi/kötü karışımlar) × 3 migration sonucu × 2 tekrar → playbook (her arketip "bir sonraki hafta gelirse" en iyi cevap) → `--validate`: en iyi 3 plan + kararsız, gerçek LLM ile (lite, 1 seed, ~4-5 dk).
- Çıktı: `outputs/planner/<ts>_w<N>/report.md`, `candidates.csv`, `plan_rank{1..5}.json` (kilitlemeye hazır karar dosyası; mesaj metnini gözden geçir, gerçekleri koru).
- Surrogate (`surrogate.py`): LLM koşularından "ne gördü → ne yaptı" öğrenen lojistik model. Hızlı simülatör (`fastsim.py`) aynı dünya, ağ ve kuyrukla ~800 plan-simülasyonu/sn. **Yalnız eleme içindir; teslim koşuları LLM.** Yeni LLM koşuları geldikçe: `python -m code_kit.cobalt.surrogate fit --min-time <ts>` sonra `python -m code_kit.cobalt.surrogate_check` (koşu düzeyi doğruluk; rapora girer).
- Eğitim verisi üret: `python -m code_kit.cobalt.trainset --n 32 --seed <yeni>` → `python -m code_kit.cobalt.experiments train_<seed> --live`.

## API kredisi (16:05, hedef: yarıya indirmek)
- `[budget]` bölümü (`params/default.toml`), varsayılan açık; `--set budget.lean_prompts=false` eski prompt'ları birebir geri getirir.
  - Tur A yalnız önemli olayda (yeni şirket mesajı, migration, sürpriz haberi, destek deneyimi, itiraz kredisi) ya da arkadaştan Cobalt'la ilgili mesajda. Rakip reklamı tek başına, süren kampanya satırı ve sohbet zinciri tur A açtırmaz (eskiden tur A'ların %48'i buydu). Cevaplar tur B'ye yine "what people told you" olarak gider.
  - Geçmiş: tur B son 2, tur A son 1 haftanın notu tam; eskiler tek satır durum. Kilitli şirket mesajı yalnız ulaştığı hafta tam, sonra ilk 160 karakteri (check.py şartı korunur).
  - Kimlik kartı aynı alanlarla kısa etiketli tek paragraf (~%20 kısa). Talimatlar sıkıştırıldı; durum tanımları aynen.
  - Serbest metin kısa: thoughts 1 cümle, memory_note 40 kelime, yorum/cevap 20 kelime.
  - Tahmin (T25 seed 1 gerçek prompt'larına kurallar uygulanarak): prompt −%37, cevap −%37, tur A çağrısı 548 → ~280-330.
- Deney ızgaraları: `experiments <spec> --live --confirm-top K` → hepsi 1 seed, ikinci seed yalnız en iyi K. 32×2 = 64 koşu yerine 32 + K.
- Her canlı çağrının gerçek token sayısı `calls.jsonl` → `usage`, koşu toplamı `meta.json` → `tokens`.
- Dikkat: prompt değiştiği için disk cache eski koşulardan cevap vermez; değişiklikten sonraki ilk koşular tam ücretli. Eski ve yeni prompt'lu koşular doğrudan karşılaştırılmaz (teslim koşuları hep aynı ayarla).

## Son kalibrasyon (16:45-17:00, final duyurular + kilitli kararlar)
- Kararlar: `params/decisions/final.json` = `team-04_decisions.json` → `run_decisions` (kilitlendiği gibi; config "→" ve "+150 staff" yazımlarını tanır). Paket referansı `metrics_v2.canonical_decisions = "final"`.
- Duyurular: `announcements.json` son hali (3, 4. hafta kart krizi; 7. hafta kapanma + migration sonucu; 8. hafta kapanma güncellemesi). Migration sonucu `known_outcome: "a few hours late"` → her koşuda (plan_nosurprises dahil) aynı; 6. haftada personalar gerçek sonuç metnini görür.
- Düzeltilen hata: crisis_kb A05 şablonu ("Persona event: $87 charge") haberi gören herkese kişisel olay yazıyordu → 3. haftada personaların ağırlıklı %69'u desteği arıyordu, bekleme 180 dk, kayıp ~%20. Kişisel olay artık bilinen sıklıkla (`affected_share` = 9.000/2,1M) ya da açık eşleşmeyle (kapanma: mesleği federal olan) çekilir; dashboard duyurularına uydurma "News" satırı eklenmez.
- Kalibrasyon çıpası (kararsız, sürprizsiz, lite s1): aktif %99,3, mevduat %98,8 → sanity sınırlarında.
- Sonuç (lite, v2): plan s1 98,8 / 103,9 / 4,46; plan s2 99,7 / 102,3 / 4,45; kararsız s1 99,3 / 104,2 / 4,46. CFPB ölçülemez (olay az).
- Dikkat: plan ile kararsız kontrol artık ayırt edilemiyor; mevduat >%100 "para ekledim" cevaplarından geliyor (girişler sayılmazsa 99,6 / 96,5 / 99,1).

## Karar kilitleme
- Karar dosyası: `params/decisions/<ad>.json` → `{"decisions": [...kilitlenen hali...], "filters": {"1": {"groups": [...], "where": {"lives_paycheck_to_paycheck": "yes"}}}}`. Aksiyon adları/seviyeleri `docs/talp_db/data/crises/decision_menu.json` etiketleriyle aynı olmalı; `budget_check` menü/bütçe/600 karakter/3 satır why denetler.
- Teslimdeki karar dosyası `params/decisions/plan.json` (dashboard'da kilitlenenle birebir aynı olmalı).

## Bilinen sınırlar / yapılacaklar
- Kural tabanlı baz (E8) ve hafızasız varyant (E9) henüz kodlanmadı.
- `support` ve `metrics` parametrelerinin çoğu VARSAYIM; duyarlılık için `--set` ile deney koş.
- `team` parametresi `team-NN`: paketlemeden önce `--set run.team="team-07"` gibi gerçek numarayı ver.

## Canlı "personaya soru sor" (tools/ask_persona.py, 24 Ekim 17:30)
- Teslim run'ını yalnız okur (`--run runs/plan_1` varsayılan; yoksa `outputs/submissions/*/runs/plan_1`), her soru tek çağrı: `gemini-3.5-flash-lite`, thinking kapalı, temp 0.7, seed 7, 15 sn timeout + 1 retry. Persona yalnız kendi round-B prompt'unda gördüğü satırları (kurul mesajı kelimesi kelimesine, haberler, kişisel olaylar), status/money/memory_note'u bilir.
- Komutlar: `--list`, `--suggest`, `--timeline P07`, `--persona P07` (etkileşimli; "exit"), `--prerecord` (3 öneri × 6 soru → `tools/prerecorded.json`). Log: `tools/live_log.jsonl`.
- Hata/anahtar yok/Wi-Fi yok → `--fallback` dosyasından en yakın hazır cevap "(cached)"; `--offline` API'yi hiç denemez. Sunumdan önce teslim run'ı üzerinde `--prerecord` koşulmalı.
