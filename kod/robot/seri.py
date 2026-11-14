# Ne yapıyor: Pi'den ESP32'ye komut gönderir (USB-UART, 115200 baud, her satır bir JSON).
# Komutlar: {"k":"jest","ad":"selam"}  {"k":"jest","ad":"isaret","yon":"sol"}  {"k":"sur","v":0.3,"w":0.0}
#           {"k":"dur"}  {"k":"odo_sifirla"}  {"k":"rampa","ac":true|false}  {"k":"ping"}
#           {"k":"arm"}  {"k":"birak"}  {"k":"reset"}   (güç/röle, firmware 0.5.0)
# ESP32'den gelen: {"ok":...} cevapları, {"k":"odo","sol":tik,"sag":tik,"yaw":..,"ms":..} (robot/konum okur),
# {"k":"guc","guc":..,"neden":..,"ms":..} olayları, açılışta {"k":"hazir",...}.
# Port yoksa SahteSeri komutları yalnız log'a yazar; ESP32 gelmeden her şey denenebilir.
#
# WATCHDOG (ESP32 tarafında): ESP32 500 ms boyunca "sur" alamazsa motorları DURDURUR (0.5.0'da rampasız,
# ani duruş). Bu yüzden robot sürülürken Pi "sur" komutunu ~200 ms'de bir tekrar göndermelidir.
# Pi çökerse ya da kablo çıkarsa robot kendiliğinden durur. Donanım acil stop ayrıca şart.
#
# RAMPA KİPİ (29 Ekim 2026, firmware 0.4.0): rampa(True) -> ESP32 teker ivmesini/frenini 0,1 m/s^2'ye
# indirir, kolları ev pozuna alır, jest ve elle servo komutlarını reddeder. ESP32 IMU eğimiyle kipi
# kendisi de açabilir; rampa_acik yalnız Pi'nin son isteğidir (ESP32'nin etkin kipi ping/durum'da).
#
# GÜÇ / RÖLE (14 Kasım 2026, firmware 0.5.0): ESP32 açılışta ve resetten sonra röleleri BIRAKIK tutar
# (motor ve servo gücü yok, kollar düşük). arm() -> "onsarj" (~0,6 s) -> "devrede"; birak() röleleri
# bırakır (servoların gücü de kesilir: kollar düşer). Devreye alma yalnız operatör işidir: Pi hiçbir
# yerde kendiliğinden arm() göndermez. Devredeyken ESP32 5 s hiç geçerli komut almazsa kendisi bırakır
# ("sessizlik"); bu yüzden devredeyken ~1 s'de bir ping atılır (robot/uzaktan/kopru.py canli_tut).
# Bütün koruma bırakmaları (sessizlik, bara_gitti, acil_stop, onsarj_sure ...) "ariza"ya geçer ve kilitli
# kalır: birak durumu değiştirmez, yalnız yeni arm temizler. guc olayı komut cevabından SONRA gelir.
# Bırakıkken mantara basmak durum değiştirmez; acil yalnız ping cevabında görünür.
# Son bilinen güç durumu (guc, neden, ariza, acil, bara, aku) gelen satırlardan güncellenir: satir_oku()
# her satırı satir_isle()'den geçirir, satırı kim okursa okusun (konum yöneticisinin iş parçacığı,
# hazir_bekle, konum aracı). İkinci bir okuyucu açılmaz; konum kapalıysa ana.py okuyucu_baslat() der.
#
# PORT AÇILIŞI (14 Kasım 2026): ESP32 DevKit'teki CP2102 DTR/RTS hatlarını iki transistörle EN/GPIO0'a
# bağlar: RTS etkin + DTR bırakık = EN LOW (RESET); DTR etkin + RTS bırakık = GPIO0 LOW (zararsız, EN
# yüksek); ikisi aynı (ikisi etkin ya da ikisi bırakık) = etkisiz. Reset = röleler bırakır = kollar düşer.
# Linux portu açarken ikisini de etkin yapar; pyserial open() sonra ÖNCE DTR'yi SONRA RTS'yi ayarlar
# (serialposix.py open: _update_dtr_state, ardından _update_rts_state). Eskiden dtr=False, rts=False
# veriliyordu: arada "DTR bırakık, RTS etkin" anı = EN LOW = istenmeyen reset. Şimdi port_ac DTR etkin,
# RTS bırakık açar (en kötü ara durum GPIO0 LOW, zararsız), açıldıktan sonra DTR'yi bırakır: EN hiç
# LOW olmaz. Yine de reset olabilir (sürücüye göre); SeriBaglanti açılışta "hazir" ya da ping bekler.

import json
import logging
import threading
import time

log = logging.getLogger("seri")

# Pi tarafındaki hız sınırları (TAHMİNİ; taban testinde ayarlanacak). v: m/s, w: rad/s
EN_FAZLA_V = 0.5
EN_FAZLA_W = 1.0

HAZIR_SURE = 3.0      # s: açılışta ESP32'yi en çok bu kadar bekle (resetlenirse "hazir" ~1 s'de gelir)
PING_ARALIK = 0.5     # s: beklerken bu aralıkla ping (resetlenmediyse "hazir" hiç gelmez, ping cevap verir)
RESET_SURE = 0.1      # s: esp32_reset'te EN'in LOW tutulduğu süre

GUC_DURUMLARI = ("birakik", "onsarj", "devrede", "ariza")
CANLI_GUC = ("onsarj", "devrede")     # bu durumlarda ESP32'nin 5 s sessizlik bekçisi işler


def sinirla(deger, sinir):
    return max(-sinir, min(sinir, deger))


def komut_satiri(komut):
    """Sözlüğü boşluksuz tek satır JSON'a çevirir: {"k":"dur"}"""
    return json.dumps(komut, ensure_ascii=False, separators=(",", ":"))


class SeriProtokol:
    """Komutları hazırlayan ve gelen satırlardan güç durumunu tutan ortak kısım.
    Alt sınıf satir_yaz() yazar; satır okuyan alt sınıf her satırı satir_isle()'ye verir."""

    rampa_acik = False      # Pi'nin son gönderdiği elle rampa kipi (ESP32 IMU ile ayrıca açabilir)

    def __init__(self):
        self._guc_kilidi = threading.Lock()   # okuyucu iş parçacığı yazar, köprü okur
        self.guc = None           # "birakik" | "onsarj" | "devrede" | "ariza" | None (bilinmiyor / eski firmware)
        self.neden = None         # son güç değişiminin nedeni ("sessizlik", "acil_stop", ...) ya da None
        self.ariza = None         # arıza nedeni (ping'in "ariza" alanı ya da "ariza" olayının nedeni)
        self.acil = None          # acil stop basılı mı (ping/hazir); bilinmiyorsa None
        self.bara = None          # güç barasında gerilim var mı
        self.aku = None           # akü gerilimi (V) ya da None
        self.son_ret = None       # ESP32'nin son reddettiği komut: {"k": .., "hata": ..}
        self.surum = None         # ESP32 firmware sürümü (hazir ya da ping cevabından)
        self.arm_bekliyor = False  # arm gönderildi, sonucu henüz okunmadı (okuyucu yoksa da canlı tut)
        self.okuyucu_var = False   # sürekli satır okuyan bir iş parçacığı var mı (hazir_bekle satır çalmasın)
        self._hazir_olayi = threading.Event()
        self._hazir_turu = None   # "hazir" | "ping": hazir_bekle'nin beklediği son satır

    # ---------- gönderme ----------

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

    def ping(self):
        self.gonder({"k": "ping"})

    def rampa(self, ac):
        """Elle rampa kipi: ivme/fren 0,1 m/s^2, kollar ev pozunda, jest yok (ESP32 0.4.0+)."""
        self.rampa_acik = bool(ac)
        self.gonder({"k": "rampa", "ac": self.rampa_acik})

    def arm(self):
        """Röleleri devreye al (ESP32 0.5.0). Sonuç olayla gelir: "onsarj" -> ~0,6 s -> "devrede".
        YALNIZ operatör isteğiyle çağrılır (telefondaki "Devreye al"); hiçbir yerde otomatik değil."""
        with self._guc_kilidi:
            self.arm_bekliyor = True
            if self.son_ret and self.son_ret.get("k") == "arm":
                self.son_ret = None           # yeni deneme: eski "devreye alınamadı" nedeni silinir
        self.gonder({"k": "arm"})

    def birak(self):
        """Röleleri bırak: motor ve servo gücü kesilir, KOLLAR DÜŞER. Her durumda gönderilebilir."""
        with self._guc_kilidi:
            self.arm_bekliyor = False
        self.gonder({"k": "birak"})

    def reset(self):
        """Yazılımla reset ({"k":"reset"}): ESP32 cevap verip yeniden başlar, "hazir" (birakik) gelir."""
        with self._guc_kilidi:
            self.arm_bekliyor = False
            self.guc = None                   # "hazir" gelene kadar bilinmiyor
        self.gonder({"k": "reset"})

    def satir_yaz(self, satir):
        raise NotImplementedError

    # ---------- gelen satırlar ----------

    def satir_isle(self, mesaj):
        """ESP32'den gelen her satır buradan geçer (kanca). Güç durumunu ve hazir/ping bilgisini günceller;
        başka satırlara (odo, jest cevabı) dokunmaz. Okuyan iş parçacığında çalışır, kısa ve kilitli."""
        if not isinstance(mesaj, dict):
            return
        k = mesaj.get("k")
        with self._guc_kilidi:
            if k == "guc" and "ok" not in mesaj:              # komutsuz olay: durum değişti
                self._guc_ata(mesaj.get("guc"))
                self.neden = mesaj.get("neden")
                self.ariza = self.neden if self.guc == "ariza" else None
            elif k == "hazir" or (k == "ping" and mesaj.get("ok")):
                for alan in ("acil", "bara", "aku", "ariza"):
                    if alan in mesaj:
                        setattr(self, alan, mesaj[alan])
                if "guc" in mesaj:
                    self._guc_ata(mesaj.get("guc"))
                if k == "hazir":                               # ESP32 yeniden başladı: elle rampa ve arm da gitti
                    self.rampa_acik = False
                    self.arm_bekliyor = False
                    self.neden = None
                if "surum" in mesaj:
                    self.surum = mesaj["surum"]
                self._hazir_turu = k
                self._hazir_olayi.set()
            elif mesaj.get("ok") is False:                     # reddedilen komut (arm, sur, ...)
                self.son_ret = {"k": k, "hata": mesaj.get("hata")}
                if k == "arm":
                    self.arm_bekliyor = False
                    if mesaj.get("hata") == "zaten_devrede":
                        self.guc = "devrede"
            elif k == "arm" and mesaj.get("ok"):
                self._guc_ata(mesaj.get("guc"))

    def _guc_ata(self, guc):
        if guc in GUC_DURUMLARI:
            self.guc = guc
            if guc in ("birakik", "ariza"):
                self.arm_bekliyor = False
        elif guc is not None:
            log.warning("ESP32'den bilinmeyen güç durumu: %r", guc)

    def guc_durumu(self):
        """Son bilinen güç durumu (köprü ve telefon için tek sözlük)."""
        with self._guc_kilidi:
            return {"guc": self.guc, "neden": self.neden, "ariza": self.ariza, "acil": self.acil,
                    "bara": self.bara, "aku": self.aku, "son_ret": self.son_ret}

    def devrede_mi(self):
        return self.guc == "devrede"

    def canli_tut_gerekli(self):
        """Devredeyken (ya da arm sonucu bilinmiyorken) ESP32'nin 5 s sessizlik bekçisi beslenmeli."""
        with self._guc_kilidi:
            return self.guc in CANLI_GUC or self.arm_bekliyor

    def okuyucu_kaydet(self, var):
        """Sürekli okuyan iş parçacığı (konum yöneticisi) başlarken True, biterken False der."""
        self.okuyucu_var = bool(var)

    def okuyucu_baslat(self):
        """Konum yöneticisi seriyi okumuyorsa ana.py çağırır. Sahte seride okunacak satır yok."""
        return None


class SahteSeri(SeriProtokol):
    """ESP32 yokken: komutları log'a yazar ve listede tutar (testler bu listeye bakar).
    Güç sözleşmesini kabaca taklit eder (arm -> onsarj -> devrede anında, birak -> birakik,
    devrede değilken sur reddedilir) ki telefon sayfası ESP32'siz denenebilsin. Cevaplar
    gonderilenler'e girmez; doğrudan satir_isle()'den geçer. 5 s sessizlik bekçisi taklit edilmez."""

    def __init__(self):
        super().__init__()
        self.gonderilenler = []
        self.guc = "birakik"          # gerçek ESP32 gibi bırakık açılır
        self.acil, self.bara = False, True

    def satir_yaz(self, satir):
        self.gonderilenler.append(satir)
        log.info("[sahte seri] %s", satir)
        print(f"[seri] {satir}")
        self._taklit_et(json.loads(satir))

    def _taklit_et(self, komut):
        k, ms = komut.get("k"), int(time.monotonic() * 1000)
        if k == "arm":
            if self.guc == "devrede" or self.acil:
                self.satir_isle({"ok": False, "k": "arm", "hata": "acil_stop" if self.acil else "zaten_devrede"})
                return
            self.satir_isle({"ok": True, "k": "arm", "guc": "onsarj"})
            self.satir_isle({"k": "guc", "guc": "devrede", "neden": None, "ms": ms})
        elif k == "birak":
            self.satir_isle({"ok": True, "k": "birak", "ms": ms})
            if self.guc not in ("birakik", "ariza"):      # arıza kilitli: birak durumu değiştirmez
                self.satir_isle({"k": "guc", "guc": "birakik", "neden": None, "ms": ms})
        elif k == "reset":
            self.satir_isle({"ok": True, "k": "reset"})
            self.satir_isle({"k": "hazir", "surum": "sahte", "guc": "birakik"})
        elif k == "sur" and self.guc != "devrede":
            self.satir_isle({"ok": False, "k": "sur", "hata": "devrede_degil"})
        elif k == "ping":
            self.satir_isle({"ok": True, "k": "ping", "surum": "sahte", "guc": self.guc, "acil": self.acil,
                             "bara": self.bara, "aku": None, "ariza": self.ariza})

    def esp32_reset(self, hazir_sure=None):
        self.satir_isle({"k": "hazir", "surum": "sahte", "guc": "birakik"})
        return "hazir"

    def satir_oku(self):
        return None

    def kapat(self):
        pass


def port_ac(port, hiz=115200, serial_modulu=None):
    """Seri portu ESP32'yi resetlemeden açar (bkz. dosya başı "PORT AÇILIŞI"):
      - açılırken DTR ETKİN, RTS BIRAKIK: pyserial önce DTR'yi sonra RTS'yi ayarlar; Linux'un açılışta
        ikisini de etkin yapmasından sonra sıra (etkin, etkin) -> (etkin, etkin) -> (etkin, bırakık) olur,
        EN hiç LOW olmaz (ara durum yalnız GPIO0 LOW: EN yüksekken zararsız);
      - açıldıktan sonra DTR bırakılır: ikisi de bırakık, ESP32 normal çalışır.
    serial.Serial(port, ...) DEĞİL: o yazım portu hemen, varsayılan DTR/RTS ile açar.
    Linux'ta `stty -F /dev/ttyUSB0 -hupcl` artık şart değil (port kapanırken iki hat zaten bırakık);
    zararı yok, eski kurulumlarda kalabilir.
    serial_modulu yalnız testte sahte pyserial vermek için."""
    if serial_modulu is None:
        import serial as serial_modulu        # pyserial
    ser = serial_modulu.Serial()
    ser.port = port
    ser.baudrate = hiz
    ser.timeout = 0.1
    ser.dtr = True            # açılışta etkin: DTR'nin RTS'den önce bırakılıp EN'i LOW'a çekmesini önler
    ser.rts = False
    ser.open()
    ser.dtr = False           # açık portta hemen uygulanır: ikisi de bırakık
    return ser


def esp32_reset(ser, sure=RESET_SURE, uyu=time.sleep):
    """Bilinçli donanım reseti, aynı DTR/RTS devresiyle: DTR bırakık kalır (GPIO0 yüksek = normal açılış,
    indirme kipine girmez), RTS etkin -> EN LOW -> sure kadar bekle -> RTS bırakık -> ESP32 açılır.
    DTR hiç etkinleşmez. Sonrasında "hazir" satırı ~1 s'de gelir (SeriBaglanti.esp32_reset bekler)."""
    ser.dtr = False
    ser.rts = True
    uyu(sure)
    ser.rts = False


class SeriBaglanti(SeriProtokol):
    """Gerçek USB seri port (pyserial). baglanti parametresi yalnız testte sahte port vermek için.
    Port bu sınıf açtıysa (baglanti=None) açılışta hazir_bekle() çalışır; hazir_sure ile değişir."""

    def __init__(self, port, hiz=115200, baglanti=None, hazir_sure=None, saat=time.monotonic):
        super().__init__()
        if baglanti is None:
            baglanti = port_ac(port, hiz)
            if hazir_sure is None:
                hazir_sure = HAZIR_SURE
        self.baglanti = baglanti
        self.hazir_kaynagi = None     # "hazir" (ESP32 resetlendi) | "ping" (resetlenmedi) | None
        self._okuyucu_durdur = threading.Event()
        self._okuyucu = None
        if hazir_sure:
            self.hazir_bekle(hazir_sure, saat)

    def hazir_bekle(self, sure=HAZIR_SURE, saat=time.monotonic, yalniz_hazir=False):
        """ESP32 komut almaya hazır mı? İki durum da çalışır:
          - port açılırken resetlendiyse ~1 s sonra {"k":"hazir",...} gelir;
          - resetlenmediyse "hazir" hiç gelmez, beklerken gönderilen ping'e {"ok":true,"k":"ping"} gelir.
        yalniz_hazir=True (bilinçli resetten sonra): ping atılmaz, yalnız "hazir" kabul edilir.
        Satırları başka bir iş parçacığı sürekli okuyorsa (okuyucu_var) burada okunmaz, satir_isle()
        kancasının işaretini bekler (satır çalınmaz). Arada gelen odo/bozuk satırlar atlanır.
        Süre dolarsa uyarı yazılır ama devam edilir. -> "hazir" | "ping" | None"""
        self._hazir_olayi.clear()
        bitis = saat() + sure
        son_ping = None
        while saat() < bitis:
            simdi = saat()
            if not yalniz_hazir and (son_ping is None or simdi - son_ping >= PING_ARALIK):
                self.ping()
                son_ping = simdi
            if self.okuyucu_var:
                self._hazir_olayi.wait(0.05)
            else:
                self.satir_oku()
            if not self._hazir_olayi.is_set():
                continue
            self._hazir_olayi.clear()
            if yalniz_hazir and self._hazir_turu != "hazir":
                continue
            self.hazir_kaynagi = self._hazir_turu
            print(f"[seri] ESP32 hazır ({self.hazir_kaynagi}, sürüm {self.surum}, güç {self.guc}).")
            return self.hazir_kaynagi
        print(f"[seri] ESP32 {sure:g} s içinde cevap vermedi; komutlar yine de gönderilecek.")
        return None

    def esp32_reset(self, hazir_sure=HAZIR_SURE, uyu=time.sleep):
        """Bilinçli donanım reseti (DTR/RTS) + "hazir" bekleme. Röleler bırakır, kollar düşer.
        Yazılım yolu için reset() ({"k":"reset"}) kullanılabilir."""
        with self._guc_kilidi:
            self.arm_bekliyor = False
            self.guc = None
        esp32_reset(self.baglanti, uyu=uyu)
        return self.hazir_bekle(hazir_sure, yalniz_hazir=True)

    def satir_yaz(self, satir):
        self.baglanti.write((satir + "\n").encode("utf-8"))

    def satir_oku(self):
        """ESP32'den gelen bir satırı sözlük olarak döner; yoksa ya da bozuksa None.
        Her geçerli satır satir_isle() kancasından geçer (güç durumu, hazir/ping)."""
        ham = self.baglanti.readline().decode("utf-8", errors="replace").strip()
        if not ham:
            return None
        try:
            mesaj = json.loads(ham)
        except json.JSONDecodeError:
            log.warning("ESP32'den bozuk satır: %s", ham)
            return None
        self.satir_isle(mesaj)
        return mesaj

    def okuyucu_baslat(self):
        """Konum yöneticisi kapalıyken tek okuyucu: satırları okuyup yalnız kancadan geçirir."""
        if self._okuyucu is not None or self.okuyucu_var:
            return self._okuyucu
        self._okuyucu_durdur.clear()
        self._okuyucu = threading.Thread(target=self._oku_dongusu, name="seri-okuyucu", daemon=True)
        self.okuyucu_kaydet(True)
        self._okuyucu.start()
        return self._okuyucu

    def _oku_dongusu(self):
        while not self._okuyucu_durdur.is_set():
            try:
                if self.satir_oku() is None:
                    self._okuyucu_durdur.wait(0.01)
            except Exception as hata:
                print(f"[seri] okuma hatası ({hata}); 1 s sonra yeniden.")
                self._okuyucu_durdur.wait(1.0)
        self.okuyucu_kaydet(False)

    def kapat(self):
        """Robot kapanırken: dur gönderir, birak GÖNDERMEZ (kollar birden düşmesin). Pi geri gelmezse
        ESP32 5 s sessizlikten sonra röleleri kendisi bırakır; hızlı yeniden başlatmada (servis) robot
        devrede kalır, yeni süreç ping'le durumu öğrenip canlı tutar. Bilinçli kapatma: önce "Bırak"."""
        self._okuyucu_durdur.set()
        if self._okuyucu is not None:
            self._okuyucu.join(1)
            self._okuyucu = None
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
