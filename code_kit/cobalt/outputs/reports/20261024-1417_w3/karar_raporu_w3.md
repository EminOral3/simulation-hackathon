# Hafta 3 kriz kararı (14:17) — kilit 14:20/14:30, 4. hafta

**Kriz (3. hafta, dashboard):** tanınmayan küçük kart harcamaları + "Cobalt hacklendi" paylaşımı. Okuma: A05 kart dolandırıcılığı + A07 söylenti. En erken cevap: 4. hafta.

## Öneri: **A1'i 4. hafta için kilitle**
4. hafta: erken maaş + güvenlik paketi (yeni kart + her ödemede uyarı) + anlık itiraz kredisi, herkese, $1.2M. 7. hafta: tasarruf faizi +0.5 (savers), $1.6M. Toplam $2.8M; K2 15:30'a kadar değiştirilebilir (opsiyon korunur).

## Kanıt (LLM, lite, 75 persona; 2 seed: nodecision, A1, B1, C2, D1; diğerleri 1 seed)
| | 4. hafta sonu çıkış (75'te) | 10. hafta aktif % | mevduat % |
|---|---|---|---|
| A1 (4. hafta güvenlik+itiraz, K2=faiz) | **7 / 4** | 69.3 | 79.9 |
| B1 (4. hafta güvenlik+itiraz, K1=5. hafta) | **9 / 3** | 70.3 | 75.4 |
| D1 (kriz cevapsız, 5. hafta K1) | 15 / 10 | 71.1 | 80.6 |
| A3 (4. hafta, itiraz kredisi yok) | 14 | 67.2 | 75.6 |
| Karar yok | — | 68.7 | 83.1 |

- Tek tutarlı sinyal: **güvenlik paketi + anlık itiraz kredisini 4. haftada vermek, krizin ilk haftasındaki çıkışları ~yarıya indiriyor** (iki seed'de de). İtiraz kredisi olmayan A3 bu etkiyi göstermiyor.
- A1 ile B1 arasında 4. hafta etkisi aynı; A1 7. haftadaki faiz opsiyonunu (mevduat hedefi, CFO önceliği) koruduğu için tercih.
- 10. hafta sonuçları setler arasında **ayrışmıyor** (fark 1–2 seed gürültüsü içinde). Surrogate taraması (A3/C1'i öne koydu) bu krizde güvenilir değil: koşu düzeyinde aktiflik r=0.49, mesajı ve itiraz kredisini iyi tanımıyor.

## Güvenmemeniz gereken yer
- **Mutlak seviyeler gerçekçi değil:** bütün setlerde personaların yarısı 10 haftada ayrılıyor/pasifleşiyor (aktif %60–76). Challenge "kriz şirketi batırmaz" diyor; TSB felaketinde yıllık kayıp %1.5. Bu, LLM personalarının akran mesajlarıyla birbirini besleyen aşırı tepkisi (yankı odası). Board'a bu sayılar gösterilmez; kilitten sonra düzeltilecek (bkz. sonraki adım).
- Karar, sadece göreli ve erken-hafta sinyaline dayanıyor.

## Sonraki adım (14:20–15:00)
1. Aşırı tepki: çıkış kaskadını kalibre et (akran etkisi / dormant tanımı), sonra A1 vs D1'i 3 seed ile yeniden koş.
2. K2 (7. hafta faiz) 15:30'a kadar planlayıcıyla yeniden değerlendirilir.
