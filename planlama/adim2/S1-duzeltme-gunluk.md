# S1 kaseti düzeltmeleri K1–K6 (plan Y1b) — tasarım ajanı günlüğü

Girdi: `K2-s1-kontrol.md` (KOŞULLU GEÇTİ, B1–B11, K1–K6). Dal `lale-duzeltme`, başlangıç HEAD `102f246`, çalışma ağacı temiz.
Kapsam: S1 kaseti + bağlı parçalar (omuz/kabuk modülleri, ilgili kontrol betikleri, `eklem_sinirlari.json`, `S1-kaset.md`,
`M6-montaj-sirasi.md`). Commit yok. Ajan kesilirse buradan devam.

## Durum
- [x] 0. Okuma (CLAUDE.md, dongu.md, K2-s1-kontrol.md, S1-kaset.md, freecad README/OZET, arayuz OMUZ/13/KOL_KABLO, kabuk/omuz parçaları, M6)
- [x] 1. arayuz: K1 kablo notu, K4 u_pay 6,5, K2 bağlama ipi yolu, K3 pah + S1/S2 bağımlı sınır, ikinci pim, S2 birleşim göbekte
- [x] 2. omuz_parcalar: tambur kayış yarıkları → bağlama ipi yolu (+ ip modeli, kontrol)
- [x] 3. kabuk_parcalar: flanş pahı, duvar bağı ip delikleri, ikinci pim kulağı
- [x] 4. eklem_sinirlari.json (üretici) + K6 kontrol betikleri (carpisma statik, taslak_montaj, taslak_analiz statik)
- [x] 5. Yeniden üretim: omuz_montaj, omuz_baski, kabuk_montaj, dirsek_montaj (omuz+kabuk kullanır), taslak_montaj
- [x] 6. Kısa yerleşim kontrolü (K2/K3 boşlukları, cep, pim, delikler)
- [x] 7. Belgeler: S1-kaset.md (K1, K4, K5, uzatma boyu), M6-montaj-sirasi.md (K5)

## Günlük
- 2026-10-25: dosya açıldı, okuma bitti.
- Tasarım kararları (gerekçe):
  - **K2 kelepçe yerine bağlama ipi:** tambur kanalı dudak arası 4,8, demet 4,2 (her yanda 0,3); +x dudak ↔ flanş yalnız 0,5 radyal
    (aynı eksenel bantta, x 158,3–159,3), −x dudak arkasında kabuk (x ≤ 152) / arka plaka. Kelepçenin sırt plakası demetin üstüne
    (r 43,2 → ≥ 44,5) çıkınca flanşa, kanat/vida yeri için dudak dışına çıkınca kabuğa ya da flanşa giriyor; halkaya radyal M2 için
    et yok (2 mm halka, altında kapak cıvatası 0,7). → Ø0,4 mumlu polyester ip: halka iç yüzünde 0,5 oluk + iki dudak iç yüzünde 0,3
    cep + halkadan radyal kanal; ilmek halka zarfının içinde (r ≥ 37,1). Eski 3 × 1,6 kayış yarıkları kaldırıldı. İp ilmekleri omuzda
    parça olarak modellendi ("S1 tambur baglama ipi", Gobek, 2 adet) → omuz_montaj ve kontrol betiği ölçüyor.
  - **K4 duvar bağı da ip:** kayışlı bağ (1,0 kalınlık) demetin yanlarından geçemez (arka plaka 0,8, flanş 0,3 eksenel). İp
    arka plaka dibinde 0,8 × 1,2 radyal yarıktan ve duvar üst kenarında 0,8 × 1,2 çentikten geçer; ψ 226,5 ve 230.
  - **İkinci pim** U'nun süpürdüğü halkaya (r < 75,2, ψ ≤ U ucu) konamaz → duvar dışı kulak ψ 300, r 80 (govde dikme + köprü
    r 76,2…; kapak flanş uzantısı + Ø3 pim). Görünüm uç değerleri değişmez (ψ 300'de y 40 < tepe 67,5; z 69 < ön 77,2).
  - **K3 sınırı** `arayuz.KOL_KABLO["s1"]["s2_s1_kosul"]` → `eklem_sinirlari()` → JSON `bagimli` listesi (r/l); üretici kontrolü genişletildi.
  - **S2 servo kablosu** göbekte (G2'den ~20 mm önce) uzatmaya eklenir (`s2_birlesim`); U'dan 3 aynı PVC şerit. `dirsek_montaj` S2 boy
    hesabı hâlâ "servo kablosu yarığa kadar" modelinde (dirsek modülü kapsam dışı; Y2'de) → uzatma boyları aşağıda elle.
  - **K6:** `carpisma.py` statik (+ `carpisma_kos` birleştirme), `taslak_montaj.py` ev pozu, `taslak_analiz.py` statik → S2 5'te kontrol,
    S2 0 bilgi listesi. FCStd eklem sıfırı değişmedi.
- Koşular: omuz_montaj 90 s: 75 parça (73 + 2 ip), statik (S2 5) 0, S2 0 bilgi 2 (tambur ↔ çatal 97,87 / tüp 65,01, önceki gibi),
  aralık içi serbest olmayan poz 0, göbek × gövde 0. İp ↔ kapak cıvatası **0,809** (φ 80), ↔ rulman kapağı **1,20** (S1 −60…180 / 2°);
  ip ↔ tambur ortak 0.
- (durum notu, koordinatör mesajı sonrası) Bitti: arayuz, omuz_parcalar, kabuk_parcalar, eklem_sinirlari (+üretici), K6 betikleri,
  M6 (K5 + ip + S2 bağlantısı), S1-kaset.md eski kısımlar işaretlendi. Koşular: omuz_montaj, omuz_baski (tambur +X destekli 769 mm²,
  değişmedi), kabuk_montaj (206 parça, tüm kontroller geçti, kaset baskı destek sorunu 0, kütle 4.922,3 g), dirsek_montaj
  (lace hariç tutuldu → kablo kontrolü OK), taslak_montaj bitti (sonuç aşağıda). Sürüyor: S1-duzeltme-kontrol.py, K2-montaj radyal (scratch kopya).
- Ölçümler (scratch kopyalar K2-ek / K2-ek2, kontrol ajanının JSON'larına yazılmadı):
  - **K3:** S2 lopu ↔ kapak flanşı (pahlı): S2 120 → **+0,39** çevrel / +0,43 dikdörtgen (S1 ≥ 125); S2 117 → **0,89** / 0,94;
    S2 120 @ S1 120 0,66, @ S1 115 1,60. Bağımlı sınırla izinli bölgede en az ≈ 0,66 (S1 < 120, S2 120).
  - **K4 cep:** U ucu ↔ cep, L 171,4: φ 135 0,34 (dış temas bölgesi), uç temas eşiği **L +2,7 mm** (L +2 0,33, +3 −0,13) ve
    **S1 +3,8°** (138 0,28, 139 −0,07). Önce L +0,7 / S1 +1. Kontrolün hedefi (L +3 / S1 +4) için u_pay ≈ 7,0 gerekirdi;
    brief 6,5 dediği için 6,5 bırakıldı (L toleransı −5…0 tek yönlü olduğundan pay 2,7 mm). Pim (ψ 331) φ 135'te 3,26.
  - dirsek_montaj S1: U R_min 12,91, en dar 0,93 (omuz bandı), geçiş 2,18, çıkış 0,30 (kapak), tambur ↔ kol 0,82, kaset ↔ kol 1,36
    (15° ızgara), tambur ↔ kaset 0,50.
- Sonuç ölçümleri (S1-duzeltme-kontrol.json, K2-montaj radyal scratch kopyası, carpisma statik, taslak_montaj):
  - İp ↔ kapak cıvatası 0,809, ↔ rulman kapağı 1,20, ↔ kaset kapağı 0,60 (S1 −60…180 / 1°); tambur ↔ sabit 0,50; pah r 44,25 (x 158,35) → 45,35 (159,45).
  - pim2 delik iç kenarı r 78,4 (duvar dış 77,2), kapakta pim var, gövdede delik boş; duvar ip delikleri 4/4 açık, yanlarında duvar dolu.
  - Kaset ↔ kol 1,358 (S1 15, S2 5; 5° ızgara), kaset ↔ göbek 3,5. Gövde ↔ kapak 0,378 mm³ (kulak x 158,31 bindirmesi, eşik altı; açık).
  - Radyal montaj: gövde x 0 dört pozda 0; kapak x +3,3 dört pozda 0; +3,6 S1 −45/−20'de göbek (önceki gibi).
  - carpisma statik (S1 0, S2 5): 0 çakışma, S2 0 bilgi 2; taslak_montaj ev pozu (S2 5): 0, S2 0 bilgi 4; taslak 1.064 parça, 24.511,3 g.
  - S1-kaset.md "Y1b düzeltmeleri" bölümü yazıldı (K1–K6 tablosu, montaj sırası, uzatma boyu: taslak ≈ 11,7 m, +%10 ≈ 12,9 m).
- Yeniden üretilmeyen (bilerek): ana montaj (`montaj/`), carpisma diğer bölümleri, görseller (GUI), rapor.html'ler, taslak_analiz (yalnız kod), M6_erisim/M6_ek → Y3/Y4.
