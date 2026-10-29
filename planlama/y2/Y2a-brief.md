# Y2a brief (yeniden başlatma için; 29 Ekim 2026)

Yeni oturumda bu ajan SendMessage ile devam ettirilemezse: aynı brief ile **yeni Opus ajanı** (general-purpose, `model: opus`)
başlat ve "önce `planlama/y2/Y2a-gunluk.md`'yi ve `git status`'u oku, yapılanı tekrarlama" de.

## Görev (Duffy 25.10 "ana projeye 170den devam", 29.10 "165 olsun")
1,65 m tasarımı ana tasarıma taşı: `tasarim/freecad/taslak-170/` varyantındaki değişiklikler (uzun direk + gövde uzatma bantları,
10" kafa `kafa10.py`, kol ×1,25 ek uzama ön kolda, omuz DS3235, dirsek çatalı dış kol 8 mm + M3x12 + 2× DIN125 pul + 45° destek,
taban genişliği) modüllere, `arayuz.py`'ye ve `montaj/`'a işlenir; taslak klasörü arşiv olur.
- **Boy 1650 mm** (yerden kafa tepesine): gövde uzatması **385 mm**, direk **1.185,5 mm** tek parça, 2 m stoktan. Boy/uzatma
  `arayuz.py`'de tek parametre; bant bölünmesi tablaya (25×25×25) göre yeniden.
- Göğüs Nextion kaldırılır (ekran, tutucu, kablo, kabuk açıklığı).
- Taban 520 mm (taslaktaki `TASLAK_TABAN_W=520` davranışı) + akü 75 mm öne.
- S1 kaseti: KZ1 `duvar.pim.bosluk` 0,5 → 1,0 (u_pay 6,5; U ucu eşiği ≥ L +3 mm / S1 +4° yeniden ölçülür), KZ2 tambur ip deliği
  eksenel ≥ 0,8 mm, `planlama/adim2/S1-kaset.md` belge düzeltmeleri (`adim2/K3-s1-duzeltme-kontrol.md` listesi).
- Sıra: arayuz → iskelet → kabuk → omuz → dirsek → kafa → taban → ana montaj; her modülden sonra kendi kontrolleri.
- Bağlantı elemanları modellenir; ana montaj FCStd/STEP/parça listesi/kütle-AM; kısa yerleşim kontrolü (ev pozu S2 5°).
- Dokunma: `tasarim/cad/`, `planlama/maliyet.json`, README dışı belgeler (Y2b). Commit/push yok (orkestratör commit'ler, push yok).
- FreeCAD: `%LOCALAPPDATA%\Programs\FreeCAD 1.1\bin\freecadcmd.exe`, başlatıcı `C:\Users\Victus\.robot-cad\run_fc.py`
  (FC_SCRIPT, ASCII yol), GUI'yi `App.closeDocument` + pencere kapatarak bitir, `PYTHONIOENCODING=utf-8`.
- Rapor: modül modül değişiklik, ana montaj sayıları + taslakla fark (50 mm boy farkı ayrı), Nextion/taban/akü yerleşimi,
  KZ1/KZ2 ölçümleri, değişen dosyalar, kontrol ajanına kalanlar.

Sonra: Y2a kontrol (ayrı Opus ajanı: tam tarama, devrilme/motor/servo 1650 ile) → Y2b (eklem_sinirlari, maliyet.json —
`taslak-170/maliyet-farki.md` + uzatma kablosu ~12,9 m (1650'de yeniden hesapla) —, baskı listesi, elektrik/akü, README,
proje planı, demodan lidar/otonomi `c8c4de7`) → Y3–Y6 (`planlama/dongu.md`).
