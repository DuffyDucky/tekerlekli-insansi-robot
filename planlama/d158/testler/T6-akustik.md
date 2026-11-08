# T6 · Akustik: Ø3 delikler, mikrofon–hoparlör, gürültü tabanı

Kâğıt T6 / 9 · Lale 1,58 m · sürüm 08.11.2026

| Tarih | Ölçen | Yazan | Kontrol eden | Ses seviyesi ölçer markası/modeli |
|---|---|---|---|---|
| | | | | |

## Amaç

Mikrofon dizisinin (ReSpeaker Mic Array v2.0) robotun üstündeki yerinde ne kadar iyi duyduğunu üç bölümde ölçmek:
**A** ölçü (delikler, mikrofon–hoparlör uzaklığı), **B** servo ve motor güçleri açılınca gürültü tabanındaki artış,
**C** Ø3 deliklerin ve robotun kendi hoparlörünün (yankı) etkisi.

## Neden önemli

Dizi kafa kabuğunun 2,5 mm altında, tavandaki 4 adet Ø3 delikten duyuyor; delik çapı **varsayım** (`secenekler.md:215`, `secenekler.md:274`,
`uygulama-notu.md:45`). Araştırma önerisinin H1 hedefi: dizi hoparlörden en az 40 cm uzakta ve servo ile motor güçleri açıkken gürültü
tabanındaki artış **en çok 3 dB** (`oneri-taslak-v8.md:68`). Bu değerlerin hiçbiri ölçülmedi (`secenekler.md:247-254`).

### Doğruladığı varsayım

| Değer | Kaynak | Durum |
|---|---|---|
| Tavanda 4 delik, Ø3 | `uygulama-notu.md:45`, `secenekler.md:215`, `secenekler.md:274` | **Varsayım** (çap) |
| Mikrofon portu → tavan iç yüzü 4,9 mm, port → dış hava 7,4 mm | `secenekler.md:213-214` | Model |
| Mikrofon–hoparlör ≥ 400 mm (H1); model: ev pozu 595,7 mm, en az 574,3 mm (pan −90°, tilt −15°) | `oneri-taslak-v8.md:68`, `dongu-158.md:25`, `uygulama-notu.md:24-25`, `secenekler.md:231` | Model; korunan değer |
| Servo + motor güçleri açıkken gürültü tabanı artışı ≤ 3 dB | `oneri-taslak-v8.md:68`, `oneri-taslak-v8.md:199` | Hedef; ölçülmedi |
| Soğutucu fanının gürültüsü ayrıca raporlanır, 3 dB ölçütüne katılmaz | `oneri-taslak-v8.md:199` | Yöntem. Not: `secenekler.md:251` fanı da 3 dB içinde sayıyor; bu kâğıt öneri metnini izler |
| Tilt yazılım sınırı ±13° | `kararlar:19` | Karar |
| Hoparlör ekseni duvara paralel (yatayın 35° altı) | `uygulama-notu.md:59`, `karar-kuyrugu.md:21` (K6) | Model; K6 açık |

## Gereken alet

- Şerit metre, kumpas, Ø3,0 ve Ø3,5 matkap ucu (ölçü pimi olarak, sap tarafı)
- Ses seviyesi ölçer, A ağırlıklı, yavaş yanıt (`oneri-taslak-v8.md:160`); yoksa telefon uygulaması (yalnız aynı ayarı tekrarlamak için)
- Test hoparlörü (kutulu, kablolu) + bilgisayar; pembe gürültü dosyası (30 s), konuşma dosyası (30 s); tripod
- Pi'de: `arecord`, `sox`; ReSpeaker **6 kanallı** yazılımı ve Seeed'in `tuning.py` aracı (kaynak: https://wiki.seeedstudio.com/ReSpeaker_Mic_Array_v2.0/ ,
  `secenekler.md:349`). 6 kanallı yazılımda kanal 0 işlenmiş ses, kanal 1–4 ham mikrofonlardır (Seeed wiki).

Seviye ölçme komutları (kart numarasını `arecord -l` ile bul):

```
arecord -D plughw:KART,0 -c 6 -r 16000 -f S16_LE -d 60 olcum.wav
sox olcum.wav -n remix 1 stats 2>&1 | grep "RMS lev"     # kanal 0 (işlenmiş)
sox olcum.wav -n remix 2 stats 2>&1 | grep "RMS lev"     # kanal 1 (ham)
rm olcum.wav                                              # kayıt tutulmaz
```

Seviye dBFS olarak okunur (negatif sayı). Fark = açık − kapalı (dB).

## Güvenlik

- **B bölümünde servolar güçlü ve konum tutuyor:** kolların erişim alanında kimse durmaz, acil stop elde ve denenmiş. Servo gücü verilmeden
  önce yazılım servo hedeflerini son konuma yazmış olmalı (`elektrik.md:224`), yoksa kollar ani hareket eder.
- Motor gücü açıkken tekerlerin altı takozlu, robot zeminden kaçamaz; PWM 0.
- Akü: ana sigorta ve dal sigortaları takılı.
- Hoparlör testlerinde kulak hoparlöre yakın tutulmaz.
- **Ses kaydı saklanmaz:** seviye hesaplanınca dosya silinir (`oneri-taslak-v8.md:199`).

## Yöntem

**A. Ölçü (robot kapalı)**

1. Tavandaki delikleri say. Her deliğe Ø3,0 ucunu sap tarafından sok: giriyor mu? Ø3,5 giriyor mu? Kumpasla bir deliğin çapını ölç.
2. Kafa ev pozunda: dizinin merkezinden (dört deliğin ortası) hoparlör ızgarasının merkezine şerit metreyle düz çizgi ölç.
3. Kafayı elle ya da yazılımla **pan −90°, tilt −13°** konumuna getir (en kötü pozun izinli sınırı); 2. adımı tekrarla.

**B. Gürültü tabanı (`oneri-taslak-v8.md:199` yöntemi)**

4. Oda: kapı ve pencere kapalı. Hoparlörler susarken ses seviyesi ölçerle odanın gürültüsünü oku: **≤ 40 dB(A)** olmalı (`oneri-taslak-v8.md:260`);
   değilse daha sessiz saate al. Soğutucu fanı iki ölçümde aynı durumda kalmalı (ör. sabit orta hız).
5. **B1 kapalı:** servo ve motor güçleri kapalı (röle K1 çekmemiş). 60 s kaydet, kanal 0 ve kanal 1 seviyesini yaz.
6. **B2 açık:** röle çekili (anahtarlı 12 V var), servolar ev pozunda konum tutuyor, motor sürücüsü etkin ama PWM 0 (tekerler dönmez;
   "motor gücü açık" bu kâğıtta böyle yorumlandı). 60 s kaydet, aynı iki seviyeyi yaz.
7. B1 ve B2'yi bir kez daha yap (toplam iki tekrar). Fark = B2 − B1.
8. **B3 soğutucu (ayrı rapor):** servo ve motor güçleri kapalı. Fan kapalı 60 s, fan tam hız 60 s. Fanı Pi 5'te
   `/sys/class/thermal/cooling_device0/cur_state` ile 0 ve en yüksek değere almak mümkün olabilir (**doğrulanmadı**; yöntemi yazılım ekibi belirler).

**C. Delik etkisi ve yankı**

9. **C1 delik etkisi:** test hoparlörünü robotun önüne, 1,0 m uzağa, 1,6 m yüksekliğe koy (`oneri-taslak-v8.md:175`, `:185`). Pembe gürültüyü
   hoparlörün 1 m önünde 60 dB(A) okunacak sesle çal (`oneri-taslak-v8.md:187`). Ses ayarını kaydet ve değiştirme.
   - Önce **tavansız**: **Pi'yi kapat ve kafanın enerjisini kes** (dizi USB'si Pi'ye bağlı; servo gücü de kapalı). Dizi tavandaki 3 vidadan
     sökülür (`secenekler.md:197`), aynı yükseklikte ve aynı yöne bakacak biçimde kafanın üstüne açıkta konur (bant ya da küçük sehpa;
     `secenekler.md:248` "kapaksız diziyle karşılaştırma"). Enerji ver, Pi'yi aç. 30 s kaydet, kanal 0 ve 1 seviyesi; `tuning.py DOAANGLE` ile 10 okuma.
   - Sonra **tavan takılı**: yine Pi'yi kapat, enerjiyi kes, diziyi tavana vidala (Ø3 delikli tavanın altında), enerji ver; aynısını yap.
   - Test hoparlörünü sağ 45°'ye al (aynı 1,0 m), iki durumu tekrarla.
10. **C2 yankı:** test hoparlörü sessiz. Robotun kendi hoparlöründen (PAM8403) pembe gürültüyü, robot hoparlörünün 1 m önünde 60 dB(A) okunacak
    seviyede çal (varsayım: ziyaretçi konuşmasıyla aynı düzey). 30 s kaydet. Kanal 1 (ham) ve kanal 0 (işlenmiş) seviyesini yaz.
    Bastırma = kanal 1 − kanal 0.
    Not: ReSpeaker'ın yankı gidermesinin, sesin dizinin kendi çıkışından değil ayrı USB ses kartından çalındığı bu düzende referans alıp
    alamadığı **doğrulanmadı**; sonuç bunu gösterir, üretici belgesinde de kontrol edilmeli.

## Kayıt tablosu

**A. Ölçü**

| Ölçüm | Değer | Birim |
|---|---|---|
| Delik sayısı | | adet |
| Ø3,0 uç giriyor (4 delikte) | ☐ evet ☐ hayır | |
| Ø3,5 uç giriyor | ☐ evet ☐ hayır | |
| Kumpasla delik çapı | | mm |
| Mikrofon–hoparlör, ev pozu | | mm |
| Mikrofon–hoparlör, pan −90° tilt −13° | | mm |

**B. Gürültü tabanı** Oda gürültüsü: ______ dB(A)

| Tekrar | B1 kapalı, k0 (dBFS) | B2 açık, k0 (dBFS) | Fark k0 (dB) | B1 kapalı, k1 (dBFS) | B2 açık, k1 (dBFS) | Fark k1 (dB) |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |

| B3 soğutucu | Fan kapalı k0 / k1 (dBFS) | Fan tam hız k0 / k1 (dBFS) | Fark k0 / k1 (dB) |
|---|---|---|---|
| | / | / | / |

**C. Delik etkisi ve yankı** Test hoparlörü ses ayarı: ______

| Durum | Açı | k0 (dBFS) | k1 (dBFS) | DOA ortalaması (°) | DOA en küçük / en büyük (°) |
|---|---|---|---|---|---|
| Tavansız | 0° | | | | / |
| Tavan takılı | 0° | | | | / |
| Tavansız | 45° | | | | / |
| Tavan takılı | 45° | | | | / |

| C2 yankı | k1 ham (dBFS) | k0 işlenmiş (dBFS) | Bastırma k1 − k0 (dB) |
|---|---|---|---|
| Robot hoparlörü, 60 dB(A) @ 1 m | | | |

## Geçer / kalır sınırı

| Ölçüt | GEÇER | Kaynak |
|---|---|---|
| A: mikrofon–hoparlör, iki pozda | **≥ 400 mm** | `oneri-taslak-v8.md:68`, `dongu-158.md:25` |
| A: delik sayısı ve çapı | **4 delik**, Ø3,0 uç giriyor | `uygulama-notu.md:45`, `secenekler.md:215` (çap varsayım) |
| B: B2 − B1, kanal 0, iki tekrarın büyüğü | **≤ 3 dB** | `oneri-taslak-v8.md:68`, `oneri-taslak-v8.md:199` |
| B: oda gürültüsü | **≤ 40 dB(A)**, değilse ölçüm geçersiz | `oneri-taslak-v8.md:260` |
| C1: tavan takılı − tavansız seviye farkı (k0, 0° ve 45°) | **≤ 3 dB kayıp** | **Varsayım, kaynakta sınır yok** (B'deki 3 dB ölçeğine benzetildi) |
| C1: DOA ortalaması farkı, tavan takılı ↔ tavansız | **≤ 10°** | **Varsayım, kaynakta sınır yok** |
| C2: yankı bastırma (k1 − k0) | **≥ 10 dB** | **Varsayım, kaynakta sınır yok** |

B3 (soğutucu) yalnız raporlanır. C satırları kaynaksız olduğu için C'de kalma **KOŞULLU** sayılır ve karara gider; A ve B'de kalma **KALIR**'dır.

## Sınır aşılırsa

- **A, 400 mm altı:** korunan değer bozulmuş demektir (`dongu-158.md:25`): durdur, orkestratöre ve **Ahmet Yorulmaz**'a bildir. Delik sayısı/çapı
  farklıysa kafa kabuğu betiği (`tasarim/freecad/kafa/kafa_parcalar.py`) için tasarım ajanına.
- **B, 3 dB üstü:** H1 hedefi tutmuyor. Öneri metnindeki önlemler: dizi USB'si güç kablolarından ayrı kanal, servo ve motor hatlarıyla mantık
  devrelerinin tek noktada topraklanması (`oneri-taslak-v8.md:199`). Tasarım ajanı + Ahmet Yorulmaz. [T4](T4-pam8403-ses-karti.md) uğultu gözlemiyle birlikte değerlendir.
- **C:** delik çapı ya da tavan biçimi için tasarım ajanına; hoparlör ekseni kararı `karar-kuyrugu.md` **K6** (varsayılan "paralel, ölçümden sonra
  yeniden"); yankı giderme referansı sorusu yazılım ekibine (Efe). Karar Ahmet Yorulmaz'da.

## Sonuç

A ☐ GEÇER ☐ KALIR   B ☐ GEÇER ☐ KALIR   C ☐ GEÇER ☐ KOŞULLU

Ölçen imza: ____________  Kontrol eden imza: ____________

Kaynak dosyalar için kısaltma tablosu: [00-genel.md](00-genel.md).
