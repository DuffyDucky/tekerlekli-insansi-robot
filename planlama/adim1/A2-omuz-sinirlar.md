# A2: omuz sınırları (düzeltme planı 1. adım: C1, C2, C3, M3-omuz)

Başlangıç: 14 Ekim 2026. Ajan: tasarım ajanı A2. Git commit yapılmadı. Tam çakışma taraması (C7) koşulmadı.

## Özet (önce → sonra)
| Değer | Önce | Sonra |
|---|---|---|
| Omuz yana açma (S2) sınırı | 0…120° | **3…120°** (`arayuz.OMUZ["yana_aralik"]`) |
| Omuz öne-arka (S1) sınırı | −45…135° | aynı (`arayuz.OMUZ["one_arka_aralik"]`) |
| Kol ↔ kabuk en küçük boşluk (yana alt sınırda) | 3,76 mm (yana 0°, öne ±40°) | **7,17 mm** (yana 3°; hedefli ölçüm, bkz. C1) |
| M6 vida ucu − çekiç somun alt yüzü | 0,1 mm | **1,7 mm** (4/4 yüzde) |
| M6 vida ucu − kanal tabanı | 2,4 mm | 0,8 mm |
| Omuz parça sayısı / kütle | 70 / 852,56 g | 66 / 848,49 g (−4 pul, −4,07 g; robot toplamı −8 parça, −8,13 g) |
| Kafa-kol yasak bölgesi | tablo: öne 125…135°, yana 0°, dirsek 70…105°; pan 30…55°, tilt 25…30° | **kutu: pan 25…60° (sol kolda −60…−25°), tilt 20…30°**; kol koşulu öne 120…135°, yana 3…5°, dirsek 65…105°, bilek ±90° |

## Değişen dosyalar (hepsi `tasarim/freecad/` altında, yoksa yazılı)
- `arayuz.py`: `OMUZ` (S1/S2 aralığı, yana alt sınır boşluk verileri) bölüm 6'ya; bölüm 13 (yeni): `YASAK_OLCULEN`, `YASAK_PAY`, `KAFA_KOL_YASAK`, `eklem_sinirlari()`. Başka satıra dokunulmadı (A.GECME / tüp-bilezik başka ajanda).
- `omuz/omuz_parcalar.py`: yuva M6 pulları kaldırıldı (M3), vida `screw912(6, 16, pv, dv)`.
- `omuz/omuz_montaj.py`: eklem sınırları `A.OMUZ`'dan; yeni kontrol 1b (M6 uç payı ≥ 0,5 mm ve kanal tabanına değmeme), `omuz-analiz.json`'a `m6_vida_pay` ve `eklem_siniri`.
- `omuz/omuz_rapor.py`: sınır süzgeci/çerçeve `A.OMUZ`'dan; pul metinleri; servo sıfır kalibrasyonu notu.
- `carpisma.py`: `KOL_ARALIK`, omuz yükleyicisinin `eklem_araligi`, `KABA` ızgarası `A.OMUZ`'dan (yana ızgarası 3,15,30…120; eskiden 0,15,…); kol-kol ve jest test pozlarındaki "yana 0" → `YANA_MIN` (`ev` pozu hariç).
- `dirsek/dirsek_montaj.py` (yalnız `lim` süzgeci satırı, geometri değil), `kabuk/kabuk_rapor.py` (yalnız `eklem_ici` lambda).
- `kod/ortak/eklem_sinirlari_uret.py` (yeni), `kod/ortak/eklem_sinirlari.json` (üretilmiş; `--kontrol` bayrağı güncel mi bakar).

## C3: sınırların eskiden elle yazıldığı yerler (kod/mantık)
| Dosya:satır (önce) | İçerik | Şimdi |
|---|---|---|
| omuz/omuz_montaj.py:189-190 | eklem sınırı (-45,135) / (0,120) | `A.OMUZ` |
| omuz/omuz_rapor.py:60 (+ `range(0,121,5)` serbest aralık, harita çerçevesi) | süzgeç | `A.OMUZ` |
| carpisma.py:86 | omuz `eklem_araligi` lambda | `A.OMUZ` |
| carpisma.py:405-406 | `KOL_ARALIK`, `KABA` | `A.OMUZ`'dan türetilir |
| dirsek/dirsek_montaj.py:452 | `lim` | `A.OMUZ` |
| kabuk/kabuk_rapor.py:120 | `eklem_ici` | `A.OMUZ` |

Ana montaj (`ana_montaj.py`, `moduller.py`) sınırı `omuz-montaj.FCStd`'den okuyor, elle yazılı sayı yok. Kontrol: `omuz-montaj.FCStd`'de `OmuzYanaAcma` AngleMin=3°, AngleMax=120°; `OmuzOneArka` −45…135° (freecadcmd ile okundu).

## C1: S2 alt sınırı +3°
Hedefli ölçüm (6 poz × yana −3, −2, 0, 3, 5, 10°; sağ kol, kol grubu ↔ 202 kabuk parçası, tam tarama değil; betik scratchpad'de `c1_bosluk.py`), boşluk mm:

| poz (öne, dirsek, bilek) | −3° | −2° | 0° | **3°** | 5° | 10° |
|---|---|---|---|---|---|---|
| 0, 0, 0 | temas | 0,63 | 4,67 | **8,18** | 8,60 | 8,60 |
| 40, 0, 0 | temas | temas | 3,76 | **7,17** | 8,56 | 8,60 |
| −35, 0, 0 | temas | temas | 3,81 | **7,17** | 8,57 | 8,60 |
| 20, 0, 0 | temas | 0,37 | 4,40 | **7,40** | 8,60 | 8,60 |
| −5, 105, −90 (el) | temas | temas | 4,12 | **7,79** | 8,60 | 8,60 |
| −10, 105, −90 (el) | temas | temas | 4,35 | **7,57** | 8,60 | 8,60 |

Plan sayıları (0°'de 4,7; −2°'de 0,6; −3°'te temas) yalnız öne 0° için doğru. Öne ±35–40°'de 0° boşluğu 3,76 mm ve −2°'de zaten temas. Sınır +3°'ye çekilince boşluk en az 7,17 mm; 3°'de sınırlayan parça artık göğüs bandı değil omuz bandı (Ø84 delik kenarı). Servo sıfır kalibrasyonu notu `omuz_rapor.py` ACIK listesine yazıldı: kayma ≤ ±2° olmalı (3° komutunda gerçek ≥ 1°, boşluk ≥ 3,76 mm), 5°'yi geçerse gerçek −2°'de temas.
Tarama etkisi: omuz taramaları (`PHIS`, `THS`) sınır değişikliğinden etkilenmez; sınır yalnız "eklem aralığında" sayımını ve eklem nesnesini değiştirir.

## C2: kafa-kol yasak kutusu
Kural: ölçülen aralık her eksende ±5° (tarama adımı, OZET'teki "+1 adım pay" kuralı) genişletilip eklem aralığına kırpıldı (`arayuz._genislet`). Pan 30…55 → **25…60**; tilt 25…30 → **20…30** (üst sınır tilt sınırı 30'a kırpıldı); sol kolda pan −60…−25, tilt aynı. Kol koşulu: öne 125…135 → 120…135, yana 0 → **3…5** (0 artık erişilemez), dirsek 70…105 → 65…105, bilek tümü. `kol_kosulu` dışında çakışma bulunmadı (kutu kol koşuluyla birlikte uygulanır; koşulsuz uygulamak güvenli ama kafayı gereksiz kısıtlar). JSON'da `kafa_kol_yasak.sag_kol/sol_kol` (koşul + kutu). **Kutu yeni taramayla doğrulanmadı**; tablonun kenarındaki sıfır boşluklu pozlar C7 taramasında (kol yana 3, 5° ince adım) yeniden bakılmalı.

## C3: kod/ortak/eklem_sinirlari.json
Biçim: `{surum, birim, kaynak, eklemler:{r_s1, r_s2, r_dirsek, r_bilek, l_s1, l_s2, l_dirsek, l_bilek, pan, tilt}, teker, sol_isaret, kafa_kol_yasak}`; her eklemde `min`, `max`, `servo`, `neden`. Anahtarlar seri protokolün `q` adlarıyla uyumlu (`r_s1`, `r_s2`, …). Sol kol sınırları sağ ile aynı (eklem açısı aynalı), servo komut işareti ters (`sol_isaret`, tahmini, C4). Üretim: `python kod/ortak/eklem_sinirlari_uret.py` (FreeCAD gerekmez), `--kontrol` güncel mi bakar. Yazılım planının sözünü ettiği C başlık dosyası yapılmadı (planda Y0 işi).

## M3 (omuz): karar, pul kaldırıldı, M6×16 kaldı
Önce: pul 1,6 + vida 16 → uç yuva dış yüzünden 14,4 mm derinde; çekiç somun (dudak altı 9,3, kalınlık 5) alt yüzü 14,3 → pay 0,1 mm. Kanal tabanı 16,8 mm.

| Seçenek | Uç derinliği | Somun payı | Kanal tabanı payı | Geometri etkisi |
|---|---|---|---|---|
| **A: pulsuz M6×16 (seçildi)** | 16,0 | 1,7 | 0,8 | Zarf yalnız küçülür (eski pulun yeri boşalır), yeni çakışma imkânsız; −4 parça, yeni vida boyu yok; baş 1,6 mm aşağı iner (kabuk üst kapak erişim deliği O14 etkilenmez) |
| B: M6×18 + pul | 16,4 | 2,1 | 0,4 | Dış geometri aynı; yeni bir vida boyu (BOM çeşidi artar, M9'a ters); tabana 0,4 mm, uzunluk toleransında değme riski |

Gerekçe: A'nın zarfı B'nin altkümesi, payları dengeli (1,7 / 0,8; B'de 2,1 / 0,4), yeni stok kalemi yok. **Risk (doğrulanmadı):** pul PETG duvara basıncı yayıyordu; pulsuz baş 4,8 mm PETG duvara doğrudan oturuyor (baş Ø10, pul Ø12). Basılı yuvada sıkarken ezilme görülürse geri dönüş B (M6×18 + pul). Kayıt: `omuz-analiz.json` `m6_vida_pay` (4 yüzde somun payı 1,7, taban payı 0,8; kontrol OK). Omuz kontrolüne kalıcı eklendi (≥ 0,5 mm ve kanal tabanına değmeme).

## Kontroller (omuz_regresyon `once` → `sonra`, 56 s)
- Statik çakışma 0 (önce 0); ev pozu boşlukları aynı (Kol-Gobek 0,0; Kol-Gövde 4,0; Gobek-Gövde 0,0).
- Tarama aynı: kol×göbek 8, göbek×gövde 0, kol×gövde 94 çakışan poz (875 poz); tork tablosu en büyük fark 0 (en büyük 5,722 kg·cm).
- Beklenen (kasıtlı) fark: parça sayısı 70→66 (4 pul), BOM 17→16 satır, kütle −4,07 g. Diğer 66 parçanın hacmi/adı aynı.
- FreeCAD eklem testi (`omuz-montaj.FCStd`): S2 AngleMin=3, AngleMax=120; S1 −45…135; `joints_ok` True.
- `eklem_sinirlari.json` üretildi, `--kontrol` güncel; JSON içi tutarlılık denetimi (min<max, kutu eklem aralığında, sol kutu sağın aynası) geçti.

## Açık sorunlar / sonraki ajanlar için
1. **Yalnız metin, dokunulmadı** (sayılar 0…120 diyor): `OZET.md` S2 ve yasak bölge satırları, `README.md`, `dirsek/dirsek_rapor.py` (273, 425, 522, 532), `kabuk/kabuk_rapor.py` (267, 376), `kafa/kafa_rapor.py` (286-287, yasak_metni), `taban/taban_rapor.py` (402), `montaj/montaj_rapor.py` (272-274, 297-298, 448), `iskelet/*` (en kötü durum taraması "yana 0…120"). Rapor üretimi / D1-D2 adımında güncellenmeli. Servo sıfır kalibrasyon cümlesi `dirsek_rapor.py:273` ("0° konumu kabuğa doğru kaçmamalı") ve `montaj_rapor.py:274` de var.
2. **Montaj tarafı, dokunulmadı:** `montaj/montaj_gorsel.py` Kollari_oynat (yana 0…69°) ve poz-önü (yana 0°) sınırın altına iniyor; `montaj/eklem_dogrulama.py` POZ/TPOZ yana 0 (çözücü sınır dışını kabul ediyor, sorun değil, ama "hareketler sınır içinde" ifadesi artık doğru değil); `montaj_gui_kontrol.py` sınır beklentisi; `iskelet_montaj.py` en kötü durum taraması yana 0…120 (3…120'ye daraltılabilir).
3. **Ana montaj sayıları:** omuz −4 pul × 2 (sağ+sol) → 907 → 899 parça, −8,13 g. Ana montaj, taban devrilme hesabı ve belgelerdeki "907 parça / 21.260,9 g" bu adımda yenilenmedi.
4. `carpisma.py` KABA yana ızgarası artık 3,15,30…120 (eskiden 0,15,…): poz sayısı aynı (9), pozlar farklı. `carpisma-bolum/*.json` eski; `carpisma_kos.py` izleme listesi C6 işi. Jest "ev" pozu (yana 0) kasıtlı bırakıldı (güç kapalı dinlenme konumu); jest "el yüze / el ağıza" yana 0 → 3 yapıldı.
5. Yasak kutu ve kol koşulundaki "yana 3…5" taramayla doğrulanmadı (C7).
6. Servo S2 horn takma açısı ve yazılımdaki sıfır kayması C4 tablosuna girmeli (mekanik 0° = ev, yazılım alt sınırı 3°).
7. Pulsuz M6 baş altı PETG ezilmesi doğrulanmadı (M3 riski, yukarıda).
8. Omuz görselleri ve `rapor.html` yeniden üretimi: aşağıda "Üretim" bölümünde.

## Üretim
(omuz_gorsel ve omuz_rapor sonucu aşağıya eklenecek)
- `omuz_gorsel.py` (freecad.exe GUI, 15:08): omuz-genel/arka/yakin/patlatilmis PNG ve FCStd GUI durumuyla yeniden kaydedildi. Sonda `JointObject.ViewProviderJoint ... app_obj` izleri (8 adet) GUI simge hatası, çıktı etkilenmedi (rc=0).
- `omuz_rapor.py`: `rapor.md` + `rapor.html` + çalışma alanı haritası yeniden üretildi (çerçeve artık 3…120 × −45…135). GIF kareleri (`gorsel/kare`) 7 Ekim'den, yeniden çekilmedi (kol hareketi aynı, pul görünmez). Rapor "Yana açma serbest aralık 0°…120°" satırı geometrik serbest aralıktır (yazılım sınırı değil), doğru.
- Not: `once.json`, çalışma ağacının (11-14 Ekim değişiklikleri dahil) mevcut halinden alındı; git HEAD'e göre rapor farkındaki tüp 32→30 g ve STL değişimleri bu adımın değil, önceki (M2/11 Ekim) değişikliklerin sonucu.
