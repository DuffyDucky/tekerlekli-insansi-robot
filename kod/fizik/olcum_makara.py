"""Y0f: makaralı omni (ONERI-MAKARA, `omni_makara.py`) ile küre omni (ONERI-ADAY, aynı aday ölçüler) yan yana. VARSAYIM; V0 ve
öbür varyantlar değişmez. Başsız, belirlenimci, protokol üzerinden.

    "%LALE_SIM_VENV%\\Scripts\\python.exe" kod/fizik/olcum_makara.py      # -> planlama/d158/Y0f-olcum/omni-makara.json + .md

Bölümler:
  - hız ve kararlılık: gerçek zaman oranı (kayıtsız, düz 0,25 m/s ve yerinde w 1), MuJoCo uyarıları; zaman adımı / çözücü ayarı
  - dönüş (µ 0,5 / 0,8 x 21 / 9 kg·cm): yerinde w 0,5 / 1 / 1,5, yay, 90°, kolonu dolaşma (olcum_oneri ile aynı ölçüler)
  - yan etkiler (µ 0,8, 21 kg·cm): düz, yanal itme, `dur`, acil stop, 5° yan eğim; rampa 5° / 10° (tutma); eşik 5 / 10 / 15 mm
  - titreşim: düz gidişte gövde düşey ivmesi, pitch / roll salınımı, baskın frekans, 1,58 m'deki noktanın ve kafanın genliği
  - eşik duyarlılığı: makara çapı 15 / 19 / 23 mm, temas biçimi (elipsoid / kapsül)
  - makara yatağı sürtünmesi (makara başına, tek temas fazında yanal kuvvet 0-20 N): yerinde w, 5° yan eğim
  - enkoder arka (lastik; pin planı, asıl) / ön (omni; duyarlılık): dönüş, 90°, 10° / 15° rampa çıkışı, enkoder arızası
"""

import json
import math
import os
import statistics as st
import sys
import time

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)
import numpy as np  # noqa: E402
import mujoco  # noqa: E402
import olcumler as O  # noqa: E402
import olcum_varyantlar as OV  # noqa: E402
import olcum_oneri as OO  # noqa: E402  (yanlış alarm izleyicisini de kurar: OO.ALARM)
import omni_makara as OM  # noqa: E402
import varyantlar as VR  # noqa: E402

CIKTI = OV.CIKTI
DURMA = OV.DURMA
KURE, MAKARA = "ONERI-ADAY", "ONERI-MAKARA"
VARS = [KURE, MAKARA]
H_KAFA = 1.58
ENK_ON = {"enkoder_teker": "on"}   # duyarlılık: enkoder ön (omni) tekerde olsaydı; asıl değer arka (pin planı, varyantlar.ENKODER_ONERI)


def _dg(d, kume):
    """MuJoCo uyarı sayıları toplamı (kararsızlık göstergesi)."""
    return int(sum(d.warning[i].number for i in range(len(d.warning)))) if kume else 0


# ------------------------------------------------------------------ hız ve kararlılık
def hiz_kos(var, degis=None, ayar=None):
    dn = OV.deney(var, 0.8, 2.059, degis=degis)
    if ayar:
        ayar(dn)
    w = dn.w
    dn.devreye_al()
    sonuc = {}
    en_makara = 0.0
    for ad, (v, wc) in (("duz", (0.25, 0.0)), ("yerinde", (0.0, 1.0))):
        s0, t0 = w.zaman_s, time.perf_counter()
        dn.e.sur_tut(v, wc, 5000)
        sonuc["rtf_" + ad] = (w.zaman_s - s0) / (time.perf_counter() - t0)
        sonuc[ad + "_son"] = dict(v=w.hiz()[0], w=w.hiz()[1])
    if w.makarali:
        mk = [w.m.jnt_dofadr[j] for j in range(w.m.njnt) if (mujoco.mj_id2name(w.m, mujoco.mjtObj.mjOBJ_JOINT, j) or "").find("_mk_") > 0]
        en_makara = float(max(abs(w.d.qvel[i]) for i in mk))
    sonuc.update(uyari=_dg(w.d, True), nbody=int(w.m.nbody), ngeom=int(w.m.ngeom), nv=int(w.m.nv), ncon_son=int(w.d.ncon),
                 nefc_son=int(w.d.nefc), en_buyuk_makara_hizi_rad_s=en_makara, dt_s=float(w.m.opt.timestep))
    return sonuc


def _piramit(dn):
    dn.w.m.opt.cone = mujoco.mjtCone.mjCONE_PYRAMIDAL


def _impratio(dn):
    dn.w.m.opt.impratio = 10.0


def _iter20(dn):
    dn.w.m.opt.iterations = 20


def _ccd6(dn):
    dn.w.m.opt.ccd_tolerance = 1e-6


AYARLAR = [("ana (dt 1 ms, eliptik koni, Newton)", None, None), ("dt 0,5 ms", {"zaman_adimi_s": 0.0005}, None),
           ("ccd toleransı 1e-6 (MuJoCo varsayılanı)", None, _ccd6),
           ("dt 2 ms", {"zaman_adimi_s": 0.002}, None), ("piramit koni", None, _piramit), ("impratio 10", None, _impratio),
           ("çözücü yinelemesi 20", None, _iter20), ("temas solref 0,002", {"temas_solref_s": 0.002}, None),
           ("temas solref 0,008", {"temas_solref_s": 0.008}, None)]


# ------------------------------------------------------------------ titreşim
def titresim(var, v, mu=0.8, durma=2.059, degis=None, ayar=None):
    dn = OV.deney(var, mu, durma, degis=degis)
    if ayar:
        ayar(dn)
    w = dn.w
    d = w.d
    kafa = w.m.body("kafa_bas").id
    dn.devreye_al()
    dn.e.sur_tut(v, 0.0, 3000)
    seri = []

    def kay(_):
        R = d.xmat[w.taban].reshape(3, 3)
        p = d.xpos[w.taban]
        tepe = p + R[:, 2] * H_KAFA
        _, _, _, yaw, pitch, roll = w.poz()
        seri.append((w.zaman_s, float(p[2]), float(d.qacc[2]), pitch, roll, yaw, float(tepe[0]), float(tepe[1]), float(tepe[2]),
                     float(d.xpos[kafa][0]), float(d.xpos[kafa][1]), float(d.xpos[kafa][2])))
    w.adim_kaydi = kay
    dn.e.sur_tut(v, 0.0, 4000)
    w.adim_kaydi = dn._kaydet
    a = np.array(seri)
    t = a[:, 0] - a[0, 0]
    yaw = float(np.mean(a[:, 5]))
    c, s = math.cos(yaw), math.sin(yaw)

    def egilimsiz(y):
        k = np.polyfit(t, y, 1)
        return y - np.polyval(k, t)

    def genlik(xi, yi, zi):
        ileri = egilimsiz(xi * c + yi * s)
        yan = egilimsiz(-xi * s + yi * c)
        dus = egilimsiz(zi)
        return dict(ileri_tt_mm=float(np.ptp(ileri) * 1000), yan_tt_mm=float(np.ptp(yan) * 1000), dusey_tt_mm=float(np.ptp(dus) * 1000),
                    ileri_rms_mm=float(np.std(ileri) * 1000), yan_rms_mm=float(np.std(yan) * 1000), dusey_rms_mm=float(np.std(dus) * 1000))

    def baskin(y):
        y = egilimsiz(y) * np.hanning(len(y))
        f = np.fft.rfftfreq(len(y), d=float(np.mean(np.diff(t))))
        P = np.abs(np.fft.rfft(y))
        ok = f >= 2.0
        return float(f[ok][int(np.argmax(P[ok]))])
    pitch, roll = egilimsiz(a[:, 3]), egilimsiz(a[:, 4])
    v_ort = float(np.hypot(a[-1, 6] - a[0, 6], a[-1, 7] - a[0, 7]) / t[-1])
    R = 0.0635 if var in (KURE, MAKARA) or isinstance(var, dict) else 0.0625
    return dict(v_komut=v, v_ort=v_ort, makara_gecis_hz=v_ort / (2 * math.pi * R) * 22, teker_tur_hz=v_ort / (2 * math.pi * R),
                govde_z_tt_mm=float(np.ptp(egilimsiz(a[:, 1])) * 1000), az_rms=float(np.std(a[:, 2])), az_tepe=float(np.max(np.abs(a[:, 2]))),
                pitch_tt_derece=float(np.degrees(np.ptp(pitch))), roll_tt_derece=float(np.degrees(np.ptp(roll))),
                pitch_baskin_hz=baskin(a[:, 3]), az_baskin_hz=baskin(a[:, 2]), roll_baskin_hz=baskin(a[:, 4]),
                yon_sapmasi_derece=float(np.degrees(a[-1, 5] - a[0, 5])),
                nokta_158=genlik(a[:, 6], a[:, 7], a[:, 8]), kafa=genlik(a[:, 9], a[:, 10], a[:, 11]))


# ------------------------------------------------------------------ rampa çıkışı (rampa_parkuru boyutları)
def rampa_cikis(var, egim, durma=2.059, degis=None, v=0.25, sinir_s=30.0):
    """2 m yatay rampa (x 12-14) + 1 m platform; robot x 10,5'ten v ile, rampa kipi açık, sonar kapalı (sonar kuralı 15°'de
    rampa önünde durdurur: teşhis). Ölçülen: çıktı mı, rampada hız, ön / arka teker çevre hızı / gövde hızı, arka tork / durma,
    ön / arka yük, enkoder arızası kilidi."""
    sahne = {"rampalar": [{"x": 12.0, "y": 40.0, "aci_derece": 0, "egim_derece": egim, "uzunluk_m": 2.0, "genislik_m": 1.2,
                           "ust_uzunluk_m": 1.0}]}
    d = {"teker_zemin_surtunme": 0.8, "motor_durma_torku_Nm": durma}
    d.update(degis or {})
    dn = O.Deney(degis=d, sahne=sahne, konum=(10.5, 40.0, 0.0), sonar_acik=False, varyant=OV._var(var))
    w = dn.w
    r = w.teker_r
    dn.devreye_al()
    dn.e.istek({"k": "rampa", "ac": True})
    k = []

    def kay(c):
        if 12.3 < c.x < 13.7:
            tv = w.teker_hizlari()
            k.append(dict(v=w.hiz()[0], on=(tv[0] * r[0] + tv[2] * r[2]) / 2, arka=(tv[1] * r[1] + tv[3] * r[3]) / 2,
                          tork_arka=(abs(w.son_tork[1]) + abs(w.son_tork[3])) / 2, tork_on=(abs(w.son_tork[0]) + abs(w.son_tork[2])) / 2,
                          pitch=w.poz()[4]))
    adim = dict(n=0, N=[0.0] * 4, bos_on=0)

    def adim_kay(_):                                  # her fizik adımında yük (10 ms örnek temas sıçramasında yanıltır)
        if 12.3 < w.d.xpos[w.taban][0] < 13.7:
            N = w.teker_yukleri()
            adim["n"] += 1
            adim["N"] = [a + b for a, b in zip(adim["N"], N)]
            adim["bos_on"] += (N[0] <= 0.0) + (N[2] <= 0.0)
    dn.c.kayitci = kay
    w.adim_kaydi = adim_kay
    dn.e.sur_tut(v, 0.0, int(sinir_s * 1000), dur_kosul=lambda e: dn.c.x >= 14.4 or abs(w.poz()[4]) > math.radians(egim + 20))
    dn.c.kayitci = None
    w.adim_kaydi = dn._kaydet
    o = dn.c._oneri
    son = k[-300:] if k else []
    n = max(1, adim["n"])
    vv = st.mean(x["v"] for x in son) if son else None
    return dict(egim=egim, cikti=dn.c.x >= 14.4, son_x=dn.c.x, devrildi=abs(w.poz()[4]) > math.radians(egim + 20),
                rampada_hiz=vv, on_cevre=(st.mean(x["on"] for x in son) / vv) if son and vv and abs(vv) > 1e-3 else None,
                arka_cevre=(st.mean(x["arka"] for x in son) / vv) if son and vv and abs(vv) > 1e-3 else None,
                on_cevre_hiz=st.mean(x["on"] for x in son) if son else None, arka_cevre_hiz=st.mean(x["arka"] for x in son) if son else None,
                tork_arka_durma=(st.mean(x["tork_arka"] for x in son) / durma) if son else None,
                tork_on_durma=(st.mean(x["tork_on"] for x in son) / durma) if son else None,
                N_on=(adim["N"][0] + adim["N"][2]) / 2 / n if adim["n"] else None,
                N_arka=(adim["N"][1] + adim["N"][3]) / 2 / n if adim["n"] else None,
                on_temassiz_orani=adim["bos_on"] / (2.0 * n) if adim["n"] else None,
                pitch_derece=math.degrees(st.mean(x["pitch"] for x in son)) if son else None,
                enkoder_kilidi=list(o["arizali"]) if o else None)


# ------------------------------------------------------------------ enkoder arızası (test_enkoder_ariza ile aynı kurgu)
def ariza_kos(var, bozuk, degis=None):
    dn = O.Deney(varyant=OV._var(var), degis=degis)
    dn.devreye_al()
    dn.e.sur_tut(0.10, 0.0, 1000)
    t_ariza = dn.c.ms
    dn.c.enkoder_bozuk = list(bozuk)
    x0, y0, _, a0, _, _ = dn.w.poz()
    dn.e.sur_tut(0.10, 0.0, 2000)
    x1, y1, _, _, _, _ = dn.w.poz()
    dn.e.sur_tut(0.10, 0.0, 1000)
    x2, y2, _, a2, _, _ = dn.w.poz()
    o = dn.c._oneri
    return dict(bozuk=[b or "-" for b in bozuk], v_son=math.hypot(x2 - x1, y2 - y1), aci_derece=math.degrees(a2 - a0),
                arizali=list(o["arizali"]), tespit_ms=[None if m is None else m - t_ariza for m in o["ariza_ms"]])


def statik(var):
    """Yerleşmiş robotta teker yükleri ve ön tekerde temas eden makara sayısı."""
    dn = OV.deney(var, 0.8, 2.059)
    w = dn.w
    n_on = sum(1 for i in range(w.d.ncon) if (w.d.contact[i].geom1 in w.teker_geom_kume[0] or w.d.contact[i].geom2 in w.teker_geom_kume[0]))
    return dict(kutle_kg=float(sum(w.m.body_mass)), yuk_N=w.teker_yukleri(), on_sol_temas_sayisi=n_on)


def main():
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    p = OM.yukle()
    o = dict(varyantlar={k: dict(ad=VR.VARYANTLAR[k]["ad"], aciklama=VR.VARYANTLAR[k]["aciklama"]) for k in VARS},
             omni_parametreleri=p, geometri={}, statik={}, hiz={}, kosular=[], yan_etki={}, rampa={}, esik={}, titresim=[])
    for b in ("elipsoid", "kapsul"):
        g = OM.geometri(dict(p, temas_bicimi=b))
        lo, hi, n = OM.sapma_ozeti(g)
        o["geometri"][b] = dict(a_mm=None if g["a"] is None else g["a"] * 1000, etkin_yaricap_mm=[lo * 1000, hi * 1000],
                                sapma_mm=(hi - lo) * 1000, makara_gecisi_tur=n, Rc_mm=g["Rc"] * 1000)
    for var in VARS:
        o["statik"][var] = statik(var)
    print("statik", o["statik"], flush=True)
    # hız ve kararlılık
    for var in VARS:
        o["hiz"][var] = []
        for ad, dg, ay in AYARLAR:
            OO.AKTIF[0] = "%s hız %s" % (var, ad)
            r = hiz_kos(var, dg, ay)
            r["ayar"] = ad
            r["yerinde_w"] = OO.yerinde(var, 0.8, 2.059, 0.0, 1.0, degis=dg, ayar=ay)["w_gercek"]
            r["titresim"] = titresim(var, 0.25, degis=dg, ayar=ay)
            o["hiz"][var].append(r)
            print("hiz %-12s %-34s RTF duz %.1f yerinde %.1f | w %.3f | pitch tt %.3f° az rms %.2f | uyari %d" % (
                var, ad, r["rtf_duz"], r["rtf_yerinde"], r["yerinde_w"], r["titresim"]["pitch_tt_derece"], r["titresim"]["az_rms"],
                r["uyari"]), flush=True)
    # dönüş
    for var in VARS:
        for dad, durma in DURMA.items():
            for mu in (0.5, 0.8):
                r = dict(varyant=var, durma=dad, mu=mu)
                OO.AKTIF[0] = "%s %s µ %.1f dönüş / yay / 90° / kolon" % (var, dad, mu)
                r["yerinde"] = {str(w): OO.yerinde(var, mu, durma, 0.0, w) for w in (0.5, 1.0, 1.5)}
                r["yay"] = {str(w): OO.yerinde(var, mu, durma, 0.25, w) for w in (0.5, 1.0)}
                r["doksan"] = OO.doksan(var, mu, durma)
                r["dolasma"] = OV.dolas_kos(var, mu, durma)
                o["kosular"].append(r)
                print("%-12s %s mu %.1f | yerinde %s | yay w %.3f | 90: %s | kolon %s" % (
                    var, dad, mu, " ".join("%.3f" % r["yerinde"][k]["w_gercek"] for k in ("0.5", "1.0", "1.5")),
                    r["yay"]["1.0"]["w_gercek"], "-" if not r["doksan"]["ulasti"] else "%.1f s asma %.1f" % (
                        r["doksan"]["sure_90_s"], r["doksan"]["asma_derece"]),
                    "%.1f s" % r["dolasma"]["sure_s"] if r["dolasma"]["basarili"] else "basarisiz"), flush=True)
        OO.AKTIF[0] = "%s yan etkiler" % var
        o["yan_etki"][var] = OV.yan_etki(var)
        OO.AKTIF[0] = "%s rampa" % var
        o["rampa"][var] = {str(e): OO.olcumler_ile(var, O.rampa_kos, e, "ana") for e in (5, 10)}
        OO.AKTIF[0] = "%s eşik" % var
        o["esik"][var] = [OO.olcumler_ile(var, O.esik_kos, h, t, v) for t in ("ana", "durma_9kgcm") for v in (0.2, 1.0)
                          for h in (5, 10, 15)]
        print("%-12s yan etki / rampa / esik bitti" % var, flush=True)
    # titreşim
    OO.AKTIF[0] = "titreşim"
    for ad, var in (("V0 (lastik)", "V0"), ("küre (ONERI-ADAY)", KURE), ("makara elipsoid", MAKARA),
                    ("makara 5 küre", VR.makara_varyanti(temas_bicimi="kureler")),
                    ("makara kapsül", VR.makara_varyanti(temas_bicimi="kapsul"))):
        for v in (0.1, 0.25, 0.39):
            r = titresim(var, v)
            r["durum"] = ad
            o["titresim"].append(r)
            print("titresim %-20s v %.2f | z tt %.3f mm az rms %.2f | pitch tt %.3f° (%.1f Hz; makara %.1f Hz) | 1,58 m ileri tt %.2f mm "
                  "yan %.2f dusey %.2f | kafa ileri %.2f" % (ad, v, r["govde_z_tt_mm"], r["az_rms"], r["pitch_tt_derece"], r["pitch_baskin_hz"],
                                                           r["makara_gecis_hz"], r["nokta_158"]["ileri_tt_mm"], r["nokta_158"]["yan_tt_mm"],
                                                           r["nokta_158"]["dusey_tt_mm"], r["kafa"]["ileri_tt_mm"]), flush=True)
    # eşik duyarlılığı: makara çapı ve temas biçimi
    OO.AKTIF[0] = "eşik duyarlılığı"
    o["esik_duyarlilik"] = []
    for ad, var in (("makara Ø15", VR.makara_varyanti(makara_capi_mm=15.0, sira_eksen_araligi_mm=14.0)),
                    ("makara Ø19 (ana)", MAKARA),
                    ("makara Ø23", VR.makara_varyanti(makara_capi_mm=23.0, sira_eksen_araligi_mm=6.0)),
                    ("5 küre Ø19", VR.makara_varyanti(temas_bicimi="kureler")),
                    ("kapsül Ø19", VR.makara_varyanti(temas_bicimi="kapsul")),
                    ("küre modeli (ONERI-ADAY)", KURE)):
        for t in ("ana", "durma_9kgcm"):
            for h in (5, 10, 15, 20, 25, 30):
                r = OO.olcumler_ile(var, O.esik_kos, h, t, 0.2)
                o["esik_duyarlilik"].append(dict(durum=ad, takim=t, yukseklik_mm=h, gecti=r["gecti"], on_teker_cikti=r["on_teker_cikti"],
                                                 govde_degdi=r["govde_degdi"], tepe_tork_Nm=r["tepe_tork_Nm"]))
        print("esik duyarlilik %s bitti" % ad, flush=True)
    # makara yatağı sürtünmesi
    OO.AKTIF[0] = "makara yatağı sürtünmesi"
    o["yatak"] = []
    for F in (0.0, 0.05, 1.0, 2.0, 3.0, 5.0, 7.0, 13.0, 20.0):
        var = VR.makara_varyanti(makara_yatak_surtunmesi_N=F)
        r = dict(yanal_N=F)
        for dad, durma in DURMA.items():
            for mu in (0.5, 0.8):
                y = OO.yerinde(var, mu, durma, 0.0, 1.0)
                r["%s_%s" % (dad, mu)] = dict(w=y["w_gercek"], tork_surekli=y["tork_surekli_orani"])
        e = OO.yan_egim(var)
        r["yan_egim_kayma_m"], r["yan_egim_yon_derece"] = e["yan_kayma_m"], e["yon_sapmasi_derece"]
        o["yatak"].append(r)
        print("yatak %.0f N | %s | yan egim %.3f m" % (F, " ".join("%s %.3f" % (k, r[k]["w"]) for k in r if k.endswith(("0.5", "0.8"))),
                                                      r["yan_egim_kayma_m"]), flush=True)
    # rampa çıkışı: temas biçimi ve ccd toleransı (enkoder arka; ccd ve ana biçim ön enkoderle de: önceki ölçümün kurgusu)
    o["rampa_bicim"] = []
    for ad, var, dg in (("küre modeli ONERI (Ø125, teşhisteki)", "ONERI", None), ("küre modeli ONERI-ADAY", KURE, None),
                        ("makara elipsoid (ana)", MAKARA, None), ("makara 5 küre", VR.makara_varyanti(temas_bicimi="kureler"), None),
                        ("makara kapsül", VR.makara_varyanti(temas_bicimi="kapsul"), None),
                        ("makara elipsoid, ccd 1e-6 (hatalı normal)", VR.makara_varyanti(ccd_toleransi=1e-6), None),
                        ("makara elipsoid, enkoder ön", MAKARA, ENK_ON),
                        ("makara elipsoid, ccd 1e-6 (hatalı normal), enkoder ön", VR.makara_varyanti(ccd_toleransi=1e-6), ENK_ON)):
        for egim in (10, 15):
            OO.AKTIF[0] = "rampa biçim %s %d°" % (ad, egim)
            r = rampa_cikis(var, egim, degis=dg)
            r["durum"] = ad
            o["rampa_bicim"].append(r)
            print("rampa bicim %-42s %d°: cikti %s v %s on/govde %s N on %s temassiz %s" % (
                ad, egim, r["cikti"], _y(r["rampada_hiz"]), _y(r["on_cevre"]), _y(r["N_on"], "%.1f"), _y(r["on_temassiz_orani"])), flush=True)
    # enkoder ön / arka
    OO.AKTIF[0] = "enkoder ön / arka"
    o["enkoder"] = dict(donus=[], rampa=[], ariza=[])
    for var in VARS:
        for enk, dg in (("arka", None), ("ön (duyarlılık)", ENK_ON)):
            for dad, durma in DURMA.items():
                OO.AKTIF[0] = "enkoder %s %s %s dönüş / yay / 90°" % (var, enk, dad)
                y = OO.yerinde(var, 0.8, durma, 0.0, 1.0, degis=dg)
                a = OO.yerinde(var, 0.8, durma, 0.25, 0.5, degis=dg)
                d9 = OO.doksan(var, 0.8, durma, degis=dg)
                o["enkoder"]["donus"].append(dict(varyant=var, enkoder=enk, durma=dad, yerinde_w=y["w_gercek"], yay_w=a["w_gercek"],
                                                  yay_v=a["v_gercek"], doksan_s=d9["sure_90_s"], doksan_asma=d9["asma_derece"]))
                for egim in (10, 15):
                    OO.AKTIF[0] = "enkoder %s %s %s %d° rampa" % (var, enk, dad, egim)
                    r = rampa_cikis(var, egim, durma=durma, degis=dg)
                    r.update(varyant=var, enkoder=enk, durma=dad)
                    o["enkoder"]["rampa"].append(r)
                    print("rampa %-12s enk %-4s %s %d°: cikti %s x %.2f v %s on/govde %s arka/govde %s arka tork/durma %s kilit %s" % (
                        var, enk, dad, egim, r["cikti"], r["son_x"], _y(r["rampada_hiz"]), _y(r["on_cevre"]), _y(r["arka_cevre"]),
                        _y(r["tork_arka_durma"]), r["enkoder_kilidi"]), flush=True)
    for enk, dg in (("arka", None), ("ön (duyarlılık)", ENK_ON)):
        for bozuk in ((None, None), ("takili", "takili"), ("ters", "ters"), ("takili", None)):
            OO.AKTIF[0] = "KASITLI enkoder arızası (beklenen tespit) %s %s" % (enk, "/".join(b or "-" for b in bozuk))
            r = ariza_kos(MAKARA, bozuk, degis=dg)
            r["enkoder"] = enk
            o["enkoder"]["ariza"].append(r)
    o["yanlis_alarm"] = OO.ALARM
    print("enkoder arizasi korumasi tetiklendi: %d (%s)" % (len(OO.ALARM), sorted(set(a["olcum"] for a in OO.ALARM))), flush=True)
    os.makedirs(CIKTI, exist_ok=True)
    with open(os.path.join(CIKTI, "omni-makara.json"), "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, indent=1, sort_keys=True, default=float)
    with open(os.path.join(CIKTI, "omni-makara.md"), "w", encoding="utf-8") as f:
        f.write(md(o))
    print("yazıldı: planlama/d158/Y0f-olcum/omni-makara.json + .md")


def _doksan_degis(var, mu, durma, degis):
    eski = OV.deney

    def yeni(v, m, dd, degis_=None, **kw):
        dd2 = dict(degis)
        dd2.update(degis_ or {})
        return eski(v, m, dd, degis=dd2, **kw)
    OV.deney = yeni
    try:
        return OO.doksan(var, mu, durma)
    finally:
        OV.deney = eski


def _y(x, f="%.3f"):
    return "-" if x is None else f % x


def s(x, f="%.2f"):
    return "-" if x is None else (f % x).replace(".", ",")


def md(o):
    p = o["omni_parametreleri"]
    ge = o["geometri"]
    L = ["# Makaralı omni modeli (ONERI-MAKARA) ve küre modeli (ONERI-ADAY) (Y0f, `kod/fizik/olcum_makara.py`)", "",
         "**VARSAYIM**, bugünkü robot değil; aday teker (Nexus 14075) SEÇİLMEDİ. İkisi de öneri firmware (PI açık) ve aynı aday "
         "ölçüler (Ø127 × 29 mm, 480 g, merkez 14,5 mm içeri). Küre: ön teker tek küre + her adımda sıfırlanan x menteşesi "
         "(yanal direnç 0,05 × yük). Makara: göbek + 2 × 11 makara, her biri kendi ekseninde menteşe, temas makaralardan "
         "(`kod/fizik/omni_makara.py`, parametreler `kod/fizik/omni_teker.json`). Makara Ø %s mm (ürün sayfası), boy %s mm "
         "(TAHMİN), sıra eksen aralığı %s mm (TAHMİN), makara %s g (TAHMİN), yatak sürtünmesi makara başına %s N (tek temas fazında "
         "yanal; pirinç boru, TAHMİN), enkoder arka (lastik) tekerde (pin planı), temas biçimi %s (elipsoid a %s mm). Etkin yarıçap sapması: elipsoid %s mm, kapsül %s mm; tur başına %d makara geçişi." % (
             s(p["makara_capi_mm"], "%.0f"), s(p["makara_boyu_mm"], "%.0f"), s(p["sira_eksen_araligi_mm"], "%.0f"),
             s(p["makara_kutlesi_g"], "%.0f"), s(p["makara_yatak_surtunmesi_N"], "%.0f"), p["temas_bicimi"],
             s(ge["elipsoid"]["a_mm"], "%.1f"), s(ge["elipsoid"]["sapma_mm"], "%.3f"), s(ge["kapsul"]["sapma_mm"], "%.3f"),
             ge["elipsoid"]["makara_gecisi_tur"]), ""]
    L += ["Statik: " + "; ".join("%s %s kg, yük ön sol / arka sol / ön sağ / arka sağ %s N, ön solda temas eden geom %d" % (
        k, s(v["kutle_kg"], "%.3f"), " / ".join(s(n, "%.1f") for n in v["yuk_N"]), v["on_sol_temas_sayisi"]) for k, v in o["statik"].items()), ""]
    L += ["## Hız, kararlılık, zaman adımı ve çözücü (µ 0,8, 21 kg·cm)", "",
          "Gerçek zaman oranı (RTF) = sanal s / duvar s, kayıtsız, tek iş parçacığı, bu makinede. Titreşim: v 0,25, 4 s.", "",
          "| varyant | ayar | RTF düz / yerinde | yerinde w | pitch t-t ° | düşey ivme rms m/s² | 1,58 m ileri t-t mm | uyarı | nv / ngeom |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for var, liste in o["hiz"].items():
        for r in liste:
            t = r["titresim"]
            L.append("| %s | %s | %s / %s | %s | %s | %s | %s | %d | %d / %d |" % (
                var, r["ayar"], s(r["rtf_duz"], "%.1f"), s(r["rtf_yerinde"], "%.1f"), s(r["yerinde_w"], "%.3f"), s(t["pitch_tt_derece"], "%.3f"),
                s(t["az_rms"], "%.2f"), s(t["nokta_158"]["ileri_tt_mm"], "%.2f"), r["uyari"], r["nv"], r["ngeom"]))
    L += ["", "## Dönüş (küre / makara yan yana)", "",
          "| varyant | durma | µ | yerinde w (komut 0,5 / 1 / 1,5) | tork / sürekli (w 1) | yay v 0,25 + w 0,5: w / yarıçap m | yay + w 1: w / yarıçap m | 90°: s / aşma ° | kolon |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in o["kosular"]:
        y, a, d, k = r["yerinde"], r["yay"], r["doksan"], r["dolasma"]
        L.append("| %s | %s | %s | %s / %s / %s | %s | %s / %s | %s / %s | %s | %s |" % (
            r["varyant"], r["durma"], s(r["mu"], "%.1f"), s(y["0.5"]["w_gercek"], "%.3f"), s(y["1.0"]["w_gercek"], "%.3f"),
            s(y["1.5"]["w_gercek"], "%.3f"), s(y["1.0"]["tork_surekli_orani"], "%.1f"), s(a["0.5"]["w_gercek"], "%.3f"),
            s(a["0.5"]["yaricap_m"]), s(a["1.0"]["w_gercek"], "%.3f"), s(a["1.0"]["yaricap_m"]),
            ("%s / %s" % (s(d["sure_90_s"], "%.1f"), s(d["asma_derece"], "%.1f"))) if d["ulasti"] else "ulaşmadı (20 s)",
            ("başarılı, %s s" % s(k["sure_s"], "%.1f")) if k["basarili"] else "başarısız (%d / 3)" % k["ulasilan_ara_nokta"]))
    L += ["", "## Yan etkiler, rampa, eşik (µ 0,8, 21 kg·cm; eşik 9 kg·cm de)", "",
          "| varyant | düz 6 s yol m | yanal itme 10 N: yan m / yön ° | dur m | acil stop m | 5° yan eğim duruş: yan m | 5° yan eğim düz 5 s: yan m / yön ° |",
          "| --- | --- | --- | --- | --- | --- | --- |"]
    for k, e in o["yan_etki"].items():
        L.append("| %s | %s | %s / %s | %s | %s | %s | %s / %s |" % (
            k, s(e["duz_6s"]["yol_m"]), s(e["yanal_itme"]["yan_kayma_m"], "%.3f"), s(e["yanal_itme"]["yon_sapmasi_derece"], "%.1f"),
            s(e["dur"]["yol_m"], "%.3f"), s(e["acil_stop"]["yol_m"], "%.3f"), s(e["yan_egim_5_durus"]["yan_kayma_m"], "%.3f"),
            s(e["yan_egim_5_duz_gidis"]["yan_kayma_m"], "%.3f"), s(e["yan_egim_5_duz_gidis"]["yon_sapmasi_derece"], "%.1f")))
    L += ["", "| varyant | eğim | ortasına ulaştı | rampada hız m/s | `dur` sonrası 5 s geri kayma m | tutuyor |", "| --- | --- | --- | --- | --- | --- |"]
    for k, rr in o["rampa"].items():
        for e, r in rr.items():
            L.append("| %s | %s° | %s | %s | %s | %s |" % (k, e, "evet" if r["rampanin_ortasina_ulasti"] else "hayır", s(r["rampada_hiz_m_s"], "%.3f"),
                                                       s(r["suzulme_sonrasi_5s_geri_kayma_m"], "%.3f"), "evet" if r["dur_sonrasi_tutuyor"] else "hayır"))
    L += ["", "| varyant | durma | v komutu | 5 mm | 10 mm | 15 mm |", "| --- | --- | --- | --- | --- | --- |"]
    for k, liste in o["esik"].items():
        for t in ("ana", "durma_9kgcm"):
            for v in (0.2, 1.0):
                h = {r["yukseklik_mm"]: r for r in liste if r["takim"] == t and r["v_komut"] == v}
                L.append("| %s | %s | %s | %s |" % (k, "21 kg·cm" if t == "ana" else "9 kg·cm", s(min(v, 0.39)), " | ".join(
                    _esik(h[mm]) for mm in (5, 10, 15))))
    L += ["", "## Titreşim (düz gidiş, µ 0,8, 21 kg·cm, 4 s; eğilim çıkarılmış)", "",
          "t-t = tepeden tepeye. 1,58 m: tabana rijit bağlı, tabandan 1,58 m yukarıdaki nokta (gövde salınımının kafa yüksekliğindeki "
          "karşılığı); kafa: `kafa_bas` gövdesi (boyun / gövde servolarının esnekliği dahil). Makara geçiş frekansı = v / (2πR) × 22.", "",
          "| durum | v m/s | gövde z t-t mm | düşey ivme rms / tepe m/s² | pitch t-t ° (baskın Hz) | roll t-t ° (Hz) | makara geçişi Hz | 1,58 m ileri / yan / düşey t-t mm | kafa ileri / yan t-t mm |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in o["titresim"]:
        n, kf = r["nokta_158"], r["kafa"]
        L.append("| %s | %s | %s | %s / %s | %s (%s) | %s (%s) | %s | %s / %s / %s | %s / %s |" % (
            r["durum"], s(r["v_komut"]), s(r["govde_z_tt_mm"], "%.3f"), s(r["az_rms"], "%.2f"), s(r["az_tepe"], "%.1f"),
            s(r["pitch_tt_derece"], "%.3f"), s(r["pitch_baskin_hz"], "%.1f"), s(r["roll_tt_derece"], "%.3f"), s(r["roll_baskin_hz"], "%.1f"),
            s(r["makara_gecis_hz"], "%.1f"), s(n["ileri_tt_mm"]), s(n["yan_tt_mm"]), s(n["dusey_tt_mm"]), s(kf["ileri_tt_mm"]), s(kf["yan_tt_mm"])))
    L += ["", "## Eşik duyarlılığı (makara, v 0,2, sonar kapalı)", "", "| durum | durma | 5 mm | 10 mm | 15 mm | 20 mm | 25 mm | 30 mm |",
          "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    ed = {}
    for r in o["esik_duyarlilik"]:
        ed.setdefault((r["durum"], r["takim"]), {})[r["yukseklik_mm"]] = r
    for (ad, t), h in ed.items():
        L.append("| %s | %s | %s |" % (ad, "21 kg·cm" if t == "ana" else "9 kg·cm", " | ".join(_esik(h[mm]) for mm in (5, 10, 15, 20, 25, 30))))
    L += ["", "## Makara yatağı sürtünmesi (makara başına; yerinde w komutu 1; enkoder arka)", "",
          "Her makara ekleminde sabit Coulomb momenti = kuvvet × makara yarıçapı (yükle değişmez). Parametre, tek makara temasta "
          "iken tekerin yanal direncidir; iki sıra birden yere değerken model direnci ≈ 2,1 katına çıkar (B, Y0f-kontrol § 14.2: "
          "yerinde dönüşte zamanın ≈ %10'u, düz gidişte ≈ %30'u). Gerçekte pim sürtünmesi yükle bölünür, iki temasta toplam aynı "
          "kalır. Teker seçimi ölçütü: masada teker gerçek yükte (≈ 62 N) yavaşça yana çekilirken ölçülen sürekli kuvvet bu "
          "tablonun ilk sütunuyla (tek temas değeri) karşılaştırılır. TAHMİN'e bağlı, mertebe, sınır değil (2 N, pim µ 0,2 "
          "TAHMİN'inden).", "",
          "| yanal N (tek temas) | 21 kg·cm µ 0,5 | 21 kg·cm µ 0,8 | 9 kg·cm µ 0,5 | 9 kg·cm µ 0,8 | 5° yan eğim 5 s: yan m / yön ° |", "| --- | --- | --- | --- | --- | --- |"]
    for r in o["yatak"]:
        L.append("| %s | %s | %s / %s |" % (s(r["yanal_N"], "%.2f"), " | ".join("%s (%s)" % (s(r[k]["w"], "%.3f"), s(r[k]["tork_surekli"], "%.1f"))
                                                                            for k in ("21kgcm_0.5", "21kgcm_0.8", "9kgcm_0.5", "9kgcm_0.8")),
                                         s(r["yan_egim_kayma_m"], "%.3f"), s(r["yan_egim_yon_derece"], "%.1f")))
    L.append("")
    L.append("Hücre: gerçekleşen w rad/s (tork / sürekli).")
    L += ["", "## Rampa çıkışı ve temas biçimi (rampa_parkuru boyutları, rampa kipi, sonar kapalı, v 0,25, µ 0,8, 21 kg·cm, enkoder arka; "
          "\"enkoder ön\" satırları önceki ölçümün kurgusu)", "",
          "Ön temassız = ön tekerin zemine değmediği fizik adımlarının oranı (sıçrama). Yük her fizik adımında ortalanır.", "",
          "| durum | eğim | çıktı | rampada v m/s | ön çevre oranı | ön / arka yük N | ön temassız % | arka tork / durma |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in o["rampa_bicim"]:
        L.append("| %s | %d° | %s | %s | %s | %s / %s | %s | %s |" % (
            r["durum"], r["egim"], "evet" if r["cikti"] else ("devrildi" if r["devrildi"] else "hayır (x %s)" % s(r["son_x"])),
            s(r["rampada_hiz"], "%.3f"), s(r["on_cevre"]), s(r["N_on"], "%.0f"), s(r["N_arka"], "%.0f"),
            s(None if r["on_temassiz_orani"] is None else 100 * r["on_temassiz_orani"], "%.0f"), s(r["tork_arka_durma"])))
    L += ["", "## Enkoder arka (lastik; asıl) / ön (omni; duyarlılık: enkoder önde olsaydı) (µ 0,8)", "",
          "Depoda enkoderler arka motorlarda (`planlama/adim3/pin-haritasi.md` 100–103: GPIO 18 / 17 sol arka JGB37, 16 / 15 sağ "
          "arka; 398 ve `elektrik.md` 495: ön motorlarda enkoder yok; firmware `pinler.h` aynı pinler). Bu dosyanın öbür bütün "
          "sayıları arka enkoderle; 23.11 ilk sürümü ön enkoder kabulüyle alınmıştı.", "",
          "| varyant | enkoder | durma | yerinde w | yay v 0,25 + w 0,5: v / w | 90° s / aşma ° |", "| --- | --- | --- | --- | --- | --- |"]
    for r in o["enkoder"]["donus"]:
        L.append("| %s | %s | %s | %s | %s / %s | %s / %s |" % (r["varyant"], r["enkoder"], r["durma"], s(r["yerinde_w"], "%.3f"),
                                                             s(r["yay_v"], "%.3f"), s(r["yay_w"], "%.3f"), s(r["doksan_s"], "%.1f"), s(r["doksan_asma"], "%.1f")))
    L += ["", "Rampa çıkışı (rampa_parkuru boyutları: 2 m yatay + 1 m platform; rampa kipi, sonar kapalı, v 0,25, en çok 30 s; "
          "son 3 s'nin ortalaması; çevre oranı = teker çevre hızı / gövde hızı, 1 = kaymasız).", "",
          "| varyant | enkoder | durma | eğim | çıktı (son x) | rampada v m/s | ön / arka çevre oranı | ön / arka tork / durma | ön / arka yük N (ön temassız adım %) | enkoder kilidi |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in o["enkoder"]["rampa"]:
        L.append("| %s | %s | %s | %d° | %s (%s) | %s | %s / %s | %s / %s | %s / %s (%s) | %s |" % (
            r["varyant"], r["enkoder"], r["durma"], r["egim"], "evet" if r["cikti"] else ("devrildi" if r["devrildi"] else "hayır"),
            s(r["son_x"]), s(r["rampada_hiz"], "%.3f"), s(r["on_cevre"]), s(r["arka_cevre"]), s(r["tork_on_durma"]), s(r["tork_arka_durma"]),
            s(r["N_on"], "%.0f"), s(r["N_arka"], "%.0f"), s(None if r["on_temassiz_orani"] is None else 100 * r["on_temassiz_orani"], "%.0f"), "-" if r["enkoder_kilidi"] is None else "/".join("evet" if a else "hayır" for a in r["enkoder_kilidi"])))
    L += ["", "Enkoder arızası (ONERI-MAKARA, korumalı; test_enkoder_ariza.py kurgusu: v 0,10, 1 s sonra arıza, 3 s):", "",
          "| enkoder | arıza (sol / sağ) | son 1 s m | açı ° | kilit | tespit ms |", "| --- | --- | --- | --- | --- | --- |"]
    for r in o["enkoder"]["ariza"]:
        L.append("| %s | %s | %s | %s | %s | %s |" % (r["enkoder"], " / ".join(r["bozuk"]), s(r["v_son"], "%.3f"), s(r["aci_derece"], "%.1f"),
                                                    "/".join("evet" if a else "hayır" for a in r["arizali"]),
                                                    " / ".join("-" if m is None else str(m) for m in r["tespit_ms"])))
    kasitli = sum(1 for a in o["yanlis_alarm"] if a["olcum"].startswith("KASITLI"))
    L += ["", "## Enkoder arızası koruması: yanlış alarm", "",
          "Tetiklenme: %d; bunların %d'i KASITLI arıza denemesi (beklenen tespit), öbürleri ölçümün adıyla." % (
              len(o["yanlis_alarm"]), kasitli), ""]
    for a in o["yanlis_alarm"]:
        L.append("- %s: %s teker, %d ms" % (a["olcum"], a["yan"], a["ms"]))
    return "\n".join(L) + "\n"


def _esik(r):
    return "geçti" if r["gecti"] else ("ön çıktı" if r["on_teker_cikti"] else "geçmedi")


if __name__ == "__main__":
    main()
