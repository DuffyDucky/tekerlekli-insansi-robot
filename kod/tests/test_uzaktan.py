# Ne yapıyor: telefondan kumanda (robot/uzaktan) testleri. Sunucu 127.0.0.1'de boş bir portta açılır,
# uçlar http.client ile denenir; robot sahte (sahte seri, kayıt tutan TTS), donanım gerekmez.

import glob
import http.client
import json
import os
import re
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


def komutlar(robot):
    """Gönderilen komutlar; devredeyken köprünün 1 s'de bir attığı canlı tutma ping'leri hariç."""
    return [k for k in (json.loads(x) for x in robot.seri.gonderilenler) if k != {"k": "ping"}]


def son_komut(robot):
    return komutlar(robot)[-1]


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
    assert json_istek(ortam.sunucu, "POST", "/arm", {}, cerez)[0] == 200
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
    kopru.arm()
    kopru.sur(0.15, 0)
    assert kopru.adim(0.10) is None                  # yeni gönderildi, yineleme zamanı gelmedi
    assert kopru.adim(0.16) == "sur"                 # 150 ms: ESP32 watchdog'u beslenir
    assert kopru.adim(0.35) == "sur"
    assert kopru.adim(0.41) == "dur"                 # 400 ms telefondan ses yok: dur
    assert kopru.suruluyor is False and son_komut(robot) == {"k": "dur"}
    assert kopru.adim(1.0) is None                   # durmuşken bir şey gönderilmez


def test_olu_adam_gercek_sunucuda(ortam):
    cerez = giris_yap(ortam.sunucu)
    json_istek(ortam.sunucu, "POST", "/arm", {}, cerez)
    json_istek(ortam.sunucu, "POST", "/sur", {"v": 0.15, "w": 0}, cerez)
    time.sleep(0.8)                                  # telefon "düştü": artık sur gelmiyor
    adlar = [k["k"] for k in komutlar(ortam.robot)]
    assert adlar.count("sur") >= 2                   # Pi kendisi yineledi
    assert adlar[-1] == "dur" and ortam.kopru.suruluyor is False


def test_kapatinca_suruluyorsa_dur(tmp_path):
    robot = sahte_robot()
    sunucu = UzaktanSunucu(RobotKoprusu(robot, bakim_dosyasi=str(tmp_path / "b.txt")), port=0,
                           adres="127.0.0.1").baslat()
    sunucu.kopru.arm()
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
    assert json_istek(ortam.sunucu, "POST", "/arm", {}, cerez)[0] == 200
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


# ---------- güç / röle (ESP32 0.5.0) ----------

def test_guc_arm_birak_uclari(ortam):
    cerez = giris_yap(ortam.sunucu)
    durum = json_istek(ortam.sunucu, "GET", "/durum", cerez=cerez)[1]
    assert durum["guc"] == "birakik" and "Devreye al" in durum["surus_engeli"]
    for alan in ("guc_neden", "ariza", "acil", "bara", "aku", "guc_uyari"):
        assert alan in durum
    # bırakıkken sürüş reddedilir, nedeni telefona yazılır, ESP32'ye sur gitmez
    kod, veri = json_istek(ortam.sunucu, "POST", "/sur", {"v": 0.1, "w": 0}, cerez)
    assert kod == 409 and "bırakık" in veri["hata"] and komutlar(ortam.robot) == []
    kod, veri = json_istek(ortam.sunucu, "POST", "/arm", {}, cerez)
    assert kod == 200 and veri["guc"] == "devrede" and son_komut(ortam.robot) == {"k": "arm"}
    durum = json_istek(ortam.sunucu, "GET", "/durum", cerez=cerez)[1]
    assert durum["guc"] == "devrede" and durum["surus_engeli"] is None and durum["guc_uyari"] is None
    assert json_istek(ortam.sunucu, "POST", "/sur", {"v": 0.1, "w": 0}, cerez)[0] == 200
    kod, veri = json_istek(ortam.sunucu, "POST", "/birak", {}, cerez)
    assert kod == 200 and veri["guc"] == "birakik"
    assert komutlar(ortam.robot)[-2:] == [{"k": "dur"}, {"k": "birak"}] and ortam.kopru.suruluyor is False
    # güvenlik kalıbı aynı: PIN, Origin, yalnız JSON
    assert json_istek(ortam.sunucu, "POST", "/arm", {})[0] == 401
    yanit, _ = istek(ortam.sunucu, "POST", "/arm", {}, cerez, basliklar={"Origin": "http://kotu.example"})
    assert yanit.status == 403
    yanit, _ = istek(ortam.sunucu, "POST", "/birak", "x", cerez, tur="text/plain")
    assert yanit.status == 415


def test_birak_bakimda_ve_rampada_da_calisir(ortam):
    cerez = giris_yap(ortam.sunucu)
    json_istek(ortam.sunucu, "POST", "/arm", {}, cerez)
    json_istek(ortam.sunucu, "POST", "/bakim", {"ac": True}, cerez)
    json_istek(ortam.sunucu, "POST", "/rampa", {"ac": True}, cerez)
    kod, veri = json_istek(ortam.sunucu, "POST", "/birak", {}, cerez)
    assert kod == 200 and veri["guc"] == "birakik" and son_komut(ortam.robot) == {"k": "birak"}
    ortam.robot.seri.satir_isle({"k": "guc", "guc": "ariza", "neden": "i2c", "ms": 1})
    kod, veri = json_istek(ortam.sunucu, "POST", "/birak", {}, cerez)
    assert kod == 200 and son_komut(ortam.robot) == {"k": "birak"}
    # arıza kilitli: birak durumu değiştirmez, telefon "ariza" görür; yalnız yeni arm temizler
    assert veri["guc"] == "ariza"
    assert json_istek(ortam.sunucu, "GET", "/durum", cerez=cerez)[1]["ariza"] == "i2c"
    assert json_istek(ortam.sunucu, "POST", "/arm", {}, cerez)[1]["guc"] == "devrede"
    assert ortam.kopru.durum()["ariza"] is None


def test_ariza_ve_arm_reddi_telefonda_gorunur(ortam):
    cerez = giris_yap(ortam.sunucu)
    ortam.robot.seri.satir_isle({"ok": False, "k": "arm", "hata": "acil_stop"})
    durum = json_istek(ortam.sunucu, "GET", "/durum", cerez=cerez)[1]
    assert durum["guc_uyari"] == "Devreye alınamadı: acil stop basılı."
    ortam.robot.seri.satir_isle({"k": "guc", "guc": "ariza", "neden": "bara_gitti", "ms": 1})
    ortam.robot.seri.son_ret = None
    durum = json_istek(ortam.sunucu, "GET", "/durum", cerez=cerez)[1]
    assert durum["guc"] == "ariza" and durum["ariza"] == "bara_gitti"
    assert "güç barası kesildi" in durum["surus_engeli"] and durum["guc_uyari"] == durum["surus_engeli"]
    ortam.robot.seri.satir_isle({"k": "guc", "guc": "ariza", "neden": "sessizlik", "ms": 2})
    kod, veri = json_istek(ortam.sunucu, "POST", "/sur", {"v": 0.1, "w": 0}, cerez)
    assert kod == 409 and "5 s komut gelmedi" in veri["hata"] and "Devreye al" in veri["hata"]
    ortam.robot.seri.satir_isle({"k": "guc", "guc": "ariza", "neden": "onsarj_sure", "ms": 3})
    assert "ön şarj 1 s'de bitmedi" in ortam.kopru.durum()["surus_engeli"]
    ortam.robot.seri.satir_isle({"ok": False, "k": "arm", "hata": "zamanlayici_yok"})
    assert "süre zamanlayıcısı kurulamadı" in ortam.kopru.durum()["guc_uyari"]


def test_birakikken_acil_basili_uyarisi_ve_durum_sorma():
    """Bırakıkken mantar basılırsa güç olayı gelmez, yalnız ping'de acil:true görünür. Telefon /durum
    sordukça köprü en çok 2 s'de bir ping atar; acil basılıyken uyarı "Devreye al"ın neden olmayacağını söyler."""
    zaman = [0.0]
    robot = sahte_robot()
    kopru = RobotKoprusu(robot, saat=lambda: zaman[0])
    assert kopru.durum()["guc_uyari"].startswith("Röleler bırakık")
    assert robot.seri.gonderilenler == ['{"k":"ping"}']       # durum sorusu ping attı
    robot.seri.acil = True                                     # mantar basıldı (sahte ESP32 ping'de bildirir)
    assert kopru.durum()["guc_uyari"] == "Acil stop basılı: mantarı açmadan devreye alınamaz."
    assert len(robot.seri.gonderilenler) == 1                  # 2 s dolmadan yeni ping yok
    zaman[0] = 2.0
    durum = kopru.durum()
    assert durum["acil"] is True and durum["guc"] == "birakik" and len(robot.seri.gonderilenler) == 2
    kopru.arm()                                                # sahte ESP32 de acil basılıyken reddeder
    assert robot.seri.guc == "birakik" and "Devreye alınamadı" not in kopru.durum()["guc_uyari"]
    robot.seri.acil = False
    kopru.arm()                                                # devredeyken durum sorusu ping atmaz
    sayi = len(robot.seri.gonderilenler)
    zaman[0] = 10.0
    kopru.durum()
    assert len(robot.seri.gonderilenler) == sayi


def test_canli_tut_devredeyken_saniyede_bir_ping():
    zaman = [0.0]
    robot = sahte_robot()
    kopru = RobotKoprusu(robot, saat=lambda: zaman[0])
    assert kopru.canli_tut(0.0) is False                 # bırakık: ping yok (ESP32 sessizlik bekçisi işlemez)
    kopru.arm()
    assert kopru.canli_tut(0.0) is True
    assert kopru.canli_tut(0.5) is False
    assert kopru.canli_tut(1.0) is True
    assert robot.seri.gonderilenler.count('{"k":"ping"}') == 2
    kopru.birak()
    assert kopru.canli_tut(5.0) is False


def test_surerken_role_birakilirsa_surus_kesilir():
    zaman = [0.0]
    robot = sahte_robot()
    kopru = RobotKoprusu(robot, saat=lambda: zaman[0])
    kopru.arm()
    kopru.sur(0.2, 0)
    robot.seri.satir_isle({"k": "guc", "guc": "ariza", "neden": "acil_stop", "ms": 1})
    assert kopru.adim(0.16) == "guc"
    assert kopru.suruluyor is False and son_komut(robot) == {"k": "dur"}
    assert kopru.adim(0.3) is None


def test_guc_bilinmiyorsa_surus_esp32ye_kalir():
    """Eski firmware (ping'de guc yok) ya da satır okunmuyorsa köprü sürmeyi engellemez."""
    robot = sahte_robot()
    robot.seri.guc = None
    kopru = RobotKoprusu(robot)
    assert kopru.sur(0.1, 0) == (0.1, 0.0) and kopru.durum()["surus_engeli"] is None


def test_hicbir_yerde_otomatik_arm(ortam):
    kod_klasoru = os.path.dirname(ana.__file__)
    dosyalar = [os.path.join(kod_klasoru, "ana.py")] + glob.glob(os.path.join(kod_klasoru, "robot", "**", "*.py"),
                                                              recursive=True)
    cagiranlar = {os.path.relpath(d, kod_klasoru).replace(os.sep, "/")
                  for d in dosyalar if re.search(r"\.arm\(\)", open(d, encoding="utf-8").read())}
    # yalnız operatörün POST /arm'ı: sunucu ucu -> köprü -> seri
    assert cagiranlar == {"robot/uzaktan/sunucu.py", "robot/uzaktan/kopru.py"}
    time.sleep(0.2)                                        # sunucu ve köprü döngüsü açık, istek yok
    assert all(k["k"] != "arm" for k in komutlar(ortam.robot))
    assert ortam.robot.seri.guc == "birakik"


def test_sayfada_guc_dugmeleri(ortam):
    _, icerik = istek(ortam.sunucu, "GET", "/")
    sayfa = icerik.decode("utf-8")
    assert 'id="arm"' in sayfa and 'id="birak"' in sayfa and '"/arm"' in sayfa and '"/birak"' in sayfa
    assert "Devreye al" in sayfa and "kollar düşer" in sayfa and "surus_engeli" in sayfa


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
