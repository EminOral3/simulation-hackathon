# 3. hafta krizi: 16 karar seti (dec_00 formatı)

Duyuru: `announcements/ann_real.json` = dossier krizi + 3. hafta dashboard duyurusu (source: dashboard). Okumamız: A05 kart dolandırıcılığı/kart testi + A07 "hacklendi" söylentisi → HIZLI kriz → N+1.

## ÖNEMLİ: hafta kuralı
Challenge: "Bir hafta içinde gelen krize en erken N+1'de cevap verilir; haftası başlamış karar bir sonraki haftaya kayar." → 3. hafta için girilen karar 4. haftaya (14:30) kayar. Dosyalarda en erken hafta = 4. **4. hafta için son kilit 14:20.** Dashboard'da gerçekten 3. hafta seçilebiliyorsa sadece `week` alanını değiştirin.

## 16 set = 4 araç × 4 varyant
| Kod | Araç | K1 | K2 | Toplam |
|---|---|---|---|---|
| A1 | K1'i 4. haftaya çek, krizi katla | H4: erken maaş + güvenlik paketi + itiraz kredisi | H7 faiz | 2,8M |
| A2 | 〃 | H4: güvenlik + itiraz + destek 150 | H7 faiz | 3,0M |
| A3 | 〃 | H4: erken maaş + offline 250 + güvenlik | H7 faiz | 2,5M |
| A4 | 〃 + CEO videosu | A1 aksiyonları | H7 faiz | 2,8M |
| B1 | K2'yi şimdi harca | H5 varsayılan | H4: güvenlik + itiraz | 2,0M |
| B2 | 〃 | H5 varsayılan | H4: güvenlik + itiraz + destek 50 | 2,25M |
| B3 | 〃 + CEO videosu | H5 varsayılan | H4: güvenlik + itiraz | 2,0M |
| B4 | 〃 (en ucuz) | H5 varsayılan | H4: itiraz | 1,7M |
| C1 | K1 5. haftada katla (1 hafta geç) | H5: erken maaş + offline + güvenlik | H7 faiz | 2,5M |
| C2 | 〃 | H5: erken maaş + güvenlik + itiraz | H7 faiz | 2,8M |
| C3 | 〃 | H5: güvenlik + itiraz + destek 150 | H7 faiz | 3,0M |
| C4 | 〃 + CEO videosu | C1 aksiyonları | H7 faiz | 2,5M |
| D1 | Kontrol: cevap yok | H5 varsayılan | H7 faiz | 2,9M |
| D2 | Kontrol: cevap yok, K2 geç | H5 varsayılan | H8 faiz | 2,9M |
| D3 | K2 şimdi, K1 geç | H6 varsayılan | H4: güvenlik + itiraz | 2,0M |
| D4 | Katla, K2 geç | H4: A1 aksiyonları | H8 faiz | 2,8M |

Mesajlar ≤600 karakter, "why" 3 satır, bütçe ≤4M (hepsi doğrulandı). Mesajlar nedeni iddia etmez ("hacklenmedi" demez), bilinmeyeni söyler (dürüstlük + stealing thunder), oltalamaya karşı uyarı içerir.

## Koşu önceliği (14:20 kilidi için zaman çok dar)
1. 14:20'ye kadar: **D1 (kontrol), A1, B1, C2** (×1 seed). Karşılaştırma: "4. haftada K1'e katla" mı, "K2'yi harca" mı, "5. haftaya kadar bekle" mi?
2. Sonra, 14:40'a kadar (C seçeneği 14:50'de kilitlenebilir): A2-A4, B2-B4, C1, C3, C4.
3. D2-D4: K2 haftası/etkileşim için, zaman kalırsa.
Klasör: `runs_exp/{KOD}__REAL__s{seed}/metrics.json`.

## Önsel tercihimiz (sonuç gelmezse)
A1: krizi 4. haftada K1'e katla (playbook R5 + R1/R2: hızlı kriz → N+1; K2 opsiyonu korunur). Bedeli: offline limit ve ek destek düşer.
