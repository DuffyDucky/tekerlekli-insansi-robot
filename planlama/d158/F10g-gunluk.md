# F10g günlüğü: K56 + K57 montaj sırası kararları rehberde (P10.5b)

Uygulama ajanı A. Başlangıç 13.11.2026 23:29 (saat `date` ile okundu), dal `lale-duzeltme`, HEAD `9145164`. Karar: Ahmet, 13.11.2026
≈ 23:28, "K56 ve K57 önerdiğin gibi olsun, devam" (K56 seçenek C, K57 seçenek a; `planlama/d158/karar-kuyrugu.md`). Geçici dosyalar
scratchpad'de (`k5657-a/`), depoya kopyalanmadı. Commit / push / `git add` yok (C adımı).

Çalışma ağacında bu işten eski 14 değişik dosya (dokunulmadı, geri alınmadı): `tasarim/freecad/kabuk/gorsel/*.png` (13),
`tasarim/freecad/montaj/yerlesim-kontrol.json`. Üretim zinciri bunları yeniden yazmadı (bkz. § 6).

## 0. Komutlar, çıkış kodları, bellek

Uzun komutlar F10f'in yöntemiyle: scratchpad `baslat.ps1` (boş fiziksel bellek ≥ 2 GB ve ≥ 300 MB'lık python / FreeCAD süreci yok)
→ `sarmal.ps1` (ayrı gizli süreç, çıktı / dönüş kodu dosyaya, 15 s bellek bekçisi: boş fiziksel < 0,5 GB art arda iki kez ya da boş
commit < 2 GB → yalnız kendi süreç ağacını durdurur) → ön planda `yokla.ps1`. Her koşunun `.durum` kaydı scratchpad'de
(`k5657-a/<ad>.durum`). Fark (F10f'e göre): kullanıcının kendi Chrome'u açık olduğundan (13.11 23:28 ölçümü 16 süreç) `baslat.ps1`
Chrome sayısını yalnız kayda yazıyor, başlatmayı engellemiyor; tarayıcı kullanan betikler kendi başsız Chrome'larını kendi profil
klasörleriyle açıp kapatıyor (ada göre toplu kapatma yok). "En az" = bekçinin koşu boyunca gördüğü en düşük boş fiziksel bellek.

| Ad | Komut | Başlangıç | Boş bellek önce (GB) | En az (GB) | Süre (s) | Çıkış | Not |
| --- | --- | --- | --- | --- | --- | --- | --- |
| veri1 | `rehber_uret.py --gorsel-yok --ek-yok` (FreeCAD'li veri) | 23:36:18 | 6,09 | 5,64 | 224 | 0 | kilit 23:36 → 23:40 "boş" |
| sim1 | scratchpad `sim.py` (rehberin kendi `ucus_yolu` + `perdelenme` + `sira`, adım 39, 40, 43, 44; depoya yazmaz) | 23:40:25 | 6,18 | 5,93 | 32 | 0 | § 2 |
| zin1 | zincir (§ 5) | 23:42:17 | 5,86 | 2,77 | 5158 | 0 | 14.11 01:08:48 bitti; kilit 23:42 → 23:45 "boş" (FreeCAD aşaması 186 s) |
| kare | scratchpad `p_kare.py` (kendi başsız Chrome'u, kendi profili; § 3) | 14.11 01:11 | 5,11 | — | ≈ 30 | 0 | depoya yazmaz |

FreeCAD kilidi (`planlama/d158/FREECAD-KILIT.txt`): veri1 ve zin1'in FreeCAD aşamasında satır yazıldı, ikisinde de aşama bitince
"boş". Son hâli "boş".

## 1. Ne değişti (kaynak)

### 1.1 Parça ↔ adım ataması (`tasarim/freecad/rehber/rehber_secici.py`)

- G2 satırının önüne yeni satır: omuz göbeği grubundaki `625ZZ` ve `Mafsal` adlı parçalar G3'e (K56).
- H0b seçicisi `merkez vidasi` adlı parçayı dışarıda bırakıyor; dirsek horn merkez vidası H0c seçicisine (`Dirsek_ust` grubu) düşüyor
  (K57).

Sonuç (veri1 / zin1 verisi ↔ HEAD verisi, `rehber-veri.json` `parcalar[].a / b`; başka parçada `a` / `b` farkı 0):

| Kimlik | Parça | Yan | Önce (a / b) | Sonra (a / b) | Uçuş |
| --- | --- | --- | --- | --- | --- |
| p0116 | 625ZZ rulman (iç bilezik) | sağ | 39 / 39 | 40 / 40 | önce kendi satırı (u [0,987, 0, −0,163], d 40); sonra kol çatalı p0121 ile birlikte (h p0121, u [1, 0, 0], d 56,9) |
| p0189 | 625ZZ rulman (iç bilezik) | sol | 39 / 39 | 40 / 40 | aynı, h p0194, u [−1, 0, 0] |
| p0117 | Mafsal pulu M5 | sağ | 39 / 39 | 40 / 40 | değişmedi (u [0, 0, −1], d 25), 40.1'de çatal satırından sonraki bağlantı satırı |
| p0190 | Mafsal pulu M5 | sol | 39 / 39 | 40 / 40 | aynı |
| p0118 | Mafsal cıvatası M5x12 | sağ | 39 / 39 | 40 / 40 | değişmedi (u [0, 0, −1], d 42,5) |
| p0191 | Mafsal cıvatası M5x12 | sol | 39 / 39 | 40 / 40 | aynı |
| p0573 | Dirsek horn merkez vidası M3 | sağ | 43 / 48 | 44 / 48 | değişmedi (u [1, 0, 0], d 25), 44.1'de çatal satırından sonraki bağlantı satırı |
| p0630 | Dirsek horn merkez vidası M3 | sol | 43 / 48 | 44 / 48 | değişmedi (u [−1, 0, 0], d 25) |

`b` = robota giriş adımı: omuz parçaları robotta takılıyor (a = b); dirsek parçaları tezgâhta, H1'de (48) robota giriyor.
Parça sayısı 1192 ↔ 1192; BOM / adet değişmedi (yalnız adım). Alt adım sayısı 71 ↔ 71 (yeni alt adım açılmadı: pul + cıvata ve horn
vidası çatalın alt adımında, bağlantı satırı olarak çatal satırından sonra; F10d'den beri alt adımda önce parça, sonra bağlantı satırları
dizilir, `rehber_veri.py`).

### 1.2 Rehber metni ve görünüm alanları (`tasarim/freecad/rehber/rehber_metin.py`)

- **G2 (39):** "3. Karşı tarafa 625ZZ ve M5 pim." kalktı; "2. Servoyu göbeğe cıvatala. Göbeğin karşı tarafındaki mafsal (625ZZ, pul,
  M5×12) G3'te, kol çatalıyla gelir." Bağlantı "Kol başına 4 × M4×16 + 4 kontra somun" (M5×12 + pul çıktı); alet "alyan 3 + 7 mm"
  (alyan 4, M5×12 içindi).
- **G3 (40):** madde 2 "Kol çatalı → horn (4 × M3×8). 625ZZ çatalın arka kolunun Ø16 yuvasında: tezgâhta önceden preslenir, iki
  bileziğiyle çatalla gelir. Çatal yerindeyken mafsal pulu + M5×12: arka koldan rulmanın iç bileziğinden göbekteki M5 ısıl gömmeye (iç
  bileziği göbeğe sıkar, çatal döner)." Bağlantıya "1 × M5×12 + pul mafsal (çataldan sonra)", alet "PH1, alyan 2,5 / 4" (M6 tablosu
  "PH1, alyan 2,5" diyordu), kontrol listesine "Mafsal cıvatası sıkıyken çatal S2 ekseninde elle dönüyor, 625ZZ yuvasından çıkmadı".
  40.1: desen + "Mafsal"; `birlikte` + "625ZZ rulman (iç bilezik)" → "Kol çatalı"; F10f'in K1-a dar istisnası (`ucus_ok` p0121 / p0194)
  silindi; alt adım metni aynı sırayla yeniden yazıldı; `gizli_ok` p0116 / p0189 (§ 2.3).
- **H0b (43):** "Dirsek hornunu servo miline geçir (merkez vidası bu adımda takılmaz: H0c'de, dirsek çatalından sonra)."; bağlantı
  "Kol başına yok (horn merkez vidası M3×5 H0c'de)"; alet "el"; erişim "Düz" (M6 tablosunun erişim sütunu "düz; **çataldan önce**"
  diyordu ve rehberde görünüyordu, ezildi); kontrol "Horn servo milinin dişlisine oturdu"; alt adım adları "Sağ / Sol kol: dirsek hornu".
- **H0c (44):** madde 1'e "çatal yerindeyken dirsek horn merkez vidası M3×5 (PH1), çatalın dış kolundaki erişim deliğinden"; bağlantıya
  "1 × M3×5 horn merkez vidası (çataldan sonra)"; alet "PH1, alyan 2,5 / 4"; kontrol + "Horn merkez vidası sıkı, horn servo milinde
  oturdu"; 44.1 adı "Dirsek çatalı + horn merkez vidası + pim (sağ + sol)", desen + "Dirsek horn merkez"; F10f'in K1-b dar istisnası
  (`ucus_ok` p0562 / p0619) silindi; alt adım metni aynı. Erişim deliği kaynaktan: `dirsek/dirsek_parcalar.py` çatalın dış kolunda
  r 4,5 (Ø9) "horn merkez vidasi erisimi" kesimi.
- `K1_KOL`, `K1_DIRSEK` sabitleri silindi (başka kullanan yok; yerine K56 / K57 notu).
- `rehber_denetim.py` `ASCII_TAMAM` + 4 kelime ("preslenir", "yerindeyken", "koldan", "kolundaki"; Türkçe harfi olmayan doğru yazım,
  gözden geçirildi). Yeni metin ön denetimde bunları buldu, başka kalıntı yoktu.

Tek sıra (F10f üçüncü bakış Y1): 39'da 625ZZ / pim / M5 artık yok, 40 metni rulmanı tezgâhta çatala preslenmiş, pul + cıvatayı
çataldan sonra anlatıyor; 43'te vida yok, 44 vidayı çataldan sonra anlatıyor. Aynı parçanın iki adımda takıldığını söyleyen metin
kalmadı (metin taraması § 4).

### 1.3 Tasarım kaynakları (montaj sırası)

- **Omuz** (`tasarim/freecad/omuz/omuz_rapor.py` SIRA ve üretilmiş `omuz/rapor.md`, `rapor.html`): **değişiklik gerekmedi.** SIRA 2
  "6808-2RS'yi rulman kapağına, 625ZZ'yi çatalın arka koluna bastır." ve SIRA 9 "Çatalı tak: ön kol horn'a 4× M3×8; arka kol M5×12 +
  pulla göbekteki somuna (rulmanı sıkar, çatal döner)." zaten K56 C'nin sırası. Uyuşmayan rehberdi (G2 "Karşı tarafa 625ZZ ve M5 pim").
- **Dirsek** (`tasarim/freecad/dirsek/dirsek_rapor.py` SIRA, `dirsek/rapor.html`): SIRA 5 "Horn'u ... tak, merkez vidasını sık." →
  "Horn'u ... tak (merkez vidası 6. maddede, çataldan sonra)."; SIRA 6'nın sonuna "Horn merkez vidasını çatalın dış kolundaki erişim
  deliğinden sık." Yalnız metin; geometri, parça listesi, korunan değerler değişmedi.
  - `dirsek_rapor.py` bu makinede koşmuyor (HEAD sürümünde de aynı yerde): satır 248 `KABUK_MIN = sayi(min(...))` "min() iterable
    argument is empty" (kol tarama sonucunda "kabuk" boşluğu yok). Rapor betikle yeniden üretilemediği için `dirsek/rapor.html`'de
    yalnız bu iki `<li>` elle, betiğin üreteceği metinle aynı düzeltildi (52,5° ve `&#x27;` kaçışı korunarak); dosyanın başka yeri
    değişmedi (git farkı 1 satır, satır sonları CRLF korundu). Betiğin kırılması bu paketin işi değil (§ 7).
  - Regresyon: `dirsek_rapor.py` ve `rapor.html` `carpisma_kos kontrol`'ün 17 dosyalık özetinde ve `regresyon.py`'nin kaynaklarında
    yok (kodda arandı); regresyon referansı oynamadı.
- **M6 tablosu** (`planlama/adim4/M6-montaj-sirasi.md` satır 132 "mafsal 625ZZ + M5 pim", satır 136 "çataldan önce"): **dokunulmadı.**
  125 cm erişim analizinin kaydı (`M6_erisim.py` + JSON + tablo üçlüsü, `rehber_secici.py` başlık notu); rehber bu sütunları
  `rehber_metin.py`'den eziyor. Rehberde görünen tek M6 kalıntısı (H0b erişim "çataldan önce") ezildi.

## 2. Ölçüm: uçuş, perdelenme, alet erişimi (sim1, yeni veri, rehberin kendi denetimiyle)

### 2.1 Uçuş yolu (adım 39, 40, 43, 44)

42 satır, çarpışan **0**, istisna **0**, `istisna_bos` 0 (40.1 ve 44.1'deki dört "karar" sınıfı dar istisna silinmiş hâlde).
Kol çatalı p0121 / p0194 (+x / −x, d 56,9; iki bilezik + 2 ısıl gömme birlikte) ve dirsek çatalı p0562 / p0619 (+y, d 63,5; iki bilezik
birlikte) temiz; mafsal pulu / cıvatası (−z, d 25 / 42,5) ve horn merkez vidası (±x, d 25) kendi düz yollarında temiz. Bütün rehberin
sayıları § 5 (zin1 `kontrol.json`).

### 2.2 Alet erişimi (rehberin `sira` denetimi: alet ışını + 20 mm el vokseli)

Adım 39, 40, 43, 44'te 44 bağlantı, ulaşılamaz 0. Taşınan bağlantılar: p0118 / p0191 mafsal cıvatası M5x12 "DUZ" (alyan 4, serbest
130 mm, düz el 19,0 mm); p0573 / p0630 dirsek horn merkez vidası "DUZ" (PH1, serbest 80 mm, düz el 29,5 / 31,0 mm). Bu, rehberin kaba
modeli (düz alet ışını, el bölgesi); karar kuyruğundaki "Ölçülmedi: alet erişimi (cıvatanın çatal takılıyken sıkılması), rulmanın
çatala presle takılmasının elle denenmesi" ve K57'deki "çatal takılıyken vidanın horna alet erişimi" ölçümü **değil**: gerçek alet
ve elle deneme yapılmadı, açık not olarak kalıyor.

### 2.3 Perdelenme (40.1'de yeni iki gizli parça)

İç bilezik G2'de alt adımsız adımdaydı (perdelenme orada yalnız bilgi). 40.1'e gelince alt adım sınırına girdi: sim1'de 40.1 sonunda
p0116 ve p0189 (625ZZ iç bilezik) gerekçesiz tamamen gizli (26 yön, 3 mm voksel). Nedeni yeri: kol çatalının arka kolundaki Ø16 yuvada,
mafsal pulu ve cıvata başının altında; 44.1'deki dirsek 625ZZ bileziklerinin (p0583 / p0628 / p0640, F10f'ten beri kimlik anahtarlı
gerekçe) aynısı. Bu iki parçaya F10f'teki gibi kimlik anahtarlı `gizli_ok` gerekçesi yazıldı. **Bu bir uçuş istisnası ya da engel
değil, perdelenme gerekçesi; yine de yeni bir gerekçe olduğu için ayrıca bildiriyorum:** perdelenme alt adım istisnası 115 → 117.
Okur pikseli (F10f-dogrula `gizli_piksel`): p0116 fark 0 / tek başına 333 px, p0189 fark 0 / 202 px, iki temada; yani okur bu
bileziği 40.1 karesinde görmüyor (yuvanın içinde), varlığı yalnız parça listesinde ve metinde.

## 3. Karelere bakış

Zincirden sonra (14.11 01:11) rehberin kendisinden 1400 × 900 kare, kendi başsız Chrome'umla (scratchpad profili, iş bitince
kapandı): "sonra" = çalışma ağacı, "önce" = HEAD `9145164`'ün `rehber/` kopyası (`git archive`, scratchpad). Karelere kendim baktım.

| Adres | Tema | Görülen |
| --- | --- | --- |
| 39 | açık, koyu | Yalnız S2 servo + çıkış mili ve 8 × M4×16 + kontra somun; 625ZZ / pul / M5 yok. Metin "mafsal G3'te, kol çatalıyla gelir". 4 parça, 16 bağlantı. |
| 40.1 | açık, koyu | Kol çatalı turuncu, üst kol tüpü mavi; "bağlandığı yer" pembe artık göbeği de gösteriyor (pul + cıvatanın hedefi). Parça 8 → 10 (iç bilezik ×2), bağlantı 18 → 22 (pul + M5×12 ×2); çatalın arka kolunda ×2 bağlantı yeri işareti. İç bilezik görünmüyor (yuvada, § 2.3). |
| 40.1 patlat | açık, koyu | Çatal yönü (+x / −x) okunuyor; çatal, tüp ve bağlantılar ayrı ayrı; saydam / gri karışması yok. |
| 43.1, 43.2 | açık, koyu | Yalnız dirsek hornu (1 parça, 0 bağlantı); başlık "Sağ / Sol kol: dirsek hornu", merkez vidası yok. Horn alüminyum gerçek renkle açık gri, servo önceki adım grisi üzerinde: önce de aynıydı (HEAD karesi), bu işin getirdiği bir şey değil (§ 7). |
| 44.1 | açık, koyu | Dirsek çatalları turuncu, ön kol pembe; başlık "Dirsek çatalı + horn merkez vidası + pim (sağ + sol)", 6 parça, 22 bağlantı; metin vidayı çataldan sonra ve erişim deliğinden anlatıyor. |
| 44.1 patlat | açık | Çatal yukarıda (+y), M3 vidalar ve pim kendi yollarında ayrı; yön okunuyor. |

Bu bakış görsel bir okuma; hangi küçük bağlantı simgesinin horn merkez vidası olduğunu karede tek tek ayırt etmedim (yeri
`kontrol.json` uçuş satırlarında ölçülü, § 5).

## 4. Metin taraması

`rehber-veri.json` ve `rehber_metin.py`'de "625ZZ", "Mafsal", "M5×12", "merkez vida", "horn" geçen bütün adım / alt adım metinleri
tarandı (zin1 verisi):

- 39 (G2) yalnız "mafsal G3'te, kol çatalıyla gelir" diyor; takma eylemi yok.
- 40 / 40.1 (G3) rulmanın tezgâhta preslenip çatalla geldiğini, pul + M5×12'nin çataldan sonra takıldığını söylüyor.
- 43 / 43.x (H0b) "merkez vidası H0c'de, çataldan sonra" diyor; takma eylemi yok.
- 44 / 44.1 (H0c) vidayı çatal yerindeyken anlatıyor.
- Aynı parçayı iki adımda taktıran metin bulunmadı; ASCII kalıntı denetimi 0.

## 5. Zincir (son kod yazımından sonra)

Son kod yazımı: `rehber_denetim.py` 13.11 23:41:49 (dosya zamanı). Zincir başlangıcı 23:42:17. Zincirden sonra koda yazılmadı (yalnız
bu günlük ve plan belgeleri). `.durum`: `k5657-a/zin1.durum` "BITTI cikis 0 sure 5158 enaz 2.77".

| Sıra | Komut | Başlangıç | Boş bellek (GB) | Süre (s) | Çıkış | Sonuç |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `rehber_uret.py` (FreeCAD'li tam üretim) | 23:42:18 | 5,76 | 2478 | 0 | veri + kareler + PDF + `kontrol.json` |
| 2 | `planlama/d158/F10f-dogrula.py` | 00:23:36 | 5,25 | 623 | 0 | GEÇTİ |
| 3 | `F10e-dogrula.py --goruntu-yok` | 00:33:59 | 5,02 | 897 | 0 | renk_demo KALDI (F10e'den beri bilinen karar), gerisi geçti |
| 4 | `F10d-dogrula.py --goruntu-yok` | 00:48:56 | 5,39 | 719 | 0 | geçti |
| 5 | `F10a-dogrula.py --kanit-yok` | 01:00:56 | 5,21 | 434 | 0 | geçti |
| 6 | `F9b-dogrula.py` | 01:08:10 | — | 5 | 0 | GEÇER, hata 0 |
| 7 | `carpisma_kos.py kontrol` | 01:08:15 | — | 0 | 0 | 17 dosya aynı |
| 8 | `regresyon.py --yazma` | 01:08:15 | — | 0 | 0 | GEÇER, bütün değerler aynı |

`planlama/rehber/kontrol.json` (benim okumam; "önce" HEAD `kontrol.json`):

| Ölçü | Önce | Sonra |
| --- | --- | --- |
| Uçuş satırı | 336 | 340 (+4: 40.1'de pul + M5×12 sağ / sol; horn vidası 43 → 44 taşındı, sayıyı değiştirmedi) |
| Çarpışan | 0 | 0 |
| Uçuş istisnası | 20 | 16 (40.1 ve 44.1'in dört "karar" istisnası silindi) |
| `istisna_bos` | 0 | 0 |
| İstisna sınıfları (sonra) | | dize 9, duruş 4 (41.6), yol 2 (36.1 / 36.2), ölçüm kaydı 1, karar 0 |
| Perdelenme: gerekçesiz / istisna | 0 / 115 | 0 / 117 (§ 2.3) |
| Toplam gizli | 262 | 264 |
| Alt adım | 71 | 71; konsol hatası 0 |
| Alet erişimi: ulaşılamaz | 0 | 0 / 565 |
| ASCII kalıntı | 0 | 0 |
| PDF | 75 sayfa | 75 sayfa, en küçük yazı 8,1 pt, 16198 kB (önce 16193); baskı karesi 121, boş 0 |
| kol_kablo | GEÇTİ | GEÇTİ |

40.1 ve 44.1'in bütün uçuş satırları istisnasız temiz. F10f-dogrula `gizli_piksel`: 11 parça okurun göremediği yerde (p0116 / p0189
dahil, § 2.3); `parca_kare` bilgi.

## 6. Dokunulan dosyalar

- **Kaynak (elle):** `tasarim/freecad/rehber/rehber_secici.py`, `rehber_metin.py`, `rehber_denetim.py`;
  `tasarim/freecad/dirsek/dirsek_rapor.py`, `dirsek/rapor.html` (§ 1.3).
- **Plan belgeleri (elle):** `planlama/d158/karar-kuyrugu.md` (K56 / K57 özet ve "Durum"), `planlama/dongu-158.md` (P10.5b satırı, § 5
  girdileri), bu günlük.
- **Üretilen (zincir):** `rehber/veri/rehber-veri.json` / `.js`; `rehber/goruntu/adim-{39,40,40-01,43,43-01,43-02,44,44-01}.png`;
  `planlama/rehber/kontrol.json`, `Lale-montaj-rehberi.pdf`, `planlama/rehber/goruntu/adim-{39,40,40-01..03,43,43-01,43-02,44,
  44-01..03}.png` ve `adim-33-04.png` (§ 7); `planlama/d158/F10{a,d,e,f}-dogrula.json`. `robot.glb` / `robot-glb.js` değişmedi.
- **Dokunulmayan:** eski 14 değişik dosya (zincir yeniden yazmadı, git durumu bu işten önceki gibi); `omuz_rapor.py`;
  `M6-montaj-sirasi.md`; `.git/info/exclude` klasörleri.

## 7. Açık kalanlar, kapsam dışı fark edilenler

- **Ölçülmedi:** alet erişimi (çatal takılıyken M5×12'nin ve horn merkez vidasının gerçek aletle sıkılması), 625ZZ'nin çatala elle
  preslenmesi. § 2.2'deki sayılar rehberin kaba modeli, ölçüm değil.
- `dirsek_rapor.py` HEAD'de de koşmuyor (satır 248, boş `min()`); rapor betikle yeniden üretilemiyor.
- `M6-montaj-sirasi.md` satır 132 / 136 eski sırayı yazıyor (125 cm kaydı; rehber eziyor).
- Karar kuyruğunda K57 başlığı "S2 horn" diyor; taşınan parça dirsek hornunun merkez vidası (rehber adı "Dirsek horn merkez vidası").
- 40.1 panelinde üst kol tüpü (parça) mafsal cıvatasından (bağlantı) önce listeleniyor (alt adımda önce parça, sonra bağlantı kuralı);
  omuz SIRA'sında M5 tüpten önce. Gerçek sırada fark yaratmıyor (ikisi bağımsız), ama okur için tek sıra değil.
- S2 horn merkez vidası 40.1 panelinde çatal satırından sonra görünüyor (aynı kural; bu işten önce de böyleydi).
- "Bağlandığı yer" kaynak sayıları değişti: baglanti 77 → 74, temas 9 → 12 (taşınan parçaların hedefi yeniden hesaplandı).
- 43.x'te 0 bağlantı varken panel "Bağlantı elemanları takma sırasıyla yukarıdaki tabloda" yazıyor (genel cümle).
- 43.x'te alüminyum horn ile gri servo açık temada yakın tonda (önceden de böyle).
- `planlama/rehber/goruntu/adim-33-04.png` zincirde yeniden yazıldı: HEAD ile piksel farkı 0 (bbox yok), yalnız bayt farkı.
- Bu işin dışında, zincir koşarken (14.11 00:32–01:06 dosya zamanları) çalışma ağacında başka bir işin dosyaları belirdi:
  `planlama/adim3/elektrik.md` değişmiş; izlenmeyen `planlama/adim3/pin-haritasi.md`, `planlama/d158/pin-karari-gunluk.md`,
  `pin-karari-kontrol.md`, `pin-karari-kontrol-2.md`. Dokunmadım; commit adımında ayrı tutulmalı.
- K56 / K57 "kapandı" C adımında, bağımsız kontrolden sonra.
