# Kriz Kütüphanesi (Cobalt Bank)

Repo konumu: `docs/crisis_kb/CRISIS_KB.md` ve `code/data/crisis_kb.json`

## Ne için var, ne için yok
- **VAR:** Dashboard'dan gelen kriz duyurusunu sınıflandırmak, şiddet aralığı (düşük/baz/yüksek) seçmek, personaların haftalık "gördükleri" akışına haber/sosyal medya/rakip reklamı eklemek ve sonuçların akıl dışı olup olmadığını kontrol etmek.
- **YOK:** Gerçek vakalarda müşterilerin ne yaptığını persona prompt'una yazmak. Bunu yaparsak sonucu önceden yazmış oluruz, jüri bunu "script" olarak görür.

## Kalibrasyon çıpaları (sahnede kullanılabilir, kaynaklar ikincil haber: [KISMEN])
- **TSB 2018:** 5,2 milyon müşterili bir bankada haftalarca süren göç felaketi. Bir yılda yaklaşık 80 bin hesap kapandı (%1,5) ve yaklaşık 204 bin şikâyet geldi (%3,9). → Cobalt'ın 36 saatlik **planlı** kesintisi bunun çok altında kalmalı. Simülasyon %5 aktif kaybı gösteriyorsa önce kodu kontrol et.
- **Capital One, Ocak 2025:** Maaş haftasına denk gelen çok günlü bir sağlayıcı kesintisi. Öfkenin asıl kaynağı belirsiz ve gecikmeli iletişimdi. Birçok müşteri "kapatacağım" dedi. → "Söylenen ile yapılan" farkı için iyi bir örnek.
- **SVB 2023:** Bir günde mevduatın yaklaşık %24'ü çekildi; sigortasız ve birbirine sıkı bağlı mevduat sahipleri vardı. → Yalnızca uç sınır olarak kullanılmalı. Cobalt'ın müşterileri bireysel ve çoğunlukla sigortalı.
- **Kesintilerin ardından oltalama dalgası:** TSB, Rogers ve CrowdStrike vakalarında görüldü. → Migration haftasından sonra ücretli SMS bile dolandırıcılık gibi algılanabilir.

## 14 kriz arketipi (detaylar JSON'da)
A01 Migration'ın uzaması · A02 Göç sonrası hatalı bakiye · A03 Maaş gecikmesi · A04 Oltalama dalgası · A05 Kart dolandırıcılığı veya veri ihlali · A06 Rakiplerin faizle müşteri çekmesi · A07 Batma söylentisi · A08 Üçüncü taraf kesintisi · A09 Kart okuyucu ve ödeme sorunları · A10 Regülatör veya medya incelemesi · A11 Faiz kararı · A12 Kamu kapanması (federal maaşlar) · A13 Austin'de hava olayı veya personel eksikliği · A14 Uygulama ya da giriş hatası

## Kriz geldiğinde 5 dakikalık prosedür
1. Duyuru metnini JSON'daki `signals` alanıyla eşleştir ve 1-2 arketip seç.
2. Okumamızı TEAM_DOC'a yaz: ne biliniyor, ne bilinmiyor, hangi şiddeti varsaydık ve neden.
3. `world_feed_templates` alanından içerik üret ve yalnızca bu krize maruz kalan personalara ver. Maruz kalmayı haber kaynağı, sosyal medya kullanımı ve çevre büyüklüğü belirler.
4. Bir sonraki karara (N+1. hafta) `menu_responses` ve `message_rules` alanlarından aday çıkar.
5. Koşudan sonra `sanity_bounds` değerlerini aşan bir sonuç varsa önce prompt'ları incele.

---

## Tolga'nın Claude'una verilecek prompt

```
GÖREV: Kriz kütüphanesini koda bağla.
KAYNAK: docs/CASE.md esas. Yeni dosya: code/data/crisis_kb.json (ekte).
DOSYALAR: yeni → code/world/crisis.py | değişecek → haftalık döngü (persona prompt'unu kuran fonksiyon) | dokunma → kayıt formatı (runs/*), check.py
İSTENEN:
1. crisis.py: load_kb(); classify(announcement_text) -> [archetype_id] (signals ile anahtar kelime eşleşmesi + elle override); world_items(archetype_id, severity, week, rng) -> haber/sosyal/rakip metinleri.
2. Haftalık döngüde personaya "This week you saw:" bölümü ekle: o haftanın aktif kriz duyurusu (dashboard metni aynen) + exposure'a göre filtrelenmiş world_items. Exposure basit kural: persona'nın news_sources/social_media_use alanları.
3. config/announcements.json: hafta -> duyuru metni + archetype override + severity. surprises=False ise bu dosya yüklenmez (plan_nosurprises için); bilinen migration krizi her zaman açık kalır.
4. JSON'daki calibration_anchors ve outcome bilgileri ASLA persona prompt'una girmez; sadece sanity_check(metrics) için kullanılır ve uyarı basar.
KABUL KRİTERİ: mock modda surprises açık/kapalı iki koşu farklı prompt üretir; check.py kayıt formatını bozmaz; sanity_check çalışır.
ÇIKTI: tam dosyalar; sonunda 3 satır durum; DEVAM_NOTU.md güncelle.
SINIR: yeni bağımlılık yok.
```

---

## İlgililik sınıflandırması (Cobalt için)

| Öğe | Karar | Neden |
|---|---|---|
| TSB 2018 | **Çekirdek** | Aynı kriz tipi (core migration); kayıp ve şikâyet oranları üst sınır olarak kullanılacak |
| Capital One 2025 | **Çekirdek** | Maaş zamanlaması ve iletişim belirsizliği; Cobalt'ın 11 Aralık maaş + 12 Aralık kesinti durumuna birebir uyuyor |
| Kesinti sonrası oltalama | **Çekirdek** | Dossier'deki "SMS'e tepki" ve "dolandırıcılık mağduru" özellikleri buna işaret ediyor |
| SVB 2023 | Sınırlı | Sadece FDIC limiti üstündeki büyük tasarrufçular için uç senaryo |
| Synapse 2024 | Sınırlı | Sadece "FDIC sigortalı" mesajının yeterli olmayabileceğini göstermek için |
| TSB'nin para cezaları, CEO istifası, toplam maliyet | İlgisiz (persona için) | Kurulun bütçesiyle ilgisi yok; sadece sunumda "risk büyüklüğü" örneği olabilir |
| A11 faiz kararı, A12 kamu kapanması, A13 hava olayı | Beklemede | Sadece duyuru gelirse devreye girer; önceden kod yazmaya değmez |
| A10 regülatör incelemesi, A14 uygulama hatası | Düşük öncelik | Etkisi G3 ile sınırlı; şablon yeterli |

## Persona temellendirme kaynakları

| Kaynak | Ne verir | Hangi persona özelliği | Etiket |
|---|---|---|---|
| Fed SHED 2025 (federalreserve.gov/consumerscommunities/shed.htm) | Yetişkinlerin %63'ü 400 $'lık acil gideri nakit veya eşdeğeriyle karşılayabiliyor; %94'ünün banka hesabı var | "maaştan maaşa yaşıyor" ve "birikim" dağılımı | KISMEN |
| Fed SHED 2024 | Yetişkinlerin %21'i 2024'te finansal dolandırıcılık veya scam yaşamış | "dolandırıcılık/oltalama mağduru" dağılımı | KISMEN |
| CFPB Consumer Complaint Database (ücretsiz API, anahtar gerekmez) | Ürün ve konuya göre şikâyet türleri ve müşteri anlatıları | Şikâyet türlerinin dağılımı, personaların şikâyet dili, şikâyet taban oranı | KISMEN |
| ACS (Census) | 22-40 yaş, şehir ve banliyö nüfusunda gelir, meslek, hane yapısı | Demografik alanlar | DOGRULANAMADI (bugün açılmadı) |
| Fed Survey of Consumer Finances | Mevduat bakiyesi dağılımı | Bakiye bandı (büyük tasarrufçular için) | DOGRULANAMADI |
| FDIC household banking survey | Çok bankalılık, hesabı olmayanlar | "kaç bankası var" | DOGRULANAMADI |

Kural: Bu kaynakların ulusal oranlarını doğrudan kopyalamıyoruz. Cobalt'ın müşterisi 22-40 yaşında, şehirli ve dijital. Ulusal oranı başlangıç noktası alıp hangi yönde düzelttiğimizi TEAM_DOC'a yazıyoruz.
