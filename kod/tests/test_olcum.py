import csv
import os
from datetime import datetime

from conftest import KOD
from olcum.test_seti import (duzenleme_mesafesi, kaydet, kelime_hata_orani, normalize, olc, ozet,
                             satir_degerlendir, seti_oku, sonuc_yolu)
from robot.dil import KuralTabanli
from robot.gunluk import AYIRAC


def test_duzenleme_mesafesi():
    assert duzenleme_mesafesi([], []) == 0
    assert duzenleme_mesafesi("a b c".split(), "a b c".split()) == 0
    assert duzenleme_mesafesi("a b c".split(), "a x c".split()) == 1      # değiştirme
    assert duzenleme_mesafesi("a b c".split(), "a c".split()) == 1        # silme
    assert duzenleme_mesafesi("a b".split(), "a b c d".split()) == 2      # iki ekleme
    assert duzenleme_mesafesi([], "a b".split()) == 2


def test_kelime_hata_orani():
    assert kelime_hata_orani("Kantin nerede?", "kantin nerede") == 0          # normalize sonrası aynı
    assert kelime_hata_orani("Kantin nerede?", "kantinde nerede") == 0.5
    assert kelime_hata_orani("Neler yapabilirsin?", "neler yapa bilirsin") == 1.0   # 1 değiştirme + 1 ekleme
    assert kelime_hata_orani("Kayıt için ne gerekiyor", "") == 1.0
    assert kelime_hata_orani("", "") == 0.0


def test_normalize_turkce():
    assert normalize("  İŞLEM, Işık! ") == "işlem ışık"


def test_satir_degerlendir(paket):
    dil = KuralTabanli(paket)
    s = satir_degerlendir(1, "Kantin nerede?", "kantin nerede", 850, dil)
    assert (s["tam"], s["normalize"], s["hata"], s["konu_ayni"]) == (0, 1, 0, 1)
    s = satir_degerlendir(2, "Kantin nerede?", "kanser nerede", 900, dil)
    assert s["normalize"] == 0 and s["kho_yuzde"] == 50 and s["konu_ayni"] == 0
    s = satir_degerlendir(3, "Kantin nerede?", None, 0, dil)              # hiçbir şey duyulmadı
    assert s["taninan"] == "" and s["hata"] == 2


def test_ozet_oranlar(paket):
    dil = KuralTabanli(paket)
    satirlar = [satir_degerlendir(1, "Kantin nerede?", "Kantin nerede?", 100, dil),
                satir_degerlendir(2, "Laboratuvar nerede?", "laboratuvar nerede", 300, dil),
                satir_degerlendir(3, "Kayıt nerede?", "kayak nerede", 200, dil)]
    o = dict(ozet(satirlar))
    assert o["Tam eşleşme"].startswith("1/3")
    assert o["Normalize eşleşme"].startswith("2/3")
    assert o["Kelime hata oranı"].startswith("%16,7")                     # 1 hata / 6 kelime
    assert o["Konu (niyet) eşleşmesi"].startswith("2/3")
    assert o["Dinleme süresi ms (ort/medyan/en fazla)"] == "200 / 200 / 300"


def test_olc_sahte_stt_ile_ve_erken_bitis(paket):
    class SahteSTT:
        def __init__(self):
            self.cevaplar = ["merhaba"]

        def dinle(self):
            if not self.cevaplar:
                raise EOFError                       # girdi bitti: ölçüm erken biter
            return self.cevaplar.pop(0)
    satirlar = olc(["Merhaba", "Kantin nerede?"], SahteSTT(), KuralTabanli(paket))
    assert len(satirlar) == 1 and satirlar[0]["normalize"] == 1


def test_sonuc_dosyasi(tmp_path):
    yol = sonuc_yolu(str(tmp_path), "vosk", "lab 45dB/ön", datetime(2026, 10, 26, 21, 5))
    assert os.path.basename(yol) == "2026-10-26_2105_vosk_lab_45dB_ön.csv"
    satir = satir_degerlendir(1, "Merhaba", "merhaba", 10)
    kaydet(yol, [satir], ozet([satir]), {"Etiket": "lab 45dB/ön"})
    with open(yol, encoding="utf-8-sig", newline="") as dosya:
        satirlar = list(csv.reader(dosya, delimiter=AYIRAC))
    assert satirlar[0][0] == "no" and satirlar[1][1] == "Merhaba"
    assert ["Etiket", "lab 45dB/ön"] in satirlar and ["Cümle sayısı", "1"] in satirlar


def test_universite_seti_her_cumlenin_konusu_var():
    from robot.icerik import IcerikPaketi
    dil = KuralTabanli(IcerikPaketi.dosyadan(os.path.join(KOD, "icerik", "universite.yaml")))
    cumleler = seti_oku(os.path.join(KOD, "olcum", "test_seti_universite.txt"))
    assert 30 <= len(cumleler) <= 100 and len(set(cumleler)) == len(cumleler)
    for cumle in cumleler:
        assert satir_degerlendir(0, cumle, cumle, 0, dil)["konu_ayni"] == 1, cumle
