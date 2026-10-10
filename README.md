# Stockmarket Backtest — "Alsaydım ne olurdu?"

**Canlı site:** https://mastartm.github.io/stockmarket-backtest/

> **⚠ Eğitim amaçlıdır, yatırım tavsiyesi değildir.** Geçmiş performans geleceği garanti etmez. Gerçek komisyon, vergi ve kur farkı sonuçları değiştirir.

## Amaç
Bir ABD hissesine veya ETF'ine geçmişte yatırım yapsaydın bugün ne kadar paran olurdu? Bu site bu soruyu cevaplar ve iki yöntemi yan yana koyar:

- **Al-ve-tut:** Başlangıçta al, dönem sonuna kadar elinde tut.
- **SMA 50/200:** 50 günlük ortalama fiyat 200 günlük ortalamanın üstündeyse hissede kal, altındaysa sat ve nakitte bekle.

Amaç gerçek para riske etmeden stratejileri denemek ve "karmaşık strateji her zaman basit al-ve-tuttan iyidir" gibi varsayımları geçmiş veriyle sınamaktır. Küçük sermayeyle ABD hisselerine başlamak isteyen biri için öğrenme aracı olarak yapıldı.

## Nasıl kullanılır
1. **Hisse / ETF** seç (39 seçenek: SPY, QQQ, AAPL, TSLA, NVDA vb.).
2. **Dönem** seç: yıl başından beri, son 1/3/5/10 yıl veya en uzun dönem.
3. **Başlangıç parasını** yaz (varsayılan 1.000 USD).
4. Sonuçları oku:
   - **Kartlar:** Dönem sonundaki değer, toplam getiri, yıllık getiri, en büyük düşüş ve alım/satım sayısı.
   - **Grafik:** İki stratejinin portföy değeri zaman içinde nasıl değişti.
5. Sağ üstteki düğmeyle açık/koyu temayı değiştirebilirsin.

### Sonuçlar nasıl okunur
- **En büyük düşüş:** Portföyün tepe noktasından dibe kadar yaşadığı en büyük kayıp. Elinde tutarsan bir ara paranın bu kadarı silinmiş görünür.
- **Yıllık getiri:** Bir yıldan kısa dönemlerde gösterilmez (`—`), çünkü yıllığa çevirmek yanıltıcı olur.
- **SMA genelde geç kalır.** Ortalamalar geçmişe baktığı için sinyal geç gelir. Güçlü yükseliş dönemlerinde SMA çoğunlukla al-ve-tuttan kötü çıkar.
- Her sonuç **tek bir dönemin, tek bir denemesidir.** Başka dönemde sonuç farklı olabilir.

## Varsayımlar ve sınırlar
- Her alım ve satımda **%0,1 maliyet** düşülür (komisyon + spread + kur farkı varsayımı). Gerçek broker maliyetin farklıysa sonuç değişir.
- Sinyal bir sonraki gün uygulanır (geleceğe bakma hatası yok).
- Fiyatlar temettü ve bölünmeler için düzeltilmiştir.
- Vergi, TL/USD kuru, kaldıraç ve emir gecikmeleri hesaba **katılmaz**.
- Duygusal kararlar (panik satışı, FOMO) ölçülmez; gerçek hayatta stratejiye uymak kâğıt üstünden zordur.

## Veri ve güncelleme
- Fiyatlar Yahoo Finance'ten `yfinance` ile çekilir (resmi bir API değildir).
- Veri **her iş günü** otomatik güncellenir (GitHub Actions). Sayfanın altındaki "Son güncelleme" tarihinden kontrol edebilirsin.
- Sitede ham fiyat yayınlanmaz, sadece hesaplanmış portföy eğrisi (haftalık örneklenmiş) ve istatistikler gösterilir.
- Kısa geçmişi olan hisselerde (örn. PLTR, UBER) 10 yıllık dönem yoktur.

## Proje yapısı
- `docs/` — Site (`index.html` + `data/results.json`)
- `scripts/build_data.py` — Backtest'i hesaplayıp `docs/data/results.json` dosyasını üretir
- `.github/workflows/update-data.yml` — Scripti her iş günü otomatik çalıştırır
- `backtest.py` — Terminalden tek hisse deneme scripti (siteden bağımsız, `matplotlib` ister). Bu script dönem öncesi veriyi SMA ısınması için kullanmaz; kısa dönemlerde sitedeki sonuçla farklı çıkabilir.

## Geliştirme notları
- **Hisse listesini değiştirmek:** `scripts/build_data.py` içindeki `TICKERS` sözlüğüne sembol ekle/çıkar.
- **Yerelde çalıştırmak:**
  ```bash
  pip install -r requirements.txt
  python scripts/build_data.py
  cd docs
  python -m http.server 8000
  ```
  Sonra tarayıcıda `http://localhost:8000` aç. (`index.html` dosyasına çift tıklamak çalışmaz, veri dosyası sunucu ister.)
- **Güncelleme durursa:** GitHub, 60 gün hareketsiz kalan repolarda zamanlanmış işleri durdurabilir. Repo → Actions → "Veriyi güncelle" → Run workflow ile elle başlat.
