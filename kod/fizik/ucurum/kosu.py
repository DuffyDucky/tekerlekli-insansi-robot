"""Uçurum deney düzeneği: sahne + sahte ESP32 (fizik, ONERI) + uçurum sensörleri + ESP32 uçurum denetçisi + hakem.

Robot GERÇEK sürüş yolundan sürülür: "Pi" (burada senaryo) uçurumu bilmeden `sur` gönderir (Pi istemcisi, bellek
taşıması); uçurum denetçisi sahte ESP32'nin döngüsünde (`UcurumEsp32._dilim`) çalışır ve tetiklenince motor çıkışını
Pi'den bağımsız keser / frenler. Denetçi yalnız sensör okumalarını görür. Hakem (yer gerçeği: teker temas noktalarının
kenara payı, gövde eğimi, z düşüşü) yalnız ölçümdedir.

    from ucurum import kosu
    r = kosu.kos("merdiven_17x30", yerlesim=sensor.yerlesim("3KO", 0.06, 15), ayar=DenetciAyar(...),
                 senaryo=dict(tur="ileri", aci=30, v=0.39), tohum=1)
"""

import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ucurum import _yol  # noqa: E402,F401
from ucurum import sahne as S  # noqa: E402
from ucurum.denetci import DenetciAyar, UcurumDenetci  # noqa: E402

VARYANT = "ONERI"          # deneylerin robotu (görev: ön tekerler omni, öneri firmware; VARSAYIM)
TEKER_R = 0.0625
YERLESIK = 0.3             # s: başta motorlar boşta oturma
KAL_SURE_MS = 520          # kalibrasyon: 26 örnek (50 Hz)


def _esp32_sinifi():
    from fizik_esp32 import FizikEsp32

    class UcurumEsp32(FizikEsp32):
        """FizikEsp32 + ESP32 uçurum denetçisi. denetci None iken davranış FizikEsp32 ile aynıdır."""

        def ucurum_bagla(self, sensorler, denetci, golgeler=(), zorla_tetik=None):
            self.u_sensor = sensorler
            self.u_den = denetci                    # etkin denetçi (motoru keser) ya da None
            self.u_golge = list(golgeler)           # gölge denetçiler: aynı okumaları görür, motora dokunmaz
            self.u_zorla = zorla_tetik              # ölçüm: zorla_tetik(self) True dönerse tetik (fren ölçümü)
            self.u_kal = True                       # kalibrasyon evresi
            self.u_kayit = []                       # (t, i, değer) bütün okumalar (gölge / analiz)
            self.u_tetik_ms = None
            self.u_kayit_ac = True
            self._u_bekleyen = []

        def _dilim(self):
            s = getattr(self, "u_sensor", None)
            if s is not None and self.calisiyor:
                t_ms = self.dunya_ms                # her dilimde 10 ms artar; sensör saati
                s.ornekle(t_ms)
                hz = s.hazir(t_ms)
                t = self.dunya.zaman_s
                d = self.u_den
                isle = d is None or (t_ms % d.ayar.dongu_ms == 0)
                for i, v in hz:
                    if self.u_kayit_ac:
                        self.u_kayit.append((t, i, v))
                    if self.u_kal:
                        for dd in ([d] if d else []) + self.u_golge:
                            dd.kalibrasyon_ornegi(i, v)
                        continue
                    for g in self.u_golge:
                        g.isle(t, i, v)
                    if d is not None:
                        self._u_bekleyen.append((t, i, v))
                if d is not None and not self.u_kal and isle:
                    for (tt, i, v) in self._u_bekleyen:
                        d.isle(t, i, v)
                    self._u_bekleyen = []
                if self.u_zorla is not None and self.u_den is not None and not self.u_den.tetik and self.u_zorla(self):
                    self.u_den._tetikle(t, -1, "zorla")
                if d is not None and d.tetik and self.u_tetik_ms is None:
                    self.u_tetik_ms = t_ms
                    self.u_tetik_poz = self.dunya.poz()[:2]
                    self.u_tetik_v = self.dunya.hiz()[0]
            super()._dilim()

        def _surucu(self):
            d = getattr(self, "u_den", None)
            if d is not None and d.tetik and d.ayar.fren == "kes":
                return False, [0.0, 0.0]            # EN LOW: sürücü boşta (motor kesme)
            return super()._surucu()

        def _motor_guncelle(self):
            d = getattr(self, "u_den", None)
            if d is None:
                return super()._motor_guncelle()
            if d.tetik:
                self.v_hedef = self.w_hedef = 0.0
                self.hedef = [0.0, 0.0]
                if d.ayar.fren in ("fren", "kes"):
                    self.rampa_hiz = [0.0, 0.0]     # rampasız: PWM 0 (EN HIGH -> kısa devre freni; kes -> boşta)
                    return super()._motor_guncelle()
                eski = self.ivme
                a = d.ayar.fren_ivme
                self.ivme = {"duz": (eski["duz"][0], a), "rampa": (eski["rampa"][0], a)}
                try:
                    return super()._motor_guncelle()
                finally:
                    self.ivme = eski
            lim = d.hiz_siniri(self.dunya.zaman_s)
            if lim is not None and max(abs(h) for h in self.hedef) > lim:
                o = lim / max(abs(h) for h in self.hedef)
                self.hedef = [h * o for h in self.hedef]
            return super()._motor_guncelle()

    return UcurumEsp32


_SINIF = {}


def esp32_sinifi():
    if "c" not in _SINIF:
        _SINIF["c"] = _esp32_sinifi()
    return _SINIF["c"]


# ------------------------------------------------------------------ hakem
class Hakem:
    """Yer gerçeği. Her 10 ms: teker temas noktalarının kenara payı, eğim, z, aks yükü (isteğe bağlı)."""

    def __init__(self, c, kenarlar, yuk_olc=False):
        import mujoco
        self.c, self.w = c, c.dunya
        self.kenarlar = kenarlar
        m = self.w.m
        self.teker_body = [mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, t) for t in ("teker_on_sol", "teker_arka_sol",
                                                                                         "teker_on_sag", "teker_arka_sag")]
        self.yuk_olc = yuk_olc
        self.z0 = None
        self.pay_min = math.inf
        self.pay_min_teker = None
        self.egim_max = 0.0
        self.pitch_max = -math.inf
        self.dz_min = 0.0
        self.dustu = False
        self.dustu_neden = None
        self.dustu_t = None
        self.satir = []          # (t, x, y, yaw, v, pitch, pay, arka_yuk, on_yuk, arka_z) seyrek değil: 10 ms
        self.kayit_ac = False

    def paylar(self):
        d = self.w.d
        out = []
        for b in self.teker_body:
            p = d.xpos[b]
            out.append(S.pay(self.kenarlar, float(p[0]), float(p[1])))
        return out

    def guncelle(self):
        x, y, z, yaw, pitch, roll = self.w.poz()
        if self.z0 is None:
            self.z0 = z
        pp = self.paylar()
        p = min(pp)
        if p < self.pay_min:
            self.pay_min, self.pay_min_teker = p, pp.index(p)
        eg = math.degrees(self.w.egim())
        self.egim_max = max(self.egim_max, eg)
        self.pitch_max = max(self.pitch_max, math.degrees(pitch))
        dz = z - self.z0
        self.dz_min = min(self.dz_min, dz)
        t = self.w.zaman_s
        if not self.dustu:
            neden = None
            if p < 0.0:
                neden = "teker_kenari_gecti"
            elif self.kenarlar and eg > 15.0:
                neden = "egim"
            elif self.kenarlar and dz < -0.03:
                neden = "z_dusus"
            elif eg > 25.0:                     # kenarsız (denetim) sahne: rampada z ve eğim değişir; yalnız devrilme
                neden = "devrilme"
            if neden:
                self.dustu, self.dustu_neden, self.dustu_t = True, neden, t
        if self.kayit_ac:
            v, w = self.w.hiz()
            ay = oy = None
            az = ax = None
            if self.yuk_olc:
                F = self.w.teker_yukleri()
                oy, ay = F[0] + F[2], F[1] + F[3]
                az = (float(self.w.d.xpos[self.teker_body[1]][2]) + float(self.w.d.xpos[self.teker_body[3]][2])) / 2
                ax = (float(self.w.d.xpos[self.teker_body[1]][0]) + float(self.w.d.xpos[self.teker_body[3]][0])) / 2
            self.satir.append((t, x, y, yaw, v, math.degrees(pitch), p, ay, oy, az, ax))


# ------------------------------------------------------------------ yerleştirme
TEKERLER_YEREL = ((0.185, 0.216), (-0.185, 0.216), (0.185, -0.216), (-0.185, -0.216))


def _donus(a, p):
    c, s = math.cos(a), math.sin(a)
    return (c * p[0] - s * p[1], s * p[0] + c * p[1])


def baslangic_pozu(kenar, senaryo, rng):
    """Senaryo -> (x, y, yaw) dünya. kenar [nx, ny, c]: güvenli taraf n.p < c. Yaklaşma açısı kenar normaline göre."""
    nx, ny, c = kenar
    na = math.atan2(ny, nx)
    tur = senaryo["tur"]
    aci = math.radians(senaryo.get("aci", 0.0) + float(rng.uniform(-2.0, 2.0)))
    ya = senaryo.get("yanal", (-0.5, 0.5))
    yanal = float(rng.uniform(ya[0], ya[1]))
    if tur in ("ileri", "geri"):
        yaw = na + aci + (math.pi if tur == "geri" else 0.0)
        v = abs(senaryo["v"])
        s_hiz = v * v / (2 * 0.5) + 0.08 + 0.10 * (v / 0.39)         # hızlanma + PI oturması (yol, m)
        d0 = s_hiz * math.cos(aci) + 0.20 + float(rng.uniform(0.0, 0.10))
        # en öndeki tekerin kenara normal uzaklığı d0 olsun
        on = max(nx * q[0] + ny * q[1] for q in (_donus(yaw, w) for w in TEKERLER_YEREL))
        k = c - d0 - on                       # merkezin normal koordinatı
    elif tur == "donus":
        # kenara paralel (kenar robotun sağında), dönme merkezinin (x -0,18) kenara uzaklığı senaryo["d"]
        yaw = na + math.pi / 2
        mx = _donus(yaw, (-0.18, 0.0))
        k = c - senaryo["d"] - (nx * mx[0] + ny * mx[1])
    elif tur == "yay":
        yaw = na + math.radians(senaryo.get("aci", 60.0))
        k = c - senaryo.get("d", 1.0)
    else:
        raise ValueError(tur)
    if abs(nx) > 0.5:                           # x kenarı: y orta hatta
        bx, by = k / nx, S.Y0 + yanal
    else:
        bx, by = S.E - 1.5 + yanal, k / ny
    return bx, by, yaw


# ------------------------------------------------------------------ koşu
def dunya_kur(sahne_ad, yerlesim, tohum, baslangic=(S.E - 1.5, S.Y0, 0.0), varyant=VARYANT):
    import numpy as np
    import varyantlar as VR
    from sahte_esp32.harita import Harita
    from sahte_esp32.tasima import BellekTasima
    from lale_pi.istemci import Esp32Istemci
    from ucurum.sensor import SensorDizisi
    S.kur()
    sz = S.sahne_sozlugu(sahne_ad, baslangic)
    harita = Harita.dosyadan(S.HARITA)
    C = esp32_sinifi()
    c = C(harita, konum=baslangic, sahne=sz, varyant=VR.al(varyant), sonar_acik=False)
    z = sz["ucurum"].get("taban_z", 0.0)
    if z:
        c.dunya.konum_ayarla(baslangic[0], baslangic[1], baslangic[2], z=z + 0.002)
        c._enkoder_bas()
    rng = np.random.default_rng(tohum)
    sd = SensorDizisi(c.dunya, yerlesim, rng)
    e = Esp32Istemci(BellekTasima(c))
    e.baglan()
    return sz, c, e, sd, rng


def kos(sahne_ad, yerlesim, ayar, senaryo, tohum=0, golgeler=(), etkin=True, kayit=False, yuk_olc=False,
        zorla_tetik=None, baslangic=None, t_max=None, ariza=None):
    """Tek koşu. ayar: DenetciAyar (etkin denetçi; etkin False ise yalnız gölge). golgeler: [DenetciAyar].
    ariza: {sensör sırası: "sabit" | "yok"} ya da None. Döner: sonuç sözlüğü (+ kayıt istenmişse '_hakem', '_okuma')."""
    import numpy as np
    duvar0 = time.perf_counter()
    rng0 = np.random.default_rng(10_000 + tohum)
    u = S.al(sahne_ad)
    kenar = u.get("yaklasma") or (u["kenarlar"] or [[1.0, 0.0, S.E]])[0]   # dar açıklık: yakın kenar x = E
    if baslangic is None:
        baslangic = baslangic_pozu(kenar, senaryo, rng0)
    sz, c, e, sd, rng = dunya_kur(sahne_ad, yerlesim, tohum, baslangic)
    for k, v in (ariza or {}).items():
        sd.ayarlar[k].ariza = v
    den = UcurumDenetci(len(yerlesim), ayar) if etkin else None
    gol = [UcurumDenetci(len(yerlesim), g) for g in golgeler]
    c.ucurum_bagla(sd, den, gol, zorla_tetik)
    hk = Hakem(c, u["kenarlar"], yuk_olc=yuk_olc)
    hk.kayit_ac = kayit
    onceki = c.kayitci

    def kanca(cc):
        if onceki is not None:
            onceki(cc)
        hk.guncelle()
    # oturma (motorlar boşta), devreye alma, kalibrasyon (robot duruyor)
    e.bekle(int(YERLESIK * 1000))
    o = e.devreye_al_ve_bekle()
    assert o.get("guc") == "devrede", o
    c.u_kayit = []
    e.bekle(KAL_SURE_MS)
    for i, a in enumerate(sd.ayarlar):
        if a.ariza == "sabit":
            vals = [v for (_, j, v) in c.u_kayit if j == i and v is not None]
            sd.sabit[i] = vals[len(vals) // 2] if vals else 0.06
    beklenen = den.kalibre() if den else None
    for g in gol:
        g.kalibre()
    c.u_kal = False
    c.u_kayit = []
    c.kayitci = kanca
    hk.z0 = None
    t0 = c.dunya.zaman_s
    # sürüş: Pi uçurumu bilmez, komutu 50 ms'de bir yineler
    tur = senaryo["tur"]
    v_k = float(senaryo.get("v", 0.0))
    w_k = float(senaryo.get("w", 0.0))
    if tur == "geri":
        v_k = -abs(v_k)
    if tur == "donus":
        v_k, w_k = 0.0, float(senaryo.get("w", -1.0))
    if t_max is None:
        if tur in ("ileri", "geri"):
            vn = max(abs(v_k) * math.cos(math.radians(senaryo.get("aci", 0.0))), 0.01)
            t_max = min(45.0, 1.2 / vn + 3.0)
        elif tur == "donus":
            t_max = 9.0
        else:
            t_max = float(senaryo.get("t", 12.0))
    dur_bas = None
    bitis = "sure"
    yol_tetik = None
    x_tetik = None
    v_tetik = None
    son_ok = True
    while c.dunya.zaman_s - t0 < t_max:
        cv = e.istek({"k": "sur", "v": round(v_k, 4), "w": round(w_k, 4)}, denetle=False)
        son_ok = bool(cv.get("ok"))
        e.kalp_atisi()
        e.bekle(50)
        t = c.dunya.zaman_s
        if den is not None and den.tetik and x_tetik is None:
            x_tetik = c.u_tetik_poz
            v_tetik = c.u_tetik_v
        if hk.dustu and t - hk.dustu_t > 0.3:
            bitis = "dustu"
            break
        tetik = den.tetik if den is not None else False
        if tetik:
            v, w = c.dunya.hiz()
            if abs(v) < 0.005 and abs(w) < 0.01:
                dur_bas = dur_bas or t
                if t - dur_bas >= 0.3:
                    bitis = "durdu"
                    break
            else:
                dur_bas = None
    x, y, _, yaw, pitch, _ = c.dunya.poz()
    durma_yolu = math.hypot(x - x_tetik[0], y - x_tetik[1]) if x_tetik else None
    r = dict(sahne=sahne_ad, tur=tur, aci=senaryo.get("aci"), v=senaryo.get("v"), w=senaryo.get("w"), d=senaryo.get("d"),
             tohum=tohum, sensor_n=len(yerlesim), bitis=bitis, sure_s=round(c.dunya.zaman_s - t0, 3),
             tetik=bool(den.tetik) if den else None,
             tetik_t=round(den.tetik_t - t0, 3) if (den and den.tetik) else None,
             tetik_sensor=(sd.ayarlar[den.tetik_sensor].ad if (den and den.tetik and den.tetik_sensor >= 0) else
                           ("zorla" if den and den.tetik else None)),
             neden=den.neden if den else None, v_tetik=round(v_tetik, 4) if v_tetik is not None else None,
             durma_yolu_m=round(durma_yolu, 4) if durma_yolu is not None else None,
             dustu=hk.dustu, dustu_neden=hk.dustu_neden,
             pay_min_cm=round(hk.pay_min * 100, 2) if math.isfinite(hk.pay_min) else None,
             pay_min_teker=hk.pay_min_teker, egim_max_der=round(hk.egim_max, 2), pitch_max_der=round(hk.pitch_max, 2),
             dz_min_mm=round(hk.dz_min * 1000, 1), ariza_olay=len(den.ariza_olay) if den else None,
             beklenen_mm=[round(b * 1000, 1) if b is not None else None for b in (beklenen or [])],
             yok_orani=round(den.yok_say / max(den.ornek_say, 1), 3) if den else None,
             duvar_s=round(time.perf_counter() - duvar0, 2), son_sur_ok=son_ok)
    r["golge"] = [dict(anahtar=g.ayar.anahtar(), tetik=g.tetik, tetik_t=(round(g.tetik_t - t0, 3) if g.tetik else None),
                       neden=g.neden) for g in gol]
    if kayit:
        r["_hakem"] = hk.satir
        r["_okuma"] = c.u_kayit
        r["_t0"] = t0
    return r
