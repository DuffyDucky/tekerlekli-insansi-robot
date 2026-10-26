import os

import pytest

import ana
from robot.dil import KuralTabanli
from robot.durum import Durum, DurumMakinesi
from robot.seri import SahteSeri
from robot.tts import YaziTTS
from robot.yuz import Yuz


class ListeSTT:
    """Sırayla verilen cümleleri 'duyar'."""

    def __init__(self, cumleler):
        self.cumleler = list(cumleler)

    def dinle(self):
        return self.cumleler.pop(0)


class AnindaTetik:
    def bekle(self):
        pass


def robot_kur(paket, cumleler):
    yuz = Yuz()
    yuz.etkin = False
    durum = DurumMakinesi()
    durum.dinleyici_ekle(yuz.durum_degisti)
    return ana.Robot(durum, AnindaTetik(), ListeSTT(cumleler), KuralTabanli(paket),
                     YaziTTS(), SahteSeri(), yuz, jest_suresi=0)


def test_tek_tur_jestli_cevap(paket, capsys):
    robot = robot_kur(paket, ["Merhaba"])
    gecisler = []
    robot.durum.dinleyici_ekle(lambda eski, yeni: gecisler.append(yeni))
    ana.tek_tur(robot)
    assert gecisler == [Durum.DINLE, Durum.DUSUN, Durum.JEST, Durum.KONUS, Durum.BEKLE]
    assert robot.seri.gonderilenler == ['{"k":"jest","ad":"selam"}']
    assert "Robot: Merhaba, hoş geldiniz!" in capsys.readouterr().out
    assert robot.yuz.metin == "Merhaba, hoş geldiniz!"


def test_bos_girdi_bekle_ye_doner(paket):
    robot = robot_kur(paket, [None])
    ana.tek_tur(robot)
    assert robot.durum.durum == Durum.BEKLE
    assert robot.seri.gonderilenler == []


def test_ayar_dosyasi_ve_secenekler():
    sec = ana.secenekleri_oku(["--yuzsuz", "--icerik", "tesis", "--saglayici", "anthropic"])
    ayar = ana.secenekleri_uygula(ana.ayarlari_oku(sec.ayar), sec)
    assert ayar["yuz"]["etkin"] is False
    assert ayar["dil"]["saglayici"] == "anthropic"
    assert os.path.exists(ana.paket_yolu(ayar["icerik"]["paket"]))


def test_varsayilan_ayarla_bilesenler_kurulur():
    sec = ana.secenekleri_oku(["--yuzsuz"])
    robot = ana.bilesenleri_kur(ana.secenekleri_uygula(ana.ayarlari_oku(sec.ayar), sec))
    assert isinstance(robot.seri, SahteSeri)
    assert robot.durum.durum == Durum.BEKLE


def test_yuz_cizimi_tum_durumlar():
    pygame = pytest.importorskip("pygame")
    from robot.yuz import yuz_ciz
    pygame.font.init()
    ekran = pygame.Surface((1280, 800))
    yazi_tipi = pygame.font.Font(None, 36)
    for durum in Durum:
        yuz_ciz(ekran, durum, 1.3, yazi_tipi, "Kantin giriş katında, sağ tarafta.")


def test_pygame_yoksa_yuz_kapali(monkeypatch):
    import robot.yuz as yuz_modulu
    monkeypatch.setattr(yuz_modulu, "pygame", None)
    assert yuz_modulu.Yuz().etkin is False
