# Dirsek çatalı dış kolu 5 → 7 mm: CAD tasarım ajanı notları (ara kayıt)

Durum: başladı (24 Ekim 2026). Gerekçe: kontrol ajanı (KOL125-KONTROL-NOTLAR.md, kol-analiz/) dirsek çatalı dış kolu
L3 (servo stall) SF 1,86, L4 (darbe) 0,77. Duffy'nin şartı: "absürd gözükmez ve çarpışmaya yol açmazsa onaylarım".
Onaysız öneriler (6806, 6808 çifti, kelepçeli horn, 20 AWG, XL4016 6,4 V) uygulanmaz.

## Hangi kol "dış" kol
- dirsek/dirsek_parcalar.py: `DIS_KOL = (X_HORN1, X_HORN1 + 5)` = x 219,9 … 224,9 (omuz yereli, +X dışarı = gövdeden uzak taraf).
  Dirsek MG996R horn'una 4× M3x8 ile bağlı kol. `IC_KOL = (156, 167)` 11 mm, 625ZZ yuvası (gövde tarafı).
- kol_analiz.py: "Dirsek çatalı dış kolu (horn plakası 5 × 32, PETG)" `PLAKA_5x32`; iç kol `PLAKA_11x32`. Yani kastedilen = horn tarafı,
  gövdeden uzak 5 mm kol. (Gövdeden uzak taraf ile horn tarafı aynı kol.)

## Kalınlaştırma yönü
- İçe (−X) yer yok: dış kolun iç yüzü (x 219,9) doğrudan horn üst yüzüne (X_HORN1) oturuyor; horn → servo kasası → ön kol. İçe almak
  horn/servo/dirsek eksenini kaydırmak demek (yasak).
- Dışa (+X): x 224,9 → 226,9. Kesit (YZ) eski kolla aynı → ön kolun dirsek 0–105° bükülmesinde YZ boşluğu değişmez (ön kol alt U
  x 223,7–226,7 eski kolla zaten X'te örtüşüyordu). Köprü de 2 mm dışa uzatıldı (kol ile köprü dış yüzü aynı düzlemde kalsın).
- Horn cıvataları: baş yüzü 2 mm dışa kayar; M3x8 → M3x10 (uç x 216,9'da aynı: horn'da diş boyu aynı, kasaya inmez). Delik
  konumları, Ø9 horn merkez vidası erişim deliği, 625ZZ, pim, eksen konumları aynı.
- 45° destek (köprü üstü) aynı bırakıldı: x 224,9'a kadar; yeni 2 mm şerit baskıda (ters, kollar yukarı) 2 mm çıkıntı, sorun değil.

## Uygulama
- taslak_ayar.py: `CATAL_DIS_KOL` (ortam `TASLAK_CATAL_DIS_KOL`, varsayılan 7), `CATAL_DIS_KOL_ESKI` 5.
- taslak_parcalar.py: dirsek bölümünde "Dirsek catali" + 4 "Catal-horn civatasi" (yalnız dirsek modülü; omuzdaki aynı adlı
  cıvatalar kol çatalı ↔ S2 horn, dokunulmadı). 5'te eski dal aynen çalışır.

## Regresyon (24 Ekim, scratch reg5.py: taslak_parcalar parça listesi ↔ önceki kutle.json)
- `TASLAK_CATAL_DIS_KOL=5`: 1052 parça, ad/modül/kütle/AM/durum farkı 0 (birebir).
- 7 mm: yalnız 10 parça değişir: 2 Dirsek catali (87,49 → 90,25 g, 1 katı, geçerli), 8 Catal-horn civatasi M3x8 → M3x10 (0,93 → 1,04 g).
  Toplam +6,41 g (24.496,25 → 24.502,66 g).

## Sonuç (24 Ekim 2026, taslak_montaj ~6 dk + taslak_gorsel + taslak_rapor)
- 1052 parça, STEP 1052 katı, 22 eklem, solve 0. Kütle 24.496,3 → 24.502,7 g (+6,4), AM (−0,11; 567,08; −10,72).
- Dirsek çatalı (her kol) 87,49 → 90,25 g, 1 katı, geçerli; baskı 72,9 × 72,0 × 74,0 mm, yön aynı (−Y yukarı), tablaya sığar.
- Ev pozu: 773 aday çift, 4 çakışma, hepsi 125 cm'den (tüp ↔ S1 tamburu / kaset kapağı), taslaktan 0. Kafa süpürmesi 0/24.
  Kol kaba ızgara 0/240 (çatal hedefte), el en alt y 982,5.
- Çatal kontrolü (sağ; aynı komşulara 5 mm ve 7 mm): ev pozunda 15 mm içinde 28 parça, hiçbiri yaklaşmadı (dış yüzün 15 mm
  yakınında parça yok; en yakınlar iç/üst taraf: ön kol gövdesi 1,0, servo mili 1,39, MG996R 3,3, göğüs bandı 5,91 — hepsi aynı).
  Dirsek 0…105° (5°): ön kol gövdesine en az 1,0 → 1,0 mm (eş eksenli mil/rulman/pim hariç). S1 {−45…135} × S2 {5, 45, 90, 120}:
  gövde/kafa/omuza en az 18,74 → 18,74 mm (göğüs bandı, S1 0 / S2 5).
- Kol ↔ gövde kabuğu en dar 5,91 mm (dirsek çatalı ↔ göğüs bandı sağ) değişmedi (iç kol tarafı).
- Görsel: gorsel/catal-5-7.png (2 × 2: önce/sonra × önden/izometrik). Rapor: rapor.html (görünümler + kol + kısa yerleşim satırları).
- Tahmini dayanım (kesit ∝ t, kol analizi yeniden koşulmadı): gerilme ×0,71 → L3 SF ~2,60 (güvenli), L4 ~1,08 (hâlâ < 1,2).
  L4 ≥ 1,2 için t ≈ 8 mm gerekir (8 mm: ~1,23). Kontrol ajanı kol_analiz'de PLAKA_5x32 ve horn ezilme t 5'i 7'ye almalı.
- Bilinen: analiz/*.json ve kol-analiz eski kütleyle (fark +6,4 g, ihmal edilebilir); maliyet.json / BOM'a M3x10 (8 adet) eklenmedi
  (dokunulmadı); 45° destek x 224,9'da bitiyor, dış 2 mm şerit köprü üstünde düz (baskıda 2 mm çıkıntı).
- Durum: Duffy onayı bekliyor ("absürd gözükmez ve çarpışmaya yol açmazsa").

# Dış kol 7 → 8 mm (Duffy kararı "8mm yap 3 ünün görünümünü ver"): CAD tasarım ajanı notları

## Durum (24 Ekim 22:51, 3 saatlik aradan dönüş)
- Ara öncesi yalnız okuma yapıldı (CLAUDE.md, CATAL-NOTLAR, CATAL-KONTROL-NOTLAR, taslak_ayar/parcalar/montaj/gorsel, dirsek_lib). Hiçbir dosya
  değiştirilmedi; çalışan FreeCAD yok, yarım üretilmiş çıktı yok. Klasördeki tüm `M` dosyalar (FCStd/STEP/kutle/analiz 18:01–18:08, py'ler)
  önceki 7 mm işinden (tasarım + kontrol ajanı), kendi içinde tutarlı (7 mm). Bunlar commitlenmemiş; 7 mm temel çıktılar scratch'e kopyalandı
  (regresyon için: kutle.json, taslak-analiz.json, py'ler, catal-5-7.png, STEP md5; 5 mm temel = git HEAD kutle.json).
- Plan: 8 varsayılan; cıvata boyu standart listeden; 45° destek dış yüze (parametre, 7'de varsayılan kapalı → 7 birebir); 7 mm ara çatal
  şekilleri de üretilip görsel belgeye (Catal5/Catal7/Catal8); catal-5-7.png korunur, catal-5-7-8.png yeni.

## Uygulama (24 Ekim ~23:00)
- taslak_ayar: `CATAL_DIS_KOL` varsayılan 8 (karar notu). `horn_civatasi_secim(t)`: gereken boy 8 + (t − 5), standart M3 seri (6, 8, 10, 12, 16, 20;
  M3x11 standart değil) → bir üst boy + baş altına DIN 125-A M3 pul yığını (0,5 mm katları) → uç her kalınlıkta eski yerde (x 216,9).
  5 → M3x8, 7 → M3x10, 8 → M3x12 + 2 pul (1,0 mm), 9 → M3x12. `CATAL_DESTEK_DIS` (ortam `TASLAK_CATAL_DESTEK` 1/0; varsayılan t > 7 ise açık).
- taslak_parcalar: `catal_kalinlastir(s0, t, destek)`, `horn_civatasi(g, t)` → (cıvata, pul, L, n). Pul ayrı parça "Catal-horn pulu M3 (2x DIN 125-A)"
  (kol başına 4, 1 mm yığın tek katı). 45° destek: aynı eğim dışa kaydırıldı, (213; −128 + d) → (x1; −139,9), z TZ ± 16 (eski desteği kapsar).
  `CATAL_ARA_T` / `CATAL_ARA`: 8 mm koşusunda 7 mm çatal + M3x10 da kurulur (yalnız görsel + kısa kontrol; parça listesine girmez).
- taslak_montaj: kısa çatal kontrolünde pullar dahil (CAT_N) ve 7 mm üçüncü sütun (`ara_mm` / `ara`); görsel belgede Catal5 / Catal7 / Catal8
  (+ `Baslik` "kalınlık|cıvata"). taslak_gorsel: 2 takım → catal-5-7.png (eski düzen), 3 takım → catal-5-7-8.png (sütun = kalınlık, satır = önden / izo);
  8 koşusu catal-5-7.png'ye dokunmaz. taslak_rapor: görsel adı, cıvata metni (M3x12 + 2 pul), karar satırı, açık iş satırı (yalnız metin).

## Regresyon (scratch geo8.py, freecadcmd 3 paralel koşu; önceki kodun 18:21 dökümleri geo5/geo7.json + HEAD/7 mm kutle.json)
- 5: 1052 parça; ad/grup/durum/hacim/kütle/sınır kutusu/merkez farkı 0 (eski kod dökümü), kutle.json (HEAD) farkı 0. Birebir.
- 7: 1052 parça; aynı ölçütlerle fark 0 (eski kod dökümü ve 7 mm kutle.json). Birebir (45° destek 7'de kapalı).
- 8 ↔ 7: 1060 parça (+8 pul). Pul hariç yalnız 10 parça farklı: 2 Dirsek çatalı 90,25 → 92,80 g (1 katı, geçerli), 8 cıvata M3x10 → M3x12
  (1,04 → 1,15 g); pullar 8 × 0,24 g. Toplam 24.496,25 (5) / 24.502,66 (7) / 24.510,56 g (8): 7'ye +7,90, 5'e +14,31.
- Çatal (sağ yerel): bbox x 154,0 … 227,9 (yalnız dış yüz +3), çıkan hacim 0, eklenen 5.228 mm³ (bbox x 213 … 227,9; y −189 … −125);
  45° destek eki 1.153 mm³ (x 213 … 227,9, y −140 … −125, yalnız köprü üstü). Horn delik eksenleri r 1,6 ile ortak hacim 0, Ø9 erişim ortak 0.

## Horn cıvatası seçimi ve servoya mesafe (dirsek yereli; servo gövdesi dirsek ekseni etrafında −105 … +105°, 1°)
| seçenek | uç x | horn'da diş | uç → kasa üstü | çıkış kubbesine | servo gövdesine en az |
| 7 mm: M3x10 | 216,9 | 3,0 | 3,3 | 1,39 | 3,3 |
| 8 mm: M3x12 + 2× DIN 125-A (seçilen) | 216,9 | 3,0 | 3,3 | 1,39 | 3,3 |
| 8 mm: M3x12 pulsuz | 215,9 | 3,3 (horn'u 0,7 geçer) | 2,3 | 0,58 | 2,3 |
| 8 mm: M3x10 + 1 mm havşa | 216,9 | 3,0 | 3,3 | 1,39 | 3,3 |
- Gerekçe: pulsuz M3x12 ucu horn altından 0,7 mm çıkar, servo çıkış kubbesine (MG996R üst çıkıntısı, model tahmini) 0,58 mm kalır → ret.
  Havşa aynı mesafeyi verir ama cıvata deliği bölgesinde plakayı 7 mm'ye indirir (8 mm'nin dayanım kazancı kısmen gider, ezilme boyu 7) → ret.
  Pul: kalınlık tam 8 kalır, PETG'ye baş yükünü Ø7'ye yayar, uç/diş/servo mesafeleri 5 ve 7 mm ile aynı. dirsek_montaj ölçütü (diş ≥ 2,5, kasaya ≥ 1) geçer.

## Montaj (8 mm varsayılan, 24 Ekim 22:59–23:10, 625 s)
- 1060 parça (1052 + 8 pul), STEP 1060 katı, 22 eklem, solve 0, geçersiz / çoklu katı yok. Kütle 24.510,6 g, AM (−0,11; 567,28; −10,71).
- Dirsek çatalı 87,49 → 92,80 g (her kol), 1 katı, geçerli; baskı 73,9 × 72,0 × 74,0 mm (ters, −Y yukarı) → tabla 250 / hedef 230 içinde.
- Ev pozu: 789 aday çift, 4 çakışma (hepsi 125 cm'den: üst kol tüpü ↔ S1 tamburu / kaset kapağı), taslaktan 0. Kol kaba ızgara 0/240, el en alt y 982,5.
- Kısa çatal kontrolü (sağ; 5 / 7 / 8 aynı komşulara, pullar dahil): ev pozunda yaklaşan 0 (15 mm içindeki her parça 5 = 7 = 8; en yakınlar iç/üst taraf:
  bilezik cıvatası 0,2, ön kol gövdesi 1,0, servo çıkış mili 1,39, MG996R 3,3, göğüs bandı 5,91). Dirsek 0…105° (5°) ön kola en az 1,0 / 1,0 / 1,0.
  S1 × S2 kaba ızgara: göğüs bandı 18,74 / 18,74 / 18,74 (S1 0, S2 5). Kol ↔ gövde kabuğu en dar 5,91 (iç kol tarafı) değişmedi.

## Düzeltme (23:15): 45° destek tüp yuvasına giriyordu
- Dış yüz bölgesi ölçümü (scratch dis8.py) üst kol tüpüne 0,0 mm gösterdi. Neden: dirsek_parcalar'da tüp yuvası (r R_BIL_IC = 28 + geçme, x 213,2'ye kadar)
  destek füzyonundan SONRA oyuluyor; taslakta destek yuvadan sonra eklenince x 213 yüzü yuvanın ~0,2 mm içine girip (y −140 … −125) tüp geçme boşluğunu
  dolduruyordu. Düzeltme: uzatılmış destekten r R_BIL_IC silindiri yeniden çıkarıldı (yalnız 8 mm / destek açık dalı; 5 ve 7 etkilenmez).
  Montaj + görsel yeniden koşuldu (aşağıda).
- İlk koşunun dış bölge ölçümü (düzeltme öncesi, bilgi): ev pozunda dış bölgeye en yakın horn (cıvata dişi, 0), servo çıkış mili 1,39, horn merkez vidası 2,66,
  MG996R 3,3, kulak cıvataları 7,72, ön kol gövdesi 13,54; dirsek ±105° (5°) ön kol + el + servolar en az 3,3 (MG996R ↔ cıvata ucu, açıyla sabit).

## Sonuç (24 Ekim 23:25; düzeltmeden sonra montaj 639 s + GUI görseller)
- Doğrulama (geo-8b): tüp yuvası ile ortak hacim 5 mm ve 8 mm'de aynı (29.168,88 mm³ = pim/yuva, giriş yok); çatal 92,78 g (her kol), eklenen 5.209 mm³,
  destek eki 1.135 mm³ (x 213 … 227,9, y −140 … −125). Delik / Ø9 ortak hacim 0. Ev pozunda üst kol tüpü 0,0 = 5 mm'deki oturma teması (değişmedi).
- Çıktılar: taslak-170.FCStd / .step (1060 parça = 1060 katı, 22 eklem, solve 0), kutle.json 24.510,5 g, AM (−0,11; 567,28; −10,71),
  taslak-analiz.json, gorsel/*.png (catal-5-7-8.png yeni; catal-5-7.png 24 Ekim kaydı olarak korundu). Baskı 73,9 × 72,0 × 74,0 mm, tabla 250 / hedef 230 içinde.
- Kısa kontrol (montaj, düzeltme sonrası): ev pozu taslaktan çakışma 0, çatal yaklaşan 0; dirsek 0…105° ön kola 1,0 (5 = 7 = 8); S1 × S2 18,74 (5 = 7 = 8);
  kol ↔ gövde kabuğu 5,91 (iç taraf, değişmedi); kol kaba ızgara 0/240.
- Kütle (toplam): 5 mm 24.496,25 g / 7 mm 24.502,66 g / 8 mm 24.510,52 g (8: 7'ye +7,86, 5'e +14,27). Çatal 87,49 / 90,25 / 92,78 g;
  cıvata 4 × 0,93 / 1,04 / 1,15 g; 8'de + 4 pul yığını × 0,24 g (kol başına).
- Yeniden üretilmedi: rapor.html (7 mm hâliyle kaldı; RA.catal ve analiz/*.json, kol-analiz kontrol ajanının 7 mm koşusu). taslak_rapor.py metni 8'e hazır.
- Açık: kontrol ajanı 8 mm ile tam tarama (taslak_analiz catal / catal_geo / kol_*) + kol_analiz PLAKA t = 8 + taslak_rapor; maliyet.json'a M3x12 (8) +
  DIN 125-A M3 pul (16) eklenmedi; analiz/catal-geo*.json 7 mm'ye göre (taslak_analiz.py'ye dokunulmadı; pulları "Catal-horn civatasi" önekiyle saymaz).
- Durum: bitti (tasarım ajanı). Commit/push yok.
