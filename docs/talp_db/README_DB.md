# Talp Hackathon: Proje Veritabanı (kod yazmadan önce okunur)

## Klasörler
```
docs/theory/01_THEORY_AND_DESIGN.md   mimari, persona, metrik, doğrulama, deney planı
docs/theory/02_LITERATURE.md          4 makale → tasarım kararları D1-D7
docs/crises/CRISIS_PLAYBOOK.md        kriz okuma prosedürü, kalibrasyon çıpaları, veri kaynakları
data/theory/population_priors.json    grup büyüklükleri, bakiye bantları, SHED çıpaları, persona sayısı
data/theory/metric_spec.json          status kelimeleri, G1-G3b formülleri, varsayım parametreleri
data/crises/crisis_kb.json            14 kriz arketipi, takvim bağlamı, akıl kontrolü sınırları
data/crises/decision_menu.json        menü (dashboard etiketleriyle), maliyetler, kurallar
data/crises/announcements.json        hafta hafta duyuru günlüğü (bilinen migration hazır)
```

## Kodun uyacağı kurallar
1. Kaynak sırası: dossier ve challenge > bu klasör > tahmin. Çelişki varsa önce belirt.
2. `crisis_kb.json` içindeki calibration_anchors ve gerçek vaka sonuçları ASLA persona prompt'una girmez; sadece sanity_check ve dünya akışı şablonları için.
3. Persona prompt'una giren banka mesajı, kilitlenen kararın mesajıyla kelimesi kelimesine aynı olmalı ve yalnızca hedef gruba, yalnızca etkili haftadan itibaren girmeli.
4. VARSAYIM etiketli tüm parametreler config'te açık olmalı (duyarlılık analizi için).
5. API anahtarı yalnız `TALP_KEY` ortam değişkeninde; ZIP'e girmez.

## Tolga'nın Claude'una ilk prompt
```
ÖNCE OKU: README_DB.md, docs/theory/01_THEORY_AND_DESIGN.md, data/theory/*.json, data/crises/decision_menu.json.
Kod yazmadan önce 8 satırda: anladığın mimari, persona sayısı ve grupları, 3 metrik formülü, check.py'nin zorunlu kıldığı 5 şey, çelişki/eksik gördüğün yerler.
Sonra mock modda (LLM yerine sahte cevap üreten fonksiyon) uçtan uca 1 koşu üret ve python3 check.py ile doğrula. Gerçek API'ye geçiş tek bayrakla olsun (--live).
SINIR: yeni bağımlılık sadece google-genai; dosya listesi ve tam dosyalar ver; DEVAM_NOTU.md güncelle.
```
