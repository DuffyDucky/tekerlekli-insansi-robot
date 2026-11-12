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
GRUP_ALAN = ("ad", "is_", "kamera", "gizli_ok", "ucus_ok", "giris_ok", "piksel_ok")
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
        for n, (g, e) in enumerate(zip(sira, a["sira_grup"])):
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
