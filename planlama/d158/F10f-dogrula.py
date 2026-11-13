# F10f (P10.5) doğrulama: kol içi kablo yolu rehberde.
# 1) yol ↔ kaynak: tasarim/freecad/rehber/rehber_kol_kablo.py denetle() (KOL_KABLO + kablo_yolu.py türetmesi ↔ dirsek-analiz.json örnek
#    noktaları; veri ↔ türetme; sağ ↔ sol ayna; uçlar beklenen parçada; katı içinden geçmiyor; sıra / el; metin sayıları ↔ kaynak).
#    Sınama: bir şema bilerek bir katının içine kaydırılır ve adım bağı bilerek bozulur; denetim ikisini de yakalamalı.
# 2) yol ↔ adım: her bölüm tam bir alt adımda (denetle adim_bagi) + tarayıcıda o alt adımda "simdi", sonrakinde "onceki".
# 3) karede görünürlük, okurun pikseli: RehberTest.gorunurlukFark (sayfanın kendi tuvali, iki tema, şema gizlenip yeniden çizilir; güvenli
#    alanda Σ|ΔRGB| > 24) ↔ RehberTest.gorunurluk (kimlik tamponu, şema tek başına). Ölçüt F10d / F10e ile aynı: ≥ 30 px ve ≥ 0,20 ×
#    yalnız. Uçlar: iki uç güvenli alanda ve uç çevresinde (12 CSS px) okurun pikseli > 0.
# 4) sağ / sol: sağ ve sol alt adım karelerinde küçük görünüm etiketi kendi tarafını söylüyor, kare başlıkları farklı.
# F10e devri: (a) kol adımlarında (37–48) ve yeni alt adımlarda yeni parçaların okur pikseli iki temada; (c) küçük görünüm etiketinin
# açıklaması; (d) 360 px'te etiket tek satır.
# Kullanım: py -3 F10f-dogrula.py [--goruntu-yok] [--el-yok] [--sinama-yok]   -> F10f-dogrula.json
import os, sys, json, time, copy, argparse, importlib.util, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(HERE))
REHBER = os.path.join(ROBOT, "rehber")
REH_PY = os.path.join(ROBOT, "tasarim", "freecad", "rehber")
sys.path.insert(0, REH_PY)
import rehber_kol_kablo as RK                                         # noqa: E402
import rehber_gorunum as G                                            # noqa: E402

CIKTI = os.path.join(HERE, "F10f-dogrula.json")
TEMALAR = ("light", "dark")
FARK_ESIK, PX_ESIK, ORAN_ESIK = 24, 30, 0.20                          # F10d / F10e ölçütü
UC_PX = 12                                                            # uç çevresi (CSS px)
KOL_ADIM = range(37, 49)                                              # G0–H1


def veri():
    return json.load(open(os.path.join(REHBER, "veri", "rehber-veri.json"), encoding="utf-8"))


def adr(s, j):
    return "%d.%d" % (s, j) if j else "%d" % s


# ------------------------------------------------------------------ 1) + 2) veri denetimi ve sınama
def sinama(V):
    """Denetim kendi hatasını yakalıyor mu: (a) sağ tüp içi yolu dirsek servosunun gövdesinin içinden geçir; (b) bir şemayı grubundan çıkar;
    (c) birim; (d) F10f düzeltme 2: etiket takası, ikinci yanlış birimli geçiş, 625ZZ eski uçuş yönü (duruşta örtüşen çift)."""
    import numpy as np
    out = {}
    V2 = copy.deepcopy(V)
    M = G.Mesh(V2)
    pid = next(p["id"] for p in V2["parcalar"] if p["ad"] == "Dirsek servosu MG996R" and p["modul"] == "dirsek_sag")
    b0, b1 = M.P[pid]["bmin"], M.P[pid]["bmax"]
    c = (b0 + b1) / 2
    ek = int(np.argmax(b1 - b0))                                      # servonun uzun ekseni boyunca, merkezden geçen doğru
    a_, b_ = c.copy(), c.copy(); a_[ek] = b0[ek] + 3; b_[ek] = b1[ek] - 3
    i = next(k for k, s in enumerate(V2["semalar"]) if s["kaynak"] == "kol_kablo:sag:servo_dirsek")
    V2["semalar"][i]["pts"] = [[float(x) for x in a_], [float(x) for x in b_]]
    r = RK.denetle(V2, el=False, sessiz=True)
    out["kati"] = dict(beklenen="sağ dirsek servo yolu servonun içinden: katı içinden geçen ≥ 1 ve veri ↔ türetme farkı aşar",
                       kati_asan=[(x["bolum"], x["ad"], x["derinlik_mm"]) for x in r["kati"]["asan"]], veri_asan=r["veri_turetme"]["asan"],
                       gecti=bool(any(x["parca"] == pid for x in r["kati"]["asan"]) and r["veri_turetme"]["asan"] and not r["gecti"]))
    V3 = copy.deepcopy(V)
    j = next(k for k, s in enumerate(V3["semalar"]) if s["kaynak"] == "kol_kablo:sol:govde")
    for a in V3["adimlar"]:
        for g in a.get("sira_grup") or []:
            if j in (g.get("sema") or []):
                g["sema"] = [x for x in g["sema"] if x != j]
    r3 = RK.denetle(V3, el=False, sessiz=True)
    out["adim_bagi"] = dict(beklenen="sol gövde yolu grubundan çıkarılınca adım bağı hatalı ≥ 1", hatali=r3["adim_bagi"]["hatali"],
                            gecti=bool(r3["adim_bagi"]["hatali"]) and not r3["gecti"])
    # F10f düzeltme 1 (c): birim. G4 iç koşu yayı derece; metinde "mm" yazılınca birim hatası ≥ 1 ve denetim geçmez
    V4 = copy.deepcopy(V)
    n = 0
    for a in V4["adimlar"]:
        for g in a.get("sira_grup") or []:
            if "125,3°" in (g.get("is_") or ""):
                g["is_"] = g["is_"].replace("125,3°", "125,3 mm"); n += 1
    m4 = RK.metin_denetle(V4)
    out["birim"] = dict(beklenen="41.4 iç koşu yayı 125,3° -> '125,3 mm' yazılınca birim hatası ≥ 1 (sayı eksik de olur)", degisen=n,
                        birim_hata=m4["birim_hata"], eksik=m4["eksik"],
                        gecti=bool(n == 1 and any(x["sayi"] == "125,3" and "mm" in x["metinde"] for x in m4["birim_hata"])))
    # F10f düzeltme 2 (kontrol F10f-kontrol-2 T4 / T9): iç ↔ dış koşu değer takası etiket hatası, doğru geçişin yanına yanlış birimli
    # ikinci geçiş ("125,3 m") birim hatası verir
    def g4_degis(f):
        V5 = copy.deepcopy(V)
        for a in V5["adimlar"]:
            for g in a.get("sira_grup") or []:
                if "125,3°" in (g.get("is_") or ""):
                    g["is_"] = f(g["is_"])
        return RK.metin_denetle(V5)
    m5 = g4_degis(lambda s: s.replace("125,3°", "@@").replace("10,2°", "125,3°").replace("@@", "10,2°"))
    m6 = g4_degis(lambda s: s.replace("125,3°", "125,3° (125,3 m)", 1))
    out["etiket"] = dict(beklenen="41.4 iç / dış koşu yayı takas (125,3° ↔ 10,2°): etiket hatası ≥ 1", etiket_hata=m5["etiket_hata"],
                         gecti=bool(m5["etiket_hata"]))
    out["birim_ikinci"] = dict(beklenen="41.4'te doğru 125,3°'nin yanına '125,3 m': birim hatası ≥ 1", birim_hata=m6["birim_hata"],
                               gecti=any(x["sayi"] == "125,3" and "m" in x["metinde"] for x in m6["birim_hata"]))
    out["dinlenme"] = sinama_dinlenme(V)
    out["gecti"] = all(out[k]["gecti"] for k in ("kati", "adim_bagi", "birim", "etiket", "birim_ikinci", "dinlenme"))
    return out


def sinama_dinlenme(V):
    """F10f düzeltme 2 (madde 1c, kontrol F10f-kontrol-2 3.1): 625ZZ dış bileziği düzeltme turu 1'deki yönüne geri konur (kendi satırında
    sağ −x / sol +x, d 40; iç bilezik dış bilezikle birlikte). Rulman yuvada 0,06 mm sıkı geçme: duruşta örtüşen çift. Eski kural (çift
    yol boyunca hiç sayılmaz) bu yolu temiz sayar; düzeltilmiş denetim (eşik = duruş derinliği + rehber_sira.DINLENME_PAY) çatal yuvasının
    omzundaki geçişi yakalamalı. Rehberin kendi ucus_yolu'su, yalnız adım 44, veri kopyasında."""
    import numpy as np
    import rehber_sira as RS
    V2 = copy.deepcopy(V)
    PP = {p["id"]: p for p in V2["parcalar"]}
    dis = {p["modul"]: p for p in V2["parcalar"] if p["ad"] == "625ZZ rulman (dış bilezik)" and p["modul"] in ("dirsek_sag", "dirsek_sol")}
    ic = {p["modul"]: p for p in V2["parcalar"] if p["ad"] == "625ZZ rulman (iç bilezik)" and p["modul"] in ("dirsek_sag", "dirsek_sol")}
    s = dis["dirsek_sag"]["a"]
    for m, x in (("dirsek_sag", -1.0), ("dirsek_sol", 1.0)):
        dis[m].update(u=[x, 0.0, 0.0], d=40.0, h=None)
        ic[m].update(u=[x, 0.0, 0.0], d=40.0, h=dis[m]["id"])
    D = RS.Denetim.__new__(RS.Denetim)                                 # GLB + veri; ses / ızgara gerekmez (ucus_yolu)
    D.V, D.el_mm, D.A = V2, 20.0, V2["adimlar"]
    meshes, nodes = RS.glb_oku(os.path.join(REHBER, "veri", "robot.glb"))
    D.P = []
    for name, mi, M in nodes:
        p = dict(PP[name]); v, f = meshes[mi]
        p["v"] = v @ M[:3, :3].T + M[:3, 3]; p["f"] = f; p["bmin"], p["bmax"] = p["v"].min(0), p["v"].max(0)
        D.P.append(p)
    D.N = len(D.P); D.ID = {p["id"]: k for k, p in enumerate(D.P)}
    D.a_ = np.array([p["a"] for p in D.P]); D.b_ = np.array([p["b"] for p in D.P])
    D.t_ = np.array([p["t"] or "" for p in D.P]); D.ref = np.array([p["tur"] == "Referans" for p in D.P])
    D.bag = np.array([p["tur"] == "Baglanti" for p in D.P])
    hedef = {dis[m]["id"] for m in dis}
    catal = {p["id"] for p in V2["parcalar"] if p["ad"] == "Dirsek çatalı"}
    pay0 = RS.DINLENME_PAY
    sonuc = {}
    try:
        for ad, pay in (("yeni", pay0), ("eski", None)):
            RS.DINLENME_PAY = pay
            r = D.ucus_yolu([s])
            sat = [x for x in r["olcum"] if x["id"] in hedef]
            sonuc[ad] = [dict(adres="%d.%d" % (x["adim"], x["alt_adim"]), id=x["id"], temiz=x["temiz"], istisna=bool(x.get("istisna")),
                              carpan=[(c["engel"], c["derinlik_mm"]) for c in x.get("carpan_hepsi") or []]) for x in sat]
    finally:
        RS.DINLENME_PAY = pay0
    yakalar = lambda L: [x for x in L if not x["temiz"] and not x["istisna"] and any(e.split("[")[-1].rstrip("]") in catal for e, _ in x["carpan"])]
    return dict(beklenen="625ZZ dış bilezik eski yönde (sağ −x / sol +x, d 40): düzeltilmiş denetim iki bileziği çatal yuvasında çarpışan "
                         "sayar (pay %g mm); eski kural temiz sayar (kör nokta)" % pay0,
                pay_mm=pay0, yeni=sonuc.get("yeni"), eski=sonuc.get("eski"),
                gecti=bool(len(yakalar(sonuc.get("yeni", []))) == 2 and not yakalar(sonuc.get("eski", []))))


# ------------------------------------------------------------------ 3) tarayıcı
def _F():
    s = importlib.util.spec_from_file_location("f10a_dogrula", os.path.join(HERE, "F10a-dogrula.py"))
    F = importlib.util.module_from_spec(s); s.loader.exec_module(F)
    return F


def gor(f, y):
    return bool(f >= PX_ESIK and f >= ORAN_ESIK * max(y, 1))


def satir_ids(st, g):
    out = []
    for k in g["satir"]:
        t, i = k.split(":")
        out += (st["parcalar"] if t == "p" else st["baglantilar"])[int(i)]["ids"]
    return out + list(g.get("ref") or [])


def _pl_uzak(p, pts):
    """Nokta ↔ çoklu doğru parçası en kısa uzaklık (mm)."""
    best = float("inf")
    for a, b in zip(pts[:-1], pts[1:]):
        ab = [y - x for x, y in zip(a, b)]; ap = [y - x for x, y in zip(a, p)]
        L2 = sum(x * x for x in ab) or 1e-12
        t = max(0.0, min(1.0, sum(x * y for x, y in zip(ab, ap)) / L2))
        q = [x + t * y for x, y in zip(a, ab)]
        best = min(best, sum((x - y) ** 2 for x, y in zip(p, q)) ** 0.5)
    return best


def kablo_kare(c, F, V):
    global BEK, PAD
    K = V["kol_kablo"]
    S = V["semalar"]
    BEK = {t["sema"]: tuple(t["uc"]) for t in K["bolum"]}
    PAD = {p["id"]: p["ad"] for p in V["parcalar"]}
    adres = collections.OrderedDict()
    for t in K["bolum"]:
        adres.setdefault(t["adres"], []).append(t["sema"])
    out = []
    for tema in TEMALAR:
        for a, ids in adres.items():
            ok = c.git(F.url(REHBER, "?adim=%s&cekim=1&tema=%s" % (a, tema)))
            keys = ["sema%d" % i for i in ids]
            f = c.js("RehberTest.gorunurlukFark(%s)" % json.dumps(dict(ids=keys, uc_px=UC_PX, alan="hepsi"))) or {}
            g = c.js("RehberTest.gorunurluk({alan:'hepsi'})") or {}
            durum = c.js("(function(){return RehberTest.SEMA_OBJ.map(function(o,i){return o?[i,o.userData.d,o.visible]:null}).filter(function(x){return x})})()")
            dd = {x[0]: x[1] for x in durum if x[2]}
            mini = c.js("(function(){var e=document.getElementById('mini-yer');return e&&!e.hidden?{t:e.textContent,title:e.title}:null})()")
            # ortak uç: aynı alt adımda iki yolun ucu aynı noktada (≤ 1 mm; ör. tırnak, birleşim, duvar bağı). Bir yol gizlenince öbürü
            # ucu örter, tek tek fark 0 çıkar: ortak uçta ortaklardan birinin uç pikseli > 0 yeter
            UC = {}
            for i, k in zip(ids, keys):
                for n_, p in enumerate((S[i]["pts"][0], S[i]["pts"][-1])):
                    UC[(i, n_)] = (p, ((f.get("uc") or {}).get(k) or [{}, {}])[n_] if len((f.get("uc") or {}).get(k) or []) == 2 else {})
            for i, k in zip(ids, keys):
                px, y = (f.get("piksel") or {}).get(k, 0), (g.get("yalniz") or {}).get(k, 0)
                uc = (f.get("uc") or {}).get(k) or []
                ortu = c.js("RehberTest.ucOrtu(%d)" % i) or [{}, {}]
                bek = BEK.get(i, ("", ""))
                uc2 = []
                for n_, u in enumerate(uc):
                    p = UC[(i, n_)][0]
                    ort = [(j, m) for (j, m), (q, v) in UC.items() if j != i and sum((a_ - b_) ** 2 for a_, b_ in zip(p, q)) <= 1.0]
                    pk = max([u.get("piksel", 0)] + [UC[o][1].get("piksel", 0) for o in ort])
                    # uç pikseli 0 ise önündeki ilk opak nesne: yolun devamı (ucun 6 mm yakınından geçen şema: ek işareti, önceki adımın
                    # yolu, K2 demeti) ya da varış parçası (bölümün beklenen uç parçası) ise "örtülü, beklenen"
                    o_ = ortu[n_] if n_ < len(ortu) else {}
                    neden = None
                    if pk <= 0 and o_.get("ilk"):
                        ilk = o_["ilk"]
                        if ilk.startswith("sema") and _pl_uzak(p, S[int(ilk[4:])]["pts"]) <= 6.0:
                            neden = "yolun devamı %s (%s)" % (ilk, S[int(ilk[4:])]["ad"][:50])
                        elif not ilk.startswith("sema") and PAD.get(ilk, "").startswith(bek[n_]):
                            neden = "varış parçası %s (%s)" % (ilk, PAD[ilk])
                    # ortak uç, önceki alt adımın şeması (ör. iki gövde yolu aynı K2 noktasında biter; 36.5'te sağ yol "onceki", yarı
                    # saydam, ucOrtu saymıyor): kabul, ama o şemanın aynı ucu kendi karesinde görünür olmalı (sonda denetlenir)
                    onc = None
                    if pk <= 0 and not neden:
                        onc = next((j for j in sorted(dd) if j != i and j not in ids and any(
                            sum((a_ - b_) ** 2 for a_, b_ in zip(p, q)) <= 1.0 for q in (S[j]["pts"][0], S[j]["pts"][-1]))), None)
                        if onc is not None:
                            neden = "ortak uç, önceki şema sema%d (%s)" % (onc, S[onc]["ad"][:50])
                    uc2.append(dict(u, ortak=["sema%d" % j for j, _ in ort], ortak_piksel=pk, onunde=o_, ortulu_beklenen=neden,
                                    onceki_ortak=onc, gorunur=bool(u.get("ic") and (pk > 0 or neden))))
                ucg = bool(len(uc2) == 2 and all(u["gorunur"] for u in uc2))
                out.append(dict(adres=a, tema=tema, hazir=ok, sema=i, kaynak=S[i]["kaynak"], durum=dd.get(i), fark=px, yalniz=y,
                                oran=round(px / max(y, 1), 3), karede=(g.get("karede") or {}).get(k), uc=uc2, uc_gorunur=ucg,
                                gorunur=gor(px, y), mini=mini and mini["t"],
                                gecti=bool(ok and dd.get(i) == "simdi" and gor(px, y) and ucg)))
    # önceki şemayla ortak uç: o şemanın aynı noktadaki ucu kendi alt adımında (aynı tema) görünür olmalı, değilse kayıt kalır
    kayit = {(r["tema"], r["sema"]): r for r in out}
    for r in out:
        for n_, u in enumerate(r["uc"]):
            j = u.get("onceki_ortak")
            if j is None:
                continue
            p = (S[r["sema"]]["pts"][0], S[r["sema"]]["pts"][-1])[n_]
            o = kayit.get((r["tema"], j))
            ok = bool(o) and any(v["gorunur"] and not v.get("onceki_ortak") and
                                 sum((a_ - b_) ** 2 for a_, b_ in zip(p, (S[j]["pts"][0], S[j]["pts"][-1])[m])) <= 1.0
                                 for m, v in enumerate(o["uc"]))
            u["onceki_ortak_gorunur"] = ok
            if not ok:
                u["gorunur"] = False
                r["uc_gorunur"] = False
                r["gecti"] = False
    # sonraki konumda önceki (yalnız açık tema; durum tema bağımsız)
    sonra = []
    KON = G.konumlar(V["adimlar"])
    for t in K["bolum"]:
        s, j = (int(x) for x in t["adres"].split("."))
        k = KON.index((s, j))
        if k + 1 < len(KON) and KON[k + 1][0] == s:
            s2, j2 = KON[k + 1]
            c.git(F.url(REHBER, "?adim=%s&cekim=1&tema=light" % adr(s2, j2)))
            d = c.js("(function(){var o=RehberTest.SEMA_OBJ[%d];return o?[o.userData.d,o.visible]:null})()" % t["sema"])
            sonra.append(dict(sema=t["sema"], kaynak=S[t["sema"]]["kaynak"], adres=adr(s2, j2), durum=d and d[0], gorunur=d and d[1],
                              # uç duruş şeması kendi alt adımından sonra çizilmez (beklenen "gizli"); öbürleri "onceki"
                              beklenen="gizli" if S[t["sema"]].get("tur") in ("poz_a", "poz_b") else "onceki",
                              # F10f düzeltme 1: öbür uç duruş karesinde soluk iz ("iz", grup iz listesinde) de beklenen
                              gecti=bool(d and ((d[0] == "gizli" or (d[0] == "iz" and t["sema"] in (V["adimlar"][s2]["sira_grup"][j2 - 1].get("iz") or [])))
                                                if S[t["sema"]].get("tur") in ("poz_a", "poz_b") else
                                                (d[0] == "onceki" or (d[0] == "gizli" and V["adimlar"][s]["sira_grup"][j2 - 1].get("sema_yalniz")))))))
    return out, sonra


def sag_sol(olc, V):
    """Sağ / sol alt adım çiftleri: küçük görünüm etiketi tarafı söylüyor; kare başlığı (alt adım adı) farklı."""
    ad = {}
    for a in V["adimlar"]:
        for n, g in enumerate(a.get("sira_grup") or []):
            ad["%d.%d" % (a["i"], n + 1)] = g["ad"]
    cift = []
    sag = sorted({x["adres"] for x in olc if ":sag:" in x["kaynak"] and "s1_-" not in x["kaynak"] and "s1_+" not in x["kaynak"]})
    for a in sag:
        x = next(y for y in olc if y["adres"] == a and y["tema"] == "light")
        sol_k = x["kaynak"].replace(":sag:", ":sol:")
        y = next((z for z in olc if z["kaynak"] == sol_k and z["tema"] == "light"), None)
        if not y:
            continue
        cift.append(dict(sag=a, sol=y["adres"], mini_sag=x["mini"], mini_sol=y["mini"], baslik_sag=ad[a], baslik_sol=ad[y["adres"]],
                         gecti=bool(x["mini"] and y["mini"] and x["mini"].startswith("sağ") and y["mini"].startswith("sol")
                                    and ad[a] != ad[y["adres"]])))
    return dict(cift=cift, gecti=all(x["gecti"] for x in cift) and bool(cift))


def parca_kare(c, F, V):
    """F10e devri (a): kol adımlarının (G0–H1) her konumunda yeni parçalar, iki tema. F10e ile aynı ayrım: kendi satırındaki parça ölçütü
    geçmeli; bağlanan masa birimi / alt montajda yalnız en büyük parça (iç parçaları masada ölçülür); ısıl gömme ayrı sayılır."""
    A = V["adimlar"]
    PID = {p["id"]: p for p in V["parcalar"]}
    out = []
    for tema in TEMALAR:
        for s in KOL_ADIM:
            st = A[s]
            js = range(1, (st.get("alt") or 0) + 1) if st.get("alt") else [0]
            for j in js:
                t0 = time.time()
                ok = c.git(F.url(REHBER, "?adim=%s&cekim=1&tema=%s" % (adr(s, j), tema)))
                r = {"hazir": ok, "adres": adr(s, j), "tema": tema}
                for alan, op in (("sutun", "{}"), ("hepsi", "{alan:'hepsi'}")):
                    f = c.js("RehberTest.gorunurlukFark(%s)" % op) or {}
                    g = c.js("RehberTest.gorunurluk(%s)" % op) or {}
                    px, yal = f.get("piksel") or {}, g.get("yalniz") or {}
                    kendi = set(satir_ids(st, st["sira_grup"][j - 1])) if j else {i for i in px if PID[i]["a"] == s}
                    yeni = [i for i in px if i in kendi]
                    alt = [i for i in px if i not in kendi]
                    kalan = [i for i in yeni if not gor(px[i], yal.get(i, 0)) and G.bag_tipi(PID[i]) != "gomme"]
                    gomme = [i for i in yeni if not gor(px[i], yal.get(i, 0)) and G.bag_tipi(PID[i]) == "gomme"]
                    birim = None
                    if alt:
                        en = max(alt, key=lambda i: yal.get(i, 0))
                        birim = dict(en_buyuk=PID[en]["ad"], fark=px[en], yalniz=yal.get(en, 0), gorunur=gor(px[en], yal.get(en, 0)), parca=len(alt))
                    r[alan] = dict(yeni=len(yeni), gorunmeyen=[(i, PID[i]["ad"], px[i], yal.get(i, 0)) for i in kalan],
                                   gomme=[(i, PID[i]["ad"], px[i], yal.get(i, 0)) for i in gomme], birim=birim,
                                   gecti=bool(ok and not kalan and (birim is None or birim["gorunur"])))
                r["sure_s"] = round(time.time() - t0, 1)
                out.append(r)
    oz = {"%s %s" % (t, al): dict(konum=sum(1 for x in out if x["tema"] == t), yeni=sum(x[al]["yeni"] for x in out if x["tema"] == t),
                                  gorunmeyen=sum(len(x[al]["gorunmeyen"]) for x in out if x["tema"] == t),
                                  gomme=sum(len(x[al]["gomme"]) for x in out if x["tema"] == t),
                                  birim_gorunmeyen=sum(1 for x in out if x["tema"] == t and x[al]["birim"] and not x[al]["birim"]["gorunur"]),
                                  gecen_konum=sum(1 for x in out if x["tema"] == t and x[al]["gecti"]))
          for t in TEMALAR for al in ("sutun", "hepsi")}
    return dict(kapsam="kol adımları G0–H1 (37–48), her alt adım (alt adımı olmayan adımda adımın kendisi); iki ölçüm alanı: 'sutun' F10e'nin "
                       "kendisi (ilk güvenli alan), 'hepsi' güvenli alanların birleşimi. Öbür adımlar F10e-dogrula kabuk adımlarında ölçülüyor, "
                       "bütün alt adımlara genişletilmedi (süre: aşağıda)", ozet=oz, olcum=out,
                sure_s=round(sum(x["sure_s"] for x in out), 1),
                # bilgi: bu paket kol adımlarına parça eklemedi; eşik altı parçalar F10f'den önce de vardı (ölçülmemişti). Geçme şartına girmez
                gecti=None, gecen_hepsi=all(x["hepsi"]["gecti"] for x in out))


def gizli_piksel(c, F, V):
    """F10f düzeltme 1 (kontrol F10f-K1 e): perdelenmede tamamen gizli sayılıp dar gizli_ok (parça kimliği) alan parçaların kendi alt
    adım karesindeki okur pikseli (gorunurlukFark: bu parça çizilince değişen piksel; gorunurluk: tek başına), iki tema, iki alan.
    Bilgi: geçme şartı değil; görünmeyenler günlükte yazılır."""
    import re as _re
    A = V["adimlar"]
    PID = {p["id"]: p for p in V["parcalar"]}
    hedef = []
    for s in KOL_ADIM:
        for j, g in enumerate(A[s].get("sira_grup") or [], 1):
            ids = [k for k in (g.get("gizli_ok") or {}) if _re.match(r"^p\d{4}$", k)]
            if ids:
                hedef.append((s, j, ids))
    out = []
    for tema in TEMALAR:
        for s, j, ids in hedef:
            ok = c.git(F.url(REHBER, "?adim=%s&cekim=1&tema=%s" % (adr(s, j), tema)))
            for alan, op in (("sutun", "{}"), ("hepsi", "{alan:'hepsi'}")):
                f = c.js("RehberTest.gorunurlukFark(%s)" % op) or {}
                g = c.js("RehberTest.gorunurluk(%s)" % op) or {}
                px, yal = f.get("piksel") or {}, g.get("yalniz") or {}
                for i in ids:
                    out.append(dict(adres=adr(s, j), tema=tema, alan=alan, id=i, ad=PID[i]["ad"], hazir=ok, fark=px.get(i), yalniz=yal.get(i),
                                    gorunur=gor(px.get(i) or 0, yal.get(i) or 0)))
    return dict(yontem="kendi alt adım karesi (?cekim=1), gorunurlukFark + gorunurluk, ölçüt ≥ %d px ve ≥ %.2f × yalnız" % (PX_ESIK, ORAN_ESIK),
                olcum=out, parca=len({x["id"] for x in out}), gorunmeyen=sorted({(x["adres"], x["id"], x["ad"]) for x in out
                                                                                    if x["alan"] == "hepsi" and not x["gorunur"]}),
                gecti=None)


def mini_etiket(c, F):
    """F10e devri (c) açıklama metni, (d) 360 px'te tek satır (49.3 ve kol kablo alt adımları)."""
    out = {}
    c.git(F.url(REHBER, "?adim=49.3&cekim=1&tema=light"))
    out["aciklama"] = c.js("(function(){var e=document.getElementById('mini-yer');return e?e.title:null})()")
    out["aciklama_gecti"] = bool(out["aciklama"] and "model koordinatı" in out["aciklama"] and "yerden yükseklik değil" in out["aciklama"])
    c.boyut(360, 740, True)
    sat = []
    for a in ("49.3", "49.4", "34.3", "36.4", "40.2", "41.2", "41.4", "42.2", "44.2", "48.2", "48.3"):
        c.git(F.url(REHBER, "?adim=%s&cekim=1&tema=light" % a))
        c.js("RehberTest.miniGoster(true)")
        time.sleep(0.2)
        r = c.js("(function(){var e=document.getElementById('mini-yer');if(!e||e.hidden)return null;var cs=getComputedStyle(e);"
                 "var lh=parseFloat(cs.lineHeight)||parseFloat(cs.fontSize)*1.25;var rr=e.getBoundingClientRect();"
                 "return {t:e.textContent,sw:e.scrollWidth,cw:e.clientWidth,h:e.clientHeight,lh:lh,fs:parseFloat(cs.fontSize),"
                 "pad:parseFloat(cs.paddingTop)+parseFloat(cs.paddingBottom),w:rr.width}})()")
        if r:
            r["tek_satir"] = bool(r["sw"] <= r["cw"] + 0.5 and r["h"] - r["pad"] <= r["lh"] * 1.5)
        sat.append(dict(adres=a, olcum=r, gecti=bool(r and r["tek_satir"])))
    c.boyut(1400, 900)
    out["dar_360"] = sat
    out["gecti"] = out["aciklama_gecti"] and all(x["gecti"] for x in sat)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goruntu-yok", action="store_true", help="tarayıcı ölçümlerini atla")
    ap.add_argument("--el-yok", action="store_true", help="el bölgesi (sıra) ölçümünü atla")
    ap.add_argument("--sinama-yok", action="store_true")
    ap.add_argument("--yalniz-kablo", action="store_true", help="tarayıcıda yalnız kablo kareleri (parça karesi ve etiket atlanır)")
    g = ap.parse_args()
    t0 = time.time()
    V = veri()
    r = dict(tarih=time.strftime("%Y-%m-%d %H:%M"), betik="planlama/d158/F10f-dogrula.py")
    d = RK.denetle(V, el=not g.el_yok, sessiz=False)
    r["veri"] = d
    r["sinama"] = sinama(V) if not g.sinama_yok else dict(durum="atlandı", gecti=True)
    sure = {"veri_s": round(time.time() - t0, 1)}
    if not g.goruntu_yok:
        F = _F()
        c = F.Cdp(F.tarayici(), "f10f-dogrula")
        try:
            c.boyut(1400, 900)
            t1 = time.time()
            olc, sonra = kablo_kare(c, F, V)
            sure["kablo_kare_s"] = round(time.time() - t1, 1)
            r["kablo_kare"] = dict(yontem="gorunurlukFark(ids=şema, uc_px=%d, alan=hepsi) + gorunurluk(alan=hepsi); ölçüt ≥ %d px ve ≥ %.2f × "
                                   "yalnız; iki uç güvenli alanların birinde, uç çevresinde piksel > 0 (ortak uçta ortaklardan biri); durum "
                                   "'simdi'" % (UC_PX, PX_ESIK, ORAN_ESIK),
                                   olcum=olc, sayi=len(olc), gecen=sum(1 for x in olc if x["gecti"]),
                                   kalan=[(x["adres"], x["tema"], x["kaynak"], x["fark"], x["yalniz"], x["uc"]) for x in olc if not x["gecti"]],
                                   sonra=sonra, sonra_gecti=all(x["gecti"] for x in sonra),
                                   gecti=all(x["gecti"] for x in olc) and all(x["gecti"] for x in sonra))
            r["sag_sol"] = sag_sol(olc, V)
            if g.yalniz_kablo:
                r["parca_kare"] = r["mini_etiket"] = dict(durum="atlandı (--yalniz-kablo)", gecti=None)
            else:
                t1 = time.time()
                r["parca_kare"] = parca_kare(c, F, V)
                sure["parca_kare_s"] = round(time.time() - t1, 1)
                r["gizli_piksel"] = gizli_piksel(c, F, V)
                r["mini_etiket"] = mini_etiket(c, F)
        finally:
            c.kapat()
    else:
        r["kablo_kare"] = r["sag_sol"] = r["parca_kare"] = r["mini_etiket"] = dict(durum="atlandı (--goruntu-yok)", gecti=None)
    sure["toplam_s"] = round(time.time() - t0, 1)
    r["sure"] = sure
    parcalar = [r["veri"]["gecti"], r["sinama"]["gecti"]] + [r[k]["gecti"] for k in ("kablo_kare", "sag_sol", "parca_kare", "mini_etiket")
                                                             if r[k].get("gecti") is not None]
    r["gecti"] = all(parcalar)
    json.dump(r, open(CIKTI, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print("F10f: veri %s, sinama %s, kablo kare %s, sag/sol %s, parca kare %s, mini etiket %s -> %s (%.0f s)" % (
        r["veri"]["gecti"], r["sinama"]["gecti"], r["kablo_kare"].get("gecti"), r["sag_sol"].get("gecti"), r["parca_kare"].get("gecti"),
        r["mini_etiket"].get("gecti"), "GECTI" if r["gecti"] else "KALDI", sure["toplam_s"]))
    if r["kablo_kare"].get("kalan"):
        for x in r["kablo_kare"]["kalan"][:20]:
            print("  KABLO KARE", x)
    if isinstance(r["parca_kare"].get("ozet"), dict):
        print("  parca kare", r["parca_kare"]["ozet"])
    if isinstance(r.get("gizli_piksel"), dict):
        print("  gizli piksel: parca %d, gorunmeyen (hepsi alanı) %s" % (r["gizli_piksel"]["parca"], r["gizli_piksel"]["gorunmeyen"]))
    sys.exit(0 if r["gecti"] else 2)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    main()
