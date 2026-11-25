"""Beyinler: v3 olduğu gibi (A'dan B'ye tek harita, 6 haritalı izleme) ve isteğe bağlı "algi" sürümü.

VARSAYILANLAR DEĞİŞMEDİ: `gezinme.beyinler` ve `konumlama` dokunulmadan kullanılır. "algi" sürümü yalnız bu deneyde,
v3 beyninin dışına sarılan bir katmandır:

  1. Taşınma algısı (`TasinmaAlgisi`): her taramada, beynin şimdiki poz tahmininde taramanın haritayla uyumu ölçülür
     (yalnız tarama + tahmin + harita; yer gerçeği yok):
       uyum  = ışın ucu harita yüzeyine `yakin_m`'den yakın olan ışınların oranı
       gecis = ölçülen menzil, haritadan ışın izlemeyle beklenenden `gecis_m` uzun olan ışınların oranı ("duvarın
               arkasını görmek": insan / eşya bunu yapamaz, yalnız yanlış poz, açık kapı ya da cam yapar)
     Tarama "kötü": uyum < `uyum_esik` ya da gecis > `gecis_esik`. Son `pencere` taramanın en az `kayip_say`'ı kötüyse
     "kayboldum"; en az `suphe_say`'ı kötüyse "şüphe".
  2. Kayboldum: robot durur (`dur_s`), konumlayıcı küresel yeniden başlar (aynı aday haritalarla, kafes başlangıcı:
     adaylar bütün haritaya yeniden yayılır), keşif sürüşüyle (yavaş) yeniden karar verir (`KayipBeyni`, aynı
     karar ölçütleri), sonra aynı (göreli) hedefe yeniden planlar. Kurtarma `kurtarma_en_cok_s`'yi ya da
     `en_cok_kurtarma` sayısını aşarsa durur ("yardım bekliyor").
  3. Güvenli davranış: şüphede ya da konumlayıcı `konum_kararsiz` iken hız `v_yavas`'a kırpılır (eğrilik korunur).
"""

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kacirma  # noqa: E402,F401  (yollar)
from gezinme.beyinler import AbBeyni, KayipBeyni, KORIDORLAR, govdeden_noktaya, haritalar  # noqa: E402

MONTAJ_X = 0.19


class IzBeyni(KayipBeyni):
    """v3, 6 harita aday, bilinen başlangıç: KayipBeyni'nin karardan sonraki (izleme) evresi.

    Konumlayıcı `baslat_poz(koridor, poz, diger_haritalar=True)` (öbür haritalar en az kotayla serbest alanda), karar
    baştan verilmiş sayılır ve hedefe rota çizilir. Sonrası KayipBeyni'nin kendi denetimi (değiştirilmedi): başka
    haritaya kararlı geçiş -> yeniden plan; `geri_adim` tarama kararsız -> keşfe dönüş; poz sıçraması -> yeniden plan."""

    def __init__(self, koridor, baslangic, hedef_goreli, tohum=0, **k):
        super().__init__(hedef=hedef_goreli, tohum=tohum, **k)
        self.mcl.baslat_poz(koridor, *baslangic, diger_haritalar=True)
        self.r = govdeden_noktaya(baslangic)
        self._planla(0.0, koridor, "bilinen baslangic")


def goreli_hedef(tam):
    """k5_kapi_3 -> kapi_3."""
    return tam.split("_", 1)[1] if tam.startswith("k") and "_" in tam else tam


class TasinmaAlgisi:
    def __init__(self, isin=90, yakin_m=0.20, gecis_m=0.50, uyum_esik=0.60, gecis_esik=0.10, pencere=10,
                 kayip_say=8, suphe_say=3, sicrama_esik=1.0, ozellik=None):
        from konumlama import LidarOzellik
        self.isin, self.yakin_m, self.gecis_m = isin, yakin_m, gecis_m
        self.uyum_esik, self.gecis_esik = uyum_esik, gecis_esik
        self.pencere, self.kayip_say, self.suphe_say = pencere, kayip_say, suphe_say
        self.sicrama_esik = sicrama_esik
        self.sicrama = None
        self.oz = ozellik if ozellik is not None else LidarOzellik.varsa_dosyadan()
        self._kor = None
        self.gecmis = []
        self.son = None

    def sifirla(self):
        self.gecmis = []

    def olc(self, harita, poz, tarama):
        """-> (uyum, gecis, kullanılan ışın). harita: Harita2B (hazırlanmış), poz: gövde merkezi (harita)."""
        a = np.asarray(tarama["acilar"], dtype=float)
        m = np.asarray([np.nan if d is None else d for d in tarama["mesafeler"]], dtype=float)
        if self._kor is None or self._kor.shape != a.shape:
            self._kor = self.oz.kor_mu(a)
        ok = np.flatnonzero(np.isfinite(m) & ~self._kor & (m > 0.05))
        if ok.size < 10:
            return None, None, int(ok.size)
        if ok.size > self.isin:
            ok = ok[np.linspace(0, ok.size - 1, self.isin).round().astype(int)]
        x, y, th = poz
        ox, oy = x + MONTAJ_X * math.cos(th), y + MONTAJ_X * math.sin(th)
        yon = th + a[ok]
        ex, ey = ox + m[ok] * np.cos(yon), oy + m[ok] * np.sin(yon)
        d = harita.alan_uzakligi_surekli(ex, ey)
        uyum = float(np.mean(d < self.yakin_m))
        beklenen = harita.isin_izle(np.array([ox]), np.array([oy]), yon[None, :], menzil=30.0)[0]
        gecis = float(np.mean(m[ok] > beklenen + self.gecis_m))
        return uyum, gecis, int(ok.size)

    def guncelle(self, harita, poz, tarama, kararsiz=False, sicrama_m=0.0):
        """-> "iyi" | "suphe" | "kayip". kararsiz: konumlayıcının `konum_kararsiz`'ı (kötü sayılır); sicrama_m: poz
        tahmininin odometri öngörüsünden sapması (bir taramada `sicrama_esik`'ten çoksa doğrudan "kayip")."""
        u, g, n = self.olc(harita, poz, tarama)
        self.son = (u, g, n)
        if sicrama_m > self.sicrama_esik:
            self.sicrama = sicrama_m
            return "kayip"
        if u is None and not kararsiz:
            return self.durum()
        kotu = bool(kararsiz) or (u is not None and (u < self.uyum_esik or g > self.gecis_esik))
        self.gecmis.append(kotu)
        if len(self.gecmis) > self.pencere:
            del self.gecmis[0]
        return self.durum()

    def durum(self):
        k = sum(self.gecmis)
        if len(self.gecmis) >= self.pencere and k >= self.kayip_say:
            return "kayip"
        if k >= self.suphe_say:
            return "suphe"
        return "iyi"


class TasinmaBeyni:
    """"algi" sürümü: v3 beyni (ic) + taşınma algısı + kurtarma + güvenli hız. Beyin protokolü (adim / durum / poz)."""

    def __init__(self, ic, adaylar, hedef_tam, tohum, algi=None, v_yavas=0.12, dur_s=1.0, kurtarma_en_cok_s=150.0,
                 en_cok_kurtarma=3, kesif_v=0.15):
        self.ic = ic
        self.aktif = ic
        self.adaylar = list(adaylar)
        self.hedef_goreli = goreli_hedef(hedef_tam)
        self.tohum = tohum
        self.algi = algi or TasinmaAlgisi()
        self.v_yavas, self.dur_s = v_yavas, dur_s
        self.kurtarma_en_cok_s, self.en_cok_kurtarma, self.kesif_v = kurtarma_en_cok_s, en_cok_kurtarma, kesif_v
        self.evre = "izle"                    # izle | kurtar | yardim
        self.olaylar = []                     # (t, olay, ayrıntı)
        self.kurtarma = 0
        self._kayip_t = None
        self._durum = "iyi"
        self.son_uyum = None

    # --- Beyin protokolü / Benzet2B'nin baktığı alanlar
    @property
    def poz(self):
        return self.aktif.poz

    @property
    def tah(self):
        return self.aktif.tah

    @property
    def k(self):
        return getattr(self.aktif, "k", None)

    @property
    def izleyici(self):
        return self.aktif.izleyici

    @property
    def mcl(self):
        return self.aktif.mcl

    def inanilan_harita(self):
        b = self.aktif
        if isinstance(b, KayipBeyni):
            return b.karar
        return b.koridor

    def izliyor_mu(self):
        b = self.aktif
        if isinstance(b, KayipBeyni):
            return b.karar is not None and b.mod != "kesif"
        return True

    def _kayboldum(self, t, neden=""):
        self.kurtarma += 1
        self.olaylar.append((round(t, 2), "kayboldum", dict(neden=neden, uyum=self.algi.son, sayi=self.kurtarma)))
        self.algi.sifirla()
        if self.kurtarma > self.en_cok_kurtarma:
            self.evre = "yardim"
            self.olaylar.append((round(t, 2), "yardim", "kurtarma sayisi"))
            return
        n = 1500 if len(self.adaylar) == 1 else 3000
        yeni = KayipBeyni(hedef=self.hedef_goreli, tohum=self.tohum + 7919 * self.kurtarma, adaylar=self.adaylar,
                          parcacik=n)
        yeni.kesif.v = self.kesif_v
        yeni.izleyici.ayar.dt_s = self.aktif.izleyici.ayar.dt_s
        self.aktif = yeni
        self.evre = "kurtar"
        self._kayip_t = t

    def adim(self, t, tarama, artim):
        from gezinme.beyinler import bilesik, noktadan_govdeye
        onceki = self.aktif.poz
        v, w = self.aktif.adim(t, tarama, artim)
        if self.evre == "yardim":
            return 0.0, 0.0
        if self.evre == "kurtar":
            b = self.aktif
            if b.karar is not None and b.mod != "kesif":
                self.evre = "izle"
                self.algi.sifirla()
                self._durum = "iyi"
                self.olaylar.append((round(t, 2), "yerini buldum", dict(harita=b.karar, p=round(b._p(), 3))))
                onceki = None
            elif t - self._kayip_t > self.kurtarma_en_cok_s:
                self.evre = "yardim"
                self.olaylar.append((round(t, 2), "yardim", "kurtarma suresi"))
                return 0.0, 0.0
            if t - self._kayip_t < self.dur_s:
                return 0.0, 0.0
        if self.evre == "izle" and tarama is not None and self.izliyor_mu() and self.aktif.poz is not None:
            p = self.aktif.poz
            sic = 0.0
            if onceki is not None:
                ong = noktadan_govdeye(bilesik(govdeden_noktaya(onceki), artim))
                sic = math.hypot(p[0] - ong[0], p[1] - ong[1])
            tah = self.aktif.tah
            h = haritalar([self.inanilan_harita()])[0]
            self._durum = self.algi.guncelle(h, p, tarama, kararsiz=bool(tah is not None and tah.konum_kararsiz),
                                             sicrama_m=sic)
            self.son_uyum = self.algi.son
            k = getattr(self.aktif, "k", None)
            if self._durum == "kayip" or (k is not None and k.bitti and self._durum != "iyi"):
                self._kayboldum(t, "sicrama %.2f m" % sic if sic > self.algi.sicrama_esik else
                                ("bitti ama supheli" if self._durum != "kayip" else "uyum"))
                return 0.0, 0.0
        if self.evre == "izle":
            tah = self.aktif.tah
            if self._durum == "suphe" or (tah is not None and tah.konum_kararsiz):
                if abs(v) > self.v_yavas:
                    f = self.v_yavas / abs(v)
                    v, w = v * f, w * f
        return v, w

    def durum(self):
        d = dict(self.aktif.durum() or {})
        if self.evre == "yardim":
            d["mod"] = "yardim"
        ek = dict(d.get("ek") or {})
        ek.update(tasinma_evre=self.evre, kurtarma=self.kurtarma, algi=self._durum)
        d["ek"] = ek
        return d


def beyin_kur(senaryo, surum, koridor, bilinen, hedef_tam, tohum):
    """-> beyin. senaryo "ab": AbBeyni (tek harita); "cok": IzBeyni (6 harita). surum "v3" | "algi"."""
    if senaryo == "ab":
        ic = AbBeyni(koridor, bilinen, hedef_tam, tohum=tohum)
        adaylar = [koridor]
    else:
        ic = IzBeyni(koridor, bilinen, goreli_hedef(hedef_tam), tohum=tohum)
        adaylar = list(KORIDORLAR)
    if surum == "v3":
        return ic
    return TasinmaBeyni(ic, adaylar, hedef_tam, tohum)
