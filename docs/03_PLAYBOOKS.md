# 03_PLAYBOOKS — 8 case arketipi [tümü HİPOTEZ; case gelince doğrula]

Kısaltmalar: **KD** = karar verici ve karar · **LK** = LLM kapısı + ajansız baz · **Y** = yöntem · **V** = veri/vekil · **T** = validasyon testi · **ROI** · **G** = ana grafik · **Tz** = tuzaklar · **20dk** = ilk 20 dk planı (Tolga / Emin / Gürkan).
Kit dosyaları: `dm`=decision_models, `sc`=sim_core, `val`=validation, `ds`=data_sampling.
ROI formüllerindeki tüm parametreler VARSAYIM etiketli girilir; `roi.tornado` ile duyarlılık verilir.

---
## 1. Fiyat / paket
- **KD:** Ürün/ pazarlama müdürü; fiyat ve paket (Basic/Plus/Pro) seçimi.
- **LK:** Satış/ A-B verisi varsa → **ajansız** (MNL/lojistik). Veri yoksa ve yeni ürünse → hibrit: LLM persona yalnız sözlü tercih/WTP üretir, klasik modelle kalibre edilir. Baz: kural/MNL (`RuleModel`/`MLModel`).
- **Y:** MNL/conjoint + dağılım-öncelikli mikro-simülasyon + Monte Carlo. **Alışılmadık:** *Kalman ile canlı kalibrasyon*: LLM'in WTP tahmini önsel, her gerçek satış/anket cevabı gözlem; sentetik yanlılık terimi çevrimiçi güncellenir (demo'da "veri geldikçe aralık daralıyor").
- **V:** Gerçek: işlem logu, anket. Vekil: yayımlanmış WTP/fiyat esnekliği literatürü [DOĞRULANDI etiketi ancak kaynak okununca]; sentetik: `ds.synth_choice_data`. Hepsi "varsayım" etiketli.
- **T:** Fiyat↑ → talep↓ yön testi; hold-out fiyat noktasında JSD/MAE; alt grup tablosu (`val.subgroup_table`); PPI ile yanlılık düzeltmesi.
- **ROI:** (Δfiyat × P(al) × hacim × marj) − uygulama maliyeti; kannibalizasyon terimi: − Σ paket geçiş kaybı.
- **G:** Fiyat → gelir eğrisi, güven bandı + gerçek hold-out noktaları.
- **Tz:** LLM'in fiyat duyarlılığını olduğundan düşük/yüksek vermesi (kalibrasyon şart); tek segment ortalaması; "söylenen WTP ≠ ödenen".
- **20dk:** T: prompt+mock arayüz / E: veri envanteri, hold-out ayır / G: karar ve ROI parametre listesi.

## 2. Reklam / yaratıcı
- **KD:** Pazarlama; hangi mesaj/kreatif, hangi kitleye.
- **LK:** Açık uçlu metin ve yorum önemli → **LLM lehine**. Baz: TF-IDF/gömme + lojistik (geçmiş CTR varsa) veya kural tabanlı skor.
- **Y:** Gömme+kümeleme (kreatif/kitle), LLM persona tepkisi, PPI/DR düzeltme (az sayıda gerçek CTR/anket). **Alışılmadık:** *epidemiyoloji modeli viralite için* — kreatiften çıkan paylaşılma olasılığı → ağda SIR/IC kaskadı (`sc.cascade`, `ba_graph`); R_eff>1 eşiği kreatif seçim ölçütü.
- **V:** Gerçek: geçmiş kampanya CTR. Vekil: kamuya açık reklam metin setleri, yayımlanmış anket tepkileri. Sentetik: kreatif × segment tepki matrisi (varsayım).
- **T:** Kreatif sıralaması için Spearman (LLM vs. gerçek CTR); mod çöküşü (hepsi aynı kreatifi seçiyor mu); yön uyumu.
- **ROI:** (Δ CTR × gösterim × dönüşüm × değer) − üretim/medya maliyeti; viral ek erişim: seed × R_eff etkisi.
- **G:** Kreatif sıralaması (tahmin vs. gerçek) + belirsizlik çubukları.
- **Tz:** LLM'in "iyi yazılmış" metni sevmesi (estetik yanlılık); küçük n'de sıralama gürültüsü; marka güvenliği.
- **20dk:** T: kreatif×persona prompt / E: gerçek CTR ile sıralama testi / G: kampanya maliyet yapısı.

## 3. Churn
- **KD:** CRM/ürün; kimi, hangi müdahaleyle elde tutmalı (bütçe kısıtlı).
- **LK:** Genelde bol tablo → **ajansız** (sağkalım/GBM + uplift). LLM yalnız ayrılma nedeni metni/çağrı notlarında (hibrit özellik üretimi). Baz: GBM + uplift.
- **Y:** Sağkalım/GBM, uplift, ROI optimizasyonu. **Alışılmadık:** *kuyruk teorisi churn için* — müşteri "sistemde" hizmet bekler; destek bekleme süresi sabır (patience) aşılınca terk eder: `sc.simulate_queue(patience=...)` ile bekleme→churn ilişkisi; kapasite artırımı vs. kampanya maliyeti kıyaslanır.
- **V:** Gerçek: abonelik/olay logu. Vekil: Telco churn tipi açık veri setleri (lisans kontrol edilmeli). Sentetik: terk süresi dağılımı (varsayım).
- **T:** Zamana göre hold-out (sızıntı yok), ECE, uplift için Qini; alt grup tablosu.
- **ROI:** Σ_i [ P(churn_i)·uplift_i·CLV_i ] − müdahale maliyeti; yalnız uplift>maliyet/CLV olanlara.
- **G:** Müdahale bütçesine karşı kurtarılan CLV (uplift vs. rastgele vs. risk-sıralı).
- **Tz:** Risk ≠ uplift (ikna edilebilirler farklı); zaman sızıntısı; kampanya etkisini nedensel olmayan veriyle ölçmek.
- **20dk:** T: veri şeması+uplift iskeleti / E: sızıntısız bölme, baz GBM / G: CLV ve müdahale maliyeti.

## 4. Funnel / UX / yolculuk
- **KD:** Ürün/UX; hangi adımı düzeltmeli.
- **LK:** Olay logu varsa **ajansız** (süreç madenciliği + Markov). LLM: oturum kayıtlarından/geri bildirimden sürtünme notu sınıflandırma (hibrit). Baz: Markov zinciri.
- **Y:** Süreç madenciliği, Markov/DES, Monte Carlo. **Alışılmadık:** *SIR-benzeri "terk bulaşması"* — bir adımdaki hata/yavaşlık sonraki adımda terk olasılığını yükseltir (durum geçiş matrisinde yük); veya akışı kuyruk ağı gibi modelle (adım = istasyon, gecikme = bekleme).
- **V:** Gerçek: tıklama/olay logu. Vekil: açık e-ticaret oturum veri setleri. Sentetik: geçiş matrisi.
- **T:** Hold-out oturumlarında adım dönüşüm tahmini; müdahale sonrası A/B varsa DiD.
- **ROI:** (Δ adım dönüşümü × sonraki adımların çarpanı × sipariş değeri × trafik) − geliştirme maliyeti.
- **G:** Sankey/funnel + "darboğaz düzeltilirse" karşı-olgusal funnel.
- **Tz:** Korelasyon ≠ neden; bot trafiği; oturum tanımı.
- **20dk:** T: olay şeması/ akış / E: veri temizleme, geçiş matrisi / G: adım değerleri.

## 5. Kriz / itibar
- **KD:** İletişim/kriz yönetimi; hangi yanıt, ne zaman, hangi kanal.
- **LK:** Metin (tepki tonu) önemli → **hibrit**: LLM ton/duygu sınıflandırır, yayılım klasik ağ modelidir. Baz: sözlük tabanlı duygu + SIR.
- **Y:** Ağ kaskadı/SIR, fikir dinamiği (bounded confidence), LLM ton sınıflandırma. **Alışılmadık:** *Bass/SIR iyileşmeli* — "kriz olgunlaşır, ilgi söner (R bölmesi)"; yanıt zamanlaması R_eff'i düşürür.
- **V:** Gerçek: sosyal medya akışı. Vekil: kamuya açık kriz olay veri setleri; sentetik: BA ağı + varsayılan p.
- **T:** Geçmiş bir krizde yayılım eğrisini geriye dönük uydurma (zaman bölme); tepe zamanı hatası.
- **ROI:** (önlenen erişim × itibar kaybı/kişi × zaman erkenliği çarpanı) − müdahale maliyeti; belirsizlik geniş verilir.
- **G:** Yayılım eğrisi (müdahale zamanına göre senaryolar, bantlı).
- **Tz:** Ağ yapısı bilinmez; duygu sınıflandırma Türkçe/ironi; gerçek itibar kaybını parasallaştırmak.
- **20dk:** T: ton sınıflandırıcı mock / E: ağ parametreleri, p kalibrasyonu / G: itibar maliyeti varsayımı.

## 6. Kapasite / operasyon
- **KD:** Operasyon müdürü; vardiya/ kapasite/ rota sayısı.
- **LK:** **Ajansız**. LLM gerekmez (hız, doğrulanabilirlik kritik). Baz çözüm zaten M/M/c + DES. LLM yalnız senaryo anlatımı/açıklama için.
- **Y:** DES (SimPy) + M/M/c sağlaması + simülasyon-optimizasyon (min maliyet, hizmet seviyesi kısıtı). Dry-run'da heterojen hizmetin M/M/c'yi yanılttığı görüldü (`01_DRY_RUN.md`). **Alışılmadık:** *Bayes opt. ile DES* — pahalı DES çağrısını azaltmak için surrogate.
- **V:** Gerçek: varış/hizmet logları (dağılım uydur). Vekil: literatür tipik dağılımları (varsayım).
- **T:** DES vs. analitik (basitleştirilmiş durumda), tarihsel hafta vs. simüle KPI (Wq, doluluk), replikasyon CI.
- **ROI:** (azalan bekleme maliyeti + terk kaybı azalması) − ek kapasite maliyeti.
- **G:** Kapasite → Wq/terk eğrisi, hizmet seviyesi çizgisi ve CI.
- **Tz:** Varış sürecini Poisson varsaymak (pik saatler); warm-up atlamak; tek replikasyon.
- **20dk:** T: parametre arayüzü / E: dağılım uydurma / G: sistem şeması + KPI tanımı.

## 7. Segmentasyon / pazar girişi
- **KD:** Strateji/GTM; hangi segment, hangi pazar önce.
- **LK:** Anket/pazar verisi varsa ajansız (kümeleme + MNL). Yeni pazarda veri yoksa LLM persona (hibrit) ile ön tarama. Baz: k-means/GMM + pazar payı MC.
- **Y:** Gömme+kümeleme, IPF ağırlıklama (hedef pazar nüfusuna), Monte Carlo pazar payı. **Alışılmadık:** *Difüzyon + rakip tepkisi oyunu* — Bass büyümesi + basit oyun kuramı (rakip fiyat yanıtı) ile giriş zamanlaması; Kalman ile pazar parametresi güncelleme.
- **V:** Gerçek: TÜİK/anket (nüfus marjinalleri). Vekil: WVS/Hofstede benzeri (bkz. 06). Sentetik: `ds.synth_population` + IPF.
- **T:** Bilinen bir pazarda "geriye dönük giriş" testi; segment boyutu doğruluğu; kararlılık (bootstrap kümeler).
- **ROI:** (segment boyutu × penetrasyon × ARPU × marj × ufuk) − giriş maliyeti; senaryo: düşük/baz/yüksek penetrasyon.
- **G:** Segmentlere göre değer × risk haritası (balon grafiği) veya pazar payı yolu.
- **Tz:** WEIRD yanlılığı (LLM Batı-merkezli); küme sayısı keyfî; IPF boş hücre.
- **20dk:** T: gömme+küme / E: marjinal veriler, IPF / G: giriş maliyet yapısı.

## 8. Regülasyon / sürdürülebilirlik
- **KD:** Kamu/kurumsal politika; hangi düzenleme/teşvik, hangi eşik.
- **LK:** Sistem düzeyi, bireysel yorum az → **ajansız** (SD + MC). LLM: yalnız paydaş tepkisi senaryoları (hibrit, düşük ağırlık). Baz: SD.
- **Y:** Sistem dinamiği (stok-akış, `sc.stock_flow`), Monte Carlo, nedensel (DiD/sentetik kontrol) varsa tarihsel uygulama. **Alışılmadık:** *SIR/Bass ile politika benimseme* + *ABM-SD köprüsü*: SD makro stoku, ABM mikro karar; veya sentetik kontrolle kalibre edilmiş SD.
- **V:** Gerçek: kamu istatistikleri, emisyon/enerji verisi. Vekil: uluslararası açık veri (OECD/Eurostat; erişim kontrolü). Sentetik: stok başlangıç değerleri (varsayım).
- **T:** Geçmiş yıl politikasında geriye dönük; birim/denge kontrolü (stok korunumu); parametre duyarlılığı.
- **ROI:** (Δ emisyon × karbon fiyatı + sağlık/enerji tasarrufu) − uygulama maliyeti; sosyal NPV ufku ve iskonto açıkça etiketli.
- **G:** Senaryolara göre stok yolu (örn. emisyon) ve belirsizlik şeridi.
- **Tz:** SD'de keyfî katsayılar (doğrulanamaz); uzun ufuk; ikincil etkiler.
- **20dk:** T: stok-akış şeması kodu / E: veri bulma, parametre aralığı / G: politika senaryoları ve kriter.

---
## Alışılmadık hibrit özeti (≥3; hepsi [HİPOTEZ], hiçbiri bu fazda test edilmedi)
| # | Hibrit | Playbook | Neden ilginç |
|---|---|---|---|
| 1 | Epidemiyoloji (SIR/R_eff) → viralite | 2, 5 | Kreatif seçimi tek ölçüte (R_eff>1) indirger |
| 2 | Kuyruk teorisi (patience) → churn | 3 | Destek kapasitesi ile terk arasında nedensel hikâye |
| 3 | Kalman/çevrimiçi Bayes → canlı kalibrasyon | 1, 7 | Jüri önünde "veri geldikçe belirsizlik daralıyor" |
| 4 | Bayes opt. + DES surrogate | 6 | Pahalı simülasyonda hızlı arama |
| 5 | SD makro + ABM mikro | 8 | Politika katmanları arası |
