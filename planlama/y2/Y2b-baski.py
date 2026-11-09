# -*- coding: utf-8 -*-
"""Y2b: 1,58 m baski listesi toplamlari ve tablo satirlari (planlama/baski-listesi.md icin). Yalniz okur.
F6b (P6.2, 09.11.2026): TEK kaynak tasarim/freecad/lale158/baski-analiz.json (baski_analiz_ortak.py; butun modullerin baski parcalari
ayni yontemle: 45 derece, tasarim yonu, destek filamenti dahil). Eskiden <modul>-analiz.json 'baski' + omuz/omuz-baski.json okunuyordu.
g ve sa alt/ust: doluluk araligi (omuz PETG-CF 0,8 / 0,9; digerleri tek deger). Dirsek analizi sag kol: 4 parca x 2, omuz 6 parca x 2.
PETG-CF: tasarim karari (baski-listesi.md) 12 tur; boyun yukseltme adaptoru PETG -> PETG-CF (Ahmet karari 29 Ekim 2026; kafa10_lib).
Cikti: Y2b-baski.json + ekrana markdown satirlari.   py -3 planlama/y2/Y2b-baski.py
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.normpath(os.path.join(HERE, "..", "..", "tasarim", "freecad"))
CF = {"Omuz yuvasi", "Rulman kapagi", "Omuz gobegi", "Kol catali", "Dirsek catali", "Bilek flansi",
      "Servo yuvasi", "Rulman yuvasi", "Boyun mili", "Egme catali", "Boyun yukseltme adaptoru", "Gogus ekrani VESA tasiyici"}
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
    return 3   # kafa kabugu, iskelet: 7" ekran gelince (03.11.2026; tirnak kalkti)


BA = os.path.join(FC, "lale158", "baski-analiz.json")
with open(BA, encoding="utf-8") as f:
    ba = json.load(f)
satir = []
for i, p in enumerate(ba["parcalar"]):
    satir.append(dict(modul=p["modul"], ad=p["ad"], adet=p["adet"], olcu=p["olcu"], g=tuple(p["toplam_g"]), sa=tuple(p["sure_sa"]),
                      desteksiz=p["desteksiz"], yon=p["yon"], destek_g=tuple(p["destek_g"]), destek_alan_mm2=p["destek_alan_mm2"],
                      x2d=p["x2d_sigar"], kaynak="baski-analiz/parcalar[%d]" % i))
top = {"adet": 0, "g": [0, 0], "sa": [0, 0], "cf_g": [0, 0], "petg_g": [0, 0], "destek_g": [0, 0], "parti": {}}
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
        top["destek_g"][i] += s["adet"] * s["destek_g"][i]
top["destekli"] = [(s["modul"], s["ad"], s["adet"]) for s in satir if not s["desteksiz"]]
top["kaynak"] = dict(dosya="tasarim/freecad/lale158/baski-analiz.json", tarih=ba["tarih"], betik=ba["betik"])


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
print("\nTOPLAM adet %d, filament %.0f-%.0f g (PETG %.0f-%.0f, CF %.0f-%.0f; destek %.0f-%.0f), sure %.1f-%.1f sa" % (
    top["adet"], *top["g"], *top["petg_g"], *top["cf_g"], *top["destek_g"], *top["sa"]))
print("destekli:", top["destekli"])
with open(os.path.join(HERE, "Y2b-baski.json"), "w", encoding="utf-8") as fo:
    json.dump({"satirlar": satir, "toplam": top}, fo, ensure_ascii=False, indent=1)
