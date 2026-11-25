"""Görünürlük haritası: mesafe x bakış açısı x etiket boyu x yükseklik x mercek x çözünürlük x bozulma için algılama
oranı ve poz hatası.

    %V% kod\\fizik\\sanalray\\gorunurluk.py            # -> sonuc/gorunurluk.csv (koşul başına), sonuc/ham/gorunurluk_ornek.csv
    %V% kod\\fizik\\sanalray\\gorunurluk.py --hiz      # görüntü üretimi / algılama hızı -> sonuc/hiz.csv

Sahne: düz duvar (opak, koridor duvarıyla aynı malzeme) + tek etiket + zemin; kamera kafa yüksekliğinde (1,565 m, CAD),
yatayda etikete çevrilmiş (etiket görüntünün yatay ortasında; dikeyde yüksekliğe göre). Görüntü 1536 x 864'te üretilir,
768 x 432 ve 1152 x 648 INTER_AREA ile küçültülür. Bozulmalar `kamera.boz` ile: yer gerçeği burada yalnız bozulmanın
nereye uygulanacağını (parlama / kapanma) ve hatayı ölçmek için kullanılır. Hız için kırpma: algılama etiketin çevresindeki
pencerede (en az 3 etiket boyu, 240 px) koşar; oran ve hata kırpmadan etkilenmez, süre ölçümü ayrıca tam karede yapılır."""

import argparse
import csv
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sanalray import _yol  # noqa: E402

MESAFELER = [0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]
ACILAR = [0, 30, 50, 65, 75]
BOYLAR = [0.10, 0.15, 0.20]
YUKSEKLIKLER = ["goz", "kapi_ustu"]
MERCEKLER = ["std", "genis"]
COZ = ["768x432", "1152x648", "1536x864"]
KAMERA_Z = 1.565
# bozulmalar: ad -> (örnek sayısı, ayar). Pozlama 10 ms (kamera.POZLAMA_S); loşta 30 ms.
BOZULMALAR = {
    "temiz": (4, dict(isik=1.0, okuma_gurultu=2.0)),
    "gurultu": (3, dict(isik=1.0, okuma_gurultu=10.0)),
    "los": (3, dict(isik=0.12, okuma_gurultu=2.0)),
    "parlama": (3, dict(parlama=True)),
    "kapanma25": (2, dict(kapanma=0.25)),
    "kapanma50": (2, dict(kapanma=0.50)),
    "donus_0.4": (3, dict(donus_rad_s=0.4)),
    "donus_0.89": (3, dict(donus_rad_s=0.89)),
}


def sahne_xml(boy, z):
    from sanalray import etiket as E
    e = dict(id=1, x=0.0, y=0.0, z=z, yaw=0.0, boy_m=boy)
    return """<mujoco><visual><global offwidth="1536" offheight="864"/></visual>
<asset>%s
<material name="m_sr_duvar" rgba="0.80 0.78 0.72 1" specular="0.1" shininess="0.1"/>
<texture name="t_zemin" type="2d" builtin="checker" rgb1="0.82 0.82 0.8" rgb2="0.7 0.7 0.68" width="512" height="512"/>
<material name="m_zemin" texture="t_zemin" texrepeat="1 1" texuniform="true"/></asset>
<worldbody><light pos="0 0 6" dir="0 0 -1" diffuse="0.8 0.8 0.8" directional="true"/>
<geom type="plane" size="0 0 0.05" material="m_zemin"/>
<geom type="box" pos="-0.0035 0 1.35" size="0.002 20 1.35" material="m_sr_duvar" group="2"/>
%s
<camera name="c" pos="2 0 1.565" xyaxes="0 -1 0 0 0 1" fovy="41"/></worldbody></mujoco>""" % (E.etiket_varlik([1]), E.etiket_geom(e)), e


def kamera_koy(m, d, cam, x, y, yon):
    import mujoco
    import numpy as np
    f = np.array([math.cos(yon), math.sin(yon), 0.0])
    up = np.array([0.0, 0.0, 1.0])
    xr = np.cross(f, up)
    M = np.stack([xr, up, -f], 1)
    q = np.zeros(4)
    mujoco.mju_mat2Quat(q, M.ravel())
    m.cam_pos[cam] = (x, y, KAMERA_Z)
    m.cam_quat[cam] = q
    mujoco.mj_forward(m, d)


def kosullar():
    for mer in MERCEKLER:
        for boy in BOYLAR:
            for yuk in YUKSEKLIKLER:
                for dist in MESAFELER:
                    for aci in ACILAR:
                        yield mer, boy, yuk, dist, aci


def olc(cikti_kosul, cikti_ornek, tohum=0):
    import numpy as np
    import mujoco
    from sanalray import etiket as E, kamera as KM
    rng = np.random.default_rng(tohum)
    bul = KM.Bulucu()
    satir_k, satir_o = [], []
    modeller = {}
    t_bas = time.time()
    n = 0
    for mer, boy, yuk, dist, aci in kosullar():
        z = E.YUKSEKLIKLER[yuk]
        anahtar = (boy, z)
        if anahtar not in modeller:
            xml, e = sahne_xml(boy, z)
            m = mujoco.MjModel.from_xml_string(xml)
            d = mujoco.MjData(m)
            kam = KM.Kamera(m, d, mer, 1536, 864, kamera="c")
            modeller[anahtar] = (m, d, kam, e)
        m, d, kam, e = modeller[anahtar]
        kam.mercek_ayarla(mer)
        a = math.radians(aci)
        cx, cy = dist * math.cos(a), dist * math.sin(a)
        kamera_koy(m, d, kam.cam, cx, cy, math.atan2(-cy, -cx))
        tam = kam.gri()
        p, R = kam.poz()
        gercek_menzil = math.hypot(cx, cy)
        n += 1
        for coz in COZ:
            W, H = KM.COZUNURLUKLER[coz]
            g = KM.kucult(tam, W, H)
            K = KM.ic_parametre(mer, W, H)
            uv, zz = KM.izdusur(K, p, R, KM.etiket_koseleri(e))
            gorus_ici = bool((uv[:, 0] >= 1).all() and (uv[:, 0] <= W - 2).all() and (uv[:, 1] >= 1).all() and (uv[:, 1] <= H - 2).all())
            boy_px = float(np.max(np.linalg.norm(uv - uv.mean(0), axis=1)) * 2 / math.sqrt(2))
            c = uv.mean(0)
            yari = max(120.0, 1.5 * boy_px * 1.25 + 40)
            u0, v0 = int(max(0, c[0] - yari)), int(max(0, c[1] - yari))
            u1, v1 = int(min(W, c[0] + yari)), int(min(H, c[1] + yari))
            kir = g[v0:v1, u0:u1]
            Kk = K.copy()
            Kk[0, 2] -= u0
            Kk[1, 2] -= v0
            uvk = uv - [u0, v0]
            for boz_ad, (adet, ayar) in BOZULMALAR.items():
                for i in range(adet):
                    kw = dict(isik=ayar.get("isik", 1.0), okuma_gurultu=ayar.get("okuma_gurultu", 2.0))
                    poz_s = KM.POZLAMA_S / kw["isik"] if kw["isik"] < 1 else KM.POZLAMA_S
                    poz_s = min(poz_s, 0.033)
                    if "donus_rad_s" in ayar:
                        kw["bulanik_px"] = ayar["donus_rad_s"] * poz_s * K[0, 0]
                    if kw["isik"] < 1:                       # loşta pozlama uzar: yavaş sürüş (0,25 m/s) yanal bulanıklık yok
                        pass
                    if ayar.get("parlama"):
                        kw["parlama"] = (uvk[:, 0].mean() + 0.25 * boy_px, uvk[:, 1].mean() - 0.1 * boy_px,
                                         max(3.0, 0.45 * boy_px), 230.0)
                    if "kapanma" in ayar:
                        umin, umax = uvk[:, 0].min(), uvk[:, 0].max()
                        kw["kapanma"] = [(umin - 0.4 * boy_px, -10, umin + ayar["kapanma"] * (umax - umin), kir.shape[0] + 10)]
                    gb = KM.boz(kir, rng, **kw)
                    sonuc = bul.bul(gb)
                    bulunan = [s for s in sonuc if s[0] == 1]
                    yanlis = len([s for s in sonuc if s[0] != 1])
                    r = dict(mercek=mer, boy_cm=round(boy * 100), yukseklik=yuk, mesafe_m=dist, aci_derece=aci,
                             cozunurluk=coz, bozulma=boz_ad, ornek=i, gorus_ici=int(gorus_ici), boy_px=round(boy_px, 1),
                             bulundu=int(bool(bulunan)), yanlis_kimlik=yanlis)
                    if bulunan:
                        ps = bul.poz(bulunan[0][1], boy, Kk)
                        if ps is not None:
                            rr, b, psi = KM.olcum_2b(*ps)
                            # gerçek: kamera çerçevesinde etiket (yatay): menzil, kerteriz 0 (kamera etikete dönük), psi
                            ger_psi = math.atan2(math.sin(math.pi - a), math.cos(math.pi - a))
                            ger_psi = -ger_psi if False else ger_psi
                            r.update(menzil_hata_m=round(rr - gercek_menzil, 4), kerteriz_hata_derece=round(math.degrees(b), 3),
                                     psi_hata_derece=round(math.degrees(_sar(psi - _psi_gercek(a))), 2))
                            # tek etiketten kamera pozu (etiket yeri biliniyor): konum hatası
                            th_c = _sar(0.0 - psi)                          # etiket normali yaw 0
                            f_, l_ = rr * math.cos(b), rr * math.sin(b)
                            kx = 0.0 - (math.cos(th_c) * f_ - math.sin(th_c) * l_)
                            ky = 0.0 - (math.sin(th_c) * f_ + math.cos(th_c) * l_)
                            r["tek_etiket_konum_hata_m"] = round(math.hypot(kx - cx, ky - cy), 4)
                            r["tek_etiket_yon_hata_derece"] = round(math.degrees(_sar(th_c - math.atan2(-cy, -cx))), 2)
                    satir_o.append(r)
        if n % 50 == 0:
            _yol.durum_yaz("gorunurluk %d / %d kosul, %.0f s" % (n, 600, time.time() - t_bas))
            print("gorunurluk", n, round(time.time() - t_bas), flush=True)
    for (m, d, kam, e) in modeller.values():
        kam.kapat()
    # koşul özeti
    from collections import defaultdict
    gr = defaultdict(list)
    for r in satir_o:
        gr[(r["mercek"], r["boy_cm"], r["yukseklik"], r["mesafe_m"], r["aci_derece"], r["cozunurluk"], r["bozulma"])].append(r)
    for k, rs in gr.items():
        bul_ = [r for r in rs if r["bulundu"] and "menzil_hata_m" in r]
        med = lambda a: (sorted(a)[len(a) // 2] if a else None)
        satir_k.append(dict(mercek=k[0], boy_cm=k[1], yukseklik=k[2], mesafe_m=k[3], aci_derece=k[4], cozunurluk=k[5],
                            bozulma=k[6], n=len(rs), gorus_ici=rs[0]["gorus_ici"], boy_px=rs[0]["boy_px"],
                            algilama_orani=round(sum(r["bulundu"] for r in rs) / len(rs), 3),
                            yanlis_kimlik=sum(r["yanlis_kimlik"] for r in rs),
                            menzil_hata_med_m=med([abs(r["menzil_hata_m"]) for r in bul_]),
                            kerteriz_hata_med_derece=med([abs(r["kerteriz_hata_derece"]) for r in bul_]),
                            psi_hata_med_derece=med([abs(r["psi_hata_derece"]) for r in bul_]),
                            tek_etiket_konum_hata_med_m=med([r["tek_etiket_konum_hata_m"] for r in bul_ if "tek_etiket_konum_hata_m" in r])))
    _csv(cikti_ornek, satir_o)
    _csv(cikti_kosul, satir_k)
    return satir_k


def _psi_gercek(a):
    # kamera etiketin normalinden a açısıyla (etiket çerçevesinde +a yönünde) bakıyor; kamera ileri = etikete doğru.
    # etiket normali (yaw 0) kamera yönünde: normal yaw 0, kamera yaw = pi + a  ->  psi = 0 - (pi + a)
    return _sar(-(math.pi + a))


def _sar(x):
    return (x + math.pi) % (2 * math.pi) - math.pi


def _csv(yol, satirlar):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    alan = []
    for r in satirlar:
        for k in r:
            if k not in alan:
                alan.append(k)
    with open(yol, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=alan)
        w.writeheader()
        for r in satirlar:
            w.writerow(r)


def hiz_olc(cikti):
    """mujoco.Renderer görüntü üretimi ve aruco algılama süresi (bu makine), koridor sahnesinde kafa kamerasından."""
    import numpy as np
    from sanalray import etiket as E, kamera as KM
    from gezinme.duzenek import Duzenek
    plan = E.plan_oku("koridor_1", 5, 0.15, "goz")
    dz = Duzenek(E.etiketli_sahne("koridor_1", plan), tohum=0)
    dz.lidar.ayir()
    out = []
    bul = KM.Bulucu()
    rng = np.random.default_rng(0)
    for coz, (W, H) in KM.COZUNURLUKLER.items():
        for mer in MERCEKLER:
            kam = KM.Kamera(dz.w.m, dz.w.d, mer, W, H)
            for _ in range(5):
                kam.gri()
            t0 = time.perf_counter()
            N = 40
            for _ in range(N):
                g = kam.gri()
            t_r = (time.perf_counter() - t0) / N
            t0 = time.perf_counter()
            for _ in range(N):
                gb = KM.boz(g, rng)
            t_b = (time.perf_counter() - t0) / N
            t0 = time.perf_counter()
            for _ in range(N):
                s = bul.bul(gb)
            t_a = (time.perf_counter() - t0) / N
            out.append(dict(cozunurluk=coz, mercek=mer, uretim_ms=round(t_r * 1000, 2), uretim_kare_s=round(1 / t_r, 1),
                            bozulma_ms=round(t_b * 1000, 2), algilama_ms=round(t_a * 1000, 2),
                            toplam_kare_s=round(1 / (t_r + t_b + t_a), 1), bulunan=len(s)))
            print(out[-1], flush=True)
            kam.kapat()
    _csv(cikti, out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hiz", action="store_true")
    a = ap.parse_args()
    _yol.dusuk_oncelik()
    if a.hiz:
        hiz_olc(os.path.join(_yol.SONUC, "hiz.csv"))
        return 0
    olc(os.path.join(_yol.SONUC, "gorunurluk.csv"), os.path.join(_yol.HAM, "gorunurluk_ornek.csv"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
