# Taşınma ("kaçırılmış robot") deneyi

Robot A'dan B'ye giderken biri onu kaldırıp başka yere koyarsa ne olur? Odometri bunu görmez (teker dönmez); robot
taşındığını yalnız LiDAR taramasından anlayabilir. Bu deney v3 gezinmeyi (`gezinme.beyinler`, `konumlama` v3,
varsayılan ayarlar) **değiştirmeden** ölçer, sonra isteğe bağlı bir "algi" sürümünü (varsayılan değişmedi) aynı
koşularda karşılaştırır. Sonuç ve hüküm: `sonuc/SONUC.md`.

## v3'te taşınmayı fark edecek ne var (koddan)

- Konumlayıcı (`konumlama/mcl.py`): yalnız artırılmış MCL. Işın başına ortalama log-olasılığın hızlı ortalaması (α 0,5)
  yavaş ortalamanın (α 0,05) altına düşünce her haritada parçacıkların en çok %10'u serbest alana rastgele saçılır
  (`rastgele_en_cok`). Çapraz enjeksiyon v3'te kaldırıldı; çapraz tohum yalnız harita kanıtında, parçacık taşımıyor.
  Saçılan parçacık doğru yere düşer ve ağırlık kazanırsa poz tahmini oraya atlar; konumlayıcı bunu açıkça "kayboldum"
  diye bildirmez, yalnız `konum_kararsiz` (ana mod payı < 0,8 ya da xy std > 0,5 m) yükselir.
- `AbBeyni` (A'dan B'ye, tek harita): taşınmaya tepkisi yok. `konum_kararsiz`'a bakmaz; poz tahmini nereye atlarsa
  oradan sürer, izleyicinin bitti dediği yerde durur.
- `KayipBeyni` izleme evresi (6 harita): başka haritaya kararlı geçiş -> yeniden plan, 15 tarama kararsız -> keşfe
  dönüş, poz tahmini odometri öngörüsünden 0,7 m'den çok sıçrarsa -> yeniden plan (sıçramayı kabul eder).

## Senaryolar ve sürümler

| Senaryo | Beyin | Ne |
| --- | --- | --- |
| `ab` | `AbBeyni` (tek harita, bilinen başlangıç, 1500 parçacık) | önceki aşamanın A'dan B'ye'si; hedef t tek -> 2. hedef, t çift -> en uzak kapı |
| `cok` | `algi.IzBeyni` = `KayipBeyni` + `baslat_poz(..., diger_haritalar=True)` + baştan karar (6 harita, 3000 parçacık) | KayipBeyni'nin karardan sonraki evresi; hedef orta hat sonu (`son`, her koridorda var: başka koridora taşınınca aynı göreli hedef) |

| Sürüm | Ne |
| --- | --- |
| `v3` | olduğu gibi |
| `algi` | v3 beyni + `algi.TasinmaBeyni` katmanı (yalnız bu klasörde): taşınma algısı, durma, küresel yeniden başlatma + yavaş keşifle yeniden karar, şüphede yavaşlama (ayrıntı `algi.py` başı ve SONUC.md) |

Taşıma türleri (`kacirma.TURLER`): aynı koridorda uzak (>= min(5 m, boyun %40'ı)), 180° çevrilmiş (aynı yerde),
küçük kaydırma (orta hat boyunca 1-3 m, yan ±0,2 m, yön ±15°), başka koridor. Taşıma anı: yer gerçeği yolu rota boyunun
U(0,25, 0,60)'ına ulaşınca. Yanlış alarm koşulları (taşıma yok): `taban`, `insan_2` (1 kişi / 10 m), `esya_2`
(1 eşya / 10 m), `karma_2` (ikisi birden), `karma_3` (insan 2 + eşya 2 / 10 m; yalnız sınamada); önceki aşamanın
`insan` / `esya` bozucuları aynen.

## Nasıl çalıştırılır (`cd kod\fizik\deneyler\tasinma`)

`%V%` = `%LOCALAPPDATA%\lale-sim-venv\Scripts\python.exe` (yalnız MuJoCo için). Betikler süreci düşük önceliğe alır,
numpy iş parçacığını 1'e indirir.

    py -3 kos_tasinma.py --kume gelistirme --surum algi --isci 3 --kosul ayni_uzak,ters180,kucuk,baska_koridor,ya_taban,ya_insan_2,ya_esya_2,ya_karma_2
                                                                     # geliştirme kümesi (eşik ayarı; 144 koşu, karma_3 hariç)
    py -3 kos_tasinma.py --kume sinama --isci 3                      # sınama kümesi (hüküm): 2 senaryo x 2 sürüm x 9 koşul x 12 = 432
    py -3 kos_tasinma.py --tek sinama:ab:v3:ters180:koridor_5:1      # tek koşu, ekrana
    %V% kos_mj.py --kosu koridor_5:1,koridor_1:2,koridor_3:1,koridor_6:2,koridor_4:2
                                                                     # MuJoCo doğrulaması (A'dan B'ye, 40 koşu)
    py -3 gerileme.py --isci 3                                       # koridor_karisiklik kayıtlarıyla gerileme denetimi
    py -3 rapor.py                                                   # CSV, sonuc/tablolar.md, sonuc/ozet.json, gorsel/
    py -3 -m unittest discover -s testler -v                         # birim testleri

Süreler (bu PC, tek iş parçacığı): 2B `ab` koşusu 2-10 s, `cok` 6-25 s; MuJoCo 6-40 s; gerileme kaydı başına ≈ 20-30 s. Ölçümde sınama (432 koşu) 3 işçiyle ≈ 25 dk, geliştirme (144) ≈ 10 dk, MuJoCo (40) ≈ 15 dk, gerileme 2 işçiyle ≈ 7 dk.
Bitmiş koşu `sonuc/ham/<2b/<küme> | mujoco/mujoco>/<id>.json` olarak durur, yeniden koşmaz (kaldığı yerden). Yarıda
öldürülen koşunun `.kilit` dosyası elle silinir. `sonuc/ham/` ve `.durum` depoya girmez; tohumlar sabit.

## Dosyalar

| Dosya | İş |
| --- | --- |
| `kacirma.py` | yollar (önceki aşamanın `ortak.py`'si `he_ortak` adıyla), kümeler, tohumlar, taşıma pozları (`tasima_pozu`), görev listesi |
| `algi.py` | `IzBeyni` (v3, 6 harita izleme), `TasinmaAlgisi`, `TasinmaBeyni` ("algi" sürümü), `beyin_kur` |
| `kos_tasinma.py` | 2B koşucu; `Kacirici` (hakem tarafı: taşır, ölçer), `TasinmaHakemi` (son süre) |
| `kos_mj.py` | MuJoCo doğrulaması (`Duzenek`; taşıma `c.konum_ayarla`, odometri değişmez) |
| `gerileme.py` | koridor_karisiklik `akis/` kayıtlarının küçültülmüş alt kümesiyle gerileme |
| `rapor.py` | tablolar, CSV, görsel |
| `testler/` | algı, taşıma pozları, taşımanın odometriye yansımaması, sarmalayıcının iyi taramada komutu aynen geçirmesi |

## Ölçüm (hakem tarafı; beyne gitmez)

Her taramada: poz hatası (tahmin - gerçek; yön 30°'den çok yanlışsa ya da inanılan harita yanlışsa "yanlış poz"),
konumlayıcının emin olup olmadığı (`konum_kararsiz` ve `kararsiz` False, beyin rota izliyor), komut, temas, gerçek yer.
Türetilenler: tepki (beynin davranış değiştirdiği ilk an), şüphe (ilk `konum_kararsiz`), bulma (taşımadan sonra poz
doğru olup sonuna dek öyle kalan dilimin başı), yanlış poza emin süre ve yol, yanlış poza göre sürüş süresi, taşımadan
sonraki temas olayları (1 s birleştirme), hedefe varış (0,3 m içinde durdu; tek haritalı beyni başka koridora
taşımada hedef yok: "güvenli durdu" = yardım bekliyor, son 10 s'de < 5 cm yol, temas yok).
