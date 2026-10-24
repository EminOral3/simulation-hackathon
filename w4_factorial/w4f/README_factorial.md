# K2 için 2^4 tam faktöriyel set (16 koşu, etkileşimler dahil)

**Sabit:** K1 = A1 (kilitli). **Çakışma yok:** K2 setleri K1'in aksiyonlarını (erken maaş, güvenlik paketi, itiraz kredisi) içermez; önceki 16 setle de aynı kombinasyon yok (destek +50 ve kısa/uzun mesaj faktörü yeni).

## Faktörler (her biri 2 seviye; her kombinasyon geçerli bir karar)
| Faktör | -1 | +1 | Neden |
|---|---|---|---|
| A Hafta | 6 (kilit 15:20) | 8 (kilit 16:20) | migration öncesi mi, ölçüm tarihini kapsayan mı |
| B Faiz | +0,25 | +0,5 | rakip farkının yarısı mı tamamı mı |
| C Destek | +50 | +150 | kesinti/sonrası kapasite |
| D Mesaj | kısa (teşekkür + aksiyonlar) | tam (kriz olguları + upgrade) | "mesaj alarmı artırıyor mu" hipotezi (Tolga'nın gözlemi) |
Toplam maliyet 2,25-3,5 M$ (K1 dahil). Offline limit dışarıda (8. haftada geçersiz olur, faktör seviyesi tutarlı kalsın diye).

## Beklenen etkileşimler (test edilecek hipotezler)
- **A×B:** 6. haftada başlayan faiz 3 Ocak'ta biter, 10 Ocak ölçümünü kaçırır → faizin mevduata etkisi 8. haftada daha büyük olmalı.
- **A×D:** tam mesaj 6. haftada migration'ı anlatır (önleyici), 8. haftada geçmişi anlatır → mesajın etkisi haftaya bağlı olabilir.
- **C×A:** destek 6. haftada kesintiyi kapsar, 8. haftada kapsamaz → aktif müşteri ve şikâyete etkisi haftaya bağlı.

## Analiz
- `analyze_factorial.py runs_exp factorial_design.json` → her hedef için 15 kontrast (4 ana, 6 ikili, 4 üçlü, 1 dörtlü etki).
- Tek seed'de hata terimi yok → **Lenth yöntemi**: etkilerin çoğunun sıfır olduğu varsayımıyla (etki seyrekliği) gürültü tahmini (PSE) ve %95 hata payı (ME = 2,57 × PSE). |etki| > ME olanlar gerçek kabul edilir. İkinci seed alınırsa script otomatik ortalar.
- Klasör: `runs_exp/F01__REAL__s1/metrics.json` … `F16`.

## Zaman ve öncelik
- 15:15'e kadar (6. hafta kilidi 15:20): en az **yarım fraksiyon** (D = A·B·C, çözünürlük IV: ana etkiler temiz, ikili etkiler çiftler halinde karışık): F01, F04, F06, F07, F10, F11, F13, F16. Bu 8 koşu A'nın (6 mı 8 mi) ana etkisini verir.
- Kalan 8 koşu 16:15'e kadar → tam tasarım, tüm ikili etkileşimler ayrışır, B/C/D seviyeleri 16:20 kilidi için seçilir.

## Karar kuralı
1. A anlamlı değilse → 8. hafta (opsiyon). A anlamlıysa işaretine göre.
2. Seçilen haftada B, C, D'nin anlamlı seviyeleri; anlamlı değilse ucuz seviye (bütçe/CFO) ve kısa mesaj.
3. Anlamlı ikili etkileşim varsa seviye seçimi o etkileşimin tablosundan yapılır (ana etkiden değil).

**Not:** Dosyalardaki "why" satırları deney etiketidir ("Factorial test run..."). Kilitlenecek K2 seçilince dashboard için 3 satırlık kurul gerekçesi yeniden yazılacak.
