"""Bağımsız hüküm 3: beş düzen AYNI görev listesinde, tohum 211-220 ve hiçbir önceki koşuda geçmeyen geometrilerle.

    %V% hukum3.py kos   [--surec 6]      # hüküm koşusu (sonuc/ham/hukum3.jsonl -> sonuc/hukum3.csv); kaldığı yerden sürer
    %V% hukum3.py fiz   [--surec 6]      # hakemin düşme saydığı her görev, koşu sürdürülerek (sonuc/hukum3_fiz.csv)
    py -3 hukum3.py tablo                # sonuc/hukum3_tablo.md
    py -3 hukum3.py say                  # görev sayıları (ön kayıt)

Ön kayıt: sonuc/on_kayit_3.md (koşudan önce yazıldı). Aday kodu (sensor / denetci / kosu / deney) değiştirilmedi; bu modül
yalnız onları çağırır. Görev kimliği `hukum3-<düzen>-<taban sırası>`: aynı taban sırası beş düzende aynı sahne, senaryo ve
tohum (eşli karşılaştırma)."""

import csv
import json
import math
import os
import sys
import time

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ucurum import _yol  # noqa: E402
from ucurum import deney  # noqa: E402

ASAMA = "hukum3"
TOHUM = tuple(range(211, 221))
HIZ = (0.10, 0.25, 0.39)
TUR_N = 3                  # görevler üç tura bölünür (sınıf içi sıra mod 3); süre yetmezse son tur(lar) bütün sınıflardan birlikte düşer
SUREC_TAVAN = 7

# Düzenler (dondurulmuş tanımlar; bu dosyada yalnız kopyalandı). Ortak koşul: SECIM_3'ün hukum_kosul'u (kısa kip K20, konum
# tutma). 6 sensör (SECIM_2) kendi tanımında hukum_kosul taşımıyordu; aynı görev listesi için ortak koşulla ölçülür (ön kayıt).
_K = dict(deney.SECIM_3["hukum_kosul"])
S14 = {"yerlesim": {"ad": "8WRD+4AD+2YR40", "z": 0.12, "e": 30, "koni": 27.0}, "esik_m": 0.1, "onay": 3, "politika": "yavasla",
       "fren": "rampa", "fren_ivme": 2.0, "sensor_n": 14, "on_n": 8, "hiz_onerisi_m_s": 0.25,
       "hukum_kosul": {"periyot_ms": 20, "butce_ms": 20, "menzil_m": 1.3, "tutma": ["konum", 40.0, 100.0]}}
DUZENLER = {
    "6": (deney.SECIM_2, _K, 6, "4OD+2AD (SECIM_2)"),
    "10": (deney.SECIM_3, dict(deney.SECIM_3["hukum_kosul"]), 10, "6OD+4AD (SECIM_3)"),
    "14": (S14, dict(S14["hukum_kosul"]), 14, "8WRD+4AD+2YR40 (önceki secim.json, t2_hukum)"),
    "3A": (deney.SECIM_3A, dict(deney.SECIM_3A["hukum_kosul"]), 14, "8WRaD+4AD+2YR40 (SECIM_3A)"),
    "3B": (deney.SECIM_3B, dict(deney.SECIM_3B["hukum_kosul"]), 10, "6OD+4AD + kural (SECIM_3B)"),
}

SINIFLAR = (
    ("merdiven_ileri", "Merdiven başı / sahanlık kenarı, ileri"),
    ("kose_ileri", "Sahanlık köşesi, ileri"),
    ("kuyu_ileri", "Kuyu, ileri"),
    ("dar_ileri", "Dar açıklık 0,48-0,85 m, ileri"),
    ("dar_geri", "Dar açıklığa geri gidiş"),
    ("genis_geri", "Geniş kenara geri gidiş"),
    ("donus_genis", "Yerinde dönüş, geniş kenar"),
    ("donus_dar", "Yerinde dönüş, dar açıklık yanında"),
    ("yarik_dar", "Dar yarık 8,5-16 cm"),
    ("yarik_egik", "Eğik yarık 15-45°"),
    ("rampa_ucu", "İniş rampasının ucunda düşüş"),
    ("yanlis_alarm", "Yanlış alarm"),
)


def _taban():
    """Düzenden bağımsız görev tabanı: (sınıf, sahne, senaryo, ek alanlar). Sınıf içi sıra tohumu (211 + i mod 10) ve turu
    (i mod 3) belirler."""
    from ucurum import sahne as SH
    B = []

    def ekle(sinif, sahne, sen, **ek):
        B.append((sinif, sahne, sen, ek))
    MER = ("h3_merdiven_16x29", "h3_merdiven_18x26", "h3_burun_17x30")
    ACIK = tuple("h3_acik_%d" % c for c in SH.H3_ACIK)
    for r in range(3):
        for geo in MER:
            for aci in (5, 18, 33, 47, 63, 76):
                for v in HIZ:
                    ekle("merdiven_ileri", geo, dict(tur="ileri", aci=aci, v=v))
    for r in range(3):
        for geo in ("h3_kose_150", "h3_kose_60"):
            for aci in (5, 18, 33, 47, 63, 76):
                for v in HIZ:
                    ekle("kose_ileri", geo, dict(tur="ileri", aci=aci, v=v, yanal=[-0.85, -0.35]))
    for r in range(4):
        for geo, ya in (("h3_kuyu_120", [-0.25, 0.25]), ("h3_kuyu_200", [-0.6, 0.6])):
            for aci in (5, 18, 33, 47):
                for v in HIZ:
                    ekle("kuyu_ileri", geo, dict(tur="ileri", aci=aci, v=v, yanal=ya))
    for geo in ACIK:
        for o in (-0.13, -0.04, 0.07, 0.18, 0.27):
            for aci in (4, 14, 26):
                for v in HIZ:
                    ekle("dar_ileri", geo, dict(tur="ileri", aci=aci, v=v, yanal=[o - 0.02, o + 0.02], yanal_ad=o))
    for r in range(2):
        for geo in ACIK:
            for o in (-0.12, 0.03, 0.17):
                for aci in (5, 17, 28):
                    for v in (0.10, 0.25):
                        ekle("dar_geri", geo, dict(tur="geri", aci=aci, v=v, yanal=[o - 0.02, o + 0.02], yanal_ad=o))
    for r in range(3):
        for geo in MER:
            for aci in (6, 20, 35, 48):
                for v in (0.10, 0.25):
                    ekle("genis_geri", geo, dict(tur="geri", aci=aci, v=v))
    for r in range(3):
        for geo in MER:
            for d in (0.33, 0.38, 0.43, 0.48):
                for w in (-1.0, 1.0):
                    ekle("donus_genis", geo, dict(tur="donus", d=d, w=w))
    for r in range(2):
        for geo in ACIK:
            for d in (0.33, 0.38, 0.43, 0.48):
                for w in (-1.0, 1.0):
                    for o in (-0.25, 0.04, 0.26):
                        ekle("donus_dar", geo, dict(tur="donus", d=d, w=w, yanal=[o - 0.02, o + 0.02], yanal_ad=o))
    for j, mm in enumerate(SH.H3_YARIK):
        for i, yr in enumerate((0.02, 0.07, 0.13, 0.185, 0.205, 0.222, 0.245, 0.29)):
            yr = yr if (i + j) % 2 == 0 else -yr                 # deliğin robota göre y'si; yarısı sağda (ayna)
            for aci in (-12, -7, 3, 8, 12):
                for v in HIZ:
                    ekle("yarik_dar", "h3_yarik_%d" % mm, dict(tur="ileri", aci=aci, v=v, yanal=[-yr - 0.01, -yr + 0.01],
                                                                yanal_ad=yr))
    for mm in SH.H3_EGIK_W:
        for p in SH.H3_EGIK_PHI:
            s = math.sin(math.radians(p)) * 0.5
            for yan in (1, -1):                                  # sol teker izi (+1) ya da sağ teker izi (-1) yarığı keser
                for q in (-0.6, 0.0, 0.6):
                    o = round(q * s - yan * 0.216, 4)            # robot merkezinin yarık merkezine göre y'si
                    for v in HIZ:
                        ekle("yarik_egik", "h3_egik_%d_%d" % (mm, p), dict(tur="ileri", aci=0, v=v, yanal=[o - 0.01, o + 0.01],
                                                                         yanal_ad=o))
    for r in range(3):
        for geo, L in (("h3_rampa_6_ucurum", 3.0), ("h3_rampa_9_ucurum", 2.0)):
            for v in (0.10, 0.20, 0.25, 0.39):
                for aci in (0, 7, 18):
                    ekle("rampa_ucu", geo, dict(tur="ileri", aci=aci, v=v),
                         baslangic=(SH.E - 0.8, SH.Y0, math.radians(aci)), t_max=(L + 1.3) / v + 8.0, durdu_bekle_s=3.0)
    for r in range(5):
        for geo in SH.H3_DENETIM:
            for v in HIZ:
                for aci in (7, 26, 43):
                    ek = {"etkin": True}
                    if geo in SH.H3_PARLAK:
                        ek["yok"] = SH.H3_PARLAK[geo]
                    ekle("yanlis_alarm", geo, dict(tur="ileri", aci=aci, v=v, yol_m=2.2), **ek)
    say = {}
    out = []
    for sinif, sahne, sen, ek in B:
        i = say.get(sinif, 0)
        say[sinif] = i + 1
        out.append(dict(sinif=sinif, sahne=sahne, senaryo=sen, tohum=TOHUM[i % len(TOHUM)], tur_no=i % TUR_N, **ek))
    for k, b in enumerate(out):
        b["taban"] = k
    return out


def gorevler():
    T = _taban()
    G = []
    for tur in range(TUR_N):
        for dz, (s, ks, n, _) in DUZENLER.items():
            for b in T:
                if b["tur_no"] != tur:
                    continue
                g = dict(asama=ASAMA, alt=b["sinif"], sahne=b["sahne"], ys=dict(s["yerlesim"]), ayar=deney._ana(s),
                         senaryo=dict(b["senaryo"]), tohum=b["tohum"], kosul=dict(ks), kad=dz, duzen=dz, taban=b["taban"],
                         tur_no=tur)
                for k in ("baslangic", "t_max", "durdu_bekle_s", "etkin", "yok"):
                    if k in b:
                        g[k] = b[k]
                g["kimlik"] = "%s-%s-%05d" % (ASAMA, dz, b["taban"])
                G.append(g)
    return G


def _fiz_gorev(g):
    v = abs(g["senaryo"].get("v") or 0.25)
    h = dict(g, asama=ASAMA + "_fiz", surdur=True, kimlik=g["kimlik"].replace(ASAMA, ASAMA + "_fiz", 1))
    if g["senaryo"]["tur"] in ("ileri", "geri") and g["alt"] != "rampa_ucu":
        h["t_max"] = 12.0 / v * 0.25 + 6.0                       # t2_hukum_fiz ile aynı
    return h


def _oku(ad):
    p = os.path.join(_yol.HAM, ad + ".jsonl")
    R = {}
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            for x in f:
                try:
                    r = json.loads(x)
                except ValueError:
                    continue
                R[r["kimlik"]] = r
    return R


def _csv(ad, R):
    satir = []
    for r in sorted(R.values(), key=lambda r: r["kimlik"]):
        s = deney._duz_satir(r)
        g = r.get("gorev", {})
        s = dict(duzen=g.get("duzen"), taban=g.get("taban"), tur_no=g.get("tur_no"), **s)
        satir.append(s)
    alan = []
    for s in satir:
        for k in s:
            if k not in alan:
                alan.append(k)
    with open(os.path.join(_yol.SONUC, ad + ".csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=alan)
        w.writeheader()
        w.writerows(satir)


def _kos(G, ad, ns):
    import multiprocessing as mp
    os.makedirs(_yol.HAM, exist_ok=True)
    bitti = set(_oku(ad))
    kalan = [g for g in G if g["kimlik"] not in bitti]
    _yol.durum_yaz("%s basladi: %d gorev, %d kalan, %d surec" % (ad, len(G), len(kalan), ns))
    t0 = time.time()
    n = 0
    with open(os.path.join(_yol.HAM, ad + ".jsonl"), "a", encoding="utf-8") as f:
        havuz = mp.Pool(ns, initializer=deney._isci_kur)
        for r in havuz.imap_unordered(deney.gorev_kos, kalan, chunksize=2):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
            if n % 100 == 0:
                f.flush()
            if n % 500 == 0:
                _yol.durum_yaz("%s %d / %d (%.0f s)" % (ad, n, len(kalan), time.time() - t0))
        havuz.close()
        havuz.join()
    R = _oku(ad)
    _csv(ad, R)
    hata = sum(1 for r in R.values() if r.get("hata"))
    _yol.durum_yaz("%s bitti: %d kosu, %d hata, %.0f s" % (ad, len(R), hata, time.time() - t0))
    print("%s: %d kosu, %d hata" % (ad, len(R), hata))


# ------------------------------------------------------------------ fiziksel düşme (ön kayıtlı tanım)
def fiziksel_dustu(r, g):
    """Sürdürülen koşuda fiziksel düşme: teker merkezi 20 mm'den çok iner, ya da eğim > 5°, ya da gövde zemine değer (ön kayıt).
    Rampa ucu sahnesinde teker rampadan iner ve eğim rampanın kendisidir: düşme = teker merkezi rampa ucunu teker yarıçapından
    (6,25 cm) çok geçer ya da eğim > rampa eğimi + 5°."""
    if r.get("hata"):
        return None
    if g.get("alt") == "rampa_ucu":
        eg = 6.0 if "rampa_6" in g["sahne"] else 9.0
        return bool((r.get("pay_min_cm") or 0) < -6.25 or (r.get("egim_max_der") or 0) > eg + 5.0)
    return bool((r.get("teker_dz_min_mm") or 0) < -20.0 or (r.get("egim_max_der") or 0) > 5.0 or r.get("govde_temas"))


def tablo():
    G = {g["kimlik"]: g for g in gorevler()}
    R = _oku(ASAMA)
    F = _oku(ASAMA + "_fiz")
    Ff = {}
    for k, r in F.items():
        Ff[k.replace(ASAMA + "_fiz", ASAMA, 1)] = r
    hucre = {}
    for k, g in G.items():
        r = R.get(k)
        key = (g["duzen"], g["alt"])
        h = hucre.setdefault(key, dict(n=0, kosuldu=0, hata=0, hakem=0, fiz=0, fiz_olc=0, pay=math.inf, durma=0,
                                       hakem_v={}, n_v={}, dusen=[]))
        h["n"] += 1
        if r is None:
            continue
        if r.get("hata"):
            h["hata"] += 1
            continue
        h["kosuldu"] += 1
        v = g["senaryo"].get("v")
        h["n_v"][v] = h["n_v"].get(v, 0) + 1
        if g["alt"] == "yanlis_alarm":
            if r.get("tetik"):
                h["durma"] += 1
                h["dusen"].append(k)
            if r.get("dustu"):
                h["hakem"] += 1
            continue
        if r.get("pay_min_cm") is not None:
            h["pay"] = min(h["pay"], r["pay_min_cm"])
        if r.get("dustu"):
            h["hakem"] += 1
            h["hakem_v"][v] = h["hakem_v"].get(v, 0) + 1
            h["dusen"].append(k)
            fr = Ff.get(k)
            if fr is not None:
                fd = fiziksel_dustu(fr, g)
                if fd is not None:
                    h["fiz_olc"] += 1
                    h["fiz"] += int(fd)
    return G, R, Ff, hucre


def _cm(p):
    return ("%.1f" % p).replace(".", ",") if math.isfinite(p) else "-"


def tablo_yaz():
    G, R, Ff, H = tablo()
    dz_l = list(DUZENLER)
    L = ["# Bağımsız hüküm 3: düzen x tehlike sınıfı", "",
         "Kaynak: `sonuc/hukum3.csv` (hüküm koşusu), `sonuc/hukum3_fiz.csv` (hakemin düşme saydığı görevler, koşu sürdürülerek).",
         "Ön kayıt: `sonuc/on_kayit_3.md`. Tohum 211-220, bütün sahneler yeni (`h3_*`). Üretici: `py -3 hukum3.py tablo`.", "",
         "Hücre (uçurum sınıfları): `hakem düşme / koşu · fiziksel düşme / sürdürülen · en küçük pay cm`. Yanlış alarm: "
         "`durma / koşu`. Hata varsa ayrıca yazılır.", ""]
    L.append("| sınıf | " + " | ".join("%s (%s)" % (dz, DUZENLER[dz][3]) for dz in dz_l) + " |")
    L.append("| --- |" + " --- |" * len(dz_l))
    top = {dz: dict(n=0, k=0, hakem=0, fiz=0, fiz_olc=0, pay=math.inf, hata=0, durma=0, fa=0) for dz in dz_l}
    for sinif, baslik in SINIFLAR:
        c = []
        for dz in dz_l:
            h = H.get((dz, sinif))
            if not h or h["kosuldu"] == 0:
                c.append("ölçülmedi")
                continue
            t = top[dz]
            t["hata"] += h["hata"]
            if sinif == "yanlis_alarm":
                t["durma"] += h["durma"]
                t["fa"] += h["kosuldu"]
                s = "%d / %d" % (h["durma"], h["kosuldu"])
            else:
                t["n"] += h["n"]
                t["k"] += h["kosuldu"]
                t["hakem"] += h["hakem"]
                t["fiz"] += h["fiz"]
                t["fiz_olc"] += h["fiz_olc"]
                t["pay"] = min(t["pay"], h["pay"])
                fz = "%d / %d" % (h["fiz"], h["fiz_olc"]) if h["hakem"] else "0"
                s = "%s%d / %d%s · %s · %s" % ("**" if h["hakem"] else "", h["hakem"], h["kosuldu"], "**" if h["hakem"] else "",
                                               fz, _cm(h["pay"]))
            if h["kosuldu"] < h["n"]:
                s += " (koşulmadı %d)" % (h["n"] - h["kosuldu"] - h["hata"])
            if h["hata"]:
                s += " (hata %d)" % h["hata"]
            c.append(s)
        L.append("| %s | %s |" % (baslik, " | ".join(c)))
    L.append("| **Uçurum toplamı** | " + " | ".join(
        "**%d / %d** · %d / %d · %s" % (top[dz]["hakem"], top[dz]["k"], top[dz]["fiz"], top[dz]["fiz_olc"], _cm(top[dz]["pay"]))
        if top[dz]["k"] else "ölçülmedi" for dz in dz_l) + " |")
    L.append("| **Yanlış durma toplamı** | " + " | ".join("**%d / %d**" % (top[dz]["durma"], top[dz]["fa"]) for dz in dz_l) + " |")
    L += ["", "## Ön kayıtlı ölçüte göre", "",
          "Ölçüt (SONUC.md'den aynen): uçurum koşularında 0 hakem düşmesi, yanlış alarm koşularında 0 durma. Izgaradaki bütün "
          "hızlar (0,10 / 0,20 / 0,25 / 0,39 m/s) sayılır. Hatalı koşu geçti sayılmaz.", "",
          "| düzen | sensör | hakem düşme | yanlış durma | hata | hüküm |", "| --- | --- | --- | --- | --- | --- |"]
    gecen = []
    for dz in dz_l:
        t = top[dz]
        ok = t["k"] > 0 and t["hakem"] == 0 and t["durma"] == 0 and t["hata"] == 0
        if ok:
            gecen.append(dz)
        L.append("| %s | %d | %d / %d | %d / %d | %d | **%s** |" % (DUZENLER[dz][3], DUZENLER[dz][2], t["hakem"], t["k"], t["durma"],
                                                                   t["fa"], t["hata"], "GEÇTİ" if ok else "GEÇMEDİ"))
    L += ["", "## Hıza göre hakem düşmesi (ikincil)", "",
          "Yerinde dönüş koşuları (dar ve geniş, 456 / düzen) ilerleme hızı taşımaz, bu tabloda yoktur (w ±1 rad/s; 3B'de "
          "kural geri yaya çevirir).", "", "| düzen | " + " | ".join("%.2f m/s" % v for v in (0.10, 0.20, 0.25, 0.39)) + " |",
          "| --- |" + " --- |" * 4]
    for dz in dz_l:
        c = []
        for v in (0.10, 0.20, 0.25, 0.39):
            hk = sum(h["hakem_v"].get(v, 0) for (d, s), h in H.items() if d == dz and s != "yanlis_alarm")
            n = sum(h["n_v"].get(v, 0) for (d, s), h in H.items() if d == dz and s != "yanlis_alarm")
            c.append("%d / %d" % (hk, n))
        L.append("| %s | %s |" % (dz, " | ".join(c)))
    def _ayr(baslik, sinif, anahtar, degerler):
        out = ["", "## Ayrıntı: %s" % baslik, "", "Hücre: `hakem düşme / koşu · en küçük pay cm`.", "",
               "| düzen | " + " | ".join(str(d) for d in degerler) + " |", "| --- |" + " --- |" * len(degerler)]
        for dz in dz_l:
            c = []
            for dv in degerler:
                rr = [R[k] for k, g in G.items() if g["duzen"] == dz and g["alt"] == sinif and anahtar(g) == dv
                      and k in R and not R[k].get("hata")]
                if not rr:
                    c.append("ölçülmedi")
                    continue
                pm = min((r["pay_min_cm"] for r in rr if r.get("pay_min_cm") is not None), default=math.inf)
                c.append("%d / %d · %s" % (sum(1 for r in rr if r.get("dustu")), len(rr), _cm(pm)))
            out.append("| %s | %s |" % (dz, " | ".join(c)))
        return out
    from ucurum import sahne as SH
    L += _ayr("dar yarık, genişliğe göre (mm)", "yarik_dar", lambda g: int(g["sahne"].split("_")[-1]), list(SH.H3_YARIK))
    L += _ayr("dar yarık, açıya göre (°)", "yarik_dar", lambda g: g["senaryo"]["aci"], [-12, -7, 3, 8, 12])
    L += _ayr("eğik yarık, eksen açısına göre (°)", "yarik_egik", lambda g: int(g["sahne"].split("_")[-1]), list(SH.H3_EGIK_PHI))
    L += _ayr("dar açıklık yanında dönüş, d'ye göre (m)", "donus_dar", lambda g: g["senaryo"]["d"], [0.33, 0.38, 0.43, 0.48])
    L += _ayr("dar açıklığa geri, genişliğe göre (cm)", "dar_geri", lambda g: int(g["sahne"].split("_")[-1]), list(SH.H3_ACIK))
    L += ["", "## Hakemin düşme saydığı koşular (en çok 60)", "",
          "| kimlik | sınıf | sahne | açı | v | yanal | d | pay cm | tetik sensörü | neden | fiziksel (teker dz mm, eğim °, gövde) |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    k_l = sorted(k for (dz, s), h in H.items() if s != "yanlis_alarm" for k in h["dusen"])
    for k in k_l[:60]:
        g, r = G[k], R[k]
        fr = Ff.get(k)
        fz = ("%s (%s, %s, %s)" % ("düştü" if fiziksel_dustu(fr, g) else "düşmedi", fr.get("teker_dz_min_mm"), fr.get("egim_max_der"),
                                   "temas" if fr.get("govde_temas") else "yok")) if fr else "ölçülmedi"
        sn = g["senaryo"]
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (k, g["alt"], g["sahne"], sn.get("aci"), sn.get("v"),
                 sn.get("yanal_ad"), sn.get("d"), r.get("pay_min_cm"), r.get("tetik_sensor"), r.get("neden"), fz))
    if len(k_l) > 60:
        L.append("")
        L.append("(%d koşu daha; hepsi `hukum3.csv`'de `dustu` = True)" % (len(k_l) - 60))
    fa = sorted(k for (dz, s), h in H.items() if s == "yanlis_alarm" for k in h["dusen"])
    if fa:
        L += ["", "## Yanlış durmalar", "", "| kimlik | sahne | açı | v | tetik sensörü | neden |", "| --- | --- | --- | --- | --- | --- |"]
        for k in fa:
            g, r = G[k], R[k]
            L.append("| %s | %s | %s | %s | %s | %s |" % (k, g["sahne"], g["senaryo"]["aci"], g["senaryo"]["v"], r.get("tetik_sensor"),
                                                        r.get("neden")))
    with open(os.path.join(_yol.SONUC, "hukum3_tablo.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print("\n".join(L[:40]))
    print("gecen:", gecen)
    return top, gecen


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("is_", choices=("kos", "fiz", "tablo", "say"))
    ap.add_argument("--surec", type=int, default=6)
    a = ap.parse_args()
    ns = max(1, min(a.surec, SUREC_TAVAN))
    if a.is_ == "say":
        G = gorevler()
        from collections import Counter
        c = Counter((g["duzen"], g["alt"]) for g in G)
        for dz in DUZENLER:
            print(dz, sum(v for (d, s), v in c.items() if d == dz and s != "yanlis_alarm"), "ucurum,",
                  c[(dz, "yanlis_alarm")], "yanlis alarm")
        for s, _ in SINIFLAR:
            print("  ", s, c[("6", s)])
        print("toplam", len(G))
        return
    if a.is_ == "tablo":
        tablo_yaz()
        return
    _yol.dusuk_oncelik()
    if a.is_ == "kos":
        _kos(gorevler(), ASAMA, ns)
    else:
        R = _oku(ASAMA)
        G = [_fiz_gorev(g) for g in gorevler() if g["alt"] != "yanlis_alarm" and R.get(g["kimlik"], {}).get("dustu")]
        _kos(G, ASAMA + "_fiz", ns)


if __name__ == "__main__":
    main()
