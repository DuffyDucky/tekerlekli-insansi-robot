# A1 dirsek ajanı günlüğü (düzeltme planı 1. adım: M2, D3, C6)

Başlangıç: 14 Ekim 2026. Kapsam: arayuz (GECME / tüp-bilezik), dirsek/, rapor betik metinleri, carpisma_kos.py.

## Durum
- [x] M2 arayuz.GECME + dirsek bileziği 0,1 -> 0,25
- [x] M2 dirsek kontrolü tüp iç çapını A.GECME'den okusun, kabul 0,3
- [x] D3 rapor betiklerinde eski değer metinleri
- [x] C6 carpisma_kos.py izleme listesi + rapor uyarısı
- [x] dirsek yeniden üret + kontrol

## Bulgular (başlangıç)
- arayuz.GECME yalnız tup_pim=0,25 içeriyor. DIRSEK["tup_ri"]=25,5 eski sabit (gerçek tüp iç yarıçapı omuzda 25,4+0,25=25,65).
  Kontrol "pim-tüp boşluğu" bu yüzden 0,1 gösteriyor, gerçek 0,25.
- Bilezik iç yarıçapı dirsek_parcalar.py'de elle 28,1 (tüp dış 28,0 -> 0,1 boşluk).

## M2 uygulandı (14 Ekim 2026)
- `arayuz.py`: `GECME` = {tup_pim 0,25, **tup_bilezik 0,25 (yeni)**, **kabul_max 0,3 (yeni)**}; yeni `TUP_PIM_R = 25,4`;
  `DIRSEK["tup_ri"]` elle 25,5 yerine `TUP_PIM_R + GECME["tup_pim"]` (= 25,65); yeni `DIRSEK["bilezik_ri"]` = 28,0 + GECME["tup_bilezik"] (= 28,25).
- `dirsek/dirsek_parcalar.py`: bilezik iç yarıçapı elle 28,1 yerine `R_BIL_IC = tup_ro + GECME["tup_bilezik"]`; pim yarıçapı `A.TUP_PIM_R`; V oluk dış kenarı `D["tup_ro"]`.
- `dirsek/dirsek_montaj.py`: tüp iç yarıçapı `A.DIRSEK["tup_ri"]` (GECME'den) okunuyor ve omuzdaki gerçek tüp geometrisiyle (dilim) çapraz doğrulanıyor;
  pim/tüp ve bilezik/tüp boşluk kabulü `0 < b <= GECME["kabul_max"]` (0,3; eskiden 0,2) ve tasarım değerine eşitlik.
- Önce: pim-tüp boşluğu kontrolde 0,10 görünüyordu (eski sabit 25,5; gerçek geometri zaten 0,25 idi), bilezik-tüp 0,10.
  Sonra: pim-tüp 0,25, bilezik-tüp 0,25, tüp iç yarıçapı 25,650 (geometri = arayüz); kabul <= 0,30.
- dirsek_montaj.py koşusu (47 s): geçersiz 0, çoklu katı 0, ev pozu çakışma 0, omuz arayüzü çakışma 0, bağlantı 22/22 tamam, 5/5 omuz-arayüz kontrolü geçti.
  Dirsek çatalı 89,45 -> 88,78 g (bilezik duvarı 2,9 -> 2,75 mm); dirsek modülü 369,3 -> 368,7 g; AM (189,4; -206,4; -1,6).
  Dirsek serbest aralık -60...110 (arayüz 0...105), bükülme boşluğu 105°'de 4,19 mm: değişmedi. Baskı: 4/4 sığar, destek sorunu 0.
- Log: %TEMP%\dirsek_montaj_a1.log

## D3 uygulandı (rapor betik metinleri)
- `dirsek/dirsek_rapor.py`: BAGLANTI satırı (tüp içi Ø51 / 0,1 mm / iç Ø56,2 eski) ve "Geçme toleransları" maddesi artık `A.TUP_PIM_R`, `A.DIRSEK`, `A.GECME` ile üretiliyor
  (Ø50,8; tüp içi Ø51,3; her yanda 0,25; bilezik iç Ø56,5; tüp dışı Ø56,0; kabul ≤ 0,30). Pim giriş boyu analiz kontrolünden.
  Regresyon paragrafı (elle yazılı "202 / 202 parça, 1,3·10⁻⁹ mm³, git ile geri alındı") `omuz|iskelet/regresyon/fark.json` + `taban/regresyon/moduller.json`'dan üretiliyor.
  `rapor.html` yeniden üretildi (python dirsek_rapor.py); çıktı kontrol edildi.
- `iskelet/iskelet_rapor.py`: omuz regresyonu notu ("çakışan pozlar ... önce de aynıydı") tarama satırlarından üretiliyor (kol↔göbek 8, göbek↔gövde 0, kol↔gövde 94, önce=sonra).
- `kabuk/kabuk_rapor.py`: "Cam ön yüzü duvar iç yüzüne 0,1 mm" -> `kabuk-analiz.json bosluk.cam_duvar_mm`.
- `taban/taban_rapor.py`: regresyon etiketi ("arayuz.py'ye taban eklendikten sonra") -> ölçüt sayısı / REGM tarihi. "uç somunu 0,1 mm" satırı başka ajan tarafından zaten PLAKA_GECME değişkenine bağlanmıştı (dokunmadım).
- omuz/kafa/montaj rapor betiklerinde eski değer metni bulunamadı. Not: iskelet/kabuk/taban rapor.html'leri yeniden üretmedim (başka ajanlar çalışıyor); betikler sözdizimi + parçacık testinden geçti.

## C6 uygulandı (`tasarim/freecad/carpisma_kos.py`)
- İzleme listesi (`KAYNAK_SABIT` + `kaynak_listesi()`): önceki 10 dosyaya `sigma_profil.py`, `kafa/kafa-analiz.json` eklendi; tüm `*_lib.py` (kök + modül klasörleri: ortak, dirsek, kabuk, kafa, omuz, taban) dinamik glob ile izleniyor (yeni kütüphane kendiliğinden girer).
  Önceki listede `omuz_lib.py`, `dirsek_lib.py`, `kabuk_lib.py`, `kafa_lib.py` da yoktu. Kaynak özeti (md5) her çağrıda listeyi yeniden okur.
- Yeni işlevler: `eskime()` (kayıtlı özetler vs bugün; değişen / kayıtta olmayan / kaynağı eski bölümler), `eskime_metni()`, `eskime_html()` (rapor uyarı kutusu, stderr'e de basar), CLI `python carpisma_kos.py kontrol` (eskiyse çıkış kodu 1). `birlestir()` sonunda da uyarı basar.
- Raporlar: dirsek, iskelet, kabuk, kafa, montaj, taban rapor betiklerine `<h1>` satırından sonra tek satır eklendi (`H.append(__import__("carpisma_kos").eskime_html())`); omuz raporu carpisma-sonuc.json okumuyor, dokunmadım.
- Şu anki durum (`kontrol`): ESKİ. Kosudan sonra değişen: arayuz.py, dirsek_parcalar.py, kabuk_parcalar.py, omuz_parcalar.py, ortak_lib.py, taban_parcalar.py (iki kısmı başka ajanların); kayıtta özeti olmayan: dirsek/kabuk/kafa/omuz _lib.py, sigma_profil.py, kafa-analiz.json; 9 bölümün hepsi eski. C7 tam taramasıyla temizlenecek.
- Kuru koşu: 6 rapor betiği, çıktı geçici dizine yönlendirilerek çalıştırıldı, hepsi hatasız ve uyarı kutusu HTML'de var. `dirsek/rapor.html` gerçekten yeniden üretildi (uyarı kutusu dahil).
- Yan etki: kuru koşuda `montaj_rapor.py` kendi GIF'ini projede yeniden yazdı (`montaj/gorsel/montaj-hareket.gif`, aynı karelerden; içerik değişmemeli).

## Açık sorunlar / notlar
- Bilezik yarığı 2 mm: tüp ile pim arası 0,25 + bilezik-tüp 0,25 = toplam radyal 0,5 mm; yarık kapanınca çevre kısalması 2 mm ≈ 0,32 mm yarıçap. Sıkıştırmanın tüpü pime tam bastırması için yarık/bilezik kalınlığı baskı kuponunda denenmeli (şüpheli, ölçüm gerekir). Yarığı değiştirmedim (kapsam dışı karar).
- `taban/regresyon/moduller.json` dirsek satırı 8 Ekim tarihli arayuz.py'ye göre; dirsek çatalı artık 0,67 g hafif (kasıtlı fark) -> D4'te yeniden koşulup "kasıtlı fark" işaretlenmeli.
- `carpisma-sonuc.json`, `montaj-analiz.json`, ana montaj dirsek kütlesi (−0,6 g) yeniden üretilmedi (sıra: carpisma, ana montaj en sonda).
- `dirsek_gorsel.py` (GUI) koşulmadı; görseller eski bilezik (0,15 mm fark, gözle görülmez).
