# P10.8e kare önizlemesi (FreeCAD'siz; P108b § 5 yöntemi): rehber/ klasörünün geçici kopyasında veriye aday görünüm alanları yazılır,
# headless Chrome kareyi çeker. Depodaki rehber/ ve planlama/rehber/goruntu/ DEĞİŞMEZ; kopya sistemin geçici klasöründe.
# Adaylar (ADAY): ad -> [(adım kodu, alt adım no, {alan: değer})]; alan "odak_desen" parça görünen adı desenleri (rehber_veri kuralı:
# a <= adım), "sema_on" {desen: (y üst, not)} (rehber_veri kuralı), "kamera" olduğu gibi. Çıktı: P108e-olcum/onizleme/<ad>-<adım>.png
# Koşu (depo kökünden): py -3 -B -X utf8 planlama/d158/P108e-onizleme.py [aday ...]
import os, sys, json, shutil, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROBOT, "tasarim", "freecad", "rehber"))
import rehber_uret as RU  # noqa: E402

TABAN_ODAK = ("Servo dağıtım kartı A", "Servo dağıtım kartı B", "XL4016 servo 6 V A", "XL4016 servo 6 V B",
              "Bara tutucusu anahtarlı")
ADAY = {
    "simdiki": [("K2", 1, {}), ("K1", 11, {})],
    "k1_11": [("K1", 11, {"sema_on": {"(U06)": (300.0, "yalnız taban bölümü (direk dibinden ESP32'ye); tamamı K2 madde 4'ün karesinde")},
                          "odak_desen": ("ESP32 taşıyıcı kart", "PCA9685 servo sürücü", "XL4016 servo 6 V C", "Dağıtım kartı C")})],
    "k2_1_arka_taban": [("K2", 1, {"odak_desen": TABAN_ODAK})],
    "k2_1_arkaust_taban": [("K2", 1, {"kamera": [0.35, 1.0, -0.8], "odak_desen": TABAN_ODAK})],
    "k2_1_arkaust_tum": [("K2", 1, {"kamera": [0.35, 0.6, -1.0]})],
    "k2_1_arka_dik": [("K2", 1, {"kamera": [0.0, 1.0, -0.7], "odak_desen": TABAN_ODAK})],
    "k2_1_arka_yuksek": [("K2", 1, {"kamera": [0.08, 1.4, -0.6], "odak_desen": TABAN_ODAK})],
}


def uygula(V, kod, j, alan):
    a = next(x for x in V["adimlar"] if x["kod"] == kod)
    g = a["sira_grup"][j - 1]
    for k, v in alan.items():
        if k == "odak_desen":
            g["odak"] = [p["id"] for p in V["parcalar"] if p["a"] <= a["i"] and any(d in p["ad"] for d in v)]
            bos = [d for d in v if not any(d in p["ad"] for p in V["parcalar"] if p["a"] <= a["i"])]
            if bos:
                print("  UYARI odak deseni boş:", bos)
        elif k == "sema_on":
            g["sema_on"] = []
            for desen, (ymax, not_) in v.items():
                ks = [i for i, s in enumerate(V["semalar"]) if desen in s["ad"]]
                s = V["semalar"][ks[0]]
                g["sema_on"].append(dict(i=ks[0], pts=[q for q in s["pts"] if q[1] <= ymax], not_=not_, y_ust=ymax))
        else:
            g[k] = v
    return a["i"]


def main(adlar):
    tb = RU.tarayici()
    cikti = os.path.join(HERE, "P108e-olcum", "onizleme")
    os.makedirs(cikti, exist_ok=True)
    for ad in adlar:
        kok = os.path.join(tempfile.gettempdir(), "p108e-onizleme-" + ad)
        if os.path.isdir(kok):
            shutil.rmtree(kok)
        shutil.copytree(os.path.join(ROBOT, "rehber"), kok, ignore=shutil.ignore_patterns("goruntu"))
        V = json.load(open(os.path.join(kok, "veri", "rehber-veri.json"), encoding="utf-8"))
        adres = []
        for kod, j, alan in ADAY[ad]:
            adres.append("%d.%d" % (uygula(V, kod, j, alan), j))
        open(os.path.join(kok, "veri", "rehber-veri.js"), "w", encoding="utf-8").write(
            "window.REHBER_VERI=" + json.dumps(V, ensure_ascii=False, separators=(",", ":")) + ";\n")
        ortak = RU.ortak_arg(tb, (1400, 900))
        for a in adres:
            png = os.path.join(cikti, "%s-%s.png" % (ad, a.replace(".", "-")))
            subprocess.run(ortak + ["--screenshot=" + png, RU.url(a, "&sahne=1&tema=light", kok=kok)], capture_output=True)
            print(ad, a, os.path.relpath(png, ROBOT), os.path.getsize(png) if os.path.exists(png) else "YOK")
        shutil.rmtree(kok, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1:] or list(ADAY))
