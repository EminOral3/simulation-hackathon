# Cobalt metrikleri v2 — dört board hedefi korunur

## Kapsam ve sürüm

Kaynak: 5772aaf üzerine uygulanan yerel revizyon. Yeni LLM/API çağrısı, persona üretimi veya simülasyon çalıştırılmadı. G1 ≥98%, G2 ≥97%, G3 puan ≥4.3 ve CFPB ≤240/ay, G4 bütçe ≤4M değişmedi.

Mevcut metrics.json v1 olarak korunur. Tamamlanmış yeni koşular ayrıca metrics_v2.json üretir. Bu sürüm puan hedeflerinin yerine başka hedefler koymaz.

## Ölçümler

### G1
Son dört haftada en az bir main bank/second bank statüsü görülmesi, **28 günlük ilişki-statüsü vekili** olarak kullanılır. Bu, gerçek 30 günlük uygulama kullanımı değildir. Başlangıç aktif kohortu temsil edilir; pasiflerin yeniden aktifleşmesi yoktur.

Varsayılan exclude_closed=false: son gün hesabını kapatmak geçmişteki aktif statüyü silmez. Aynı kayıtlardan exclude_closed=true ile hesaplanan relationship_preserving_28d_pct de raporlanır; bu ek ilişkiyi sürdürme koşuludur.

exit_conversion=0.69 varsayımı korunur ve 1.0 ile duyarlılık tablosu ayrıca verilir. İkisi de veriyle doğrulanmış dönüşüm değildir.

### G2
Mevcut kümülatif maksimum taşınma düzeyi hesabı korunur. Art arda “moved most” demek yeni hareket olarak tekrar toplanmaz. some/most/left oranları ve sabit pasif mevduat varsayımı görünür kalır. Prompt değişmediği için stok/haftalık hareket belirsizliği tamamen çözülmüş sayılmaz.

### G3
Puan ve CFPB vekili ile giriş düzeltmesinde temiz takvim referansı 1–2. haftalardır; 3. haftadaki kriz referansa katılmaz. Bütün değerlendirilen koşullarda aynı dönem tanımı kullanılır; bunlar her koşunun kendi taban oranlarıdır, haricen kalibre edilmiş ortak BAU oranı değildir.

App Store k modeli korunur; başlangıç yorum sayısı bilinmediği için yeni N0 varsayımı eklenmez.

CFPB sayısal vekili teslim alanıyla uyum için korunur. Ancak raw_events, base_raw_events, measurable ve reason alanları ayrıca gelir. Kalibrasyon doğrulanmadıkça veya olaylar seyrekken goal_3b met değeri null olur. Sayısal değerin 240 altında olması tek başına kanıtlanmış başarı değildir.

raw_events, cfpb=true yazılan persona-hafta sayısıdır; benzersiz başvuru kimliği bulunmadığından aynı başvurunun farklı haftalarda tekrar anlatılması ayırt edilemez. Gerçek benzersiz başvuru sayısı diye sunulmamalıdır.

cfpb_min_events=20 ve cfpb_min_base_events=5 yalnız operasyonel tarama eşikleridir; istatistiksel yeterlilik kanıtı değildir. cfpb_calibration_validated varsayılan false'tur.

### G4
CFO maliyetleri, kalan bütçe, kullanım oranı ve menü uygunluğu raporlanır. final_decision_count_valid ayrıca tam iki kararı kontrol eder. Kontrol koşusunda sıfır karar olması geçerli bir deneydir; final planın yerine geçmez.

## Geçerlilik ve belirsizlik

Eksik/tekrarlı persona-hafta, bozuk alan, parsed=false veya başarısız yanıt varsa koşu geçersizdir; varsayılan main bank/kept ile başarı üretilmez.

all_targets_met üç değer taşır:
- false: bilinen en az bir hedef veya bütçe başarısız;
- null: bilinen başarısızlık yok ama en az bir hedef ölçülemiyor;
- true: bütün hedefler model içinde değerlendirilebilir ve sağlanmış.

Bootstrap açıklaması düzeltildi: tüm panelden yeniden örnekleme + grup ağırlıklarını yeniden ölçekleme. Klasik tabakalı bootstrap değildir; ağ bağımlılığını hesaba katmaz; gerçek müşterilere ilişkin doğrulanmış %95 kapsama iddiası yoktur.

G1'in aralığı yeni vekil tanımıyla yeniden hesaplanır; eski G1 aralığı yeni tanımın altına kopyalanmaz. Grup sonuçları betimleyicidir; nedensel etki veya adalet garantisi değildir.

## Eski kayıtları yeniden hesaplamak (yalnız dosya okuma/hesaplama)

Repo kökünde, yeni API çağrısı olmadan:

```powershell
python -m code_kit.cobalt.recompute_metrics <kayitli-kosu-klasoru-veya-kosularin-ust-klasoru> --out <yeni-rapor-klasoru>
```

- Her kayda ayrı metrics_v2.json yazılır; v1, weekly, calls ve persona dosyaları değiştirilmez.
- V2 zaten varsa varsayılan işlem reddeder. --force yalnız v2 dosyasını yeniler.
- --bootstrap yalnız yerel yeniden örnekleme yapar; LLM çağırmaz.
- summary.csv: eski/yeni değerler, seed, hedef durumları ve bütçe.
- paired_deltas.csv: aynı seed/model/kod/persona/duyuru/dünya/ağ/destek/metrik ayarları eşleşen plan–kontrol farkları.
- groups.csv: grup sonuçları.
- exit_sensitivity.csv: 0.69 / 1.0 dönüşüm duyarlılığı.
- errors.json: okunamayan veya üzerine yazılmayan kayıtlar.
- Tarihsel prompt sürümü kayıtlı değilse unknown bırakılır; mevcut prompt hash'i eski koşuya aitmiş gibi yazılmaz.

Sıralamanın aynı kalması hedef değildir. Çıkan farklar ve başarısızlıklar raporlanır.

## Yeni koşu ve rapor entegrasyonu

Bu görevde yeni koşu çalıştırılmadı. İleride açıkça koşu istenirse:
- run modülü v1 ve v2 dosyalarını birlikte üretir; prompt dosyasının hash'i kaydedilir.
- experiments varsayılan olarak v2 sonuçlarını okur; eski davranış için --metrics-version v1 seçilebilir.
- Eski outputs/index.csv v1 geçmişini korur. V2 karşılaştırması için yeni deney summary.csv veya recompute raporu kullanılmalıdır.
- report modülünde --metrics-version v2 seçilir; eksik v2 dosyasında v1'e sessiz düşmez ve farklı metrik sürümlerini karıştırmaz.
- Sayısal CFPB grafiği ölçülebilirlik kanıtı değildir; v2 raporunda bu açıkça etiketlenir.
- planner ve fastsim/surrogate bu görevde yeniden eğitilmedi/değiştirilmedi. Onların skorları v1 varsayımlarıyla kalır; v2 değerlendirme olarak sunulmamalı.

## Teslim paketi ve doğru plan

Repodaki eski plan.json 2.1M planı içerir; otomatik değiştirilmedi. Mevcut önerilen kilit referansı w4t/w4t_T25_lock (3.6M) olarak metrics_v2.canonical_decisions içinde tanımlı.

package modülü varsayılan v2 kullanır ve kaynak koşuların kararları/filtrelerini bu referansla karşılaştırır. Fark varsa paketlemeyi reddeder. Gerçek dashboard kilidi değişirse --locked-decisions <gercek-kilit-dosyasi> veya canonical_decisions ayarı güncellenmelidir. Kod dashboard'a bağlanmaz; sağlanan dosyayla tutarlılığı doğrular.

Yeni pakette metrics.json v2 olur, metrics_v1.json eski sonucu taşır; kaynak koşu klasörleri değişmez. Geçersiz kayıt/bütçe paketlenmez. CFPB belirsizliği uyarı ve metrik alanlarıyla taşınır; yok sayılıp başarı ilan edilmez.

## Kontroller

```powershell
python -m unittest code_kit.cobalt.tests.test_metrics_v2 code_kit.cobalt.tests.test_manual40 -v
```

Testler elle tanımlanmış kayıt tablolarını ve dosyaları kullanır. Simülasyon motoru veya API çalıştırmaz. Varsayılan 75 kişi ve ayrı manual40 paneli korunur.
