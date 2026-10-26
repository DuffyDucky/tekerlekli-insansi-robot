import json

from robot.seri import EN_FAZLA_V, SahteSeri, SeriBaglanti, komut_satiri, seri_sec


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
