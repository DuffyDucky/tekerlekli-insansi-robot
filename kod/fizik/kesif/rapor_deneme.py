"""Deneme zinciri (HAFIZALI sınıf) raporu: sonuc/deneme_*.csv, deneme_*_hizala.csv -> SONUC.md bölümü.

    py -3 -m kesif.rapor_deneme          # bölümü yazdırır; `kesif.kos rapor` SONUC.md'ye ekler

Bu bölümün sayıları "ilk girişte, hiç bilgi olmadan" KPI'larıyla karıştırılmaz: 2. ve sonraki denemelerde beyin önceki
denemelerin haritasını bilir.
"""

import csv
import json
import os
import statistics as st

from ._yol import SAHNELER
from .rapor import SONUC

KUMELER = [("gelistirme", "deneme_gelistirme.csv"), ("sinama2", "deneme_sinama2.csv")]
ILK_KPI = {"gelistirme": "mujoco_v3.csv", "sinama2": "mujoco_sinama2_v3.csv"}


def _oku(ad):
    yol = os.path.join(SONUC, ad)
    if not os.path.exists(yol):
        return []
    with open(yol, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _f(v, d=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def _zincirler(R):
    Z = {}
    for r in R:
        Z.setdefault((r["sahne"], int(r["tohum"])), []).append(r)
    for k in Z:
        Z[k].sort(key=lambda r: int(r["deneme_no"]))
    return Z


def _cozum_m(ad):
    try:
        with open(os.path.join(SAHNELER, ad + ".json"), encoding="utf-8") as f:
            return float(json.load(f)["labirent"]["cozum_uzunlugu_m"])
    except Exception:
        return None


def ana_tablo(kumeler):
    md = ["| küme | zincir | 1. denemede | 2. | 3. | 4. | 4 denemede çözülmedi | toplam süre ortanca (s, çözülen) | "
          "deneme sayısı | çarpma (toplam) | fail_start | START kesme | hata satırı |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for kume, R in kumeler:
        if not R:
            continue
        Z = _zincirler(R)
        dag = {1: 0, 2: 0, 3: 0, 4: 0}
        coz, tops = 0, []
        for rs in Z.values():
            son = rs[-1]
            if son.get("durum") == "basari":
                dag[int(son["deneme_no"])] = dag.get(int(son["deneme_no"]), 0) + 1
                tops.append(_f(son.get("toplam_sure_s"), 0.0))
                coz += 1
        n = len(Z)
        md.append("| %s | %d | %d | %d | %d | %d | %d | %s | %d | %d | %d | %d | %d |" % (
            kume, n, dag[1], dag[2], dag[3], dag[4], n - coz, ("%.0f" % st.median(tops)) if tops else "-", len(R),
            int(sum(_f(r.get("carpma_sayisi"), 0) for r in R)), sum(int(_f(r.get("fail_start"), 0)) for r in R),
            int(sum(_f(r.get("start_kesme"), 0) for r in R)), sum(1 for r in R if r.get("durum") == "hata")))
    return md


def zincir_tablo(R):
    md = ["| sahne | tohum | çözüm (m) | deneme: durum / süre (s) | çözüldüğü deneme | toplam süre (s) | "
          "bilinen alan sonda (m²), deneme başına | birleşik hücre (deneme sonu) | poz hatası maks (m) | "
          "START hatası 0,5 s (m / °) |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for (ad, t), rs in sorted(_zincirler(R).items()):
        son = rs[-1]
        md.append("| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            ad, t, ("%.0f" % _f(son.get("cozum_m"))) if _f(son.get("cozum_m")) else "-",
            "; ".join("%s %s %.0f" % (r["deneme_no"], r.get("durum"), _f(r.get("sure_s"), 0)) for r in rs),
            son["deneme_no"] if son.get("durum") == "basari" else "yok",
            son.get("toplam_sure_s"),
            " → ".join("%.0f" % _f(r.get("bilinen_son_m2"), 0) for r in rs),
            " → ".join(str(r.get("birlesik_hucre")) for r in rs),
            " / ".join(str(r.get("poz_hata_maks_m")) for r in rs),
            " / ".join("%s %s" % (r.get("bas_hata_m"), r.get("bas_hata_der")) for r in rs[1:]) or "-"))
    return md


def buyume_tablo(kumeler):
    """Deneme no başına: yeni bilinen alan, yeni hücre, süre."""
    md = ["| küme | deneme no | n | başarı | harita büyümesi ort (m²) | yeni hücre ort (birleşik artışı) | "
          "poz hatası maks ort (m) | kurtarma ort |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for kume, R in kumeler:
        Z = _zincirler(R)
        for k in (1, 2, 3, 4):
            rs, yeni = [], []
            for z in Z.values():
                for i, r in enumerate(z):
                    if int(r["deneme_no"]) == k:
                        rs.append(r)
                        onceki = int(z[i - 1]["birlesik_hucre"]) if i > 0 else 0
                        yeni.append(int(r["birlesik_hucre"]) - onceki)
            if not rs:
                continue
            md.append("| %s | %d | %d | %d | %.1f | %.1f | %.2f | %.1f |" % (
                kume, k, len(rs), sum(r.get("durum") == "basari" for r in rs),
                st.mean(_f(r.get("buyume_m2"), 0) for r in rs), st.mean(yeni),
                st.mean(_f(r.get("poz_hata_maks_m"), 0) for r in rs), st.mean(_f(r.get("kurtarma"), 0) for r in rs)))
    return md


def ilk_eslesme(kume, R):
    """1. deneme satırları eski ilk giriş koşusuyla aynı mı (aynı kurulum; belirlenimcilik denetimi)."""
    eski = {(r["sahne"], int(r["tohum"])): r for r in _oku(ILK_KPI[kume])}
    n = ayni = 0
    fark = []
    for r in R:
        if int(r["deneme_no"]) != 1:
            continue
        e = eski.get((r["sahne"], int(r["tohum"])))
        if e is None:
            continue
        n += 1
        if e.get("durum") == r.get("durum") and abs(_f(e.get("sure_s"), 0) - _f(r.get("sure_s"), 0)) < 1.0:
            ayni += 1
        else:
            fark.append("%s t%s: eski %s %s, şimdi %s %s" % (r["sahne"], r["tohum"], e.get("durum"), e.get("sure_s"),
                                                         r.get("durum"), r.get("sure_s")))
    return n, ayni, fark


def hizala_tablo(ad):
    H = _oku(ad)
    if not H:
        return []
    md = ["| hizalama | n | yerleştirme hatası ort (m / °) | START hatası 0,5 s ort / maks (m) | yön 0,5 s ort / maks (°) | "
          "10 s ort / maks (m) | yön 10 s ort / maks (°) |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for hz in ("1", "0"):
        rs = [r for r in H if r.get("hizala") == hz]
        if not rs:
            continue

        def om(k):
            v = [_f(r.get(k), 0) for r in rs]
            return "%.3f / %.3f" % (st.mean(v), max(v))
        yer = st.mean((_f(r["yer_dx_m"]) ** 2 + _f(r["yer_dy_m"]) ** 2) ** 0.5 for r in rs)
        yd = st.mean(abs(_f(r["yer_dth_der"])) for r in rs)
        md.append("| %s | %d | %.3f / %.2f | %s | %s | %s | %s |" % (
            "açık" if hz == "1" else "kapalı", len(rs), yer, yd, om("hata_05_m"), om("hata_05_der"), om("hata_10_m"),
            om("hata_10_der")))
    return md


def hiz_tablo(kumeler):
    """Harita tam bilinse sığar mı: bilinen haritada ölçülen yürüyüş temposu (s / m çözüm) x çözüm uzunluğu.
    Tempo kaynağı: mujoco_sinama_v2.csv `kos` = hafiza satırları (ilk koşusu başarılı labirentte, tam bilinen çözüm
    yolunu yeniden süren koşu; v2 hız profili, v3 ile aynı sürüş)."""
    H = [r for r in _oku("mujoco_sinama_v2.csv") if r.get("kos") == "hafiza" and r.get("durum") == "basari"]
    tempo = sorted(_f(r["sure_s"]) / _cozum_m(r["sahne"]) for r in H if _cozum_m(r["sahne"]))
    if not tempo:
        return []
    t_min, t_ort, t_maks = tempo[0], st.median(tempo), tempo[-1]
    md = ["Bilinen haritada ölçülen tempo (çözüm metresi başına süre, %d hafızalı koşu): en iyi %.2f, ortanca %.2f, "
          "en kötü %.2f s/m (yalnız düz sürüş + köşelerde dur–dön–kalk; ölçülen düz hız ~0,23 m/s)." % (
              len(tempo), t_min, t_ort, t_maks), "",
          "| sahne | çözüm (m) | alt sınır çözüm / 0,39 m/s (s) | tam haritayla beklenen süre en iyi / ortanca / en kötü (s) | "
          "900 s'ye sığar mı | zincir sonucu (tohum: çözüldüğü deneme) |", "| --- | --- | --- | --- | --- | --- |"]
    Z = {}
    for _, R in kumeler:
        for (ad, t), rs in _zincirler(R).items():
            Z.setdefault(ad, []).append("t%d: %s" % (t, rs[-1]["deneme_no"] if rs[-1].get("durum") == "basari"
                                                     else "yok (%d deneme)" % len(rs)))
    for ad in sorted(Z, key=lambda a: -(_cozum_m(a) or 0)):
        c = _cozum_m(ad) or 0.0
        if c < 140:
            continue
        b = c * t_min, c * t_ort, c * t_maks
        sig = "evet" if b[2] < 900 else ("hayır" if b[0] > 900 else
                                         "sınırda: ortanca tempoda %+.0f s pay, en kötüde %+.0f s; keşfe yer yok" % (
                                             900 - b[1], 900 - b[2]))
        md.append("| %s | %.0f | %.0f | %.0f / %.0f / %.0f | %s | %s |" % (ad, c, c / 0.39, b[0], b[1], b[2], sig,
                                                                          ", ".join(sorted(Z[ad]))))
    return md


def deneme_bolumu():
    kumeler = [(k, _oku(a)) for k, a in KUMELER]
    if not any(R for _, R in kumeler):
        return []
    md = ["## Deneme zinciri (HAFIZALI sınıf): başarısız denemenin haritası sonraki denemeye taşınır", "",
          "**Bu bölüm \"ilk girişte, hiç bilgi olmadan\" KPI'sı değildir.** 2. ve sonraki denemelerde beyin önceki "
          "denemelerin haritasını bilir. İlk giriş KPI'sı (v3, ön bilgisiz) değişmedi: yukarıdaki \"v2 / v3\" bölümü. "
          "CSV: `sonuc/deneme_gelistirme.csv`, `sonuc/deneme_sinama2.csv` (sütunlar `sinif` = hafizali, `kume`, "
          "`deneme_no`; her deneme ayrı satır). Kurulum: `kesif.kos_deneme`, `kesif.deneme`. Robot her yeni denemede "
          "START pozuna + yerleştirme hatasına (std 3 cm, 2°; kırpma 6 cm, 4°) konur; beyin pozunu harita çerçevesinde "
          "START'a sıfırlar, ilk iki taramayı geniş aramayla eski haritaya oturtur. En çok 4 deneme, her biri 900 s.", ""]
    md += ana_tablo(kumeler) + [""]
    for kume, R in kumeler:
        if not R:
            continue
        n, ayni, fark = ilk_eslesme(kume, R)
        md.append("1. deneme = eski ilk giriş koşusu (%s, `%s`): %d/%d aynı sonuç ve süre (±1 s)%s." % (
            kume, ILK_KPI[kume], ayni, n, ("; farklı: " + "; ".join(fark)) if fark else ""))
    md.append("")
    md += buyume_tablo(kumeler) + [""]
    for kume, R in kumeler:
        if R:
            md += ["### Zincirler: %s" % kume, ""] + zincir_tablo(R) + [""]
    for kume, a in KUMELER:
        h = hizala_tablo(os.path.splitext(a)[0] + "_hizala.csv")
        if h:
            md += ["### START'ta yeniden hizalama (%s; aynı beyin kopyası, aynı yerleştirme, 10 s sonda)" % kume, ""]
            md += h + [""]
    k = hiz_tablo(kumeler)
    if k:
        md += ["### Hız sınırı: harita tam bilinse 900 s'ye sığar mı", ""] + k + [""]
    return md


def gorsel_yaz(yol=None):
    """gorsel/deneme_zinciri.png: zincir başına deneme sonunda bilinen alan (m²); çözüldüğü deneme işaretli."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ._yol import KESIF
    yol = yol or os.path.join(KESIF, "gorsel", "deneme_zinciri.png")
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    fig, eksen = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, (kume, ad) in zip(eksen, KUMELER):
        for (sahne, t), rs in sorted(_zincirler(_oku(ad)).items()):
            x = [int(r["deneme_no"]) for r in rs]
            y = [_f(r["bilinen_son_m2"], 0) for r in rs]
            coz = rs[-1].get("durum") == "basari"
            ax.plot(x, y, "-", color="#4a78b5" if coz else "#c0504d", lw=1, alpha=0.7)
            ax.plot(x[-1], y[-1], "o" if coz else "x", color="#4a78b5" if coz else "#c0504d", ms=5)
        ax.set_title("%s: deneme sonunda bilinen alan" % kume)
        ax.set_xlabel("deneme no")
        ax.set_xticks([1, 2, 3, 4])
        ax.grid(alpha=0.3)
    eksen[0].set_ylabel("bilinen alan (m²)")
    fig.text(0.5, 0.005, "mavi nokta: o denemede çözüldü; kırmızı x: 4 denemede çözülmedi (hafızalı sınıf)",
             ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(yol, dpi=90)
    return yol


if __name__ == "__main__":
    import sys
    if "--gorsel" in sys.argv:
        print(gorsel_yaz())
    else:
        print("\n".join(deneme_bolumu()))
