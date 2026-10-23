# 06_DATASETS_AND_TALP — 24 Ekim 2026

Etiketler: [KISMEN] = birincil/resmî sayfa veya özet okundu, ayrıntı doğrulanmadı · [DOĞRULANAMADI] = yalnız arama özeti/ikincil kaynak. **Lisans ve erişim şartlarını indirmeden önce kaynağında oku;** burada hiçbir lisans birincil metinden doğrulanmadı.

## A. Veri setleri (Türkiye / non-WEIRD ağırlıklı)
| Veri | İçerik / neden | Erişim | Lisans | Playbook | Etiket |
|---|---|---|---|---|---|
| **World Values Survey Wave 7** (Türkiye 2018, N≈2 415 CAPI, üniversite listesine göre) | Değer/tutum maddeleri, demografi; LLM'in non-WEIRD yanlılığını ölçmek için hold-out | WVS sitesinden indirme (kayıt/kullanım koşulu kabulü olabilir) | Bu çalışmada okunmadı → siteden doğrula | 7, 8; yanlılık testi | [KISMEN] |
| **TÜİK mikro veri** (İşgücü, Gelir ve Yaşam Koşulları, Nüfus; HBA için doğrulanamadı) | Gerçek nüfus marjinalleri (IPF), harcama/gelir | Bilimsel amaçlı başvuru + Başkanlık izni; A grubu yalnız TÜİK Veri Araştırma Merkezi'nde, B grubu dağıtılabilir. **Hackathon gününe kadar erişim pratikte yok.** | Sözleşme/protokol | 1, 7, 8 (marjinaller yayımlı tablolardan alınabilir, mikro veri gerekmez) | [KISMEN] |
| **TÜİK yayımlı tablolar** (yaş×cinsiyet×bölge, hane büyüklüğü) | IPF hedef marjinalleri için yeterli | Açık web | Siteden doğrula | 1, 7 | [DOĞRULANAMADI] (bu oturumda açılmadı) |
| **Twin-2K-500** (Toubia vd.; 2 058 ABD katılımcı, 500+ soru, 19 deney) | Gerçek-insan + twin karşılaştırma kalıbı, fiyatlama soruları. **Türkiye değil (ABD)** | HuggingFace (ikincil kaynak) | CC BY 4.0 (ikincil kaynak) | 1, 2; yöntem provası | [DOĞRULANAMADI] |
| **European Social Survey** | Avrupa karşılaştırma | ESS veri portalı, giriş sonrası ücretsiz | Açık lisans (Sikt sayfaları) | 7, 8 | [KISMEN]; **Türkiye'nin hangi turlarda yer aldığını doğrulayamadım** |
| Afrobarometer / Arab Barometer | non-WEIRD karşılaştırma | – | – | – | [DOĞRULANAMADI] (arama sonuç vermedi) |
| Sentetik/vekil (kit) | `ds.synth_choice_data`, `ds.synth_population` | yerel | – | tümü | Kendi kodumuz, "SENTETİK" etiketli |

**Bilinmeyen:** Türkiye için perakende/churn/kuyruk gibi operasyonel açık veri setleri aramadım. Kaggle/UCI tipi (Telco churn, e-ticaret oturum logları) çeşit aday ama lisans ve içerik doğrulanmadı.

### Yükleme kodu (kit ile uyumlu; yalnız WVS CSV sütunlarını örnek kabul eder)
```python
# 02_CODE_KIT içinden. Dosya adı/sütunlar indirdiğin sürüme göre değişir: önce df.columns'a bak.
import pandas as pd
from data_sampling import load_proxy, ipf

wvs = load_proxy("WVS_Cross-National_Wave_7.csv", "WVS7 Türkiye",
                 column_map={"B_COUNTRY": "country", "Q262": "age"},   # sütun kodlarını kılavuzdan doğrula
                 low_memory=False)
tr = wvs[wvs["country"] == 792].copy()          # 792 = Türkiye ISO numerik kodu (kod kitabından doğrula)
tr["age_band"] = pd.cut(tr["age"], [17, 29, 44, 59, 120], labels=["18-29", "30-44", "45-59", "60+"])
tr["w"] = ipf(tr.dropna(subset=["age_band"]), {"age_band": {"18-29": .25, "30-44": .30, "45-59": .27, "60+": .18}})  # HEDEF ORANLAR VARSAYIM; TÜİK tablosundan al
```
**Test edilmedi** (veri indirilmedi). Sütun kodları ve hedef oranlar yer tutucudur.

---
## B. Talp (halka açık bilgi; 24 Ekim 2026'da toplandı)
**Kaynak türleri:** talp.ai ana sayfası (WebFetch ile okundu → ürün dili için [KISMEN]); finansman ve kurucu bilgisi ikincil haberler → [DOĞRULANAMADI].

### Ürün dili (talp.ai'den, parafraz)
- "Behavior simulation platform": simüle insan persona'larıyla davranış ve niyet tahmini; **say-do gap** (söylenen vs. yapılan) merkezî kavram; kendini "infrastructure for foresight" diye tanımlıyor.
- Ürünler: **Ad Intelligence** (reklam tepkisi), **Product Intelligence** (ürün/arayüz/Figma testi), **Strategy Intelligence** (pazar/segment/konumlandırma, kapalı testte).
- Sektör çözümleri: E-ticaret (dönüşüm/ödeme), Havacılık (rezervasyon, sadakat), B2B (satın alma komitesi), Medya, Perakende; Finans "yakında".
- Sayfada: ayda 650+ kampanya; kendi tahmin doğruluğuna dair **rakam yok**; isimli müşteri yok; fiyat yok. Genel anket eleştirisi rakamları (ör. anket yanıtlarının %40–45'i sonraki davranışla uyuşmuyor, tek ABD odak grubu ≈ $11K/21 gün) site iddiasıdır, doğrulanmadı.
- İkincil haberler: pre-seed $20M (Temmuz 2026 başı, Formus Capital öncülüğünde) ve kurucu isimleri; kaynaklar merkez konumu ve yatırımcılar konusunda çelişiyor. Sunuma koyma.

### Rakipler (ikincil kaynak; hepsi [DOĞRULANAMADI])
Simile (Joon Sung Park'ın kurucusu olduğu bildiriliyor; haberlerde büyük Series B/değerleme), Aaru, Evidenza, Artificial Societies, Synthetic Users, Viewpoints.ai, Swarm (canlı ürüne persona koşturan). Aynı kategori; **ayrıştırıcı iddialar doğrulanmadı.**

### Olası zayıf noktalar (bunlar hipotezdir, Talp'in gerçek durumunu bilmiyorum)
1. **Kamuya açık doğruluk kanıtı yok:** sayfa kendi tahmin doğruluğunu vermiyor; jüri "kanıt" isteyebilir → bizim güç noktamız: aralık, hold-out, güvenme rozeti.
2. **Say-do gap'ı hem sorun hem iddia:** persona davranışını doğrulamak için gerçek davranış verisi gerekir; bunun nasıl çözüldüğü görünmüyor.
3. **Genel kategori eleştirileri** (varyans sıkışması, grup düzleşmesi, istem duyarlılığı) Talp'e de uygulanabilir — bkz. `05_LITERATURE.md` #5, #9. Talp'in bunları nasıl ele aldığını bilmiyorum.
4. **Operasyon/kapasite gibi LLM-dışı problemler** görünür ürün dilinin dışında (sektör çözümleri tüketici davranışı ağırlıklı).
5. **Türkçe/non-WEIRD doğrulama** kamuya açık değil.
> Uyarı: Bunlar jüriye "Talp şunu yapamaz" diye söylenmemeli; Talp jüride/ortakta olabilir. Doğru ton: "Biz bu case'te şunu *kanıtlıyoruz*." (04'teki soru 7.)

### Etkinlik
"TALP Simulation Hackathon / QNBeyond" için arama sonuç vermedi; etkinlik formatı CLAUDE.md'deki bilgiye dayanıyor, doğrulanmadı.
