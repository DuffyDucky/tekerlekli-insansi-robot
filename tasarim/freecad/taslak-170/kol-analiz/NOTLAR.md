# Kol analiz ajanı: çalışma notları (ara kayıt)

Durum: başladı (2026-10-24). Bulgular ilerledikçe buraya eklenir.

## Okunan bağlam (özet)
- Servo hattı 6 V (XL4016 A/B, 8 A modül, sürekli <= 5 A önerilir), hat sigortası 7,5 A, XL->dağıtım 16 AWG, servo uzatma 22 AWG ~1,3 m (+0,435 m taslakta). Hat A: sağ kol 4 servo + pan; B: sol kol + tilt.
- E1 servo akım tahmini: jest S1 0,8 / S2 0,6, yoğun 1,5 / 0,9 A; kalkış 2,5 A; DS3218 stall 2,6 A @6,8 V (aifitlab).
- taslak_hesap.py: kol_servo(rb, ek) STALL_DS=20 global; ALFA = 26,2 rad/s2 (60° 0,4 s üçgen). Kol oranı ek boyu tüp:yaka = 30:19; birim kütle tüp 0,403 g/mm, yaka 0,597 g/mm.
- hesap.json: x1,15 S1 statik 9,87 kgcm (pay 2,03), ivme +6,49 (toplam 16,37 -> 1,22); x1,25 11,14 / +7,98; x1,36 12,56 / +9,78. Dirsek MG996R statik 1,77/1,97/2,17 kgcm (stall 9,4 @4,8V).
- Malzeme: PETG-CF (Polymaker Fiberon PETG-rCF08) = omuz yuvası, rulman kapağı, göbek, kol çatalı. PETG (Microzey HS PETG) = üst kol tüpü (Ø56/Ø51,3), dirsek çatalı, ön kol, bilek flanşı, el.
- Fiyatlar (maliyet.json): DS3218MG 964,5 TL Robocombo (4 + 1 yedek), MG996R 199 TL, XL4016 242,4 TL.

## 1) Servo verisi (web, 24 Ekim 2026)
- Robocombo "DSSERVO DS3235 35kg Servo Motor - 180 Derece - Su Geçirmez" https://www.robocombo.com/dsservo-ds3235-35kg-servo-motor-180-derece-su-4148 : sellPrice 1.255 TL, indirimli 1.171,50 TL (KDV dahil), stok 134, SKU 2402150004. Tablo: çalışma 6-7,4 V; tork 29 (5 V) / 32 (6 V) / 35 kg·cm (7,4 V); hız 0,13/0,12/0,11 s/60°; PWM 500-2500 us; boyut 40×20×40. DİKKAT: açıklama metni "RDS3235 ... U Servo Braket Dahil" diyor (kopyala-yapıştır karışıklığı) -> satıcıya sorulacak. Ayrı ürünler: Coreles DS3235 (-4534) 1.796,50 TL; Coreles RDS3235 (-4614) 1.707 TL; BLS3235 (-4613).
- DS3235 datasheet (Rochester ME240 kopyası, https://hajim.rochester.edu/me/sites/kelley/me240/DS3235-270_datasheet.pdf, arama özetinden; PDF indirilemedi): 5-7,4 V, 29/32/35 kg·cm @5/6/7,4 V, stall akımı 1,9/2,1/2,3 A (6 V'ta 2,1 A), 40×20×38,5 mm, 60 g, dişli oranı 373, coreless. Diğer satıcı tablolarında stall 2,2-3,9 A -> tasarımda 3,0 A @6 V (tahmini, ihtiyatlı).
- probots DS3235: 40×20×40,5, 60 g, çift bilyeli, 4,8-6,8 V (çelişkili).
- DS3218 PRO datasheet (itgresa PDF, proje kaynağı): 40×20×40,5 (çizim 40,4), kulak 54,5, delik 49,5×10, kulak altı 27,7, 60 g, oran 236, 21 kg·cm @5 V / 23,5 @6,8 V, stall 2,1 A @5 V / 2,9 A @6,8 V. Proje 20 kg·cm kullanıyor (DS3218MG standart; 6 V'ta ~20, tahmini).

## Malzeme (kaynaklı)
- Polymaker Fiberon PETG-rCF08 TDS V1.0 (https://fiberon.polymaker.com/wp-content/uploads/TDS_FIBERON-PETG-rCF08_V1.0_EN.pdf): E X-Y 3710 / Z 2652 MPa; çekme X-Y 59,8 / Z 41,1 MPa; uzama X-Y 5,7 / Z 1,9 %; eğilme X-Y 94,6 / Z 47,8 MPa; HDT 65,7 °C @1,8 / 68,6 @0,45 MPa; Tg 69,7 °C; yoğunluk 1,30. Numuneler %100 dolu.
- Prusament PETG TDS v1.1 16-02-2022 (kopya https://www.3dprintergear.com.au/assets/files/technical-data-sheet%20(1).pdf): baskı numune akma yatay 47±2 / dikey xz 50±1 MPa, E 1,5 / 1,6 GPa, eğilme 66 / 70 MPa, katmanlar arası yapışma 18±4 MPa, HDT 68 °C. Microzey HS PETG için veri yok -> Prusament değerleri temsilî (tahmini).
- Rulman: SKF 61808-2RS1 C 4,49 / C0 3,75 kN (RS Online 2076965); SKF 625-2Z C 1,14 / C0 0,38 kN (RS 2867827). KWC/BGR eşdeğeri -> tahmini.
- Servo mili radyal yük üreticide yok. Karşılaştırma: ROBOTIS XM430-W350 radyal 40 N (horn'dan 10 mm), eksenel 20 N (https://emanual.robotis.com/docs/en/dxl/x/xm430-w350).
- Isıl gömme somun çekme: kaynaklı test verisi bulunamadı -> geometriden (π·D·L·τ, τ = 0,5 × katman yapışması) tahmini.

## Yapısal model kararları (ara)
- Göbek: S1 horn (x≈148,4) ile 6808 merkezi (x 156,5) arası 8,15 mm. 6808 moment taşımazsa S1 mili radyal yük = M_dik / 8,15 mm (üst sınır). S2 torku göbeğe M_z olarak biner.
- Kol çatalı: S2 horn (z≈28) ile 625ZZ (z≈-30,5) arası 58,5 mm -> S1 yönü moment çift kuvvet.
- Baskı yönleri: üst kol tüpü +Y (katman eksene dik -> eğilme katmanlar arası!), kol çatalı -Z, dirsek çatalı -Y (kollar katmanlar arası), ön kol -Z (iyi), bilek flanşı -Y, El +Y (yaka katmanlar arası).

## Plan (24 Ekim, yazılıyor)
- kol_analiz.py (sistem Python, FreeCAD yok): taslak_hesap.Robot + kopyalanmış servo ızgarası (doğrulama hesap.json ile), 1-B kol kütle modeli (kesit momentleri), yük durumları L1 statik / L2 ivmeli / L3 stall (S1, S2, S1+S2) / L4 darbe (enerji: v·sqrt(m_eff·k), k = servo 1° @stall + tüp eğilme + temas 20 N/mm, tahmini).
- Emniyet: sigma_izin = sigma_malz(yön) × k_dolu × k_T × k_creep; güvenli >= 2, sınırda 1,2-2, yetersiz < 1,2.
- Çıktı kol-analiz.json; kol_rapor.py -> rapor.html.

## İlk koşu (kol_analiz.py, 2 dk)
- Izgara hesap.json ile aynı (doğrulandı).
- S1 statik pay (servo gerilimi ~5,5-5,6 V'ta): DS3218 2,01/1,78/1,58; DS3235 3,08/2,73/2,42 (x1,15/1,25/1,36). İvmeli: DS3218 1,21/1,04/0,89; DS3235 1,86/1,59/1,36.
- 2x statik payla elde yük: DS3218 ~0; DS3235 143/101/60 g.
- Hat A yoğun: DS3218 5,3-6,3 A; DS3235 4,9-6,1 A (DS3235 aynı torkta daha az akım). Tepe DS3235 ~7,7 A (XL 8 A sınırında). S1 stall anında servo gerilimi ~5,5 V (22 AWG).
- Darbe (jest tepe hızı, sert engel): omuzda 85-127 kg·cm = stall'ın 3-5 katı (tahmini model).

## İkinci koşu bulguları (servo mili/6808 modeli düzeltildi)
- Baskı parçaları L1-L3'te hep SF >= 2 (en düşük: dirsek çatalı dış kolu L3 ~2,1, x1,36 DS3235 - dirsek geri sürme). L4 darbede: dirsek çatalı dış kolu 0,76, yaka vidası ezilme 0,89, tüp penceresi 1,82, kol çatalı ön kolu 1,25 (x1,36 DS3235).
- Zayıf halkalar plastik değil: servo milleri (S2 horn tarafı radyal L2-L3, bilek konsol L3), 25T Al horn kanalı (DS3235 stall SF 1,30; DS3218 2,05), dirsek MG996R'ın DS3235 tarafından geri sürülmesi 1,30-1,33×.
- Darbe güvenli hız (moment <= stall): DS3235 1,3-1,6 rad/s (jest tepe 5,24).
- Öneri adayı: x1,25 + DS3235 (statik 2,73 / ivmeli 1,59; 6,4 V + 20 AWG ile 2,88 / 1,68, 121 g). x1,36 ancak 60°/0,5 s profil ile.

## Teslim (24 Ekim 2026)
- kol_analiz.py -> kol-analiz.json; kol_rapor.py -> rapor.html. taslak-170/rapor.html'e "Kol oranı" başlığının altına bağlantı satırı eklendi (taslak_rapor.py yeniden koşulursa satır kaybolur).
- Öneri: x1,25 + DS3235 (+ 20 AWG S1/S2 uzatma, XL 6,4 V, kelepçeli horn, S2 destek rulmanı, 6808 çifti, yazılım hız/temas sınırı).

## Kontrol ajanı yeniden koşusu (24 Ekim 2026, karar: ×1,25 + DS3235, ek ön kolda)
- kol_analiz.py tabanı artık ×1,25 taslak geometrisi (girdi + kutle.json); ×1,15 = ön kol uzatması geri alınır (gerçek ×1,15 ile birebir: S1 9,87, dirsek 1,77),
  ×1,36 = ek ön kola (doğrusal). Gruplar taslak_hesap.kol_gruplari'ndan. Ön kol kesitleri CAD dilimlerinden (üst s 30 pencere Wz 1.073; alt U s 42).
- Önceki sonuç (git e8697ac) kol-analiz.json 'onceki', bu koşu 'ozet'; fark rapor Bölüm 8. Ayrıntı: ../KOL125-KONTROL-NOTLAR.md.
- ×1,25 + DS3235: S1 2,84 / 1,66, elde 111 g; dirsek geri sürme 1,32 -> 1,46; dirsek çatalı dış kolu L3 SF 2,07 -> 1,86 (sınırda), L4 0,77.

## Dirsek çatalı dış kolu 5 → 7 mm (kontrol ajanı, 24 Ekim 2026 akşam)
- kol_analiz.py: dış kol kalınlığı `T_DIS = TA.CATAL_DIS_KOL` (kesit t × 32, horn cıvatası ezilme boyu t, çift kuvvet kolu 61 + (t − 5)/2 mm);
  her varyant × servoda `catal_dis_kol` {5, 7, 8} (8 yalnız hesap); `catal5` = git 8ee72a0 özeti. t = 5 → 8ee72a0 ile 672 satır fark 0.
- ×1,25 + DS3235 (7 mm, yeni kütleler): dış kol L3 1,86 → 2,61, L4 0,77 → 1,07 (8 mm hesap 2,99 / 1,23); horn cıvatası ezilme L3 6,30 → 8,82.
  S1 statik 10,72 → 10,78 kg·cm (pay 2,84 → 2,82, ivmeli 1,66 → 1,65, elde 111 → 109 g). L4'te en zayıf hâlâ dış kol (1,07), sonra kol çatalı ön kolu 1,42.
  Ayrıntı: ../CATAL-KONTROL-NOTLAR.md.

## Dirsek çatalı dış kolu 8 mm (karar Duffy 25 Ekim; kontrol ajanı 24 Ekim gece)
- kol_analiz.py: T_DIS_HESAP {5, 7, 8} (8 varsayılanken 7 düşüyordu), 7 etiketi "onceki (7 mm)"; `horn_sikma(t)`: M3x12 + 2× DIN 125-A pul etkisi
  (baş altı oturma 14,7 → 29,4 mm², izinli sıkma torku ~0,25 → ~0,5 N·m, Al horn dişi sıyırma SF 1,69 izinli ön yükte; tahmini).
- ×1,25 + DS3235 dış kol SF L3 1,86 / 2,61 / 2,99, L4 0,76 / 1,07 / 1,22 (5 / 7 / 8, güncel kütleyle). S1 statik 10,85 kg·cm (pay 2,80, ivmeli 1,64, elde 108 g).
  Ayrıntı: ../CATAL-KONTROL-NOTLAR.md.
