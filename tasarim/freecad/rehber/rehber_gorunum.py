# 3B montaj rehberi: görünüm verisi (F10e, P10.4b). FreeCAD İSTEMEZ (standart kütüphane + numpy); CAD dosyalarını yalnız okur.
# rehber_uret.py her üretimde (FreeCAD'li ya da --veri-yok) veri adımından sonra çağırır. Tek başına:
#   py -3 -X utf8 tasarim/freecad/rehber/rehber_gorunum.py            # rehber/veri/rehber-veri.{json,js} yerinde güncellenir
#   py -3 -X utf8 tasarim/freecad/rehber/rehber_gorunum.py --yazma    # yalnız ölçüm, özet
# Veriye yazdıkları (her koşuda baştan hesaplanır, aynı girdiyle aynı çıktı):
#   1) parcalar[].gr  gerçek renk "#rrggbb". Tek kaynak CAD: parçanın modül FCStd'sindeki "Renk" özelliği (Document.xml) ve o modülü
#      boyayan betiğin RENK tablosu (<modül>_gorsel.py, ast ile okunur; tabloda olmayan ad "gri", gorsel betiklerindeki
#      RENK.get(o.Renk, RENK["gri"]) kuralı). Rehberde ayrı renk tablosu yok. Bağımsız denetim: FCStd'nin GuiDocument.xml'inde kayıtlı
#      ShapeAppearance yayınık rengi (gorsel betiği doc.save() ile yazmış; kafa dosyasında GuiDocument yok) parça parça karşılaştırılır
#      -> renk_kaynak.denetim. Parça sırası rehber_veri.py ile aynı (Y.DOSYA sırası, Document.xml nesne sırası, Tur özellikli
#      Part::Feature, HARIC önekleri); her parçada modül, tür ve kod veriyle eşleşmeli, yoksa betik durur.
#   2) sira_grup / adım görünüm alanları rehber_metin.py'den (kamera, saydam, is_, ad, gizli_ok, ucus_ok, giris_ok, piksel_ok; adım
#      düzeyinde baslik, is_, baglanti_md, alet, erisim, kontrol, kablo, not_, kamera, saydam). rehber_veri.py'nin yazdığıyla aynı kural;
#      --veri-yok yolunda rehber_metin değişikliği (kamera, saydam, metin) veriye böyle girer. Grup sayısı / satırlar değişmez (değişirse
#      betik durur: FreeCAD'li tam üretim gerekir).
#   3) sira_grup[].ev ve adimlar[].ev: "bağlandığı yer". Alt adımın (ya da adımın) yeni bağlantı elemanlarının geçtiği / oturduğu, o
#      konumda yerinde duran ("önceki") parçalar. Yöntem (rehber_sira.isil_gomme'nin halka yöntemi): cıvata ekseninin çevresinde
#      (r + 0,8 ve r + 2,5 mm yarıçap, 8 açı, gövde boyunca 6 yükseklik = 96 nokta) ve somun / çekiç somunun dış yüzünün 0,8 mm dışında
#      24 nokta; nokta GLB mesh'inin içinde mi (eğik ışın paritesi). En az EV_ESIK nokta içeren önceki parça ev. Pul ve ısıl gömme
#      örneklenmez (pul cıvatanın altında; ısıl gömmenin ev sahibi zaten h). Yeni bağlantı elemanı yoksa ya da hiçbir önceki parçaya
#      girmiyorsa: yeni ana parçaların yüzeyinden dışa 0,6 mm (köşe normali) kaydırılmış noktalar -> temas eden önceki parça (en az
#      TEMAS_ESIK nokta). Kaynak: ev_kaynak (sayılar, boş kalan konumlar ve nedeni).
#   4) parcalar[].ip: bağlantı elemanının işaret noktası (cıvata: baş üst merkezi; öbürleri sınır kutusu merkezi), dünya, mm.
#   Konum durumu app.js durum(p, s, j) ile aynı kural (aşağıda durum()).
import os, sys, re, ast, json, math, time, struct, zipfile, argparse, collections
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.dirname(HERE)
ROBOT = os.path.dirname(os.path.dirname(FC))
VERI_DIR = os.path.join(ROBOT, "rehber", "veri")
sys.path.insert(0, HERE)

# rehber_veri.py / m6_yukle.py ile aynı modül dosyaları ve hariç önekleri (m6_yukle FreeCAD import ettiği için burada kopya değil
# okuma: planlama/adim4/m6_yukle.py'den ast ile alınır)
M6_YUKLE = os.path.join(ROBOT, "planlama", "adim4", "m6_yukle.py")
GORSEL = {"iskelet": "iskelet/iskelet_gorsel.py", "omuz": "omuz/omuz_gorsel.py", "kabuk": "kabuk/kabuk_gorsel.py",
          "dirsek": "dirsek/dirsek_gorsel.py", "kafa": "kafa/kafa_gorsel.py", "taban": "taban/taban_gorsel.py"}
EV_ESIK = 3          # nokta: cıvata / somun halkasının en az bu kadarı parçanın içindeyse ev
TEMAS_ESIK = 6       # nokta: yedek yöntemde (yüzeyden dışarı kaydırılmış) en az bu kadar nokta
TEMAS_OFS = (0.6, 1.5, 3.0)   # mm: yedek yöntemin kaydırması (önce 0,6; bulunmazsa 1,5, sonra 3)
D_ISIN = None        # eğik ışın yönü (eksenlere paralel değil: yüzeyle aynı düzleme düşmesin)


def _ast_sabit(yol, ad):
    t = ast.parse(open(yol, encoding="utf-8").read())
    for n in t.body:
        if isinstance(n, ast.Assign) and any(getattr(x, "id", None) == ad for x in n.targets):
            return ast.literal_eval(n.value)
    raise SystemExit("%s içinde %s yok" % (yol, ad))


def _hex(rgb):
    return "#%02x%02x%02x" % tuple(int(x * 255 + 0.5) for x in rgb[:3])


# ------------------------------------------------------------------ 1) gerçek renk
def fcstd_oku(yol):
    """Document.xml: nesne sırası + String özellikleri; GuiDocument.xml: ShapeAppearance yayınık rengi (varsa)."""
    z = zipfile.ZipFile(yol)
    doc = ET.fromstring(z.read("Document.xml"))
    sira = [(o.get("type"), o.get("name")) for o in doc.find("Objects").findall("Object")]
    ozellik = {}
    for o in doc.find("ObjectData").findall("Object"):
        pr = {}
        for p in o.find("Properties").findall("Property"):
            s = p.find("String")
            if s is not None:
                pr[p.get("name")] = s.get("value")
        ozellik[o.get("name")] = pr
    gui = {}
    if "GuiDocument.xml" in z.namelist():
        g = ET.fromstring(z.read("GuiDocument.xml"))
        for vp in g.iter("ViewProvider"):
            for p in vp.iter("Property"):
                if p.get("name") != "ShapeAppearance":
                    continue
                ml = p.find("MaterialList")
                if ml is None:
                    continue
                b = z.read(ml.get("file"))
                dif = struct.unpack("<I", b[8:12])[0]                  # sayı, ortam, YAYINIK (RGBA paketli) ...
                gui[vp.get("name")] = "#%02x%02x%02x" % ((dif >> 24) & 255, (dif >> 16) & 255, (dif >> 8) & 255)
    return sira, ozellik, gui


def cad_parcalar():
    dosya = _ast_sabit(M6_YUKLE, "DOSYA")
    haric = _ast_sabit(M6_YUKLE, "HARIC")
    tablo = {m: _ast_sabit(os.path.join(FC, f), "RENK") for m, f in GORSEL.items()}
    out, cache = [], {}
    for mod, f in dosya.items():
        if f not in cache:
            cache[f] = fcstd_oku(os.path.join(FC, f))
        sira, oz, gui = cache[f]
        tb = tablo[mod.split("_")[0]]
        for typ, name in sira:
            pr = oz.get(name, {})
            if typ != "Part::Feature" or "Tur" not in pr:
                continue
            if any(pr["Label"].startswith(h) for h in haric.get(mod, ())):
                continue
            ad = pr.get("Renk") or "gri"
            out.append(dict(modul=mod, nesne=name, etiket=pr["Label"], kod=pr.get("Kod", ""), tur=pr["Tur"], renk_ad=ad,
                            renk=_hex(tb.get(ad, tb["gri"])), tabloda=ad in tb, gui=gui.get(name), dosya=f,
                            gorsel=GORSEL[mod.split("_")[0]]))
    return out


def renk_isle(V):
    import rehber_metin as RM
    C = cad_parcalar()
    P = V["parcalar"]
    if len(C) != len(P):
        raise SystemExit("CAD parça sayısı %d, veri %d: FreeCAD'li tam üretim gerekir" % (len(C), len(P)))
    uyumsuz = [i for i, (c, p) in enumerate(zip(C, P))
               if c["modul"] != p["modul"] or c["tur"] != p["tur"] or RM.tr(c["kod"]) != p["kod"]]
    if uyumsuz:
        i = uyumsuz[0]
        raise SystemExit("CAD ↔ veri sırası uyuşmuyor (%d parça; ilki %s: %s / %s)" % (len(uyumsuz), P[i]["id"], C[i]["etiket"], P[i]["ad"]))
    gui_var = gui_ayni = 0
    farkli = []
    for c, p in zip(C, P):
        p["gr"] = c["renk"]
        if c["gui"]:
            gui_var += 1
            if c["gui"] == c["renk"]:
                gui_ayni += 1
            else:
                farkli.append(dict(id=p["id"], ad=p["ad"], tablo=c["renk"], gui=c["gui"]))
    say = collections.Counter((c["modul"].split("_")[0], c["renk_ad"], c["renk"]) for c in C)
    V["renk_kaynak"] = dict(
        yontem="parça rengi = modül gorsel betiğinin RENK tablosundan RENK.get(FCStd Renk özelliği, RENK['gri']) (FreeCAD'siz: "
               "Document.xml + ast); denetim: FCStd GuiDocument.xml ShapeAppearance yayınık rengi",
        betik="tasarim/freecad/rehber/rehber_gorunum.py", tablo={m: "tasarim/freecad/" + f for m, f in GORSEL.items()},
        parca=len(P), veri_cad_eslesen=len(P) - len(uyumsuz),
        denetim=dict(gui_kayitli=gui_var, ayni=gui_ayni, farkli=farkli, gui_yok=len(P) - gui_var,
                     gui_yok_modul=sorted({c["modul"] for c in C if not c["gui"]})),
        tabloda_olmayan_ad=sorted({"%s:%s" % (c["modul"].split("_")[0], c["renk_ad"]) for c in C if not c["tabloda"]}),
        ozet=[dict(modul=m, ad=a, renk=r, adet=n) for (m, a, r), n in sorted(say.items())])
    return V["renk_kaynak"]


# ------------------------------------------------------------------ 2) görünüm alanları (rehber_metin.py)
# F10f: sema_yalniz = alt adımda yalnız o grubun şemaları çizilir (kol kablo yolu uç duruş yakın kareleri; öbür yollar üst üste binmesin)
GRUP_ALAN = ("ad", "is_", "kamera", "gizli_ok", "ucus_ok", "giris_ok", "piksel_ok", "sema_yalniz", "sema_ortulu")   # P10.7b2d-A d1
ADIM_ALAN = ("baslik", "is_", "baglanti_md", "alet", "erisim", "kontrol", "kablo", "not_", "kamera")


def alan_isle(V):
    """rehber_veri.py ile aynı kural: grup alanı rehber_metin'de varsa yazılır, yoksa veride silinir (ad her zaman); saydam = adın
    (görünen ad) içinde desen geçen, adımı <= (grup) / < (adım) olan Referans dışı parçalar."""
    import importlib
    import rehber_metin as RM
    importlib.reload(RM)
    P = V["parcalar"]
    degisen = []
    for a in V["adimlar"]:
        kod, i = a["kod"], a["i"]
        mt = RM.HAZIRLIK if kod == "0" else RM.ADIM.get(kod, {})
        # P10.7b2d-A: metinde alt adım var, veride yoksa (ör. K1 / K2 demet alt adımları, eski veri) ana metin yalnız başlık paragrafı
        # kalırdı: FreeCAD'siz yol durur
        if mt.get("sira") and not a.get("sira_grup"):
            raise SystemExit("%s: rehber_metin'de sira var, veride sira_grup yok: FreeCAD'li tam üretim gerekir" % kod)
        for k in ADIM_ALAN:
            if k in mt and mt[k]:
                v = list(mt[k]) if isinstance(mt[k], tuple) else mt[k]
                if a.get(k) != v:
                    degisen.append("%s %s" % (kod, k))
                a[k] = v
        if mt.get("saydam"):
            ids = [q["id"] for q in P if q["a"] < i and q["tur"] != "Referans" and any(d in q["ad"] for d in mt["saydam"])]
            if a.get("saydam") != ids:
                degisen.append("%s saydam" % kod)
            a["saydam"] = ids
        sira = mt.get("sira")
        if not a.get("sira_grup"):
            continue
        if not sira or len(sira) != len(a["sira_grup"]):
            raise SystemExit("%s: rehber_metin sira grubu sayısı veriden farklı: FreeCAD'li tam üretim gerekir" % kod)
        if bool(mt.get("demet_alt")) != bool(a.get("demet_alt")):
            raise SystemExit("%s: demet alt adımı işareti veriden farklı: FreeCAD'li tam üretim gerekir" % kod)
        for n, (g, e) in enumerate(zip(sira, a["sira_grup"])):
            # P10.7b2d-A: demet alanları rehber_veri.py ile aynı kuraldan (rehber_metin.demet_grup_alanlari)
            dg = RM.demet_grup_alanlari(g, mt.get("kablo") or [], kod, n)
            for k in ("demet", "genel", "kablo"):
                if k in dg:
                    if e.get(k) != dg[k]:
                        degisen.append("%s.%d %s" % (kod, n + 1, k))
                    e[k] = dg[k]
                elif k in e:
                    degisen.append("%s.%d %s (silindi)" % (kod, n + 1, k))
                    e.pop(k)
            for k in GRUP_ALAN:
                v = g.get(k)
                if k == "kamera" and v is not None and not isinstance(v, str):
                    v = list(v)
                if v:
                    if isinstance(v, dict):
                        v = dict(v)
                    if e.get(k) != v:
                        degisen.append("%s.%d %s" % (kod, n + 1, k))
                    e[k] = v
                elif k in e:
                    degisen.append("%s.%d %s (silindi)" % (kod, n + 1, k))
                    e.pop(k)
            if g.get("saydam"):
                ids = [q["id"] for q in P if q["a"] <= i and q["tur"] != "Referans" and any(d in q["ad"] for d in g["saydam"])]
                if e.get("saydam") != ids:
                    degisen.append("%s.%d saydam" % (kod, n + 1))
                e["saydam"] = ids
            elif "saydam" in e:
                degisen.append("%s.%d saydam (silindi)" % (kod, n + 1))
                e.pop("saydam")
            if g.get("odak"):                                       # P10.7b2e kısım 2: kadraj odak parçaları (rehber_veri ile aynı)
                ids = [q["id"] for q in P if q["a"] <= i and any(d in q["ad"] for d in g["odak"])]
                bos = [d for d in g["odak"] if not any(d in q["ad"] for q in P if q["a"] <= i)]
                if bos:
                    raise SystemExit("%s.%d: odak deseni bu adima kadar takilan hicbir parcaya uymuyor: %s" % (kod, n + 1, bos))
                if e.get("odak") != ids:
                    degisen.append("%s.%d odak" % (kod, n + 1))
                e["odak"] = ids
            elif "odak" in e:
                degisen.append("%s.%d odak (silindi)" % (kod, n + 1))
                e.pop("odak")
            if g.get("kenar"):                                      # F10f düzeltme 1: kenar çizgisi alan parçalar (rehber_veri ile aynı)
                ids = [q["id"] for q in P if q["a"] <= i and q["tur"] != "Referans" and any(d in q["ad"] for d in g["kenar"])]
                if e.get("kenar") != ids:
                    degisen.append("%s.%d kenar" % (kod, n + 1))
                e["kenar"] = ids
            elif "kenar" in e:
                e.pop("kenar")
    return degisen


# ------------------------------------------------------------------ konum durumu (app.js durum0 / durum ile aynı)
def grup_harita(st):
    h = dict(p={}, bag={})
    for n, g in enumerate(st.get("sira_grup") or []):
        for k in g["satir"]:
            t, i = k.split(":")
            r = (st["parcalar"] if t == "p" else st["baglantilar"])[int(i)]
            for pid in r["ids"]:
                h["p"][pid] = n
        for pid in g.get("ref") or []:
            h["p"][pid] = n
        if g.get("bag"):
            h["bag"][g["bag"]] = n
    return h


def durum0(p, s, A):
    st = A[s]
    if s == 0:
        return "hedef"
    if st["tezgah"]:
        if p["t"] != st["tezgah"] or p["a"] > s:
            return "gizli"
        return "simdi" if p["a"] == s else "onceki"
    if p["b"] > s:
        return "gizli"
    if p["b"] == s:
        return "simdi" if p["a"] == s else "alt"
    return "onceki"


def durum(p, s, j, A, GH):
    st = A[s]
    d0 = durum0(p, s, A)
    if not j or not st.get("alt") or s == 0:
        return d0
    G = st["sira_grup"]
    g = G[j - 1]
    gh = GH[s]
    pg = gh["p"].get(p["id"]) if p["a"] == s else None
    if g["tezgah"]:
        if pg is None or G[pg]["tezgah"] != g["tezgah"] or pg > j - 1:
            return "gizli"
        return "simdi" if pg == j - 1 else "onceki"
    if p["a"] != s:
        return ("alt" if j == 1 else "onceki") if d0 == "alt" else d0
    if pg is None:
        return d0
    key = G[pg]["tezgah"]
    if key and gh["bag"].get(key) is not None:
        bi = gh["bag"][key]
        return "gizli" if j - 1 < bi else ("alt" if j - 1 == bi else "onceki")
    return "onceki" if pg < j - 1 else ("simdi" if pg == j - 1 else "gizli")


def konumlar(A):
    out = []
    for a in A:
        out.append((a["i"], 0))
        out += [(a["i"], j) for j in range(1, (a.get("alt") or 0) + 1)]
    return out


# ------------------------------------------------------------------ 3) bağlandığı yer + 4) işaret noktası (GLB mesh, numpy)
class Mesh:
    def __init__(self, V):
        import numpy as np
        import rehber_sira as RS
        self.np = np
        meshes, nodes = RS.glb_oku(os.path.join(VERI_DIR, "robot.glb"))
        PP = {p["id"]: p for p in V["parcalar"]}
        self.P = {}
        for name, mi, M in nodes:
            v, f = meshes[mi]
            w = v @ M[:3, :3].T + M[:3, 3]
            self.P[name] = dict(v=w, f=f, bmin=w.min(0), bmax=w.max(0), veri=PP[name])
        global D_ISIN
        D_ISIN = np.array([0.5773, 0.5779, 0.5767]); D_ISIN /= np.linalg.norm(D_ISIN)
        self._tri = {}

    def tri(self, pid):
        if pid not in self._tri:
            p = self.P[pid]
            T = p["v"][p["f"]]
            v0, e1, e2 = T[:, 0], T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]
            h = self.np.cross(D_ISIN, e2)
            a = self.np.einsum("ij,ij->i", e1, h)
            ok = self.np.abs(a) > 1e-12
            self._tri[pid] = (v0[ok], e1[ok], e2[ok], h[ok], 1.0 / a[ok])
        return self._tri[pid]

    def icinde(self, pts, pid):
        """pts (m, 3) noktalarından hangileri pid'in kapalı mesh'inin içinde (eğik ışın paritesi)."""
        np = self.np
        v0, e1, e2, h, f = self.tri(pid)
        s_ = pts[:, None, :] - v0[None, :, :]
        uu = f[None, :] * np.einsum("mnk,nk->mn", s_, h)
        qq = np.cross(s_, e1[None, :, :])
        vv = f[None, :] * (qq @ D_ISIN)
        tt = f[None, :] * np.einsum("nk,mnk->mn", e2, qq)
        n = ((uu >= 0) & (vv >= 0) & (uu + vv <= 1) & (tt > 1e-9)).sum(1)
        return (n % 2) == 1

    def eksen(self, pid):
        np = self.np
        p = self.P[pid]
        u = np.array(p["veri"]["u"], float)
        u /= max(np.linalg.norm(u), 1e-9)
        a = np.array([1.0, 0, 0]) if abs(u[0]) < 0.9 else np.array([0, 1.0, 0])
        e1 = a - u * a.dot(u); e1 /= np.linalg.norm(e1); e2 = np.cross(u, e1)
        v = p["v"]
        c1 = 0.5 * ((v @ e1).min() + (v @ e1).max()); c2 = 0.5 * ((v @ e2).min() + (v @ e2).max())
        return e1 * c1 + e2 * c2, u, e1, e2, (v @ u).min(), (v @ u).max()


def civata_mi(p):
    return p["tur"] == "Baglanti" and any(x in p["kod"] for x in ("DIN 912", "ISO 7380", "DIN 913", "horn vida", "PT vida", "saplama"))


def bag_tipi(p):
    a = (p["ad"] + " " + p["kod"]).lower()
    if p["tur"] != "Baglanti":
        return None
    if "ısıl gömme" in a or "isil gomme" in a:
        return "gomme"
    if civata_mi(p):
        return "civata"
    if re.search(r"\bpul\b", a):
        return "pul"
    if "somun" in a or "perçin" in a:
        return "somun"
    return "diger"


def _cap(kod):
    m = re.search(r"M(\d+(?:[.,]\d+)?)", kod)
    return float(m.group(1).replace(",", ".")) if m else 3.0


def ornek_noktalar(M, pid):
    np = M.np
    p = M.P[pid]["veri"]
    tip = bag_tipi(p)
    c, u, e1, e2, tl, tu = M.eksen(pid)
    if tip == "civata":
        d = _cap(p["kod"])
        bas_h = 0.55 * d if "7380" in p["kod"] else (0.0 if "913" in p["kod"] else d)
        t1 = tu - bas_h - 0.4
        t0 = tl + 0.5
        if t1 <= t0:
            t1 = tu - 0.3
        out = []
        for t in np.linspace(t0, t1, 6):
            for rr in (d / 2 + 0.8, d / 2 + 2.5):
                for k in range(8):
                    a = 2 * math.pi * (k + 0.5) / 8
                    out.append(c + u * t + rr * (math.cos(a) * e1 + math.sin(a) * e2))
        return np.array(out)
    if tip == "somun":
        v = M.P[pid]["v"]
        R = float(np.sqrt(((v - c) @ e1) ** 2 + ((v - c) @ e2) ** 2).max())     # eksene dik en büyük yarıçap
        out = []
        for t in (tl + 0.3 * (tu - tl), 0.5 * (tl + tu), tl + 0.7 * (tu - tl)):
            for k in range(8):
                a = 2 * math.pi * k / 8
                out.append(c + u * t + (R + 0.8) * (math.cos(a) * e1 + math.sin(a) * e2))
        return np.array(out)
    return None


def isaret_noktasi(M, pid):
    p = M.P[pid]
    if bag_tipi(p["veri"]) == "civata":
        c, u, e1, e2, tl, tu = M.eksen(pid)
        q = c + u * tu
    else:
        q = 0.5 * (p["bmin"] + p["bmax"])
    return [round(float(x), 1) for x in q]


def yuzey_noktalari(M, pid, n=3000, ofs=0.6):
    """Ana parçanın üçgen ağırlık merkezlerinden yüz normali boyunca iki yana ofs mm kaydırılmış noktalar (yön bağımsız: içe düşen
    nokta parçanın kendisinde kalır, yalnız öbür parçalar sınanır). Üçgenler alanı büyükten küçüğe, en çok n tanesi."""
    np = M.np
    p = M.P[pid]
    v, f = p["v"], p["f"]
    fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    L = np.linalg.norm(fn, axis=1)
    idx = np.argsort(-L)
    idx = idx[L[idx] > 1e-9][:n]
    c = v[f[idx]].mean(1)
    nn = fn[idx] / L[idx, None]
    return np.vstack([c + nn * ofs, c - nn * ofs])


def ev_isle(V, M):
    np = M.np
    A, P = V["adimlar"], V["parcalar"]
    GH = {a["i"]: grup_harita(a) for a in A}
    PID = {p["id"]: p for p in P}
    aday_mi = {p["id"]: (p["tur"] not in ("Baglanti", "Referans") and not p.get("renk")) for p in P}
    # bağlantı elemanı başına: içinde örnek nokta bulunan aday parçalar ve nokta sayısı (konumdan bağımsız; konumda önceki olanlar süzülür)
    t0 = time.time()
    temas = {}
    say = collections.Counter()
    for p in P:
        if p["tur"] != "Baglanti":
            continue
        p["ip"] = isaret_noktasi(M, p["id"])
        pts = ornek_noktalar(M, p["id"])
        say[bag_tipi(p) or "?"] += 1
        if pts is None:
            continue
        lo, hi = pts.min(0), pts.max(0)
        sk = {}
        for q, mq in M.P.items():
            if not aday_mi[q] or np.any(mq["bmax"] < lo) or np.any(mq["bmin"] > hi):
                continue
            n = int(M.icinde(pts, q).sum())
            if n:
                sk[q] = n
        temas[p["id"]] = sk
    t_bag = time.time() - t0
    yuzey = {}

    def yuzey_temas(pid, onceki, ofs):
        if (pid, ofs) not in yuzey:
            yuzey[(pid, ofs)] = yuzey_noktalari(M, pid, ofs=ofs)
        pts = yuzey[(pid, ofs)]
        lo, hi = pts.min(0) - 1, pts.max(0) + 1
        sk = {}
        for q in onceki:
            mq = M.P[q]
            if np.any(mq["bmax"] < lo) or np.any(mq["bmin"] > hi):
                continue
            n = int(M.icinde(pts, q).sum())
            if n >= TEMAS_ESIK:
                sk[q] = n
        return sk

    kayit = []
    for s, j in konumlar(A):
        if s == 0:
            continue
        st = A[s]
        d = {p["id"]: durum(p, s, j, A, GH) for p in P}
        onceki = [i for i, x in d.items() if x == "onceki" and aday_mi[i]]
        oset = set(onceki)
        yeni_bag = [i for i, x in d.items() if x == "simdi" and PID[i]["tur"] == "Baglanti"]
        yeni_ana = [i for i, x in d.items() if x in ("simdi", "alt") and aday_mi[i]]
        ev = collections.Counter()
        kaynak = "baglanti"
        for i in yeni_bag:
            for q, n in temas.get(i, {}).items():
                if q in oset and n >= EV_ESIK:
                    ev[q] += n
        for ofs in TEMAS_OFS:                                       # yedek: yüzey teması (önce 0,6 mm, bulunmazsa 1,5 mm)
            if ev or not yeni_ana or not onceki:
                break
            kaynak = "temas %.1f mm" % ofs
            for i in yeni_ana:
                for q, n in yuzey_temas(i, onceki, ofs).items():
                    ev[q] += n
        evs = [q for q, _ in ev.most_common()]
        masa = bool(st["tezgah"] or (j and st["sira_grup"][j - 1]["tezgah"]))
        if not evs and masa and not onceki:
            # masada ilk alt adım: önceki parça yok; parçalar birimin tabanına (bu alt adımda yeni; yerinde duran d = 0 parça, yoksa
            # sınır kutusu köşegeni en büyük ana parça) bağlanır. app.js tabanı gerçek renginde, ev tonunda kenar çizgisiyle gösterir.
            evs = [i for i in yeni_ana if PID[i]["d"] == 0]
            if not evs and len(yeni_ana) > 1:
                evs = [max(yeni_ana, key=lambda i: float(M.np.linalg.norm(M.P[i]["bmax"] - M.P[i]["bmin"])))]
            kaynak = "masa tabanı (yeni)" if evs else "masada ilk parça, taban yok"
        if not evs and not kaynak.startswith("masa"):
            kaynak = "yeni parça yok" if not yeni_ana and not yeni_bag else ("önceki parça yok" if not onceki else "bulunamadı")
        hedef = st["sira_grup"][j - 1] if j else st
        hedef["ev"] = evs
        kayit.append(dict(adres="%d.%d" % (s, j) if j else str(s), kod=st["kod"], ev=len(evs), kaynak=kaynak,
                          yeni_bag=len(yeni_bag), yeni_ana=len(yeni_ana), ev_ad=[PID[q]["ad"] for q in evs[:6]]))
    bos = [k for k in kayit if not k["ev"]]
    V["ev_kaynak"] = dict(
        yontem="ev = konumda yerinde duran (önceki) parçalardan, yeni bağlantı elemanlarının halka noktalarının en az %d'ünü içeren "
               "(cıvata: eksen çevresinde r + 0,8 / r + 2,5 mm, 6 yükseklik × 8 açı; somun: dış yüzün 0,8 mm dışı, 3 × 8); bulunmazsa "
               "yeni ana parçaların yüzeyinden 0,6 mm (yoksa 1,5, sonra 3 mm) dışarıdaki noktaların en az %d'ünü içeren önceki parça (temas); "
               "masada ilk alt adımda önceki parça yoksa birimin yerinde duran tabanı (d = 0, yeni). Mesh: robot.glb, içerde testi eğik "
               "ışın paritesi" % (EV_ESIK, TEMAS_ESIK),
        baglanti_turu=dict(say), konum=len(kayit), ev_bulunan=len(kayit) - len(bos),
        kaynak=dict(collections.Counter(k["kaynak"] for k in kayit)), bos=[dict(adres=k["adres"], kod=k["kod"], neden=k["kaynak"]) for k in bos],
        sure_s=round(time.time() - t0 + 0.0, 1), sure_baglanti_s=round(t_bag, 1))
    return kayit


# ------------------------------------------------------------------ ana
# ------------------------------------------------------------------ 5) uç etiketleri (P10.7b2f; F10m-kare-inceleme § 6)
# Konumun (alt adımın; alt adımı olmayan adımda adımın) metninde kimliği geçen ve o konumda çizilen kabloların (CAD kablo parçası
# kablo listesi, şemanın kablo listesi; bağlantı tablosu kabloları metinde geçmesi yeter) damar uçları. Uç kısa adı (rehber_kablo.uc_kisa)
# UC_ETIKET'le modeldeki parçaya bağlanır; parça o konumda gizli değilse etiket olur: metin = kısa ad (aynı parçaya düşen adlar " / "
# ile birleşir), yer = parçanın robot.glb kutusunun merkezi (dünya, mm). Parçası olmayan ya da o konumda takılı olmayan uç
# "uc_yok"a nedeniyle yazılır (basılı sayfa ve lejant "karede görünmez" der). Demet adımının ana karesi (j = 0) etiketlenmez (bütün
# kablolar birden). En çok UC_EN_COK etiket: fazlası basılı listede kalır, karede numarası yoktur (sıra: metinde geçiş sırası).
# rehber_metin.UC_ORTULU {(kod, alt adım): {kısa ad: neden}}: ölçümde karede görünmeyen uç (F10d uc_etiket) etiketlenmez, uc_yok'a.
UC_EN_COK = 10
_UC_KIMLIK = re.compile(r"(?<![\w{.])([A-Z]{1,2}\d{1,2})(?![\w}])")
_UC_ARALIK = re.compile(r"(?<![\w{.])([A-Z]{1,2})(\d{2})\s*[–-]\s*\1(\d{2})(?![\w}])")


def _metin_kimlikleri(metin, tum):
    """Metinde geçiş sırasıyla kimlikler (A01–A06 aralığı açılır); yalnız tablodakiler."""
    out = []
    for m in re.finditer(r"%s|%s" % (_UC_ARALIK.pattern, _UC_KIMLIK.pattern), metin or ""):
        if m.group(1):
            ks = ["%s%02d" % (m.group(1), n) for n in range(int(m.group(2)), int(m.group(3)) + 1)]
        else:
            ks = [m.group(4)]
        out += [k for k in ks if k in tum and k not in out]
    return out


def uc_isle(V, kutular, cad=None):
    """sira_grup[].uc / adimlar[].uc ve uc_yok alanlarını yazar (yukarıdaki kural). kutular: parça kimliği → (bmin, bmax)."""
    import rehber_kablo as RK
    import rehber_metin as RM
    TB = RK.Tablo()
    cad = cad if cad is not None else cad_parcalar()
    A, P, S = V["adimlar"], V["parcalar"], V.get("semalar", [])
    if len(cad) != len(P):
        raise SystemExit("uc_isle: CAD parça sayısı %d, veri %d" % (len(cad), len(P)))
    GH = {a["i"]: grup_harita(a) for a in A}
    PID = {p["id"]: p for p in P}
    hedef = {}                                                    # kısa ad → parça kimliği
    for ad, (desen, mod) in RK.UC_ETIKET.items():
        ids = [P[i]["id"] for i, c in enumerate(cad) if re.search(desen, c["etiket"]) and (mod is None or c["modul"] == mod)]
        if len(ids) != 1:
            raise SystemExit("uc_isle: %s deseni %d parçaya uyuyor (rehber_kablo.uc_etiket_denetle)" % (ad, len(ids)))
        hedef[ad] = ids[0]
    say = dict(konum=0, etiket=0, yok=0)
    kullanilan = set()

    def konum(a, j, g, metin, ciz, ortulu):
        bt = {k for k, kod in RK.BAGLANTI_TABLOSU.items() if kod == a["kod"]}
        kim = [k for k in _metin_kimlikleri(metin, TB.K) if k in ciz or k in bt]
        uc, yok = collections.OrderedDict(), collections.OrderedDict()
        for k in kim:
            for d in TB.K[k].get("damarlar") or []:
                for y in "ab":
                    ad = RK.uc_kisa(d.get(y))
                    if not ad:
                        continue
                    pid = hedef.get(ad)
                    if pid is None:
                        yok.setdefault(ad, dict(ad=ad, neden=RK.UC_MODELSIZ.get(ad, "modelde yok"), kablo=[]))["kablo"].append(k)
                    elif ad in ortulu:
                        kullanilan.add((a["kod"], j, ad))
                        yok.setdefault(ad, dict(ad=ad, neden=ortulu[ad], kablo=[]))["kablo"].append(k)
                    elif durum(PID[pid], a["i"], j, A, GH) == "gizli":
                        yok.setdefault(ad, dict(ad=ad, neden="bu adımda takılı değil", kablo=[]))["kablo"].append(k)
                    else:
                        u = uc.setdefault(pid, dict(id=pid, adlar=[], kablo=[]))
                        if ad not in u["adlar"]:
                            u["adlar"].append(ad)
                        if k not in u["kablo"]:
                            u["kablo"].append(k)
        for x in yok.values():
            x["kablo"] = sorted(set(x["kablo"]))
        liste = []
        for n, u in enumerate(uc.values(), 1):
            bmin, bmax = kutular[u["id"]]
            liste.append(dict(n=n, id=u["id"], ad=" / ".join(u["adlar"]), kablo=u["kablo"],
                              ip=[round((float(bmin[i]) + float(bmax[i])) / 2, 1) for i in range(3)], karede=n <= UC_EN_COK))
        for k in ("uc", "uc_yok"):
            g.pop(k, None)
        if liste:
            g["uc"] = liste
        if yok:
            g["uc_yok"] = list(yok.values())
        if liste or yok:
            say["konum"] += 1
            say["etiket"] += sum(1 for x in liste if x["karede"])
            say["yok"] += len(yok)

    for a in A:
        if a["i"] == 0:
            continue
        mt = RM.ADIM.get(a["kod"], {})
        G = a.get("sira_grup") or []
        if a.get("alt") and G:
            a.pop("uc", None); a.pop("uc_yok", None)
            for j, g in enumerate(G, 1):
                ciz = set()
                for pid in g.get("ref") or []:
                    ciz |= set(PID[pid].get("kablo") or [])
                for i in g.get("sema") or []:
                    ciz |= set(S[i].get("kablo") or [])
                # P10.8b (planlama/d158/P108b-gunluk.md § 4): etiket_kablo = şeması bu alt adımda çizilmeyen (başka adımın şeması)
                # ama ucu bu alt adımda takılan kablolar; uç etiketi basılır, çizgi çizilmez (U06'nın ESP32 ucu 17.11, şeması K2'de).
                # Kimlik tabloda ve alt adımın metninde olmalı (sessiz düşüş yok)
                sg = mt.get("sira") or []
                ek = tuple(sg[j - 1].get("etiket_kablo") or ()) if j - 1 < len(sg) else ()
                for k in ek:
                    if k not in TB.K or k not in _metin_kimlikleri(g.get("is_") or "", TB.K):
                        raise SystemExit("uc_isle: %s.%d etiket_kablo %s tabloda ya da alt adımın metninde yok" % (a["kod"], j, k))
                ciz |= set(ek)
                konum(a, j, g, g.get("is_") or "", ciz, dict(RM.UC_ORTULU.get((a["kod"], j)) or {}))
        else:
            ciz = set()
            for p in P:
                if p.get("kablo") and durum0(p, a["i"], A) == "simdi":
                    ciz |= set(p["kablo"])
            for s in S:
                if s.get("a") == a["i"]:
                    ciz |= set(s.get("kablo") or [])
            konum(a, 0, a, a.get("is_") or "", ciz, dict(RM.UC_ORTULU.get((a["kod"], 0)) or {}))
    say["ortulu_kullanilmayan"] = ["%s.%d %s" % (k, j, ad) for (k, j), d in sorted(RM.UC_ORTULU.items()) for ad in d
                                   if (k, j, ad) not in kullanilan]
    V["uc_kaynak"] = dict(say, en_cok=UC_EN_COK, kural="rehber_gorunum.uc_isle (P10.7b2f)")
    return say


def yaz(V):
    open(os.path.join(VERI_DIR, "rehber-veri.json"), "w", encoding="utf-8").write(json.dumps(V, ensure_ascii=False, indent=0))
    open(os.path.join(VERI_DIR, "rehber-veri.js"), "w", encoding="utf-8").write(
        "window.REHBER_VERI=" + json.dumps(V, ensure_ascii=False, separators=(",", ":")) + ";\n")


def isle(yazma=False, sessiz=False):
    t0 = time.time()
    V = json.load(open(os.path.join(VERI_DIR, "rehber-veri.json"), encoding="utf-8"))
    rk = renk_isle(V)
    deg = alan_isle(V)
    M = Mesh(V)
    kayit = ev_isle(V, M)
    us = uc_isle(V, {pid: (q["bmin"], q["bmax"]) for pid, q in M.P.items()})   # P10.7b2f
    if not sessiz:
        print("gorunum: uc etiketi %d konumda %d etiket (karede), karede gorunmez uc %d" % (us["konum"], us["etiket"], us["yok"]))
    if not sessiz:
        d = rk["denetim"]
        print("gorunum: renk %d parca (CAD sirasi esles %d), GuiDocument kayitli %d, ayni %d, farkli %d, GuiDocument yok %d (%s)" % (
            rk["parca"], rk["veri_cad_eslesen"], d["gui_kayitli"], d["ayni"], len(d["farkli"]), d["gui_yok"], ",".join(d["gui_yok_modul"])))
        print("gorunum: rehber_metin alanlari, degisen %d%s" % (len(deg), (": " + ", ".join(deg[:12]) + (" ..." if len(deg) > 12 else "")) if deg else ""))
        ek = V["ev_kaynak"]
        print("gorunum: baglandigi yer %d / %d konumda, kaynak %s, bos %s (%.0f s)" % (
            ek["ev_bulunan"], ek["konum"], ek["kaynak"], ["%s %s" % (b["adres"], b["neden"]) for b in ek["bos"]], time.time() - t0))
    if not yazma:
        yaz(V)
    return V, kayit, deg


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--yazma", action="store_true", help="veriyi yazma, yalnız özet")
    ap.add_argument("--json", default="", help="konum başına ev kaydı bu dosyaya")
    g = ap.parse_args()
    V, kayit, deg = isle(yazma=g.yazma)
    if g.json:
        json.dump(dict(renk_kaynak=V["renk_kaynak"], ev_kaynak=V["ev_kaynak"], ev=kayit, alan_degisen=deg),
                  open(g.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
