# Cobalt Bank: 10 haftalık persona simülasyonu, çözüm planı

> **Adım 0 (onaydan hemen sonra):** Bu plan `docs/07_COBALT_PLAN.md` olarak repoya kopyalanır. `docs/KARARLAR.md`'de K1 güncellenir (deneyler `gemini-3.5-flash-lite`, teslim ve persona üretimi `gemini-3.7-flash`). K3 eklenir: şirket Cobalt; veri kaynağı `docs/talp_db/`; 75 persona tasarımı. Implementation, kullanıcı ayrıca isteyene kadar başlamaz.

## Context
Case belli: TALP Simulation Lab, şirketimiz **Cobalt Bank**. Gerçek zamanlı takvim 13:00'te başlıyor (30 dk = 1 hafta, 18:00'de bitiyor). **Tam 2 karar** veriyoruz (bütçe $4M, menü, kırmızı çizgiler). Bilinen kriz 6. haftada: core banking geçişi (36 saat salt-okunur app, offline kart limiti $100, süre uzayabilir, maaş günü Cuma 11 Aralık). Bilinmeyen sürprizler hafta başlarında dashboard'a düşecek.

**Teslim (18:00):**
- 5 koşu: `plan_1/2`, `nodecision_1/2`, `plan_nosurprises`
- `CLIENT_MEMO.md`, `TEAM_DOC.md`, `code/`
- Yapı `check.py` ile denetleniyor.

**Sunum (18:30):** 5 dk; board bir personaya canlı soru soracak. Jüri 5 kriter puanlıyor: reasoning, own idea, approach comparison, working example, limits/next.

**Bize iletilen öncelik:** Personalar ve personaların birbiriyle etkileşimi hackathonun en önemli noktası. Plan bu yüzden persona kalitesi (bölüm 3) ve etkileşim katmanı (bölüm 4) üzerine kurulu. Geri kalan her şey (metrik, karar, paketleme) bunlara hizmet eder ve sade tutulur.

**Kaynak sırası** (`docs/talp_db/README_DB.md`): dossier ve challenge > `docs/talp_db/` > tahmin.

Kullanılanlar:
- Persona: `talp_db/docs/theory/03_PERSONA_DESIGN.md`, `data/theory/persona_schema.json`, `persona_design.json`, `population_priors.json`
- Teori: `01_THEORY_AND_DESIGN.md`, `02_LITERATURE.md` (D1–D7)
- Metrik: `metric_spec.json`
- Kriz: `crisis_kb.json`, `CRISIS_PLAYBOOK.md`, `announcements.json`
- Karar: `decision_menu.json`
- Eski hazırlıktan: 00 (zaman noktaları, B planı), 03 #3 (kuyruk→churn), 04 (Q&A şablonları)

Atlananlar: 06 Türkiye/WVS verisi, MNL/conjoint, app_stub fiyat demosu, `LLMPersonaModel` tek-adım arayüzü, verbalized sampling (Özkan 2026 uyarısı; ana koşularda kullanılmıyor).

**Çözülen çelişkiler:**

| Konu | `talp_db` | Plan kararı |
|---|---|---|
| Model | flash-lite | Kullanıcı kararı: deneyler lite; persona üretimi ve teslim 3.7-flash |
| Anahtar | `TALP_KEY` | Önce `TALP_KEY`, yoksa `.env → VERTEX_AI_KEY` |
| Kod yolu | `code/...` | `code_kit/cobalt/`; `package.py` bunu `code/` olarak paketler |
| Persona sayısı | 01'de 64, 03'te 75 | **75** (DOE + klon; en ağır persona ~74k müşteri) |
| Ağırlık tabanı | `weight_customers` toplam müşteriye göre (2.1M) | G1 aktifler üzerinden tanımlı: `w_active = weight_customers × active_share(group)`. Hücre içinde aktif payı sabit (VARSAYIM); tüm personalar aktif başlar, dormant segmentin deposits'i sabit tutulur |
| Çıktı biçimi | `Status:` / `Money:` satırları | JSON mode (`status`, `money` alanları); `check.py` normalize ederek kelime aradığı için geçer. Sorun çıkarsa satır formatına dönülür |

---

## 1. Karar kartı
1. **Karar verici:** CEO + board (CFO: G2 ve bütçe, CMO: G1, CRO: G3). Karar: hangi 2 müdahale, hangi hafta, kime, hangi mesajla.
2. **LLM kapısı:** Persona davranışı kural gereği LLM'den gelmek zorunda. Bu yüzden **hibrit**: persona der/yapar/konuşur/karar verir LLM'de; dünya mekaniği, mesaj yönlendirme, kuyruk ve metrikler deterministik Python. LLM'siz baz kural modeli yalnız karşılaştırma için.
3. **Yöntemler:**
   - DOE ile tasarlanmış persona paneli + post-stratification (03 §3)
   - İki turlu haftalık döngüde **persona–persona etkileşim ağı**
   - Erlang-C destek kuyruğu geri beslemesi
   - Exit–Voice–Loyalty çerçevesiyle metrik eşleme
   - CRN + tabakalı bootstrap
4. **Kendi fikirlerimiz:**
   - **Deney tasarımıyla persona kapsaması** (2^4 / 2^(4−1)) sayesinde her davranış ekseninin etkisi ayrıştırılabiliyor: "söylentiye inanan tasarrufçular kaç kat fazla para taşıdı?" sorusu cevaplanabilir hale geliyor ve K2'nin target'ı buna göre seçilir.
   - **Kuyruk döngüsü:** şikâyetler → Wq → sonraki haftanın deneyimi.
   - **Etkileşim payı:** ağ kapatılınca kaybın ne kadarının sosyal yayılımdan geldiği ölçülür.
5. **Ana grafik:** Hedef takip paneli. G1/G2/G3/G3b, plan ve nodecision karşılaştırmalı, CI bantlı, hedef çizgileri ve kriz işaretleri üzerinde. Destek grafik: etkileşim ağı animasyonu (hafta hafta kim kime ne dedi, status renkleri).
6. **Veri:** Dossier FACT'leri + `population_priors` / `persona_design` (VARSAYIM) + SHED çıpaları [KISMEN] + J.D. Power %13 niyet / %9 gerçek geçiş [KISMEN, Bankrate aktarımı].
7. **Roller:** bölüm 9.
8. **Riskler:** 3.7-flash süresi/kotası (iki tur × 75 persona); LLM aşırı tepkisi ve yankı odası etkisi (sanity bounds + ağ ablasyonu); ölçek parametrelerinin varsayıma bağlılığı.

---

## 2. Mimari ve dosyalar (`code_kit/cobalt/`)
| Dosya | İçerik |
|---|---|
| `config.py` | `talp_db/data/*` yükleyici; VARSAYIM parametreleri açık; `budget_check()`: ≤ $4M, SMS $25k/gönderim, 1–3 aksiyon, mesaj ≤ 600 karakter, `why` = 3 satır, yalnız menü seviyeleri |
| `llm.py` | `google-genai` aio, `seed` + `temperature=1.0`, JSON schema, retry 5, semaphore. **Cache anahtarı (model, seed, prompt)** ile artımlı yeniden koşu; tüm çağrılar `calls.jsonl`'a loglanır. Mock varsayılan, gerçek API `--live` ile |
| `personas.py` | Bölüm 3'teki üretim hattı → `data/personas.jsonl` (dondurulur) |
| `network.py` | Sosyal ağ (bölüm 4.1) → `data/network.json` (dondurulur; `personas.jsonl`'a `ties` alanı olarak girer) |
| `crisis.py` | `classify`, `world_items`, `sanity_check`. `calibration_anchors` asla prompt'a girmez |
| `world.py` | Takvim, BAU, migration, rakip, maruziyet, feed derleme |
| `interact.py` | DM/soru yönlendirme, kamusal feed sıralaması (etkileşim × ağırlık), söylenti izleme |
| `support_queue.py` | `sim_core.erlang_c` ile Wq |
| `agent.py` | Prompt'lar: hikâye, tutarlılık kontrolü, tur A, tur B, probe, canlı Q&A |
| `engine.py` | Haftalık döngü: dünya → tur A → yönlendirme → tur B → güncelleme; checkpoint |
| `metrics.py`, `analysis.py` | Goal'ler + CI; persona kalite metrikleri; DOE ana etkileri; ağ/yayılım metrikleri |
| `baseline_rule.py`, `run.py`, `experiments.py`, `report.py`, `ask_persona.py`, `package.py`, `DEVAM_NOTU.md` | Karşılaştırma; CLI; deney ızgarası; grafikler; canlı soru; paketleme + `check.py` |

**Kit'ten yeniden kullanım:** `load_env`, `DiskCache` (anahtar genişletilir), `sim_core.erlang_c / mmc_analytic / ba_graph`, `validation.bootstrap_ci / mode_collapse_index`, `roi.Param / tornado`. Tek yeni bağımlılık: `google-genai`.

### 2.1 Parametreler: tek yerden, kolay değiştirilebilir
- **Kod içinde sihirli sayı yok.** Ayarlanabilir her şey `code_kit/cobalt/params/default.toml` dosyasında durur (TOML, stdlib `tomllib`, ek bağımlılık yok). Bölümler:
  - `[llm]` model_experiment, model_final, temperature, concurrency, thinking_level, cache
  - `[personas]` persona_set (hangi dondurulmuş set), memory_words, story_model
  - `[network]` strong_ties_min/max, leader_degree_boost, homophily, cross_group_links, feed_size, dm_max, enabled_ties, enabled_feed
  - `[turns]` round_a_skip_if_quiet, max_replies
  - `[world]` migration overrun dağılımı, severity, channel exposure olasılıkları, rakip kampanya haftaları, surprises_on
  - `[support]` base_agents, target_wait_min, peak_hour_factor
  - `[metrics]` out_fraction, k_rating, cfpb_floor, bootstrap_n
  - `[sanity]` sanity_bounds kopyası
  - `[paths]` talp_db, outputs, cache
- **Değer kaynağı:** `talp_db` JSON'larındaki VARSAYIM değerleri burada **referansla** tutulur (varsayılan = JSON'daki değer). Elle değiştirilmiş her değer `# VARSAYIM: neden` yorumu taşır.
- **Katmanlı override, sırayla:**
  1. `default.toml`
  2. `--params experiments/e11_no_network.toml`: kısmi dosya, deep merge; her deney yalnız değişen anahtarları içerir.
  3. `--set network.enabled_feed=false --set metrics.k_rating=1.5`: tek seferlik CLI override.
- **Kararlar ayrı dosyada:** `params/decisions/<ad>.json`. Duyurular `talp_db/data/crises/announcements.json`'da. Üçü birlikte bir koşuyu tam tanımlar.
- **Doğrulama:** yüklemede bilinmeyen anahtar veya tip hatası çalıştırmayı durdurur (yazım hatası sessizce varsayılana düşmesin). `python -m code_kit.cobalt.params --show` çözülmüş parametreleri basar.

### 2.2 Koşu kayıtları: hiçbir sonuç üzerine yazılmaz
- **Her koşu kendi klasörüne:** `code_kit/cobalt/outputs/runs/<YYYYMMDD-HHMMSS>_<type>_s<seed>_<model-kısa>[_<etiket>]/`. Örnek: `20261024-143212_plan_s1_lite_e11-noties`. Klasör `exist_ok=False` ile açılır; aynı saniyede çakışırsa `-2`, `-3` eki alır. Var olan bir koşu klasörüne hiçbir kod yazmaz.
- **Klasör içeriği:**
  - Challenge'ın 6 dosyası
  - `params.resolved.json`: tüm katmanlar birleşmiş, son hali
  - `decisions.json` ve `announcements.snapshot.json`: koşu anındaki kopyalar
  - `meta.json`: başlangıç/bitiş zamanı, süre, çağrı sayısı, cache hit oranı, git commit + dirty bayrağı, persona_set, parametre/karar/duyuru hash'leri
  - `interactions.jsonl` (DM, soru, cevap, post) ve `log.txt`
- **Deney grupları:** `outputs/experiments/<timestamp>_<deney-adı>/` içinde `summary.csv` ve alt koşulara linkler. Koşular yine `outputs/runs/` altında durur, deney klasörü onları referansla gösterir.
- **Kayıt defteri:** `outputs/index.csv` append-only; koşu başına bir satır (timestamp, klasör, type, seed, model, etiket, hash'ler, goal_1..3b, süre, durum: ok/failed/partial). Yarıda kalan koşu silinmez, `partial` olarak işaretlenir. `python -m code_kit.cobalt.runs list|show|diff A B` ile listelenir ve karşılaştırılır.
- **Persona setleri de sürümlü:** `data/personas/<timestamp>_<etiket>/` (`personas.jsonl`, `network.json`, üretim çağrıları, kalite raporu). Hangi setin kullanılacağını `personas.persona_set` seçer; yeni üretim eskisini ezmez.
- **Teslim paketi kopyalayarak kurulur:** `package.py --plan_1 <run_dir> --plan_2 ... --nodecision_1 ... --nodecision_2 ... --plan_nosurprises ...`. Seçilen koşular `outputs/submissions/<timestamp>_team-NN/runs/plan_1/` vb. altına **kopyalanır**; zip aynı klasöre yazılır. Orijinal koşular ve önceki paketler yerinde kalır.
- **LLM cache** içerik adreslidir (`outputs/cache/`, anahtar = model + seed + prompt hash). Yalnız ekleme yapılır, koşu sonuçlarından ayrıdır.
- `outputs/` git'e girmez (`.gitignore`), silinmez. Seçilen final koşular `package.py` ile ayrıca saklanır.

---

## 3. Personalar: "önce dağılım, sonra hikâye" (en çok özen gösterilecek kısım)
**3.1 Tasarım** (`persona_design.json`, değişmeden kullanılır): 75 slot. Her grupta 4 davranış ekseni var; 16 kişilik gruplarda tam 2^4 faktöriyel, 8 kişilik gruplarda 2^(4−1) yarım fraksiyon (I=ABCD). 75k'dan ağır hücreler klonlanır (everyday'de 11 klon). Kapsama tasarımdan, temsil ağırlıktan gelir (`weight_customers`, `cell_prob`).

**3.2 Alan doldurma (kod, seed'li):** `persona_schema.json`'daki tüm `fixed` alanlar, eksen seviyeleriyle **tutarlı** koşullu kurallarla örneklenir. Örnekler:
- fragility=paycheck to paycheck → gelir bandı düşük/orta, balance <1k–10k
- fdic_exposure=over → balance 250k+ ya da knows_fdic=unsure
- students → yaş 19–24, who_pays bilgisi
- small business → ticket_size'a göre hafta sonu satış tutarı

Kurallar `personas.py`'de tablo halinde tutulur ve TEAM_DOC'a aynen girer. Ek alanlar:
- **İsim:** ortak ABD isimleri listesinden, özniteliklerden bağımsız rastgele; etkileşim ve canlı soru için gerekli. Karar girdisi değildir.
- Hassas özellik yok. Yaşam tarzından en fazla 1 detay (insan dokusu için).

**3.3 Hikâye (LLM, 3.7, bir kez):** 03 §4 şablonu kullanılır. 4–6 cümle, birinci tekil şahıs; yalnız verilen alanlar kullanılır. İçerir: Cobalt'ı neden açtığı, geçmiş bir para/banka deneyimi, bir hafta sonu parasına ulaşamazsa ne yapacağı. Li 2025 uyarısı gereği **alanları LLM uydurmaz**.

**3.4 Kalite kapısı (her persona, otomatik):**
1. Tutarlılık kontrol çağrısı: anlatı alanlarla çelişiyor mu (evet/hayır + hangi alan). Çelişki varsa farklı seed ile yeniden yazılır, en fazla 2 deneme.
2. Kalıp yargı / hassas kelime taraması (liste).
3. Tekrar taraması: anlatılar arası gömme veya n-gram benzerliği; aşırı benzer çiftler yeniden yazılır, özellikle klonlarda.
4. Emin elle 10 persona okur (spot check).

**3.5 Durum biçimleri** (katalog talimatı: fixed / narrative / memory / dynamic):
- **memory_note:** ≤ 60 kelime, her hafta personanın kendi çağrısıyla yeniden yazılır.
- **dynamic:** status, money, trust_feeling 1–5, support_contacts, posted_this_week.
- **İlişki hafızası (yeni):** "Maya (coworker) told me she moved her savings" gibi; bağ başına son etkileşimin tek satırı.

**3.6 Persona testleri (koşudan önce):** hafta 0 probe üzerinde
- S: personalar arası ayrışma
- grup içi entropi
- eksen seviyeleri arasında yön testi (örn. vocal personalar "şikâyet ederim" demeye daha yatkın mı)

Ayrışma düşükse prompt revize edilir (persona alanlarının prompt'ta görünürlüğü, hikâyenin ağırlığı).

---

## 4. Etkileşim katmanı (ikinci öncelik ve ana farklılaştırıcı)
**4.1 Ağ** (`network.py`, seed'den bağımsız ve dondurulmuş; tüm koşularda aynı):
- **Güçlü bağlar** (aile/arkadaş/iş grup sohbeti): persona başına 3–6 bağ. Grup içi homofili ve gerçekçi çapraz bağlar (paycheck↔everyday iş arkadaşı, students↔students, small business↔müşterileri). `opinion_role=leads` olanlar daha yüksek dereceli: tercihli bağlanma (`sim_core.ba_graph` uyarlaması). Bağlar `personas.jsonl`'a `ties` olarak girer.
- **Kamusal kanallar:** persona `news_sources` alanına göre Reddit / X / TikTok / Facebook / aile grubunda "bulunur".
- **Cobalt dışı çevre:** başka bankadaki arkadaşın yorumu, rakip reklamı. `crisis_kb` şablonlarından gelir, persona değildir.

**4.2 İki turlu hafta:**
1. **Dünya adımı (kod):** olaylar, Cobalt mesajları (hedefe, kelimesi kelimesine), kriz haberi + `world_items` (maruziyete göre), kişisel deneyimler (reddedilen ödeme, P2P, destek bekleme), rakip; t−1'in kamusal postları feed'e (sıralama: yazarın `w` ağırlığı × geçen haftaki etkileşim).
2. **Tur A, "Fark et ve konuş"** (yalnız yeni uyaranı olan personalar; sessiz haftada atlanır). Çıktı: duygu, `public_post` (kanal), `messages` (en fazla 2 bağa DM), `question` (bir bağa "sen ne yapıyorsun?"), ön niyet.
3. **Yönlendirme (kod):** DM'ler ve sorular alıcılarına, kamusal postlar aynı kanaldaki personaların tur B görünümüne gider.
4. **Tur B, "Karar ver"** (tüm personalar). Persona tur A notunu, **aynı hafta** bağlarından gelen DM/soruları ve aynı haftanın kamusal postlarını görür. Karar verir: aksiyonlar, review, CFPB, destek, dispute, para, status. Gelen sorulara `replies` yazar; cevaplar sonraki haftanın tur A'sına gider. `weekly.jsonl` satırındaki `call` = tur B çağrısı.
5. **Durum güncelleme:** memory_note, ilişki hafızası, kuyruk, metrikler.

**4.3 Ölçek varsayımı:** 75 personalık ağ, gerçek ağın temsilî mikro örneği. Bir kamusal post `w` müşterinin benzer postlarını temsil eder ve feed'de bu ağırlıkla sıralanır. VARSAYIM, TEAM_DOC'a yazılır.

**4.4 Etkileşim analizi** (`analysis.py`):
- **Akran etkisi:** bir bağdan olumsuz DM/post aldıktan sonraki hafta status/money değişme oranı vs almayanlar.
- **Kaskad izi:** söylenti/şikâyet postunun hangi zincirle yayıldığı (kim → kim → ne yaptı).
- **R_eff:** olumsuz bir postun ürettiği yeni olumsuz post sayısı.
- **Ağ ablasyonu (E11):** bağlar ve feed kapalıyken aynı koşu; aradaki fark "etkileşimin payı".
- Canlı demoda tek bir zincir anlatılır: "Maya'nın Reddit postu → Jordan'ın DM'i → Jordan parasının bir kısmını taşıdı."

**Maliyet:** 75 persona × (tur A ~%60 + tur B) × 10 hafta ≈ 1.200 çağrı/koşu. Lite ile ≈ 1–2 dk; 3.7 ile ≈ 20 tur × ~20 sn ≈ 7 dk/koşu. 5 koşu paralel ve artımlı cache'le koşar.

---

## 5. Dünya mekaniği, krizler, kararlar
**Mekanik** (seed'li RNG, anahtar = seed, hafta, persona, amaç):
- CRN: `plan_k` ve `nodecision_k` aynı şokları paylaşır.
- Migration uzaması A01 `severity_prior`'dan çekilir.
- BAU: migration emaili 5 Aralık, olay sonrası holding statement, dispute kuralları.
- Mevsim arka planı (`calendar_context`, HİPOTEZ).
- Destek kuyruğu: hafta t'nin hacmi → Wq → hafta t+1'deki deneyim. 180 ajan + karar; bazda Wq 4 dk'ya kalibre.
- Bankayı değiştirmenin maliyeti (maaş yönlendirme, otomatik ödemeler) prompt'ta açık yazılı. Çıktı asla sonradan düzeltilmez.

**Duyuru prosedürü** (CRISIS_PLAYBOOK, 5 dk; Gürkan her :00 ve :30'da):
1. Metni kelimesi kelimesine `announcements.json`'a ekle.
2. `classify` → arketip ve şiddet.
3. Okumamızı TEAM_DOC'a yaz.
4. `world_items` → feed.
5. `menu_responses` / `message_rules` → N+1 karar adayları.
6. `sanity_check`.

`surprise:false` migration her koşuda açık; `plan_nosurprises` diğer duyuruları yüklemez.

**Kilitleme takvimi:**
- **K1: hedef 5. hafta, kilit 14:55.** Aday ([HİPOTEZ]): early pay (6. haftadan) + offline limit + extra support +150 (≈ $1.3M), target everyone. Dürüst mesaj: "expected" bitiş + güncelleme sözü (A01 rules), 9 Aralık erken maaş, freeze öncesi ödeme tavsiyesi. Kanallar push/email/in-app; SMS'ten kaçınılır (A04 oltalama algısı, E7).
- **K2: yer tutucu 15:00'te, 7. hafta** (boost 10 Ocak'ta bitecek şekilde hizalı). **Target, DOE ana etkilerinden seçilir** (örn. "paycheck customers who live paycheck to paycheck" → advance; rumor-prone savers → güven mesajı + boost). Sürpriz playbook'ları: A06/A07 → boost; A04/A05 → security pack + dispute credit; A01/A03 → advance / goodwill. Son değişiklik ≤15:55 (7. hafta) veya ≤16:25 (8. hafta). Free instant transfers G2'yi bozabilir. Boost'un $50k tavanı nedeniyle büyük saver'lara etkisi sınırlı; bu bulgu memo'ya girer.

---

## 6. Deneyler (lite; `experiments/summary.csv` → TEAM_DOC)
| # | Ne değişir | Ne ölçülür |
|---|---|---|
| E0 | nodecision × 2–3 seed | BAU çıpası (1.800 şikâyet, 120 CFPB, 4.6), seed uyumu |
| E1 / E2 | K1 6. hafta vs 5. hafta | G1, G3, zamanlama |
| E3 | Boost 7. hafta vs 5. hafta | G2 hizalama hipotezi |
| E4 | Mesaj: kesin saat vs "expected + update" | G3, güven |
| E5 | Surprises kapalı | Krizlerin katkısı |
| E6 | Destek +0 / +50 / +150 | Kuyruk döngüsü |
| E7 | SMS var/yok | Oltalama algısı |
| E8 | Kural tabanlı baz (LLM'siz) | LLM ne ekledi |
| E9 | Hafızasız; ilgisiz öznitelik ekli | Hafızanın değeri; sahte duyarlılık |
| E10 | lite vs 3.7 (~14:15) | Model tutarlılığı (yön uyumu) |
| **E11** | **Ağ kapalı (bağ + feed yok) / yalnız feed / yalnız bağ** | **Etkileşimin goal'lere payı; hangi kanal daha etkili** |
| **E12** | **K2 target varyantları** (DOE'den seçilen grup vs everyone) | Hedeflemenin değeri |

## 7. Metrikler ve doğrulama
**Formüller** (`metric_spec.json`, hafta 0'a oran, `w_active` ağırlıklı):
- `goal_1`: aktif %.
- `goal_2`: deposits %. `out_fraction` kümülatif maksimum (kept 0 / some 0.3 / most 0.8 / left 0.95, VARSAYIM).
- `goal_3`: `4.6 − k·Δneg_review`, k=2 (duyarlılık 1–3).
- `goal_3b`: `120 × max_month` oranı.
- `units` + `_ci`.

**Belirsizlik:** 2 seed + tabakalı bootstrap + k / out_fraction duyarlılığı.

**Exit–Voice–Loyalty sunumu:** exit = G1/G2, voice = G3, loyalty = affetme/main bank; grup ve eksen bazında tablo.

**Doğrulama:**
1. Seed uyumu (tavan, D5).
2. Entropi / modal pay (D3).
3. S ve R (D4).
4. Ters kodlu probe tutarlılığı.
5. Say-do: probe 2a/2b vs son status; dış çıpa %13 niyet / %9 gerçek.
6. `sanity_bounds`: haftalık kayıp ≤ %1; 10 haftada %0.5–3; deposits çıkışı %1–5; migration şikâyeti 1.5–4×. TSB üst sınırı aşılırsa önce prompt.
7. Yankı odası alarmı: R_eff > 1 iken ağ kapalı koşuyla fark çok büyükse önce prompt incelenir.
8. Kural baz modeliyle karşılaştırma.

Geçerlilik dili: Argyle'ın 4 kriteri (D6).

## 8. Teslim, sunum, demo
- **Final:** 16:00 freeze'den sonra 3.7 ile artımlı koşular. 17:30 duyurusu → yeniden koşu → `package.py` + `check.py` → 17:55 upload. **B planı:** 16:30'da ölçülen süre > 15 dk ise final koşular lite ile, gerekçesi TEAM_DOC'ta.
- `CLIENT_MEMO.md` (1 sayfa): ne kararlaştırdık ve neden; ne diyor (aralıklarla); neyi söyleyemez; neyi izlemeli; sonraki adım (200–300 gerçek müşteriyle check-in + PPI, D7).
- `TEAM_DOC.md`: persona tasarımı (DOE, alan kuralları, kullanılan/kullanılmayan öznitelikler ve nedenleri), etkileşim modeli, kriz okumaları, deney tablosu, karşılaşılan sorunlar, daha fazla zaman olsa ne yapardık.
- **Sunum (5 dk):** karar → persona tasarımı (DOE + ağ) → ana grafik → bir kaskad zinciri → canlı persona (`ask_persona.py`: profil + hikâye + 10 haftalık hafıza + aldığı/gönderdiği mesajlar; model 3.7, >10 sn ise lite) → karşılaştırmalar (E8/E10/E11) → sınırlar.
- Hazır cevap, "Personaları nasıl seçtiniz?" (03 §6): "Grupları ve sayıları dossier'den, kırılganlık ve dolandırıcılık oranlarını Fed anketinden aldık. Personaları LLM'e uydurtmadık: dört davranış eksenini deney tasarımıyla tam kapsadık, sonra her personayı nüfustaki payıyla ağırlıklandırdık. LLM yalnızca bu sabit özelliklerden hikâye yazdı."

## 9. Roller ve saat planı
| Saat | Tolga | Emin | Gürkan | Claude |
|---|---|---|---|---|
| →12:15 | `llm.py`, `engine.py` (iki tur), `run.py` mock, `package.py`, check.py yeşil | `personas.py` alan kuralları (3.2), `w_active` | `config.py` / `budget_check`, BAU metinleri, `crisis.py` | `agent.py` prompt'ları, `network.py`, `interact.py` |
| 12:15–13:00 | `--live` lite, süre ölçümü | 75 hikâye (3.7) + kalite kapısı + spot okuma, dondur | K1 adayları, mesaj taslakları | Persona testleri (3.6), E0 |
| 13:00–14:50 | Deney koşucusu, `ask_persona.py` | S/R, entropi, DOE ana etkileri | Duyuru prosedürü, E1–E4 | E5–E12, E10 (14:15), kaskad analizi |
| **14:55** | | | **K1 + K2 yer tutucusunu kilitle** | |
| 15:00–16:25 | Final hat (3.7) | Sonuç tabloları | **K2 son hali** (E12 + sürprizler) | Ana grafik + ağ görseli, TEAM_DOC |
| 16:00 | **FEATURE FREEZE** | | | |
| 16:00–17:30 | Artımlı final koşular | Memo sayıları | CLIENT_MEMO, slaytlar, prova | Doküman revizyonu |
| 17:30–17:55 | Yeniden koşu, zip, upload | check.py | Prova | |
| 18:00 | Demo kaydı + yedek | | | |

---

## Doğrulama (uçtan uca)
1. **Mock:** 5 koşu tipi → `python3 talp-hackathon-participants/yeni-case-5-sirket/check.py submission/` → **"Nothing to fix."** Kapsadığı kontroller: persona-haftalar, tur B call izlenebilirliği, mesajın kelimesi kelimesine ulaşması ve erken sızıntı yok, nodecision'da mesaj yok, seed farkı, surprises prompt farkı, 5 koşuda aynı personas.
2. **Persona kapısı:** 75/75 tutarlılık kontrolünden geçmiş; hassas kelime taraması temiz; hafta 0 probe'da S > 0 ve grup içi entropi raporlanmış.
3. **Etkileşim:** mock'ta gönderilen her DM alıcının tur B prompt'unda görünür; ağ kapalı koşuda hiçbir prompt'ta başka personanın metni yok.
4. Lite canlı tam koşu < 2 dk; `sanity_check` temiz ya da açıklanmış. Aynı seed ve kararla ikinci koşu tamamen cache'ten gelir.
5. **Unit testler** (`code_kit/tests/` kalıbı):
   - `budget_check` menü dışı/bütçe aşımını reddeder
   - `classify` migration metnini A01'e eşler
   - `metrics` bilinen sonucu verir
   - Prompt'larda `calibration_anchors` metni yoktur
   - Ağırlık toplamları population_priors'a uyar (2.1M / 1.0M / $6.0B)
6. Teslim öncesi `package.py`: `AQ.` anahtar taraması + zip üzerinde `check.py`.
7. **Parametre ve kayıt:**
   - Aynı komutu iki kez çalıştırmak iki ayrı zaman damgalı klasör üretir, ilk koşunun dosyaları değişmez (dosya hash'leriyle test edilir).
   - `--set` ile bir parametre değiştirildiğinde `params.resolved.json` ve `index.csv` farkı gösterir.
   - Bilinmeyen anahtar (`--set netwrk.feed_size=3`) hata verir.
   - `runs diff` iki koşunun metrik ve parametre farkını basar.
