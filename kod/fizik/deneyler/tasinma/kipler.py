"""Konumlayıcı kiplerinin AYNI koşullarda yan yana ölçümü (A'dan B'ye, tek harita, bilinen başlangıç, 2B).

    py -3 kipler.py --kume gelistirme --isci 2     # "emin değilim" ölçütünün ayarı (tohum 7, 8; v3 ve izleme)
    py -3 kipler.py --kume sinama --isci 2         # hüküm (tohum 5, 6; dört kip)
    py -3 kipler.py --tek sinama:izleme_algi:kapi_2+kucuk:koridor_5:5
    py -3 kipler.py --kume sinama --liste

Kipler (VARSAYILANLAR DEĞİŞMEDİ; hepsi bu deneyin koşucusunda, beyin kurulduktan sonra):
  v3           AbBeyni olduğu gibi
  izleme       AbBeyni + `mcl.ayar.rastgele_en_cok = 0` (harita_eskimesi/kos_varyant.py "izleme")
  algi         algi.TasinmaBeyni(AbBeyni)  (taşınma algısı + kurtarma + şüphede yavaşlama; eşikler tasinma
               geliştirme kümesinde donmuştu, burada DEĞİŞTİRİLMEDİ)
  izleme_algi  algi.TasinmaBeyni(AbBeyni + izleme); kurtarma beyni (KayipBeyni) varsayılan ayarlı

Koşul adı: "<dünya>" ya da "<dünya>+<taşıma türü>"; dünya harita_eskimesi koşul kimliği (taban, okul_orta, kapi_2 ...),
taşıma türü kacirma.TURLER. Tohumlar (hiçbiri önceki aşamalarda kullanılmadı: harita_eskimesi 1-4, tasinma 1, 2,
901-903): sinama t ∈ {5, 6}, gelistirme t ∈ {7, 8}; biçimler kos_tasinma.py ile aynı (başlangıç sapması
10000 + 31 t + 7 k, MCL 500000 + t, hedef t tek -> hedefler[1], çift -> en uzak; dünya bozucusu crc32("ab", etken,
koridor, t); taşıma crc32("kacir", "ab", koşul, koridor, t); benzetici gürültüsü crc32("sim", "ab", koridor, t)).
Kipler aynı görevde eşli (aynı dünya, sapma, MCL tohumu, taşıma anı / pozu, gürültü).

Hakem (ölçüm tarafı): koşu YALNIZ beyin "bitti" deyip 1 s durunca (Benzet2B "beyin"), süre dolunca ya da "algi"
yardım durumunda 10 s kalınca biter; harita_eskimesi'ndeki "hedefte 1,5 s durdu = başarı" kısa yolu kapalı (beyin
"vardım" demeden varış sayılmaz). Sonuç türü:
  dogru_varis    beyin "vardım" dedi, gövde merkezi hedefin GERÇEK yerine < 0,3 m
  sessiz_hata    beyin "vardım" dedi, hedefe >= 0,3 m (yanlış yerde "vardım"; başka koridora taşımada her "vardım")
  guvenli_durma  beyin "yardım" durumunda durdu ("emin değilim"), son 10 s'de < 5 cm yol
  sure_doldu     hiçbiri (süre: rota / 0,25 x 1,8 + 130 s; taşımadan sonra kalan rota / 0,25 x 1,8 + 90 s)

Gözlemci (`Gozlemci`, pasif): beynin her adımında yalnız beynin gördüklerinden (tarama, odometri artımı, kendi poz
tahmini ve konumlayıcı çıktısı) "emin değilim" ölçütünün adaylarını kaydeder; komutu DEĞİŞTİRMEZ. "Vardım" anındaki
değerler ham sonuca yazılır; ölçüt `emin.py`'de çevrimdışı uygulanır (vardım anında durmak gidişi değiştirmez).
"""

import argparse
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kacirma as KC  # noqa: E402

KIPLER = ["v3", "izleme", "algi", "izleme_algi"]
YA_DUNYA = ["taban", "okul_hafif", "okul_orta", "okul_agir", "kapi_2", "esya_2", "insan_2", "grup_2", "olcek_2",
            "genislik_2", "donussuz_2", "cam_2", "menzil_2", "odo_kayma_2", "kapi_3", "cam_3", "donussuz_3",
            "donussuz_4", "menzil_3"]
TASIMALI = ["taban+ayni_uzak", "taban+ters180", "taban+kucuk", "taban+baska_koridor", "kapi_2+ayni_uzak",
            "kapi_2+kucuk", "cam_2+ayni_uzak", "cam_2+kucuk", "donussuz_3+ayni_uzak", "donussuz_3+kucuk"]
# Süre bütçesi yüzünden daraltıldı (ilk plan 29 sınama koşulu; atılanlar SONUC.md "Kapsam"): sıra önem sırası,
# kesilirse sondakiler eksik kalır.
KUMELER = {
    "sinama": dict(tohumlar=(5, 6), kipler=KIPLER,
                   kosullar=["taban", "okul_hafif", "okul_orta", "taban+ayni_uzak", "taban+kucuk", "taban+ters180",
                             "taban+baska_koridor", "kapi_2", "cam_2", "donussuz_3", "kapi_2+kucuk", "cam_2+kucuk",
                             "donussuz_3+kucuk", "okul_agir", "kapi_3"]),
    # ikinci daraltma (süre): "cam_3", "donussuz_4", "esya_2" koşulmadı
    "gelistirme": dict(tohumlar=(7, 8), kipler=["v3", "izleme"],
                       kosullar=["taban", "okul_hafif", "okul_orta", "kapi_3", "cam_3", "taban+kucuk",
                                 "taban+ayni_uzak"]),
}
YARDIM_BITIR_S = 10.0


def kosul_coz(kosul):
    """-> (dünya koşul kimliği, taşıma türü | None)."""
    if "+" in kosul:
        d, t = kosul.split("+", 1)
        return d, t
    return kosul, None


def gorevler(kume):
    K = KUMELER[kume]
    out = []
    for kosul in K["kosullar"]:
        for kip in K["kipler"]:
            for kor in KC.KORIDORLAR:
                for t in K["tohumlar"]:
                    out.append(dict(id="%s_%s_%s_%s_%d" % (kume, kip, kosul, kor, t), kume=kume, kip=kip,
                                    kosul=kosul, koridor=kor, tohum=t))
    return out


def ham_yol(g):
    return os.path.join(KC.HAM, "kipler", g["kume"], g["id"] + ".json")


# ------------------------------------------------------------------ beyin tarafı: pasif gözlemci
class Gozlemci:
    """Beyni aynen iletir; yalnız beynin gördüğünden "emin değilim" adaylarını biriktirir (yer gerçeği yok).

    Biriken (algi kurtarmasından sonra sıfırlanır): her adımda poz tahmininin odometri öngörüsünden sapması
    (`sic`: en büyük, toplam, > 0,3 m olay sayısı); her taramada tahmin pozunda tarama-harita uyumu (`uyum`, `gecis`:
    algi.TasinmaAlgisi.olc ile aynı tanım), konumlayıcının ana mod payı / xy std'si / rastgele saçma oranı."""

    def __init__(self, beyin, koridor):
        from gezinme.beyinler import haritalar
        import algi
        self.b = beyin
        self.h = haritalar([koridor])[0]
        self.olcer = algi.TasinmaAlgisi()
        self.vardim = None             # son "bitti" geçişindeki kayıt
        self.vardim_sayisi = 0
        self._bitti_onceki = False
        self._sifirla()

    def _sifirla(self):
        self.sic_maks = 0.0
        self.sic_top = 0.0
        self.sic_03 = 0
        self.rast_n = 0
        self.kk_n = 0
        self.tarama_n = 0
        self.uyum = []                 # (uyum, gecis) son 20 tarama

    def __getattr__(self, ad):
        return getattr(self.b, ad)

    @property
    def poz(self):
        return self.b.poz

    def durum(self):
        return self.b.durum()

    def adim(self, t, tarama, artim):
        from gezinme.beyinler import bilesik, govdeden_noktaya, noktadan_govdeye
        onceki = self.b.poz
        evre0 = getattr(self.b, "evre", "izle")
        v, w = self.b.adim(t, tarama, artim)
        evre = getattr(self.b, "evre", "izle")
        if evre != "izle":
            self._sifirla()
        else:
            p = self.b.poz
            if evre0 == "izle" and onceki is not None and p is not None:
                ong = noktadan_govdeye(bilesik(govdeden_noktaya(onceki), artim))
                s = math.hypot(p[0] - ong[0], p[1] - ong[1])
                self.sic_maks = max(self.sic_maks, s)
                self.sic_top += s
                if s > 0.3:
                    self.sic_03 += 1
            if tarama is not None and p is not None:
                self.tarama_n += 1
                u, gc, _ = self.olcer.olc(self.h, p, tarama)
                if u is not None:
                    self.uyum.append((u, gc))
                    if len(self.uyum) > 20:
                        del self.uyum[0]
                tah = self.b.tah
                if tah is not None:
                    if tah.rastgele_oran > 0:
                        self.rast_n += 1
                    if tah.konum_kararsiz:
                        self.kk_n += 1
        mod = (self.b.durum() or {}).get("mod")
        bitti = mod == "bitti"
        if bitti and not self._bitti_onceki:
            self.vardim_sayisi += 1
            self.vardim = self._kayit(t)
        self._bitti_onceki = bitti
        return v, w

    def _kayit(self, t):
        import numpy as np
        tah = self.b.tah
        U = [u for u, _ in self.uyum[-10:]]
        G = [g for _, g in self.uyum[-10:]]
        modlar = [m for m in (tah.modlar if tah else []) if m.get("pay", 0) > 0.05]
        return dict(t=round(t, 2), u_med=(round(float(np.median(U)), 3) if U else None),
                    u_min=(round(min(U), 3) if U else None), g_med=(round(float(np.median(G)), 3) if G else None),
                    g_maks=(round(max(G), 3) if G else None),
                    std_xy=(round(math.hypot(tah.std_x, tah.std_y), 3) if tah else None),
                    std_th=(round(tah.std_theta, 3) if tah else None),
                    pay=(round(tah.konum_payi, 3) if tah else None), kk=(bool(tah.konum_kararsiz) if tah else None),
                    n_mod=len(modlar), sic_maks=round(self.sic_maks, 3), sic_top=round(self.sic_top, 3),
                    sic_03=self.sic_03, rast_n=self.rast_n, kk_n=self.kk_n, tarama_n=self.tarama_n)


# ------------------------------------------------------------------ hakem tarafı
def hakem_sinifi():
    import kos_tasinma as KT

    class KipHakemi(KT.TasinmaHakemi):
        """TasinmaHakemi; "hedefte durdu = bitti" kısa yolu kapalı; yardımda 10 s kalınca biter."""

        def __init__(self, hedef, son_t, beyin):
            super().__init__(hedef, son_t)
            self.h.durma_s = 1e9
            self.beyin = beyin
            self._yardim_t = None
            self.yardim_bitti = False

        @property
        def bitti(self):
            return self.h.bitti or self.zaman_doldu or self.yardim_bitti

        def guncelle(self, t, gercek, temas):
            super().guncelle(t, gercek, temas)
            if getattr(self.beyin, "evre", None) == "yardim":
                if self._yardim_t is None:
                    self._yardim_t = t
                elif t - self._yardim_t >= YARDIM_BITIR_S:
                    self.yardim_bitti = True
            else:
                self._yardim_t = None
    return KipHakemi


def beyin_kur(kip, kor, bilinen, tam, mcl_t):
    import algi
    surum = "algi" if kip in ("algi", "izleme_algi") else "v3"
    b = algi.beyin_kur("ab", surum, kor, bilinen, tam, mcl_t)
    if kip in ("izleme", "izleme_algi"):
        ic = b.ic if surum == "algi" else b
        ic.mcl.ayar.rastgele_en_cok = 0.0
    return b


def kos(g):
    import numpy as np  # noqa: F401
    from benzet2b import Benzet2B
    from gezinme import rota as R
    from gezinme import senaryo_ortak as SO
    from gezinme.senaryo_ab import hedefler
    import kos2b as HK
    import kos_tasinma as KT
    kor, t = g["koridor"], int(g["tohum"])
    ki = KC.KORIDORLAR.index(kor)
    dunya, tur = kosul_coz(g["kosul"])
    k = KC.HO.kosul(dunya)
    dn, kal = HK._dunya_ve_kalabalik(dict(senaryo="ab", koridor=kor, tohum=t), k)
    s = dn["sahne"]
    b = s["baslangic"]
    bilinen = (float(b["x"]), float(b["y"]), math.radians(float(b.get("aci_derece", 0))))
    gercek_h = SO.baslangic_sapmasi(bilinen, random.Random(10000 + 31 * t + 7 * ki))
    hl = hedefler(kor)
    hedef = hl[1] if t % 2 == 1 else hl[-1]
    tam, hxy = R.durak_coz(kor, hedef)
    hxy_dunya = dn["T"].nokta(*hxy)
    HK._baslangicta_insan_cek(kal, gercek_h)
    beyin = beyin_kur(g["kip"], kor, bilinen, tam, 500000 + t)
    beyin.hedef_tam = tam
    goz = Gozlemci(beyin, kor)
    rota_m = R.yol_boyu(R.rota(kor, bilinen[:2], hxy))
    rng = random.Random(KC.tohum("kacir", "ab", g["kosul"], kor, t))
    s_tasima = rng.uniform(0.25, 0.60) * rota_m if tur else None
    hakem = hakem_sinifi()(hxy_dunya, rota_m / 0.25 * 1.8 + 130.0, beyin)
    kc = KT.Kacirici(goz, "ab", kor, tur, rng, s_tasima, hakem, rota_m, dn["veri"])
    kc.hedef_tam = tam
    bz = Benzet2B(dn, kc, dn["T"].poz(gercek_h), KC.tohum("sim", "ab", kor, t), k["p"], kalabalik=kal)
    kc.bz = bz
    r = bz.kos(3000.0, hakem=hakem)
    return ozetle(g, dunya, tur, kc, goz, beyin, hakem, r, tam, rota_m, dn, kal)


def ozetle(g, dunya, tur, kc, goz, beyin, hakem, r, tam, rota_m, dn, kal):
    son = r["son_gercek"]
    hh = hakem.h
    ulasilamaz = hh.hedef[0] > 1e5
    varis = None if ulasilamaz else math.hypot(son[0] - hh.hedef[0], son[1] - hh.hedef[1])
    beyin_bitti = r["bitis"] == "beyin"
    seri = kc.seri
    son10 = [x for x in seri if x[0] >= seri[-1][0] - 10.0] if seri else []
    son10_yol = sum(math.hypot(b_[7] - a_[7], b_[8] - a_[8]) for a_, b_ in zip(son10, son10[1:]))
    yardim = getattr(beyin, "evre", None) == "yardim"
    if beyin_bitti:
        sonuc = "sessiz_hata" if (ulasilamaz or varis >= KC.VARIS_PAYI) else "dogru_varis"
    elif yardim and son10_yol < 0.05:
        sonuc = "guvenli_durma"
    else:
        sonuc = "sure_doldu"
    olaylar = [list(o) for o in getattr(beyin, "olaylar", [])]
    tk = kc.t_tasima
    alarm = [o for o in olaylar if o[1] == "kayboldum"]
    alarm_once = sum(1 for o in alarm if tk is None or o[0] < tk)
    tepki = next((o[0] - tk for o in alarm if tk is not None and o[0] >= tk), None)
    H = [x[1] for x in seri if x[1] is not None and math.isfinite(x[1])]
    return dict(g, dunya=dunya, tur=tur, hedef=tam, sonuc=sonuc, beyin_bitti=beyin_bitti,
                varis_m=(round(varis, 4) if varis is not None else None), sure_s=r["sure_s"], bitis=r["bitis"],
                rota_m=round(rota_m, 2), tasima=kc.tasima, t_tasima=tk,
                alarm=len(alarm), alarm_tasima_oncesi=alarm_once, tepki_s=(round(tepki, 2) if tepki is not None else None),
                kurtarma=getattr(beyin, "kurtarma", None), yardim=yardim, son10_yol_m=round(son10_yol, 3),
                temas_olay=r["temas_olay"], temas_hareketli=r["temas_hareketli"], temas_duran=r["temas_duran"],
                temas_sonra=kc.temas_sonra, yanlis_surus_s=round(kc.yanlis_surus_s, 1),
                yanlis_emin_s=round(kc.yanlis_emin_s, 1), konum_maks_m=(round(max(H), 3) if H else None),
                konum_kesin_yanlis=r["konum_kesin_yanlis"], bekleme_s=r["bekleme_s"], vardim=goz.vardim,
                vardim_sayisi=goz.vardim_sayisi, olaylar=olaylar[:30], insan=(kal.sayi() if kal else None),
                dunya_kayit=dn["kayit"], nan_orani=r["nan_orani"], duvar_s=r["duvar_s"])


def kos_gorev(g):
    yol = ham_yol(g)
    if os.path.exists(yol):
        return g["id"], "var"
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    try:
        os.close(os.open(yol + ".kilit", os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError:
        return g["id"], "kilitli"
    t0 = time.time()
    try:
        s = kos(g)
    except Exception as hata:
        import traceback
        s = dict(g, sonuc="istisna", neden="istisna: %r" % hata, iz=traceback.format_exc())
    s["duvar_toplam_s"] = round(time.time() - t0, 1)
    KC.json_yaz(yol, s)
    try:
        os.remove(yol + ".kilit")
    except OSError:
        pass
    return g["id"], "%s varis=%s alarm=%s duvar=%.0fs" % (s.get("sonuc"), s.get("varis_m"), s.get("alarm"),
                                                          s["duvar_toplam_s"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kume", default="sinama", choices=list(KUMELER))
    ap.add_argument("--isci", type=int, default=2)
    ap.add_argument("--tek", default=None, help="kume:kip:kosul:koridor:tohum")
    ap.add_argument("--liste", action="store_true")
    a = ap.parse_args()
    KC.dusuk_oncelik()
    if a.tek:
        ku, kip, ko, kor, t = a.tek.split(":")
        g = dict(id="tek", kume=ku, kip=kip, kosul=ko, koridor=kor, tohum=int(t))
        s = kos(g)
        print(json.dumps(s, ensure_ascii=False, default=str, indent=1))
        return 0
    G = gorevler(a.kume)
    bekleyen = [g for g in G if not os.path.exists(ham_yol(g))]
    if a.liste:
        print("%d gorev, %d bekliyor" % (len(G), len(bekleyen)))
        return 0
    KC.durum_yaz("kipler %s basladi: %d gorev, %d isci" % (a.kume, len(bekleyen), a.isci))
    import multiprocessing as mp
    with mp.Pool(a.isci, initializer=KC.dusuk_oncelik, maxtasksperchild=30) as havuz:
        n = 0
        for gid, msj in havuz.imap(kos_gorev, bekleyen):
            n += 1
            if n % 12 == 0 or "sessiz" in msj or "istisna" in msj:
                KC.durum_yaz("kipler %d/%d %s %s" % (n, len(bekleyen), gid, msj))
    KC.durum_yaz("kipler %s bitti (%d)" % (a.kume, len(bekleyen)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
