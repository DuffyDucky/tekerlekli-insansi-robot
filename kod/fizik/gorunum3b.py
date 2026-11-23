"""Y0f: 3B etkileşimli fizik penceresi (MuJoCo görüntüleyici). Tek komut: `kod\\simulasyon3b.bat [sahne]`.

Robot PROTOKOLDEN sürülür: klavye -> Pi istemcisi (Esp32Istemci) -> bellek taşıması (port açılmaz) -> sahte ESP32
firmware modeli (bekçi, ivme / fren sınırı, güç durumları) -> MuJoCo fizik dünyası. Acil stop mantarı fiziksel düğmedir
(protokol komutu değil): basılınca firmware modeli arızaya geçer, sürücüler boşa düşer; kartın bildirdikleri yine protokol
mesajıdır.

Sürüş (basılı tuttukça; bırakınca `dur`, firmware fren sınırıyla durur):
  Yukarı / Aşağı   ileri / geri 0,25 m/s (Shift ile 0,39 = teker azamisi)
  Sol / Sağ        dönüş 1 rad/s (firmware giriş tavanı; sola +). İleri / geri ile birlikte: yay. Geri giderken araba
                   direksiyonu gibi: Aşağı+Sağ = arka sağa gider (w +). Bu yalnız pencerenin komut işaretidir, robot davranışı değil.
Bırakma ve odak: Windows'ta tuş durumu her döngüde yoklanır (GetAsyncKeyState), yalnız pencere bu sürecinkiyken
(GetForegroundWindow); pencere odakta değilse hiçbir tuş basılı sayılmaz -> robot durur. Öbür sistemlerde tuş olayının
tekrarından (basılı tutunca işletim sistemi tekrarlar) son 0,6 s içinde gelen tuş basılı sayılır.

Öbür tuşlar (her klavyede olan rakamlar; MuJoCo'nun kendi kısayollarıyla çakışmaz: 0-5 geom grubu, Shift+0-5 site grubu,
harfler görselleştirme / çizim bayrakları, Space, + -, [ ], Tab, Esc, F1-F5 görüntüleyicinin):
  6  devreye al (arm)            7  dur                   8  ACİL STOP mantarı bas / bırak     9  gücü bırak (birak)
  Enter  kol pozu (ev, öne, öne-yukarı, yana, dirsek bükük, geri)
  Shift+6 rampa kipi aç / kapa   Shift+7 kafa sola / ortaya / sağa   Shift+8 robotu başa koy   Shift+9 sonraki sahne
Eski tuşlar da çalışır: Home arm, End dur, Delete mantar, Insert birak, Page Up / Down kol pozu, F9 rampa, F10 kafa,
F11 başa koy, F12 sonraki sahne.
Shift+Enter  sonraki dönüş varyantı (V0 bugünkü robot; V1..V2+V3, ONERI, ONERI-T, ONERI-ADAY, ONERI-MAKARA VARSAYIM; `varyantlar.py`;
ONERI-MAKARA'da ön tekerler göbek + 22 makara, `omni_makara.py`; etek tekerleri örttüğü için 1 tuşu gövde ağını gizler). Varyant V0 değilse üstte kalıcı
"VARSAYIM: <ad> (bugunku robot DEGIL)" satırı. Komut satırından: `kod\\simulasyon3b.bat <sahne> <varyant>` ya da `--varyant`.

    "%LALE_SIM_VENV%\\Scripts\\python.exe" kod/fizik/gorunum3b.py --sahne oda_rampa
    ... gorunum3b.py --senaryo --ekran <klasör>     # kendi kendine tuşlara basar (doğrulama), ekran görüntüsü alır
"""

import argparse
import math
import os
import queue
import sys
import time

BURASI = os.path.dirname(os.path.abspath(__file__))
KOD = os.path.dirname(BURASI)
for _y in (os.path.join(KOD, "ortak"), os.path.join(KOD, "pi"), os.path.join(KOD, "araclar"), BURASI):
    if _y not in sys.path:
        sys.path.insert(0, _y)

import dunya as D  # noqa: E402
import varyantlar as VR  # noqa: E402

# GLFW tuş kodları
T_SAG, T_SOL, T_ASAGI, T_YUKARI = 262, 263, 264, 265
T_PGUP, T_PGDN, T_HOME, T_END, T_INS, T_DEL = 266, 267, 268, 269, 260, 261
T_F9, T_F10, T_F11, T_F12 = 298, 299, 300, 301
T_ENTER, T_KP_ENTER = 257, 335
T_6, T_7, T_8, T_9 = 54, 55, 56, 57
OKLAR = (T_SAG, T_SOL, T_ASAGI, T_YUKARI)
DEGISTIRICI = (340, 341, 342, 343, 344, 345, 346, 347)   # Shift / Ctrl / Alt / Super: tek başına iş değil
# Num Lock kapalı sayısal tuş takımı (ve genişletilmiş bayraksız gelen tuş olayları) aynı işleri görsün
KP_ESLE = {327: T_HOME, 321: T_END, 328: T_YUKARI, 322: T_ASAGI, 324: T_SOL, 326: T_SAG, 329: T_PGUP, 323: T_PGDN,
           330: T_DEL, 320: T_INS, T_KP_ENTER: T_ENTER}

# işler: (tuş, shift) -> ad
ISLER = {(T_6, False): "arm", (T_HOME, False): "arm", (T_7, False): "dur", (T_END, False): "dur",
         (T_8, False): "mantar", (T_DEL, False): "mantar", (T_9, False): "birak", (T_INS, False): "birak",
         (T_ENTER, False): "kol+", (T_PGUP, False): "kol+", (T_PGDN, False): "kol-",
         (T_6, True): "rampa", (T_F9, False): "rampa", (T_7, True): "kafa", (T_F10, False): "kafa",
         (T_8, True): "basa", (T_F11, False): "basa", (T_9, True): "sahne", (T_F12, False): "sahne",
         (T_ENTER, True): "varyant"}

V_SURUS, V_AZAMI, W_SURUS = 0.25, 0.39, 1.0      # m/s, m/s (teker azamisi, firmware kırpar), rad/s (firmware tavanı)
SUR_ARALIK_MS = 200                               # basılıyken sur tekrarı (bekçi 500 ms)

SAHNELER = ["oda_rampa", "rampa_parkuru"]
KOL_POZLARI = [   # (ad, eklem derecesi: omuz, omuz_yan, dirsek); servo = eklem + ofset (protokol servo çerçevesi)
    ("ev", 0, 5, 0), ("one", 90, 5, 0), ("one-yukari", 135, 5, 0), ("yana", 0, 90, 0),
    ("dirsek bukuk", 60, 20, 90), ("geri", -45, 5, 0)]
KAFA = [0, 45, 0, -45]
PNG_IMZA = bytes([137, 80, 78, 71, 13, 10, 26, 10])

# MuJoCo katman metni tek parça en çok 500 karakter çizer (fazlası sessizce kesilir; B § 14.6'da son satır kesiliyordu).
# Üst metin bu sınırın altında tutulur: ipucu kısa, sınır aşılırsa önce ikinci, sonra birinci ipucu satırı düşer.
KATMAN_SINIRI = 499
IPUCU_SATIRLARI = (
    "oklar (basili): Yukari/Asagi ileri/geri, Sol/Sag don, ikisi yay, Shift hizli; birakinca durur",
    "geri giderken araba gibi: Asagi+Sag = arka saga",
    "6 devreye al   7 dur   8 ACIL STOP   9 gucu birak   Enter kol pozu",
    "Shift+ 6 rampa  7 kafa  8 basa koy  9 sonraki sahne  Enter varyant   fare: kamera")
IPUCU = "\n".join(IPUCU_SATIRLARI)


def ust_metin(bas):
    """Durum satırları (bas) + ipucu; KATMAN_SINIRI'nı aşmaz. Son ipucu satırları (Shift ve 6-9 tuşları) her zaman kalır."""
    satirlar = list(IPUCU_SATIRLARI)
    metin = bas + "\n".join(satirlar)
    for at in (1, 0):
        if len(ascii_tr(metin)) <= KATMAN_SINIRI:
            break
        satirlar.pop(at)
        metin = bas + "\n".join(satirlar)
    return metin[:KATMAN_SINIRI]


def ascii_tr(s):
    """MuJoCo'nun yerleşik yazı tipi yalnız ASCII çizer."""
    return s.translate(str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU"))


def png_yaz(yol, rgb):
    """numpy (h, w, 3) uint8 -> PNG (standart kitaplık: zlib)."""
    import struct
    import zlib
    h, w = rgb.shape[0], rgb.shape[1]
    ham = b"".join(bytes(1) + rgb[i].tobytes() for i in range(h))

    def parca(tur, veri):
        return struct.pack(">I", len(veri)) + tur + veri + struct.pack(">I", zlib.crc32(tur + veri) & 0xFFFFFFFF)
    with open(yol, "wb") as f:
        f.write(PNG_IMZA + parca(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                + parca(b"IDAT", zlib.compress(ham, 6)) + parca(b"IEND", b""))


class Klavye:
    """Ok tuşlarının ve Shift'in ŞU ANKİ durumu. Windows: GetAsyncKeyState, yalnız ön plandaki pencere bu süreçteyse
    (odak yoksa hiçbir tuş basılı değil). Öbür sistemler: son 0,6 s içinde tuş olayı geldiyse basılı (otomatik tekrar)."""

    VK = {T_YUKARI: 0x26, T_ASAGI: 0x28, T_SOL: 0x25, T_SAG: 0x27}
    VK_SHIFT = 0x10

    def __init__(self):
        self.win = sys.platform == "win32"
        self.son_olay = {}
        if self.win:
            import ctypes
            self.u = ctypes.windll.user32
            self.ctypes = ctypes

    def odakta(self):
        if not self.win:
            return True
        h = self.u.GetForegroundWindow()
        pid = self.ctypes.c_ulong(0)
        self.u.GetWindowThreadProcessId(h, self.ctypes.byref(pid))
        return pid.value == os.getpid()

    def shift(self):
        return bool(self.win and self.odakta() and self.u.GetAsyncKeyState(self.VK_SHIFT) & 0x8000)

    def olay(self, k):
        """Tuş olayı (görüntüleyici iş parçacığından). Windows dışında basılı tutmanın tek kaynağı."""
        self.son_olay[k] = time.perf_counter()

    def basili(self):
        """(basılı ok tuşları kümesi, shift, odakta)."""
        if self.win:
            if not self.odakta():
                return set(), False, False
            b = {k for k, vk in self.VK.items() if self.u.GetAsyncKeyState(vk) & 0x8000}
            return b, bool(self.u.GetAsyncKeyState(self.VK_SHIFT) & 0x8000), True
        simdi = time.perf_counter()
        return {k for k in OKLAR if simdi - self.son_olay.get(k, -1e9) < 0.6}, False, True


class Pencere:
    def __init__(self, sahne_ad, degis=None, klavye=None, varyant_ad="V0"):
        from fizik_esp32 import FizikEsp32
        from sahte_esp32.harita import Harita
        from sahte_esp32.tasima import BellekTasima
        from lale_pi.istemci import Esp32Istemci
        import lale_protokol as P
        self.sahne_ad = sahne_ad
        self.sahne = D.sahne_oku(sahne_ad)
        self.harita = Harita.dosyadan(os.path.join(KOD, "araclar", "haritalar", self.sahne["harita"] + ".json"))
        b = self.sahne.get("baslangic", self.harita.veri.get("baslangic"))
        self.bas = (float(b["x"]), float(b["y"]), math.radians(float(b.get("aci_derece", 0))))
        self.varyant_ad = varyant_ad or "V0"
        self.varyant = VR.al(self.varyant_ad)        # None = bugünkü robot
        self.w_surus = float(self.varyant["fw_w_giris"]) if self.varyant and self.varyant.get("fw_w_giris") else W_SURUS
        self.c = FizikEsp32(self.harita, konum=self.bas, sahne=self.sahne, degis=degis, varyant=self.varyant)
        self.w = self.c.dunya
        self.e = Esp32Istemci(BellekTasima(self.c))
        self.e.baglan()
        self.servo = {s["ad"]: s for s in P.servo_tablosu()}
        self.klavye = klavye
        self.v = self.w_cmd = 0.0                 # komut edilen (Pi'nin gönderdiği) v / w
        self.suruyor = False
        self.odakta = True
        self.yapay = None                         # senaryo: klavye yerine (basılı oklar, shift)
        self.kol = self.kafa = 0
        self.rampa = False
        self.son_sur_ms = -1e9
        self.olay = queue.Queue()
        self.gunluk = []
        self.sahne_degis = False
        self.varyant_degis = None
        self.red = None                           # son reddedilen sur: (hata, sanal ms)
        self.son_t = None                         # MuJoCo d.time (Backspace sıfırlamasını algılamak için)
        self.sifir_ms = None

    def _yaz(self, s):
        self.gunluk.append("%7.2f s  %s" % (self.e.zaman_ms / 1000.0, s))
        self.gunluk = self.gunluk[-4:]
        print(self.gunluk[-1], flush=True)

    def _cevap(self, komut):
        # bellek taşıması sanal saatli: istek en çok birkaç sanal ms sürer, pencereyi bekletmez
        c = self.e.istek(komut, denetle=False)
        self._yaz("%s -> %s" % (komut.get("k"), "ok" if c.get("ok") else c.get("hata", c)))
        return c

    def tus_olayi(self, k):
        """Görüntüleyicinin tuş olayı (basma ya da tekrar). Shift o anki durumdan okunur."""
        k = KP_ESLE.get(k, k)
        if self.klavye is not None:
            self.klavye.olay(k)
        if k in OKLAR:
            return                                # sürüş basılı tutma yoklamasıyla (adim)
        shift = self.klavye.shift() if self.klavye is not None else False
        self.is_yap(ISLER.get((k, shift)) or ISLER.get((k, False)), k)

    def is_yap(self, ad, k=None):
        if ad is None:
            if k in DEGISTIRICI:
                return
            print("tus %s: atanmamis (MuJoCo'nun kendi tusu olabilir)" % k, flush=True)
            return
        if ad in ("arm", "dur", "birak", "mantar", "basa"):
            self.v = self.w_cmd = 0.0
            self.suruyor = False
        if ad == "arm":
            self._cevap({"k": "arm"})
        elif ad == "dur":
            self._cevap({"k": "dur"})
        elif ad == "birak":
            self._cevap({"k": "birak"})
        elif ad == "mantar":
            self.c.mantar = not self.c.mantar
            self._yaz("ACIL STOP mantari %s" % ("BASILDI" if self.c.mantar else "birakildi (yeniden devreye: 6)"))
        elif ad in ("kol+", "kol-"):
            self.kol = (self.kol + (1 if ad == "kol+" else -1)) % len(KOL_POZLARI)
            pad, s1, s2, dr = KOL_POZLARI[self.kol]
            self._yaz("kol pozu: %s" % pad)
            for t in ("sag", "sol"):
                for e, a in (("omuz", s1), ("omuz_yan", s2), ("dirsek", dr)):
                    n = "%s_%s" % (t, e)
                    self._cevap({"k": "servo", "kanal": n, "aci": a + self.servo[n]["ofset"]})
        elif ad == "rampa":
            self.rampa = not self.rampa
            self._cevap({"k": "rampa", "ac": self.rampa})
        elif ad == "kafa":
            self.kafa = (self.kafa + 1) % len(KAFA)
            self._cevap({"k": "servo", "kanal": "kafa_pan", "aci": KAFA[self.kafa] + self.servo["kafa_pan"]["ofset"]})
        elif ad == "basa":
            self.c.konum_ayarla(*self.bas)
            self._yaz("robot baslangica kondu")
        elif ad == "sahne":
            self.sahne_degis = True
        elif ad == "varyant":
            self.varyant_degis = VR.SIRA[(VR.SIRA.index(self.varyant_ad) + 1) % len(VR.SIRA)]

    def _surus_guncelle(self):
        if self.yapay is not None:
            basili, shift, odak = self.yapay[0], self.yapay[1], True
        elif self.klavye is not None:
            basili, shift, odak = self.klavye.basili()
        else:
            basili, shift, odak = set(), False, True
        if odak != self.odakta:
            self._yaz("pencere odakta" if odak else "odak kayboldu: surus tuslari birakilmis sayilir")
            self.odakta = odak
        hv = V_AZAMI if shift else V_SURUS
        v = (hv if T_YUKARI in basili else 0.0) - (hv if T_ASAGI in basili else 0.0)
        w = (self.w_surus if T_SOL in basili else 0.0) - (self.w_surus if T_SAG in basili else 0.0)
        if v < 0:
            w = -w                                # geri giderken araba direksiyonu: Sağ = arka sağa (w +)
        degisti = (v, w) != (self.v, self.w_cmd)
        self.v, self.w_cmd = v, w
        if v or w:
            if degisti or self.e.zaman_ms - self.son_sur_ms >= SUR_ARALIK_MS:
                # sur m/s ve rad/s (protokol); firmware w'yi giriş tavanına (0.5.0: 1), tekerleri azamiye kırpar
                c = self.e.istek({"k": "sur", "v": v, "w": w}, denetle=False)
                self.son_sur_ms = self.e.zaman_ms
                if c.get("ok"):
                    self.red = None
                else:                             # reddedilen sur (acil stop, devrede değil): durum kutusunda görünür
                    self.red = (c.get("hata", "?"), self.e.zaman_ms)
            if not self.suruyor:
                self._yaz("surus v %.2f m/s  w %.2f rad/s" % (v, w))
            self.suruyor = True
        elif self.suruyor:
            self.suruyor = False
            self.e.gonder({"k": "dur"}, denetle=False)
            x, y, _, yaw, _, _ = self.w.poz()
            self._yaz("tus birakildi -> dur  (x %.2f y %.2f yon %.0f)" % (x, y, math.degrees(yaw)))

    def mujoco_sifirlandi(self):
        """MuJoCo görüntüleyicisinin Backspace'i mj_resetData yapar: robot modelin sıfır pozuna (oda dışı) ışınlanır, servo
        hedefleri 0 olur, firmware modeli sürmeye devam eder. Bunu "başa koy"a çevir: robot başlangıç pozuna, servolar
        firmware'in bildiği açılara, sürüş `dur`; enkoder sayımı sıçramaz (konum_ayarla taban açıyı yeniler)."""
        self.v = self.w_cmd = 0.0
        self.suruyor = False
        self.c.konum_ayarla(*self.bas)
        self.w.servo_eklem_ayarla({t["ad"]: math.radians(a - t["ofset"]) for t, a in zip(self.c.servo_tablo, self.c.servo_simdi)})
        self.c._servo_uygula()
        self.e.gonder({"k": "dur"}, denetle=False)
        self.sifir_ms = self.e.zaman_ms
        self._yaz("MuJoCo sifirlandi (Backspace): robot basa kondu, dur")

    def adim(self, ms):
        self._surus_guncelle()
        self.e.kalp_atisi()
        self.e.bekle(ms)

    def metin(self):
        """Pencere katmanı: kısa, yalnız ASCII (MuJoCo yazı tipi). (üst: ipucu, alt: durum)."""
        h = self.c.hakem()
        f = h["fizik"]
        ust = ""
        if self.varyant is not None:
            ust = "VARSAYIM: %s (bugunku robot DEGIL)\n" % VR.VARYANTLAR[self.varyant_ad]["ad"]
            if self.w.makarali:
                ust += "1: govde agini gizle / goster (omni tekerler etegin altinda)\n"
        if self.c.mantar:
            ust += "ACIL STOP BASILI: once 8 ile mantari birak, sonra 6\n"
        elif h["guc"] != "devrede":
            ust += "ONCE 6'YA BAS: devreye al (guc %s; devrede degilken surulmez)\n" % h["guc"]
        if not self.odakta:
            ust += "pencere odakta degil: tiklayin (odak yokken robot durur)\n"
        ust = ust_metin(ust)
        sol = "guc\n            komut / gercek\nileri v m/s\ndonus w rad/s\negim / kol\nteker yuku N"
        sag = ("%s%s  [%s, %s]\n\n%+.2f / %+.2f\n%+.2f / %+.2f\npitch %.1f  roll %.1f   rampa %s   kol %s\n%s"
               % (h["guc"], " ACIL STOP" if self.c.mantar else "", self.sahne_ad, self.varyant_ad, self.v, h["v"], self.w_cmd, h["w"],
                  math.degrees(f["pitch"]), math.degrees(f["roll"]), "acik" if self.rampa else "kapali",
                  KOL_POZLARI[self.kol][0], " ".join("%.0f" % n for n in f["teker_yuk_N"])))
        if self.sifir_ms is not None and self.e.zaman_ms - self.sifir_ms < 3000:
            sol += "\nsifir"
            sag += "\nMuJoCo sifirlandi (Backspace): robot basa kondu"
        if self.red is not None and self.e.zaman_ms - self.red[1] < 1500:
            sol += "\nsur"
            sag += "\n" + ("acil stop: komut reddedildi" if self.c.mantar else "komut reddedildi (%s)" % self.red[0])
        if self.gunluk:
            sol += "\nson"
            sag += "\n" + self.gunluk[-1].strip()
        return ascii_tr(ust), ascii_tr(sol), ascii_tr(sag)


def pencereyi_sigdir():
    """Windows: bu sürecin görüntüleyici penceresini çalışma alanına (görev çubuğu hariç) sığdırır. Görüntüleyici pencereyi
    ekrandan büyük açınca alt kenar (sol alttaki durum kutusu) görev çubuğunun altında kalıyordu. Döner: sığdırıldı mı."""
    if sys.platform != "win32":
        return True
    import ctypes
    from ctypes import wintypes
    u = ctypes.windll.user32
    bulunan = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def gez(h, _):
        pid = wintypes.DWORD(0)
        u.GetWindowThreadProcessId(h, ctypes.byref(pid))
        if pid.value == os.getpid() and u.IsWindowVisible(h):
            n = u.GetWindowTextLengthW(h)
            b = ctypes.create_unicode_buffer(n + 1)
            u.GetWindowTextW(h, b, n + 1)
            if b.value.startswith("MuJoCo"):
                bulunan.append(h)
        return True
    u.EnumWindows(gez, 0)
    if not bulunan:
        return False
    alan = wintypes.RECT()
    u.SystemParametersInfoW(0x0030, 0, ctypes.byref(alan), 0)     # SPI_GETWORKAREA
    u.ShowWindow(bulunan[0], 1)                                    # SW_SHOWNORMAL (büyütülmüşse normale)
    u.MoveWindow(bulunan[0], alan.left, alan.top, alan.right - alan.left, alan.bottom - alan.top, True)
    return True


def kamera_kur(cam, w, taban):
    """Robotu izleyen kamera: robotun arka-sağından, yukarıdan, 3,5 m."""
    import mujoco
    cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
    cam.trackbodyid = taban
    cam.distance, cam.elevation = 3.5, -30.0
    cam.azimuth = math.degrees(w.poz()[3]) + 180.0 + 35.0
    cam.lookat[:] = w.am()


# (sanal saniye, iş: tuş kodu / ("tut", oklar kümesi, shift) / None, ekran görüntüsü adı ya da None). Doğrulama için.
SENARYOLAR = {
    "oda_rampa": [
        (0.5, T_6, None), (2.0, ("tut", {T_YUKARI}, False), None), (4.0, ("tut", {T_YUKARI, T_SOL}, False), None),
        (5.5, None, "1-surus-yay"), (6.0, ("tut", set(), False), None), (7.0, T_8, None), (7.3, ("tut", {T_YUKARI}, False), None),
        (8.0, None, "2-acil-stop"), (8.2, ("tut", set(), False), None), (8.5, T_8, None), (9.0, T_6, None), (9.5, T_ENTER, None), (10.0, T_ENTER, None), (13.0, None, "3-kollar-one-yukari"),
        (14.0, (T_9, True), None)],
    "rampa_parkuru": [   # 10 derecelik rampaya (y = 15) rampa kipinde tırman
        (0.5, T_6, None), (1.0, (T_6, True), None), (1.5, ("tut", {T_YUKARI}, True), None),
        (10.0, None, "5-rampa-10-derece"), (12.0, ("tut", set(), False), None), (13.0, None, "6-rampada-dur")],
}


def calistir(sahne_ad, senaryo_var, ekran, sure, varyant_ad="V0"):
    """Bir sahne + varyant penceresi. Döner: None (kapandı) ya da (sonraki sahne mi, sonraki varyant ya da None)."""
    import mujoco
    import mujoco.viewer
    p = Pencere(sahne_ad, klavye=Klavye(), varyant_ad=varyant_ad)
    senaryo = list(SENARYOLAR.get(sahne_ad, [])) if senaryo_var else []
    if senaryo_var:
        p.yapay = (set(), False)               # senaryoda gerçek klavye sürüşe karışmaz
    rend = mujoco.Renderer(p.w.m, 720, 1280) if ekran else None
    print("sahne %s acildi, varyant %s%s" % (sahne_ad, p.varyant_ad, "" if p.varyant is None else " (VARSAYIM)"), flush=True)
    with mujoco.viewer.launch_passive(p.w.m, p.w.d, key_callback=p.olay.put, show_left_ui=False,
                                      show_right_ui=False) as v:
        with v.lock():
            kamera_kur(v.cam, p.w, p.w.taban)
        t0 = time.perf_counter()
        sanal0 = p.e.zaman_ms
        en_uzun = 0.0
        sigdi, sig_deneme = False, 0
        while v.is_running() and not p.sahne_degis and p.varyant_degis is None:
            dongu = time.perf_counter()
            if not sigdi and sig_deneme < 100:            # pencere birkaç döngü sonra görünür; bir kez çalışma alanına sığdır
                sig_deneme += 1
                try:
                    sigdi = pencereyi_sigdir()
                except Exception:                         # sığdırma yalnız görünüm; başarısızsa pencere olduğu gibi kalır
                    sigdi = True
            while not p.olay.empty():
                p.tus_olayi(p.olay.get())
            t_s = (p.e.zaman_ms - sanal0) / 1000.0
            while senaryo and senaryo[0][0] <= t_s:
                _, k, foto = senaryo.pop(0)
                if isinstance(k, tuple) and k[0] == "tut":
                    p.yapay = (k[1], k[2])
                elif isinstance(k, tuple):
                    p.is_yap(ISLER.get(k), k)
                elif k is not None:
                    p.is_yap(ISLER.get((k, False)), k)
                if foto and rend is not None:
                    cam = mujoco.MjvCamera()
                    with v.lock():
                        kamera_kur(cam, p.w, p.w.taban)
                        rend.update_scene(p.w.d, cam)
                        rgb = rend.render()
                    png_yaz(os.path.join(ekran, foto + ".png"), rgb)
                    if p.w.makarali:              # makaralı omni: gövde ağı (grup 1) gizli ikinci görüntü, tekerler görünsün
                        sec = mujoco.MjvOption()
                        sec.geomgroup[1] = 0
                        with v.lock():
                            rend.update_scene(p.w.d, cam, scene_option=sec)
                            rgb = rend.render()
                        png_yaz(os.path.join(ekran, foto + "-tekerler.png"), rgb)
                    p._yaz("ekran goruntusu %s.png" % foto)
            with v.lock():
                if p.son_t is not None and p.w.d.time < p.son_t - 1e-9:
                    p.mujoco_sifirlandi()         # zaman geri gitti: görüntüleyici sıfırladı
                p.adim(20)
                p.son_t = p.w.d.time
            ust, sol, sag = p.metin()
            # set_texts kendi kilidini alır; v.lock() içinde çağrılırsa görüntüleyici kilitlenir ("Yanıt Vermiyor")
            v.set_texts([(mujoco.mjtFontScale.mjFONTSCALE_50, mujoco.mjtGridPos.mjGRID_TOPLEFT, ust, None),
                         (mujoco.mjtFontScale.mjFONTSCALE_50, mujoco.mjtGridPos.mjGRID_BOTTOMLEFT, sol, sag)])
            v.sync()
            en_uzun = max(en_uzun, time.perf_counter() - dongu)
            ileri = (p.e.zaman_ms - sanal0) / 1000.0 - (time.perf_counter() - t0)
            if ileri > 0:
                time.sleep(ileri)
            if sure is not None and t_s >= sure:
                break
        sonraki = (p.sahne_degis, p.varyant_degis) if (p.sahne_degis or p.varyant_degis) else None
    print("sahne %s kapandi: sanal %.1f s, duvar %.1f s, en uzun dongu %.0f ms"
          % (sahne_ad, (p.e.zaman_ms - sanal0) / 1000.0, time.perf_counter() - t0, en_uzun * 1000), flush=True)
    return sonraki


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sahne", default="oda_rampa")
    ap.add_argument("--senaryo", action="store_true", help="tuşlara kendi basar (doğrulama); Shift+9 ile sonraki sahneye geçer")
    ap.add_argument("--ekran", default=None, help="senaryoda ekran görüntülerinin yazılacağı klasör")
    ap.add_argument("--sure", type=float, default=None, help="her sahneyi bu kadar sanal saniye sonra kapat")
    ap.add_argument("--varyant", default="V0", choices=VR.SIRA, help="dönüş varyantı (V0 bugünkü robot; öbürleri VARSAYIM)")
    a = ap.parse_args()
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    if not D.FIZIK_VAR:
        print("fizik bagimliligi (mujoco) yok: %s. Kurulum: kod/SIMULASYON.md 'Fizik simulasyonu (Y0f)'." % D.FIZIK_HATA)
        return 2
    if a.ekran:
        os.makedirs(a.ekran, exist_ok=True)
    sahne, varyant = a.sahne, a.varyant
    while True:
        sonraki = calistir(sahne, a.senaryo, a.ekran, a.sure, varyant)
        if sonraki is None:
            break
        if sonraki[0]:
            sahne = SAHNELER[(SAHNELER.index(sahne) + 1) % len(SAHNELER)] if sahne in SAHNELER else SAHNELER[0]
        if sonraki[1]:
            varyant = sonraki[1]
    return 0


if __name__ == "__main__":
    sys.exit(main())
