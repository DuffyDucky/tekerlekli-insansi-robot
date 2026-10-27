# Selamlama ve kalıp cevaplarında varyant: tek metin ya da liste; listeden rastgele ama art arda aynısı değil.

import os

from conftest import KOD, ORNEK
from icerik_kontrol import denetle
from robot.dil import KuralTabanli, VaryantSecici
from robot.icerik import IcerikPaketi, metin_listesi

SELAMLAR = ["Merhaba!", "Hoş geldiniz!", "İyi günler, hoş geldiniz!", "Selam, buyurun!"]


def paket_kur(**ekler):
    return IcerikPaketi({**ORNEK, **ekler}, esik=3)


def test_metin_listesi_tek_metin_ve_liste():
    assert metin_listesi("Merhaba") == ["Merhaba"]
    assert metin_listesi(["a", "", None, "  b "]) == ["a", "b"]
    assert metin_listesi(None, "varsayılan") == ["varsayılan"]
    assert metin_listesi([], None) == []


def test_tek_metin_selamlama_hep_ayni(paket):
    k = KuralTabanli(paket, tohum=1)
    assert {k.cevapla("merhaba").metin for _ in range(5)} == {"Merhaba, hoş geldiniz!"}


def test_liste_selamlama_ardisik_tekrar_yok():
    k = KuralTabanli(paket_kur(selamlama=SELAMLAR), tohum=42)
    soylenenler = [k.cevapla("Merhaba").metin for _ in range(40)]
    assert set(soylenenler) == set(SELAMLAR)                   # hepsi bir kez de olsa söylenir
    assert all(a != b for a, b in zip(soylenenler, soylenenler[1:]))
    assert k.cevapla("selam").jest == "selam"


def test_ayni_tohum_ayni_sira():
    a = KuralTabanli(paket_kur(selamlama=SELAMLAR), tohum=7)
    b = KuralTabanli(paket_kur(selamlama=SELAMLAR), tohum=7)
    assert [a.cevapla("merhaba").metin for _ in range(6)] == [b.cevapla("merhaba").metin for _ in range(6)]


def test_iki_secenekte_sirayla_degisir():
    s = VaryantSecici(tohum=3)
    secilen = [s.sec("x", ["bir", "iki"]) for _ in range(6)]
    assert secilen in (["bir", "iki"] * 3, ["iki", "bir"] * 3)


def test_paket_kaliplari_ve_yer_tutucular():
    p = paket_kur(kaliplar={"kimsin": ["Ben {ad}, {rol}.", "Adım {ad}; {kurum} için buradayım."],
                            "tesekkur": "Ne demek!"})
    k = KuralTabanli(p, "Lale", tohum=0)
    kimsin = {k.cevapla("Sen kimsin?").metin for _ in range(6)}
    assert kimsin == {"Ben Lale, karşılama robotu.", "Adım Lale; Deneme Okulu için buradayım."}
    assert k.cevapla("teşekkürler").metin == "Ne demek!"
    assert k.cevapla("hoşça kal").metin == "Hoşça kalın, iyi günler!"     # yazılmayan kalıp koddaki


def test_ornek_paketlerde_selamlama_varyantlari():
    for ad in ("universite", "tesis"):
        p = IcerikPaketi.dosyadan(os.path.join(KOD, "icerik", ad + ".yaml"))
        assert 4 <= len(p.selamlamalar) <= 5
        k = KuralTabanli(p, "Lale", tohum=5)
        for _ in range(10):
            metin = k.cevapla("Merhaba").metin
            assert metin in [s.replace("{ad}", "Lale") for s in p.selamlamalar]
            assert "{" not in metin


def test_kontrol_liste_selamlama_ve_kaliplar():
    temel = 'kurum: "Okul"\nkonular:\n  - baslik: Kantin\n    anahtarlar: [kantin]\n    cevap: "Altta."\n'
    assert denetle(temel + 'selamlama: ["Merhaba!", "Selam!"]\n').hatalar == []
    assert denetle(temel + "selamlama: []\n").hatalar == ["'selamlama' alanı yok ya da boş"]
    rapor = denetle(temel + 'selamlama: "Merhaba"\nkaliplar:\n  tesekkur: []\n  dans: "Olmaz"\n')
    assert any("tesekkur" in h for h in rapor.hatalar)
    assert any("dans" in u for u in rapor.uyarilar)
