"""Gezinme için robot ölçüleri (adım 1): ayak izi, dönme merkezi, süpürülen çap, hız / dönüş, LiDAR yeri.

    %V% kod\\fizik\\gezinme\\olcum_robot.py [--varyant ONERI ONERI-MAKARA] -> gezinme/sonuc/robot_olculeri.json

Geometri MuJoCo modelinin çarpışma geom'larından (ev pozu, taban çerçevesi: +x ileri, +y sol, köken taban gövdesi).
Hız ve dönüş protokolden (sahte ESP32 + Pi istemcisi), yer gerçeğiyle ölçülür. Belirlenimci."""

import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _yol  # noqa: E402

_yol.dusuk_oncelik()
import numpy as np  # noqa: E402


def geom_kutulari(w):
    """Robot çarpışma geom'larının taban çerçevesinde köşe noktaları: {ad: (8, 3)}."""
    import mujoco
    m, d = w.m, w.d
    Rt = d.xmat[w.taban].reshape(3, 3)
    pt = d.xpos[w.taban]
    sonuc = {}
    for g in sorted(w.robot_geom):
        ad = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or str(g)
        c, h = m.geom_aabb[g, :3], m.geom_aabb[g, 3:]
        kose = np.array([[sx, sy, sz] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]) * h + c
        Rg = d.geom_xmat[g].reshape(3, 3)
        dunya = kose @ Rg.T + d.geom_xpos[g]
        sonuc[ad] = (dunya - pt) @ Rt
    return sonuc


def kur(varyant, sahne="oda_bos_buyuk"):
    import dunya as D
    import varyantlar as VR
    from fizik_esp32 import FizikEsp32
    from sahte_esp32.harita import Harita
    from sahte_esp32.tasima import BellekTasima
    from lale_pi.istemci import Esp32Istemci
    veri = {"ad": "olcum_bos", "aciklama": "gezinme ölçümü, boş 20 x 20 m", "boyut_m": [20.0, 20.0],
            "cevre_duvari": True, "duvarlar": [], "engeller": [], "baslangic": {"x": 10.0, "y": 10.0, "aci_derece": 0}}
    h = Harita(veri, ad="olcum_bos")
    c = FizikEsp32(h, konum=(10.0, 10.0, 0.0), varyant=VR.al(varyant))
    e = Esp32Istemci(BellekTasima(c))
    e.baglan()
    o = e.devreye_al_ve_bekle()
    assert o.get("guc") == "devrede", o
    return c, e


def sur_kaydet(c, e, v, w, sure_ms):
    """sure_ms boyunca sur(v, w); 20 ms'de bir yer gerçeği (x, y, yaw, v, w)."""
    satir = []
    t = 0
    son = -1e9
    while t < sure_ms:
        if t - son >= 200:
            e.sur(v, w)
            son = t
        e.kalp_atisi()
        e.bekle(20)
        t += 20
        x, y, _, yaw, _, _ = c.dunya.poz()
        vv, ww = c.dunya.hiz()
        satir.append((t / 1000.0, x, y, yaw, vv, ww))
    e.istek({"k": "dur"})
    e.bekle(1000)
    return np.array(satir)


def cember_uydur(P):
    """En küçük kareler çember: (cx, cy, r)."""
    A = np.c_[2 * P[:, 0], 2 * P[:, 1], np.ones(len(P))]
    b = (P ** 2).sum(1)
    cx, cy, k = np.linalg.lstsq(A, b, rcond=None)[0]
    return cx, cy, math.sqrt(k + cx * cx + cy * cy)


def olc(varyant):
    c, e = kur(varyant)
    w = c.dunya
    kutu = geom_kutulari(w)
    import mujoco
    teker = {}
    for t in ("teker_on_sol", "teker_arka_sol", "teker_on_sag", "teker_arka_sag"):
        b = mujoco.mj_name2id(w.m, mujoco.mjtObj.mjOBJ_BODY, t)
        p = (w.d.xpos[b] - w.d.xpos[w.taban]) @ w.d.xmat[w.taban].reshape(3, 3)
        teker[t] = [round(float(z), 4) for z in p]
    tum = np.concatenate(list(kutu.values()))
    taban_ad = [a for a in kutu if a in ("c_etek", "c_govde")]
    taban = np.concatenate([kutu[a] for a in taban_ad])
    # duvar yüksekliği 1,0 m: 0-1 m arasındaki geom'lar duvara değebilir; kollar ve kafa bunun üstünde mi?
    alt = {a: k for a, k in kutu.items() if k[:, 2].min() < 1.0}
    dusuk = np.concatenate(list(alt.values()))
    sonuc = dict(varyant=varyant,
                 geomlar={a: dict(x=[round(float(k[:, 0].min()), 4), round(float(k[:, 0].max()), 4)],
                                  y=[round(float(k[:, 1].min()), 4), round(float(k[:, 1].max()), 4)],
                                  z=[round(float(k[:, 2].min()), 4), round(float(k[:, 2].max()), 4)]) for a, k in kutu.items()},
                 tekerler=teker)
    arka_x = (teker["teker_arka_sol"][0] + teker["teker_arka_sag"][0]) / 2
    for ad, P in (("taban_etek_govde", taban), ("tum_carpisma", tum), ("duvar_yuksekligi_alti", dusuk)):
        sonuc["ayak_izi_" + ad] = dict(x=[round(float(P[:, 0].min()), 4), round(float(P[:, 0].max()), 4)],
                                       y=[round(float(P[:, 1].min()), 4), round(float(P[:, 1].max()), 4)])
        r = float(np.max(np.hypot(P[:, 0] - arka_x, P[:, 1])))
        sonuc["supurulen_cap_arka_dingil_" + ad] = round(2 * r, 4)
        sonuc["supurulen_cap_govde_merkezi_" + ad] = round(2 * float(np.max(np.hypot(P[:, 0], P[:, 1]))), 4)
    sonuc["arka_dingil_x"] = round(arka_x, 4)
    sonuc["alt_geomlar"] = sorted(alt)
    # hız
    S = sur_kaydet(c, e, 0.39, 0.0, 6000)
    sonuc["ileri_v_komut_0_39"] = round(float(np.mean(S[S[:, 0] > 4.0, 4])), 4)
    S = sur_kaydet(c, e, 0.25, 0.0, 5000)
    sonuc["ileri_v_komut_0_25"] = round(float(np.mean(S[S[:, 0] > 3.0, 4])), 4)
    S = sur_kaydet(c, e, -0.25, 0.0, 4000)
    sonuc["geri_v_komut_-0_25"] = round(float(np.mean(S[S[:, 0] > 2.5, 4])), 4)
    # yerinde dönüş: w 1 (firmware tavanı) 8 s; dönme merkezi çember uydurmayla
    for wk in (1.0, 0.6):
        S = sur_kaydet(c, e, 0.0, wk, 8000)
        kalici = S[S[:, 0] > 2.0]
        sonuc["yerinde_w_komut_%g" % wk] = round(float(np.mean(kalici[:, 5])), 4)
        cx, cy, r = cember_uydur(kalici[:, 1:3])
        # dönme merkezinin gövde çerçevesindeki yeri (her satırda, ortalama)
        bx = [(cx - x) * math.cos(a) + (cy - y) * math.sin(a) for _, x, y, a, _, _ in kalici]
        by = [-(cx - x) * math.sin(a) + (cy - y) * math.cos(a) for _, x, y, a, _, _ in kalici]
        sonuc["donme_merkezi_govdede_w_%g" % wk] = dict(x=round(float(np.mean(bx)), 4), y=round(float(np.mean(by)), 4),
                                                        x_std=round(float(np.std(bx)), 4), yaricap=round(r, 4))
        dm = (float(np.mean(bx)), float(np.mean(by)))
        sonuc["supurulen_cap_olculen_merkez_w_%g" % wk] = round(
            2 * float(np.max(np.hypot(dusuk[:, 0] - dm[0], dusuk[:, 1] - dm[1]))), 4)
    # yay: v 0,25 + w 1
    S = sur_kaydet(c, e, 0.25, 1.0, 6000)
    k = S[S[:, 0] > 3.0]
    sonuc["yay_v0_25_w1"] = dict(v=round(float(np.mean(k[:, 4])), 4), w=round(float(np.mean(k[:, 5])), 4))
    # 90 derece yerinde dönüş süresi (w 1)
    yaw0 = c.dunya.poz()[3]
    t = 0
    while t < 10000:
        e.sur(0.0, 1.0)
        e.bekle(20)
        t += 20
        d = math.atan2(math.sin(c.dunya.poz()[3] - yaw0), math.cos(c.dunya.poz()[3] - yaw0))
        if d >= math.pi / 2:
            break
    sonuc["donus_90_s"] = round(t / 1000.0, 2)
    e.istek({"k": "dur"})
    e.bekle(1000)
    sonuc["donus_90_asma_derece"] = round(math.degrees(math.atan2(math.sin(c.dunya.poz()[3] - yaw0),
                                                                  math.cos(c.dunya.poz()[3] - yaw0))) - 90.0, 2)
    return sonuc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--varyant", nargs="+", default=["ONERI", "ONERI-MAKARA"])
    a = ap.parse_args()
    import lidar as L
    la = L.LidarAyar.dosyadan()
    cikti = {"lidar_montaj": dict(x=la.montaj_x_m, y=la.montaj_y_m, z=la.montaj_z_m, yaw=la.montaj_yaw_rad,
                                  kor_sektor=la.kor_sektorler_derece, kor_pay=la.kor_pay_derece),
             "varyantlar": {}}
    for v in a.varyant:
        cikti["varyantlar"][v] = olc(v)
        print(json.dumps(cikti["varyantlar"][v], ensure_ascii=False), flush=True)
    yol = os.path.join(_yol.GEZINME, "sonuc", "robot_olculeri.json")
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(cikti, f, ensure_ascii=False, indent=1)
    print("->", yol)


if __name__ == "__main__":
    main()
