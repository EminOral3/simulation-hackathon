# Persona Tasarımı: Teori, Önceki Uygulamalar, Bizim Yöntem

Dosyalar: `data/theory/persona_schema.json` (alanlar), `data/theory/persona_design.json` (75 persona slotu, ağırlıklar), `data/theory/population_priors.json` (grup toplamları).

## 1. Önceki çalışmalar ne yaptı, ne öğrendik
| Çalışma | Persona nasıl kuruldu | Ders | Etiket |
|---|---|---|---|
| Argyle ve ark. 2022, Out of One, Many | Gerçek anket katılımcılarının demografisinden birinci tekil şahıs "backstory" | Doğru koşullama alt grup dağılımlarını taklit edebilir; geçerlilik için 4 kriter | DOĞRULANDI |
| Park ve ark. 2024, 1.000 kişi | 2 saatlik röportaj transkripti | Zengin hikâye, demografik etikete göre daha az gruplar arası yanlılık | KISMEN |
| Santurkar ve ark. 2023 | Demografik yönlendirme ("steering") | Yönlendirme uyumsuzluğu gidermiyor; modeller modal cevaba yığılıyor | DOĞRULANDI |
| Li ve ark. 2025, NeurIPS, "LLM Generated Persona is a Promise with a Catch" | Personaların kendisini LLM'e ürettirme | Persona üretme adımının kendisi sistematik yanlılık katıyor ve sonuçları gerçekten saptırıyor | KISMEN (özet) |
| Hu ve ark. 2025, Population-Aligned Persona Generation | Önce çok persona üret, sonra hedef dağılıma uyacak şekilde yeniden örnekle | Persona seti nüfus dağılımına hizalanmalı; alt gruba göre ayrıca ayarlanmalı | KISMEN (özet) |
| Özkan 2026, Distribution-First Population Simulation (İTÜ, ön baskı) | Gerçek WVS mikroverisine dayanan bağımsız ajanlar | Bağımsız ajanlar modal varsayılana yığılıyor; "verbalized sampling" dağılımı genişletiyor ama aşırıya kaçıyor; anket uyumu ajan davranışına zayıf aktarılıyor (en ucuz varsayılan baskın) | KISMEN (özet) |
| Costa & Vicente 2026 | 100 persona ile anket | Personalar arası ayrışma (S) ve persona içi tutarlılık (R) ölçülebilir | DOĞRULANDI |

## 2. Davranış teorisi: hangi eksenler önemli
- **Exit, Voice, Loyalty (Hirschman, 1970; klasik çerçeve, bugün doğrulanmadı):** Hizmet bozulunca müşteri ya çıkar (exit) ya ses yükseltir (voice); sadakat çıkışı geciktirir. Bizdeki karşılığı: exit = "dormant/left" ve para taşıma (G1, G2); voice = şikâyet, yorum, CFPB (G3); loyalty = "main bank", geçmiş deneyim, affetme.
- **Atalet ve geçiş maliyeti:** J.D. Power'a göre Ocak 2025'e kadarki 12 ayda tüketicilerin yalnızca %9'u banka değiştirmiş; %13'ü önümüzdeki 12 ayda değiştirebileceğini söylüyor. Değiştirmeme nedenleri: zahmet, faydadan emin olmama, geçişte ödeme kaçırma endişesi. → Söylenen (%13) ile yapılan (%9) farkı twist'imizin dış çıpası. [KISMEN: Bankrate'in aktarımı]
- **Finansal kırılganlık:** SHED 2025'e göre yetişkinlerin %63'ü 400 $'lık acil gideri nakitle karşılayabiliyor. [KISMEN]
- **Bilgi ve sosyal etki:** Söylentiye inanma, fikir lideri/takipçi olma; SVB örneği. [KISMEN]

## 3. Bizim yöntem: "Önce dağılım, sonra hikâye" (attribute-first, narrative-second)
1. **Kategorileme (3 katman):**
   - K1 Yapısal tabaka = dossier grubu (5 grup). Kotalar ve ağırlıklar bu katmanda.
   - K2 Davranış eksenleri = grup başına kararı ve krizleri en çok etkileyen 4 ikili eksen (ör. tasarrufçu: faiz avcılığı, FDIC maruziyeti, söylenti tarzı, ses).
   - K3 Anlatı = 4-6 cümlelik hikâye + haftalık hafıza.
2. **Deney tasarımı ile kapsama (bizim fikrimiz, endüstri mühendisliğinden):** 16 kişilik gruplarda 4 eksenin tam faktöriyel tasarımı (2^4), 8 kişilik gruplarda yarım fraksiyon (2^(4-1), I=ABCD, çözünürlük IV). Böylece her sürücü eşit kapsanır ve etkileri ayrıştırılabilir. Rastgele örnekleme ise nadir ama kritik kombinasyonları (FDIC limitinin üstünde, söylentiye inanan tasarrufçu) atlayabilir.
3. **Post-stratifikasyon ile temsil:** Tasarım dengeli ama nüfus dengeli değil; her hücreye "o hücrenin gerçek nüfustaki olasılığı × grup büyüklüğü" ağırlığı verilir. Kapsama tasarımdan, temsil ağırlıktan gelir.
4. **Ağır hücre bölme:** 75 bin müşteriden ağır hücreler klonlanır (aynı eksen seviyeleri, farklı hikâye ve detay). Sonuç: 75 persona, en ağır persona ~74 bin müşteri. Neden: G1 toleransı 20 bin.
5. **Hikâyeyi LLM yazar, alanları kod belirler:** Li 2025'in uyarısı gereği personayı LLM'e "uydurtmayız". Alanlar kod tarafından örneklenir; LLM sadece bu alanlarla çelişmeyen bir anlatı yazar. Ardından bir kontrol çağrısı anlatıyı alanlarla karşılaştırır.

## 4. Prompt şablonları
**Hikâye yazımı (hafta öncesi, 1 kez):**
```
Write a 4-6 sentence first-person backstory for this Cobalt Bank customer. Use ONLY these facts; do not add race, religion, health, politics or immigration status; avoid stereotypes.
FACTS: {fixed fields as key: value}
Include: why you opened Cobalt, one past money or bank experience, what you would do if you could not reach your money for a weekend.
```
**Haftalık karar (her hafta, persona başına 1 çağrı):** sistem kısmı = hikâye + alanlar + hafıza; kullanıcı kısmı = "bu hafta gördüklerin" + "ne yaparsın?" + JSON şeması + son satırlar `Status: ...` ve `Money: ...`.
**Dağılım genişletme (deney, opsiyonel):** Özkan 2026'daki "verbalized sampling" bulgusu nedeniyle ana koşularda kullanmıyoruz; dağılım genişliği varyant olarak denenip aşırı yayılma kontrol edilebilir.

## 5. Kalite kontrolleri (kodlanacak)
- Alan-anlatı tutarlılığı: kontrol çağrısı "anlatı alanlarla çelişiyor mu? evet/hayır + hangi alan".
- Kalıp yargı taraması: hassas kelime listesi + jüriye "hangi özellikleri neden kullandık" tablosu.
- Ayrışma ve tutarlılık: S ve R (check-in soruları), seed uyumu.
- Mod çöküşü: grup içi status entropisi ve en sık cevap payı.
- Söylenen-yapılan: başlangıçtaki 2a/2b cevabı ile 10. hafta status uyumu; dış çıpa J.D. Power %13 niyet / %9 gerçekleşme.

## 6. Jüri sorusu: "Personaları nasıl seçtiniz?" (20 sn)
"Grupları ve sayıları dossier'den, kırılganlık ve dolandırıcılık oranlarını Fed anketinden aldık. Personaları LLM'e uydurtmadık: kararları etkileyen dört davranış eksenini deney tasarımıyla tam kapsadık, sonra her personayı nüfustaki payıyla ağırlıklandırdık. LLM sadece bu sabit özelliklerden hikâye yazdı."
