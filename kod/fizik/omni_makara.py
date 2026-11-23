"""Y0f: ön omni tekerin MAKARALI fizik modeli (ONERI-MAKARA varyantı; VARSAYIM, aday teker Nexus 14075 seçilmedi).

Parametreler tek dosyada: `kod/fizik/omni_teker.json` (ürün sayfası / TAHMİN / modelleme ayrımıyla). Bu modül onu okur ve
`lale.xml` metninde ön iki tekeri göbek + 22 makaralı tekere çevirir (`dunya.model_kur`, varyant `on_teker` = "makara").

Model:
  - Göbek: tekerin kendi gövdesi (motor eklemi, enkoder açısı, motor torku aynı yerde); kütle = teker - makaralar; atalet
    disk yaklaşımı (TAHMİN). Göbeğin çarpışma geometrisi YOK (düz zeminde, rampada ve 15 mm'ye dek eşikte göbeğe değen bir şey
    olmaz: makaralar dış çemberi kesintisiz kaplar).
  - Makara: her biri ayrı gövde, kendi ekseninde (teker çemberine teğet) pasif menteşe; yatak sürtünmesi eklemde sabit Coulomb
    momenti (eşdeğer yanal kuvvet x makara yarıçapı) + küçük viskoz sönüm. İki sıra x 11, sıralar yarım adım (16,36°)
    kaydırılmış, eksenel ±5 mm.
  - Temas biçimi: fıçı yüzeyi elipsoidle (temas bölgesinde fıçı kesiti teker dış çemberindedir). Elipsoidin eksen yarı boyu a,
    teker dönerken etkin yarıçap sapması en küçük olacak biçimde seçilir (elipsoid_a). Bu a fiziksel makara boyundan uzundur;
    fazla kısım teker dış çemberinin içinde kalır (düz zeminde, rampada ve eşik köşesinde temas vermez; sivri bir engelin
    makaralar arasına girdiği durumda gerçekte olmayan temas verebilir). Seçenekler: "kureler" (eksen üzerinde 5 küre, MuJoCo'nun
    kesin küre çarpışması; çapraz denetim), "kapsul" (aynı çap, gerçek boy; çember sapması 0,36 mm, titreşim duyarlılığı).
  - İki sayısal ayar (omni_teker.json, "modelleme"): elipsoid-kutu teması genel dışbükey çarpışmadan gelir, ccd toleransı 1e-9
    (varsayılan 1e-6 ile rampada temasların ≈ %3'ünde normal 28° sapıp sahte çekiş veriyordu); makara ekleminin Coulomb
    sürtünme kısıtı solimpfriction 0,9999 (varsayılan 0,9 ile makaranın küçük ataleti yüzünden kısıt yumuşak kalıp sürtünmeyi
    yok sayıyordu).
Doğru verdiği: ayrık temas (her an 1-2 makara), sıra geçişinde temas noktasının eksenel sıçraması (±5 mm), makara yatağının
yanal direnci, makaranın kendi ataleti, etkin yarıçap sapması (elipsoidde ≈ 0, kapsülde ölçülür), eşik köşesine makara
yüzeyiyle değme. Kaba verdiği: kauçuğun yerel esnekliği ve histerezisi (MuJoCo yumuşak teması solref ile, tek nokta), temas
yaması, yükle değişen pim sürtünmesi (sabit Coulomb), makara uçlarının ve göbek tırnaklarının geometrisi, imalat salgısı.
"""

import json
import math
import os

BURASI = os.path.dirname(os.path.abspath(__file__))
PARAMETRE = os.path.join(BURASI, "omni_teker.json")


def yukle(degis=None):
    """omni_teker.json değerleri {ad: değer}; `degis` ile duyarlılık için üzerine yazılır."""
    with open(PARAMETRE, encoding="utf-8") as f:
        p = {k: v["deger"] for k, v in json.load(f)["parametreler"].items()}
    for k, v in (degis or {}).items():
        if k not in p:
            raise KeyError("bilinmeyen omni parametresi: %s" % k)
        p[k] = v
    return p


def geometri(p):
    """Türetilen ölçüler (m): R dış yarıçap, rho makara yarıçapı, Rc makara ekseninin teker merkezine uzaklığı, adım açısı,
    sıra kaydırma, eksenel sıra yarı aralığı, makara boyu, temas şeklinin boyutları."""
    R = p["teker_dis_capi_mm"] / 2000.0
    rho = p["makara_capi_mm"] / 2000.0
    n_sira = int(p["sira_sayisi"])
    n = int(p["makara_sayisi_toplam"]) // n_sira
    adim = 2 * math.pi / n
    g = dict(R=R, rho=rho, Rc=R - rho, n_sira=n_sira, n=n, adim=adim, kaydirma=math.radians(p["sira_kaydirma_derece"]),
             e=p["sira_eksen_araligi_mm"] / 2000.0, boy=p["makara_boyu_mm"] / 1000.0, bicim=p["temas_bicimi"])
    g["a"] = elipsoid_a(g) if g["bicim"] == "elipsoid" else None
    g["hl"] = max(0.0, g["boy"] / 2 - rho) if g["bicim"] == "kapsul" else None
    g["kureler"] = None
    if g["bicim"] == "kureler":
        g["kureler"] = kure_dizisi(g, kureler_smax(g))
    return g


def kure_dizisi(g, s_max, n=5):
    """Makara ekseni üzerinde n küre: (eksen konumu s, yarıçap); her kürenin dış ucu teker dış çemberine değer."""
    out = []
    for k in range(n):
        s = -s_max + 2 * s_max * k / (n - 1)
        out.append((s, g["R"] - math.hypot(g["Rc"], s)))
    return out


def _uzanim(g, alfa, a=None):
    """Teker düzleminde, makara merkez doğrultusundan alfa açısındaki yönde temas şeklinin teker merkezinden uzanımı."""
    s, c = abs(math.sin(alfa)), math.cos(alfa)
    if g["bicim"] == "elipsoid":
        a = g["a"] if a is None else a
        return g["Rc"] * c + math.sqrt(a * a * s * s + g["rho"] ** 2 * c * c)
    if g["bicim"] == "kureler":
        kk = kure_dizisi(g, a) if a is not None else g["kureler"]
        return max(math.hypot(g["Rc"], sk) * math.cos(abs(alfa) - math.atan2(abs(sk), g["Rc"])) + rk for sk, rk in kk)
    return g["Rc"] * c + g["hl"] * s + g["rho"]


def kureler_smax(g):
    """Küre dizisinin uç küre konumu: sapmayı en küçük yapan (altın oran araması, fiziksel makara boyu içinde)."""
    def sapma(sm):
        r = [etkin_yaricap(g, k * g["kaydirma"] / 40.0, sm) for k in range(41)]
        return max(r) - min(r)
    lo, hi = 0.2 * g["boy"] / 2, g["boy"] / 2
    for _ in range(50):
        m1, m2 = lo + (hi - lo) * 0.382, lo + (hi - lo) * 0.618
        if sapma(m1) < sapma(m2):
            hi = m2
        else:
            lo = m1
    return (lo + hi) / 2


def etkin_yaricap(g, phi, a=None):
    """Düz zeminde teker phi açısındayken etkin yarıçap: bütün makaraların en çok uzananı (eksenel konum yüksekliği etkilemez)."""
    en = 0.0
    for j in range(g["n_sira"]):
        for i in range(g["n"]):
            th = i * g["adim"] + j * g["kaydirma"]
            d = math.atan2(math.sin(phi - th), math.cos(phi - th))
            if abs(d) < math.pi / 2:
                en = max(en, _uzanim(g, d, a))
    return en


def elipsoid_a(g):
    """Etkin yarıçap sapmasını (en büyük - en küçük, bir sıra geçişi boyunca) en küçük yapan a (altın oran araması)."""
    def sapma(a):
        r = [etkin_yaricap(g, k * g["kaydirma"] / 40.0, a) for k in range(41)]
        return max(r) - min(r) + abs(max(r) - g["R"])
    lo, hi = g["rho"], 6 * g["rho"]
    for _ in range(60):
        m1, m2 = lo + (hi - lo) * 0.382, lo + (hi - lo) * 0.618
        if sapma(m1) < sapma(m2):
            hi = m2
        else:
            lo = m1
    return (lo + hi) / 2


def sapma_ozeti(g):
    """(en küçük, en büyük etkin yarıçap m, makara geçiş sayısı / tur)."""
    r = [etkin_yaricap(g, k * 2 * math.pi / 3600) for k in range(3600)]
    return min(r), max(r), g["n"] * g["n_sira"]


def _f(x):
    return "%.6g" % x


def teker_xml(ad, girinti, pos, p, g):
    """Bir ön tekerin MJCF gövdesi (eklem adı ve motor aynı: ad)."""
    G = girinti
    m_makara = p["makara_kutlesi_g"] / 1000.0
    m_gobek = p["teker_kutlesi_g"] / 1000.0 - m_makara * g["n"] * g["n_sira"]
    r_d, h_d = g["Rc"] + 0.002, p["teker_eksenel_genislik_mm"] / 1000.0
    Iyy = 0.5 * m_gobek * r_d * r_d
    Ixx = m_gobek * (3 * r_d * r_d + h_d * h_d) / 12.0
    rho, boy = g["rho"], g["boy"]
    I_eks = 0.5 * m_makara * rho * rho
    I_yan = m_makara * (3 * rho * rho + boy * boy) / 12.0
    surt = p["makara_yatak_surtunmesi_N"] * rho          # Coulomb momenti N·m
    r_uc = math.sqrt(max(0.0, g["R"] ** 2 - (boy / 2) ** 2)) - g["Rc"]
    s = ['%s<body name="%s" pos="%s">' % (G, ad, pos),
         '%s  <inertial pos="0 0 0" mass="%s" diaginertia="%s %s %s"/>' % (G, _f(m_gobek), _f(Ixx), _f(Iyy), _f(Ixx)),
         '%s  <joint name="%s" class="teker" axis="0 1 0"/>' % (G, ad)]
    # görsel göbek: iki alüminyum plaka + orta göbek (çarpışmasız)
    for yy in (-g["e"], g["e"]):
        s.append('%s  <geom type="cylinder" contype="0" conaffinity="0" group="2" mass="0" fromto="0 %s 0 0 %s 0" size="%s" '
                 'rgba="0.72 0.74 0.78 1"/>' % (G, _f(yy - 0.0015), _f(yy + 0.0015), _f(g["Rc"] - 0.004)))
    s.append('%s  <geom type="cylinder" contype="0" conaffinity="0" group="2" mass="0" fromto="0 %s 0 0 %s 0" size="0.016" '
             'rgba="0.55 0.57 0.6 1"/>' % (G, _f(-h_d / 2), _f(h_d / 2)))
    for j in range(g["n_sira"]):
        yy = (-g["e"], g["e"])[j] if g["n_sira"] == 2 else 0.0
        for i in range(g["n"]):
            th = i * g["adim"] + j * g["kaydirma"]
            cx, cz = g["Rc"] * math.sin(th), -g["Rc"] * math.cos(th)    # th = 0: en altta
            tx, tz = math.cos(th), math.sin(th)                          # teğet (makara ekseni)
            mk = "%s_mk_%s%02d" % (ad, "ab"[j], i)
            if g["bicim"] == "elipsoid":
                carp = ['<geom name="c_%s" class="teker_carpisma" type="ellipsoid" size="%s %s %s"/>' % (mk, _f(g["a"]), _f(rho), _f(rho))]
            elif g["bicim"] == "kureler":
                carp = ['<geom name="c_%s_k%d" class="teker_carpisma" type="sphere" pos="%s 0 0" size="%s"/>' % (mk, k, _f(sk), _f(rk))
                        for k, (sk, rk) in enumerate(g["kureler"])]
            else:
                carp = ['<geom name="c_%s" class="teker_carpisma" type="capsule" fromto="%s 0 0 %s 0 0" size="%s"/>' % (
                    mk, _f(-g["hl"]), _f(g["hl"]), _f(rho))]
            s += ['%s  <body name="%s" pos="%s %s %s" xyaxes="%s 0 %s 0 1 0">' % (G, mk, _f(cx), _f(yy), _f(cz), _f(tx), _f(tz)),
                  '%s    <inertial pos="0 0 0" mass="%s" diaginertia="%s %s %s"/>' % (G, _f(m_makara), _f(I_eks), _f(I_yan), _f(I_yan)),
                  '%s    <joint name="%s" type="hinge" axis="1 0 0" frictionloss="%s" damping="%s" armature="%s" '
                  'solimpfriction="%s %s 0.001" solreffriction="0.02 1"/>' % (
                      G, mk, _f(surt), _f(p["makara_yatak_sonumu_Nms_rad"]), _f(p["makara_armatur_kgm2"]),
                      _f(p["makara_surtunme_solimp"]), _f(p["makara_surtunme_solimp"]))]
            s += ['%s    %s' % (G, c) for c in carp]
            s += [
                  # görsel fıçı: silindir (uç çapı) + kısa elipsoid (orta şişkinlik); dönüşü görünsün diye bir çizgi
                  '%s    <geom type="cylinder" contype="0" conaffinity="0" group="2" mass="0" fromto="%s 0 0 %s 0 0" size="%s" '
                  'rgba="0.13 0.13 0.15 1"/>' % (G, _f(-boy / 2), _f(boy / 2), _f(r_uc)),
                  '%s    <geom type="ellipsoid" contype="0" conaffinity="0" group="2" mass="0" size="%s %s %s" rgba="0.13 0.13 0.15 1"/>' % (
                      G, _f(boy / 2 * 0.98), _f(rho), _f(rho)),
                  '%s    <geom type="box" contype="0" conaffinity="0" group="2" mass="0" pos="0 0 %s" size="%s 0.0012 0.0006" '
                  'rgba="0.85 0.6 0.15 1"/>' % (G, _f(rho * 0.97), _f(boy / 2 * 0.8)),
                  '%s  </body>' % G]
    s.append('%s</body>' % G)
    return "\n".join(s)


def makara_xml(x, p=None, y_iceri_m=0.0):
    """lale.xml metninde ön iki tekeri makaralı omniye çevirir. Aks yeri aynı (teker merkezi), ön uç R - 0,0625 kadar yükselir;
    y_iceri_m: dar teker, iç yüzü aynı yerde (varyantlar.ADAY_TEKER gibi)."""
    import re
    p = p or yukle()
    g = geometri(p)
    for yan in ("sol", "sag"):
        ad = "teker_on_" + yan
        m = re.search(r'( *)<body name="%s" pos="([^"]+)">(.*?)\n\1</body>' % ad, x, flags=re.S)
        if m is None:
            raise RuntimeError("lale.xml'de %s gövdesi bulunamadı" % ad)
        px, py_, pz = (float(t) for t in m.group(2).split())
        if y_iceri_m:
            py_ -= math.copysign(y_iceri_m, py_)
        yeni = teker_xml(ad, m.group(1), "%s %s %s" % (_f(px), _f(py_), _f(pz)), p, g)
        x = x[:m.start()] + yeni + x[m.end():]
    # görünüm: tekerler grup 2'de (göbek / makara yukarıda; arka lastiklerin ağı buraya taşınır). Pencerede 1 tuşu gövde
    # ağlarını (grup 1, etek dahil) gizler, tekerler görünür kalır. Fizik etkilenmez.
    for yan in ("sol", "sag"):
        x = x.replace('<geom class="gorsel" mesh="m_teker_arka_%s"' % yan, '<geom class="gorsel" group="2" mesh="m_teker_arka_%s"' % yan)
    return x


if __name__ == "__main__":
    p = yukle()
    for b in ("elipsoid", "kureler", "kapsul"):
        g = geometri(dict(p, temas_bicimi=b))
        lo, hi, n = sapma_ozeti(g)
        if g["kureler"]:
            print("kureler", [("%.2f" % (s_ * 1000), "%.2f" % (r_ * 1000)) for s_, r_ in g["kureler"]])
        print("%-8s a %s mm  etkin yaricap %.3f..%.3f mm (sapma %.3f mm), %d makara gecisi / tur" % (
            b, "-" if g["a"] is None else "%.2f" % (g["a"] * 1000), lo * 1000, hi * 1000, (hi - lo) * 1000, n))
