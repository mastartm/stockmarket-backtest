# Strateji Geçmiş Testi

"Şu tarihte şu hisseyi alsaydım ne olurdu?" sorusunu cevaplar. Al-ve-tut ile SMA 50/200 stratejisini karşılaştırır.

**Eğitim amaçlıdır, yatırım tavsiyesi değildir.**

## Klasör yapısı
- `docs/` — GitHub Pages'in yayınladığı site (`index.html` + `data/results.json`)
- `scripts/build_data.py` — sonuçları hesaplayıp `docs/data/results.json` dosyasına yazar
- `.github/workflows/update-data.yml` — scripti her iş günü otomatik çalıştırır
- `backtest.py` — terminalden tek hisse deneme scripti (siteden bağımsız, `matplotlib` ister)

## Yerelde deneme
```bash
pip install -r requirements.txt
python scripts/build_data.py
cd docs
python -m http.server 8000
```
Sonra tarayıcıda `http://localhost:8000` aç. (`index.html` dosyasına çift tıklamak çalışmaz, veri dosyası sunucu ister.)

## GitHub'da yayınlama
1. GitHub'da **public** yeni bir repo aç (örn. `strateji-gecmis-testi`). Pages ücretsiz planda sadece public repoda çalışır.
2. Bu klasörde:
   ```bash
   git init
   git add .
   git commit -m "İlk sürüm"
   git branch -M main
   git remote add origin https://github.com/KULLANICI_ADIN/strateji-gecmis-testi.git
   git push -u origin main
   ```
3. Repo → **Settings → Pages** → Source: `Deploy from a branch`, Branch: `main`, klasör: `/docs` → Save.
4. Birkaç dakika sonra site `https://KULLANICI_ADIN.github.io/strateji-gecmis-testi/` adresinde açılır.
5. Repo → **Actions** sekmesinde "Veriyi güncelle" iş akışını bir kez **Run workflow** ile çalıştırıp dene. Sonra her iş günü kendiliğinden çalışır.

GitHub, 60 gün boyunca hareketsiz kalan repolarda zamanlanmış işleri durdurabilir. Veri güncellenmeyi bırakırsa Actions sekmesinden elle çalıştırman yeter.

## Hisse listesini değiştirme
`scripts/build_data.py` içindeki `TICKERS` sözlüğüne sembol ekle/çıkar.

## Veri notu
Fiyatlar Yahoo Finance'ten `yfinance` ile çekilir (resmi API değil). Sitede ham fiyat yayınlanmaz, sadece hesaplanmış portföy eğrisi ve istatistikler yayınlanır.
