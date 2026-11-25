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
  F8  sanal LiDAR katmanı aç / kapa (`lidar.py`; varsayılan kapalı, `--lidar` ile açık başlar; kapalıyken LiDAR hiç
      kurulmaz, fizik ve pencere eskisi gibi). Son tam taramanın noktaları kırmızı küre; sahne değişince açık kalır.
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
T_F6, T_F7, T_F8, T_F9, T_F10, T_F11, T_F12 = 295, 296, 297, 298, 299, 300, 301
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
         (T_ENTER, True): "varyant",
         (T_F8, False): "lidar",
         (T_F6, False): "hedef+", (T_F7, False): "bastan", (T_F7, True): "birak_rastgele"}   # gezinme katmanı   # F8: görüntüleyicinin kısayol tablosunda yok (F1-F5 #290-294, Backspace #259)

# Labirent gösterimi (`--hakem labirent`, kod\labirent.bat): rakam tuşları demo işlerine geçer (elle sürüş yok);
# F tuşları HP dizüstünde Fn isteyebilir, o yüzden her işin bir rakam / Enter karşılığı var.
T_KP_EKSI, T_KP_ARTI = 333, 334
DEMO_ISLER = {(T_6, False): "hiz-", (T_9, False): "hiz+", (T_KP_EKSI, False): "hiz-", (T_KP_ARTI, False): "hiz+",
              (T_7, False): "duraklat", (T_8, False): "kamera", (T_F9, False): "kamera",
              (T_8, True): "bastan", (T_F7, False): "bastan", (T_F11, False): "bastan",
              (T_9, True): "sonraki", (T_F12, False): "sonraki", (T_7, True): "onceki", (T_F10, False): "onceki",
              (T_ENTER, False): "hafiza", (T_6, True): "hafiza", (T_F6, False): "hafiza",
              (T_F8, False): "lidar", (T_ENTER, True): "varyant"}
DEMO_IPUCU = (
    "6 / 9 hiz - / +   7 duraklat   8 kamera ust / izle",
    "Shift+8 bastan   Shift+7 / Shift+9 onceki / sonraki labirent",
    "Enter 2. tur (kendi haritasiyla)   F8 lidar noktalari",
    "turuncu START  mor FINISH  camgobegi: robotun haritasi",
    "mavi: tahmini poz  sari: yol  yesil: hedef")
HIZLAR = (0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0)
DEMO = {"hiz": 1.0, "kamera": "ust"}            # sahne değişince korunur
LABIRENTLER = [x for x in [
    "labirent_5x5_t1", "labirent_7x7_t1", "labirent_9x9_t1", "labirent_9x9_t2", "labirent_9x9_t3",
    "labirent_13x13_t1", "labirent_13x13_t2", "labirent_13x13_t3",
    "labirent_17x17_t1", "labirent_17x17_t2", "labirent_17x17_t3"]]

V_SURUS, V_AZAMI, W_SURUS = 0.25, 0.39, 1.0      # m/s, m/s (teker azamisi, firmware kırpar), rad/s (firmware tavanı)
SUR_ARALIK_MS = 200                               # basılıyken sur tekrarı (bekçi 500 ms)

SAHNELER = ["oda_rampa", "rampa_parkuru", "koridor_1", "koridor_2", "koridor_3", "koridor_4", "koridor_5", "koridor_6",
            # labirent dünyası (kod/fizik/labirent/; robot START pozunda, `labirent.start.poz`)
            "labirent_5x5_t1", "labirent_7x7_t1", "labirent_9x9_t1", "labirent_9x9_t2", "labirent_9x9_t3",
            "labirent_13x13_t1", "labirent_13x13_t2", "labirent_13x13_t3",
            "labirent_17x17_t1", "labirent_17x17_t2", "labirent_17x17_t3"]
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
    "Shift+ 6 rampa  7 kafa  8 basa koy  9 sonraki sahne  Enter varyant   F8 lidar   fare: kamera")
IPUCU = "\n".join(IPUCU_SATIRLARI)
LIDAR_DURUM = {"acik": False}       # sahne / varyant değişince yeni pencere aynı durumla açılır


def ust_metin(bas, ipucu=IPUCU_SATIRLARI):
    """Durum satırları (bas) + ipucu; KATMAN_SINIRI'nı aşmaz. Son ipucu satırları (Shift ve 6-9 tuşları) her zaman kalır."""
    satirlar = list(ipucu)
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
        lab_poz = ((self.sahne.get("labirent") or {}).get("start") or {}).get("poz")
        if lab_poz:                               # labirent: robot START pozunda (x, y, yön rad)
            self.bas = (float(lab_poz[0]), float(lab_poz[1]), float(lab_poz[2]))
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
        self.lidar = None                         # sanal LiDAR (F8); kapalıyken hiç kurulmaz
        self._lidar_cizilen = -1
        self.gezinme = None                       # canlı gezinme katmanı (gezinme/canli.py; --senaryo ab|kayip, --beyin)
        self.demo = False                         # labirent gösterimi (gezinme + hakem): tuşlar DEMO_ISLER
        self.donuk = False                        # duraklat: fizik adımı atılmaz (hakem saati de durur)
        self.sahne_yon = 1                        # sonraki (+1) / önceki (-1) sahne
        self.kamera_degis = False
        self.gercek_hiz = None                    # ulaşılan sanal / gerçek süre oranı (son 2 s)

    def lidar_ac(self, acik):
        """Sanal LiDAR'ı kur ve fizik adımına bağla (acik) ya da ayır. Ayarlar lidar_ozellik.json + varsayılanlar."""
        LIDAR_DURUM["acik"] = bool(acik)
        if acik and self.lidar is None:
            import lidar as L
            self.lidar = L.SanalLidar(self.w)
            self.lidar.bagla()
            self._yaz("LiDAR acik (F8 kapatir): %d isin / tur, %.0f Hz" % (self.lidar.N, self.lidar.ayar.tarama_hz))
        elif not acik and self.lidar is not None:
            self.lidar.ayir()
            self.lidar = None
            self._yaz("LiDAR kapali")

    def lidar_ciz(self, scn, bas=0, zorla=False):
        """Son tam taramanın isabet noktalarını scn'ye küre olarak koy (görüntüleyicinin user_scn'i: bas 0; ekran
        görüntüsü için Renderer.scene: bas = scn.ngeom, zorla). Yeni tur yoksa dokunmaz. Döner: nokta sayısı."""
        import mujoco
        import numpy as np
        if self.lidar is None or self.lidar.son_ek is None:
            if self._lidar_cizilen != -1 or zorla:
                scn.ngeom = bas
                self._lidar_cizilen = -1
            return 0
        if self._lidar_cizilen == self.lidar.tarama_sayisi and not zorla:
            return scn.ngeom - bas - 1
        P = self.lidar.son_ek.noktalar()
        P = P[np.isfinite(P[:, 0])]
        n = max(0, min(len(P), scn.maxgeom - bas - 1))
        es = np.eye(3).ravel()
        for i in range(n):
            mujoco.mjv_initGeom(scn.geoms[bas + i], mujoco.mjtGeom.mjGEOM_SPHERE, np.array([0.025, 0, 0]), P[i], es,
                                np.array([0.95, 0.1, 0.1, 1.0], dtype=np.float32))
        koken = self.lidar.koken_ve_eksen()[0]
        mujoco.mjv_initGeom(scn.geoms[bas + n], mujoco.mjtGeom.mjGEOM_CYLINDER, np.array([0.028, 0.021, 0]), koken, es,
                            np.array([0.1, 0.3, 0.9, 1.0], dtype=np.float32))
        scn.ngeom = bas + n + 1
        if not zorla:
            self._lidar_cizilen = self.lidar.tarama_sayisi
        return n

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
        if self.demo:
            ad = DEMO_ISLER.get((k, shift)) or (None if shift and k in (T_6, T_7, T_8, T_9) else DEMO_ISLER.get((k, False)))
            if ad is not None:
                self.demo_is(ad)
                return
        self.is_yap(ISLER.get((k, shift)) or ISLER.get((k, False)), k)

    def demo_is(self, ad):
        if ad in ("hiz-", "hiz+"):
            i = min(range(len(HIZLAR)), key=lambda j: abs(HIZLAR[j] - DEMO["hiz"]))
            DEMO["hiz"] = HIZLAR[max(0, min(len(HIZLAR) - 1, i + (1 if ad == "hiz+" else -1)))]
            self._yaz("hiz %gx" % DEMO["hiz"])
        elif ad == "duraklat":
            self.donuk = not self.donuk
            self._yaz("DURAKLATILDI (7 devam)" if self.donuk else "devam")
        elif ad == "kamera":
            DEMO["kamera"] = "izle" if DEMO["kamera"] == "ust" else "ust"
            self.kamera_degis = True
            self._yaz("kamera: %s" % ("ustten" if DEMO["kamera"] == "ust" else "robotu izle"))
        elif ad == "bastan":
            self.donuk = False
            self.gezinme.is_yap("bastan")
        elif ad in ("sonraki", "onceki"):
            self.sahne_yon = 1 if ad == "sonraki" else -1
            self.sahne_degis = True
        elif ad == "hafiza":
            self.donuk = False
            self.gezinme.is_yap("hafiza")
        elif ad == "lidar":
            self.gezinme.is_yap("lidar")
        elif ad == "varyant":
            self.is_yap("varyant")

    def is_yap(self, ad, k=None):
        if ad is None:
            if k in DEGISTIRICI:
                return
            print("tus %s: atanmamis (MuJoCo'nun kendi tusu olabilir)" % k, flush=True)
            return
        if self.gezinme is not None and ad in ("hedef+", "bastan", "birak_rastgele", "dur", "lidar", "basa"):
            self.gezinme.is_yap({"hedef+": "hedef+", "bastan": "bastan", "birak_rastgele": "birak", "dur": "duraklat",
                                 "basa": "bastan", "lidar": "lidar"}[ad])
            return
        if ad in ("hedef+", "bastan", "birak_rastgele"):
            print("tus: yalniz gezinme katmaninda (--senaryo ab|kayip ya da --beyin)", flush=True)
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
        elif ad == "lidar":
            self.lidar_ac(self.lidar is None)

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
        if self.gezinme is not None:
            self.gezinme.adim()                   # Beyin sürer (oklar devre dışı)
            self.e.kalp_atisi()
            self.e.bekle(ms)
            return
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
        if self.demo:
            return self.demo_metin(ust)
        if self.gezinme is not None:
            ust += self.gezinme.metin()
        if self.lidar is not None and self.lidar.son_tarama is not None:
            n_ok = sum(1 for d in self.lidar.son_tarama["mesafeler"] if not math.isnan(d))
            ust += "LiDAR (F8): %d / %d isin olcum, kirmizi noktalar\n" % (n_ok, self.lidar.N)
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


def _dk(s):
    s = max(0.0, float(s))
    return "%02d:%02d" % (int(s // 60), int(s % 60))


def _demo_metin(self, ust):
    """Labirent gösterimi: (üst, alt sol, alt sağ). Sonuç ve puan dökümü ayrı (demo_sonuc_metni)."""
    g = self.gezinme
    o = g.ozet() or {}
    ad = self.sahne_ad.replace("labirent_", "")
    ust += "LABIRENT %s   beyin %s   %s. tur%s\n" % (
        ad, g.beyin_yolu or g.tur, o.get("tur_no", 1), " (kendi haritasiyla)" if o.get("tur_no") == 2 else "")
    ust = ust_metin(ust, DEMO_IPUCU)
    hiz = "%gx" % DEMO["hiz"]
    if self.donuk:
        hiz += "  DURAKLATILDI"
    elif self.gercek_hiz is not None and self.gercek_hiz < 0.9 * DEMO["hiz"]:
        hiz += "  (gercek %.1fx, bilgisayar yetismiyor)" % self.gercek_hiz
    elif self.gercek_hiz is not None:
        hiz += "  (gercek %.1fx)" % self.gercek_hiz
    sol = "sure\nyol\ncarpma\nmod\nhucre\nhiz"
    sag = "%s / %s\n%.1f m\n%d  (temas %.1f s)\n%s\n%d / %d   ilerleme %%%d\n%s" % (
        _dk(o.get("sure_s", 0)), _dk(o.get("sinir_s", 900)), o.get("yol_m", 0), o.get("carpma", 0),
        o.get("carpma_s", 0), o.get("mod", "-"), o.get("hucre", 0), o.get("toplam_hucre", 0),
        int(round(100 * o.get("p_en", 0))), hiz)
    if self.gunluk:
        sol += "\nson"
        sag += "\n" + self.gunluk[-1].strip()
    return ascii_tr(ust), ascii_tr(sol), ascii_tr(sag)


def _demo_sonuc_metni(self):
    """Koşu bitince: (büyük başlık, döküm sol, döküm sağ) ya da None."""
    o = self.gezinme.ozet() if self.gezinme is not None else None
    if not o or not o.get("bitti"):
        return None
    baslik = ("2. TUR: " if o["tur_no"] == 2 else "") + o["ad"] + "   %.0f puan" % o["puan"]
    sol, sag = ["puan", "sure"], ["%.1f" % o["puan"], "%.1f s" % o["sure_s"]]
    for k, v in o["dokum"].items():
        sol.append("  " + k)
        sag.append("%+.1f" % v)
    if o["tur_no"] == 2 and "ek_tur_puani" in o:
        sol.append("ek tur puani")
        sag.append("%.1f" % o["ek_tur_puani"])
        for k, v in o["ek_tur_dokum"].items():
            sol.append("  " + k)
            sag.append("%+.1f" % v)
        if o.get("tur1"):
            sol.append("1. tur")
            sag.append("%.1f s, puan %.1f" % (o["tur1"]["sure_s"], o["tur1"]["puan"]))
    if o.get("hafiza_olur") and o["tur_no"] == 1:
        sol.append("Enter")
        sag.append("ayni labirente kendi haritasiyla gir")
    sol.append("Shift+8")
    sag.append("bastan   Shift+9 sonraki labirent")
    return ascii_tr(baslik), ascii_tr("\n".join(sol)), ascii_tr("\n".join(sag))


Pencere.demo_metin = _demo_metin
Pencere.demo_sonuc_metni = _demo_sonuc_metni


def ust_kamera(cam, p):
    """Labirentin tamamı üstten (labirent.sinir; yoksa robot çevresi 8 m)."""
    import mujoco
    lab = p.sahne.get("labirent") or {}
    if lab.get("sinir"):
        x0, y0, x1, y1 = lab["sinir"]
    else:
        x, y = p.w.poz()[:2]
        x0, y0, x1, y1 = x - 4, y - 4, x + 4, y + 4
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    gor = max(x1 - x0, y1 - y0) / 0.62               # labirent ekran yüksekliğinin %62'si
    cam.lookat[:] = ((x0 + x1) / 2 - 0.13 * gor, (y0 + y1) / 2, 0.0)   # biraz sağda: soldaki metin kutularından uzak
    cam.distance = gor / (2 * math.tan(math.radians(22.5)))
    cam.elevation, cam.azimuth = -89.0, 90.0


def kamera_sec(cam, p):
    if p.demo and p.gezinme is not None:          # robotun haritası: üstten bakışta duvar tepesinde, izlerken zeminde
        z = 1.03 if DEMO["kamera"] == "ust" else 0.006
        if p.gezinme.harita_z != z:
            p.gezinme.harita_z = z
            p.gezinme._harita_duvar = p.gezinme._harita_t = -1e9
        p.gezinme.harita_renk = (0.0, 0.75, 0.8, 0.8)
    if p.demo and DEMO["kamera"] == "ust":
        ust_kamera(cam, p)
    else:
        kamera_kur(cam, p.w, p.w.taban)
        if p.demo:
            cam.distance, cam.elevation = 5.0, -50.0


def yazili_goruntu(rend, metinler):
    """Renderer sahnesi + görüntüleyicinin katman metinleri (aynı mjr_overlay) -> rgb. Pencerenin ekran görüntüsünün eşi."""
    import mujoco
    import numpy as np
    rend._gl_context.make_current()
    ctx = rend._mjr_context
    mujoco.mjr_setBuffer(mujoco.mjtFramebuffer.mjFB_OFFSCREEN, ctx)
    mujoco.mjr_render(rend._rect, rend._scene, ctx)
    for font, yer, a, b in metinler:
        mujoco.mjr_overlay(int(font), int(yer), rend._rect, a or "", b or "", ctx)
    rgb = np.empty((rend.height, rend.width, 3), dtype=np.uint8)
    mujoco.mjr_readPixels(rgb, None, rend._rect, ctx)
    return np.ascontiguousarray(np.flipud(rgb))


def pencere_yakala(yol):
    """Windows: görüntüleyici penceresinin ekrandaki halini (BitBlt) PNG'ye yazar. Döner: yazıldı mı (ekran kilitliyse
    ya da pencere örtülüyse siyah / yanlış olur; o zaman False)."""
    if sys.platform != "win32":
        return False
    import ctypes
    from ctypes import wintypes
    import numpy as np
    u, g = ctypes.windll.user32, ctypes.windll.gdi32
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
    h = bulunan[0]
    u.GetDC.restype = ctypes.c_void_p
    g.CreateCompatibleDC.restype = ctypes.c_void_p
    g.CreateCompatibleBitmap.restype = ctypes.c_void_p
    g.SelectObject.restype = ctypes.c_void_p
    for f in (g.CreateCompatibleDC, g.DeleteDC):
        f.argtypes = [ctypes.c_void_p]
    g.CreateCompatibleBitmap.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    g.SelectObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    g.BitBlt.argtypes = [ctypes.c_void_p] + [ctypes.c_int] * 4 + [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_uint32]
    g.GetDIBits.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p,
                            ctypes.c_void_p, ctypes.c_uint]
    g.DeleteObject.argtypes = [ctypes.c_void_p]
    u.ReleaseDC.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    u.GetDC.argtypes = [ctypes.c_void_p]
    r = wintypes.RECT()
    u.GetClientRect(h, ctypes.byref(r))
    pt = wintypes.POINT(0, 0)
    u.ClientToScreen(h, ctypes.byref(pt))
    W, H = r.right - r.left, r.bottom - r.top
    if W <= 0 or H <= 0:
        return False
    ekran = u.GetDC(None)
    dc = g.CreateCompatibleDC(ekran)
    bmp = g.CreateCompatibleBitmap(ekran, W, H)
    eski = g.SelectObject(dc, bmp)
    g.BitBlt(dc, 0, 0, W, H, ekran, pt.x, pt.y, 0x00CC0020)       # SRCCOPY

    class BIH(ctypes.Structure):
        _fields_ = [("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32), ("biHeight", ctypes.c_int32),
                    ("biPlanes", ctypes.c_uint16), ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32),
                    ("biSizeImage", ctypes.c_uint32), ("biXPelsPerMeter", ctypes.c_int32),
                    ("biYPelsPerMeter", ctypes.c_int32), ("biClrUsed", ctypes.c_uint32), ("biClrImportant", ctypes.c_uint32)]
    bi = BIH(ctypes.sizeof(BIH), W, -H, 1, 32, 0, 0, 0, 0, 0, 0)
    buf = (ctypes.c_ubyte * (W * H * 4))()
    g.SelectObject(dc, eski)
    g.GetDIBits(dc, bmp, 0, H, buf, ctypes.byref(bi), 0)
    g.DeleteObject(bmp)
    g.DeleteDC(dc)
    u.ReleaseDC(None, ekran)
    a = np.frombuffer(buf, dtype=np.uint8).reshape(H, W, 4)[:, :, 2::-1]
    if a.max() < 10:
        return False
    png_yaz(yol, np.ascontiguousarray(a))
    return True


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


def varsayilan_varyant(sahne_ad):
    """Varyant verilmeyince: koridor_* / labirent_* sahnelerinde ONERI (öneri firmware + ön omni; koridor deneyi bununla
    koştu, V0 modelde dönemiyor), öbür sahnelerde V0 (bugünkü robot). Tek kaynak: gezinme/duzenek.py."""
    from gezinme.duzenek import varsayilan_varyant as vv
    return vv(sahne_ad)


def gezinme_kur(p, gezinme):
    """gezinme: None ya da {"tur": "ab" | "kayip" | "beyin", "hedef", "beyin", "beyin_arg", "tohum", "cerceve", "hakem"}."""
    if not gezinme:
        return
    from gezinme.canli import CanliGezinme
    hakem = gezinme.get("hakem") if p.sahne_ad.startswith("labirent_") else None
    p.gezinme = CanliGezinme(p, gezinme["tur"], hedef=gezinme.get("hedef"), beyin_yolu=gezinme.get("beyin"),
                             beyin_arg=gezinme.get("beyin_arg"), tohum=gezinme.get("tohum", 0),
                             cerceve=gezinme.get("cerceve"), hakem=hakem,
                             sure_siniri_s=gezinme.get("sure_siniri_s", 900.0))
    p.demo = hakem is not None


GEZINME_EKRAN_S = (5.0, 15.0, 30.0, 60.0, 120.0)   # gezinmede --ekran ile bu sanal saniyelerde görüntü


def metin_listesi(p):
    """Görüntüleyici katman metinleri: [(yazı tipi, yer, sol, sağ)]. Demo bitince büyük sonuç + puan dökümü."""
    import mujoco
    ust, sol, sag = p.metin()
    L = [(mujoco.mjtFontScale.mjFONTSCALE_50, mujoco.mjtGridPos.mjGRID_TOPLEFT, ust, None),
         (mujoco.mjtFontScale.mjFONTSCALE_50, mujoco.mjtGridPos.mjGRID_BOTTOMLEFT, sol, sag)]
    if p.demo:
        r = p.demo_sonuc_metni()
        if r is not None:
            L.append((mujoco.mjtFont.mjFONT_BIG, mujoco.mjtGridPos.mjGRID_TOPRIGHT, r[0], None))
            L.append((mujoco.mjtFontScale.mjFONTSCALE_50, mujoco.mjtGridPos.mjGRID_BOTTOMRIGHT, r[1], r[2]))
    return L


def calistir(sahne_ad, senaryo_var, ekran, sure, varyant_ad="V0", gezinme=None):
    """Bir sahne + varyant penceresi. Döner: None (kapandı) ya da (sonraki sahne mi, sonraki varyant ya da None)."""
    import mujoco
    import mujoco.viewer
    p = Pencere(sahne_ad, klavye=Klavye(), varyant_ad=varyant_ad)
    if LIDAR_DURUM["acik"]:
        p.lidar_ac(True)
    gezinme_kur(p, gezinme)
    gez_ekran = [t for t in GEZINME_EKRAN_S if sure is None or t <= sure] if (gezinme and ekran) else []
    senaryo = list(SENARYOLAR.get(sahne_ad, [])) if senaryo_var else []
    if senaryo_var:
        p.yapay = (set(), False)               # senaryoda gerçek klavye sürüşe karışmaz
    rend = mujoco.Renderer(p.w.m, 720, 1280) if ekran else None
    print("sahne %s acildi, varyant %s%s" % (sahne_ad, p.varyant_ad, "" if p.varyant is None else " (VARSAYIM)"), flush=True)
    with mujoco.viewer.launch_passive(p.w.m, p.w.d, key_callback=p.olay.put, show_left_ui=False,
                                      show_right_ui=False) as v:
        with v.lock():
            kamera_sec(v.cam, p)
        t0 = time.perf_counter()
        sanal0 = p.e.zaman_ms
        en_uzun = 0.0
        sigdi, sig_deneme = False, 0
        butce = 0.0                                       # sanal s: gerçek süre x hız kadar ileri gidilebilir
        son_duvar = time.perf_counter()
        hiz_iz = []                                       # (gerçek s, sanal s): ulaşılan hız çarpanı
        sonuc_foto = None                                 # demo: koşu bitince ekran görüntüsü (bir kez)
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
            ad = None
            if gez_ekran and t_s >= gez_ekran[0]:
                ad = "gezinme-%s-%s-%03ds" % (gezinme["tur"], sahne_ad, int(gez_ekran.pop(0)))
            if p.demo and ekran and p.gezinme.hakem is not None and p.gezinme.hakem.bitti:
                bt = p.gezinme.hakem.t_bitis
                if sonuc_foto != (p.gezinme.tur_no, bt) and p.w.zaman_s - bt >= 1.0:
                    sonuc_foto = (p.gezinme.tur_no, bt)
                    ad = "labirent-%s-tur%d-sonuc" % (sahne_ad, p.gezinme.tur_no)
            if ad and rend is not None:
                cam = mujoco.MjvCamera()
                with v.lock():
                    if p.demo:
                        kamera_sec(cam, p)
                    else:
                        kamera_kur(cam, p.w, p.w.taban)
                        cam.distance, cam.elevation = 6.0, -55.0
                    rend.update_scene(p.w.d, cam)
                    p.gezinme.ciz(rend.scene, bas=rend.scene.ngeom)
                    if p.lidar is not None:
                        p.lidar_ciz(rend.scene, bas=rend.scene.ngeom, zorla=True)
                    rgb = yazili_goruntu(rend, metin_listesi(p)) if p.demo else rend.render()
                png_yaz(os.path.join(ekran, ad + ".png"), rgb)
                if p.demo and pencere_yakala(os.path.join(ekran, ad + "-pencere.png")):
                    p._yaz("ekran goruntusu %s.png (+ pencere)" % ad)
                else:
                    p._yaz("ekran goruntusu %s.png" % ad)
            if p.kamera_degis:
                p.kamera_degis = False
                with v.lock():
                    kamera_sec(v.cam, p)
            simdi = time.perf_counter()
            hiz = DEMO["hiz"] if p.demo else 1.0
            if p.donuk:
                butce = 0.0
            else:
                butce = min(butce + (simdi - son_duvar) * hiz, max(0.1, 0.25 * hiz))
            son_duvar = simdi
            adim_n = 0
            while not p.donuk and butce >= 0.02 - 1e-9 and (adim_n == 0 or time.perf_counter() - simdi < 0.05):
                z0 = p.e.zaman_ms
                with v.lock():
                    if p.son_t is not None and p.w.d.time < p.son_t - 1e-9:
                        p.mujoco_sifirlandi()     # zaman geri gitti: görüntüleyici sıfırladı
                    p.adim(20)
                    p.son_t = p.w.d.time
                butce -= max(0.02, (p.e.zaman_ms - z0) / 1000.0)    # istekler de birkaç sanal ms sürer
                adim_n += 1
            hiz_iz.append((time.perf_counter(), p.w.zaman_s))
            while len(hiz_iz) > 2 and hiz_iz[-1][0] - hiz_iz[0][0] > 2.0:
                hiz_iz.pop(0)
            if p.donuk:
                p.gercek_hiz = None
            elif hiz_iz[-1][0] - hiz_iz[0][0] > 0.5:
                p.gercek_hiz = (hiz_iz[-1][1] - hiz_iz[0][1]) / (hiz_iz[-1][0] - hiz_iz[0][0])
            with v.lock():
                if p.gezinme is not None:
                    p.gezinme.ciz_pencere(v.user_scn)
                elif p.lidar is not None or p._lidar_cizilen != -1:
                    p.lidar_ciz(v.user_scn)
            # set_texts kendi kilidini alır; v.lock() içinde çağrılırsa görüntüleyici kilitlenir ("Yanıt Vermiyor")
            v.set_texts(metin_listesi(p))
            v.sync()
            en_uzun = max(en_uzun, time.perf_counter() - dongu)
            if butce < 0.02 or p.donuk:                       # yetişildi: bir sonraki 20 ms'lik dilime dek bekle
                time.sleep(min(0.02, (0.02 - max(0.0, butce)) / max(hiz, 1e-3)))
            if sure is not None and t_s >= sure:
                break
        sonraki = ((p.sahne_yon if p.sahne_degis else False), p.varyant_degis) if (p.sahne_degis or p.varyant_degis) else None
    print("sahne %s kapandi: sanal %.1f s, duvar %.1f s, en uzun dongu %.0f ms"
          % (sahne_ad, (p.e.zaman_ms - sanal0) / 1000.0, time.perf_counter() - t0, en_uzun * 1000), flush=True)
    return sonraki


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sahne", default="oda_rampa")
    ap.add_argument("--senaryo", nargs="?", const="tus", default=None, choices=["tus", "ab", "kayip"],
                    help="değersiz ya da 'tus': tuşlara kendi basar (doğrulama; Shift+9 ile sonraki sahne). 'ab': A'dan B'ye "
                         "(bilinen koridor + başlangıç), 'kayip': kayıp robot (6 koridor aday); gezinme/canli.py")
    ap.add_argument("--beyin", default=None, help="gezinme beyni modul:Sinif (kod/fizik altından, ör. kesif.beyin:Beyin)")
    ap.add_argument("--beyin-arg", action="append", default=[], help="beyin kurucusuna anahtar=değer (tekrarlanır)")
    ap.add_argument("--hedef", default=None, help="gezinme hedef durağı (k5_kapi_3 ya da kapi_3)")
    ap.add_argument("--tohum", type=int, default=0, help="gezinme tohumu (konumlayıcı, rastgele bırakma)")
    ap.add_argument("--cerceve", default=None, choices=["harita", "baslangic"],
                    help="Beyin poz / harita çerçevesi (durum()['ek']['cerceve'] yoksa); varsayılan labirentte baslangic, öbürlerinde harita")
    ap.add_argument("--hakem", default=None, choices=["labirent"],
                    help="labirent: kod/fizik/labirent/hakem.py (900 s) koşuyu yönetir, sonuç + puan ekranda; tuşlar demo")
    ap.add_argument("--hiz", type=float, default=1.0, help="labirent gösteriminde sanal / gerçek süre (1, 2, 4, 8 ...)")
    ap.add_argument("--kamera", default="ust", choices=["ust", "izle"], help="labirent gösteriminde başlangıç kamerası")
    ap.add_argument("--ekran", default=None, help="senaryoda ekran görüntülerinin yazılacağı klasör")
    ap.add_argument("--sure", type=float, default=None, help="her sahneyi bu kadar sanal saniye sonra kapat")
    ap.add_argument("--varyant", default=None, choices=VR.SIRA,
                    help="dönüş varyantı (V0 bugünkü robot; öbürleri VARSAYIM). Verilmezse koridor_* / labirent_* "
                         "sahnelerinde ONERI (koridor deneyinin robotu), öbürlerinde V0")
    ap.add_argument("--lidar", action="store_true", help="sanal LiDAR katmanı açık başlasın (pencerede F8 aç / kapa)")
    ap.add_argument("--eklenti", action="append", default=[],
                    help="pencere kurulmadan önce içe aktarılacak modül (kod/fizik altından, ör. ucurum.demo); modül kendi "
                         "kancalarını bu süreçte kurar. Verilmezse davranış aynı")
    a = ap.parse_args()
    if a.eklenti:
        import importlib
        for _m in a.eklenti:
            importlib.import_module(_m)
    LIDAR_DURUM["acik"] = a.lidar
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
    gezinme = None
    if a.senaryo in ("ab", "kayip") or a.beyin:
        def _deger(v):
            for tur in (int, float):
                try:
                    return tur(v)
                except ValueError:
                    pass
            return v
        gezinme = dict(tur="beyin" if a.beyin else a.senaryo, beyin=a.beyin, hedef=a.hedef, tohum=a.tohum, cerceve=a.cerceve,
                       hakem=a.hakem,
                       beyin_arg={k: _deger(v) for k, v in (x.split("=", 1) for x in a.beyin_arg)})
        if gezinme["tur"] in ("ab", "kayip") and not sahne.startswith("koridor_"):
            print("--senaryo %s yalniz koridor sahnelerinde; koridor_1 aciliyor" % gezinme["tur"], flush=True)
            sahne = "koridor_1"
    senaryo_tus = a.senaryo == "tus"
    DEMO["hiz"], DEMO["kamera"] = max(0.05, a.hiz), a.kamera
    acik_varyant = varyant is not None             # elle seçilen varyant sahne değişince korunur
    while True:
        if not acik_varyant:
            varyant = varsayilan_varyant(sahne)
        sonraki = calistir(sahne, senaryo_tus, a.ekran, a.sure, varyant, gezinme)
        if sonraki is None:
            break
        if sonraki[0]:
            liste = SAHNELER
            if gezinme and gezinme["tur"] in ("ab", "kayip"):
                liste = [x for x in SAHNELER if x.startswith("koridor_")]   # A-B / kayıp yalnız koridorlarda
            elif gezinme and gezinme.get("hakem") == "labirent":
                liste = LABIRENTLER                                          # kolaydan zora
            yon = sonraki[0] if isinstance(sonraki[0], int) and not isinstance(sonraki[0], bool) else 1
            sahne = liste[(liste.index(sahne) + yon) % len(liste)] if sahne in liste else liste[0]
        if sonraki[1]:
            varyant = sonraki[1]
            acik_varyant = True
    return 0


if __name__ == "__main__":
    sys.exit(main())
