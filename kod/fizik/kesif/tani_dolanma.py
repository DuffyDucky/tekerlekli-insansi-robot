"""Dolanma tanısı: MuJoCo kaydında (.npz) robotun yeni hücreye girmeden geçirdiği en uzun aralıkta beyin ne yapıyordu.
Yer gerçeği (sahne labirenti) yalnız ölçüm içindir.

    py -3 -m kesif.tani_dolanma sonuc/ham/mujoco_uzatilmis_v2/labirent_17x17_t3_t0.npz [...]

Kayıttaki `ek` (2 s aralık): sınır listesi [merkez_x, merkez_y, boy, bakış_x, bakış_y, maliyet], seçilen sınır,
plan bilgisi, sayaçlar. Sınır merkezi yer gerçeğine çevrilir ve sınıflanır:
- gercek: merkezin düştüğü hücre (ya da 0,5 m çevresi) robotun hiç girmediği bir labirent hücresi
- sahte_ic: merkez, robotun zaten girdiği hücrelerde (harita gürültüsü / kayma / ince duvar arkası)
- dis: labirent sınırının dışında (FINISH / START açıklığı yakınıysa ayrıca işaretlenir)
"""

import ast
import json
import math
import os
import sys
from collections import Counter

import numpy as np

from .tani import _meta, _sahne_json, labirent_grafi


def _uzaklik_dogru(px, py, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy or 1e-9
    u = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - u * dx, py - ay - u * dy)


def dolanma(yol):
    from gezinme.duzenek import kayit_oku
    from .sahne import beyinden_dunyaya, sahne_yukle
    m, d = kayit_oku(yol)
    ad = m["sahne"]
    s2 = sahne_yukle(ad)
    with open(_sahne_json(ad), encoding="utf-8") as f:
        sj = json.load(f)
    G = labirent_grafi(sj)
    L = sj["labirent"]
    x0, y0, x1, y1 = L["sinir"]
    fin = L["finish"]["cizgi"]
    T = d["t"]
    gx, gy = d["gercek"][:, 0], d["gercek"][:, 1]
    hc = [G["hucre"](x, y) for x, y in zip(gx, gy)]
    # yeni hücre girişleri ve ilk giriş anları
    ilk_giris = {}
    for i, q in enumerate(hc):
        if q is not None and q not in ilk_giris:
            ilk_giris[q] = T[i]
    girisler = sorted(ilk_giris.values())
    bosluk = np.diff(girisler + [float(T[-1])])
    k = int(np.argmax(bosluk))
    w0, w1 = girisler[k], girisler[k] + float(bosluk[k])
    # FINISH'e en yakın gerçek yaklaşım
    fin_d = min(_uzaklik_dogru(x, y, fin[0], fin[1]) for x, y in zip(gx[::10], gy[::10]))
    ekler = _meta(m, "ekler") or []
    pencere = [e for e in ekler if w0 <= e["t"] <= w1]

    def ziyaret_edildi_mi(t):
        return {q for q, tt in ilk_giris.items() if tt <= t}

    sinif = Counter()
    sinir_say = []
    hedefler = []
    plan_yok = 0
    for e in pencere:
        ek = e["ek"]
        S = ek.get("sinirlar") or []
        sinir_say.append(len(S))
        if (ek.get("plan") or {}).get("sinir") == 0:
            plan_yok += 1
        gor = ziyaret_edildi_mi(e["t"])
        for sn in S:
            wx, wy = beyinden_dunyaya(s2, sn[0], sn[1])
            wx, wy = float(wx), float(wy)
            if not (x0 - 0.05 <= wx <= x1 + 0.05 and y0 - 0.05 <= wy <= y1 + 0.05):
                c = "dis_finish" if _uzaklik_dogru(wx, wy, fin[0], fin[1]) < 2.0 else "dis"
            else:
                yak = {G["hucre"](wx + dx, wy + dy) for dx in (-0.5, 0, 0.5) for dy in (-0.5, 0, 0.5)}
                yak.discard(None)
                c = "gercek" if any(q not in gor for q in yak) else "sahte_ic"
            sinif[c] += 1
        sec = ek.get("secilen_sinir")
        hedefler.append((e["t"], tuple(sec) if sec else None, (ek.get("plan") or {}).get("d_yol")))
    # hedef değişimleri ve varış
    degisim = 0
    varmadan = 0
    onceki = None
    for t, h, dy in hedefler:
        if h is None:
            continue
        if onceki is not None and math.hypot(h[0] - onceki[1][0], h[1] - onceki[1][1]) > 1.0:
            degisim += 1
            # önceki hedefe varılmış mıydı: değişim anında robot (tahmin) önceki hedefe 1,5 m'den uzaksa varmadan
            i = int(np.searchsorted(T, t))
            i = min(i, len(T) - 1)
            p = d["tahmin"][i]
            if math.hypot(p[0] - onceki[1][0], p[1] - onceki[1][1]) > 1.5:
                varmadan += 1
        onceki = (t, h)
    dyol = [h[2] for h in hedefler if h[2] is not None]
    # pencerede yürünen yol ve mod dağılımı
    ii = (T >= w0) & (T <= w1)
    adim = np.hypot(np.diff(gx[ii]), np.diff(gy[ii]))
    modlar = _meta(m, "modlar") or []
    md = Counter(modlar[j] if 0 <= j < len(modlar) else "" for j in d["mod"][ii])
    hak = _meta(m, "hakem") or {}
    son = ekler[-1]["ek"]["sayac"] if ekler else {}
    return {"kayit": os.path.basename(yol), "sahne": ad, "durum": (hak or {}).get("durum") if isinstance(hak, dict) else None,
            "sure": round(float(T[-1]), 1), "pencere": (round(w0, 1), round(w1, 1)), "pencere_s": round(w1 - w0, 1),
            "pencere_yol_m": round(float(adim.sum()), 1), "gezilen_hucre": len(ilk_giris),
            "toplam_hucre": G["R"] * G["C"], "finish_en_yakin_m": round(fin_d, 2),
            "sinir_sayisi_ort": round(float(np.mean(sinir_say)), 1) if sinir_say else None,
            "sinir_sayisi_min_maks": (min(sinir_say), max(sinir_say)) if sinir_say else None,
            "sinir_sinif": dict(sinif), "hedef_degisim": degisim, "varmadan_birakilan": varmadan,
            "ek_sayisi": len(pencere), "plan_sinirsiz": plan_yok,
            "hedef_d_yol_ort": round(float(np.mean(dyol)), 1) if dyol else None,
            "hedef_d_yol_maks": round(float(np.max(dyol)), 1) if dyol else None,
            "mod": {k: round(v * 0.05, 1) for k, v in md.most_common()}, "sayac_son": son}


if __name__ == "__main__":
    from ._yol import dusuk_oncelik
    dusuk_oncelik()
    for y in sys.argv[1:]:
        print(json.dumps(dolanma(y), ensure_ascii=False, default=str))
