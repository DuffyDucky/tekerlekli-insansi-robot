# Ne yapıyor: Pi'den ESP32'ye komut gönderir (USB-UART, 115200 baud, her satır bir JSON).
# Komutlar: {"k":"jest","ad":"selam"}  {"k":"jest","ad":"isaret","yon":"sol"}  {"k":"sur","v":0.3,"w":0.0}
#           {"k":"dur"}  {"k":"odo_sifirla"}
# ESP32'den gelen: {"ok":...} cevapları, {"k":"odo","sol":tik,"sag":tik,"yaw":..,"ms":..} (robot/konum okur)
# Port yoksa SahteSeri komutları yalnız log'a yazar; ESP32 gelmeden her şey denenebilir.
#
# WATCHDOG (ESP32 tarafında yazılacak): ESP32 500 ms boyunca komut alamazsa motorları DURDURUR.
# Bu yüzden robot sürülürken Pi "sur" komutunu ~200 ms'de bir tekrar göndermelidir.
# Pi çökerse ya da kablo çıkarsa robot kendiliğinden durur. Donanım acil stop ayrıca şart.

import json
import logging

log = logging.getLogger("seri")

# Pi tarafındaki hız sınırları (TAHMİNİ; taban testinde ayarlanacak). v: m/s, w: rad/s
EN_FAZLA_V = 0.5
EN_FAZLA_W = 1.0


def sinirla(deger, sinir):
    return max(-sinir, min(sinir, deger))


def komut_satiri(komut):
    """Sözlüğü boşluksuz tek satır JSON'a çevirir: {"k":"dur"}"""
    return json.dumps(komut, ensure_ascii=False, separators=(",", ":"))


class SeriProtokol:
    """Komutları hazırlayan ortak kısım. Alt sınıf yalnız satir_yaz() yazar."""

    def gonder(self, komut):
        self.satir_yaz(komut_satiri(komut))

    def jest(self, ad, yon=None):
        """yon None ise eski biçim ({"k":"jest","ad":..}); eski ESP32 firmware'i de anlar."""
        komut = {"k": "jest", "ad": ad}
        if yon:
            komut["yon"] = yon
        self.gonder(komut)

    def sur(self, v, w):
        self.gonder({"k": "sur", "v": sinirla(v, EN_FAZLA_V), "w": sinirla(w, EN_FAZLA_W)})

    def dur(self):
        self.gonder({"k": "dur"})

    def satir_yaz(self, satir):
        raise NotImplementedError


class SahteSeri(SeriProtokol):
    """ESP32 yokken: komutları log'a yazar ve listede tutar (testler bu listeye bakar)."""

    def __init__(self):
        self.gonderilenler = []

    def satir_yaz(self, satir):
        self.gonderilenler.append(satir)
        log.info("[sahte seri] %s", satir)
        print(f"[seri] {satir}")

    def satir_oku(self):
        return None

    def kapat(self):
        pass


class SeriBaglanti(SeriProtokol):
    """Gerçek USB seri port (pyserial). baglanti parametresi yalnız testte sahte port vermek için."""

    def __init__(self, port, hiz=115200, baglanti=None):
        if baglanti is None:
            import serial                     # pyserial
            baglanti = serial.Serial(port, hiz, timeout=0.1)
        self.baglanti = baglanti

    def satir_yaz(self, satir):
        self.baglanti.write((satir + "\n").encode("utf-8"))

    def satir_oku(self):
        """ESP32'den gelen bir satırı sözlük olarak döner; yoksa ya da bozuksa None."""
        ham = self.baglanti.readline().decode("utf-8", errors="replace").strip()
        if not ham:
            return None
        try:
            return json.loads(ham)
        except json.JSONDecodeError:
            log.warning("ESP32'den bozuk satır: %s", ham)
            return None

    def kapat(self):
        self.dur()
        self.baglanti.close()


def seri_sec(port, hiz=115200):
    """Port boşsa ya da açılamazsa SahteSeri döner."""
    if not port:
        return SahteSeri()
    try:
        return SeriBaglanti(port, hiz)
    except Exception as hata:   # pyserial yok ya da port yok/meşgul
        print(f"[seri] {port} açılamadı ({hata}); sahte seriye düşüyorum.")
        return SahteSeri()
