"""Y0f: Lale'nin fizik modelini (MuJoCo MJCF) CAD verisinden üretir. Yalnız standart kitaplık.

Kullanım (depo kökünden):
    py -3 kod/fizik/model_uret.py --cad     # önce FreeCAD'den yeniden çıkar (cad_cikar.py, ~20 s), sonra üret
    py -3 kod/fizik/model_uret.py           # yalnız üret (kod/fizik/model/cad_govdeler.json ve ham ağ önbelleğinden)

Girdi:  kod/fizik/model/cad_govdeler.json (cad_cikar.py çıktısı: grup kütlesi, AM, atalet, sınır kutusu)
        tasarim/freecad/montaj/montaj-analiz.json (eklem noktası / ekseni / sınırı, montaj kütlesi ve AM'si)
        kod/ortak/eklem_sinirlari.json, kod/ortak/robot_parametreleri.json, kod/fizik/fizik_parametreleri.json
        $LALE_FIZIK_ONBELLEK/cad_ham/*.stl (ham CAD ağı; varsayılan %LOCALAPPDATA%/lale-fizik-onbellek; OneDrive dışında)
Çıktı:  kod/fizik/model/lale.xml (robot; sahne dunya.py'de eklenir), kod/fizik/model/ag/*.stl (seyreltilmiş görsel ağ,
        gövde çerçevesinde, m), kod/fizik/model/kutle_karsilastirma.json / .md (fark tablosu)

Çerçeve: robot +x ileri (CAD +Z), +y robotun kendi solu (CAD +X, K65), +z yukarı (CAD +Y); orijin zemin + robot merkezi.
Ev pozunda (bütün eklem açıları 0, montajdaki duruş) her gövde çerçevesi dünya eksenlerine paralel, orijini eklem noktasında.
"""

import argparse
import json
import math
import os
import struct
import subprocess
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
KOD = os.path.dirname(BURASI)
KOK = os.path.dirname(KOD)
MODEL = os.path.join(BURASI, "model")
AG = os.path.join(MODEL, "ag")
MONTAJ = os.path.join(KOK, "tasarim", "freecad", "montaj", "montaj-analiz.json")
TABAN_ANALIZ = os.path.join(KOK, "tasarim", "freecad", "taban", "taban-analiz.json")
FCSTD = os.path.join(KOK, "tasarim", "freecad", "montaj", "robot-montaj.FCStd")


def onbellek():
    v = os.environ.get("LALE_FIZIK_ONBELLEK")
    if v:
        return v
    return os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "lale-fizik-onbellek")


def oku(yol):
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------ CAD -> robot çerçevesi
def nokta(p_mm):
    """CAD (X, Y, Z) mm -> robot (x ileri, y sol, z yukarı) m."""
    return [p_mm[2] / 1000.0, p_mm[0] / 1000.0, p_mm[1] / 1000.0]


def eksen(e):
    return [float(e[2]), float(e[0]), float(e[1])]


_P = (2, 0, 1)   # robot ekseni a = CAD ekseni _P[a]


def tensor(I_g_mm2):
    """CAD g*mm^2 tensörü -> robot çerçevesi kg*m^2."""
    return [[I_g_mm2[_P[a]][_P[b]] * 1e-9 for b in range(3)] for a in range(3)]


def paralel(I, m, d):
    d2 = sum(x * x for x in d)
    return [[I[i][j] + m * ((d2 if i == j else 0.0) - d[i] * d[j]) for j in range(3)] for i in range(3)]


def birlestir(parcalar):
    """[(m kg, c m, I kg m2 AM'de)] -> (m, c, I AM'de)."""
    m = sum(p[0] for p in parcalar)
    c = [sum(p[0] * p[1][i] for p in parcalar) / m for i in range(3)]
    I = [[0.0] * 3 for _ in range(3)]
    for pm, pc, pI in parcalar:
        Ip = paralel(pI, pm, [pc[i] - c[i] for i in range(3)])
        I = [[I[i][j] + Ip[i][j] for j in range(3)] for i in range(3)]
    return m, c, I


# ------------------------------------------------------------------ gövde ağacı (montaj eklem zinciri)
# Gövde adlarında sağ / sol ROBOTUN KENDİ çerçevesidir (protokol.json servo adları gibi). CAD grup adları önden bakanın
# sağı / solu (K65, planlama/d158/sag-sol-karari.md): CAD "Sag" grupları (+X) robotun kendi SOLUNDA.
# (gövde adı, ebeveyn, montaj grupları, montaj eklemi (montaj-analiz eklemler.isim) ya da None)
AGAC = [
    ("taban", None, ["Taban_Govde"], "serbest"),
    ("govde", "taban", ["Iskelet", "Kabuk", "OmuzSag_Govde", "OmuzSol_Govde", "Kafa_Govde"], None),
    ("kafa_boyun", "govde", ["Kafa_Boyun"], "Kafa_Pan"),
    ("kafa_bas", "kafa_boyun", ["Kafa_Bas"], "Kafa_Tilt"),
    ("sag_omuz_gobek", "govde", ["OmuzSol_Gobek"], "OmuzSol_OneArka"),
    ("sag_ust_kol", "sag_omuz_gobek", ["OmuzSol_Kol", "DirsekSol_UstKol"], "OmuzSol_Yana"),
    ("sag_on_kol", "sag_ust_kol", ["DirsekSol_OnKol"], "DirsekSol_Dirsek"),
    ("sag_el", "sag_on_kol", ["DirsekSol_El"], "DirsekSol_Bilek"),
    ("sol_omuz_gobek", "govde", ["OmuzSag_Gobek"], "OmuzSag_OneArka"),
    ("sol_ust_kol", "sol_omuz_gobek", ["OmuzSag_Kol", "DirsekSag_UstKol"], "OmuzSag_Yana"),
    ("sol_on_kol", "sol_ust_kol", ["DirsekSag_OnKol"], "DirsekSag_Dirsek"),
    ("sol_el", "sol_on_kol", ["DirsekSag_El"], "DirsekSag_Bilek"),
    ("teker_on_sol", "taban", ["Taban_OnSagTeker"], "Taban_TekerOnSag"),
    ("teker_arka_sol", "taban", ["Taban_ArkaSagTeker"], "Taban_TekerArkaSag"),
    ("teker_on_sag", "taban", ["Taban_OnSolTeker"], "Taban_TekerOnSol"),
    ("teker_arka_sag", "taban", ["Taban_ArkaSolTeker"], "Taban_TekerArkaSol"),
]
# montaj eklemi -> (protokol servo adı, servo türü). Eklem sınırı protokol.json servolar[].eklem -> eklem_sinirlari.json.
# Not: eklem_sinirlari.json r_* / l_* "taraf" alanı CAD adını izler (r_s1 ayna False = CAD +X), protokol ise robotun kendi
# sağını; sınırlar iki yanda aynı olduğu için sonuç değişmez (Y0f-gunluk.md Ç-f1).
EKLEM_ESLE = {
    "OmuzSol_OneArka": ("sag_omuz", "ds3235"), "OmuzSol_Yana": ("sag_omuz_yan", "ds3235"),
    "DirsekSol_Dirsek": ("sag_dirsek", "mg996r"), "DirsekSol_Bilek": ("sag_bilek", "mg996r"),
    "OmuzSag_OneArka": ("sol_omuz", "ds3235"), "OmuzSag_Yana": ("sol_omuz_yan", "ds3235"),
    "DirsekSag_Dirsek": ("sol_dirsek", "mg996r"), "DirsekSag_Bilek": ("sol_bilek", "mg996r"),
    "Kafa_Pan": ("kafa_pan", "mg996r"), "Kafa_Tilt": ("kafa_tilt", "mg996r"),
}


# ------------------------------------------------------------------ ağ: oku, seyrelt, yaz
def stl_oku(yol):
    with open(yol, "rb") as f:
        veri = f.read()
    n = struct.unpack_from("<I", veri, 80)[0]
    ucgen = []
    for i in range(n):
        v = struct.unpack_from("<12f", veri, 84 + 50 * i)
        ucgen.append((v[3:6], v[6:9], v[9:12]))
    return ucgen


def seyrelt(ucgenler, hucre):
    """Köşe kümeleme: aynı hücreye düşen köşeler ortalamada birleşir; çökmüş ve yinelenen üçgenler atılır."""
    anahtar, toplam = {}, {}
    def k(p):
        return (int(math.floor(p[0] / hucre)), int(math.floor(p[1] / hucre)), int(math.floor(p[2] / hucre)))
    for u in ucgenler:
        for p in u:
            kk = k(p)
            t = toplam.setdefault(kk, [0.0, 0.0, 0.0, 0])
            t[0] += p[0]; t[1] += p[1]; t[2] += p[2]; t[3] += 1
    for kk, t in toplam.items():
        anahtar[kk] = (t[0] / t[3], t[1] / t[3], t[2] / t[3])
    cikan, gorulen = [], set()
    for u in ucgenler:
        a, b, c = (k(p) for p in u)
        if a == b or b == c or a == c:
            continue
        imza = tuple(sorted((a, b, c)))
        if imza in gorulen:
            continue
        gorulen.add(imza)
        cikan.append((anahtar[a], anahtar[b], anahtar[c]))
    return cikan


def stl_yaz(yol, ucgenler):
    with open(yol, "wb") as f:
        f.write(b"Lale Y0f seyreltilmis gorsel ag (govde cercevesi, m)".ljust(80, b" "))
        f.write(struct.pack("<I", len(ucgenler)))
        for a, b, c in ucgenler:
            u = [b[i] - a[i] for i in range(3)]
            v = [c[i] - a[i] for i in range(3)]
            n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
            L = math.sqrt(sum(x * x for x in n)) or 1.0
            f.write(struct.pack("<12fH", n[0] / L, n[1] / L, n[2] / L, *a, *b, *c, 0))


def f(x):
    return "%.6g" % x


def v3(v):
    return " ".join(f(x) for x in v)


# ------------------------------------------------------------------ ana iş
def uret(cad_yeniden=False, hucre_m=0.005):
    if cad_yeniden:
        fc = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "FreeCAD 1.1", "bin", "freecadcmd.exe")
        bas = os.path.join(os.path.expanduser("~"), ".robot-cad", "run_fc.py")
        env = dict(os.environ, FC_SCRIPT=os.path.join(BURASI, "cad_cikar.py"), LALE_FCSTD=FCSTD, LALE_CIKTI=MODEL,
                   LALE_HAM=os.path.join(onbellek(), "cad_ham"))
        print("FreeCAD: cad_cikar.py (robot-montaj.FCStd geçici kopyadan okunur) ...")
        r = subprocess.run([fc, bas], env=env, cwd=os.environ.get("TEMP", None), capture_output=True, text=True,
                           errors="replace")
        for satir in r.stdout.splitlines():
            if satir.startswith(("grup", "TOPLAM")):
                print("  " + satir)
        if r.returncode != 0 or "TOPLAM" not in r.stdout:
            print(r.stdout[-2000:], r.stderr[-2000:])
            raise SystemExit("cad_cikar.py başarısız")

    cad = oku(os.path.join(MODEL, "cad_govdeler.json"))
    montaj = oku(MONTAJ)
    taban_analiz = oku(TABAN_ANALIZ)
    eklem_sinir = oku(os.path.join(KOD, "ortak", "eklem_sinirlari.json"))
    robot_par = oku(os.path.join(KOD, "ortak", "robot_parametreleri.json"))["parametreler"]
    fp = oku(os.path.join(BURASI, "fizik_parametreleri.json"))["parametreler"]
    eklemler = {e["isim"]: e for e in montaj["eklemler"]}
    servo_eklem = {sv["ad"]: sv["eklem"] for sv in oku(os.path.join(KOD, "ortak", "protokol.json"))["servolar"]["liste"]}
    G = cad["gruplar"]

    # gövde orijinleri (robot çerçevesi, ev pozu)
    orijin = {}
    for ad, ebeveyn, gruplar, ek in AGAC:
        if ek in (None, "serbest"):
            orijin[ad] = [0.0, 0.0, 0.0] if ebeveyn is None else orijin[ebeveyn]
        else:
            orijin[ad] = nokta(eklemler[ek]["nokta"])

    # gövde kütle / AM / atalet (gruplardan); kablo payı tabana nokta kütle
    govde = {}
    for ad, ebeveyn, gruplar, ek in AGAC:
        pp = []
        for g in gruplar:
            gg = G[g]
            pp.append((gg["kutle_g"] / 1000.0, nokta(gg["am_mm"]), tensor(gg["atalet_am_g_mm2"])))
        if ad == "taban":
            kp = fp["kablo_payi"]["deger"]
            pp.append((kp["kutle_g"] / 1000.0, nokta(kp["merkez_cad_mm"]), [[0.0] * 3 for _ in range(3)]))
        govde[ad] = birlestir(pp)

    # toplam (model) ve karşılaştırma
    m_top = sum(b[0] for b in govde.values())
    c_top = [sum(b[0] * b[1][i] for b in govde.values()) / m_top for i in range(3)]
    kp = fp["kablo_payi"]["deger"]
    mm = montaj["kutle_g"] / 1000.0
    cm = nokta(montaj["agirlik_merkezi"])
    m_bek = mm + kp["kutle_g"] / 1000.0
    c_bek = [(mm * cm[i] + kp["kutle_g"] / 1000.0 * nokta(kp["merkez_cad_mm"])[i]) / m_bek for i in range(3)]
    ev = next(p for p in taban_analiz["robot"]["pozlar"] if p["kod"] == "ev")
    c_ta = nokta(ev["am"])
    I_top = [[0.0] * 3 for _ in range(3)]
    for b in govde.values():
        Ip = paralel(b[2], b[0], [b[1][i] - c_top[i] for i in range(3)])
        I_top = [[I_top[i][j] + Ip[i][j] for j in range(3)] for i in range(3)]
    kars = dict(
        model=dict(kutle_kg=m_top, am_m=c_top, atalet_am_kgm2=I_top),
        satirlar=[
            dict(kaynak="montaj-analiz.json kutle_g / agirlik_merkezi (kablosuz) + kablo payi 400 g (taban-analiz.json, TAHMIN)",
                 kutle_kg=m_bek, am_m=c_bek),
            dict(kaynak="montaj-analiz.json (kablosuz, yalniz CAD parcalari)", kutle_kg=mm, am_m=cm,
                 not_="model bundan kablo payi kadar agir (400 g)"),
            dict(kaynak="taban-analiz.json robot.pozlar[ev] (kablo payli; tarih farkli montajdan)", kutle_kg=ev["kutle_g"] / 1000.0,
                 am_m=c_ta),
        ],
        cad_toplam_cikarim=dict(kutle_kg=cad["toplam"]["kutle_g"] / 1000.0, am_m=nokta(cad["toplam"]["am_mm"]),
                                not_="cad_cikar.py'nin FCStd'den okudugu (parca Kutle_g toplami, geometrik AM)"),
        atalet_kaynagi=cad["atalet_yontemi"],
        govdeler={ad: dict(kutle_kg=b[0], am_m=b[1], atalet_am_kgm2=b[2], gruplar=next(a[2] for a in AGAC if a[0] == ad))
                  for ad, b in govde.items()},
    )
    for s in kars["satirlar"]:
        s["fark_kutle_g"] = (m_top - s["kutle_kg"]) * 1000.0
        s["fark_am_mm"] = [(c_top[i] - s["am_m"][i]) * 1000.0 for i in range(3)]

    # görsel ağ (ham önbellek varsa)
    ham = os.path.join(onbellek(), "cad_ham")
    os.makedirs(AG, exist_ok=True)
    ag_var = {}
    for ad, ebeveyn, gruplar, ek in AGAC:
        o = orijin[ad]
        u = []
        for g in gruplar:
            yol = os.path.join(ham, g + ".stl")
            if not os.path.exists(yol):
                continue
            for tri in stl_oku(yol):
                u.append(tuple(tuple(x - o[i] for i, x in enumerate(nokta(p))) for p in tri))
        cikis = os.path.join(AG, ad + ".stl")
        if u:
            s = seyrelt(u, hucre_m)
            stl_yaz(cikis, s)
            ag_var[ad] = len(s)
        elif os.path.exists(cikis):
            ag_var[ad] = -1                # önbellek yok, eski (depodaki) ağ kullanılır
    # ---- MJCF
    r_teker = robot_par["teker_capi_m"]["deger"] / 2.0
    teker_gen = 0.058
    mu = fp["teker_zemin_surtunme"]["deger"]
    mu_g = fp["govde_zemin_surtunme"]["deger"]
    solref = fp["temas_solref_s"]["deger"]
    servo_tork = {"ds3235": fp["servo_ds3235_tork_Nm"]["deger"], "mg996r": fp["servo_mg996r_tork_Nm"]["deger"]}

    def kutu_robot(gruplar_, alt_y=None, ust_y=None, sec=None):
        kk = []
        for g in gruplar_:
            for p in G[g]["parcalar"]:
                if "kutu" not in p or (sec and not sec(p)):
                    continue
                kk.append(p["kutu"])
        lo = [min(k[0][i] for k in kk) for i in range(3)]
        hi = [max(k[1][i] for k in kk) for i in range(3)]
        if alt_y is not None:
            lo[1] = max(lo[1], alt_y)
        if ust_y is not None:
            hi[1] = min(hi[1], ust_y)
        a, b = nokta(lo), nokta(hi)
        return [min(a[i], b[i]) for i in range(3)], [max(a[i], b[i]) for i in range(3)]

    def kutu_geom(ad, lo, hi, o, sinif="carpisma", ek_=""):
        merkez = [(lo[i] + hi[i]) / 2.0 - o[i] for i in range(3)]
        yari = [(hi[i] - lo[i]) / 2.0 for i in range(3)]
        return '<geom name="%s" class="%s" type="box" pos="%s" size="%s"%s/>' % (ad, sinif, v3(merkez), v3(yari), ek_)

    def kapsul_geom(ad, lo, hi, o):
        # dikey (z) kapsül; yarıçap yatay kesitin küçük yarısı
        merkez = [(lo[i] + hi[i]) / 2.0 - o[i] for i in range(3)]
        r = min(hi[0] - lo[0], hi[1] - lo[1]) / 2.0
        yari_boy = max(1e-3, (hi[2] - lo[2]) / 2.0 - r)
        return '<geom name="%s" class="kol_carpisma" type="capsule" pos="%s" size="%s %s"/>' % (ad, v3(merkez), f(r), f(yari_boy))

    carp = {}
    o = orijin["taban"]
    lo, hi = kutu_robot(["Kabuk"], sec=lambda p: p["ad"].startswith("Etek"))
    carp["taban"] = [kutu_geom("c_etek", lo, hi, o)]
    o = orijin["govde"]
    lo, hi = kutu_robot(["Kabuk"], alt_y=262.0, sec=lambda p: not p["ad"].startswith("Etek"))
    carp["govde"] = [kutu_geom("c_govde", lo, hi, o)]
    o = orijin["kafa_bas"]
    lo, hi = kutu_robot(["Kafa_Bas"])
    carp["kafa_bas"] = [kutu_geom("c_kafa", lo, hi, o)]
    for t in ("sag", "sol"):
        T = "Sol" if t == "sag" else "Sag"          # robotun kendi sağı = CAD "Sol" (K65)
        lo, hi = kutu_robot(["Omuz%s_Kol" % T, "Dirsek%s_UstKol" % T])
        carp["%s_ust_kol" % t] = [kapsul_geom("c_%s_ust_kol" % t, lo, hi, orijin["%s_ust_kol" % t])]
        lo, hi = kutu_robot(["Dirsek%s_OnKol" % T])
        carp["%s_on_kol" % t] = [kapsul_geom("c_%s_on_kol" % t, lo, hi, orijin["%s_on_kol" % t])]
        lo, hi = kutu_robot(["Dirsek%s_El" % T])
        carp["%s_el" % t] = [kapsul_geom("c_%s_el" % t, lo, hi, orijin["%s_el" % t])]

    renk = {"taban": "0.35 0.36 0.4 1", "govde": "0.86 0.84 0.8 1", "kafa_bas": "0.9 0.9 0.92 1",
            "kafa_boyun": "0.4 0.4 0.45 1"}

    def govde_xml(ad, girinti):
        g = " " * girinti
        b = govde[ad]
        o = orijin[ad]
        ebeveyn = next(a[1] for a in AGAC if a[0] == ad)
        ek = next(a[3] for a in AGAC if a[0] == ad)
        poz = [o[i] - (orijin[ebeveyn][i] if ebeveyn else 0.0) for i in range(3)]
        satir = ['%s<body name="%s" pos="%s">' % (g, ad, v3(poz))]
        I = b[2]
        satir.append('%s  <inertial pos="%s" mass="%s" fullinertia="%s"/>' % (
            g, v3([b[1][i] - o[i] for i in range(3)]), f(b[0]),
            v3([I[0][0], I[1][1], I[2][2], I[0][1], I[0][2], I[1][2]])))
        if ek == "serbest":
            satir.append('%s  <freejoint name="kok"/>' % g)
        elif ek is not None:
            e = eklemler[ek]
            if ad.startswith("teker"):
                satir.append('%s  <joint name="%s" class="teker" axis="%s"/>' % (g, ad, v3(eksen(e["eksen"]))))
            else:
                servo, tur = EKLEM_ESLE[ek]
                s = eklem_sinir["eklemler"][servo_eklem[servo]]
                satir.append('%s  <joint name="%s" class="servo_eklem" axis="%s" range="%s %s"/>' % (
                    g, servo, v3(eksen(e["eksen"])), f(s["min"]), f(s["max"])))
        if ad in ag_var:
            satir.append('%s  <geom class="gorsel" mesh="m_%s" rgba="%s"/>' % (
                g, ad, renk.get(ad, "0.75 0.73 0.7 1" if "kol" in ad or "el" in ad or "omuz" in ad else "0.2 0.2 0.22 1")))
        if ad.startswith("teker"):
            satir.append('%s  <geom name="c_%s" class="teker_carpisma" type="cylinder" size="%s %s" pos="0 0 0" '
                         'quat="0.7071068 0.7071068 0 0"/>' % (g, ad, f(r_teker), f(teker_gen / 2.0)))
        for c in carp.get(ad, []):
            satir.append(g + "  " + c)
        if ad == "taban":
            for sad, s in robot_par["sonarlar"]["liste"].items():
                satir.append('%s  <site name="sonar_%s" pos="%s %s 0.110" size="0.012" rgba="0.1 0.6 0.9 1"/>' % (
                    g, sad, f(s["x_m"]), f(s["y_m"])))
            satir.append('%s  <site name="imu" pos="0 0 0.2" size="0.01"/>' % g)
        for cocuk in [a[0] for a in AGAC if a[1] == ad]:
            satir.extend(govde_xml(cocuk, girinti + 2))
        satir.append("%s</body>" % g)
        return satir

    gorsel_ag = "\n".join('    <mesh name="m_%s" file="%s.stl" inertia="shell"/>' % (ad, ad) for ad in ag_var)
    servo_satir = []
    for ad, ebeveyn, gruplar, ek in AGAC:
        if ek in EKLEM_ESLE:
            servo, tur = EKLEM_ESLE[ek]
            servo_satir.append('    <position name="servo_%s" joint="%s" kp="%s" kv="%s" forcerange="-%s %s" ctrlrange="-3.2 3.2"/>' % (
                servo, servo, f(fp["servo_kp_Nm_rad"]["deger"]), f(fp["servo_kv_Nms_rad"]["deger"]),
                f(servo_tork[tur]), f(servo_tork[tur])))
    stall = fp["motor_durma_torku_Nm"]["deger"]
    motor_satir = ['    <motor name="motor_%s" joint="%s" ctrlrange="-%s %s"/>' % (ad, ad, f(3 * stall), f(3 * stall))
                   for ad in ("teker_on_sol", "teker_arka_sol", "teker_on_sag", "teker_arka_sag")]

    xml = """<!-- Y0f Lale fizik modeli. URETILIR: py -3 kod/fizik/model_uret.py (elle duzenleme).
     Kutle / AM / atalet: CAD (kod/fizik/model/cad_govdeler.json, FreeCAD katilarindan); eklemler: montaj-analiz.json;
     eklem siniri: kod/ortak/eklem_sinirlari.json; temas, motor, servo: kod/fizik/fizik_parametreleri.json (cogu TAHMIN).
     Carpisma geometrisi ilkel sekiller (etek / govde / kafa kutusu, kol kapsulleri, teker silindirleri); gorsel ag CAD'den.
     Sahne (zemin, duvar, rampa) kod/fizik/dunya.py'de eklenir: <!--SAHNE--> isareti. -->
<mujoco model="lale">
  <compiler angle="degree" meshdir="__AG__" inertiafromgeom="false" autolimits="true"/>
  <option timestep="%(dt)s" integrator="implicitfast" cone="elliptic" gravity="0 0 -9.81"/>
  <size memory="64M"/>
  <visual><global offwidth="1280" offheight="720"/><quality shadowsize="2048"/></visual>
  <default>
    <geom solref="%(solref)s 1"/>
    <default class="gorsel"><geom type="mesh" contype="0" conaffinity="0" group="1" density="0"/></default>
    <default class="carpisma"><geom contype="2" conaffinity="1" group="3" friction="%(mug)s 0.005 0.0001" rgba="0.9 0.5 0.1 0.25"/></default>
    <default class="kol_carpisma"><geom contype="2" conaffinity="1" group="3" friction="0.4 0.005 0.0001" rgba="0.9 0.5 0.1 0.25"/></default>
    <default class="teker_carpisma"><geom contype="2" conaffinity="1" group="3" friction="%(mu)s 0.005 0.0001" rgba="0.1 0.1 0.1 0.6" condim="3"/></default>
    <default class="teker"><joint type="hinge" armature="%(arm)s" frictionloss="%(fl)s" damping="0"/></default>
    <default class="servo_eklem"><joint type="hinge" armature="%(sarm)s" damping="0.05"/></default>
  </default>
  <asset>
%(ag)s
  </asset>
  <worldbody>
    <!--SAHNE-->
%(govde)s
  </worldbody>
  <contact>
    <exclude body1="taban" body2="govde"/>
  </contact>
  <actuator>
%(motor)s
%(servo)s
  </actuator>
  <sensor>
    <framepos name="taban_konum" objtype="body" objname="taban"/>
    <subtreecom name="am" body="taban"/>
  </sensor>
</mujoco>
""" % dict(dt=f(fp["zaman_adimi_s"]["deger"]), solref=f(solref), mug=f(mu_g), mu=f(mu),
           arm=f(fp["motor_yansiyan_atalet_kgm2"]["deger"]), fl=f(fp["motor_disli_surtunme_Nm"]["deger"]),
           sarm=f(fp["servo_yansiyan_atalet_kgm2"]["deger"]), ag=gorsel_ag, govde="\n".join(govde_xml("taban", 4)),
           motor="\n".join(motor_satir), servo="\n".join(servo_satir))
    with open(os.path.join(MODEL, "lale.xml"), "w", encoding="utf-8") as fh:
        fh.write(xml)
    kars["ag_ucgen"] = ag_var
    with open(os.path.join(MODEL, "kutle_karsilastirma.json"), "w", encoding="utf-8") as fh:
        json.dump(kars, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(MODEL, "kutle_karsilastirma.md"), "w", encoding="utf-8") as fh:
        fh.write(karsilastirma_md(kars))
    print(karsilastirma_md(kars))
    return kars


def karsilastirma_md(k):
    m = k["model"]
    s = ["# Lale fizik modeli: kütle ve ağırlık merkezi karşılaştırması (üretilir: `kod/fizik/model_uret.py`)", "",
         "Robot çerçevesi: x ileri, y robotun kendi solu, z yukarı; orijin zemin + robot merkezi; ev pozu. AM mm.", "",
         "| Kaynak | Kütle (g) | AM x | AM y | AM z | Fark kütle (g) | Fark AM (mm) |", "| --- | --- | --- | --- | --- | --- | --- |",
         "| **Model** (`lale.xml` gövdeleri toplamı) | %.1f | %.2f | %.2f | %.2f | | |" % (
             m["kutle_kg"] * 1000, m["am_m"][0] * 1000, m["am_m"][1] * 1000, m["am_m"][2] * 1000)]
    for r in k["satirlar"]:
        s.append("| %s | %.1f | %.2f | %.2f | %.2f | %+.2f | %s |" % (
            r["kaynak"], r["kutle_kg"] * 1000, r["am_m"][0] * 1000, r["am_m"][1] * 1000, r["am_m"][2] * 1000,
            r["fark_kutle_g"], " / ".join("%+.2f" % x for x in r["fark_am_mm"])))
    I = m["atalet_am_kgm2"]
    s += ["", "Model toplam atalet tensörü (AM'de, kg·m²): Ixx %.4f, Iyy %.4f, Izz %.4f, Ixy %.5f, Ixz %.5f, Iyz %.5f." % (
        I[0][0], I[1][1], I[2][2], I[0][1], I[0][2], I[1][2]),
          "Atalet kaynağı: %s. Karşılaştırılacak CAD atalet değeri yok (montaj-analiz.json ataleti yazmıyor)." % k["atalet_kaynagi"],
          "", "| Gövde | Montaj grupları | Kütle (g) | AM x / y / z (mm) | Ixx / Iyy / Izz (kg·m²) |", "| --- | --- | --- | --- | --- |"]
    for ad, b in k["govdeler"].items():
        s.append("| %s | %s | %.1f | %.1f / %.1f / %.1f | %.5f / %.5f / %.5f |" % (
            ad, ", ".join(b["gruplar"]), b["kutle_kg"] * 1000, b["am_m"][0] * 1000, b["am_m"][1] * 1000, b["am_m"][2] * 1000,
            b["atalet_am_kgm2"][0][0], b["atalet_am_kgm2"][1][1], b["atalet_am_kgm2"][2][2]))
    s.append("")
    return "\n".join(s)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cad", action="store_true", help="önce FreeCAD'den yeniden çıkar")
    a = ap.parse_args()
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    uret(cad_yeniden=a.cad)
