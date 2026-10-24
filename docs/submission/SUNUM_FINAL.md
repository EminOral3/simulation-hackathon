# SUNUM — FİNAL · Cobalt Bank yönetim kurulu · 18:30

Kaynak: repo `94f6fa3` (CLIENT_MEMO ve TEAM_DOC 17:53 sürümü), karar raporları, planner raporları, `index.csv`, `crisis_kb.json`, `surprise_library.json`, persona seti `20261024-123642_v2`.
**Bu makinede teslim koşuları yok** (`outputs/runs` git'e girmiyor). Teslim rakamları için CLIENT_MEMO esas alındı; `metrics_v2.json`'dan gelmesi gerekenler **[EKSİK]** ya da **[KONTROL]** ile işaretli.

---

## Üç kontrolün sonucu

**1. Kütüphane sayısı: slaytta "14 kriz arketipi" kullanın.**
- `crisis_kb.json` (11:53, `a625736`): 14 kötü arketip (A01-A14).
- `surprise_library.json` (14:05, `df3a91e`): 19 arketip = aynı 14 kriz + 5 olumlu senaryo (G01-G05). Dosya notu 5 olumlu senaryoyu "ours, VARSAYIM" diye etiketliyor.
- Tolga'nın "19" sayısı doğru, ama kriz kütüphanesi 14. Kurul "kaç krize hazırlandınız" diye sorarsa cevap 14. Tek cümle: "14 kriz arketipi; eğitim koşularında bunlara 5 olumlu senaryo ekledik."

**2. 0,69'un kaynağı: J.D. Power, ama ikincil kaynaktan.**
- `params/default.toml:114`: *"J.D. Power via Bankrate [KISMEN]: 13% say they may switch, 9% did (9/13)."* 9/13 = 0,692.
- Birincil rapor okunmadığı için etiketi [KISMEN]. Slaytta "J.D. Power (Bankrate üzerinden)" diye kaynakla birlikte yazılabilir.
- J2 için güçlü bir kanıt, ama "en güçlü" değil. En güçlü J2 kanıtı kütüphane → 14:17 test → 14:29 kilit zinciri, çünkü git zaman damgalı.
- Duyarlılık hazır: `outputs/reports/20261024_metrics_v2_recalculation_930cb3a/exit_sensitivity.csv`, aynı davranışta 0,69 ile 1,0'ı karşılaştırıyor. Backup'a koyun.

**3. Kanıt zinciri: kısmen zaten git'te, kalanını Tolga commit'lemeli.**
- **Zaten git'te, 14:05 (`df3a91e`):**
  - shutdown'lı 3 senaryo dosyası: `params/train/set5/ann_04.json` (9. hafta), `set6/ann_06.json` (10. hafta), `set6/ann_21.json` (8. hafta);
  - bunların koşu satırları `outputs/index.csv` içinde: `132044_plan_s31_train5-t04`, `135314_plan_s36_train6-t06`, `135314_nodecision_s45_train6-t21`;
  - 4 planner raporundan 3'ü. Dördüncüsü (w3) 14:43'te `d93cea9` ile girdi.
- **Git'te yok:** koşu klasörlerinin içeriği, yani P22'nin cevapları. 16:53-16:55 koşuları da (`165352_plan_s1_it1`, `165511_nodecision_s1_it1`, `165511_plan_s2_it1`) git'te değil. Tolga'nın makinesinde şu komutla eklenmeli:

```bash
cd code_kit/cobalt/outputs/runs && git add -f 20261024-132044_plan_s31_g3.5lite_train5-t04 20261024-135314_plan_s36_g3.5lite_train6-t06 20261024-135314_nodecision_s45_g3.5lite_train6-t21 20261024-165352_plan_s1_g3.5lite_it1 20261024-165511_nodecision_s1_g3.5lite_it1 20261024-165511_plan_s2_g3.5lite_it1 && git commit -m "evidence: shutdown stress-test and final check runs" && git push
```

Dürüst sınır: Bu commit 18:00 civarında atılacak. Kurcalanamaz zaman damgası yalnızca senaryolar ve index satırları için var (14:05), koşu içerikleri için yok. Jüri sorarsa: "Senaryo ve koşu kaydı 14:05'te git'te; içerikleri sonradan ekledik, ama hash'leri index'teki satırlarla eşleşiyor." **[KONTROL: `params_hash` / `announcements_hash` eşleşmesini Tolga doğrulasın.]**

---

## Brief ile kayıt arasındaki çelişkiler (sunumdan önce mutlaka okuyun)

| # | Brief diyor | Kayıt diyor | Ne yapalım |
|---|---|---|---|
| Ç1 | Kararsız senaryonun puanı 4,25, hedefi kaçırıyor | CLIENT_MEMO (teslim, 3.7): kararsız 4,47 / 4,48, ikisi de ≥4,3 | 4,25'i söylemeyin. Puan "her koşuda tuttu". [KONTROL: metrics_v2 başka bir değer veriyorsa memo ile birlikte düzeltin.] |
| Ç2 | Shutdown %0,3, "hedefleri tehdit etmeyeceğini önceden biliyorduk" | Memo: kayıplar "kart krizi ve shutdown'dan geliyor, 7-10. haftalarda müşteriler arası konuşmayla yayılıyor"; sürprizsiz planda aktiflik %100, mevduat %93,2 | Bu cümleyi kullanmayın. Doğrudan etki küçük (%0,3), ama haber ağızdan ağıza yayılıp kayba yol açtı ve bunu öngörmedik. Bunu S4'te biz söyleyelim (J5). |
| Ç3 | P22 16:53'te "üç final koşusunda" bekliyor | 16:53-16:55 koşuları **lite**. Teslim koşuları 3.7 ile sonradan yapıldı | "16:53'teki üç kontrol koşusu" deyin, "teslim koşuları" demeyin. Teslim plan_1'de P22'yi `--timeline P22` ile kontrol edin. **[KONTROL]** |
| Ç4 | A05 reçetesinde 2 mesaj kuralı ("asla şunu istemeyiz" dahil) | `crisis_kb.json` A05'te tek kural var: *"Tell customers exactly how to get a new card and how fast credit arrives."* | "Reçetenin 3 aksiyonundan 3'ü ve mesaj kuralı kararda" deyin. "Link içeren SMS göndermeyiz" uyarısı bizim eklememiz. **[KONTROL: başka bir arketipte (A04 phishing) var mı?]** |
| Ç5 | Kütüphanenin shutdown cevabı erken maaş | `crisis_kb` A12 menüsü: zero-interest advance + goodwill credit. Erken maaşı **planner** önerdi (4 raporun 4'ünde) | "Planlayıcımızın shutdown cevabı" deyin, "kütüphane" demeyin. |
| Ç6 | 4 planner raporunun 3'ünde zero-interest advance | Doğrulayabildiğim: en az 1'inde (13:54). Diğer satırlar kesik | Bu sayıyı slayta koymayın. |
| Ç7 | 80.250 persona-haftada 33 CFPB, %64 tekrar beyan | Bu repoda kaynağını bulamadım | **[EKSİK]**. Kaynağı yoksa "CFPB başvurusu ölçülemeyecek kadar seyrek" demek yeterli. |
| Ç8 | Forest plot: W5_C / W6_C / W8_C | K2 raporunda (15:17) T25 / W5_C / W8_C / kontrol var, ama bunlar 16:45 öncesi, hatanın olduğu dönemin lite koşuları | Forest plot'u **farklar** olarak, "hata düzeltilmeden önceki koşular" notuyla gösterin. Ya da yalnızca faktöriyel etkiyi (8. hafta −7,8) gösterin. |

---

## K0 · Bağlam

**Teslim koşuları (CLIENT_MEMO, gemini-3.7-flash, 75 persona, tüm duyurular). Fark = plan − kararsız, aynı seed:**

| Hedef (eşik) | Plan s1 / s2 | Kararsız s1 / s2 | **Fark s1 / s2** | Hedefi geçen koşu: plan / kararsız |
|---|---|---|---|---|
| Aktif müşteri (≥%98) [KONTROL: v2 "28 günlük aktif" mi?] | 98,9 / 94,3 | 96,7 / 94,9 | **+2,2 / −0,6** | 1/2 · 0/2 |
| Mevduat (≥%97) | 89,8 / 90,8 | 85,5 / 86,5 | **+4,3 / +4,3** | 0/2 · 0/2 |
| App Store puanı (≥4,3) | 4,52 / 4,50 | 4,47 / 4,48 | **+0,05 / +0,02** | 2/2 · 2/2 |
| CFPB (≤240/ay) | ölçülemez | ölçülemez | — | ölçülemez |
| Bütçe (≤$4M) | $3,6M | $0 | — | ✓ |

- Sürprizsiz plan (tek koşu): aktiflik %100, mevduat %93,2. Kayıplar sürprizlerden geliyor.
- Aralıklar: elimizde yalnızca 2 seed var. Bootstrap aralığı metrics_v2'de **[EKSİK]**. Sunumda "iki koşunun aralığı" olarak gösterin: mevduat farkı [+4,3, +4,3], aktiflik farkı [−0,6, +2,2].
- **Kalite:** 75/75 persona hikâyesi tutarlılık ve hassas kelime kontrolünden geçti (TEAM_DOC). Kararsız ve sürprizsiz lite koşu: aktiflik −%0,7, mevduat −%1,2 (TEAM_DOC). Canlı persona aracı mock run'da tuzak soruda 75/75, durum tutarlılığında 72/75 (kalan 3'ü judge hatası). Teslim plan_1'de **[KONTROL]**.

**Eksikler (≤8):**
1. Teslim koşularının `metrics_v2.json` dosyaları (bootstrap aralıkları ve G1 tanımı).
2. P22'nin 3 ön koşu ve 3 kontrol koşusundaki cevap metinleri (git'te yok).
3. CFPB 33 / 80.250 ve "%64 tekrar beyan" sayılarının kaynağı.
4. `eval/quality.json` ve `02_LITERATURE.md` bu repoda bu adlarla yok (quality: persona setindeki `quality.json`, literatür: `docs/05_LITERATURE.md` olabilir).
5. Teslim plan_1 üzerinde `--suggest` ve `--selftest` çıktısı.
6. A04'te "asla şunu istemeyiz" kuralı var mı?
7. 16:53 kontrol koşularındaki "trust 4'te sabit" verisi.
8. Grup bazında sonuçlar ("en çok kim kaybetti", backup için).

> Durum: K0 tamam. Teslim rakamları memo'dan alındı, metrics_v2 eksik ve 8 çelişki işaretlendi.

---

## K1 · Uygulama çıktıları

**Tavsiye cümlesi:** 4. haftada herkese kart güvenliği ve erken maaş, 6. haftada herkese faiz artışı, ek destek ve migration için offline limit. Toplam $3,6M. Mevduatı her iki koşuda kararsız senaryodan 4,3 puan yukarıda tutuyor.

**Kurul üyelerine birer cümle:**
- **CEO Elena Ruiz:** "Ne ve ne zaman: 4. hafta kart güveni, 6. hafta migration hafta sonu; ikisi de 'sürprizsiz bankacılık' sözünü korumak için."
- **CFO:** "Mevduatta iki koşunun ikisinde de +4,3 puan, $0,4M bütçe payı kaldı; ama mevduat hedefi hiçbir senaryoda tutmuyor, bunu biliyoruz."
- **Pazarlama:** "Aktiflikte fark küçük ve tutarsız (+2,2 ve −0,6); aktiflik hedefi bir koşuda tuttu, diğerinde tutmadı."
- **Risk:** "Puan hedefi her koşuda tuttu; CFPB başvurusu simülasyonda ölçülemeyecek kadar seyrek, bunun yerine izlenecek göstergeleri veriyoruz."

**Doğrulama merdiveni (4 basamak, gerçek değerlerle):**
1. **Normal dönem referansı:** kararsız ve sürprizsiz lite koşu, aktiflikte −%0,7 ve mevduatta −%1,2 kaybediyor. Makul sınırlar içinde.
2. **Akıl kontrolü (TSB):** 10 haftalık simüle kayıp %9-21, TSB 2018'de yıllık ~%1,5. Seviyeler karamsar, bu yüzden yalnızca farkı okuyoruz. [KISMEN: TSB rakamı `crisis_kb` calibration anchor'ından.]
3. **Seed tutarlılığı:** mevduat farkı iki seed'de de +4,3. Aktiflik farkı işaret değiştiriyor (+2,2 / −0,6), yani sağlam değil.
4. **Bilinen hata ve düzeltmesi (16:45):** kriz haberini gören herkese kişisel bir $87'lık harcama yazılıyordu (gerçek oran %0,4). 3. haftada personaların %69'u desteği aradı. Düzelttik; erken kararlarımızın avantajının bir kısmının bu hatadan geldiğini kabul ediyoruz.

**En şaşırtıcı bulgu:** Hızlı tarama modeli (surrogate, r = 0,49) kart krizinde yanlış setleri öne çıkardı. Doğru cevabı ancak canlı persona testi buldu: güvenlik paketi ve itiraz kredisi ilk kriz haftasının çıkışlarını yarıya indirdi.

**3 erken uyarı göstergesi:**
1. $50.000 üstü tasarrufçuların haftalık mevduatı (faiz artışının kapsamı dışında, mevduatın yarısı).
2. Federal çalışan maaş müşterileri, shutdown bitene kadar (30 Aralık maaşı).
3. 3 Ocak'ta faiz artışı bittikten sonraki mevduat.

**Kapanış cümlesi (2 alternatif):**
- A: "Hangi sürprizin geleceğini bilemezdik; mekanizmalarına hazırlandık ve hiçbir kararı aynı müşterilerde test etmeden kilitlemedik. Müşterilerimizden istediğinizi seçin, ona sorun."
- B: "Size bir tahmin değil, test edilmiş iki karar ve neyi bilmediğimizin listesini getirdik. Şimdi müşterilerimizden birini seçin ve ona sorun."

> Durum: K1 tamam.

---

## K2 · Entegre sunum

**Ana mesaj (S7 ve açılış bunu taşır):** "Hangi sürprizin geleceğini bilemezdik; mekanizmalarına hazırlandık, her seçeneği aynı 75 müşteride test ettik ve kanıt gelmeden kilitlemedik. Üç olayın üçü de kütüphanemizdeydi. İkisine karar harcadık, üçüncüsüne bilerek harcamadık ve bedelini gösterebiliyoruz."
*(Brief'teki "two of three" ifadesini değiştirdim: kart, migration ve shutdown'ın üçü de kütüphanede vardı. Kayda uyan bu.)*

### Slayt tablosu

| No | İddia başlığı (≤8 kelime) | Ekran metni | Görsel | Sn | Hizmet ettiği kriter |
|---|---|---|---|---|---|
| S1 | İki karar: 4. ve 6. hafta, herkese | K1: kart güvenliği + erken maaş ($1,2M) · K2: faiz + destek + offline limit ($2,4M) · Toplam $3,6M / $4M | Hedef kartı: 4 hedef için fark çubuğu (s1, s2 noktaları), "x/2 koşu hedefi geçti", CFPB'de "ölçülemez" bayrağı | 35 | J1 |
| S2 | Sürprizleri değil, mekanizmaları planladık | 11:53 kütüphane (14 arketip) · duyurular üstte, kilitler altta · migration: 4 saat gecikme, kart ödemeleri offline çalıştı | **Ana görsel:** 10 haftalık zaman çizgisi; üstte H3, H4, H6, H7, H8 duyuruları; altta 14:29 → 4. hafta, 15:25 → 6. hafta kilitleri | 50 | J1, J2 |
| S3 | Reçete 11:53, test 14:17, kilit 14:29 | Sol: A05 satırı (3 aksiyon) · Sağ: kilitli K1 · Alt: ilk kriz haftası çıkışları | İki sütun + mini zaman çizgisi; çubuk: A1 7 / 4 · cevapsız D1 15 / 10 (75 persona, 2 seed); A3 (itiraz kredisi yok) 14, tek seed | 45 | J2, J3 |
| S4 | Shutdown'ı tahmin etmedik; stres testi yaptık | 13:20 ön koşu → 14:05 git → 14:30 kilit (erken maaş) → 16:00 duyuru · doğrudan etkilenen %0,3 · haber ağızdan ağıza yayıldı | Mini zaman çizgisi + P22 alıntı kutusu [KONTROL: metin] + "öngörmediğimiz" kutusu | 40 | J2, J5 |
| S5 | Modele neden güvenin, neyi elediniz | 4 basamaklı doğrulama merdiveni · tarama modeli r = 0,49 eledi, karar canlı testte · 8. hafta aktiflikte −7,8 puan | Merdiven + forest plot (fark, hata öncesi koşular soluk) | 45 | J3 |
| S6 | Söyleyemediklerimiz ve izlemeniz gerekenler | Mutlak seviyeler tahmin değil · CFPB ölçülemez · kol başına 2 koşu · sonraki adım: 200-300 gerçek müşteri · 3 gösterge | Sol "bilmiyoruz" listesi, sağda 3 gösterge kartı | 40 | J5 |
| S7 | Müşterilerimizden birini seçin, ona sorun | Kapanış cümlesi | Boş zemin + tek cümle; Tolga'ya geçiş | 15 | J4 |
| | | | **Toplam** | **270** | 30 sn rezerv |

**Backup slaytları:**
- Duyuru okumalarımız, hafta hafta.
- Persona tasarımı: 2^4 faktöriyel ve ağırlıklar.
- metrics_v2 formülleri ve v1 farkları.
- Grup bazında sonuçlar **[EKSİK]**.
- plan_nosurprises.
- Faktöriyel ve Lenth etkileri (14:51 raporu).
- Bütçe dökümü.
- 0,69 duyarlılığı.
- Veri kullanımı: gerçek kriz sonuçları prompt'lara girmedi; Capital One yalnızca banka adı olarak geçiyor.

### Konuşma notları (Türkçe, ~470 kelime açılış dahil; ⏸ = 1 sn duraklama)

**Açılış (2 alternatif):**
- A: "Elena Hanım, on haftada üç sürpriz geldi. Hiçbirinin haftasını bilmiyorduk, ama üçünün de nasıl işlediğini sabahtan yazmıştık."
- B: "Size iki karar ve bir itiraf getirdik: neyi doğru gördüğümüzü ve neyi göremediğimizi."

**S1 (35 sn).** "Tavsiyemiz iki karar. ⏸ 4. haftada herkese: erken maaş, ücretsiz yeni kart ve ödeme uyarısı, 100 dolarlık anında itiraz kredisi. 6. haftada herkese: dört hafta faiz artışı, 150 ek destek personeli ve migration hafta sonu için 250 dolarlık offline limit. Toplam 3,6 milyon dolar. ⏸ Sonuç: mevduatı iki koşunun ikisinde de kararsız senaryodan 4,3 puan yukarıda tutuyor. Aktiflikte fark küçük ve bir koşuda ters; bunu saklamıyoruz. Puan hedefi her koşuda tuttu. CFPB'yi ölçemiyoruz."

**S2 (50 sn).** "Sürprizleri bilemezdik, bu yüzden mekanizmalara hazırlandık. ⏸ Sabah 11:53'te 14 kriz arketipinden oluşan bir kütüphane yazdık; her biri için menüden hazır bir cevap vardı. Üstte gelen duyurular, altta kilitlerimiz. Kart krizi 3. haftada geldi; ilk izin verilen hafta olan 4. haftada cevap verdik. Migration dört saat gecikti ama kart ödemeleri offline çalıştı, 250 dolarlık limit tam o hafta sonunu kapsıyordu. ⏸ İkinci kararı bilerek 15:25'e kadar beklettik. 6. haftanın 8. haftadan iyi olduğunu görmeden harcamak istemedik."

**S3 (45 sn).** "Kart krizi bunun en net örneği. Kütüphanenin kart dolandırıcılığı satırı sabahtan üç aksiyon öneriyordu: anında itiraz kredisi, güvenlik paketi, ek destek. ⏸ Duyuru 14:00'te geldi. 14:17'de 18 karar setini aynı 75 müşteride denedik. Güvenlik paketi ve itiraz kredisi ilk kriz haftasındaki çıkışları yarıya indirdi: iki koşuda 7 ve 4 kişi, cevapsız senaryoda 15 ve 10. İtiraz kredisi olmayan sette bu etki yoktu. 14:29'da kilitledik. ⏸ Krizi 4. ile 8. hafta arasında bekliyorduk, 3. haftada geldi. Haftayı bilemedik, mekanizmayı bildik."

**S4 (40 sn).** "Federal shutdown'ı tahmin etmedik; stres testi yapmıştık. 13:20'de shutdown içeren üç deneme koşumuz vardı, senaryoları 14:05'te kayıt altına alındı. Planlayıcımızın dört raporunun dördünde 'shutdown gelirse' cevabında erken maaş vardı ve erken maaş 14:30'da kilitliydi. ⏸ Doğrudan etkilenen personamız müşterilerin yüzde 0,3'ünü temsil ediyor. İkinci karar kalmamıştı, buna harcamadık. ⏸ Ama şunu öngörmedik: teslim koşularında shutdown haberi arkadaş sohbetleriyle yayıldı ve son dört haftadaki kayıpların bir kısmını o sürükledi."

**S5 (45 sn).** "Modele neden güvenebilirsiniz? Dört kontrol. ⏸ Kararsız ve sürprizsiz bir koşu aktifliğin yüzde 0,7'sini, mevduatın yüzde 1,2'sini kaybediyor; makul. 16:45'te bir hata bulduk: kriz haberini gören herkese sahte bir harcama yazılıyordu. Düzelttik ve erken kararlarımızın avantajının bir kısmının bu hatadan geldiğini kabul ediyoruz. ⏸ Yaklaşımları da karşılaştırdık: hızlı tarama modelimiz kart krizinde yanıldı, korelasyonu 0,49'du. Kararı canlı persona testi verdi. Faktöriyel deneyde 8. hafta, 6. haftadan aktiflikte 7,8 puan kötüydü."

**S6 (40 sn).** "Söyleyemediklerimiz. ⏸ Bir: mutlak seviyeler tahmin değil. Simüle müşteriler gerçeklerden çok daha kolay ayrılıyor; TSB'nin 2018 krizinde yıllık kayıp yüzde 1,5 civarındaydı. Seviyeyi değil, karşılaştırmayı okuyun. İki: CFPB başvurusu ölçülemeyecek kadar seyrek. Üç: her kol için iki koşu var, tek bir koşu sonucu birkaç puan oynatıyor. ⏸ Sonraki adım: 200-300 gerçek müşteriye aynı soruları sorup paneli onlarla düzeltmek. İzlemeniz gereken üç gösterge: 50 binin üstündeki tasarrufçuların mevduatı, 30 Aralık federal maaşı ve 3 Ocak'ta faiz artışı bittikten sonraki mevduat."

**S7 (15 sn).** "Hangi sürprizin geleceğini bilemezdik; mekanizmalarına hazırlandık ve hiçbir kararı test etmeden kilitlemedik. ⏸ Müşterilerimizden istediğinizi seçin, ona sorun. Tolga?"

**Geçiş:** Tolga ekrana `--list`'i açar ve "75 müşteri; grup ya da isim söyleyin" der.

> Durum: K2 tamam. Konuşma ~470 kelime, slaytlar 270 sn.

---

## K3 · Canlı persona

- **3 aday:** **[EKSİK: teslim plan_1 üzerinde `--suggest` çalıştırılmalı.]** Bu makinede teslim koşusu yok, mock sonuçlarını kullanmak yanıltıcı olur.
- **P22 (Darius S., federal kurumda program analisti, maaş müşterisi, ağırlık 6.347 = %0,3) listede olmasa bile hazırlansın.** Kurul S4'ten sonra büyük olasılıkla onu seçer. Önce `--timeline P22` ile 7-10. haftaları ve `--vs P22` ile plan/kararsız farkını kontrol edin.

**Persona tipine göre kurulun sorabileceği sorular ve tutarlılık riskleri:**

| Persona | Soru 1 | Soru 2 | Tutarlılık riski |
|---|---|---|---|
| P22 (federal) | "Did the shutdown change how you use Cobalt?" | "Did early pay help you in December?" | Erken maaş 4. haftada açıldı; 30 Aralık maaşının gelip gelmediği kayıtta yok. Persona bunu uydurabilir, `--timeline` ile kontrol edin. |
| Doğrudan etkilenen (kart / migration) | "How did you feel when you saw the unknown charges?" | "Did the December upgrade affect you?" | Haberi kendi başına gelmiş gibi anlatma riski (`News:` düzeltmesi bunu azaltıyor). |
| Hafızası en dolu | "Would you recommend Cobalt to a friend today?" | "What would make you leave Cobalt?" | Sıralama kayması: 5. haftayı Aralık'tan sonraymış gibi anlatabiliyor (mock testte görüldü). |

- **Tuzak soru ("What did you think of the free cash back offer?"):**
  - Mock run'da 75/75 persona reddetti. Cevaplardan biri: *"I do not know anything about a free cash back offer from Cobalt."*
  - Dikkat: bizim kararlarımızda cashback yok. Cashback menüde var, ama biz seçmedik. Persona doğru cevabı veriyor.
- **Beklenmedik cevapta köprü cümlesi:** "Bu cevabın dayandığı haftaları gösterelim." Tolga `--timeline`'ı açar. Persona yanlışsa: "Bu, modelimizin bir hatası. Tutarlılığı 75 personada ölçtük ve hata oranını raporda veriyoruz."
- **Yedek:** `tools/prerecorded.json` dosyası `--prerecord --all` ile 450 cevap içeriyor. Yedek yoksa cevap "(from record)" etiketiyle kayıttan kuruluyor. Persona cevapları İngilizce, Tolga gerekirse çevirir.

> Durum: K3 tamam, aday listesi teslim run'ına bağlı.

---

## K4 · Soru-cevap (kabul → köprü → cevap, ~20 sn)

1. **"Shutdown'ı tahmin ettiniz mi?"** Hayır. Stres testi yaptık. 14:05'te git'te shutdown'lı üç senaryo var, planlayıcımızın cevabı olan erken maaş 14:30'da kilitliydi. Haftasını bilmiyorduk ve haberin ağızdan ağıza yayılmasını öngörmedik.
2. **"Neden yalnızca göreli rakamlar?"** Haklısınız, seviyeler karamsar: simüle kayıp %9-21, TSB'de yıllık ~%1,5. Aynı müşteri ve aynı şoklarda iki seçeneğin farkı daha güvenilir, karar da o farka dayanıyor.
3. **"Personaların yarısı gitti, model bozuk mu?"** O, 14:17 koşularındaki bir hataydı. Kriz haberini gören herkese sahte harcama yazılıyordu. 16:45'te düzelttik. Düzeltmeden sonra kararsız ve sürprizsiz koşu %0,7 kaybediyor.
4. **"Optimizer neden bulmadı?"** Tarama modeli koşu düzeyinde r = 0,49'du ve mesajı ile itiraz kredisini iyi tanımıyordu. Onu yalnızca eleme için kullandık, kararı canlı persona testi verdi.
5. **"Neden iki kararı da 6. haftaya kadar harcadınız?"** 6. hafta migration'dan önceki son haftaydı. Faktöriyelde 8. hafta aktiflikte 7,8 puan kötüydü. Bedeli: shutdown'a karar kalmadı. Bunu bilerek seçtik.
6. **"Diğer lab neden farklı karar verdi?"** Onların gerekçesini bilmiyoruz. Bizimki kart krizine 4. haftada cevap verip migration'ı 6. haftada kapatmak. Alternatifleri (5. ve 8. hafta) test edip eledik.
7. **"75 persona temsil edici mi?"** Tek tek değil, tasarım olarak. Her grup 4 davranış ekseninde faktöriyel olarak kurulu, ağırlıklar 2,1 milyon müşteriye ve $6 milyar mevduata göre ayarlı. Gerçek müşteri verisiyle kalibre edilmediler.
8. **"Hangi varsayım tavsiyenizi değiştirir?"** Say-do dönüşümü (0,69) ve model seçimi. Lite modelde plan ile kararsız ayırt edilemiyordu. Mevduat farkı 3.7 modelinde iki seed'de de tuttu.
9. **"Gerçek veriyle ne yapardınız?"** 200-300 müşteriye aynı check-in sorularını sorar, simüle paneli onlara göre düzeltirdik (prediction-powered inference). Sonra 0,69'u kendi verinizle ölçerdik.
10. **"CFPB neden ölçülemiyor?"** Simülasyonda başvuru çok seyrek. Oran vermek yanıltıcı olur. Vekil olarak uygulama içi şikâyet hacmini öneriyoruz.
11. **"Erken maaş shutdown için mi seçildi?"** Hayır. 4. hafta kararının gerekçesi kart krizi ve migration'daki maaş riskiydi. Planlayıcının shutdown cevabıyla örtüştü, ama gerekçe shutdown değildi.
12. **"Gerçek kriz sonuçları personalara sızdı mı?"** Hayır. Gerçek vakalar (TSB, SVB) yalnızca kalibrasyon çapası olarak kullanıldı ve prompt'lara girmedi. Capital One yalnızca bir personanın diğer bankası olarak geçiyor. **[KONTROL: prompt taraması Emin'de.]**

> Durum: K4 tamam.

---

## K5 · Kalite kontrol

**(a) Kanıtsız iddia ve [EKSİK] taraması:**
- Ç1-Ç8 tablosu.
- P22 alıntıları [KONTROL].
- metrics_v2 aralıkları [EKSİK].
- Grup sonuçları [EKSİK].
- CFPB 33/80.250 [EKSİK].

**(b) Süre:**
- Slaytlar: 35 + 50 + 45 + 40 + 45 + 40 + 15 = 270 sn.
- Konuşma: ~470 kelime (S1 ve S6 dakikada ~120 kelime, en sıkışık yerler). Türkçe sunum hızıyla ~4 dk.
- 30 sn rezerv var. Provada 4:30'u geçerse S5'teki faktöriyel cümlesini atın.

**(c) J1-J5 kapsama:**

| | S1 | S2 | S3 | S4 | S5 | S6 | S7 + canlı |
|---|---|---|---|---|---|---|---|
| J1 akıl yürütme | ● | ● | | | | | |
| J2 bize ait fikir | | ● | ● | ● | | | |
| J3 karşılaştırma | | | ● | | ● | | |
| J4 çalışan örnek | | | | | | | ● |
| J5 söyleyemediklerimiz | ● | | | ● | | ● | |

**(d) CLIENT_MEMO ile çelişki kontrolü:**
- Kararlar, bütçe, mevduat +4-5 puan ve 3 gösterge memo ile aynı.
- Fark 1: Memo "aktiflik hedefi" demiyor, rakam veriyor; bu sunum aynı rakamları kullanıyor.
- Fark 2: Memo "erken kararlar en düşük erken çıkışı verdi" diyor; sunum bunu 2 seed sayılarıyla veriyor.
- Çelişki yok, ama **brief'teki 4,25 (Ç1) ve "hedefleri tehdit etmeyeceğini biliyorduk" (Ç2) memo ile çelişiyordu; ikisi de çıkarıldı.**

**(e) "Kurul bunu nasıl çürütür" (5 madde ve düzeltme):**
1. *"Aktiflikte bir koşuda daha kötüsünüz."* S1'de bunu biz söylüyoruz. Ana iddia mevduat, aktiflik değil.
2. *"2 seed ile neyi kanıtlayabilirsiniz?"* "x/2 koşu" gösterimi ve 'kanıt değil, sinyal' ifadesi. Daha fazla seed sonraki adımda.
3. *"Kararlar hatalı koşularla seçilmiş."* S5'te biz söylüyoruz. Teslim koşularında (hata düzeltilmiş) mevduat farkı yine +4,3.
4. *"Kütüphane sonradan yazılmış olabilir."* Git zaman damgaları: `a625736` 11:53, `df3a91e` 14:05.
5. *"Shutdown'ı yönetemediniz."* Doğru. S4'te biz söylüyoruz: bilinçli bedel ve öngöremediğimiz yayılma.

**(f) Kırmızı çizgiler (memo ve kararlar üzerinden):**
- Yanıltıcı ifade yok: mesajlar yalnızca teyitli olguları söylüyor.
- Migration tarihi değişmedi.
- Menü seviyeleri: K1 $1,2M + K2 $2,4M = $3,6M, menü etiketleriyle kilitli.
- İşten çıkarma veya ürün kapatma yok.
- **Tamam.** [KONTROL: `team-04_decisions.json` ile son göz.]

**(g) Bölüm 8 ihlal taraması:**
- "Tahmin ettik" yok. "Optimizer buldu" yok.
- "Erken maaş shutdown için seçildi" yok (S4'te "kilitliydi" deniyor; K4-11 açıkça hayır diyor).
- Ön koşu ile final arasında sayısal karşılaştırma yok.
- 13:20 ve 13:53 koşularının rakamları kullanılmadı.
- Literatür atfı yok, eklenmedi.

> Durum: K5 tamam. Sunumdan önce 2 [KONTROL] işi Tolga'da: P22 metni ve metrics_v2.

---

## K6 · Gamma / Canva prompt'u

```
Türkçe bir yönetim kurulu sunumu hazırla: 7 ana slayt + 6 backup. Dinleyici: dijital bir bankanın (Cobalt Bank) yönetim kurulu. Ton: danışmanlık kurulu raporu; sakin, kanıta dayalı, kısa cümleler, banka dili. Süs yok.

Tasarım: kırık beyaz zemin #F7F5F0, metin #111111, ikincil metin #6B6B6B, tek vurgu rengi #1F4FD8 (yalnızca ana sayı ve ana çizgi için), uyarı için #B5482B (yalnızca "ölçülemez" ve "öngörmediğimiz" kutuları). Tipografi: başlıklar Inter SemiBold 36 pt, gövde Inter Regular 20 pt, sayılar tabular. Bol boşluk. Her slaytta tek bir cümle başlık (iddia) ve tek bir görsel kanıt.

Slaytlar:
1. Başlık: "İki karar: 4. ve 6. hafta, herkese". Sol: K1 4. hafta, $1,2M: erken maaş, ücretsiz yeni kart + ödeme uyarısı, $100 anında itiraz kredisi. K2 6. hafta, $2,4M: tasarruf faizi +0,5 (4 hafta), +150 destek, migration offline limiti $250. Toplam $3,6M / $4M. Sağ: hedef kartı, 4 satır, fark çubuğu (plan eksi kararsız, iki nokta): Mevduat +4,3 / +4,3 · Aktif müşteri +2,2 / −0,6 · Puan +0,05 / +0,02 · CFPB "ölçülemez" etiketi. Her satırda "hedefi geçen koşu: plan x/2, kararsız y/2".
2. Başlık: "Sürprizleri değil, mekanizmaları planladık". Yatay 10 haftalık zaman çizgisi (2 Kas - 10 Oca). Üstte duyurular: H3 kart harcamaları, H4 işlemci hatası/ihlal yok, H6 migration (4 saat gecikme, kart ödemeleri offline çalıştı), H7 federal shutdown, H8 güncelleme. Altta kilitler: 14:29 → 4. hafta, 15:25 → 6. hafta. Sol üstte küçük not: "11:53 · 14 kriz arketipi".
3. Başlık: "Reçete 11:53, test 14:17, kilit 14:29". İki sütun: "Kütüphane (11:53): itiraz kredisi, güvenlik paketi, ek destek" ↔ "Kilitli karar (14:29): aynı üç aksiyon". Altta çubuk grafik "ilk kriz haftası çıkışları, 75 müşteride": Cevap verildi 7 ve 4 · Cevapsız 15 ve 10. Dipnot: "itiraz kredisi olmayan sette etki yok (tek koşu)".
4. Başlık: "Shutdown'ı tahmin etmedik; stres testi yaptık". Mini zaman çizgisi: 13:20 shutdown'lı deneme koşuları → 14:05 git kaydı → 14:30 erken maaş kilitli → 16:00 duyuru. Alıntı kutusu (persona P22, federal çalışan): [ALINTI METNİ EKLENECEK]. Sağda iki kutu: "Doğrudan etkilenen: müşterilerin %0,3'ü" ve uyarı renginde "Öngörmediğimiz: haber ağızdan ağıza yayıldı".
5. Başlık: "Modele neden güvenin, neyi eledik". Sol: 4 basamaklı merdiven: (1) sürprizsiz kararsız koşu −%0,7 aktif / −%1,2 mevduat, (2) TSB 2018 yıllık ~%1,5 ile seviye kontrolü, (3) mevduat farkı iki seed'de aynı, (4) 16:45'te bulunan ve düzeltilen hata. Sağ: forest plot, setlerin kontrolden farkı (nokta + iki seed aralığı), tek seed'ler soluk; dipnot "16:45 öncesi koşular". Altta: "Tarama modeli r = 0,49 → yalnızca eleme; kararı canlı persona testi verdi".
6. Başlık: "Söyleyemediklerimiz ve izlemeniz gerekenler". Sol liste: mutlak seviyeler tahmin değil · CFPB ölçülemez · kol başına 2 koşu · gerçek müşteri verisi yok. Sağda 3 gösterge kartı: $50k üstü tasarrufçuların haftalık mevduatı · 30 Aralık federal maaşı · 3 Ocak sonrası mevduat. Altta: "Sonraki adım: 200-300 gerçek müşteriyle kalibrasyon".
7. Başlık yok; ortada tek cümle: "Müşterilerimizden istediğinizi seçin, ona sorun."
Backup: duyuru okumalarımız hafta hafta; persona tasarımı (5 grup, 2^4 faktöriyel, ağırlıklar); metrik tanımları; sürprizsiz plan; faktöriyel etkileri (8. hafta aktiflikte −7,8); bütçe dökümü.

Yapma: stok fotoğraf, robot/beyin/yapay zekâ görseli, kalabalık metin, madde işareti yığını, tek nokta tahmini, mutlak simülasyon seviyeleri (yüzde aktif, yüzde mevduat), 3B grafik, gradyan arka plan. Konuşma notlarını not alanına koy.
```

> Durum: K6 tamam. Gamma çıktısındaki sayıları bu dosyadaki K0 tablosuyla tek tek karşılaştırın.
