# 32 plan: canlı Gemini sonuçları

Model: gemini-3.5-flash-lite. Kaynak kod: 930cb3a. Aynı mevcut 75 persona, 10 hafta, seed=1. Bilinen migration açık; diğer tüm sürpriz duyurular kapalı. Bu rapor surrogate sonuçlarından ayrıdır.

Tek seed taraması: güvenilir başarı olasılığı veya küresel optimum iddiası yoktur. Migration bitişi aşağıdaki tabloda yer alır. Mevcut goal formülleri ve exit_conversion=0.69 dahil varsayımlar değiştirilmedi. Sıralama mevcut optimize utility ve maliyet cezasına göre.

75×10 benzersiz persona-hafta, parsed durumu, failed_parses ve meta status kontrol edildi. Geçersiz koşu hedef başarısı sayılmadı. Mevcut motorun görünmeyen schema/semantik hataları bu yapısal denetimle dışlanamaz.

Tamamlanan: 33 / 33; geçerli: 33; dört hedefi ve bütçeyi sağlayan plan: 29.

|Plan|Maliyet $|G1 %|G2 %|Puan|CFPB/ay|Geçerli|Tüm hedefler|
|---|---:|---:|---:|---:|---:|---|---|
|BASELINE|0|99.17|99.13|4.511|120.0|True|True|
|P03|750,000|99.95|100.25|4.593|120.0|True|True|
|P19|750,000|99.72|102.23|4.562|120.0|True|True|
|P04|1,150,000|100.00|102.07|4.593|120.0|True|True|
|P11|1,200,000|100.00|103.07|4.581|120.0|True|True|
|P27|1,200,000|100.00|102.03|4.578|120.0|True|True|
|P07|1,250,000|100.00|100.88|4.589|120.0|True|True|
|P23|1,250,000|100.00|102.12|4.583|120.0|True|True|
|P12|1,600,000|100.00|102.46|4.568|120.0|True|True|
|P28|1,600,000|99.72|102.65|4.568|120.0|True|True|
|P08|1,650,000|100.00|101.63|4.590|120.0|True|True|
|P24|1,650,000|100.00|101.59|4.589|120.0|True|True|
|P15|1,700,000|100.00|99.68|4.590|120.0|True|True|
|P31|1,700,000|100.00|101.68|4.589|120.0|True|True|
|P16|2,100,000|100.00|102.74|4.590|120.0|True|True|
|P32|2,100,000|100.00|100.79|4.591|120.0|True|True|
|P21|1,650,000|100.00|98.24|4.573|120.0|True|True|
|P22|2,450,000|100.00|98.19|4.565|120.0|True|True|
|P20|1,150,000|98.49|103.04|4.576|120.0|True|True|
|P26|2,400,000|100.00|97.85|4.572|120.0|True|True|
|P30|2,900,000|100.00|97.84|4.596|120.0|True|True|
|P05|1,650,000|100.00|97.75|4.594|120.0|True|True|
|P18|1,950,000|99.72|97.71|4.579|120.0|True|True|
|P29|2,100,000|100.00|97.54|4.596|120.0|True|True|
|P06|2,450,000|100.00|97.39|4.594|120.0|True|True|
|P02|1,950,000|100.00|97.26|4.577|120.0|True|True|
|P17|1,150,000|99.86|97.21|4.575|120.0|True|True|
|P14|2,900,000|100.00|97.24|4.590|120.0|True|True|
|P13|2,100,000|100.00|97.05|4.590|120.0|True|True|
|P01|1,150,000|99.95|97.02|4.580|120.0|True|True|
|P09|1,600,000|99.86|96.90|4.581|120.0|True|False|
|P10|2,400,000|99.72|96.74|4.588|120.0|True|False|
|P25|1,600,000|98.88|95.29|4.555|120.0|True|False|

## Kararlar

- **P03:** H5: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +50; H7: Savings boost on new money only, 4 weeks / +0.25 points. Migration: on time.
- **P19:** H6: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +50; H7: Savings boost on new money only, 4 weeks / +0.25 points. Migration: on time.
- **P04:** H5: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +50; H7: Savings boost on new money only, 4 weeks / +0.5 points. Migration: on time.
- **P11:** H5: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +150; H7: Savings boost on new money only, 4 weeks / +0.25 points. Migration: on time.
- **P27:** H6: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +150; H7: Savings boost on new money only, 4 weeks / +0.25 points. Migration: on time.
- **P07:** H5: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +50; Early pay up to 2 days early, permanently / on; H7: Savings boost on new money only, 4 weeks / +0.25 points. Migration: on time.
- **P23:** H6: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +50; Early pay up to 2 days early, permanently / on; H7: Savings boost on new money only, 4 weeks / +0.25 points. Migration: on time.
- **P12:** H5: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +150; H7: Savings boost on new money only, 4 weeks / +0.5 points. Migration: on time.
- **P28:** H6: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +150; H7: Savings boost on new money only, 4 weeks / +0.5 points. Migration: on time.
- **P08:** H5: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +50; Early pay up to 2 days early, permanently / on; H7: Savings boost on new money only, 4 weeks / +0.5 points. Migration: on time.
- **P24:** H6: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +50; Early pay up to 2 days early, permanently / on; H7: Savings boost on new money only, 4 weeks / +0.5 points. Migration: on time.
- **P15:** H5: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +150; Early pay up to 2 days early, permanently / on; H7: Savings boost on new money only, 4 weeks / +0.25 points. Migration: on time.
- **P31:** H6: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +150; Early pay up to 2 days early, permanently / on; H7: Savings boost on new money only, 4 weeks / +0.25 points. Migration: on time.
- **P16:** H5: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +150; Early pay up to 2 days early, permanently / on; H7: Savings boost on new money only, 4 weeks / +0.5 points. Migration: on time.
- **P32:** H6: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +150; Early pay up to 2 days early, permanently / on; H7: Savings boost on new money only, 4 weeks / +0.5 points. Migration: on time.
- **P21:** H6: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +50; Early pay up to 2 days early, permanently / on; H7: Savings rate boost for 4 weeks, balances up to $50,000 / +0.25 points. Migration: on time.
- **P22:** H6: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +50; Early pay up to 2 days early, permanently / on; H7: Savings rate boost for 4 weeks, balances up to $50,000 / +0.5 points. Migration: on time.
- **P20:** H6: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +50; H7: Savings boost on new money only, 4 weeks / +0.5 points. Migration: on time.
- **P26:** H6: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +150; H7: Savings rate boost for 4 weeks, balances up to $50,000 / +0.5 points. Migration: on time.
- **P30:** H6: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +150; Early pay up to 2 days early, permanently / on; H7: Savings rate boost for 4 weeks, balances up to $50,000 / +0.5 points. Migration: on time.
- **P05:** H5: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +50; Early pay up to 2 days early, permanently / on; H7: Savings rate boost for 4 weeks, balances up to $50,000 / +0.25 points. Migration: on time.
- **P18:** H6: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +50; H7: Savings rate boost for 4 weeks, balances up to $50,000 / +0.5 points. Migration: on time.
- **P29:** H6: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +150; Early pay up to 2 days early, permanently / on; H7: Savings rate boost for 4 weeks, balances up to $50,000 / +0.25 points. Migration: on time.
- **P06:** H5: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +50; Early pay up to 2 days early, permanently / on; H7: Savings rate boost for 4 weeks, balances up to $50,000 / +0.5 points. Migration: on time.
- **P02:** H5: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +50; H7: Savings rate boost for 4 weeks, balances up to $50,000 / +0.5 points. Migration: on time.
- **P17:** H6: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +50; H7: Savings rate boost for 4 weeks, balances up to $50,000 / +0.25 points. Migration: on time.
- **P14:** H5: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +150; Early pay up to 2 days early, permanently / on; H7: Savings rate boost for 4 weeks, balances up to $50,000 / +0.5 points. Migration: on time.
- **P13:** H5: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +150; Early pay up to 2 days early, permanently / on; H7: Savings rate boost for 4 weeks, balances up to $50,000 / +0.25 points. Migration: on time.
- **P01:** H5: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +50; H7: Savings rate boost for 4 weeks, balances up to $50,000 / +0.25 points. Migration: on time.
- **P09:** H5: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +150; H7: Savings rate boost for 4 weeks, balances up to $50,000 / +0.25 points. Migration: on time.
- **P10:** H5: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +150; H7: Savings rate boost for 4 weeks, balances up to $50,000 / +0.5 points. Migration: on time.
- **P25:** H6: Offline card limit during migration $100 -> $250 / on; Extra support staff for 4 weeks / +150; H7: Savings rate boost for 4 weeks, balances up to $50,000 / +0.25 points. Migration: on time.

## Ana bulgular
- 32 planın 29'u bu tek canlı koşuda dört hedefi ve bütçeyi sağladı. P09, P10, P25 mevduat hedefinde kaldı.
- 33 koşunun tamamında 750 benzersiz persona-hafta kaydı var; toplam 24.750 kayıt. failed_parses=0 ve parsed=false haftası yok.
- Seed 1'de bilinen geçiş on time bitti. Bu sonuç gecikmeli geçiş senaryolarını kapsamıyor.
- Kontrol koşusu da tüm hedefleri sağladı: G1=99.1653, G2=99.1256, puan=4.5112, CFPB=120. Karar yok senaryosu yalnız kontrol; yarışmanın tam iki karar şartının yerine geçmez.
- Mevcut utility fonksiyonu yeterli hedef marjında doygunluğa ulaşıyor. P03/P19 aynı skorla en yüksek sıralı iki kararlı planlar; bu, gerçek dünyada eşdeğer veya tek optimum oldukları anlamına gelmez.
- P11 en yüksek son mevduatı verdi (%103.0698), ama farklı amaç ve maliyet ağırlıkları farklı sıralama üretir.
- CFPB bütün koşularda 120: bu taramada ayrıştırıcı bir gösterge olmadı.
- API maliyeti ölçülmedi. Çağrı loglarındaki toplam mantıksal çağrı sayısı 37.636; aynı anda gelen özdeş model+seed+prompt+schema istekleri deney başlatıcısında birleştirildi. Bu yüzden bu sayı faturalanan API istek sayısı değildir.
- Kaynak kod ve goal hesapları değiştirilmedi. Çıktılar yerelde; commit/push yapılmadı.
