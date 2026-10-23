# 00_CHEATSHEET — TALP Simulation Hackathon, 24 Ekim 2026

**Ekip:** Tolga (LLM/backend/demo) · Emin (veri bilimi/validasyon) · Gürkan (DES/senaryo/ROI/sunum)

## 1. Ana ilke
**Araç hedef değildir.** Problem → karar → yöntem. Kazanan = iş değeri + kanıtlanmış doğruluk + dürüst belirsizlik + çalışan demo.
Kapsam: **1 problem, 1 karar, 1 ana grafik, 1 demo yolu.** Case gelmeden yöntem kararı yok (her öneri [HİPOTEZ]).

## 2. "LLM/ajan gerekli mi?" kutusu
| Kriter | LLM/ajan lehine | Ajansız lehine |
|---|---|---|
| Birim | Bireysel insan yorumu/davranışı | Süreç, kapasite, kuyruk, akış |
| Girdi | Açık uçlu metin / niyet | Sayısal, yapılandırılmış |
| Veri | Tablo yok/yetersiz | Bol, temiz tablo / zaman serisi |
| Ölçülen | "Söylenen vs. yapılan" farkı | Karar kuralları belli |
| Kısıt | Hız/maliyet esnek | Hız, maliyet, doğrulanabilirlik kritik |

**Karar:** 3+ kriter sol → LLM/ajan. 3+ sağ → ajansız. Karışık → **hibrit** (klasik çekirdek, LLM yalnız eksik halkada: özellik üretimi, metin sınıflandırma, senaryo üretimi, açıklama).
**Her durumda 2 cümle yaz:** "LLM'siz baz çözüm şu. LLM şunu ekliyor (ölçülmüş farkla)." Fark ölçülemiyorsa LLM'i çıkar.

## 3. Case tipi → yöntem karar ağacı (8 madde) [HİPOTEZ]
1. Fiyat/paket/tercih → ayrık seçim (MNL) + dağılım-öncelikli mikro-simülasyon; LLM yalnız veri yoksa.
2. Reklam/yaratıcı/metin tepkisi → LLM persona + gömme/kümeleme; PPI düzeltmesi.
3. Churn/elde tutma → sağkalım/GBM + uplift; LLM yalnız neden-metni için.
4. Funnel/UX/yolculuk → süreç madenciliği + Markov/DES; LLM sürtünme notu için.
5. Kriz/itibar/yayılım → ağ kaskadı/SIR/Bass + fikir dinamiği; LLM ton sınıflandırma.
6. Kapasite/operasyon/kuyruk → DES (SimPy) + M/M/c sağlaması + simülasyon-optimizasyon. **LLM gerekmez.**
7. Segmentasyon/pazar girişi → gömme+kümeleme, IPF ağırlıklama, Monte Carlo pazar payı.
8. Regülasyon/sürdürülebilirlik → sistem dinamiği (stok-akış) + senaryo MC + nedensel (DiD/sentetik kontrol).

## 4. Yapılmaması gerekenler (10)
1. Case okumadan mimari kurmak.
2. LLM'i baz çözümle kıyaslamadan kullanmak.
3. Kanıtsız "yüksek doğruluk" demek; her sonuç aralıkla.
4. Doğrulamayı aynı veriyle yapmak (döngüsel doğrulama).
5. Doğrulanmamış kaynak/rakamı sunuma koymak.
6. Birden fazla problem/ana grafik.
7. Feature freeze'den sonra özellik eklemek.
8. Canlı API'ye bağımlı demo (mock mod + kayıt şart).
9. Mod çöküşünü kontrol etmemek (tüm persona aynı cevabı verir).
10. Varsayımı gerçek veri gibi göstermek; "varsayım" etiketi her yerde.

## 5. Zaman noktaları (24 Ekim; saatler sunum saatine göre T)
| Zaman | İş |
|---|---|
| Sabah, konu açılışı | Karar Kartı (≤400 kelime), rol dağılımı |
| İlk 30 dk | Tolga: arayüz+mock; Emin: veri/vekil; Gürkan: karar/ROI çerçevesi |
| T-5 saat | Çekirdek çalışıyor (mock uçtan uca) |
| **T-2,5 saat** | **FEATURE FREEZE** |
| T-2 saat | Validasyon sonuçları + ROI sayıları kilit |
| T-1 saat | Slaytlar bitti, prova 1 |
| **T-30 dk** | **Demo kaydı + mock mod hazır** |
| T-10 dk | Cihaz/ağ kontrolü, yedek PDF |
| Sunum | 5 dk: Acı, Yöntem, Kanıt, Demo, ROI, Sınırlar |

## 6. B planı özeti
- LLM/API düşer → `MockProvider` + disk cache; sonuçlar "mock" rozetiyle.
- Canlı demo çöker → kayıtlı video + statik PNG grafik.
- Doğrulama zayıf → dürüstçe sun: "güvenme uyarısı" rozeti + sınırlar slaytı; iddiayı küçült.
- Veri yok → vekil veri, "varsayım" etiketi, duyarlılık tablosu.
- Zaman biter → yalnız ana grafik + ROI aralığı + 1 slayt sınırlar; geri kalanı kes.
- Streamlit çalışmaz → notebook/statik HTML export.
