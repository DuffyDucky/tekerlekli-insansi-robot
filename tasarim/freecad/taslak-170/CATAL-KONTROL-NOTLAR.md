# Dirsek çatalı dış kolu 5 → 7 mm: CAD kontrol ajanı notları (ara kayıt)

Durum: başladı (24 Ekim 2026). Görev: tasarım ajanının 5 → 7 mm işini (CATAL-NOTLAR.md) bağımsız doğrula; tam çarpışma taraması
(taslak_analiz.py), kol_analiz.py'de dış kol kalınlığını parametreye bağla ve 7 (ve gerekirse 8, yalnız hesap) ile koş; analiz/*.json,
kol-analiz/, rapor.html'leri yeniden üret. Mevcut modüllere, arayuz.py, montaj/, tasarim/cad/, demo, maliyet.json'a dokunulmaz.

## Okunan bağlam
- Tasarım ajanı diff: taslak_ayar `CATAL_DIS_KOL` (ortam `TASLAK_CATAL_DIS_KOL`, 5…9), taslak_parcalar `catal_kalinlastir` (dış kol + köprü
  x 224,9 → 226,9, R16 kol ucu, Ø9 erişim, 4 horn deliği), `horn_civatasi` M3x(8+ek) baş yeni dış yüzde; `CATAL_ESKI` (5 mm şekiller).
  taslak_montaj kısa çatal kontrolü (sağ kol), görsel belgede Catal5/Catal7/CatalCevre.
- analiz/*.json ve kol-analiz 24 Ekim ~02:00–02:47 (5 mm çatal geometrisiyle).

## 1) Bağımsız geometri kontrolü (24 Ekim ~18:30; scratch geo_kontrol.py, taslak_parcalar iki kez: TASLAK_CATAL_DIS_KOL=5 ve 7)
- 5 mm koşusu ↔ git HEAD kutle.json (çatal öncesi): 1052 parça, ad/modül/kütle/merkez farkı 0 (eşik 0,006). Toplam 24.496,26 g = HEAD. Birebir.
- 5 ↔ 7: yalnız 10 parça farklı (2 Dirsek çatalı + 8 Catal-horn civatası M3x8 → M3x10); diğer 1042 parçanın hacim, sınır kutusu, kütle
  merkezi birebir. 22 eklem ekseni (n, u) birebir. 7 mm koşusu = güncel kutle.json (fark 0). Toplam 24.502,66 g (+6,41).
- Çatal (sağ; sol X aynası aynı): bbox x 154,0…224,9 → 154,0…226,9 (yalnız dış yüz +2 mm). Çıkan hacim 0 (iç yüz/horn oturması aynı),
  eklenen 2.716 mm³, bbox x 224,9…226,9, y 1171…1220, z −17,25…14,75 = dış kol + R16 uç + köprü (dirsek ekseni ZE ± 16). 1 katı, geçerli.
- Delikler: 4 horn deliği ekseninde r 1,6 silindir → çatal ortak hacmi 5 ve 7'de aynı (76,93 mm³, iç kol kısmı) → yeni 2 mm'de delik açık;
  Ø9 merkez vidası erişimi (dış bölge) ortak hacim 0. Delik eksenleri (y, z) eski = yeni. Dirsek ekseni (216,6; 1187; −1,25) / −X aynı;
  625ZZ dış bilezik, servo mili, horn eksende (0 mm).
- Cıvatalar: M3x10 baş alt yüzü x 226,9 (çatala temas 0 mm, ortak hacim 0: delikte boşluklu), baş üstü 229,9 (eski 227,9); uç x 216,9 = eski.
  Horn x 216,6…219,9 (3,3 mm): kavrama 3,0 mm (eski 3,0), uç horn alt yüzünden 0,3 mm içeride; servo kasası üstü 213,6 → uç-kasa 3,3 mm.
  Dirsek 0…105° (5°) cıvata ↔ servo kasası en az 3,3 mm (eski 3,3). Kasaya inmiyor. (dirsek_montaj ölçütü kavrama ≥ 2,5, kasaya ≥ 1: geçer.)
- Baskı: 74,0 × 72,9 × 72,0 mm (eski 74 × 72 × 70,9) → tabla 250 ve hedef 230 içinde.
- Sonuç: geometri TUTTU.

## Koşular (24 Ekim ~18:13 başladı, paralel FreeCAD; scratch kos.sh)
- A catal (yeni bölüm), B kol_sag, C kol_sol, D kafa, E statik+kolkol+kafakol_sag/sol+kafakol_ince_sag/sol+dogrula+kutle (444),
  F 480/500/520 kutle+statik → kol_sag dirsek-only → kafakol_sag S2=0. Sonra catal_geo (5 sonra 7). 5 mm sonuçları git 8ee72a0 (+ scratch kopya).

## taslak_analiz.py eklemeleri
- `TA_BOLUM=catal` → analiz/catal-yeni.json: aynı hedeflere eski (TP.CATAL_ESKI, 5 mm + M3x8) ve yeni çatal (+ M3x10), iki kol:
  (a) dirsek 0…105° (1°) ön kol + el (bilek ±90 5°'de bir), eş eksenli (mil, 625ZZ iç, pim, pul) ayrı; (b) S1 × S2 5° (37 × 24 = 888 poz)
  iskelet/kabuk/taban/kafa/omuz gövdeleri/göbek (S1 ile)/karşı kol ev pozunda. Kesişim hacmi de.
- `TA_BOLUM=catal_geo` → catal-geo-5.json (TASLAK_CATAL_DIS_KOL=5) / catal-geo.json (+ fark_5 parça parça): geometri kontrolü repo içinde
  tekrarlanabilir (scratch geo_kontrol.py'nin aynısı).

## 3) kol_analiz.py (24 Ekim ~18:45)
- `plaka(t)`, `T_DIS = TA.CATAL_DIS_KOL`, `T_DIS_HESAP = [5, 7, 8]`, `catal_kol_arasi(t) = 61 + (t − 5)/2 mm`; yapisal(..., t_dis): dış kol kesiti,
  horn cıvatası ezilme boyu t, çift kuvvet kolu. Varyant × servo başına `catal_dis_kol` {5, 7, 8} (8 yalnız hesap). `catal5` = git 8ee72a0 özeti.
- Regresyon: scratch kopyada (HEAD kutle.json + 5 mm analiz/) TASLAK_CATAL_DIS_KOL=5 → 8ee72a0 kol-analiz.json ile 672 satır, sayısal fark 0, ad farkı 0.
- Rapor: taslak_rapor_analiz.catal() (yeni bölüm, id='catal'), taslak_rapor.py dış kol paragrafı kol-analiz değerlerine bağlandı, kol_rapor.py 5b bölümü.

## 2a) catal bölümü sonucu (analiz/catal-yeni.json, 1.870 s) — iki kolda aynı
- Dirsek 0…105° (1°), ön kol + el: 5 mm çatal en az 1,00 mm (On kol gövdesi) = 7 mm 1,00; M3x8 / M3x10 ↔ dirsek servosu MG996R 3,30 = 3,30.
  Sonraki: ısıl gömme M5 4,90, servo kasası 5,66, kontra somun 5,70, kulak cıvatası 6,07 (hepsi 5 = 7). Kesişim hacmi 0.
- S1 × S2 (5°, aralık içi, 888 poz) gövde/iskelet/taban/kafa/omuzlar/göbek/karşı kol: çatal en az 17,93 mm (göğüs bandı, S1 35 / S2 5) 5 = 7;
  horn cıvataları hiçbir pozda hedeflerin 30 mm'sine girmedi (dış taraf). Kesişim 0.
- Tasarım ajanının "göğüs bandı 5,91" değeri ev pozu (S2 0°, aralık dışı, iç kol tarafı); aralık içinde 17,93.
- catal_geo (repo içi) scratch sonucuyla aynı: 5 ↔ 8ee72a0 kutle.json fark 0; 5 ↔ 7 yalnız 10 parça; eksenler aynı.

## 3b) Dayanım ön sonucu (scratch, eski girdi kütleleriyle; nihai koşu girdiler gelince)
- ×1,25 + DS3235 dış kol SF: 5 mm L3 1,86 / L4 0,77; 7 mm 2,61 / 1,08; 8 mm (hesap) 2,99 / 1,23. Horn cıvatası ezilme L3 6,30 → 8,82 → 10,08.
- ×1,36 + DS3235 7 mm L4 0,91; ×1,25 + DS3218MG 7 mm L4 1,31.

## 2b) Tam taramalar (24 Ekim 18:13–19:25) — 5 mm (git 8ee72a0) → 7 mm
- Statik ev pozu 444/480/500/520: çakışma 0/6, 16/6 (480'de bilinen braket M4 ↔ uzun ray), 0/6, 0/6 → aynı; aday çift sayıları aynı; dosyalar bayt bayt aynı çıktı.
- Kol sağ/sol tam (43.043 ölçüm): çakışma 0 → 0; en dar her hedef modülde aynı (kabuk 0,50 S1 tamburu↔kaset kapağı, omuz gövdesi 5,07 kol çatalı↔kapak
  cıvatası, iskelet 45,1, kafa gövde 98,75). Dikkat: "Catal-horn civatasi M3x8 ↔ S2 servo çıkış mili 0,58" OMUZDAKİ kol çatalı cıvatası (grup Kol), değişmedi.
- Kol sağ yalnız dirsek: çakışma 0; dirsek çatalının tüm en dar çiftleri birebir aynı (kabuk 17,95 göğüs bandı, iskelet 136,87, kafa 156,55, göbek 103,71, omuz 104,24).
- Kol ↔ kol 227 poz: 0, en dar 290 mm (aynı). Kafa pan ±90 × tilt ±15: 0, en dar aynı (kabuk 34,7, omuz 42,98).
- Kafa × kol kaba sağ/sol: 0, 10,98 (aynı); ince sağ/sol: 0, 7,71 (aynı); S2 = 0 (aralık dışı) 357 → 357 (El ↔ yüz kabuğu, çatal yok).
- Doğrulama: yeniden kurulum 24.502,66 g = kutle.json, FCStd 1052, STEP 1052/1052 eşleşme.
- Sonuç: çatal 7 mm hiçbir taramada yeni çakışma ya da daralma üretmedi. Görsel (catal-5-7.png) incelendi: dış kol ön kol alt U dış duvarıyla
  (x 226,7) neredeyse aynı düzlemde, absürd değil; tek kozmetik iz: 45° destek x 224,9'da bitiyor, köprü üstünde 2 mm basamak.

## 4) Raporlar (19:35)
- taslak_hesap.py (hesap.json; S1 statik 10,78 pay 2,82), kol_analiz.py + kol_rapor.py (5b bölümü), taslak_rapor.py (dış kol paragrafı kol analizine bağlı,
  "Dirsek çatalı kontrolü" bölümü id=catal, açık iş satırı). "Yeniden hesaplanacak" notu yok.
- Konsolda cp1254 hatası: taslak_hesap / raporlar PYTHONIOENCODING=utf-8 ile koşulmalı (betik sorunu değil).

## Durum: bitti. Açık: Duffy onayı; L4 1,07 < 1,2 (8 mm hesapla 1,23; onaylanmamış seçenek); M3x10 maliyet.json'da yok; 45° destek kozmetik basamak.

# Dış kol 7 → 8 mm (M3x12 + 2× DIN 125-A pul): CAD kontrol ajanı notları (ara kayıt)

Durum: başladı (24 Ekim 2026 gece). Görev: tasarım ajanının 8 mm işini (CATAL-NOTLAR.md, 2. bölüm) bağımsız doğrula; taslak_analiz çatal
kontrolü pulları saysın; tam çarpışma taraması (7 mm kapsamıyla aynı); kol_analiz t = 8; analiz/*.json, kol-analiz/, rapor.html'ler 8 mm ile;
rapora catal-5-7-8.png + 5/7/8 tablosu. Modüller, arayuz.py, montaj/, tasarim/cad/, demo, maliyet.json dokunulmaz; commit/push yok.

## Hazırlık (23:20–23:35)
- 7 mm temel çıktılar (analiz/, kol-analiz/, rapor.html, taslak-analiz.json, py'ler) scratch b7/'ye kopyalandı. DİKKAT: kutle.json ve taslak-analiz.json
  o anda zaten 8 mm (tasarım ajanı 23:16); 7 mm parça listesi referansı = 18:47 eski kod catal-geo.json (7 mm koşusu, parça parça).
- 7 mm tarama sonuçları repo içinde dondu: analiz/onceki-7mm/ (statik ×4, kol ×3, kolkol, kafa, kafakol ×5, catal-yeni, dogrulama, girdi-444, hesap,
  catal-geo-7-eskikod, kol-analiz-7mm.json). 5 mm = git 8ee72a0.
- taslak_analiz.py: b_catal → yeni_civata seti = 4 cıvata + 4 pul yığını (assert pul sayısı = 4 × [HORN_PUL_N > 0]); 8 mm koşusunda 7 mm ara çatal
  (TP.CATAL_ARA) aynı hedeflere `ara7_catal` / `ara7_civata` olarak. b_catal_geo yeniden yazıldı: pul kontrolü (dış yüze oturma, çatal/cıvata ile
  ortak hacim, 0,5 mm içeri kaydırılmış kopyayla oturma oranı, kenar boşluğu), cıvata ucu horn altı, servo gövdesi + çıkış mili mesafesi dirsek
  aralığında 1° (cıvata + pul), üst kol tüpü ↔ çatal ortak hacim / mesafe, eklenen hacim yalnız dış tarafta mı, tabla; parça farkları pullar
  ayrılarak eşlenir (fark_5 / fark_7). Çıktı adı: ortamda TASLAK_CATAL_DIS_KOL varsa catal-geo-<t>.json, yoksa catal-geo.json.
- kol_analiz.py: T_DIS_HESAP {5, 7, 8} (önceden {5, T, 8} → 8'de 7 düşüyordu), geometri etiketi "onceki (7 mm)"; `horn_sikma(t)` (pul etkisi).
- Koşu düzeni: bellek dar (15,3 GB, ~1,5 GB boş, kullanıcı uygulamaları açık; FreeCAD süreci ~0,55 GB) → en çok 5 paralel (scratch kos.sh).

## 1) Geometri: 5 ve 7 birebir (23:33, catal_geo env 5 / 7, yeni kod)
- 5: 1052 parça; 18:47 eski kod dökümü (catal-geo-5) ile parça listesi (ad/kütle/hacim/bb/merkez) farkı 0, eksenler aynı, cıvata kayıtları ve servo
  kasası mesafeleri aynı; git 8ee72a0 kutle.json farkı 0.
- 7: 1052 parça; 18:47 eski kod 7 mm dökümü (catal-geo.json) ile farkı 0, eksenler aynı; 8ee72a0'a göre yalnız 10 parça (2 çatal + 8 cıvata). 45° destek
  7'de kapalı (eski hâl). Cıvata ucu horn alt yüzünün 0,3 mm içinde, servo kasasına 3,3, çıkış miline 1,393 (5 = 7).

## 1b) Geometri 8 mm (23:38, catal_geo varsayılan; pul oturma oranı ölçütü düzeltilip 5/7/8 yeniden koşuluyor)
- 1060 parça = 1052 + 8 pul yığını. Pullar ayrılınca 5 ve 7 ile aynı sırada eşleşir; farklı yalnız 10 parça (2 Dirsek çatalı + 8 horn cıvatası
  M3x8/M3x10 → M3x12); eklem eksenleri aynı. 8ee72a0 kutle.json'a göre (pullar hariç) yalnız aynı 10 parça. Toplam 24.496,26 / 24.502,66 / 24.510,53 g.
- Çatal (sağ; sol ayna aynı): bbox x 154,0 … 227,9 (5'te 224,9): yalnız dış yüz +3; iç yüz 154,0 aynı; çıkan hacim 0; 1 katı, geçerli; 91.318,8 mm³.
  Eklenen 5.209 mm³, bbox x 213 … 227,9: dış kol + köprü + 45° destek uzantısı (destek x 213'ten başlar, köprü üstü).
- Delikler: 4 horn deliği eksen silindiri ortak hacmi 76,93 = 5 mm ile aynı; Ø9 merkez erişimi 0. Delik eksenleri (y, z) aynı.
- Cıvata M3x12: uç x 216,9 (5 = 7 = 8), horn'da 3,0 mm kavrama, uç horn alt yüzünün 0,3 mm içinde (dışarı çıkmıyor). Gövde delikte 0,2 mm boşluklu,
  baş pula, pul çatala temaslı (ortak hacim 0). Pul yığını x 227,9 … 228,9 (alt yüz = dış yüz, fark 0), Ø7, kenara en az 6,49 mm (taşmıyor).
- Dirsek 0 … 105° (1°): cıvata + pul ↔ servo kasası en az 3,30 (5 = 7 = 8), ↔ çıkış mili (kubbe) 1,393 sabit (5 = 7 = 8). İnmiyor.
- 45° destek: çatal ↔ üst kol tüpü ortak hacim 0 (5'te de 0), mesafe 0 (oturma teması, 5'te de 0); eklenen hacim tüpe 3,0 mm → yuvaya girmiyor
  (tasarım ajanının 23:15 düzeltmesi tutmuş).
- Baskı 74,0 × 73,9 × 72,0 mm → tabla 250 / hedef 230 içinde.
- Not: ilk ölçümde pul "oturma oranı" 0,48 çıktı: 1 mm'lik yığın 0,5 mm kaydırıldığı için ölçüt hatası (gerçek ~0,97, delik Ø3,4 > pul iç Ø3,2);
  kaydırma yığın kalınlığına çekildi. "Eklenen hacim yalnız dış tarafta" ölçütü de destek uzantısını yanlış işaretliyordu → iç/dış bölge ayrımına çevrildi.
- Yeniden koşu (00:01, düzeltilmiş ölçütler): 5 ve 7 yine eski kod dökümleriyle birebir. 8: eklenen hacim = eski dış yüz düzleminin dışı 4.228 mm³
  (x 224,9 … 227,9: dış kol + R16 uç + köprü) + içi 981 mm³ (yalnız 45° destek uzantısı, x 213 … 224,9, y 1220,1 … 1235 = köprü üstü; horn'a 21,2,
  servoya 24,9 mm). Pul oturma oranı %96,6 (eksik kısım delik Ø3,4 − pul iç Ø3,2 halkası).
- Sonuç: geometri TUTTU (yalnız dış yüz +3; delik/625ZZ/pim/eksen aynı; M3x12 + 2 pul doğru oturuyor, uç kasaya 3,3 / kubbeye 1,39; destek tüp yuvasına
  girmiyor; tablaya sığar; 5 ve 7 eskiyle birebir).

## 3a) catal bölümü (aynı hedeflere 5 / 7 / 8, analiz/catal-yeni.json, 3.310 s, 00:31) — iki kolda aynı
- Setler: eski (5 mm + M3x8), ara7 (7 mm + M3x10, TP.CATAL_ARA), yeni (8 mm + M3x12 + 4 pul yığını). 25/30 mm içindeki her hedef parçada en dar
  boşluk üç sette birebir (dirsek 10 hedef, omuz 7 hedef; fark 0). Kesişim hacmi her yerde 0.
- Dirsek 0…105° (1°) ön kol + el: çatal en dar 1,00 (On kol govdesi) 5 = 7 = 8; cıvata (+ pul) ↔ MG996R 3,30 = 3,30 = 3,30; sonra ısıl gömme M5 4,90,
  servo 5,66, kontra somun 5,70, kulak cıvatası 6,07 (çatal). Eş eksenli: cıvata ucu ↔ servo çıkış mili 1,393, pim pulu 1,5, mil ↔ çatal 1,6, pim cıvatası 2,25 (hepsi aynı).
- S1 × S2 5° (888 poz): çatal en dar 17,93 (göğüs bandı) 5 = 7 = 8; horn cıvataları / pullar hiçbir pozda hedeflerin 30 mm'sine girmedi.
- 7 mm ara set, 24 Ekim 7 mm koşusunun (onceki-7mm/catal-yeni.json) yeni_* değerleriyle aynı (1,00 / 3,30 / 17,93).

## 3b) Tam taramalar (8 mm, 23:33 → ; kos.sh, 5 paralel) — ara sonuçlar
- Kol sağ / sol tam (43.043 ölçüm, ~3.985 s): çakışma 0 → 0; en dar her hedef modülde 7 mm ile aynı (kabuk 0,50, omuz gövdesi 5,07, iskelet 45,1, kafa
  gövde 98,75; göbek 0,0 = S2 horn vidası ↔ mil eş eksen). 31 en dar çiftin tamamı 7 mm ile birebir; dirsek çatalı / cıvata / pul en dar 12 çiftin dışında.
- Kafa × kol ince sağ: 0 çakışma, en dar 7,71 (El ↔ yüz kabuğu) = 7 mm.
- Ev pozu 444: çakışma 0 yeni / 6 mevcut (S1 tamburu ↔ kol çatalı / tüp, tüp ↔ kaset kapağı; 125'te de var) = 7 mm birebir; aday çift 3.285 → 3.301 (+16: pullar).
- Kol ↔ kol 227 poz: 0, en dar 290 (aynı). Kafa × kol kaba sağ/sol: 0, 10,98 (aynı).
- Doğrulama: yeniden kurulum 1060 parça 24.510,52 g (kutle.json farkı 0,02 g, sıra/kütle aynı), FCStd 1060 nesne, STEP 1060/1060 eşleşti.
- Ev pozu 480 / 500 / 520: 16/6, 0/6, 0/6 (yeni/mevcut) = 7 mm, çakışma listeleri birebir; aday çiftler +16 (pullar).
- Kafa pan × tilt: 0, en dar her modülde aynı (kabuk 34,7, omuz 42,98). Kafa × kol ince sol 7,71 (aynı). S2 = 0 dahil 357 → 357 (El, çatal yok).
- Kol sağ yalnız dirsek: 0; en dar çiftlerin tamamı birebir (kabuk 17,95 göğüs bandı, iskelet 136,87, kafa 156,55, göbek 103,71, omuz 104,24).
- Sonuç: 8 mm hiçbir taramada yeni çakışma ya da daralma üretmedi (5 = 7 = 8). Bitti 01:01.

## 4) Dayanım (01:05; taslak_hesap.py → hesap.json, kol_analiz.py → kol-analiz.json; kütle 24.510,5 g)
- ×1,25 + DS3235 dış kol SF (L1 / L2 / L3 / L4): 5 mm 8,14 / 12,93 / 1,86 / 0,76; 7 mm 11,42 / 18,13 / 2,61 / 1,07; 8 mm 13,06 / 20,74 / 2,99 / 1,22.
  (DS3218MG: L3 2,72 / 3,81 / 4,36, L4 0,93 / 1,31 / 1,49.) Horn cıvatası delik ezilmesi L3 6,30 / 8,82 / 10,08, L4 2,57 / 3,60 / 4,11.
  Güncel kütleyle 5 mm L4 0,77 → 0,76 ve 8 mm 1,23 → 1,22 (çatal + cıvata + pul +7 g); 8 mm L4 1,22 ≥ 1,2: sınırda bandında, pay çok dar.
- L4'te baskı parçaları: dış kol 1,22 en zayıf, sonra kol çatalı ön kolu 1,41, tüp penceresi 2,09. Bağlantıda el yakası vidası ezilme 1,20 (değişmedi).
  Asıl L4 zayıfları servo milleri (S2 0,19, bilek 0,22, dirsek 0,25) ve S1 horn kanalı 0,37 (değişmedi, hız sınırı önerisi geçerli).
- Pul yığını (horn_sikma, tahmini): ezilme boyu (PETG'de t) ve horn'daki 3,0 mm kavrama değişmez; baş altı oturma 14,7 → 29,4 mm² → PETG kısa süreli
  izniyle (28,2 MPa) izinli ön yük 414 → 829 N, sıkma torku ~0,25 → ~0,5 N·m; 0,5 N·m'de basınç 56,8 → 28,3 MPa. Horn dişi sıyırma (Al 3,0 mm) 1.405 N →
  izinli ön yükte SF 3,39 (5/7) / 1,69 (8): 0,5 N·m üstüne çıkılmamalı. Ön yük PETG sürünmesiyle gevşer (her durumda), tork kayma olursa delik ezilmesiyle.
- Omuz S1 (×1,25 + DS3235): statik 10,78 → 10,85 kg·cm (pay 2,82 → 2,80), ivmeli 1,65 → 1,64, 2× payla elde yük 109 → 108 g. Dirsek geri sürme 1,46 (aynı).

## 5) Raporlar (01:06)
- taslak_rapor_analiz.py catal(): 5 / 7 / 8 özet tablosu (geometri, aynı hedeflere en dar, SF, sıkma) + catal-5-7-8.png bölüm içinde; geometri tablosuna
  pul yığını, tüp / destek, fark_5 / fark_7 satırları; aynı hedeflere tablosu 6 sütun (5 / 7 / 8 çatal, M3x8 / M3x10 / M3x12 + 2 pul); tam taramalar
  5 → 7 → 8 (7 = analiz/onceki-7mm); pul etkisi tablosu. CATAL_ADLAR'a "Catal-horn pulu" eklendi.
- taslak_rapor.py: dış kol SF metni 5 → 7 → 8 (önce "8 mm olsaydı" diyordu), 8 mm açık iş satırı kontrol yapıldı olarak; kol_rapor.py 5b başlık/metin
  8 mm kararı, 7 etiketi, sıkma tablosu, zayıf halka 6 satırı. rapor.html + kol-analiz/rapor.html yeniden üretildi ("yeniden hesaplanacak" notu yok).

## Durum: bitti (25 Ekim 01:10). Değiştirilen: taslak_analiz.py, taslak_rapor.py, taslak_rapor_analiz.py, kol-analiz/kol_analiz.py, kol_rapor.py,
  NOTLAR.md, analiz/*.json (+ onceki-7mm/, catal-geo-5/-7), kol-analiz/kol-analiz.json, rapor.html'ler. Modüller, arayuz, montaj/, tasarim/cad/, demo,
  maliyet.json'a dokunulmadı. Commit yok.
- Açık: BOM/maliyet.json'a M3x12 (8) + DIN 125-A M3 (16); L4 1,22 sınırın hemen üstünde (tahmini model; jest hız sınırı önerisi duruyor); horn cıvatası
  sıkma ≤ ~0,5 N·m montaj notu; 45° destek uzantısı tüpe 3,0 mm (temiz).
