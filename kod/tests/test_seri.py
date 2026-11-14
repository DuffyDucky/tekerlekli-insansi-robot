import json
import threading
import time

from robot.seri import EN_FAZLA_V, SahteSeri, SeriBaglanti, esp32_reset, komut_satiri, port_ac, seri_sec


def test_jest_satiri():
    s = SahteSeri()
    s.jest("selam")
    assert s.gonderilenler == ['{"k":"jest","ad":"selam"}']


def test_sur_ve_dur():
    s = SahteSeri()
    s.sur(0.3, 0.0)
    s.dur()
    assert json.loads(s.gonderilenler[0]) == {"k": "sur", "v": 0.3, "w": 0.0}
    assert s.gonderilenler[1] == '{"k":"dur"}'


def test_hiz_sinirlanir():
    s = SahteSeri()
    s.sur(5.0, -9.0)
    komut = json.loads(s.gonderilenler[0])
    assert komut["v"] == EN_FAZLA_V and komut["w"] < 0


def test_turkce_karakter_bozulmaz():
    assert komut_satiri({"k": "jest", "ad": "başla"}) == '{"k":"jest","ad":"başla"}'


def test_gercek_baglanti_satir_sonu_ekler():
    class SahtePort:
        def __init__(self):
            self.yazilan = b""

        def write(self, veri):
            self.yazilan += veri

    port = SahtePort()
    SeriBaglanti("COM_YOK", baglanti=port).dur()
    assert port.yazilan == b'{"k":"dur"}\n'


def test_port_bossa_sahte():
    assert isinstance(seri_sec(""), SahteSeri)


# ---------- rampa kipi ve port açılışı (29 Ekim 2026) ----------

def test_rampa_satiri_ve_durumu():
    s = SahteSeri()
    assert s.rampa_acik is False
    s.rampa(True)
    assert s.gonderilenler[-1] == '{"k":"rampa","ac":true}' and s.rampa_acik is True
    s.rampa(False)
    assert s.gonderilenler[-1] == '{"k":"rampa","ac":false}' and s.rampa_acik is False


class DevKitPortu:
    """pyserial + DevKit otomatik reset devresi taklidi (CP2102 DTR/RTS -> iki transistör -> EN/GPIO0).
    open(), serialposix.py'deki sırayı izler: Linux açılışta iki hattı da etkin yapar, sonra pyserial
    ÖNCE DTR'yi SONRA RTS'yi ayarlar. Açık portta dtr/rts ataması hemen uygulanır (serialutil setter'ı).
    Her hat değişiminden sonra EN ve GPIO0 hesaplanır; EN LOW = reset."""

    def __init__(self):
        object.__setattr__(self, "acik", False)
        object.__setattr__(self, "istenen", {"dtr": True, "rts": True})   # pyserial varsayılanı
        object.__setattr__(self, "hat", {"dtr": False, "rts": False})     # port kapalıyken ikisi bırakık
        object.__setattr__(self, "olaylar", [])
        object.__setattr__(self, "resetler", 0)
        object.__setattr__(self, "indirme_kipi", 0)

    def _uygula(self, ad, deger):
        self.hat[ad] = deger
        self.olaylar.append((ad, deger))
        en_low = self.hat["rts"] and not self.hat["dtr"]
        io0_low = self.hat["dtr"] and not self.hat["rts"]
        if en_low:
            object.__setattr__(self, "resetler", self.resetler + 1)
        if en_low and io0_low:                          # devrede ikisi birden olamaz; olursa indirme kipi
            object.__setattr__(self, "indirme_kipi", self.indirme_kipi + 1)

    def __setattr__(self, ad, deger):
        if ad in ("dtr", "rts"):
            self.istenen[ad] = deger
            if self.acik:
                self._uygula(ad, deger)
        else:
            object.__setattr__(self, ad, deger)

    def open(self):
        self.olaylar.append(("open", None))
        self._uygula("dtr", True)                       # çekirdek açılışta ikisini de etkin yapar
        self._uygula("rts", True)
        self._uygula("dtr", self.istenen["dtr"])        # serialposix.py open: önce DTR ...
        self._uygula("rts", self.istenen["rts"])        # ... sonra RTS
        object.__setattr__(self, "acik", True)


class SahteSerialModulu:
    def __init__(self):
        self.portlar = []

    def Serial(self):
        port = DevKitPortu()
        self.portlar.append(port)
        return port


def test_port_ac_esp32yi_resetlemez():
    modul = SahteSerialModulu()
    ser = port_ac("/dev/ttyUSB0", 115200, serial_modulu=modul)
    assert ser.port == "/dev/ttyUSB0" and ser.baudrate == 115200 and ser.acik
    assert ser.resetler == 0                            # EN hiç LOW olmadı
    assert ser.hat == {"dtr": False, "rts": False}      # açıldıktan sonra ikisi de bırakık
    acilis = ser.olaylar.index(("open", None))
    assert ser.olaylar[-1] == ("dtr", False) and len(ser.olaylar) > acilis + 1


def test_eski_sira_resetliyordu():
    """Model doğru mu: eski kod (dtr=False, rts=False ile açmak) bu modelde ESP32'yi resetler."""
    port = DevKitPortu()
    port.dtr = False
    port.rts = False
    port.open()
    assert port.resetler == 1


def test_esp32_reset_dtr_etkinlesmez():
    modul = SahteSerialModulu()
    ser = port_ac("/dev/ttyUSB0", serial_modulu=modul)
    uykular = []
    esp32_reset(ser, uyu=uykular.append)
    assert ser.resetler == 1 and ser.indirme_kipi == 0
    sonra = ser.olaylar[ser.olaylar.index(("dtr", False)) + 1:]
    assert sonra[-2:] == [("rts", True), ("rts", False)] and ("dtr", True) not in sonra
    assert uykular == [0.1] and ser.hat == {"dtr": False, "rts": False}


class SatirPortu:
    """readline() sırayla verilen satırları döner; ping yazılınca isteğe bağlı cevap ekler."""

    def __init__(self, satirlar=(), ping_cevabi=None):
        self.satirlar = list(satirlar)
        self.ping_cevabi = ping_cevabi
        self.yazilan = b""

    def write(self, veri):
        self.yazilan += veri
        if self.ping_cevabi and b'"k":"ping"' in veri:
            self.satirlar.append(self.ping_cevabi)

    def readline(self):
        return self.satirlar.pop(0) if self.satirlar else b""


def test_hazir_satiri_beklenir_reset_olursa():
    port = SatirPortu([b"ets Jun  8 2016 rst:0x1\n",
                       b'{"k":"odo","sol":0,"sag":0,"yaw":null,"ms":5}\n',
                       b'{"k":"hazir","surum":"0.4.0","pca9685":true}\n'])
    s = SeriBaglanti("COM_YOK", baglanti=port, hazir_sure=1.0)
    assert s.hazir_kaynagi == "hazir" and s.surum == "0.4.0"


def test_reset_olmazsa_ping_cevabi_yeter():
    port = SatirPortu(ping_cevabi=b'{"ok":true,"k":"ping","surum":"0.4.0","rampa":false}\n')
    s = SeriBaglanti("COM_YOK", baglanti=port, hazir_sure=1.0)
    assert s.hazir_kaynagi == "ping" and s.surum == "0.4.0"
    assert b'{"k":"ping"}\n' in port.yazilan


def test_hic_cevap_yoksa_yine_de_acilir():
    port = SatirPortu()
    s = SeriBaglanti("COM_YOK", baglanti=port, hazir_sure=0.2)
    assert s.hazir_kaynagi is None
    s.dur()
    assert port.yazilan.endswith(b'{"k":"dur"}\n')


# ---------- güç / röle (firmware 0.5.0) ----------

def test_arm_birak_reset_satirlari():
    port = SatirPortu()
    s = SeriBaglanti("COM_YOK", baglanti=port)
    s.arm()
    s.birak()
    s.reset()
    assert port.yazilan == b'{"k":"arm"}\n{"k":"birak"}\n{"k":"reset"}\n'


def test_guc_olayi_ve_ping_durumu_gunceller():
    port = SatirPortu([b'{"ok":true,"k":"arm","guc":"onsarj"}\n',
                       b'{"k":"odo","sol":1,"sag":1,"yaw":null,"ms":9}\n',
                       b'{"k":"guc","guc":"devrede","neden":null,"ms":600}\n',
                       b'{"ok":true,"k":"ping","surum":"0.5.0","guc":"devrede","acil":false,"bara":true,'
                       b'"aku":24.6,"ariza":null}\n',
                       b'{"k":"guc","guc":"ariza","neden":"acil_stop","ms":900}\n'])
    s = SeriBaglanti("COM_YOK", baglanti=port)
    assert s.guc is None and not s.canli_tut_gerekli()
    s.arm()
    assert s.canli_tut_gerekli()                        # cevap okunmadan da canlı tutulur
    assert s.satir_oku()["guc"] == "onsarj" and s.guc == "onsarj"
    assert s.satir_oku()["k"] == "odo" and s.guc == "onsarj"     # odo satırı okuyana aynen döner
    s.satir_oku()
    assert s.devrede_mi() and s.canli_tut_gerekli()
    s.satir_oku()
    g = s.guc_durumu()
    assert (g["acil"], g["bara"], g["aku"], s.surum) == (False, True, 24.6, "0.5.0")
    s.satir_oku()
    g = s.guc_durumu()
    assert (g["guc"], g["neden"], g["ariza"]) == ("ariza", "acil_stop", "acil_stop")
    assert not s.canli_tut_gerekli()


def test_arm_reddi_ve_sessizlik():
    port = SatirPortu([b'{"ok":false,"k":"arm","hata":"acil_stop"}\n',
                       b'{"ok":false,"k":"arm","hata":"zaten_devrede"}\n',
                       b'{"k":"guc","guc":"birakik","neden":"sessizlik","ms":5000}\n',
                       b'{"ok":false,"k":"sur","hata":"devrede_degil"}\n'])
    s = SeriBaglanti("COM_YOK", baglanti=port)
    s.arm()
    s.satir_oku()
    assert s.son_ret == {"k": "arm", "hata": "acil_stop"} and not s.canli_tut_gerekli()
    s.arm()
    assert s.son_ret is None                            # yeni deneme eski nedeni siler
    s.satir_oku()
    assert s.guc == "devrede"                           # "zaten devrede" cevabı durumu düzeltir
    s.satir_oku()
    assert (s.guc, s.neden, s.ariza) == ("birakik", "sessizlik", None)
    s.satir_oku()
    assert s.son_ret == {"k": "sur", "hata": "devrede_degil"}


def test_hazir_resetten_sonra_birakik_ve_rampa_kapali():
    port = SatirPortu([b'{"k":"hazir","surum":"0.5.0","guc":"birakik"}\n'])
    s = SeriBaglanti("COM_YOK", baglanti=port)
    s.rampa(True)
    s.arm()
    s.satir_oku()
    assert s.guc == "birakik" and s.rampa_acik is False and not s.canli_tut_gerekli()


def test_eski_firmware_guc_bilinmiyor():
    port = SatirPortu(ping_cevabi=b'{"ok":true,"k":"ping","surum":"0.4.0","rampa":false}\n')
    s = SeriBaglanti("COM_YOK", baglanti=port, hazir_sure=1.0)
    assert s.hazir_kaynagi == "ping" and s.guc is None


class ResetPortu(SatirPortu):
    """Sahte pyserial: rts etkinden bırakığa dönünce ESP32 açılmış gibi "hazir" satırı ekler."""

    def __init__(self):
        super().__init__()
        self.hatlar = []

    def __setattr__(self, ad, deger):
        if ad in ("dtr", "rts"):
            self.hatlar.append((ad, deger))
            if ad == "rts" and deger is False and ("rts", True) in self.hatlar:
                self.satirlar += [b'{"ok":true,"k":"ping","guc":"devrede"}\n',   # eski ping cevabı
                                  b'{"k":"hazir","surum":"0.5.0","guc":"birakik"}\n']
        object.__setattr__(self, ad, deger)


def test_baglanti_esp32_reset_hazir_bekler():
    port = ResetPortu()
    s = SeriBaglanti("COM_YOK", baglanti=port)
    s.guc = "devrede"
    assert s.esp32_reset(hazir_sure=1.0, uyu=lambda _: None) == "hazir"
    assert port.hatlar == [("dtr", False), ("rts", True), ("rts", False)]
    assert s.guc == "birakik" and b"ping" not in port.yazilan    # resetten sonra ping atılmaz


def test_hazir_bekle_okuyucu_varken_satir_calmaz():
    port = SatirPortu()
    s = SeriBaglanti("COM_YOK", baglanti=port)
    s.okuyucu_kaydet(True)
    okunan = []
    port.readline = lambda: okunan.append(1) or b""
    zamanlayici = threading.Timer(0.15, s.satir_isle, args=({"k": "hazir", "surum": "0.5.0", "guc": "birakik"},))
    zamanlayici.start()
    basla = time.monotonic()
    assert s.hazir_bekle(1.0, yalniz_hazir=True) == "hazir"
    assert okunan == [] and time.monotonic() - basla < 0.9


def test_okuyucu_baslat_kancadan_gecirir():
    port = SatirPortu([b'{"k":"guc","guc":"devrede","neden":null,"ms":1}\n'])
    s = SeriBaglanti("COM_YOK", baglanti=port)
    port.close = lambda: None
    s.okuyucu_baslat()
    try:
        bitis = time.monotonic() + 2
        while s.guc != "devrede" and time.monotonic() < bitis:
            time.sleep(0.01)
        assert s.guc == "devrede" and s.okuyucu_var
    finally:
        s.kapat()
    assert not s.okuyucu_var and port.yazilan.endswith(b'{"k":"dur"}\n')
    assert b"birak" not in port.yazilan                 # kapanışta röle bırakılmaz (kollar düşmesin)


def test_sahte_seri_gucu_taklit_eder():
    s = SahteSeri()
    assert s.guc == "birakik"
    s.sur(0.1, 0)
    assert s.son_ret == {"k": "sur", "hata": "devrede_degil"}
    s.arm()
    assert s.devrede_mi() and s.canli_tut_gerekli()
    s.ping()
    assert s.guc_durumu()["bara"] is True
    s.birak()
    assert s.guc == "birakik" and not s.canli_tut_gerekli()
    s.arm()
    s.reset()
    assert s.guc == "birakik"
    assert [json.loads(x)["k"] for x in s.gonderilenler] == ["sur", "arm", "ping", "birak", "arm", "reset"]
