# Sürprizsiz 32 plan — canlı deney

Bu klasör **930cb3a** kod sürümünde, **gemini-3.5-flash-lite** ile çalıştırılan 32 farklı iki kararlı planın ve bir kararsız kontrol koşusunun sonuçlarını içerir.

- [Sonuç raporu ve bütün kararlar](report.md)
- [Sonuç tablosu (CSV)](summary.csv)
- [Sonuç tablosu (JSON)](summary.json)
- [Koşu bilgileri ve kontrol özeti](manifest.json)
- [32 planın tam mesajları, aksiyonları ve hedefleri](decisions/)

## Deney koşulları

75 persona, 10 hafta, seed=1. Tüm sürpriz duyurular kapalıdır; bilinen 6. hafta sistem geçişi korunur. Bu seed'de geçiş zamanında bitmiştir. Önceki surrogate taramasının sonuçları bu klasöre dahil edilmemiştir.

32 plan: ilk karar haftası (5/6) × ek destek (+50/+150) × erken maaş (var/yok) × faiz türü (tüm uygun bakiyeler/yeni para) × faiz seviyesi (+0.25/+0.5 puan). İlk kararda kart limiti her planda $250; ikinci karar her planda 7. haftada. Hedef everyone; kanallar push/email/in_app.

29/32 plan bu tek seed'de bütün hedefleri ve bütçeyi sağladı. Kararsız kontrol de hedefleri sağladı. Bu kontrol, final teslimin tam iki karar şartının yerine geçmez. Sonuçlar başka seed veya gecikmeli geçiş için doğrulanmış değildir.

33 koşuda toplam 24.750 benzersiz persona-hafta kaydı kontrol edildi; başarısız parse veya eksik hafta yok. Bu yapısal kontrol, gerçek dünyada tahmin doğruluğunun kanıtı değildir.

## Dosyaların anlamı

summary.csv/json içindeki goal değerleri canlı koşu sonuçlarıdır. delta_goal alanları kontrol koşusundan farktır (yüzde puan/puan/şikâyet). score mevcut optimize utility ve maliyet cezasıdır; hedef marjı doygunluğa ulaştığından tek bir küresel optimum iddiası taşımaz. valid alanı kayıt bütünlüğü ve parse kontrollerini ifade eder.

folder alanı orijinal yerel koşu klasörünün adıdır. Tam prompt/response, haftalık kayıtlar ve cache yerelde saklanmaktadır; bu commit ekip incelemesi için raporları ve karar dosyalarını taşır. Final teslim paketi değildir.

Aynı anda başlayan özdeş model+seed+prompt+schema istekleri deney başlatıcısında birleştirildi; mevcut simülasyon kodu ve goal formülleri değiştirilmedi. Anahtar veya .env dosyası bu sonuç paketine dahil değildir.

Repoya eklenme anında master daha yeni commitlere ilerlemiştir. Bu sonuçlar **930cb3a** sürümüne aittir; sonradan değişen kodla üretilmiş gibi yorumlanmamalıdır.
