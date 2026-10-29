import json

from robot.seri import EN_FAZLA_V, SahteSeri, SeriBaglanti, komut_satiri, port_ac, seri_sec


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


class SahteSerialModulu:
    """pyserial taklidi: Serial() nesnesine yapılan atamaları ve open() anını kaydeder."""

    def __init__(self):
        self.olaylar = []
        modul = self

        class Serial:
            def __setattr__(self, ad, deger):
                modul.olaylar.append((ad, deger))
                object.__setattr__(self, ad, deger)

            def open(self):
                modul.olaylar.append(("open", None))

        self.Serial = Serial


def test_port_dtr_rts_kapali_acilir():
    modul = SahteSerialModulu()
    ser = port_ac("/dev/ttyUSB0", 115200, serial_modulu=modul)
    adlar = [ad for ad, _ in modul.olaylar]
    assert adlar[-1] == "open"
    # DTR ve RTS open()'dan ÖNCE kapalıya çekilir (açılışta ESP32 resetlenmesin)
    assert ("dtr", False) in modul.olaylar and ("rts", False) in modul.olaylar
    assert adlar.index("dtr") < adlar.index("open") and adlar.index("rts") < adlar.index("open")
    assert ser.port == "/dev/ttyUSB0" and ser.baudrate == 115200


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
