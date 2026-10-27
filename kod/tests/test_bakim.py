# Bakım modu: BEKLE -> BAKIM (bir kez söyler, dur gönderir, mikrofonu kapatır) -> dosya silinince BEKLE.
# Tetik beklerken bakım açılırsa tur yapılmaz; mikrofonun zaman aşımlı beklemesi.

import pytest

import ana
from robot.bakim import BAKIM_SOZU, Bakim
from robot.dil import KuralTabanli
from robot.durum import Durum, DurumMakinesi, GecersizGecis
from robot.mikrofon import PARCA, Mikrofon
from robot.seri import SahteSeri
from robot.tetik import DokunmaTetik
from robot.yuz import Yuz


class ListeSTT:
    def __init__(self, cumleler):
        self.cumleler = list(cumleler)

    def dinle(self):
        return self.cumleler.pop(0)


class AnindaTetik:
    def bekle(self):
        pass


class SayanTTS:
    def __init__(self):
        self.soylenenler = []

    def soyle(self, metin):
        self.soylenenler.append(metin)


class SahteMikrofon:
    def __init__(self):
        self.kapatildi = 0

    def kapat(self):
        self.kapatildi += 1


def robot_kur(paket, tmp_path, cumleler=(), tetik=None):
    yuz = Yuz()
    yuz.etkin = False
    durum = DurumMakinesi()
    durum.dinleyici_ekle(yuz.durum_degisti)
    bakim = Bakim(dosya=str(tmp_path / "bakim.txt"), aralik=0.01, uyu=lambda s: None)
    return ana.Robot(durum, tetik or AnindaTetik(), ListeSTT(cumleler), KuralTabanli(paket),
                     SayanTTS(), SahteSeri(), yuz, jest_suresi=0, bakim=bakim)


def test_bakim_dosyasi_ve_kalici_bakim(tmp_path):
    dosya = tmp_path / "bakim.txt"
    b = Bakim(dosya=str(dosya))
    assert not b.acik_mi()
    dosya.write_text("", encoding="utf-8")
    assert b.acik_mi()
    dosya.unlink()
    assert not b.acik_mi()
    assert Bakim(etkin=True, dosya=None).acik_mi()


def test_durum_tablosunda_bakim():
    m = DurumMakinesi()
    m.gec(Durum.BAKIM)
    with pytest.raises(GecersizGecis):
        m.gec(Durum.DINLE)                       # bakımdan doğrudan dinlemeye geçilmez
    m.gec(Durum.BEKLE)
    m.gec(Durum.DINLE)
    with pytest.raises(GecersizGecis):
        m.gec(Durum.BAKIM)                       # konuşma turu yarıda kesilmez


def test_bakima_gir_bir_kez_soyle_sonra_cik(paket, tmp_path):
    robot = robot_kur(paket, tmp_path, ["Merhaba"])
    robot.tetik.mikrofon = SahteMikrofon()
    gecisler = []
    robot.durum.dinleyici_ekle(lambda eski, yeni: gecisler.append(yeni))
    (tmp_path / "bakim.txt").write_text("telefon", encoding="utf-8")

    ana.tek_tur(robot)
    assert robot.durum.durum == Durum.BAKIM
    assert robot.seri.gonderilenler == ['{"k":"dur"}']
    assert robot.tts.soylenenler == [BAKIM_SOZU]
    assert robot.tetik.mikrofon.kapatildi == 1
    assert robot.yuz.durum == Durum.BAKIM and robot.yuz.metin == BAKIM_SOZU

    ana.tek_tur(robot)
    ana.tek_tur(robot)
    assert robot.tts.soylenenler == [BAKIM_SOZU]              # bakım boyunca sessiz
    assert robot.stt.cumleler == ["Merhaba"]                   # dinlenmedi

    (tmp_path / "bakim.txt").unlink()
    ana.tek_tur(robot)                                         # bakımdan çıkar ve normal tur yapar
    assert gecisler == [Durum.BAKIM, Durum.BEKLE, Durum.DINLE, Durum.DUSUN, Durum.JEST, Durum.KONUS, Durum.BEKLE]
    assert robot.tts.soylenenler[-1] == "Merhaba, hoş geldiniz!"


def test_bakim_yoksa_eski_davranis(paket, tmp_path):
    robot = robot_kur(paket, tmp_path, ["Merhaba"])
    robot.bakim = None
    (tmp_path / "bakim.txt").write_text("", encoding="utf-8")
    ana.tek_tur(robot)
    assert robot.durum.durum == Durum.BEKLE and robot.tts.soylenenler == ["Merhaba, hoş geldiniz!"]


def test_beklerken_bakim_acilirsa_tur_yok(paket, tmp_path):
    tetik = DokunmaTetik()
    robot = robot_kur(paket, tmp_path, ["Merhaba"], tetik=tetik)
    (tmp_path / "bakim.txt").write_text("", encoding="utf-8")
    assert ana.tetik_bekle(robot) is False                     # kimse dokunmadı, bakım açık
    (tmp_path / "bakim.txt").unlink()
    tetik.dokunuldu()
    assert ana.tetik_bekle(robot) is True                      # bekleme sürüyordu: dokunma sayılır


def test_dokunma_tetik_zaman_asimi():
    tetik = DokunmaTetik()
    assert tetik.bekle(0.01) is False
    tetik.dokunuldu()
    assert tetik.bekle(0.01) is True
    tetik.dokunuldu()                                          # tur bitti; eski dokunma
    assert tetik.bekle(0.01) is False                          # yeni beklemenin başında atılır


def test_mikrofon_zaman_asimli_bekleme():
    np = pytest.importorskip("numpy")
    sessiz = bytes(PARCA * 2)
    yuksek = np.full(PARCA, 3000, dtype=np.int16).tobytes()
    parcalar = [sessiz] * 10 + [sessiz] * 40 + [yuksek] * 3

    class Akis:
        def start(self): pass
        def stop(self): pass
        def close(self): pass
        def read(self, adet):
            return (parcalar.pop(0) if parcalar else sessiz), False

    mik = Mikrofon(esik=500, vad_duzeyi=-1, akis_ac=Akis)
    assert mik.konusma_bekle(zaman_asimi=0.9) is False          # 30 parça sessizlik
    assert mik.konusma_bekle(zaman_asimi=0.9) is True           # kalan 10 sessiz + 3 konuşma
    assert mik.on_kayit[-3:] == [yuksek] * 3 and len(mik.on_kayit) == 10


def test_bakim_secenegi_mikrofonsuz_durmaz(tmp_path):
    sec = ana.secenekleri_oku(["--yuzsuz", "--bakim"])
    ayar = ana.secenekleri_uygula(ana.ayarlari_oku(sec.ayar), sec)
    ayar["konum"]["etkin"] = False
    ayar["gunluk"]["etkin"] = False
    assert ayar["bakim"]["etkin"] is True
    robot = ana.bilesenleri_kur(ayar)                          # mikrofon/Vosk yok ama SesliModKurulamadi yok
    assert robot.bakim.acik_mi()
