**DÜZELTME GEREKLİ** (küçük; üretimden önce). Sağ / sol iddiası doğru, rapordaki tablo doğru, düzeltme yönü doğru. K52 / K64
metinleri kayıtlarla tutuyor; onay kaydında kritik değer değişmedi; kapsam temiz. Ama adım 0'a eklenen sağ / sol cümlesi FreeCAD'siz
hiçbir denetimden geçmiyor ve veri modundaki ASCII denetimini düşürüyor: tam üretim bugünkü haliyle 50 dakika sonunda "denetim"
hatasıyla sıfırdan farklı çıkar (D1). K1 kurulum testinin metni de bir yerde yanlış okunmaya açık (D2). İkisi de ucuz.

# F10m kontrolü · P10.7b2e (K52, K64, kare düzeltmeleri, sağ / sol K65)

16.11.2026. Dal `lale-duzeltme`, HEAD = `84f1a4a`; paket commit edilmemiş, farkı `git diff 84f1a4a` ile kendim okudum. Salt okuma:
depoda yalnız bu dosya yazıldı (bir kaza için bkz. "Kaza" bölümü). Sınamalar depo dışında, ağacın bir kopyasında (oturum scratchpad'i
`b2e-kontrol\kopya`) koştu; bozma denemelerim bellekte. FreeCAD, `rehber_veri.py`, `rehber_uret.py` tam koşusu yok. Bitişte depoda
`__pycache__` yok.

## Sağ / sol: kendi sonucum (raporu okumadan önce)

- CAD çerçevesi: +X "sağ", +Y yukarı, +Z ileri (yüz). Eksenler sağ elli; yukarı +Y, ileri +Z ise robotun kendi sağı
  ileri × yukarı = +Z × +Y = −X'tir. Yani **CAD "sağ" (+X) = robotun kendi solu = önden bakanın sağı.**
  Ön görünüm karelerinde +X ekranın sağında; montajcı robota önden bakıyorsa CAD adı gördüğüyle tutar.
- Yazılım (`git show origin/main:…`): `motorlar.cpp` `motorlar_hedef` w > 0 (sola) için `v_sol` < `v_sag`; yani `sol` adı robotun
  **kendi** solu olarak kullanılıyor. `odometri.py` aynı. `kanallar.yaml` `sag_*` = robotun kendi sağı niyetiyle yazılmış (jestler).
  Pinler `pinler.json` / `pinler.h`'de donanım adıyla (`SOL_*` = GPIO25/26, enkoder 16/15, IS 32) ve kablo tablosunda bu adlar −X
  tarafına gidiyor.
- Sonuç: donanım "sol" = −X = robotun kendi sağı; yazılım onu robotun kendi solu sanıyor. Bugünkü yazılımla `sur` w > 0 robotu kendi
  **sağına** döndürür; odometri yaw işareti ters. Düzeltme yazılım tarafında (pin adları ya da `motorlar_hedef` / odometri takası),
  kablo değil. Paketin iddiası ve yönü bununla aynı.
- `sag-sol-karari.md` § 3 tablosunu satır satır `pinler.json`, `pin-haritasi.md` ve `kablolar.json` ile karşılaştırdım: motor
  PWM / yön, enkoder A / B, IS 32 / 33, sonar Q01 / Q02, kol kanalları 0–3 / 4–7 eşlemesi doğru. Hata yok.
- K1 testi: önerilen beklenen sonuç (w = 0,2'de önden bakınca soldaki tekerler ileri; soldaki arka teker `sag` sayacını değiştirir)
  **düzeltilmiş** yazılımla tutar; bugünkü yazılımla bilerek tutmaz (iki gözlem de ters çıkar). Komut adları (`sur`, `odo_sifirla`,
  `odo` satırı `sol` / `sag`) OKU_BENI 0.5.0 ile aynı; `odo_sifirla` güç durumuna bakmaz (`seri_protokol.cpp`), sorun yok.

## D bulguları (düzeltilmeli)

### D1 (engelleyici, üretim) Adım 0 sağ / sol cümlesi ASCII denetimini düşürüyor, FreeCAD'siz sınamalar bunu görmüyor

- **Yer:** `tasarim/freecad/rehber/rehber_metin.py:101` (HAZIRLIK `is_`, yeni cümle); `tasarim/freecad/rehber/rehber_denetim.py:63-75`
  (`ASCII_TAMAM`), `:1067` (`kaynak_metinler` yalnız `ADIM`'ı dolaşır, `HAZIRLIK`'ı değil).
- **Ne yanlış:** Kaynak modu denetimi adım 0'ı hiç okumadığı için yeni cümle "temiz" görünüyor. Veri modunda (`denetle(V)`, tam üretimin
  sonunda `rehber_uret` "denetim" kapısı) adım 0 `is_` okunur ve beş kelime izinli listede yok: `rehberde`, `tablosunda`, `bakan`,
  `soludur`, `adlar`. `gecti` False → üretim b2d'deki gibi sıfırdan farklı çıkar.
- **Kanıt:** `veri_benzet.py` (eski üretim verisine FreeCAD'siz `rehber_gorunum.alan_isle` + `rehber_denetim.denetle`): adım 0 yeni
  cümleyi taşıyor; `ascii_kalinti_sayi` 5, tam olarak yukarıdaki beş kelime, hepsi `ilk_yer: adım 0 is_`. Doğrudan
  `ascii_kalinti([("adım 0 is_", HAZIRLIK["is_"])])` aynı beşi verir. (Aynı koşudaki `elektrik 1` eski verideki şema 4 metninden;
  kaynak düzeltilmiş, `rehber_denetim.py:1751` yalnız bozmada geçiyor, üretimde kalkar.)
- **Öneri:** Beş kelimeyi `ASCII_TAMAM`'a ekle (TR sözlüğünde ASCII karşılıkları yok, gevşetme olmaz); `kaynak_metinler` adım 0'ı da
  (`HAZIRLIK` `is_` / `kontrol` / `not_`) dolaşsın ki bir daha üretimde yakalanmasın. İkincisi `ZORUNLU` / onay kaydına dokunuyorsa
  onayı yenile.

### D2 (orta) K1 kurulum testinin sayaç cümlesi ve yazılım raporunun takas uyarısı

- **Yer:** `tasarim/freecad/rehber/rehber_metin.py:584-590` (K1 kontrol, sağ / sol testi); `planlama/d158/sag-sol-karari.md` § 3
  (`:75-82`).
- **Ne yanlış:**
  1. Test "F5 aşama 2'de devreye aldıktan sonra" diyor ama **motor / enkoder yön kalibrasyonundan (`*_MOTOR_TERS`,
     `*_ENKODER_TERS`, OKU_BENI) sonra** yapılacağını söylemiyor. Kalibrasyon yapılmadan teker ters dönebilir ya da sayaç azalabilir;
     montajcı yön hatasını taraf hatası sanar (ya da tersi).
  2. "soldaki arka teker `sag` sayacını … artırmalı" testi iki soruyu birleştiriyor: hangi sayacın değiştiği (taraf, K65) ve işareti
     (yön, `ENKODER_TERS`). Taraf testi için doğru ölçüt "hangi sayaç değişiyor"; artıp azalması ayrı bir kalibrasyon sorusu.
  3. `sag-sol-karari.md` § 3 "`*_TERS` tarafı düzeltmez" diyor (doğru), ama takas yapıldığında F5'te kalibre edilmiş `*_TERS`
     bayraklarının da **taraflarıyla birlikte takas edilmesi / yeniden kalibre edilmesi** gerektiğini söylemiyor; Efe pinleri takas
     edip bayrakları yerinde bırakırsa iki teker de ters döner. Asgari düzeltme listesinde BTS IS girişleri (GPIO32 / 33, `guc.*`
     arıza bayrağı) yok; tabloda var (`:62-63`), listede eksik.
- **Kanıt:** `git show origin/main:kod/esp32/src/motorlar.cpp` (TERS bayrakları taraf adına bağlı: `SOL_MOTOR_TERS` false,
  `SAG_MOTOR_TERS` true, `SOL_ENKODER_TERS` false, `SAG_ENKODER_TERS` true, hepsi TAHMİNİ); `OKU_BENI.md:32` (IS 32 / 33 `guc.*`).
- **Öneri:** Test cümlesine "motor ve enkoder yön testinden sonra (F5)" ekle; sayaç cümlesini "`sag` sayacı değişmeli, `sol` sabit
  kalmalı (artıp azalması yön kalibrasyonudur)" yap; F5 aşama 2'ye bu teste tek satır gönderme koy. Raporda § 3'e "takasta `*_TERS`
  bayrakları da taraflarıyla taşınır ya da yeniden kalibre edilir" ve "IS 32 / 33 (`guc.*`)" maddesini ekle. Metin değişikliği:
  `ZORUNLU` / onay kaydı gerekebilir.

## N bulguları (not düzeyi)

- **N1** `planlama/adim3/kablolar.json` G20 `rehber` hâlâ `[K1 17, K2 32]`; demet alt adımlarında G20'nin taban ucu artık K1'de.
  Tutarsızlık yok sayılabilir (iki uç iki adımda), ama kablo tablosunda "hangi adımda" sorusu belirsiz.
- **N2** G20 `boy_tahmin` üst sınırı yeni kablo yoluna göre denetlenmedi (yol 12 K1'e taşındı).
- **N3** `karar-kuyrugu.md` K64 gövdesindeki "Kayıtta olmayan …" paragrafı kapanış sonrası eskimiş; sayımlar (açık 48 / kapandı 17 /
  toplam 65) doğru.
- **N4** `rehber_metin.py:~1006` K2 kablo listesi hâlâ "Taban şeması 12'nin direkten kafaya çıkan kısmı eski" diyor; K2 karelerinde
  eski kablo yolu 12 direk boyunca soluk görünmeye devam ediyor, cümle doğru ama montajcıya hangi çizgiye bakacağını söylemiyor.
- **N5** 32.5'te AU3 / S10 / G17 için alt adım gönderme yok (şema var, metin anmıyor).
- **N6** D8 kuralı tam eşitliğe bakıyor: kamera tuple'ı 1e-6 farklıysa ya da `odak` aynı küme ters sıradaysa aynı kareyi geçiriyor
  (bozma 2 ve 3). Bugünkü veride böyle bir çift yok; kural sınırı.
- **N7** Kapalı-karar düzenli ifadesi `\bK(1|10|11|14|52|64)\b(?! a)` K65'i içermiyor: "Sağ / sol karar bekliyor (K65)" yazılsa
  yakalanmaz (bozma). K65 metinde "karar" diye geçmiyor; ileride gerekebilir.
- **N8** TÜBİTAK kaynakları depoda `.gitignore`'da; `sag-sol-karari.md` onlara atıf yapıyor, Efe depodan göremez.
- **N9** 17.11 mini haritada halka yok (odak var ama küçük harita vurgulamıyor); kare doğru, gezinme yardımı eksik.
- **N10** Testteki w = 0,2 rad/s yaklaşık %11 PWM; takozdaki tekerler sürtünmeyle dönmeyebilir. Metin "gerekirse yinele" diyor, ama
  dönmezse w'yi artırma izni yok.
- **N11** 17.1, F1, B6a ve birkaç kartta "kare düzeltmesi" yalnız metin (yer tarifi); kare değişmedi. Bu dürüstçe "Karede görünmez" ya
  da "Karede yer" diye yazılmış, yanıltıcı değil. 17.4 / 17.5 / 17.10 / 17.11 / 31.2 / 31.4 / 32.x gerçek kamera / saydam / odak /
  şema değişikliği.
- **N12** "528 ad" gibi sayımları yeniden saymadım.
- **N13** Adım 0'a "arkadan çalışırken sağ / sol ters okunur" gibi tek ipucu eklenebilir (K1 / K2 kareleri arkadan).
- **N14** `koordinat` alanı eski veride "+X sag"; yeni metin (`rehber_veri.py:951`) doğru ve ASCII temiz, ama ancak FreeCAD koşusundan
  sonra veride görünür.

## Sınamalar ve sonuçlar (FreeCAD'siz, kopya ağaçta)

| Sınama | Sonuç |
| --- | --- |
| `rehber_denetim` kaynak modu (ASCII, ZORUNLU, SIRA, CÜMLE, elektrik, D1–D8, bozmalar) | geçti (adım 0'ı okumuyor: D1) |
| `rehber_denetim` veri modu, eski veri + `alan_isle` (`veri_benzet.py`) | **ascii 5**, zorunlu eksik 0, yasak 0, çelişki 0 → gecti False (D1) |
| `veri_is_ana_bozma_denemesi`, `_veri_benzetimi` | yakalıyor |
| Onay kaydı (`rehber_kritik_onay.json`) HEAD ile fark | yalnız beklenen cümle özetleri; kritik değer değişikliği 0 |
| `F10l-birlesim.py` (taban 84f1a4a) | beklenen listeler (B2E, B2E_K2) gerçek cümle farkıyla aynı |
| `F10d-dogrula.py` sentetik `sema_karede_bozma` | 5 / 5 yakaladı; eşikler PX 30, oran 0,20 (17.10 B01 oranı 0,68) |
| Önizleme / tarayıcı (kopyada, FCStd kopyalandı) | 40 alt adım, 40 geçti; tarayıcı 5 / 5, konsol hatası 0; en düşük çizim oranı 0,0804 |
| `kablolar_uret` + `kablolar_denetim` | GEÇER; `kablolar.md` güncel |
| `rehber_kablo --veri` | geçti |
| `F9c-uret.py --kuru` | geçti (GRUP K64 / K65) |
| Kendi bozmalarım (`bozma_kontrol.py`, 15) | 11 beklendiği gibi. Tutmayan 4: D8 1e-6 ve odak sırası (N6), K65 (N7), "solunda" (benim hatalı denemem: Türkçe yazımı zaten doğru) |

Bozma ayrıntısı: D8 kopya bakış yakalandı; şemalı alt adımda aynı bakış doğru geçirildi. D4: yol 12 iki alt adımda, yanlış alt adımda,
`KABLO_KAPI_ISTISNA` silinince: üçü de yakalandı. Elektrik: K64 / K52 "karar bekliyor", K60 "kararlaştırılmış": yakalandı. ASCII:
`sagda`, `onden`, `sagdakiler` yakalandı; yeni izinli kelimelerin hiçbirinin sözlükte ASCII karşılığı yok (gevşetme yok). D6'nın yeni
cümlesi ("dalını (G20) bağla;") ve ASCII listesi bozmaları geçti.

Kapsam: K50 dokunulmamış; CAD model dosyaları (`*.FCStd`, model betikleri) dokunulmamış; üretilmiş rehber çıktısı (`rehber/veri`,
`rehber/goruntu`) elle düzenlenmemiş; paket dışı dosya yok; eski kir (kabuk görselleri, `yerlesim-kontrol.json`, `dongu-158.md`)
anlık görüntüyle aynı hash'te.

## Kaza (bildirim)

`py -3 planlama/d158/F9c-uret.py --help` betiği bayrağı tanımadan üretti ve depodaki `planlama/d158/sonuc-rapor.html`'in üzerine
yazdı. Hemen `git restore -- planlama/d158/sonuc-rapor.html` ile geri aldım; dosya HEAD ile bayt bayt aynı, `git status` anlık
görüntüyle aynı. Sonra yalnız `--kuru` koştum.

## Bakamadıklarım

- FreeCAD yolu: `rehber_veri.py` desen → ref ve sema → `_sema` atamaları; yol 12'nin 17.10'a, U06'nın 32.4'e, AU3'ün 32.6'ya gerçekten
  doğru geometriyle düşmesi; yeni kamera açılarının gerçek kareleri.
- PDF (sayfa sayısı ~85–86), koyu tema, lejant beyaz satırının gerçek görünümü.
- Donanımda K1 testi (gerçek tekerler, w = 0,2'nin yetip yetmediği).
- TÜBİTAK v14 docx'teki sağ / sol kullanımı; Efe'nin origin/main dışındaki dalları.

## Üretimden sonra gözle bakılacaklar

- 17.10: kablo yolu 12 K1 karesinde, kırpma içinde ve vurgulu.
- 32.4: yalnız U06 şeması; taban ucu doğru yerde mi (eski yol 12 ucu değil).
- 32.5 / 32.6: AU3 görünüyor ve vurgulu.
- 17.1: sarı çizgi SV3 mü; 17.4: G12 görünüyor mu; 31.2: USB soluk ama seçilebilir mi.
- Lejant adları (beyaz "açık temada koyu çizilir"), `koordinat` satırı yeni metinle, koyu tema.
- PDF'te adım 0 sağ / sol cümlesi ve K1 kontrolündeki test metni tam ve kırpılmadan.
