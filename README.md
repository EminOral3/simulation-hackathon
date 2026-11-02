# Cobalt Bank — Müşteri Davranışı Simülasyonu

TALP Simulation Hackathon için üç kişilik ekibimizle geliştirdiğimiz proje. Cobalt Bank senaryosunda, bir bankacılık sistemi geçişi ve beklenmedik krizler sırasında müşterilerin nasıl davranabileceğini simüle ettik.

Amacımız, bankanın alacağı kararların müşteri kaybı, mevduat ve müşteri deneyimi üzerindeki olası etkilerini karşılaştırmaktı.

## Ne yaptık?

- Farklı müşteri gruplarını temsil eden 75 sentetik persona oluşturduk.
- Müşterilerin haberlerden, banka mesajlarından ve birbirlerinden etkilenmesini 10 haftalık bir simülasyonda modelledik.
- İletişim, destek kapasitesi ve finansal teşvikler içeren kararları, hiçbir müdahale yapılmayan senaryoyla karşılaştırdık.
- Deney sonuçlarını analiz edip yönetim kurulu raporu, sunum ve persona davranışlarını inceleyen bir web demosu hazırladık.

Python tabanlı projede LLM destekli ajanlar, davranış modelleme, kuyruk hesaplamaları ve istatistiksel analiz birlikte kullanılıyor.

## Lokalde çalıştırma

Python 3.11 veya üzeri ile, proje klasöründe:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r code_kit/requirements.txt pydantic
```

API anahtarı gerektirmeyen kısa bir mock simülasyonu:

```powershell
.\.venv\Scripts\python.exe -m code_kit.cobalt.run --type plan --seed 1 --weeks 3 --personas 20 --no-probe
```

Sonuçlar `code_kit/cobalt/outputs/runs/` altında oluşur. Mock modu akışı denemek içindir; gerçek LLM deneylerinin sonuçlarını üretmez. Canlı Gemini koşuları için `--live`, uygun API erişimi ve `TALP_KEY` veya `VERTEX_AI_KEY` gerekir. Anahtarları Git'e eklemeyin.

Web demosu iki koşunun kayıtlarını karşılaştırır:

```powershell
.\.venv\Scripts\python.exe tools/demo_ui.py --run "KOŞU_KLASÖRÜ" --other "KARŞILAŞTIRMA_KLASÖRÜ" --offline
```

Arayüz: <http://localhost:8765>. Koşu klasörlerini kendi ürettiğiniz kayıtlarla değiştirin; demo varsayılanındaki teslim kayıtları bu repoya dahil değildir.

## Dosyalar

- [`code_kit/cobalt/`](code_kit/cobalt/): Simülasyon motoru, personalar, deneyler ve metrikler.
- [`tools/`](tools/): Web demosu ve persona soru-cevap araçları.
- [`docs/submission/TEAM_DOC.md`](docs/submission/TEAM_DOC.md): Yöntem ve deneylerin açıklaması.
- [`docs/submission/CLIENT_MEMO.md`](docs/submission/CLIENT_MEMO.md): Kararlar ve sonuçların kısa raporu.
- [`code_kit/README.md`](code_kit/README.md): Genel simülasyon modüllerinin teknik notları.

## Ekip

Emin Oral · Gürkan Türker · Süleyman Tolga Acar

Bu repo, [ortak proje deposunun](https://github.com/SuleymanTolgaAcar/simulation-hackathon) commit geçmişini koruyan bir kopyasıdır.

> Personalar sentetiktir; gerçek Cobalt müşteri verisi kullanılmadı. Sonuçlar model ve varsayımlara bağlıdır, gerçek müşteri davranışının doğrulanmış tahminleri değildir.
