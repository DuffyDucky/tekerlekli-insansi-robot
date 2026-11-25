"""3B pencerede canlı gezinme katmanı (`gorunum3b.py --senaryo ab|kayip` ya da `--beyin modul:Sinif`).

Pencerenin sahte ESP32'sini (`p.c`), Pi istemcisini (`p.e`) ve sanal LiDAR'ını (`p.lidar`) kullanır; başsız düzenekteki
(`duzenek.Duzenek.kos`) gibi Beyin'e yalnız tarama + enkoder odometrisi verir, (v, w)'sini `sur` ile gönderir. Çizim:
tahmini poz (yarı saydam hayalet taban + ok), rota çizgisi, hedef işareti, ileri bakış noktası, (varsa) doluluk haritası.

Beyin çerçevesi: `durum()["ek"]["cerceve"]` "harita" (varsayılan; harita = dünya, koridorlar) ya da "baslangic"
(Beyin'in (0, 0, 0)'ı robotun bırakıldığı gerçek gövde pozu; SLAM). Çizim buna göre dünyaya taşınır.
"""

import importlib
import importlib.util
import inspect
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gezinme.duzenek import goreli, sar  # noqa: E402

DENETIM_MS = 50
HARITA_ARALIK_S = 2.0          # harita katmanı en sık: 2 sanal s ...
HARITA_DUVAR_S = 1.0           # ... ve 1 gerçek s (hızlandırmada çizim fiziği yavaşlatmasın)
SONUC_ADI = {"basari": "BASARI", "fail_start": "START'TAN CIKTI", "fail_sure": "SURE DOLDU", "fail_sikisma": "SIKISTI"}
HARITA_EN_COK_HUCRE = 3000
YOL_EN_COK_PARCA = 200


def beyin_sinifi(yol):
    """"modul:Sinif" (modül kod/fizik altından, ör. kesif.beyin:LabirentBeyni) ya da "dosya.py:Sinif"."""
    if ":" not in yol:
        raise ValueError("--beyin modul:Sinif biçiminde olmalı: %r" % yol)
    mod, sinif = yol.rsplit(":", 1)
    if mod.endswith(".py"):
        spec = importlib.util.spec_from_file_location(os.path.splitext(os.path.basename(mod))[0], mod)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
    else:
        m = importlib.import_module(mod)
    return getattr(m, sinif)


def beyin_kur(sinif, **aday):
    """Sinif'ın kurucusunun kabul ettiği anahtarları (sahne, sahne_ad, baslangic, tohum, hedef, ...) vererek kur."""
    try:
        imza = inspect.signature(sinif)
        if any(p.kind == p.VAR_KEYWORD for p in imza.parameters.values()):
            return sinif(**aday)
        return sinif(**{k: v for k, v in aday.items() if k in imza.parameters})
    except (TypeError, ValueError):
        return sinif()


class CanliGezinme:
    """Pencereye bağlı Beyin sürücüsü. tur: "ab" | "kayip" | "beyin" (dış sınıf)."""

    def __init__(self, p, tur, hedef=None, beyin_yolu=None, beyin_arg=None, tohum=0, cerceve=None, hakem=None,
                 sure_siniri_s=900.0):
        self.p, self.tur, self.tohum = p, tur, tohum
        # hakem "labirent": kod/fizik/labirent/hakem.py her denetim adımında yer gerçeğiyle; bitince robot durur
        self.hakem_tur, self.sure_siniri_s = hakem, float(sure_siniri_s)
        self.hakem = None
        self.tur_no = 1                          # 2: hafızalı ikinci tur (aynı labirent, Beyin'in kendi haritası)
        self.tur1 = None                         # birinci turun hakem sonucu (ikinci turda)
        self.bitis_islendi = False
        self.cizgiler = []                       # START / FINISH şeritleri (yalnız izleyici için; Beyin'e verilmez)
        lab = p.sahne.get("labirent") if hakem == "labirent" else None
        for k, renk in (("start", (1.0, 0.35, 0.0, 0.95)), ("finish", (0.8, 0.2, 0.9, 0.9))):
            if lab and lab.get(k, {}).get("cizgi"):
                (ax, ay), (bx, by) = lab[k]["cizgi"]
                self.cizgiler.append(((ax + bx) / 2, (ay + by) / 2, math.hypot(bx - ax, by - ay) / 2,
                                      math.atan2(by - ay, bx - ax), renk))
        self.beyin_yolu, self.beyin_arg = beyin_yolu, dict(beyin_arg or {})
        self.sahne = p.sahne_ad
        self.kapilar = []
        if self.sahne.startswith("koridor_"):
            from gezinme import rota as R
            self.kapilar = [a for a in R.duraklar(self.sahne) if "_kapi_" in a]
        self.hedef_i = 0
        if hedef:
            for i, a in enumerate(self.kapilar):
                if a == hedef or a.endswith("_" + hedef):
                    self.hedef_i = i
        elif tur == "ab" and self.kapilar:
            from gezinme.senaryo_ab import hedefler
            self.hedef_i = self.kapilar.index(hedefler(self.sahne)[-1])
        elif tur == "kayip" and self.kapilar:
            self.hedef_i = min(2, len(self.kapilar) - 1)
        self.bas = tuple(p.bas)                 # senaryonun başlangıcı (F7 buraya döner)
        # Beyin durum()["ek"]["cerceve"] vermezse: labirentte "baslangic" (ön bilgisiz beyin kendi START çerçevesinde),
        # öbür sahnelerde "harita"; --beyin-arg ile değil, gorunum3b --cerceve ile ezilir
        self.cerceve_varsayilan = cerceve or ("baslangic" if self.sahne.startswith("labirent_") else "harita")
        self.rng = random.Random(tohum)
        if tur == "kayip" and self.sahne.startswith("koridor_"):
            from gezinme.senaryo_ortak import rastgele_birak
            self.bas = rastgele_birak(self.sahne, self.rng)     # kayıp robot: rastgele yer ve yön
        self._bekleyen = []
        p.lidar_ac(True)
        p.lidar.dinleyiciler.append(lambda tar, ek: self._bekleyen.append(tar))
        self.goster_lidar = True
        self.duraklat = False
        self._kanca_kur()
        self.kur(self.bas, yeni_beyin=True)
        self._harita_cache = None               # (t, geom listesi)
        self._harita_t = -1e9
        self._harita_duvar = -1e9
        self.harita_z = 0.006                    # üstten bakışta duvar üstüne (1,03 m) alınır: duvarla çakışma görünsün
        self.harita_renk = (0.15, 0.15, 0.2, 0.55)
        self.harita_hucre = 0

    # ------------------------------------------------------------ odometri (Duzenek ile aynı formül)
    def _kanca_kur(self):
        c = self.p.c
        self.tik_m = math.pi * c.teker_capi / c.tik_tur
        self.iz = c.fw_iz
        onceki = c.kayitci

        def kanca(cc):
            if onceki is not None:
                onceki(cc)
            self._dilim()
        c.kayitci = kanca

    def _dilim(self):
        c = self.p.c
        tik = list(c.tik)
        if tik == [0, 0] and self._tik != [0, 0]:
            self._tik = tik
        dl = (tik[0] - self._tik[0]) * self.tik_m
        dr = (tik[1] - self._tik[1]) * self.tik_m
        self._tik = tik
        ds, dth = (dl + dr) / 2.0, (dr - dl) / self.iz
        o = self.odo
        o[0] += ds * math.cos(o[2] + dth / 2.0)
        o[1] += ds * math.sin(o[2] + dth / 2.0)
        o[2] = sar(o[2] + dth)
        self.odo_gecmis.append((self.p.w.zaman_s, o[0], o[1], o[2]))
        if len(self.odo_gecmis) > 400:
            del self.odo_gecmis[:200]
        if self.p.w.temas_engel():
            t = self.p.w.zaman_s
            if not self._temas_onceki and t - self._temas_son_t > 1.0:   # 1 s içinde yeniden temas aynı olay
                self.temas_olay += 1
            self._temas_son_t = t
            self._temas_onceki = True
        else:
            self._temas_onceki = False

    def _odo_ara(self, t):
        G = self.odo_gecmis
        if not G or t >= G[-1][0]:
            return tuple(self.odo)
        for a, b in zip(reversed(G[:-1]), reversed(G)):
            if a[0] <= t:
                u = (t - a[0]) / max(b[0] - a[0], 1e-9)
                return (a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u, a[3] + sar(b[3] - a[3]) * u)
        return G[0][1:]

    # ------------------------------------------------------------ kurulum / tuşlar
    def _beyin_yap(self, bas, hafiza=None):
        if self.tur == "ab":
            from gezinme.beyinler import AbBeyni
            return AbBeyni(self.sahne, bas, self.kapilar[self.hedef_i], tohum=self.tohum)
        if self.tur == "kayip":
            from gezinme.beyinler import KayipBeyni
            ad = self.kapilar[self.hedef_i].split("_", 1)[1] if self.kapilar else "kapi_3"
            return KayipBeyni(hedef=ad, tohum=self.tohum)
        sinif = beyin_sinifi(self.beyin_yolu)
        aday = dict(sahne=self.p.sahne, sahne_ad=self.sahne, baslangic=bas, tohum=self.tohum,
                    hedef=(self.kapilar[self.hedef_i] if self.kapilar else None))
        if self.sahne.startswith("labirent_"):
            # ön bilgisiz keşif: labirent alanı (START / FINISH / çözüm) ve dünya başlangıç pozu Beyin'e verilmez
            aday["sahne"] = {k: v for k, v in self.p.sahne.items() if k != "labirent"}
            aday.pop("baslangic")
        aday.update(self.beyin_arg)
        if hafiza is not None:
            aday["hafiza"] = hafiza
        return beyin_kur(sinif, **aday)

    def hafiza_turu(self):
        """Başarılı turdan sonra: aynı labirente START'tan, Beyin'in kendi haritasıyla (`hafiza_ver()` ->
        kurucu `hafiza=`) yeniden gir. kesif/kos.py'deki hafızalı koşunun aynısı."""
        h = self.hakem
        if h is None or not h.bitti or h.sonuc["durum"] != "basari":
            self.p._yaz("ikinci tur: once bir tur BASARI ile bitmeli")
            return False
        sinif = type(self.beyin)
        try:
            kabul = "hafiza" in inspect.signature(sinif).parameters
        except (TypeError, ValueError):
            kabul = False
        if not hasattr(self.beyin, "hafiza_ver") or not kabul:
            self.p._yaz("ikinci tur: bu Beyin hafiza_ver() / hafiza= desteklemiyor")
            return False
        hz = self.beyin.hafiza_ver()
        self.tur1 = h.sonuc if self.tur_no == 1 else self.tur1
        self.tur_no = 2
        self.kur(self.bas, yeni_beyin=True, hafiza=hz)
        self.p._yaz("2. tur: ayni labirent, robotun kendi haritasiyla")
        return True

    def _hakem_yap(self):
        if self.hakem_tur != "labirent":
            return None
        if not hasattr(CanliGezinme, "_H"):
            yol = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "labirent", "hakem.py")
            spec = importlib.util.spec_from_file_location("lale_labirent_hakem_canli", yol)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            CanliGezinme._H = m
        return CanliGezinme._H.Hakem(self.p.sahne, sure_siniri_s=self.sure_siniri_s)

    def kur(self, bas, yeni_beyin=True, hafiza=None):
        """Robotu bas'a koy, odometriyi oraya kur, Beyin'i yeniden kur, devreye al."""
        p = self.p
        p.c.konum_ayarla(*bas)
        if p.lidar is not None:
            p.lidar._sifirla_tur()               # yarım tur (ışınlanma öncesi + sonrası karışık) atılsın
        self._gecerli_t = p.w.zaman_s
        self.bas_simdi = tuple(bas)
        self.odo = list(bas)
        self._tik = list(p.c.tik)
        self.odo_gecmis = []
        self._bekleyen.clear()
        self._son_odo = tuple(self.odo)
        self.temas_olay = 0
        self._temas_onceki = False
        self._temas_son_t = -1e9
        self.t0 = p.w.zaman_s
        self._sonraki_ms = p.e.zaman_ms
        self.v = self.w = 0.0
        self.durum = {}
        self.hakem = self._hakem_yap()
        self.bitis_islendi = False
        self._harita_t = self._harita_duvar = -1e9
        self._harita_cache = None
        if yeni_beyin:
            self.beyin = self._beyin_yap(bas, hafiza)
        c = p.e.istek({"k": "arm"}, denetle=False)
        p._yaz("gezinme %s: robot (%.2f, %.2f, %.0f der), arm %s" % (self.tur, bas[0], bas[1], math.degrees(bas[2]),
                                                                   "ok" if c.get("ok") else c.get("hata")))

    def is_yap(self, ad):
        if ad == "hedef+":
            if not self.kapilar:
                return
            self.hedef_i = (self.hedef_i + 1) % len(self.kapilar)
            yeni = self.kapilar[self.hedef_i]
            if hasattr(self.beyin, "hedef_degistir"):
                self.beyin.hedef_degistir(yeni if self.tur == "ab" else yeni.split("_", 1)[1])
            self.p._yaz("hedef: %s" % yeni)
        elif ad == "bastan":
            self.tur_no, self.tur1 = 1, None
            self.kur(self.bas, yeni_beyin=True)
        elif ad == "hafiza":
            self.hafiza_turu()
        elif ad == "birak":
            from gezinme.senaryo_ortak import rastgele_birak
            if self.sahne.startswith("koridor_"):
                yer = rastgele_birak(self.sahne, self.rng)
            else:
                yer = (self.bas[0], self.bas[1], self.rng.uniform(-math.pi, math.pi))
            self.kur(yer, yeni_beyin=True)
        elif ad == "lidar":
            self.goster_lidar = not self.goster_lidar
            self.p._yaz("LiDAR noktalari %s (gezinmede LiDAR hep acik)" % ("gorunur" if self.goster_lidar else "gizli"))
        elif ad == "duraklat":
            self.duraklat = not self.duraklat
            self.p.e.gonder({"k": "dur"}, denetle=False)
            self.p._yaz("gezinme %s" % ("DURAKLATILDI (7 devam)" if self.duraklat else "devam"))

    # ------------------------------------------------------------ döngü
    def adim(self):
        """Her pencere döngüsünde (bekle'den önce). Denetim 20 Hz."""
        p = self.p
        if self.duraklat or p.e.zaman_ms < self._sonraki_ms:
            return
        self._sonraki_ms = p.e.zaman_ms + DENETIM_MS
        t = p.w.zaman_s
        if self.hakem is not None:
            if not self.hakem.bitti:
                g = p.w.poz()
                self.hakem.guncelle(t, (g[0], g[1], g[3]), p.w.temas_engel())
            if self.hakem.bitti:
                if not self.bitis_islendi:
                    self.bitis_islendi = True
                    self.v = self.w = 0.0
                    p.v = p.w_cmd = 0.0
                    p.e.gonder({"k": "dur"}, denetle=False)
                    r = self.hakem.sonuc
                    p._yaz("%s. tur bitti: %s  sure %.1f s  puan %.1f  carpma %d" % (
                        self.tur_no, SONUC_ADI.get(r["durum"], r["durum"]), r["sure_s"], r["puan"], r["carpma_sayisi"]))
                return
        tarama = None
        self._bekleyen = [x for x in self._bekleyen if x["t"] >= self._gecerli_t - 1e-9]
        if self._bekleyen:
            tarama = dict(self._bekleyen[-1])
            tarama["atlanan"] = len(self._bekleyen) - 1
            self._bekleyen.clear()
            o_orta = self._odo_ara(tarama["t"] + 0.5 / p.lidar.ayar.tarama_hz)
            tarama["artim_once"] = goreli(self._son_odo, o_orta)
            tarama["artim_sonra"] = goreli(o_orta, tuple(self.odo))
        simdi = tuple(self.odo)
        artim = goreli(self._son_odo, simdi)
        self._son_odo = simdi
        self.v, self.w = (float(z) for z in self.beyin.adim(t, tarama, artim))
        p.e.istek({"k": "sur", "v": round(self.v, 4), "w": round(self.w, 4)}, denetle=False)
        p.v, p.w_cmd = self.v, self.w
        self.durum = self.beyin.durum() or {}

    def ozet(self):
        """Pencere metni için: hakem ara / son durumu (+ ikinci turda ek tur puanı)."""
        h = self.hakem
        if h is None:
            return None
        o = dict(tur_no=self.tur_no, sure_s=h.sure_s, sinir_s=h.T, yol_m=h.yol_m, carpma=h.carpma_sayisi,
                 carpma_s=h.carpma_suresi_s, hucre=len(h.ziyaret), toplam_hucre=h.toplam_hucre, p_en=h.p_en,
                 bitti=h.bitti, mod=self.durum.get("mod", "-"))
        if h.bitti:
            r = h.sonuc
            o.update(durum=r["durum"], ad=SONUC_ADI.get(r["durum"], r["durum"]), puan=r["puan"], dokum=r["puan_dokumu"],
                     hafiza_olur=(r["durum"] == "basari" and hasattr(self.beyin, "hafiza_ver")))
            if self.tur_no == 2:
                s2, d2 = CanliGezinme._H.P.ek_tur_puani(r["durum"] == "basari", r["sure_s"], r["carpma_sayisi"],
                                                         h.cozum_m)
                o.update(ek_tur_puani=s2, ek_tur_dokum=d2)
        if self.tur1 is not None:
            o["tur1"] = self.tur1
        return o

    # ------------------------------------------------------------ çerçeve
    def _dunyaya(self, x, y, th=0.0):
        if (self.durum.get("ek") or {}).get("cerceve", self.cerceve_varsayilan) == "baslangic":
            bx, by, bt = self.bas_simdi
            c, s = math.cos(bt), math.sin(bt)
            return bx + c * x - s * y, by + s * x + c * y, sar(bt + th)
        return x, y, th

    # ------------------------------------------------------------ metin
    def metin(self):
        d = self.durum
        ek = d.get("ek") or {}
        t = self.p.w.zaman_s - self.t0
        poz = d.get("poz")
        g = self.p.w.poz()
        satir = "GEZINME %s  mod %s  sure %.0f s  temas %d" % (self.tur.upper(), d.get("mod", "-"), t, self.temas_olay)
        if self.duraklat:
            satir += "  DURAKLATILDI"
        s2 = ""
        if ek.get("koridor"):
            s2 += "koridor %s p %.2f" % (ek["koridor"], float(ek.get("p") or 0))
            if ek.get("karar"):
                s2 += " (karar %s)" % ek["karar"]
            elif self.tur == "kayip":
                s2 += " (karar yok: kesif)"
        if ek.get("hedef_ad") or d.get("hedef"):
            s2 += "  hedef %s" % (ek.get("hedef_ad") or "")
            if ek.get("hedefe_m") is not None:
                s2 += " %.1f m" % ek["hedefe_m"]
        if poz is not None:
            wx, wy, _ = self._dunyaya(*poz)
            s2 += "  tahmin hatasi %.2f m" % math.hypot(wx - g[0], wy - g[1])
        s3 = "F6 sonraki durak  F7 bastan  Shift+F7 rastgele birak  7 duraklat  F8 lidar noktalari"
        return "%s\n%s\n%s\n" % (satir, s2, s3)

    # ------------------------------------------------------------ çizim
    DINAMIK = YOL_EN_COK_PARCA + 12          # pencerede sabit yer: rota, hedef, hayalet

    def _yaz(self, scn, n, tur, boyut, poz, renk, mat=None):
        import mujoco
        import numpy as np
        g = scn.geoms[n]
        mujoco.mjv_initGeom(g, tur, np.asarray(boyut, dtype=float), np.asarray(poz, dtype=float),
                            np.eye(3).ravel() if mat is None else mat, np.asarray(renk, dtype=np.float32))
        return g

    def _dinamik(self, scn, bas, en_cok):
        """Rota, hedef, tahmini poz -> scn[bas : bas + en_cok]. Döner: yazılan sayı."""
        import mujoco
        import numpy as np
        d = self.durum
        n = bas
        son = bas + en_cok
        G = mujoco.mjtGeom
        for (cx, cy, yari, aci, renk) in self.cizgiler:      # START / FINISH şeritleri (zemin)
            c, s_ = math.cos(aci), math.sin(aci)
            R = np.array([[c, -s_, 0], [s_, c, 0], [0, 0, 1.0]]).ravel()
            self._yaz(scn, n, G.mjGEOM_BOX, (yari, 0.07, 0.004), (cx, cy, 0.009), renk, R)
            n += 1
        yol = [self._dunyaya(*q)[:2] for q in (d.get("yol") or [])]
        if len(yol) > YOL_EN_COK_PARCA:
            k = int(math.ceil(len(yol) / YOL_EN_COK_PARCA))
            yol = yol[::k] + [yol[-1]]
        for a, b in zip(yol, yol[1:]):
            if n >= son - 8:
                break
            g = self._yaz(scn, n, G.mjGEOM_CAPSULE, (0.025, 0.025, 0.025), (a[0], a[1], 0.03), (1.0, 0.8, 0.1, 0.8))
            mujoco.mjv_connector(g, G.mjGEOM_CAPSULE, 0.025, np.array([a[0], a[1], 0.03]), np.array([b[0], b[1], 0.03]))
            n += 1
        h = d.get("hedef")
        if h is not None and n + 3 <= son:
            hx, hy, _ = self._dunyaya(h[0], h[1])
            self._yaz(scn, n, G.mjGEOM_CYLINDER, (0.30, 0.01, 0), (hx, hy, 0.012), (0.1, 0.9, 0.2, 0.45))
            self._yaz(scn, n + 1, G.mjGEOM_CYLINDER, (0.03, 0.5, 0), (hx, hy, 0.5), (0.1, 0.8, 0.2, 0.9))
            self._yaz(scn, n + 2, G.mjGEOM_SPHERE, (0.08, 0, 0), (hx, hy, 1.05), (0.1, 0.9, 0.2, 0.9))
            n += 3
        poz = d.get("poz")
        if poz is not None and n + 2 <= son:
            x, y, th = self._dunyaya(*poz)
            c, s = math.cos(th), math.sin(th)
            R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]]).ravel()
            self._yaz(scn, n, G.mjGEOM_BOX, (0.2642, 0.2617, 0.30), (x, y, 0.32), (0.2, 0.6, 1.0, 0.22), R)
            g = self._yaz(scn, n + 1, G.mjGEOM_ARROW, (0.04, 0.04, 0.5), (x, y, 0.66), (0.2, 0.5, 1.0, 0.85))
            mujoco.mjv_connector(g, G.mjGEOM_ARROW, 0.04, np.array([x, y, 0.66]), np.array([x + 0.55 * c, y + 0.55 * s, 0.66]))
            n += 2
        return n - bas

    def _harita_yaz(self, scn, bas, en_cok):
        import mujoco
        n = 0
        for (x, y, yari, renk) in (self._harita_cache or [])[:en_cok]:
            self._yaz(scn, bas + n, mujoco.mjtGeom.mjGEOM_BOX, (yari, yari, 0.004), (x, y, self.harita_z), renk)
            n += 1
        return n

    def ciz(self, scn, bas=0):
        """Ekran görüntüsü için: hepsini scn'ye bas'tan sırayla yaz (harita + dinamik). Döner: yazılan sayı."""
        hr = self.durum.get("harita")
        if hr is not None and self._harita_cache is None:
            self._harita_cache = self._harita_hucreleri(hr)
        en_cok = scn.maxgeom - bas - 10
        n = self._harita_yaz(scn, bas, max(0, en_cok - self.DINAMIK)) if hr is not None else 0
        n += self._dinamik(scn, bas + n, min(self.DINAMIK, en_cok - n))
        scn.ngeom = bas + n
        return n

    def ciz_pencere(self, scn):
        """Görüntüleyicinin user_scn'i: [0, DINAMIK) her döngü, harita bloğu yalnız güncellenince (2 s'de bir), LiDAR
        noktaları en sonda (yalnız yeni turda). Görünmeyen boş yerler saydam."""
        import mujoco
        D = self.DINAMIK
        n = self._dinamik(scn, 0, D)
        for i in range(n, D):
            self._yaz(scn, i, mujoco.mjtGeom.mjGEOM_SPHERE, (0.001, 0, 0), (0, 0, -10), (0, 0, 0, 0))
        hr = self.durum.get("harita")
        zorla = False
        if (hr is not None and self.p.w.zaman_s - self._harita_t >= HARITA_ARALIK_S
                and time.perf_counter() - self._harita_duvar >= HARITA_DUVAR_S):
            self._harita_cache = self._harita_hucreleri(hr)
            self._harita_t = self.p.w.zaman_s
            self._harita_duvar = time.perf_counter()
            self._H = self._harita_yaz(scn, D, min(HARITA_EN_COK_HUCRE, scn.maxgeom - D - 1200))
            zorla = True
        H = getattr(self, "_H", 0)
        if self.goster_lidar and self.p.lidar is not None:
            if self.p.lidar_ciz(scn, bas=D + H, zorla=zorla) == 0 and self.p.lidar.son_ek is None:
                scn.ngeom = D + H
        else:
            scn.ngeom = D + H

    def _harita_hucreleri(self, hr):
        """Doluluk ızgarası -> (x, y, yarı boy, renk) listesi; en çok HARITA_EN_COK_HUCRE (kaba ızgarada en büyük)."""
        import numpy as np
        ham = np.asarray(hr["izgara"])
        if ham.size == 0:
            return []
        iz = ham.astype(float)
        if ham.dtype.kind == "i" or (iz.min() < 0 and iz.max() <= 100):
            iz = iz / 100.0                   # -1 bilinmeyen, 0 boş, 100 dolu (ROS OccupancyGrid)
        elif iz.max() > 1.0:
            iz = iz / 255.0                   # uint8 0..255
        coz = float(hr["cozunurluk_m"])
        x0, y0 = (float(v) for v in hr["orijin"])
        dolu = np.nan_to_num(iz, nan=0.5) >= 0.65
        k = 1
        while dolu.sum() / (k * k) > HARITA_EN_COK_HUCRE and k < 64:
            k *= 2
        if k > 1:
            H, W = dolu.shape
            Hk, Wk = -(-H // k), -(-W // k)
            pad = np.zeros((Hk * k, Wk * k), dtype=bool)
            pad[:H, :W] = dolu
            dolu = pad.reshape(Hk, k, Wk, k).any(axis=(1, 3))
        ii, jj = np.nonzero(dolu)
        hucre = coz * k
        out = []
        for i, j in zip(ii[:HARITA_EN_COK_HUCRE], jj[:HARITA_EN_COK_HUCRE]):
            x, y, _ = self._dunyaya(x0 + (j + 0.5) * hucre, y0 + (i + 0.5) * hucre)
            out.append((x, y, hucre / 2 * 0.95, self.harita_renk))
        self.harita_hucre = len(out)
        return out
