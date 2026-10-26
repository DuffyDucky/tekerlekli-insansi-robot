# Robot projesi — yapay zekâ oturumları için bağlam

Tekerlekli insansı robot (üniversite projesi, 4 kişilik ekip, MCBÜ Mekatronik MYO). Proje sahibi
Duffy; mekanik, montaj, kablaj ve SolidWorks'te güçlü, yazılımı yapay zekâ yardımıyla yazıyor.

- Türkçe konuş; doğrudan ol, ilk cümlede cevaba başla. Bitmiş işi tablo veya kısa listeyle özetle.
- Projenin güncel durumu: `README.md` (kararlar, CAD sonuçları, açık işler) ve `planlama/proje-plani.md`.
  Varsayımda bulunmadan önce bu dosyaları ve ilgili kaynak notunu oku.
- Yeni rapor → `raporlar/`, dayandığı araştırma → `raporlar/kaynaklar/` (kaynak URL'li; tahminleri
  "tahmini" diye işaretle). Plan değişikliği → `planlama/`. Tasarım → `tasarim/`. Yazılım kodu → `kod/`
  (aşağıdaki "Yazılım" bölümü).
- CAD: `tasarim/cad/robot_cad.py` tek kaynak; STEP, `parca-listesi.csv` ve `tasarim/Robot-Tasarim-Demosu.html`
  bu betikten üretilir, üretilmiş dosyaları elle düzenleme. Demo arayüzü `tasarim/cad/viewer-template.html`.
  Koordinat: Y yukarı, Z ileri (yüz +Z), X sağ-sol, mm. Python 3.12 + CadQuery 2.8; sanal ortam OneDrive
  dışında (`README.md`). Değişiklikten sonra betiği çalıştır, çakışma kontrolünü ve kütle/ağırlık
  merkezi çıktısını raporla.
- Maliyet: `planlama/maliyet.json` tek kaynak (TL fiyat, satıcı, bağlantı, durum, stok; USD kurdan hesaplanır).
  Değişince `tasarim/cad/demo_uret.py` çalıştır (CadQuery gerekmez). Yeni fiyatı satıcı sayfasından doğrula;
  kanıt `raporlar/kaynaklar/05-fiyat-arastirmasi.md`.
- Parça ölçüsü ekliyorsan kaynağını `raporlar/kaynaklar/04-parca-olculeri.md` ile tutarlı tut.
- Bu klasör OneDrive'da; büyük geçici dosyaları ve sanal ortamları buraya koyma.
- Proje genelde DuffyOS oturumundan yönetiliyor (Duffy'nin tercihi, 26 Eylül 2026); dosyalar buraya
  yazılıyor. Bu klasörde doğrudan açılan bir oturumda proje hafızası bu klasördeki dosyalardır.

## Yazılım (`kod/`, dal `yazilim-baslangic`, 26 Ekim 2026)

Tek Python süreci (Pi 5'te 3.11/3.12, Windows'ta 3.13). ROS yok, IK yok; jest = ESP32'de kayıtlı servo
açıları. Durum makinesi BEKLE → DİNLE → DÜŞÜN → (JEST) → KONUŞ → BEKLE. Ayrıntı: `kod/OKU_BENI.md`.

| Dosya | İş |
|---|---|
| `kod/ana.py` | Ayarları okur, bileşenleri kurar (`bilesenleri_kur`), konuşma turu (`tek_tur`); yüz ana iş parçacığında, döngü ayrı iş parçacığında |
| `kod/ayarlar.yaml` | Tek ayar dosyası: sağlayıcılar, içerik paketi, ekran, GPIO pini, seri port, model adları. Windows varsayılanı donanımsız; Pi'ye geçiş yalnız bu dosyayla |
| `kod/robot/durum.py` | `Durum`, `DurumMakinesi`; izinli geçişler `GECISLER` tablosu, geçersiz geçiş `GecersizGecis`, dinleyiciler `(eski, yeni)` |
| `kod/robot/icerik.py` | İçerik paketi (YAML) ve arama: `turkce_kucuk`, kök = ilk 5 harf, anahtar 3 / ortak kelime 1 puan, eşik altı None |
| `kod/robot/dil.py` | `Cevap(metin, jest)`; `KuralTabanli` (içerik → kalıp → "bilmiyorum"); `BulutDilModeli` gemini/anthropic, sorunla `KuralTabanli`'ye düşer |
| `kod/robot/stt.py` · `tts.py` · `tetik.py` | `dinle()`, `soyle()`, `bekle()` arayüzleri; `*_sec()` ayardan kurar, olmazsa klavye/yazıya düşer |
| `kod/robot/yuz.py` | pygame yüzü, `yuz_ciz()` pencere olmadan da çizer; pygame yoksa `etkin=False` |
| `kod/robot/seri.py` | ESP32'ye satır JSON (`jest`, `sur`, `dur`), hız sınırı; port boşsa `SahteSeri` |
| `kod/icerik/*.yaml` | İçerik paketleri (`universite`, `tesis`); "..." = doldurulacak bilgi |
| `kod/tests/` | pytest; `conftest.py` `kod/`'u yola ekler ve örnek paketi verir |
| `kod/kur_pi.sh` · `requirements.txt` | Pi kurulumu (apt + `~/robot-venv --system-site-packages`), paket listesi |

- Test: `py -3 -m pytest kod/tests -q` (depo kökünden; pygame/vosk/bulut paketi olmadan da geçer).
- Çalıştırma: `py -3 kod/ana.py --yuzsuz --icerik universite`; yüz denemesi `--yuz --deneme-saniye 3`.
  Pi'de `kod/` içinde `source ~/robot-venv/bin/activate && python3 ana.py --icerik universite`.
- Tuzaklar: pygame yalnız ana iş parçacığında çalışır (`Yuz.calistir`), konuşma döngüsü arka planda;
  Pi 5'te 3,5 mm ses yok, HDMI çıkışı masaüstünden ya da `aplay -D plughw:CARD=vc4hdmi0,DEV=0` ile seçilir;
  Türkçe küçük harf için `str.lower()` değil `icerik.turkce_kucuk` (İ→i, I→ı); Pi 5 GPIO için apt'tan
  gelen gpiozero + lgpio gerekir (venv `--system-site-packages`); `kod/modeller/` depoya girmez.
- Donanımda hiçbir şey doğrulanmadı (26 Ekim 2026); doğrulama listesi `kod/OKU_BENI.md` 5. bölümde.
