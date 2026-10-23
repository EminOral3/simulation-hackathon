# 05_LITERATURE — 24 Ekim 2026

## Etiket kuralı (dürüst)
- **[DOĞRULANDI]** = birincil kaynağın tam metni okundu. **Bu dosyada hiçbir kaynak bu seviyede değil.**
- **[KISMEN]** = birincil kaynağın arXiv/yayın sayfasındaki **özet** okundu (WebFetch, 24 Ekim). Tam metin, yöntem ve tablolar okunmadı.
- **[DOĞRULANAMADI]** = yalnız ikincil kaynak/arama özeti gördüm. Sunuma konmaz.
Sayılar yalnız özet veya belirtilen kaynaktan alındı; tam metinde farklı olabilir. Alıntı yok, yalnız parafraz.

## A. Temel kaynaklar
| # | Kaynak | Yıl | Bulgu (özet parafrazı) | Bize katkısı | Jüriye tek cümle | Etiket |
|---|---|---|---|---|---|---|
| 1 | Argyle vd., *Out of One, Many* (arXiv 2209.06899; Political Analysis 2023 sürümü sayfada bağlı) | 2022/23 | GPT-3'ün yanlılıkları demografiye bağlı ve ayrıntılı; sosyodemografik arka plan verilince alt grup örüntülerine yaklaşabiliyor ("algorithmic fidelity"). | Persona koşullamanın savunulabilirliği. | "Persona koşullama alt grup örüntülerini yakalayabilir; biz bunu hold-out ile ölçüyoruz." | [KISMEN] |
| 2 | Park vd., *Generative Agents* (arXiv 2304.03442) | 2023 | Hafıza, yansıtma, planlama ile 25 ajanlık sandbox'ta tek fikir (parti) topluluğa yayıldı; ablasyonda üç bileşen de katkılı. | Çoklu ajan/sosyal yayılım olabilirliği. Davranış doğruluğu kanıtı **değil** (inandırıcılık ölçüldü). | "Ajanlar inandırıcı davranır; inandırıcı ≠ doğru, biz doğruluğu ayrıca ölçüyoruz." | [KISMEN] |
| 3 | Park vd., *LLM Agents Grounded in Self-Reports…* (arXiv 2411.10109) | 2024 (sayfada sonraki revizyonlar) | 1 052 kişi; mülakat+anket ajanı GSS maddelerinde katılımcının kendi 2 haftalık test-tekrar tutarlılığının ~%86'sı; yalnız demografi %74. | İnsan tavanına göre normalize edilmiş doğruluk: bizim `human_ceiling` yaklaşımının kaynağı. | "Ölçüt insanın kendi tutarlılığı; ondan fazlasını beklemiyoruz." | [KISMEN] |
| 4 | Santurkar vd., *Whose Opinions Do Language Models Reflect?* (arXiv 2303.17548) | 2023 | Modeller ABD demografik grupların görüşlerinden belirgin sapıyor; gruba yönlendirmeyle de kalıyor; 65+ ve dul gibi gruplar zayıf temsil. | Yanlılık ve alt grup hatası için gerekçe. | "Modeller bazı grupları sistematik kaçırıyor; alt grup tablomuz bunu gösterir." | [KISMEN] |
| 5 | Wang, Morgenstern, Dickerson, *LLMs that replace human participants can harmfully misportray and flatten identity groups* (arXiv 2402.01908; Nature Machine Intelligence'a kabul, sayfada yazıyor) | 2024/25 | 3 200 katılımcı, 16 kimlik, 4 LLM: gruplar yanlış temsil ediliyor ve düzleştiriliyor; çıkarım-zamanı teknikleri azaltıyor ama gidermiyor. | Mod çöküşü/düzleşme riski; kimlik özelinde kullanımdan kaçınma. | "Düzleşmeyi ölçüyor ve uyarıyoruz; kimliğin kritik olduğu yerde LLM'i çekirdek yapmıyoruz." | [KISMEN] |
| 6 | Aher, Arriaga, Kalai, *Using LLMs to Simulate Multiple Humans…* (arXiv 2208.10264; ICML 2023 sözlü sunum, sayfada yazıyor) | 2022/23 | "Turing Experiment": Ultimatum, garden-path, Milgram yeniden üretildi; bilgelik-kalabalık testinde bazı modellerde "hiper-doğruluk" bozulması. | Klasik deney yeniden üretimi örnek testi; fazla doğru çıkma tuzağı. | "Fazla iyi çıkmak da bir hata işaretidir." | [KISMEN] |
| 7 | Angelopoulos vd., *Prediction-Powered Inference* (arXiv 2301.09633) | 2023 | Az gerçek etiket + çok model tahmini ile, tahmin modeline varsayım koymadan geçerli güven aralığı; daha iyi tahmin → dar aralık. | `validation.ppi_mean` temeli; "sentetik + az gerçek veri" düzeltmesi. | "Birkaç gerçek etiketle sentetik yanlılığı düzeltip geçerli aralık veriyoruz." | [KISMEN] |
| 8 | Maier vd., *LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings* (arXiv 2510.08338) | 2025 (v3) | Doğrudan sayısal puan istemek gerçekçi olmayan dağılım veriyor; serbest metni referans ifadelerle gömme benzerliğinden Likert dağılımına çevirmek (SSR) 57 anket/~9 300 yanıtta insan test-tekrar güvenilirliğinin ~%90'ı, KS benzerliği >0.85 (özete göre). | Dağılım elde etme stratejisi; `decision_models` bu yolu henüz **uygulamıyor** (bkz. eksikler). Güvenilirlik ≠ satın alma davranışı doğruluğu. | "Puan değil dağılım ister, metinden dağılıma çeviririz." | [KISMEN] |
| 9 | Bisbee vd., *Synthetic Replacements for Human Survey Data?* (Political Analysis 32, 2024, 401–416; doi 10.1017/pan.2024.5) | 2024 | ChatGPT 3.5, 11 grup için his termometresi: ortalamalar ANES'e yakın ama varyasyon düşük, regresyon katsayıları sıklıkla farklı, istem sözcüğü ve zamana (3 ay) duyarlı. | En güçlü eleştiri; tekrarlanabilirlik ve varyans sönümlemesi. | "Ortalama tutması yetmez; varyans, katsayı ve zamansal kararlılığı da ölçüyoruz." | [KISMEN] (yalnız arama özeti okundu: **[DOĞRULANAMADI]'ya yakın**, tam özeti yayıncıdan oku) |
| 10 | Hewitt, Ashokkumar, Ghezae, Willer, *Predicting results of social science experiments using LLMs* | 2024 | Sürümlere göre farklı rakamlar: 70 anket deneyi, GPT-4 tahmin–gerçek etki korelasyonu r≈0.85 (bir sayfa); sonraki listede etkiler sistematik **fazla büyük**; ana arşivde etkileri ~0.56 ile küçültme önerisi (ikincil kaynak). | Etki yönü/büyüklüğü testi; kalibrasyon (etki küçültme) fikri. | "Yön iyi, büyüklük şişkin; ikisini ayrı raporluyoruz." | [DOĞRULANAMADI] (yalnız arama özetleri; sürümler çelişiyor) |
| 11 | Brand, Israeli, Ngwe, *Using GPT for Market Research* (HBS WP 23-062) | 2023 | GPT-3 yanıtlarıyla WTP'de gerçekçi sonuçlar (azalan marjinal fayda, durum bağımlılığı) bildirilmiş. Büyüklükleri okumadım. | Fiyat/paket playbook'u için ilk referans. | – | [DOĞRULANAMADI] (yalnız arama özeti) |
| 12 | Toubia vd., *Twin-2K-500* (arXiv 2505.17479; Marketing Science 44(6), 1446–1455) | 2025 | 2 058 kişi, 500+ soru, 19 deney açık veri (HuggingFace, CC BY 4.0 – ikincil kaynak). İkincil: heterojenliği yakalıyor, bireysel tahmin zayıf, "mavi kayma". | Açık gerçek-insan–twin veri seti; **doğrulama için aday veri**. | – | [DOĞRULANAMADI] (yalnız arama özeti; erişimi kendi gözünle doğrula) |
| 13 | Tigre & Souto, *When Can You Trust Your Synthetic Users?* (arXiv 2609.13148; sayfada Haziran 2026 yazıyor) | 2026 | Toplam skorlar varyans sıkışması, işaret terslenmesi, alt grup hatasını gizleyebilir; kovaryat/kavram kayması ayrımı; AIPW ile küçük insan örneği; ANES'te yanlılığı ~%93–100 azalttığı bildiriliyor. | `ppi_mean`/`doubly_robust_mean` ile doğrudan akraba "güven/düzelt/bırak" çerçevesi. | – | [KISMEN] (özet okundu; **arXiv no/tarih tutarsızlığı** var, preprint; hakemli değil) |

## B. Çelişkili/uyumsuz bulgular yan yana
| Konu | Olumlu | Olumsuz/uyarı |
|---|---|---|
| Ortalamalar | Persona koşullama alt grup örüntülerine yaklaşıyor (#1); mülakat tabanlı ajanlar insan tutarlılığının ~%86'sı (#3) | Aynı ortalama uyumu varyansı ve katsayıları gizleyebilir (#9, #13); gruplar düzleşir (#5) |
| Dağılım biçimi | SSR gerçekçi Likert dağılımı (#8) | Doğrudan puan istemi gerçekçi değil (#8), istem sözcüğüne duyarlı (#9) |
| Etki tahmini | Etki yönü/korelasyon yüksek (#10) | Büyüklük şişkin (#10) |
| Demografi | Detaylı koşullama işe yarıyor (#1, #3) | Daha zengin persona "mavi kayma" yapabilir (#12, ikincil); bazı gruplar sürekli kaçırılıyor (#4) |
| "Fazla iyi" | – | Bilgelik-kalabalıkta hiper-doğruluk (#6) |
| Zaman | – | Aynı istem 3 ay sonra farklı dağılım (#9): önbellek/model sürümü sabitle |

## C. SAHNEDE İDDİA ETME (yasak liste)
1. "LLM persona gerçek insanın yerini alır." (#5, #9 aksini söylüyor.)
2. Herhangi bir "%X doğruluk" rakamını kendi ölçümün değilse söyleme; #3'teki %86 ve #8'deki %90 **insan test-tekrar güvenilirliğine oranla**, davranış doğruluğu değildir.
3. #10, #11, #12'den bir sayı: doğrulanamadı.
4. "PPI/AIPW yanlılığı %93–100 azaltır" (#13): preprint, özet düzeyi, tutarsız arXiv numarası.
5. Türkiye/non-WEIRD için doğruluk iddiası: bu dosyada Türkiye'ye özel kaynak **yok**.
6. "Generative Agents davranışı doğru tahmin eder." (#2 inandırıcılığı ölçtü.)
7. Mock çıktılarından çıkan hiçbir sonuç (bkz. `docs/01_DRY_RUN.md`).
8. Mod çöküşü eşiği (0.6) için kaynak yok; sezgiseldir.

## D. Eksik konular (bu fazda yapılmadı)
- **Mod çöküşü / çeşitlilik kaybı** için ayrı birincil kaynak aranmadı (RLHF homojenleşmesi vb.); #5 ve #9 dolaylı.
- **Sosyal simülasyon çerçeveleri** (ABM+LLM anketleri, AgentSociety, S³ vb.) okunmadı.
- **SSR'yi uygulamak:** gömme tabanlı dağılım elde etme `decision_models`'a eklenmedi; opsiyonel iş (embedding sağlayıcısı gerekir).
- Hiçbir makalenin tam metni okunmadı; sunuma konacak her kaynak için kullanılacak satırlar sunumdan önce tam metinden doğrulanmalı.
