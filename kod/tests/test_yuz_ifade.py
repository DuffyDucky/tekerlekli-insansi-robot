# Yüz animasyonu: göz kırpma aralığı, bakışın gezinmesi, bakis_hedefi, DÜŞÜN'de yukarı bakış, KONUŞ'ta ağız.
# Ifade pygame gerektirmez; çizim testleri SDL "dummy" sürücüsüyle bir Surface üzerinde.

import pytest

import robot.yuz as yuz_modulu
from robot.durum import Durum
from robot.yuz import (ELLE_BAKIS_SURESI, GEZINME_GENISLIGI, KIRPMA_ARALIGI, ONBELLEK, Ifade, Yuz,
                       ekrandan_bakis, yuz_ciz)

KARE = 1 / 30


def oynat(ifade, durum, bas, son, metin=""):
    """bas..son saniyeleri arasında 30 fps kare kare günceller; her karenin (t, kırpıyor mu) listesi."""
    kareler = []
    t = bas
    while t < son:
        ifade.guncelle(t, durum, metin)
        kareler.append((t, ifade.kirpiyor, tuple(ifade.bakis), ifade.agiz))
        t += KARE
    return kareler


def test_ifade_pygamesiz_calisir(monkeypatch):
    monkeypatch.setattr(yuz_modulu, "pygame", None)
    oynat(Ifade(tohum=1), Durum.BEKLE, 0, 2)
    assert Yuz().etkin is False


def test_kirpma_3_6_saniyede_bir():
    kareler = oynat(Ifade(tohum=3), Durum.BEKLE, 0, 60)
    # Kırpmanın başladığı kareler: bu karede kırpıyor, önceki karede kırpmıyordu
    baslangiclar = [kareler[i][0] for i in range(1, len(kareler)) if kareler[i][1] and not kareler[i - 1][1]]
    assert len(baslangiclar) >= 9                                   # 60 s'de en az 10'a yakın kırpma
    assert KIRPMA_ARALIGI[0] - KARE <= baslangiclar[0] <= KIRPMA_ARALIGI[1] + KARE
    for a, b in zip(baslangiclar, baslangiclar[1:]):
        assert KIRPMA_ARALIGI[0] - KARE <= b - a <= KIRPMA_ARALIGI[1] + KARE


def test_bekle_disinda_kirpmaz():
    assert not any(k for _, k, *_ in oynat(Ifade(tohum=3), Durum.DINLE, 0, 20))


def test_bakis_gezinir_ve_sinirda_kalir():
    kareler = oynat(Ifade(tohum=5), Durum.BEKLE, 0, 30)
    xler = [b[0] for _, _, b, _ in kareler]
    assert max(abs(x) for x in xler) <= GEZINME_GENISLIGI + 1e-9
    assert max(xler) - min(xler) > 0.1                              # gerçekten kayıyor
    adimlar = [abs(a - b) for a, b in zip(xler, xler[1:])]
    assert max(adimlar) < 0.1                                       # sıçramadan, yavaşça


def test_bakis_hedefi_sonra_gezinmeye_doner():
    ifade = Ifade(tohum=2)
    oynat(ifade, Durum.BEKLE, 0, 1)
    ifade.bakis_hedefi(1.0, -1.0)
    oynat(ifade, Durum.BEKLE, 1, 2.5)
    assert ifade.bakis[0] == pytest.approx(1.0, abs=0.05) and ifade.bakis[1] == pytest.approx(-1.0, abs=0.05)
    oynat(ifade, Durum.BEKLE, 2.5, 1 + ELLE_BAKIS_SURESI + 3)
    assert abs(ifade.bakis[0]) <= GEZINME_GENISLIGI + 0.05          # süre bitti, yeniden gezinmede
    ifade.bakis_hedefi(9, -9)
    assert ifade.istenen[:2] == (1.0, -1.0)                          # sınırlanır


def test_dusunurken_yukari_bakar():
    ifade = Ifade()
    oynat(ifade, Durum.DUSUN, 0, 2)
    assert ifade.bakis[1] < -0.5


def test_konusurken_agiz_metne_gore():
    ifade = Ifade()
    sesli = oynat(ifade, Durum.KONUS, 0, 0.25, metin="aaaaaaaaaa")
    assert sesli[-1][3] > 0.8                                        # sesli harflerde ağız açık
    ifade = Ifade()
    bosluk = oynat(ifade, Durum.KONUS, 0, 0.25, metin="          ")
    assert bosluk[-1][3] == 0.0
    ifade = Ifade()
    kareler = oynat(ifade, Durum.KONUS, 0, 2.0, metin="Merhaba")    # 7 harf / 14 = 0,5 s
    assert max(a for *_, a in kareler[:15]) > 0.5 and kareler[-1][3] < 0.05


def test_ekrandan_bakis_ve_dokunulan_yere_bakar():
    assert ekrandan_bakis((640, 304), (1280, 800)) == pytest.approx((0.0, 0.0))
    yuz = Yuz(1280, 800)
    yuz.dokunma((1280, 0), (1280, 800))
    assert yuz.ifade.istenen[0] == 1.0 and yuz.ifade.istenen[1] < 0


@pytest.fixture
def pg(monkeypatch):
    pygame = pytest.importorskip("pygame")
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    pygame.font.init()
    yield pygame
    pygame.quit()


def test_tum_ifadeler_cizilir_ve_yazi_onbellekte(pg):
    ekran = pg.Surface((1280, 800))
    yazi_tipi = pg.font.Font(None, 36)
    ifade = Ifade(tohum=1)
    t = 0.0
    for durum in Durum:
        for _ in range(10):
            yuz_ciz(ekran, durum, t, yazi_tipi, "Kantin giriş katında.", ifade=ifade)
            t += KARE
    ilk = ONBELLEK.yuzey(yazi_tipi, "BEKLE", (1, 2, 3))
    assert ONBELLEK.yuzey(yazi_tipi, "BEKLE", (1, 2, 3)) is ilk      # ikinci karede yeni yüzey yok
