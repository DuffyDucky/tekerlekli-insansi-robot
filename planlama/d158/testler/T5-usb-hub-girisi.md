# T5 · USB hub girişinde gerilim (yükte)

Kâğıt T5 / 9 · Lale 1,58 m · sürüm 08.11.2026

| Tarih | Ölçen | Yazan | Kontrol eden | USB ölçer markası/modeli |
|---|---|---|---|---|
| | | | | |

## Amaç

USB hub gövdede, üst arka servis kapağının içinde duruyor ve Pi'den uzun bir kabloyla besleniyor. Hub'ın **girişindeki** ve
**çıkış portlarındaki** 5 V gerilimini yük altında ölçmek, Pi'nin USB portlarından çekilen toplam akımı ölçmek.

## Neden önemli

Hub USB'den besleniyor (kendi adaptörü yok). Kablo yolu uzadı: Pi 3 numaralı port → ~1 m USB-A uzatma → hub'ın 130 mm kablosu
(`uygulama-notu.md:106`). Göğüs dokunmatiği ve ESP32 bu tek kabloya bağlı; hub girişindeki gerilim **ölçülmedi**
(`uygulama-notu.md:100`, `secenekler.md:254`). Gerilim düşerse dokunmatik kopar ya da ESP32 USB'den kaybolur.

### Doğruladığı varsayım

| Değer | Kaynak | Durum |
|---|---|---|
| Hub yeri: gövde, üst arka servis kapağı içi | `uygulama-notu.md:58` | Model (B + R1 seçimi) |
| Yol: Pi 3 → uzatma → hub; sipariş boyu 920 mm + hub 130 mm | `uygulama-notu.md:106` | Model; uzatma listede yok (`karar-kuyrugu.md` K4) |
| Hub 1 göğüs dokunmatiği, Hub 2 ESP32, Hub 3–4 boş | `uygulama-notu.md:129-132` | Model; altıncı cihaz bilinmiyor (`karar-kuyrugu.md` K1) |
| Göğüs dokunmatiği ~80 mA (5 V) | `07-gogus.md:19`, `elektrik.md:19` | Üretici wiki'si |
| ESP32 asıl beslemesi çevre 5 V; USB VBUS'ta seri 1N5819. Çevre 5 V düşerse ESP32 Pi'den ~4,4–4,7 V alır | `elektrik.md:250-251` | Tasarım (diyotlu VEYA) |
| ESP32 akımı 0,24 A | `elektrik.md:320` | Tahmini |
| Pi 5 USB çıkışları toplam 1,6 A (5 A kaynakta) | `07-gogus.md:47` | Satıcı/üretici notu |
| Hub girişinde gerilim yeterli | `uygulama-notu.md:100` | **Ölçülmedi**; bu kâğıt doğrular |

## Gereken alet

- USB gerilim/akım ölçer (USB-A erkek–dişi, 0,01 V çözünürlük) ×1, varsa ×2
- Multimetre
- İsteğe bağlı: USB yük kartı (ayarlı, 0,5 A), altıncı cihazı taklit etmek için
- Robot kurulu: Pi kafada, hub kapakta, uzatma boyundan geçmiş, ESP32 tabanda

## Güvenlik

- **ESP32 resetlenirse röle bırakır, servo ve motor gücü kesilir, kollar düşer** (`elektrik.md:229`). Bu testte servo gücü **kapalı**
  olmalı (anahtarlı bara kapalı) ya da kollar ev pozunda ve destekli. L2'de ESP32'nin USB'den beslenmesi bilerek zorlanır.
- Akü: ana sigorta, F3 (kafa) ve F4 (çevre 5 V) takılı. Servis kapağını açarken enerji kapalı.
- **Sigorta enerji varken çekilmez ve takılmaz:** sigorta kutusu akü barasının yanında. L2 için önce ana anahtarla enerjiyi kes, F4'ü çıkar,
  sonra enerji ver; L2 bitince yine enerjiyi kesip F4'ü geri tak.
- **Saat, yüzük, bileklik çıkar** (sigorta kutusu ve bara yakınında çalışılıyor).
- USB ölçeri takıp çıkarırken ilgili cihaz bir an kopar; ESP32 portu açıkken çıkarma.

## Yöntem

1. Ölçüm noktaları: **U1** Pi 3 numaralı portun çıkışı (uzatmanın Pi ucu ile Pi arasına ölçer), **U2** hub girişi (uzatmanın dişi ucu ile
   hub fişi arasına ölçer), **U3** Hub 1 portu (göğüs dokunmatiği ile hub arasına), **U4** Hub 2 portu (ESP32 kablosu ile hub arasına).
   Tek ölçer varsa her yük durumunu noktalar arasında tekrarla.
2. Yük durumları; her birinde 1 dk bekle, en düşük gerilimi ve en yüksek akımı yaz:
   - **L0:** hub takılı, porta cihaz yok.
   - **L1:** dokunmatik + ESP32 bağlı, çevre 5 V **açık** (normal çalışma). Dokunmatik ekrana sürekli dokun, ESP32 Pi ile seri haberleşiyor.
   - **L2:** çevre 5 V **kapalı**, ESP32 USB'den beslenir; en kötü durum. Sıra: **enerjiyi kes → F4'ü çıkar → enerji ver** → Pi açılınca
     L1'deki gibi dokunmatik ve seri haberleşme. Bitince enerjiyi kes, F4'ü geri tak.
   - **L3 (isteğe bağlı):** L2 + Hub 3'e 0,5 A yük kartı (altıncı cihaz yerine; varsayım: USB 2.0 tek cihaz sınırı).
3. Her durumda kontrol et: dokunmatik çalışıyor mu? ESP32 görünüyor mu (`ls /dev/ttyUSB*`)? ESP32 resetlendi mi (boot mesajı)?
4. **Pi USB toplamı:** L2'de Pi'nin dört portunu sırayla ölç (ölçeri her portun önüne tak): Pi 1 ReSpeaker, Pi 2 ses kartı, Pi 3 hub,
   Pi 4 kafa ekranı Touch (`uygulama-notu.md:125-128`). Toplamı yaz. Ses kartı ölçülürken hoparlörden konuşma çalsın.
5. Kablo düşümü = U1 − U2. Yaz.
   **Ölçerin kendi düşümü:** her USB ölçer araya kendi direncini (fiş + şönt) ekler, birkaç yüz mA'de onlarca mV olabilir. U1 ve U2 iki ölçerle
   aynı anda alınırsa U2 iki ölçerin düşümünü de içerir; tabloya "iki ölçer" yaz. Tek ölçerle sırayla alınırsa iki okumada yük durumu
   (dokunmatik, seri haberleşme, ses) **aynı** tutulur ve ölçer her seferinde yalnız tek noktada takılı olur. Sonuç sınırın 0,05 V yakınındaysa
   ölçüm ölçersiz noktadan multimetreyle (uzatmanın dişi ucunda açık bir USB test kartı) tekrarlanır (0,05 V: varsayım).

## Kayıt tablosu

Ölçer düzeni: ☐ tek ölçer, sırayla  ☐ iki ölçer aynı anda

Tablo 1: Pi portu ve hub girişi

| Durum | U1 Pi portu (V) | U1 (A) | U2 hub girişi (V) | U2 (A) | Düşüm U1 − U2 (V) |
|---|---|---|---|---|---|
| L0 | | | | | |
| L1 | | | | | |
| L2 | | | | | |
| L3 | | | | | |

Tablo 2: hub çıkışları ve cihazlar

| Durum | U3 Hub 1 dokunmatik (V / A) | U4 Hub 2 ESP32 (V / A) | Dokunmatik çalışıyor | ESP32 görünüyor / reset yok |
|---|---|---|---|---|
| L1 | / | / | ☐ | ☐ / ☐ |
| L2 | / | / | ☐ | ☐ / ☐ |
| L3 | / | / | ☐ | ☐ / ☐ |

Pi USB toplamı (L2):

| Port | Cihaz | Akım (A) |
|---|---|---|
| Pi 1 | ReSpeaker | |
| Pi 2 | USB ses kartı | |
| Pi 3 | Hub | |
| Pi 4 | Kafa ekranı Touch | |
| **Toplam** | | |

## Geçer / kalır sınırı

| Ölçüt | GEÇER | Kaynak |
|---|---|---|
| U3 ve U4 (hub çıkışı, cihaz ucu), L1 ve L2'de en düşük | **≥ 4,40 V** | USB 2.0 belirtimi, Tablo 7-7: hub'dan beslenen (düşük güçlü) port alt sınırı (dış kaynak) |
| U2 hub girişi, L1 ve L2'de en düşük | **≥ 4,75 V** | **Varsayım:** USB 2.0'da Pi gibi yüksek güçlü portun alt sınırı (Tablo 7-7); hub'ın kendi düşümüne pay kalsın diye girişte de bu hedeflendi |
| Pi USB toplamı (L2) | **≤ 1,6 A** | `07-gogus.md:47` |
| Dokunmatik ve ESP32, L1 ve L2 | Hepsi ☐ işaretli (kopma, reset yok) | `elektrik.md:231` (ESP32 resetlenmemeli) |

L3 yalnız kayıttır; altıncı cihaz belli olunca (`karar-kuyrugu.md` K1) yeniden değerlendirilir.

## Sınır aşılırsa

- Hub girişi ya da çıkışı düşükse: sonuç `uygulama-notu.md:100` ve `elektrik.md` USB bölümüne (`elektrik.md:58`, P4.1) işlenir. Kablo
  türü/kesiti ve uzatmanın listeye girişi `karar-kuyrugu.md` **K4**; hub yeri **K1/K5** ile bağlantılı. Karar **Ahmet Yorulmaz**'da.
- Pi USB toplamı 1,6 A'i geçerse: `usb_max_current_enable=1` ayarını kontrol et (`elektrik.md:248`), [T3](T3-kafa-5v-akim.md) ile birlikte
  tasarım ajanına ver.
- ESP32 resetleniyorsa: yazılım ekibine (Efe) DTR/RTS notu (`elektrik.md:228-231`) ile birlikte bildir.

## Sonuç

☐ GEÇER  ☐ KALIR    Hub girişi en düşük: ______ V   Hub çıkışı en düşük: ______ V   Pi USB toplamı: ______ A

Ölçen imza: ____________  Kontrol eden imza: ____________

Kaynak dosyalar için kısaltma tablosu: [00-genel.md](00-genel.md).
