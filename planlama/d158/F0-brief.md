# F0 brief (P0.1, P0.2, P0.3) — 08.11.2026

Plan: `planlama/dongu-158.md`. Depo: `%USERPROFILE%\OneDrive\Masaüstü\Robot`, dal `lale-duzeltme`.

## P0.1 Commitlenmemiş dosyaları sınıflandır
`git status` ve `git diff --stat` ile her değişiklik/izlenmeyen yol için: ne değişmiş (özet), hangi işe ait
(158 QLED / kafa-yerleşim / rehber / elektrik / KVKK / tek sayfa rapor / 2209-B / bilinmiyor), commit grubu önerisi,
dışlanması gereken (satıcı dosyaları `kafa-yerlesim/kaynak/`, büyük ikili, kişisel veri) var mı.
Özellikle: `tasarim/freecad/rehber/rehber_metin.py` (+356 satır) kimin işi, rehber günlüğüyle (`planlama/rehber/R-gunluk.md`) tutarlı mı.
**Commit atma, dosya silme, geri alma YOK.** Çıktı: `planlama/d158/P0.1-siniflandirma.md` (tablo + önerilen commit grupları
ve her grup için tam `git add` yol listesi + commit mesajı).

## P0.2 Karar kuyruğu
`planlama/d158/karar-kuyrugu.md`: dongu-158.md bölüm 4'teki K1–K9 + kaynaklarda bulduğun başka açık kararlar
(`tasarim/freecad/lale158/qled-cerceve-tasarim-notu.md` "Ahmet'e sorular" (belgedeki başlık takma adla), `kafa-yerlesim/uygulama-notu.md` "Karar gereken
noktalar", `kafa-yerlesim/secenekler.md` "sorular", `planlama/y3/Y3-kontrol.md`). Her madde: soru, en az 2 seçenek,
sayısal etki (kaynak dosya:satır), önerilen varsayılan, hangi paket(ler)i bloke ettiği, durum (açık/kapandı + kaynak).
Kapanmış olanı açık gösterme. Belgede kişi adı "Ahmet" (takma ad yazma).

## P0.3 Regresyon betiği
`planlama/d158/regresyon.py` (yalnız standart kütüphane): dongu-158.md bölüm 1'deki korunan değerleri ilgili JSON'lardan
(`tasarim/freecad/lale158/lale158-kontrol.json`, `kafa-yerlesim/*.json`, `carpisma-sonuc.json` vb. — kendin bul) okur,
`planlama/d158/regresyon.json`'a yazar, önceki kayıt varsa karşılaştırıp kötüleşeni listeler ve çıkış kodu 1 verir.
Her değerin kaynağını (dosya + anahtar yolu) çıktıda göster. Bugünkü değerlerle koşturup sonucu günlüğe yaz.
Beklenen bugünkü değerler: boy 1580,0; rampa yüksüz 1,517; tilt 3,64; pan 2,21; mik-hoparlör 574,3; SY8205×USB 0.
Bulunamayan değer varsa uydurma, "kaynak yok" yaz.

Günlük: `planlama/d158/F0-gunluk.md` (ne yaptın, hangi dosyaya dokundun, açık kalanlar).
