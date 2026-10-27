# Konum paketi: Wi-Fi parmak izi, GPS (NMEA + geofence), BLE, odometri, elle kaynak ve birleştirme kuralı.
# Donanım yok: taramalar, NMEA satırları ve ESP32 mesajları sahte verilir.

import math
import time

import pytest

from robot.konum.ble import BleKaynagi, en_guclu, rssi_guveni
from robot.konum.birlestirici import KonumYoneticisi, ayar_birlestir
from robot.konum.bolgeler import Bolgeler, veriden
from robot.konum.elle import ElleKaynak
from robot.konum.gps import GpsKaynagi, bolge_bul, haversine, hdop_guveni, nmea_ayristir
from robot.konum.kaynak import KonumKaynagi, KonumTahmini
from robot.konum.odometri import Odometri
from robot.konum.wifi import (WifiKaynagi, eslestir, netsh_ayristir, nmcli_ayristir, ortalama_iz, uzaklik,
                              veritabani_oku)

# ---------- Wi-Fi ----------

NMCLI = "AA\\:BB\\:CC\\:00\\:00\\:01:72:6\nAA\\:BB\\:CC\\:00\\:00\\:02:40:11\nbozuk\n"

NETSH = """\
SSID 1 : eduroam
    Network type            : Infrastructure
    BSSID 1                 : 44:12:44:8b:3a:c0
         Signal             : 90%
         Channel            : 1
    BSSID 2                 : 44:12:44:8D:C3:80
         Sinyal             : %65
SSID 2 :
    BSSID 1                 : 34:fc:b9:08:69:01
         Signal             : 22%
"""


def test_nmcli_kacisli_bssid():
    assert nmcli_ayristir(NMCLI) == {"aa:bb:cc:00:00:01": 72.0, "aa:bb:cc:00:00:02": 40.0}


def test_netsh_turkce_ve_ingilizce():
    # Türkçe Windows '%65' yazar; BSSID küçük harfe çevrilir
    assert netsh_ayristir(NETSH) == {"44:12:44:8b:3a:c0": 90.0, "44:12:44:8d:c3:80": 65.0,
                                     "34:fc:b9:08:69:01": 22.0}


VERITABANI = {
    "giris-holu": [{"a": 80, "b": 30}, {"a": 76, "b": 34, "c": 10}],
    "kantin-onu": [{"a": 20, "b": 70, "c": 60}],
}


def test_ortalama_ve_uzaklik():
    iz = ortalama_iz(VERITABANI["giris-holu"])
    assert iz == {"a": 78, "b": 32, "c": 5}           # görünmeyen c bir ölçümde 0 sayıldı
    assert uzaklik({"a": 3}, {"b": 4}) == 5.0           # görünmeyen = 0


def test_parmak_izi_en_yakin_bolge():
    bolge, guven, uzakliklar = eslestir({"a": 79, "b": 31}, VERITABANI)
    assert bolge == "giris-holu" and guven > 0.8
    assert uzakliklar["giris-holu"] < uzakliklar["kantin-onu"]
    assert eslestir({"a": 25, "b": 68, "c": 55}, VERITABANI)[0] == "kantin-onu"


def test_iki_bolge_benzerse_guven_duser():
    bolge, guven, _ = eslestir({"a": 50, "b": 50, "c": 32}, VERITABANI)   # ikisinin ortası
    assert guven < 0.3


def test_ortak_bssid_yoksa_none():
    assert eslestir({"zz": 90}, VERITABANI)[0] is None
    assert eslestir({"a": 80}, {})[0] is None


def test_wifi_kaynagi_kaydet_ve_oku(tmp_path):
    yol = tmp_path / "parmak_izi.yaml"
    olcumler = iter([{"a": 80, "b": 30}, {"a": 78, "b": 33}, {"a": 20, "b": 70}, {"a": 79, "b": 31}])
    wifi = WifiKaynagi(veritabani_yolu=str(yol), tarayici=lambda: next(olcumler))
    wifi.baslat()                                       # dosya yok: boş veritabanı, uyarı
    assert wifi.oku() is None                           # kayıt yokken tarama bile yapılmaz
    assert wifi.kaydet("giris-holu", adet=2, bekleme=0, yazdir=lambda m: None) == 2
    assert wifi.kaydet("kantin-onu", adet=1, bekleme=0, yazdir=lambda m: None) == 1
    assert veritabani_oku(str(yol))["giris-holu"] == [{"a": 80, "b": 30}, {"a": 78, "b": 33}]
    assert yol.read_text(encoding="utf-8").startswith("# Wi-Fi parmak izi")
    tahmin = wifi.oku()
    assert tahmin.bolge == "giris-holu" and tahmin.kaynak == "wifi"


def test_tarama_komutu_yoksa_pasif(tmp_path):
    yol = tmp_path / "pi.yaml"
    yol.write_text("giris-holu:\n- {a: 80}\n", encoding="utf-8")

    def yok():
        raise FileNotFoundError("nmcli")
    wifi = WifiKaynagi(veritabani_yolu=str(yol), tarayici=yok)
    wifi.baslat()
    assert wifi.oku() is None and not wifi.etkin


# ---------- GPS ----------

def nmea(govde):
    toplam = 0
    for harf in govde:
        toplam ^= ord(harf)
    return f"${govde}*{toplam:02X}"


BOLGELER = veriden({
    "bolgeler": {
        "bahce": {"ad": "Bahçe", "gps": {"lat": 48.1173, "lon": 11.5167, "yaricap_m": 30}, "yerel": {"x": 5, "y": 7}},
        "giris-holu": {"ad": "Giriş holü", "gps": {"lat": None, "lon": None, "yaricap_m": None}},
    },
    "isaretler": {7: "giris-holu", "8": {"bolge": "bahce", "x": 1.5, "y": 2.0, "yon": 90}},
    "beaconlar": {"aa:bb:cc:dd:ee:ff": "bahce", "Lale-Kantin": "kantin-onu"},
})


def test_haversine_bir_derece_enlem():
    assert haversine(38.0, 27.0, 39.0, 27.0) == pytest.approx(111195, rel=1e-3)
    assert haversine(38.6, 27.4, 38.6, 27.4) == 0


def test_gga_ve_rmc_ayristirma():
    gga = nmea_ayristir(nmea("GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,"))
    assert gga["fix"] and gga["uydu"] == 8 and gga["hdop"] == 0.9
    assert gga["lat"] == pytest.approx(48.1173) and gga["lon"] == pytest.approx(11.516667)
    rmc = nmea_ayristir(nmea("GNRMC,123519,A,3836.000,N,02724.000,E,0.0,0.0,271026,,"))
    assert rmc["fix"] and rmc["lat"] == pytest.approx(38.6)
    guney = nmea_ayristir(nmea("GPGGA,1,3000.000,S,01000.000,W,1,05,1.0,0,M,0,M,,"))
    assert guney["lat"] == -30.0 and guney["lon"] == -10.0


def test_fix_yok_ve_bozuk_saglama():
    assert nmea_ayristir(nmea("GPGGA,123519,,,,,0,00,,,M,,M,,"))["fix"] is False
    assert nmea_ayristir("$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*00") is None
    assert nmea_ayristir("çöp") is None


def test_geofence_ve_hdop():
    bolge, mesafe = bolge_bul(48.1174, 11.5168, BOLGELER)
    assert bolge.kimlik == "bahce" and mesafe < 30
    assert bolge_bul(48.2, 11.5167, BOLGELER) == (None, None)       # ~9 km uzak
    assert hdop_guveni(0.9) == 1.0 and hdop_guveni(3.0) == pytest.approx(0.5)


def test_gps_kaynagi_sahte_satirlarla():
    satirlar = iter([nmea("GPGGA,1,,,,,0,00,,,M,,M,,"),
                     nmea("GPGGA,123519,4807.038,N,01131.000,E,1,08,3.0,545.4,M,46.9,M,,")])
    gps = GpsKaynagi(BOLGELER, satir_kaynagi=lambda: next(satirlar, None))
    gps.baslat()
    t = gps.oku()
    assert t.bolge == "bahce" and t.guven == pytest.approx(0.5) and (t.x, t.y) == (5, 7)
    assert gps.oku() is None                            # satır bitti: fix yok


def test_gps_port_bossa_pasif():
    gps = GpsKaynagi(BOLGELER, port="")
    gps.baslat()
    assert not gps.etkin and gps.oku() is None


# ---------- BLE ----------

def test_ble_en_guclu_beacon():
    gorulen = [("AA:BB:CC:DD:EE:FF", "", -80), ("11:22:33:44:55:66", "Lale-Kantin", -60), ("00:00", "x", -30)]
    assert en_guclu(gorulen, BOLGELER.beaconlar) == ("kantin-onu", -60)    # bilinmeyen -30 yoksayıldı
    ble = BleKaynagi(BOLGELER, tarayici=lambda: gorulen)
    ble.baslat()
    t = ble.oku()
    assert t.bolge == "kantin-onu" and t.guven == pytest.approx(rssi_guveni(-60))
    assert rssi_guveni(-40) == 1.0 and rssi_guveni(-120) == 0.1


# ---------- odometri ----------

def odo(sol, sag, yaw=None):
    return {"k": "odo", "sol": sol, "sag": sag, "yaw": yaw, "ms": 0}


def kolay_odometri():
    # teker çevresi = pi * (1/pi) = 1 m, 1000 tik/tur -> 1 tik = 1 mm; iz 0.5 m
    return Odometri(tik_tur=1000, teker_cap_m=1 / math.pi, iz_genislik_m=0.5)


def test_odometri_duz_bir_metre():
    o = kolay_odometri()
    assert o.oku() is None                              # mesaj gelmeden tahmin yok
    for i in range(11):
        o.isle(odo(i * 100, i * 100))
    t = o.oku()
    assert t.x == pytest.approx(1.0) and t.y == pytest.approx(0.0) and t.yon_derece == pytest.approx(0.0)
    assert t.bolge is None and t.guven < 1.0


def test_odometri_yerinde_90_derece_sonra_ileri():
    o = kolay_odometri()
    yay = 0.5 * math.pi / 2 / 2                         # her teker iz/2 yarıçaplı çeyrek çember: 0.3927 m
    adim = yay * 1000 / 10
    for i in range(11):
        o.isle(odo(round(-i * adim), round(i * adim)))   # sol geri, sağ ileri = sola dönüş
    assert o.yon == pytest.approx(90.0, abs=0.5)
    assert math.hypot(o.x, o.y) < 0.01
    sol0, sag0 = o.onceki
    for i in range(1, 11):
        o.isle(odo(sol0 + i * 100, sag0 + i * 100))
    assert o.x == pytest.approx(0.0, abs=0.02) and o.y == pytest.approx(1.0, abs=0.01)


def test_odometri_imu_yawi_ve_duzeltme():
    o = kolay_odometri()
    o.isle(odo(0, 0, yaw=200.0))                        # ilk yaw bizim 0°'mize hizalanır
    o.isle(odo(500, 500, yaw=200.0))
    o.isle(odo(1000, 1000, yaw=290.0))                  # IMU: 90° sola döndü (enkoder dönüş görmedi)
    assert o.yon == pytest.approx(90.0)
    o.duzelt(3.0, 4.0, 180.0)
    assert (o.x, o.y, o.yon, o.yol_m) == (3.0, 4.0, 180.0, 0.0)
    o.isle(odo(1100, 1100, yaw=290.0))                  # düzeltmeden sonra yaw yeniden hizalanır
    assert o.x == pytest.approx(2.9) and o.yon == pytest.approx(180.0)


def test_odometri_sifirlanan_sayac_ve_baska_mesaj():
    o = kolay_odometri()
    o.isle(odo(5000, 5000))
    o.isle(odo(0, 0))                                   # ESP32 odo_sifirla: büyük geri sıçrama sayılmaz
    assert o.x == 0.0
    assert o.isle({"ok": True, "k": "jest"}) is False and o.isle({"k": "odo", "sol": "x"}) is False


# ---------- elle ----------

def test_elle_komut_satiri_ve_dosya(tmp_path):
    dosya = tmp_path / "bolge.txt"
    e = ElleKaynak("giris-holu", str(dosya), bilinen_bolgeler=["giris-holu", "bahce"])
    t = e.oku()
    assert t.bolge == "giris-holu" and t.guven == 1.0
    dosya.write_text("bahce\n", encoding="utf-8")       # açılıştan sonra yazıldı: dosya kazanır
    assert e.oku().bolge == "bahce"
    dosya.write_text("", encoding="utf-8")
    assert e.oku().bolge == "giris-holu"                # boş dosya: komut satırına dön
    assert ElleKaynak(None, str(tmp_path / "yok.txt")).oku() is None


def test_elle_eski_dosya_komut_satirini_ezmez(tmp_path):
    dosya = tmp_path / "bolge.txt"
    dosya.write_text("bahce", encoding="utf-8")
    eski = time.time() - 3600
    import os
    os.utime(dosya, (eski, eski))
    assert ElleKaynak("giris-holu", str(dosya)).oku().bolge == "giris-holu"
    assert ElleKaynak(None, str(dosya)).oku().bolge == "bahce"


# ---------- birleştirme ----------

class Sabit(KonumKaynagi):
    def __init__(self, ad, agirlik=1.0, tahmin=None, aralik=0.05):
        super().__init__(agirlik, aralik)
        self.ad = ad
        self.tahmin = tahmin

    def olc(self):
        return self.tahmin


def tahmin(bolge, guven, zaman, kaynak, **kw):
    return KonumTahmini(bolge=bolge, guven=guven, zaman=zaman, kaynak=kaynak, **kw)


def yonetici(*kaynaklar, **kw):
    return KonumYoneticisi(list(kaynaklar), tazelik_saniye=30, **kw)


def test_puan_agirlik_guven_tazelik():
    wifi, ble = Sabit("wifi"), Sabit("ble")
    y = yonetici(wifi, ble)
    y.tahmin_ekle(wifi, tahmin("giris-holu", 0.6, 100.0, "wifi"))
    y.tahmin_ekle(ble, tahmin("kantin-onu", 0.5, 100.0, "ble"))
    assert y.birlestir(simdi=100.0)[0] == "giris-holu"           # 0.6 > 0.5
    assert y.birlestir(simdi=120.0)[0] == "giris-holu"           # ikisi de aynı yaşta: sıra değişmez
    y.tahmin_ekle(ble, tahmin("kantin-onu", 0.5, 120.0, "ble"))  # ble tazelendi, wifi 20 s eski: 0.2 < 0.5
    bolge, guven, destek = y.birlestir(simdi=120.0)
    assert bolge == "kantin-onu" and destek == ["ble"] and 0 < guven < 0.5


def test_ayni_bolgeyi_soyleyenler_toplanir():
    wifi, ble, aruco = Sabit("wifi"), Sabit("ble"), Sabit("aruco", agirlik=2.0)
    y = yonetici(wifi, ble, aruco)
    y.tahmin_ekle(wifi, tahmin("A", 0.5, 10.0, "wifi"))
    y.tahmin_ekle(ble, tahmin("A", 0.4, 10.0, "ble"))
    y.tahmin_ekle(aruco, tahmin("B", 0.4, 10.0, "aruco"))        # 2 x 0.4 = 0.8 < 0.5 + 0.4
    bolge, guven, destek = y.birlestir(simdi=10.0)
    assert bolge == "A" and destek == ["ble", "wifi"]
    assert guven == pytest.approx(min(1, 0.9) * 0.9 / 1.7, abs=1e-3)


def test_son_bilinen_bolge_korunur():
    wifi = Sabit("wifi")
    y = yonetici(wifi, son_bilinen_bolge="giris-holu")
    assert y.birlestir(simdi=0.0) == ("giris-holu", 0.0, ["son-bilinen"])   # ayardan başlangıç
    y.tahmin_ekle(wifi, tahmin("bahce", 0.9, 0.0, "wifi"))
    assert y.birlestir(simdi=1.0)[0] == "bahce"
    assert y.birlestir(simdi=500.0) == ("bahce", 0.0, ["son-bilinen"])      # eskidi ama bölge korunur
    assert yonetici(Sabit("wifi")).birlestir(simdi=0.0) == (None, 0.0, [])


def test_elle_eskimez_ve_kaldirilinca_silinir():
    elle, wifi = ElleKaynak("bahce", None), Sabit("wifi")
    elle.agirlik = 3.0
    y = yonetici(elle, wifi)
    y.tahmin_ekle(elle, elle.oku())
    y.tahmin_ekle(wifi, tahmin("giris-holu", 1.0, time.time() + 1000, "wifi"))
    assert y.birlestir(simdi=time.time() + 1000)[0] == "bahce"   # elle 1000 s sonra da tam puan
    y.tahmin_ekle(elle, None)                                     # elle seçim kaldırıldı
    assert y.birlestir(simdi=time.time() + 1000)[0] == "giris-holu"


def test_aruco_odometriyi_duzeltir_gps_yalniz_uzaksa():
    o = kolay_odometri()
    o.isle(odo(0, 0))
    aruco, gps = Sabit("aruco"), Sabit("gps")
    y = KonumYoneticisi([o, aruco, gps], tazelik_saniye=30, gps_duzeltme_m=10)
    y.tahmin_ekle(gps, tahmin("bahce", 1.0, 0.0, "gps", x=5.0, y=0.0))    # 5 m < 10 m: düzeltme yok
    assert (o.x, o.y) == (0.0, 0.0)
    y.tahmin_ekle(gps, tahmin("bahce", 1.0, 1.0, "gps", x=50.0, y=0.0))   # 50 m: GPS'e çekilir
    assert (o.x, o.y) == (50.0, 0.0)
    y.tahmin_ekle(aruco, tahmin("giris-holu", 1.0, 2.0, "aruco", x=1.0, y=2.0, yon_derece=90.0))
    assert (o.x, o.y, o.yon) == (1.0, 2.0, 90.0)
    y.tahmin_ekle(gps, tahmin("bahce", 1.0, 3.0, "gps", x=80.0, y=0.0))   # ArUco taze: GPS dokunmaz
    assert (o.x, o.y) == (1.0, 2.0)
    d = y.durum(simdi=3.0)
    assert (d["x"], d["y"], d["yon"]) == (1.0, 2.0, 90.0)
    assert set(d) == {"bolge", "bolge_adi", "guven", "kaynak", "kaynaklar", "x", "y", "yon"}


def test_durum_pasif_kaynagi_gosterir():
    bozuk = Sabit("ble")
    bozuk.pasif_yap("bleak yok")
    y = yonetici(bozuk, bolgeler=BOLGELER)
    d = y.durum(simdi=0.0)
    assert d["kaynaklar"]["ble"] == {"pasif": "bleak yok"} and d["bolge"] is None


def test_hata_veren_kaynak_robotu_dusurmez():
    class Bozuk(KonumKaynagi):
        ad = "bozuk"

        def olc(self):
            raise RuntimeError("donanım koptu")
    assert Bozuk().oku() is None


def test_is_parcaciklari_ve_seri_odometri():
    class SahteSeri:
        def __init__(self):
            self.satirlar = [odo(0, 0), {"ok": True, "k": "jest"}, odo(500, 500)]
            self.gonderilenler = []

        def satir_oku(self):
            return self.satirlar.pop(0) if self.satirlar else None

        def gonder(self, komut):
            self.gonderilenler.append(komut)

    seri = SahteSeri()
    o = kolay_odometri()
    wifi = Sabit("wifi", tahmin=KonumTahmini("bahce", guven=0.9, kaynak="wifi"))
    y = KonumYoneticisi([wifi, o], seri=seri)
    y.baslat()
    bitis = time.time() + 2
    while time.time() < bitis and (o.mesaj_sayisi < 2 or "wifi" not in y.son_tahminler):
        time.sleep(0.02)
    d = y.durum()
    y.kapat()
    assert d["bolge"] == "bahce" and d["x"] == pytest.approx(0.5)
    y.odometri_sifirla()
    assert seri.gonderilenler == [{"k": "odo_sifirla"}] and o.x == 0.0


def test_ayarlardan_kurulum_ve_elle_bolge(tmp_path):
    ayar = {"wifi": {"etkin": False}, "gps": {"etkin": False}, "ble": {"etkin": False},
            "elle": {"dosya": str(tmp_path / "bolge.txt")}, "tazelik_saniye": 10}
    y = KonumYoneticisi.ayarlardan(ayar, elle_bolge="giris-holu")
    assert set(y.kaynaklar) == {"elle", "odometri"} and y.tazelik_saniye == 10
    y.bir_kez()
    d = y.durum()
    assert d["bolge"] == "giris-holu" and d["bolge_adi"] == "Giriş holü" and d["kaynak"] == "elle"


def test_ayar_birlestir_varsayilanlar():
    a = ayar_birlestir({"wifi": {"aralik": 20}, "son_bilinen_bolge": "bahce"})
    assert a["wifi"]["aralik"] == 20 and a["wifi"]["agirlik"] == 1.0
    assert a["son_bilinen_bolge"] == "bahce" and a["aruco"]["etkin"] is False
    assert ayar_birlestir(None)["tazelik_saniye"] == 30.0


def test_bolgeler_dosyasi_okunur():
    from robot.konum.bolgeler import BOLGELER_DOSYASI, bolgeleri_oku
    b = bolgeleri_oku(BOLGELER_DOSYASI)
    assert {"giris-holu", "kantin-onu", "mekatronik-lab-kapisi", "bahce", "sekreterlik-koridoru"} <= set(b.adlar())
    assert not any(bolge.gps_var for bolge in b.bolgeler.values())     # koordinat uydurulmadı
    assert BOLGELER.isaretler[8] == {"bolge": "bahce", "x": 1.5, "y": 2.0, "yon": 90.0}
    assert BOLGELER.beaconlar["LALE-KANTIN"] == "kantin-onu"
    assert isinstance(bolgeleri_oku("yok.yaml"), Bolgeler)


def test_komut_satiri_bolgeler(capsys):
    from robot.konum.__main__ import main
    assert main(["bolgeler"]) == 0
    cikti = capsys.readouterr().out
    assert "giris-holu" in cikti and "ArUco işaretleri" in cikti
