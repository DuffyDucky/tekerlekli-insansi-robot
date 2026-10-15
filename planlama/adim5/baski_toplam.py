# -*- coding: utf-8 -*-
"""5. adim (D6/B1): baski listesi toplamlari, modul analizlerinden. Yalniz okur.
Omuz: omuz/omuz-baski.json (M4, doluluk 0,8 / 0,9). Digerleri <modul>-analiz.json 'baski' (%80).
PETG-CF parcalari: baski-listesi.md'deki 10 tur (omuz yuva/kapak/gobek/catal, dirsek catal/flans, kafa 4 parca).
  py -3 planlama/adim5/baski_toplam.py
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.normpath(os.path.join(HERE, "..", "..", "tasarim", "freecad"))
CF = {"Omuz yuvasi", "Rulman kapagi", "Omuz gobegi", "Kol catali", "Dirsek catali", "Bilek flansi",
      "Servo yuvasi", "Rulman yuvasi", "Boyun mili", "Egme catali"}
ADET2 = {"Dirsek catali", "On kol govdesi", "Bilek flansi", "El"}  # dirsek analizi sag kol
satir = []
for mod in ("taban", "kabuk", "kafa", "dirsek"):
    with open(os.path.join(FC, mod, mod + "-analiz.json"), encoding="utf-8") as f:
        for p in json.load(f)["baski"]:
            n = 2 if (mod == "dirsek" and p["ad"] in ADET2) else int(p.get("adet") or 1)
            satir.append(dict(modul=mod, ad=p["ad"], adet=n, g=(p["filament_g"], p["filament_g"]),
                              sa=(p["sure_saat"], p["sure_saat"]), desteksiz=p.get("desteksiz"), yon=p.get("yon")))
with open(os.path.join(FC, "omuz", "omuz-baski.json"), encoding="utf-8") as f:
    for p in json.load(f)["parcalar"]:
        fg, ss = p["filament_g"], p["sure_saat"]
        satir.append(dict(modul="omuz", ad=p["ad"], adet=p["adet"], g=(fg["0.80"], fg.get("0.90", fg["0.80"])),
                          sa=(ss["0.80"], ss.get("0.90", ss["0.80"])), desteksiz=p["desteksiz"], yon=p.get("yon")))
top = {"adet": 0, "g": [0, 0], "sa": [0, 0], "cf_g": [0, 0], "petg_g": [0, 0]}
for s in satir:
    s["cf"] = s["ad"] in CF
    top["adet"] += s["adet"]
    for i in (0, 1):
        g = s["adet"] * s["g"][i]
        top["g"][i] += g
        top["sa"][i] += s["adet"] * s["sa"][i]
        top["cf_g" if s["cf"] else "petg_g"][i] += g
for s in satir:
    print("%-7s %-24s %d  %6.1f-%6.1f g  %4.2f-%4.2f sa  %s %s" % (s["modul"], s["ad"], s["adet"], s["g"][0], s["g"][1],
          s["sa"][0], s["sa"][1], "CF" if s["cf"] else "  ", "" if s["desteksiz"] else "DESTEKLI"))
print("TOPLAM adet %d, filament %.0f-%.0f g (PETG %.0f-%.0f, CF %.0f-%.0f), sure %.1f-%.1f sa" % (
    top["adet"], *top["g"], *top["petg_g"], *top["cf_g"], *top["sa"]))
with open(os.path.join(HERE, "baski_toplam.json"), "w", encoding="utf-8") as f:
    json.dump({"satirlar": satir, "toplam": top}, f, ensure_ascii=False, indent=1)
