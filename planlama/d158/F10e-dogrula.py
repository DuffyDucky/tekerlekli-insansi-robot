# F10e doğrulama: gerçek renk, bağlandığı yer vurgusu, cıvata yeri işaretleri, okurun gördüğü pikselle görünürlük, önce / sonra kareleri.
#   py -3 -X utf8 planlama/d158/F10e-dogrula.py                 # -> planlama/d158/F10e-dogrula.json + F10e-goruntu-*.png
#   py -3 -X utf8 planlama/d158/F10e-dogrula.py --goruntu-yok
# FreeCAD istemez. Tarayıcı: Chrome DevTools protokolü (F10a-dogrula.py'nin Cdp sınıfı), file://, 1400 × 900, ?cekim=1.
# Ölçtükleri (her biri JSON'da "yontem" metniyle):
#   1) renk_cad: veri (parcalar[].gr) ↔ CAD. CAD rengi rehber_gorunum.cad_parcalar() ile FCStd'den yeniden okunur (Document.xml "Renk"
#      özelliği × modülün gorsel betiğindeki RENK tablosu); ayrıca FCStd GuiDocument.xml'de kayıtlı yayınık renkle parça parça.
#   2) renk_sahne: her konumda (50 adım + alt adımlar) sahnede yeni çizilen her parçanın malzeme rengi (RehberTest.renkler, sRGB) =
#      verideki rengi (kablo: renk, öbürleri: gr). Bütün parçalar en az bir konumda yeni: 1192 parçanın her biri sayılır.
#      P10.7b1 üretim uyumu (S3): kablo parçasında beklenen, etkin temanın tonu (veri rt[tema], rehber_kablo.TEMA_TON); ton yoksa renk.
#   3) renk_demo: tasarım demosunun (tasarim/Robot-Tasarim-Demosu.html) bir parçaya verdiği renk = sayfadaki TUR tablosu × verideki r
#      (sayfanın renkOf kuralı; sayfa render edilmez, three r128'i ağdan yükler) ↔ rehberin aynı parçaya verdiği renk (gerçek kip ve
#      sınıf kipi, sahneden okunur). Örneklem: parça listesinde her 30. parça (≥ 30 parça).
#   4) karsitlik: iki temada her konumda yeni parça rengi ile zemin (--sahne) arasındaki WCAG karşıtlık oranı; KENAR_ESIK (3,0) altında
#      kalan her yeni parçanın kenar çizgisi olmalı; saydam çizilen yeni parçanın da. Ton ayrımı: bağlandığı yer tonu, seçim yeşili ve
#      küçük görünüm kehribarı ile verideki her gerçek renk arasındaki en küçük CIELAB ΔE76.
#   5) ev: her konumda (bağlandığı yer verisi olan) sahnede ev tonunda ya da ev kenarlı ≥ 1 parça; doğruluk: verideki her (konum, ev
#      parçası) çifti için yeni bağlantı elemanının (yoksa yeni ana parçanın) köşe noktalarından ev parçasının üçgenlerine en kısa uzaklık
#      ≤ EV_UZAK mm (nokta–üçgen, robot.glb; rehber_gorunum'un ışın paritesinden bağımsız ikinci yöntem). Masa tabanı (yeni) ayrı sayılır.
#   6) isaret: her konumda işaret listesi = o konumda yeni (durum "simdi") bağlantı elemanı sayısı (verinin durum kuralı, Python), küme
#      adetleri toplamı = liste (her işaret karede), SVG'deki halka sayısı = küme sayısı. Panel satırı tıklanınca seçili halka > 0.
#   7) gorunurluk: kabuk adımlarının (31, 33, 34, 35, 36, 49) alt adımlarında, açık ve koyu temada, her yeni parça için
#      RehberTest.gorunurlukFark: parça gizlenip sahne sayfanın tuvaline yeniden çizilir (ekrana giden çizim: gerçek malzeme, saydamlık,
#      kenar çizgileri, sRGB çıktı), güvenli alanda Σ|ΔRGB| > 24 olan piksel sayılır. Ölçüt F10d'ninkiyle aynı eşik: ≥ 30 px ve
#      ≥ 0,20 × yalnız (parça tek başına, kimlik tamponu). İstisna yalnız grubun piksel_ok gerekçesi. Isıl gömmeler (hazırlıkta takılı,
#      burada yalnız sayılır) ayrı listelenir. Düzeltme 1: iki tema geçme şartında; ölçüm render target yerine tuvalde (render target
#      çıktısı doğrusaldı, ekrandan farklı sayı veriyordu).
#   8) arayuz: renk kipi düğmesi / C tuşu, işaret düğmesi / I tuşu, ?renk= ve ?isaret= adresleri, kare başlığı (benzer çiftler).
#   9) kareler: zor 8 alt adım önce (HEAD rehber/) / sonra yan yana (açık + koyu), benzer çiftler yan yana.
import os, sys, json, time, re, math, subprocess, tempfile, shutil, argparse, importlib.util, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(HERE))
REHBER = os.path.join(ROBOT, "rehber")
REH_PY = os.path.join(ROBOT, "tasarim", "freecad", "rehber")
sys.path.insert(0, REH_PY)
_s = importlib.util.spec_from_file_location("f10a_dogrula", os.path.join(HERE, "F10a-dogrula.py"))
F10A = importlib.util.module_from_spec(_s)
_s.loader.exec_module(F10A)
Cdp, tarayici, url = F10A.Cdp, F10A.tarayici, F10A.url
import rehber_gorunum as G

V = json.load(open(os.path.join(REHBER, "veri", "rehber-veri.json"), encoding="utf-8"))
A, P = V["adimlar"], V["parcalar"]
PID = {p["id"]: p for p in P}
GH = {a["i"]: G.grup_harita(a) for a in A}
KONUM = G.konumlar(A)
KABUK = (31, 33, 34, 35, 36, 49)
ZOR8 = ("31.5", "31.9", "31.10", "34.4", "34.6", "34.7", "35.3", "36.3")     # F10d'nin "zor" dediği 8 alt adım
CIFT = (("34.3", "34.5"), ("34.4", "34.6"), ("49.3", "49.4"))
SOLUK = {"31.3": "p0762", "34.7": "p0440"}                                       # F10d'de kimlik tamponunda soluk kalan iki parça
PX_ESIK, ORAN_ESIK, FARK_ESIK = 30, 0.20, 24
EV_UZAK = 1.0
KENAR_ESIK = 3.0
CIKTI = os.path.join(HERE, "F10e-dogrula.json")


def adr(s, j):
    return "%d.%d" % (s, j) if j else str(s)


# ------------------------------------------------------------------ renk yardımcıları
def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def parlaklik(h):
    r, g, b = (_lin(x) for x in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def karsitlik(a, b):
    la, lb = parlaklik(a), parlaklik(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def lab(h):
    r, g, b = (_lin(x) for x in rgb(h))
    X = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    Y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    Z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return 116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))


def de76(a, b):
    return math.dist(lab(a), lab(b))


def appjs_sabit(ad):
    t = open(os.path.join(REHBER, "app.js"), encoding="utf-8").read()
    m = re.search(r"\b%s\s*=\s*\"(#[0-9a-fA-F]{6})\"" % ad, t)
    return m.group(1).lower() if m else None


# ------------------------------------------------------------------ 1) veri ↔ CAD
def renk_cad():
    C = G.cad_parcalar()
    esit = sum(1 for c, p in zip(C, P) if c["renk"] == p.get("gr"))
    sira = sum(1 for c, p in zip(C, P) if c["modul"] == p["modul"] and c["tur"] == p["tur"])
    gui = [(c, p) for c, p in zip(C, P) if c["gui"]]
    gui_esit = sum(1 for c, p in gui if c["gui"] == p.get("gr"))
    say = collections.Counter(p.get("gr") for p in P)
    return dict(yontem="CAD rengi rehber_gorunum.cad_parcalar() ile FCStd'den yeniden okunur (Document.xml Renk özelliği × gorsel betiğinin "
                       "RENK tablosu); ayrıca GuiDocument.xml yayınık rengi", cad=len(C), veri=len(P), sira_eslesen=sira, esit=esit,
                gui_kayitli=len(gui), gui_esit=gui_esit, farkli_renk=len(say),
                renkler=[dict(renk=k, adet=n) for k, n in say.most_common()],
                gecti=len(C) == len(P) == esit == sira and gui_esit == len(gui))


# ------------------------------------------------------------------ 5) ev doğruluğu (nokta–üçgen uzaklık, numpy)
def _nokta_ucgen(np, Pn, T):
    """Pn (n, 3) noktalarının T (m, 3, 3) üçgenlerine en kısa uzaklığı (Ericson, en yakın nokta), n'nin her biri için en küçük."""
    a, b, c = T[:, 0][None], T[:, 1][None], T[:, 2][None]
    p = Pn[:, None, :]
    ab, ac, ap = b - a, c - a, p - a
    d1, d2 = (ab * ap).sum(-1), (ac * ap).sum(-1)
    bp = p - b; d3, d4 = (ab * bp).sum(-1), (ac * bp).sum(-1)
    cp = p - c; d5, d6 = (ab * cp).sum(-1), (ac * cp).sum(-1)
    va = d3 * d6 - d5 * d4; vb = d5 * d2 - d1 * d6; vc = d1 * d4 - d3 * d2
    den = va + vb + vc
    den = np.where(np.abs(den) < 1e-18, 1e-18, den)
    v = vb / den; w = vc / den
    q = a + ab * v[..., None] + ac * w[..., None]                                   # iç bölge
    # kenar ve köşe bölgeleri
    m = (d1 <= 0) & (d2 <= 0); q = np.where(m[..., None], a, q)
    m = (d3 >= 0) & (d4 <= d3); q = np.where(m[..., None], b, q)
    m = (d6 >= 0) & (d5 <= d6); q = np.where(m[..., None], c, q)
    vv = d1 / np.where(np.abs(d1 - d3) < 1e-18, 1e-18, d1 - d3)
    m = (vc <= 0) & (d1 >= 0) & (d3 <= 0); q = np.where(m[..., None], a + ab * vv[..., None], q)
    ww = d2 / np.where(np.abs(d2 - d6) < 1e-18, 1e-18, d2 - d6)
    m = (vb <= 0) & (d2 >= 0) & (d6 <= 0); q = np.where(m[..., None], a + ac * ww[..., None], q)
    w2 = (d4 - d3) / np.where(np.abs((d4 - d3) + (d5 - d6)) < 1e-18, 1e-18, (d4 - d3) + (d5 - d6))
    m = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0); q = np.where(m[..., None], b + (c - b) * w2[..., None], q)
    return np.sqrt(((p - q) ** 2).sum(-1)).min(1)


def en_kisa(M, kaynak, hedef, nmax=600):
    """kaynak parçanın köşelerinden (en çok nmax) hedef parçanın üçgenlerine en kısa uzaklık (mm); sınır kutuları 5 mm'den uzaksa None."""
    np = M.np
    pk, ph = M.P[kaynak], M.P[hedef]
    if np.any(pk["bmin"] - 5 > ph["bmax"]) or np.any(ph["bmin"] - 5 > pk["bmax"]):
        return None
    pts = pk["v"]
    if len(pts) > nmax:
        pts = pts[np.linspace(0, len(pts) - 1, nmax).astype(int)]
    T = ph["v"][ph["f"]]
    lo, hi = pts.min(0) - 2, pts.max(0) + 2
    tl, th = T.min(1), T.max(1)
    T = T[np.all(th >= lo, 1) & np.all(tl <= hi, 1)]
    if not len(T):
        return None
    en = math.inf
    for k in range(0, len(T), 1500):
        en = min(en, float(_nokta_ucgen(np, pts, T[k:k + 1500]).min()))
    return en


def ev_dogruluk():
    M = G.Mesh(V)
    out = []
    for s, j in KONUM:
        if s == 0:
            continue
        st = A[s]
        hedef = st["sira_grup"][j - 1] if j else st
        ev = hedef.get("ev") or []
        if not ev:
            continue
        d = {p["id"]: G.durum(p, s, j, A, GH) for p in P}
        yeni_bag = [i for i, x in d.items() if x == "simdi" and PID[i]["tur"] == "Baglanti"]
        yeni_ana = [i for i, x in d.items() if x in ("simdi", "alt") and PID[i]["tur"] not in ("Baglanti", "Referans") and not PID[i].get("renk")]
        for q in ev:
            if d.get(q) in ("simdi", "alt"):
                out.append(dict(adres=adr(s, j), ev=q, ad=PID[q]["ad"], tur="masa tabanı (yeni)", uzaklik=None, yol=None, dogru=None))
                continue
            # kaynak: yeni bağlantı elemanları ve yeni ana parçalar (veri, halka bulunmazsa yüzey temasına düşer: ör. adım 8 teker → motor)
            kaynak = [i for i in yeni_bag + yeni_ana if i in M.P]
            u = [x for x in (en_kisa(M, i, q) for i in kaynak) if x is not None]
            en = min(u) if u else None
            yol = "doğrudan" if en is not None and en <= EV_UZAK else None
            if not yol:                                     # köşesi ev parçasının içinde (delik modellenmemiş: vida gövdenin içinde)
                for i in kaynak:
                    v = M.P[i]["v"]
                    v = v[M.np.linspace(0, len(v) - 1, min(len(v), 300)).astype(int)]
                    if int(M.icinde(v, q).sum()) >= 3:
                        yol = "içinde"
                        break
            if not yol and yeni_bag:                        # ara bağlantı elemanı üzerinden (ısıl gömme, somun: cıvata ↔ ara ≤ 1, ara ↔ ev ≤ 1)
                ara = [x for x in M.P if PID[x]["tur"] == "Baglanti" and x not in kaynak and d.get(x) in ("onceki", "simdi", "alt")]
                for i in kaynak:
                    for x in ara:
                        a1 = en_kisa(M, i, x, 300)
                        if a1 is None or a1 > EV_UZAK:
                            continue
                        a2 = en_kisa(M, x, q, 300)
                        if a2 is not None and a2 <= EV_UZAK:
                            yol = "ara: " + PID[x]["ad"][:40]
                            break
                    if yol:
                        break
            out.append(dict(adres=adr(s, j), ev=q, ad=PID[q]["ad"], tur="bağlantı elemanı + yeni ana parça",
                            uzaklik=None if en is None else round(en, 3), yol=yol, dogru=bool(yol)))
    olc = [x for x in out if x["dogru"] is not None]
    return dict(yontem="her (konum, ev) çifti: konumun yeni bağlantı elemanlarının ve yeni ana parçalarının köşe noktalarından (parça başına en çok "
                       "600) ev parçasının üçgenlerine en kısa nokta–üçgen uzaklığı ≤ %.1f mm (doğrudan); değilse köşelerinin en az 3'ü ev "
                       "parçasının içinde (delik modellenmemiş); değilse araya giren bir bağlantı elemanı (ısıl gömme, somun) üzerinden iki "
                       "uzaklık da ≤ %.1f mm. robot.glb dünya koordinatı" % (EV_UZAK, EV_UZAK),
                cift=len(out), olculen=len(olc), dogru=sum(1 for x in olc if x["dogru"]), masa_tabani=len(out) - len(olc),
                yol=dict(collections.Counter((x["yol"] or "yok").split(":")[0] for x in olc)),
                yanlis=[x for x in olc if not x["dogru"]], olcum=out, gecti=all(x["dogru"] for x in olc))


# ------------------------------------------------------------------ tarayıcı ölçümleri
def yeni_bag_say(s, j):
    return sum(1 for p in P if p.get("r") == "baglanti" and G.durum(p, s, j, A, GH) == "simdi")


def sahne_tara(c):
    """Her konumda iki temada RehberTest.renkler() (gerçek kip), açık temada isaretler()."""
    sonuc = {}
    for tema in ("light", "dark"):
        for s, j in KONUM:
            c.git(url(REHBER, "?adim=%s&cekim=1&tema=%s&renk=gercek&isaret=1" % (adr(s, j), tema)))
            r = c.js("RehberTest.renkler()")
            r["hata"] = c.js("document.documentElement.dataset.hata || null")
            if tema == "light":
                r["isaret"] = c.js("RehberTest.isaretler()")
            sonuc[(tema, s, j)] = r
    return sonuc


def beklenen_renk(p, tema):
    """P10.7b1 üretim uyumu (S3): kablo parçası sahnede etkin temanın tonuyla çizilir (veri rt[tema]; tek kaynak rehber_kablo.TEMA_TON,
    rehber_kablo.py --veri tablodan denetler); ton yoksa sınıf rengi (renk). Öbür parçalar gerçek renk (gr)."""
    if p.get("renk"):
        return ((p.get("rt") or {}).get(tema) or p["renk"]).lower()
    return p["gr"].lower()


def renk_sahne(T):
    gor, esit, yanlis = set(), set(), []
    for (tema, s, j), r in T.items():
        if tema != "light":
            continue
        for i, x in r["parca"].items():
            if x["d"] not in ("simdi", "alt"):
                continue
            bek = beklenen_renk(PID[i], tema)
            gor.add(i)
            if x["renk"].lower() == bek:
                esit.add(i)
            else:
                yanlis.append(dict(adres=adr(s, j), id=i, sahne=x["renk"], veri=bek))
    return dict(yontem="her konumda (açık tema, ?renk=gercek) sahnede yeni çizilen parçanın malzeme rengi (sRGB) = veri (kablo: temanın tonu "
                       "rt[tema], yoksa renk; öbürleri: gr)",
                parca=len(P), yeni_gorulen=len(gor), esit=len(esit - {y["id"] for y in yanlis}), yanlis=yanlis[:20], yanlis_sayi=len(yanlis),
                gecti=len(gor) == len(P) and not yanlis)


def onceki_gri():
    t = open(os.path.join(REHBER, "app.js"), encoding="utf-8").read()
    m = re.search(r'SINIF\.onceki\[0\]\s*=\s*tema\(\)\s*===\s*"dark"\s*\?\s*"(#[0-9a-fA-F]{6})"\s*:\s*"(#[0-9a-fA-F]{6})"', t)
    o = re.search(r"\bONCEKI_ESIK\s*=\s*([0-9.]+)", t)
    return dict(dark=m.group(1).lower(), light=m.group(2).lower()), float(o.group(1)) if o else None


def karsitlik_olc(T):
    out = {}
    gri, oesik = onceki_gri()
    for tema in ("light", "dark"):
        alt, kenarsiz, saydam_kenarsiz, oran = 0, [], [], []
        gri_yakin, gri_kenarsiz = 0, []
        zemin = None
        for (tm, s, j), r in T.items():
            if tm != tema:
                continue
            zemin = r["zemin"]
            for i, x in r["parca"].items():
                if x["d"] not in ("simdi", "alt"):
                    continue
                k = karsitlik(x["renk"], r["zemin"])
                oran.append(k)
                if k < KENAR_ESIK:
                    alt += 1
                    if not x["kenar"]:
                        kenarsiz.append(dict(adres=adr(s, j), id=i, renk=x["renk"], oran=round(k, 2)))
                if x["opak"] < 1 and not x["kenar"]:
                    saydam_kenarsiz.append(dict(adres=adr(s, j), id=i, renk=x["renk"], opak=x["opak"]))
                if oesik and karsitlik(x["renk"], gri[tema]) < oesik:
                    gri_yakin += 1
                    if not x["kenar"]:
                        gri_kenarsiz.append(dict(adres=adr(s, j), id=i, renk=x["renk"]))
        renkler = sorted({(PID[p["id"]].get("renk") or p["gr"]).lower() for p in P})
        esik_alti = [h for h in renkler if karsitlik(h, zemin) < KENAR_ESIK]
        out[tema] = dict(zemin=zemin, yeni_parca_konum=len(oran), esik_alti=alt, esik_alti_kenarsiz=len(kenarsiz), kenarsiz=kenarsiz[:20],
                         saydam_kenarsiz=len(saydam_kenarsiz), saydam_kenarsiz_ornek=saydam_kenarsiz[:10],
                         onceki_gri=gri[tema], onceki_esik=oesik, onceki_yakin=gri_yakin, onceki_yakin_kenarsiz=len(gri_kenarsiz),
                         renk_sayisi=len(renkler), esik_alti_renk=esik_alti,
                         en_kucuk_oran=round(min(oran), 2) if oran else None,
                         gecti=not kenarsiz and not saydam_kenarsiz and not gri_kenarsiz)
    ev = appjs_sabit("EV_RENK")
    sec = appjs_sabit("VURGU_ANA")
    keh = appjs_sabit("KONUM_RENK")
    renkler = sorted({p["gr"].lower() for p in P if not p.get("renk")})
    ton = {}
    for ad, h in (("ev", ev), ("secim", sec), ("kucuk_gorunum", keh)):
        if not h:
            ton[ad] = None
            continue
        en = min(renkler, key=lambda x: de76(h, x))
        ton[ad] = dict(renk=h, en_yakin=en, de76=round(de76(h, en), 1),
                       zemin_karsitlik=dict(light=round(karsitlik(h, out["light"]["zemin"]), 2), dark=round(karsitlik(h, out["dark"]["zemin"]), 2)))
    return dict(yontem="WCAG göreli parlaklık karşıtlık oranı (yeni parça rengi ↔ --sahne); eşik %.1f altı kenar çizgisi ister; saydam "
                       "çizilen yeni parça kenar ister. Ton: CIELAB ΔE76 (D65)" % KENAR_ESIK, esik=KENAR_ESIK, tema=out, ton=ton,
                gecti=out["light"]["gecti"] and out["dark"]["gecti"])


def ev_sahne(T):
    out, eksik = 0, []
    for (tema, s, j), r in T.items():
        if tema != "light" or s == 0:
            continue
        st = A[s]
        hedef = st["sira_grup"][j - 1] if j else st
        if not (hedef.get("ev") or []):
            continue
        out += 1
        if not r["ev"]:
            eksik.append(adr(s, j))
    bos = [b["adres"] for b in V["ev_kaynak"]["bos"]]
    kabuk = [(s, j) for s, j in KONUM if s in KABUK and j]
    kabuk_yeni = [(s, j) for s, j in kabuk if any(G.durum(p, s, j, A, GH) in ("simdi", "alt") for p in P)]
    kabuk_ev = sum(1 for s, j in kabuk_yeni if T[("light", s, j)]["ev"])
    return dict(konum=len(KONUM) - 1, veride_ev=out, sahnede_ev=out - len(eksik), eksik=eksik, bos=bos, kabuk_alt_adim=len(kabuk),
                kabuk_yeni_parcali=len(kabuk_yeni), kabuk_ev=kabuk_ev,
                kabuk_yeni_parcasiz=[adr(s, j) for s, j in kabuk if (s, j) not in kabuk_yeni],
                kaynak=V["ev_kaynak"]["kaynak"], gecti=not eksik and kabuk_ev == len(kabuk_yeni))


def isaret_olc(T):
    out, kotu = [], []
    for (tema, s, j), r in T.items():
        if tema != "light":
            continue
        I = r["isaret"]
        bek = yeni_bag_say(s, j)
        n_kume = sum(k["n"] for k in I["kume"])
        x = dict(adres=adr(s, j), beklenen=bek, liste=len(I["liste"]), kumede=n_kume, kume=len(I["kume"]), dom=I["dom"])
        x["gecti"] = bool(I["acik"] and x["liste"] == bek and n_kume == bek and I["dom"] == len(I["kume"]))
        out.append(x)
        if not x["gecti"]:
            kotu.append(x)
    kabuk = [x for x in out if int(x["adres"].split(".")[0]) in KABUK and "." in x["adres"]]
    return dict(yontem="işaret listesi = konumda yeni (durum simdi) bağlantı elemanı sayısı (Python durum kuralı); küme adetleri toplamı = "
                       "liste (her işaret tuvalde); SVG halka sayısı = küme sayısı", konum=len(out),
                toplam_beklenen=sum(x["beklenen"] for x in out), toplam_isaret=sum(x["kumede"] for x in out),
                kabuk_beklenen=sum(x["beklenen"] for x in kabuk), kabuk_isaret=sum(x["kumede"] for x in kabuk),
                kabuk_kume=sum(x["kume"] for x in kabuk), kotu=kotu, olcum=out, gecti=not kotu)


def renk_demo(c):
    t = open(os.path.join(ROBOT, "tasarim", "Robot-Tasarim-Demosu.html"), encoding="utf-8").read()
    m = re.search(r"var TUR=\{(.*?)\};", t, re.S)
    TUR = {k: v.lower() for k, v in re.findall(r"(\w+):\[\"(#[0-9a-fA-F]{6})\"", m.group(1))}
    orn = [p for n, p in enumerate(P) if n % 30 == 0]
    rehber = {}
    for kip in ("gercek", "sinif"):
        rk = {}
        for p in orn:
            s, j = p["a"], 0
            j = next((jj for jj in range(1, (A[s].get("alt") or 0) + 1) if G.durum(p, s, jj, A, GH) in ("simdi", "alt")), 0) if A[s].get("alt") else 0
            c.git(url(REHBER, "?adim=%s&cekim=1&tema=light&renk=%s" % (adr(s, j), kip)))
            x = c.js("RehberTest.renkler()")["parca"].get(p["id"])
            rk[p["id"]] = x["renk"].lower() if x else None
        rehber[kip] = rk
    sat = []
    for p in orn:
        d = TUR.get(p["r"], TUR.get("ref"))
        sat.append(dict(id=p["id"], ad=p["ad"], r=p["r"], demo=d, gercek=rehber["gercek"][p["id"]], sinif=rehber["sinif"][p["id"]],
                        veri_gr=p["gr"]))
    eg = sum(1 for x in sat if x["gercek"] == x["demo"])
    es = sum(1 for x in sat if x["sinif"] == x["demo"])
    sinif_tablo = {}
    for x in sat:
        sinif_tablo.setdefault(x["r"], dict(demo=x["demo"], rehber_sinif=x["sinif"]))
    return dict(yontem="demo rengi = Robot-Tasarim-Demosu.html TUR tablosu × veri r (renkOf kuralı; sayfa render edilmedi: three r128 "
                       "ağdan); rehber rengi sahneden (RehberTest.renkler), parçanın yeni olduğu konumda", ornek=len(sat),
                demo_tur=TUR, gercek_esit=eg, sinif_esit=es, sinif_tablo=sinif_tablo, ornekler=sat,
                gecti=eg == len(sat), not_="demoda gerçek renk kipi yok; renkler ancak demo_uret.py / sayfa değişirse eşitlenir (karar)")


def satir_ids(st, g):
    out = []
    for k in g["satir"]:
        t, i = k.split(":")
        out += (st["parcalar"] if t == "p" else st["baglantilar"])[int(i)]["ids"]
    return out + list(g.get("ref") or [])


def gorunurluk(c):
    """F10d'nin ayrımı: alt adımın kendi satırlarındaki her yeni parça ölçütü geçmeli (istisna: grubun piksel_ok gerekçesi); bağlanan masa
    birimi (durum "alt"): birimin en büyük parçası (yalnız pikseline göre) ölçütü geçmeli, iç parçaları masada yeni oldukları alt adımın
    ölçümüyle (orada görünmüş olmalı)."""
    # F10e düzeltme 1 (kontrol bulgu 1): iki temada ölçülür, ikisi de geçme şartında (önceden yalnız açık tema)
    out = []
    for tema in TEMALAR:
        out += _gorunurluk_tema(c, tema)
    soluk = {}
    for tema in TEMALAR:
        for a, i in SOLUK.items():
            x = next((y for y in out if y["adres"] == a and y["tema"] == tema), None)
            r = next((y for y in (x or {}).get("parca", []) if y["id"] == i), None)
            soluk["%s %s" % (a, tema)] = dict(id=i, ad=PID[i]["ad"], fark=r and r["fark"], yalniz=r and r["yalniz"], gorunur=bool(r and r["gorunur"]))
    ozet = {}
    for tema in TEMALAR:
        o = [x for x in out if x["tema"] == tema]
        ozet[tema] = dict(alt_adim=len(o), yeni=sum(x["yeni"] for x in o), gorunmeyen=sum(len(x["gorunmeyen"]) for x in o),
                          gomme_gorunmeyen=sum(len(x["gomme"]) for x in o), istisna=sum(len(x["istisna"]) for x in o),
                          birim_gorunmeyen=sum(1 for x in o if x["birim"] and not x["birim"]["gorunur"]),
                          kalan=[(x["adres"], y["id"], y["fark"], y["yalniz"]) for x in o for y in x["gorunmeyen"]],
                          gomme=[(x["adres"], y["id"], y["fark"], y["yalniz"]) for x in o for y in x["gomme"]],
                          gecti=all(x["gecti"] for x in o))
    return dict(yontem="RehberTest.gorunurlukFark: parça gizlenip sayfanın tuvaline yeniden çizilir (ekrana giden çizimin kendisi: gerçek malzeme, "
                       "saydamlık, kenar çizgileri, sRGB çıktı, tuvalin kenar yumuşatması; 1400 × 900), güvenli alanda Σ|ΔRGB| > %d piksel; ölçüt "
                       "≥ %d px ve ≥ %.2f × yalnız (kimlik tamponu, parça tek başına). İki tema. " % (FARK_ESIK, PX_ESIK, ORAN_ESIK)
                       + gorunurluk.__doc__.strip(),
                esik=dict(fark=FARK_ESIK, piksel=PX_ESIK, oran=ORAN_ESIK), tema=ozet, soluk=soluk, olcum=out,
                # geçme şartı (düzeltme 1): iki temada bütün kabuk alt adımları (gerekçesiz eşik altı yeni parça 0; ısıl gömmeler ayrı
                # sayılır) ve F10d'nin soluk bulduğu iki parça iki temada ölçütü geçer
                tam_gecti=all(v["gecti"] for v in ozet.values()),
                gecti=all(v["gecti"] for v in ozet.values()) and all(v["gorunur"] for v in soluk.values()))


TEMALAR = ("light", "dark")
GOR_EK = ""                       # ek sorgu (ör. "&ustte=0": düzeltme öncesi çizimle karşılaştırma); tam koşuda boş


def _gorunurluk_tema(c, tema):
    out = []
    ad = {p["id"]: p["ad"] for p in P}
    olc = {}
    for s in KABUK:
        st = A[s]
        for j in range(1, (st.get("alt") or 0) + 1):
            ok = c.git(url(REHBER, "?adim=%s&cekim=1&tema=%s%s" % (adr(s, j), tema, GOR_EK)))
            f = c.js("RehberTest.gorunurlukFark()") or {}
            g = c.js("RehberTest.gorunurluk()") or {}
            olc[(s, j)] = (ok, f.get("piksel") or {}, g.get("yalniz") or {}, g.get("piksel") or {})
    gor = lambda f, y: bool(f >= PX_ESIK and f >= ORAN_ESIK * max(y, 1))
    for (s, j), (ok, px, yal, kid) in olc.items():
        st = A[s]
        grp = st["sira_grup"][j - 1]
        kendi = set(satir_ids(st, grp))
        pok = grp.get("piksel_ok") or {}
        parca, kalan, istisna, gomme = [], [], [], []
        for i in sorted(px):
            if i.startswith("sema") or i not in kendi:
                continue
            y = yal.get(i, 0)
            r = dict(id=i, ad=ad[i], fark=px[i], kimlik=kid.get(i), yalniz=y, oran=round(px[i] / max(y, 1), 3), gorunur=gor(px[i], y))
            parca.append(r)
            if r["gorunur"]:
                continue
            ger = next((v for k, v in pok.items() if k in ad[i]), None)
            if ger:
                istisna.append(dict(r, gerekce=ger))
            else:
                (gomme if G.bag_tipi(PID[i]) == "gomme" else kalan).append(r)
        birim = None
        alt_ids = [i for i in px if not i.startswith("sema") and i not in kendi]
        if grp.get("bag") and alt_ids:
            en = max(alt_ids, key=lambda i: yal.get(i, 0))
            ic = []
            for i in alt_ids:
                if gor(px[i], yal.get(i, 0)):
                    continue
                n0 = next((n for n, x in enumerate(st["sira_grup"]) if i in satir_ids(st, x)), None)
                o0 = olc.get((s, n0 + 1)) if n0 is not None else None
                f0 = o0[1].get(i) if o0 else None
                y0 = o0[2].get(i) if o0 else None
                ic.append(dict(id=i, ad=ad[i], fark=px[i], masada="%d.%d" % (s, n0 + 1) if n0 is not None else None, masada_fark=f0,
                               masada_yalniz=y0, masada_gorunur=bool(f0 is not None and gor(f0, y0 or 0)),
                               gomme=G.bag_tipi(PID[i]) == "gomme"))
            birim = dict(en_buyuk=ad[en], fark=px[en], yalniz=yal.get(en, 0), gorunur=gor(px[en], yal.get(en, 0)), parca=len(alt_ids),
                         ic_gorunmeyen=ic)
        bk = birim is None or (birim["gorunur"] and all(x["masada_gorunur"] or x["gomme"] for x in birim["ic_gorunmeyen"]))
        out.append(dict(adres=adr(s, j), tema=tema, hazir=ok, yeni=len(parca), gorunmeyen=kalan, gomme=gomme, istisna=istisna, birim=birim,
                        parca=parca, gecti=bool(ok and not kalan and bk)))
    return out


def arayuz(c):
    r = {}
    c.git(url(REHBER, "?adim=34.4&tema=light"), cekim=False)
    c.bekle("!RehberTest.anim()", 15)
    k0 = c.js("RehberTest.renkKip()")
    b0 = c.js("document.getElementById('renk-dugme') ? document.getElementById('renk-dugme').textContent.trim() : null")
    c.tus("c", "KeyC", 67)
    k1 = c.js("RehberTest.renkKip()")
    rs = c.js("(function(){var r=RehberTest.renkler().parca,n=0;for(var k in r){if(r[k].d==='simdi')n++;}return n;})()")
    c.tus("c", "KeyC", 67)
    k2 = c.js("RehberTest.renkKip()")
    r["renk_kip"] = dict(varsayilan=k0, dugme=b0, c_tusu=k1, c_iki=k2, gecti=k0 == "gercek" and k1 == "sinif" and k2 == "gercek")
    i0 = c.js("RehberTest.isaretler().dom")
    c.tus("i", "KeyI", 73)
    i1 = c.js("RehberTest.isaretler().dom")
    c.tus("i", "KeyI", 73)
    i2 = c.js("RehberTest.isaretler().dom")
    r["isaret_tus"] = dict(acik=i0, kapali=i1, yeniden=i2, gecti=i0 > 0 and i1 == 0 and i2 == i0)
    c.js("(function(){var e=document.querySelector(\"#baglantilar [data-satir^='b:'], #parcalar [data-satir^='b:']\");if(e)e.click();})()")
    time.sleep(0.3)
    sel = c.js("RehberTest.isaretler()")
    r["satir_secim"] = dict(secili_halka=sel["dom_secili"], kume=len(sel["kume"]), gecti=sel["dom_secili"] > 0)
    c.git(url(REHBER, "?adim=34.4&tema=light&renk=sinif&isaret=0"), cekim=False)
    r["adres"] = dict(renk=c.js("RehberTest.renkKip()"), isaret=c.js("RehberTest.isaretler().acik"))
    r["adres"]["gecti"] = r["adres"]["renk"] == "sinif" and r["adres"]["isaret"] is False
    bas = {}
    for a, b in CIFT:
        x = []
        for q in (a, b):
            # kare başlığı yalnız yazdırma / PDF karesinde (?sahne=1); etkileşimli sayfada panel başlığı (F10d görünürlüğü, günlük §2)
            c.git(url(REHBER, "?adim=%s&sahne=1&cekim=1&tema=light" % q))
            x.append(c.js("RehberTest.kareBaslik()"))
        bas["%s/%s" % (a, b)] = dict(baslik=x, farkli=bool(x[0] and x[1] and x[0] != x[1]))
    r["kare_baslik"] = dict(cift=bas, gecti=all(v["farkli"] for v in bas.values()))
    c.git(url(REHBER, "?adim=0&tema=light"), cekim=False)
    r["gecti"] = all(v["gecti"] for v in r.values() if isinstance(v, dict) and "gecti" in v)
    return r


def head_kopya():
    tmp = tempfile.mkdtemp(prefix="lale-f10e-head-")
    kok = os.path.join(tmp, "rehber")
    os.makedirs(os.path.join(kok, "veri")); os.makedirs(os.path.join(kok, "vendor"))
    for f in ("index.html", "app.js", "stil.css", "veri/rehber-veri.js", "veri/robot-glb.js"):
        b = subprocess.run(["git", "show", "HEAD:rehber/" + f], cwd=ROBOT, capture_output=True).stdout
        open(os.path.join(kok, f), "wb").write(b)
    shutil.copy2(os.path.join(REHBER, "vendor", "three-0.160.0-paket.min.js"), os.path.join(kok, "vendor"))
    return tmp, kok


def kareler(c):
    from PIL import Image, ImageDraw
    c.boyut(1400, 900)
    liste = []
    tmp, head = head_kopya()
    gt = tempfile.gettempdir()
    try:
        for a in ZOR8:
            for tema, ad in (("light", "acik"), ("dark", "koyu")):
                im = []
                for kok in (head, REHBER):
                    y = os.path.join(gt, "f10e-kare.png")
                    c.git(url(kok, "?adim=%s&cekim=1&tema=%s" % (a, tema)))
                    c.goruntu(y)
                    im.append(Image.open(y).convert("RGB").resize((1050, 675)))
                yer = Image.new("RGB", (2100, 715), (255, 255, 255) if tema == "light" else (20, 20, 22))
                yer.paste(im[0], (0, 40)); yer.paste(im[1], (1050, 40))
                d = ImageDraw.Draw(yer)
                rk = (0, 0, 0) if tema == "light" else (230, 230, 230)
                d.text((10, 12), "ONCE (HEAD, F10d): %s" % a, fill=rk)
                d.text((1060, 12), "SONRA (F10e): %s" % a, fill=rk)
                y = os.path.join(HERE, "F10e-goruntu-%s-once-sonra-%s.png" % (a.replace(".", "-"), ad))
                yer.save(y, optimize=True); liste.append(os.path.basename(y))
        for a, b in CIFT:
            im = []
            for q in (a, b):
                y = os.path.join(gt, "f10e-kare.png")
                c.git(url(REHBER, "?adim=%s&cekim=1&tema=light" % q))
                c.goruntu(y)
                im.append(Image.open(y).convert("RGB").resize((1050, 675)))
            yer = Image.new("RGB", (2100, 715), (255, 255, 255))
            yer.paste(im[0], (0, 40)); yer.paste(im[1], (1050, 40))
            d = ImageDraw.Draw(yer)
            d.text((10, 12), "BENZER CIFT (sonra): %s" % a, fill=(0, 0, 0)); d.text((1060, 12), "%s" % b, fill=(0, 0, 0))
            y = os.path.join(HERE, "F10e-goruntu-cift-%s-%s.png" % (a.replace(".", "-"), b.replace(".", "-")))
            yer.save(y, optimize=True); liste.append(os.path.basename(y))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return liste


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--goruntu-yok", action="store_true")
    g = ap.parse_args()
    t0 = time.time()
    sonuc = dict(tarih=time.strftime("%Y-%m-%d %H:%M"), konum=len(KONUM))
    print("renk: veri <-> CAD"); sonuc["renk_cad"] = rc = renk_cad()
    print("  CAD %d veri %d esit %d; GuiDocument %d / %d -> %s" % (rc["cad"], rc["veri"], rc["esit"], rc["gui_esit"], rc["gui_kayitli"], rc["gecti"]))
    print("ev dogrulugu (nokta-ucgen)"); sonuc["ev_dogruluk"] = ed = ev_dogruluk()
    print("  cift %d, olculen %d, dogru %d, masa tabani %d -> %s" % (ed["cift"], ed["olculen"], ed["dogru"], ed["masa_tabani"], ed["gecti"]))
    c = Cdp(tarayici(), "f10e")
    try:
        c.boyut(1400, 900)
        print("sahne taramasi (%d konum x 2 tema)" % len(KONUM)); T = sahne_tara(c)
        sonuc["konsol_hatasi"] = sorted({adr(s, j) for (tm, s, j), r in T.items() if r.get("hata")})
        sonuc["renk_sahne"] = rs = renk_sahne(T)
        print("  renk: yeni gorulen %d / %d, esit %d, yanlis %d -> %s" % (rs["yeni_gorulen"], rs["parca"], rs["esit"], rs["yanlis_sayi"], rs["gecti"]))
        sonuc["karsitlik"] = ks = karsitlik_olc(T)
        for tm in ("light", "dark"):
            x = ks["tema"][tm]
            print("  karsitlik %s: zemin %s, esik alti %d (kenarsiz %d), saydam kenarsiz %d, onceki griye yakin %d (kenarsiz %d), en kucuk %s" % (
                tm, x["zemin"], x["esik_alti"], x["esik_alti_kenarsiz"], x["saydam_kenarsiz"], x["onceki_yakin"], x["onceki_yakin_kenarsiz"],
                x["en_kucuk_oran"]))
        print("  ton:", json.dumps(ks["ton"], ensure_ascii=False))
        sonuc["ev"] = ev = ev_sahne(T)
        print("  ev: veride %d, sahnede %d, kabuk alt adim (yeni parcali) %d / %d, yeni parcasiz %s -> %s" % (
            ev["veride_ev"], ev["sahnede_ev"], ev["kabuk_ev"], ev["kabuk_yeni_parcali"], ev["kabuk_yeni_parcasiz"], ev["gecti"]))
        sonuc["isaret"] = isr = isaret_olc(T)
        print("  isaret: beklenen %d, isaret %d; kabuk %d / %d (kume %d); kotu %d -> %s" % (
            isr["toplam_beklenen"], isr["toplam_isaret"], isr["kabuk_isaret"], isr["kabuk_beklenen"], isr["kabuk_kume"], len(isr["kotu"]), isr["gecti"]))
        print("renk demo"); sonuc["renk_demo"] = rd = renk_demo(c)
        print("  ornek %d, gercek = demo %d, sinif = demo %d" % (rd["ornek"], rd["gercek_esit"], rd["sinif_esit"]))
        print("gorunurluk (gizle-fark)"); sonuc["gorunurluk"] = gr = gorunurluk(c)
        for x in gr["olcum"]:
            b = x["birim"]
            bk = [(y["id"], y["masada"], y["masada_fark"]) for y in (b or {}).get("ic_gorunmeyen", []) if not y["masada_gorunur"] and not y["gomme"]]
            if x["gorunmeyen"] or x["gomme"] or x["istisna"] or bk or (b and not b["gorunur"]):
                print("  %-6s %-5s yeni %2d gorunmeyen %s gomme %s istisna %s birim %s ic %s" % (
                    x["adres"], x["tema"], x["yeni"], [(y["id"], y["fark"], y["yalniz"]) for y in x["gorunmeyen"]],
                    [(y["id"], y["fark"]) for y in x["gomme"]],
                    [y["id"] for y in x["istisna"]], (b["en_buyuk"][:20], b["fark"], b["yalniz"]) if b else "-", bk))
        for tm, v in gr["tema"].items():
            print("  %s: kabuk alt adim %d, yeni %d, gorunmeyen %d, gomme %d, istisna %d, birim %d -> %s" % (
                tm, v["alt_adim"], v["yeni"], v["gorunmeyen"], v["gomme_gorunmeyen"], v["istisna"], v["birim_gorunmeyen"], v["gecti"]))
        print("  soluk %s -> %s" % ({k: (v["fark"], v["yalniz"]) for k, v in gr["soluk"].items()}, gr["gecti"]))
        print("arayuz"); sonuc["arayuz"] = ar = arayuz(c)
        print("  ", json.dumps({k: v.get("gecti") if isinstance(v, dict) else v for k, v in ar.items()}, ensure_ascii=False))
        sonuc["goruntu"] = [] if g.goruntu_yok else kareler(c)
    finally:
        c.kapat()
    sonuc["sure_s"] = round(time.time() - t0)
    ana = ("renk_cad", "renk_sahne", "karsitlik", "ev", "ev_dogruluk", "isaret", "gorunurluk", "arayuz")
    sonuc["gecti_ozet"] = {k: sonuc[k]["gecti"] for k in ana + ("renk_demo",)}
    sonuc["gecti"] = all(sonuc[k]["gecti"] for k in ana) and not sonuc["konsol_hatasi"]
    json.dump(sonuc, open(CIKTI, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("F10e dogrulama: %s (%d s); renk_demo %s (karar); kare %d" % ("GECTI" if sonuc["gecti"] else "KALDI", sonuc["sure_s"],
          "GECTI" if sonuc["renk_demo"]["gecti"] else "KALDI", len(sonuc["goruntu"])))
    sys.exit(0 if sonuc["gecti"] else 2)


if __name__ == "__main__":
    main()
