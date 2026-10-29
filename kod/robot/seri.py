# Ne yapıyor: Pi'den ESP32'ye komut gönderir (USB-UART, 115200 baud, her satır bir JSON).
# Komutlar: {"k":"jest","ad":"selam"}  {"k":"jest","ad":"isaret","yon":"sol"}  {"k":"sur","v":0.3,"w":0.0}
#           {"k":"dur"}  {"k":"odo_sifirla"}  {"k":"rampa","ac":true|false}  {"k":"ping"}
# ESP32'den gelen: {"ok":...} cevapları, {"k":"odo","sol":tik,"sag":tik,"yaw":..,"ms":..} (robot/konum okur)
# Port yoksa SahteSeri komutları yalnız log'a yazar; ESP32 gelmeden her şey denenebilir.
#
# WATCHDOG (ESP32 tarafında yazılacak): ESP32 500 ms boyunca komut alamazsa motorları DURDURUR.
# Bu yüzden robot sürülürken Pi "sur" komutunu ~200 ms'de bir tekrar göndermelidir.
# Pi çökerse ya da kablo çıkarsa robot kendiliğinden durur. Donanım acil stop ayrıca şart.
#
# RAMPA KİPİ (29 Ekim 2026, firmware 0.4.0): rampa(True) -> ESP32 teker ivmesini/frenini 0,1 m/s^2'ye
# indirir, kolları ev pozuna alır, jest ve elle servo komutlarını reddeder. ESP32 IMU eğimiyle kipi
# kendisi de açabilir; rampa_acik yalnız Pi'nin son isteğidir (ESP32'nin etkin kipi ping/durum'da).
#
# PORT AÇILIŞI (29 Ekim 2026, köprü F5): ESP32 DevKit'in USB çipi DTR/RTS hatlarını EN/IO0'a bağlar;
# port açılırken bunlar oynarsa ESP32 resetlenir (ileride röle varken: reset = röle bırakır = kollar
# düşer). Bu yüzden port DTR/RTS KAPALI açılır (port_ac). Yine de reset olabilir (sürücüye göre), bu
# yüzden SeriBaglanti açılışta "hazir" satırını ya da ping cevabını bekler: iki durumda da çalışır.

import json
import logging
import time

log = logging.getLogger("seri")

# Pi tarafındaki hız sınırları (TAHMİNİ; taban testinde ayarlanacak). v: m/s, w: rad/s
EN_FAZLA_V = 0.5
EN_FAZLA_W = 1.0

HAZIR_SURE = 3.0      # s: açılışta ESP32'yi en çok bu kadar bekle (resetlenirse "hazir" ~1 s'de gelir)
PING_ARALIK = 0.5     # s: beklerken bu aralıkla ping (resetlenmediyse "hazir" hiç gelmez, ping cevap verir)


def sinirla(deger, sinir):
    return max(-sinir, min(sinir, deger))


def komut_satiri(komut):
    """Sözlüğü boşluksuz tek satır JSON'a çevirir: {"k":"dur"}"""
    return json.dumps(komut, ensure_ascii=False, separators=(",", ":"))


class SeriProtokol:
    """Komutları hazırlayan ortak kısım. Alt sınıf yalnız satir_yaz() yazar."""

    rampa_acik = False      # Pi'nin son gönderdiği elle rampa kipi (ESP32 IMU ile ayrıca açabilir)

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

    def rampa(self, ac):
        """Elle rampa kipi: ivme/fren 0,1 m/s^2, kollar ev pozunda, jest yok (ESP32 0.4.0+)."""
        self.rampa_acik = bool(ac)
        self.gonder({"k": "rampa", "ac": self.rampa_acik})

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


def port_ac(port, hiz=115200, serial_modulu=None):
    """Seri portu DTR/RTS KAPALI açar (açılışta ESP32 resetlenmesin; bkz. dosya başı).
    serial.Serial(port, ...) DEĞİL: o yazım portu hemen açar ve DTR'yi açılışta oynatır.
    Linux'ta (Pi) ek olarak, port kapanınca DTR düşüp ESP32'yi resetlemesin diye bir kez:
        stty -F /dev/ttyUSB0 -hupcl
    (açılıştan önce; kalıcı olması için robot servisinin ExecStartPre'sine ya da udev kuralına yazılabilir).
    serial_modulu yalnız testte sahte pyserial vermek için."""
    if serial_modulu is None:
        import serial as serial_modulu        # pyserial
    ser = serial_modulu.Serial()
    ser.port = port
    ser.baudrate = hiz
    ser.timeout = 0.1
    ser.dtr = False
    ser.rts = False
    ser.open()
    return ser


class SeriBaglanti(SeriProtokol):
    """Gerçek USB seri port (pyserial). baglanti parametresi yalnız testte sahte port vermek için.
    Port bu sınıf açtıysa (baglanti=None) açılışta hazir_bekle() çalışır; hazir_sure ile değişir."""

    def __init__(self, port, hiz=115200, baglanti=None, hazir_sure=None, saat=time.monotonic):
        if baglanti is None:
            baglanti = port_ac(port, hiz)
            if hazir_sure is None:
                hazir_sure = HAZIR_SURE
        self.baglanti = baglanti
        self.surum = None             # ESP32 firmware sürümü (hazir ya da ping cevabından)
        self.hazir_kaynagi = None     # "hazir" (ESP32 resetlendi) | "ping" (resetlenmedi) | None
        if hazir_sure:
            self.hazir_bekle(hazir_sure, saat)

    def hazir_bekle(self, sure=HAZIR_SURE, saat=time.monotonic):
        """ESP32 komut almaya hazır mı? İki durum da çalışır:
          - port açılırken resetlendiyse ~1 s sonra {"k":"hazir",...} gelir;
          - resetlenmediyse "hazir" hiç gelmez, beklerken gönderilen ping'e {"ok":true,"k":"ping"} gelir.
        Arada gelen odo/bozuk satırlar atlanır. Süre dolarsa uyarı yazılır ama devam edilir.
        -> "hazir" | "ping" | None"""
        bitis = saat() + sure
        son_ping = None
        while saat() < bitis:
            simdi = saat()
            if son_ping is None or simdi - son_ping >= PING_ARALIK:
                self.gonder({"k": "ping"})
                son_ping = simdi
            satir = self.satir_oku()
            if not isinstance(satir, dict):
                continue
            if satir.get("k") == "hazir":
                self.hazir_kaynagi = "hazir"
            elif satir.get("k") == "ping" and satir.get("ok"):
                self.hazir_kaynagi = "ping"
            else:
                continue
            self.surum = satir.get("surum")
            print(f"[seri] ESP32 hazır ({self.hazir_kaynagi}, sürüm {self.surum}).")
            return self.hazir_kaynagi
        print(f"[seri] ESP32 {sure:g} s içinde cevap vermedi; komutlar yine de gönderilecek.")
        return None

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
