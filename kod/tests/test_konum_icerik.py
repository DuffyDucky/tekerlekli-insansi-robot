# Konumun konuşmaya bağlanması: bölgeye göre tarif ve işaret yönü (icerik, dil), seri jest "yon" alanı,
# ana.tek_tur'da bölgeli cevap, günlükte bolge/konum_kaynak sütunları, icerik_kontrol'ün yeni denetimleri.

import csv
from types import SimpleNamespace

import ana
import icerik_kontrol
from robot.dil import BulutDilModeli, Cevap, KuralTabanli, sistem_istemi
from robot.gunluk import ALANLAR, AYIRAC, Gunluk
from robot.icerik import IcerikPaketi, Kayit
from robot.seri import SahteSeri
from test_ana import robot_kur
from test_icerik_kontrol import SAGLAM

YERLI = {
    "kurum": "Deneme Okulu",
    "selamlama": "Merhaba!",
    "yerler": [
        {"ad": "Kantin", "tarif": "Kantin giriş katında.",
         "tarifler": {"giris-holu": "Kantin buradan solda.", "bahce": "Kantin binanın içinde, kapıdan girin."},
         "yon": "ileri", "yonler": {"giris-holu": "sol"}},
        {"ad": "Lavabo", "tarif": "Lavabo her katta.", "yon": "..."},
    ],
}


def yerli_paket():
    return IcerikPaketi(YERLI, esik=3)


class SahteKonum:
    def __init__(self, bolge, kaynak="wifi"):
        self.bolge, self.kaynak = bolge, kaynak

    def durum(self):
        return {"bolge": self.bolge, "kaynak": self.kaynak, "guven": 0.9}


def test_tarif_ve_yon_secimi():
    k = Kayit("Kantin", "genel", tarifler={"a": "a'dan"}, yon="ileri", yonler={"a": "sol", "b": "yamuk"})
    assert k.tarif_sec("a") == "a'dan" and k.tarif_sec("z") == "genel" and k.tarif_sec(None) == "genel"
    assert k.yon_sec("a") == "sol" and k.yon_sec(None) == "ileri"
    assert k.yon_sec("b") is None                       # geçersiz yön: yönsüz işaret
    assert Kayit("x", "y", yon="...").yon_sec() is None   # "..." yer tutucu


def test_kural_tabanli_bolgeye_gore_cevap():
    dil = KuralTabanli(yerli_paket())
    c = dil.cevapla("Kantin nerede?", bolge="giris-holu")
    assert (c.metin, c.jest, c.yon) == ("Kantin buradan solda.", "isaret", "sol")
    c = dil.cevapla("Kantin nerede?", bolge="bahce")
    assert (c.metin, c.yon) == ("Kantin binanın içinde, kapıdan girin.", "ileri")
    c = dil.cevapla("Kantin nerede?")
    assert (c.metin, c.yon) == ("Kantin giriş katında.", "ileri")
    assert dil.cevapla("Lavabo nerede?").yon is None
    assert Cevap("x").yon is None


def test_bulut_istemine_bolge_eklenir():
    istem = sistem_istemi(yerli_paket(), "Lale", "kantin nerede", "giris-holu")
    assert "Robot şu an: giris-holu" in istem and "Kantin buradan solda." in istem
    assert "Robot şu an" not in sistem_istemi(yerli_paket(), "Lale", "kantin nerede")
    cagrilar = []

    def create(**kw):
        cagrilar.append(kw)
        return SimpleNamespace(content=[SimpleNamespace(text="Kantin hemen solunuzda.")])
    istemci = SimpleNamespace(messages=SimpleNamespace(create=create))
    c = BulutDilModeli("anthropic", "m", yerli_paket(), istemci=istemci).cevapla("Kantin nerede?", bolge="giris-holu")
    assert "Robot şu an: giris-holu" in cagrilar[0]["system"]
    assert (c.metin, c.jest, c.yon) == ("Kantin hemen solunuzda.", "isaret", "sol")


def test_seri_jest_yon():
    s = SahteSeri()
    s.jest("isaret", "sol")
    s.jest("selam")
    assert s.gonderilenler == ['{"k":"jest","ad":"isaret","yon":"sol"}', '{"k":"jest","ad":"selam"}']


def test_tek_tur_bolgeli_cevap_ve_yonlu_isaret(capsys):
    robot = robot_kur(yerli_paket(), ["Kantin nerede?", "Merhaba"])
    robot.konum = SahteKonum("giris-holu")
    ana.tek_tur(robot)
    assert robot.seri.gonderilenler == ['{"k":"jest","ad":"isaret","yon":"sol"}']
    assert "Robot: Kantin buradan solda." in capsys.readouterr().out
    ana.tek_tur(robot)                                  # selam jesti yön almaz (eski biçim)
    assert robot.seri.gonderilenler[-1] == '{"k":"jest","ad":"selam"}'


def test_tek_tur_konumsuz_ve_konum_hatasi(capsys):
    robot = robot_kur(yerli_paket(), ["Lavabo nerede?", "Kantin nerede?"])
    ana.tek_tur(robot)                                  # konum yok, yön "...": eski biçim
    assert robot.seri.gonderilenler == ['{"k":"jest","ad":"isaret"}']

    class BozukKonum:
        def durum(self):
            raise RuntimeError("bozuk")
    robot.konum = BozukKonum()
    ana.tek_tur(robot)                                  # konum hata verse de tur tamamlanır, genel tarif
    assert "Robot: Kantin giriş katında." in capsys.readouterr().out
    assert robot.seri.gonderilenler[-1] == '{"k":"jest","ad":"isaret","yon":"ileri"}'


def satirlar(yol):
    with open(yol, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=AYIRAC))


def test_gunlukte_bolge_sutunlari(tmp_path):
    robot = robot_kur(yerli_paket(), ["Kantin nerede?", None])
    robot.konum = SahteKonum("giris-holu", "wifi+aruco")
    robot.gunluk = Gunluk(str(tmp_path))
    ana.tek_tur(robot)
    ana.tek_tur(robot)                                  # duyulmayan soru da bölgeyle yazılır
    s = satirlar(robot.gunluk.dosya_yolu())
    assert ALANLAR[-2:] == ["bolge", "konum_kaynak"] and list(s[0]) == ALANLAR
    assert (s[0]["bolge"], s[0]["konum_kaynak"]) == ("giris-holu", "wifi+aruco")
    assert s[1]["taninan"] == "" and s[1]["bolge"] == "giris-holu"


def test_eski_baslikli_gunluk_ayri_dosyaya(tmp_path, capsys):
    g = Gunluk(str(tmp_path))
    eski = g.dosya_yolu()
    with open(eski, "w", encoding="utf-8-sig", newline="") as f:
        f.write(AYIRAC.join(ALANLAR[:-2]) + "\r\n")      # konum sütunları olmayan eski sürüm
    g.yaz({"zaman": "x", "bolge": "bahce"})
    yeni = g.dosya_yolu()
    assert yeni.endswith("_2.csv") and satirlar(yeni)[0]["bolge"] == "bahce"
    assert "eski sütunlarla" in capsys.readouterr().out
    assert open(eski, encoding="utf-8-sig").read().count("\n") == 1   # eski dosyaya dokunulmadı


YERLI_METIN = SAGLAM.replace("sss:\n", """\
  - ad: Kafe
    tarif: "Kafe giriş katında."
    tarifler: {giris-holu: "Buradan solda.", uzay: "Ayda."}
    yon: yukari
    yonler: {giris-holu: sol, bahce: "..."}
sss:
""")


def test_icerik_kontrol_yon_ve_bolge_adlari():
    hatalar = icerik_kontrol.denetle(YERLI_METIN, {"giris-holu", "bahce"}).hatalar
    assert any("geçersiz yön 'yukari'" in h for h in hatalar)
    assert any("'uzay' bölgesi bolgeler.yaml'da yok" in h for h in hatalar)
    assert not any("bahce" in h or "giris-holu" in h for h in hatalar)   # "..." yön hata değil
    rapor = icerik_kontrol.denetle(YERLI_METIN)          # bolgeler.yaml yok: yalnız uyarı
    assert not any("uzay" in h for h in rapor.hatalar)
    assert any("bolgeler.yaml yok" in u for u in rapor.uyarilar)


def test_icerik_kontrol_tarifler_bicimi():
    metin = SAGLAM.replace('    tarif: "Kütüphane ... katında."',
                           '    tarif: "Kütüphane ... katında."\n    tarifler: [a, b]')
    assert any("bölge -> değer" in h for h in icerik_kontrol.denetle(metin, set()).hatalar)


def test_ornek_paket_bolgeleri_tutarli():
    # universite.yaml'daki tarifler/yonler bölge adları konum/bolgeler.yaml'da var
    bolge_adlari = icerik_kontrol.bolge_adlarini_oku()
    with open(ana.paket_yolu("universite"), encoding="utf-8") as f:
        rapor = icerik_kontrol.denetle(f.read(), bolge_adlari)
    assert bolge_adlari and rapor.hatalar == []
    paket = IcerikPaketi.dosyadan(ana.paket_yolu("universite"))
    kantin = next(k for k in paket.kayitlar if k.baslik == "Kantin")
    assert kantin.tarifler and kantin.tarif_sec("giris-holu") != kantin.cevap


def test_konum_secenegi_ve_kapali_konum():
    sec = ana.secenekleri_oku(["--yuzsuz", "--gelistirici", "--konum", "giris-holu"])
    ayar = ana.secenekleri_uygula(ana.ayarlari_oku(sec.ayar), sec)
    assert ayar["konum"]["elle"]["bolge"] == "giris-holu" and ayar["konum"]["elle"]["etkin"] is True
    ayar["konum"].update({"wifi": {"etkin": False}, "gps": {"etkin": False}, "ble": {"etkin": False}})
    robot = ana.bilesenleri_kur(ayar)
    robot.konum.bir_kez()
    assert robot.konum.durum()["bolge"] == "giris-holu"
    ayar["konum"]["etkin"] = False
    assert ana.konum_kur(ayar, SahteSeri()) is None
