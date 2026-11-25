"""MuJoCo'da deneme zinciri: başarısızlıkta robot START'a geri konur, beyin haritasını korur (HAFIZALI sınıf).

    set PY=%LOCALAPPDATA%\\lale-sim-venv\\Scripts\\python.exe
    %PY% -m kesif.kos_deneme --kume gelistirme --tam labirent_13x13_t2,... --tohum 0,1 --cikti deneme_gelistirme.csv
    %PY% -m kesif.kos_deneme --kume sinama2 --tam ... --cikti deneme_sinama2.csv

Bu satırlar "ilk girişte, hiç bilgi olmadan" KPI'sı DEĞİLDİR: 2. ve sonraki denemelerde beyin önceki denemelerin
haritasını bilir. CSV'de `sinif` = "hafizali", `kume`, `deneme_no` sütunları var; her deneme ayrı satır.

Zincir (sahne, tohum başına bir süreç): 1. deneme ön bilgisiz `KesifBeyni(ayar=surum_ayari(surum))`, düzenek tohumu =
tohum (eski 15/20 koşusuyla aynı kurulum). Başarısızsa (`fail_*`) aynı beyin `deneme.yeni_deneme` ile sıfırlanır,
yeni `Duzenek` (tohum + 1000 (k - 1)) robotu START pozuna + yerleştirme hatasına koyar, yeni `Hakem` 900 s sayar.
En çok `--deneme` deneme. Hakem ve puan dosyaları değişmedi; her deneme hakemin gözünde bağımsız bir koşudur.

`--ablasyon`: 2. denemeden itibaren her denemenin başında beynin kopyası iki kez 10 s koşturulur (hizalamalı /
hizalamasız; aynı yerleştirme, aynı tohum) ve START poz hatası ölçülür (sonuc/<cikti>_hizala.csv). Asıl deneme
`--hizala` (varsayılan açık) ile koşar.

"""

import argparse
import copy
import csv
import math
import os
import time

from ._yol import KESIF, durum_yaz, dusuk_oncelik
from .kos import HAM, SONUC

D_ALANLAR = ["sinif", "surum", "kume", "sahne", "tohum", "deneme_no", "deneme_maks", "sure_siniri_s", "durum",
             "sure_s", "toplam_sure_s", "cozuldu", "yol_m", "carpma_sayisi", "carpma_suresi_s", "puan", "p_en",
             "kesfedilen_hucre", "birlesik_hucre", "toplam_hucre", "bilinen_bas_m2", "bilinen_son_m2", "buyume_m2",
             "sikisma_sebebi", "fail_start", "start_kesme", "kurtarma", "hizala", "yer_dx_m", "yer_dy_m",
             "yer_dth_der", "bas_hata_m", "bas_hata_der", "hizala_duzeltme", "poz_hata_maks_m", "poz_hata_son_m",
             "yon_hata_maks_der", "cozum_m", "duvar_s", "rtf", "k_don", "son_mod", "olaylar", "zaman", "kayit"]
H_ALANLAR = ["kume", "sahne", "tohum", "deneme_no", "yer_dx_m", "yer_dy_m", "yer_dth_der", "hizala",
             "hata_05_m", "hata_05_der", "hata_10_m", "hata_10_der", "hata_maks_m"]


def _poz_hatasi(s2, S):
    """Kayıt satırlarından (t, gerçek dünya, ..., tahmin beyin) poz hatası dizileri (beyin çerçevesinde)."""
    import numpy as np
    from .sahne import dunyadan_beyne
    gx, gy = dunyadan_beyne(s2, S[:, 1], S[:, 2])
    gth = S[:, 3] - s2.start_poz[2]
    e = np.hypot(gx - S[:, 7], gy - S[:, 8])
    eth = np.abs((gth - S[:, 9] + np.pi) % (2 * np.pi) - np.pi)
    return e, eth


def _sonda(beyin, ad, tohum, deneme_no, bas, hizala, sure=10.0):
    """Beyin kopyasını sure s koştur (hakem yok), poz hatası zaman dizisi. Yalnız ölçüm (ablasyon)."""
    import numpy as np
    from gezinme.duzenek import Duzenek
    from .deneme import yeni_deneme
    from .sahne import dunyadan_beyne, sahne_yukle
    s2 = sahne_yukle(ad)
    b, z = beyin
    b = copy.deepcopy(b)
    z = copy.deepcopy(z)
    yeni_deneme(b, z, hizala=hizala)
    dz = Duzenek(ad, tohum=tohum + 1000 * (deneme_no - 1), baslangic=bas)
    kay = []

    def olay(d, t):
        x, y, th = d.gercek_poz()
        gx, gy = dunyadan_beyne(s2, x, y)
        p = b.slam.poz
        kay.append((t, float(math.hypot(gx - p[0], gy - p[1])),
                    abs((th - s2.start_poz[2] - p[2] + math.pi) % (2 * math.pi) - math.pi)))
    dz.kos(b, sure, olay=olay)
    K = np.array(kay)

    def an(t):
        i = int(np.searchsorted(K[:, 0], t))
        i = min(i, len(K) - 1)
        return round(float(K[i, 1]), 4), round(math.degrees(float(K[i, 2])), 3)
    h05, h05d = an(0.5)
    h10, h10d = an(sure - 0.1)
    return {"hata_05_m": h05, "hata_05_der": h05d, "hata_10_m": h10, "hata_10_der": h10d,
            "hata_maks_m": round(float(K[:, 1].max()), 4), "hizala": int(bool(hizala))}


def zincir_mujoco(g):
    dusuk_oncelik()
    import numpy as np
    from gezinme.duzenek import Duzenek, Kayit
    from labirent.hakem import Hakem
    from .beyin import KesifBeyni, surum_ayari
    from .deneme import bilinen_alan_m2, dunya_baslangic, yerlestirme_hatasi, yeni_deneme, zincir_hazirla
    from .sahne import sahne_yukle
    ad, tohum = g["sahne"], g["tohum"]
    s2 = sahne_yukle(ad)
    b = KesifBeyni(ayar=surum_ayari(g["surum"]))
    z = zincir_hazirla(b)
    kdiz = os.path.join(HAM, g["kayit_dizin"])
    os.makedirs(kdiz, exist_ok=True)
    satirlar, sondalar = [], []
    birlesik = set()
    toplam = 0.0
    onceki_sayac = dict(b.sayac)
    for k in range(1, g["deneme_maks"] + 1):
        hata = yerlestirme_hatasi(ad, tohum, k, g["yer_std_m"], g["yer_std_der"])
        bas = dunya_baslangic(s2.start_poz, hata) if k > 1 else None
        if k > 1:
            if g.get("ablasyon"):
                for hz in (True, False):
                    r_s = _sonda((b, z), ad, tohum, k, bas, hz)
                    r_s.update({"kume": g["kume"], "sahne": ad, "tohum": tohum, "deneme_no": k,
                                "yer_dx_m": round(hata[0], 4), "yer_dy_m": round(hata[1], 4),
                                "yer_dth_der": round(math.degrees(hata[2]), 3)})
                    sondalar.append(r_s)
            yeni_deneme(b, z, hizala=g["hizala"])
        bilinen_bas = bilinen_alan_m2(b)
        dz = Duzenek(ad, tohum=tohum + 1000 * (k - 1), baslangic=bas)
        kyol = os.path.join(kdiz, "%s_t%d_d%d.npz" % (ad, tohum, k))
        kayit = Kayit(kyol, taramalar=g.get("taramalar", True))
        kayit.meta = {"beyin_surum": g["surum"], "kume": g["kume"], "sinif": "hafizali", "deneme_no": k,
                      "sure_siniri_s": g.get("sure", 900.0), "yerlestirme_hatasi": list(hata), "hizala": bool(g["hizala"])}
        h = Hakem(ad, sure_siniri_s=g.get("sure", 900.0))
        r = dz.kos(b, g.get("sure", 900.0), hakem=h, kayit=kayit)
        hs = dict(r.get("hakem") or {})
        durum = hs.get("durum")
        if not durum and float(r.get("sure_s") or 0) >= g.get("sure", 900.0) - 0.2:
            durum = "fail_sure"
        sure = float(hs.get("sure_s") or r.get("sure_s") or 0.0)
        toplam += sure
        birlesik |= set(h.ziyaret)
        bilinen_son = bilinen_alan_m2(b)
        S = np.array(kayit.satir, dtype=float).reshape(-1, 18)
        satir = {"sinif": "hafizali", "surum": g["surum"], "kume": g["kume"], "sahne": ad, "tohum": tohum,
                 "deneme_no": k, "deneme_maks": g["deneme_maks"],
                 "sure_siniri_s": g.get("sure", 900.0), "durum": durum, "sure_s": round(sure, 2),
                 "toplam_sure_s": round(toplam, 2), "cozuldu": int(durum == "basari"),
                 "yol_m": hs.get("yol_m"), "carpma_sayisi": hs.get("carpma_sayisi"),
                 "carpma_suresi_s": hs.get("carpma_suresi_s"), "puan": hs.get("puan"), "p_en": hs.get("p_en"),
                 "kesfedilen_hucre": hs.get("kesfedilen_hucre"), "birlesik_hucre": len(birlesik),
                 "toplam_hucre": hs.get("toplam_hucre"), "bilinen_bas_m2": round(bilinen_bas, 2),
                 "bilinen_son_m2": round(bilinen_son, 2), "buyume_m2": round(bilinen_son - bilinen_bas, 2),
                 "sikisma_sebebi": hs.get("sikisma_sebebi"), "fail_start": int(durum == "fail_start"),
                 "start_kesme": b.sayac["start_kesme"] - onceki_sayac.get("start_kesme", 0),
                 "kurtarma": b.sayac["kurtarma"] - onceki_sayac.get("kurtarma", 0),
                 "hizala": int(bool(g["hizala"]) and k > 1), "yer_dx_m": round(hata[0], 4),
                 "yer_dy_m": round(hata[1], 4), "yer_dth_der": round(math.degrees(hata[2]), 3),
                 "hizala_duzeltme": "; ".join("%s %s %s" % (d.get("durum"), d.get("kalite"), d.get("duzeltme"))
                                              for d in getattr(b.slam, "hizala_kaydi", []) or []),
                 "cozum_m": hs.get("cozum_uzunlugu_m"), "duvar_s": r.get("duvar_s"), "rtf": r.get("rtf"),
                 "k_don": round(b.slam.k_don, 3), "son_mod": r.get("son_mod"),
                 "olaylar": "; ".join("%s:%s" % (o[0], o[1]) for o in b.olaylar[-8:]),
                 "zaman": time.strftime("%Y-%m-%d %H:%M:%S"), "kayit": os.path.relpath(kyol, KESIF)}
        onceki_sayac = dict(b.sayac)
        if S.shape[0]:
            e, eth = _poz_hatasi(s2, S)
            ok = np.isfinite(e)
            if ok.any():
                i05 = int(np.searchsorted(S[:, 0], 0.5))
                i05 = min(i05, len(e) - 1)
                satir.update({"poz_hata_maks_m": round(float(np.nanmax(e)), 3),
                              "poz_hata_son_m": round(float(e[ok][-1]), 3),
                              "yon_hata_maks_der": round(float(np.degrees(np.nanmax(eth))), 2),
                              "bas_hata_m": round(float(e[i05]), 4),
                              "bas_hata_der": round(float(np.degrees(eth[i05])), 3)})
        try:
            from .ciz import ciz
            ciz(s2, b, kyol[:-4] + ".png", gercek_poz=dz.gercek_poz(),
                baslik="MuJoCo %s t%d deneme %d %s %.0fs" % (ad, tohum, k, durum, sure))
        except Exception:
            pass
        satirlar.append(satir)
        del kayit, dz
        if durum == "basari":
            break
    return {"satirlar": satirlar, "sondalar": sondalar}


def _guvenli(g):
    try:
        return zincir_mujoco(g)
    except Exception as e:
        import traceback
        return {"satirlar": [{"sinif": "hafizali", "sahne": g["sahne"], "tohum": g["tohum"], "durum": "hata",
                              "kume": g["kume"], "olaylar": "%s: %s" % (type(e).__name__,
                                                                         traceback.format_exc()[-600:].replace("\n",
                                                                                                               " | "))}],
                "sondalar": []}


def main(argv=None):
    import multiprocessing as mp
    p = argparse.ArgumentParser()
    p.add_argument("--is", dest="is_sayisi", type=int, default=4)
    p.add_argument("--tam", required=True, help="virgüllü tam sahne adları")
    p.add_argument("--tohum", default="0,1")
    p.add_argument("--surum", default=None)
    p.add_argument("--kume", default="gelistirme")
    p.add_argument("--deneme", type=int, default=4, help="en çok deneme")
    p.add_argument("--hizala", type=int, default=1, help="1: START'ta yeniden hizalama (varsayılan), 0: kapalı")
    p.add_argument("--yer-std-m", type=float, default=0.03, help="yerleştirme hatası std (m); 0 = tam START")
    p.add_argument("--yer-std-der", type=float, default=2.0)
    p.add_argument("--ablasyon", action="store_true", help="her yeni denemede hizalamalı / hizalamasız 10 s sonda")
    p.add_argument("--taramalar", type=int, default=1)
    p.add_argument("--sure", type=float, default=900.0, help="hakem süre sınırı (kural 900 s; başka değer yalnız duman sınaması)")
    p.add_argument("--cift", default=None, help="süzgeç: virgüllü sahne:tohum çiftleri")
    p.add_argument("--cikti", required=True, help="sonuc/ altındaki csv adı")
    p.add_argument("--kayit-dizin", default=None, help="sonuc/ham/ altındaki klasör (varsayılan: cikti adı)")
    a = p.parse_args(argv)
    dusuk_oncelik()
    if a.surum is None:
        from .beyin import VARSAYILAN_SURUM
        a.surum = VARSAYILAN_SURUM
    korunan = {"mujoco.csv", "mujoco_v2.csv", "mujoco_v3.csv", "mujoco_sinama2_v3.csv", "mujoco_sinama2_v2.csv"}
    if a.cikti in korunan or not a.cikti.startswith("deneme"):
        raise SystemExit("çıktı adı deneme* olmalı (mevcut CSV'ler korunur)")
    kd = a.kayit_dizin or os.path.splitext(a.cikti)[0]
    G = [{"sahne": l, "tohum": int(t), "surum": a.surum, "kume": a.kume, "deneme_maks": a.deneme,
          "hizala": bool(a.hizala), "yer_std_m": a.yer_std_m, "yer_std_der": a.yer_std_der,
          "ablasyon": a.ablasyon, "sure": a.sure, "taramalar": bool(a.taramalar), "kayit_dizin": kd}
         for l in a.tam.split(",") for t in a.tohum.split(",")]
    if a.cift:                      # yalnız verilen (sahne, tohum) çiftleri: "labirent_17x17_t2:1,..."
        istek = {(c.split(":")[0], int(c.split(":")[1])) for c in a.cift.split(",")}
        G = [g for g in G if (g["sahne"], g["tohum"]) in istek]
    G.sort(key=lambda g: -int(g["sahne"].split("_")[1].split("x")[0]))
    yol = os.path.join(SONUC, a.cikti)
    yol_h = os.path.join(SONUC, os.path.splitext(a.cikti)[0] + "_hizala.csv")
    durum_yaz("deneme basladi (%s -> %s): %d zincir, %d surec" % (a.surum, a.cikti, len(G), a.is_sayisi))
    t0 = time.time()
    fh = None
    wh = None
    with open(yol, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=D_ALANLAR, extrasaction="ignore")
        w.writeheader()
        if a.ablasyon:
            fh = open(yol_h, "w", newline="", encoding="utf-8")
            wh = csv.DictWriter(fh, fieldnames=H_ALANLAR, extrasaction="ignore")
            wh.writeheader()
        try:
            with mp.get_context("spawn").Pool(max(1, min(4, a.is_sayisi)), maxtasksperchild=1) as hv:
                for k, s in enumerate(hv.imap_unordered(_guvenli, G)):
                    for r in s["satirlar"]:
                        w.writerow(r)
                    f.flush()
                    if wh is not None:
                        for r in s["sondalar"]:
                            wh.writerow(r)
                        fh.flush()
                    son = s["satirlar"][-1]
                    m = "[%d/%d %.0fs] %s t%s -> %d deneme, son %s, toplam %s s" % (
                        k + 1, len(G), time.time() - t0, son.get("sahne"), son.get("tohum"), len(s["satirlar"]),
                        son.get("durum"), son.get("toplam_sure_s"))
                    print(m, flush=True)
                    durum_yaz("deneme " + m)
        finally:
            if fh is not None:
                fh.close()
    durum_yaz("deneme bitti (%s -> %s)" % (a.surum, a.cikti))


if __name__ == "__main__":
    main()
