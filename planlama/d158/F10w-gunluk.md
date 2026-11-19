# F10w · P10.7b2j birleştirme günlüğü (CAD dalı → `lale-duzeltme`, montaj zinciri yeniden)

DURUM: BİTTİ (19.11.2026 07:46). Commit yok, push yok (commit kapanış ajanının). Tam çakışma taraması koşulmadı (ayrı ajan).
Açılış 07:27. Ana ağaç `lale-duzeltme` HEAD = uzak = `896c9a7`; CAD dalı `lale-cad-b2j` ucu `06b2ed9` (taban `8bca2f5`).

## 1. Ön kontrol

- CAD worktree temiz, uç `06b2ed9`. Ana ağaçta FreeCAD / Python süreci yok, `FREECAD-KILIT.txt` "boş", boş bellek 5,4 GB.
- Ana ağacın `git status --porcelain -uall` listesi (37 satır: b2k paketi + 19 eski kir) depo dışı yedek klasörüne
  (`%USERPROFILE%\lale-birlestirme-yedek\status-oncesi.txt`) yazıldı; 37 dosyanın md5'i `kir-md5-oncesi.txt`.
- Kesişim (üç yönlü): dalın değiştirdiği 80 dosya (`8bca2f5..06b2ed9`) ∩ çalışma ağacı kiri = 0; ∩ `896c9a7`'nin dosyaları = 0.

## 2. Squash birleştirme (commit'siz)

- `git merge --squash lale-cad-b2j` (07:29): "Automatic merge went well; stopped before committing". Çakışma yok, reddedilen dosya yok.
  Ara commit'lerin geçmişi taşınmadı (HEAD hâlâ `896c9a7`).
- Eski kir dosyalarından hiçbiri dalla çakışmadı; yine de 19'unun mevcut hâli önlem olarak yedeklendi
  (`%USERPROFILE%\lale-birlestirme-yedek\kir\`, md5 `kir-yedek-md5.txt`): `tasarim/freecad/kabuk/gorsel/*.png` (13),
  `tasarim/freecad/montaj/yerlesim-kontrol.json`, `geometri_cikar.py`, `geometri2_cikar.py`, `geometri2_dogrula.py`, `gez.js`, `uc.js`.
- Doğrulama:
  - Dizin = dal ucu: `git diff --cached lale-cad-b2j -- <80 dosya>` boş; staged dosya listesi dalın 80 dosyasıyla birebir.
  - b2k farkı korundu: `git diff 896c9a7 -- <37 yol>` birleştirmeden önce ve sonra aynı md5 (`c29aa489…`); 37 dosyanın md5'i aynı
    (izlenmeyen `F10u-gunluk.md` / `F10u-kontrol.md` dahil).
  - Gizlilik: `pre-push` kancasının yerel yol / takma ad / ekip adı kalıpları squash farkının eklenen satırlarında (402.447 satır) 0;
    b2k farkının eklenen satırlarında ve iki F10u dosyasında 0.

## 3. Montaj zinciri (birleşik ağaç; her FreeCAD koşusunda kilitte satır, sonunda "boş"; günlükler depo dışında, okundu)

| Saat | Komut | Süre | Çıkış | Sonuç |
|---|---|---|---|---|
| 07:30 | `kafa/kafa_montaj.py` | 238 s | 0 | 161 parça, geçersiz 0, ev pozu çakışma 0 (499 çift), bağlantı 29 / 29, parça kütlesi 2.081,4 g (değişmedi), STEP 161; tilt tork kütlesi 1.549,7 → **1.542,7 g (−7,0 g**: KABLO_EK'ten "Ses karti uzatmasi" 6,5 + "3,5 mm -> PAM" 0,5), tilt payı 3,8, pan 2,26. Traceback yok; 12 satır bilinen OCC "makeElementFace" uyarısı |
| 07:34 | `taban/taban_montaj.py` | 92 s | 0 | 388 parça, geçersiz 0, iç çakışma 0 (660 çift), bağlantı 140 / 140, × iskelet 0 (temas 36), × kabuk 0 (temas 1), bölge ihlali 0, kütle 8.231,4 g; `taban-analiz.json` farkı yalnız `sure_s` |
| 07:36 | `montaj/ana_montaj.py` | 95 s | 0 | 1225 parça (beklenen 1225; kafa 163 → 161), geçersiz 0, solve 0, eklem 22, kütle 25.843,2 → **25.835,1 g** (−8,1 g kart), AM y 527,03 → 526,72; `robot-bom.csv`: ses kartı satırı çıktı, köpük bant 11 → 10 |
| 07:38 | `montaj/montaj_gorsel.py` (GUI) | 50 s | 0 | 11 görsel + 81 hareket karesi (depo dışı TEMP), animasyon 161 kare ihlal 0, GUI kurulumu kaydedildi (eklem 21); bilinen `ViewProviderJoint` uyarıları (84 satır) |
| 07:39 | `taban/taban_gorsel.py` (GUI) | 32 s | 0 | 18 görsel |
| 07:40 | `kafa/kafa_gorsel.py` (GUI) | 23 s | 0 | 17 görsel |
| 07:41–07:43 | `lale158/baski_analiz_ortak.py` × 5 (taban / kabuk / kafa / dirsek / omuz) | 5 / 129 / 21 / 4 / 5 s | 0 | hata yok; ara klasör depo dışında |
| 07:43 | `birlestir` → `Y2b-baski.py` → `F4c-partiler.py` → `F4c-liste.py` → `F4c-dogrula.py` | < 2 s | 0 | **SONUÇ: GEÇTİ**; 64 tür / **74 adet**, 7.722,7–7.780,5 g, 161,0–162,2 sa; çıktılarda fark yalnız tarih / süre |
| 07:44 | `iskelet_regresyon.py`, `omuz_regresyon.py` (`REG_ETIKET=sonra`) | 3 / 43 s | 0 | ikisi de **SONUÇ: BİREBİR AYNI**; yan ürünler (`iskelet/regresyon/fark.json`, `omuz/regresyon/fark.json`, `omuz-analiz.json`, `omuz-montaj.FCStd`, `omuz-montaj.step`) geri alındı |

Eski kir: koşuların hiçbiri 19 kir dosyasından birini yeniden yazmadı (07:45'te 37 dosyanın md5'i yine aynı; `kabuk_gorsel` ve
`yerlesim_kontrol.py` koşulmadı).

## 4. Kaynak sınamaları (bilgi; düzeltme yapılmadı, `git status` değişmedi)

- `rehber_kablo.py`: **SONUÇ KALDI (4 hata)**, hepsi yol 9 (`CAD_KIRP[9]["son"]` 3 kaldığı için; beklenen, b2k'nın sıradaki turu):
  geometri "yol 9: G18 b yanı (XL4016 çevre) yola ulaşmıyor"; geometri "yol 9 son ucu [25, 197, −130] … anahtarlı bara tutucusu eşlenen
  kabloların ucu değil"; bara yolu "yol 9 yıldız 4. saplamasına ulaşmıyor"; onay kaydı "CAD_KIRP 9 değişti" (kesim 143,92 → 49,88, çünkü
  `son` 3 artık yeni yolun 4. noktası). Diğer bölümler 0 hata (kırpma, şema 27, bağlantı tablosu, şema boyu, uç etiketi).
- `rehber_denetim.py --kaynak`: çıkış 1, tek bulgu "onaylı kritik girdi farkı 1: CAD_KIRP 9" (aynı neden). Zorunlu uyarı eksik 0,
  yasak 0, tamlık eksik 0; F10u'nun beklediği 3 terim artık yok (yama dalda uygulanmış).
- `planlama/adim3/kablolar_denetim.py`: **SONUÇ: GEÇER**. `planlama/d158/F10l-birlesim.py`: **GECER**.
- `planlama/d158/F10v-yol-bosluk.py` (FreeCAD, 13 s): F10v § 1 tablosuyla aynı; `F10v-yol-bosluk.json` değişmedi.
- Beklenmedik kırmızı: yok.

## 5. Tarama için ağaç durumu

- İzlenen kaynaklardan (`carpisma_kos.kaynak_listesi()`, 17 dosya) HEAD'e göre değişik: `arayuz.py`, `taban/taban_parcalar.py`,
  `kafa/kafa10_lib.py` (dal) ve `kafa/kafa-analiz.json` (bu turun `kafa_montaj`'ı). 9 bölümün hepsi eski; tam koşu gerekli.
- Bu turdan sonra izlenen dosyalara dokunacak bilinen iş: yok. Sıradaki b2k düzeltmesi (`rehber_kablo.py` `CAD_KIRP`) izlenmiyor.
  Uyarı: `kafa_montaj.py` yeniden koşulursa `kafa-analiz.json` (`sure_s`) değişir ve taramayı eskitir; tarama sırasında koşulmamalı.
- Taramaya bağlı olmayan, koşulmamış kalanlar (F10u § 7.2): `lale158_kontrol` (`lale158-kontrol.json`, iki ses yolu satırı), `uygulama_olc`
  → `uygulama_rapor.py`, F10d gizli ölçümü; tarama sonrası `kafa_rapor.py` / `taban_rapor.py` / `montaj_rapor.py`. Bunlar izlenen
  dosyaları yazmıyor.

## 6. `git status` (07:46)

117 satır: 80 staged (squash; 61'i bu turda yeniden üretilip çalışma ağacında da değişik), 30 yalnız çalışma ağacında değişik
(b2k kaynakları + 19 kirden 14'ü), 7 izlenmeyen (F10u × 2 + 5 kir), + bu günlük.
