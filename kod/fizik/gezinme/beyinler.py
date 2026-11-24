"""Gezinme beyinleri (Beyin protokolü, `duzenek.py`): yalnız tarama + odometri görürler.

- `OdometriBeyni`: bilinen başlangıçtan yalnız enkoder odometrisiyle (ölü hesap) yol izler. Test ve taban çizgisi.
- `AbBeyni`: senaryo 1 (A'dan B'ye): bilinen koridor haritası + başlangıç pozu (v3 konumlayıcı `baslat_poz`), rota orta
  hat boyunca, konumlayıcının tahmini pozuyla sürer; önde engel çıkarsa dur-bekle.
- `KayipBeyni`: senaryo 2 (kayıp robot): 6 koridor haritası aday, poz ve yön bilinmez. Güvenli keşif sürüşü (öne ilerle,
  engelde dön) -> konumlayıcı kararlı olunca rota -> hedef durak; konumlayıcı fikir değiştirirse yeniden planlar.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gezinme import _yol  # noqa: E402,F401
from gezinme.izleyici import IzleyiciAyar, YolIzleyici, on_mesafe_hesapla, sar  # noqa: E402

XR = -0.185          # dönme merkezi / odometri noktası (arka dingil), gövde merkezine göre


def bilesik(p, a):
    """p pozu ∘ a artımı (a, p'nin çerçevesinde)."""
    c, s = math.cos(p[2]), math.sin(p[2])
    return (p[0] + c * a[0] - s * a[1], p[1] + s * a[0] + c * a[1], sar(p[2] + a[2]))


def govdeden_noktaya(p, px=XR):
    return (p[0] + px * math.cos(p[2]), p[1] + px * math.sin(p[2]), p[2])


def noktadan_govdeye(r, px=XR):
    return (r[0] - px * math.cos(r[2]), r[1] - px * math.sin(r[2]), r[2])


class OdometriBeyni:
    """Ölü hesap: bilinen başlangıç + enkoder artımları (arka dingil noktası). Yer gerçeğini görmez."""

    def __init__(self, baslangic, yol, ayar=None, serit_m=0.60):
        self.r = govdeden_noktaya(baslangic)
        self.izleyici = YolIzleyici(ayar or IzleyiciAyar())
        self.izleyici.yol_ver(yol)
        self.yol = list(yol)
        self.serit_m = serit_m
        self.on = None
        self.k = None

    @property
    def poz(self):
        return noktadan_govdeye(self.r)

    def adim(self, t, tarama, artim):
        self.r = bilesik(self.r, artim)
        if tarama is not None:
            self.on = on_mesafe_hesapla(tarama, self.serit_m)
        self.k = self.izleyici.komut(self.poz, self.on)
        return self.k.v, self.k.w

    def durum(self):
        return {"poz": self.poz, "mod": self.k.mod if self.k else "", "yol": self.yol,
                "hedef": tuple(self.yol[-1]) if self.yol else None, "harita": None,
                "ek": {"on_mesafe": self.on}}


# ------------------------------------------------------------------ konumlayıcı
_HARITA_ONBELLEK = {}


def haritalar(adlar):
    """Harita2B nesneleri (süreç başına bir kez hazırlanır; ızgaralar önbellekte)."""
    from konumlama.harita2b import harita_yukle
    out = []
    for ad in adlar:
        if ad not in _HARITA_ONBELLEK:
            h = harita_yukle(ad)
            h.hazirla(0.05, 0.20, erisilebilir=True)
            _HARITA_ONBELLEK[ad] = h
        out.append(_HARITA_ONBELLEK[ad])
    return out


class _Konumlu:
    """Konumlayıcıyı tarama + odometriyle besler; denetim için anlık poz (tur ortası tahmini + sonraki odometri)."""

    serit_m = 0.60

    def _konum_kur(self, harita_adlari, tohum, **mcl_ayar):
        from konumlama import CokHaritaliMCL
        self.mcl = CokHaritaliMCL(haritalar(harita_adlari), tohum=tohum, **mcl_ayar)
        self.r = None              # dönme merkezi (arka dingil) pozu, harita çerçevesi
        self.tah = None
        self.on = None
        self.mcl_s = 0.0           # konumlayıcıda geçen duvar saati (s)
        self.olcum_sayisi = 0

    def _besle(self, tarama, artim):
        import time
        if tarama is None:
            self.mcl.hareket(*artim)
            if self.r is not None:
                self.r = bilesik(self.r, artim)
            return False
        once = tarama.get("artim_once", artim)
        sonra = tarama.get("artim_sonra", (0.0, 0.0, 0.0))
        t0 = time.perf_counter()
        tah = self.mcl.guncelle(tarama, artim=once)
        self.mcl_s += time.perf_counter() - t0
        self.mcl.hareket(*sonra)
        self.tah = tah
        self.r = bilesik(govdeden_noktaya((tah.x, tah.y, tah.theta)), sonra)
        self.on = on_mesafe_hesapla(tarama, self.serit_m)
        if tah.olcum_islendi:
            self.olcum_sayisi += 1
        return bool(tah.olcum_islendi)

    @property
    def poz(self):
        return None if self.r is None else noktadan_govdeye(self.r)


class AbBeyni(_Konumlu):
    """Senaryo 1: bilinen koridor + bilinen başlangıç pozu -> hedef durak, orta hat boyunca.

    Konumlayıcı yalnız bilinen koridorun haritasıyla (`baslat_poz`, std 0,2 m / 0,2 rad, `diger_haritalar=False`); poz
    tahmini her turda konumlayıcıdan, turlar arasında odometriyle. İzleyici önde engel görürse durur, bekler."""

    def __init__(self, koridor, baslangic, hedef, tohum=0, ayar=None, parcacik=1500):
        from gezinme import rota as R
        self.koridor = koridor
        self.hedef_ad, self.hedef = R.durak_coz(koridor, hedef) if isinstance(hedef, str) else (None, tuple(hedef))
        self._konum_kur([koridor], tohum, parcacik_sayisi=parcacik)
        self.mcl.baslat_poz(koridor, *baslangic, diger_haritalar=False)
        self.r = govdeden_noktaya(baslangic)
        self.izleyici = YolIzleyici(ayar or IzleyiciAyar())
        self.yol = R.rota(koridor, baslangic[:2], self.hedef)
        self.izleyici.yol_ver(self.yol)
        self.k = None

    def hedef_degistir(self, hedef):
        from gezinme import rota as R
        self.hedef_ad, self.hedef = R.durak_coz(self.koridor, hedef) if isinstance(hedef, str) else (None, tuple(hedef))
        self.yol = R.rota(self.koridor, self.poz[:2], self.hedef)
        self.izleyici.yol_ver(self.yol)

    def adim(self, t, tarama, artim):
        self._besle(tarama, artim)
        self.k = self.izleyici.komut(self.poz, self.on)
        return self.k.v, self.k.w

    def durum(self):
        p = self.poz
        return {"poz": p, "mod": self.k.mod if self.k else "", "yol": self.yol, "hedef": self.hedef, "harita": None,
                "ek": {"koridor": self.koridor, "p": 1.0, "hedef_ad": self.hedef_ad, "on_mesafe": self.on,
                       "hedefe_m": (math.hypot(p[0] - self.hedef[0], p[1] - self.hedef[1]) if p else None),
                       "konum_kararsiz": (self.tah.konum_kararsiz if self.tah else None), "evre": "izle"}}


class Kesif:
    """Güvenli keşif sürüşü (tepkisel): LiDAR'da önündeki en açık doğrultuya ilerle, yan duvarlar arasında ortalan,
    önde engel yakınsa yerinde dön (daha açık yana). Konum bilmez."""

    def __init__(self, v=0.20, w_don=0.6, on_dur=0.70, on_acik=1.6, montaj=(0.19, 0.0)):
        self.v, self.w_don, self.on_dur, self.on_acik, self.montaj = v, w_don, on_dur, on_acik, montaj
        self.donuyor = 0.0           # 0 değil: dönüş yönü (+1 / -1)
        self.donulen = 0.0
        self.mod = "kesif"
        self._son = (0.0, 0.0)

    def _noktalar(self, tarama):
        import numpy as np
        a = np.asarray(tarama["acilar"], dtype=float)
        m = np.asarray([np.nan if d is None else d for d in tarama["mesafeler"]], dtype=float)
        ok = np.isfinite(m)
        return self.montaj[0] + m[ok] * np.cos(a[ok]), self.montaj[1] + m[ok] * np.sin(a[ok])

    @staticmethod
    def _serbest(px, py, aci, yari=0.30, on=0.2642):
        import numpy as np
        c, s = math.cos(aci), math.sin(aci)
        boy = px * c + py * s
        yan = np.abs(-px * s + py * c)
        sec = (yan < yari) & (boy > 0.0)
        return float(boy[sec].min() - on) if sec.any() else 12.0

    def adim(self, tarama, artim):
        """Yeni tarama varsa karar ver; yoksa son komutu sürdür. -> (v, w)."""
        if self.donuyor:
            self.donulen += abs(artim[2])
        if tarama is None:
            return self._son
        import numpy as np
        px, py = self._noktalar(tarama)
        if px.size == 0:
            self._son = (0.0, 0.0)
            return self._son
        on = self._serbest(px, py, 0.0)
        if self.donuyor:
            acilar = np.radians(np.arange(-30, 31, 5))
            en_iyi = max(acilar, key=lambda a: self._serbest(px, py, a) - 2.0 * abs(a))
            if (on > self.on_acik and abs(en_iyi) < 0.35) or self.donulen > 3.6:
                self.donuyor = 0.0
            else:
                self.mod = "yerinde"
                self._son = (0.0, self.donuyor * self.w_don)
                return self._son
        if on < self.on_dur:
            # daha açık yana dön: sol (y > 0) ve sağ yanda, gövdenin hizasındaki en yakın yan noktalar
            sol = py[(py > 0) & (px > -0.3) & (px < 1.5)]
            sag = -py[(py < 0) & (px > -0.3) & (px < 1.5)]
            ds = float(sol.min()) if sol.size else 12.0
            dr = float(sag.min()) if sag.size else 12.0
            self.donuyor = 1.0 if ds >= dr else -1.0
            self.donulen = 0.0
            self.mod = "yerinde"
            self._son = (0.0, self.donuyor * self.w_don)
            return self._son
        acilar = np.radians(np.arange(-45, 46, 3))
        puan = [min(self._serbest(px, py, a), 6.0) - 1.5 * abs(a) for a in acilar]
        a_en = float(acilar[int(np.argmax(puan))])
        yan = (px > -0.4) & (px < 0.6)
        sol = py[yan & (py > 0)]
        sag = -py[yan & (py < 0)]
        ds = float(sol.min()) if sol.size else 2.0
        dr = float(sag.min()) if sag.size else 2.0
        w = 1.2 * a_en + 0.6 * max(-0.4, min(0.4, (ds - dr) / 2.0))
        v = self.v if on > 1.5 else max(0.08, self.v * on / 1.5)
        self.mod = "kesif"
        self._son = (v, max(-0.8, min(0.8, w)))
        return self._son


KORIDORLAR = ["koridor_%d" % i for i in range(1, 7)]


class KayipBeyni(_Konumlu):
    """Senaryo 2: robot bilinmeyen bir koridorda, bilinmeyen poz ve yönle. 6 koridor haritası aday.

    1. keşif (`Kesif`) -> konumlayıcı kararlı olana dek: en olası harita aynı, `kararsiz` ve `konum_kararsiz` False,
       en olası p >= `karar_p`, art arda `karar_adim` işlenen tarama;
    2. karar -> o koridorda hedef durağa (göreli ad: "kapi_3" -> "k<N>_kapi_3") orta hat rotası, izleyiciyle;
    3. izlerken konumlayıcı başka haritaya kararlı geçerse (`degis_adim` tarama) ya da poz tahmini odometri öngörüsünden
       `sicrama_m`'den çok sıçrarsa yeniden planlar; harita kararsızlaşırsa (`geri_adim` tarama) keşfe döner."""

    def __init__(self, hedef="kapi_3", tohum=0, ayar=None, adaylar=None, karar_p=0.9, karar_adim=10, degis_adim=5,
                 geri_adim=15, sicrama_m=0.7, parcacik=3000):
        self.adaylar = list(adaylar or KORIDORLAR)
        self.hedef_goreli = hedef
        self._konum_kur(self.adaylar, tohum, parcacik_sayisi=parcacik)
        self.kesif = Kesif()
        self.izleyici = YolIzleyici(ayar or IzleyiciAyar())
        self.karar_p, self.karar_adim, self.degis_adim, self.geri_adim, self.sicrama_m = \
            karar_p, karar_adim, degis_adim, geri_adim, sicrama_m
        self.mod = "kesif"
        self.karar = None            # karar verilen koridor
        self.karar_t = None          # ilk karar anı (dunya.zaman_s)
        self.kararlar = []           # (t, koridor, p, neden) her karar / yeniden plan
        self.yeniden_plan = 0
        self.kesfe_donus = 0
        self._ardisik = 0
        self._aday = None
        self._degis = 0
        self._kararsiz_say = 0
        self.yol = []
        self.hedef = None
        self.hedef_ad = None
        self.k = None

    def _p(self):
        return self.tah.olasiliklar.get(self.tah.en_olasi, 0.0) if self.tah else 0.0

    def _kararli_mi(self):
        t = self.tah
        return t is not None and not t.kararsiz and not t.konum_kararsiz and self._p() >= self.karar_p

    def hedef_degistir(self, hedef):
        self.hedef_goreli = hedef
        if self.karar is not None:
            self._planla(self.kararlar[-1][0] if self.kararlar else 0.0, self.karar, "hedef degisti", kaydet=False)

    def _planla(self, t, koridor, neden, kaydet=True):
        from gezinme import rota as R
        self.karar = koridor
        if kaydet:
            self.kararlar.append((round(t, 2), koridor, round(self._p(), 4), neden))
        if self.karar_t is None:
            self.karar_t = t
        self.hedef_ad, self.hedef = R.durak_coz(koridor, self.hedef_goreli)
        self.yol = R.rota(koridor, self.poz[:2], self.hedef)
        self.izleyici.yol_ver(self.yol)
        self.mod = "izle"

    def _kesif_karari(self, t):
        en = self.tah.en_olasi
        k = self._kararli_mi()
        self._ardisik = (self._ardisik + 1) if (k and en == self._aday) else (1 if k else 0)
        self._aday = en if k else None
        if self._ardisik >= self.karar_adim:
            self._planla(t, en, "karar")

    def _izleme_denetimi(self, t, ongoru):
        tah = self.tah
        en = tah.en_olasi
        self._kararsiz_say = self._kararsiz_say + 1 if tah.kararsiz else 0
        self._degis = self._degis + 1 if (not tah.kararsiz and en != self.karar) else 0
        if self._degis >= self.degis_adim and self._kararli_mi():
            self.yeniden_plan += 1
            self._degis = 0
            self._planla(t, en, "harita degisti")
        elif self._kararsiz_say >= self.geri_adim:
            self.kesfe_donus += 1
            self.kararlar.append((round(t, 2), None, round(self._p(), 4), "kararsiz: kesfe donus"))
            self.mod = "kesif"
            self._ardisik = 0
            self._kararsiz_say = 0
            self.izleyici.yol_ver([])
            self.yol = []
        elif ongoru is not None and self.mod == "izle":
            p = self.poz
            if math.hypot(p[0] - ongoru[0], p[1] - ongoru[1]) > self.sicrama_m:
                self.yeniden_plan += 1
                self._planla(t, self.karar, "poz sicradi")

    def adim(self, t, tarama, artim):
        onceki = self.poz
        ongoru = None if onceki is None else noktadan_govdeye(bilesik(govdeden_noktaya(onceki), artim))
        if self._besle(tarama, artim):
            if self.mod == "kesif":
                self._kesif_karari(t)
            else:
                self._izleme_denetimi(t, ongoru)
        if self.mod == "kesif":
            self.k = None
            return self.kesif.adim(tarama, artim)
        self.k = self.izleyici.komut(self.poz, self.on)
        self.mod = "bitti" if self.k.bitti else "izle"
        return self.k.v, self.k.w

    def durum(self):
        p = self.poz
        tah = self.tah
        if self.mod == "kesif":
            mod = "kesif" if self.kesif.mod == "kesif" else "kesif-don"
        else:
            mod = "bitti" if self.mod == "bitti" else (self.k.mod if self.k else self.mod)
        return {"poz": p, "mod": mod, "yol": self.yol, "hedef": self.hedef, "harita": None,
                "ek": {"koridor": tah.en_olasi if tah else None, "p": round(self._p(), 4),
                       "kararsiz": tah.kararsiz if tah else None,
                       "konum_kararsiz": tah.konum_kararsiz if tah else None,
                       "karar": self.karar, "karar_t": self.karar_t, "yeniden_plan": self.yeniden_plan,
                       "kesfe_donus": self.kesfe_donus, "hedef_ad": self.hedef_ad, "on_mesafe": self.on,
                       "hedefe_m": (math.hypot(p[0] - self.hedef[0], p[1] - self.hedef[1]) if (p and self.hedef) else None),
                       "evre": self.mod}}
