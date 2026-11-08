# F5 günlüğü (P5.1, P5.2, P5.3 taslağı) — ajan A, 08.11.2026

Dal `lale-duzeltme` (HEAD `c1bb4ed`). Yazılan dosyalar yalnız: `servo-10-oneri.md`, `kablo-kurali-notu.md`, `F5-pano-taslak.md`, bu günlük.
`kod/`, `main`, CAD betikleri: yalnız okundu (CAD betiği ve `eklem_sinirlari_uret.py` koşturulmadı). Commit / push / pano mesajı yok.

## Okunanlar
- Brief, `dongu-158.md` (§1–§5), `karar-kuyrugu.md` (K9, K14), `yazilim-plani.md`, `README.md:39, 43`.
- `main:kod/jestler/kanallar.yaml`, `jest_verisi.h`, `servolar.cpp`, `bosta/evet/isaret/selam.yaml`, `ayarlar.yaml`, `PI5-KURULUM.md`, `pinler.h`.
- `kod/ortak/eklem_sinirlari.json` (bu dalda; `main`'de `kod/ortak` yok), `tasarim/freecad/arayuz.py` (OMUZ, DIRSEK, KAFA, SES_USB),
  `omuz_rapor.py`, `omuz_montaj.py`, `dirsek_rapor.py`, `dirsek_montaj.py`, `kafa_montaj.py`, `kafa_rapor.py`, `montaj/eklem-dogrulama.json`.
- `planlama/adim3/elektrik.md`, `lale158/kablo_yolu_ekran.py`, `lale158-kontrol.json` `kablo_ozet`, `kafa-yerlesim/uygulama-olcum.json` `kablo_listesi`.

## P5.1 sonuç
- 10 satırlık tablo (kanal 0–9; 10–12 sonar ile çakışma yok). EJ ↔ AY 10 eklem elle karşılaştırıldı: aynı.
- Kod ↔ CAD çelişkisi: **11** (Ç1–Ç11). En önemlileri: Ç6 horn sıfırı (omuz 45°, dirsek 37,5° kayık; kodda sıfır kayması yok), Ç4 tilt ±20 ↔ ±13,
  Ç2/Ç8 omuz 160 ve jestlerde 150 ↔ 135, Ç9 evet tilt 75 (= +15), Ç3 dirsek 110 ↔ 105, Ç1 DS3218 ↔ DS3235.
- Belge çelişkisi (bilgi): brief / `dongu-158.md:87` / `omuz_rapor.py:122` S2 alt sınırı +3°; güncel kaynak +5° (`arayuz.py:176`, EJ). Tabloda +5.
- Kanal düzeni için iki seçenek: brief'teki (0–5 aynen) ve `elektrik.md:455` bloklarına uyan (sol_omuz 2 → 6, sol_dirsek 3 → 7).
- Belirsiz kalan: S2 horn açısı (`omuz_rapor.py:114` kol pozunu yazmıyor); DS3235 darbe aralığı ve yeni kanalların `hiz` değeri depoda kaynaksız.

## P5.2 sonuç
- Eski kural `0b8a245^:planlama/yazilim-plani.md:64`. Güncel CAD (05.11 B + R1) boyundan 5 kablo: kafa 12 V, tilt, göğüs HDMI (757 / 950 mm),
  hub uzatması (617 / 920), hoparlör (823 / 1.030); demet 69,9 mm², en dolu kesit %44,8.
- `yazilim-plani.md:63–64` ve `elektrik.md:30, 50–51, 56, 242, 272` 05.11 öncesi düzeni anlatıyor (P4.1). Yollar P1.4 sonrası değişebilir.
- Soru sayısı 4.

## P5.3 taslak
- Mesaj metni (çizgiler arası, satır sonları dahil) **1.563 karakter** (satır sonları hariç 1.545); sınır 1.800. 6 soru (servo 2 + kablo 4). Gönderilmedi.

## Düzeltme turu 1 (F5-kontrol.md, madde 1–6 + Ç11 atfı + horn uyarısı)
- **B1 / B2 (servo §1, §4 madde 3):** `main:kod/jestler/jest_uret.py:63` açı sınırını yalnız 0 … 180 içinde kabul ediyor (doğrulandı). Çevrim tablosunda
  omuz **kod = CAD + 45** (0 … 180, kol aşağıda = 45) ve bilek **kod = CAD + 90** (0 … 180) önerildi; ikisinde de kod 90 = servo orta, KY:13 ile uyumlu.
  S2 ayrı satır (kod = CAD, 5 … 120). §1 notuna `jest_uret.py:63` eklendi.
- **§4 madde 4** üç yola açıldı: (a) kod birimi kaydırma (dirsek için aynı mantıkla CAD + 37,5, DR:239'dan hesap), (b) sıfır kayması alanı, (c) horn'u KY:13'e göre takma.
- **B3 (Ç8):** atıf `jest_uret.py:111–112` (genel kural KY:19) oldu (doğrulandı).
- **Ç6:** kontrolün uyarısı eklendi: "kol 45° geriye" yorumu servo dönüş yönünü varsayıyor; sol kolda horn açısı ve yön montajda doğrulanmalı.
- **Ç11:** EL:105 ve EL:181–182 atıfları eklendi (doğrulandı: A = sağ kol + pan, B = sol kol + tilt).
- **B4 / B5 (kablo):** birincil kaynak `lale158-kontrol.json:392` `kablo_tup_cakisma`; kesişme göğüs ekranı **kasasıyla** (HDMI 897,1 / 12 V 617,3 / USB dokunmatik 167,6 mm³).
  "P1.4 yolu değiştirecek" → "göğüs kablo kesişmesi ayrıca ölçülecek".
- **B6:** kablo tablosuna "Boyunda kesişme" sütunu: HDMI × boyun mili 15,1, × servo yuvası 1,7; hub uzatması × boyun mili 1,2; hoparlör × boyun mili 1,2 mm³
  (kafa 12 V ve tilt tüp olarak modellenmemiş, KYE:32). `kablo_tup_notu` (`lale158-kontrol.json:456`) gereği elle bakılacak.
- **B7:** `ayarlar.yaml:39–40` → `:40–41`.
- Madde 7 (`dongu-158.md`) orkestratörde; dokunulmadı.

**Pano taslağı değişmedi.** Düzeltmelerin pano iddialarına etkisi:
- "bu montajla omuz 0 komutu kolu 45° geriye götürür" artık belgede bir varsayıma bağlı (dönüş yönü; sol kolda montajda doğrulanacak). Pano bu çekinceyi taşımıyor.
- Soru (a) panoda iki yol soruyor (sıfır kayması / horn'u kod kuralına göre takma); belgede üçüncü yol (kod birimini kaydırma) eklendi.
- Diğer pano iddiaları (sayılar, 5 kablo, ~950 mm, HDMI0/HDMI1, 1280×800, vc4hdmi0) değişmedi. Karakter sayısı aynı: 1.563.

## Pano hizalaması (orkestratör onayı)
- "45° geriye" cümlesine "(servo yönü varsayımıyla; sol kolda yön montajda doğrulanmalı)" eklendi.
- (a) sorusu üç yolu sayıyor: kod birimi kaydırma (omuz CAD + 45, bilek CAD + 90), eklem başına sıfır kayması, horn'u "servo ortası = 90" kuralına göre takma.
- Mesaj metni artık **1.701 karakter** (satır sonları hariç 1.683); sınır 1.800. Başka değişiklik yok, karar yok, kişi adı yalnız "Efe".

## Düzeltme turu 2 (F5-kontrol.md "Yeniden kontrol 1", R1–R4)
- **R1 (pano):** (a) sorusu "(omuz CAD + 45, dirsek CAD + 37,5, bilek CAD + 90)" oldu. Mesaj metni **1.720 karakter** (satır sonları hariç 1.702); sınır 1.800.
- **R2 (servo §1):** çevrim tablosunun dirsek satırına "§4 madde 4 seçenek (a) seçilirse kod = CAD + 37,5 → 37,5 … 142,5" eklendi.
- **R3 (servo §4 madde 7):** S1 sınırı birimiyle yazıldı: "CAD biriminde ≤ 135 (seçenek a'da kod ≤ 180; mevcut 150 + 45 = 195 olacağı için yeniden yazılır)".
- **R4 (kablo notu satır 40):** `kablo_tup_notu` tam alıntı yapıldı: "Listede rulman yuvasi, servo yuvasi, mil varsa o kablo gecisi elle bakilmali." (`lale158-kontrol.json:456`, birebir).
- Başka değişiklik yok.
