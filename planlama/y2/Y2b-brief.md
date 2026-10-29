# Y2b brief (yeniden başlatma için; 29 Ekim 2026)

Yeni oturumda bu ajan devam ettirilemezse: aynı brief ile **yeni Opus ajanı** başlat ve "önce `planlama/y2/Y2b-gunluk.md`'yi ve
`git status`'u oku, yapılanı tekrarlama" de.

## Resmi tanım (`planlama/dongu.md`, "1,70 m planı")
> Y2b | Veri/belge: eklem_sinirlari, maliyet.json, baskı listesi, elektrik/akü, README, proje planı, demodan lidar/otonomi

Y2a brief'indeki ek: maliyet.json — `taslak-170/maliyet-farki.md` + uzatma kablosu (1650'de yeniden hesapla) —, demodan lidar/otonomi
`c8c4de7`. Çelişkide dongu.md esas.

## Depo ve sınırlar
- `C:\Users\Victus\OneDrive\Masaüstü\Robot`, dal `lale-duzeltme` (başlangıç `2b07779`). **Push yok**, tek yerel commit (Türkçe mesaj,
  boş satır + `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`).
- `tasarim/solidworks/` izlenmiyor: dokunma, commit'e ekleme. `main` / `yazilim-baslangic` dallarına dokunma (Efe'nin yazılımı).
  Köprü notu (`planlama/kopru-mekanik-yazilim.md`, main) bu adımda **değişmez**; Efe'yi ilgilendirenler raporda listelenir.
- Her dosyayı değiştirmeden önce oku. Kapsam dışı sorunlar raporda listelenir, dokunulmaz.
- Ölçüler: `tasarim/freecad/arayuz.py` tek doğruluk kaynağı; `kod/ortak/eklem_sinirlari.json` betikle üretilir (elle düzenleme yok).

## Bilinen durum (Y2a + 29.10 kararları)
1650 mm boy, direk 1.185,5, 1.073 parça, 24.396 g, AM (−0,20; 527,43; −12,38); kol başına 4 servo + kafa pan/tilt (10 servo, omuz
DS3235); göğüste Nextion yok; akü yerinde (şart: rampada kollar ev pozunda, doğrusal ivme ≤ 0,1 m/s²); kafa tilt ±13°; kafa kabuğu sağ
ön/arka destekli baskı; el yükü ~100 g (KZ2 açık). Mikrofon Efe tarafından ReSpeaker Lite → XVF3800 dizi + yönlü mikrofon (main'de
`git show origin/main:<yol>`).

## İşler
1. Maliyet (`maliyet.json` + türevleri): 1650 tasarım + XVF3800 + yönlü mik + DS3235 omuzlar; Nextion çıkar; toplam yeniden.
2. Baskı listesi (`planlama/baski-listesi.md`): 1650 ana montajdan yeniden; kafa kabuğu sağ ön/arka "destekli baskı (16 mm şerit,
   ~1,25 mm konsol)".
3. Elektrik/akü belgeleri: akü yerinde; güç/röle (E3/E9, K1 GPIO12, K2 GPIO2, PC817) tutarlı.
4. İvme: rampada ≤ 0,1 m/s² (karar). Düz zeminde pay ≥ 1,5 tutan sınırı AM / iz (432, ±216) ve kontrol yöntemiyle hesapla; teker
   notundaki "≤ 0,25" ve "≤ 0,5" ifadelerini tutarlı yap (arayuz.py'de düzelt, JSON'u betikle üret). Hesap günlükte.
5. README + proje planı 1,65 m'ye; demodan lidar/otonomi (hoca kararı 21.10: otonomi iptal, ROS 2 yok).
6. Y2a belge düzeltmeleri: günlük başlığı 1,70 → 1,65; sehim 0,336 / 0,371 (kaynaktan doğrusunu belirle).
7. `kabuk_rapor.py` (Nextion arıyor, bozuk): Y2b kapsamındaysa düzelt, değilse hangi adım.
8. Bitince: `dongu.md` Y2b satırı, tek commit, rapor (≤ 15 satır: hash, yapılanlar, düz zemin ivme sonucu, yapılamayanlar, köprü
   notuna eklenecekler, bağımsız kontrol için 3–5 kritik iddia).

İlerleme: `planlama/y2/Y2b-gunluk.md` (adım adım).
