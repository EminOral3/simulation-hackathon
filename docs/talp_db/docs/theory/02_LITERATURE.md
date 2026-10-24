# Literatür → Tasarım Kararları (Cobalt simülasyonu)

Etiket: [DOĞRULANDI] = birincil kaynak (makale PDF'i) okundu. Alıntılar 15 kelimeyi geçmez; geri kalanı kendi cümlelerimiz.

## Karar özeti (koda ve sunuma girecekler)

| # | Tasarım kararı | Dayanak |
|---|---|---|
| D1 | Persona = kısa birinci tekil şahıs **yaşam hikâyesi** + sabit alanlar (sadece özellik listesi değil) | Argyle 2022 (backstory ile koşullama), Park 2024 (röportaj tabanlı ajanlar demografik tanımlı ajanlardan daha az yanlı) |
| D2 | Dağılımı **çok örnekle** ölç: aynı persona × 2 seed × (mümkünse) 2-3 örnek; tek cevaba güvenme | Santurkar 2023 (RLHF modelleri tek, modal görüşe yığılıyor) |
| D3 | **Mod çöküşü göstergesi** raporla: haftalık durum dağılımının normalize entropisi ve en sık cevabın payı, grup bazında | Santurkar 2023 (entropi analizi) |
| D4 | **Persona ayrışma (S) ve persona tutarlılık (R) metrikleri**: aynı check-in sorusuna personalar arası varyans (S) ve aynı personanın seed'ler arası varyansı (R) | Costa & Vicente 2026 (moral susceptibility/robustness tanımları) |
| D5 | Simülasyonun güvenilirlik "tavanı" = seed'ler arası tutarlılık; sonuçları buna göre yorumla | Park 2024 (doğruluğu insanların kendi 2 hafta sonraki tutarlılığına göre normalize ediyor) |
| D6 | Geçerlilik ölçütleri olarak Argyle'ın 4 kriteri: dil gerçekçiliği, geçmişle tutarlılık, bağlamdan doğal akış, örüntü uyumu | Argyle 2022 |
| D7 | Gerçek müşteri verisi olmadığı için PPI uygulanamıyor → "Sonraki adım" olarak sunulacak: küçük gerçek panel + büyük sentetik panel ile geçerli güven aralığı | Angelopoulos 2023 |

---

## 1. Argyle ve ark. (2022) Out of One, Many — arXiv:2209.06899 [DOĞRULANDI]
- **Bulgu:** GPT-3'teki yanlılık tek tip değil, demografik olarak ince taneli. Doğru koşullandırılırsa alt grupların cevap dağılımlarını taklit edebiliyor; yazarlar buna "algorithmic fidelity" diyor ve gerçek anket katılımcılarının sosyo-demografik hikâyeleriyle "silikon örneklem" kuruyorlar.
- **Dört kriter:** Sosyal bilim Turing testi, geriye dönük tutarlılık, ileriye dönük tutarlılık, örüntü uyumu.
- **Bize katkısı:** D1 ve D6. Personayı birinci tekil şahıs hikâyesiyle kurmak; jüri "personalar gerçekçi mi?" diye sorduğunda bu dört kriterle cevap vermek.
- **Jüriye tek cümle:** "Personalarımızı demografik etiketle değil, yaşam hikâyesiyle koşullandırdık; bu, LLM'in alt grup dağılımlarını taklit etme kapasitesini kullanmanın bilinen yolu."
- **Sınır:** Siyasi anket bağlamında test edildi; bankacılık davranışına genellenmesi kanıtlanmış değil.

## 2. Santurkar ve ark. (2023) Whose Opinions Do Language Models Reflect? — arXiv:2303.17548 [DOĞRULANDI]
- **Bulgu:** LM görüşleri ile 60 ABD demografik grubu arasında ciddi uyumsuzluk var ve bu uyumsuzluk modeli belirli bir gruba yönlendirince de sürüyor. İnsan geri bildirimiyle eğitilmiş modellerin cevap dağılımı çok keskin, düşük entropili; çeşitliliği tek bir modal görüşe indirgiyor. 65+ ve dul bireyler gibi gruplar kötü temsil ediliyor. Ölçüt olarak 1-Wasserstein mesafesi kullanılıyor.
- **Bize katkısı:** D2 ve D3. "Personaya grup bilgisi vermek dağılımı otomatik düzeltmez" uyarısı. Bu yüzden haftalık durumların grup içi dağılımını entropiyle raporlayacağız; tek bir personanın cevabını grubun cevabı saymayacağız.
- **Jüriye tek cümle:** "LLM'ler modal cevaba yığılır; bu yüzden her grupta cevap çeşitliliğini ayrıca ölçtük ve düşükse bunu sınır olarak raporladık."
- **Not:** Cobalt müşterisi 22-40 yaşında; Santurkar'ın en kötü temsil edilen grupları (65+) bizde yok, bu bir avantaj ama "iyi temsil ediliyor" kanıtı değil.

## 3. Angelopoulos ve ark. (2023) Prediction-Powered Inference — arXiv:2301.09633 [DOĞRULANDI]
- **Bulgu:** Az sayıda altın standart (gerçek) gözlem ile çok sayıda makine tahmini birleştirilerek geçerli güven aralıkları kurulabiliyor. Tahminler gerçek veri gibi kullanılırsa (imputation) aralıklar yanlış yere ve fazla dar çıkıyor. "Rectifier" ile tahmin hatası ölçülüp düzeltiliyor. Ortalama için tahminci: sentetik ortalama eksi (tahmin − gerçek) farkının ortalaması.
- **Ne zaman işe yarar:** Sentetik örneklem gerçek örneklemden çok büyükse ve tahminler sonuç varyansının bir kısmını açıklıyorsa. Model zayıfsa ya da sentetik örneklem küçükse klasik yöntem daha iyi.
- **Bize katkısı:** D7. Bugün gerçek Cobalt müşteri verisi olmadığı için uygulayamıyoruz. Dürüst sınır ve "sonraki adım" olarak sunacağız: Cobalt'ın 200-300 gerçek müşterisine aynı check-in sorularını sorup sentetik paneli PPI ile düzeltmek.
- **Jüriye tek cümle:** "Sentetik sonuçları gerçek veri gibi kullanmak yanlı ve aşırı emin aralıklar verir; küçük bir gerçek panelle düzeltilmeli."

## 4. Costa & Vicente (2026) Persona-Model Collapse in Emergent Misalignment — LatinX @ ICML 2026 [DOĞRULANDI]
- **Bulgu:** Zararlı veriyle ince ayar yapılan modellerde persona makinesi bozuluyor: personalar arası ayrışma kontrolsüz artıyor (S), aynı personanın tutarlılığı düşüyor (R).
- **Metrikler:** S = her soru için persona ortalamalarının standart sapmasının sorular üzerinden ortalaması (personalar arası ayrışma). R = 1 / (aynı persona-soru çiftindeki tekrarlar arası standart sapmanın ortalaması) (persona içi tutarlılık).
- **Bize katkısı:** D4. Biz ince ayar yapmıyoruz, makalenin ana konusu bizimle ilgisiz. Ama S ve R metrikleri doğrudan kullanılabilir: check-in sorularındaki 8 soru üzerinde, persona × seed verisiyle S ve R hesaplarız. Düşük S = personalar birbirine benziyor (ayrışma yok); düşük R = aynı persona seed'ler arasında tutarsız.
- **Jüriye tek cümle:** "Personalarımızın hem birbirinden ayrıştığını hem de kendi içinde tutarlı kaldığını iki ayrı metrikle ölçtük."
- **Sınır:** Bu metrikler ahlaki temeller anketi için geliştirildi; bizim 8 check-in sorumuza uyarlama bizim tercihimiz.

## 5. Park ve ark. (2024) Generative Agent Simulations of 1,000 People — arXiv:2411.10109 [KISMEN: özet ve Stanford HAI sayfası okundu]
- **Bulgu:** İki saatlik röportaj transkriptleriyle kurulan ajanlar GSS cevaplarını, katılımcıların kendi iki hafta sonraki tutarlılıklarının %85'i kadar doğru tekrarlıyor; demografik tanım verilen ajanlara göre gruplar arası doğruluk farkı daha düşük.
- **Bize katkısı:** D1 ve D5.

## 6. Park ve ark. (2023) Generative Agents [DOĞRULANAMADI: bugün okunmadı]
- Hafıza akışı, yansıtma ve planlama mimarisi. Bizdeki karşılığı: personanın haftalık hafıza özeti (10 hafta boyunca süreklilik ve jürinin canlı sorgusu için).

---

## Sahnede iddia ETME
- "Personalarımız gerçek müşterileri %X doğrulukla temsil ediyor" → elimizde gerçek veri yok.
- "LLM personaları anketlerin yerini alır" → Santurkar ve PPI tam tersini söylüyor; düzeltme gerektiriyor.
- Park 2024'teki %85'i kendi sonucumuz gibi sunmak → farklı model, farklı görev.
