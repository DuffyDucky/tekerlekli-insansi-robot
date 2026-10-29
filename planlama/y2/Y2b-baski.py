# -*- coding: utf-8 -*-
"""Y2b: 1,65 m baski listesi toplamlari ve tablo satirlari (planlama/baski-listesi.md icin). Yalniz okur.
Kaynak: <modul>-analiz.json 'baski' (taban, kabuk, kafa, dirsek; %80 doluluk) + omuz/omuz-baski.json (M4, PETG-CF 0,8 / 0,9;
29 Ekim 2026'da 1650 omuz FCStd'sinden yeniden kosuldu). Dirsek analizi sag kol: 4 parca x 2.
PETG-CF: tasarim karari (baski-listesi.md) 10 tur; Y2a'da eklenen boyun yukseltme adaptoru CAD'de PETG (kafa10_lib).
Cikti: Y2b-baski.json + ekrana markdown satirlari.   py -3 planlama/y2/Y2b-baski.py
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.normpath(os.path.join(HERE, "..", "..", "tasarim", "freecad"))
CF = {"Omuz yuvasi", "Rulman kapagi", "Omuz gobegi", "Kol catali", "Dirsek catali", "Bilek flansi",
      "Servo yuvasi", "Rulman yuvasi", "Boyun mili", "Egme catali"}
ADET2 = {"Dirsek catali", "On kol govdesi", "Bilek flansi", "El"}
DESTEK_NOT = {"Yuz kabugu (on) sag": "**destekli** (dikiş dili: 16 mm şerit, ~1,25 mm konsol; karar 29.10)",
              "Arka kafa kabugu sag": "**destekli** (dikiş dili: 16 mm şerit, ~1,25 mm konsol; karar 29.10)"}


def parti(mod, ad):
    if mod == "taban" and ad.startswith("Sonar"): return 1
    if mod == "taban": return 4
    if mod == "kabuk" and (ad.startswith("Etek")): return 4
    if mod == "kabuk" and ad.startswith("S1 kaset"): return 2
    if mod == "kabuk": return 1
    if mod == "omuz" and ad in ("Rulman kapagi", "Ust kol tupu"): return 1
    if mod in ("omuz", "dirsek"): return 2
    if mod == "kafa" and ad in ("Servo yuvasi", "Rulman yuvasi", "Boyun mili", "Egme catali", "Boyun yukseltme adaptoru"): return 2
    return 3   # kafa kabugu, iskelet, ekran tirnaklari: 10,1" ekran gelince


satir = []
for mod in ("taban", "kabuk", "kafa", "dirsek"):
    with open(os.path.join(FC, mod, mod + "-analiz.json"), encoding="utf-8") as f:
        for p in json.load(f)["baski"]:
            n = 2 if (mod == "dirsek" and p["ad"] in ADET2) else int(p.get("adet") or 1)
            satir.append(dict(modul=mod, ad=p["ad"], adet=n, olcu=p.get("olcu"), g=(p["filament_g"], p["filament_g"]),
                              sa=(p["sure_saat"], p["sure_saat"]), desteksiz=p.get("desteksiz"), yon=p.get("yon")))
with open(os.path.join(FC, "omuz", "omuz-baski.json"), encoding="utf-8") as f:
    ob = json.load(f)
olcu_om = {p["ad"]: p["olcu"] for p in json.load(open(os.path.join(FC, "omuz", "omuz-analiz.json"), encoding="utf-8"))["baski"]}
for p in ob["parcalar"]:
    fg, ss = p["filament_g"], p["sure_saat"]
    satir.append(dict(modul="omuz", ad=p["ad"], adet=p["adet"], olcu=olcu_om.get(p["ad"]), g=(fg["0.80"], fg.get("0.90", fg["0.80"])),
                      sa=(ss["0.80"], ss.get("0.90", ss["0.80"])), desteksiz=p["desteksiz"], yon=p.get("yon")))
top = {"adet": 0, "g": [0, 0], "sa": [0, 0], "cf_g": [0, 0], "petg_g": [0, 0], "parti": {}}
for s in satir:
    s["cf"] = s["ad"] in CF
    s["parti"] = parti(s["modul"], s["ad"])
    t = top["parti"].setdefault(s["parti"], {"adet": 0, "g": [0, 0], "sa": [0, 0]})
    top["adet"] += s["adet"]; t["adet"] += s["adet"]
    for i in (0, 1):
        g = s["adet"] * s["g"][i]
        top["g"][i] += g; t["g"][i] += g
        top["sa"][i] += s["adet"] * s["sa"][i]; t["sa"][i] += s["adet"] * s["sa"][i]
        top["cf_g" if s["cf"] else "petg_g"][i] += g
top["destekli"] = [(s["modul"], s["ad"], s["adet"]) for s in satir if not s["desteksiz"]]
top["omuz_baski_tarih"] = ob["tarih"]


def f(x, n=0):
    return ("%%.%df" % n % x).replace(".", ",")


def aralik(v, n=0):
    return f(v[0], n) if abs(v[0] - v[1]) < 1e-9 else "%s–%s" % (f(v[0], n), f(v[1], n))


for k in sorted(top["parti"]):
    print("\n## Parti %d: %d adet, %s kg, %s sa" % (k, top["parti"][k]["adet"], aralik([x / 1000 for x in top["parti"][k]["g"]], 2),
                                                    aralik(top["parti"][k]["sa"], 0)))
    for s in [s for s in satir if s["parti"] == k]:
        o = " × ".join(f(x, 0) for x in s["olcu"]) if s["olcu"] else "—"
        print("| ☐ | %s | %s%s | %d | %s | %s | %s | %s%s |" % (
            s["modul"], s["ad"], " **(PETG-CF)**" if s["cf"] else "", s["adet"], o, aralik(s["g"]), aralik(s["sa"], 2),
            s["yon"] or "", "" if s["desteksiz"] else ", " + DESTEK_NOT.get(s["ad"], "**destekli**")))
print("\nTOPLAM adet %d, filament %.0f-%.0f g (PETG %.0f-%.0f, CF %.0f-%.0f), sure %.1f-%.1f sa" % (
    top["adet"], *top["g"], *top["petg_g"], *top["cf_g"], *top["sa"]))
print("destekli:", top["destekli"])
with open(os.path.join(HERE, "Y2b-baski.json"), "w", encoding="utf-8") as fo:
    json.dump({"satirlar": satir, "toplam": top}, fo, ensure_ascii=False, indent=1)
