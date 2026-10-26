import csv
import os

import ana
from robot.dil import Cevap
from robot.gunluk import ALANLAR, AYIRAC, Gunluk, Kronometre, bilesen_adi, tur_satiri
from test_ana import robot_kur


def satirlari_oku(yol):
    with open(yol, encoding="utf-8-sig", newline="") as dosya:
        return list(csv.DictReader(dosya, delimiter=AYIRAC))


def test_iki_tur_tek_baslik(paket, tmp_path):
    robot = robot_kur(paket, ["Merhaba", "Kantin nerede?"])
    robot.gunluk = Gunluk(str(tmp_path / "gunlukler"))      # klasör yoksa açılır
    ana.tek_tur(robot)
    ana.tek_tur(robot)
    yol = robot.gunluk.dosya_yolu()
    ham = open(yol, "rb").read()
    assert ham.count(b"\xef\xbb\xbf") == 1                   # Excel için BOM yalnız dosya başında
    satirlar = satirlari_oku(yol)
    assert list(satirlar[0].keys()) == ALANLAR
    assert len(satirlar) == 2
    selam, kantin = satirlar
    assert selam["konu"] == "kalıp:merhaba" and selam["jest"] == "selam"
    assert kantin["taninan"] == "Kantin nerede?" and kantin["konu"] == "Kantin"
    assert int(kantin["puan"]) >= 3 and kantin["cevap"] == "Kantin giriş katında."
    assert kantin["tetik"] == "AnindaTetik" and kantin["stt"] == "ListeSTT"
    for alan in ("dinleme_ms", "dusunme_ms", "seslendirme_ms", "uctan_uca_ms"):
        assert int(kantin[alan]) >= 0


def test_duyulmayan_soru_da_yazilir(paket, tmp_path):
    robot = robot_kur(paket, [None])
    robot.gunluk = Gunluk(str(tmp_path))
    ana.tek_tur(robot)
    satir = satirlari_oku(robot.gunluk.dosya_yolu())[0]
    assert satir["taninan"] == "" and satir["cevap"] == "" and satir["dusunme_ms"] == ""


def test_bilmiyorum_konusu_bos(paket):
    robot = robot_kur(paket, [])
    cevap = robot.dil.cevapla("bugün hava çok güzel")
    satir = tur_satiri(robot, "bugün hava çok güzel", cevap, Kronometre())
    assert satir["konu"] == "" and satir["puan"] == 0


def test_kronometre_adimlari():
    k = Kronometre()
    k.adim("dinleme")
    k.adim("dusunme")
    assert set(k.sureler) == {"dinleme", "dusunme"}
    assert k.toplam() >= k.sureler["dinleme"]


def test_bulut_adi_saglayiciyi_gosterir():
    class SahteBulut:
        saglayici = "gemini"
        calisiyor = False
    assert bilesen_adi(SahteBulut()) == "SahteBulut(gemini, kurala düştü)"
    assert bilesen_adi(Cevap("x")) == "Cevap"


def test_yazilamazsa_robot_durmaz(tmp_path, capsys):
    engel = tmp_path / "dosya"
    engel.write_text("klasör değil")
    Gunluk(str(engel / "alt")).yaz({"zaman": "x"})          # klasör açılamaz -> yalnız uyarı
    assert "Yazılamadı" in capsys.readouterr().out
    assert not os.path.exists(engel / "alt")
