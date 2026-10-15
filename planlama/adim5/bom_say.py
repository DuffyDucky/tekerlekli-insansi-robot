# -*- coding: utf-8 -*-
"""5. adim (B1/B2): CAD BOM toplami. Yalniz okur; tasarim/freecad altina yazmaz.
Toplam = iskelet + taban + kabuk + kafa + 2 x omuz (travers sigmasi haric, iskelette var) + dirsek (iki kol sutunu).
Cikti: planlama/adim5/bom_toplam.json ve ekrana tablo.
  py -3 planlama/adim5/bom_say.py
"""
import csv, json, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.normpath(os.path.join(HERE, "..", "..", "tasarim", "freecad"))


def oku_csv(yol, sutun):
    with open(yol, encoding="utf-8-sig") as f:
        r = csv.reader(f, delimiter=";")
        bas = next(r)
        i = bas.index(sutun)
        return [(row[0], row[1], float(row[i])) for row in r if row]


kaynak = {
    "iskelet": oku_csv(os.path.join(FC, "iskelet", "iskelet-bom.csv"), "Adet"),
    "taban": oku_csv(os.path.join(FC, "taban", "taban-bom.csv"), "Adet"),
    "kabuk": oku_csv(os.path.join(FC, "kabuk", "kabuk-bom.csv"), "Adet"),
    "kafa": oku_csv(os.path.join(FC, "kafa", "kafa-bom.csv"), "Adet"),
    "dirsek (iki kol)": oku_csv(os.path.join(FC, "dirsek", "dirsek-bom.csv"), "Adet (iki kol)"),
}
with open(os.path.join(FC, "omuz", "omuz-analiz.json"), encoding="utf-8") as f:
    om = json.load(f)["bom"]
kaynak["omuz (x2, travers haric)"] = [(t, k, 2.0 * a) for t, k, a in om if "Sigma" not in k]


def anahtar(k):
    k = k.replace("cekic somun (kanal 10)", "cekic somun, kanal 10")
    k = re.sub(r"\s*\(tahmini olcu\)", "", k)
    return k


top = collections.OrderedDict()
detay = collections.defaultdict(dict)
for mod, satirlar in kaynak.items():
    for t, k, a in satirlar:
        kk = (t, anahtar(k))
        top[kk] = top.get(kk, 0) + a
        detay["%s|%s" % kk][mod] = a

out = [{"tur": t, "kalem": k, "adet": round(a, 1), "modul": detay["%s|%s" % (t, k)]}
       for (t, k), a in sorted(top.items(), key=lambda x: (x[0][0], x[0][1]))]

# Ozet gruplari (B1/B2 icin)
def topla(f):
    return sum(o["adet"] for o in out if f(o))
ozet = {
    "M2,5 DIN 912": topla(lambda o: o["kalem"].startswith("M2,5x") and "DIN 912" in o["kalem"]),
    "M3 DIN 912": topla(lambda o: re.match(r"M3x\d+ DIN 912", o["kalem"])),
    "M3 ISO 7380": topla(lambda o: re.match(r"M3x\d+ ISO 7380", o["kalem"])),
    "M4 DIN 912": topla(lambda o: re.match(r"M4x\d+ DIN 912", o["kalem"])),
    "M5 DIN 912": topla(lambda o: re.match(r"M5x\d+ DIN 912", o["kalem"])),
    "M5 DIN 913": topla(lambda o: re.match(r"M5x\d+ DIN 913", o["kalem"])),
    "M6 DIN 912": topla(lambda o: re.match(r"M6x\d+ DIN 912", o["kalem"])),
    "M6 DIN 913": topla(lambda o: re.match(r"M6x\d+ DIN 913", o["kalem"])),
    "M6 ISO 7380": topla(lambda o: re.match(r"M6x\d+ ISO 7380", o["kalem"])),
    "M3 isil gomme": topla(lambda o: o["kalem"] == "M3 isil gomme somun"),
    "M5 isil gomme": topla(lambda o: o["kalem"] == "M5 isil gomme somun"),
    "M3 DIN 985": topla(lambda o: o["kalem"].startswith("M3 DIN 985")),
    "M4 DIN 985": topla(lambda o: o["kalem"].startswith("M4 DIN 985")),
    "M3 pul": topla(lambda o: o["kalem"] == "M3 DIN 125 pul"),
    "M4 pul": topla(lambda o: o["kalem"] == "M4 DIN 125 pul"),
    "M5 pul": topla(lambda o: o["kalem"] == "M5 DIN 125 pul"),
    "M6 pul": topla(lambda o: o["kalem"] == "M6 DIN 125 pul"),
    "M6 cekic somun": topla(lambda o: o["kalem"].startswith("M6 cekic")),
    "M5 cekic somun": topla(lambda o: o["kalem"].startswith("M5 cekic")),
    "M4 cekic somun": topla(lambda o: o["kalem"].startswith("M4 cekic")),
    "horn vidasi (servo ile)": topla(lambda o: "horn vidasi" in o["kalem"]),
}
# boy dagilimi
boy = collections.defaultdict(dict)
for o in out:
    m = re.match(r"(M[\d,]+)x(\d+) (DIN 912|ISO 7380|DIN 913)", o["kalem"])
    if m:
        boy["%s %s" % (m.group(1), m.group(3))][m.group(2)] = o["adet"]

res = {"kaynak": "tasarim/freecad/*/*-bom.csv + omuz-analiz.json bom (x2, travers sigmasi haric)",
       "dosya_saati": {m: os.path.getmtime(p) for m, p in {
           "iskelet": os.path.join(FC, "iskelet", "iskelet-bom.csv"),
           "taban": os.path.join(FC, "taban", "taban-bom.csv"),
           "kabuk": os.path.join(FC, "kabuk", "kabuk-bom.csv"),
           "kafa": os.path.join(FC, "kafa", "kafa-bom.csv"),
           "dirsek": os.path.join(FC, "dirsek", "dirsek-bom.csv"),
           "omuz": os.path.join(FC, "omuz", "omuz-analiz.json")}.items()},
       "ozet": ozet, "boy": boy, "kalemler": out}
with open(os.path.join(HERE, "bom_toplam.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
for k, v in ozet.items():
    print("%-26s %5g" % (k, v))
for k, v in sorted(boy.items()):
    print("%-14s %s" % (k, ", ".join("%sx%g" % (b, a) for b, a in sorted(v.items(), key=lambda x: int(x[0])))))
print("--- satin / imalat / lazer ---")
for o in out:
    if o["tur"] != "Baglanti" and o["tur"] != "Baski":
        print("%-8s %-75s %g" % (o["tur"], o["kalem"], o["adet"]))
