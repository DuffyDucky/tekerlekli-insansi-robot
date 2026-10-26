import os

from conftest import KOD
from robot.icerik import IcerikPaketi, ifade_geciyor_mu, kelimeler, turkce_kucuk


def test_turkce_kucuk_harf():
    assert turkce_kucuk("İSTANBUL IŞIK") == "istanbul ışık"
    assert turkce_kucuk("İzmir Irmak") == "izmir ırmak"


def test_noktalama_temizlenir():
    assert kelimeler("Kantin, nerede?!") == ["kantin", "nerede"]


def test_ekli_kelime_anahtarla_eslesir():
    assert ifade_geciyor_mu("kantin", ["kantinde", "çay"])
    assert ifade_geciyor_mu("sağ ol", kelimeler("Çok sağ olun"))
    assert not ifade_geciyor_mu("kantin", ["otobüs"])


def test_buyuk_harfli_soru_eslesir(paket):
    eslesme = paket.ara("LABORATUVAR NEREDE?")
    assert eslesme.kayit.baslik == "Laboratuvar"
    assert eslesme.puan >= 3


def test_yer_ve_sss_aranir(paket):
    assert paket.ara("Kantine nasıl giderim?").kayit.baslik == "Kantin"
    assert paket.ara("WiFi şifresi").kayit.cevap.startswith("Evet")


def test_esik_altinda_none(paket):
    assert paket.ara("bugün hava çok güzel") is None


def test_esik_ayarlanabilir():
    from conftest import ORNEK
    gevsek = IcerikPaketi(ORNEK, esik=1)
    siki = IcerikPaketi(ORNEK, esik=100)
    assert gevsek.ara("ikinci katta ne var") is not None   # yalnız kelime örtüşmesi
    assert siki.ara("laboratuvar") is None


def test_en_iyiler_en_fazla_uc(paket):
    sonuc = paket.en_iyiler("laboratuvar kayıt otobüs kantin internet", 3)
    assert len(sonuc) == 3
    assert sonuc[0].puan >= sonuc[-1].puan


def test_ornek_paketler_yuklenir():
    for ad in ("universite", "tesis"):
        p = IcerikPaketi.dosyadan(os.path.join(KOD, "icerik", ad + ".yaml"))
        assert p.kurum and p.selamlama and len(p.kayitlar) >= 5


def test_universite_paketinde_tipik_sorular():
    p = IcerikPaketi.dosyadan(os.path.join(KOD, "icerik", "universite.yaml"))
    assert p.ara("Kantin nerede?").kayit.baslik == "Kantin"
    assert p.ara("Kayıt için ne gerekiyor?").kayit.baslik == "Kayıt"
    assert p.ara("Kampüse hangi otobüs gidiyor?").kayit.baslik == "Ulaşım"
