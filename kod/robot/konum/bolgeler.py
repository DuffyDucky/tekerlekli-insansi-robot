# Ne yapıyor: kod/konum/bolgeler.yaml dosyasını okur: bölgeler (ad, açıklama, GPS çemberi, yerel x/y),
# ArUco işaretleri (id -> bölge, isteğe bağlı x/y/yön) ve BLE beaconları (MAC ya da ad -> bölge).
# Dosya yoksa ya da bozuksa boş tablo döner (robot durmaz, yalnız uyarı yazılır).

import os
from dataclasses import dataclass, field

import yaml

KOD_KLASORU = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KONUM_KLASORU = os.path.join(KOD_KLASORU, "konum")
BOLGELER_DOSYASI = os.path.join(KONUM_KLASORU, "bolgeler.yaml")


@dataclass
class Bolge:
    kimlik: str                       # tarif tablolarında kullanılan ad: "giris-holu"
    ad: str = ""                      # insanın okuyacağı ad: "Giriş holü"
    aciklama: str = ""
    lat: float | None = None          # GPS çemberinin merkezi (derece)
    lon: float | None = None
    yaricap_m: float | None = None    # GPS çemberinin yarıçapı (m)
    x: float | None = None            # yerel haritadaki merkez (m); yoksa yalnız bölge adı kullanılır
    y: float | None = None

    @property
    def gps_var(self):
        return None not in (self.lat, self.lon, self.yaricap_m)


@dataclass
class Bolgeler:
    bolgeler: dict = field(default_factory=dict)     # kimlik -> Bolge
    isaretler: dict = field(default_factory=dict)    # ArUco id (int) -> {"bolge", "x", "y", "yon"}
    beaconlar: dict = field(default_factory=dict)    # MAC (büyük harf) ya da ad -> bölge kimliği

    def adlar(self):
        return list(self.bolgeler)

    def ad(self, kimlik):
        """Bölgenin okunur adı; tabloda yoksa kimliğin kendisi."""
        b = self.bolgeler.get(kimlik)
        return (b.ad or kimlik) if b else kimlik


def sayi(deger):
    """YAML'daki değer sayıysa float, değilse (null, "...") None."""
    try:
        return float(deger)
    except (TypeError, ValueError):
        return None


def bolge_kur(kimlik, veri):
    veri = veri or {}
    gps = veri.get("gps") or {}
    yerel = veri.get("yerel") or {}
    return Bolge(str(kimlik), str(veri.get("ad") or ""), str(veri.get("aciklama") or ""),
                 sayi(gps.get("lat")), sayi(gps.get("lon")), sayi(gps.get("yaricap_m")),
                 sayi(yerel.get("x")), sayi(yerel.get("y")))


def isaret_kur(deger):
    """'7: giris-holu' ya da '7: {bolge: giris-holu, x: 1.0, y: 2.0, yon: 90}' biçimlerini kabul eder."""
    if isinstance(deger, dict):
        return {"bolge": deger.get("bolge"), "x": sayi(deger.get("x")), "y": sayi(deger.get("y")),
                "yon": sayi(deger.get("yon"))}
    return {"bolge": deger, "x": None, "y": None, "yon": None}


def veriden(veri):
    veri = veri or {}
    bolgeler = {str(k): bolge_kur(k, v) for k, v in (veri.get("bolgeler") or {}).items()}
    isaretler = {}
    for kimlik, deger in (veri.get("isaretler") or {}).items():
        try:
            isaretler[int(kimlik)] = isaret_kur(deger)
        except (TypeError, ValueError):
            print(f"[konum] bolgeler.yaml: işaret kimliği sayı olmalı: {kimlik}")
    beaconlar = {str(k).upper(): v for k, v in (veri.get("beaconlar") or {}).items()}
    return Bolgeler(bolgeler, isaretler, beaconlar)


def bolgeleri_oku(yol=BOLGELER_DOSYASI):
    """Dosyayı okur. Yoksa ya da bozuksa boş Bolgeler döner."""
    if not os.path.exists(yol):
        return Bolgeler()
    try:
        with open(yol, encoding="utf-8") as dosya:
            return veriden(yaml.safe_load(dosya))
    except (OSError, yaml.YAMLError, AttributeError) as hata:
        print(f"[konum] {yol} okunamadı ({hata}); bölge tablosu boş.")
        return Bolgeler()
