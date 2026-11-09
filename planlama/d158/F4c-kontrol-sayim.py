# -*- coding: utf-8 -*-
"""F4c B (bagimsiz kontrol) sayimi. A'nin betiklerini (Y2b-baski.py, F4c-*.py) KULLANMAZ; yalniz okur, FreeCAD istemez.
Girdi: tasarim/freecad/<modul>/<modul>-analiz.json (baski), omuz/omuz-baski.json, montaj/robot-bom.csv, modul BOM'lari,
test/m7-kupon-sonuc.json, model kaynaklarindaki M5 isil gomme etiketleri, git (03.11 listesi fa49caa).
Cikti: planlama/d158/F4c-kontrol-sayim.json + ekrana ozet.     py -3 planlama/d158/F4c-kontrol-sayim.py
PETG-CF kumesi: modelde PETG-CF diyen parcalar (omuz, boyun adaptoru, VESA tasiyici) + 03.11 listesinin "(PETG-CF)" isaretli 11 turu.
"""
import csv, json, os, re, subprocess, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
KOK = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FC = os.path.join(KOK, "tasarim", "freecad")
TR = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")


def J(*p):
    return json.load(open(os.path.join(FC, *p), encoding="utf-8"))


def git(*a):
    return subprocess.run(["git", "-C", KOK] + list(a), capture_output=True).stdout.decode("utf-8")


def bom(yol):
    out = {}
    with open(yol, encoding="utf-8-sig") as f:
        for r in csv.reader(f, delimiter=";"):
            if r and r[0] in ("Baski", "Baglanti"):
                out[(r[0], r[1])] = int(r[3] if "dirsek-bom" in yol else r[2])   # dirsek-bom: 4. sutun iki kol
    return out


# 1 parca satirlari (analiz) ve BOM
rows = {}
for m in ("taban", "kabuk", "kafa", "dirsek"):
    for p in J(m, m + "-analiz.json")["baski"]:
        rows[(m, p["ad"])] = dict(adet=int(p.get("adet") or 1), g=[p["filament_g"]] * 2, sa=[p["sure_saat"]] * 2, kutle=p["kutle_g"],
                                  olcu=p["olcu"], desteksiz=p["desteksiz"], sigar=p.get("sigar"))
for p in J("omuz", "omuz-baski.json")["parcalar"]:
    fg, ss, y = p["filament_g"], p["sure_saat"], p["yonler"][p["secilen_yon"]]
    rows[("omuz", p["ad"])] = dict(adet=p["adet"], g=[fg["0.80"], fg.get("0.90", fg["0.80"])], sa=[ss["0.80"], ss.get("0.90", ss["0.80"])],
                                   kutle=p["model_kutle_g"], olcu=y["olcu"], desteksiz=p["desteksiz"], sigar=y.get("sigar"), malz=p.get("malzeme"))
RB = bom(os.path.join(FC, "montaj", "robot-bom.csv"))
rb_baski = {k[1]: v for k, v in RB.items() if k[0] == "Baski"}
adet_fark = []
for k, v in rows.items():
    if rb_baski.get(k[1]) != v["adet"]:
        adet_fark.append([k[0], k[1], v["adet"], rb_baski.get(k[1])])
        v["adet"] = rb_baski.get(k[1], v["adet"])        # BOM esas (dirsek analizi sag kol)
# kutle (BOM toplam / adet) ile analiz kutlesi: kafa analizi 05.11, BOM 09.11 guncel kaynaktan kurulur
bom_kutle = {}
with open(os.path.join(FC, "montaj", "robot-bom.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f, delimiter=";"):
        if r["Tur"] == "Baski":
            bom_kutle[r["Kalem"]] = float(r["Toplam kutle (g)"]) / int(r["Adet"])
kafa_kutle_fark = {k[1]: round(bom_kutle[k[1]] - v["kutle"], 2) for k, v in rows.items() if k[0] == "kafa"}

# 2 PETG-CF kumesi
eski = git("show", "fa49caa:planlama/baski-listesi.md")
cf_eski = {re.sub(r"\s+", " ", m.group(1)).strip().translate(TR).lower() for m in re.finditer(r"^\| ☐ \| \w+ \| (.+?) \*\*\(PETG-CF\)\*\*", eski, re.M)}
cf = {k for k, v in rows.items() if v.get("malz") == "PETG-CF" or k[1].lower() in cf_eski}
cf |= {("kafa", "Boyun yukseltme adaptoru"), ("kabuk", "Gogus ekrani VESA tasiyici")}   # modelde malzeme="PETG-CF" (kafa10_lib.py:569, kabuk_parcalar.py:375-376)

T = dict(tur=len(rows), adet=0, g=[0.0, 0.0], sa=[0.0, 0.0], petg_g=[0.0, 0.0], cf_g=[0.0, 0.0], cf_tur=0, cf_adet=0, destekli_adet=0)
for k, v in rows.items():
    T["adet"] += v["adet"]
    T["destekli_adet"] += 0 if v["desteksiz"] else v["adet"]
    if k in cf:
        T["cf_tur"] += 1
        T["cf_adet"] += v["adet"]
    for i in (0, 1):
        T["g"][i] += v["adet"] * v["g"][i]
        T["sa"][i] += v["adet"] * v["sa"][i]
        T["cf_g" if k in cf else "petg_g"][i] += v["adet"] * v["g"][i]
for x in ("g", "sa", "petg_g", "cf_g"):
    T[x] = [round(a, 2) for a in T[x]]
y_eski = json.loads(git("show", "fa49caa:planlama/y2/Y2b-baski.json"))
eski_k = {(s["modul"], s["ad"]) for s in y_eski["satirlar"]}
x2d_disi = [k[1] for k, v in rows.items() if not (v["sigar"] and v["olcu"][0] <= 246 and v["olcu"][1] <= 246 and v["olcu"][2] <= 250)]

# 3 isil gomme somun: BOM + kuponlar + M5'in hangi parcada oldugu (model etiketi)
ins = {s: RB.get(("Baglanti", "M%d isil gomme somun" % s), 0) for s in (3, 5)}
m7 = J("test", "m7-kupon-sonuc.json")["kupon_c_delikler"]
kupon_c = {s: sum(1 for d in m7 if d["boy"] == "M%d" % s) for s in (3, 5)}
kupon_b = {3: 4, 5: 3}            # tasarim/freecad/test/tolerans_kuponu.py:8-9 (M3 4 delik, M5 3 delik)
m5_yer = []
for yol, parca in (("dirsek/dirsek_parcalar.py", "On kol govdesi (PETG; g.cut, :235 -> I_ONKOL :242)"),
                   ("kafa/kafa7_parcalar.py", "Egme catali (PETG-CF listede; cb.cut :284)"),
                   ("omuz/omuz_parcalar.py", "Omuz gobegi (PETG-CF; hub.cut :149)")):
    for no, L in enumerate(open(os.path.join(FC, yol), encoding="utf-8"), 1):
        m = re.search(r'add\("(Isil gomme somun M5[^"]*)"', L)
        if m:
            m5_yer.append(dict(dosya=yol, satir=no, etiket=m.group(1), parca=parca))
gereken = dict(M3=ins[3] + 2 * (kupon_b[3] + kupon_c[3]), M5_yalniz_cf_kupon=ins[5] + kupon_b[5] + kupon_c[5],
               M5_iki_malzeme_kupon=ins[5] + 2 * (kupon_b[5] + kupon_c[5]))

out = dict(toplam=T, bom_baski_kalem=len(rb_baski), bom_baski_adet=sum(rb_baski.values()),
           analiz_bom_ad_esit=sorted(k[1] for k in rows) == sorted(rb_baski), adet_fark_analiz_bom=adet_fark,
           kafa_kutle_fark_bom_eksi_analiz_g=kafa_kutle_fark, cf_turleri=sorted(k[1] for k in cf),
           eski_0311=dict(adet=y_eski["toplam"]["adet"], g=y_eski["toplam"]["g"], sa=y_eski["toplam"]["sa"], cf_g=y_eski["toplam"]["cf_g"]),
           yeni_parcalar=sorted(k[1] for k in rows if k not in eski_k), kalkan=sorted(k[1] for k in eski_k if k not in rows), x2d_disi=x2d_disi,
           isil_gomme=dict(bom=ins, kupon_b=kupon_b, kupon_c=kupon_c, m5_yerleri=m5_yer, gereken=gereken))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "F4c-kontrol-sayim.json"), "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
print("tur %d, adet %d (BOM %d kalem / %d adet), g %s, sa %s, PETG %s, CF %s (%d tur, %d adet), destekli %d" % (
    T["tur"], T["adet"], len(rb_baski), sum(rb_baski.values()), T["g"], T["sa"], T["petg_g"], T["cf_g"], T["cf_tur"], T["cf_adet"], T["destekli_adet"]))
print("yeni:", out["yeni_parcalar"], "kalkan:", out["kalkan"], "X2D disi:", x2d_disi)
print("kafa kutle farki en buyuk:", max(abs(x) for x in kafa_kutle_fark.values()))
print("isil gomme:", out["isil_gomme"]["bom"], "gereken", gereken)
