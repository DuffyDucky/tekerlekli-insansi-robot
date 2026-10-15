# M6_erisim_sonuc.json -> rehber tablosu (Markdown satirlari). Sistem Python'u: python m6_tablo.py > m6_tablo.md
import json, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "M6_erisim_sonuc.json"), encoding="utf-8"))
ad_adim = {a["no"]: a for a in d["adimlar"]}
grp = collections.OrderedDict()
for b in sorted(d["baglanti"], key=lambda b: b["adim"]):
    if "sol" in b["modul"]:
        continue                                   # sol = sag aynasi; adet x2 yazilir
    k = (b["adim"], b["kod"])
    grp.setdefault(k, []).append(b)

SINIF = {"DUZ": "düz", "L": "L", "L_DAR": "L dar", "ACILI": "açılı", "YOK": "**YOK**", "LOKMA": "lokma", "ACIK_AGIZ": "açık ağız",
         "CEP": "cep", "?": "?"}
satir = collections.OrderedDict()
for (no, kod), L in grp.items():
    cift = any(x in L[0]["modul"] for x in ("_sag",))
    n = len(L) * (2 if cift else 1)
    m = [b["montajda"] for b in L]
    alet = m[0].get("alet") or ("anahtar %s" % re.match(r"M[0-9,]+", kod).group(0) if "somun" in kod else "-")
    sin = collections.Counter(x.get("sinif") for x in m)
    ser = [x.get("serbest_mm", x.get("lokma_serbest_mm")) for x in m if x.get("serbest_mm", x.get("lokma_serbest_mm")) is not None]
    sv = collections.Counter(b["serviste"].get("sinif") for b in L)
    satir.setdefault(no, []).append("%d × %s | %s | %s (en az %s mm) | servis: %s" % (
        n, kod, alet, ", ".join("%s %d" % (SINIF.get(k, k), v * (2 if cift else 1)) for k, v in sin.items()),
        min(ser) if ser else "-", ", ".join("%s %d" % (SINIF.get(k, k), v * (2 if cift else 1)) for k, v in sv.items())))
for no in sorted(set(list(satir.keys()) + [a["no"] for a in d["adimlar"]])):
    a = ad_adim.get(no)
    if not a:
        continue
    print("| %s | %s | %s%s |" % (a["kod"], no, a["baslik"], " (tezgâh: %s)" % a["tezgah"] if a.get("tezgah") else ""))
    for s in satir.get(no, []):
        print("|  |  | %s |" % s)
