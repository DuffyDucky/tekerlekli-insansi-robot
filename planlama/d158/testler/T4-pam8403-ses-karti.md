# T4 · PAM8403 + USB ses kartı: besleme noktası ve akım

Kâğıt T4 / 9 · Lale 1,58 m · sürüm 08.11.2026

| Tarih | Ölçen | Yazan | Kontrol eden | Alet markası/modeli |
|---|---|---|---|---|
| | | | | |

## Amaç

Robotun sesi şu yoldan çıkıyor: Pi → USB ses kartı → 3,5 mm kablo → PAM8403 yükselteç → göğüsteki hoparlör (Ø40, 4 Ω, 3 W).
Bu kâğıt PAM8403'ün 5 V'u **nereden** aldığını kaydeder, en yüksek seste PAM'in ve ses kartının çektiği akımı ve beslendiği hattın
gerilimini ölçer.

## Neden önemli

PAM'in besleme noktası karara bağlanmadı (`karar-kuyrugu.md` K10, satır 165). Modelde D24V50F5'ten (Pi hattı) beslendiği
**varsayım** olarak çizildi (`uygulama-notu.md:113`). PAM en yüksek seste Pi hattına ~0,71 A ekler; Pi hattı tepede 5 A'nın %66–68'ine
çıkar (hesap, `uygulama-notu.md:98`). Akımlar ölçülmedi (`elektrik.md:21`).

### Doğruladığı varsayım

| Değer | Kaynak | Durum |
|---|---|---|
| PAM8403 5 V'u D24V50F5'ten (Pi hattı) | `uygulama-notu.md:97`, `uygulama-notu.md:113`, `karar-kuyrugu.md:25` | **Varsayım**; karar K10 açık, varsayılan a |
| PAM tepe akımı 0,71 A (3 W hoparlör, verim %85) | `uygulama-notu.md:98` | Hesap; verim %85 varsayım |
| Pi hattı PAM ile tepede 3,28–3,38 A (%66–68) | `uygulama-notu.md:98`, `karar-kuyrugu.md:25` | Hesap |
| Hoparlör Ø40 × 20, 4 Ω, 3 W | `secenekler.md:262` | Satıcı sayfası |
| Ses kartı Pi'nin 2 numaralı USB portunda (uzatma + L dirsek) | `uygulama-notu.md:126` | Model |
| USB ses kartı akımı | yok | **Kaynakta değer yok**; USB 2.0 tek cihaz sınırı 0,5 A (dış kaynak) |
| D24V50F5 çıkışı 5 V ±%4, 5 A sürekli | `elektrik.md:16` | Satıcı sayfası |

## Gereken alet

- T3 düzeneği (ölçüm köprüleri, pens ya da multimetre, laboratuvar kaynağı ya da akü + F3 5 A)
- PAM8403'ün 5 V girişine seri ölçüm köprüsü (klemens) ya da pens. PAM akımı küçük (< 1 A beklenir), 30 s'lik ölçümde seri multimetre olur.
  **Pi hattının toplamı (N2) ise pensle** ölçülür; adım 4 (A4 + S2) pens olmadan akımsız yapılır.
- USB gerilim/akım ölçer (Pi portu ile ses kartı uzatması arasına)
- Ses dosyaları: 1 kHz sinüs (30 s), konuşma kaydı (30 s). Pi'de `aplay` ya da `speaker-test -t sine -f 1000`
- Kulak koruyucu ya da kulak tıkacı

## Güvenlik

- **PAM8403'ün çıkışları köprü (BTL) tipidir** (üretici datasheet'i; depoda kaynak yok): hoparlörün hiçbir ucunu GND'ye bağlama,
  osiloskop probunun toprak klipsini hoparlör ucuna takma. Kısa devre PAM'i yakar.
- En yüksek seste hoparlöre yakın durma, kulak koruyucu tak; en yüksek seste deneme **en çok 30 s** (varsayım: hoparlörü ve kulağı korumak için).
- Akü ya da laboratuvar kaynağı: T3'teki uyarılar geçerli (ters bağlama, F3 5 A, sıcak düşürücüler).
- **Multimetreyle akım:** [00-genel.md](00-genel.md) "Multimetreyle akım ölçümü" kuralı. Kısaca: kırmızı uç 10 A soketine, yalnız seri,
  enerji kapalıyken bağla; iş bitince kırmızı uç V soketine geri; 10 A süre sınırına uy.
- **Saat, yüzük, bileklik çıkar.**
- Servo gücü bu testte gerekmez; anahtarlı bara kapalı.

## Yöntem

1. **Besleme noktasını kaydet:** PAM'in 5 V teli nereye bağlı? ☐ a) D24V50F5 (Pi hattı) ☐ b) SY8205 (ekran hattı) ☐ c) ayrı düşürücü
   (`karar-kuyrugu.md:25` seçenekleri). Kablonun boyunu yaz (modelde 80 mm, `uygulama-notu.md:113`).
2. Ölçüm noktaları: **P1** PAM 5 V girişi (gerilim + akım), **P2** beslendiği hattın düşürücü çıkışı (a ise T3'teki N2), **P3** USB ölçer:
   ses kartının akımı ve o porttaki gerilim. P1'de seri multimetre varsa PAM gerilimini multimetrenin **PAM tarafında** oku; P2 akımı pensle.
3. Ses seviyesini sistemde %50'ye al, PAM üstündeki ses ayarı (varsa) ortada. Her durumda 30 s çal, P1–P3'te **en yüksek akımı** ve
   **en düşük gerilimi** yaz:
   - **A1 sessiz:** program çalışıyor, ses yok.
   - **A2 konuşma, orta ses:** konuşma kaydı, sistem sesi %50.
   - **A3 konuşma, en yüksek ses:** sistem sesi %100.
   - **A4 1 kHz sinüs, en yüksek ses:** en kötü durum. 30 s'den uzun tutma.
4. A4'ü T3'teki **S2 stres** senaryosuyla birlikte bir kez daha yap (Pi tam yükte + en yüksek ses). Pi hattının toplam akımını (N2, **yalnız pensle**)
   ve `vcgencmd get_throttled` çıktısını yaz. Bu adımda Pi hattında seri multimetre bulunmaz (gerilimi düşürür, `get_throttled`'ı bozar).
5. **Uğultu:** önce, **anahtarlı bara kapalıyken** (servo ve motor gücü yok), ses yokken (A1) hoparlöre 10 cm'den kulak ver: uğultu ya da
   cızırtı var mı? Sonra **enerji yokken** bir telefonu (ses kaydı ya da ses seviyesi uygulaması) hoparlörün 10 cm önüne sabitle (bantla ya da
   sehpaya koy) ve kayda başlat; herkes kolların erişim alanının dışına çıkar. Ancak o zaman **anahtarlı barayı aç** (kol ve kafa servoları ile
   motor sürücüsü de güç alır; `elektrik.md:60`), hareket komutu verme. Uğultuyu yalnız alan dışından dinle ya da telefonun kaydından izle;
   **servo gücü açıkken kimse kolların erişim alanına girmez**, hoparlöre yaklaşmaz. Bitince anahtarlı barayı kapat, telefonu sonra al.
   Bu ölçüm değil, gözlemdir; sayısal karşılığı [T6](T6-akustik.md) B bölümündedir.
6. **İsteğe bağlı (K10 için veri):** besleme noktası b) ile de denenecekse PAM'i SY8205'e bağla ve 3–4. adımı tekrarla. QLED'de
   titreme ya da kararma olursa hemen durdur.

## Kayıt tablosu

Besleme noktası: ☐ a  ☐ b  ☐ c    PAM 5 V kablo boyu: ______ mm

Tablo 1: PAM ve beslendiği hat

| Durum | P1 PAM akımı en yüksek (A) | P1 PAM gerilimi en düşük (V) | P2 hat gerilimi en düşük (V) | P2 hat akımı en yüksek (A, pens) |
|---|---|---|---|---|
| A1 sessiz | | | | |
| A2 konuşma %50 | | | | |
| A3 konuşma %100 | | | | |
| A4 sinüs %100 | | | | |
| A4 + S2 stres | | | | |
| İsteğe bağlı b) A4 | | | | |

Tablo 2: ses kartı ve notlar

| Durum | P3 ses kartı akımı (A) | P3 port gerilimi (V) | Not (A4 + S2: get_throttled; b: QLED titredi mi) |
|---|---|---|---|
| A1 sessiz | | | |
| A2 konuşma %50 | | | |
| A3 konuşma %100 | | | |
| A4 sinüs %100 | | | |
| A4 + S2 stres | | | |
| İsteğe bağlı b) A4 | | | |

Uğultu gözlemi: servo kapalı ☐ yok ☐ var   servo açık ☐ yok ☐ var   Açıklama: ______________________

## Geçer / kalır sınırı

| Ölçüt | GEÇER | Kaynak |
|---|---|---|
| PAM akımı, A4'te en yüksek | **≤ 0,71 A** (hesabı doğrular) | `uygulama-notu.md:98` |
| Pi hattı (N2) toplamı, A4 + S2 stres | **< 5,0 A** | `elektrik.md:16` |
| Pi hattı (N2) gerilimi, A4 + S2 stres | **≥ 4,80 V** | `elektrik.md:16` (5 V ±%4) |
| Ses kartı akımı | **≤ 0,5 A** | USB 2.0 belirtimi (dış kaynak) |
| `get_throttled`, A4 + S2 stres | **0x0** | `oneri-taslak-v8.md:68` |
| İsteğe bağlı b): SY8205 toplamı / gerilimi | **< 3,7 A** / **4,75–5,25 V** | `elektrik.md:18`; USB 2.0 (dış kaynak) |

PAM akımı 0,71 A'i geçip diğer satırlar geçerse sonuç **KOŞULLU**: hesap (`uygulama-notu.md:98`) ölçülen değerle düzeltilir.

## Sınır aşılırsa

- Sonuç `karar-kuyrugu.md` **K10**'a veri olarak eklenir; besleme noktası kararı **Ahmet Yorulmaz**'ın. Ölçülen akım `elektrik.md:21`
  satırına ("Besleme noktası ve akımı doğrulanmadı") işlenir.
- Pi hattı sınırı aşılırsa [T3](T3-kafa-5v-akim.md) "Sınır aşılırsa" bölümü geçerlidir.
- Uğultu varsa: toprak yolu ve kablo ayrımı (dizi USB'si güç kablolarından ayrı, `oneri-taslak-v8.md:199`) tasarım ajanına; T6 B
  ölçümüyle birlikte değerlendirilir.

## Sonuç

☐ GEÇER  ☐ KOŞULLU  ☐ KALIR    PAM en yüksek: ______ A   Pi hattı en yüksek: ______ A

Ölçen imza: ____________  Kontrol eden imza: ____________

Kaynak dosyalar için kısaltma tablosu: [00-genel.md](00-genel.md).
