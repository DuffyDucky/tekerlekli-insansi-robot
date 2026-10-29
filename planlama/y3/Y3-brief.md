# Y3 brief (yeniden başlatma için; 29 Ekim 2026)

Oturum sınırına takılırsa: aynı brief ile **yeni Opus ajanı** başlat ve "önce `planlama/y3/Y3-gunluk.md`'yi ve `git status`'u oku,
yapılanı tekrarlama" de.

## Resmi tanım (`planlama/dongu.md`, "1,70 m planı")
> Y3 | M6 CAD (erişim düzeltmeleri, eski 4. adımdaki liste) | ⏳

Eski 4. adımdaki liste (`planlama/dongu.md` 4. satır, `planlama/adim4/M6-montaj-sirasi.md` "4. CAD değişiklik listesi"):
C1 göbek–horn cıvatası, C2 dirsek servo kulağı, C3 kontra somun cepleri, K1 / K2 dışarıdan vida + perçin somun, K3 ped yarığı + Ø84,
K4 göğüs (üst arka) servis kapağı, K5 etek kapağı, K6 ana sigorta, K7 ana anahtar deliği. Eski 5. adım notu: ön şarj K2 rölesi + 5,6 Ω
CAD'de yok → M6 CAD ile. Çelişkide dongu.md esas. **Liste 125 cm CAD'de ölçüldü: her madde 1,65 m CAD'de yeniden doğrulanır.**

## Y2b'den devredilenler (hangisi Y3'e düşüyor)
- Y3: dördüncü XL4016 (kafa servo hattı C, 5 A mini sigorta) CAD / BOM yerleşimi (`kararlar-2026-10-29.md` 6).
- Y4: `dirsek-analiz.json` yeniden üretimi (S2 ~1.770 mm; Y3'te dirsek yeniden koşulursa erken düzelir), `kabuk_rapor.py` (Nextion), tam
  çakışma taraması, M6_erisim / M6_ek yeniden koşusu, regresyon.
- Y4 / Y6: `tasarim/freecad/OZET.md`, `taban/taban_rapor.py` (0,25 m/s²), `Lale-Proje-Ozeti.txt`, `raporlar/kaynaklar/05-fiyat-arastirmasi.md`.
- Duffy kararı (karar verme, sor): boyun adaptörü PETG → PETG-CF; KZ2 el yükü ~100 g.
- main'de, dokunma, listele: köprü notundaki "USB 1,25 m" satırı.

## Depo ve sınırlar
- `C:\Users\Victus\OneDrive\Masaüstü\Robot`, dal `lale-duzeltme`. **Push yok**, tek yerel commit (Türkçe, `Lale: Y3 ...`, boş satır +
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`). Adım 0 commit'i `59367ab` (rampa freni ≤ 0,1, Pi 4 GB).
- `tasarim/solidworks/` izlenmiyor: dokunma, commit'e ekleme. `main` / `yazilim-baslangic`'e dokunma.
- Her dosyayı değiştirmeden önce oku. Üretilen dosyaları elle düzenleme (FCStd, STEP, JSON, BOM, `eklem_sinirlari.json`, demo, maliyet türevleri):
  kaynağı değiştir, betiği koş. Kapsam dışı sorun: raporda listele, dokunma.
- FreeCAD: `tasarim/freecad/README.md` "Çalıştırma" (ASCII başlatıcı `C:\Users\Victus\.robot-cad\run_fc.py`, `FC_SCRIPT`).

## Bilinen durum (Y2a / Y2b + 29.10 kararları)
1650 mm, direk 1.185,5, 1.073 parça, 24.396 g, AM (−0,20; 527,43; −12,38), teker izi 432 mm, 10 servo (omuz DS3235), kafa tilt ±13, akü
yerinde, servo besleme 3 hat (sağ kol / sol kol / kafa pan + tilt), maliyet genel 103.166,51 TL (Adım 0'dan sonra; önce 109.001,35).

## Bitince
`planlama/dongu.md` Y3 satırı, tek commit, rapor (≤ 15 satır): hash, yapılanlar (sayısal), yapılamayanlar, Duffy kararları, köprü notuna
eklenecekler, bağımsız kontrol için 3–5 kritik iddia. İlerleme: `planlama/y3/Y3-gunluk.md`.
