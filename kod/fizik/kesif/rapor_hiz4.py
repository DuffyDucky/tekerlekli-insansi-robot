"""v4 (hız zarfı) bölümü: SONUC.md'ye eklenir (`kesif.kos rapor`); tek başına: py -3 -m kesif.rapor_hiz4.

Kaynaklar (hepsi sonuc/ altında; sayılar CSV'den, elle düzeltme yok):
- hiz_tani_*.csv (`kesif.hiz_tani`): koşu başına hız / kip / duvar payı ölçüsü (kayıtlardan)
- v3_2b.csv (v3 satırları) / v4_2b.csv: 2B geliştirme
- mujoco_v3.csv / mujoco_v4.csv: MuJoCo geliştirme (aynı labirent ve tohumlar)
- mujoco_sinama3_v3.csv / mujoco_sinama3_v4.csv: YENİ sınama kümesi (13x13 / 17x17 t14..t18 x tohum {0, 1})
- mujoco_sinama2_v3.csv / mujoco_sinama2_v4.csv: görülmüş ikinci sınama kümesi, yalnız gerileme ve "sonradan bakıldı"
"""

import csv
import glob
import os
import statistics as st

from ._yol import KESIF

SONUC = os.path.join(KESIF, "sonuc")


def _csv(ad):
    yol = os.path.join(SONUC, ad)
    if not os.path.exists(yol):
        return []
    with open(yol, encoding="utf-8") as f:
        R = list(csv.DictReader(f))
    for r in R:
        if not r.get("durum") and (_f(r.get("sure_s")) or 0) >= 899.8:
            r["durum"] = "fail_sure"
    return [r for r in R if r.get("kos", "ilk") in ("", "ilk")]


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _hiz():
    H = {}
    for yol in sorted(glob.glob(os.path.join(SONUC, "hiz_tani_*.csv"))):
        with open(yol, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                H[(r.get("surum"), r.get("sahne"), str(r.get("tohum")), r.get("kume"))] = r
    return H


def _anahtar(r):
    return r["sahne"], str(r["tohum"])


def ozet(R, H, surum, kume):
    """Bir sürüm x küme satırının ölçüleri."""
    ok = [r for r in R if r.get("durum") == "basari"]
    hz = [H.get((surum, r["sahne"], str(r["tohum"]), r.get("kume") or kume)) for r in R]
    hz = [h for h in hz if h and h.get("duz_s")]
    Td = sum(_f(h["duz_s"]) for h in hz) or None

    def ag(k):
        if not Td:
            return None
        return sum(_f(h[k]) * _f(h["duz_s"]) for h in hz if _f(h.get(k)) is not None) / Td
    return {"n": len(R), "basari": len(ok),
            "sure_ort": st.median([_f(r["sure_s"]) for r in ok]) if ok else None,
            "puan_ort": st.mean([_f(r.get("puan")) or 0.0 for r in R]) if R else None,
            "carpma": sum(int(_f(r.get("carpma_sayisi")) or 0) for r in R),
            "temas": sum(_f(r.get("carpma_suresi_s")) or 0.0 for r in R),
            "v_duz": ag("v_duz_ort"), "hizli": ag("hizli_pay"), "kuyruk": sum(_f(h["kuyruk_s"]) for h in hz) if hz else None,
            "pay_min": min((_f(h["duvar_pay_min_m"]) for h in hz), default=None),
            "pay_5mm": sum(_f(h["duvar_pay_min_m"]) < 0.005 for h in hz),
            "pay_p01": st.median([_f(h["duvar_pay_p01_m"]) for h in hz]) if hz else None, "n_hiz": len(hz)}


def oran(R3, R4):
    a = {_anahtar(r): r for r in R3 if r.get("durum") == "basari"}
    o = [_f(r["sure_s"]) / _f(a[_anahtar(r)]["sure_s"]) for r in R4 if r.get("durum") == "basari" and _anahtar(r) in a]
    return (st.median(o), st.mean(o), len(o)) if o else (None, None, 0)


def _s(v, fmt="%.0f"):
    return "-" if v is None else fmt % v


def tablo(satirlar, H):
    md = ["| küme | sürüm | başarı | süre ortanca (başarılı, s) | v4/v3 süre ortanca (ort; çift) | puan ort | "
          "düz hız ort (m/s) | hızlı kip payı (düz süre) | 0,10 m/s altı kuyruk (s) | çarpma olayı | temas (s) | "
          "en küçük duvar payı (m; koşu p01 ortancası) | payı < 5 mm koşu |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for kume, R3, R4 in satirlar:
        o = oran(R3, R4)
        for sur, R in (("v3", R3), ("v4", R4)):
            if not R:
                md.append("| %s | %s | koşulmadı | | | | | | | | | | |" % (kume, sur))
                continue
            z = ozet(R, H, sur, kume)
            md.append("| %s | %s | %d/%d | %s | %s | %s | %s | %s | %s | %d | %s | %s (%s) | %d/%d |" % (
                kume, sur, z["basari"], z["n"], _s(z["sure_ort"]),
                ("%.3f (%.3f; %d)" % o) if sur == "v4" and o[0] is not None else "",
                _s(z["puan_ort"]), _s(z["v_duz"], "%.3f"), _s(z["hizli"], "%.2f"), _s(z["kuyruk"]), z["carpma"],
                _s(z["temas"], "%.2f"), _s(z["pay_min"], "%.3f"), _s(z["pay_p01"], "%.3f"), z["pay_5mm"], z["n_hiz"]))
    return md


def karar(R3, R4):
    b3 = sum(r.get("durum") == "basari" for r in R3)
    b4 = sum(r.get("durum") == "basari" for r in R4)
    c3 = sum(int(_f(r.get("carpma_sayisi")) or 0) for r in R3)
    c4 = sum(int(_f(r.get("carpma_sayisi")) or 0) for r in R4)
    return b3, b4, c3, c4, (len(R4) == len(R3) and len(R4) > 0 and b4 >= b3 and c4 <= c3)


def v4_bolumu():
    H = _hiz()
    md = ["## v4: hız zarfı (fren zarfı, ölçüye dayalı hızlanma izni, yay süpürme denetimi)", ""]
    t3 = [h for h in H.values() if h.get("surum") == "v3" and h.get("kume") in ("gelistirme", "sinama2")
          and h.get("duz_s")]
    if t3:
        T = sum(_f(h["sure_s"]) for h in t3)
        Td = sum(_f(h["duz_s"]) for h in t3)

        def ag(k):
            return sum(_f(h[k]) * _f(h["duz_s"]) for h in t3) / Td
        md += ["### Tanı (v3 MuJoCo kayıtları, geliştirme + sınama2, %d koşu; `sonuc/hiz_tani_v3.csv`)" % len(t3), "",
               "- Düz sürüş toplam sürenin %%%.0f'i; ölçülen düz hız (düz süre ağırlıklı) %.3f m/s." % (
                   100 * Td / T, ag("v_duz_ort")),
               "- Hızlı kip (v_komut > 0,26) düz sürenin %%%.0f'inde açık. Koşulların tek başına engellediği pay: "
               "1,0 m ön şerit %%%.0f, |w| <= 0,12 %%%.0f, 1,5 s bekleme %%%.0f. Yalnız ön şerit %%%.0f, yalnız w "
               "%%%.0f, yalnız bekleme %%%.1f." % tuple(100 * ag(k) for k in (
                   "hizli_pay", "kosul_A", "kosul_B", "kosul_C", "yalniz_A", "yalniz_B", "yalniz_C")),
               "- Düz sürenin hız dağılımı: < 0,10 m/s %%%.0f, 0,10–0,20 %%%.0f, 0,20–0,24 %%%.0f, 0,24–0,26 %%%.0f, "
               "0,26–0,33 %%%.0f, >= 0,33 %%%.0f." % tuple(100 * ag(k) for k in (
                   "h_0_10", "h_10_20", "h_20_24", "h_24_26", "h_26_33", "h_33_40")),
               "- Düz parça %d (ortalama %.2f m). 1,5 m'den kısa %d parça %.0f s sürdü; ideal dur-kalk süresi %.0f s. "
               "Parça sonunda 0,10 m/s altında geçen kuyruk toplam %.0f s (toplam sürenin %%%.1f'i): izleyicinin "
               "doğrusal yumuşak varışı (v <= 0,8 x kalan) köşeye üstel yaklaşıyor." % (
                   sum(int(_f(h["parca_sayisi"])) for h in t3), st.mean(_f(h["parca_ort_m"]) for h in t3),
                   sum(int(_f(h["kisa_parca"])) for h in t3), sum(_f(h["kisa_s"]) for h in t3),
                   sum(_f(h["kisa_ideal_s"]) for h in t3), sum(_f(h["kuyruk_s"]) for h in t3),
                   100 * sum(_f(h["kuyruk_s"]) for h in t3) / T),
               "- Üst sınır: her düz parça 0,39 m/s tavan ve 0,5 m/s² hızlanma / yavaşlamayla (yay ve eğrilik yok "
               "sayılarak) %.0f s yerine %.0f s sürerdi; kazanç en çok %.0f s, toplam sürenin %%%.0f'i. Yerinde "
               "dönüş, plan ve kurtarma değişmez sayıldı." % (
                   Td, sum(_f(h["ideal_duz_s"]) for h in t3), sum(_f(h["ust_kazanc_s"]) for h in t3),
                   100 * sum(_f(h["ust_kazanc_s"]) for h in t3) / T), ""]
    b23 = [r for r in _csv("v3_2b.csv") if r.get("ayar") == "v3"]
    b24 = _csv("v4_2b.csv")
    if b24:
        o = oran(b23, b24)
        md += ["### 2B geliştirme (21 labirent x tohum {0, 1}; `sonuc/v3_2b.csv` v3 satırları, `sonuc/v4_2b.csv`)", "",
               "| sürüm | başarı | çarpma olayı | temas (s) | süre ortanca (başarılı) |", "| --- | --- | --- | --- | --- |"]
        for sur, R in (("v3", b23), ("v4", b24)):
            ok = [_f(r["sure_s"]) for r in R if r.get("durum") == "basari"]
            md.append("| %s | %d/%d | %d | %.2f | %s |" % (
                sur, len(ok), len(R), sum(int(_f(r.get("carpma_sayisi")) or 0) for r in R),
                sum(_f(r.get("carpma_suresi_s")) or 0 for r in R), _s(st.median(ok) if ok else None)))
        md += ["", "v4/v3 süre oranı (ikisi de başarılı, %d çift): ortanca %s, ortalama %s." % (
            o[2], _s(o[0], "%.3f"), _s(o[1], "%.3f")), ""]
    d3, d4 = _csv("mujoco_v3.csv"), _csv("mujoco_v4.csv")
    s3, s4 = _csv("mujoco_sinama3_v3.csv"), _csv("mujoco_sinama3_v4.csv")
    q3, q4 = _csv("mujoco_sinama2_v3.csv"), _csv("mujoco_sinama2_v4.csv")
    anah4 = {_anahtar(r) for r in d4}
    d3 = [r for r in d3 if _anahtar(r) in anah4] if d4 else d3
    md += ["### MuJoCo v3 / v4 (900 s, ön bilgisiz)", "",
           "Geliştirme ve sınama3 ayrı satırda. Sınama3 (13x13 / 17x17 t14..t18) bu aşamada üretildi; v4'ün sınama3 "
           "sonuçlarına geliştirme bitene kadar bakılmadı. Sınama2 görülmüş kümedir, yalnız gerileme denetimi.", ""]
    md += tablo([("geliştirme", d3, d4), ("sınama3", s3, s4)], H)
    md += ["", "Duvar payı gerçek pozdan ölçülür: ayak izi kutusu (±0,264 x ±0,262 m) ile 2B duvar çizgileri arası, her 2. "
           "adım (`kesif.hiz_tani`). -0,001 = kutu çizgiye değdi. MuJoCo temas bayrağı bu anların çoğunda 0 kaldı "
           "(temas sütunu); çarpışma geometrisinin kutudan birkaç mm farkı olabilir. Yine de bu, payın tükendiği andır."]
    if q4:
        anah = {_anahtar(r) for r in q4}
        md += ["", "Sonradan bakıldı (sınama2, görülmüş küme; v4 koşulan satırlar):", ""]
        md += tablo([("sınama2 (sonradan bakıldı)", [r for r in q3 if _anahtar(r) in anah], q4)], H)
        hz = [r for r in q4 if r["sahne"] in ("labirent_17x17_t11", "labirent_17x17_t12")]
        if hz:
            md += ["", "Hız sınıfı (sınama2'de v3'ün süreye sığmadığı 17x17_t11 ve t12; sonradan bakıldı):", "",
                   "| sahne | tohum | v3 durum / süre | v4 durum / süre | v4 p_en | v4 yol (m) |",
                   "| --- | --- | --- | --- | --- | --- |"]
            a3 = {_anahtar(r): r for r in q3}
            for r in sorted(hz, key=_anahtar):
                e = a3.get(_anahtar(r), {})
                md.append("| %s | %s | %s / %s | %s / %s | %s | %s |" % (
                    r["sahne"], r["tohum"], e.get("durum", "-"), e.get("sure_s", "-"), r.get("durum"), r.get("sure_s"),
                    r.get("p_en"), r.get("yol_m")))
    if s4:
        b3, b4, c3, c4, ok = karar(s3, s4)
        md += ["", "**Karar kuralı** (sınama3): v4 başarısı v3'ten az değil (%d / %d) ve çarpma artmadı (%d / %d) -> %s" % (
            b3, b4, c3, c4, "sağlandı, `VARSAYILAN_SURUM = \"v4\"` (sonra v3'e döndü: v5 bölümü)." if ok else
            "SAĞLANMADI, `VARSAYILAN_SURUM` v3 kalır."), ""]
        md += ["Kalan başarısızlıklar (v4):", "", "| küme | sahne | tohum | durum | süre | p_en | yol (m) | çarpma | son olaylar |",
               "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for kume, R in (("geliştirme", d4), ("sınama3", s4), ("sınama2", q4)):
            for r in sorted(R, key=_anahtar):
                if r.get("durum") != "basari":
                    md.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                        kume, r["sahne"], r["tohum"], r.get("durum"), r.get("sure_s"), r.get("p_en"), r.get("yol_m"),
                        r.get("carpma_sayisi"), (r.get("olaylar") or "").replace("|", "/")[:120]))
        md.append("")
    return md


def gorsel(yol=None):
    """gorsel/hiz_v3_v4.png: düz sürenin hız dağılımı (küme x sürüm, düz süre ağırlıklı)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    H = list(_hiz().values())
    kut = ["h_0_10", "h_10_20", "h_20_24", "h_24_26", "h_26_33", "h_33_40"]
    et = ["<0,10", "0,10-0,20", "0,20-0,24", "0,24-0,26", "0,26-0,33", ">=0,33"]
    gr = [("v3", "gelistirme", "geliştirme v3"), ("v4", "gelistirme", "geliştirme v4"),
          ("v3", "sinama3", "sınama3 v3"), ("v4", "sinama3", "sınama3 v4")]
    renk = ["#9aa7b8", "#2b6cb0", "#c9b39a", "#b7642b"]
    fig, ax = plt.subplots(figsize=(8, 3.6), dpi=110)
    w = 0.2
    for k, (sur, kume, ad) in enumerate(gr):
        R = [h for h in H if h.get("surum") == sur and h.get("kume") == kume and h.get("duz_s")]
        if not R:
            continue
        Td = sum(_f(h["duz_s"]) for h in R)
        y = [sum(_f(h[c]) * _f(h["duz_s"]) for h in R) / Td for c in kut]
        ax.bar([i + (k - 1.5) * w for i in range(len(kut))], y, w, color=renk[k], label="%s (%d koşu)" % (ad, len(R)))
    ax.set_xticks(range(len(kut)))
    ax.set_xticklabels(et)
    ax.set_xlabel("ölçülen ileri hız (m/s), düz sürüş")
    ax.set_ylabel("düz sürenin payı")
    ax.set_title("MuJoCo: v3 / v4 düz sürüş hız dağılımı", fontsize=10, loc="left")
    ax.legend(fontsize=8, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    yol = yol or os.path.join(KESIF, "gorsel", "hiz_v3_v4.png")
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    fig.tight_layout()
    fig.savefig(yol)
    plt.close(fig)
    return yol


if __name__ == "__main__":
    import sys
    if "--gorsel" in sys.argv:
        print(gorsel())
    else:
        print("\n".join(v4_bolumu()))
