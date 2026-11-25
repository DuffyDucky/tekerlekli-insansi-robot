"""Duvar etiketleri (AprilTag 36h11): doku üretimi, etiket planı (ayrı JSON dosyası), sahneye ekleme ve kafa kamerası.

Mevcut sahne JSON'ları ve ortak modüller DEĞİŞMEZ. Ekleme bu süreç içinde `dunya` modülünün üç adını sarmalayarak
yapılır (`kur()`):
  - `dunya.MODEL_XML` -> `lale.xml`'in kafa kameralı kopyası (sonuc/ham/onbellek/, her çağrıda depodaki lale.xml'den
    yeniden üretilir; tek fark kafa_bas gövdesine eklenen <camera name="kafa_kamera">),
  - `dunya.VARLIK` -> + etiket dokuları / malzemeleri + opak duvar malzemesi; asıl yarı saydam duvar malzemesi görünmez
    yapılır (fiziği etkilemez: yalnız rgba),
  - `dunya.sahne_xml` -> asıl sahne + yalnız görsel geom'lar (grup 2, contype 0): 2,7 m yüksek opak duvarlar (asıl
    duvarlar 1,0 m ve yarı saydam; kafa kamerası 1,565 m'de olduğu için duvarın üstünden boşluğa bakardı) ve etiketler.
Görsel geom'lar grup 2'de: sonar / LiDAR ışınları yalnız grup 0'a çarpar (dunya.isin), çarpışma yok, `engel_*` adı yok.
Böylece robotun yolu etiketli ve etiketsiz sahnede aynıdır (test).

Etiket boyu = siyah karenin kenarı (solvePnP'nin kullandığı); baskıda çevresinde 1 hücre beyaz pay vardır (toplam kenar
boy x 10 / 8)."""

import json
import math
import os

from sanalray import _yol

SOZLUK = "DICT_APRILTAG_36h11"
HUCRE_PX = 24                       # doku: hücre başına piksel (8 hücre etiket + 2 hücre beyaz pay = 240 px)
DUVAR_YUKSEKLIK_M = 2.70            # görsel duvar (VARSAYIM: okul koridoru tavanı ≈ 2,7-3 m; tavan çizilmez)
YUKSEKLIKLER = {"goz": 1.55, "kapi_ustu": 2.20}   # etiket merkezi z (m); kamera 1,565 m (CAD)
KIMLIK_BLOK = 50                    # koridor_N etiketleri: 50 (N-1) .. 50 (N-1) + 49 (her koridor ayrı kimlik)
DUVAR_PAYI_M = 0.004                # etiket yüzü duvar çizgisinden bu kadar içeride (duvar levhası 2 mm)


# ------------------------------------------------------------------ doku
def etiket_resmi(kimlik, hucre_px=HUCRE_PX):
    """Beyaz paylı etiket görüntüsü (uint8, kare, (8 + 2) x hucre_px)."""
    import cv2
    import numpy as np
    d = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, SOZLUK))
    ic = cv2.aruco.generateImageMarker(d, int(kimlik), 8 * hucre_px)
    out = np.full((10 * hucre_px, 10 * hucre_px), 255, np.uint8)
    out[hucre_px:9 * hucre_px, hucre_px:9 * hucre_px] = ic
    return out


def doku_yolu(kimlik):
    import cv2
    import numpy as np
    os.makedirs(_yol.ONBELLEK, exist_ok=True)
    yol = os.path.join(_yol.ONBELLEK, "tag36h11_v2_%03d.png" % int(kimlik))
    if not os.path.exists(yol):
        # MuJoCo 2B dokuyu satırları ters çevirerek kaplar: dikey aynalanmış yazılır (sınandı: aynasız kod çözülmez)
        im = np.ascontiguousarray(etiket_resmi(kimlik)[::-1])
        ok, buf = cv2.imencode(".png", cv2.cvtColor(im, cv2.COLOR_GRAY2BGR))   # imwrite ASCII dışı yolda yazmaz
        with open(yol, "wb") as f:
            f.write(buf.tobytes())
    return yol


# ------------------------------------------------------------------ plan
def _sahne(ad):
    with open(os.path.join(_yol.FIZIK, "sahneler", ad + ".json"), encoding="utf-8") as f:
        return json.load(f)


def _harita(ad):
    from gezinme.duzenek import sahne_yukle
    from sahte_esp32.harita import Harita
    a, s, veri = sahne_yukle(ad)
    return Harita(veri, ad=a)


def _hatlar(s):
    out = [("orta_hat", [tuple(p) for p in s["orta_hat"]])]
    if s.get("orta_hat_yan_kol"):
        out.append(("orta_hat_yan_kol", [tuple(p) for p in s["orta_hat_yan_kol"]]))
    return out


def _nokta_yon(P, s):
    for a, b in zip(P, P[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if s <= L + 1e-9:
            t = s / L if L else 0.0
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), math.atan2(b[1] - a[1], b[0] - a[0])
        s -= L
    a, b = P[-2], P[-1]
    return tuple(b), math.atan2(b[1] - a[1], b[0] - a[0])


def _boy(P):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(P, P[1:]))


def _duvara_koy(h, x, y, aci, en_cok=6.0):
    """(x, y)'den aci yönündeki duvar: etiket merkezi (duvar yüzünün DUVAR_PAYI içi) ve yüz normali (ışının tersi)."""
    r = h.isin(x, y, aci, en_cok)
    if r is None:
        return None
    d = r[0] - DUVAR_PAYI_M
    return (x + d * math.cos(aci), y + d * math.sin(aci), math.atan2(-math.sin(aci), -math.cos(aci)), r[0], r[1])


def plan_uret(kor, aralik, boy_m=0.15, yukseklik="goz"):
    """Koridor için etiket planı. aralik: "kavsak" (yalnız uç duvarlar + köşe / kavşak karşı duvarları) ya da metre
    (ek olarak yan duvarlarda her `aralik` m'de bir, sırayla sol / sağ, koridora paralel). Döner: plan sözlüğü."""
    s = _sahne(kor)
    h = _harita(kor)
    n = int(kor.split("_")[-1])
    z = YUKSEKLIKLER[yukseklik] if isinstance(yukseklik, str) else float(yukseklik)
    etk = []

    def ekle(tur, k, hat, s_m):
        if k is None:
            return
        x, y, nyaw, d, gelis = k
        for e in etk:                                   # aynı yere ikinci etiket koyma
            if math.hypot(e["x"] - x, e["y"] - y) < 0.5 and abs(math.atan2(math.sin(e["yaw"] - nyaw), math.cos(e["yaw"] - nyaw))) < 0.3:
                return
        etk.append(dict(tur=tur, x=round(x, 4), y=round(y, 4), z=z, yaw=round(nyaw, 5), boy_m=boy_m, hat=hat,
                        s_m=round(s_m, 3)))

    hatlar = _hatlar(s)
    # karşı duvarlar: hattın uçları ve köşeleri (gidiş yönünde ileri / geri)
    for ad, P in hatlar:
        L = _boy(P)
        s0 = 0.0
        for i, p in enumerate(P):
            if i > 0:
                s0 += math.hypot(p[0] - P[i - 1][0], p[1] - P[i - 1][1])
            gelen = math.atan2(p[1] - P[i - 1][1], p[0] - P[i - 1][0]) if i > 0 else None
            giden = math.atan2(P[i + 1][1] - p[1], P[i + 1][0] - p[0]) if i + 1 < len(P) else None
            if ad == "orta_hat_yan_kol" and i == 0:
                # kavşak: yan kolun karşısındaki ana duvar (yan koldan gelen görür)
                ekle("kavsak", _duvara_koy(h, p[0], p[1], giden + math.pi), ad, 0.0)
                continue
            if gelen is not None:
                ekle("uc" if i == len(P) - 1 else "kose", _duvara_koy(h, p[0], p[1], gelen), ad, s0)
            if giden is not None:
                ekle("uc" if i == 0 else "kose", _duvara_koy(h, p[0], p[1], giden + math.pi), ad, s0)
        del L
    # T kavşağı: ana hattan bakınca yan kolun girişinin iki yanı yerine ana hattın kavşak noktası (yan kolun ucu
    # zaten "uc"); ek yok.
    if aralik != "kavsak":
        A = float(aralik)
        taraf = 1
        for ad, P in hatlar:
            L = _boy(P)
            nk = max(1, int(math.floor((L - 1.0) / A)))
            bas = (L - (nk - 1) * A) / 2.0 if nk > 1 else L / 2.0
            for k in range(nk):
                s_m = bas + k * A
                konuldu = False
                for kay in (0.0, 0.3, -0.3, 0.6, -0.6, 0.9, -0.9, 1.2, -1.2):
                    ss = min(max(0.3, s_m + kay), L - 0.3)
                    (px, py), yon = _nokta_yon(P, ss)
                    k_ = _duvara_koy(h, px, py, yon + taraf * math.pi / 2)
                    # kapı girintisi / açıklığı olmayan düz duvar: sağ ve sol 0,25 m ötede de aynı uzaklık
                    if k_ is None:
                        continue
                    iyi = True
                    for dd in (-0.25, 0.25):
                        (qx, qy), _ = _nokta_yon(P, min(max(0.0, ss + dd), L))
                        r2 = h.isin(qx, qy, yon + taraf * math.pi / 2, 6.0)
                        if r2 is None or abs(r2[0] - k_[3]) > 0.01:
                            iyi = False
                    if iyi and k_[3] < 2.5:
                        ekle("yan", k_, ad, ss)
                        konuldu = True
                        break
                taraf = -taraf
                del konuldu
    for i, e in enumerate(sorted(etk, key=lambda e: (e["hat"], e["s_m"]))):
        e["id"] = KIMLIK_BLOK * (n - 1) + i
    etk.sort(key=lambda e: e["id"])
    if len(etk) > KIMLIK_BLOK:
        raise ValueError("%s: %d etiket > kimlik bloğu %d" % (kor, len(etk), KIMLIK_BLOK))
    return dict(koridor=kor, aralik=aralik, boy_m=boy_m, yukseklik=yukseklik, z_m=z, sozluk=SOZLUK,
                etiketler=etk, sayi=len(etk),
                aciklama="x, y etiket yüzünün merkezi (harita çerçevesi); yaw yüz normalinin yönü (koridora bakar); "
                         "boy_m siyah karenin kenarı; kimlik koridorlar arasında tekil")


def plan_adi(kor, aralik, boy_m, yukseklik):
    return "%s_%s_%dcm_%s" % (kor, "kavsak" if aralik == "kavsak" else "%gm" % float(aralik), round(boy_m * 100), yukseklik)


def plan_yaz(plan):
    os.makedirs(_yol.PLANLAR, exist_ok=True)
    yol = os.path.join(_yol.PLANLAR, plan_adi(plan["koridor"], plan["aralik"], plan["boy_m"], plan["yukseklik"]) + ".json")
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=1)
    return yol


def plan_oku(kor, aralik, boy_m=0.15, yukseklik="goz", uret=True):
    yol = os.path.join(_yol.PLANLAR, plan_adi(kor, aralik, boy_m, yukseklik) + ".json")
    if os.path.exists(yol):
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    if not uret:
        raise FileNotFoundError(yol)
    p = plan_uret(kor, aralik, boy_m, yukseklik)
    plan_yaz(p)
    return p


# ------------------------------------------------------------------ MJCF
def _g(x):
    return "%.6g" % x


def etiket_varlik(kimlikler):
    s = []
    for k in sorted(set(int(i) for i in kimlikler)):
        s.append('<texture name="tx_etk_%d" type="2d" file="%s"/>' % (k, doku_yolu(k).replace("\\", "/")))
        s.append('<material name="mt_etk_%d" texture="tx_etk_%d" texrepeat="1 1" texuniform="false" '
                 'specular="0" shininess="0" reflectance="0"/>' % (k, k))
    return "\n    ".join(s)


def etiket_geom(e, ad=None):
    """Tek etiket: dikey ince kutu, 1 mm (yerel z = yüz normali, yerel y = dünya yukarı). Düzlem (plane) geom'u dokuyu
    düşük karşıtlıkla çiziyordu (siyah 88 / beyaz 150; kutu 0 / 229)."""
    yaw = e["yaw"]
    nx, ny = math.cos(yaw), math.sin(yaw)
    rx, ry = ny, -nx                     # bakan için sağ: -n x z
    yari = e["boy_m"] / 2.0 * 10.0 / 8.0
    return ('<geom name="%s" type="box" pos="%s %s %s" size="%s %s 0.0005" xyaxes="%s %s 0 0 0 1" material="mt_etk_%d" '
            'contype="0" conaffinity="0" group="2"/>' % (ad or "etiket_%d" % e["id"], _g(e["x"]), _g(e["y"]), _g(e["z"]),
                                                         _g(yari), _g(yari), _g(rx), _g(ry), e["id"]))


def gorsel_duvarlar(harita, yuk=DUVAR_YUKSEKLIK_M, kal=0.002):
    """Asıl duvarların (dunya.sahne_xml) aynı yerde, `yuk` yüksek, opak, yalnız görsel kopyası (grup 2)."""
    s = []
    w, h = harita.genislik, harita.yukseklik
    cevre = []
    if harita.veri.get("cevre_duvari", True):
        cevre = [(0, 0, w, 0), (w, 0, w, h), (w, h, 0, h), (0, h, 0, 0)]
    for n, (x1, y1, x2, y2) in enumerate(harita.parcalar):
        boy = math.hypot(x2 - x1, y2 - y1)
        if boy < 1e-9:
            continue
        a = math.atan2(y2 - y1, x2 - x1)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        k = kal
        if (x1, y1, x2, y2) in cevre:
            mx, my = (cx - w / 2), (cy - h / 2)
            nx, ny = -math.sin(a), math.cos(a)
            if nx * mx + ny * my < 0:
                nx, ny = -nx, -ny
            cx, cy, boy, k = cx + nx * 0.05, cy + ny * 0.05, boy + 0.2, 0.1
        q = (math.cos(a / 2), 0, 0, math.sin(a / 2))
        s.append('<geom name="sr_duvar_%d" type="box" pos="%s %s %s" size="%s %s %s" quat="%s 0 0 %s" material="m_sr_duvar" '
                 'contype="0" conaffinity="0" group="2"/>' % (n, _g(cx), _g(cy), _g(yuk / 2), _g(boy / 2 + 0.001), _g(k / 2),
                                                              _g(yuk / 2), _g(q[0]), _g(q[3])))
    for i, (cx, cy, r) in enumerate(harita.daireler):
        s.append('<geom name="sr_kolon_%d" type="cylinder" pos="%s %s %s" size="%s %s" material="m_sr_duvar" '
                 'contype="0" conaffinity="0" group="2"/>' % (i, _g(cx), _g(cy), _g(yuk / 2), _g(r), _g(yuk / 2)))
    return s


# ------------------------------------------------------------------ dunya sarmalama
_ASIL = {}
KAMERA_ADI = "kafa_kamera"


def kamera_govde_konumu():
    """Kameranın CAD'deki yeri (montaj-analiz.json 'Kamera Raspberry Pi Camera Module 3' merkezi) -> robot gövde
    çerçevesi (m), model_uret.nokta ile aynı dönüşüm: (z, x, y) / 1000. Döner (x, y, z), kaynak metni."""
    yol = os.path.join(_yol.DEPO, "tasarim", "freecad", "montaj", "montaj-analiz.json")
    try:
        with open(yol, encoding="utf-8") as f:
            veri = json.load(f)

        def gez(o):
            if isinstance(o, dict):
                if str(o.get("ad", "")).startswith("Kamera Raspberry Pi Camera Module 3") and "merkez" in o:
                    return o["merkez"]
                for v in o.values():
                    r = gez(v)
                    if r is not None:
                        return r
            elif isinstance(o, list):
                for v in o:
                    r = gez(v)
                    if r is not None:
                        return r
            return None
        m = gez(veri)
        if m is not None:
            return (m[2] / 1000.0, m[0] / 1000.0, m[1] / 1000.0), "CAD montaj-analiz.json"
    except (OSError, ValueError):
        pass
    return (0.0651, 0.0, 1.565), "VARSAYIM (CAD okunamadı)"


def _kafa_govdeleri(x):
    """lale.xml metninden kafa_boyun ve kafa_bas gövde konumları."""
    import re
    kb = re.search(r'<body name="kafa_boyun" pos="([^"]+)"', x).group(1)
    ks = re.search(r'<body name="kafa_bas" pos="([^"]+)"', x).group(1)
    return [float(v) for v in kb.split()], [float(v) for v in ks.split()]


def kamerali_model_xml(fovy=41.0):
    import dunya as D
    yol_kaynak = _ASIL.get("MODEL_XML", D.MODEL_XML)
    with open(yol_kaynak, encoding="utf-8") as f:
        x = f.read()
    (cx, cy, cz), _ = kamera_govde_konumu()
    kb, ks = _kafa_govdeleri(x)
    rel = (cx - kb[0] - ks[0], cy - kb[1] - ks[1], cz - kb[2] - ks[2])
    cam = ('<camera name="%s" pos="%s %s %s" xyaxes="0 -1 0 0 0 1" fovy="%s"/>' %
           (KAMERA_ADI, _g(rel[0]), _g(rel[1]), _g(rel[2]), _g(fovy)))
    i = x.index('<geom name="c_kafa"')
    j = x.index("\n", i)
    x = x[:j + 1] + "            " + cam + "\n" + x[j + 1:]
    os.makedirs(_yol.ONBELLEK, exist_ok=True)
    yol = os.path.join(_yol.ONBELLEK, "lale_kamerali.xml")
    with open(yol, "w", encoding="utf-8") as f:
        f.write(x)
    return yol


def kur():
    """dunya modülünü bu süreçte sarmalar (idempotent). Sahne sözlüğünde `_sanalray` = plan yoksa davranış aynı,
    yalnız kafa kamerası eklenir (görsel; fiziğe etkisi yok)."""
    import dunya as D
    if "kuruldu" in _ASIL:
        return
    _ASIL.update(MODEL_XML=D.MODEL_XML, VARLIK=D.VARLIK, sahne_xml=D.sahne_xml)
    D.MODEL_XML = kamerali_model_xml()
    asil_xml = _ASIL["sahne_xml"]

    def sahne_xml(harita=None, sahne=None, p=None):
        x = asil_xml(harita, sahne, p)
        plan = (sahne or {}).get("_sanalray")
        if plan is None:
            return x
        ek = []
        if harita is not None:
            ek += gorsel_duvarlar(harita)
        ek += [etiket_geom(e) for e in plan.get("etiketler", [])]
        return x + "\n    " + "\n    ".join(ek)
    D.sahne_xml = sahne_xml
    _ASIL["kuruldu"] = True


def varlik_ayarla(plan):
    """Bir sonraki model_kur çağrısı için dokular (plan kimlikleri) + opak duvar malzemesi; asıl m_duvar görünmez."""
    import dunya as D
    v = _ASIL["VARLIK"]
    if plan is not None:
        v = v.replace('<material name="m_duvar" rgba="0.55 0.6 0.68 0.55"/>', '<material name="m_duvar" rgba="0.55 0.6 0.68 0"/>')
        v += ('\n    <material name="m_sr_duvar" rgba="0.80 0.78 0.72 1" specular="0.1" shininess="0.1"/>\n    ' +
              etiket_varlik([e["id"] for e in plan.get("etiketler", [])]) + "\n")
    D.VARLIK = v


def etiketli_sahne(kor, plan):
    """Duzenek'e verilecek sahne sözlüğü (asıl JSON + ad + plan; dosya değişmez)."""
    kur()
    s = dict(_sahne(kor))
    s["ad"] = kor
    s["_sanalray"] = plan
    varlik_ayarla(plan)
    return s
