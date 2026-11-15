**KAYNAK GEÇER**: D1, D2 ve D3 doğru ve kilitli; dar ekler doğru yerde. Düzeltme şartı olan bulgu yok. Beş öneri var, hiçbiri montajcıya yanlış bilgi vermiyor.

# F10k kontrolü 2 · P10.7b2c düzeltme turu 1 (dar, kaynak düzeyi)

15.11.2026, bitiş 14:01 (saat okundu). Dal `lale-duzeltme`, HEAD = uzak = `b6022c3`; paket commit edilmemiş. Salt okuma: depoda
yalnız bu dosya yazıldı. Bu turun farkını kendim çıkardım. Taban, ilk kontrolün 13:08'de aldığı MD5 özeti (1039 dosya). Turdan önceki
kopyalar o özetle birebir tuttu. Özete göre değişen 10 dosya: `rehber/app.js`, `rehber_metin.py`, `rehber_kablo.py`,
`rehber_denetim.py`, `rehber_uret.py`, `rehber_kritik_onay.json`, `lale158/kablo_yolu_taban.py`, `dongu-158.md`, `karar-kuyrugu.md`,
`F10k-gunluk.md`. `kablolar.json`, `kablolar.md`, `pin-haritasi.md`, `maliyet.json`, `README.md`, `kod/` ve izlenen CAD dosyaları
değişmemiş. Günlük `kablo_yolu_taban.py`'yi dosya listesinde saymıyor; değişiklik orada yalnız `DAGITIM_C` sabiti ve yorum, SV3'ün son
noktası aynı değer. Koşulardan önce ve sonra kaynakların özetini aldım: aynı. Bozmaları bellekteki kopyada yaptım.

## Bulgular (önem sırasıyla; hepsi öneri)

1. **`kablolar.md`'de "Dağıtım kartı C (kafa)" eksiz** (`planlama/adim3/kablolar.md:1112`, `:1122–1123` P03; `:1295`, `:1355` S09 /
   S10). Rehber K1'de montajcıyı kablo listesine bu dosyaya gönderiyor. P03 bölümünde kartın yeri yazmıyor; SV3 notunda (`:683`) yalnız
   "XL4016 C'nin yanında" var. Rehber metninin hepsinde ek var. Montajda risk düşük, çünkü montajcı P03'ü K1'deki satırdan bağlıyor.
   En dar düzeltme: `kablolar_uret.py` görünümünde aynı eki uçlara koy, kayıttaki ad aynı kalsın. Sonraki paket.
2. **E3a'da etiketsiz bir kablo boyu kaldı** (`rehber_metin.py:650`, kontrol listesi): "D24V50F5 → Pi USB-C yaklaşık 10 cm". Kayıtta K03
   `boy_tahmin` 200 mm, `boy_not` "belgede ~10 cm (EL:279)". Şema kartında "çizim yolu ~47 mm (kesim boyu değil)" yazıyor. Metin HEAD'de
   de vardı, bu turda değişmedi ve kuyrukta. Başka tarama sonucum: S2 uzatması 1700, H01 ve K04 30 cm, K2'deki önerilen boylar kayıtla
   aynı. Öbür mm sayıları ya parça ölçüsü ya koordinat.
3. **D2 cümlesi daha kesin olabilir:** kayıtta U06'nın ucu "ESP32 · micro USB". Cümle "USB girişine" diyor; doğru, ama "micro USB
   girişine" demek daha iyi. Aynı kartın kb satırı zaten "ESP32 · micro USB" gösteriyor. Günlükte "soket tipi rehberde yazmıyor" deniyor;
   kb satırı için bu doğru değil.
4. **Kilitlerin sınırları** (aşağıdaki kendi bozmalarımda): (a) `sema_boy_etiketi_denetle` yalnız `app.js`'i okuyor. `yazdir.html`
   bugün sayı göstermiyor ama ona bir kilit yok. (b) Kayıttaki adın yazımı değişirse (ör. büyük harf "(Kafa)") kb satırı eksiz kalır ve
   hiçbir denetim düşmez. (c) SV3'ün ucu, `SEMA_KONUM` ve `DAGITIM_C` üçü birlikte panelin öbür köşesine taşınırsa geometri sınaması
   geçer; yalnız `sema_boy` tazeliği ve onay kaydı yakalar. (d) KABLO_AD'deki "K1'de" eki yalnız metin onay kaydıyla korunuyor.
5. **`planlama/dongu-158.md:186` eskimiş:** "27 gösterim şeması, kol bölümleri değişmedi" yazıyor. Turun ekinde kol bölümleri de
   etiketlendi (günlük bunu düzeltmiş, döngü kaydı düzeltmemiş). Montajcıyı etkilemez.

## Montajcının göreceği yeni metinler (harfiyen, çözülmüş)

- D1, tıklama kartı (`app.js:1124–1125`): gösterim şemasında `Kablo şeması · adım N (KOD) · çizim yolu ~N mm (kesim boyu değil)`, kol
  içi bölümde `… · bölüm uzunluğu ~N mm (kesim boyu değil)`.
- D2 (K2 kablo listesi): "ESP32 USB" şemasının (U06) taban ucu yanlış yerde, güç panelinin üstünde çizili (şema yeniden çizilecek):
  kablonun taban ucu elektronik katındaki ESP32 taşıyıcısında ESP32'nin USB girişine takılır
- D3 (K1, P03 satırı): … → Dağıtım kartı C (kafa) tilt sinyal girişi. Dağıtım kartı C (kafa): kart güç panelinde, XL4016 C'nin yanında;
  adındaki "kafa" beslediği pan / tilt servolarıdır. Dağıtım kartı C modelde yok, yeri çizilmez; …
- D3, kb satırları (SV3, S09, S10, P03): `… → Dağıtım kartı C (kafa) (kart güç panelinde, XL4016 C'nin yanında; adındaki "kafa" beslediği
  pan / tilt servolarıdır) · V+ · 16 AWG …` (SV3'te); öbürlerinde de aynı ek.

## Doğruladıklarım

- **D1:** Etiketin tek bir anlamı var: sayının "çizim yolu" ya da "bölüm uzunluğu" olduğunu ve kesim boyu olmadığını söylüyor. Kesim
  boyunun nerede olduğunu söylemiyor; bu iş kuyrukta. `boy_mm` taşıyan iki tür var: `rehber_veri.py:893` (SEMA'nın 27 şemasının hepsi)
  ve `rehber_kol_kablo.py:399` (38 bölüm, `kol=yan`). Etiket ikisinde de uygulanmış. `kol` alanı yalnız kol bölümlerinde (mevcut veride
  38 / 38, gösterim şemalarında 0). Etiketsiz kalan bir gösterim yok: CAD "Kablo yolu N" parçaları (`parcaSec`) sayı göstermiyor.
  Basılı sayfa `yazdir.html:172`'de yalnız "(şema)" basıyor. Sayıları kayıtla karşılaştırdım. Eski şemalar: K04 114 / liste 300, U04
  217 / 350, H01 254 / 300. Yeni şemalar: SV3 39 / 300, K01 14 / 200. Kol bölümünün sayısı bölümün kendi uzunluğu, kayıttaki boy
  değil (S02 `gereken_mm` 1700). Etiket bu yüzden hepsinde gerekli.
- **D2:** Kayıtta U06'nın uçları "USB hub · port 2 → ESP32 · micro USB". Şemanın taban ucu (51,6; 190; −120): bu nokta güç panelinin
  (y 174,5–179,5; z −250…23,8) 10,5 mm üstünde. ESP32 DevKit ise elektronik katındaki taşıyıcıda (z 61…89). Cümle doğru. Montajcı ESP32'yi
  bu tarifle bulur, çünkü B6a "ESP32 taşıyıcı" diye tarif ediyor ve taban şemalarının adlarında da aynı ad geçiyor. Şemanın adı ("→ ESP32
  (taban)"), K1 madde 7 ("ESP32 USB'nin (U06) taban uçlarını bağla") ve K2 madde 4 ile çelişmiyor.
- **D3:** Kayıtta dayanak P7b2a-6 ("Dağıtım kartı C güç panelinde, XL4016 C'nin yanında"), SV3 `boy_tahmin` yöntemi ve B5a iş metni.
  Adı rehber metinlerinin hepsinde (`ADIM`, SEMA adları, KABLO_AD, 74 kb satırı) kendim aradım. Tam ad yalnız K1 P03 satırında ve kb
  satırlarında geçiyor, ikisinde de ek var. Öbür yerlerde (`rehber_metin.py:226`, `:230`, `:416`, `:841`, `:1934`) ad küçük harfle ve
  "(kafa)" eki olmadan geçiyor; yer ya yazılı ya da yerin yanlış anlaşılacağı bir şey yok. Kayıttaki ad değişmemiş.
- **SV3'ün nominal noktası** (100; 192; −60): güç panelinin 12,5 mm üstünde, x XL4016 C'nin içinde (65…130), kutunun −z kenarından 36,5
  mm uzakta. SV3'ün şemadaki son noktasıyla aynı. SV3'ün adında "yeri yaklaşık" yazıyor, B5a notunda "şemanın o ucunun yeri yaklaşık".
- **KABLO_AD ekleri:** 9 (G19), 11 (Q01, Q02) ve 12 (N01, N02, B02): bu altı kimliğin SEMA adımı K1, ekler doğru. 4'teki M02 → B3 de
  doğru.
- **Onay kaydı farkı** (turdan önceki kopyayla, satır satır): kablo bölümünde 4 girdi eklenmiş, çıkan yok. Listeye 2 `ZORUNLU_ALAN`
  girmiş. Metinde 4 girdi aynı cümlenin uzamış hâli (E3a notu, KABLO_AD 9, 11, 12), 2 girdi yeni (D2, D3). Kritik değer değişmemiş, uyarı
  silinmemiş.
- **Yan etki:** Talimat cümlelerinde değer, sıra ve güvenlik koşulu aynı. Değişen metinler yalnız yukarıdaki ekler. `rehber_uret.py`'de
  yalnız üç denetim çağrısı eklenmiş (2 satır). Devre değerleri, kablo uçları ve boylar değişmemiş.
- **Gizlilik:** `.git/hooks/pre-push`'un yedi kalıbını bu turda eklenen 537 satıra uyguladım (fark satırları ve günlüğün "Düzeltme turu
  1" bölümü). Kalıplar: anahtar biçimleri, anahtar ya da parola ataması, e-posta, IBAN ya da telefon, yerel yol ve makine adı, takma ad,
  ekip soyadları. Eşleşme 0.

## Kendi bozmalarım (bellekte; turun denetimleri + onay kaydı)

Yakalananlar:
- D1: "çizim yolu" → "kablo boyu"; "(kesim boyu değil)" → "(kesim boyu)"; semaSec'te ikinci, etiketsiz bir boy; `const boy`'un
  kullanılmaması.
- SV3: uç, nominal nokta ve `DAGITIM_C` birlikte 60 mm −z'ye (uç ana sigorta yuvasına düşüyor); uç tek başına 8 mm oynatıldı (yalnız
  `sema_boy` yakaladı, geometri eşiğin içinde).
- Gösterim notu: K1 notunun silinmesi (9 şema); E4 notunda "boy ölçümü değildir" → "boy ölçüsüdür"; SV3 ve K01 adlarından "yeri
  yaklaşık"ın silinmesi.
- Yanlış adım: G19 → E3a, G19 → B6a, N01 → B3, K01 → E4.
- D3: B5a'ya eksiz ad; K1 ekinde "güç panelinde" → "kafada".
- D2 (`ZORUNLU_ALAN`): "ESP32 taşıyıcısında" → "güç panelinde"; "yanlış yerde" → "yaklaşık yerde"; cümle K2'den K1'e taşındı; D3 eki
  K1'den B5a'ya taşındı. Hepsi zorunlu ve onay ile.

Yalnız onay kaydının (ya da `sema_boy`'un) yakaladıkları ya da hiçbir denetimin yakalamadıkları (sınır; öneri 4):
- uç, nominal nokta ve `DAGITIM_C` birlikte x −100'e;
- KABLO_AD 9 "K1'de" → "B3'te" (metin onayı 1); KABLO_AD 12 ekinin silinmesi;
- G19 → B3 ve B3 notunun G19'u da anması (G19 tabloda B3'te de var; yapısal kural geçer);
- K1 ekinin arkasına çelişen bir cümle; K2'ye ayrı madde olarak "U06'nın taban ucunu şemadaki uca tak" (yapısal kural geçer, metin onayı
  yakalar);
- kayıttaki adın büyük harfle "(Kafa)" yazılması: hiçbir denetim yakalamadı;
- `parcaSec`'e köşeli ayraçla yazılmış bir boy (kasıtlı atlatma): yakalanmadı, gerçek risk değil.

## Koşular (FreeCAD'siz; `py -3 -B -X utf8`, `PYTHONDONTWRITEBYTECODE=1`)

| Koşu | Çıkış | Sayılar |
|---|---|---|
| `kablolar_uret.py --kontrol` | 0 | kablolar.md ve elektrik.md bloğu güncel |
| `kablolar_denetim.py` | 0 | GEÇER (sema_boy dahil) |
| `kablolar_denetim.py --bozma-denemesi` | 0 | 172 bozma |
| `rehber_denetim.py --kaynak` | 0 | metin 575; ASCII 0; elektrik 0; zorunlu eksik 0; onay farkı 0 (kablo 165, liste 204, metin 1040); tamlık 172, eksik 0, muaf 19; kablo 74 / 74 |
| `rehber_denetim.py --bozma-denemesi` | 0 | 249 / 249 |
| `rehber_kablo.py` | 0 | 68 (CAD 39, kol 6, şema 29) / 5 / 1; şema 27, hata 0, bilgi 15, istisnalı 5; tablo hata 0; şema boyu hata 0, şema > kayıt 0; kart etiketi 0, gösterim notu 16 şema hata 0, yer eki hata 0; onay tutuyor |
| `rehber_kablo.py --bozma-denemesi` | 0 | 86 / 86 |
| `rehber_kablo.py --veri rehber/veri/rehber-veri.json` | 0 | eşlemesiz 0 (o sırada veri eski üretimdendi) |
| `rehber_kablo.py --veri … --bozma-denemesi` | 0 | 95 / 95 |
| `rehber_kol_kablo.py --yazma` | 0 | 38 bölüm, kaynak fark 0,0007 mm, GEÇTİ |
| `node --check rehber/app.js` | 0 | |

Sayılar günlükteki ekten sonraki değerlerle aynı.

## Sonraki pakete kalabilecekler

Öneri 1 (`kablolar.md`'de yer eki), öneri 2 (E3a "10 cm", kuyrukta), öneri 3 ("micro USB"), öneri 4'teki kilit sınırları (basılı sayfa,
ad yazımı, nominal noktanın sınırı), öneri 5 (döngü kaydı). Bunlara ek olarak kuyruktaki işler: kesim boyunun karta yazılması, U06'nın
yeniden çizimi (çizilince D2 cümlesi ve kilidi kalkar), eski kaynakların gösterim notu.

## Bakmadıklarım ve ortam notu

- Üretim, kareler, PDF ve tarayıcı görülmedi. `app.js` yalnız kaynak ve `node --check` ile sınandı.
- `kablolar_denetim.py` ve `kablolar_uret.py` bu turda değişmedi; bakmadım.
- Paralel üretim 13:55'te başladı: `rehber/veri` ve `planlama/rehber/goruntu` değişmeye başladı. Depoda 4 `__pycache__` klasörü var
  (`planlama/adim4`, `tasarim/freecad`, `tasarim/freecad/lale158`, `tasarim/freecad/rehber`). Hepsi 13:55–13:59 arasında `cpython-311`
  ile yazılmış, yani FreeCAD'in Python'u ve üretim koşusu. Benim koşularım başka bir Python sürümüyle ve `-B` ile koştu. Klasörlere
  dokunmadım. `FREECAD-KILIT.txt` "boş".
