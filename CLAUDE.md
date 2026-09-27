# Robot projesi — yapay zekâ oturumları için bağlam

Tekerlekli insansı robot (üniversite projesi, 4 kişilik ekip, MCBÜ Mekatronik MYO). Proje sahibi
Duffy; mekanik, montaj, kablaj ve SolidWorks'te güçlü, yazılımı yapay zekâ yardımıyla yazıyor.

- Türkçe konuş; doğrudan ol, ilk cümlede cevaba başla. Bitmiş işi tablo veya kısa listeyle özetle.
- Projenin güncel durumu: `README.md` (kararlar, CAD sonuçları, açık işler) ve `planlama/proje-plani.md`.
  Varsayımda bulunmadan önce bu dosyaları ve ilgili kaynak notunu oku.
- Yeni rapor → `raporlar/`, dayandığı araştırma → `raporlar/kaynaklar/` (kaynak URL'li; tahminleri
  "tahmini" diye işaretle). Plan değişikliği → `planlama/`. Tasarım → `tasarim/`. Yazılım kodu → `kod/`
  (henüz yok; ilk kod geldiğinde oluştur).
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
