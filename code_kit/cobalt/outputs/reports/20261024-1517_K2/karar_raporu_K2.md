# İkinci karar (K2) — karar raporu, 15:17

**Öneri: T25'i 6. hafta için kilitle (son an 15:30; hedef 15:20).** Herkese: tasarruf faizi +0,5 puan (4 hafta, $50k'ya kadar) + ek destek +150 + offline kart limiti $250, "güvenlik" mesajıyla. K2 $2,4M; K1 (A1, 4. hafta) ile toplam **$3,6M**. Dosya: `code_kit/cobalt/params/decisions/w4t/w4t_T25.json`.

## 10. hafta sonu, dört board hedefi
LLM personaları (lite, 75 kişi), 2 seed (seed 1: migration zamanında biter, seed 2: birkaç saat uzar). Ağırlıklı board metrikleri, say-do dönüşümü 0,69.

| | Aktif % (≥98) | Mevduat % (≥97) | Rating (≥4,3) | CFPB/ay (≤240) | Bütçe (≤$4M) |
|---|---|---|---|---|---|
| **T25 (öneri)** | **82,0** (83,9 / 80,2) | **88,2** (89,6 / 86,7) | **4,44** ✓ | 120 ✓* | **$3,6M ✓** |
| T17 (T25, offline'sız) | 81,9 | 88,3 | 4,41 ✓ | 135 ✓* | $3,5M ✓ |
| F08 (önceki öneri) | 84,0 | 87,1 | 4,47 ✓ | 120 ✓* | $3,5M ✓ |
| W5_C (5. hafta) | 76,9 | 84,2 | 4,47 ✓ | 120 ✓* | $3,6M ✓ |
| W8_C (8. hafta, 1 seed) | 75,9 | 83,3 | 4,42 ✓ | 120 ✓* | $3,5M ✓ |
| Kontrol (K2 yok) | 63,3 | 77,7 | 4,34 (seed 2: **4,26 ✗**) | 201 ✓* | $1,2M ✓ |

\* CFPB metriği bu koşularda bilgi taşımıyor (personalar CFPB'ye neredeyse hiç başvurmuyor; 120 = "taban kadar"). Vekil olarak uygulama içi şikâyet sayısı: T25 ayda en çok ~3.300–3.500 (olağan 1.800'ün ~1,9 katı), kontrol ~3.900–4.200 (~2,3 katı). "Olağanın 2 katı" sınırına T25 yakın, kontrol üstünde.

### Hedef bazında yorum
1. **Aktif müşteri (pazarlama):** Hiçbir seçenek 98'e ulaşmıyor. T25 kontrolden +19, W5_C'den +5, 8. haftadan +6 puan. F08 ile fark (−2) gürültü içinde (aynı karar tekrar koşulunca 7 puana kadar oynuyor). Kayıp T25'te 3.–5. haftada (kart krizi), migration sonrası yavaşlıyor.
2. **Mevduat (CFO önceliği):** 97'ye ulaşan yok. T25 en yüksek grupta (88,2), iki seed'de de 86,7'nin üstünde. Faiz 3 Ocak'ta biter; 6. haftada başlamak 10 Ocak'ı kapsayan 8. haftadan yine de daha iyi, çünkü kayıp migration çevresindeki çıkışlardan geliyor.
3. **Rating + CFPB (risk direktörü):** Rating hedefi tutuyor (4,44). Dikkat: rating 6. haftada 4,34'e iniyor, 10. haftada 4,52'ye toparlanıyor; ölçüm 10 Ocak'ta. Kontrolde bir seed'de hedef kaçıyor. Şikâyet yükü sınıra yakın; ek 150 destek kuyruğu kısa tutuyor.
4. **Bütçe (CFO önceliği):** $3,6M, $0,4M pay. T17 ile $0,1M tasarruf mümkün; fark offline limit.

## Neden T25
- **6. hafta + faiz +0,5:** iki ayrı deneyde (17 set, 2^4 faktöriyel) en üstte; 8. hafta faktöriyelde anlamlı biçimde kötü (aktif −7,8).
- **Güvenlik mesajı:** 32 varyantlık ince ayarda tek tutarlı iyileştirme; 4 koşunun 4'ünde iyi (aktif 82,0, mevduat 88,2, en kötü durum 80,2; F08 mesajında en kötü 72,3). İçerik: kart krizinin teyitli nedeni, "sistemlerimiz ihlal edilmedi", itiraz kredisi, "link içeren SMS göndermeyiz", migration'ın ne zaman ve ne yapılamayacağı, aksiyonlar.
- **Offline $250:** simülasyonda ölçülebilir fark yok ama $0,1M'a migration hafta sonu $100 üstü kart ödemelerinin reddini (özellikle küçük işletmeler) önlüyor.
- **Seviyeler:** faizi +0,75'e çıkarmak, cashback eklemek veya "sadece yeni paraya" yapmak iyileştirmedi; ek desteği kaldırmak kötüleştirdi.

## Simülasyonun söyleyemedikleri
- **Mutlak seviyeler gerçekçi değil.** 10 haftada müşterilerin ~%18'ini kaybetmek, TSB'nin yıllık %1,5'lik kaybının çok üstünde. LLM personaları birbirini kızıştırarak aşırı tepki veriyor (sanity uyarıları: 3.–5. haftalarda haftalık kayıp >%1). Board'a güvenilecek kısım **göreli sıralama**, mutlak hedef tahmini değil.
- Tek koşu gürültüsü ±3,5 puan; T25/T17/F08 birbirinden ayırt edilemez, hepsi diğer seçeneklerden iyidir.
- CFPB ve rating'i gerçek dünyaya bağlayan katsayılar varsayım (k=2, CFPB tabanı).
- K2 de harcanmış olur: 6. haftadan sonraki bir krize menüden cevap verilemez (simülasyona göre bekleme bedeli bu opsiyondan büyük).

## Dashboard için "why" (3 satır, deney etiketi yerine)
1. After the card-charge scare and before the Dec 12-13 upgrade, we confirm the facts, warn about scam texts and say what pauses.
2. A 0.5-point savings boost on balances up to $50,000 and 150 extra support staff hold deposits and keep waits short in upgrade week.
3. The $250 offline limit covers larger card payments during the upgrade; $2.4M now, $3.6M total, inside the $4M budget.

## Kilitlenecek dosya ve mesaj düzeltmesi
`code_kit/cobalt/params/decisions/w4t/w4t_T25_lock.json` (T25 + yukarıdaki "why"). Mesajda tek düzeltme: "we credit it at once" → **"we credit up to $100 at once"** (A1'deki itiraz kredisi müşteri başına $100 ile sınırlı; aksi yanıltıcı olur = kırmızı çizgi). Sığması için tekrar eden ", ending after 4 weeks" çıkarıldı ("For the next 4 weeks" süreyi zaten söylüyor). Simüle edilen metinden farkı bu iki ifade; teslim koşuları kilitlenen metinle yapılacak.
