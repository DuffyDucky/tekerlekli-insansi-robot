# Kol ×1,25 + DS3235: CAD tasarım ajanı çalışma notları (ara kayıt)

Durum: başladı (24 Ekim 2026). Karar (Duffy, 24 Ekim 2026): taslak-170 kolu ×1,25, omuz S1/S2 (iki kol) DS3218MG yerine DS3235.

## Okunan bağlam
- Kol zinciri (omuz yereli, S1 ekseni y 0): dirsek ekseni y -173 (tüp ucu -140'tan 33 aşağı), bilek horn s 83,1 (y -256,1), el ucu s 152,5 (y -325,5).
- ×1,15 taslak: tüp +30 (100 → 130), el yakası +19 (13,6 → 32,6) → kol 374,5 mm. Dirsek global y 1187, bilek 1103,9, el ucu 1015,5 (S3 1390).
- Kol analizi önerisi (kol-analiz/kol_rapor.py satır 313, 355): ×1,25'te ek 32,4 mm'yi tüpe / ön kola ver, yaka 32,6 kalsın; ön kol uzarsa bilek servosu yerini (ön kol ucunda) koru.
- ×1,15 grup kütleleri (sağ): Kol 159,0 g, dirsek çatalı (UstKol) 103,5, ön kol + 2 servo (OnKol) 188,9, El 86,3. S1 statik moment (kol yatay) 100.669 g·mm.

## Dağılım kararı (gerekçe)
Hedef 325,5 × 1,25 = 406,875 → ek 32,4 mm (yuvarlak; kol 406,9, ×1,2501).
- Tümü tüpe: S1'in taşıdığı tüm dirsek grubu (UstKol + OnKol + El ≈ 379 g) 32,4 mm uzaklaşır → ΔM_S1 ≈ +15.000 g·mm.
- Tümü ön kola (dirsek ile bilek servosu arası): yalnız bilek servosu + kulak civataları (70 g) + El (86 g) + ön kol uzatması (~11 g) uzaklaşır → ΔM_S1 ≈ +8.000 g·mm (kaba).
- S1 sınırlayıcı eklem (kol analizi: DS3235 ×1,25 ivmeli pay 1,59 < 2); dirsek MG996R'ın payı büyük (statik ~1,8-2,0 kg·cm / stall 9,4) → ek ön kola.
- Tüp +Y basılıyor (eğilme katmanlar arası); tüpü uzatmamak tüp kökü momentini de artırmaz.
- Oran: üst kol (S1 → dirsek) 203 / ön kol (dirsek → bilek) 83,1 → 115,5 / el (bilek → uç) 88,4; insan oranına (üst/ön ≈ 1,27) yaklaşır (2,44 → 1,76).
- Seçim: UST_KOL_UZAMA 30 (değişmez), ON_KOL_UZAMA 32,4 (yeni), EL_UZAMA 19 (değişmez).

## Uygulama planı
- taslak_ayar.py: KOL_SECENEK {"115", "125"} + TASLAK_KOL ortam değişkeni (varsayılan 125); OMUZ_SERVO (DS3235, eski DS3218MG) parametresi.
- taslak_parcalar.py: ön kol gövdesini s = 42,75'te (ara duvar altı 42 ile bilek servosu tabanı 43,5 arası) kes, alt parçayı ON_KOL_UZAMA aşağı taşı, aradaki U kesitini (yan duvarlar + ön duvar) uzat. Bilek servosu + mili + 4 M4 + 4 somun + El grubu ON_KOL_UZAMA ek aşağı. kaydir(): El grubu V_DIR + (0, -f, 0).
- S1/S2 servo parçaları: ad/kod "DS3235", kütle 60 g (aynı), not: yükseklik 38,5/40/40,5 → kumpasla doğrulanacak.

## Yapılanlar (24 Ekim, ara)
- taslak_ayar.py: KOL_SECENEK + TASLAK_KOL (varsayılan 125), ON_KOL_UZAMA 32,4, ON_KOL_KES_S 42,75, OMUZ_SERVO (DS3235) + TASLAK_OMUZ_SERVO.
- taslak_parcalar.py: ön kol kesit uzatması (onkol_uzat), V_EL (bilek servosu + El grubu), kaydir() El grubu, S1/S2 servo yeniden adlandırma (durum değişti, rijit v), eski_ad alanı.
- taslak_montaj.py: el ucu toplam uzamadan, bolum_boylari_mm, oran sözlüğü (seçim, karar, servo), kısa kol taraması (sağ kol 240 poz), eski_ad eşlemesi.
- taslak_analiz.py: KARSI eşlemesi eski_ad ile; ozel_parca'ya On kol govdesi. taslak_hesap.py: el ucu ofseti KOL_BOY_YENI - KOL_BOY_ESKI (tek satır).
- taslak_rapor.py: karar kutusu, kol bölümü (dağılım tablosu + gerekçe), kalıcı kol-analiz bağlantısı (kol + kol oranı bölümleri), analiz bölümlerinde "yeniden hesaplanacak" notu (analiz girdisinin bilek ekseni / servo adı güncel değilse otomatik), açık işler (onaylanmamış öneriler listede, uygulanmadı).
- taslak_rapor_analiz.py: açık işlerde "Kol oranı kararı" ve "Omuz servosu" satırları karara göre.
- taslak_gorsel.py: taslak-kol.png (sağ kol yakın).

## Sonuç (24 Ekim 2026, taslak_montaj 446 s + taslak_gorsel + taslak_rapor)
- Eksenler (sağ; sol X aynası): S1 (150; 1390; 0), dirsek (216,6; 1187,0; −1,25) değişmedi, bilek (185; 1103,9 → 1071,5; −1,25), el ucu (185; 1015,5 → 983,1; −1,25). Bölümler: üst kol 203,0 / ön kol 115,5 / el 88,4 = 406,9 (×1,2501).
- Ön kol gövdesi: kesit 339,3 mm² (tek U), 1 katı, 42,2 → 53,4 g; baskı 129,6 × 128,9 × 33,5 (tablaya sığar).
- Kütle 24.473,9 → 24.496,3 g (paylı 24.941,3), AM (−0,11; 566,92; −10,72). Kol (Kol + dirsek, kol başına) 537,7 → 548,9 g; S1 statik moment (kol yatay) 100.669 → 109.146 g·mm (125 cm'ye göre ×1,21 → ×1,31).
- Kol grupları (sağ): S1 ile 724,1 g AM y 1241,2; S2 ile 548,9 g y 1191,2; dirsek ile 286,4 g y 1103,7; bilek ile 86,3 g y 1025,7.
- Kontroller: 1052 parça, STEP 1052 katı, solve 0; ev pozu 4 çakışma (hepsi 125'te de var: tüp ↔ S1 tamburu / kaset kapağı); kafa süpürmesi 0/24; kol kaba ızgara 0/240, el en alt y 982,5; dirsek çatalı ↔ göğüs bandı 5,9 mm.
- Baskı: 61 parça, 250'ye sığmayan 0, 230'u aşan 2 (Etek arka/ön sağ, önceden de).
