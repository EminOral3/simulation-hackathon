# 4. hafta güncellemesi: K2 için 16 set (+1 kontrol)

**Kilitli:** K1 = A1 (4. hafta, everyone: erken maaş + güvenlik paketi + anlık itiraz kredisi, 1,2 M$). Tüm dosyalarda birinci karar budur, değiştirilmez.
**Duyurular:** `announcements/ann_real.json` = 6. hafta (dossier, tam metin) + 3. hafta kriz (dashboard) + 4. hafta güncellemesi (dashboard, update_of: 3, severity: low).

## Okuma
4. hafta güncellemesi krizi küçültüyor: neden belli (işlemci hatası + başka yerde çalınmış kartlarla test işlemleri), Cobalt'ın sistemleri ihlal edilmemiş, etkilenen ~9.000 müşteri (2,1 milyonun ~%0,4'ü). A1'in dispute credit ve güvenlik paketi tam bu iki soruna cevap. → Hızlı tehdit kalmadı. Açık kalan riskler: (1) 6. hafta migration'ı offline limit ve ek destek olmadan, (2) 10 Ocak mevduat ölçümü, (3) henüz görmediğimiz krizler.

## 16 set = 4 hafta × 4 paket (K2)
| Set | Hafta (kilit) | Paket | Toplam |
|---|---|---|---|
| W5_M / W6_M | 5 (14:50) / 6 (15:20) | offline 250 + destek 150 | 2,0M |
| W5_P / W6_P | 5 / 6 | faiz +0,5 (10 Ocak'tan önce biter) | 2,8M |
| W5_C / W6_C | 5 / 6 | offline + destek 150 + faiz +0,5 | 3,6M |
| W5_V / W6_V | 5 / 6 | offline + faizsiz avans + destek 50 | 1,95M |
| W7_P / W8_P | 7 (15:50) / 8 (16:20) | faiz +0,5 (10 Ocak'ı kapsar) | 2,8M |
| W7_C / W8_C | 7 / 8 | faiz +0,5 + destek 150 | 3,5M |
| W7_G / W8_G | 7 / 8 | faiz +0,5 + 5$ iyi niyet (etkilenen ~9.000) | 3,3M |
| W7_L / W8_L | 7 / 8 | faiz +0,25 + destek 150 | 2,7M |
| CONTROL_K1only | — | K2 yok (sadece kontrol amaçlı; teslimde 2 karar şart) | 1,2M |

W5/W6 mesajları kriz güncellemesini teyitli olgularla kapatır ve migration'ı anlatır. W7_G/W8_G iyi niyet kredisi için persona bayrağı gerekir (`affected_card_incident`); 75 personada ~%0,4'lük grup en fazla 0-1 persona eder, etkisi simülasyonda görünmeyebilir (bilinen sınır).

## Koşu önceliği
1. **14:45'e kadar (W5 kilidi 14:50):** CONTROL_K1only, W5_M, W5_C, W7_P → "K2'yi migration öncesi harcamak, kontrol ve varsayılana göre fark yaratıyor mu?"
2. **15:15'e kadar (W6 kilidi 15:20):** W6_M, W6_C, W6_V, W8_P
3. **15:45'e kadar (W7 kilidi 15:50):** W7_C, W7_G, W7_L, W8_C (R2b: W7 mi W8 mi)
4. Kalanlar: W5_P, W5_V, W6_P, W8_G, W8_L

## Karar kuralı
- W5/W6 paketi, CONTROL'e ve W7_P'ye göre 6. hafta çıkışlarını belirgin biçimde (iki seed'de de) düşürmüyorsa → K2'yi harcama, 7/8. haftaya sakla (minimax pişmanlık: gelecek krizler).
- W7 ve W8 farkı seed gürültüsü içindeyse → W8 (opsiyon bir hafta daha açık).
- Önsel tercih (sonuç gelmezse): **W8_C** (faiz +0,5 + destek 150, 3,5M toplam), 16:20'de kilit. 15:50'ye kadar yeni kriz gelirse playbook R1-R4.
