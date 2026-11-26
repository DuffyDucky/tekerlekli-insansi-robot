"""v5 (dönüş / yay güvenliği) bölümü: SONUC.md'ye eklenir (`kesif.kos rapor`); tek başına: py -3 -m kesif.rapor_v5.

Kaynaklar (hepsi sonuc/ altında; sayılar CSV'den, elle düzeltme yok):
- mujoco_v3.csv / mujoco_v4.csv / mujoco_v5.csv: MuJoCo geliştirme (v5 koşulan sahne + tohumlarla eşlenir)
- mujoco_sinama2_v3.csv / _v4.csv / _v5.csv: sınama2 (görülmüş; v4 çarpmalarının tanısı burada yapıldı -> geliştirme
  sayılır)
- mujoco_sinama4_v3.csv / _v4.csv / _v5.csv: YENİ sınama4 (13x13 / 17x17 t19..t23 x tohum {0, 1}); v5 dondurulduktan sonra koşuldu
"""

import statistics as st

from .rapor_hiz4 import _anahtar, _csv, _f, _hiz, _s


def _ozet(R):
    ok = [r for r in R if r.get("durum") == "basari"]
    return {"n": len(R), "basari": len(ok),
            "sure": st.median([_f(r["sure_s"]) for r in ok]) if ok else None,
            "puan": st.mean([_f(r.get("puan")) or 0.0 for r in R]) if R else None,
            "carpma": sum(int(_f(r.get("carpma_sayisi")) or 0) for r in R),
            "carpmali_kosu": sum((_f(r.get("carpma_sayisi")) or 0) > 0 for r in R),
            "temas": sum(_f(r.get("carpma_suresi_s")) or 0.0 for r in R),
            "kurtarma": sum(int(_f(r.get("kurtarma")) or 0) for r in R)}


def _oran(Ra, Rb):
    a = {_anahtar(r): r for r in Ra if r.get("durum") == "basari"}
    o = [_f(r["sure_s"]) / _f(a[_anahtar(r)]["sure_s"]) for r in Rb if r.get("durum") == "basari" and _anahtar(r) in a]
    return (st.median(o), len(o)) if o else (None, 0)


def _esle(R, anah):
    return [r for r in R if _anahtar(r) in anah]


def _pay(H, sur, R):
    """Gerçek pozdan ölçülen duvar payı < 5 mm koşu sayısı / ölçülen koşu (kesif.hiz_tani; ölçüm tarafı)."""
    h = [H.get((sur, r["sahne"], str(r["tohum"]), r.get("kume"))) for r in R]
    h = [x for x in h if x and x.get("duvar_pay_min_m") not in (None, "")]
    return "%d/%d" % (sum(_f(x["duvar_pay_min_m"]) < 0.005 for x in h), len(h)) if h else "-"


def tablo(satirlar):
    H = _hiz()
    md = ["| küme | sürüm | başarı | çarpma olayı (koşu) | temas (s) | süre ortanca (başarılı, s) | süre oranı / v4 "
          "(ortanca; çift) | süre oranı / v3 | puan ort | kurtarma | duvar payı < 5 mm koşu |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for kume, D in satirlar:
        for sur in ("v3", "v4", "v5"):
            R = D.get(sur)
            if not R:
                continue
            z = _ozet(R)
            o4 = _oran(D.get("v4") or [], R) if sur == "v5" else (None, 0)
            o3 = _oran(D.get("v3") or [], R) if sur != "v3" else (None, 0)
            md.append("| %s | %s | %d/%d | %d (%d) | %.2f | %s | %s | %s | %s | %d | %s |" % (
                kume, sur, z["basari"], z["n"], z["carpma"], z["carpmali_kosu"], z["temas"], _s(z["sure"]),
                ("%.3f; %d" % o4) if o4[0] is not None else "", ("%.3f; %d" % o3) if o3[0] is not None else "",
                _s(z["puan"]), z["kurtarma"], _pay(H, sur, R)))
    return md


def kumeler():
    d5 = _csv("mujoco_v5.csv")
    anah = {_anahtar(r) for r in d5}
    gel = {"v3": _esle(_csv("mujoco_v3.csv"), anah), "v4": _esle(_csv("mujoco_v4.csv"), anah), "v5": d5}
    q5 = _csv("mujoco_sinama2_v5.csv")
    anq = {_anahtar(r) for r in q5}
    s2 = {"v3": _esle(_csv("mujoco_sinama2_v3.csv"), anq), "v4": _esle(_csv("mujoco_sinama2_v4.csv"), anq), "v5": q5}
    s4 = {"v3": _csv("mujoco_sinama4_v3.csv"), "v4": _csv("mujoco_sinama4_v4.csv"), "v5": _csv("mujoco_sinama4_v5.csv")}
    return gel, s2, s4


def karar(s4):
    R3, R5 = s4.get("v3") or [], s4.get("v5") or []
    b3 = sum(r.get("durum") == "basari" for r in R3)
    b5 = sum(r.get("durum") == "basari" for r in R5)
    c3 = sum(int(_f(r.get("carpma_sayisi")) or 0) for r in R3)
    c5 = sum(int(_f(r.get("carpma_sayisi")) or 0) for r in R5)
    return b3, b5, c3, c5, (len(R5) == len(R3) and len(R5) > 0 and b5 >= b3 and c5 <= c3)


def v5_bolumu():
    gel, s2, s4 = kumeler()
    if not (gel["v5"] or s2["v5"] or s4["v5"]):
        return []
    md = ["## v5: dönüş / yay güvenliği (durunca dönüş denetimi, körlemesine dönmeme, yay kaçınma)", "",
          "Geliştirme: MuJoCo geliştirme kümesi ve sınama2 (v4'ün iki çarpmasının tanısı sınama2 kayıtlarında yapıldı; "
          "bu yüzden sınama2 artık geliştirme sayılır). Sınama4 (13x13 / 17x17 t19..t23 x 2) bu aşamada üretildi; v5 "
          "kodu dondurulduktan sonra koşuldu, karar yalnız ona göre. v3 sınama4 koşuları v5 öncesi kod kopyasından, v4 "
          "sınama4 koşuları (yalnız karşılaştırma, karardan sonra) v4_kod kopyasından.", ""]
    md += tablo([("geliştirme", gel), ("sınama2 (görülmüş, tanı)", s2), ("**sınama4** (YENİ)", s4)])
    if s4.get("v5"):
        b3, b5, c3, c5, ok = karar(s4)
        md += ["", "**Karar kuralı** (sınama4): v5 başarısı v3'ten az değil (%d / %d) ve çarpma artmadı (%d / %d) -> %s" % (
            b3, b5, c3, c5, "sağlandı." if ok else "SAĞLANMADI.")]
        top = {sur: sum(int(_f(r.get("carpma_sayisi")) or 0) for D in (gel, s2, s4) for r in (D.get(sur) or []))
               for sur in ("v3", "v4", "v5")}
        n = {sur: sum(len(D.get(sur) or []) for D in (gel, s2, s4)) for sur in ("v3", "v4", "v5")}
        from .beyin import VARSAYILAN_SURUM
        md += ["", "Bu aşamada koşulan üç MuJoCo kümesinde (geliştirme + sınama2 + sınama4) çarpma olayı (koşu sayısı): "
               "v3 %d (%d), v4 %d (%d), v5 %d (%d). \"Çarpma sıfır\" hedefi bu üç kümede yalnız v3'te tutuyordu; bu yüzden "
               "o aşamada `VARSAYILAN_SURUM` v3'e döndü (sınama4 kuralı v5 için sağlansa da). v5 seçmeli: "
               "`surum_ayari(\"v5\")`." % (top["v3"], n["v3"], top["v4"], n["v4"], top["v5"], n["v5"]),
               "", "**Güncellendi (2026-11-26):** yukarıdaki \"v3'e döndü\" cümlesi o aşamanın kararıdır, güncel değil. v3 de "
               "çarpma sıfır değil: ilk girişte sınama3'te 1 ve sınama5'te 1 temas olayı, hafızalı zincirde 2 (v6 bölümü, "
               "\"v3 tabanı\"). Güncel varsayılan `VARSAYILAN_SURUM = \"%s\"`; dayanağı v6 bölümünde." % VARSAYILAN_SURUM]
    md += ["", "Çarpmalı ya da başarısız v5 koşuları:", "",
           "| küme | sahne | tohum | durum | süre | p_en | çarpma | temas (s) | son olaylar |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for kume, D in (("geliştirme", gel), ("sınama2", s2), ("sınama4", s4)):
        for r in sorted(D.get("v5") or [], key=_anahtar):
            if r.get("durum") != "basari" or (_f(r.get("carpma_sayisi")) or 0) > 0:
                md.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                    kume, r["sahne"], r["tohum"], r.get("durum"), r.get("sure_s"), r.get("p_en"),
                    r.get("carpma_sayisi"), r.get("carpma_suresi_s"), (r.get("olaylar") or "").replace("|", "/")[:120]))
    md.append("")
    return md


if __name__ == "__main__":
    print("\n".join(v5_bolumu()))
