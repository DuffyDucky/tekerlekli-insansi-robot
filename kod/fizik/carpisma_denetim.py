"""Y0f: kol - gövde / kol - kafa / kol - kol çarpışması, CAD parçalarının DIŞBÜKEY ZARFLARIYLA (MuJoCo temas denetimi).

Kaba bir ikinci bakıştır; kesin tarama P10.8d'deki FreeCAD katı taramasıdır (planlama/d158/P108d-kontrol-olcum, b2-log:
"kol sag: aralikta cakisan tam poz 0 / 1755", "kol-kol: cakisan 0"). Burada her CAD parçası (1.251 parça, ham ağ
önbellekte: model_uret.py --cad) kendi dışbükey zarfıyla temsil edilir. İçbükey parçanın zarfı parçadan büyüktür, bu yüzden
yöntem çarpışmayı FAZLA bulur (muhafazakâr); "temas yok" sonucu güvenilir, "temas var" sonucu incelenmelidir.

Ev pozunda (bütün eklemler 0, S2 5 derece) zaten dokunan zarf çiftleri montaj teması sayılır (yanyana oturan parçalar,
horn - göbek); bu çiftler ev derinliğinden 2 mm daha derine girerse yine temas sayılır. Poz ızgarası eklem_sinirlari.json aralıklarında, bağımlı sınır (S1 >= 120 iken S2 <= 117) uygulanarak.
"""

import json
import math
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)
import dunya as D  # noqa: E402
import model_uret as MU  # noqa: E402

KOL_GOVDE = {"sag": ["sag_omuz_gobek", "sag_ust_kol", "sag_on_kol", "sag_el"],
             "sol": ["sol_omuz_gobek", "sol_ust_kol", "sol_on_kol", "sol_el"]}
EN_COK_KOSE = 400
DALMA_ESIGI_M = 0.0005           # 0,5 mm'den derin zarf girişimi temas sayılır
MONTAJ_PAYI_M = 0.002            # ev pozunda dokunan çift, ev derinliğinden 2 mm daha derine girerse yine sayılır


def _stl_kose(yol):
    with open(yol, "rb") as f:
        veri = f.read()
    n = struct.unpack_from("<I", veri, 80)[0]
    return [struct.unpack_from("<12f", veri, 84 + 50 * i)[3:12] for i in range(n)]


def model_xml():
    """lale.xml'in gövde / eklem ağacı (geom'suz) + her CAD parçası için zarf geom'u."""
    import mujoco
    cad = MU.oku(os.path.join(BURASI, "model", "cad_govdeler.json"))
    ham = os.path.join(MU.onbellek(), "cad_ham")
    if not os.path.isdir(ham):
        raise RuntimeError("ham CAD ağı yok (%s): önce py -3 kod/fizik/model_uret.py --cad" % ham)
    w = D.FizikDunya(None, None, (0, 0, 0))
    mujoco.mj_forward(w.m, w.d)
    govde_konum = {w.m.body(i).name: [float(v) for v in w.d.xpos[i]] for i in range(w.m.nbody)}
    with open(os.path.join(BURASI, "model", "lale.xml"), encoding="utf-8") as f:
        metin = f.read()
    metin = metin[metin.index("<worldbody>"):metin.index("</worldbody>") + len("</worldbody>")]
    kok = ET.fromstring("<mujoco>" + re.sub(r"<!--.*?-->", "", metin, flags=re.S) + "</mujoco>")
    grup_govde = {}
    for ad, _, gruplar, _ in MU.AGAC:
        for g in gruplar:
            grup_govde[g] = ad
    mesh, geom = [], {}
    for g, govde in grup_govde.items():
        if govde.startswith("teker"):
            continue
        ucg = _stl_kose(os.path.join(ham, g + ".stl"))
        o = govde_konum[govde]
        taraf = "sag" if govde.startswith("sag_") else "sol" if govde.startswith("sol_") else "sabit"
        ct, ca = {"sag": (1, 4), "sol": (5, 0), "sabit": (0, 1)}[taraf]
        for k, p in enumerate(cad["gruplar"][g]["parcalar"]):
            if "ucgen" not in p:
                continue
            s, n = p["ucgen"]
            kose = {}
            for t in ucg[s:s + n]:
                for j in range(3):
                    r = MU.nokta(t[3 * j:3 * j + 3])
                    q = tuple(round(r[i] - o[i], 5) for i in range(3))
                    kose[q] = 1
            kose = list(kose)
            if len(kose) < 4:
                continue
            lo = [min(c[i] for c in kose) for i in range(3)]
            hi = [max(c[i] for c in kose) for i in range(3)]
            if min(hi[i] - lo[i] for i in range(3)) < 0.0003:      # düz levha: zarf hacimsiz, 0,3 mm kalınlık ver
                kose += [(c[0] + 0.0003, c[1] + 0.0003, c[2] + 0.0003) for c in kose[:50]]
            if len(kose) > EN_COK_KOSE:
                adim = len(kose) / float(EN_COK_KOSE)
                kose = [kose[int(i * adim)] for i in range(EN_COK_KOSE)] + [tuple(lo), tuple(hi)]
            ad = "p_%s_%d" % (g, k)
            mesh.append('<mesh name="%s" vertex="%s"/>' % (ad, " ".join("%.5f" % v for c in kose for v in c)))
            geom.setdefault(govde, []).append('<geom name="%s" type="mesh" mesh="%s" contype="%d" conaffinity="%d"/>'
                                              % (ad, ad, ct, ca))
            geom_ad_parca[ad] = (g, p["ad"])

    def govde_yaz(b, girinti):
        ad = b.get("name")
        sat = ['%s<body name="%s" pos="%s">' % (girinti, ad, b.get("pos", "0 0 0"))]
        sat.append('%s  <inertial pos="0 0 0" mass="0.1" diaginertia="1e-4 1e-4 1e-4"/>' % girinti)
        for j in b.findall("joint"):
            sat.append('%s  <joint name="%s" axis="%s" range="%s"/>' % (girinti, j.get("name"), j.get("axis"), j.get("range")))
        for gx in geom.get(ad, []):
            sat.append(girinti + "  " + gx)
        for c in b.findall("body"):
            if c.get("name").startswith("teker"):
                continue
            sat += govde_yaz(c, girinti + "  ")
        sat.append("%s</body>" % girinti)
        return sat

    wb = kok.find("worldbody")
    taban = wb.find("body")
    x = ['<mujoco model="lale_zarf"><compiler angle="degree" inertiafromgeom="false"/>',
         '<option><flag gravity="disable"/></option><size memory="200M"/>', "<asset>"] + mesh + ["</asset><worldbody>"]
    x += govde_yaz(taban, "")
    x.append("</worldbody></mujoco>")
    return "\n".join(x)


geom_ad_parca = {}


def tara(adim_derece=15):
    import mujoco
    m = mujoco.MjModel.from_xml_string(model_xml())
    d = mujoco.MjData(m)
    sinir = MU.oku(os.path.join(os.path.dirname(BURASI), "ortak", "eklem_sinirlari.json"))
    jid = {m.joint(i).name: i for i in range(m.njnt)}

    def kur(aci):
        d.qpos[:] = 0
        for ad, a in aci.items():
            d.qpos[m.jnt_qposadr[jid[ad]]] = math.radians(a)
        mujoco.mj_forward(m, d)
        cift = {}
        for i in range(d.ncon):
            c = d.contact[i]
            if c.dist < -DALMA_ESIGI_M:
                k = tuple(sorted((m.geom(c.geom1).name, m.geom(c.geom2).name)))
                cift[k] = min(cift.get(k, 0.0), c.dist)
        return cift

    ev = {"sag_omuz_yan": 5, "sol_omuz_yan": 5}
    montaj = kur(ev)
    sonuc = dict(yontem=__doc__.strip().split("\n\n")[0], zarf_sayisi=m.ngeom, montaj_temasi_cift=len(montaj),
                 montaj_temasi_ornek=sorted(" / ".join("%s:%s" % geom_ad_parca[g] for g in k) for k in montaj)[:10],
                 dalma_esigi_mm=DALMA_ESIGI_M * 1000, adim_derece=adim_derece, kollar={}, kol_kol={})
    rng = lambda a, b, s: list(range(int(a), int(b) + 1, s)) + ([int(b)] if (int(b) - int(a)) % s else [])
    S1 = rng(-45, 135, adim_derece)
    S2 = rng(5, 120, adim_derece)
    DR = rng(0, 105, adim_derece)
    BL = [-90, 0, 90]
    for t in ("sag", "sol"):
        poz = carp = uzak = 0
        ornek = {}
        derin = 0.0
        for s1 in S1:
            for s2 in S2:
                if s1 >= 120 and s2 > 117:
                    continue
                for dr in DR:
                    for bl in BL:
                        a = dict(ev)
                        a.update({"%s_omuz" % t: s1, "%s_omuz_yan" % t: s2, "%s_dirsek" % t: dr, "%s_bilek" % t: bl})
                        yeni = {k: v for k, v in kur(a).items() if k not in montaj or v < montaj[k] - MONTAJ_PAYI_M}
                        poz += 1
                        if yeni:
                            carp += 1
                            if any(geom_ad_parca[g][0].startswith(("Dirsek", "Kafa")) for k in yeni for g in k):
                                uzak += 1
                            for k, v in yeni.items():
                                ad = " / ".join("%s:%s" % geom_ad_parca[g] for g in k)
                                if ad not in ornek or v < ornek[ad][0]:
                                    ornek[ad] = (v, [s1, s2, dr, bl])
                                derin = min(derin, v)
        sonuc["kollar"][t] = dict(poz=poz, temasli_poz=carp, en_derin_mm=-derin * 1000,
                                  dirsek_el_ya_da_kafa_temasli_poz=uzak,
                                  ciftler=sorted(([k, round(-v[0] * 1000, 1), v[1]] for k, v in ornek.items()),
                                                 key=lambda r: -r[1])[:15])
    # kol - kol: iki kol aynı anda öne (S1 45 / 90 / 135), dirsek ve bilek tarama; omuz yan 5
    poz = carp = 0
    for s1 in (0, 45, 90, 135):
        for dr in DR:
            for bl in BL:
                a = {"sag_omuz": s1, "sol_omuz": s1, "sag_omuz_yan": 5, "sol_omuz_yan": 5, "sag_dirsek": dr, "sol_dirsek": dr,
                     "sag_bilek": bl, "sol_bilek": bl}
                yeni = {k: v for k, v in kur(a).items() if (k not in montaj or v < montaj[k] - MONTAJ_PAYI_M) and (k[0].startswith("p_Dirsek") or k[0].startswith("p_Omuz"))
                        and any(g in geom_ad_parca and ("Sag" in geom_ad_parca[g][0]) for g in k)
                        and any(g in geom_ad_parca and ("Sol" in geom_ad_parca[g][0]) for g in k)}
                poz += 1
                carp += bool(yeni)
    sonuc["kol_kol"] = dict(poz=poz, temasli_poz=carp)
    sonuc["yorum"] = ("zarf temasları omuz mekanizmasında (göbek, kol çatalı, tambur ipi <-> omuz gövdesi, rulman kapağı, S1 "
                      "kaseti): bunlar iç içe dönen eş eksenli parçalar, içbükey çatal / halkanın zarfı mili yutuyor. "
                      "dirsek_el_ya_da_kafa_temasli_poz = üst kol / ön kol / el ya da kafa parçasının karıştığı poz sayısı.")
    sonuc["eklem_sinirlari_kaynak"] = sinir.get("kaynak", "kod/ortak/eklem_sinirlari.json")
    sonuc["cad_kesin_tarama"] = ("P10.8d FreeCAD katı taraması: kol sağ / sol aralıkta çakışan tam poz 0 / 1755, kol-kol 0 "
                                 "(planlama/d158/P108d-kontrol-olcum/b2-log)")
    return sonuc


if __name__ == "__main__":
    print(json.dumps(tara(), ensure_ascii=False, indent=1))
