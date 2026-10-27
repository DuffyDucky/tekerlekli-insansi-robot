# Ne yapıyor: seri porttan gelen NMEA satırlarını (GGA, RMC) kendisi ayrıştırır (pynmea2 ve gpsd GEREKMEZ),
# enlem/boylamı bolgeler.yaml'daki GPS çemberleriyle (merkez + yarıçap) karşılaştırıp bölge bulur.
# Mesafe haversine formülüyle hesaplanır. Fix yoksa None; HDOP büyükse (uydu geometrisi kötü) güven düşer.
#
# Not: GPS yalnız açık alanda (bahçe, giriş önü) işe yarar; bina içinde fix çoğu zaman olmaz.
# Tipik doğruluk açık havada 2-5 m; bölge yarıçaplarını 15 m'den küçük seçmeyin.

import math
import time

from robot.konum.kaynak import KonumKaynagi, KonumTahmini, sinirla

DUNYA_YARICAPI_M = 6371000.0
IYI_HDOP = 1.5          # bu ve altı tam güven; HDOP 3 -> 0.5, HDOP 6 -> 0.25


def haversine(lat1, lon1, lat2, lon2):
    """İki enlem/boylam noktası arası mesafe (metre)."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * DUNYA_YARICAPI_M * math.asin(math.sqrt(a))


def sagla_toplami_dogru_mu(satir):
    """'$...*HH' sonundaki XOR sağlama toplamı. '*' yoksa denetlenmez (bazı modüller yazmaz)."""
    if "*" not in satir:
        return True
    govde, toplam = satir[1:].split("*", 1)
    hesap = 0
    for harf in govde:
        hesap ^= ord(harf)
    try:
        return hesap == int(toplam[:2], 16)
    except ValueError:
        return False


def derece(deger, yon):
    """NMEA 'ddmm.mmmm' + N/S/E/W -> ondalık derece (güney ve batı eksi)."""
    if not deger:
        return None
    nokta = deger.index(".") if "." in deger else len(deger)
    derece_kismi = float(deger[:nokta - 2])
    dakika = float(deger[nokta - 2:])
    sonuc = derece_kismi + dakika / 60.0
    return -sonuc if yon in ("S", "W") else sonuc


def nmea_ayristir(satir):
    """Tek NMEA satırı -> sözlük ya da None.
    GGA: {"tur": "GGA", "fix": bool, "lat", "lon", "hdop", "uydu"}
    RMC: {"tur": "RMC", "fix": bool, "lat", "lon"}"""
    satir = (satir or "").strip()
    if not satir.startswith("$") or not sagla_toplami_dogru_mu(satir):
        return None
    alanlar = satir.split("*")[0].split(",")
    tur = alanlar[0][3:]          # "$GPGGA" -> "GGA" (GP, GN, GL... hepsi kabul)
    try:
        if tur == "GGA" and len(alanlar) >= 9:
            fix = alanlar[6] not in ("", "0")
            return {"tur": "GGA", "fix": fix, "lat": derece(alanlar[2], alanlar[3]),
                    "lon": derece(alanlar[4], alanlar[5]),
                    "uydu": int(alanlar[7]) if alanlar[7] else 0,
                    "hdop": float(alanlar[8]) if alanlar[8] else None}
        if tur == "RMC" and len(alanlar) >= 7:
            return {"tur": "RMC", "fix": alanlar[2] == "A", "lat": derece(alanlar[3], alanlar[4]),
                    "lon": derece(alanlar[5], alanlar[6])}
    except ValueError:
        return None
    return None


def hdop_guveni(hdop):
    if hdop is None:
        return 0.5                      # RMC'de HDOP yok: orta güven
    return sinirla(IYI_HDOP / hdop if hdop > 0 else 1.0, 0.05, 1.0)


def bolge_bul(lat, lon, bolgeler):
    """Çemberinin içinde olunan bölgelerden merkezi en yakın olanı: (Bolge, mesafe) ya da (None, None)."""
    en_iyi, en_iyi_mesafe = None, None
    for b in bolgeler.bolgeler.values():
        if not b.gps_var:
            continue
        mesafe = haversine(lat, lon, b.lat, b.lon)
        if mesafe <= b.yaricap_m and (en_iyi_mesafe is None or mesafe < en_iyi_mesafe):
            en_iyi, en_iyi_mesafe = b, mesafe
    return en_iyi, en_iyi_mesafe


class GpsKaynagi(KonumKaynagi):
    ad = "gps"

    def __init__(self, bolgeler, port="", hiz=9600, agirlik=1.0, aralik=2.0, satir_kaynagi=None):
        super().__init__(agirlik, aralik)
        self.bolgeler = bolgeler
        self.port = port
        self.hiz = hiz
        self.satir_kaynagi = satir_kaynagi     # testte sahte: çağrılınca bir NMEA satırı (str) ya da None döner
        self.baglanti = None
        self.son_konum = None                  # tara/ham için son okunan (lat, lon, hdop)

    def baslat(self):
        if self.satir_kaynagi is not None:
            return
        if not self.port:
            self.pasif_yap("konum.gps.port boş (GPS modülü takılınca /dev/ttyAMA0 ya da /dev/ttyUSB1 yazın)")
            return
        if not any(b.gps_var for b in self.bolgeler.bolgeler.values()):
            print("[konum/gps] bolgeler.yaml'da GPS çemberi olan bölge yok; GPS yalnız ham konum verir.")
        try:
            import serial                      # pyserial
            self.baglanti = serial.Serial(self.port, self.hiz, timeout=0.2)
        except Exception as hata:
            self.pasif_yap(f"{self.port} açılamadı ({hata})")
            return
        self.satir_kaynagi = self._seri_satiri

    def _seri_satiri(self):
        return self.baglanti.readline().decode("ascii", errors="replace")

    def kapat(self):
        if self.baglanti is not None:
            self.baglanti.close()
            self.baglanti = None

    def son_fix(self, sure=1.5):
        """En fazla 'sure' saniye satır okur; fix'li ilk GGA'yı (yoksa RMC'yi) döner."""
        if self.baglanti is not None:
            self.baglanti.reset_input_buffer()     # tamponda bekleyen eski satırlar değil, taze konum
        bitis = time.monotonic() + sure
        rmc = None
        while time.monotonic() < bitis:
            satir = self.satir_kaynagi()
            if satir is None:
                break
            veri = nmea_ayristir(satir)
            if not veri or not veri["fix"] or veri["lat"] is None:
                continue
            if veri["tur"] == "GGA":
                return veri
            rmc = veri
        return rmc

    def olc(self):
        self.son_konum = None
        veri = self.son_fix()
        if veri is None:
            return None
        self.son_konum = (veri["lat"], veri["lon"], veri.get("hdop"))
        bolge, mesafe = bolge_bul(veri["lat"], veri["lon"], self.bolgeler)
        if bolge is None:
            return None
        return KonumTahmini(bolge=bolge.kimlik, x=bolge.x, y=bolge.y, guven=hdop_guveni(veri.get("hdop")),
                            kaynak=self.ad)

    def ham(self):
        if not self.etkin:
            return f"pasif: {self.pasif_nedeni}"
        tahmin = self.oku()
        if self.son_konum is None:
            return "fix yok"
        lat, lon, hdop = self.son_konum
        return f"lat {lat:.6f}, lon {lon:.6f}, HDOP {hdop}; bölge: {tahmin.bolge if tahmin else '-'}"
