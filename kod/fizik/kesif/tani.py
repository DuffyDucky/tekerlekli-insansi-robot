"""MuJoCo kaydı (.npz) zaman dökümü ve keşif verimi tanısı. Yer gerçeği (sahne labirenti) yalnız ölçüm içindir;
beyin bunu görmez.

    py -3 -m kesif.tani sonuc/ham/mujoco/labirent_17x17_t3_t0.npz [...]   # tek tek
    py -3 -m kesif.tani --csv sonuc/mujoco.csv --cikti sonuc/tani_v1.csv  # csv'deki tüm kayıtlar

Zaman kalemleri (ayrık, toplamı koşu süresi):
- kurtarma: beyin modu kurtarma / konumlan / duvar_izle / tukendi
- duz: |v_komut| > 0,02 m/s (yay dahil)
- donus: |v_komut| <= 0,02 ve |w_komut| > 0,05 rad/s (yerinde dönüş, bakış dönüşü dahil)
- bekle: geri kalan (başlangıç taraması, plan bekleme, engel bekleme)
Kesişen kalemler: tekrar_s = daha önce girilip çıkılmış hücrede geçen süre (geri dönüş); cikmaz_s = çözüm yolu
dışındaki hücrelerde geçen süre; cikmaz_gir = girilen çıkmaz kol sayısı (kol: tek açık kenarlı hücreden kavşağa);
cikmaz_gorulmus = girildiği anda o kolun tüm hücre merkezleri son harita anlık görüntüsünde zaten biliniyordu (uzaktan elenebilirdi).
"""

import ast
import csv
import json
import math
import os
import sys

import numpy as np

KESIF = os.path.dirname(os.path.abspath(__file__))
KURTARMA_MOD = {"kurtarma", "konumlan", "duvar_izle", "tukendi"}
ALANLAR = ["sahne", "tohum", "surum", "durum", "sure_s", "kurtarma_s", "duz_s", "donus_s", "bekle_s", "tekrar_s",
           "cikmaz_s", "yol_m", "cozum_m", "yol_orani", "cikmaz_gir", "cikmaz_gorulmus", "dal_sayisi", "hucre_gezilen",
           "hucre_toplam", "v_duz_ort", "donus_sayisi", "poz_h_25", "poz_h_50", "poz_h_75", "poz_h_son",
           "yon_h_son_der"]


def _meta(m, k):
    v = m.get(k)
    if isinstance(v, str):
        try:
            return ast.literal_eval(v)
        except (ValueError, SyntaxError):
            try:
                return json.loads(v)
            except ValueError:
                return v
    return v


def labirent_grafi(s):
    L = s["labirent"]
    R, C, h = L["satir"], L["sutun"], L["hucre_m"]
    x0, y0, x1, y1 = L["sinir"]
    kod = L["hucreler"]
    if isinstance(kod, str):
        kod = ast.literal_eval(kod)
    acik = np.array([[int(ch, 16) for ch in satir] for satir in kod])
    cozum = L["cozum_yolu"]
    if isinstance(cozum, str):
        cozum = ast.literal_eval(cozum)

    def hucre(x, y):
        c = int(math.floor((x - x0) / h))
        r = int(math.floor((y1 - y) / h))
        return (r, c) if 0 <= r < R and 0 <= c < C else None
    cz = set()
    for p in cozum:
        q = hucre(p[0], p[1])
        if q:
            cz.add(q)
    # çözüm dışı bileşenler (dallar)
    kom = {}
    for r in range(R):
        for c in range(C):
            n = []
            b = acik[r, c]
            if b & 1 and r > 0:
                n.append((r - 1, c))
            if b & 4 and r < R - 1:
                n.append((r + 1, c))
            if b & 2 and c < C - 1:
                n.append((r, c + 1))
            if b & 8 and c > 0:
                n.append((r, c - 1))
            kom[(r, c)] = n
    dal = {}
    k = 0
    for q in kom:
        if q in cz or q in dal:
            continue
        yig = [q]
        dal[q] = k
        while yig:
            a = yig.pop()
            for b in kom[a]:
                if b not in cz and b not in dal:
                    dal[b] = k
                    yig.append(b)
        k += 1
    # çıkmaz kollar: tek açık kenarlı hücreden kavşağa (>= 3 komşu) kadar; START / FINISH hücreleri hariç
    uc = set()
    for k_ in ("start", "finish"):
        hh = L.get(k_, {}).get("hucre")
        if hh:
            uc.add(tuple(hh))
    kollar = []
    for q, nb in kom.items():
        if len(nb) != 1 or q in uc or q in cz:
            continue
        kol = [q]
        onc, a = q, nb[0]
        while len(kom[a]) == 2 and a not in cz:
            kol.append(a)
            b = kom[a][0] if kom[a][0] != onc else kom[a][1]
            onc, a = a, b
        kollar.append(kol)
    merkez = lambda r, c: (x0 + (c + 0.5) * h, y1 - (r + 0.5) * h)
    return {"kollar": kollar, "R": R, "C": C, "h": h, "hucre": hucre, "cozum": cz, "dal": dal, "dal_sayisi": k, "merkez": merkez,
            "cozum_m": L["cozum_uzunlugu_m"]}


def tani(yol, sahne=None):
    from gezinme.duzenek import kayit_oku
    from .sahne import dunyadan_beyne, sahne_yukle
    m, d = kayit_oku(yol)
    ad = sahne or m["sahne"]
    s2 = sahne_yukle(ad)
    with open(_sahne_json(ad), encoding="utf-8") as f:
        sj = json.load(f)
    G = labirent_grafi(sj)
    modlar = _meta(m, "modlar") or []
    T = d["t"]
    n = len(T)
    dt = np.diff(T, append=T[-1] + (T[-1] - T[-2] if n > 1 else 0.05))
    mod = [modlar[i] if 0 <= i < len(modlar) else "" for i in d["mod"]]
    vk, wk = d["komut"][:, 0], d["komut"][:, 1]
    kur = np.array([mm in KURTARMA_MOD for mm in mod])
    duz = ~kur & (np.abs(vk) > 0.02)
    don = ~kur & ~duz & (np.abs(wk) > 0.05)
    bek = ~kur & ~duz & ~don
    gx, gy = d["gercek"][:, 0], d["gercek"][:, 1]
    # hücre ziyaretleri
    hc = [G["hucre"](x, y) for x, y in zip(gx, gy)]
    ziyaret = {}
    onceki = None
    tekrar = np.zeros(n, bool)
    cikmaz = np.zeros(n, bool)
    for i, q in enumerate(hc):
        if q is None:
            continue
        if q != onceki:
            ziyaret[q] = ziyaret.get(q, 0) + 1
            onceki = q
        tekrar[i] = ziyaret[q] >= 2
        cikmaz[i] = q not in G["cozum"]
    # çıkmaz kollara girişte kol haritada biliniyor muydu
    hl = _meta(m, "haritalar") or []
    hts = np.array([h["t"] for h in hl]) if hl else np.zeros(0)
    kol_i = {}
    for k, kol in enumerate(G["kollar"]):
        for q in kol:
            kol_i[q] = k
    girilen = {}
    son = None
    for i, q in enumerate(hc):
        k = kol_i.get(q) if q is not None else None
        if k is not None and k != son and k not in girilen:
            girilen[k] = i
        son = k
    gorulmus = 0
    for k, i in girilen.items():
        j = int(np.searchsorted(hts, T[i]) - 1) if hl else -1
        if j < 0:
            continue
        h = hl[j]
        A = d[h["anahtar"]]
        coz = float(h["cozunurluk_m"])
        ox, oy = h["orijin"]
        bil = 0
        for (r, c) in G["kollar"][k]:
            wx, wy = G["merkez"](r, c)
            bx, by = dunyadan_beyne(s2, wx, wy)
            ii = int((bx - ox) / coz)
            jj = int((by - oy) / coz)
            if 0 <= jj < A.shape[0] and 0 <= ii < A.shape[1] and A[jj, ii] >= 0:
                bil += 1
        if bil == len(G["kollar"][k]):
            gorulmus += 1
    # poz hatası seyri
    bx, by = dunyadan_beyne(s2, gx, gy)
    tx, ty, tth = d["tahmin"][:, 0], d["tahmin"][:, 1], d["tahmin"][:, 2]
    e = np.hypot(bx - tx, by - ty)
    gth = d["gercek"][:, 2] - s2.start_poz[2]
    eth = np.degrees(np.abs((gth - tth + np.pi) % (2 * np.pi) - np.pi))
    ok = np.isfinite(e)

    def q_(f):
        if not ok.any():
            return None
        k = int(f * (n - 1))
        w = e[: k + 1][ok[: k + 1]]
        return round(float(w.max()), 3) if w.size else None
    adim = np.hypot(np.diff(gx), np.diff(gy))
    yol_m = float(adim.sum())
    sonuc = _meta(m, "sonuc") or {}
    # yerinde dönüş başlangıç sayısı
    ds = np.flatnonzero(don[1:] & ~don[:-1]).size
    out = {"sahne": ad, "tohum": _meta(m, "tohum"), "durum": (sonuc.get("hakem") or {}).get("durum") if isinstance(
        sonuc, dict) else None, "sure_s": round(float(T[-1]), 1),
        "kurtarma_s": round(float(dt[kur].sum()), 1), "duz_s": round(float(dt[duz].sum()), 1),
        "donus_s": round(float(dt[don].sum()), 1), "bekle_s": round(float(dt[bek].sum()), 1),
        "tekrar_s": round(float(dt[tekrar].sum()), 1), "cikmaz_s": round(float(dt[cikmaz].sum()), 1),
        "yol_m": round(yol_m, 1), "cozum_m": G["cozum_m"], "yol_orani": round(yol_m / G["cozum_m"], 2),
        "cikmaz_gir": len(girilen), "cikmaz_gorulmus": gorulmus, "dal_sayisi": len(G["kollar"]),
        "hucre_gezilen": len(ziyaret), "hucre_toplam": G["R"] * G["C"],
        "v_duz_ort": round(float(np.abs(d["olculen"][duz, 0]).mean()), 3) if duz.any() else None,
        "donus_sayisi": ds, "poz_h_25": q_(0.25), "poz_h_50": q_(0.5), "poz_h_75": q_(0.75), "poz_h_son": q_(1.0),
        "yon_h_son_der": round(float(eth[ok][-1]), 2) if ok.any() else None}
    return out


def _sahne_json(ad):
    return os.path.join(os.path.dirname(KESIF), "sahneler", ad + ".json")


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("kayitlar", nargs="*")
    p.add_argument("--csv", default=None, help="kayit sütunu olan sonuç csv'si")
    p.add_argument("--surum", default="")
    p.add_argument("--cikti", default=None)
    a = p.parse_args(argv)
    yollar = list(a.kayitlar)
    durumlar = {}
    if a.csv:
        with open(a.csv, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                k = r.get("kayit")
                if k:
                    k = k if os.path.isabs(k) else os.path.join(KESIF, k)
                    yollar.append(k)
                    durumlar[os.path.normcase(os.path.abspath(k))] = r.get("durum")
    satirlar = []
    for y in yollar:
        if not os.path.exists(y):
            continue
        r = tani(y)
        r["surum"] = a.surum
        r["durum"] = durumlar.get(os.path.normcase(os.path.abspath(y)), r["durum"])
        satirlar.append(r)
        print(", ".join("%s=%s" % (k, r.get(k)) for k in ALANLAR), flush=True)
    if a.cikti:
        with open(a.cikti, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=ALANLAR, extrasaction="ignore")
            w.writeheader()
            w.writerows(satirlar)


if __name__ == "__main__":
    from ._yol import dusuk_oncelik
    dusuk_oncelik()
    main()
