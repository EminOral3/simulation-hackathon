# 04_PITCH_AND_QA — 5 dk, 6 slayt (jüri: sektör + akademi)

`[X]` = case gelince doldur. **Hiçbir sayı kanıtsız slayta girmez.** Her sayı: aralık + etiket (veri / vekil / varsayım).

## Süre bütçesi
Acı 40 sn · Yöntem 50 sn · Kanıt 70 sn · Demo 70 sn · ROI 40 sn · Sınırlar 30 sn = 300 sn. (Rezerv yok: provayı 4:30'a göre yap.)

## Vuruş cümlesi (şablon)
> "[Karar verici] için [karar]'ı, [yöntem] ile simüle ettik; [metrik]'i [aralık] doğrulukla tahmin ediyor, [sınırlar] içinde güvenmeniz gereken yeri de **biz** söylüyoruz."

Alternatif açılış: "Yapay zekâ eklemek kolaydı; biz önce gerçekten gerekip gerekmediğini ölçtük."

## Slaytlar
**1. Acı (40 sn)** — Karar verici kim, hangi karar, yanlış verilirse maliyeti ne. Tek rakam [X] (etiketli). Bir cümle: bugünkü yöntem neden yetmiyor.

**2. Yöntem (50 sn)** — Tek diyagram: veri → model(ler) → karar çıktısı. "LLM/ajan kapısı" kararımız ve 2 cümle gerekçe: "LLM'siz baz çözüm [X]; LLM şu ek değeri katıyor: [ölçülmüş fark] / katmıyor, o yüzden kullanmadık." Twist'i burada göster.

**3. Kanıt (70 sn)** — Tek ana grafik: gerçek/vekil vs. simüle dağılım + güven bandı. Altında 3 satır: hata (JSD/MAE) aralığı, yön uyumu, insan tavanı (split-half) ile kıyas. "Neyi geri tutarak (hold-out) test ettik" bir cümle.

**4. Demo (70 sn)** — Tek yol: kaydırıcıyı oynat (what-if) → grafik ve KPI değişir → güvenme rozeti. Mock/canlı düğmesi hazır; kayıt yedekte. Cümle: "Parametre değiştirince şu karar değişiyor."

**5. ROI (40 sn)** — Düşük/baz/yüksek, tornado'nun en uzun çubuğu, P(net>0). "Varsayımlar etiketli ve değiştirilebilir."

**6. Sınırlar (30 sn)** — Neyi iddia etmiyoruz (en az 3 madde), hangi veriyle ne zaman yeniden kalibre edilir, sonraki adım. Dürüstlük bizi ayıran şey.

## 12 zor jüri sorusu ve 20 sn cevaplar
Cevaplar şablondur; `[X]` yerine **gerçek** sonucu koy, yoksa cevabı "bunu ölçmedik" diye ver.

1. **Gerçekçilik: Sentetik davranış gerçeğe ne kadar benziyor?**
   "[Hold-out] üzerinde JSD [a–b], yön uyumu [c]. İnsan tavanı (split-half) [d]; sentetik bunu aşamaz, ona ne kadar yaklaştığımızı gösteriyoruz. Aralığı slaytta, dışındaki durumlar için güvenme rozetimiz uyarıyor."

2. **Önyargı: LLM Batı-merkezli/WEIRD; Türkiye'ye uyar mı?**
   "Bu risk gerçek. Bu yüzden LLM'i [çekirdek değil / marjinalleri yerel veriyle ağırlıklandırarak (IPF)] kullandık ve alt grup tablosunda hata dağılımını gösteriyoruz. Yerel veride hata [X] ise kullanım dışı bırakırız."

3. **Veri gizliliği: Müşteri verisi LLM'e gidiyor mu?**
   "Gitmiyor: bireysel kayıt yerine sentetik/marjinal personalar gönderiyoruz. İstenirse tamamen yerel modelle veya LLM'siz çekirdekle çalışır; mimari değiştirilebilir sağlayıcılıdır."

4. **Döngüsel doğrulama: LLM ile üretip LLM ile mi doğruladınız?**
   "Hayır. Doğrulama hold-out gerçek/vekil veriye karşı; LLM yargıç kullanmadık. Gerçek veri azsa PPI ile az sayıda gerçek etiketle sentetik yanlılığı düzeltiyoruz."

5. **Maliyet: Kaç çağrı, kaç TL?**
   "Persona × örnek × senaryo = [N] çağrı, disk cache sayesinde tekrar çalıştırmada sıfır. Ölçülen maliyet: [X]. LLM'siz çekirdek ise saniyeler ve ücretsiz."

6. **Ölçek: 1 milyon müşteriye ölçeklenir mi?**
   "Dağılım-öncelikli yaklaşım: segmentleri simüle edip ağırlıklarız, 1 milyon birey çağırmayız. DES/MC kısmı doğrusal ölçeklenir. [Ölçülen: X persona/sn.] Daha fazlasını ölçmedik."

7. **Talp'ten fark: Zaten böyle bir ürün var.**
   "Talp persona simülasyonuna odaklı [halka açık dili doğrulayıp söyle]. Biz bugün tek bir karar için kanıtlı, belirsizlik bantlı bir çözüm gösteriyoruz; yöntemi probleme göre seçiyoruz — gerektiğinde LLM'siz."

8. **Neden LLM kullandınız?** *(LLM kullandıysak)*
   "Çünkü [tablo verisi yoktu / serbest metin vardı]. LLM'siz baz çözümümüz [X] hata verdi; LLM'li [Y]. Farkı [aralık] ile ölçtük."

9. **Neden LLM kullanmadınız?** *(kullanmadıysak)*
   "Problem kapasite/kuyruk yapısında; kurallar belli, doğrulanabilirlik kritik. LLM'siz çözüm [X] doğrulukta; LLM'in ekleyeceği değer ölçülebilir değil, eklemek yalnız belirsizlik ve maliyet getirirdi."

10. **Mod çöküşü / hepsi aynı cevabı vermez mi?**
    "Evet, bilinen bir risk. Çöküş indeksini ölçüyoruz; [değer]. Eşik aşılırsa arayüz rozet gösteriyor. Not: eşiğimiz sezgiseldir, [bu veri] ile kalibre ettik / etmedik."

11. **Varsayımlarınız çok; ROI'ye neden güveneyim?**
    "Güvenmeyin, bakın: her parametre etiketli ve aralıklı; tornado, kararı en çok neyin değiştirdiğini gösteriyor: [parametre]. Kararı o parametreyi ölçerek netleştirmeyi öneriyoruz."

12. **Bu gerçek insan davranışının yerine geçiyor mu?**
    "Hayır. Karar öncesi eleme ve hipotez üretme aracı; gerçek araştırmayı ve A/B'yi ucuz ve hızlı hâle getirir, onların yerine geçmez. Slayt 6'da bunu açıkça söylüyoruz."

## Sunum günü kontrol
- Demo kaydı + mock mod: T-30 dk. Yedek PDF slaytlar. Tek kişi konuşur (süre), diğerleri soru dağıtır: teknik→Tolga, istatistik→Emin, iş/ROI→Gürkan.
- Cevaba sayı koyamıyorsan "ölçmedik" de; uydurma yok.
