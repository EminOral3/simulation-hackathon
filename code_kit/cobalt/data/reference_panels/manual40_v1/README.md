# manual40 — ayrı referans persona deneyi

**Durum:** Kullanıma hazır veri/yükleyici entegrasyonu; yeni simülasyon veya API koşusu yapılmadı. 40 kişi, beş dossier grubuna sekizer kişi. IDs M01–M40.

Bu panel Codex tarafından hazırlanan taslaktır; gerçek müşteri verisi veya insan tarafından doğrulanmış ground truth değildir. Orijinal hikâyeler değişmeden korunur. İnsan ekip incelemesi beklenmektedir.

## Güvenli seçim

Mevcut CLI flag'i kullanılır:

```text
--persona-set manual40
```

Flag verilmediğinde mevcut varsayılan latest ve 75 kişilik normal set seçimi aynen çalışır. manual40 klasörü data/personas/ altında değildir; bu nedenle otomatik latest seçimi onu hiçbir zaman almaz.

API veya simülasyon başlatmadan paneli incelemek için repo kökünden:

```powershell
python -m code_kit.cobalt.personas show --set personas.persona_set=manual40 --id M01
```

İleride açıkça koşu istenirse ayrı parametre overlay'i kullanılabilir: code_kit/cobalt/params/personas/manual40.toml. Bu overlay paneli seçer ve çıktı yolunu outputs/manual40 olarak ayırır. Mevcut run CLI'sindeki --persona-set manual40 seçeneği de tek başına çalışır, fakat tek başına çıktı yolunu değiştirmez.

code_kit/cobalt/params/experiments/manual40_compare.toml dört kol tanımlar: mevcut 75 kişiyle plan/kararsız ve referans 40 kişiyle plan/kararsız. Tanım otomatik çalışmaz; iki seed ve bilinen geçiş açık/sürprizler kapalıdır. Mevcut kilitlenen kararları değiştirmez; karar dosyası ayrıca seçilmelidir.

## Dosyalar

- source.json: daha önce hazırlanan JSON'un birebir kopyası.
- personas.jsonl: mevcut motorun tükettiği 40 kayıt.
- network.json: sadece bu M kimlikleri arasında dondurulmuş ayrı ağ.
- quality.json: kontrolün kapsamı ve eksikleri.
- Her runtime kaydında reference_source orijinal profilin kopyasıdır.
- manual40.py: hikâye üretmeden ve API çağırmadan runtime alanları ekleyen uyarlama fonksiyonu.

## Uyarlama varsayımları

- Ağırlık: grup müşteri sayısı / 8. Aktif ağırlık mevcut population_priors içindeki active_share ile çarpılır. Toplam müşteri ağırlığı 2.1M; aktif ağırlık mevcut priors nedeniyle 999492 (yaklaşık 1M). Bunlar bu panelin temsili olduğunun kanıtı değildir.
- Mevduat metriği mevcut motorun bakiye bandı ve grup ölçeklemesini kullanır. source balance_usd doğrudan bankanın toplam mevduatına eşitlenmez.
- opinion_role, rumor_style ve voice_propensity yazımları mevcut tüketicilerin beklediği enum/prefix biçimine çevrilir.
- location mevcut state_city_type'tan; sosyal kanallar news_sources'tan türetilir.
- checks_app_daily ve autopays kaynakta yok: main bank için yes/2, second bank için no/0 varsayılır. Alanlar provenance içinde açıkça işaretlidir.
- Maaş günü metni mevcut world.py ile uyumlu biçime çevrilir. Cobalt'a maaş yatmıyorsa başka geliri Cobalt maaşı gibi gösterilmez.
- business alanında tam satış tutarı korunur. Ayrıca mevcut world.py'nin metin tabanlı tanıdığı 120-300/15-60 kategori işareti eklenir; bu işaret kesin satış aralığı iddiası değildir.
- Yeni switch_cost, eksik otomatik ödeme varsayımına ve mevcut kaynak alanlarına dayanır.
- Ağ mevcut network.build ile offline oluşturulur. Normal setin ağına dokunulmaz.
- Başlangıç trust/status ve hafıza mevcut motorun davranışını izler; kaynak JSON'daki bütün dynamic alanlar motor tarafından başlangıç durumu olarak okunmaz.
- design_levels sadece betimleyici karşılaştırma alanlarıdır. 40 kişilik panel faktöriyel DOE değildir; analysis modülündeki grup farklarına nedensel ana etki denmemelidir.

## Karşılaştırmayı yorumlama

40 ve 75 kişilik panelin özellik, bakiye bandı ve ağ dağılımları farklıdır. KPI farkı yalnız hikâye üretim yönteminin etkisi olarak yorumlanamaz. Bu deney bütün panelin alternatifini sınar.

Sadece hikâye yöntemini karşılaştırmak için aynı 40 sabit profilden alternatif anlatılar üretmek ve diğer koşulları eşitlemek gerekir. Bu görevde yeni anlatı üretimi ve yeni API koşusu yapılmadı.

Mevcut surrogate, 75 kişilik dağılımdaki LLM çıktılarından eğitilmiştir. Bu paneldeki tahminleri ayrıca doğrulanmadan güvenilir kabul edilmemeli. Yeni kaynak profilleri mevcut 75 setin dosyalarına kopyalanmamalı.
