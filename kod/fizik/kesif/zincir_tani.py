"""Deneme zinciri tanısı (HAFIZALI sınıf): her denemenin .npz kaydından sınır sırası, FINISH yanındaki sınır, harita
doğruluğu. Yalnız ölçüm; beyin bu bilgileri görmez (FINISH yeri ve gerçek duvarlar YER GERÇEĞİ, tanı için).

    py -3 -m kesif.zincir_tani --csv deneme_sinama4.csv --cikti tani_zincir_sinama4.csv
    py -3 -m kesif.zincir_tani --csv deneme_sinama2.csv --cikti tani_zincir_sinama2.csv

Satır = bir deneme. Alanlar:
- `hedef_dyol_dizi`: denemede seçilen sınır her değiştiğinde (merkez > 1 m oynayınca) planın yol uzunluğu `plan.d_yol`
  (m), seçildiği ilk 2 s'lik ek kaydında; `hedef_maliyet_dizi` aynı anlarda `plan.hedef_maliyet` (ilk 6).
  `hedef_dyol_ilk` dizinin ilki (START'tan ilk hedef). Denemenin ilk 2 s'si atlanır: o ek kaydı önceki denemenin son
  planını taşıyabilir.
- `finish_sinir_*`: merkezi FINISH çizgisine 2,0 m'den yakın sınır (beyin çerçevesinden dünyaya, START pozuyla
  çevrilir; harita kayması bu çevirmeyi bozar, 2 m eşik bunu tolere etmek için). `_ilk_t` ilk görüldüğü an, `_bas_maliyet`
  denemenin 2. saniyeden sonraki ilk ek kaydındaki maliyeti (robot START'ta), `_son_maliyet` son ek kaydındaki maliyeti (robot denemenin
  sonundaki yerinde), `_secildi` denemede seçilen sınır oldu mu.
- `finish_en_yakin_m`: robotun gerçek gövde merkezinin FINISH çizgisine en yakın yaklaşımı.
- `cozum_hucre_orani`: çözüm yolu hücrelerinden zincir boyunca (bu deneme dahil) gerçekten girilenlerin oranı.
- `start_bagli_025`: denemenin son haritasında START ile robotun son tahmini pozu, dolu hücreler 0,25 m şişirilince
  bağlı mı (yaklaşık; planlayıcı 0,36 m açıklık ister, yani 0 ise planlayıcı için de kopuktur).
- `duvar_hata_ort_m`, `dogru_duvar_orani`: denemenin son haritasındaki dolu hücrelerin gerçek duvara uzaklığı
  (`benzet2b.harita_dogrulugu`, eşik 0,10 m).
"""

import argparse
import csv
import json
import math
import os

import numpy as np

from ._yol import KESIF, SAHNELER
from .tani import labirent_grafi
from .tani_dolanma import _uzaklik_dogru

SONUC = os.path.join(KESIF, "sonuc")
T_BAYAT = 2.0                 # s: bu andan önceki ek kayıtları atlanır
ALANLAR = ["kume", "sahne", "tohum", "deneme_no", "durum", "sure_s", "cozum_m", "yol_m", "yol_cozum", "p_en",
           "finish_en_yakin_m", "cozum_hucre_orani", "hedef_sayisi", "hedef_dyol_ilk", "hedef_dyol_ort",
           "hedef_dyol_dizi", "hedef_maliyet_dizi", "finish_sinir_ilk_t", "finish_sinir_bas_maliyet", "finish_sinir_son_maliyet",
           "finish_sinir_secildi", "sinir_sayisi_son", "poz_hata_maks_m", "poz_hata_son_m", "duvar_hata_ort_m",
           "dogru_duvar_orani", "start_bagli_025", "kayit"]
R_BAG = 0.25                  # m: bağlantı denetiminde dolu hücre şişirmesi (planlayıcının sert sınırı 0,36 m, daha katı)


def _oku_npz(yol):
    with np.load(yol, allow_pickle=False) as z:
        d = {k: z[k] for k in z.files if not k.startswith("harita_") and k != "tarama_mm"}
        m = json.loads(str(z["meta"]))
        son = None
        if m.get("haritalar"):
            h = m["haritalar"][-1]
            son = {"izgara": z[h["anahtar"]], "cozunurluk_m": h["cozunurluk_m"], "orijin": h["orijin"]}
    d.pop("meta", None)
    return m, d, son


def start_bagli(harita, son_poz, r_m=R_BAG):
    """Son haritada (eşiklenmiş -1/0/100) START (0, 0) ile denemenin son tahmini pozu, dolu hücreler r_m şişirilince
    boş hücrelerden 4 komşulu yolla bağlı mı. Yaklaşık denetim (planlayıcı değil; o 10 cm kaba ızgara ve 0,36 m ister)."""
    iz = np.asarray(harita["izgara"])
    c = float(harita["cozunurluk_m"])
    x0, y0 = harita["orijin"]
    dolu = iz == 100
    r = int(round(r_m / c))
    D = dolu.copy()
    for di in range(-r, r + 1):
        for dj in range(-r, r + 1):
            if di * di + dj * dj <= r * r:
                D[max(0, di):D.shape[0] + min(0, di), max(0, dj):D.shape[1] + min(0, dj)] |=                     dolu[max(0, -di):dolu.shape[0] + min(0, -di), max(0, -dj):dolu.shape[1] + min(0, -dj)]
    gec = (iz == 0) & ~D

    def h(x, y):
        return int((y - y0) / c), int((x - x0) / c)
    a, b = h(0.0, 0.0), h(son_poz[0], son_poz[1])
    for q in (a, b):
        if not (0 <= q[0] < gec.shape[0] and 0 <= q[1] < gec.shape[1]):
            return None
        gec[q] = True
    ni, nj = gec.shape
    P = nj + 2
    gp = np.zeros((ni + 2, nj + 2), dtype=bool)
    gp[1:-1, 1:-1] = gec
    gf = gp.ravel()
    gor = np.zeros(gf.size, dtype=bool)
    bas, hedef = (a[0] + 1) * P + a[1] + 1, (b[0] + 1) * P + b[1] + 1
    gor[bas] = True
    F = np.array([bas], dtype=np.int64)
    ofs = np.array([P, -P, 1, -1], dtype=np.int64)
    while F.size and not gor[hedef]:
        N = (F[:, None] + ofs[None, :]).ravel()
        N = np.unique(N[gf[N] & ~gor[N]])
        gor[N] = True
        F = N
    return int(bool(gor[hedef]))


def deneme_tani(yol, s2, sj, G, gorulen):
    from .benzet2b import harita_dogrulugu
    from .sahne import beyinden_dunyaya
    m, d, harita = _oku_npz(yol)
    fin = sj["labirent"]["finish"]["cizgi"]
    T = d["t"]
    gx, gy = d["gercek"][:, 0], d["gercek"][:, 1]
    for x, y in zip(gx[::5], gy[::5]):
        q = G["hucre"](float(x), float(y))
        if q is not None:
            gorulen.add(q)
    fin_d = min(_uzaklik_dogru(float(x), float(y), fin[0], fin[1]) for x, y in zip(gx[::5], gy[::5]))
    ekler = m.get("ekler") or []
    secimler, maliyetler, onceki = [], [], None
    f_ilk_t, f_bas, f_son, f_sec = None, None, None, 0
    ilk_ek = True
    for e in ekler:
        if float(e["t"]) < T_BAYAT:
            continue                  # ilk ek kaydı önceki denemenin son planını taşıyabilir (sinirlar "son plan")
        ek = e["ek"]
        S = ek.get("sinirlar") or []
        fmal = []
        for sn in S:
            wx, wy = beyinden_dunyaya(s2, sn[0], sn[1])
            if _uzaklik_dogru(float(wx), float(wy), fin[0], fin[1]) < 2.0:
                fmal.append(float(sn[5]))
        if fmal and f_ilk_t is None:
            f_ilk_t = round(float(e["t"]), 1)
        if ilk_ek and S:
            f_bas = round(min(fmal), 1) if fmal else None
            ilk_ek = False
        f_son = round(min(fmal), 1) if fmal else None
        sec = ek.get("secilen_sinir")
        if sec:
            wx, wy = beyinden_dunyaya(s2, sec[0], sec[1])
            if _uzaklik_dogru(float(wx), float(wy), fin[0], fin[1]) < 2.0:
                f_sec = 1
            if onceki is None or math.hypot(sec[0] - onceki[0], sec[1] - onceki[1]) > 1.0:
                pl = ek.get("plan") or {}
                dy, hm = pl.get("d_yol"), pl.get("hedef_maliyet")
                secimler.append(round(float(dy), 1) if dy is not None else None)
                maliyetler.append(round(float(hm), 1) if hm is not None else None)
            onceki = sec
    sayi_son = len((ekler[-1]["ek"].get("sinirlar") or [])) if ekler else None
    dog = harita_dogrulugu(s2, {"harita": harita}) if harita is not None else {}
    dyol = [v for v in secimler if v is not None]
    bag = None
    if harita is not None and len(d.get("tahmin", [])):
        ok = np.isfinite(d["tahmin"][:, 0])
        if ok.any():
            bag = start_bagli(harita, d["tahmin"][ok][-1])
    return {"start_bagli_025": bag,"finish_en_yakin_m": round(fin_d, 2), "hedef_sayisi": len(secimler),
            "hedef_dyol_ilk": dyol[0] if dyol else None,
            "hedef_dyol_ort": round(float(np.mean(dyol)), 1) if dyol else None,
            "hedef_dyol_dizi": " ".join("%.0f" % v for v in dyol[:12]) + (" ..." if len(dyol) > 12 else ""),
            "hedef_maliyet_dizi": " ".join("%.1f" % v for v in maliyetler[:6] if v is not None),
            "finish_sinir_ilk_t": f_ilk_t, "finish_sinir_bas_maliyet": f_bas, "finish_sinir_son_maliyet": f_son,
            "finish_sinir_secildi": f_sec, "sinir_sayisi_son": sayi_son,
            "duvar_hata_ort_m": dog.get("duvar_hata_ort_m"), "dogru_duvar_orani": dog.get("dogru_duvar_orani")}


def main(argv=None):
    from .sahne import sahne_yukle
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True, help="sonuc/ altındaki deneme_*.csv")
    p.add_argument("--cikti", required=True, help="sonuc/ altındaki çıktı csv adı")
    a = p.parse_args(argv)
    with open(os.path.join(SONUC, a.csv), encoding="utf-8") as f:
        R = list(csv.DictReader(f))
    Z = {}
    for r in R:
        Z.setdefault((r["sahne"], int(r["tohum"])), []).append(r)
    out = []
    for (ad, t), rs in sorted(Z.items()):
        rs.sort(key=lambda r: int(r["deneme_no"]))
        s2 = sahne_yukle(ad)
        with open(os.path.join(SAHNELER, ad + ".json"), encoding="utf-8") as f:
            sj = json.load(f)
        G = labirent_grafi(sj)
        cz = set()
        cy = sj["labirent"]["cozum_yolu"]
        if isinstance(cy, str):
            import ast
            cy = ast.literal_eval(cy)
        for q in cy:
            h = G["hucre"](q[0], q[1])
            if h:
                cz.add(h)
        gorulen = set()
        for r in rs:
            yol = os.path.join(KESIF, r["kayit"].replace("\\", os.sep))
            satir = {k: r.get(k) for k in ("kume", "sahne", "tohum", "deneme_no", "durum", "sure_s", "cozum_m",
                                           "yol_m", "p_en", "poz_hata_maks_m", "poz_hata_son_m")}
            try:
                satir["yol_cozum"] = round(float(r["yol_m"]) / float(r["cozum_m"]), 2)
            except (TypeError, ValueError, ZeroDivisionError):
                satir["yol_cozum"] = None
            satir["kayit"] = r["kayit"]
            if os.path.exists(yol):
                satir.update(deneme_tani(yol, s2, sj, G, gorulen))
                satir["cozum_hucre_orani"] = round(len(gorulen & cz) / len(cz), 3) if cz else None
            out.append(satir)
            print(ad, t, r["deneme_no"], r["durum"], satir.get("hedef_dyol_dizi"), flush=True)
    with open(os.path.join(SONUC, a.cikti), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ALANLAR, extrasaction="ignore")
        w.writeheader()
        for s in out:
            w.writerow(s)
    print(os.path.join("sonuc", a.cikti))


if __name__ == "__main__":
    main()
