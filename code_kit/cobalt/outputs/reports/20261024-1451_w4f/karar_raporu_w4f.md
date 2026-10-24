# Hafta 4 faktöriyel (14:51): K2 — 2^4 tam tasarım, 16 LLM koşusu (lite, seed 1)

**Öneri: F05 — 6. hafta, herkese: faiz +0,5 + destek +50, kısa mesaj.** K2 $1,85M, toplam $3,05M. Kilit: 6. hafta (15:30'dan önce; README 15:20).
**Acil:** W5_C 5. hafta için kilitliyse 15:00'ten önce F05 ile değiştirin; 5. hafta başlayınca değiştirilemez.

## Etkiler (Lenth, |etki| > ME = gerçek)
| hedef | anlamlı etki | yorum |
|---|---|---|
| aktif (g1) | **A (hafta) −7,8**, **A×B −5,0** | 8. hafta, 6. haftadan 7,8 puan kötü. Faiz +0,5 6. haftada yardımcı, 8. haftada değil |
| mevduat (g2) | yok (A −2,8, ME 4,0) | yön aynı: 6. hafta daha iyi |
| rating (g3) | **A −0,05** | 6. hafta daha iyi |
| CFPB (g3b) | yok | güvenilir ayrım yok |
| destek (C), mesaj (D) | anlamlı değil | kural: ucuz seviye (+50) ve kısa mesaj |

A×B hücre ortalamaları (aktif %): 6. hf +0,25: 77,9 · 6. hf +0,5: **82,0** · 8. hf +0,25: 75,0 · 8. hf +0,5: 69,2.

## Hücre seçimi
6. hafta + faiz +0,5: F05 (destek 50, kısa) **85,8 / 88,4** · F06 (destek 50, tam) 82,6 / 85,4 · F08 (destek 150, tam) 82,3 / 83,9 · F07 (destek 150, kısa) 77,5 / 81,4 (aktif / mevduat).
Önceki tur W5_C (5. hf, offline+destek150+faiz) seed 1: 76,9 / 81,6 → F05 aynı seed'de +9 / +7.

## Riskler
- Tek seed; tek koşu gürültüsü ≈ ±3,5 puan (PSE'den). Seed 2 (F05, F06, F08, F02) koşuyor, ~14:54'te.
- F05'te offline limit yok: 6. hafta migration'ında $100 üstü kart ödemeleri reddedilir (A1 bunu kapsamıyor).
- Faiz 6.–9. hafta açık, 3 Ocak'ta biter; 10 Ocak ölçümünden önce. Buna rağmen mevduat en yüksek hücre.
- Mutlak seviyeler hâlâ gerçekçi değil; karar göreli sıralamaya dayanır.

## GÜNCELLEME 14:53 — seed 2 sonrası öneri değişti: **F08**
| set (6. hf, faiz +0,5) | seed 1 aktif/mevduat | seed 2 | **2 seed ort.** | rating ort. | maliyet (toplam) |
|---|---|---|---|---|---|
| **F08** destek 150, tam mesaj | 82,3 / 83,9 | 85,7 / 90,4 | **84,0 / 87,1** | 4,47 | $3,5M |
| F05 destek 50, kısa mesaj | 85,8 / 88,4 | 75,8 / 86,0 | 80,8 / 87,2 | 4,41 | $3,05M |
| F06 destek 50, tam mesaj | 82,6 / 85,4 | 79,7 / 83,2 | 81,2 / 84,3 | 4,41 | $3,05M |
| F02 faiz +0,25, destek 50, tam | 81,9 / 82,2 | 75,5 / 81,9 | 78,7 / 82,0 | 4,42 | $2,25M |
| W5_C (5. hf; önceki öneri) | 76,9 / 81,6 | 77,0 / 86,8 | 76,9 / 84,2 | 4,47 | $3,6M |

- Sağlam bulgu (faktöriyel + 2 seed): **6. hafta + faiz +0,5**, 8. haftadan ve W5_C'den iyi.
- Hücre içinde F08: aktifte en iyi (+3,2 F05'e göre), mevduat eşit, rating en iyi; tek seed gürültüsü ±3,5 olduğundan F05/F08 farkı kesin değil. F05 $0,45M ucuz.
- F08 mesajı kriz olgularını ve upgrade'i (6. hafta) anlatıyor: dürüstlük + migration bilgisi.
