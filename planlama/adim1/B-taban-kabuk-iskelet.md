# Adım 1 / B: taban, kabuk, iskelet (M3-taban, M5, M8)

Başlangıç: 14 Ekim 2026. Durum: başladı (dosyalar okunuyor).

## Günlük

### 14 Ekim, okuma ve ölçüm (üretimden önce, mevcut dosyalar)
- **M3-taban önce:** `taban-analiz.json`: 14 plaka→ray bağlantısı (M6×14 DIN 912 + DIN 125 pul 1,6 mm + M6 çekiç somun). Vida ucu rayın alt yüzünden 9,4 mm, çekiç somunun üst yüzü 9,3 mm -> somunu geçme payı **0,1 mm** (şart ≥ 0,5). Uç kanal tabanına 2,4 mm.
  Diğer kanal bağlantıları (4 sonar M6: pay 1,7; 8 motor braketi M4: pay 1,4) zaten ≥ 0,5.
- Seçenekler (uç y = 91,5 − pul + L; somun üstü 103,8; kanal tabanı 106,3; şart: somun üstü + 0,5 ≤ uç ≤ taban − 0,5 yani 104,3…105,8):
  M6×14 + pul = 103,9 (pay 0,1, **geçmez**); M6×16 + pul = 105,9 (taban payı 0,4, **geçmez**); M6×15 standart değil; **M6×14 pulsuz = 105,5 (pay 1,7, tabana 0,8) geçer**. -> pul kaldırılacak (omuzdaki çözümle aynı).
- Not: `arayuz.TABAN['plaka_civata']` ve satırdaki açıklama (pul var diyor) `arayuz` dosyasında, dokunmuyorum; değişiklik taban_parcalar.py içinde.
- **M5 önce:** `KABUK_BINDIRME_BOSLUK = 0,2` (arayuz) yalnız dil kesiminde kullanılıyor, ölçen kontrol yok. Dil civata boss'ları orta yüzeye kadar iner (boss komşuya dayanır, tasarım gereği sıkıştırma), duvar boşluğu bunların dışında ölçülecek.
- **M8 önce:** 3 çubuk, artıklar 3,5 / 101,0 / 304,0 mm (stok 1000, testere 3, stok toleransı yok). Parçalar: 800,5; 500×2; 200; 190×3.

### Uygulanan değişiklikler (14 Ekim)
- **M3-taban:** `taban/taban_parcalar.py`: `PLAKA_PUL = False`; 14 plaka→ray bağlantısında M6 pulu kaldırıldı (M6×14 DIN 912 baş doğrudan plakada). Kontrol: `taban/taban_montaj.py` kanal bağlantılarında `somun_gecme_pay` = uç − somun üstü ≥ `SOMUN_GECME` (0,5 mm). Rapor metni (`taban_rapor.py`) değişkenden üretiliyor.
- **M8:** `iskelet/iskelet_montaj.py`: açık kesim planı (çubuk 1: direk; 2: uzun sol + travers + ara ön; 3: uzun sağ + ara arka + ara orta); `STOK_TOL` 2 mm (tahmini, satıcı teyidi yok), testere `A.TESTERE` 3 mm her kesimde, `MIN_ARTIK` 10 mm kontrolü. Çalıştırıldı: artıklar **194,5 / 99,0 / 109,0 mm** (önce 3,5 / 101,0 / 304,0). Geometri, kütle (5793,1 g) ve parça sayısı (59) aynı. `iskelet_rapor.py` güncellendi, rapor.html üretildi.
- **M5:** `kabuk/kabuk_parcalar.py`: `DIS_HUCRE` sözlüğü eklendi (yalnız kayıt, geometri değişmedi). `kabuk/kabuk_montaj.py` bölüm 5b: her dil–komşu çifti için dil (boss'suz) ↔ komşunun dış yarısı en kısa mesafe, şart ≥ 0,15 mm (`BINDIRME_BOSLUK_MIN`); boss dahil ölçü bilgi amaçlı. Çıktı `kabuk-analiz.json` → `bindirme_bosluk`.

### Kontrol sonuçları
**Taban** (`taban_montaj.py`, 88 s, yeniden üretildi + `taban_rapor.py`):
| | önce | sonra |
|---|---|---|
| Plaka M6 vida ucu − çekiç somun üstü | 0,1 mm | **1,7 mm** (şart ≥ 0,5) |
| Plaka M6 vida ucu − kanal tabanı | 2,4 mm | 0,8 mm (şart ≥ 0,5) |
| Parça sayısı / kütle | 306 / 7507,6 g | 292 / 7493,4 g (−14 pul, −14,2 g) |
| Bağlantı kontrolü | 111/111 | 111/111 (26 kanal bağlantısı: M6 pay 1,7; M4 pay 1,4) |
| Geçersiz / tek katı / taban içi çakışma | 0 / 0 / 0 | 0 / 0 / 0 |
| Taban × iskelet / kabuk ev pozu | çakışma 0 | çakışma 0 (44 / 1 temas, aynı) |
| Taban AM (yüklü) | (−1,12; 119,50; −47,42) | (−1,12; 119,57; −47,51) |
Not: `carpisma-sonuc.json` bu değişiklikle eskidi (taban bölümü); tam tarama en sonda yapılacak.

**İskelet** (`iskelet_montaj.py`, 22 s + `iskelet_rapor.py`): geometri/kütle/parça aynı (59 parça, 5793,1 g), bağlantı 12/12, çakışma 0, bölge ihlali 0. Kesim: artık 194,5 / 99,0 / 109,0 mm (tolerans sonrası; nominal 196,5 / 101,0 / 111,0), `kesim_hatasi` boş.

**Kabuk** (`kabuk_montaj.py`, 646 s + `kabuk_rapor.py`): geometri/kütle aynı (202 parça, 4901,2 g, AM aynı); kabuk içi çakışma 0, kabuk×iskelet 0, bölge ihlali 0, braket 10/10, bindirme cıvatası 51/51, ekran 4/4.
**M5 yeni kontrol, sonuç: GEÇİYOR, ince farkla.** 21 dil–komşu çifti, şart ≥ 0,15 mm, ihlal 0:
- gövde alt/orta/omuz bantları ve kapak: 0,1932…0,2000 mm
- orta → göğüs bandı (dikiş y 690, eğik ön duvar): **0,1505 mm** (en küçük; sağ ve sol), göğüs sağ ↔ sol / orta sağ → göğüs sol: 0,1615
- etek: 0,1722 (orta ↔ ön/arka), 0,1980 (sağ ↔ sol)
- Bindirme cıvatası bossları (Ø8 damla) orta yüzeye iner ve komşunun dış yarısına dayanır (boss dahil ölçüm 0,0 mm); sıkıştırma için tasarım gereği, şart duvar boşluğuna uygulanır.
- Neden 0,2 değil: 15° eğik göğüs duvarında ve değişen kesitte (loft) ofset yüzey normal yönde daha az; marjin 0,0005 mm. Öneri: `arayuz.KABUK_BINDIRME_BOSLUK` 0,2 → 0,25 (dokunmadım), yoksa baskı toleransında göğüs dikişi sınırda kalır.
- Açık not (kapsam dışı): kabuk gövde braketi M6×16 ucu kanal tabanına 0,4 mm (11,4 / 11,8); mevcut kontrol yalnız "değmiyor" diyor, taban modülündeki gibi ≥ 0,5 şartı yok.

## Arayüz/diğer dosyalar için öneriler (dokunmadım)
- `arayuz.TABAN['plaka_civata']` açıklaması "pul + ..." diyor; artık pulsuz (ve 'uç yüzden 9,4' yerine 11,0).
- `arayuz.KABUK_BINDIRME_BOSLUK` 0,2 → 0,25; isteğe bağlı `arayuz`'a `SOMUN_GECME`, `BINDIRME_BOSLUK_MIN`, `STOK_TOL`, `MIN_ARTIK` sabitleri (şimdilerde ilgili montaj betiğinde).
- `maliyet.json`: M6 DIN 125 pul −14 adet (taban); sigma kesim listesi B2 ile birlikte yeni plana göre (3 × 1 m çubuk, değişmedi, parça atamaları değişti).
- Ana montaj: tam robot 907 → 893 parça, −14,2 g (21.260,9 → ~21.246,7 g); `montaj` ve `taban/regresyon` yeniden üretilecek (taban pulsuz). `carpisma-sonuc.json` taban bölümü eskidi, son tam taramada yenilenecek.
- Stok boy toleransı 2 mm tahmini; Robolink'ten kesim toleransı teyit edilmeli (doğrulanmadı).
