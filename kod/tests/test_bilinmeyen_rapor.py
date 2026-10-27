# Bilinmeyen soru raporu: sentetik günlük CSV'lerinden cevapsız / zayıf soruların gruplanması ve Markdown rapor.

import csv
import os

from olcum import bilinmeyen_rapor as br
from robot.gunluk import ALANLAR, AYIRAC, KODLAMA


def gunluk_yaz(yol, satirlar):
    with open(yol, "w", encoding=KODLAMA, newline="") as dosya:
        yazici = csv.DictWriter(dosya, fieldnames=ALANLAR, delimiter=AYIRAC)
        yazici.writeheader()
        for taninan, konu, puan in satirlar:
            yazici.writerow({"zaman": "2026-10-27T10:00:00", "taninan": taninan, "konu": konu, "puan": puan,
                             "cevap": "..."})


def ornek_klasor(tmp_path):
    klasor = tmp_path / "gunlukler"
    klasor.mkdir()
    gunluk_yaz(klasor / "2026-10-27.csv", [
        ("Kantin nerede?", "Kantin", 6),               # iyi cevap: rapora girmez
        ("Otopark nerede?", "", 0),                    # cevapsız
        ("otopark nerede", "", 0),                     # aynı soru, farklı yazım
        ("Otoparkı nerede?", "bilmiyorum", 0),         # aynı kök: 'otopa'
        ("Merhaba", "kalıp:merhaba", 0),               # kalıp: girmez
        ("", "", ""),                                  # duyulamayan: girmez
        ("Laboratuvar saat kaçta açılıyor", "Laboratuvarlar", 3),   # zayıf eşleşme
        ("Uzaylılar var mı?", "", 0),
    ])
    gunluk_yaz(klasor / "2026-10-25_2.csv", [("otopark nerede", "", 0)])   # pencere içinde, _2 dosyası
    gunluk_yaz(klasor / "2026-10-01.csv", [("Eski soru", "", 0)])        # pencere dışı
    (klasor / "notlar.csv").write_text("bu bir günlük değil", encoding="utf-8")
    return klasor


def test_tur_bul():
    assert br.tur_bul({"taninan": "x", "konu": "", "puan": "0"}) == "cevapsiz"
    assert br.tur_bul({"taninan": "x", "konu": "bilmiyorum", "puan": ""}) == "cevapsiz"
    assert br.tur_bul({"taninan": "x", "konu": "Kantin", "puan": "3"}, esik=4) == "dusuk"
    assert br.tur_bul({"taninan": "x", "konu": "Kantin", "puan": "6"}, esik=4) is None
    assert br.tur_bul({"taninan": "x", "konu": "kalıp:merhaba", "puan": "0"}) is None
    assert br.tur_bul({"taninan": "", "konu": "", "puan": ""}) is None


def test_grup_anahtari_kok_ve_durak_kelime():
    assert br.grup_anahtari("Otopark nerede?") == br.grup_anahtari("OTOPARKI nerede") == "otopa"
    assert br.grup_anahtari("ne?") == "ne"                      # yalnız durak kelime: normalize metin


def test_dosya_penceresi(tmp_path):
    from datetime import date
    klasor = ornek_klasor(tmp_path)
    adlar = [os.path.basename(y) for y in br.gunluk_dosyalari(str(klasor), date(2026, 10, 27), 7)]
    assert adlar == ["2026-10-25_2.csv", "2026-10-27.csv"]


def test_gruplama_siklik_sirasi(tmp_path):
    from datetime import date
    klasor = ornek_klasor(tmp_path)
    gruplar = br.grupla(br.satirlari_oku(br.gunluk_dosyalari(str(klasor), date(2026, 10, 27), 7)))
    # En sık önce; eşit sıklıkta alfabetik
    assert [(g.tur, g.adet, g.soru) for g in gruplar] == [
        ("cevapsiz", 4, "otopark nerede"),
        ("dusuk", 1, "laboratuvar saat kaçta açılıyor"),
        ("cevapsiz", 1, "uzaylılar var mı")]
    assert gruplar[0].ornek == "otopark nerede"            # ilk görülen asıl cümle (eski dosya önce okunur)
    assert gruplar[1].konular["Laboratuvarlar"] == 1


def test_main_rapor_yazar(tmp_path, capsys):
    klasor = ornek_klasor(tmp_path)
    sonuc = tmp_path / "sonuclar"
    kod = br.main(["--gun", "7", "--bugun", "2026-10-27", "--gunluk-klasoru", str(klasor),
                   "--sonuc-klasoru", str(sonuc), "--icerik", "universite"])
    assert kod == 0
    metin = (sonuc / "bilinmeyen-2026-10-27.md").read_text(encoding="utf-8")
    assert "| 1 | otopark nerede | 4 |" in metin
    assert "uzaylılar var mı" in metin
    assert "Laboratuvar saat kaçta açılıyor" in metin and "Eski soru" not in metin
    assert "Laboratuvarlar (puan" in metin or "Laboratuvarlar" in metin    # en yakın kayıt önerisi
    assert "İçeriğe ekle" in metin


def test_gunluk_yoksa_cikis_1(tmp_path):
    assert br.main(["--gunluk-klasoru", str(tmp_path), "--sonuc-klasoru", str(tmp_path / "s")]) == 1
    assert not (tmp_path / "s").exists()
