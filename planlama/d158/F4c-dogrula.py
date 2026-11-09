# -*- coding: utf-8 -*-
r"""F4c (P4.3 + P8.2) dogrulama. Yalniz okur; kaynak betikleri DEGISTIRMEZ (kopyalarini bellekte, gecici dosyayla kosar). FreeCAD istemez.
  1. Y2b yeniden uretimi: planlama/y2/Y2b-baski.py gecici cikti yoluyla kosulur, sonuc depodaki Y2b-baski.json ile ayni mi.
  2. BOM: tasarim/freecad/montaj/robot-bom.csv "Baski" satirlari (ad, adet) = Y2b satirlari.
  3. baski-listesi.md parca satirlari: her satir tek bir Y2b satirina bagli (modul + ad), adet / olcu / g / sa / malzeme / destek / X2D /
     kaynak anahtari / parti JSON ile ayni; her Y2b satiri tam bir kez.
  4. Ozet tablosu ve F4c-partiler.json: parti toplamlari = Y2b toplam.parti, Parti 1-4 toplami = Y2b toplam (adet, g, sa, PETG, PETG-CF).
  5. tasarim/freecad/lale158/baski_listesi_guncelle.py (a) oldugu gibi, (b) F4c-gunluk.md'deki onerilen yamayla (YAMA) gecici kopya uzerinde
     kosulur; (b)'nin ciktisi baski-listesi.md ile satir satir ayni olmali (sabit nokta), (a)'nin farki listelenir.
Kullanim:  py -3 planlama/d158/F4c-dogrula.py      (cikis 0 = hepsi gecti)
"""
import contextlib, csv, difflib, io, json, os, re, sys, tempfile, unicodedata
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.normpath(os.path.join(HERE, "..", ".."))
MD = os.path.join(KOK, "planlama", "baski-listesi.md")
Y2B_PY = os.path.join(KOK, "planlama", "y2", "Y2b-baski.py")
Y2B = os.path.join(KOK, "planlama", "y2", "Y2b-baski.json")
GUNC = os.path.join(KOK, "tasarim", "freecad", "lale158", "baski_listesi_guncelle.py")
BOM = os.path.join(KOK, "tasarim", "freecad", "montaj", "robot-bom.csv")
PARTI = os.path.join(HERE, "F4c-partiler.json")
FC = os.path.join(KOK, "tasarim", "freecad")
TR = str.maketrans("ığüşöçİĞÜŞÖÇ", "igusocIGUSOC")

# baski_listesi_guncelle.py icin onerilen yama (F4c-gunluk.md "Betik yamasi"); (eski, yeni) kaynak metni, her eski tam bir kez gecmeli
YAMA = [
    # Y1 kat(): betigin kendi yazdigi "(gomulu 11,6" cep)" ekini de at (yoksa ikinci kosuda gogus bantlari "yeni" sayiliyor)
    (r'''.replace(" (Nextion yok, kapalı)", "")''', r'''.replace(" (Nextion yok, kapalı)", "").replace(" (gömülü 11,6\" cep)", "")'''),
    # Y2 10,1" -> 7" metin cevirileri (03.11 oncesi icin yazilmis; QLED'de ters yone yanlis)
    (r'''    r = m.group(7).replace('**10,1" ekran + kamera delikleri**', '7" ekran kulak delikleri (04) + kamera delikleri').replace('**10,1" ekran ölçüsü**', '7" ekran ölçüsü').replace('10,1" ekran ölçüsü', '7" ekran ölçüsü')''',
     r'''    r = m.group(7)'''),
    # Y3 ust bolum metni (tarih, QLED, satiri olmayan parca yoksa bos tablo yazma)
    (r'''"## 158 cm güncellemesi (03.11.2026)"''', r'''"## 158 cm güncellemesi (09.11.2026)"'''),
    (r'''"Boy 1,58 m, göğüste 11,6\" gömülü ekran, kafada 7\" ekran. Kabuk ve kafa satırları `*-analiz.json`'dan güncellendi; dosyadaki eski açıklamalar (1,65 m, 10,1\") yalnız tarihsel. "''',
     r'''"Boy 1,58 m, göğüste 11,6\" gömülü ekran, kafada 10,1\" QLED. Kabuk ve kafa satırları bu betikle `Y2b-baski.json`'dan; öteki satırlar ve ek sütunlar F4c'de (denetim `planlama/d158/F4c-dogrula.py`). "'''),
    (r'''; giriş ve renk metinleri 1,65 m tarihli."''', r'''."'''),
    (r'''"Ekran tutucu tırnaklar kalktı. Değişen baskılar: göğüs bandı, orta bant, omuz bandı (basamak), uzatma bantları (157,5), üst arka kapak, kafa kabukları (ekran yuvası), kafa iskeleti, boyun mili ve servo yuvası (kablo penceresi), boyun adaptörü (62,8). Aşağıdaki tablolarda satırı olmayan parçalar:", "",''',
     r'''"Parti tablolarında satırı olmayan kabuk / kafa parçası:", "",'''),
    (r'''       "| Parça | Adet | Ölçü (mm) | Filament (g) | Süre (sa) | Yön | Destek |", "|---|---|---|---|---|---|---|"]''',
     r'''       ] + (["| Parça | Adet | Ölçü (mm) | Filament (g) | Süre (sa) | Yön | Destek |", "|---|---|---|---|---|---|---|"] if yeni else ["yok."])'''),
    # Y4 Parti 3 etiketi
    (r'''3: "| 3 | 7\" yüz ekranı gelip ölçülünce |"''', r'''3: "| 3 | 10,1\" QLED yüz ekranı gelip ölçülünce |"'''),
    # Y5 aralik: yuvarlanmis iki uc ayniysa tek deger ("69–69 sa" yazmasin)
    (r'''    return f(v[0] / b, n) if abs(v[0] - v[1]) < 1e-9 else''', r'''    return f(v[0] / b, n) if f(v[0] / b, n) == f(v[1] / b, n) else'''),
    # Y6 baslik tarihi
    (r'''        cikti[k_] = "# Baskı listesi (1,58 m ana tasarım; 03.11.2026)"''', r'''        cikti[k_] = "# Baskı listesi (1,58 m ana tasarım; 09.11.2026)"'''),
    # Y7 Parti 3 basligini 7"'ye cevirme
    (r'''        cikti[k_] = L.replace('10,1" yüz ekranı', '7" yüz ekranı')''', r'''        cikti[k_] = L'''),
]


def kat(s):
    s = re.sub(r"\*\*.*?\*\*", "", s).translate(TR)
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKD", s)).strip().lower()


def f(x, n=0):
    return ("%.*f" % (n, x)).replace(".", ",")


def aralik(v, n=0):
    a, c = f(v[0], n), f(v[1], n)
    return a if a == c else "%s–%s" % (a, c)


def kos(yol, kaynak, degis, glob_ek=None):
    """Betik kaynagini bellekte degistirip kosar; stdout'u yutar."""
    for a, b in degis:
        n = kaynak.count(a)
        if n != 1:
            raise SystemExit("yama/yonlendirme metni %d kez bulundu (1 olmali): %r" % (n, a[:80]))
        kaynak = kaynak.replace(a, b)
    g = {"__file__": yol, "__name__": "__f4c__"}
    g.update(glob_ek or {})
    with contextlib.redirect_stdout(io.StringIO()) as o:
        exec(compile(kaynak, yol, "exec"), g)
    return o.getvalue()


def guncelle(md_metin, yama):
    """baski_listesi_guncelle.py'yi md_metin'in gecici kopyasinda kosar, yeni metni dondurur."""
    src = open(GUNC, encoding="utf-8").read()
    with tempfile.TemporaryDirectory() as d:
        tmp = os.path.join(d, "baski-listesi.md")
        open(tmp, "w", encoding="utf-8", newline="\n").write(md_metin)
        yon = [('MD = os.path.join(KOK, "planlama", "baski-listesi.md")', "MD = F4C_MD")]
        kos(GUNC, src, yon + (YAMA if yama else []), {"F4C_MD": tmp})
        return open(tmp, encoding="utf-8").read()


def main():
    hata = []

    def kontrol(ok, ad, ayrinti=""):
        print(("GECTI " if ok else "KALDI ") + ad + ((": " + ayrinti) if ayrinti else ""))
        if not ok:
            hata.append(ad)

    Y = json.load(open(Y2B, encoding="utf-8"))
    S, T = Y["satirlar"], Y["toplam"]

    # 1 Y2b yeniden uretim
    with tempfile.TemporaryDirectory() as d:
        tmp = os.path.join(d, "Y2b-baski.json").replace("\\", "/")
        kos(Y2B_PY, open(Y2B_PY, encoding="utf-8").read(), [('open(os.path.join(HERE, "Y2b-baski.json"), "w"', 'open(%r, "w"' % tmp)])
        yeni = json.load(open(tmp, encoding="utf-8"))
    kontrol(yeni == Y, "1 Y2b-baski.py ciktisi = Y2b-baski.json", "%d satir, %d parca" % (len(S), T["adet"]))

    # 2 BOM
    bom = {}
    for r in csv.reader(open(BOM, encoding="utf-8-sig"), delimiter=";"):
        if r and r[0] == "Baski":
            bom[r[1]] = bom.get(r[1], 0) + int(r[2])
    y2 = {}
    for s in S:
        y2[s["ad"]] = y2.get(s["ad"], 0) + s["adet"]
    kontrol(bom == y2, "2 robot-bom.csv Baski = Y2b", "BOM %d kalem / %d adet" % (len(bom), sum(bom.values())))

    # kaynak anahtarlari (analiz index'i)
    anah = {}
    for mod in ("taban", "kabuk", "kafa", "dirsek"):
        for i, p in enumerate(json.load(open(os.path.join(FC, mod, mod + "-analiz.json"), encoding="utf-8"))["baski"]):
            anah[(mod, p["ad"])] = ("%s/baski[%d]" % (mod, i), p["olcu"], p.get("sigar"))
    for i, p in enumerate(json.load(open(os.path.join(FC, "omuz", "omuz-baski.json"), encoding="utf-8"))["parcalar"]):
        y = p["yonler"][p["secilen_yon"]]
        anah[("omuz", p["ad"])] = ("omuz-baski/parcalar[%d]" % i, y["olcu"], y.get("sigar"), p["secilen_yon"])

    # 3 liste satirlari
    metin = open(MD, encoding="utf-8").read()
    satir_re = re.compile(r"^\| ☐ \| (\w+) \| (.+?) \| (\d+) \| (.+?) \| (.+?) \| (.+?) \| (PETG-CF|PETG) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.*) \|$")
    parti = None
    gorulen, sorun = {}, []
    for no, L in enumerate(metin.splitlines(), 1):
        m = re.match(r"## Parti (\d)", L)
        if m:
            parti = int(m.group(1))
        if not L.startswith("| ☐ | ") or L.startswith("| ☐ | Modül"):
            continue
        m = satir_re.match(L)
        if not m:
            sorun.append("%d: satir bicimi" % no)
            continue
        mod, ad, adet, olcu, g, sa, mlz, yon, destek, x2d, kay, bagli = m.groups()
        ad_k = kat(ad).replace(" (520 taban)", "")
        idx = [i for i, s in enumerate(S) if s["modul"] == mod and kat(s["ad"]) == ad_k]
        if len(idx) != 1:
            sorun.append("%d: %s %s Y2b'de %d kez" % (no, mod, ad, len(idx)))
            continue
        i = idx[0]
        s = S[i]
        gorulen[i] = gorulen.get(i, 0) + 1
        a = anah[(mod, s["ad"])]
        bek = dict(adet=str(s["adet"]), olcu=" × ".join(f(x) for x in s["olcu"]), g=aralik(s["g"]), sa=aralik(s["sa"], 2),
                   mlz="PETG-CF" if s["cf"] else "PETG", destek=("**destekli**" if not s["desteksiz"] else "desteksiz"),
                   x2d="sığar" if (a[2] and a[1][0] <= 246 and a[1][1] <= 246 and a[1][2] <= 250) else "SIĞMAZ",
                   kay="`%s` · Y2b[%d]" % (a[0], i), parti=s["parti"])
        gercek = dict(adet=adet, olcu=olcu, g=g, sa=sa, mlz=mlz, destek=destek.split(":")[0], x2d=x2d, kay=kay, parti=parti)
        for k in bek:
            if bek[k] != gercek[k]:
                sorun.append("%d: %s %s %s: liste %r, JSON %r" % (no, mod, ad, k, gercek[k], bek[k]))
        yk = kat(yon)
        if mod == "omuz":
            if not yk.startswith(kat(a[3]) + ":"):
                sorun.append("%d: %s yon %r, secilen_yon %s" % (no, ad, yon, a[3]))
        elif yk != kat(s["yon"] or ""):
            sorun.append("%d: %s yon %r, JSON %r" % (no, ad, yon, s["yon"]))
    eksik = [S[i]["ad"] for i in range(len(S)) if gorulen.get(i, 0) != 1]
    kontrol(not sorun and not eksik, "3 baski-listesi.md satirlari = Y2b (her satir bir JSON anahtarina bagli, her parca bir kez)",
            "%d satir; sorun %s; eksik/cift %s" % (sum(gorulen.values()), sorun[:6], eksik))

    # 4 ozet + partiler
    oz = {}
    for L in metin.splitlines():
        m = re.match(r"\| ([1-4]) \| .+? \| (\d+) \| (.+?) kg \| ≈ (.+?) sa \|$", L)
        if m:
            oz[int(m.group(1))] = (int(m.group(2)), m.group(3), m.group(4))
        m = re.match(r"\| \*\*Toplam\*\* \| \| \*\*(\d+)\*\* \| \*\*(.+?) kg\*\* \| \*\*≈ (.+?) sa\*\* \|$", L)
        if m:
            oz["T"] = (int(m.group(1)), m.group(2), m.group(3))
    bek = {k: (T["parti"][str(k)]["adet"], aralik([x / 1000 for x in T["parti"][str(k)]["g"]], 2), aralik(T["parti"][str(k)]["sa"], 0)) for k in (1, 2, 3, 4)}
    bek["T"] = (T["adet"], aralik([x / 1000 for x in T["g"]], 2), aralik(T["sa"], 0))
    kontrol(oz == bek, "4a Ozet tablosu = Y2b toplam.parti / toplam", str(oz.get("T")))
    P = json.load(open(PARTI, encoding="utf-8"))
    top = dict(adet=0, g=[0.0, 0.0], sa=[0.0, 0.0], petg_g=[0.0, 0.0], cf_g=[0.0, 0.0])
    atanan = []
    for k in ("1", "2", "3", "4"):
        for r in P["partiler"][k]["parcalar"]:
            atanan.append(r["y2b"])
            top["adet"] += r["adet"]
            for j in (0, 1):
                top["g"][j] += r["adet"] * r["g"][j]
                top["sa"][j] += r["adet"] * r["sa"][j]
                top["cf_g" if r["malzeme"] == "PETG-CF" else "petg_g"][j] += r["adet"] * r["g"][j]
    esit = top["adet"] == T["adet"] and all(abs(top[k][j] - T[k][j]) < 1e-6 for k in ("g", "sa", "petg_g", "cf_g") for j in (0, 1))
    kontrol(esit and sorted(atanan) == list(range(len(S))), "4b F4c-partiler Parti 1-4 toplami = baski listesi (adet, kg, sa, PETG, PETG-CF); her parcanin bir partisi var",
            "%d adet, %s–%s g, %s–%s sa (PETG %s, CF %s–%s g)" % (top["adet"], f(top["g"][0], 1), f(top["g"][1], 1), f(top["sa"][0], 2), f(top["sa"][1], 2),
                                                                 f(top["petg_g"][0], 1), f(top["cf_g"][0], 1), f(top["cf_g"][1], 1)))

    # 5 guncelleme betigi
    a = guncelle(metin, False)
    fark = [L for L in difflib.unified_diff(metin.splitlines(), a.splitlines(), "baski-listesi.md", "betik (yamasiz)", n=0, lineterm="") if L[:1] in "+-" and L[:3] not in ("+++", "---")]
    satir_fark = [L for L in fark if L[1:].startswith("| ☐ |")]
    kontrol(not satir_fark, "5a baski_listesi_guncelle.py (yamasiz): parca satirlari ayni", "%d metin satiri farkli (baslik, ust bolum, Parti 3 etiketi)" % len(fark))
    for L in fark:
        print("      " + L[:150])
    b = guncelle(metin, True)
    kontrol(b == metin, "5b baski_listesi_guncelle.py + YAMA: cikti = baski-listesi.md (sabit nokta)",
            "" if b == metin else "%d satir farkli" % sum(1 for x, y in zip(b.splitlines(), metin.splitlines()) if x != y))
    print("SONUC:", "GECTI" if not hata else "KALDI " + ", ".join(hata))
    return 1 if hata else 0


if __name__ == "__main__":
    sys.exit(main())
