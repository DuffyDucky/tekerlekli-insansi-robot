# Dokunma tetiği ve ekrandaki metin kutusu (metin kutusu yalnız --gelistirici). pygame olayları (tıklama, parmak, Türkçe harf, Enter)
# sentezlenip yüzün olay işleyicisine verilir; pencere için SDL'nin "dummy" sürücüsü kullanılır.

import threading
import time

import pytest

import ana
from robot.dil import KuralTabanli
from robot.durum import Durum, DurumMakinesi
from robot.gunluk import Gunluk
from robot.seri import SahteSeri
from robot.stt import EkranSTT, KlavyeSTT
from robot.tetik import DokunmaTetik, KlavyeTetik, tetik_sec
from robot.tts import YaziTTS
from robot.yuz import Olcu, Yuz, alanda_mi, alt_alan

BOYUT = (1280, 800)


# ---------- pygame gerektirmeyenler ----------

def test_dokunma_tetik_kuyrugu():
    tetik = DokunmaTetik()
    tetik.dokunuldu()                       # eski dokunma: bekle() başında atılmalı
    sonuc = []
    is_parcacigi = threading.Thread(target=lambda: sonuc.append(tetik.bekle()))
    is_parcacigi.start()
    time.sleep(0.1)
    assert is_parcacigi.is_alive()          # eski dokunma sayılmadı, hâlâ bekliyor
    tetik.dokunuldu()
    is_parcacigi.join(1)
    assert not is_parcacigi.is_alive()


def test_ekran_stt_kuyrugu():
    stt = EkranSTT()
    threading.Timer(0.05, stt.gonder, args=["  Kantin nerede?  "]).start()
    assert stt.dinle() == "Kantin nerede?"
    threading.Timer(0.05, stt.gonder, args=["   "]).start()
    assert stt.dinle() is None              # boş Enter: soru yok


def test_tetik_sec_dokunma():
    assert isinstance(tetik_sec("dokunma"), DokunmaTetik)
    assert isinstance(tetik_sec("klavye"), KlavyeTetik)


def test_alan_hesabi():
    o = Olcu(*BOYUT, True)
    x, y, gen, yuk = alt_alan(o)
    assert alanda_mi(o, x + gen / 2, y + yuk / 2)
    assert not alanda_mi(o, o.cx, o.goz_y)          # yüze dokunmak tetik değil
    assert y + yuk <= BOYUT[1] and o.metin_y < y   # alan ekranda, alt yazının altında


def test_yuz_kapaliysa_klavyeye_duser():
    yuz = Yuz()
    yuz.etkin = False
    tetik, stt = ana.ekran_girdisini_bagla(yuz, DokunmaTetik(), KlavyeSTT())
    assert isinstance(tetik, KlavyeTetik) and isinstance(stt, KlavyeSTT)


def test_yuz_aciksa_ekrana_baglanir():
    yuz = Yuz()
    yuz.etkin = True
    tetik, stt = ana.ekran_girdisini_bagla(yuz, DokunmaTetik(), KlavyeSTT(), gelistirici=True)
    assert yuz.dokunma_tetik is tetik and yuz.yazi_alici is stt
    assert isinstance(stt, EkranSTT)


def test_metin_kutusu_yalniz_gelistiricide():
    yuz = Yuz()
    yuz.etkin = True
    tetik, stt = ana.ekran_girdisini_bagla(yuz, DokunmaTetik(), KlavyeSTT())
    assert yuz.dokunma_tetik is tetik                       # dokunma tetiği normal modda da seçenek
    assert yuz.yazi_alici is None and isinstance(stt, KlavyeSTT)


# ---------- pygame olaylarıyla ----------

@pytest.fixture
def pg(monkeypatch):
    pygame = pytest.importorskip("pygame")
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    yield pygame
    pygame.quit()


def bagli_yuz():
    yuz = Yuz(*BOYUT)
    yuz.dokunma_tetik = DokunmaTetik()
    yuz.yazi_alici = EkranSTT()
    return yuz


def dugme_merkezi():
    x, y, gen, yuk = alt_alan(Olcu(*BOYUT, True))
    return (int(x + gen / 2), int(y + yuk / 2))


def olaylari_ver(pygame, yuz, olaylar):
    for olay in olaylar:
        pygame.event.post(olay)
    yuz._olaylari_isle(threading.Event(), BOYUT)


def yaz_olaylari(pygame, metin):
    return [pygame.event.Event(pygame.TEXTINPUT, text=harf) for harf in metin]


def tus(pygame, kod):
    return pygame.event.Event(pygame.KEYDOWN, key=kod, mod=0, unicode="", scancode=0)


def test_tiklama_yalniz_bekle_de_ve_alanda_tetikler(pg):
    yuz = bagli_yuz()
    yuz.pencere_ac()
    kuyruk = yuz.dokunma_tetik.kuyruk
    olaylari_ver(pg, yuz, [pg.event.Event(pg.MOUSEBUTTONDOWN, pos=(640, 200), button=1)])
    assert kuyruk.empty()                                   # yüze tıklama sayılmaz
    olaylari_ver(pg, yuz, [pg.event.Event(pg.MOUSEBUTTONDOWN, pos=dugme_merkezi(), button=1)])
    assert kuyruk.qsize() == 1
    yuz.durum = Durum.KONUS                                 # robot konuşurken dokunma sayılmaz
    olaylari_ver(pg, yuz, [pg.event.Event(pg.MOUSEBUTTONDOWN, pos=dugme_merkezi(), button=1)])
    assert kuyruk.qsize() == 1


def test_parmak_dokunmasi_tetikler(pg):
    yuz = bagli_yuz()
    yuz.pencere_ac()
    x, y = dugme_merkezi()
    olaylari_ver(pg, yuz, [pg.event.Event(pg.FINGERDOWN, x=x / BOYUT[0], y=y / BOYUT[1],
                                          dx=0, dy=0, touch_id=0, finger_id=0, pressure=1)])
    assert yuz.dokunma_tetik.kuyruk.qsize() == 1


def test_metin_kutusu_turkce_backspace_enter(pg):
    yuz = bagli_yuz()
    yuz.pencere_ac()
    olaylari_ver(pg, yuz, yaz_olaylari(pg, "erken"))
    assert yuz.yazi == ""                                   # DİNLE değilken yazı alınmaz
    yuz.durum = Durum.DINLE
    olaylari_ver(pg, yuz, yaz_olaylari(pg, "Işık ğüşöçİx"))
    olaylari_ver(pg, yuz, [tus(pg, pg.K_BACKSPACE)])
    assert yuz.yazi == "Işık ğüşöçİ"
    olaylari_ver(pg, yuz, [tus(pg, pg.K_RETURN)])
    assert yuz.yazi == ""
    assert yuz.yazi_alici.kuyruk.get_nowait() == "Işık ğüşöçİ"


def test_kare_ciz_alt_serit(pg):
    yuz = bagli_yuz()
    ekran = yuz.pencere_ac()
    yuz.yazi = "Kantin nerede? " * 10                       # kutuya sığmayan uzun yazı
    for durum in Durum:
        yuz.kare_ciz(ekran, durum, 0.3)


def test_uctan_uca_dokun_yaz_cevap(pg, paket, tmp_path):
    """Gerçek akış: konuşma iş parçacığı tek_tur'u çalıştırır, test ana iş parçacığında
    yüzün olaylarını işler (tıklama -> yazı -> Enter) ve cevabın günlüğe yazıldığını görür."""
    yuz = bagli_yuz()
    yuz.pencere_ac()
    durum = DurumMakinesi()
    durum.dinleyici_ekle(yuz.durum_degisti)
    robot = ana.Robot(durum, yuz.dokunma_tetik, yuz.yazi_alici, KuralTabanli(paket), YaziTTS(),
                      SahteSeri(), yuz, jest_suresi=0, gunluk=Gunluk(str(tmp_path)))
    konusma = threading.Thread(target=ana.tek_tur, args=(robot,), daemon=True)
    konusma.start()
    time.sleep(0.1)                                         # tetik bekle()'ye girsin
    olaylari_ver(pg, yuz, [pg.event.Event(pg.MOUSEBUTTONDOWN, pos=dugme_merkezi(), button=1)])
    sinir = time.monotonic() + 2
    while yuz.durum != Durum.DINLE and time.monotonic() < sinir:
        time.sleep(0.01)
    assert yuz.durum == Durum.DINLE
    olaylari_ver(pg, yuz, yaz_olaylari(pg, "Kantin nerede?") + [tus(pg, pg.K_RETURN)])
    konusma.join(2)
    assert not konusma.is_alive()
    assert yuz.metin == "Kantin giriş katında."
    satirlar = robot.gunluk.dosya_yolu()
    icerik = open(satirlar, encoding="utf-8-sig").read()
    assert "DokunmaTetik;EkranSTT;Kantin nerede?;KuralTabanli;Kantin;" in icerik
