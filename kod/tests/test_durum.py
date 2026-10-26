import pytest

from robot.durum import GECISLER, Durum, DurumMakinesi, GecersizGecis


def test_baslangic_bekle():
    assert DurumMakinesi().durum == Durum.BEKLE


def test_tam_tur_gecerli():
    m = DurumMakinesi()
    for yeni in (Durum.DINLE, Durum.DUSUN, Durum.JEST, Durum.KONUS, Durum.BEKLE):
        m.gec(yeni)
    assert m.durum == Durum.BEKLE


def test_gecersiz_gecis_hata_verir_ve_durum_degismez():
    m = DurumMakinesi()
    with pytest.raises(GecersizGecis):
        m.gec(Durum.KONUS)
    assert m.durum == Durum.BEKLE


def test_konusurken_dinlemeye_gecilemez():
    # Yarım dupleks: KONUŞ'tan doğrudan DİNLE'ye geçiş yok
    m = DurumMakinesi()
    m.gec(Durum.DINLE)
    m.gec(Durum.DUSUN)
    m.gec(Durum.KONUS)
    with pytest.raises(GecersizGecis):
        m.gec(Durum.DINLE)


def test_dinleyici_haber_alir():
    m = DurumMakinesi()
    haberler = []
    m.dinleyici_ekle(lambda eski, yeni: haberler.append((eski, yeni)))
    m.gec(Durum.DINLE)
    m.gec(Durum.BEKLE)
    assert haberler == [(Durum.BEKLE, Durum.DINLE), (Durum.DINLE, Durum.BEKLE)]


def test_her_durumdan_bekle_ye_donulebilir():
    for durum, hedefler in GECISLER.items():
        if durum != Durum.BEKLE:
            assert Durum.BEKLE in hedefler
