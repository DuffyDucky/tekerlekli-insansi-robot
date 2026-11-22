"""Y0f: 3B etkileşimli fizik penceresi (MuJoCo görüntüleyici). Tek komut: `kod\\simulasyon3b.bat [sahne]`.

Robot PROTOKOLDEN sürülür: klavye -> Pi istemcisi (Esp32Istemci) -> bellek taşıması (port açılmaz) -> sahte ESP32
firmware modeli (bekçi, ivme / fren sınırı, güç durumları) -> MuJoCo fizik dünyası. Acil stop mantarı fiziksel düğmedir
(protokol komutu değil): basılınca firmware modeli arızaya geçer, sürücüler boşa düşer; kartın bildirdikleri yine protokol
mesajıdır.

Tuşlar (MuJoCo görüntüleyicisinin kendi tuşlarıyla çakışmayanlar; görüntüleyicinin: F1 yardım, Space duraklat, fare kamera):
  Home        gücü devreye al (arm)                  End        dur (fren sınırıyla)
  Yukarı/Aşağı  ileri hız +/- 0,1 m/s                Sol/Sağ    dönüş hızı +/- 0,25 rad/s (sola +)
  Delete      ACİL STOP mantarı bas / bırak          Insert     birak (gücü bırak)
  Page Up / Page Down   kol pozu ileri / geri (ev, öne, öne-yukarı, yana, dirsek bükük, geri)
  F9  rampa kipi aç / kapa    F10  kafa sola / ortaya / sağa    F11  robotu başlangıca koy (dünya)
  F12 sıradaki sahne (oda_rampa <-> rampa_parkuru; pencere yeniden açılır)
Sürüş: hız ya da dönüş sıfırdan farklıyken `sur` 200 ms'de bir tekrarlanır (bekçi 500 ms).

    "%LALE_SIM_VENV%\\Scripts\\python.exe" kod/fizik/gorunum3b.py --sahne oda_rampa
    ... gorunum3b.py --senaryo gosteri --ekran <klasör>     # kendi kendine tuşlara basar (doğrulama), ekran görüntüsü alır
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

# GLFW tuş kodları
T_SAG, T_SOL, T_ASAGI, T_YUKARI = 262, 263, 264, 265
T_PGUP, T_PGDN, T_HOME, T_END, T_INS, T_DEL = 266, 267, 268, 269, 260, 261
T_F9, T_F10, T_F11, T_F12 = 298, 299, 300, 301
# Num Lock kapalı sayısal tuş takımı (ve genişletilmiş bayraksız gelen tuş olayları) aynı işleri görsün
KP_ESLE = {327: T_HOME, 321: T_END, 328: T_YUKARI, 322: T_ASAGI, 324: T_SOL, 326: T_SAG, 329: T_PGUP, 323: T_PGDN,
           330: T_DEL, 320: T_INS}

SAHNELER = ["oda_rampa", "rampa_parkuru"]
KOL_POZLARI = [   # (ad, eklem derecesi: omuz, omuz_yan, dirsek); servo = eklem + ofset (protokol servo çerçevesi)
    ("ev", 0, 5, 0), ("one", 90, 5, 0), ("one-yukari", 135, 5, 0), ("yana", 0, 90, 0),
    ("dirsek bukuk", 60, 20, 90), ("geri", -45, 5, 0)]
KAFA = [0, 45, 0, -45]
PNG_IMZA = bytes([137, 80, 78, 71, 13, 10, 26, 10])


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


class Pencere:
    def __init__(self, sahne_ad, degis=None):
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
        self.c = FizikEsp32(self.harita, konum=self.bas, sahne=self.sahne, degis=degis)
        self.w = self.c.dunya
        self.e = Esp32Istemci(BellekTasima(self.c))
        self.e.baglan()
        self.servo = {s["ad"]: s for s in P.servo_tablosu()}
        self.v = self.w_cmd = 0.0
        self.kol = self.kafa = 0
        self.rampa = False
        self.son_sur_ms = -1e9
        self.olay = queue.Queue()
        self.gunluk = []
        self.sahne_degis = False

    def _yaz(self, s):
        self.gunluk.append("%7.2f s  %s" % (self.e.zaman_ms / 1000.0, s))
        self.gunluk = self.gunluk[-4:]
        print(self.gunluk[-1], flush=True)

    def _cevap(self, komut):
        # bellek taşıması sanal saatli: istek en çok birkaç sanal ms sürer, pencereyi bekletmez
        c = self.e.istek(komut, denetle=False)
        self._yaz("%s -> %s" % (komut.get("k"), "ok" if c.get("ok") else c.get("hata", c)))
        return c

    def tus(self, k):
        k = KP_ESLE.get(k, k)
        if k == T_HOME:
            self.v = self.w_cmd = 0.0
            self._cevap({"k": "arm"})
        elif k == T_END:
            self.v = self.w_cmd = 0.0
            self._cevap({"k": "dur"})
        elif k == T_INS:
            self.v = self.w_cmd = 0.0
            self._cevap({"k": "birak"})
        elif k == T_DEL:
            self.c.mantar = not self.c.mantar
            self.v = self.w_cmd = 0.0
            self._yaz("ACIL STOP mantari %s" % ("BASILDI" if self.c.mantar else "birakildi (yeniden devreye: Home)"))
        elif k == T_YUKARI:
            self.v = round(min(0.39, self.v + 0.1), 2)
        elif k == T_ASAGI:
            self.v = round(max(-0.39, self.v - 0.1), 2)
        elif k == T_SOL:
            self.w_cmd = round(min(1.0, self.w_cmd + 0.25), 2)
        elif k == T_SAG:
            self.w_cmd = round(max(-1.0, self.w_cmd - 0.25), 2)
        elif k in (T_PGUP, T_PGDN):
            self.kol = (self.kol + (1 if k == T_PGUP else -1)) % len(KOL_POZLARI)
            ad, s1, s2, dr = KOL_POZLARI[self.kol]
            self._yaz("kol pozu: %s" % ad)
            for t in ("sag", "sol"):
                for e, a in (("omuz", s1), ("omuz_yan", s2), ("dirsek", dr)):
                    n = "%s_%s" % (t, e)
                    self._cevap({"k": "servo", "kanal": n, "aci": a + self.servo[n]["ofset"]})
        elif k == T_F9:
            self.rampa = not self.rampa
            self._cevap({"k": "rampa", "ac": self.rampa})
        elif k == T_F10:
            self.kafa = (self.kafa + 1) % len(KAFA)
            self._cevap({"k": "servo", "kanal": "kafa_pan", "aci": KAFA[self.kafa] + self.servo["kafa_pan"]["ofset"]})
        elif k == T_F11:
            self.v = self.w_cmd = 0.0
            self.c.konum_ayarla(*self.bas)
            self._yaz("robot baslangica kondu")
        elif k == T_F12:
            self.sahne_degis = True
        else:
            print("tus %d: atanmamis (MuJoCo'nun kendi tusu olabilir)" % k, flush=True)
        if k in (T_YUKARI, T_ASAGI, T_SOL, T_SAG):
            self._yaz("komut v %.2f m/s  w %.2f rad/s" % (self.v, self.w_cmd))

    def adim(self, ms):
        if (self.v or self.w_cmd) and self.e.zaman_ms - self.son_sur_ms >= 200:
            self.e.gonder({"k": "sur", "v": self.v / 0.39, "w": self.w_cmd}, denetle=False)
            self.son_sur_ms = self.e.zaman_ms
        self.e.kalp_atisi()
        self.e.bekle(ms)

    def metin(self):
        """Pencere katmanı: kısa, yalnız ASCII (MuJoCo yazı tipi), tek köşe."""
        h = self.c.hakem()
        f = h["fizik"]
        sol = "guc\nkomut / olculen\negim / kol\nteker yuku N"
        sag = ("%s%s  [%s]\nv %.2f / %.2f m/s   w %.2f / %.2f rad/s\npitch %.1f  roll %.1f   rampa %s   kol %s\n%s"
               % (h["guc"], " ACIL STOP" if self.c.mantar else "", self.sahne_ad, self.v, h["v"], self.w_cmd, h["w"],
                  math.degrees(f["pitch"]), math.degrees(f["roll"]), "acik" if self.rampa else "kapali",
                  KOL_POZLARI[self.kol][0], " ".join("%.0f" % n for n in f["teker_yuk_N"])))
        if h["guc"] != "devrede":
            sol += "\nipucu"
            sag += "\nHome = devreye al (birakikken sur reddedilir)" + (", once Delete ile mantari birak" if self.c.mantar else "")
        if self.gunluk:
            sol += "\nson"
            sag += "\n" + self.gunluk[-1].strip()
        return ascii_tr(sol), ascii_tr(sag)


def kamera_kur(cam, w, taban):
    """Robotu izleyen kamera: robotun arka-sağından, yukarıdan, 3,5 m."""
    import mujoco
    cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
    cam.trackbodyid = taban
    cam.distance, cam.elevation = 3.5, -30.0
    cam.azimuth = math.degrees(w.poz()[3]) + 180.0 + 35.0
    cam.lookat[:] = w.am()


# (sanal saniye, tuş, ekran görüntüsü adı ya da None). Doğrulama için: aynı tus() yolundan geçer.
SENARYOLAR = {
    "oda_rampa": [
        (0.5, T_HOME, None), (2.0, T_YUKARI, None), (2.1, T_YUKARI, None), (2.2, T_YUKARI, None), (3.5, T_SOL, None),
        (4.5, None, "1-surus"), (5.0, T_DEL, None), (7.0, None, "2-acil-stop"), (7.5, T_DEL, None), (8.0, T_HOME, None),
        (9.0, T_PGUP, None), (11.0, T_PGUP, None), (14.0, None, "3-kollar-one-yukari"), (14.5, T_PGUP, None),
        (17.0, None, "4-kollar-yana"), (18.0, T_F12, None)],
    "rampa_parkuru": [   # 10 derecelik rampaya (y = 15) rampa kipinde tırman
        (0.5, T_HOME, None), (1.0, T_F9, None), (1.5, T_YUKARI, None), (1.6, T_YUKARI, None), (1.7, T_YUKARI, None),
        (1.8, T_YUKARI, None), (10.0, None, "5-rampa-10-derece"), (12.0, T_END, None), (13.0, None, "6-rampada-dur")],
}


def calistir(sahne_ad, senaryo_var, ekran, sure):
    import mujoco
    import mujoco.viewer
    p = Pencere(sahne_ad)
    senaryo = list(SENARYOLAR.get(sahne_ad, [])) if senaryo_var else []
    rend = mujoco.Renderer(p.w.m, 720, 1280) if ekran else None
    print("sahne %s acildi" % sahne_ad, flush=True)
    with mujoco.viewer.launch_passive(p.w.m, p.w.d, key_callback=p.olay.put, show_left_ui=False,
                                      show_right_ui=False) as v:
        with v.lock():
            kamera_kur(v.cam, p.w, p.w.taban)
        t0 = time.perf_counter()
        sanal0 = p.e.zaman_ms
        en_uzun = 0.0
        while v.is_running() and not p.sahne_degis:
            dongu = time.perf_counter()
            while not p.olay.empty():
                p.tus(p.olay.get())
            t_s = (p.e.zaman_ms - sanal0) / 1000.0
            while senaryo and senaryo[0][0] <= t_s:
                _, k, foto = senaryo.pop(0)
                if k is not None:
                    p.tus(k)
                if foto and rend is not None:
                    cam = mujoco.MjvCamera()
                    with v.lock():
                        kamera_kur(cam, p.w, p.w.taban)
                        rend.update_scene(p.w.d, cam)
                        rgb = rend.render()
                    png_yaz(os.path.join(ekran, foto + ".png"), rgb)
                    p._yaz("ekran goruntusu %s.png" % foto)
            with v.lock():
                p.adim(20)
            sol, sag = p.metin()
            # set_texts kendi kilidini alır; v.lock() içinde çağrılırsa görüntüleyici kilitlenir ("Yanıt Vermiyor")
            v.set_texts((mujoco.mjtFontScale.mjFONTSCALE_50, mujoco.mjtGridPos.mjGRID_BOTTOMLEFT, sol, sag))
            v.sync()
            en_uzun = max(en_uzun, time.perf_counter() - dongu)
            ileri = (p.e.zaman_ms - sanal0) / 1000.0 - (time.perf_counter() - t0)
            if ileri > 0:
                time.sleep(ileri)
            if sure is not None and t_s >= sure:
                break
        sonraki = p.sahne_degis
    print("sahne %s kapandi: sanal %.1f s, duvar %.1f s, en uzun dongu %.0f ms"
          % (sahne_ad, (p.e.zaman_ms - sanal0) / 1000.0, time.perf_counter() - t0, en_uzun * 1000), flush=True)
    return sonraki


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sahne", default="oda_rampa")
    ap.add_argument("--senaryo", action="store_true", help="tuşlara kendi basar (doğrulama); F12 ile sonraki sahneye geçer")
    ap.add_argument("--ekran", default=None, help="senaryoda ekran görüntülerinin yazılacağı klasör")
    ap.add_argument("--sure", type=float, default=None, help="her sahneyi bu kadar sanal saniye sonra kapat")
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
    sahne = a.sahne
    while calistir(sahne, a.senaryo, a.ekran, a.sure):
        sahne = SAHNELER[(SAHNELER.index(sahne) + 1) % len(SAHNELER)] if sahne in SAHNELER else SAHNELER[0]
    return 0


if __name__ == "__main__":
    sys.exit(main())
