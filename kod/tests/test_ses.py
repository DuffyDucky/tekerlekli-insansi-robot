# Sesli mod: ortak mikrofon (sahte akışla), ses tetiği, sessizlikle biten dinleme,
# mikrofon yoksa normal modda durma / geliştirici modunda klavyeye düşme.

import pytest

import ana
from robot.mikrofon import ON_KAYIT_PARCA, PARCA, PARCA_MS, Mikrofon
from robot.stt import EkranSTT, KlavyeSTT
from robot.tetik import DokunmaTetik, KlavyeTetik, SesTetik, tetik_sec

np = pytest.importorskip("numpy")

SESSIZ = bytes(PARCA * 2)                                       # 480 örnek x 2 bayt, hepsi 0
YUKSEK = np.full(PARCA, 3000, dtype=np.int16).tobytes()         # RMS 3000: konuşma


class SahteAkis:
    """sounddevice.RawInputStream yerine: sırayla verilen parçaları okur, bitince sessizlik."""

    def __init__(self, parcalar):
        self.parcalar = list(parcalar)
        self.acik = False

    def start(self):
        self.acik = True

    def stop(self):
        self.acik = False

    def close(self):
        pass

    def read(self, adet):
        assert adet == PARCA and self.acik
        return (self.parcalar.pop(0) if self.parcalar else SESSIZ), False


def sahte_mikrofon(parcalar, sessizlik_saniye=0.3):
    akis = SahteAkis(parcalar)
    mik = Mikrofon(esik=500, sessizlik_saniye=sessizlik_saniye, vad_duzeyi=-1, akis_ac=lambda: akis)
    return mik, akis


def ms_parca(ms):
    return ms // PARCA_MS


def test_tetik_konusma_baslayinca_ve_on_kayit():
    # 300 ms açılış atlanır, 600 ms sessizlik, sonra konuşma: 3 parça (90 ms) konuşma tetikler
    mik, akis = sahte_mikrofon([SESSIZ] * 10 + [SESSIZ] * 20 + [YUKSEK] * 5)
    SesTetik(mik).bekle()
    assert len(mik.on_kayit) == ON_KAYIT_PARCA                  # konuşmanın başı + 300 ms öncesi saklandı
    assert mik.on_kayit[-3:] == [YUKSEK] * 3
    assert akis.acik                                            # STT aynı akıştan devam edecek


def test_tek_tiklama_tetiklemez():
    mik, akis = sahte_mikrofon([SESSIZ] * 10 + [YUKSEK, SESSIZ, YUKSEK, YUKSEK, SESSIZ] + [YUKSEK] * 3)
    mik.konusma_bekle()
    assert len(akis.parcalar) == 0                              # ancak son 3 ardışık parçada tetikledi


def test_dinleme_sessizlikle_biter_ve_mikrofon_kapanir():
    mik, akis = sahte_mikrofon([SESSIZ] * 10 + [SESSIZ] * 20 + [YUKSEK] * 3 + [YUKSEK] * 20 + [SESSIZ] * 50)
    mik.konusma_bekle()
    ses = mik.konusmayi_kaydet(azami_saniye=8)
    parca_sayisi = len(ses) // (PARCA * 2)
    # ön kayıt (10) + kalan konuşma (20) + 0,3 s sessizlik (10 parça) sonra biter
    assert parca_sayisi == ON_KAYIT_PARCA + 20 + ms_parca(300)
    assert not akis.acik and mik.akis is None                   # yarım dupleks: DİNLE bitince kapalı


def test_kimse_konusmazsa_bos_doner():
    mik, akis = sahte_mikrofon([])
    parcalar = list(mik.konusma_parcalari(azami_saniye=8, konusmasiz_bekleme=1))
    assert len(parcalar) == 34                                  # 34 x 30 ms = 1,02 s sonra vazgeçer
    assert mik.akis is None


def test_azami_sure_siniri():
    mik, _ = sahte_mikrofon([SESSIZ] * 10 + [YUKSEK] * 1000)
    parcalar = list(mik.konusma_parcalari(azami_saniye=1))
    assert len(parcalar) <= ms_parca(1000) + 1


def test_esik_ayari():
    mik, _ = sahte_mikrofon([])
    orta = np.full(PARCA, 400, dtype=np.int16).tobytes()
    assert not mik.konusma_mi(orta)
    mik.esik = 300
    assert mik.konusma_mi(orta)


def test_tetik_sec_ses():
    mik, _ = sahte_mikrofon([])
    assert isinstance(tetik_sec("ses", mikrofon=mik), SesTetik)
    assert isinstance(tetik_sec("ses", mikrofon=None), KlavyeTetik)


# ---------- ana.py: sesli mod denetimi ----------

def ayar_kur(*secenekler):
    sec = ana.secenekleri_oku(list(secenekler))
    return ana.secenekleri_uygula(ana.ayarlari_oku(sec.ayar), sec)


def test_mikrofon_yoksa_normal_modda_durur(monkeypatch):
    monkeypatch.setattr(ana, "mikrofon_kur", lambda ayar: None)    # bu makinede mikrofon yok
    with pytest.raises(ana.SesliModKurulamadi, match="--gelistirici"):
        ana.bilesenleri_kur(ayar_kur("--yuzsuz"))
    assert ana.main(["--yuzsuz"]) == 2


def test_mikrofon_yoksa_gelistiricide_klavyeye_duser(monkeypatch):
    monkeypatch.setattr(ana, "mikrofon_kur", lambda ayar: None)
    robot = ana.bilesenleri_kur(ayar_kur("--yuzsuz", "--gelistirici"))
    assert isinstance(robot.tetik, KlavyeTetik) and isinstance(robot.stt, KlavyeSTT)
    robot = ana.bilesenleri_kur(ayar_kur("--yuz", "--gelistirici"))
    if robot.yuz.etkin:                                           # pygame kuruluysa: dokun + metin kutusu
        assert isinstance(robot.tetik, DokunmaTetik) and isinstance(robot.stt, EkranSTT)


def test_mikrofon_varsa_ses_tetigi_kurulur(monkeypatch):
    mik, _ = sahte_mikrofon([])
    monkeypatch.setattr(ana, "mikrofon_kur", lambda ayar: mik)
    # STT klavye seçilirse Vosk modeli gerekmez; tetik yine sesli
    robot = ana.bilesenleri_kur(ayar_kur("--yuzsuz", "--stt", "klavye"))
    assert isinstance(robot.tetik, SesTetik) and robot.tetik.mikrofon is mik


def test_deneme_saniye_mikrofon_istemez():
    assert ayar_kur("--yuz", "--deneme-saniye", "2")["gelistirici"] is True
    assert ayar_kur("--yuz")["gelistirici"] is False


# ---------- Vosk ortak mikrofondan okur (sahte vosk modülüyle) ----------

def test_vosk_ortak_mikrofondan_tanir(monkeypatch, tmp_path):
    import json
    import sys
    from types import SimpleNamespace

    from robot.stt import VoskSTT

    class SahteTaniyici:
        def __init__(self, model, ornekleme):
            self.bayt = 0

        def AcceptWaveform(self, parca):
            self.bayt += len(parca)
            return False

        def FinalResult(self):
            return json.dumps({"text": "kantin nerede" if self.bayt else ""})

    sahte_vosk = SimpleNamespace(Model=lambda yol: "model", KaldiRecognizer=SahteTaniyici, SetLogLevel=lambda d: None)
    monkeypatch.setitem(sys.modules, "vosk", sahte_vosk)
    mik, akis = sahte_mikrofon([SESSIZ] * 30 + [YUKSEK] * 10 + [SESSIZ] * 20)
    stt = VoskSTT(str(tmp_path), mik)
    SesTetik(mik).bekle()
    assert stt.dinle() == "kantin nerede"
    assert mik.akis is None
