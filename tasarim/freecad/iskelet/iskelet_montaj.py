# Iskelet modulu (V3) - montaj, kontroller, egilme hesabi, kesim listesi, BOM, FCStd + STEP + analiz json
# Calistir (yolda "ü" oldugu icin ASCII baslaticiyla): FC_SCRIPT=<bu dosya> freecadcmd run_fc.py
# Kontroller: her parca isValid + tek kati; parca ici cakisma (0.5 mm3 tolerans); baglanti oturmasi (kose ve
# kama profile dayali, cekic somun dudak altinda, civata ucu kanal tabanina degmiyor, set vida tabana dayali);
# taban/kafa icin ayrilmis bolgelere tasma; direk ve travers egilmesi (iki kol tam acik + el ucunda 0.5 kg).
import os, sys, json, math, time, csv
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (HERE, UST, os.path.join(UST, "omuz")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import iskelet_parcalar as I
import arayuz as A
from ortak_lib import V, box, WASH125, NUT985

P, BAG = I.P, I.BAG
t0 = time.time()
TOL = 0.5          # mm3, cakisma esigi (omuz ile ayni)
H = A.SG / 2
TEMAS = 0.01       # mm, "dayali" sayilan en buyuk mesafe
print("parca sayisi", len(P), "baglanti", len(BAG))

# ====================================================================== 1) gecerlilik ve parca ici cakisma
gecersiz = [p["ad"] for p in P if not p["shape"].isValid()]
coklu = [(p["ad"], p["kati"]) for p in P if p["kati"] != 1]
cakisma = []
n_cift = 0
for i in range(len(P)):
    for j in range(i + 1, len(P)):
        a, b = P[i], P[j]
        if not a["bb"].intersect(b["bb"]):
            continue
        n_cift += 1
        try:
            v = a["shape"].common(b["shape"]).Volume
        except Exception:
            v = -1.0
        if v > TOL or v < 0:
            cakisma.append((a["ad"], b["ad"], round(v, 3)))
print("gecersiz", len(gecersiz), "coklu kati", len(coklu), "cakisma", len(cakisma), "(sinir kutusu kesisen cift %d)" % n_cift,
      "%.1fs" % (time.time() - t0))


# ====================================================================== 2) baglanti oturma kontrolleri
def mesafe(i, j):
    return P[i]["shape"].distToShape(P[j]["shape"])[0]


def eksen_disi(sh, nokta, yon):
    """Bir civata/vida govdesinin ekseni ile verilen eksen arasindaki uzaklik (sinir kutusu merkezinden)."""
    c = sh.BoundBox.Center
    d = c - V(*nokta)
    u = V(*yon)
    return (d - u * d.dot(u)).Length


bag_kontrol = []
for b in BAG:
    g = b["govde"]
    satir = dict(ad=b["ad"], tip=b["tip"], kontroller=[])
    k = satir["kontroller"]
    for pr in b["profiller"]:
        d = mesafe(g, pr)
        k.append(("%s -> %s dayali" % ("govde", P[pr]["ad"]), round(d, 4), d <= TEMAS))
    if b["tip"] == "kose":
        pl = b["yer"]
        T, m = A.KOSE["T"], A.KOSE["DELIK_M"]
        t_pul = WASH125[6][2]
        for ayak, (pul, civ, som), pr, (p_yuz, nv_l) in (
                ("A", b["eleman"][0:3], b["profiller"][0], ((m, 0, 0), (0, 1, 0))),
                ("B", b["eleman"][3:6], b["profiller"][1], ((0, m, 0), (1, 0, 0)))):
            nv = pl.Rotation.multVec(V(*nv_l))
            yuz = pl.multVec(V(*p_yuz))                      # profil yuzunde delik ekseni noktasi
            d_som = mesafe(som, pr)
            k.append(("ayak %s cekic somun dudak altina dayali" % ayak, round(d_som, 4), d_som <= TEMAS))
            bbc = P[civ]["shape"]
            # civata ucu derinligi: profil yuzunden iceri en uzak nokta
            uc = max((yuz - v.Point).dot(nv) for v in bbc.Vertexes)
            k.append(("ayak %s civata ucu yuzden %.1f mm iceride (kanal tabani %.1f, somun alti %.1f)" %
                      (ayak, uc, A.KANAL_TABAN, A.LIP + A.CEKIC_SOMUN["T"]), round(uc, 3),
                      A.LIP + A.CEKIC_SOMUN["T"] <= uc < A.KANAL_TABAN))
            k.append(("ayak %s civata ekseni somun deligi ekseninde" % ayak,
                      round(eksen_disi(P[som]["shape"], yuz, nv), 4), eksen_disi(P[som]["shape"], yuz, nv) < 1e-6))
            d_pul = mesafe(pul, g)
            k.append(("ayak %s pul ayaga dayali" % ayak, round(d_pul, 4), d_pul <= TEMAS))
    else:
        for e in b["eleman"]:
            d = min(mesafe(e, pr) for pr in b["profiller"])
            k.append(("set vida ucu kanal tabanina dayali (%s)" % P[e]["ad"].split("(")[0].strip(), round(d, 4), d <= TEMAS))
    satir["tamam"] = all(x[2] for x in k)
    bag_kontrol.append(satir)
print("baglanti kontrol: %d/%d tamam" % (sum(1 for s in bag_kontrol if s["tamam"]), len(bag_kontrol)), "%.1fs" % (time.time() - t0))

# ====================================================================== 3) ayrilmis bolgeler (henuz cizilmemis moduller)
CIZILI = ("iskelet", "omuz_sag", "omuz_sol")
bolge_ihlal = []
bolge_n = 0
for z in A.bolgeler(haric=CIZILI):
    kb = box(*[z["kutu"][i] for i in (0, 1, 2, 3, 4, 5)])
    for c in z["bosluk"]:
        kb = kb.cut(box(*c))
    bolge_n += 1
    for p in P:
        if not p["bb"].intersect(kb.BoundBox):
            continue
        v = p["shape"].common(kb).Volume
        if v > TOL:
            bolge_ihlal.append((z["ad"], z["sahip"], p["ad"], round(v, 2)))
print("ayrilmis bolge kontrolu:", bolge_n, "bolge,", len(bolge_ihlal), "ihlal", "%.1fs" % (time.time() - t0))

# ====================================================================== 4) kutle, agirlik merkezi, kesim listesi
M = sum(p["kutle"] for p in P)
CG = V(0, 0, 0)
for p in P:
    CG = CG + p["merkez"] * (p["kutle"] / M)
kutle_grup = {g: round(sum(p["kutle"] for p in P if p["grup"] == g), 1) for g in ("Sase", "Direk", "Travers")}
kutle_tur = {t: round(sum(p["kutle"] for p in P if p["tur"] == t), 1) for t in ("Satin", "Baglanti")}
sigma = [p for p in P if p["kod"].startswith("Sigma")]
kesim = sorted([(float(p["kod"].split(",")[1].split()[0]), p["ad"]) for p in sigma], reverse=True)
cubuklar = []   # ilk sigan azalan (FFD), testere payi her kesimde
for L, ad in kesim:
    for c in cubuklar:
        if c["kalan"] >= L + A.TESTERE:
            c["parcalar"].append((L, ad))
            c["kalan"] -= L + A.TESTERE
            break
    else:
        cubuklar.append(dict(parcalar=[(L, ad)], kalan=A.STOK_BOY - L - A.TESTERE))
toplam_boy = sum(L for L, _ in kesim)
print("kutle %.1f g, AM (%.1f, %.1f, %.1f), sigma %.1f mm -> %d x %d mm cubuk" %
      (M, CG.x, CG.y, CG.z, toplam_boy, len(cubuklar), A.STOK_BOY))

# ====================================================================== 5) egilme: direk + travers
import omuz_parcalar as O          # sag omuzun parcalari ve kinematigi (yerel koordinat)

f = I.sigma_kesit().Faces[0]
AREA = f.Area
IXX = f.MatrixOfInertia.A11         # mm4 (kesit simetrik: Ixx = Iyy)
IYY = f.MatrixOfInertia.A22
WB = IXX / A.SG * 2                 # mukavemet momenti mm3
E = A.SG_E
g = 9.81e-3                         # N/g
EL_UCU = 306.0                      # rc:81 ARM0 omuz ekseni -> el ucu (yeni omuzda tahmini)
YUK = 500.0                         # g, her elde
TRAVERS_KG = sum(p["kutle"] for p in P if p["grup"] == "Travers")   # travers + ust kose baglantilari


def kol_noktalari(phi, th, yuk=True):
    """Sag omuzun (yerel) kutle noktalari: (m [g], c [mm]). Sabit omuz parcalari + hareketli + alt kol + yuk.
    Omuz traversi ve kabuk referansi haric (traversi iskelet tasir)."""
    pts = []
    for p in O.P:
        if p["kutle"] <= 0 or p["tur"] == "Referans" or p["ad"].startswith("Omuz traversi"):
            continue
        c = O.pose_place(p, phi, th).multVec(p["merkez"])
        pts.append((p["kutle"], c))
    kol = O.Pp(phi).multiply(O.Pr(th))
    pts.append((O.ALT_KOL["m"], kol.multVec(V(*O.ALT_KOL["p"]))))
    if yuk:
        pts.append((YUK, kol.multVec(V(O.XR, -EL_UCU, O.ZC))))
    return pts


def globale(pts, sag):
    out = []
    for m, c in pts:
        x = c.x if sag else -c.x
        out.append((m, V(x, c.y + A.S3, c.z)))
    return out


def durum(sag_poz, sol_poz, yuk=True):
    pts = globale(kol_noktalari(*sag_poz, yuk=yuk), True) + globale(kol_noktalari(*sol_poz, yuk=yuk), False)
    # direk: tabandan (y = DIREK_Y0) ankastre konsol; yalniz dusey yukler -> moment boy boyunca sabit
    Mx = sum(m * g * c.z for m, c in pts)                 # N*mm, X ekseni etrafinda (one-arka egilme)
    Mz = sum(m * g * c.x for m, c in pts)                 # N*mm, Z ekseni etrafinda (yana egilme)
    N = sum(m for m, _ in pts) * g + (TRAVERS_KG + sum(p["kutle"] for p in P if p["grup"] == "Direk")) * g
    L = A.DIREK_L
    sig_d = (abs(Mx) + abs(Mz)) / WB + N / AREA             # kose noktasi (iki eksenli egilme + basi)
    dx = abs(Mz) * L ** 2 / (2 * E * IXX)
    dz = abs(Mx) * L ** 2 / (2 * E * IXX)
    th_x = abs(Mx) * L / (E * IXX)                        # tepe donmesi, rad
    th_z = abs(Mz) * L / (E * IXX)
    # travers: her yari direk yuzunden (x = 20) ankastre konsol (kose baglantilari x = 57'ye kadar destekler:
    # ihmal edildi, guvenli tarafta). Yuk yuvadan (x 70...103) girer: tekil kuvvet + moment, a = 66.5
    trav = []
    for sag in (True, False):
        q = [(m, c) for m, c in pts if (c.x > 0) == sag]
        F = sum(m for m, _ in q) * g
        xa = (A.OMUZ_YUVA_X[0] + A.OMUZ_YUVA_X[1]) / 2
        Mb = sum(m * g * (abs(c.x) - H) for m, c in q)          # N*mm, x = 20'de dusey egilme
        Mt = sum(m * g * c.z for m, c in q)                      # N*mm, burulma (travers ekseni etrafinda)
        a = xa - H
        Lc = A.TRAVERS_L / 2 - H
        M0 = Mb - F * a                                          # yuk noktasinda kalan moment
        d_uc = F * a ** 2 * (3 * Lc - a) / (6 * E * IXX) + M0 * a * (2 * Lc - a) / (2 * E * IXX)
        d_a = F * a ** 3 / (3 * E * IXX) + M0 * a ** 2 / (2 * E * IXX)
        th_a = F * a ** 2 / (2 * E * IXX) + M0 * a / (E * IXX)
        trav.append(dict(taraf="sag" if sag else "sol", F_N=F, Mb_Nmm=Mb, Mt_Nmm=Mt, sigma_MPa=abs(Mb) / WB,
                         sehim_uc_mm=d_uc, sehim_yuva_mm=d_a, donme_yuva_rad=th_a))
    return dict(Mx=Mx, Mz=Mz, N=N, sigma_direk=sig_d, sehim_tepe=math.hypot(dx, dz), donme_tepe=math.hypot(th_x, th_z),
                th_x=th_x, th_z=th_z, travers=trav, pts=pts)


def el_dususu(d, sag_poz):
    """Sag elin dusey yer degistirmesi (mm): direk tepesi donmesi x el ucunun yatay uzakligi + travers sehimi."""
    kol = O.Pp(sag_poz[0]).multiply(O.Pr(sag_poz[1]))
    e = kol.multVec(V(O.XR, -EL_UCU, O.ZC))
    tr = d["travers"][0]
    xa = (A.OMUZ_YUVA_X[0] + A.OMUZ_YUVA_X[1]) / 2
    return d["th_x"] * abs(e.z) + d["th_z"] * abs(e.x) + tr["sehim_yuva_mm"] + tr["donme_yuva_rad"] * abs(e.x - xa)


ADLI = [   # rapor metni (konsola yazilmaz)
    ("İki kol öne tam açık (öne 90°) + 0,5 kg", (90, 0), (90, 0)),
    ("İki kol yana tam açık (yana 90°) + 0,5 kg", (0, 90), (0, 90)),
    ("Sağ kol yana tam açık + 0,5 kg, sol kol aşağıda", (0, 90), (0, 0)),
    ("Sağ kol öne, sol kol yana tam açık + 0,5 kg", (90, 0), (0, 90)),
    ("İki kol aşağıda (yüksüz referans)", (0, 0), (0, 0)),
]
adli = []
for ad, sp, lp in ADLI:
    d = durum(sp, lp, yuk="yüksüz" not in ad)
    adli.append(dict(ad=ad, sag=sp, sol=lp, Mx_Nm=d["Mx"] / 1000, Mz_Nm=d["Mz"] / 1000, sigma_direk_MPa=d["sigma_direk"],
                     sehim_tepe_mm=d["sehim_tepe"], donme_tepe_derece=math.degrees(d["donme_tepe"]),
                     travers=[{k: (round(v, 4) if isinstance(v, float) else v) for k, v in t.items()} for t in d["travers"]],
                     el_dususu_mm=el_dususu(d, sp)))
# en kotu durum taramasi: her kol phi 0...180 (15), yana 0...120 (15), yuklu
izgara = [(ph, th) for ph in range(0, 181, 15) for th in range(0, 121, 15)]
eniyi = dict(direk=(0, None), travers=(0, None), sehim=(0, None))
for sp in izgara:
    for lp in izgara:
        d = durum(sp, lp)
        if d["sigma_direk"] > eniyi["direk"][0]:
            eniyi["direk"] = (d["sigma_direk"], (sp, lp, d["sehim_tepe"]))
        st = max(t["sigma_MPa"] for t in d["travers"])
        if st > eniyi["travers"][0]:
            eniyi["travers"] = (st, (sp, lp, max(t["sehim_uc_mm"] for t in d["travers"])))
        if d["sehim_tepe"] > eniyi["sehim"][0]:
            eniyi["sehim"] = (d["sehim_tepe"], (sp, lp))
SINIR_DIREK = A.DIREK_L / 500.0          # tahmini kabul: L/500
SINIR_EL = 2.0                           # mm, tahmini kabul (gorsel olarak fark edilmez)
egilme = dict(
    kesit=dict(alan_mm2=round(AREA, 1), Ixx_mm4=round(IXX, 0), Iyy_mm4=round(IYY, 0), W_mm3=round(WB, 0),
               uretici_alan_mm2=A.SG_ALAN),
    varsayim=["Direk tabandan ankastre konsol (orta ara ray + 2 köşe bağlantı rijit kabul edildi), boy %.1f mm" % A.DIREK_L,
              "Travers her yarısı direk yüzünden (x = 20) ankastre konsol; köşe bağlantıların x = 57'ye kadar desteği ihmal edildi (güvenli taraf)",
              "Yük traverse omuz yuvasından (x 70…103, orta 86,5) tekil kuvvet + moment olarak girer",
              "Kol kütleleri omuz modelinden (PETG %60 doluluk, servo 60 g); dirsek ve aşağısı 260 g, omuz ekseninden 200 mm (omuz modeli, tahmini)",
              "El ucu omuz ekseninden %.0f mm (rc:81 ARM0; yeni omuzda tahmini), her elde %.0f g yük" % (EL_UCU, YUK),
              "E = %.0f MPa, Rp0,2 = %.0f MPa (6063, temper bilinmiyor: tahmini); statik hesap, dinamik etki için ×2 pay önerilir" % (E, A.SG_RP02),
              "Kabul sınırları (tahmini): direk tepe sehimi ≤ L/500 = %.1f mm, el ucu düşey yer değiştirmesi ≤ %.1f mm" % (SINIR_DIREK, SINIR_EL),
              "Bağlantı esnekliği (köşe bağlantı, çekiç somun sürtünmesi) hesaba katılmadı; gerçek sehim daha büyük olur"],
    adli=adli,
    en_kotu=dict(direk_sigma_MPa=eniyi["direk"][0], direk_poz=eniyi["direk"][1][:2], direk_sehim_mm=eniyi["direk"][1][2],
                 travers_sigma_MPa=eniyi["travers"][0], travers_poz=eniyi["travers"][1][:2], travers_sehim_uc_mm=eniyi["travers"][1][2],
                 sehim_tepe_mm=eniyi["sehim"][0], sehim_poz=eniyi["sehim"][1], izgara_poz=len(izgara) ** 2),
    sinir=dict(direk_mm=SINIR_DIREK, el_mm=SINIR_EL, Rp02_MPa=A.SG_RP02),
)
ek = egilme["en_kotu"]
egilme["sonuc"] = dict(
    direk_emniyet=A.SG_RP02 / ek["direk_sigma_MPa"], travers_emniyet=A.SG_RP02 / ek["travers_sigma_MPa"],
    direk_sehim_uygun=ek["sehim_tepe_mm"] <= SINIR_DIREK,
    el_uygun=max(a["el_dususu_mm"] for a in adli) <= SINIR_EL)
print("egilme: direk %.2f MPa / %.3f mm, travers %.2f MPa, el %.3f mm" % (ek["direk_sigma_MPa"], ek["sehim_tepe_mm"],
      ek["travers_sigma_MPa"], max(a["el_dususu_mm"] for a in adli)), "%.1fs" % (time.time() - t0))

# ====================================================================== 6) kaydet: FCStd + STEP + BOM
doc = App.newDocument("IskeletMontaj")
kok = doc.addObject("App::Part", "Iskelet")
kok.Label = "Iskelet_V3"
gruplar = {}
for gname, lab in (("Sase", "Sase_cercevesi"), ("Direk", "Govde_diregi"), ("Travers", "Omuz_traversi")):
    gp = kok.newObject("App::Part", gname)
    gp.Label = lab
    gruplar[gname] = gp
for k, p in enumerate(P):
    o = gruplar[p["grup"]].newObject("Part::Feature", "P%03d" % k)
    o.Label = p["ad"]
    o.Shape = p["shape"]
    for prop, val in (("Tur", p["tur"]), ("Malzeme", p["malzeme"]), ("Kod", p["kod"]), ("Renk", p["renk"]), ("Not", p["not_"])):
        o.addProperty("App::PropertyString", prop, "Robot")
        setattr(o, prop, val)
    o.addProperty("App::PropertyVector", "Patlat", "Robot")
    o.Patlat = V(*p["patlat"])
    o.addProperty("App::PropertyFloat", "Kutle_g", "Robot")
    o.Kutle_g = round(p["kutle"], 1)
doc.recompute()
doc.saveAs(os.path.join(HERE, "iskelet-montaj.FCStd"))
Part.Compound([p["shape"] for p in P]).exportStep(os.path.join(HERE, "iskelet-montaj.step"))
# STEP geri okuma testi
st = Part.read(os.path.join(HERE, "iskelet-montaj.step"))
step_kati = len(st.Solids)

bom = {}
for p in P:
    key = (p["tur"], p["kod"])
    if key not in bom:
        bom[key] = dict(adet=0, kutle=0.0)
    bom[key]["adet"] += 1
    bom[key]["kutle"] += p["kutle"]
with open(os.path.join(HERE, "iskelet-bom.csv"), "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(["Tur", "Kalem", "Adet", "Toplam kutle (g)"])
    for (t, kod), v in sorted(bom.items()):
        w.writerow([t, kod, v["adet"], "%.1f" % v["kutle"]])

# ====================================================================== 7) analiz json
out = dict(
    parca_sayisi=len(P),
    gecersiz=gecersiz, coklu_kati=coklu,
    cakisma=cakisma, cakisma_cift_sayisi=n_cift, tolerans_mm3=TOL,
    baglanti=[dict(ad=b["ad"], tip=b["tip"], aciklama=b["aciklama"], profiller=[P[i]["ad"] for i in b["profiller"]],
                   govde=P[b["govde"]]["ad"], eleman=[P[i]["kod"] for i in b["eleman"]]) for b in BAG],
    baglanti_kontrol=bag_kontrol,
    bolge=dict(kontrol_edilen=bolge_n, ihlal=bolge_ihlal, sahipler=sorted(set(z["sahip"] for z in A.bolgeler(haric=CIZILI)))),
    kutle_g=round(M, 1), kutle_grup=kutle_grup, kutle_tur=kutle_tur,
    agirlik_merkezi=[round(CG.x, 2), round(CG.y, 2), round(CG.z, 2)],
    kesim=dict(parcalar=[[L, ad] for L, ad in kesim], toplam_mm=toplam_boy, stok_mm=A.STOK_BOY, testere_mm=A.TESTERE,
               cubuklar=[dict(parcalar=c["parcalar"], artik=round(c["kalan"], 1)) for c in cubuklar],
               kutle_uretici_g=round(toplam_boy / 1000 * A.SG_KG_M * 1000, 0),
               kutle_model_g=round(sum(p["kutle"] for p in sigma), 1)),
    egilme=egilme,
    bom=[[t, kod, v["adet"], round(v["kutle"], 1)] for (t, kod), v in sorted(bom.items())],
    step_kati=step_kati,
    sure_s=round(time.time() - t0, 1),
)
json.dump(out, open(os.path.join(HERE, "iskelet-analiz.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("STEP kati", step_kati, "bitti %.1fs" % (time.time() - t0))
