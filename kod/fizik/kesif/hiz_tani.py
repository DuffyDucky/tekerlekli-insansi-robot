"""Hız tanısı (v4 öncesi ölçüm): MuJoCo kayıtlarında (.npz) düz sürüşün hız dağılımı, v2 hızlı kip koşullarının
hangisinin ne kadar engellediği, hızlanma / yavaşlama rampaları, kısa geçitlerde kayıp ve ideal ivmelenmeyle üst sınır.
Yer gerçeği (sahne duvarları, gerçek poz) yalnız ölçüm içindir (duvar payı); beyin bunu görmez.

    py -3 -m kesif.hiz_tani --dizin sonuc/ham/mujoco_v3,sonuc/ham/mujoco_sinama2_v3 --cikti sonuc/hiz_tani_v3.csv
    py -3 -m kesif.hiz_tani --dizin sonuc/ham/mujoco_v4 --cikti sonuc/hiz_tani_v4.csv

Tanımlar (satır başına bir koşu):
- duz: |v_komut| > 0,02 m/s ve mod kurtarma dışı (tani.py ile aynı; yay dahil). v_duz_ort: düzde |ölçülen v| ortalaması.
- hizli_pay: düz sürenin v_komut > 0,26 olan payı.
- kosul_*: düz sürede v2 hızlı kip koşulunun TEK BAŞINA sağlanmadığı süre payı. A = son taramada gövde önünde 1,0 m ve
  her yana +0,15 m şerit boş; B = son açısal komut <= 0,12 rad/s; C = son yerinde dönüş / kurtarmadan >= 1,5 s.
  yalniz_A / yalniz_B / yalniz_C: yalnız o koşulun engellediği pay (öbür ikisi sağlanıyor).
- parca: ardışık düz adımlar (0,1 s'den kısa boşluk birleşir). ideal_s: parçanın uzunluğunu dur-kalk ile 0,39 m/s tavan,
  0,5 m/s² hızlanma ve 0,5 m/s² yavaşlamayla katetme süresi (yay ve eğrilik yok sayılır: ÜST SINIR). ust_kazanc_s =
  toplam (gerçek - ideal). kisa_*: 1,5 m'den kısa parçalar.
- rampa_hiz_s: parça başında ölçülen hızın 0,2'ye çıkmasına kadar geçen süre (toplam); kuyruk_s: parça sonunda
  ölçülen hızın 0,10 m/s altında geçen süre (yumuşak varış kuyruğu).
- duvar_pay_min_m: gerçek pozda ayak izi (0,528 x 0,523 m) ile duvar çizgileri arası en küçük uzaklık (her 2. adım).
"""

import argparse
import ast
import csv
import glob
import json
import math
import os

import numpy as np

KESIF = os.path.dirname(os.path.abspath(__file__))
ON_X = 0.2642
YARI_Y = 0.2617
SERIT_YARI = 0.28          # beyin on_serit_m / 2
HIZLI_YAN = 0.15
A_ACC = 0.5
A_DEC = 0.5
KURTARMA = {"kurtarma", "konumlan", "duvar_izle", "tukendi"}

ALANLAR = ["kume", "surum", "sahne", "tohum", "durum", "sure_s", "duz_s", "duz_pay", "v_duz_ort", "v_duz_p50",
           "hizli_pay", "kosul_A", "kosul_B", "kosul_C", "yalniz_A", "yalniz_B", "yalniz_C", "uc_kosul",
           "parca_sayisi", "parca_ort_m", "ideal_duz_s", "ust_kazanc_s", "ust_sure_s", "kisa_parca", "kisa_s",
           "kisa_ideal_s", "rampa_hiz_s", "kuyruk_s", "serbest_ort_m", "h_0_10", "h_10_20", "h_20_24", "h_24_26",
           "h_26_33", "h_33_40", "carpma_temas_s", "duvar_pay_min_m", "duvar_pay_p01_m"]


def ideal_sure(D, v=0.39, a1=A_ACC, a2=A_DEC):
    """Dur-kalk düz parça: 0'dan v'ye a1, v'den 0'a a2 (üçgen profil kısa parçada)."""
    d_ramp = v * v / (2 * a1) + v * v / (2 * a2)
    if D >= d_ramp:
        return (D - d_ramp) / v + v / a1 + v / a2
    vp = math.sqrt(2 * D * a1 * a2 / (a1 + a2))
    return vp / a1 + vp / a2


def _sahne_duvar(ad):
    from ._yol import HARITALAR, SAHNELER
    with open(os.path.join(SAHNELER, ad + ".json"), encoding="utf-8") as f:
        s = json.load(f)
    with open(os.path.join(HARITALAR, s["harita"] + ".json"), encoding="utf-8") as f:
        h = json.load(f)
    return np.array(h["duvarlar"], dtype=float)


def duvar_payi(gercek, duvar, adim=2):
    """Ayak izi dikdörtgeni ile duvar parçaları arası en küçük uzaklık dizisi (m; kesişme -> 0)."""
    P = gercek[::adim]
    out = np.empty(len(P))
    A, B = duvar[:, :2], duvar[:, 2:]
    kose = np.array([[-ON_X, -YARI_Y], [ON_X, -YARI_Y], [ON_X, YARI_Y], [-ON_X, YARI_Y]])
    for k, (x, y, th) in enumerate(P):
        c, s = math.cos(th), math.sin(th)
        # yakın duvarlar
        dmin = np.minimum(np.hypot(A[:, 0] - x, A[:, 1] - y), np.hypot(B[:, 0] - x, B[:, 1] - y))
        AB = B - A
        L2 = (AB ** 2).sum(1)
        tt = np.clip(((x - A[:, 0]) * AB[:, 0] + (y - A[:, 1]) * AB[:, 1]) / np.maximum(L2, 1e-12), 0, 1)
        dmerk = np.hypot(A[:, 0] + tt * AB[:, 0] - x, A[:, 1] + tt * AB[:, 1] - y)
        yakin = np.minimum(dmin, dmerk) < 1.5
        if not yakin.any():
            out[k] = 9.9
            continue
        a, b = A[yakin], B[yakin]
        # gövde çerçevesine
        ax = c * (a[:, 0] - x) + s * (a[:, 1] - y)
        ay = -s * (a[:, 0] - x) + c * (a[:, 1] - y)
        bx = c * (b[:, 0] - x) + s * (b[:, 1] - y)
        by = -s * (b[:, 0] - x) + c * (b[:, 1] - y)
        # duvar uçlarının kutuya uzaklığı
        def kutu(px, py):
            dx = np.maximum(np.abs(px) - ON_X, 0)
            dy = np.maximum(np.abs(py) - YARI_Y, 0)
            return np.hypot(dx, dy)
        d1 = np.minimum(kutu(ax, ay), kutu(bx, by))
        # kutu köşelerinin parçalara uzaklığı
        ex, ey = bx - ax, by - ay
        l2 = np.maximum(ex * ex + ey * ey, 1e-12)
        d2 = np.full(ax.shape, 9.9)
        for kx, ky in kose:
            u = np.clip(((kx - ax) * ex + (ky - ay) * ey) / l2, 0, 1)
            d2 = np.minimum(d2, np.hypot(ax + u * ex - kx, ay + u * ey - ky))
        # kesişme: parça kutunun içinden geçiyor (Liang-Barsky)
        kes = np.zeros(ax.shape, bool)
        t0 = np.zeros(ax.shape)
        t1 = np.ones(ax.shape)
        ok = np.ones(ax.shape, bool)
        for p, q in ((-ex, ax + ON_X), (ex, ON_X - ax), (-ey, ay + YARI_Y), (ey, YARI_Y - ay)):
            sifir = np.abs(p) < 1e-12
            ok &= ~(sifir & (q < 0))
            r = np.where(sifir, 0, q / np.where(sifir, 1, p))
            t0 = np.where(~sifir & (p < 0), np.maximum(t0, r), t0)
            t1 = np.where(~sifir & (p > 0), np.minimum(t1, r), t1)
        kes = ok & (t0 <= t1)
        d = np.minimum(d1, d2) - 0.001
        d[kes] = 0.0
        out[k] = float(d.min())
    return out


def tek(yol):
    from gezinme.duzenek import kayit_oku
    m, d = kayit_oku(yol)
    t = d["t"]
    dt = np.diff(t, prepend=0.0)
    dt[0] = t[0] if len(t) else 0.0
    vk, wk = d["komut"][:, 0], d["komut"][:, 1]
    vg = d["olculen"][:, 0]
    modlar = m.get("modlar")
    if isinstance(modlar, str):
        modlar = ast.literal_eval(modlar)
    mod = np.array([modlar[i] for i in d["mod"]])
    kur = np.isin(mod, list(KURTARMA))
    duz = (np.abs(vk) > 0.02) & ~kur
    # son yerinde dönüş / kurtarma
    don = ((np.abs(vk) < 0.02) & (np.abs(wk) > 0.05)) | kur
    son_don = np.where(don, t, -1e9)
    son_don = np.maximum.accumulate(son_don)
    kC = (t - son_don) >= 1.5
    w_onceki = np.concatenate([[0.0], wk[:-1]])
    kB = np.abs(w_onceki) <= 0.12
    # tarama koşulu (son tarama, gövde çerçevesi)
    t0d = float(m.get("t0_dunya_s") or 0.0)
    tt = d["tarama_t"] - t0d
    mm = d["tarama_mm"].astype(float) / 1000.0
    ac = d["acilar"]
    montaj = m.get("montaj")
    if isinstance(montaj, str):
        montaj = ast.literal_eval(montaj)
    mx, my = (montaj or [0.19, 0.0])[:2]
    gec = mm > 0
    px = mx + mm * np.cos(ac)[None, :]
    py = my + mm * np.sin(ac)[None, :]
    serit_h = gec & (np.abs(py) <= SERIT_YARI + HIZLI_YAN) & (px > ON_X - 0.02) & (px < ON_X + 1.0)
    acikA = ~serit_h.any(1)
    seritO = gec & (np.abs(py) <= SERIT_YARI) & (px > ON_X - 0.02)
    serbest = np.where(seritO, px - ON_X, np.inf).min(1)
    ti = np.searchsorted(tt, t, side="right") - 1
    kA = np.where(ti >= 0, acikA[np.clip(ti, 0, None)], False)
    sb = np.where(ti >= 0, serbest[np.clip(ti, 0, None)], np.nan)
    Td = float(dt[duz].sum())

    def pay(mask):
        return round(float(dt[duz & mask].sum()) / Td, 3) if Td > 0 else None
    hizli = vk > 0.26
    # parçalar
    idx = np.nonzero(duz)[0]
    parcalar = []
    if idx.size:
        bas = idx[0]
        onc = idx[0]
        for i in idx[1:]:
            if t[i] - t[onc] > 0.1 + 1e-6:
                parcalar.append((bas, onc))
                bas = i
            onc = i
        parcalar.append((bas, onc))
    ideal = 0.0
    gercek_s = 0.0
    kisa_n = 0
    kisa_s = kisa_i = 0.0
    rampa = kuyruk = 0.0
    uz = []
    for a, b in parcalar:
        sl = slice(a, b + 1)
        T = float(dt[sl].sum())
        D = float((np.abs(vg[sl]) * dt[sl]).sum())
        uz.append(D)
        ti_ = ideal_sure(D)
        ideal += min(T, ti_)
        gercek_s += T
        if D < 1.5:
            kisa_n += 1
            kisa_s += T
            kisa_i += min(T, ti_)
        v = np.abs(vg[sl])
        tseg = t[sl]
        k = np.nonzero(v >= 0.2)[0]
        if k.size:
            rampa += float(tseg[k[0]] - tseg[0])
            son = k[-1]
            kuyruk += float(dt[sl][son + 1:].sum())
        else:
            rampa += T
    H = np.abs(vg[duz])
    w8 = dt[duz]

    def hpay(lo, hi):
        return round(float(w8[(H >= lo) & (H < hi)].sum()) / Td, 3) if Td > 0 else None
    hk = m.get("hakem")
    if isinstance(hk, str):
        try:
            hk = ast.literal_eval(hk)
        except (ValueError, SyntaxError):
            hk = {}
    hk = hk or {}
    ad = m.get("sahne")
    duvar = _sahne_duvar(ad)
    dp = duvar_payi(d["gercek"], duvar)
    tem = float(dt[d["temas"] > 0].sum())
    sure = float(t[-1]) if len(t) else 0.0
    return {"kume": m.get("kume"), "surum": m.get("beyin_surum"), "sahne": ad, "tohum": m.get("tohum"),
            "durum": hk.get("durum"), "sure_s": round(sure, 1), "duz_s": round(Td, 1),
            "duz_pay": round(Td / sure, 3) if sure else None,
            "v_duz_ort": round(float(H.mean()), 3) if H.size else None,
            "v_duz_p50": round(float(np.median(H)), 3) if H.size else None,
            "hizli_pay": pay(hizli), "kosul_A": pay(~kA), "kosul_B": pay(~kB), "kosul_C": pay(~kC),
            "yalniz_A": pay(~kA & kB & kC), "yalniz_B": pay(kA & ~kB & kC), "yalniz_C": pay(kA & kB & ~kC),
            "uc_kosul": pay(kA & kB & kC),
            "parca_sayisi": len(parcalar), "parca_ort_m": round(float(np.mean(uz)), 2) if uz else None,
            "ideal_duz_s": round(ideal, 1), "ust_kazanc_s": round(gercek_s - ideal, 1),
            "ust_sure_s": round(sure - (gercek_s - ideal), 1), "kisa_parca": kisa_n, "kisa_s": round(kisa_s, 1),
            "kisa_ideal_s": round(kisa_i, 1), "rampa_hiz_s": round(rampa, 1), "kuyruk_s": round(kuyruk, 1),
            "serbest_ort_m": round(float(np.nanmean(np.where(np.isfinite(sb[duz]), sb[duz], 4.0))), 2)
            if duz.any() else None,
            "h_0_10": hpay(0, 0.10), "h_10_20": hpay(0.10, 0.20), "h_20_24": hpay(0.20, 0.24),
            "h_24_26": hpay(0.24, 0.26), "h_26_33": hpay(0.26, 0.33), "h_33_40": hpay(0.33, 0.45),
            "carpma_temas_s": round(tem, 2), "duvar_pay_min_m": round(float(dp.min()), 3),
            "duvar_pay_p01_m": round(float(np.percentile(dp, 1)), 3)}


def _guvenli(yol):
    from ._yol import dusuk_oncelik
    dusuk_oncelik()
    try:
        return tek(yol)
    except Exception as e:     # bozuk kayıt da bir sonuçtur
        return {"sahne": os.path.basename(yol), "durum": "hata: %s" % e}


def main(argv=None):
    from ._yol import dusuk_oncelik
    dusuk_oncelik()
    p = argparse.ArgumentParser()
    p.add_argument("--dizin", required=True, help="virgüllü, kesif/ klasörüne göreli kayıt klasörleri")
    p.add_argument("--cikti", required=True)
    p.add_argument("--is", dest="is_sayisi", type=int, default=2)
    a = p.parse_args(argv)
    yollar = []
    for dz in a.dizin.split(","):
        yollar += sorted(g for g in glob.glob(os.path.join(KESIF, dz, "*.npz")) if "_hafiza" not in g)
    import multiprocessing as mp
    with mp.get_context("spawn").Pool(max(1, min(4, a.is_sayisi))) as hv:
        S = list(hv.imap(_guvenli, yollar))
    with open(os.path.join(KESIF, a.cikti), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ALANLAR, extrasaction="ignore")
        w.writeheader()
        for s in S:
            w.writerow(s)
    print(ozet(S))


def ozet(S):
    S = [s for s in S if s.get("duz_s")]
    if not S:
        return "kayit yok"
    T = sum(s["sure_s"] for s in S)
    Td = sum(s["duz_s"] for s in S)

    def ag(k):     # düz süre ağırlıklı
        return sum((s[k] or 0) * s["duz_s"] for s in S) / Td
    sat = ["koşu %d, toplam %.0f s, düz pay %.3f, v_duz_ort (ağırlıklı) %.3f" % (len(S), T, Td / T, ag("v_duz_ort")),
           "hızlı pay %.3f; tek başına engelleyen: A %.3f, B %.3f, C %.3f; yalnız A %.3f, yalnız B %.3f, yalnız C %.3f; "
           "üçü sağlanır %.3f" % tuple(ag(k) for k in ("hizli_pay", "kosul_A", "kosul_B", "kosul_C", "yalniz_A",
                                                      "yalniz_B", "yalniz_C", "uc_kosul")),
           "hız dağılımı (düz süre payı): <0,10 %.3f | 0,10-0,20 %.3f | 0,20-0,24 %.3f | 0,24-0,26 %.3f | 0,26-0,33 %.3f"
           " | >=0,33 %.3f" % tuple(ag(k) for k in ("h_0_10", "h_10_20", "h_20_24", "h_24_26", "h_26_33", "h_33_40")),
           "parça %d (ort %.2f m), kısa (<1,5 m) %d parça %.0f s (ideal %.0f s); rampa %.0f s, kuyruk %.0f s" % (
               sum(s["parca_sayisi"] for s in S), np.mean([s["parca_ort_m"] for s in S]),
               sum(s["kisa_parca"] for s in S), sum(s["kisa_s"] for s in S), sum(s["kisa_ideal_s"] for s in S),
               sum(s["rampa_hiz_s"] for s in S), sum(s["kuyruk_s"] for s in S)),
           "ideal düz %.0f s / gerçek düz %.0f s -> üst kazanç %.0f s (%.1f%% toplam süre)" % (
               sum(s["ideal_duz_s"] for s in S), Td, sum(s["ust_kazanc_s"] for s in S),
               100 * sum(s["ust_kazanc_s"] for s in S) / T),
           "duvar payı en küçük %.3f m, temas %.2f s" % (min(s["duvar_pay_min_m"] for s in S),
                                                        sum(s["carpma_temas_s"] for s in S))]
    return "\n".join(sat)


if __name__ == "__main__":
    main()
