# Ne yapıyor: telefondan kumanda (robot/uzaktan) testleri. Sunucu 127.0.0.1'de boş bir portta açılır,
# uçlar http.client ile denenir; robot sahte (sahte seri, kayıt tutan TTS), donanım gerekmez.

import http.client
import json
import os
import threading
import time
from types import SimpleNamespace

import pytest
import yaml

import ana
from robot.durum import Durum
from robot.konum.bolgeler import Bolge, Bolgeler
from robot.konum.elle import ElleKaynak
from robot.uzaktan import RobotKoprusu, UzaktanSunucu
from robot.uzaktan.kopru import SusturulanTetik
from robot.uzaktan.sahte import sahte_robot

PIN = "4821"


class KayitTTS:
    def __init__(self):
        self.soylenenler = []
        self.bitti = threading.Event()

    def soyle(self, metin):
        self.soylenenler.append(metin)
        self.bitti.set()


class SahteKonum:
    """KonumYoneticisi'nin köprünün kullandığı kadarı: bolgeler, kaynaklar['elle'], durum(), tahmin_ekle()."""

    def __init__(self, dosya):
        self.bolgeler = Bolgeler({"giris-holu": Bolge("giris-holu", "Giriş holü"),
                                  "kantin-onu": Bolge("kantin-onu", "Kantin önü")})
        self.kaynaklar = {"elle": ElleKaynak(dosya=dosya, bilinen_bolgeler=self.bolgeler.adlar())}
        self.son = None

    def tahmin_ekle(self, kaynak, tahmin):
        self.son = tahmin.bolge if tahmin else None

    def durum(self):
        return {"bolge": self.son, "bolge_adi": self.bolgeler.ad(self.son) if self.son else None}


@pytest.fixture
def ortam(tmp_path):
    robot = sahte_robot(tts=KayitTTS(), konum=SahteKonum(str(tmp_path / "bolge.txt")))
    kopru = RobotKoprusu(robot, bakim_dosyasi=str(tmp_path / "bakim.txt"))
    sunucu = UzaktanSunucu(kopru, port=0, pin=PIN, adres="127.0.0.1").baslat()
    yield SimpleNamespace(robot=robot, kopru=kopru, sunucu=sunucu, klasor=tmp_path)
    sunucu.kapat()


def istek(sunucu, yontem, yol, govde=None, cerez=None, tur="application/json", basliklar=None):
    baglanti = http.client.HTTPConnection("127.0.0.1", sunucu.port, timeout=5)
    b = dict(basliklar or {})
    if cerez:
        b["Cookie"] = cerez
    veri = None
    if govde is not None:
        veri = govde if isinstance(govde, (bytes, str)) else json.dumps(govde)
        b["Content-Type"] = tur
    baglanti.request(yontem, yol, body=veri, headers=b)
    yanit = baglanti.getresponse()
    icerik = yanit.read()
    baglanti.close()
    return yanit, icerik


def json_istek(sunucu, yontem, yol, govde=None, cerez=None):
    yanit, icerik = istek(sunucu, yontem, yol, govde, cerez)
    return yanit.status, json.loads(icerik)


def giris_yap(sunucu):
    yanit, _ = istek(sunucu, "POST", "/giris", {"pin": PIN})
    assert yanit.status == 200
    return yanit.getheader("Set-Cookie").split(";")[0]


def son_komut(robot):
    return json.loads(robot.seri.gonderilenler[-1])


# ---------- sayfa ve manifest ----------

def test_sayfa_manifest_ikon(ortam):
    yanit, icerik = istek(ortam.sunucu, "GET", "/")
    assert yanit.status == 200 and "text/html" in yanit.getheader("Content-Type")
    assert "Lale Kumanda" in icerik.decode("utf-8") and 'rel="manifest"' in icerik.decode("utf-8")
    yanit, icerik = istek(ortam.sunucu, "GET", "/manifest.json")
    manifest = json.loads(icerik)
    assert yanit.status == 200 and manifest["start_url"] == "/" and manifest["display"] == "standalone"
    yanit, icerik = istek(ortam.sunucu, "GET", "/ikon-192.png")
    assert yanit.status == 200 and icerik.startswith(b"\x89PNG")
    assert istek(ortam.sunucu, "GET", "/yok")[0].status == 404


# ---------- PIN ve oturum ----------

def test_pin_olmadan_401(ortam):
    assert json_istek(ortam.sunucu, "GET", "/durum")[0] == 401
    assert json_istek(ortam.sunucu, "POST", "/sur", {"v": 0.1, "w": 0})[0] == 401
    assert json_istek(ortam.sunucu, "GET", "/durum", cerez="lale_oturum=uydurma")[0] == 401
    assert ortam.robot.seri.gonderilenler == []


def test_yanlis_pin_gecikmeli_dogru_pin_cerez(ortam):
    basla = time.monotonic()
    kod, veri = json_istek(ortam.sunucu, "POST", "/giris", {"pin": "0000"})
    assert kod == 401 and time.monotonic() - basla >= 0.9 and "yanlış" in veri["hata"]
    yanit, _ = istek(ortam.sunucu, "POST", "/giris", {"pin": PIN})
    cerez = yanit.getheader("Set-Cookie")
    assert yanit.status == 200 and "HttpOnly" in cerez and "SameSite=Strict" in cerez
    kod, durum = json_istek(ortam.sunucu, "GET", "/durum", cerez=cerez.split(";")[0])
    assert kod == 200
    for alan in ("durum", "bolge", "son_soru", "son_cevap", "bakim", "seri_turu", "calisma_suresi"):
        assert alan in durum
    assert durum["durum"] == "BEKLE" and durum["seri_turu"] == "SahteSeri"


def test_yalniz_json_post_ve_ayni_kaynak(ortam):
    cerez = giris_yap(ortam.sunucu)
    yanit, _ = istek(ortam.sunucu, "POST", "/sur", "v=0.1&w=0", cerez, tur="application/x-www-form-urlencoded")
    assert yanit.status == 415
    yanit, _ = istek(ortam.sunucu, "POST", "/sur", '{"v":0.1}', cerez, tur="text/plain")
    assert yanit.status == 415
    yanit, _ = istek(ortam.sunucu, "POST", "/sur", {"v": 0.1, "w": 0}, cerez,
                     basliklar={"Origin": "http://kotu.example"})
    assert yanit.status == 403
    yanit, _ = istek(ortam.sunucu, "POST", "/sur", "[1,2]", cerez)
    assert yanit.status == 400
    assert ortam.robot.seri.gonderilenler == []


# ---------- sürüş ----------

def test_sur_hiz_sinirina_kirpilir(ortam):
    cerez = giris_yap(ortam.sunucu)
    kod, veri = json_istek(ortam.sunucu, "POST", "/sur", {"v": 5, "w": -9}, cerez)
    assert kod == 200 and (veri["v"], veri["w"]) == (0.5, -1.0)
    assert son_komut(ortam.robot) == {"k": "sur", "v": 0.5, "w": -1.0}
    yanit, _ = istek(ortam.sunucu, "POST", "/sur", '{"v": NaN, "w": 0}', cerez)
    assert yanit.status == 400
    assert json_istek(ortam.sunucu, "POST", "/dur", {}, cerez)[0] == 200
    assert son_komut(ortam.robot) == {"k": "dur"}


def test_olu_adam_ve_yineleme_sahte_saat():
    zaman = [0.0]
    robot = sahte_robot()
    kopru = RobotKoprusu(robot, saat=lambda: zaman[0])
    kopru.sur(0.15, 0)
    assert kopru.adim(0.10) is None                  # yeni gönderildi, yineleme zamanı gelmedi
    assert kopru.adim(0.16) == "sur"                 # 150 ms: ESP32 watchdog'u beslenir
    assert kopru.adim(0.35) == "sur"
    assert kopru.adim(0.41) == "dur"                 # 400 ms telefondan ses yok: dur
    assert kopru.suruluyor is False and son_komut(robot) == {"k": "dur"}
    assert kopru.adim(1.0) is None                   # durmuşken bir şey gönderilmez


def test_olu_adam_gercek_sunucuda(ortam):
    cerez = giris_yap(ortam.sunucu)
    json_istek(ortam.sunucu, "POST", "/sur", {"v": 0.15, "w": 0}, cerez)
    time.sleep(0.8)                                  # telefon "düştü": artık sur gelmiyor
    komutlar = [json.loads(s)["k"] for s in ortam.robot.seri.gonderilenler]
    assert komutlar.count("sur") >= 2                # Pi kendisi yineledi
    assert komutlar[-1] == "dur" and ortam.kopru.suruluyor is False


def test_kapatinca_suruluyorsa_dur(tmp_path):
    robot = sahte_robot()
    sunucu = UzaktanSunucu(RobotKoprusu(robot, bakim_dosyasi=str(tmp_path / "b.txt")), port=0,
                           adres="127.0.0.1").baslat()
    sunucu.kopru.sur(0.1, 0)
    sunucu.kapat()
    assert son_komut(robot) == {"k": "dur"}


# ---------- jest, söz, bölge, bakım ----------

def test_jest(ortam):
    cerez = giris_yap(ortam.sunucu)
    assert json_istek(ortam.sunucu, "POST", "/jest", {"ad": "selam"}, cerez)[0] == 200
    assert son_komut(ortam.robot) == {"k": "jest", "ad": "selam"}
    assert json_istek(ortam.sunucu, "POST", "/jest", {"ad": "isaret", "yon": "sol"}, cerez)[0] == 200
    assert son_komut(ortam.robot) == {"k": "jest", "ad": "isaret", "yon": "sol"}
    assert json_istek(ortam.sunucu, "POST", "/jest", {"ad": "dans"}, cerez)[0] == 400
    assert json_istek(ortam.sunucu, "POST", "/jest", {"ad": "selam", "yon": "sol"}, cerez)[0] == 400


def test_soyle_beklede_hemen_degilse_ret(ortam):
    cerez = giris_yap(ortam.sunucu)
    kod, veri = json_istek(ortam.sunucu, "POST", "/soyle", {"metin": "  Merhaba   dostlar "}, cerez)
    assert kod == 200 and veri["metin"] == "Merhaba dostlar"
    assert ortam.robot.tts.bitti.wait(2)
    assert ortam.robot.tts.soylenenler == ["Merhaba dostlar"] and ortam.robot.yuz.metin == "Merhaba dostlar"
    ortam.robot.durum.gec(Durum.DINLE)
    kod, veri = json_istek(ortam.sunucu, "POST", "/soyle", {"metin": "Selam"}, cerez)
    assert kod == 409 and "DİNLE" in veri["hata"]
    assert json_istek(ortam.sunucu, "POST", "/soyle", {"metin": "   "}, cerez)[0] == 400
    assert json_istek(ortam.sunucu, "POST", "/soyle", {"metin": "a" * 301}, cerez)[0] == 400
    assert ortam.robot.tts.soylenenler == ["Merhaba dostlar"]


def test_bolge_dosyasi(ortam):
    cerez = giris_yap(ortam.sunucu)
    kod, veri = json_istek(ortam.sunucu, "GET", "/bolgeler", cerez=cerez)
    assert kod == 200 and {"kimlik": "kantin-onu", "ad": "Kantin önü"} in veri["bolgeler"]
    dosya = ortam.klasor / "bolge.txt"
    assert json_istek(ortam.sunucu, "POST", "/bolge", {"ad": "kantin-onu"}, cerez)[0] == 200
    assert dosya.read_text(encoding="utf-8").strip() == "kantin-onu"
    assert ortam.robot.konum.son == "kantin-onu"            # 5 s beklemeden birleştiriciye verildi
    assert json_istek(ortam.sunucu, "GET", "/durum", cerez=cerez)[1]["bolge_adi"] == "Kantin önü"
    assert json_istek(ortam.sunucu, "POST", "/bolge", {"ad": "ay-yuzeyi"}, cerez)[0] == 400
    assert json_istek(ortam.sunucu, "POST", "/bolge", {"ad": ""}, cerez)[0] == 200
    assert not dosya.exists() and ortam.robot.konum.son is None


def test_bakim_dosyasi(ortam):
    cerez = giris_yap(ortam.sunucu)
    dosya = ortam.klasor / "bakim.txt"
    kod, veri = json_istek(ortam.sunucu, "POST", "/bakim", {"ac": True}, cerez)
    assert kod == 200 and veri["bakim"] is True and dosya.exists()
    assert json_istek(ortam.sunucu, "GET", "/durum", cerez=cerez)[1]["bakim"] is True
    assert json_istek(ortam.sunucu, "POST", "/bakim", {"ac": False}, cerez)[1]["bakim"] is False
    assert not dosya.exists()
    assert json_istek(ortam.sunucu, "POST", "/bakim", {"ac": "evet"}, cerez)[0] == 400


def test_rampa_kipi(ortam):
    cerez = giris_yap(ortam.sunucu)
    assert json_istek(ortam.sunucu, "GET", "/durum", cerez=cerez)[1]["rampa"] is False
    kod, veri = json_istek(ortam.sunucu, "POST", "/rampa", {"ac": True}, cerez)
    assert kod == 200 and veri["rampa"] is True
    assert son_komut(ortam.robot) == {"k": "rampa", "ac": True}
    assert json_istek(ortam.sunucu, "GET", "/durum", cerez=cerez)[1]["rampa"] is True
    # rampada kollar ev pozunda: jest reddedilir, ESP32'ye gönderilmez
    kod, veri = json_istek(ortam.sunucu, "POST", "/jest", {"ad": "selam"}, cerez)
    assert kod == 409 and "ev pozunda" in veri["hata"]
    assert son_komut(ortam.robot) == {"k": "rampa", "ac": True}
    # sürüş rampada da çalışır (ivme sınırını ESP32 uygular)
    assert json_istek(ortam.sunucu, "POST", "/sur", {"v": 0.1, "w": 0}, cerez)[0] == 200
    assert json_istek(ortam.sunucu, "POST", "/dur", {}, cerez)[0] == 200
    kod, veri = json_istek(ortam.sunucu, "POST", "/rampa", {"ac": False}, cerez)
    assert kod == 200 and veri["rampa"] is False
    assert son_komut(ortam.robot) == {"k": "rampa", "ac": False}
    assert json_istek(ortam.sunucu, "POST", "/jest", {"ad": "selam"}, cerez)[0] == 200
    assert json_istek(ortam.sunucu, "POST", "/rampa", {"ac": "evet"}, cerez)[0] == 400
    assert json_istek(ortam.sunucu, "POST", "/rampa", {"ac": True})[0] == 401


def test_sayfada_rampa_anahtari(ortam):
    _, icerik = istek(ortam.sunucu, "GET", "/")
    sayfa = icerik.decode("utf-8")
    assert 'id="rampa"' in sayfa and 'role="switch"' in sayfa
    assert "kollar ev pozunda, yavaş" in sayfa and '"/rampa"' in sayfa


# ---------- ana döngüyle etkileşim ----------

def test_son_soru_cevap_dil_gecmisinden(ortam):
    ortam.robot.dil.gecmis.turlar.append(("Kantin nerede?", "Giriş katında."))
    durum = ortam.kopru.durum()
    assert (durum["son_soru"], durum["son_cevap"]) == ("Kantin nerede?", "Giriş katında.")
    ortam.robot.son_tur = ("Soru", "Cevap")                 # ana.py son_tur verirse o önceliklidir
    assert ortam.kopru.durum()["son_soru"] == "Soru"


def test_soylerken_gelen_tetik_yok_sayilir():
    sayac = []

    class AnindaTetik:
        def bekle(self):
            sayac.append(1)
            time.sleep(0.01)

    robot = sahte_robot()
    robot.tetik = AnindaTetik()
    kopru = RobotKoprusu(robot)
    kopru.baslat()
    try:
        assert isinstance(robot.tetik, SusturulanTetik)
        kopru.konusma_bitti.clear()                          # uzaktan cümle sürüyor
        bitti = threading.Event()
        threading.Thread(target=lambda: (robot.tetik.bekle(), bitti.set()), daemon=True).start()
        time.sleep(0.1)
        assert not bitti.is_set()                            # robot kendi sesini soru sanmadı
        kopru.son_konusma_bitisi = time.monotonic() - 1
        kopru.konusma_bitti.set()
        assert bitti.wait(2) and len(sayac) >= 2
    finally:
        kopru.kapat()
    assert isinstance(robot.tetik, AnindaTetik)              # kapanınca asıl tetik geri gelir


def test_ana_uzaktan_kur_port_acmaz():
    assert ana.uzaktan_kur({"uzaktan": {"etkin": False}}, sahte_robot()) is None
    assert ana.uzaktan_kur({}, sahte_robot()) is None
    sunucu = ana.uzaktan_kur({"uzaktan": {"etkin": True, "port": 0, "pin": "9"}}, sahte_robot())
    assert isinstance(sunucu, UzaktanSunucu) and sunucu.httpd is None and sunucu.pin == "9"


def test_ana_main_sunucuyu_acip_kapatir(tmp_path, monkeypatch, capsys):
    with open(os.path.join(os.path.dirname(ana.__file__), "ayarlar.yaml"), encoding="utf-8") as f:
        ayar = yaml.safe_load(f)
    ayar["uzaktan"] = {"etkin": True, "port": 0, "pin": PIN}
    ayar["konum"]["etkin"] = False
    ayar["gunluk"]["etkin"] = False
    dosya = tmp_path / "ayarlar.yaml"
    dosya.write_text(yaml.safe_dump(ayar, allow_unicode=True), encoding="utf-8")

    def girdi_bitti(*_):
        raise EOFError

    monkeypatch.setattr("builtins.input", girdi_bitti)       # Enter tetiği hemen "girdi bitti" alır
    assert ana.main(["--ayar", str(dosya), "--yuzsuz", "--gelistirici", "--tts", "yazi"]) == 0
    cikti = capsys.readouterr().out
    assert "[uzaktan] Telefondan kumanda:" in cikti and "Robot kapandı" in cikti
