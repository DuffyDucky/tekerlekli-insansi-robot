# Lale 1,58 m - planlama/baski-listesi.md satirlarini modul analizlerinden gunceller (sistem Python'u; yalniz kabuk ve kafa satirlari).
# Once planlama/y2/Y2b-baski.py kosulur (Y2b-baski.json); bu betik json'dan okur. Satir yapisi: | [] | modul | Parca | Adet | Olcu | g | sa | yon | not |
import os, re, json, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
MD = os.path.join(KOK, "planlama", "baski-listesi.md")
JS = json.load(open(os.path.join(KOK, "planlama", "y2", "Y2b-baski.json"), encoding="utf-8"))
TR = str.maketrans("ığüşöçİĞÜŞÖÇ", "igusocIGUSOC")


def kat(s):
    s = re.sub(r"\*\*.*?\*\*", "", s).replace(" (520 taban)", "").replace(" (Nextion yok, kapalı)", "").replace(" (gömülü 11,6\" cep)", "").replace("sağ / sol", "sağ").translate(TR)
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKD", s)).strip().lower()


def f(x, n=0):
    return ("%.*f" % (n, x)).replace(".", ",")


SAT = {kat(s["ad"]): s for s in JS["satirlar"] if s["modul"] in ("kabuk", "kafa")}
METIN = open(MD, encoding="utf-8").read().splitlines()
gorulen, cikti = set(), []
for L in METIN:
    if L.startswith("| ☐ | kafa | Ekran tutucu"):
        continue
    m = re.match(r"\| ☐ \| (kabuk|kafa) \| (.+?) \| (\d+) \| (.+?) \| (.+?) \| (.+?) \| (.*)$", L)
    if not m:
        cikti.append(L)
        continue
    ad = kat(m.group(2).replace("Kafa iskeleti (10 in)", "Kafa iskeleti"))
    s = SAT.get(ad)
    if not s:
        cikti.append(L)
        continue
    gorulen.add(ad)
    o = " × ".join(f(x) for x in s["olcu"]) if s["olcu"] else m.group(4)
    r = m.group(7)
    ad_md = m.group(2).replace("Kafa iskeleti (10 in)", "Kafa iskeleti").replace("(Nextion yok, kapalı)", "(gömülü 11,6\" cep)")
    if ad.startswith("s1 kaset"):
        gorulen.add(ad.replace(" sag", " sol"))
    if ad.startswith("gogus bandi") and "destekli" not in r:
        r = r.replace(" |", ", **destekli: cep üst kenarı (köprü ~150 mm)** |", 1)
    cikti.append("| ☐ | %s | %s | %s | %s | %s | %s | %s" % (m.group(1), ad_md, m.group(3), o, f(s["g"][0]), f(s["sa"][0], 2), r))
yeni = [s for k, s in SAT.items() if k not in gorulen]
t = JS["toplam"]
bas = ["## 158 cm güncellemesi (09.11.2026)", "",
       "Boy 1,58 m, göğüste 11,6\" gömülü ekran, kafada 10,1\" QLED. Kabuk ve kafa satırları bu betikle `Y2b-baski.json`'dan; öteki satırlar ve ek sütunlar F4c'de (denetim `planlama/d158/F4c-dogrula.py`). "
       "Güncel toplam **%d parça, %s–%s kg, %s–%s sa** (`planlama/y2/Y2b-baski.py`, %s kg PETG + %s–%s kg PETG-CF)." % (t["adet"], f(t["g"][0] / 1000, 2), f(t["g"][1] / 1000, 2), f(t["sa"][0]), f(t["sa"][1]), f(t["petg_g"][0] / 1000, 2), f(t["cf_g"][0] / 1000, 2), f(t["cf_g"][1] / 1000, 2)),
       "Parti tablolarında satırı olmayan kabuk / kafa parçası:", "",
       ] + (["| Parça | Adet | Ölçü (mm) | Filament (g) | Süre (sa) | Yön | Destek |", "|---|---|---|---|---|---|---|"] if yeni else ["yok."])
for s in yeni:
    bas.append("| %s | %d | %s | %s | %s | %s | %s |" % (s["ad"], s["adet"], " × ".join(f(x) for x in s["olcu"]) if s["olcu"] else "—", f(s["g"][0]), f(s["sa"][0], 2), s["yon"] or "", "desteksiz" if s["desteksiz"] else "destekli"))
ds = [s["ad"] for s in JS["satirlar"] if s["modul"] in ("kabuk",) and not s["desteksiz"]]
bas += ["", "Kabukta destek isteyen parçalar: " + (", ".join(ds) or "yok") + ".", ""]
# parti ozeti ve basliklar
_P = {int(k): v for k, v in t["parti"].items()}
_ADI = {1: "| 1 | Hemen |", 2: "| 2 | Servo ve horn gelip ölçülünce |", 3: "| 3 | 10,1\" QLED yüz ekranı gelip ölçülünce |", 4: "| 4 | Etek tasarım kararından sonra (M6 CAD) |"}


def _ar(v, n, b=1.0):
    return f(v[0] / b, n) if f(v[0] / b, n) == f(v[1] / b, n) else "%s–%s" % (f(v[0] / b, n), f(v[1] / b, n))


for k_, L in enumerate(cikti):
    m_ = re.match(r"\| ([1-4]) \| ", L)
    if m_:
        q_ = _P[int(m_.group(1))]
        cikti[k_] = "%s %d | %s kg | ≈ %s sa |" % (_ADI[int(m_.group(1))], q_["adet"], _ar(q_["g"], 2, 1000.0), _ar(q_["sa"], 0))
    elif L.startswith("| **Toplam** |"):
        cikti[k_] = "| **Toplam** | | **%d** | **%s kg** | **≈ %s sa** |" % (t["adet"], _ar(t["g"], 2, 1000.0), _ar(t["sa"], 0))
    elif L.startswith("# Baskı listesi"):
        cikti[k_] = "# Baskı listesi (1,58 m ana tasarım; 09.11.2026)"
    elif L.startswith("## Parti 3"):
        cikti[k_] = L
    elif re.match(r"\d+ adet · .* kg filament · ≈", L):
        pass
# ilk '## ' basligindan once ekle
i = next(k for k, L in enumerate(cikti) if L.startswith("## "))
# onceki calismadan kalan bolumu at
if cikti[i].startswith("## 158 cm"):
    j = next(k for k, L in enumerate(cikti[i + 1:], i + 1) if L.startswith("## "))
    del cikti[i:j]
open(MD, "w", encoding="utf-8", newline="\n").write("\n".join(cikti[:i] + bas + cikti[i:]) + "\n")
print("guncellendi", len(gorulen), "yeni", [s["ad"] for s in yeni], "destekli", ds)
