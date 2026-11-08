# F5b bağımsız kontrol (ajan B) — 08.11.2026

Kontrol edilen: `planlama/d158/F5b-pano-taslak.md` (mesaj), `F5b-gunluk.md`. Brief: `F5b-brief.md` (sınır orkestratör kararıyla 2.200, 6. soru orkestratörün).
Yöntem: kod iddiaları `git show main:<yol>` ile (main = 84bc2b4), plan iddiaları çalışma dalında (`lale-duzeltme` = 7e78b45; bu üç plan dosyası HEAD ile aynı).
Yazılan tek dosya bu. Panoya gönderilmedi, commit/push yok, CAD koşulmadı.

## Sonuç: KOŞULLU

Koddaki satır iddialarının hepsi doğru, Efe'ye yanlış kod bilgisi gitmiyor. Tek bir esas düzeltme var: 6. soru main'deki 0,5 m/s² rampayı
görmüyor (D1). Kalanlar kaynak hassasiyeti ve üslup. Düzeltmelerden sonra yeniden kontrol gerekmez; yalnız karakter sayısı yeniden sayılmalı.

## 1. Kod iddiaları (main)

| İddia (mesaj) | Kaynak | Sonuç |
|---|---|---|
| Yarım dupleks: robot konuşurken mikrofon kapalı | `mikrofon.py:5` (yorum), `:144` (`finally: self.kapat()`), `durum.py:10-12` | Doğru |
| Akış açılınca ilk 300 ms atlanıyor | `mikrofon.py:20` `ATLA_PARCA = 10` (10 × 30 ms) | Doğru |
| Telefondan söyletmede 0,5 s susma | `kopru.py:28` `KONUSMA_SONRASI_SUSMA = 0.5`, kullanımı `:115` | Doğru |
| Acil stop ESP32'ye bağlı değil | `pinler.h:49` | Doğru |
| Komutlar sur, dur, jest, servo, ping, odo_sifirla | `seri_protokol.cpp:150-155` (`:156` bilinmeyen_komut) | Doğru; röle/GPIO12 kodda yok (pinler.h'de 12 yalnız strapping notu, `:6`) |
| Köprü 0,4 s sonra "dur" | `kopru.py:10, 25` (`OLU_ADAM_SANIYE = 0.4`), `:175-179`; döngü 50 ms `:277` | Doğru (en kötü ≈ 0,45 s + seri) |
| ESP32 500 ms sonra durdurur | `watchdog.cpp:11, 44-46`; `main.cpp:74` her loop'ta denetler (delay yok, `:23`) | Doğru |
| Ölü adam yalnız testte denenmiş (günlük) | `tests/test_uzaktan.py:155` (sahte saat), `:168` (sunucu, sahte robot) | Doğru; robotta ölçüm kaydı yok |
| Bluetooth gamepad main'de yok | `git grep -i "gamepad\|bluepad" main -- kod`: 0 (yalnız `konum/ble.py`, beacon) | Doğru |
| Telefondaki DUR gücü kesmiyor | `sayfa.html:229` düğme, `:307-315` `acilDur()` yalnız `/dur` | Doğru |
| DevKit port açılınca DTR/RTS ile resetlenir; seri.py kapatmıyor | `esp32/OKU_BENI.md:159`; `seri.py:77` düz `serial.Serial(port, hiz, timeout=0.1)` | Doğru |
| Reset komutu yok | `seri_protokol.cpp:150-156` | Doğru |
| dur: PWM 0 = BTS7960 fren, EN HIGH | `motorlar.cpp:122-123` | Doğru |
| "dur" ve bekçi anında durdurur, rampa yok | `motorlar.h:20`; `seri_protokol.cpp:98-99` `komut_dur()` → `motorlar_dur()`; `watchdog.cpp:45`; `motorlar_dur()` `teker_sifirla` ile `rampa_hiz = 0` (`motorlar.cpp:145-148, 226-230`) | Doğru, **ama eksik** (bkz. D1) |

**Eksik bağlam (D1):** main'de yavaşlama sınırı VAR, yalnız "sur" yolunda: `motorlar.cpp:19` `HIZLANMA = 0.5f` (m/s²), `:158-160`
`rampa_hiz += kirp(hedef - rampa, HIZLANMA*DT)` simetrik, yani hızlanmayı da yavaşlamayı da 0,5 m/s²'de tutar (`motorlar.h:4, 17-18`).
Rampasız olan yalnız `dur` ve bekçi. Telefonda yön düğmesi bırakılınca da `/dur` gidiyor (`sayfa.html:3, 304`), yani olağan duruş bile rampasız.
Mesajın "yazılımda yavaşlama sınırı planlanıyor mu?" sorusu ve günlükteki "yavaşlama sınırı main kodunda bulunamadı" (tablo satırı 6) bu yüzden yanlış
izlenim veriyor. Ayrıca plan rampayı zaten yazıyor: `yazilim-plani.md:75` (Y1, "ivme rampası düzde ≤ 0,5, rampada ≤ 0,1"). Açık olan soru,
0,1'in rampada nasıl uygulanacağı (eğim algısı) ve dur/bekçi duruşunu kapsayıp kapsamayacağı.

**Ses çıkışı (D4):** mesaj "ses ayrı USB ses kartından çıkıyor" diyor; bu plan donanımı (`elektrik.md:21, 58`). main'de ses HDMI'ya ayarlı
(`kod/ayarlar.yaml:36` `ses_cihazi: "plughw:CARD=vc4hdmi0,DEV=0"`). Soru geçerli, ama şimdiki durum gibi değil plan olarak yazılmalı.

## 2. Plan / CAD iddiaları

| İddia | Kaynak | Sonuç |
|---|---|---|
| Mic Array v2.0 | `elektrik.md:20` | Doğru |
| Ayrı USB ses kartı | `elektrik.md:58` doğru; `:20` mikrofon satırı, ses kartı `:21` (amfi satırı) | Atıf `20, 58` → `21, 58` olmalı (D5) |
| K1 / GPIO12, devreye al, bırakma | `elektrik.md:216-226` | Doğru. Planda bırakma komutla değil: mantar (PC817 #1, `:223`) ya da reset (`:226`) |
| Reset → röle bırakır, kollar düşer; DTR/RTS kapalı açılış | `elektrik.md:228-229` | Doğru; mesaj yalnız `:228` diyor, sonucu (kollar düşer, `:229`) yazmıyor (D7, isteğe bağlı) |
| Fren kararları | `kararlar-2026-10-29.md:35` (düz fren ≤ 1,8), `:77-78` (rampada ≤ 0,1, düzde 1,8 / 0,5), gerekçe `:79` (1,31 < 1,5) | Değerler doğru. Mesaj bunu "CAD devrilme hesabı … istiyor" diye yazıyor; bunlar karar, hesap gerekçe (`:79`) (D6) |
| Eski ses donanımı (günlük bulgu 1) | `yazilim-plani.md:23` ReSpeaker Lite → MAX98357A | Doğru, bulgu yerinde |
| 500 ms Pi'den mesaj yoksa dur | `yazilim-plani.md:35` | Doğru |
| "arm" var, bırakma yok | `yazilim-plani.md:46-48` (`:47` "estop", "reset" olayları; Pi→ESP yalnız arm) | Doğru |
| Rampa ≤ 0,1 | `yazilim-plani.md:75` | Doğru (mesaj bunu kullanmıyor, bkz. D1) |
| Gamepad planı | `yazilim-plani.md:36, 78` | Doğru |
| Mantar etek plakasında | `arayuz.py:436` yalnız **commit edilmemiş** çalışma kopyasında; HEAD'de `:435`, main'de `:334` | Satır numarası kaymış/kayacak (D3) |

**Dal sorunu (D2):** `kararlar-2026-10-29.md`, `adim3/elektrik.md`, `yazilim-plani.md` ve `d158/testler/` main'de YOK, yalnız çalışma dalında
(origin'de de var). Mesaj "Kodu main'den okuduk" diyor; plan atıfları için hangi dalda bakacağı yazmıyor. Efe main'de arayınca bulamaz.

**D3 sınırı (D8, isteğe bağlı):** T13 D3 tekerlerin ≤ 0,5 s içinde *durmasını* istiyor (`T13-rampada-acil-stop.md:116`). Kodda yalnız komut tarafı
≈ 0,45–0,5 s; mekanik duruş üstüne eklenir, pay sıfıra yakın. Mesajın "gerçek robotta ölçüldü mü?" sorusu bunu kapsıyor; istenirse bir
kelimeyle belirtilebilir.

## 3. Mesaj biçimi

- **Karakter:** iki `---` arası, iç satır sonları dahil **1.994** (benim sayımım, Python `len`; uç satır sonlarıyla 1.996). ≤ 2.200: GEÇER. Pay 206.
- **Karar yok:** açılış "Bilgi ve soru; karar yok" diyor; 1-3, 5, 6 soru biçiminde. GEÇER.
- **4. soru:** "önerin ya da tercihin ne?" — "tercih" donanım seçimini Efe'ye bırakıyor gibi okunabilir. Brief donanım kararını Efe'ye
  değil ekibe bırakıyor ("yalnız soru"); yalnız görüş sorulmalı (D9).
- **Kişi adı / takma ad:** büyük harfli kelime taraması: yalnız "Efe" kişi adı; geri kalanı ürün/terim (ReSpeaker, Mic Array, DevKit, Bluetooth, Pi).
  Takma ad yok. GEÇER. (D2 düzeltmesinde dal adı yazılacaksa dal adındaki robot adı yerine "çalışma dalı" demek daha güvenli.)
- **Ton:** saygılı, kısa, "Doğru anlıyor muyuz" biçimi tutarlı. GEÇER.

## Düzeltme listesi

1. **(Esas) 6. soru:** "rampa yok" ifadesini yalnız `dur`/bekçiye bağla ve var olanı yaz. Öneri metni:
   "6) Fren: sur yolunda 0,5 m/s² rampa var (motorlar.cpp:19), ama dur ve bekçi rampasız duruyor (motorlar.h:20); telefonda düğmeyi bırakmak da dur gönderiyor (sayfa.html:304). Doğru anlıyor muyuz? Kararlar rampada yavaşlama ve freni ≤ 0,1, düzde freni ≤ 1,8 m/s² istiyor (kararlar-2026-10-29.md:77-78); plan Y1'de rampa var (yazilim-plani.md:75). Rampada 0,1 ve dur/bekçi duruşu yazılımda nasıl düşünülüyor?"
   Günlük tablo satırı 6'daki "Yavaşlama sınırı main kodunda bulunamadı" da buna göre düzeltilmeli.
2. **Dal:** açılış cümlesine plan belgelerinin yerini ekle, ör. "Kodu main'den, plan belgelerini çalışma dalından okuduk." (main'de `planlama/` belgeleri yok.)
3. **arayuz.py:436** satır numarasını kaldır ya da sembolle ver: "arayuz.py, ACIL_STOP" (çalışma kopyası 436, HEAD 435, main 334).
4. **1. soru:** "ses ayrı USB ses kartından çıkıyor" → "planda ses ayrı USB ses kartından çıkacak" (main'de HDMI, `ayarlar.yaml:36`).
5. **1. soru atfı:** `elektrik.md:20, 58` → `elektrik.md:20-21, 58` (ses kartı `:21`'de).
6. **6. soru:** "CAD devrilme hesabı … istiyor" → "kararlar … istiyor" (1. maddedeki metin bunu zaten yapıyor).
7. (İsteğe bağlı) **5. soru:** reset yolunun sonucunu ekle: "reset rölenin bırakması demek, kollar düşer (elektrik.md:229)".
8. (İsteğe bağlı) **3. soru:** "en kötü ~0,5 s" sonrasına "(D3 sınırı tekerin durması için 0,5 s)" eklenebilir.
9. **4. soru:** "önerin ya da tercihin ne?" → "önerin ya da görüşün var mı? (donanım kararını ayrıca vereceğiz)". Kişi adı eklemeden.
10. Düzeltmelerden sonra karakteri yeniden say (≤ 2.200; şu an pay 206, 1. maddedeki metin 404 karakter = +123, 2-4-9 ~+80 tutar: sığmazsa 7 ve 8'i bırak, 1. soruda parantez atıflarını kısalt).

## Yeniden kontrol 1 (08.11.2026, düzeltme turu 1 sonrası)

Okunan: `F5b-pano-taslak.md` (yeni sürüm), `F5b-gunluk.md` "Düzeltme turu 1". Yeni atıflar `git show main:` ile açıldı.

| Madde | Kontrol | Sonuç |
|---|---|---|
| 1 (6. soru) | Mesajın 13. satırı benim metnimle karakter karakter aynı (Python `in` karşılaştırması: True, 404 karakter). Günlük tablo satırı 6 düzeltilmiş (`HIZLANMA`, simetrik rampa, `sayfa.html:304`) | Uygulandı |
| 2 (dal) | Açılış: "Kodu main'den, plan belgelerini lale-duzeltme dalından okuduk." Dal adındaki "Lale" robotun adı (`main:kod/ayarlar.yaml:8` `ad: "Lale"`), kişi adı ya da takma ad değil; orkestratör kararı | Uygulandı |
| 3 (arayuz.py) | "(arayuz.py, ACIL_STOP)", satır numarası yok | Uygulandı |
| 4 (ses HDMI) | "planda … çıkacak", "main'de ses HDMI'da (ayarlar.yaml:36)"; `main:kod/ayarlar.yaml:36` `vc4hdmi0` | Uygulandı, atıf doğru |
| 5 (atıf) | "elektrik.md:20-21, 58" | Uygulandı |
| 6 ("kararlar") | 1. maddeyle | Uygulandı |
| 7, 8 (isteğe bağlı) | Sınır yüzünden yapılmadı (günlük: eklenince 2.342) | Kabul; isteğe bağlıydı |
| 9 (4. soru) | "önerin ya da görüşün var mı?" — "tercih" kalktı, yalnız görüş soruyor, karar bırakmıyor | Uygulandı |
| 10 (karakter) | İki `---` arası, iç satır sonları dahil **2.192** (benim sayımım; iddia ile aynı). ≤ 2.200 | GEÇER (pay 8) |

Yeni atıflar (main): `motorlar.cpp:19` `HIZLANMA = 0.5f` doğru; `motorlar.h:20` doğru; `sayfa.html:304` `if (surduyMu) istek("/dur", {})` doğru;
`ayarlar.yaml:36` doğru. Plan atıfları (`kararlar-2026-10-29.md:77-78`, `yazilim-plani.md:75`) ilk kontrolde doğrulandı, değişmedi.

2. soru kısaltması: "komuttan baranın düşmesine gecikme" → "gecikmesi". Özne "röle K1'i bırakan komut", ölçümün ne olduğu (T13 D2: bara düşüş anı)
parantezdeki "T13 D1-D2" atfıyla korunuyor. Anlam bozulmamış; yalnız ölçümün uç noktası artık mesajda açık değil, kabul edilebilir.

Kişi adı taraması: yalnız "Efe". Karar yok. Ton değişmedi.

Not: pay 8 karakter; gönderimden önce metne eklenecek her şey (ör. imza) sınırı aşar.

### Son karar: GEÇER
