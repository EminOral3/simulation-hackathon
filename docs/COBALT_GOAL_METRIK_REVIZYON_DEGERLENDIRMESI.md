# Cobalt Bank — Hedefler, metrik revizyonları ve değerlendirme önerisi

**Tarih:** 24 Ekim 2026
**İncelenen GitHub sürümü:** `80ceb28 — initial implementation and inital run results`
**Depo:** https://github.com/SuleymanTolgaAcar/simulation-hackathon
**Belgenin amacı:** Ana geliştirmeyi yapan LLM ve ekip için teknik tartışma ve karar desteği. Bu belge uygulama talimatı veya otomatik değişiklik onayı değildir. Öneriler önce mevcut uygulama ve zaman bütçesi açısından değerlendirilmelidir.

## 1. Ana sonuç: hedefler korunmalı, ölçüm yöntemleri geliştirilebilir

Organizasyon Cobalt Bank için dört yönetim kurulu hedefi belirlemiş. Bizim görevimiz bu hedefleri başka hedeflerle değiştirmek değil, persona davranışlarından ilgili sonuçları hesaplamak ve iki kararımızın etkisini açıklamak.

**Önemli dil düzeltmesi:** Görev metninde birebir “hedefleri değiştiremezsiniz” cümlesi bulunmuyor. Hedeflerin açıkça verilmesi ve teslimde her biri için sonuç istenmesi, bunları korunması gereken gereksinimler olarak yorumlamamızın dayanağıdır. Bu yorum, doğrudan alıntı gibi sunulmamalıdır.

### Kaynaklar

1. [Cobalt dossier, satır 32–39](https://github.com/SuleymanTolgaAcar/simulation-hackathon/blob/80ceb28/talp-hackathon-participants/yeni-case-5-sirket/10-cobalt-bank.md#L32-L39): “What the board wants by January 10” başlığı altında hedef ve eşikler.
2. [Challenge, satır 64](https://github.com/SuleymanTolgaAcar/simulation-hackathon/blob/80ceb28/talp-hackathon-participants/yeni-case-5-sirket/02-challenge.md#L64): Persona davranışını yönetim kurulu hedeflerine nasıl dönüştürdüğümüzü ve her personanın kaç müşteriyi temsil ettiğini tanımlamamız isteniyor.
3. [Challenge, satır 154](https://github.com/SuleymanTolgaAcar/simulation-hackathon/blob/80ceb28/talp-hackathon-participants/yeni-case-5-sirket/02-challenge.md#L154): Bütçe hariç her yönetim kurulu hedefi için metrics.json içinde sayısal sonuç isteniyor; iki parçalı hedefe goal_3b eklenebiliyor.

| Yönetim kurulu hedefi | Korunacak eşik | Mevcut sonuç alanı |
|---|---|---|
| G1: Son 30 gündeki aktif müşteriler | 2 Kasım seviyesinin en az %98'i: 980.000 | goal_1 |
| G2: Mevduat | 6 milyar doların en az %97'si: 5,82 milyar dolar | goal_2 |
| G3a: App Store puanı | En az 4,3 | goal_3 |
| G3b: CFPB şikâyetleri | Olağan 120/ayın en fazla iki katı: 240/ay | goal_3b |
| G4: İki kararın maliyeti | En fazla 4 milyon dolar | Ayrı bütçe kontrolü |

Dört yönetim kurulu hedefi vardır; üçüncü hedef iki ölçüme ayrılır. Dört goal alanı, bütçe dahil dört hedefle birebir aynı liste değildir.

**Serbestlik alanı:** Formüller, gözlenen davranış alanları, temsil ağırlıkları, açıklanan varsayımlar, duyarlılık deneyleri ve yardımcı metrikler geliştirilebilir. Ancak hedefin anlamı korunmalıdır. Örneğin son 30 günlük kullanımın yerine son haftadaki banka statüsünü koymak ancak açıkça belirtilmiş bir vekil ölçüm olabilir.

## 2. Mevcut uygulamanın kaynakları ve sınırlar

İncelenen dosyalar:

- [metrics.py](https://github.com/SuleymanTolgaAcar/simulation-hackathon/blob/80ceb28/code_kit/cobalt/metrics.py)
- [engine.py](https://github.com/SuleymanTolgaAcar/simulation-hackathon/blob/80ceb28/code_kit/cobalt/engine.py)
- [agent.py](https://github.com/SuleymanTolgaAcar/simulation-hackathon/blob/80ceb28/code_kit/cobalt/agent.py)
- [default.toml](https://github.com/SuleymanTolgaAcar/simulation-hackathon/blob/80ceb28/code_kit/cobalt/params/default.toml)
- [config.py](https://github.com/SuleymanTolgaAcar/simulation-hackathon/blob/80ceb28/code_kit/cobalt/config.py)
- [metric_spec.json](https://github.com/SuleymanTolgaAcar/simulation-hackathon/blob/80ceb28/docs/talp_db/data/theory/metric_spec.json)
- [DEVAM_NOTU.md](https://github.com/SuleymanTolgaAcar/simulation-hackathon/blob/80ceb28/code_kit/cobalt/DEVAM_NOTU.md)

Kod, taslak metric_spec.json'dan bazı noktalarda ilerlemiş/farklılaşmış. Örneğin kod w_active kullanıyor; taslakta eşit grup ağırlığı ifadesi hâlâ bulunuyor. Uygulanan formülün kaynağı ve sürümü tekleştirilmeli.

Bu belge kodun okunmasına dayanır. Yeni canlı simülasyon, doğruluk deneyi veya değişiklik sonrası test çalıştırılmamıştır. Gerçek müşteri mikroverisi ve gerçek sonucun bulunduğu bir doğrulama seti incelenmemiştir. Aşağıdaki revizyonlar ölçüm tutarlılığını artırabilir; tek başına gerçek dünya tahmin doğruluğu sağlamaz.

## 3. G1 — Son 30 günlük aktif müşteri

### Mevcut hesap

Kod, 10. haftada status alanı main bank veya second bank olan personaların w_active ağırlıklarını topluyor ve toplam başlangıç aktif ağırlığına bölüyor:

`G1_current = 100 × Σ(w_active × I(status_week10 ∈ {main bank, second bank})) / Σw_active`

### Sorun

- Bankayla ilişki durumu, uygulama kullanımının doğrudan kaydı değildir.
- Son haftada dormant olan bir kişi önceki üç haftada uygulamayı kullanmış olabilir.
- Dün bankayı bırakan kişinin son 30 günlük kullanım geçmişi hemen sıfırlanmaz.
- Mevcut panel aktif müşteri alt nüfusunu temsil ediyor; başlangıçta pasif olanların yeniden aktifleşmesi açık biçimde modellenmiyor.
- Başlangıç aktif ağırlıklarının dossier'deki 1 milyonla tam uzlaşması ayrıca kontrol edilmeli. Oran almak her temsil hatasını ortadan kaldırmaz.

### Önerilen ölçüm

`G1_v2 = 100 × A_30d(T) / 1.000.000`

Burada A_30d(T), dönem sonu T itibarıyla son 30 gün içinde en az bir uygulama kullanımı olan temsil edilen müşteri sayısıdır. Eşik %98 olarak kalır.

### Gerekli veri ve uygulama

- RoundB çıktısına used_app_this_week ve kullanıldıysa last_app_use_date veya hafta içindeki gün eklenir.
- Motor en son kullanım tarihini saklar.
- Her persona aynı 30 günlük pencerede en fazla bir kez sayılır.
- Statü ve kullanım ayrı alanlar olur; left durumu geçmiş kullanım tarihini silmez.
- Haftalık LLM yalnız gözlemlediği haftanın kullanımını üretir; kod bu kaydı tarihe ve pencereye dönüştürür. LLM davranışının yerine kodla hedefe uygun kullanım uydurulmaz.
- Başlangıçta aktif/pasif kohort kapsamı açıklanır. Pasiflerin yeniden aktifleşmesi dışarıda bırakılıyorsa sonuç başlangıç aktif kohortunun korunması olarak etiketlenir; tam nüfus G1'i olduğu iddia edilmez.
- Gün düzeyinde çıktı eklemek fazla maliyetliyse dört haftalık kullanım ölçümü kullanılabilir, ancak 28 günün 30 gün olduğu söylenmemelidir.

### Bugün için düşük maliyetli alternatif

Mevcut G1'i geçici vekil olarak koruyup “banka ilişkisini sürdüren başlangıç aktif müşterilerin oranı” şeklinde açıkça tanımlamak. Bu, tam görev ölçümüne eşdeğer değildir; önemliyse organizatöre yorum doğrulatılmalı.

### Kontrol örnekleri

- Son haftada kullanmayan ama 20 gün önce kullanan müşteri aktif sayılır.
- Son kullanımı 31 gün önce olan müşteri sayılmaz.
- Bir kişinin birden fazla kullanım kaydı müşteri sayısını artırmaz.
- Yeni kohort eklenmiyorsa başlangıç ve son ağırlık tabanı tutarlıdır.

**Eski sonuçlardan hesaplanabilirlik:** Mevcut weekly.jsonl kesin kullanım tarihi içermiyor. Yeni G1 için yeni simülasyon çıktısı gerekir; yalnız status'tan kesin kullanım geçmişi çıkarılamaz.

## 4. G2 — Mevduatın korunması

### Mevcut hesap

- Bakiye bandı temsil değerleri w_active ile çarpılıp grup mevduatına ölçekleniyor.
- Aktif olmayan kesimin mevduatı sabit tutuluyor.
- kept=0, moved some=0,30, moved most=0,80 ve left için en az 0,95 çıkış kabul ediliyor.
- Çıkış haftalar boyunca kümülatif maksimum ile tutuluyor.
- Para girişleri none=0, some=0,10, a lot=0,30 oranlarına çevriliyor. Koşunun kendi ilk üç haftasındaki ortalama giriş çıkarılıp kalan giriş biriktiriliyor.

### Sorun

Prompt “bu haftaki hareketi” isterken çıkış hesabı “başlangıçtan beri ulaşılan en yüksek taşınma düzeyi” gibi davranıyor. İki ayrı haftadaki yeni çıkış ikinci kez sayılmayabilir; girişler ise birikiyor.

Ek olarak:
- Girişin kendi koşusunun ilk haftalarına göre düzeltilmesi, erken kararların etkisini referansa karıştırabilir.
- Pasif mevduatın sabitliği sonucu mekanik olarak daha dayanıklı gösterebilir.
- Bakiye bandını sayıya ve hareketi yüzdeye dönüştüren değerler gerçek veri değil varsayımdır.
- engine.py out_level ile metrics.py left işlemi aynı durum hesabını tam paylaşmıyor; motorun müşteriye anlattığı bakiye ile raporlanan bakiye uyumlu olmalı.

### Önerilen ölçüm

`B_i,t = B_i,t−1 + inflow_i,t − outflow_i,t`

`G2_v2 = 100 × Σ(weight_i × B_i,T) / 6.000.000.000`

Pasif mevduat ayrı sabit stok olarak bırakılıyorsa toplamda açıkça yer almalı ve alternatif tepki senaryosu gösterilmelidir.

### Gerekli veri ve uygulama

- new_inflow ve new_outflow yalnız bu haftanın yeni hareketlerini belirtir.
- Tarihçe içinde eski hareketten söz etmek yeni işlem sayılmaz.
- Kod deterministik bakiye defteri tutar; LLM eylemi ve tutarı/kategoriyi üretir.
- Çıkış mevcut kullanılabilir bakiyeyi aşamaz.
- kept, önceki çıkışı geri almaz.
- Bankayı terk etme, geçmiş yeni para girişleri dahil mevcut bakiye üzerinden ele alınır.
- Günlük olağan gelir/giderleri simüle etmiyorsak bu açıkça “kriz ve karar kaynaklı net hareket modeli” olarak tanımlanır.
- Başlangıç ağırlıklı mevduat 6 milyar dolara, büyük bakiyeli grubun payı yaklaşık yarıya uzlaştırılır.
- Temsil ağırlığı, kişinin gerçek bireysel bakiyesi ve ölçeklenmiş toplam mevduat katkısı birbirine karıştırılmaz.

### İki uygulanabilir seçenek

**A — İşlem yaklaşımı:** Haftalık yeni giriş/çıkış tutarı veya mevcut bakiyenin oranı. Daha açıklanabilir; yeni alanlar ve bakiye geri bildirimi gerekir.

**B — Stok yaklaşımı:** LLM her hafta “başlangıç bakiyenin şu anda ne kadarı Cobalt'ta?” biçiminde kümülatif kalan stok bildirir. Haftalık hareketmiş gibi toplanmaz. Daha basit olabilir; başlangıç üstü yeni para girişi de aynı tanım içinde tutarlı ele alınmalıdır.

İki yaklaşım karıştırılmamalı. Hackathon süresinde ekip hangisini daha az değişiklikle tutarlı kurabiliyorsa onu seçmeli.

### Duyarlılık ve kontroller

- some/most oranları için makul düşük/orta/yüksek varsayımlar önceden belirlenir.
- Sıfır hareket bakiyeyi korur.
- Giriş/çıkış toplama hesabı bilanço farkıyla uzlaşır.
- Aynı işlem tekrar sayılmaz; yeni işlem de kaybolmaz.
- Hiçbir varsayım sırf hedefi geçmek için seçilmez.

**Eski sonuçlardan hesaplanabilirlik:** Eski kategorilerle alternatif varsayımlar yeniden hesaplanabilir. Ancak prompt ile hareket anlamı uyuşmadığında gerçek revizyon için yeni koşu gerekir. Aynı eski çıktıya yeni anlam atamak tarafsız bir düzeltme sayılmaz.

## 5. G3a — App Store puanı

### Mevcut hesap

`rating = 4,6 − k × (5–10. haftalardaki ortalama olumsuz yorum oranı − başlangıç olumsuz yorum oranı)`

k=2 varsayım; olumsuz yorum 1–2 yıldızdır. Başlangıç her koşunun kendi 1–3. haftasından türetilir ve küçük bir taban uygulanır.

### Sorun

- 3–5 yıldızlı yorumlar doğrudan puan hesabına katılmıyor.
- Başlangıç yorum sayısı ve puan birikimi bilinmiyor.
- Aynı kişinin yorum güncellemesi ile yeni yorum ayrılmıyor.
- Puan çıktısı gerçek App Store puanlama mekanizmasının doğrulanmış modeli değil.
- Erken karar/kriz referans dönemine karışabilir.

### Önerilen ölçüm

Basitleştirilmiş yorum birikimi modeli:

`rating_v2 = (4,6 × N0 + Σ yeni_yorum_yıldızları) / (N0 + yeni_yorum_sayısı)`

Bu, gerçek mağaza algoritmasının birebir yeniden üretimi olarak sunulmamalıdır; açıklanabilir bir vekil modeldir.

### Eksik bilgi ve nasıl yönetileceği

N0, başlangıç yorum sayısı, dossier'de yok. Uydurulmuş tek bir değeri gerçek kabul etmemeliyiz.

- N0 için açıkça varsayım olarak tanımlanan senaryolar kullanılır.
- Sonucun 4,3 eşiğini geçmesinin bu varsayıma bağlı olup olmadığı gösterilir.
- Ana senaryo önceden belirlenir; goal_3 bu senaryonun sonucudur.
- “Başlangıç yorum birikimi / yeni yorum hacmi” oranıyla parametrizasyon, bilinmeyen mutlak sayı üretmekten daha anlaşılır olabilir.
- Persona müşteri ağırlığı doğrudan yorum sayısı değildir. Uygulama platformu ve yorum verme kapsamı açıklanmalıdır.
- Mevcut yorumunu değiştiren persona yeni yorum eklemiş gibi sayılmaz. Eski yıldız bilgisi yoksa bu kısıt açıklanır.

### Yardımcı doğrudan göstergeler

- Yeni yorumların 1–5 arası ortalama yıldızı.
- Yeni yorumlar içinde 1–2 yıldız payı.
- Yorum veren temsil edilen müşteri oranı.

Bunlar goal_3'ün yerine geçmez; puanın nasıl oluştuğunu açıklar.

### Bugün için düşük maliyetli alternatif

Mevcut k modelini koruyup “puan vekili” diye etiketlemek ve k duyarlılığını sunmak. Veri yokken daha karmaşık modelin otomatik olarak daha doğru olmadığı unutulmamalı.

**Eski sonuçlardan hesaplanabilirlik:** review_stars mevcut. Tam weekly kayıtlarıyla yıldız dağılımları çıkarılabilir. Yorum güncelleme kimliği veya platform bilgisi bulunmadığından tam stok modeli için ek varsayım/veri gerekir.

## 6. G3b — CFPB şikâyetleri

### Mevcut hesap

Haftalık ağırlıklı CFPB olay oranları yaklaşık dört haftalık pencerelerde ortalanıyor. Koşunun kendi ilk üç haftası baz alınıyor. Smoothing ile:

`120 × (pencere_oranı + epsilon) / (koşunun_baz_oranı + epsilon)`

En yüksek pencere goal_3b oluyor. Hiç olay yokken de sonuç 120 olabiliyor.

### Sorun

- Her koşu kendi referansını üretince karşılaştırma ölçeği değişiyor.
- Baz döneme karar/kriz girerse etki kısmen normalize edilerek silinebilir.
- Hiç CFPB olayı üretmeyen model ile gerçekten olağan şikâyet düzeyini üreten model aynı sayıyı verebilir.
- Dört hafta 28 gündür; 30 gün etiketi kesin değildir.
- Aynı şikâyeti tekrar anlatmakla yeni başvuru yapmak ayrılmalı.
- Son deneylerdeki sabit 120 değeri tek başına başarı kanıtı değildir.

### Önerilen iki katman

**Ham çıktı:** Ağırlıklı yeni CFPB olay oranı ve ham olay sayısı.

**Kurul ölçümü:** Bütün koşular için ortak, önceden dondurulmuş BAU referansıyla dönüşüm:

`C_30d = 120 × (koşunun_30g_şikâyet_oranı / ortak_BAU_30g_şikâyet_oranı)`

Bu dönüşüm de doğrulanmış gerçek müşteri kalibrasyonu değildir; dossier'deki 120'ye dayanan modelleme varsayımıdır.

### Uygulama koşulları

- BAU referansı kararlar ve krizler uygulanmadan hazırlanır; plan ve nodecision için aynıdır.
- Örnek büyüklüğü, exposure tabanı ve pencere uzunluğu aynı tanımlanır.
- Olay tarihi ve mümkünse şikâyet kimliğiyle tekrar kayıt engellenir.
- Gün 30 penceresi tutulamıyorsa 28 günlük yaklaşık pencere açıkça belirtilir.
- Bitişteki pencere ve dönem içindeki en kötü pencere ayrı raporlanır. Goal için kullanılan yorum belirtilir; en kötü pencere temkinli yaklaşımımızdır.

### Seyrek olay problemi

75 persona nadir resmî şikâyet davranışını ölçmek için yetersiz kalabilir. BAU'da sıfır olay varsa oranla sayıya dönüşüm tanımsız/güvenilmezdir.

- Sıfır paydayı küçük sayıyla gizleyip sonucu kesin tahmin gibi sunmayın.
- “Kalibrasyon için yetersiz olay” durumunu ayrıca işaretleyin.
- Gerekirse ek BAU tekrarları veya açık prior/smoothing senaryoları kullanın.
- Teslim şemasının sonlu sayı istemesi bilimsel geçerlilik garantisi değildir. Zorunlu sayısal çıktı varsayımsal senaryo olarak verilirse güvenilirlik bayrağı ve açıklaması yanında bulunmalıdır; güvenilir hedef başarısı diye sunulmamalıdır.

**Eski sonuçlardan hesaplanabilirlik:** cfpb alanı mevcut. Tam kayıtlar ve ortak referansla yeniden hesaplama yapılabilir. Olay tarihleri/kimlikleri ve sıfır-olay sorunu için ek veri gerekebilir.

## 7. G4 — Bütçe ve karar uygulanabilirliği

Mevcut temel yaklaşım korunmalı:

`maliyet = iki karardaki aksiyonların CFO menü maliyetleri + ücretli mesajlar`

Sınır 4 milyon dolardır. Yeni bir tahmin modeli gerekmiyor.

Ek rapor alanları:
- total_cost_usd
- remaining_budget_usd
- budget_utilization_pct
- decision_count
- feasible: menü, seviye, hedef grup kapasitesi, zaman ve kırmızı çizgi uygunluğu

Güncel plan dosyasındaki maliyet 1,3M + 0,8M = 2,1M dolardır; kalan bütçe 1,9M dolardır. Bu, dashboard'da kilitlendiğinin doğrulaması değildir.

config.py deneyler için ikiye kadar karara izin veriyor; final teslim tam iki karar gerektiriyor. Yazılı hedef ile filters alanının gerçek uygulaması da örtüşmeli. Bütçe kontrolü tek başına tüm kırmızı çizgileri veya dashboard kilitleme zamanını doğrulamaz.

Ücretli mesaj tekrarlarının sayısı varsa ücret her gönderim için hesaba katılmalıdır. Bütçe aşımı iyi G1/G2 ile dengelenebilecek bir ceza puanı değil, katı kısıttır.

## 8. Önerilen yardımcı metrikler

### 8.1 Eşleştirilmiş plan faydası

Aynı persona seti, dış kriz senaryosu ve karşılaştırılabilir seed ile:

- Δaktif = G1_plan − G1_nodecision (yüzde puan)
- Δmevduat = G2_plan − G2_nodecision (yüzde puan; ayrıca dolar)
- Δpuan = G3_plan − G3_nodecision
- Önlenen şikâyet = G3b_nodecision − G3b_plan
- Ek maliyet = cost_plan − cost_nodecision

Aynı API seed'inin farklı prompt'larda birebir eşlenmiş LLM rastgeleliği sağlayacağı varsayılmamalı. Dış dünya şoklarını kod düzeyinde eşleştirmek ayrı bir kontroldür.

Farklar gerçek dünyada nedensellik kanıtı değil, model içindeki karşılaştırmalı etkidir. Sadece bütün koşulların ortalamalarını çıkarmak yerine seed/senaryo bazında farklar raporlansın.

### 8.2 Hedeflerin birlikte sağlanması

`joint_pass = G1≥98 AND G2≥97 AND G3≥4,3 AND G3b≤240 AND budget≤4M`

Deneme bazında geçti/kaldı ve örnek sayısı raporlanır. İki denemeden birinin geçmesi “gerçek başarı olasılığı %50” değildir; yalnız “2 denemenin 1'i geçti”dir.

Geçersiz veya ölçülemeyen goal, otomatik başarılı sayılmaz. Ortak başarı hesabında unknown/invalid durumu görünür olmalıdır.

### 8.3 Grup bazında sonuçlar

Maaş müşterileri, yüksek bakiyeliler, öğrenciler, gündelik müşteriler ve küçük işletmeler için:
- aktiflik/ilişki kaybı;
- kendi başlangıç mevduatına göre koruma;
- toplam mevduat kaybına katkı;
- şikâyet ve destek ihtiyacı.

“En kötü grup” yalnız toplam dolar kaybına göre seçilmesin; grup içi oranla bankaya toplam katkı ayrı gösterilsin. Küçük persona sayılarındaki gürültü açıkça belirtilsin.

### 8.4 İsteğe bağlı: maliyet başına model içi fayda

`maliyet / nodecision'a göre korunan ek aktif müşteri` gibi ölçüler kullanılabilir. Payda sıfır/negatifse anlamsız oran üretmek yerine durumu belirtin.

**Mevduat kazancı banka kârı değildir.** “Korunan mevduat / müdahale maliyeti” ROI veya kârlılık diye adlandırılmamalı. Kâr için net faiz marjı ve başka maliyet verileri gerekir.

## 9. Öncelikli ölçüm güvenilirliği kontrolleri

### 9.1 Eksik yanıt başarıya dönüşmemeli

engine.py bazı ayrıştırma hatalarında önceki status ve kept kullanabiliyor. metrics.py dizileri varsayılan main bank/kept değerleriyle başlatıyor.

Öneri:
- Beklenen persona×hafta sayısı ve parsed=false sayısı kontrol edilsin.
- Eksik/bozuk veri unknown/invalid olarak işaretlensin.
- Final geçerlilik kontrolü başarısızsa “bütün hedefler sağlandı” mesajı verilmesin.
- Gösterim için carry-forward kullanılırsa tahmini doldurma olduğu ayrı bayrakla görünür olsun.
- Başarısız yanıtların etkisini hesaplamadan ortalamadan çıkarmak da yanlılık yaratabilir.

### 9.2 Bootstrap iddiası

Kod bootstrap örneklerini önce tüm panelden çekiyor, sonra grup ağırlıklarını yeniden ölçekliyor. Bu, her gruptan sabit sayıda çekilen klasik stratified bootstrap ile tam aynı uygulama değildir; etiket ve yöntem uyumu gözden geçirilmeli.

Sosyal ağdaki personalar bağımsız değildir. Persona bootstrap aralığı, gerçek müşteri nüfusunun doğrulanmış %95 güven aralığı olarak sunulmamalıdır. Daha çok seed, alternatif ağ/dünya varsayımları ve parametre duyarlılığı ayrı belirsizlik kaynaklarıdır.

### 9.3 Model ve metrik sürümü

DEVAM_NOTU, ilk deneylerden sonra metrik/prompt değiştiğini belirtiyor. Eski E1 ile yeni deney tabloları doğrudan tek karşılaştırma tablosuna konmamalı.

Her koşuda:
- kod commit'i;
- metrik sürümü;
- prompt/schema sürümü;
- persona seti;
- model;
- seed;
- kriz/karar/config özeti veya hash'i bulunmalı.

Karşılaştırılan koşul çiftlerinde bunlar, deneyde kasıtlı değiştirilen faktör dışında aynı olmalı.

## 10. Hackathon için uygulanabilir öncelik

| Öncelik | İş | Neden |
|---|---|---|
| P0 | Eksik çıktının başarılı sonuç sayılmasını engelle | Güvenilirlik için temel |
| P0 | Hedef/eşik/alan adlarını koru, metrik sürümünü kaydet | Teslim ve karşılaştırılabilirlik |
| P1 | G2 haftalık hareket ile kümülatif stok anlamını tekleştir | Sonuçları doğrudan etkileyen yapısal tutarsızlık |
| P1 | G3/G3b için ortak referans ve CFPB olay kontrolü | Sahte iyileşme/sabit sonuç riskini azalt |
| P1 | Eşleştirilmiş plan faydası ve her seed'de ortak başarı | Kararın değerini anlaşılır göster |
| P2 | G1 için kullanım geçmişi | Görev tanımına daha doğrudan uyum |
| P2 | Grup bazında raporlama ve oran duyarlılığı | Varsayım ve zarar dağılımını görünür kıl |
| P3 | App Store yorum birikimi modeli | Veri yoksa ek karmaşıklığın faydası sınırlı olabilir |

Bu sıra öneridir; kalan süre ve mevcut runtime'a göre ekip değiştirebilir. Yeni alan gerektiren revizyonların bütün koşuların yeniden çalıştırılmasına yol açabileceği hesaplanmalı. Tüm önerileri tek seferde uygulamak zorunlu değildir.

## 11. Ana geliştirmeyi yapan LLM'den istenen değerlendirme

Lütfen önce güncel commit'i ve mevcut implementasyonu kontrol et. Bu belge eski bir sürümü tarif ediyor olabilir. **Bu belgeyi doğrudan kod değişikliği emri sayma; önce eleştirel değerlendirme ve uygulama planı ver.**

Şu soruları cevapla:

1. Dört board goal ve teslim alanları hakkındaki yorum doğru mu? Kurallarla çelişen öneri var mı?
2. Kod hakkındaki hangi tespitler güncel sürümde hâlâ geçerli, hangileri düzeltildi?
3. G1: kullanım geçmişini eklemek için minimum değişiklik nedir? Pasif müşteri kapsamını nasıl açıklayacağız?
4. G2: işlem yaklaşımı mı stok yaklaşımı mı mevcut mimariye daha uygun? Motor ve metrik nasıl aynı durum defterini paylaşacak?
5. G3: yorum sayısı bilinmiyorken mevcut k modeli mi, yorum birikimi senaryosu mu hackathon için daha savunulabilir?
6. G3b: ortak BAU referansı ve sıfır olay problemi için en yalın dürüst çözüm nedir?
7. Hangi revizyonlar eski kayıtlarla hesaplanabilir, hangileri yeni LLM koşusu ister?
8. Eksik yanıtlar, bütçe uygunluğu ve yanlış geçişlerin önlenmesi için hangi kontroller gerekiyor?
9. Ek metriklerden hangileri demo ve jüri anlatımına gerçekten katkı sağlıyor?
10. Minimum değişiklik paketi, etkilenen dosyalar, çalışma süresi/maliyet etkisi ve kontrol planı nedir?

Yanıtı şu tabloyla bitir:

| Öneri | Kabul / değiştir / ertele / reddet | Gerekçe | Dosyalar | Eski çıktıyla olur mu? | Risk ve kontrol |
|---|---|---|---|---|---|

**Karar ilkesi:** Hedefi geçirecek sayıları üretmek için formül seçmeyelim. Önce anlamı ve varsayımları sabitleyelim; başarısızlık dahil çıkan sonucu dürüstçe raporlayalım.
