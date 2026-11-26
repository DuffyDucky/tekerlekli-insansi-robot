# Ön kayıt: bağımsız hüküm 3

**Yazıldığı an: 2026-11-26 06:27 (yerel saat), hüküm koşusundan ÖNCE.** Bu dosya yazıldıktan sonra görev listesi
(`hukum3.py gorevler()`), ölçüt ve raporlama kuralı değiştirilmez. Hükmü bu çalışmada tasarım ajanından ayrı bir ajan
koşuyor. Adayların ayarına dokunulmadı.

## 0. Koşudan önce yapılan denetimler

- `sonuc/dondurma_3.md`'deki sha1 özetleri koşudan önce denetlendi ve 7 / 7 tuttu: `sensor.py`, `denetci.py`, `kosu.py`,
  `deney.py`, `sahne.py`, `secim.json`, `testler/test_aday3.py`.
- Bu dosyalardan yalnız `sahne.py` değişti ve yalnız ekleme yapıldı. Eklenenler: `h3_*` sahneleri, eğik yarık kurucusu ve
  hakemde yeni bir kenar türü (`"dikr"`, döndürülmüş dikdörtgen delik). Bunun dışında yalnız `if` satırı `elif` oldu.
  Eski 89 sahnenin hepsi denetlendi: sözlükleri, XML'leri ve 89 x 50 rastgele noktadaki hakem payları değişiklikten önceki
  ve sonraki sürümde birebir aynı. `phi = 0` eğik yarığın payı `acik()` yarığıyla aynı (en büyük fark 5e-16 m).
  Yeni özetler: `sahne.py` c641ad4d32ce4702814f0edb9ae291bdebaf3711, `hukum3.py` d5a64a91c63e5e8ede3156b4562158f64af0081c.
- **Tohum:** 211-220. Bütün `sonuc/*.csv` (38) ve `sonuc/ham/*.jsonl` (35) dosyaları tarandı. Kullanılmış en büyük tohum
  210, 211-220 hiçbir dosyada geçmiyor.
- **Sahne:** 53 yeni sahnenin adı hiçbir CSV'de ya da ham kayıtta yok. Geometrileri (tür + parametreler) eski 89 sahnenin
  hiçbiriyle aynı değil. Tek bilinçli istisna `h3_parlak_3` / `h3_parlak_6`. Geometrileri `duz` ile aynı, yeni olan koşul:
  her örnekte %3 / %6 dönüşsüz okuma (parlak zemin). Önceki parlak zemin oranları %0 / 5 / 20 / 50 idi.
- **Duman denetimi:** 30 görev, tohum 0 ile koşuldu. Yalnız hata ve süreye bakıldı, sonuç yazdırılmadı. 0 hata.

## 1. Ölçüt (önceki iki hükümle aynı, SONUC.md'den aynen)

> uçurum koşularında hakem 0 düşme, yanlış alarm koşularında 0 durma. Hakem kuralı (teker merkezi kenarı geçti,
> eğim > 15°, z 3 cm düştü) değiştirilmedi.

- **Hangi hızlar sayılır:** SONUC.md'de `t2_hukum` ölçütü bütün uçurum koşularını sayar: 3476 koşunun hepsi, yani
  ızgaradaki 0,10 / 0,20 / 0,25 / 0,30 / 0,39 m/s. Burada da aynı kural geçerli: ızgaradaki bütün hızlar (0,10 / 0,20 /
  0,25 / 0,39 m/s) ölçüte girer. Hıza göre döküm yalnız ikincil olarak raporlanır.
- **Yanlış durma:** yanlış alarm koşusunda denetçinin tetiklemesi (`tetik` = True).
- **Hatalı koşu** (`hata` dolu) geçti sayılmaz. Bir düzende hata > 0 ise o düzen GEÇMEDİ.
- Rampa ucu sahnesinde hakemin z düşüşü ölçütü kapalıdır (`z_dusus_yok`, önceki hükümlerdeki gibi). Teker merkezi
  kenarı geçti ve eğim > 15° ölçütleri açıktır.

**İkincil ölçütler** (hükmü değiştirmez, raporlanır):

- **Fiziksel düşme:** hakemin düşme saydığı her uçurum görevi, hakemden sonra da sürdürülerek yeniden koşulur
  (`hukum3.py fiz`; ileri / geri için `t_max = 12 / v · 0,25 + 6` s, `t2_hukum_fiz` ile aynı). Düşme sayılanlar:
  - teker merkezi 20 mm'den çok iner,
  - eğim > 5°,
  - gövde zemine değer.

  Rampa ucunda teker zaten rampadan iner. Orada düşme şöyle tanımlanır: teker merkezi rampa ucunu > 6,25 cm (teker
  yarıçapı) geçer ya da eğim > rampa eğimi + 5°.
- **En küçük pay:** koşu boyunca dört teker merkezinin kenara en küçük yatay uzaklığı (cm), sınıf ve düzen başına.

## 2. Ölçülen düzenler (beşi de aynı görev listesinde)

| düzen | tanım | denetçi | koşul |
| --- | --- | --- | --- |
| `6` | `4OD+2AD` (`deney.SECIM_2`, son commit edilen seçim) | SECIM_2 | **ortak koşul**: SECIM_3 `hukum_kosul` (K20 20 ms, 1,3 m, konum tutma 40 / 100) |
| `10` | `6OD+4AD` (`deney.SECIM_3`) | SECIM_3 | kendi `hukum_kosul`'u (ortakla aynı) |
| `14` | `8WRD+4AD+2YR40` (`secim.json`; değerler `hukum3.S14`'e kopyalandı) | secim.json | kendi `hukum_kosul`'u |
| `3A` | `8WRaD+4AD+2YR40` (`deney.SECIM_3A`, dondurma 3) | SECIM_3A | kendi `hukum_kosul`'u |
| `3B` | `6OD+4AD` + firmware kuralları (`deney.SECIM_3B`, dondurma 3) | SECIM_3B (`kural` dahil) | kendi `hukum_kosul`'u |

Altı sensörlü düzenin kendi tanımında `hukum_kosul` yoktu: sınaması ilk zamanlama modeliyle ve konum tutmasız koşuldu.
Burada aynı görev listesinde karşılaştırılabilmesi için ortak koşulla ölçülür. Bu koşul sensör konumu ya da eşik değildir.
Bu bir ön kayıt kararıdır.

Kullanım `dondurma_3.md`'deki gibi: yerleşim `sensor.yerlesim(S["yerlesim"]["ad"], 0.12, 30)`, denetçi
`DenetciAyar(**deney._ana(S))`, koşul `S["hukum_kosul"]`. Koşucu `deney.gorev_kos` (değişmedi).

## 3. Görev listesi (`hukum3.py`, `_taban()` x beş düzen)

Her düzende aynı 3327 taban görev var: 2742 uçurum ve 585 yanlış alarm. Toplam 16 635 koşu. Tohum, sınıf içindeki sıraya
göre 211 + (i mod 10). Aynı taban görev beş düzende aynı sahneyi, senaryoyu ve tohumu kullanır. Açılar ±2° ve yanal kayma
`kosu.baslangic_pozu`'ndaki gibi tohumla oynar. Hızlar, aksi yazılmadıkça 0,10 / 0,25 / 0,39 m/s.

| sınıf | sahneler (hepsi yeni) | senaryo | koşu / düzen |
| --- | --- | --- | --- |
| merdiven_ileri | `h3_merdiven_16x29`, `h3_merdiven_18x26`, `h3_burun_17x30` (2,5 cm burun) | ileri, açı 5 / 18 / 33 / 47 / 63 / 76, x 3 yineleme | 162 |
| kose_ileri | `h3_kose_150` (D 1,5 m), `h3_kose_60` (D 0,6 m) | ileri, aynı açılar, yanal −0,85…−0,35, x 3 | 108 |
| kuyu_ileri | `h3_kuyu_120` (1,2 x 1,2 m, menzil dışı derin), `h3_kuyu_200` (2,0 x 1,5 m) | ileri, açı 5 / 18 / 33 / 47, yanal ±0,25 / ±0,6, x 4 | 96 |
| dar_ileri | `h3_acik_48/52/58/62/68/72/78/85` | ileri, yanal −0,13 / −0,04 / 0,07 / 0,18 / 0,27, açı 4 / 14 / 26 | 360 |
| dar_geri | aynı 8 açıklık | geri, yanal −0,12 / 0,03 / 0,17, açı 5 / 17 / 28, v 0,10 / 0,25, x 2 | 288 |
| genis_geri | 3 yeni merdiven | geri, açı 6 / 20 / 35 / 48, v 0,10 / 0,25, x 3 | 72 |
| donus_genis | 3 yeni merdiven | yerinde dönüş, d 0,33 / 0,38 / 0,43 / 0,48, w ±1, x 3 | 72 |
| donus_dar | 8 yeni açıklık | yerinde dönüş, d 0,33 / 0,38 / 0,43 / 0,48, w ±1, yanal −0,25 / 0,04 / 0,26, x 2 | 384 |
| yarik_dar | `h3_yarik_85/95/105/115/125/145/160` (8,5…16 cm; boy 0,9 / 1,0 / 1,2 m) | ileri, deliğin y'si 0,02 / 0,07 / 0,13 / 0,185 / 0,205 / 0,222 / 0,245 / 0,29 (yarısı aynalı, sağda), açı −12 / −7 / 3 / 8 / 12 | 840 |
| yarik_egik | `h3_egik_<95/105/125/145 mm>_<15/25/35/45°>` (1 m boy, ekseni ilerleme yönünden dönük) | ileri, açı 0; sol ya da sağ teker izi yarığı merkezde ya da ±0,6 · L/2 · sinφ'de keser | 288 |
| rampa_ucu | `h3_rampa_6_ucurum` (6°, 3 m), `h3_rampa_9_ucurum` (9°, 2 m) | ileri, v 0,10 / 0,20 / 0,25 / 0,39, açı 0 / 7 / 18, x 3 | 72 |
| yanlis_alarm | `h3_koyu_5`, `h3_koyu_20`, `h3_esik_12mm`, `h3_esik_18mm`, `h3_hali_7mm`, `h3_hali_12mm`, `h3_derz_ince`, `h3_derz_derin`, `h3_parlak_3`, `h3_parlak_6`, `h3_rampa_5_inis`, `h3_rampa_7_inis`, `h3_rampa_9_inis` | ileri, yol 2,2 m, açı 7 / 26 / 43, x 5 | 585 |

**Süre kuralı:** görevler üç tura bölünür (sınıf içi sıra mod 3). Koşu sırası tur 0 (beş düzen), tur 1, tur 2. Süre
yetmezse yalnız bütün turlar düşer. Böylece her sınıfta ve her düzende koşu aynı oranda azalır, derinlik değişmez.
Düşen tur raporda yazılır. Bitmemiş tur da raporlanır.

## 4. Karar ve raporlama (sonuç ne çıkarsa çıksın)

- `sonuc/hukum3.csv`, `sonuc/hukum3_fiz.csv`, `sonuc/hukum3_tablo.md`: düzen x sınıf tablosu (hakem düşmesi / koşu,
  fiziksel düşme, en küçük pay, yanlış durma) ve her düzen için GEÇTİ / GEÇMEDİ. Bütün düşmeler ve durmalar listelenir.
  Başarısız ve hatalı koşular CSV'de durur.
- **Karar kuralı:**
  - Ölçütü sağlayan düzen varsa, en az sensörlü olan `secim.json`'a "onaylı seçim" olarak yazılır.
  - Eşitlikte en küçük payı büyük olan seçilir, o da eşitse davranış kuralı olmayan.
  - Hiçbiri sağlamıyorsa `secim.json`'daki seçim değişmez. Yalnız `durum` alanına bu hükmün sonucu ve "GEÇMEDİ" eklenir.
- Hüküm verisiyle ayar yapılmaz. Fiziksel doğrulama hükmü değiştirmez.
- `katmanli_oneri.md` bu taze kümenin sayılarıyla güncellenir. Eski tablo "önceki, görülmüş ızgara" başlığıyla kalır.
  SONUC.md ve BENIOKU.md'ye "Bağımsız hüküm 3" bölümü eklenir.
