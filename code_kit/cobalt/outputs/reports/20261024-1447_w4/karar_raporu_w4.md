# Hafta 4 kararı (14:47): K2 — kilit 14:50 (5. hafta)

**Öneri: W5_C'yi 5. hafta için kilitle** (`params/decisions/w4/w4_W5_C.json`). Herkese: offline limit $250 + ek destek +150 + tasarruf faizi +0,5 (4 hafta, $50k'ya kadar). K2 $2,4M, toplam $3,6M (bütçe $4M).

Durum: K1 = A1 kilitli (4. hafta). 4. hafta duyurusu 3. hafta krizini küçültüyor (işlemci hatası + dışarıda çalınmış kartlarla test; sistem ihlali yok, ~9.000 müşteri).

## Sonuçlar (LLM lite, 75 persona; ağırlıklı board metrikleri, exit_conversion 0,69)
| set | n | 6. hf aktif | 7. hf aktif | 10. hf aktif (g1) | 10. hf mevduat (g2) |
|---|---|---|---|---|---|
| **W5_C** (5. hf: offline+destek+faiz) | 2 | **91,1** | **89,0** | **76,9** (76,9–77,0) | **84,2** |
| W5_M (5. hf: offline+destek) | 2 | 87,9 | 84,3 | 70,8 | 82,1 |
| W7_P (7. hf faiz, eski varsayılan) | 2 | 88,5 | 82,9 | 61,8 | 78,5 |
| Kontrol (K2 yok) | 2 | 84,6 | 81,0 | 63,3 | 77,7 |
| W6_C (aynı paket 6. hf) | 1 | 86,1 | 83,5 | 81,4 | 84,3 |
| W8_C (önsel tercihimiz) | 1 | 87,2 | 81,2 | 75,9 | 83,3 |

- README karar kuralı sağlandı: W5_C, kontrol ve W7_P'ye göre 6.–7. hafta aktifliğini **iki seed'de de** belirgin yüksek tutuyor (seed bazında 7. hf: 89,8/88,2 vs kontrol 82,3/79,6, W7_P 86,5/79,2) ve 10. haftada fark sürüyor.
- Faizin katkısı: W5_C − W5_M = 10. hf aktif +6, mevduat +2 (2 seed). Offline+destek tek başına (W5_M) de kontrolden iyi.
- W6_C tek seed'de 10. haftada daha yüksek (81,4) ama 6.–7. hafta daha kötü; tek seed, ve W5_C'nin iki seed'i birbirine çok yakın. Bekleme kazancı kanıtlanmış değil.

## Bedeli ve riskler
- İki karar da kullanılmış olur: 5. haftadan sonra gelecek bir krize karar menüsünden cevap verilemez (sadece BAU). W8_C bu opsiyonu korurdu ama sonuçları W5_C'nin gerisinde.
- Faiz 5.–8. haftada açık, 10 Ocak ölçümünden önce biter; mevduat yine en yüksek gruptan.
- Mutlak seviyeler gerçekçi değil (10. hafta aktif %60–80; personaların aşırı tepkisi). Karar göreli sıralamaya dayanıyor; sıralama W5_C için iki seed'de tutarlı.
- Rating ve CFPB setleri güvenilir biçimde ayırmıyor (CFPB tek koşuluk sıçramalar).
