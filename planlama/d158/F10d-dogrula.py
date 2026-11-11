# F10d doğrulama: alt adımlar (gezinme, adresleme, ilerleme), panel sırası = takma sırası, görünürlük (21, 25, 43, 45, 46), 360 px,
# alt adım kareleri (açık / koyu) ve 31 / 33 önce (HEAD) / sonra yan yana.
#   py -3 -X utf8 planlama/d158/F10d-dogrula.py              # -> planlama/d158/F10d-dogrula.json + F10d-goruntu-*.png
#   py -3 -X utf8 planlama/d158/F10d-dogrula.py --goruntu-yok
# Yöntem: Chrome DevTools protokolü (F10a-dogrula.py'nin Cdp sınıfı), file://.
#   1) gezinme: ?adim=0'dan → tuşuyla sonuna kadar; ziyaret edilen konumlar = RehberTest.konumlar() (alt adımlar dahil), ← ile geri
#      aynı yol; ?adim=N.J doğrudan açılır (konum, sayaç metni, seçim kutusu değeri); ilerleme çubuğu genişliği konum / (toplam - 1).
#   2) panel sırası = takma sırası: her konumda (50 adım + alt adımlar) paneldeki satır sırası (data-satir) ile sıralı takmanın satır
#      sırası (RehberTest.takmaSira) aynı mı (takmada olmayan panel satırı sayılmaz: o konumda görünen parçası yok).
#   3) görünürlük: 21, 25, 43, 45, 46 ve alt adımlarında her yeni parçanın kimlik tamponundaki piksel sayısı (kamera görüntüsü, güvenli
#      alan; saydam çizilen eski parça örtmez) > 0 ve sınır kutusu köşeleri karede. Bölünen kabuk adımlarının alt adımları da
#      ölçülür (bilgi, geçme şartı değil). --gizli JSON: perdelenmede gizli çıkanların piksel ölçümü (F10d-gizli-piksel.json).
#   4) 360 px (mobil öykünme): alt adımlı adımların her alt adımında yatay taşma 0.
#   5) kareler: alt adımlı adımların her alt adımı açık + koyu (?cekim=1, 1400 x 900); 31 ve 33 önce (HEAD rehber/ + veri) / sonra
#      yan yana (PIL).
import os, sys, json, time, re, subprocess, tempfile, shutil, argparse, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(HERE))
REHBER = os.path.join(ROBOT, "rehber")
_s = importlib.util.spec_from_file_location("f10a_dogrula", os.path.join(HERE, "F10a-dogrula.py"))
F10A = importlib.util.module_from_spec(_s)
_s.loader.exec_module(F10A)
Cdp, tarayici, url = F10A.Cdp, F10A.tarayici, F10A.url
V = json.load(open(os.path.join(REHBER, "veri", "rehber-veri.json"), encoding="utf-8"))
NA = len(V["adimlar"])
ALTLI = [a["i"] for a in V["adimlar"] if a.get("alt")]
GORUNUR_ADIM = (21, 25, 43, 45, 46)
CIKTI = os.path.join(HERE, "F10d-dogrula.json")


def konumlar():
    k = []
    for a in V["adimlar"]:
        k.append([a["i"], 0])
        k += [[a["i"], j] for j in range(1, (a.get("alt") or 0) + 1)]
    return k


def adr(s, j):
    return "%d.%d" % (s, j) if j else str(s)


def gezinme(c):
    K = konumlar()
    c.git(url(REHBER, "?adim=0&tema=light"), cekim=False)
    sayfa_k = c.js("RehberTest.konumlar()")
    ileri = [c.js("RehberTest.konum()")]
    for _ in range(len(K) - 1):
        c.tus("ArrowRight", "ArrowRight", 39)
        c.bekle("!RehberTest.anim()", 10)
        ileri.append(c.js("RehberTest.konum()"))
    c.tus("ArrowRight", "ArrowRight", 39)                           # sonda kalır
    son = c.js("RehberTest.konum()")
    geri = [son]
    for _ in range(len(K) - 1):
        c.tus("ArrowLeft", "ArrowLeft", 37)
        c.bekle("!RehberTest.anim()", 10)
        geri.append(c.js("RehberTest.konum()"))
    dogrudan = []
    for s in ALTLI:
        for j in (1, V["adimlar"][s]["alt"]):
            ok = c.git(url(REHBER, "?adim=%s&tema=light" % adr(s, j)), cekim=False)
            o = c.js("({k: RehberTest.konum(), say: document.getElementById('sayac').textContent, sec: document.getElementById('secim').value,"
                     " cubuk: document.getElementById('cubuk').style.width, altlar: document.querySelectorAll('#altlar a, #altlar [data-git]').length})")
            no = K.index([s, j])
            bek_cubuk = 100 * no / (len(K) - 1)
            cub = float((o.get("cubuk") or "0%").rstrip("%"))
            dogrudan.append(dict(adres=adr(s, j), hazir=ok, konum=o.get("k"), sayac=o.get("say"), secim=o.get("sec"), cubuk=o.get("cubuk"),
                                 alt_baglanti=o.get("altlar"),
                                 gecti=bool(ok and o.get("k") == [s, j] and o.get("sec") == adr(s, j) and ("alt adım %d / %d" % (j, V["adimlar"][s]["alt"])) in (o.get("say") or "")
                                            and abs(cub - bek_cubuk) < 0.05)))
    # alt adımsız adım bugünkü gibi: ?adim=12 -> konum [12, 0], sayaçta "alt adım" yok
    c.git(url(REHBER, "?adim=12&tema=light"), cekim=False)
    o = c.js("({k: RehberTest.konum(), say: document.getElementById('sayac').textContent})")
    duz = dict(adres="12", konum=o.get("k"), sayac=o.get("say"), gecti=o.get("k") == [12, 0] and "alt adım" not in (o.get("say") or ""))
    return dict(konum_sayisi=len(K), ana_adim=NA, alt_adim=len(K) - NA, sayfa_konumlari_esit=sayfa_k == K, ileri_esit=ileri == K,
                geri_esit=geri == K[::-1], sonda_kalir=son == K[-1], dogrudan=dogrudan, alt_adimsiz=duz,
                gecti=bool(sayfa_k == K and ileri == K and geri == K[::-1] and son == K[-1] and all(d["gecti"] for d in dogrudan) and duz["gecti"]))


def panel_takma(c):
    out = []
    c.git(url(REHBER, "?adim=0&tema=light"), cekim=False)
    for s, j in konumlar():
        c.js("RehberTest.git(%d, %d)" % (s, j))
        c.bekle("!RehberTest.anim()", 10)
        ps = c.js("RehberTest.panelSira()") or []
        ts = c.js("RehberTest.takmaSira()") or []
        tk = set(ts)
        pk = [x for x in ps if x in tk]
        out.append(dict(adres=adr(s, j), kod=V["adimlar"][s]["kod"], panel=len(ps), takma=len(ts), panelde_takmada_yok=[x for x in ps if x not in tk],
                        takmada_panelde_yok=[x for x in ts if x not in set(ps)], esit=pk == ts))
    kotu = [x for x in out if not x["esit"] or x["takmada_panelde_yok"]]
    return dict(konum=len(out), esit=sum(1 for x in out if x["esit"] and not x["takmada_panelde_yok"]), kotu=kotu,
                gecti=not kotu, olcum=out)


# F10d düzeltme 1 (kontrol B-1, B-7, B-8): görünürlük ölçütü. Bir yeni parça alt adımın kendi karesinde (alt adım kamerası, 1400 × 900,
# güvenli alan: araç çubuğu, lejant ve küçük görünüm dışı) "anlamlı görünür" sayılır: piksel ≥ PX_ESIK ve piksel ≥ ORAN_ESIK × yalnız
# (parça tek başına çizilince, engelsiz izdüşümündeki piksel). Gerekçe: 30 px ≈ 5 × 6 px'lik bir leke (1400 px genişlikte bir M3 cıvata
# başı ≈ 10–20 px çap, ≈ 80–300 px alan; 30 px altı kenar şeridi ya da birkaç dağınık piksel, "görülür" değil); oran: büyük parçanın
# yalnız ince bir kenarının görünmesi (ör. 1 mm köpük bandın yan yüzü) "görünür" sayılmasın, parçanın beşte biri görünmeli. Saydam
# çizilen (opaklık < 0,5) parça arkasını örtmez; saydam çizilen yeni parça (ör. içindeki ısıl gömme görünsün diye ev sahibi) opak
# parçaların örtmediği pikselleriyle sayılır (app.js gorunurluk). Isıl gömmeler dahil.
PX_ESIK, ORAN_ESIK = 30, 0.20
KABUK = (31, 33, 34, 35, 36, 49)


def gorunur_mu(px, yal):
    return bool(px >= PX_ESIK and px >= ORAN_ESIK * max(yal, 1))


def satir_ids(st, g):
    out = []
    for k in g["satir"]:
        t, i = k.split(":")
        out += (st["parcalar"] if t == "p" else st["baglantilar"])[int(i)]["ids"]
    return out + list(g.get("ref") or [])


def gorunurluk(c):
    """Her konumda (sınırlı: kabuk adımlarının alt adımları ve 21, 25, 43, 45, 46 ile alt adımları; öbürleri yok) RehberTest.gorunurluk().
    Alt adımın kendi satırlarındaki her yeni parça ölçütü geçmeli (istisna: grubun piksel_ok {desen: gerekçe}). Bağlanan masa birimi
    (alt): birimin en büyük parçası (yalnız pikseline göre) ölçütü geçmeli; birimin iç parçaları bilgi olarak, masada yeni oldukları alt
    adımdaki ölçümle birlikte listelenir. Masa alt adımında görünen her şema o alt adımın kendi şeması olmalı (yabancı kablo 0)."""
    out = []
    c.boyut(1400, 900)
    ad = {p["id"]: p["ad"] for p in V["parcalar"]}
    hedef = []
    for s in list(GORUNUR_ADIM) + [x for x in ALTLI if x not in GORUNUR_ADIM]:
        hedef += [(s, j) for j in [0] + list(range(1, (V["adimlar"][s].get("alt") or 0) + 1))]
    olc = {}
    for s, j in hedef:
        ok = c.git(url(REHBER, "?adim=%s&cekim=1&tema=light" % adr(s, j)))
        g = c.js("RehberTest.gorunurluk()") or {}
        olc[(s, j)] = (ok, g)
    for s, j in hedef:
        ok, g = olc[(s, j)]
        st = V["adimlar"][s]
        px, yal, kr = g.get("piksel") or {}, g.get("yalniz") or {}, g.get("karede") or {}
        grp = st["sira_grup"][j - 1] if j and st.get("alt") else None
        sinir = bool((s in GORUNUR_ADIM and (j or not st.get("alt"))) or (s in KABUK and j))
        kendi = set(satir_ids(st, grp)) if grp else {i for i in px if not i.startswith("sema")}
        pok = (grp or {}).get("piksel_ok") or {}
        parca, kalan, istisna = [], [], []
        for i in sorted(kendi):
            if i not in px:
                continue
            r = dict(id=i, ad=ad[i], px=px[i], yalniz=yal.get(i, 0), oran=round(px[i] / max(yal.get(i, 0), 1), 3),
                     karede=kr.get(i), gorunur=gorunur_mu(px[i], yal.get(i, 0)), saydam=i in (g.get("saydam") or []))
            parca.append(r)
            if not r["gorunur"]:
                ger = next((v for k, v in pok.items() if k in ad[i]), None)
                (istisna if ger else kalan).append(dict(r, gerekce=ger) if ger else r)
        birim = None
        alt_ids = [i for i in px if not i.startswith("sema") and i not in kendi]
        if grp and grp.get("bag") and alt_ids:
            en = max(alt_ids, key=lambda i: yal.get(i, 0))
            ic = []
            for i in alt_ids:
                if gorunur_mu(px[i], yal.get(i, 0)):
                    continue
                n0 = next((n for n, x in enumerate(st["sira_grup"]) if i in satir_ids(st, x)), None)
                o0 = olc.get((s, n0 + 1)) if n0 is not None else None
                p0 = ((o0[1] or {}).get("piksel") or {}).get(i) if o0 else None
                y0 = ((o0[1] or {}).get("yalniz") or {}).get(i) if o0 else None
                ic.append(dict(id=i, ad=ad[i], px=px[i], masada="%d.%d" % (s, n0 + 1) if n0 is not None else None, masada_px=p0,
                               masada_yalniz=y0, masada_gorunur=bool(p0 is not None and gorunur_mu(p0, y0 or 0))))
            birim = dict(en_buyuk=ad[en], px=px[en], yalniz=yal.get(en, 0), gorunur=gorunur_mu(px[en], yal.get(en, 0)),
                         parca=len(alt_ids), ic_gorunmeyen=ic)
        sema_kendi = set(grp.get("sema") or []) if grp else set()
        yabanci = [x for x in (g.get("sema") or []) if grp and grp.get("tezgah") and not (x.get("d") == "simdi" and x["i"] in sema_kendi)]
        sema_px = {k: (px[k], yal.get(k, 0)) for k in px if k.startswith("sema")}
        gecti = bool(ok and (parca or birim) and not kalan and (birim is None or (birim["gorunur"] and all(x["masada_gorunur"] for x in birim["ic_gorunmeyen"])))
                     and not yabanci and all(kr.get(x["id"], True) for x in parca)) if (parca or birim) else bool(ok)
        out.append(dict(adres=adr(s, j), kod=st["kod"], hazir=ok, sinir=sinir, yeni=len(parca), gorunmeyen=kalan, istisna=istisna,
                        birim=birim, sema=sema_px, yabanci_sema=yabanci, parca=parca, saydam=g.get("saydam") or [], gecti=gecti))
    sinirli = [x for x in out if x["sinir"]]
    kabuk = [x for x in out if x["sinir"] and int(x["adres"].split(".")[0]) in KABUK]
    return dict(yontem=gorunurluk.__doc__.strip(), esik=dict(piksel=PX_ESIK, oran=ORAN_ESIK), olcum=out,
                kabuk_alt_adim=len(kabuk), kabuk_yeni=sum(x["yeni"] for x in kabuk),
                kabuk_gorunmeyen=sum(len(x["gorunmeyen"]) for x in kabuk), kabuk_istisna=sum(len(x["istisna"]) for x in kabuk),
                kabuk_birim_ic=sum(len((x["birim"] or {}).get("ic_gorunmeyen", [])) for x in kabuk),
                masa_yabanci_sema=sum(len(x["yabanci_sema"]) for x in out),
                gecti=all(x["gecti"] for x in sinirli))


def gizli_piksel(c, yol):
    """Perdelenme ölçümünde (voksel 3 mm, 26 yön) alt adımında tamamen gizli çıkan yeni parçaların o alt adımın karesindeki kimlik
    tamponu piksel sayısı (bağımsız ikinci ölçüm: piksel düzeyinde, tek kamera). yol: rehber_sira --json çıktısı ya da kontrol.json."""
    r = json.load(open(yol, encoding="utf-8"))
    pr = r.get("perdelenme") or {}
    ad = {p["id"]: p["ad"] for p in V["parcalar"]}
    c.boyut(1400, 900)
    c.git(url(REHBER, "?adim=0&tema=light"), cekim=False)
    out = []
    for a in pr.get("adim", []):
        for g in a.get("grup", []):
            # F10d düzeltme 1 (kontrol B-8): ısıl gömme istisnaları da ölçülür
            ids = [x["id"] for x in g.get("gizli_istisnasiz", [])] + [x["id"] for x in g.get("istisna", [])]
            if not ids:
                continue
            ok = c.git(url(REHBER, "?adim=%d.%d&cekim=1&tema=light" % (a["adim"], g["alt_adim"])))
            px = (c.js("RehberTest.gorunurluk()") or {}).get("piksel") or {}
            # alt adım kamerasında pikseli olmayanlar için öbür kameralar (yalnız ölçüm; veri değişmez, sayfa sonra yeniden açılır)
            diger = {}
            if any(not px.get(i) for i in ids):
                for yon in DIGER_KAMERA:
                    c.js("(function(){const g=REHBER_VERI.adimlar[%d].sira_grup[%d]; g.kamera=%s; RehberTest.git(%d,%d);})()"
                         % (a["adim"], g["alt_adim"] - 1, json.dumps(list(yon)), a["adim"], g["alt_adim"]))
                    c.bekle("!RehberTest.anim()", 10)
                    p2 = (c.js("RehberTest.gorunurluk()") or {}).get("piksel") or {}
                    for i in ids:
                        if not px.get(i) and p2.get(i):
                            diger.setdefault(i, {})[str(list(yon))] = p2[i]
            for i in ids:
                out.append(dict(adres="%d.%d" % (a["adim"], g["alt_adim"]), kod=a["kod"], id=i, ad=ad.get(i), hazir=ok, piksel=px.get(i),
                                diger_kamera=diger.get(i) or None))
    return dict(yontem=gizli_piksel.__doc__.strip(), diger_kamera=[list(x) for x in DIGER_KAMERA], olcum=out,
                pikselli=sum(1 for x in out if (x["piksel"] or 0) > 0),
                baska_kamerada=sum(1 for x in out if not x["piksel"] and x["diger_kamera"]), toplam=len(out))


DIGER_KAMERA = ((0.85, 0.62, -1.25), (-0.85, 0.62, -1.25), (0.85, 0.62, 1.25), (-0.85, 0.62, 1.25), (0, 1, 0), (0.9, -0.55, 1.2),
                (0.9, -0.55, -1.2), (1, 0, 0), (-1, 0, 0))


def telefon(c):
    c.boyut(360, 1600, mobil=True)
    out = []
    for s in ALTLI:
        for j in range(1, V["adimlar"][s]["alt"] + 1):
            ok = c.git(url(REHBER, "?adim=%s&cekim=1&tema=light" % adr(s, j)))
            t = c.js("(function(){const d=document.documentElement;return Math.max(d.scrollWidth,document.body.scrollWidth)-d.clientWidth;})()")
            out.append(dict(adres=adr(s, j), hazir=ok, tasma_px=t, hata=c.js("document.documentElement.dataset.hata || null")))
    c.boyut(1400, 900)
    return dict(pencere=[360, 1600], olcum=out, tasma_max=max((x["tasma_px"] or 0) for x in out) if out else None,
                gecti=bool(out) and all(x["hazir"] and x["tasma_px"] == 0 and not x["hata"] for x in out))


def head_kopya():
    tmp = tempfile.mkdtemp(prefix="lale-f10d-head-")
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
    for s in ALTLI + [x for x in GORUNUR_ADIM if x not in ALTLI]:
        js = list(range(0, (V["adimlar"][s].get("alt") or 0) + 1))
        for j in js:
            for tema, ad in (("light", "acik"), ("dark", "koyu")):
                c.git(url(REHBER, "?adim=%s&cekim=1&tema=%s" % (adr(s, j), tema)))
                y = os.path.join(HERE, "F10d-goruntu-%02d-%02d-%s.png" % (s, j, ad)); c.goruntu(y); liste.append(os.path.basename(y))
    tmp, head = head_kopya()
    try:
        for s in (31, 33):
            for tema, ad in (("light", "acik"), ("dark", "koyu")):
                ya = os.path.join(tempfile.gettempdir(), "f10d-once.png")
                c.git(url(head, "?adim=%d&cekim=1&tema=%s" % (s, tema)))
                c.goruntu(ya)
                parcalar = [Image.open(ya).convert("RGB")]
                for j in range(1, V["adimlar"][s]["alt"] + 1):
                    yb = os.path.join(tempfile.gettempdir(), "f10d-sonra-%d.png" % j)
                    c.git(url(REHBER, "?adim=%s&cekim=1&tema=%s&sahne=1" % (adr(s, j), tema)))
                    c.goruntu(yb)
                    parcalar.append(Image.open(yb).convert("RGB"))
                # önce (tam sayfa, solda büyük) + sonra alt adımlar (3 sütun ızgara, yalnız 3B)
                w0, h0 = parcalar[0].size
                kw, kh = w0 // 3, h0 // 3
                sat = (len(parcalar) - 2) // 3 + 1
                im = Image.new("RGB", (w0 + 3 * kw, max(h0, sat * kh) + 40), (255, 255, 255) if tema == "light" else (20, 20, 22))
                im.paste(parcalar[0], (0, 40))
                for n, p in enumerate(parcalar[1:]):
                    im.paste(p.resize((kw, kh)), (w0 + (n % 3) * kw, 40 + (n // 3) * kh))
                d = ImageDraw.Draw(im)
                renk = (0, 0, 0) if tema == "light" else (230, 230, 230)
                d.text((10, 12), "ONCE (HEAD): adim %d tek kare" % s, fill=renk)
                d.text((w0 + 10, 12), "SONRA: adim %d alt adimlari %d.1 ... %d.%d (yalniz 3B)" % (s, s, s, V["adimlar"][s]["alt"]), fill=renk)
                y = os.path.join(HERE, "F10d-goruntu-%02d-once-sonra-%s.png" % (s, ad)); im.save(y); liste.append(os.path.basename(y))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return liste


def gorunurluk_yaz(gr):
    for x in gr["olcum"]:
        b = x["birim"]
        print("  %-6s %-4s yeni %2d gorunmeyen %d istisna %d%s%s %s" % (
            x["adres"], x["kod"], x["yeni"], len(x["gorunmeyen"]), len(x["istisna"]),
            (" | birim %s %s/%s px %s, ic %d" % (b["en_buyuk"][:24], b["px"], b["yalniz"], "ok" if b["gorunur"] else "YOK", len(b["ic_gorunmeyen"]))) if b else "",
            (" | yabanci sema %d" % len(x["yabanci_sema"])) if x["yabanci_sema"] else "",
            ("GECTI" if x["gecti"] else "KALDI") + ("" if x["sinir"] else " (bilgi)")))
        for r in x["gorunmeyen"]:
            print("      GORUNMEZ %s %-48s px %5d yalniz %5d oran %.3f%s" % (r["id"], r["ad"][:48], r["px"], r["yalniz"], r["oran"],
                                                                         " saydam" if r["saydam"] else ""))
        for r in (b or {}).get("ic_gorunmeyen", []):
            if not r["masada_gorunur"]:
                print("      BIRIM ICI masada gorunmedi %s %s (%s px %s)" % (r["id"], r["ad"][:40], r["masada"], r["masada_px"]))
    print("  kabuk alt adim %d, yeni parca %d, gorunmeyen %d, istisna %d, birim ici (masada gosterilen) %d; masa yabanci sema %d; esik %s" % (
        gr["kabuk_alt_adim"], gr["kabuk_yeni"], gr["kabuk_gorunmeyen"], gr["kabuk_istisna"], gr["kabuk_birim_ic"], gr["masa_yabanci_sema"],
        gr["esik"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goruntu-yok", action="store_true")
    ap.add_argument("--yalniz-gorunurluk", metavar="JSON", help="yalnız görünürlük ölçümü (-> JSON; depoya yazmaz)")
    ap.add_argument("--gizli", metavar="JSON", help="yalnız perdelenmede gizli çıkan parçaların alt adım karesindeki pikselleri "
                                                   "(-> F10d-gizli-piksel.json)")
    g = ap.parse_args()
    tb = tarayici()
    if g.yalniz_gorunurluk:
        c = Cdp(tb, "f10d")
        try:
            gr = gorunurluk(c)
        finally:
            c.kapat()
        json.dump(gr, open(g.yalniz_gorunurluk, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        gorunurluk_yaz(gr)
        return
    if g.gizli:
        c = Cdp(tb, "f10d")
        try:
            r = gizli_piksel(c, g.gizli)
        finally:
            c.kapat()
        json.dump(r, open(os.path.join(HERE, "F10d-gizli-piksel.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        for x in r["olcum"]:
            print("  %-6s %-4s %s %-50s piksel %s %s" % (x["adres"], x["kod"], x["id"], (x["ad"] or "")[:50], x["piksel"], x["diger_kamera"] or ""))
        print("gizli piksel: %d / %d parcanin alt adim karesinde pikseli var, %d baska kamerada" % (r["pikselli"], r["toplam"], r["baska_kamerada"]))
        return
    t0 = time.time()
    sonuc = dict(tarih=time.strftime("%Y-%m-%d %H:%M"), adim=NA, alt_adimli=ALTLI)
    c = Cdp(tb, "f10d")
    try:
        c.boyut(1400, 900)
        print("gezinme"); sonuc["gezinme"] = gz = gezinme(c)
        print("  konum %d (ana %d + alt %d), ileri %s geri %s dogrudan %s -> %s" % (gz["konum_sayisi"], gz["ana_adim"], gz["alt_adim"], gz["ileri_esit"],
              gz["geri_esit"], sum(1 for d in gz["dogrudan"] if d["gecti"]), "GECTI" if gz["gecti"] else "KALDI"))
        print("panel = takma"); sonuc["panel_takma"] = pt = panel_takma(c)
        print("  %d/%d konum esit; kotu %s" % (pt["esit"], pt["konum"], [x["adres"] for x in pt["kotu"]]))
        print("gorunurluk"); sonuc["gorunurluk"] = gr = gorunurluk(c)
        gorunurluk_yaz(gr)
        print("telefon"); sonuc["telefon"] = tf = telefon(c)
        print("  360 px tasma en cok %s -> %s" % (tf["tasma_max"], "GECTI" if tf["gecti"] else "KALDI"))
        sonuc["kontrol_hatasi"] = c.js("document.documentElement.dataset.hata || null")
        sonuc["goruntu"] = [] if g.goruntu_yok else kareler(c)
    finally:
        c.kapat()
    sonuc["sure_s"] = round(time.time() - t0)
    sonuc["gecti"] = all(sonuc[k]["gecti"] for k in ("gezinme", "panel_takma", "gorunurluk", "telefon"))
    json.dump(sonuc, open(CIKTI, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("F10d dogrulama: %s (%d s), kare %d" % ("GECTI" if sonuc["gecti"] else "KALDI", sonuc["sure_s"], len(sonuc["goruntu"])))
    sys.exit(0 if sonuc["gecti"] else 2)


if __name__ == "__main__":
    main()
