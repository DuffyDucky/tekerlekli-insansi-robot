# Konum test turu: sahte kaynaklarla bölge bölge ölçüm, CSV satırları, kaynak / bölge doğruluk tabloları.

import csv

from olcum import konum_turu as kt
from robot.gunluk import AYIRAC, KODLAMA
from robot.konum.birlestirici import KonumYoneticisi
from robot.konum.bolgeler import veriden
from robot.konum.kaynak import KonumKaynagi, KonumTahmini

BOLGELER = veriden({"bolgeler": {"giris-holu": {"ad": "Giriş holü"}, "kantin-onu": {"ad": "Kantin önü"},
                                 "bahce": {"ad": "Bahçe"}}})


class Yer:
    """Testin 'robotu götürdüğü' yer; sahte kaynaklar buna bakar."""
    bolge = None


class SahteKaynak(KonumKaynagi):
    """yanilma: {gerçek bölge: söylenecek bölge}; sessiz: hiçbir şey söylemez."""

    def __init__(self, ad, agirlik=1.0, yanilma=None, sessiz=False, guven=0.8):
        super().__init__(agirlik, 1.0)
        self.ad = ad
        self.yanilma = yanilma or {}
        self.sessiz = sessiz
        self.guven = guven

    def olc(self):
        if self.sessiz:
            return None
        return KonumTahmini(bolge=self.yanilma.get(Yer.bolge, Yer.bolge), guven=self.guven, kaynak=self.ad)


def yonetici_kur():
    kaynaklar = [SahteKaynak("wifi", yanilma={"bahce": "kantin-onu"}),     # bahçede yanılır
                 SahteKaynak("ble", sessiz=True),                          # hiç beacon yok
                 SahteKaynak("aruco", agirlik=2.0, guven=0.9, yanilma={"kantin-onu": None})]
    return KonumYoneticisi(kaynaklar, bolgeler=BOLGELER)


def sor_ve_gotur(cevaplar=None):
    """input() yerine: soru metnindeki bölge kimliğini Yer'e yazar (robotu oraya götürmüş gibi)."""
    cevaplar = list(cevaplar or [])

    def sor(metin):
        for kimlik in BOLGELER.adlar():
            if f"({kimlik})" in metin:
                Yer.bolge = kimlik
        return cevaplar.pop(0) if cevaplar else ""
    return sor


def test_tur_satirlari_ve_dogruluk():
    satirlar = kt.tur(yonetici_kur(), adet=2, aralik=0, sor=sor_ve_gotur(), uyu=lambda s: None,
                      yazdir=lambda *a: None)
    assert len(satirlar) == 3 * 2 * 4                         # 3 bölge x 2 tarama x (3 kaynak + birleşik)
    bahce = [s for s in satirlar if s["bolge"] == "bahce"]
    wifi = [s for s in bahce if s["kaynak"] == "wifi"]
    assert {s["tahmin"] for s in wifi} == {"kantin-onu"} and not any(s["dogru"] for s in wifi)
    birlesik = [s for s in bahce if s["kaynak"] == kt.BIRLESIK]
    assert all(s["tahmin"] == "bahce" and s["dogru"] == 1 for s in birlesik)   # ArUco (2x) wifi'ı yener
    kantin = [s for s in satirlar if s["bolge"] == "kantin-onu" and s["kaynak"] == kt.BIRLESIK]
    assert all(s["tahmin"] == "kantin-onu" for s in kantin)                    # ArUco görmedi, wifi doğru
    assert all(s["tahmin"] == "" and s["guven"] == 0 for s in satirlar if s["kaynak"] == "ble")


def test_yeni_bolgede_eski_tahmin_karismaz():
    y = yonetici_kur()
    y.kaynaklar["aruco"].yanilma = {"giris-holu": "giris-holu", "kantin-onu": None, "bahce": None}
    y.kaynaklar["wifi"].sessiz = True
    satirlar = kt.tur(y, adet=1, aralik=0, sor=sor_ve_gotur(), uyu=lambda s: None, yazdir=lambda *a: None)
    kantin = [s for s in satirlar if s["bolge"] == "kantin-onu" and s["kaynak"] == kt.BIRLESIK]
    assert kantin[0]["tahmin"] == ""                       # giriş holünün ArUco'su buraya taşınmadı


def test_atla_ve_erken_bitir():
    def sor(metin):
        if "(kantin-onu)" in metin:
            raise KeyboardInterrupt
        Yer.bolge = "giris-holu"
        return "a" if "(bahce)" in metin else ""

    satirlar = kt.tur(yonetici_kur(), adet=1, aralik=0, sor=sor, uyu=lambda s: None, yazdir=lambda *a: None)
    assert {s["bolge"] for s in satirlar} == {"giris-holu"}


def test_tablolar_ve_hedef():
    satirlar = kt.tur(yonetici_kur(), adet=3, aralik=0, sor=sor_ve_gotur(), uyu=lambda s: None,
                      yazdir=lambda *a: None)
    kaynak = "\n".join(kt.kaynak_tablosu(satirlar))
    assert "| wifi | 9 | 6 | %66,7 | 0 | 0,80 |" in kaynak
    assert "| ble | 9 | 0 | %0,0 | 9 | 0,00 |" in kaynak
    assert kaynak.strip().splitlines()[-1].startswith("| **birlesik** | 9 | 9 | %100,0")
    bolge = "\n".join(kt.bolge_tablosu(satirlar))
    assert "| bahce | 3 | 3 | %100,0 | - |" in bolge
    assert "SAĞLANDI" in kt.hedef_satiri(satirlar) and "3 bölge ölçüldü" in kt.hedef_satiri(satirlar)


def test_main_dosyalari_yazar(tmp_path, monkeypatch):
    monkeypatch.setattr(kt, "yonetici_kur", lambda ayar, kaynaklar: yonetici_kur())
    monkeypatch.setattr("builtins.input", sor_ve_gotur())
    monkeypatch.setattr(kt.time, "sleep", lambda s: None)
    kod = kt.main(["--etiket", "deneme 1", "--adet", "2", "--kaynaklar", "wifi,ble,aruco",
                   "--sonuc-klasoru", str(tmp_path)])
    assert kod == 0
    with open(tmp_path / "konum-turu-deneme_1.csv", encoding=KODLAMA, newline="") as dosya:
        satirlar = list(csv.DictReader(dosya, delimiter=AYIRAC))
    assert list(satirlar[0]) == kt.ALANLAR and len(satirlar) == 24
    assert "## Kaynak başına doğruluk" in (tmp_path / "konum-turu-deneme_1.md").read_text(encoding="utf-8")


def test_bilinmeyen_kaynak_cikis_2(tmp_path):
    assert kt.main(["--kaynaklar", "wifi,uydu", "--sonuc-klasoru", str(tmp_path)]) == 2


def test_varsayilan_kaynaklar_ayardan():
    assert kt.varsayilan_kaynaklar({"konum": {"wifi": {"etkin": True}, "gps": {"etkin": False},
                                              "ble": {"etkin": False}, "aruco": {"etkin": True}}}) == ["wifi", "aruco"]
