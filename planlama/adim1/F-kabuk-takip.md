# Adım 1 / F: kabuk takip işleri (bindirme boşluğu, gövde braketi M6, TABAN açıklaması)

Başlangıç: 14 Ekim 2026. Durum: bitti (görev 1–3 uygulandı, kabuk yeniden üretildi, rapor + görseller yenilendi). Git commit yok, `carpisma_kos.py` koşulmadı.

## Görevler
1. `arayuz.KABUK_BINDIRME_BOSLUK` 0,2 → 0,25; kabuğu yeniden üret, M5 kontrolü + tüm kabuk kontrolleri, kütle/AM farkı.
2. Kabuk gövde braketi M6×16: vida ucu–somun üstü ≥ 0,5 ve uç–kanal tabanı ≥ 0,5; kalıcı kontrol `kabuk_montaj.py`.
3. `arayuz.TABAN['plaka_civata']` açıklaması (pulsuz, uç 11,0) güncelle.

## Günlük
- 15:45 `arayuz.py`: `KABUK_BINDIRME_BOSLUK` 0,2 → 0,25, `TABAN['plaka_civata']` açıklaması (pulsuz, uç 11,0; taban_parcalar.py: PLAKA_PUL=False, uç = y0p + 14 − 3 → rayın alt yüzünden 11,0; somun üstü 9,3, kanal tabanı 11,8). KABUK_GOVDE_BRAKET'e (görev dışı) dokunmadım.
- Braket M6 seçenekleri (uç = L − braket 3 − pul 1,6; şart 9,8…11,3): M6×16+pul = 11,4 (taban payı 0,4 ✗, mevcut); M6×18+pul 13,4 ✗; M6×14+pul 9,4 ✗ (somun payı 0,1); M6×16 pulsuz 13,0 ✗; M6×12 pulsuz 9,0 ✗; **M6×14 pulsuz 11,0 ✓ (somun 1,7 / taban 0,8)**; M6×16 + 2 pul 9,8 (pay tam 0,5, ✓ ama sınırda, 2 pul fazla kalem). Seçim: M6×14 pulsuz (taban ve omuzla aynı çözüm). Etek braketi (M6×14+pul, 2 mm braket) uç 10,4 → somun 1,1 / taban 1,4 (aynı yeni kurala girer).
- `kabuk_parcalar.py`: `L6, GB_PUL = 14, False` (arayuz'deki (6,16) yerine; BAG'a `m6` rolleri), `kabuk_montaj.py`: braket kontrolü artık `SOMUN_GECME = 0,5` ve `TABAN_PAY = 0,5` şartı (hem gövde hem etek braketi), `kabuk-analiz.json` → `m6_vida_pay`.
- `kabuk_rapor.py`: braket bağlantı satırları ve kontrol notu `kabuk-analiz.json` → `m6_vida_pay`'den üretiliyor (eskiden "8× M6×16 + 8× M6 pul" elle yazılıydı).

## Sonuçlar (kabuk_montaj.py 529 s, kabuk_gorsel.py, kabuk_rapor.py)
| | önce | sonra |
|---|---|---|
| `KABUK_BINDIRME_BOSLUK` | 0,2 | **0,25** |
| M5 en küçük dil–komşu boşluğu (şart ≥ 0,15) | 0,1505 (göğüs dikişi) | **0,1881** (aynı dikiş, orta bant ↔ göğüs bandı); 21 çift, ihlal 0; diğerleri 0,2019…0,2500 (etek 0,2153 / 0,2475) |
| Gövde braketi M6 | M6×16 + pul, uç 11,4, taban payı 0,4 ✗ | **M6×14 pulsuz**, uç 11,0, somun payı 1,7, taban payı 0,8 ✓ (8 delik) |
| Etek braketi M6 (yeni kurala göre) | M6×14 + pul, uç 10,4 | aynı; somun payı 1,1, taban payı 1,4 ✓ (6 delik) |
| Parça / kütle | 202 / 4901,2 g | 194 / 4886,3 g (−8 pul, −8 M6×16 → 8 M6×14, dil incelmesi baskıda −3,2 g) |
| AM (x, y, z) | (−0,08; 467,07; 8,54) | (−0,08; 466,68; 8,57) |
- Kontroller: geçersiz 0, çoklu katı 0, kabuk içi çakışma 0 (485 çift), kabuk × iskelet 0 (116 çift), bölge ihlali 0 (51 bölge), braket 10/10, bindirme cıvatası 51/51, ekran 4/4, baskı 15/15 sığar, 15/15 desteksiz.
- Yeni kalıcı kontrol: `kabuk_montaj.py` `SOMUN_GECME`/`TABAN_PAY` (0,5/0,5), `kabuk-analiz.json` → `m6_vida_pay` (14 delik).
- BOM farkı: M6 DIN 125 pul 14 → 6, M6×16 DIN 912 8 → 0, M6×14 DIN 912 6 → 14.

## Etkilenen diğer modüller (yeniden üretmedim)
- `KABUK_BINDIRME_BOSLUK` yalnız `kabuk/` içinde kullanılıyor. Kabuk geometrisini içe alanlar: `carpisma.py` (`yukle_kabuk`; `carpisma-bolum/*.json` ve `carpisma-sonuc.json` eski), `montaj/moduller.py` (ana montaj: 893/899 → −8 pul −8 vida değişimi, kütle −14,9 g; `montaj-analiz.json`, `ana_montaj.py`), `kafa/kafa_montaj.py`, `kafa/kafa_rapor.py`, `taban/taban_montaj.py`, `taban/taban_gorsel.py` (kabuğa statik tarama; taban/regresyon/moduller.json kabuk satırı). Dil 0,05 mm daha ince: tarama sonuçlarını değiştirmesi beklenmez (kabuk dış yüzeyi aynı), ama kanıtlanmadı.
- `OZET.md:13` "Kabuk 202 parça, 4.901 g" eski. `arayuz.KABUK_GOVDE_BRAKET["civata_m6"]` hâlâ (6, 16) ve `not_` "M6x16 + pul" diyor; kabuk bu değeri `kabuk_parcalar.py`'de `L6, GB_PUL = 14, False` ile ezer. Görev "arayuz yalnız iki kayıt" dediği için dokunmadım; öneri: `civata_m6=(6, 14)` ve not metni.
- `maliyet.json`: kabuk vida/pul satırı bulunamadı (yalnız tahrik M6×16 var); kabuk bağlantı elemanları BOM'da 14× M6×14, 6× M6 pul.

## Açık sorunlar
- Pulsuz M6 başı 3 mm Al braketin Ø6,4 deliğine oturuyor (baş Ø10): ezilme/çökme doğrulanmadı (omuz M3 notuyla aynı risk; Al alt tabaka olduğu için PETG'den düşük).
- Boş kalan: 0,25 mm dilin baskı toleransında yeterli olup olmadığı baskı kuponuyla doğrulanmadı.
- `kabuk-baglanti-govde.png` bu görünümde vida başını göstermiyor, pulsuz değişimi görselden doğrulanamaz.
