"""Sanal ray deneyleri (MuJoCo, ONERI robotu, LiDAR'sız): odometri ölçümü, A'dan B'ye, rastgele bırakılma.

    %V% kod\\fizik\\sanalray\\deney.py odometri                       # MuJoCo enkoder odometrisinin doğal dönüş / öteleme oranı
    %V% kod\\fizik\\sanalray\\deney.py ab --kume gelistirme [--parca 0/2]
    %V% kod\\fizik\\sanalray\\deney.py ab --kume sinama   [--parca 1/2]
    %V% kod\\fizik\\sanalray\\deney.py kayip --kume sinama
    %V% kod\\fizik\\sanalray\\deney.py tek --koridor koridor_3 --aralik 5 [--kafa tarayan] [--kayit x.npz]
    %V% kod\\fizik\\sanalray\\deney.py ozet                           # ham -> sonuc/*.csv

Kümeler (DÜRÜST AYRIM): geliştirme = koridor_1 (düz 30 m) + koridor_3 (L), tohum 101 / 102: etiket planı ve süzgeç
ayarı yalnız bunlarla seçildi. Sınama = koridor_2, koridor_4 (T), koridor_5, koridor_6, tohum 1 / 2: hüküm bunlardan.
Başlangıç sapması, hedefler, rastgele bırakma ve hakem LiDAR'lı gezinme deneyinin (gezinme/senaryo_*) aynısı."""

import argparse
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sanalray import _yol  # noqa: E402

GELISTIRME = ["koridor_1", "koridor_3"]
SINAMA = ["koridor_2", "koridor_4", "koridor_5", "koridor_6"]
KORIDORLAR = ["koridor_%d" % i for i in range(1, 7)]
ODOMETRI_JSON = os.path.join(_yol.SONUC, "odometri.json")
VARSAYILAN = dict(mercek="std", cozunurluk="1152x648", boy_m=0.15, yukseklik="goz")


def odometri_oranlari():
    try:
        with open(ODOMETRI_JSON, encoding="utf-8") as f:
            o = json.load(f)
        return o["donus_orani"], o["oteleme_orani"]
    except (OSError, ValueError, KeyError):
        return 1.0, 1.0


# ------------------------------------------------------------------ odometri ölçümü
def odometri_olc():
    from gezinme.duzenek import Duzenek

    class Sabit:
        def __init__(self, v, w):
            self.v, self.w, self.top = v, w, [0.0, 0.0, 0.0]

        def adim(self, t, tarama, artim):
            self.top[0] += math.hypot(artim[0], artim[1])
            self.top[2] += artim[2]
            return self.v, self.w

        def durum(self):
            return {"poz": None, "mod": "", "yol": [], "hedef": None, "harita": None, "ek": {}}
    out = {}
    dz = Duzenek("koridor_2", tohum=0)
    dz.lidar.ayir()
    g0 = dz.gercek_poz()
    b = Sabit(0.0, 0.8)
    dz.kos(b, 16.0)
    g1 = dz.gercek_poz()
    # gerçek toplam dönüş: yaw farkı + tam turlar (odometri sayısından)
    odo = b.top[2]
    tur = round((odo - math.atan2(math.sin(g1[2] - g0[2]), math.cos(g1[2] - g0[2]))) / (2 * math.pi))
    gercek = math.atan2(math.sin(g1[2] - g0[2]), math.cos(g1[2] - g0[2])) + 2 * math.pi * tur
    out["donus_orani"] = round(odo / gercek, 4)
    out["donus"] = dict(odometri_rad=round(odo, 4), gercek_rad=round(gercek, 4), komut_w=0.8, sure_s=16)
    dz = Duzenek("koridor_1", tohum=0)
    dz.lidar.ayir()
    g0 = dz.gercek_poz()
    b = Sabit(0.25, 0.0)
    dz.kos(b, 30.0)
    g1 = dz.gercek_poz()
    gercek = math.hypot(g1[0] - g0[0], g1[1] - g0[1])
    out["oteleme_orani"] = round(b.top[0] / gercek, 4)
    out["oteleme"] = dict(odometri_m=round(b.top[0], 4), gercek_m=round(gercek, 4), komut_v=0.25, sure_s=30)
    out["aciklama"] = ("ONERI robotu, enkoder arka tekerde, iz 0,426 (firmware / Pi sabiti). Oran = odometri / gerçek. "
                       "Algılayıcı katmanı odometriyi bu orana bölüp istenen fazlalıkla çarpar.")
    os.makedirs(_yol.SONUC, exist_ok=True)
    with open(ODOMETRI_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(out)
    return out


# ------------------------------------------------------------------ ortak
def tum_etiketler(aralik, boy_m, yukseklik):
    """Bütün koridorların planı (kimlik -> etiket + koridor): Beyin'in ön bilgisi (kayıp robotta 6 koridor)."""
    from sanalray import etiket as E
    out = {}
    for kor in KORIDORLAR:
        p = E.plan_oku(kor, aralik, boy_m, yukseklik)
        for e in p["etiketler"]:
            out[e["id"]] = dict(e, koridor=kor)
    return out


class YanalHakem:
    """SenaryoHakemi + raydan yanal sapma (yer gerçeği gövde merkezinin planlanan rotaya uzaklığı) + konum hatası."""

    def __init__(self, hedef, yol, beyin):
        from gezinme import senaryo_ortak as SO
        self.h = SO.SenaryoHakemi(hedef, pay_m=SO.VARIS_PAYI)
        self.yol = list(yol) if yol else []
        self.beyin = beyin
        self.en_sapma = 0.0
        self.konum_hata_en = 0.0
        self.konum_hata_top = 0.0
        self.konum_n = 0
        self.std_en = 0.0
        self.sapma_aktif = bool(self.yol)

    def yol_ayarla(self, yol):
        self.yol = list(yol)
        self.sapma_aktif = True

    @property
    def bitti(self):
        return self.h.bitti

    @property
    def sonuc(self):
        return self.h.sonuc

    def guncelle(self, t, g, temas):
        self.h.guncelle(t, g, temas)
        if self.sapma_aktif and len(self.yol) >= 2:
            d = _cizgi_uzaklik(self.yol, g[0], g[1])
            if d > self.en_sapma:
                self.en_sapma = d
        p = self.beyin.ekf.govde()
        if p is not None:
            e = math.hypot(p[0] - g[0], p[1] - g[1])
            self.konum_hata_en = max(self.konum_hata_en, e)
            self.konum_hata_top += e
            self.konum_n += 1
            st = self.beyin.ekf.std()
            if st:
                self.std_en = max(self.std_en, st[0])


def _cizgi_uzaklik(P, x, y):
    en = 1e9
    for a, b in zip(P, P[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L2 = dx * dx + dy * dy
        t = max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / L2)) if L2 else 0.0
        en = min(en, math.hypot(a[0] + t * dx - x, a[1] + t * dy - y))
    return en


# ------------------------------------------------------------------ A'dan B'ye
def ab_kos(g, kayit=None):
    from gezinme import rota as R, senaryo_ortak as SO, senaryo_ab as SA
    from gezinme.duzenek import Duzenek
    from sanalray import etiket as E
    from sanalray.algilayici import Algilayicilar, SensorBeyni
    from sanalray.beyin import SanalRayBeyni
    import dunya as D
    kor, tohum = g["koridor"], int(g["tohum"])
    s = D.sahne_oku(kor)
    b = s["baslangic"]
    bilinen = (float(b["x"]), float(b["y"]), math.radians(float(b.get("aci_derece", 0))))
    rng = random.Random(10000 + 31 * tohum + 7 * SO.KORIDORLAR.index(kor))      # LiDAR'lı deneyle aynı sapma
    gercek = SO.baslangic_sapmasi(bilinen, rng)
    tam, hxy = R.durak_coz(kor, g["hedef"])
    plan = E.plan_oku(kor, g["aralik"], g["boy_m"], g["yukseklik"])
    dz = Duzenek(E.etiketli_sahne(kor, plan), tohum=1000 * tohum + SO.KORIDORLAR.index(kor), baslangic=gercek)
    k_d, k_o = odometri_oranlari()
    alg = Algilayicilar(dz, g["mercek"], g["cozunurluk"], tohum=77 * tohum + 5, donus_fazlasi=g["donus_fazlasi"],
                        dogal_donus=k_d, dogal_oteleme=k_o, bozulma=g.get("bozulma"))
    etk = tum_etiketler(g["aralik"], g["boy_m"], g["yukseklik"])
    beyin = SanalRayBeyni(etk, alg.K, gorev="ab", koridor=kor, baslangic=bilinen, hedef=tam, kafa=g["kafa"])
    sb = SensorBeyni(beyin, alg)
    rota_m = R.yol_boyu(beyin.yol)
    hakem = YanalHakem(hxy, beyin.yol, beyin)
    sure = rota_m / 0.25 * 1.8 + 40.0
    t0 = time.time()
    sonuc = dz.kos(sb, sure, hakem=hakem, kayit=kayit, olay=alg.olay)
    son = sonuc["son_gercek"]
    hata = math.hypot(son[0] - hxy[0], son[1] - hxy[1])
    basari = hata < SO.VARIS_PAYI and (hakem.bitti or sonuc["bitis"] == "beyin")
    neden = "" if basari else ("sure doldu (hedefe %.2f m)" % hata if sonuc["bitis"] == "sure" else
                               "beyin bitti dedi, hedefe %.2f m" % hata)
    if sonuc["temas_olay"]:
        neden = (neden + "; " if neden else "") + "temas %d" % sonuc["temas_olay"]
    alg.kapat()
    return dict(g, hedef_tam=tam, etiket_sayisi=plan["sayi"], basari=bool(basari), neden=neden, sure_s=sonuc["sure_s"],
                yol_m=round(hakem.h.yol_m, 3), rota_m=round(rota_m, 3), varis_hatasi_m=round(hata, 4),
                en_yanal_sapma_m=round(hakem.en_sapma, 4), temas_olay=sonuc["temas_olay"],
                temas_sure_s=sonuc["temas_sure_s"], konum_hata_en_m=round(hakem.konum_hata_en, 4),
                konum_hata_ort_m=round(hakem.konum_hata_top / max(1, hakem.konum_n), 4),
                konum_std_en_m=round(hakem.std_en, 4), etiket_olcum=beyin.olcum_sayisi, etiket_ret=beyin.ret_sayisi,
                pan_komut=alg.pan_komut_sayisi, kare=alg.kare_sayisi,
                kare_ms_ort=round(sum(alg.kare_ms) / max(1, len(alg.kare_ms)), 2), bitis=sonuc["bitis"],
                rtf=sonuc["rtf"], duvar_s=round(time.time() - t0, 1), olaylar=beyin.olaylar[-30:])


def ab_gorevler(kume, ek=None):
    from gezinme import senaryo_ab as SA
    g = []
    if kume == "gelistirme":
        # süre bütçesi için küçültüldü: koridor başına yalnız en uzak hedef; dönüş fazlası %25 (en kötü) her aralıkta,
        # %0 yalnız kavşak / 12 m'de
        for kor in GELISTIRME:
            h = SA.hedefler(kor)[-1]
            for aralik in ["kavsak", 12, 8, 5, 3]:
                for df in ((0.0, 0.25) if aralik in ("kavsak", 12) else (0.25,)):
                    g.append(dict(kume=kume, koridor=kor, hedef=h, tohum=101, aralik=aralik, donus_fazlasi=df,
                                  kafa="sabit", **VARSAYILAN))
    else:
        sec = (ek or {}).get("aralik", 5)
        komsu = (ek or {}).get("komsu", 8)
        for kor in SINAMA:
            for h in SA.hedefler(kor)[1:]:                  # süre bütçesi: orta ve en uzak hedef (3 hedeften 2'si)
                for tohum in (1,):
                    for df in (0.0, 0.14, 0.25):
                        g.append(dict(kume=kume, koridor=kor, hedef=h, tohum=tohum, aralik=sec, donus_fazlasi=df,
                                      kafa="sabit", **VARSAYILAN))
                    g.append(dict(kume=kume, koridor=kor, hedef=h, tohum=tohum, aralik=komsu, donus_fazlasi=0.25,
                                  kafa="sabit", **VARSAYILAN))
                    g.append(dict(kume=kume, koridor=kor, hedef=h, tohum=tohum, aralik=sec, donus_fazlasi=0.25,
                                  kafa="tarayan", **VARSAYILAN))
                    g.append(dict(kume=kume, koridor=kor, hedef=h, tohum=tohum, aralik="kavsak", donus_fazlasi=0.25,
                                  kafa="tarayan", **VARSAYILAN))
    for x in g:
        x["id"] = "ab_%s_%s_%s_a%s_d%02d_%s_t%d" % (x["kume"][:3], x["koridor"], x["hedef"], x["aralik"],
                                                    round(x["donus_fazlasi"] * 100), x["kafa"], x["tohum"])
    return g


# ------------------------------------------------------------------ rastgele bırakılma
def kayip_kos(g, kayit=None):
    from gezinme import rota as R, senaryo_ortak as SO
    from gezinme.duzenek import Duzenek
    from sanalray import etiket as E
    from sanalray.algilayici import Algilayicilar, SensorBeyni
    from sanalray.beyin import SanalRayBeyni
    kor, i = g["koridor"], int(g["birak"])
    k = SO.KORIDORLAR.index(kor)
    rng = random.Random(20000 + 100 * k + i + (500 if g["kume"] == "gelistirme" else 0))
    bas = SO.rastgele_birak(kor, rng)
    goreli = "kapi_%d" % rng.randint(1, 3)
    tam, hxy = R.durak_coz(kor, goreli)
    plan = E.plan_oku(kor, g["aralik"], g["boy_m"], g["yukseklik"])
    dz = Duzenek(E.etiketli_sahne(kor, plan), tohum=3000 + 10 * k + i, baslangic=bas)
    k_d, k_o = odometri_oranlari()
    alg = Algilayicilar(dz, g["mercek"], g["cozunurluk"], tohum=900 + 10 * k + i, donus_fazlasi=g["donus_fazlasi"],
                        dogal_donus=k_d, dogal_oteleme=k_o)
    etk = tum_etiketler(g["aralik"], g["boy_m"], g["yukseklik"])
    beyin = SanalRayBeyni(etk, alg.K, gorev="kayip", hedef=goreli, kafa=g["kafa"])
    sb = SensorBeyni(beyin, alg)
    hakem = YanalHakem(hxy, [], beyin)
    yol_lokalize = {"m": None, "t": None}

    def olay(dz_, t):
        alg.olay(dz_, t)
        if beyin.lokalize_t is not None and yol_lokalize["m"] is None:
            yol_lokalize["m"] = round(hakem.h.yol_m, 3)
            yol_lokalize["t"] = round(t, 2)
        if beyin.yol and not hakem.sapma_aktif:
            hakem.yol_ayarla(beyin.yol)
    t0 = time.time()
    sonuc = dz.kos(sb, g.get("sure_s", 300.0), hakem=hakem, kayit=kayit, olay=olay)
    son = sonuc["son_gercek"]
    hata = math.hypot(son[0] - hxy[0], son[1] - hxy[1])
    basari = hata < SO.VARIS_PAYI and (hakem.bitti or sonuc["bitis"] == "beyin") and beyin.koridor == kor
    if basari:
        neden = ""
    elif beyin.lokalize_t is None:
        neden = "etiket bulunamadi (%.0f s arama)" % sonuc["sure_s"]
    elif beyin.koridor != kor:
        neden = "yanlis koridor %s" % beyin.koridor
    elif sonuc["bitis"] == "sure":
        neden = "sure doldu (hedefe %.2f m)" % hata
    else:
        neden = "beyin bitti dedi, hedefe %.2f m" % hata
    if sonuc["temas_olay"]:
        neden = (neden + "; " if neden else "") + "temas %d" % sonuc["temas_olay"]
    alg.kapat()
    return dict(g, hedef_tam=tam, bas_x=bas[0], bas_y=bas[1], bas_yon_derece=round(math.degrees(bas[2]), 1),
                basari=bool(basari), neden=neden, sure_s=sonuc["sure_s"], yol_m=round(hakem.h.yol_m, 3),
                ilk_etiket_s=(round(beyin.ilk_etiket_t - (dz.w.zaman_s - sonuc["sure_s"]), 2) if beyin.ilk_etiket_t else None),
                lokalize_s=yol_lokalize["t"], lokalize_yol_m=yol_lokalize["m"], karar_koridor=beyin.koridor,
                varis_hatasi_m=round(hata, 4), en_yanal_sapma_m=round(hakem.en_sapma, 4), temas_olay=sonuc["temas_olay"],
                temas_sure_s=sonuc["temas_sure_s"], konum_hata_en_m=round(hakem.konum_hata_en, 4),
                etiket_olcum=beyin.olcum_sayisi, etiket_ret=beyin.ret_sayisi, bitis=sonuc["bitis"], rtf=sonuc["rtf"],
                duvar_s=round(time.time() - t0, 1), olaylar=beyin.olaylar[-30:])


def kayip_gorevler(kume, aralik=5):
    g = []
    korlar = GELISTIRME if kume == "gelistirme" else SINAMA
    n = 2 if kume == "gelistirme" else 3          # süre bütçesi: sınamada koridor başına 3 bırakma (LiDAR'lı deney 5)
    for kor in korlar:
        for i in range(n):
            for kafa in ("sabit", "tarayan"):
                g.append(dict(kume=kume, koridor=kor, birak=i, kafa=kafa, aralik=aralik, donus_fazlasi=0.14, **VARSAYILAN))
    for x in g:
        x["id"] = "kayip_%s_%s_b%d_a%s_%s" % (x["kume"][:3], x["koridor"], x["birak"], x["aralik"], x["kafa"])
    return g


# ------------------------------------------------------------------ koşucu
def ham_yol(ad):
    return os.path.join(_yol.HAM, "kosu", ad + ".json")


def gorev_kos(gorevler, fn, parca=None):
    if parca:
        i, n = [int(v) for v in parca.split("/")]
        gorevler = [g for j, g in enumerate(gorevler) if j % n == i]
    os.makedirs(os.path.join(_yol.HAM, "kosu"), exist_ok=True)
    for j, g in enumerate(gorevler):
        y = ham_yol(g["id"])
        if os.path.exists(y):
            continue
        t0 = time.time()
        try:
            s = fn(g)
        except Exception as h:
            import traceback
            s = dict(g, basari=False, neden="istisna: %r" % h, iz=traceback.format_exc())
        s["duvar_s"] = round(time.time() - t0, 1)
        with open(y, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=1, default=str)
        _yol.durum_yaz("%d/%d %s basari=%s hata=%s sapma=%s duvar=%.0fs" % (j + 1, len(gorevler), g["id"], s.get("basari"),
                                                                       s.get("varis_hatasi_m"), s.get("en_yanal_sapma_m"),
                                                                       s["duvar_s"]))
        print(g["id"], s.get("basari"), s.get("neden"), s.get("varis_hatasi_m"), s.get("en_yanal_sapma_m"), s["duvar_s"],
              flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("is_", choices=["odometri", "ab", "kayip", "tek", "tek_kayip", "ozet"])
    ap.add_argument("--kume", default="gelistirme", choices=["gelistirme", "sinama"])
    ap.add_argument("--parca", default=None)
    ap.add_argument("--aralik", default="5")
    ap.add_argument("--komsu", default="8")
    ap.add_argument("--koridor", default="koridor_3")
    ap.add_argument("--hedef", default=None)
    ap.add_argument("--kafa", default="sabit")
    ap.add_argument("--donus", type=float, default=0.14)
    ap.add_argument("--birak", type=int, default=0)
    ap.add_argument("--kayit", default=None)
    a = ap.parse_args()
    _yol.dusuk_oncelik()
    ar = a.aralik if a.aralik == "kavsak" else float(a.aralik)
    ar = int(ar) if isinstance(ar, float) and ar.is_integer() else ar
    ko = a.komsu if a.komsu == "kavsak" else int(float(a.komsu))
    if a.is_ == "odometri":
        odometri_olc()
    elif a.is_ == "ab":
        gorev_kos(ab_gorevler(a.kume, dict(aralik=ar, komsu=ko)), ab_kos, a.parca)
    elif a.is_ == "kayip":
        gorev_kos(kayip_gorevler(a.kume, ar), kayip_kos, a.parca)
    elif a.is_ == "tek":
        from gezinme import senaryo_ab as SA
        g = dict(id="tek", kume="tek", koridor=a.koridor, hedef=a.hedef or SA.hedefler(a.koridor)[-1], tohum=1, aralik=ar,
                 donus_fazlasi=a.donus, kafa=a.kafa, **VARSAYILAN)
        s = ab_kos(g, kayit=a.kayit)
        print(json.dumps(s, ensure_ascii=False, default=str, indent=1))
    elif a.is_ == "tek_kayip":
        g = dict(id="tek", kume="sinama", koridor=a.koridor, birak=a.birak, kafa=a.kafa, aralik=ar, donus_fazlasi=a.donus,
                 **VARSAYILAN)
        s = kayip_kos(g, kayit=a.kayit)
        print(json.dumps(s, ensure_ascii=False, default=str, indent=1))
    elif a.is_ == "ozet":
        from sanalray import rapor
        rapor.csv_uret()
    return 0


if __name__ == "__main__":
    sys.exit(main())
