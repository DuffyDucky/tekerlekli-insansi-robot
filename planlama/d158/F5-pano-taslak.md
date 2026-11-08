# F5 pano mesajı taslağı (P5.3) — GÖNDERİLMEDİ

Alıcı: Efe. Tür: bilgi + soru, karar yok. Mesaj metni aşağıdaki çizgiler arasında.

---
Efe merhaba, yazılım hizası için iki not hazırladık; kodda hiçbir şeye dokunmadık, karar senin.

1) 10 servo (planlama/d158/servo-10-oneri.md): main'de 6 servo var, tasarım 10. Öneri: 0–5 aynen, kanal 6–9 sag_omuz_yana, sag_bilek, sol_omuz_yana, sol_bilek; sınırlar eklem_sinirlari.json'dan (bu dosya main'de yok). Kodla CAD arasında 11 fark çıktı, önemlileri:
- Omuz DS3218 yazıyor, CAD DS3235.
- Omuz 0…160, CAD −45…135; selam ve işaret jestinde 150 var.
- Tilt 70…110 (±20), CAD ±13; evet jestindeki 75 sınır dışı.
- Dirsek 0…110, CAD 0…105.
- CAD montajında omuz horn'u servo 45°'deyken kol aşağıda, dirsek horn'u servo ortasında dirsek 52,5°'de takılıyor. Kodda sıfır kayması yok: bu montajla omuz 0 komutu kolu 45° geriye götürür (servo yönü varsayımıyla; sol kolda yön montajda doğrulanmalı).
- S2 en az 5°, S1 ≥ 120 iken S2 ≤ 117.

2) Boyun kabloları (planlama/d158/kablo-kurali-notu.md): "HDMI boyundan geçmez" kuralı CAD'de artık yok. Boyundan 12 V, tilt, göğüs HDMI (~950 mm, Pi HDMI1), hub uzatması ve hoparlör iniyor; ESP32 ve göğüs dokunmatiği gövdedeki hub'da. Yüz ekranı HDMI0'da (1280×720); ayarlar.yaml'da 1280×800 ve ses vc4hdmi0 yazıyor.

Sorular:
a) Servo sıfırı için üç yol var: kod birimi kaydırılsın mı (omuz CAD + 45, dirsek CAD + 37,5, bilek CAD + 90), kodda eklem başına sıfır kayması mı olsun, yoksa horn'lar kodun "servo ortası = 90" kuralına göre mi takılsın?
b) Kanal düzeni: 0–5 aynen kalsın mı, yoksa elektrik.md'deki bloklar mı (0–4 sağ kol + pan, 5–9 sol kol + tilt)?
c) Boyun düzenini kabul ediyor musun?
d) Yüz HDMI0, göğüs HDMI1 ataması yazılıma uygun mu?
e) ESP32 ve göğüs dokunmatiğinin hub arkasında olması sorun olur mu?
f) Masada ~1 m HDMI ile göğüs ekranını deneyebilir misin?
---

Karakter sayısı (iki çizgi arası, satır sonları dahil): F5-gunluk.md'de.
