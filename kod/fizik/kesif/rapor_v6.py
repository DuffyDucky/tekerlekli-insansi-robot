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
PLAN = {"mujoco_v6.csv": 37, "mujoco_sinama2_v6.csv": 20, "mujoco_sinama4_v6.csv": 20, "mujoco_sinama5_v6.csv": 20}


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
                           ("**sınama5** (YENİ)", "mujoco_sinama5_v3.csv", None, "mujoco_sinama5_v6.csv")):
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
        zin[b] = (len(R), sum(_c(r) for r in R), sum(_f(r.get("carpma_suresi_s")) or 0.0 for r in R))
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
    R = _csv("v6_2b.csv")
    if not R:
        return []
    S = {s: [r for r in R if r.get("ayar") == s] for s in ("v5", "v6")}
    an = {_anahtar(r) for r in S["v5"]} & {_anahtar(r) for r in S["v6"]}
    md = ["| sürüm | koşu | başarı | çarpma olayı (koşu) | temas (s) | süre ortanca (başarılı, s) | kurtarma |",
          "| --- | --- | --- | --- | --- | --- | --- |"]
    for s in ("v5", "v6"):
        X = [r for r in S[s] if _anahtar(r) in an]
        ok = [r for r in X if r.get("durum") == "basari"]
        md.append("| %s | %d | %d/%d | %d (%d) | %.2f | %s | %d |" % (
            s, len(X), len(ok), len(X), sum(_c(r) for r in X), sum(_c(r) > 0 for r in X),
            sum(_f(r.get("carpma_suresi_s")) or 0.0 for r in X), _s(st.median([_f(r["sure_s"]) for r in ok]) if ok else None),
            sum(int(_f(r.get("kurtarma")) or 0) for r in X)))
    o = _oran([r for r in S["v5"] if _anahtar(r) in an], [r for r in S["v6"] if _anahtar(r) in an])
    md += ["", "v6/v5 süre oranı (ikisi de başarılı): ortanca %s (%d çift). Koşulan: v5 %d, v6 %d (plan 21 + 21, yalnız "
           "tohum 0: süre bütçesi için tohum 1 atıldı)." % (_s(o[0], "%.3f"), o[1], len(S["v5"]), len(S["v6"]))]
    return md


def karar(K):
    s5 = [D for ad, D, d6, n3 in K if d6 == "mujoco_sinama5_v6.csv"][0]
    b3 = sum(r.get("durum") == "basari" for r in s5["v3"])
    b6 = sum(r.get("durum") == "basari" for r in s5["v6"])
    tam = all(len(D["v6"]) == PLAN[d6] for ad, D, d6, n3 in K)
    t6 = sum(_c(r) for ad, D, d6, n3 in K for r in D["v6"])
    a = len(s5["v6"]) == PLAN["mujoco_sinama5_v6.csv"] and len(s5["v3"]) == len(s5["v6"]) and b6 >= b3
    b = tam and t6 == 0
    return b3, b6, t6, tam, a, b


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
    md += ["", "### 2B v5 / v6 (21 geliştirme labirenti, tohum 0; `sonuc/v6_2b.csv`)", ""]
    md += ikib_tablosu()
    md += ["", "### MuJoCo (900 s, ön bilgisiz)", "",
           "v6 kodu dondurulduktan sonra (`sonuc/ham/v6_kod/`) koşuldu; ayar yapılmadı. v3 / v5 satırları v6'nın koşulduğu "
           "sahne + tohumlarla eşlenir. Sınama2 ve sınama4 görülmüş kümelerdir (gerileme denetimi). Sınama5 bu aşamada "
           "üretildi; v3 sınama5 koşuları v6 öncesi kod kopyasından (`sonuc/ham/v6_oncesi_kod/`).", "",
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
    md += ["", "**Varsayılan kuralı** (a) sınama5'te v6 başarısı v3'ten az değil: v3 %d, v6 %d -> %s; (b) koşulan bütün "
           "kümelerde (geliştirme + sınama2 + sınama4 + sınama5) v6 temas olayı sıfır ve kümeler tam koşuldu: temas %d, "
           "tam koşuldu %s -> %s. Sonuç: %s" % (
               b3, b6, "sağlandı" if a else "SAĞLANMADI", t6, "evet" if tam else "HAYIR", "sağlandı" if b else "SAĞLANMADI",
               "`VARSAYILAN_SURUM = \"v6\"`." if (a and b) else "`VARSAYILAN_SURUM` v3 KALIR. v6 seçmeli: "
               "`surum_ayari(\"v6\")`.")]
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
