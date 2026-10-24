# Teorik Altyapı ve Tasarım İlkeleri (Cobalt Bank)

Kaynaklar: dossier `10-cobalt-bank.md`, challenge `02-challenge.md`, `check.py`, `02_LITERATURE.md`.
Etiketler: FACT (dossier), VARSAYIM (bizim), HİPOTEZ (test edilecek).

## 1. Problem ve değerlendirme
- Jüri simülasyon sonucunu değil şunları puanlıyor: akıl yürütme, kendi fikrimiz, yaklaşımları karşılaştırma ve öğrenme, çalışan örnek, simülasyonun söyleyemedikleri ve sonraki adım. Jüri bir personaya canlı soru soracak.
- LLM kapısı: kurallar gereği persona davranışı LLM'den gelmek zorunda. LLM'siz baz olarak basit bir kural modeli (faiz farkı ve kesinti şiddetinden ayrılma olasılığı) kurup karşılaştırırız; "LLM ne ekledi?" sorusunun cevabı bu.

## 2. Mimari (tek döngü)
```
personas (sabit, 5 koşuda aynı)  ──►  hafta t=1..10
  her persona için tek LLM çağrısı:
    [persona hikâyesi + sabit alanlar]
    [hafıza özeti: önceki haftaların kısa özeti + kendi önceki durumu]
    [bu hafta gördükleri: banka mesajı (yalnız hedefteyse, kelimesi kelimesine),
     kriz duyurusu (maruziyete göre), arkadaş/sosyal medya akışı (önceki haftanın paylaşımlarından),
     rakip reklamı, destek bekleme süresi]
    → JSON: actions[], review_stars?, cfpb?, social_post?, memory_note, Status, Money
  dünya güncellemesi: paylaşımlar → sonraki haftanın sosyal akışı; şikâyet hacmi → destek bekleme süresi
check-in (8 soru) : hafta 0 ve 11, yalnız plan_1 ve nodecision_1
```
- Bir hafta içindeki çağrılar paralel, haftalar sıralı. Model `gemini-3.5-flash-lite`, temperature > 0, her çağrıya seed.
- Kayıt formatı `check.py` ile birebir: run.json, personas.jsonl, calls.jsonl, weekly.jsonl, metrics.json, probe.jsonl.

## 3. Persona tasarımı
- Gruplar (dossier adlarıyla aynen): everyday customers, paycheck customers, savers with large balances, small business owners with a Cobalt card reader, students.
- Sayı: 64 önerisi (16/16/16/8/8). Gerekçe: G1 toleransı %2, G2 toleransı %3. 24 personada tek bir personanın ağırlığı bu toleransları aşar (bkz. population_priors.json).
- Biçim: sabit alanlar + 4-6 cümlelik birinci tekil şahıs hikâye (Argyle 2022, Park 2024). Hassas özellik (ırk, din, sağlık, siyaset) kullanılmaz.
- Seçilen özellikler ve nedenleri:
  - Para ve ilişki: balance band, paycheck deposited into Cobalt, payday, lives paycheck to paycheck, savings, Cobalt is main or second bank, how many banks they use, moves money for a better rate, knows the FDIC insurance limit → G1 ve G2'yi doğrudan sürer.
  - Risk ve güven: has been a victim of card fraud or phishing, how they react to a text message from a bank, financial literacy, trust in institutions, believes rumors or checks them → oltalama ve söylenti krizleri.
  - Tepki: patience when waiting, how fast they get angry, tendency to forgive, complaint history, writes reviews, embarrassed to complain → G3.
  - Bilgi ağı: where they hear news, social media use, leads or follows opinions, size of circle → krizin yayılması.
  - Kullanılmayanlar (I. bölüm: burç, renk, ayakkabı numarası vb.): karara etkisi yok; sadece 1-2 tanesi hikâyeye "insan dokusu" için girebilir. Ayrıca "card design", "dark mode" yalnız A14 uygulama krizi gelirse anlamlı.

## 4. Metrikler (formüller: data/theory/metric_spec.json)
- Hepsi hafta 0'a göre oran: mutlak kalibrasyon hatası sadeleşir.
- G1 aktif müşteri, G2 mevduat (para hareketi kesirleri VARSAYIM), G3 puan, G3b CFPB (taban orana göre ölçekleme: "anchor-and-ratio").
- Belirsizlik: 2 seed ortalaması + personalar üzerinden tabakalı bootstrap %95 CI.

## 5. Kalite ve doğrulama (gerçek veri yok → iç tutarlılık + dış çıpa)
1. Seed tutarlılığı: plan_1 vs plan_2 haftalık status uyum oranı (bizim "tavanımız", Park 2024 mantığı).
2. Mod çöküşü: grup içi status dağılımının normalize entropisi ve en sık cevabın payı (Santurkar 2023).
3. Persona ayrışma S ve tutarlılık R: 8 check-in sorusu üzerinde (Costa & Vicente 2026 tanımları).
4. Söylenen ve yapılan arasındaki fark: başlangıçtaki "kalma niyeti" (2a, 2b) ile 10. haftadaki gerçek status arasındaki uyum. Twist adayı.
5. Dış çıpa: kararsız krizsiz haftalar BAU'yu üretmeli (aylık ~1.800 şikâyet, 120 CFPB, puan 4,6). Kayıplar TSB üst sınırının (yılda ~%1,5 hesap kapanışı) çok üstündeyse önce prompt'u kontrol et.
6. Kural tabanlı baz model ile LLM sonuçlarının karşılaştırması.

## 6. Deneyler (jüri "neleri denediniz" diye soracak)
| Deney | Ne değişir | Ne ölçülür |
|---|---|---|
| E0 | nodecision, 2 seed | BAU taban çizgisi, seed tutarlılığı |
| E1 | K1 = 6. hafta erken maaş + offline limit + ek destek | G1, G3 farkı |
| E2 | K1 alternatifi: 5. hafta (daha erken iletişim) | zamanlama etkisi |
| E3 | K2 = 7. hafta faiz +0,5 (10 Ocak'ta biter) vs 5. hafta faiz | G2 farkı: ölçüm tarihine hizalama hipotezi |
| E4 | Mesaj varyantı: kesin bitiş saati vs "beklenen + güncelleme sözü" | G3, güven sorusu |
| E5 | surprises kapalı | krizlerin katkısı |
Her deney için: kaç kez koşuldu, ortalama ve aralık. Sonuçlar TEAM_DOC'ta tablo halinde.

## 7. Bilinen sınırlar (CLIENT_MEMO "söyleyemedikleri")
- Gerçek Cobalt müşteri verisi yok; dağılımlar VARSAYIM + SHED çıpaları.
- LLM'ler modal cevaba yığılır ve aşırı tepki verebilir.
- Para hareketi kesirleri ve puan katsayısı varsayım; duyarlılık aralığıyla verilir.
- Sonraki adım: 200-300 gerçek müşteriye aynı check-in sorularını sorup sentetik paneli PPI ile düzeltmek (Angelopoulos 2023).
