"""Y0f: fiziğin cevapladığı sorular. Başsız, tekrarlanabilir ölçümler (aynı girdi = aynı sayı).

    "%LALE_SIM_VENV%\\Scripts\\python.exe" kod/fizik/olcumler.py            # hepsi -> planlama/d158/Y0f-olcum/olcum.json + .md
    ... olcumler.py --yalniz fren,rampa                                     # seçili bölümler
    ... olcumler.py --cikti <klasör>                                        # başka yere yaz (tekrar koşusu karşılaştırması)

Sürüş ölçümleri robotu PROTOKOLDEN sürer (Pi istemcisi -> sahte ESP32 firmware modeli -> fizik dünyası): firmware'in ivme ve
fren sınırları, bekçi, acil stop davranışı aynen uygulanır. Statik / kinematik ölçümler (AM, destek alanı, eğim eşiği) doğrudan
fizik modeline bakar. Her ölçümde el hesabı yanında yazılır; TAHMİN parametreler en az iki değerle koşulur.

Bölümler: model, statik, fren, kol, carpisma, rampa, esik, donus, tork.
"""

import argparse
import json
import math
import os
import sys
import time

BURASI = os.path.dirname(os.path.abspath(__file__))
KOD = os.path.dirname(BURASI)
KOK = os.path.dirname(KOD)
for _y in (os.path.join(KOD, "ortak"), os.path.join(KOD, "pi"), os.path.join(KOD, "araclar"), BURASI):
    if _y not in sys.path:
        sys.path.insert(0, _y)

import dunya as D  # noqa: E402
from fizik_esp32 import FizikEsp32  # noqa: E402
from sahte_esp32.harita import Harita  # noqa: E402
from sahte_esp32.tasima import BellekTasima  # noqa: E402
from lale_pi.istemci import Esp32Istemci  # noqa: E402
import lale_protokol as P  # noqa: E402

G = 9.81
CIKTI = os.path.join(KOK, "planlama", "d158", "Y0f-olcum")
BOS = {"ad": "bos_alan", "boyut_m": [80.0, 80.0], "cevre_duvari": False, "baslangic": {"x": 10.0, "y": 40.0, "aci_derece": 0}}
SERVO = {s["ad"]: s for s in P.servo_tablosu()}
TABAN_ANALIZ = os.path.join(KOK, "tasarim", "freecad", "taban", "taban-analiz.json")

# duyarlılık takımları (TAHMİN parametreler). "ana" = fizik_parametreleri.json değerleri.
TAKIM = {
    "ana": {},
    "mu_0.5": {"teker_zemin_surtunme": 0.5},
    "durma_9kgcm": {"motor_durma_torku_Nm": 0.883},
    "disli_0.2": {"motor_disli_surtunme_Nm": 0.2},
    "atalet_0": {"motor_yansiyan_atalet_kgm2": 0.0},
}
# kol pozları: eklem açısı (derece; servo = eklem + ofset). İki kol aynı.
POZ = {
    "ev": {"omuz": 0, "omuz_yan": 5, "dirsek": 0},
    "kollar_one": {"omuz": 90, "omuz_yan": 5, "dirsek": 0},          # öne tam uzanmış (yatay)
    "kollar_one_yukari": {"omuz": 135, "omuz_yan": 5, "dirsek": 0},
    "kollar_geri": {"omuz": -45, "omuz_yan": 5, "dirsek": 0},
}


def oku(yol):
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


def yuvarla(x, n=4):
    if isinstance(x, float):
        return round(x, n)
    if isinstance(x, (list, tuple)):
        return [yuvarla(v, n) for v in x]
    if isinstance(x, dict):
        return {k: yuvarla(v, n) for k, v in x.items()}
    return x


def poz_servo(poz, iki_kol=True):
    """Kol pozu (eklem derecesi) -> {servo adı: servo açısı}."""
    s = {}
    for t in (("sag", "sol") if iki_kol else ("sag",)):
        for k, a in poz.items():
            ad = "%s_%s" % (t, k)
            s[ad] = a + SERVO[ad]["ofset"]
    return s


# ====================================================================== deney düzeneği (protokol üstünden)
class Deney:
    def __init__(self, degis=None, sahne=None, konum=(10.0, 40.0, 0.0), poz=None, harita=None, sonar_acik=True, varyant=None):
        h = Harita(dict(BOS, baslangic={"x": konum[0], "y": konum[1], "aci_derece": math.degrees(konum[2])})) \
            if harita is None else harita
        # varyant: yalnız olcum_varyantlar.py (VARSAYIM); bu dosyanın ölçümleri hep None (bugünkü robot)
        self.c = FizikEsp32(h, konum=konum, sahne=sahne, degis=degis, sonar_acik=sonar_acik, varyant=varyant)
        self.w = self.c.dunya
        if poz is not None:                          # ölçüm kurulumu: kollar pozda başlar (servo hedefi de)
            for ad, a in poz_servo(poz).items():
                i = self.c.servo_adlari.index(ad)
                self.c.servo_hedef[i] = self.c.servo_simdi[i] = float(a)
            self.w.servo_eklem_ayarla({ad: math.radians(a - SERVO[ad]["ofset"]) for ad, a in poz_servo(poz).items()})
        self.t = BellekTasima(self.c)
        self.e = Esp32Istemci(self.t)
        self.e.baglan()
        self.kayit = []
        self._k = False
        self.w.adim_kaydi = self._kaydet
        self.w.adim(0.3, suruluyor=False)             # yerleşme (temas)
        self.n0 = self.w.teker_yukleri()
        self.z_teker0 = [float(self.w.d.xpos[self.w.m.body("teker_%s" % t).id][2]) for t in ("on_sol", "arka_sol", "on_sag", "arka_sag")]

    def devreye_al(self):
        o = self.e.devreye_al_ve_bekle()
        assert o.get("guc") == "devrede", o

    def kayit_ac(self):
        self.kayit = []
        self._k = True

    def _kaydet(self, w):
        if not self._k:
            return
        d = w.d
        import mujoco
        mujoco.mj_subtreeVel(w.m, d)
        v_am = d.subtree_linvel[w.taban]
        R = d.xmat[w.taban].reshape(3, 3)
        x, y, z, yaw, pitch, roll = w.poz()
        self.kayit.append(dict(
            t=w.zaman_s, v=float(R[:, 0] @ d.qvel[0:3]), v_am=float(R[:, 0] @ v_am), w=float((R @ d.qvel[3:6])[2]),
            ay=float(R[:, 1] @ v_am), x=x, y=y, yaw=yaw, pitch=pitch, roll=roll, N=w.teker_yukleri(),
            zt=[float(d.xpos[b][2]) for b in self._teker_govde()], tork=list(w.son_tork), wt=w.teker_hizlari(),
            govde_zemin=w.govde_zemine_degiyor(), rh=list(self.c.rampa_hiz)))

    def _teker_govde(self):
        if not hasattr(self, "_tg"):
            self._tg = [self.w.m.body("teker_%s" % t).id for t in ("on_sol", "arka_sol", "on_sag", "arka_sag")]
        return self._tg


def ivme_serisi(kayit, alan="v_am", pencere=5):
    """(t, a) dizisi: alan'ın `pencere` adımlık merkezi farkı (1 ms adımda 5 ms)."""
    a = []
    for i in range(pencere, len(kayit) - pencere):
        dt = kayit[i + pencere]["t"] - kayit[i - pencere]["t"]
        a.append((kayit[i]["t"], (kayit[i + pencere][alan] - kayit[i - pencere][alan]) / dt))
    return a


def am_ve_destek(w):
    """Model AM'si (dünya) ve destek dikdörtgeni payları: tekerlerin zemin temas noktalarına göre (robot çerçevesi)."""
    import numpy as np
    c = np.array(w.am())
    R = w.d.xmat[w.taban].reshape(3, 3)
    p0 = w.d.xpos[w.taban]
    yerel = R.T @ (c - p0)
    tx = [R.T @ (w.d.xpos[w.m.body("teker_%s" % t).id] - p0) for t in ("on_sol", "arka_sol", "on_sag", "arka_sag")]
    on = max(t[0] for t in tx)
    arka = min(t[0] for t in tx)
    sol = max(t[1] for t in tx)
    sag = min(t[1] for t in tx)
    return dict(am_m=[float(v) for v in yerel], h_m=float(yerel[2]), d_on_m=float(on - yerel[0]), d_arka_m=float(yerel[0] - arka),
                d_sol_m=float(sol - yerel[1]), d_sag_m=float(yerel[1] - sag))


def el_hesabi(ds):
    h = ds["h_m"]
    r = {}
    for yon, d in (("ileri", ds["d_on_m"]), ("geri", ds["d_arka_m"]), ("yan", min(ds["d_sol_m"], ds["d_sag_m"]))):
        r[yon] = dict(devrilme_ivmesi_m_s2=G * d / h, statik_devrilme_egimi_derece=math.degrees(math.atan(d / h)))
    return r


# ====================================================================== 1) model doğrulama
def olc_model():
    import numpy as np
    w = D.FizikDunya(None, None, (0, 0, 0))
    w.adim(0.5)
    kars = oku(os.path.join(BURASI, "model", "kutle_karsilastirma.json"))
    ta = oku(TABAN_ANALIZ)
    N = w.teker_yukleri()
    sonuc = dict(
        mujoco_toplam_kutle_kg=float(sum(w.m.body_mass)), model_uret_kutle_kg=kars["model"]["kutle_kg"],
        mujoco_am_m=w.am(), model_uret_am_m=kars["model"]["am_m"],
        aks_yuk_N=dict(on=N[0] + N[2], arka=N[1] + N[3], el_hesabi_taban_analiz=ta["aks"]),
        pozlar=[])
    # taban-analiz pozları: "sag" = CAD sağı = robotun kendi SOLU (K65)
    for p in ta["robot"]["pozlar"]:
        if p.get("yuk"):
            continue
        cad_sag, cad_sol = p["sag"], p["sol"]
        hedef = {}
        for robot_taraf, (s1, s2, dr) in (("sol", cad_sag), ("sag", cad_sol)):
            s2 = max(s2, 0)
            hedef.update({"%s_omuz" % robot_taraf: math.radians(s1), "%s_omuz_yan" % robot_taraf: math.radians(s2),
                          "%s_dirsek" % robot_taraf: math.radians(dr)})
        w2 = D.FizikDunya(None, None, (0, 0, 0))
        w2.servo_eklem_ayarla(hedef)
        import mujoco
        mujoco.mj_forward(w2.m, w2.d)
        c = np.array(w2.am()) * 1000.0
        cad = [p["am"][2], p["am"][0], p["am"][1]]
        sonuc["pozlar"].append(dict(kod=p["kod"], ad=p["ad"], cad_eklem_sag_sol=[cad_sag, cad_sol],
                                    model_am_mm=[float(v) for v in c], taban_analiz_am_mm=cad,
                                    fark_mm=[float(c[i] - cad[i]) for i in range(3)]))
    return sonuc


# ====================================================================== 2) statik devrilme eğimi (yerçekimi eğdirilerek)
def olc_statik():
    """Tekerler kilitli (büyük eklem sönümü), yerçekimi yönü eğdirilir = eğik zemin. Açı el hesabının 3 derece altından
    0,1 derece adımla artırılır (her adımda 1 s yerleşme); taban 0,5 dereceden çok dönünce devrilme başladı sayılır
    (çözünürlük 0,1 derece). Silindir teker - düzlem temasında teker yükleri ±3 N oynadığı için yük ölçüt değil."""
    sonuc = {}
    for poz_ad in ("ev", "kollar_one", "kollar_one_yukari", "kollar_geri"):
        r = {}
        for yon, eksen in (("ileri", (1, 0)), ("geri", (-1, 0)), ("yan_sol", (0, 1)), ("yan_sag", (0, -1))):
            w = D.FizikDunya(None, None, (0, 0, 0), degis={"teker_zemin_surtunme": 1.5})
            w.servo_eklem_ayarla({ad: math.radians(a - SERVO[ad]["ofset"]) for ad, a in poz_servo(POZ[poz_ad]).items()})
            for dof in w.teker_dof:
                w.m.dof_damping[dof] = 1e5                 # teker kilidi (frenli park); sürtünme kaybı kısıtı kaydırıyordu
            ds = am_ve_destek(w)
            eh = el_hesabi(ds)["ileri" if yon == "ileri" else "geri" if yon == "geri" else "yan"]
            # yokuş yukarı tekerler: ileri devrilme (burun aşağı) -> arka tekerler yükü boşalır
            bulunan = None
            aci = max(0.0, round(eh["statik_devrilme_egimi_derece"]) - 3.0)
            while aci < 40.0:
                th = math.radians(aci)
                w.m.opt.gravity[:] = (G * math.sin(th) * eksen[0], G * math.sin(th) * eksen[1], -G * math.cos(th))
                w.adim(1.0)
                if w.egim() > math.radians(0.5):         # gövde gerçekten dönmeye başladı (teker yükü gürültülü: ölçüt değil)
                    bulunan = aci
                    break
                aci = round(aci + 0.1, 3)
            r[yon] = dict(fizik_derece=bulunan, el_hesabi_derece=eh["statik_devrilme_egimi_derece"],
                          fark_derece=None if bulunan is None else bulunan - eh["statik_devrilme_egimi_derece"],
                          am_yuksekligi_m=ds["h_m"], d_m={"ileri": ds["d_on_m"], "geri": ds["d_arka_m"],
                                                         "yan_sol": ds["d_sol_m"], "yan_sag": ds["d_sag_m"]}[yon])
        sonuc[poz_ad] = r
    return sonuc


# ====================================================================== 3) fren / acil stop / bekçi: devrilme
def fren_kos(durus, yon, poz_ad, takim, fren_degeri=None):
    dn = Deney(degis=TAKIM[takim], poz=POZ[poz_ad])
    if fren_degeri is not None:
        dn.c.ivme["duz"] = (dn.c.ivme["duz"][0], fren_degeri)
    dn.devreye_al()
    v = 1.0 if yon == "ileri" else -1.0
    dn.e.sur_tut(v, 0.0, 2500)                     # azami hız (firmware teker azamisine kırpar)
    dn.kayit_ac()
    i0 = 0
    if durus == "dur":
        dn.e.istek({"k": "dur"})
        dn.e.bekle(2500)
    elif durus == "bekci":
        dn.e.bekle(3000)                              # son sur'dan 500 ms sonra bekçi: ani dur (EN HIGH, PWM 0 = fren)
    elif durus == "acil_stop":
        dn.c.mantar = True                            # mantar: röle bobini düşer, EN LOW, bara gider = boşta
        dn.e.bekle(8000)
    k = dn.kayit[i0:]
    # duruş başlangıcı: hız mutlak değeri ilk kez başlangıcın %98'inin altına indiği an
    v0 = k[0]["v_am"]
    bas = next((i for i, r in enumerate(k) if abs(r["v_am"]) < 0.98 * abs(v0)), 0)
    dur_i = next((i for i, r in enumerate(k) if i > bas and abs(r["v"]) < 0.005), None)
    a = ivme_serisi(k)                                # pencere 5 adım: ±5 ms = 10 ms merkezi fark
    a_tepe = max((-x if v > 0 else x) for _, x in a) if a else 0.0
    a2 = ivme_serisi(k, pencere=1)                    # ±1 ms = 2 ms merkezi fark (K3: tepe pencereye bağlı)
    a_tepe_2ms = max((-x if v > 0 else x) for _, x in a2) if a2 else 0.0
    ust = (1, 3) if v > 0 else (0, 2)                # boşalan aks: ileri giderken frende arka
    n_min = min(r["N"][ust[0]] + r["N"][ust[1]] for r in k)
    sifir_ms = sum(1 for r in k if r["N"][ust[0]] + r["N"][ust[1]] < 1.0) * dn.w.m.opt.timestep * 1000.0
    kalkma_mm = max(max(r["zt"][j] - dn.z_teker0[j] for j in ust) for r in k) * 1000.0
    pitch = max(abs(r["pitch"]) for r in k)
    ds = am_ve_destek(dn.w)
    eh = el_hesabi(ds)["ileri" if v > 0 else "geri"]
    n0 = dn.n0[ust[0]] + dn.n0[ust[1]]
    L = 0.37
    mtop = float(sum(dn.w.m.body_mass))
    return dict(durus=durus, yon=yon, poz=poz_ad, takim=takim, fren_degeri=fren_degeri,
                v0_m_s=v0, tepe_yavaslama_m_s2=a_tepe, tepe_yavaslama_2ms_m_s2=a_tepe_2ms,
                ort_yavaslama_m_s2=(abs(v0) / (k[dur_i]["t"] - k[bas]["t"]) if dur_i else None),
                durma_suresi_s=(k[dur_i]["t"] - k[bas]["t"]) if dur_i else None,
                durma_yolu_m=(math.hypot(k[dur_i]["x"] - k[bas]["x"], k[dur_i]["y"] - k[bas]["y"]) if dur_i else None),
                son_hiz_m_s=k[-1]["v"],
                bosalan_aks_statik_N=n0, bosalan_aks_en_az_N=n_min, bosalan_aks_sifir_ms=sifir_ms,
                teker_kalkma_mm=kalkma_mm, en_buyuk_egim_derece=math.degrees(pitch),
                govde_zemine_degdi=any(r["govde_zemin"] for r in k),
                el_hesabi=dict(devrilme_ivmesi_m_s2=eh["devrilme_ivmesi_m_s2"], pay=eh["devrilme_ivmesi_m_s2"] / a_tepe if a_tepe else None,
                               bosalan_aks_beklenen_N=n0 - mtop * a_tepe * ds["h_m"] / L,
                               formul="a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"))


def olc_fren():
    kos = []
    for takim in TAKIM:
        for poz_ad in ("ev", "kollar_one"):
            for durus in ("dur", "bekci", "acil_stop"):
                for yon in ("ileri", "geri"):
                    if takim != "ana" and poz_ad != "ev":
                        continue
                    kos.append(fren_kos(durus, yon, poz_ad, takim))
    # yük aktarımı eğrisi: firmware fren değeri değiştirilerek (bilgi; firmware 1,8)
    egri = [fren_kos("dur", "ileri", "ev", "ana", fren_degeri=a) for a in (1.0, 1.8, 2.5, 3.0, 4.0)]
    # K3 (düzeltme turu): bekçi duruşu (ileri, ev pozu) durma torku ve sayısal / temas ayarlarıyla
    bekci = []
    for ad, degis in (("ana", {}), ("durma_15kgcm", {"motor_durma_torku_Nm": 1.471}),
                      ("durma_9kgcm", {"motor_durma_torku_Nm": 0.883}), ("solref_0.002", {"temas_solref_s": 0.002}),
                      ("solref_0.008", {"temas_solref_s": 0.008}), ("dt_0.5ms", {"zaman_adimi_s": 0.0005})):
        TAKIM["_gecici"] = degis
        r = fren_kos("bekci", "ileri", "ev", "_gecici")
        del TAKIM["_gecici"]
        r["takim"] = ad
        bekci.append(r)
    # K7 (düzeltme turu): acil stop boşta kayması yansıyan atalet x dişli sürtünmesi aralığında (ileri, ev pozu)
    acil = []
    for J in (0.0, 0.005, 0.01, 0.015):
        for g in (0.05, 0.2):
            TAKIM["_gecici"] = {"motor_yansiyan_atalet_kgm2": J, "motor_disli_surtunme_Nm": g}
            r = fren_kos("acil_stop", "ileri", "ev", "_gecici")
            del TAKIM["_gecici"]
            acil.append(dict(yansiyan_atalet_kgm2=J, disli_surtunme_Nm=g, v0_m_s=r["v0_m_s"], durma_yolu_m=r["durma_yolu_m"],
                             durma_suresi_s=r["durma_suresi_s"], ort_yavaslama_m_s2=r["ort_yavaslama_m_s2"]))
    return dict(kosular=kos, fren_egrisi=egri, bekci_duyarlilik=bekci, acil_stop_araligi=acil,
                not_="tepe yavaşlama AM hızının 10 ms (±5 adım) merkezi farkından, tepe_yavaslama_2ms ±1 adımdan; boşalan aks = "
                     "frende yükü azalan aks (ileri giderken arka); teker_kalkma_mm boşalan aks tekerlerinin merkez yüksekliği artışı")


# ====================================================================== 4) kol hareketi: AM ve devrilme payı; dinamik kol salınımı
def olc_kol():
    import itertools
    sonuc = dict(izgara=[], en_kotu={}, dinamik=[])
    fren, rampa_fren = 1.8, 0.1
    w = D.FizikDunya(None, None, (0, 0, 0))
    S1 = list(range(-45, 136, 15))
    S2 = [5, 30, 60, 90, 120]
    DR = [0, 35, 70, 105]
    for tek_kol in (False, True):
        for s1, s2, dr in itertools.product(S1, S2, DR):
            if s1 >= 120 and s2 > 117:
                s2 = 117                                   # bağımlı sınır (eklem_sinirlari.json bagimli)
            hedef = {}
            for t in (("sag",) if tek_kol else ("sag", "sol")):
                hedef.update({"%s_omuz" % t: math.radians(s1), "%s_omuz_yan" % t: math.radians(s2), "%s_dirsek" % t: math.radians(dr)})
            if tek_kol:
                hedef.update({"sol_omuz": 0.0, "sol_omuz_yan": math.radians(5), "sol_dirsek": 0.0})
            w.servo_eklem_ayarla(hedef)
            ds = am_ve_destek(w)
            eh = el_hesabi(ds)
            pay = {y: eh[y]["devrilme_ivmesi_m_s2"] / fren for y in ("ileri", "geri", "yan")}
            # 5 derece rampada geri (yokuş yukarı giderken durunca): a_dev = g (d cos5 - h sin5) / h, fren 0,1
            th = math.radians(5)
            a5 = G * (ds["d_arka_m"] * math.cos(th) - ds["h_m"] * math.sin(th)) / ds["h_m"]
            sonuc["izgara"].append(dict(tek_kol=tek_kol, s1=s1, s2=s2, dirsek=dr, am_m=ds["am_m"], d_on=ds["d_on_m"],
                                        d_arka=ds["d_arka_m"], d_yan=min(ds["d_sol_m"], ds["d_sag_m"]),
                                        a_dev=dict((y, eh[y]["devrilme_ivmesi_m_s2"]) for y in eh), pay_fren_1_8=pay,
                                        rampa5_geri_a_dev=a5))
    for y in ("ileri", "geri", "yan"):
        e = min(sonuc["izgara"], key=lambda r: r["a_dev"][y])
        sonuc["en_kotu"][y] = dict(poz=[e["s1"], e["s2"], e["dirsek"]], tek_kol=e["tek_kol"], a_dev=e["a_dev"][y], pay=e["pay_fren_1_8"][y])
    e = min(sonuc["izgara"], key=lambda r: r["rampa5_geri_a_dev"])
    sonuc["en_kotu"]["rampa5_geri"] = dict(poz=[e["s1"], e["s2"], e["dirsek"]], tek_kol=e["tek_kol"], a_dev=e["rampa5_geri_a_dev"])
    sonuc["izgara_ozet"] = dict(poz_sayisi=len(sonuc["izgara"]), am_x_aralik_mm=[min(r["am_m"][0] for r in sonuc["izgara"]) * 1000,
                                                                              max(r["am_m"][0] for r in sonuc["izgara"]) * 1000],
                                am_z_aralik_mm=[min(r["am_m"][2] for r in sonuc["izgara"]) * 1000, max(r["am_m"][2] for r in sonuc["izgara"]) * 1000])
    # dinamik: robot devrede ve dururken iki kol S1 -45 -> 135 -> -45 servo hızıyla (85 derece/s), protokolden
    for takim in ("ana", "mu_0.5"):
        dn = Deney(degis=TAKIM[takim], poz=POZ["kollar_geri"])
        dn.devreye_al()
        dn.kayit_ac()
        for a in (135, -45, 135):
            for t in ("sag", "sol"):
                dn.e.istek({"k": "servo", "kanal": "%s_omuz" % t, "aci": a + SERVO["%s_omuz" % t]["ofset"]})
            for _ in range(5):
                dn.e.ping()
                dn.e.bekle(500)
        k = dn.kayit
        nmin = [min(r["N"][i] for r in k) for i in range(4)]
        sonuc["dinamik"].append(dict(takim=takim, hareket="iki kol S1 -45 -> 135 -> -45 -> 135 (85 derece/s, protokol servo)",
                                     teker_yuk_en_az_N=nmin, teker_yuk_statik_N=dn.n0,
                                     taban_en_buyuk_egim_derece=math.degrees(max(abs(r["pitch"]) for r in k)),
                                     yer_degistirme_mm=1000 * math.hypot(k[-1]["x"] - k[0]["x"], k[-1]["y"] - k[0]["y"])))
    sonuc["izgara"] = [r for r in sonuc["izgara"] if r["s2"] in (5, 90) and r["dirsek"] in (0, 105)]   # raporda kısaltılmış
    return sonuc


# ====================================================================== 5) rampa
def sonar_kisti(k, v_komut, azami=0.39):
    """Firmware sonar yavaşlatması (TASLAK kural) devreye girdi mi: rampa hızı komut hedefinin %90'ının altına indi mi."""
    hedef = min(abs(v_komut), 1.0) * azami
    tepe = max((max(abs(x) for x in r["rh"]) for r in k), default=0.0)
    son = [max(abs(x) for x in r["rh"]) for r in k[len(k) // 2:]]
    return bool(tepe > 0.5 * hedef and son and min(son) < 0.9 * hedef)


def rampa_kos(egim, takim, v_komut=1.0, rampa_kipi=True, sonar_acik=False):
    L = 3.0
    sahne = {"rampalar": [{"x": 11.0, "y": 40.0, "aci_derece": 0, "egim_derece": egim, "uzunluk_m": L, "genislik_m": 1.2,
                           "ust_uzunluk_m": 3.0}]}
    dn = Deney(degis=TAKIM[takim], sahne=sahne, konum=(10.0, 40.0, 0.0), sonar_acik=sonar_acik)
    dn.devreye_al()
    if rampa_kipi:
        dn.e.istek({"k": "rampa", "ac": True})
    dn.kayit_ac()
    sonuc = dict(egim_derece=egim, takim=takim, v_komut=v_komut, rampa_kipi=rampa_kipi, sonar_acik=sonar_acik)
    # rampanın ortasına dek sür (en çok 25 s)
    hedef_x = 11.0 + L * 0.5
    dn.e.sur_tut(v_komut, 0.0, 25000, dur_kosul=lambda e: dn.c.x >= hedef_x or abs(dn.w.egim()) > math.radians(egim + 15))
    k = dn.kayit
    ulasti = dn.c.x >= hedef_x
    rampada = [r for r in k if r["x"] > 11.5 and r["x"] < hedef_x]
    sonuc["rampanin_ortasina_ulasti"] = ulasti
    sonuc["sonar_yavaslatti"] = sonar_kisti(k, v_komut)
    sonuc["son_x_m"] = dn.c.x
    sonuc["rampada_hiz_m_s"] = (sum(r["v"] for r in rampada[-500:]) / len(rampada[-500:])) if rampada else None
    sonuc["rampada_tork_Nm_teker_ort"] = (sum(sum(abs(t) for t in r["tork"]) / 4 for r in rampada[-500:]) / len(rampada[-500:])) if rampada else None
    sonuc["tepe_tork_Nm"] = max(max(abs(t) for t in r["tork"]) for r in k)
    # devrilme: taban eğimi rampa eğiminden 8 dereceden çok saptı (geri yatma) ya da gövde zemine değdi
    devrildi = any(abs(r["pitch"]) > math.radians(egim + 8) or r["govde_zemin"] for r in k)
    sonuc["geri_devrildi"] = any(abs(r["pitch"]) > math.radians(egim + 8) for r in k)
    # rampada dur: firmware fren (rampa kipinde 0,1 m/s2) sonra PWM 0 + EN HIGH (kısa devre freni); 5 s tut
    # Ölçüt (düzeltme turu, K2): `dur` anından değil, robotun yukarı süzülmesi bittiği andan (dur sonrası en yüksek x)
    # sayılır. Süzülme rampa kipinin 0,1 m/s2 fren rampasından gelir (0,39 m/s'den ≈ 3,9 s); dur sonrası 15 s izlenir.
    # Bildirilen: süzülme yolu, süzülme bittikten sonra 5 s'de geri kayma (yol) ve son 2 s'nin ortalama hızı (sürekli kayma).
    x_dur = dn.c.x
    i_dur = len(dn.kayit)
    dn.e.istek({"k": "dur"})
    for _ in range(30):
        dn.e.ping()                                   # sessizlik (5 s) tetiklenmesin: güç devrede kalır
        dn.e.bekle(500)
    k2 = dn.kayit
    sonra = k2[i_dur:]
    tepe = max(sonra, key=lambda r: r["x"])
    t_tepe = tepe["t"]
    pencere = [r for r in sonra if t_tepe <= r["t"] <= t_tepe + 5.0]
    son2 = [r for r in pencere if r["t"] >= t_tepe + 3.0]
    tam = bool(sonra) and sonra[-1]["t"] >= t_tepe + 5.0
    kayma_5s = (tepe["x"] - pencere[-1]["x"]) if (ulasti and tam) else None
    v_surekli = (sum(r["v"] for r in son2) / len(son2)) if (ulasti and tam and son2) else None
    sonuc.update(dur_sonrasi_yukari_suzulme_m=(tepe["x"] - x_dur) if ulasti else None,
                 dur_sonrasi_suzulme_suresi_s=(t_tepe - sonra[0]["t"]) if ulasti else None,
                 suzulme_sonrasi_5s_geri_kayma_m=kayma_5s,
                 suzulme_sonrasi_surekli_kayma_hizi_m_s=v_surekli,
                 dur_sonrasi_tutuyor=(kayma_5s is not None and kayma_5s < 0.001),
                 dur_sonrasi_son_hiz_m_s=k2[-1]["v"],
                 devrildi_ya_da_govde_degdi=devrildi or any(r["govde_zemin"] for r in k2),
                 en_buyuk_egim_derece=math.degrees(max(abs(r["pitch"]) for r in k2)))
    p = dn.w.p
    m = float(sum(dn.w.m.body_mass))
    r_t = 0.0625
    th = math.radians(egim)
    T_tut = m * G * math.sin(th) * r_t / 4.0                       # durmak için teker başına gereken tutma torku
    T_cik = (m * G * (math.sin(th) + p["yuvarlanma_direnci_katsayisi"] * math.cos(th)) * r_t / 4.0) + p["motor_disli_surtunme_Nm"]
    sonuc["el_hesabi"] = dict(teker_basi_tutma_torku_Nm=T_tut, eklem_surtunmesi_Nm=dn.w.teker_surtunme,
                              teker_basi_cikis_torku_Nm=T_cik, durma_torku_orani=T_cik / p["motor_durma_torku_Nm"],
                              surekli_tork_orani=T_cik / p["motor_surekli_torku_Nm"],
                              kisa_devre_freninde_kayma_hizi_m_s=max(0.0, (T_tut - dn.w.teker_surtunme)) / (p["motor_durma_torku_Nm"] / dn.w.w0) * r_t)
    return sonuc


def olc_rampa():
    kos = []
    for takim in ("ana", "mu_0.5", "durma_9kgcm", "disli_0.2"):
        for egim in (3, 5, 8, 10, 12, 15, 20):
            if takim != "ana" and egim not in ((3, 5, 10, 15) if takim == "disli_0.2" else (5, 10, 15)):
                continue
            kos.append(rampa_kos(egim, takim))
    for egim in (5, 10, 15, 20):
        kos.append(rampa_kos(egim, "ana", sonar_acik=True))
    return dict(kosular=kos, not_="rampa kipi açık (firmware ivme / fren 0,1 m/s2), sur v = 1 (teker azamisi); 3 m rampa + platform; "
                                  "sonar_acik False = mekanik sığa (firmware sonar yavaşlatması kapalı), True = firmware sonar kuralı açık")


# ====================================================================== 6) eşik
def esik_kos(h_mm, takim, v_komut, sonar_acik=False):
    sahne = {"esikler": [{"x": 11.0, "y": 40.0, "aci_derece": 0, "yukseklik_mm": h_mm, "genislik_m": 1.2, "derinlik_m": 1.5}]}
    dn = Deney(degis=TAKIM[takim], sahne=sahne, konum=(10.3, 40.0, 0.0), sonar_acik=sonar_acik)
    dn.devreye_al()
    dn.kayit_ac()
    dn.e.sur_tut(v_komut, 0.0, 8000, dur_kosul=lambda e: dn.c.x > 11.6)
    k = dn.kayit
    h = h_mm / 1000.0
    on = max(min(r["zt"][0], r["zt"][2]) for r in k) - dn.z_teker0[0]
    arka = max(min(r["zt"][1], r["zt"][3]) for r in k) - dn.z_teker0[1]
    return dict(yukseklik_mm=h_mm, takim=takim, v_komut=v_komut, sonar_acik=sonar_acik, sonar_yavaslatti=sonar_kisti(k, v_komut),
                gecti=dn.c.x > 11.6 and arka > 0.8 * h,
                on_teker_cikti=on > 0.8 * h, arka_teker_cikti=arka > 0.8 * h, govde_degdi=any(r["govde_zemin"] for r in k),
                son_x_m=dn.c.x, tepe_tork_Nm=max(max(abs(t) for t in r["tork"]) for r in k),
                en_buyuk_egim_derece=math.degrees(max(abs(r["pitch"]) for r in k)))


def olc_esik():
    kos = []
    for takim in ("ana", "mu_0.5", "durma_9kgcm"):
        for v in (0.2, 1.0):
            for h in (5, 10, 15, 20, 25, 30, 40):
                if takim != "ana" and v != 1.0:
                    continue
                kos.append(esik_kos(h, takim, v))
    for v in (0.2, 1.0):
        for h in (5, 15, 30, 40):
            kos.append(esik_kos(h, "ana", v, sonar_acik=True))
    # el hesabı: tek tekerin basamağa tırmanması (statik, sürtünme sınırı): h_max = r (1 - cos(atan mu)) yaklaşık
    eh = {}
    for mu in (0.5, 0.8):
        eh["mu_%s" % mu] = dict(on_teker_h_mm=62.5 * (1 - 1 / math.sqrt(1 + mu * mu)),
                                aciklama="yalnız basamağa dayanan teker kendi sürtünmesiyle (itilmeden): h = r (1 - cos atan mu)")
    eh["etek_yuksekligi_mm"] = 35.0
    eh["not_"] = "arkadaki tahrikli tekerlerin itmesi öndekini kolaylaştırır; etek alt kenarı 35 mm (Kabuk 'Etek' parçaları)"
    return dict(kosular=kos, el_hesabi=eh)


# ====================================================================== 7) dönüş
def donus_kos(v, w_cmd, takim, sure=3000, tam_pwm=False):
    """tam_pwm: firmware'in açık çevrim eşlemesi (u = rampa_hiz / 0,39; w girişi 1 rad/s'ye kırpılı) yerine sürücüye
    doğrudan u = -1 / +1 (yerinde dönüş, tam PWM): motorun kendisinin yetip yetmediği."""
    dn = Deney(degis=TAKIM[takim])
    dn.devreye_al()
    if tam_pwm:
        dn.c.pwm_zorla = [-1.0, 1.0] if w_cmd > 0 else [1.0, -1.0]
    dn.e.sur_tut(v, w_cmd, sure)
    dn.kayit_ac()
    dn.e.sur_tut(v, w_cmd, 1000)
    k = dn.kayit
    w_ort = sum(r["w"] for r in k) / len(k)
    v_ort = sum(r["v"] for r in k) / len(k)
    hedef = dn.c._teker_hedefleri(max(-1, min(1, v)), max(-1, min(1, w_cmd)))
    w_hedef = (hedef[1] - hedef[0]) / 0.432
    v_hedef = (hedef[0] + hedef[1]) / 2
    return dict(v_komut=v, w_komut=w_cmd, takim=takim, teker_hedef_m_s=hedef, v_hedef=v_hedef, w_hedef_rad_s=w_hedef,
                v_olculen=v_ort, w_olculen_rad_s=w_ort, w_orani=(w_ort / w_hedef) if w_hedef else None,
                yanal_ivme_m_s2=max(abs(r["ay"]) for r in k) if k else None,
                en_buyuk_yatma_derece=math.degrees(max(abs(r["roll"]) for r in k)),
                teker_yuk_en_az_N=min(min(r["N"]) for r in k), tork_ort_Nm=[sum(abs(r["tork"][i]) for r in k) / len(k) for i in range(4)])


def olc_donus():
    kos = []
    for takim in ("ana", "mu_0.5", "durma_9kgcm"):
        kos.append(donus_kos(0.0, 1.0, takim))      # yerinde, firmware w azamisi
        kos.append(donus_kos(1.0, 1.0, takim))      # azami hız + azami w
        kos.append(donus_kos(0.3, 0.5, takim))
    esik = []
    for mu in (0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.8):
        for st in (2.059, 0.883):
            dn_takim = {"teker_zemin_surtunme": mu, "motor_durma_torku_Nm": st}
            TAKIM["_gecici"] = dn_takim
            r = donus_kos(0.0, 1.0, "_gecici", sure=2000)
            del TAKIM["_gecici"]
            esik.append(dict(mu=mu, durma_torku_Nm=st, w_olculen_rad_s=r["w_olculen_rad_s"], w_hedef_rad_s=r["w_hedef_rad_s"]))
    # K1 (düzeltme turu): aynı yerinde dönüş firmware eşlemesiyle (u ≈ 0,55) ve tam PWM'de (u = 1)
    pwm = []
    for mu in (0.4, 0.5, 0.8):
        for st in (2.059, 0.883):
            for tam in (False, True):
                TAKIM["_gecici"] = {"teker_zemin_surtunme": mu, "motor_durma_torku_Nm": st}
                r = donus_kos(0.0, 1.0, "_gecici", sure=2000, tam_pwm=tam)
                del TAKIM["_gecici"]
                pwm.append(dict(mu=mu, durma_torku_Nm=st, surus="tam_pwm_u1" if tam else "firmware_u0.55",
                                w_olculen_rad_s=r["w_olculen_rad_s"], tork_ort_Nm=r["tork_ort_Nm"]))
    ta = oku(TABAN_ANALIZ)
    yer = [dict(mu=y["mu"], en_cok_kgcm=y["en_cok_kgcm"], oran_stall=y["en_cok_oran_stall"], omni=y["tekerler"][0]["omni"])
           for y in ta["donus"].get("yerinde", [])]
    return dict(kosular=kos, yerinde_donus_mu_esigi=esik, yerinde_firmware_ve_tam_pwm=pwm, el_hesabi_taban_analiz_yerinde=yer,
                el_hesabi_tek_formul="sürekli yerinde dönüşte teker başına F = mu N 0,65 (L/T = 0,37/0,432; Coulomb), "
                                     "T = F r; firmware w = 1 rad/s'de u = 0,213/0,39 = 0,55 -> durmada T = 0,55 x 1,09 x T_durma")


# ====================================================================== 8) motor torku: kalkış
def olc_tork():
    """Kalkış torku. Eğim yerçekimi eğdirilerek verilir (robot düz zeminde, g dünya -x'e eğik = +x yokuş yukarı): rampa
    geometrisi gerekmez. Devreye alınırken tekerler kilitli tutulur (kalkış duruştan)."""
    kos = []
    p = D.parametreler()
    for takim in ("ana", "durma_9kgcm"):
        for egim, kip, v in ((0, False, 0.3), (0, False, 1.0), (5, True, 1.0), (5, False, 1.0), (10, True, 1.0)):
            dn = Deney(degis=TAKIM[takim])
            th = math.radians(egim)
            dn.w.m.opt.gravity[:] = (-G * math.sin(th), 0.0, -G * math.cos(th))
            for dof in dn.w.teker_dof:
                dn.w.m.dof_frictionloss[dof] = 50.0
            dn.devreye_al()
            if kip:
                dn.e.istek({"k": "rampa", "ac": True})
            dn.e.bekle(300)
            for dof in dn.w.teker_dof:
                dn.w.m.dof_frictionloss[dof] = dn.w.teker_surtunme
            dn.kayit_ac()
            dn.e.sur_tut(v, 0.0, 8000)
            k = dn.kayit
            pk = D.parametreler(TAKIM[takim])
            tepe = max(max(abs(t) for t in r["tork"]) for r in k)
            son = k[-300:]
            surekli = sum(sum(t for t in r["tork"]) / 4 for r in son) / len(son)
            geri = min(r["v"] for r in k[:400])
            m = float(sum(dn.w.m.body_mass))
            a_hed = 0.1 if kip else 0.5
            T_el = (m * (G * math.sin(th) + a_hed + G * math.cos(th) * p["yuvarlanma_direnci_katsayisi"]) * 0.0625 / 4.0
                    + p["motor_disli_surtunme_Nm"])
            kos.append(dict(takim=takim, egim_derece=egim, rampa_kipi=kip, v_komut=v, tepe_tork_Nm=tepe,
                            tepe_durma_orani=tepe / pk["motor_durma_torku_Nm"], tepe_surekli_orani=tepe / pk["motor_surekli_torku_Nm"],
                            sabit_hizda_tork_Nm=surekli, sabit_hiz_m_s=sum(r["v"] for r in son) / len(son),
                            kalkista_geri_kayma_hizi_m_s=min(0.0, geri),
                            el_hesabi_tork_Nm=T_el, el_hesabi_formul="T = m (g sin a + a_firmware + g cos a crr) r / 4 + disli"))
    ta = oku(TABAN_ANALIZ)["motor"]
    return dict(kosular=kos, el_hesabi_taban_analiz={k2: v2 for k2, v2 in ta.items() if isinstance(v2, dict) and "T_kgcm" in v2},
                birim_not_="1 N*m = 10,197 kg*cm; durma 2,059 N*m = 21 kg*cm; sürekli 0,618 N*m = 6,3 kg*cm (TAHMİN)")


# ====================================================================== 9) kol çarpması (CAD ağından dışbükey zarflar)
def olc_carpisma():
    import carpisma_denetim
    return carpisma_denetim.tara()


BOLUMLER = ["model", "statik", "fren", "kol", "carpisma", "rampa", "esik", "donus", "tork"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--yalniz", default=None)
    ap.add_argument("--cikti", default=CIKTI)
    a = ap.parse_args()
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    if not D.FIZIK_VAR:
        print("fizik bağımlılığı (mujoco) yok: %s" % D.FIZIK_HATA)
        return 2
    sec = a.yalniz.split(",") if a.yalniz else BOLUMLER
    os.makedirs(a.cikti, exist_ok=True)
    yol = os.path.join(a.cikti, "olcum.json")
    hepsi = oku(yol) if (a.yalniz and os.path.exists(yol)) else {}
    import mujoco
    hepsi["_ortam"] = dict(mujoco=mujoco.__version__, python=sys.version.split()[0],
                           parametreler=D.parametreler(), takimlar=TAKIM, pozlar=POZ)
    sureler = hepsi.get("_sure_s", {})
    for b in sec:
        t0 = time.perf_counter()
        print("== %s ..." % b, flush=True)
        hepsi[b] = yuvarla(globals()["olc_" + b]())
        sureler[b] = round(time.perf_counter() - t0, 1)
        print("   %.1f s" % sureler[b], flush=True)
    hepsi["_sure_s"] = sureler
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(hepsi, f, ensure_ascii=False, indent=1, sort_keys=True)
    import olcum_rapor
    olcum_rapor.yaz(hepsi, os.path.join(a.cikti, "olcum.md"))
    print("yazıldı: %s" % os.path.relpath(yol, KOK))
    return 0


if __name__ == "__main__":
    sys.exit(main())
