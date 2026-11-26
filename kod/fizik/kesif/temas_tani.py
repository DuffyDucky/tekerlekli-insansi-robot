"""Temas tanısı (yalnız ölçüm): MuJoCo kaydında (.npz) her temas olayını kayıttan yeniden oynatır.

    py -3 -m kesif.temas_tani --kayit sonuc/ham/mujoco_v5/labirent_17x17_t1_t1.npz,... --cikti sonuc/tani_temas_v6.csv

Yer gerçeği (sahne duvarları, gerçek poz) yalnız tanı içindir; beyin bunu görmez. Olay başına:
- temas noktası: gerçek pozda ayak izi kutusunun (±0,264 x ±0,262 m) duvar çizgisine en yakın noktası (gövde çerçevesi;
  köşe / yan etiketi) ve duvarın neresi (duvar ucu: çizgi ucu 3 cm içinde; değilse yüz);
- manevra: temastan önceki 3 s'nin kipleri, komut / ölçülen v, w, son yerinde dönüşten geçen süre;
- görünürlük: temas edilen duvar noktası son 3 s'nin taramalarında (gerçek pozla dünyaya çevrilmiş ışın uçları) 4 cm
  içinde ölçüldü mü; son ölçüm temastan kaç s önce; temas anında noktanın LiDAR çerçevesinde açısı (kör sektör
  [134, 226] derece) ve gövde x'i (LiDAR x = +0,19 m'nin gerisi mi);
- harita: temastan önceki son harita anlık görüntüsünde (beyin çerçevesi, beyin pozuyla) noktanın 5 cm çevresinde dolu
  hücre var mı;
- öngörü: temastan önceki 2 s boyunca her 0,1 s'de beyin öngörüsünün (surus4.yay_pozlari + supurme_carpar, komut v / w
  ile, ufuk fren mesafesi + 0,30 m) (a) yalnız son tarama, (b) yalnız harita, (c) son 2 s taramaları birikmiş (beyin
  pozuyla) kaynağıyla çarpma öngördüğü an sayısı. Taramalar çarpıklık giderilmeden gövde çerçevesine çevrilir (yaklaşık).
"""

import argparse
import ast
import csv
import math
import os

import numpy as np

KESIF = os.path.dirname(os.path.abspath(__file__))
ON_X = 0.2642
YARI_Y = 0.2617
LIDAR_X = 0.19

ALANLAR = ["kayit", "surum", "sahne", "tohum", "t_temas", "temas_s", "temas_kenar", "govde_nokta", "govde_x", "govde_y",
           "duvar_turu", "kipler_3s", "v_komut", "w_komut", "v_olc", "w_olc", "son_yerinde_s", "son_gorulme_s",
           "gorulen_tarama_3s", "tarama_3s", "lidar_aci_der", "kor_sektor", "lidar_gerisi", "harita_dolu",
           "harita_t", "ongoru_son_tarama", "ongoru_harita", "ongoru_birikmis", "ongoru_an", "poz_hata_m",
           "yorum"]


def _sar(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def olaylar(t, temas, birlestir_s=0.2):
    idx = np.where(temas > 0)[0]
    out = []
    for i in idx:
        if out and t[i] - t[out[-1][1]] <= birlestir_s:
            out[-1][1] = i
        else:
            out.append([i, i])
    return out


def kutu_temas(x, y, th, duvar):
    """Ayak izi kutusu ile en yakın duvar çizgisi: (uzaklık, kutu noktası gövde çerçevesi, duvar noktası dünya,
    duvar ucuna uzaklık)."""
    c, s = math.cos(th), math.sin(th)
    en = (9e9, None, None, None)
    A, B = duvar[:, :2], duvar[:, 2:]
    d0 = np.minimum(np.hypot(A[:, 0] - x, A[:, 1] - y), np.hypot(B[:, 0] - x, B[:, 1] - y))
    for k in np.where(d0 < 3.0)[0]:
        a, b = A[k], B[k]
        # çizgiyi 2 mm adımla örnekle, kutu uzaklığı
        L = math.hypot(*(b - a))
        n = max(2, int(L / 0.002) + 1)
        u = np.linspace(0, 1, n)
        px, py = a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1])
        bx = c * (px - x) + s * (py - y)
        by = -s * (px - x) + c * (py - y)
        dx = np.maximum(np.abs(bx) - ON_X, 0)
        dy = np.maximum(np.abs(by) - YARI_Y, 0)
        d = np.hypot(dx, dy)
        i = int(np.argmin(d))
        if d[i] < en[0]:
            kx = float(np.clip(bx[i], -ON_X, ON_X))
            ky = float(np.clip(by[i], -YARI_Y, YARI_Y))
            uc = min(math.hypot(px[i] - a[0], py[i] - a[1]), math.hypot(px[i] - b[0], py[i] - b[1]))
            en = (float(d[i]), (kx, ky), (float(px[i]), float(py[i])), uc)
    return en


def nokta_adi(kx, ky):
    kose_x = abs(abs(kx) - ON_X) < 0.03
    kose_y = abs(abs(ky) - YARI_Y) < 0.03
    on = "ön" if kx > 0 else "arka"
    yan = "sol" if ky > 0 else "sağ"
    if kose_x and kose_y:
        return "%s %s köşe" % (yan, on)
    if kose_y:
        return "%s yan (x %+.2f)" % (yan, kx)
    return "%s yüz (y %+.2f)" % (on, ky)


def tarama_govde(mm, acilar):
    r = mm.astype(float) / 1000.0
    ok = mm > 0
    return LIDAR_X + r[ok] * np.cos(acilar[ok]), r[ok] * np.sin(acilar[ok])


def harita_al(d, m, t_ust):
    best = None
    for h in m["haritalar"]:
        if h["t"] <= t_ust:
            best = h
    if best is None:
        return None
    return best, d[best["anahtar"]]


def tek(yol, robot=None):
    from gezinme.duzenek import kayit_oku
    from .hiz_tani import _sahne_duvar
    from .robot import VARSAYILAN, gezinmeden_oku
    from .sahne import dunyadan_beyne, sahne_yukle
    from .surus4 import supurme_carpar, yay_pozlari
    robot = robot or gezinmeden_oku(VARSAYILAN)
    m, d = kayit_oku(yol)
    ad = m["sahne"]
    s2 = sahne_yukle(ad)
    duvar = _sahne_duvar(ad)
    t = d["t"]
    G, T, K, O = d["gercek"], d["tahmin"], d["komut"], d["olculen"]
    modlar = m.get("modlar")
    if isinstance(modlar, str):
        modlar = ast.literal_eval(modlar)
    mod = [modlar[i] for i in d["mod"]]
    t0d = float(m.get("t0_dunya_s") or 0.0)
    tt = d["tarama_t"] - t0d
    TM = d["tarama_mm"]
    acilar = d["acilar"]
    satirlar = []
    for i0, i1 in olaylar(t, d["temas"]):
        x, y, th = G[i0]
        dist, kb, kw, uc = kutu_temas(x, y, th, duvar)
        tc = float(t[i0])
        p = (t >= tc - 3.0) & (t <= tc)
        kip = []
        for j in np.where(p)[0]:
            if not kip or kip[-1] != mod[j]:
                kip.append(mod[j])
        yer = np.where((t <= tc) & (np.abs(K[:, 0]) < 0.02) & (np.abs(K[:, 1]) > 0.05))[0]
        son_yer = tc - float(t[yer[-1]]) if yer.size else float("nan")
        # görünürlük
        gor, n3, son_gor = 0, 0, float("nan")
        for k in np.where((tt >= tc - 3.0) & (tt <= tc + 0.05))[0]:
            j = int(np.searchsorted(t, tt[k]).clip(0, len(t) - 1))
            gx, gy, gth = G[j]
            bx, by = tarama_govde(TM[k], acilar)
            wx = gx + math.cos(gth) * bx - math.sin(gth) * by
            wy = gy + math.sin(gth) * bx + math.cos(gth) * by
            n3 += 1
            if bx.size and float(np.hypot(wx - kw[0], wy - kw[1]).min()) < 0.04:
                gor += 1
                son_gor = tc - float(tt[k])
        # temas anında LiDAR çerçevesi
        c, s = math.cos(th), math.sin(th)
        bx = c * (kw[0] - x) + s * (kw[1] - y)
        by = -s * (kw[0] - x) + c * (kw[1] - y)
        aci = math.degrees(math.atan2(by, bx - LIDAR_X)) % 360.0
        kor = 134.0 <= aci <= 226.0
        # harita: duvar noktası beyin çerçevesinde, BEYİN pozuyla (gövde çerçevesi -> tahmin)
        hb = harita_al(d, m, tc)
        harita_dolu = ""
        h_t = ""
        tx_, ty_, tth_ = T[i0]
        if hb is not None:
            h, iz = hb
            h_t = round(tc - h["t"], 2)
            px = tx_ + math.cos(tth_) * bx - math.sin(tth_) * by
            py = ty_ + math.sin(tth_) * bx + math.cos(tth_) * by
            coz = h["cozunurluk_m"]
            ox, oy = h["orijin"]
            jx, jy = int((px - ox) / coz), int((py - oy) / coz)
            pen = iz[max(0, jy - 1):jy + 2, max(0, jx - 1):jx + 2]
            harita_dolu = int((pen == 100).any())
        # poz hatası (beyin çerçevesi)
        ex, ey = dunyadan_beyne(s2, np.array([x]), np.array([y]))
        poz_hata = float(math.hypot(ex[0] - tx_, ey[0] - ty_))
        # öngörü: son 2 s her 0,1 s
        a_n = {"son": 0, "harita": 0, "birik": 0}
        an = 0
        for tq in np.arange(tc - 2.0, tc + 1e-6, 0.1):
            j = int(np.searchsorted(t, tq).clip(0, len(t) - 1))
            v, w = float(K[j, 0]), float(K[j, 1])
            if abs(v) < 0.02:
                continue
            an += 1
            kap = w / v if abs(v) > 1e-3 else 0.0
            ufuk = v * 0.15 + v * v / (2 * 0.5) + 0.30
            P = yay_pozlari(abs(v), float(O[j, 1]), kap, robot.dingil_x_m, ufuk, a_w=3.0, w_max=1.0)
            ks = np.where(tt <= tq)[0]
            if not ks.size:
                continue
            sx, sy = tarama_govde(TM[ks[-1]], acilar)
            if supurme_carpar(P, robot, 0.03, tarama_xy=(sx, sy)):
                a_n["son"] += 1
            hb2 = harita_al(d, m, tq)
            pj = T[j]
            if hb2 is not None:
                h2, iz2 = hb2
                coz = h2["cozunurluk_m"]
                ox, oy = h2["orijin"]

                def dolu_mu(wx, wy, iz2=iz2, coz=coz, ox=ox, oy=oy):
                    jx = ((wx - ox) / coz).astype(int)
                    jy = ((wy - oy) / coz).astype(int)
                    ok = (jx >= 0) & (jx < iz2.shape[1]) & (jy >= 0) & (jy < iz2.shape[0])
                    return bool((iz2[jy[ok], jx[ok]] == 100).any())
                if supurme_carpar(P, robot, 0.03, dolu_mu=dolu_mu, govde_poz=tuple(pj)):
                    a_n["harita"] += 1
            # birikmiş: son 2 s taramaları beyin pozuyla şimdiki gövde çerçevesine
            BX, BY = [], []
            for k in ks[-20:]:
                if tt[k] < tq - 2.0:
                    continue
                jk = int(np.searchsorted(t, tt[k]).clip(0, len(t) - 1))
                qx, qy, qth = T[jk]
                ux, uy = tarama_govde(TM[k], acilar)
                wx = qx + math.cos(qth) * ux - math.sin(qth) * uy
                wy = qy + math.sin(qth) * ux + math.cos(qth) * uy
                c2, s2_ = math.cos(pj[2]), math.sin(pj[2])
                BX.append(c2 * (wx - pj[0]) + s2_ * (wy - pj[1]))
                BY.append(-s2_ * (wx - pj[0]) + c2 * (wy - pj[1]))
            if BX and supurme_carpar(P, robot, 0.03, tarama_xy=(np.concatenate(BX), np.concatenate(BY))):
                a_n["birik"] += 1
        satirlar.append({
            "kayit": os.path.relpath(yol, KESIF).replace("\\", "/"), "surum": m.get("beyin_surum"), "sahne": ad,
            "tohum": m.get("tohum"), "t_temas": round(tc, 2), "temas_s": round(float(t[i1] - t[i0]) + 0.05, 2),
            "temas_kenar": i1 - i0 + 1, "govde_nokta": nokta_adi(*kb), "govde_x": round(kb[0], 3),
            "govde_y": round(kb[1], 3), "duvar_turu": "duvar ucu (%.2f m)" % uc if uc < 0.03 else "yüz (uca %.2f m)" % uc,
            "kipler_3s": ">".join(kip), "v_komut": round(float(K[i0, 0]), 3), "w_komut": round(float(K[i0, 1]), 3),
            "v_olc": round(float(O[i0, 0]), 3), "w_olc": round(float(O[i0, 1]), 3),
            "son_yerinde_s": round(son_yer, 2), "son_gorulme_s": round(son_gor, 2), "gorulen_tarama_3s": gor,
            "tarama_3s": n3, "lidar_aci_der": round(aci, 1), "kor_sektor": int(kor), "lidar_gerisi": int(bx < LIDAR_X),
            "harita_dolu": harita_dolu, "harita_t": h_t, "ongoru_son_tarama": a_n["son"], "ongoru_harita": a_n["harita"],
            "ongoru_birikmis": a_n["birik"], "ongoru_an": an, "poz_hata_m": round(poz_hata, 3), "yorum": ""})
    return satirlar


def main():
    from ._yol import dusuk_oncelik
    dusuk_oncelik()
    ap = argparse.ArgumentParser()
    ap.add_argument("--kayit", required=True)
    ap.add_argument("--cikti", default=None)
    a = ap.parse_args()
    out = []
    for y in a.kayit.split(","):
        out += tek(os.path.join(KESIF, y) if not os.path.isabs(y) else y)
    for r in out:
        print(r)
    if a.cikti:
        with open(os.path.join(KESIF, a.cikti), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=ALANLAR)
            w.writeheader()
            w.writerows(out)


if __name__ == "__main__":
    main()
