# P10.8f kare önizlemesi (FreeCAD'siz; P108e-onizleme.py kalıbı): rehber/ klasörünün geçici kopyasında (sistemin geçici klasörü)
# 1) rehber_gorunum.isle() kopyanın verisine koşar (çalışma ağacındaki rehber_metin / rehber_gorunum kaynağıyla; --veri-yok üretiminin
#    görünüm adımı), 2) isteğe bağlı aday alanlar yazılır, 3) headless Chrome kareyi iki kipte çeker: yazdırma karesi (?sahne=1,
#    1200 x 720) ve etkileşimli (1400 x 900). Depodaki rehber/ ve planlama/rehber/ DEĞİŞMEZ.
# Adaylar (ADAY): ad -> [(adım kodu, alt adım no (0 = alt adımı yok), {alan: değer})]; alan "odak_desen" / "saydam_desen" /
# "kenar_desen" parça görünen adı desenleri (rehber_veri kuralı: a <= adım), "sil" alan listesi, öbürleri olduğu gibi.
# Çekim kipi (cekim=1) rehber_uret ve F10d ile aynı (ilk koşular cekim=1 olmadan alındı; P108f-gunluk.md § 7).
# Çıktı: P108f-olcum/onizleme/<ad>-<adres>-{sahne,etk}.png (+ -etiket.json: RehberTest.ucEtiket / etiket dökümü, --dom ile)
# Koşu (depo kökünden): py -3 -B -X utf8 planlama/d158/P108f-onizleme.py [--kopya-kalsin] [aday ...]
import os, sys, json, shutil, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROBOT, "tasarim", "freecad", "rehber"))
import rehber_uret as RU  # noqa: E402
import rehber_gorunum as RG  # noqa: E402

KAT = ("Elektronik katı",)
ADAY = {
    "simdiki": [("K1", 4, {}), ("K1", 10, {}), ("B5a", 0, {})],   # ilk koşu: kaynak değişmeden önce (bugünkü kare)
    "kaynak": [("K1", 4, {}), ("K1", 10, {}), ("B5a", 0, {})],    # çalışma ağacındaki kaynakla (aday alan yok)
    "k1_10_kenar": [("K1", 10, {"kenar_desen": KAT})],
    "k1_10_opak_kenar": [("K1", 10, {"kenar_desen": KAT, "sil": ["saydam"]})],
    "k1_10_on_alcak": [("K1", 10, {"kenar_desen": KAT, "kamera": [0.0, 0.55, 1.0]})],
    "k1_10_on_orta": [("K1", 10, {"kenar_desen": KAT, "kamera": [0.0, 0.8, 1.0]})],
}


def kod_i(V, kod):
    return next(x for x in V["adimlar"] if x["kod"] == kod)


def uygula(V, kod, j, alan):
    a = kod_i(V, kod)
    g = a["sira_grup"][j - 1] if j else a
    for k, v in alan.items():
        if k.endswith("_desen"):
            hedef = k[:-6]
            g[hedef] = [p["id"] for p in V["parcalar"] if p["a"] <= a["i"] and any(d in p["ad"] for d in v)]
            if not g[hedef]:
                print("  UYARI %s deseni boş: %s" % (hedef, v))
        elif k == "sil":
            for x in v:
                g.pop(x, None)
        else:
            g[k] = v
    return "%d.%d" % (a["i"], j) if j else str(a["i"])


def kopya_kur(ad):
    kok = os.path.join(tempfile.gettempdir(), "p108f-onizleme-" + ad)
    if os.path.isdir(kok):
        shutil.rmtree(kok)
    shutil.copytree(os.path.join(ROBOT, "rehber"), kok, ignore=shutil.ignore_patterns("goruntu"))
    RG.VERI_DIR = os.path.join(kok, "veri")            # görünüm adımı kopyanın verisine (depodaki rehber/veri değişmez)
    RG.isle(sessiz=True)
    return kok


def main(arg):
    kalsin = "--kopya-kalsin" in arg
    adlar = [a for a in arg if not a.startswith("--")] or list(ADAY)
    tb = RU.tarayici()
    cikti = os.path.join(HERE, "P108f-olcum", "onizleme")
    os.makedirs(cikti, exist_ok=True)
    for ad in adlar:
        kok = kopya_kur(ad)
        V = json.load(open(os.path.join(kok, "veri", "rehber-veri.json"), encoding="utf-8"))
        adres = [uygula(V, kod, j, alan) for kod, j, alan in ADAY[ad]]
        open(os.path.join(kok, "veri", "rehber-veri.js"), "w", encoding="utf-8").write(
            "window.REHBER_VERI=" + json.dumps(V, ensure_ascii=False, separators=(",", ":")) + ";\n")
        json.dump(V, open(os.path.join(kok, "veri", "rehber-veri.json"), "w", encoding="utf-8"), ensure_ascii=False)
        for a in adres:
            for kip, boyut, ek in (("sahne", (1200, 720), "&cekim=1&sahne=1&tema=light"), ("etk", (1400, 900), "&cekim=1&tema=light")):
                png = os.path.join(cikti, "%s-%s-%s.png" % (ad, a.replace(".", "-"), kip))
                subprocess.run(RU.ortak_arg(tb, boyut) + ["--screenshot=" + png, RU.url(a, ek, kok=kok)], capture_output=True)
                print(ad, a, kip, os.path.relpath(png, ROBOT), os.path.getsize(png) if os.path.exists(png) else "YOK")
        if kalsin:
            print("kopya:", kok)
        else:
            shutil.rmtree(kok, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1:])
