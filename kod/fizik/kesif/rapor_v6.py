"""v6 (tüm gövde süpürme öngörüsü) bölümü: SONUC.md'ye eklenir (`kesif.kos rapor`); tek başına: py -3 -m kesif.rapor_v6.

    py -3 -m kesif.rapor_v6 --birlestir     # ham/mujoco_v6_<parça>.csv -> sonuc/mujoco_v6.csv, mujoco_sinama{2,4,5}_v6.csv

Kaynaklar (hepsi sonuc/ altında; sayılar CSV'den, elle düzeltme yok):
- tani_temas_v6.csv: temas tanısı (kesif.temas_tani, kayıttan)
- v6_2b.csv: 2B v5 / v6 (21 geliştirme labirenti, tohum 0)
- mujoco_v3.csv / mujoco_v5.csv / mujoco_v6.csv: MuJoCo geliştirme
- mujoco_sinama2_v3/_v5/_v6.csv, mujoco_sinama4_v3/_v5/_v6.csv: görülmüş kümeler (gerileme denetimi)
- mujoco_sinama5_v3.csv / mujoco_sinama5_v6.csv: YENİ sınama5 (13x13 / 17x17 t24..t28 x tohum {0, 1}); v6 dondurulduktan
  sonra koşuldu
- v3 taban: mujoco_*v3*.csv (ilk giriş) ve deneme_*.csv (hafızalı zincir, v3)
- Tur 2 (eksik ölçümler, v6 kodu değişmeden): mujoco_sinama3_v6.csv (v3'ün temas yaptığı sınama3), mujoco_uzatilmis_v6.csv
  (KURAL DIŞI 1800 s, v3'ünkiyle aynı koşullar), v6_2b_t1.csv (2B tohum 1, v5 + v6), deneme_sinama4_v6.csv (zincir, v6)
"""

import csv
import glob
import os
import statistics as st
import sys

from .rapor_hiz4 import SONUC, _anahtar, _csv, _f, _hiz, _s

PARCALAR = {"mujoco_v6.csv": ["gel_t1", "gel_a1", "gel_a2", "gel_b", "gel_b2"],
            "mujoco_sinama2_v6.csv": ["s2_17", "s2_13"],
            "mujoco_sinama4_v6.csv": ["s4_17", "s4_13"],
            "mujoco_sinama5_v6.csv": ["s5_17", "s5_13"]}
PLAN = {"mujoco_v6.csv": 37, "mujoco_sinama2_v6.csv": 20, "mujoco_sinama4_v6.csv": 20, "mujoco_sinama5_v6.csv": 20,
        "mujoco_sinama3_v6.csv": 20, "mujoco_uzatilmis_v6.csv": 9}
ILK_KARAR = ("mujoco_v6.csv", "mujoco_sinama2_v6.csv", "mujoco_sinama4_v6.csv", "mujoco_sinama5_v6.csv")   # ilk karar (a)+(b)
KUME_ADI = {"mujoco_v6.csv": "geliştirme", "mujoco_sinama2_v6.csv": "sınama2", "mujoco_sinama3_v6.csv": "sınama3",
            "mujoco_sinama4_v6.csv": "sınama4", "mujoco_sinama5_v6.csv": "sınama5",
            "mujoco_uzatilmis_v6.csv": "uzatılmış (1800 s)"}
IKIB = ("v6_2b.csv", "v6_2b_t1.csv")        # 2B tohum 0 (ilk tur) ve tohum 1 (tur 2)


def birlestir():
    for hedef, parcalar in PARCALAR.items():
        R, alan = [], None
        for p in parcalar:
            yol = os.path.join(SONUC, "ham", "mujoco_v6_%s.csv" % p)
            if not os.path.exists(yol):
                continue
            with open(yol, encoding="utf-8") as f:
                r = csv.DictReader(f)
                alan = alan or r.fieldnames
                R += [x for x in r if x.get("durum") != "hata"]
        if not R:
            continue
        with open(os.path.join(SONUC, hedef), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=alan)
            w.writeheader()
            w.writerows(R)
        print(hedef, len(R))


def _c(r):
    return int(_f(r.get("carpma_sayisi")) or 0)


def _ozet(R, H, sur):
    ok = [r for r in R if r.get("durum") == "basari"]
    h = [H.get((sur, r["sahne"], str(r["tohum"]), r.get("kume"))) for r in R]
    h = [x for x in h if x and x.get("duz_s")]
    hd = sum(_f(x["duz_s"]) for x in h)
    pay = [_f(x["duvar_pay_min_m"]) for x in h if x.get("duvar_pay_min_m") not in (None, "")]
    return {"n": len(R), "basari": len(ok), "sure": st.median([_f(r["sure_s"]) for r in ok]) if ok else None,
            "carpma": sum(_c(r) for r in R), "carpmali": sum(_c(r) > 0 for r in R),
            "temas": sum(_f(r.get("carpma_suresi_s")) or 0.0 for r in R),
            "kurtarma": sum(int(_f(r.get("kurtarma")) or 0) for r in R),
            "v_duz": (sum(_f(x["v_duz_ort"]) * _f(x["duz_s"]) for x in h) / hd) if hd > 0 else None,
            "pay_min": min(pay) if pay else None, "pay5": ("%d/%d" % (sum(p < 0.005 for p in pay), len(pay))) if pay else "-"}


def _oran(Ra, Rb):
    a = {_anahtar(r): r for r in Ra if r.get("durum") == "basari"}
    o = [_f(r["sure_s"]) / _f(a[_anahtar(r)]["sure_s"]) for r in Rb if r.get("durum") == "basari" and _anahtar(r) in a]
    return (st.median(o), len(o)) if o else (None, 0)


def kumeler():
    """v6'nın koşulduğu sahne + tohumlarla eşlenmiş v3 / v5 satırları (karşılaştırma aynı koşularda)."""
    out = []
    for ad, d3, d5, d6 in (("geliştirme", "mujoco_v3.csv", "mujoco_v5.csv", "mujoco_v6.csv"),
                           ("sınama2 (görülmüş)", "mujoco_sinama2_v3.csv", "mujoco_sinama2_v5.csv", "mujoco_sinama2_v6.csv"),
                           ("sınama4 (görülmüş)", "mujoco_sinama4_v3.csv", "mujoco_sinama4_v5.csv", "mujoco_sinama4_v6.csv"),
                           ("**sınama5** (YENİ)", "mujoco_sinama5_v3.csv", None, "mujoco_sinama5_v6.csv"),
                           ("sınama3 (tur 2; v3'ün temas yaptığı küme)", "mujoco_sinama3_v3.csv", None,
                            "mujoco_sinama3_v6.csv"),
                           ("uzatılmış (tur 2; KURAL DIŞI 1800 s, tohum 0)", "mujoco_uzatilmis_v3.csv", None,
                            "mujoco_uzatilmis_v6.csv")):
        R6 = _csv(d6)
        an = {_anahtar(r) for r in R6}
        R3 = _csv(d3)
        D = {"v3": [r for r in R3 if _anahtar(r) in an] if R6 else R3,
             "v5": [r for r in _csv(d5) if _anahtar(r) in an] if d5 else [], "v6": R6}
        out.append((ad, D, d6, len(R3)))
    return out


def v3_taban():
    """v3'ün bütün MuJoCo kümelerindeki temas olayları (ilk giriş ve hafızalı zincir ayrı)."""
    ilk = {}
    for yol in sorted(glob.glob(os.path.join(SONUC, "mujoco*_v3.csv"))):
        R = _csv(os.path.basename(yol))
        ilk[os.path.basename(yol)] = (len(R), sum(_c(r) for r in R), sum(_f(r.get("carpma_suresi_s")) or 0.0 for r in R))
    zin = {}
    for yol in sorted(glob.glob(os.path.join(SONUC, "deneme_*.csv"))):
        b = os.path.basename(yol)
        if "hizala" in b:
            continue
        R = [r for r in _csv(b) if (r.get("surum") or "v3") == "v3"]
        if not R:          # ör. deneme_sinama4_v6.csv: v3 satırı yok
            continue
        zin[b] =(len(R), sum(_c(r) for r in R), sum(_f(r.get("carpma_suresi_s")) or 0.0 for r in R))
    return ilk, zin


def tani_tablosu():
    R = _csv("tani_temas_v6.csv")
    if not R:
        return []
    md = ["| kayıt | sürüm | t (s) | temas (s) | gövde noktası | duvar | kipler (3 s) | v / w komut | son yerinde dönüş (s önce) "
          "| son 3 s taramada görüldü | LiDAR açısı (kör?) | haritada dolu | öngörü çarpar (son tarama / harita / birikmiş; an) "
          "| poz hatası (m) |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in R:
        md.append("| %s | %s | %s | %s | %s | %s | %s | %s / %s | %s | %s/%s | %s (%s) | %s | %s / %s / %s; %s | %s |" % (
            r["kayit"].split("/")[-2] + "/" + r["kayit"].split("/")[-1].replace(".npz", ""), r["surum"], r["t_temas"],
            r["temas_s"], r["govde_nokta"], r["duvar_turu"], r["kipler_3s"], r["v_komut"], r["w_komut"], r["son_yerinde_s"],
            r["gorulen_tarama_3s"], r["tarama_3s"], r["lidar_aci_der"], "kör" if r["kor_sektor"] == "1" else "açık",
            "evet" if r["harita_dolu"] == "1" else "hayır", r["ongoru_son_tarama"], r["ongoru_harita"],
            r["ongoru_birikmis"], r["ongoru_an"], r["poz_hata_m"]))
    return md


def ikib_tablosu():
    R = [r for ad in IKIB for r in _csv(ad)]
    if not R:
        return []
    S = {s: [r for r in R if r.get("ayar") == s and r.get("durum") != "hata"] for s in ("v5", "v6")}
    an = {_anahtar(r) for r in S["v5"]} & {_anahtar(r) for r in S["v6"]}
    md = ["| sürüm | tohum | koşu | başarı | çarpma olayı (koşu) | temas (s) | süre ortanca (başarılı, s) | kurtarma |",
          "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for s in ("v5", "v6"):
        for tohum in ("0", "1", "0+1"):
            X = [r for r in S[s] if _anahtar(r) in an and (tohum == "0+1" or str(r["tohum"]) == tohum)]
            if not X or (tohum == "0+1" and len({str(r["tohum"]) for r in X}) < 2):
                continue
            ok = [r for r in X if r.get("durum") == "basari"]
            md.append("| %s | %s | %d | %d/%d | %d (%d) | %.2f | %s | %d |" % (
                s, tohum, len(X), len(ok), len(X), sum(_c(r) for r in X), sum(_c(r) > 0 for r in X),
                sum(_f(r.get("carpma_suresi_s")) or 0.0 for r in X),
                _s(st.median([_f(r["sure_s"]) for r in ok]) if ok else None), sum(int(_f(r.get("kurtarma")) or 0) for r in X)))
    o = _oran([r for r in S["v5"] if _anahtar(r) in an], [r for r in S["v6"] if _anahtar(r) in an])
    t1 = [r for r in R if str(r["tohum"]) == "1"]
    md += ["", "v6/v5 süre oranı (ikisi de başarılı): ortanca %s (%d çift). Koşulan: v5 %d, v6 %d (plan 42 + 42: 21 "
           "geliştirme labirenti x tohum {0, 1}). Tohum 0 ilk turda (`sonuc/v6_2b.csv`), tohum 1 tur 2'de (`sonuc/v6_2b_t1.csv`, "
           "aynı v6_kod kopyası)%s." % (_s(o[0], "%.3f"), o[1], len(S["v5"]), len(S["v6"]),
                                        "" if t1 else "; tohum 1 henüz koşulmadı"),
           "", "Başarısız ya da çarpmalı 2B koşuları:", "",
           "| sürüm | sahne | tohum | durum | sıkışma nedeni | süre (s) | p_en | çarpma | son olaylar |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in sorted(R, key=lambda r: (r.get("ayar"), r["sahne"], str(r["tohum"]))):
        if r.get("durum") != "basari" or _c(r) > 0:
            md.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                r.get("ayar"), r["sahne"], r["tohum"], r.get("durum"), r.get("sikisma_sebebi") or "-", r.get("sure_s"),
                r.get("p_en"), r.get("carpma_sayisi"), (r.get("olaylar") or "").replace("|", "/")[:140]))
    if any(r.get("ayar") == "v6" and r.get("durum") == "fail_sikisma" for r in R):
        md += ["", "v6 `fail_sikisma` (17x17_t5 t0, 717,75 s, temas 0): belirlenimci 2B yeniden koşusu aynı sonucu verdi "
               "(`sonuc/ham/tur2_2b_tani_17t5.txt`, git dışı). 658 s'den sonra robot yerinde dönüşte kaldı: her ~1 s'lik "
               "yeniden planda yolun ilk bacağı değişiyor (hedef aynı), dönüş yönü ±0,8 rad/s arasında her ~1 s tersine "
               "dönüyor (her plandan sonra), yön 2,45–2,88 rad arasında salınıyor; hakem 60 s hareketsizlikten sonra bitirdi. Bu aralıkta "
               "süpürme reddi / geri çekilme sayacı artmadı; v6'nın süpürme öngörüsüne özgü olduğu gösterilmedi. "
               "Düzeltilmedi (algoritma bu turda değişmedi). MuJoCo v6 koşularında `fail_sikisma` yok."]
    return md


def karar(K):
    """İlk karar (2026-11-26 02:44): (a) sınama5 başarısı, (b) geliştirme + sınama2 + sınama4 + sınama5'te temas sıfır."""
    K = [x for x in K if x[2] in ILK_KARAR]
    s5 = [D for ad, D, d6, n3 in K if d6 == "mujoco_sinama5_v6.csv"][0]
    b3 = sum(r.get("durum") == "basari" for r in s5["v3"])
    b6 = sum(r.get("durum") == "basari" for r in s5["v6"])
    tam = all(len(D["v6"]) == PLAN[d6] for ad, D, d6, n3 in K)
    t6 = sum(_c(r) for ad, D, d6, n3 in K for r in D["v6"])
    a = len(s5["v6"]) == PLAN["mujoco_sinama5_v6.csv"] and len(s5["v3"]) == len(s5["v6"]) and b6 >= b3
    b = tam and t6 == 0
    return b3, b6, t6, tam, a, b


def karar2(K):
    """Tur 2 kuralı (esnetilmeden): v6'nın İLK GİRİŞ koşularının tamamında (ilk karardaki 97 koşu + sınama3 20 +
    uzatılmış 9) temas olayı sıfır VE sınama3'te v6 başarısı v3'ten az değil -> v6 kalır; değilse v3."""
    kap = [(KUME_ADI[d6], len(D["v6"]), PLAN[d6], sum(_c(r) for r in D["v6"])) for ad, D, d6, n3 in K]
    s3 = [D for ad, D, d6, n3 in K if d6 == "mujoco_sinama3_v6.csv"][0]
    b3 = sum(r.get("durum") == "basari" for r in s3["v3"])
    b6 = sum(r.get("durum") == "basari" for r in s3["v6"])
    tam = all(n == p for _, n, p, _ in kap) and len(s3["v3"]) == len(s3["v6"])
    t6 = sum(c for _, _, _, c in kap)
    return kap, b3, b6, t6, tam, tam and t6 == 0 and b6 >= b3


ZINCIR = {"v3": "deneme_sinama4.csv", "v6": "deneme_sinama4_v6.csv"}


def _zincir_ozet(R):
    from .rapor_deneme import _zincirler
    Z = _zincirler(R)
    dag = {1: 0, 2: 0, 3: 0, 4: 0}
    tops = []
    for rs in Z.values():
        if rs[-1].get("durum") == "basari":
            dag[int(rs[-1]["deneme_no"])] += 1
            tops.append(_f(rs[-1].get("toplam_sure_s")) or 0.0)
    cik = [r for r in R if int(_f(r.get("fail_start")) or 0)]
    return {"Z": Z, "n": len(Z), "coz": sum(dag.values()), "dag": dag, "tops": tops,
            "toplam": sum(_f(r.get("sure_s")) or 0.0 for r in R), "deneme": len(R),
            "temas": sum(_c(r) for r in R), "temas_s": sum(_f(r.get("carpma_suresi_s")) or 0.0 for r in R),
            "fail_start": len(cik), "kesme": int(sum(_f(r.get("start_kesme")) or 0 for r in R)),
            "hata": sum(r.get("durum") == "hata" for r in R)}


def zincir_bolumu():
    """Deneme zinciri v6 / v3, sınama4 (HAFIZALI sınıf; ilk giriş KPI'sı değil)."""
    from .rapor_deneme import TANI, _cozum_m, _oku, _tempo, guvenlik_tablo, neden, zincir_tablo
    R = {s: _oku(a) for s, a in ZINCIR.items()}
    if not R["v6"]:
        return ["### Deneme zinciri v6 / v3 (sınama4)", "", "v6 zinciri koşulmadı (`sonuc/deneme_sinama4_v6.csv` yok).", ""]
    O = {s: _zincir_ozet(R[s]) for s in R}
    md = ["### Deneme zinciri v6 / v3 (sınama4; HAFIZALI sınıf, ilk giriş KPI'sı değil)", "",
          "v3 zinciri `sonuc/deneme_sinama4.csv` (zincir4_kod kopyası). v6 zinciri `sonuc/deneme_sinama4_v6.csv`: tur 2'de "
          "`sonuc/ham/zincir4_v6_kod/` kopyasından (canlı kesif: beyin / surus4 v6_kod ile aynı, `deneme.py` denemeler arası "
          "v6 geçmiş taramalarını sıfırlar), `--surum v6`, en çok 4 deneme, 2 tohum, hizalama sondası yok. Zincir mantığı ve "
          "beyin kodu değişmedi.", "",
          "| zincir beyni | zincir | 1. denemede | 2. | 3. | 4. | 4 denemede çözülmedi | deneme | toplam süre, bütün denemeler "
          "(s) | toplam süre ortanca (çözülen, s) | temas olayı | temas (s) | fail_start (START'tan çıkma) | START kesme | hata |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for s in ("v3", "v6"):
        o = O[s]
        if not o["n"]:
            continue
        md.append("| %s | %d | %d | %d | %d | %d | %d | %d | %.0f | %s | %d | %.2f | %d | %d | %d |" % (
            s, o["n"], o["dag"][1], o["dag"][2], o["dag"][3], o["dag"][4], o["n"] - o["coz"], o["deneme"], o["toplam"],
            _s(st.median(o["tops"]) if o["tops"] else None), o["temas"], o["temas_s"], o["fail_start"], o["kesme"],
            o["hata"]))
    # 1. deneme = v6 ilk giriş koşusu (aynı kurulum, aynı tohum)
    ilk = {_anahtar(r): r for r in _csv("mujoco_sinama4_v6.csv")}
    d1 = [r for r in R["v6"] if str(r.get("deneme_no")) == "1"]
    ayni = [r for r in d1 if _anahtar(r) in ilk and ilk[_anahtar(r)].get("durum") == r.get("durum")
            and abs((_f(ilk[_anahtar(r)].get("sure_s")) or 0) - (_f(r.get("sure_s")) or 0)) < 1.0]
    fark = ["%s t%s: ilk giriş %s %s, zincir 1. deneme %s %s" % (r["sahne"], r["tohum"], ilk[_anahtar(r)].get("durum"),
                                                               ilk[_anahtar(r)].get("sure_s"), r.get("durum"), r.get("sure_s"))
            for r in d1 if _anahtar(r) in ilk and r not in ayni]
    md += ["", "1. deneme = v6 ilk giriş koşusu (`mujoco_sinama4_v6.csv`, aynı kurulum ve tohum): %d/%d aynı sonuç ve süre "
           "(±1 s)%s." % (len(ayni), len(d1), ("; farklı: " + "; ".join(fark)) if fark else "")]
    # temaslar ve çözülmeyenler
    tem = [r for s in ("v3", "v6") for r in R[s] if _c(r) > 0]
    if tem:
        md += ["", "Temaslı denemeler:", "", "| beyin | sahne | tohum | deneme | temas olayı | temas (s) | durum | son olaylar |",
               "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for r in tem:
            md.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                r.get("surum") or "v3", r["sahne"], r["tohum"], r["deneme_no"], r.get("carpma_sayisi"),
                r.get("carpma_suresi_s"), r.get("durum"), (r.get("olaylar") or "").replace("|", "/")[:120]))
    tani = {"v3": _oku(TANI["sinama4"]), "v6": _oku("tani_zincir_sinama4_v6.csv")}
    tempo = _tempo()
    md += ["", "Çözülmeyen zincirler (neden: `rapor_deneme.neden` kuralı, `kesif.zincir_tani` çıktısından; tanı yoksa "
           "yalnız CSV):", "", "| beyin | sahne | tohum | deneme: durum / sıkışma / süre (s) / p_en | poz hatası maks (m) | "
           "neden |", "| --- | --- | --- | --- | --- | --- |"]
    for s in ("v3", "v6"):
        from .rapor_deneme import _zincirler
        Tz = _zincirler(tani[s]) if tani[s] else {}
        for (ad, t), rs in sorted(O[s]["Z"].items()):
            if rs[-1].get("durum") == "basari":
                continue
            nd = neden(Tz[(ad, t)], _cozum_m(ad) or 0.0, tempo) if (ad, t) in Tz else "tanı koşulmadı"
            md.append("| %s | %s | %d | %s | %s | %s |" % (
                s, ad, t, "; ".join("%s %s / %s / %.0f / %s" % (r["deneme_no"], r.get("durum"), r.get("sikisma_sebebi") or "-",
                                                             _f(r.get("sure_s")) or 0, r.get("p_en")) for r in rs),
                " / ".join(r.get("poz_hata_maks_m") or "-" for r in rs), nd))
    md += ["", "Deneme başına (v3 / v6):", ""] + guvenlik_tablo([("sinama4 v3", R["v3"]), ("sinama4 v6", R["v6"])])
    md += ["", "Zincirler (v6):", ""] + zincir_tablo(R["v6"])
    # zincir kuralı
    from . import kos_deneme
    from .beyin import VARSAYILAN_SURUM
    zv = getattr(kos_deneme, "ZINCIR_VARSAYILAN_SURUM", None) or VARSAYILAN_SURUM
    tam = O["v6"]["n"] == O["v3"]["n"] == 20 and not O["v6"]["hata"]
    kotu = O["v6"]["coz"] < O["v3"]["coz"] or O["v6"]["temas"] > O["v3"]["temas"]
    md += ["", "**Zincir kuralı** (v6 zinciri v3 zincirinden az zincir çözüyorsa ya da daha çok temas yapıyorsa "
           "`kos_deneme` varsayılan beyni açıkça v3): çözülen v3 %d / v6 %d; temas olayı v3 %d / v6 %d; v6 tam koşuldu %s "
           "-> %s. `kos_deneme --surum` verilmezse kullanılan beyin: `%s`." % (
               O["v3"]["coz"], O["v6"]["coz"], O["v3"]["temas"], O["v6"]["temas"], "evet" if tam else "HAYIR",
               ("v6 zinciri daha kötü: varsayılan v3 olmalı" if kotu else "v6 zinciri daha kötü değil: varsayılan olduğu "
                "gibi kalır") if tam else "eksik koşu: hüküm yok", zv), ""]
    return md


def v6_bolumu():
    K = kumeler()
    if not any(D["v6"] for ad, D, d6, n3 in K) and not _csv("tani_temas_v6.csv"):
        return []
    H = _hiz()
    md = ["## v6: tüm gövde süpürme öngörüsü (geçmiş taramalar + harita, açıklıklı aday kabulü)", "",
          "### Temas tanısı (`kesif.temas_tani`, kayıttan; `sonuc/tani_temas_v6.csv`)", "",
          "İlk dört satır bu aşamanın hedefi (v5 geliştirme ve v3'ün üç teması); v4 satırları başvuru. Öngörü sütunu: "
          "temastan önceki 2 s'de, 0,1 s'de bir, komut v / w ile surus4 yayı (3 cm pay) hangi kaynakla çarpma öngördü.", ""]
    md += tani_tablosu()
    md += ["", "### 2B v5 / v6 (21 geliştirme labirenti x tohum {0, 1}; `sonuc/v6_2b.csv`, `sonuc/v6_2b_t1.csv`)", ""]
    md += ikib_tablosu()
    md += ["", "### MuJoCo (900 s, ön bilgisiz)", "",
           "v6 kodu dondurulduktan sonra (`sonuc/ham/v6_kod/`) koşuldu; ayar yapılmadı. v3 / v5 satırları v6'nın koşulduğu "
           "sahne + tohumlarla eşlenir. Sınama2 ve sınama4 görülmüş kümelerdir (gerileme denetimi). Sınama5 bu aşamada "
           "üretildi; v3 sınama5 koşuları v6 öncesi kod kopyasından (`sonuc/ham/v6_oncesi_kod/`). Tur 2 (aynı v6_kod "
           "kopyası, kod değişmeden): sınama3 ve uzatılmış küme. Sınama3 v6 için tam taze değil: v6'nın temas tanısında "
           "v3'ün sınama3 kaydı (13x13_t15 t0) kullanıldı ve küme v3 / v4 kararında görülmüştü (v4 orada 17/20). Uzatılmış "
           "küme KURAL DIŞI (hakem 1800 s, tohum 0; v3'ünkiyle aynı 9 koşu ve koşullar). Düz hız ve duvar payı tur 2 için "
           "`sonuc/hiz_tani_sinama3_uzatilmis_v6.csv`'den (v3 uzatılmış için hız tanısı yok).", "",
           "| küme | sürüm | koşu (plan) | başarı | çarpma olayı (koşu) | temas (s) | süre ortanca (başarılı, s) | süre oranı "
           "/ v3 (ortanca; çift) | düz hız ort (m/s) | en küçük duvar payı (m) | payı < 5 mm koşu | kurtarma |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for ad, D, d6, n3 in K:
        for sur in ("v3", "v5", "v6"):
            R = D.get(sur)
            if not R:
                continue
            z = _ozet(R, H, sur)
            o = _oran(D["v3"], R) if sur != "v3" else (None, 0)
            plan = PLAN[d6] if sur == "v6" else len(R)
            md.append("| %s | %s | %d (%d) | %d/%d | %d (%d) | %.2f | %s | %s | %s | %s | %s | %d |" % (
                ad, sur, z["n"], plan, z["basari"], z["n"], z["carpma"], z["carpmali"], z["temas"], _s(z["sure"]),
                ("%.3f; %d" % o) if o[0] is not None else "", _s(z["v_duz"], "%.3f"), _s(z["pay_min"], "%.3f"),
                z["pay5"], z["kurtarma"]))
    b3, b6, t6, tam, a, b = karar(K)
    md += ["", "**Varsayılan kuralı, ilk karar** (2026-11-26 02:44) (a) sınama5'te v6 başarısı v3'ten az değil: v3 %d, v6 %d "
           "-> %s; (b) o anda koşulan dört MuJoCo kümesinde (geliştirme 37 + sınama2 20 + sınama4 20 + sınama5 20; sınama3 "
           "ve uzatılmış o zaman koşulmamıştı) v6 temas olayı sıfır ve kümeler tam koşuldu: temas %d, tam koşuldu %s -> %s. "
           "Sonuç: %s" % (
               b3, b6, "sağlandı" if a else "SAĞLANMADI", t6, "evet" if tam else "HAYIR", "sağlandı" if b else "SAĞLANMADI",
               "`VARSAYILAN_SURUM = \"v6\"`." if (a and b) else "`VARSAYILAN_SURUM` v3 KALIR. v6 seçmeli: "
               "`surum_ayari(\"v6\")`.")]
    from .beyin import VARSAYILAN_SURUM
    kap, c3, c6, u6, tam2, ok2 = karar2(K)
    md += ["", "**Varsayılan kuralı, tur 2** (esnetilmeden): v6'nın ilk giriş koşularının tamamında temas olayı sıfır VE "
           "sınama3'te v6 başarısı v3'ten az değil -> v6 kalır; tek temas ya da daha düşük başarı -> v3. Kapsam: %s. Temas "
           "olayı toplam %d (%d koşu); sınama3 başarı v3 %d / v6 %d; tam koşuldu %s -> %s. Koddaki değer: "
           "`VARSAYILAN_SURUM = \"%s\"`%s." % (
               " + ".join("%s %d/%d koşu, temas %d" % x for x in kap), u6, sum(x[1] for x in kap), c3, c6,
               "evet" if tam2 else "HAYIR (hüküm yok)",
               "sağlandı, `VARSAYILAN_SURUM` v6 kalır" if ok2 else ("SAĞLANMADI, `VARSAYILAN_SURUM` v3'e döner"
                                                                   if tam2 else "eksik koşu"),
               VARSAYILAN_SURUM, "" if (not tam2 or (VARSAYILAN_SURUM == ("v6" if ok2 else "v3"))) else
               " (UYUMSUZ: kural sonucu ile koddaki değer farklı)")]
    md += [""] + zincir_bolumu()
    ilk, zin = v3_taban()
    n_i = sum(v[0] for v in ilk.values())
    c_i = sum(v[1] for v in ilk.values())
    s_i = sum(v[2] for v in ilk.values())
    n_z = sum(v[0] for v in zin.values())
    c_z = sum(v[1] for v in zin.values())
    s_z = sum(v[2] for v in zin.values())
    md += ["", "**v3 tabanı (dürüst):** ilk giriş MuJoCo koşularında %d koşuda %d temas olayı, %.2f s; hafızalı zincir "
           "denemelerinde %d denemede %d olay, %.2f s. Toplam %d olay, %.2f s. v3 de sıfır değil." % (
               n_i, c_i, s_i, n_z, c_z, s_z, c_i + c_z, s_i + s_z), "",
           "| dosya | koşu / deneme | temas olayı | temas (s) |", "| --- | --- | --- | --- |"]
    for k, v in list(ilk.items()) + list(zin.items()):
        md.append("| %s | %d | %d | %.2f |" % (k, v[0], v[1], v[2]))
    md += ["", "Çarpmalı ya da başarısız v6 koşuları:", "",
           "| küme | sahne | tohum | durum | süre | p_en | çarpma | temas (s) | kurtarma | son olaylar |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for ad, D, d6, n3 in K:
        for r in sorted(D["v6"], key=_anahtar):
            if r.get("durum") != "basari" or _c(r) > 0:
                md.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                    ad, r["sahne"], r["tohum"], r.get("durum"), r.get("sure_s"), r.get("p_en"), r.get("carpma_sayisi"),
                    r.get("carpma_suresi_s"), r.get("kurtarma"), (r.get("olaylar") or "").replace("|", "/")[:120]))
    md.append("")
    return md


if __name__ == "__main__":
    if "--birlestir" in sys.argv:
        birlestir()
    else:
        print("\n".join(v6_bolumu()))
