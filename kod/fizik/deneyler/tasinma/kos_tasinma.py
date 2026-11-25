"""2B koşucu: senaryo (ab | cok) x sürüm (v3 | algi) x koşul (taşıma türü | ya_<yanlış alarm koşulu>) x koridor x tohum.

    py -3 kos_tasinma.py --kume gelistirme --isci 3 [--senaryo ab] [--surum v3,algi] [--kosul ters180,ya_taban]
    py -3 kos_tasinma.py --tek sinama:ab:v3:ters180:koridor_5:1           # tek koşu, ekrana
    py -3 kos_tasinma.py --kume sinama --liste

Benzetici: önceki aşamanın `benzet2b.Benzet2B`'si (değiştirilmedi). Taşıma, beyni saran hakem tarafı `Kacirici`
nesnesinde yapılır: Benzet2B her denetim adımında `beyin.adim`'ı çağırdığında, yer gerçeği yolu taşıma noktasına
ulaşınca benzeticinin gerçek pozu (arka dingil) yeni poza konur; odometri değişmez (teker dönmez). Başka koridora
taşımada benzeticinin dünyası (çarpışma + LiDAR) o koridorunkiyle değiştirilir. Beyin yalnız taramayı ve odometriyi
görür; Kacirici'nin ölçümleri (hata, emin, temas) yalnız sonuç dosyasına gider.

Tohumlar (sürümden bağımsız: v3 ve algi aynı dünyada, aynı taşımayla, eşli):
  başlangıç sapması random.Random(10000 + 31 t + 7 k)   (önceki aşamayla aynı biçim)
  hedef: ab'de t tek -> hedefler(kor)[1], t çift -> en uzak kapı; cok'ta orta hat sonu ("son", her koridorda var)
  konumlayıcı: ab 500000 + t, cok 700000 + 10 k + t; kurtarma beyni + 7919 n
  taşıma anı ve pozu: random.Random(crc32("kacir", senaryo, koşul, koridor, t)); an = rota boyunun U(0,25, 0,60)'ı
  dünya bozucusu (yanlış alarm koşulları): crc32(senaryo, "ya", koridor, t); benzetici gürültüsü crc32("sim", ...)
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

TEMAS_BIRLESTIR_S = 1.0


class TasinmaHakemi:
    """SenaryoHakemi + son süre (hakem tarafı): t >= son_t olunca koşu biter (başarısız)."""

    def __init__(self, hedef, son_t):
        from gezinme import senaryo_ortak as SO
        self.h = SO.SenaryoHakemi(hedef, pay_m=KC.VARIS_PAYI)
        self.son_t = son_t
        self.zaman_doldu = False

    @property
    def bitti(self):
        return self.h.bitti or self.zaman_doldu

    def guncelle(self, t, gercek, temas):
        self.h.guncelle(t, gercek, temas)
        if t >= self.son_t and not self.h.bitti:
            self.zaman_doldu = True


class Kacirici:
    """Hakem tarafı sarmalayıcı: beyni aynen iletir; taşıma anında benzeticinin gerçek pozunu değiştirir; ölçer."""

    def __init__(self, beyin, senaryo, kor, tur, rng, s_tasima, hakem, rota_m, dunya_veri):
        self.b = beyin
        self.senaryo, self.kor0, self.tur = senaryo, kor, tur
        self.kor = kor                     # robotun gerçekte bulunduğu koridor
        self.rng = rng
        self.s_tasima = s_tasima           # yer gerçeği yolu (m) bu değere ulaşınca taşı (None: taşıma yok)
        self.hakem = hakem
        self.rota_m = rota_m
        self.dunya_veri = dunya_veri
        self.bz = None
        self.t_tasima = None
        self.tasima = None
        self.yol = 0.0
        self._onceki = None
        self.seri = []                     # (t, hata, emin, izle, v, w, temas)
        self.temas_sonra = 0
        self._temas_onceki = False
        self._temas_son_t = -1e9
        self._son_t = 0.0
        self.son_komut = (0.0, 0.0)
        self.yanlis_emin_s = 0.0
        self.yanlis_emin_yol = 0.0
        self.durdu_sonra_s = 0.0
        self.yanlis_surus_s = 0.0

    def __getattr__(self, ad):
        return getattr(self.b, ad)

    @property
    def poz(self):
        return self.b.poz

    def durum(self):
        return self.b.durum()

    # ------------------------------------------------ taşıma
    def _konum_koy(self, p, yeni_kor):
        """Benzeticinin gerçek pozunu p'ye koy (odometri değişmez); başka koridorsa dünyayı değiştir."""
        from benzet2b import Benzet2B, DINGIL_X
        bz = self.bz
        if yeni_kor != self.kor:
            import numpy as np
            dn = KC.HO.dunya_kur(yeni_kor, {}, np.random.default_rng(0))
            yb = Benzet2B(dn, None, p, 0, {})
            bz.dn, bz.carp, bz.lid, bz.siyah, bz.T = yb.dn, yb.carp, yb.lid, yb.siyah, yb.T
            bz.sabit_daire_c, bz.sabit_daire_l = yb.sabit_daire_c, yb.sabit_daire_l
            bz.kal = None
        bz.px, bz.py, bz.pth = p[0] + DINGIL_X * math.cos(p[2]), p[1] + DINGIL_X * math.sin(p[2]), p[2]

    def _temas(self, g):
        from benzet2b import ROBOT
        return self.bz.carp.temas(g, ROBOT)

    def _tasi(self, t):
        bz = self.bz
        simdi = bz.govde()
        yeni_kor, p = KC.tasima_pozu(self.tur, self.kor, simdi, self.rng, dunya_veri=self.dunya_veri)
        self._konum_koy(p, yeni_kor)
        self.kor = yeni_kor
        self.t_tasima = t
        self.tasima = dict(t=round(t, 2), yol=round(self.yol, 2), once=[round(v, 3) for v in simdi],
                           sonra=[round(v, 3) for v in p], koridor=self.kor,
                           uzaklik=round(math.hypot(p[0] - simdi[0], p[1] - simdi[1]), 2) if self.kor == self.kor0
                           else None)
        # hedef ve son süre (hakem tarafı)
        from gezinme import rota as R
        from algi import goreli_hedef
        h = self.hakem
        if self.kor != self.kor0:
            if self.senaryo == "cok":
                _, hxy = R.durak_coz(self.kor, goreli_hedef(self.hedef_tam))
                h.h.hedef = hxy
            else:
                h.h.hedef = (1e6, 1e6)       # tek haritalı beyin için ulaşılamaz: güvenli durma ölçülür
                hxy = None
        else:
            hxy = h.h.hedef
        kalan = R.yol_boyu(R.rota(self.kor, p[:2], hxy)) if hxy is not None else 0.0
        h.son_t = t + (kalan / 0.25 * 1.8 + 90.0 if hxy is not None else 120.0)
        h.h._onceki = None                    # taşıma sıçraması yol sayacına girmesin
        self._onceki = None
        self.tasima["kalan_rota_m"] = round(kalan, 2)

    # ------------------------------------------------ Beyin protokolü
    def adim(self, t, tarama, artim):
        bz = self.bz
        g = bz.govde()
        if self._onceki is not None:
            self.yol += math.hypot(g[0] - self._onceki[0], g[1] - self._onceki[1])
        self._onceki = g
        if self.s_tasima is not None and self.t_tasima is None and self.yol >= self.s_tasima:
            self._tasi(t)
            g = bz.govde()
            self._onceki = g
        v, w = self.b.adim(t, tarama, artim)
        self.son_komut = (v, w)
        dt = t - self._son_t
        self._son_t = t
        sonra = self.t_tasima is not None or self.s_tasima is None
        if sonra:
            temas = self._temas(g)
            if temas and not self._temas_onceki and t - self._temas_son_t > TEMAS_BIRLESTIR_S:
                self.temas_sonra += 1
            if temas:
                self._temas_son_t = t
            self._temas_onceki = temas
        if tarama is not None and sonra:
            hata, emin, izle = self._olc(g)
            if emin and hata > KC.HATA_ESIK:
                self.yanlis_emin_s += 0.1
                if self.seri:
                    pg = self.seri[-1]
                    self.yanlis_emin_yol += math.hypot(g[0] - pg[7], g[1] - pg[8])
            if izle and hata > KC.HATA_ESIK and (abs(v) > 0.02 or abs(w) > 0.05):
                self.yanlis_surus_s += 0.1
            su = getattr(self.b, "son_uyum", None)
            self.seri.append((round(t, 2), round(hata, 3) if math.isfinite(hata) else None, emin, izle,
                              round(v, 3), round(w, 3), int(self._temas_onceki), round(g[0], 3), round(g[1], 3),
                              (round(su[0], 2) if su and su[0] is not None else None),
                              (round(su[1], 2) if su and su[1] is not None else None),
                              getattr(self.b, "evre", None)))
        return v, w

    def _inanilan(self):
        b = self.b
        if hasattr(b, "inanilan_harita"):
            return b.inanilan_harita(), b.izliyor_mu()
        from gezinme.beyinler import KayipBeyni
        if isinstance(b, KayipBeyni):
            return b.karar, b.mod != "kesif"
        return b.koridor, True

    def _olc(self, g):
        b = self.b
        harita, izle = self._inanilan()
        p = b.poz
        tah = b.tah
        if p is None or harita != self.kor:
            hata = math.inf
        else:
            hata = math.hypot(p[0] - g[0], p[1] - g[1])
            if abs(KC.HO_sar(p[2] - g[2])) > KC.YON_ESIK:
                hata = max(hata, 9.99)       # yön 30°'den çok yanlış: konum doğru olsa da yanlış poz (ters180)
        emin = bool(tah is not None and izle and not tah.konum_kararsiz and not tah.kararsiz)
        if self.senaryo == "cok" and tah is not None and tah.en_olasi != harita:
            emin = False
        return hata, emin, izle


# ------------------------------------------------------------------ koşu
def kos(g):
    import numpy as np
    from benzet2b import Benzet2B
    from gezinme import rota as R
    from gezinme import senaryo_ortak as SO
    from gezinme.senaryo_ab import hedefler
    import kos2b as HK
    import algi
    kor, t = g["koridor"], int(g["tohum"])
    ki = KC.KORIDORLAR.index(kor)
    sn, sr, kosul = g["senaryo"], g["surum"], g["kosul"]
    ya = kosul.startswith("ya_")
    p = KC.YA_KOSULLARI[kosul[3:]] if ya else {}
    hk_g = dict(senaryo=sn, koridor=kor, tohum=t)
    dn, kal = HK._dunya_ve_kalabalik(hk_g, dict(etken="ya", p=p))
    s = dn["sahne"]
    b = s["baslangic"]
    bilinen = (float(b["x"]), float(b["y"]), math.radians(float(b.get("aci_derece", 0))))
    gercek_h = SO.baslangic_sapmasi(bilinen, random.Random(10000 + 31 * t + 7 * ki))
    hl = hedefler(kor)
    hedef = hl[1] if t % 2 == 1 else hl[-1]
    if sn == "cok":
        hedef = "son"             # göreli hedef her koridorda var (başka koridora taşımada aynı göreli ad)
    tam, hxy = R.durak_coz(kor, hedef)
    HK._baslangicta_insan_cek(kal, gercek_h)
    mcl_t = 500000 + t if sn == "ab" else 700000 + 10 * ki + t
    beyin = algi.beyin_kur(sn, sr, kor, bilinen, tam, mcl_t)
    beyin.hedef_tam = tam
    rota_m = R.yol_boyu(R.rota(kor, bilinen[:2], hxy))
    rng = random.Random(KC.tohum("kacir", sn, kosul, kor, t))
    s_tasima = None if ya else rng.uniform(0.25, 0.60) * rota_m
    hakem = TasinmaHakemi(hxy, son_t=rota_m / 0.25 * 1.8 + 130.0)
    kc = Kacirici(beyin, sn, kor, kosul, rng, s_tasima, hakem, rota_m, dn["veri"])
    kc.hedef_tam = tam
    bz = Benzet2B(dn, kc, gercek_h, KC.tohum("sim", sn, kor, t), p, kalabalik=kal)
    kc.bz = bz
    r = bz.kos(3000.0, hakem=hakem)
    return ozetle(g, kc, beyin, hakem, r, tam, rota_m, dn, kal)


def ozetle(g, kc, beyin, hakem, r, tam, rota_m, dn, kal):
    son = r["son_gercek"]
    hh = hakem.h
    son_uz = math.hypot(son[0] - hh.hedef[0], son[1] - hh.hedef[1])
    vardi = bool((hh.bitti and not hakem.zaman_doldu) or (r["bitis"] == "beyin" and son_uz < KC.VARIS_PAYI))
    tk = kc.t_tasima
    seri = kc.seri
    # yerini bulma: son kesintisiz "iyi" dilimin başı (hata < 0,5 m, doğru haritada), son tarama iyiyse
    bul_t = None
    if seri and seri[-1][1] is not None and seri[-1][1] < KC.HATA_ESIK:
        i = len(seri) - 1
        while i > 0 and seri[i - 1][1] is not None and seri[i - 1][1] < KC.HATA_ESIK:
            i -= 1
        bul_t = seri[i][0]
    # v3 tepkisi: konumlayıcının şüphesi (konum_kararsiz) ve beynin davranış değişikliği
    suphe_t = next((x[0] for x in seri if not x[2]), None)
    olaylar = []
    if hasattr(beyin, "olaylar"):
        olaylar = [list(o) for o in beyin.olaylar]
        tepki_t = next((o[0] for o in beyin.olaylar if o[1] == "kayboldum"), None)
    elif hasattr(beyin, "kararlar"):
        olaylar = [list(o) for o in beyin.kararlar if o[0] > 0]
        tepki_t = next((o[0] for o in beyin.kararlar if o[0] > 0), None)
    else:
        tepki_t = None
    ref = tk if tk is not None else 0.0
    kayboldum = sum(1 for o in olaylar if len(o) > 1 and o[1] == "kayboldum")
    # durma: taşımadan sonra son 10 s gerçek yol < 0,05 m
    son10 = [x for x in seri if x[0] >= seri[-1][0] - 10.0] if seri else []
    son10_yol = sum(math.hypot(b_[7] - a_[7], b_[8] - a_[8]) for a_, b_ in zip(son10, son10[1:]))
    yardim = bool(getattr(beyin, "evre", None) == "yardim")
    if g["kosul"] == "baska_koridor" and g["senaryo"] == "ab":
        basari = bool(yardim and son10_yol < 0.05 and kc.temas_sonra == 0)       # güvenli durdu
    else:
        basari = vardi
    tah = beyin.tah
    seri_kisa = seri[::5]
    return dict(g, hedef=tam, basari=basari, vardi=vardi, bitis=("vardi" if vardi else ("sure" if hakem.zaman_doldu else "beyin bitti")),
                sure_s=r["sure_s"], rota_m=round(rota_m, 2), tasima=kc.tasima,
                tepki_s=(round(tepki_t - ref, 2) if tepki_t is not None else None),
                suphe_s=(round(suphe_t - ref, 2) if suphe_t is not None else None),
                bulma_s=(round(bul_t - ref, 2) if bul_t is not None else None),
                yanlis_emin_s=round(kc.yanlis_emin_s, 1), yanlis_emin_yol_m=round(kc.yanlis_emin_yol, 2),
                yanlis_surus_s=round(kc.yanlis_surus_s, 1),
                temas_sonra=kc.temas_sonra, temas_olay=r["temas_olay"], kayboldum=kayboldum,
                kurtarma=getattr(beyin, "kurtarma", None), yardim=yardim, son10_yol_m=round(son10_yol, 3),
                son_hata_m=(seri[-1][1] if seri else None), son_koridor_gercek=kc.kor,
                son_harita_inanilan=kc._inanilan()[0], varis_hatasi_m=round(math.hypot(
                    son[0] - hh.hedef[0], son[1] - hh.hedef[1]), 3) if hh.hedef[0] < 1e5 else None,
                bekleme_s=r["bekleme_s"], konum_kesin_yanlis=r["konum_kesin_yanlis"], olaylar=olaylar[:40],
                insan=(kal.sayi() if kal else None), dunya=dn["kayit"], seri=seri_kisa,
                son_tah=(dict(en=tah.en_olasi, kk=tah.konum_kararsiz, k=tah.kararsiz) if tah else None),
                duvar_s=r["duvar_s"])


def kos_gorev(g):
    yol = KC.ham_yol(g)
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
        s = dict(g, basari=False, neden="istisna: %r" % hata, iz=traceback.format_exc())
    s["duvar_toplam_s"] = round(time.time() - t0, 1)
    KC.json_yaz(yol, s)
    try:
        os.remove(yol + ".kilit")
    except OSError:
        pass
    return g["id"], "basari=%s tepki=%s bulma=%s ye=%s temas=%s duvar=%.0fs" % (
        s.get("basari"), s.get("tepki_s"), s.get("bulma_s"), s.get("yanlis_emin_s"), s.get("temas_sonra"),
        s["duvar_toplam_s"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kume", default="gelistirme", choices=["gelistirme", "sinama"])
    ap.add_argument("--isci", type=int, default=3)
    ap.add_argument("--senaryo", default=",".join(KC.SENARYOLAR))
    ap.add_argument("--surum", default=",".join(KC.SURUMLER))
    ap.add_argument("--kosul", default=None)
    ap.add_argument("--tek", default=None, help="kume:senaryo:surum:kosul:koridor:tohum")
    ap.add_argument("--liste", action="store_true")
    a = ap.parse_args()
    KC.dusuk_oncelik()
    if a.tek:
        ku, sn, sr, ko, kor, t = a.tek.split(":")
        g = dict(id="tek", kume=ku, senaryo=sn, surum=sr, kosul=ko, koridor=kor, tohum=int(t))
        s = kos(g)
        s.pop("seri", None)
        print(json.dumps(s, ensure_ascii=False, default=str, indent=1))
        return 0
    G = KC.gorevler(a.kume, senaryolar=a.senaryo.split(","), surumler=a.surum.split(","))
    if a.kosul:
        sec = a.kosul.split(",")
        G = [g for g in G if g["kosul"] in sec]
    bekleyen = [g for g in G if not os.path.exists(KC.ham_yol(g))]
    if a.liste:
        print("%d gorev, %d bekliyor" % (len(G), len(bekleyen)))
        return 0
    # pahalı (cok) görevler önce: havuzun sonu dengeli biter
    bekleyen.sort(key=lambda g: (g["senaryo"] != "cok", g["kosul"].startswith("ya_")))
    KC.durum_yaz("kos_tasinma %s basladi: %d gorev, %d isci" % (a.kume, len(bekleyen), a.isci))
    import multiprocessing as mp
    with mp.Pool(a.isci, initializer=KC.dusuk_oncelik, maxtasksperchild=30) as havuz:
        n = 0
        for gid, msj in havuz.imap_unordered(kos_gorev, bekleyen):
            n += 1
            KC.durum_yaz("%d/%d %s %s" % (n, len(bekleyen), gid, msj))
    KC.durum_yaz("kos_tasinma %s bitti (%d)" % (a.kume, len(bekleyen)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
