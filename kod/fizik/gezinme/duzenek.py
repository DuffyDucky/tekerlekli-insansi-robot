"""Başsız MuJoCo gezinme düzeneği: sahne + sahte ESP32 (fizik) + Pi istemcisi + sanal LiDAR + enkoder odometrisi.

    from gezinme.duzenek import Duzenek
    dz = Duzenek("koridor_5", tohum=3)                       # varyant: koridor_* / labirent_* -> ONERI, öbürleri V0
    sonuc = dz.kos(beyin, sure_s=120, hakem=None, kayit="x.npz", denetim_hz=20)

Robot GERÇEK sürüş yolundan sürülür: Beyin'in (v, w)'si Pi istemcisinin `sur` komutuyla (bellek taşıması) sahte ESP32
firmware modeline gider (bekçi, ivme / fren sınırı, TASLAK sonar kuralı, öneri firmware PI), oradan MuJoCo motor
modeline. Beyin yalnız LiDAR taramasını ve enkoder odometrisini görür; yer gerçeğini GÖRMEZ (hakem ve kayıt görür).

Beyin protokolü (duck typing; `Beyin` sınıfı yalnız belge ve taban):
    adim(t, tarama, artim) -> (v, w)
        t       dunya.zaman_s (s)
        tarama  son çağrıdan beri yeni LiDAR turu bittiyse sözleşme sözlüğü {"t", "acilar", "mesafeler"} (+ ekler,
                aşağıda), yoksa None. Birden çok tur bittiyse (denetim_hz < 10) yalnız sonuncusu; `tarama["atlanan"]`
                kaç turun atlandığını yazar.
        artim   (dx, dy, dth) son çağrıdan beri enkoder odometrisi, son çağrıdaki odometri pozunun çerçevesinde; nokta
                arka çeker dingilin ortası (konumlayıcı `odometri_noktasi_x = -0,185` ile gövde merkezine çevirir).
                Deneydeki gibi tik toplamlarından, iz 0,426 m (firmware / Pi sabiti), tik yolu π 0,125 / 1980.
        Tarama ekleri (isteğe bağlı kullanım): "artim_once" = son çağrıdan turun ORTASINA (t + 0,05 s) dek odometri,
        "artim_sonra" = tur ortasından şimdiye dek (artim = artim_once ∘ artim_sonra). Konumlayıcıyı tur ortasındaki
        pozla beslemek için (deney böyle besledi): mcl.guncelle(tarama, artim=artim_once); mcl.hareket(artim_sonra).
    durum() -> {"poz": (x, y, th) | None, "mod": str, "yol": [(x, y), ...], "hedef": (x, y) | None,
                "harita": None | {"cozunurluk_m", "orijin": (x0, y0), "izgara": 2B dizi}, "ek": {...}}
        mod "bitti" 1 s sürerse kos() biter (beyin işini bitirdi).

Hakem (isteğe bağlı): guncelle(t, gercek_poz, temas_var); .bitti (True olunca kos biter); .sonuc (sözlük).
Kayıt: kayit = dosya yolu (.npz) ya da `Kayit` nesnesi; biçim BENIOKU "Kayıt biçimi".
"""

import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gezinme import _yol  # noqa: E402,F401  (yol eklemeleri)

import numpy as np  # noqa: E402

KAYIT_SURUMU = 1
TEMAS_BIRLESTIR_S = 1.0
VARSAYILAN_GEZINME_VARYANTI = "ONERI"   # koridor deneyinin robotu (deneyler/koridor_karisiklik/ortak.py SURUS_VARYANTI)


def varsayilan_varyant(sahne_ad):
    """Koridor (`koridor_*`) ve labirent (`labirent_*`) sahnelerinde ONERI (dönebilen robot, VARSAYIM); öbürlerinde V0."""
    ad = os.path.basename(str(sahne_ad or ""))
    return VARSAYILAN_GEZINME_VARYANTI if ad.startswith(("koridor_", "labirent_")) else "V0"


def sar(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def goreli(a, b):
    """a pozundan b pozuna a'nın çerçevesinde artım (dx, dy, dth)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    c, s = math.cos(a[2]), math.sin(a[2])
    return (c * dx + s * dy, -s * dx + c * dy, sar(b[2] - a[2]))


def sahne_yukle(sahne):
    """sahne: ad (kod/fizik/sahneler/<ad>.json), JSON dosya yolu ya da sözlük. Harita: sahne["harita_veri"] (sözlük,
    yerinde) varsa o, yoksa sahne["harita"] adı (kod/araclar/haritalar/<ad>.json) ya da dosya yolu.
    Döner: (ad, sahne sözlüğü, harita veri sözlüğü)."""
    import dunya as D
    if isinstance(sahne, dict):
        s = sahne
        ad = s.get("ad", "sahne")
    else:
        s = D.sahne_oku(sahne)
        ad = os.path.splitext(os.path.basename(str(sahne)))[0]
    if isinstance(s.get("harita_veri"), dict):
        veri = s["harita_veri"]
    else:
        h = s["harita"]
        yol = h if (os.path.isabs(h) or h.endswith(".json")) and os.path.exists(h) else \
            os.path.join(_yol.KOD, "araclar", "haritalar", h + ".json")
        with open(yol, encoding="utf-8") as f:
            veri = json.load(f)
    return ad, s, veri


class Beyin:
    """Protokol tabanı (belge). Alt sınıf adim / durum yazar."""

    def adim(self, t, tarama, artim):
        return 0.0, 0.0

    def durum(self):
        return {"poz": None, "mod": "", "yol": [], "hedef": None, "harita": None, "ek": {}}


# ------------------------------------------------------------------ kayıt
MODLAR_SABIT = ["", "bos", "kesif", "izle", "yerinde", "bekle", "bitti", "planla", "kayip"]


class Kayit:
    """Adım adım kayıt (denetim adımında bir satır) + seyrek harita + (isteğe bağlı) taramalar. `kaydet(yol)` -> .npz."""

    def __init__(self, yol=None, taramalar=True, harita_aralik_s=2.0):
        self.yol = yol
        self.taramalar_acik = taramalar
        self.harita_aralik_s = harita_aralik_s
        self.satir = []          # t, gx, gy, gth, ox, oy, oth, tx, ty, tth, v_k, w_k, v_g, w_g, temas, mod_i, hx, hy
        self.modlar = list(MODLAR_SABIT)
        self.yollar = []         # (t, [[x, y], ...]) yol değişince
        self.haritalar = []      # (t, cozunurluk, (x0, y0), izgara)
        self.tarama_t, self.tarama_m = [], []
        self.ekler = []          # (t, ek sözlüğü) seyrek (harita aralığında)
        self.meta = {}
        self._son_yol = None
        self._son_harita_t = -1e9

    def _mod_i(self, m):
        m = str(m or "")
        if m not in self.modlar:
            self.modlar.append(m)
        return self.modlar.index(m)

    def adim(self, t, gercek, odo, durum, komut, olculen, temas):
        p = durum.get("poz") if durum else None
        h = durum.get("hedef") if durum else None
        nan = float("nan")
        self.satir.append((t, gercek[0], gercek[1], gercek[2], odo[0], odo[1], odo[2],
                           *(p if p is not None else (nan, nan, nan)), komut[0], komut[1], olculen[0], olculen[1],
                           1.0 if temas else 0.0, float(self._mod_i(durum.get("mod") if durum else "")),
                           *(h if h is not None else (nan, nan))))
        yol = durum.get("yol") if durum else None
        anahtar = None if not yol else (len(yol), tuple(map(float, yol[0])), tuple(map(float, yol[-1])))
        if anahtar != self._son_yol:
            self._son_yol = anahtar
            self.yollar.append((t, [[float(a), float(b)] for a, b in (yol or [])]))
        if durum and t - self._son_harita_t >= self.harita_aralik_s:
            self._son_harita_t = t
            hr = durum.get("harita")
            if hr is not None:
                self.haritalar.append((t, float(hr["cozunurluk_m"]), tuple(map(float, hr["orijin"])), np.array(hr["izgara"])))
            ek = durum.get("ek")
            if ek:
                self.ekler.append((t, ek))

    def tarama(self, tarama):
        if self.taramalar_acik and tarama is not None:
            m = np.asarray([np.nan if d is None else d for d in tarama["mesafeler"]], dtype=float)
            q = np.where(np.isfinite(m), np.round(m * 1000.0), 0).clip(0, 65535).astype(np.uint16)   # mm, 0 = yok
            self.tarama_t.append(float(tarama["t"]))
            self.tarama_m.append(q)

    def kaydet(self, yol=None, meta=None, acilar=None, montaj=None):
        yol = yol or self.yol
        S = np.array(self.satir, dtype=float).reshape(-1, 18)
        diz = dict(t=S[:, 0], gercek=S[:, 1:4], odo=S[:, 4:7], tahmin=S[:, 7:10], komut=S[:, 10:12], olculen=S[:, 12:14],
                   temas=S[:, 14].astype(np.uint8), mod=S[:, 15].astype(np.int16), hedef=S[:, 16:18])
        if self.tarama_t:
            diz["tarama_t"] = np.array(self.tarama_t)
            diz["tarama_mm"] = np.stack(self.tarama_m)
        if acilar is not None:
            diz["acilar"] = np.asarray(acilar, dtype=float)
        for i, (t, coz, org, iz) in enumerate(self.haritalar):
            diz["harita_%d" % i] = iz
        m = dict(self.meta, **(meta or {}))
        m.update(surum=KAYIT_SURUMU, modlar=self.modlar, montaj=list(montaj) if montaj is not None else None,
                 yollar=self.yollar, haritalar=[dict(t=t, cozunurluk_m=c, orijin=list(o), anahtar="harita_%d" % i)
                                                for i, (t, c, o, _) in enumerate(self.haritalar)],
                 ekler=[dict(t=t, ek=e) for t, e in self.ekler])
        os.makedirs(os.path.dirname(os.path.abspath(yol)), exist_ok=True)
        np.savez_compressed(yol, meta=np.array(json.dumps(m, ensure_ascii=False, default=_json_yedek)), **diz)
        return yol


def _json_yedek(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def kayit_oku(yol):
    """.npz kaydı -> (meta sözlüğü, diziler sözlüğü). tarama_mm 0 = ölçüm yok."""
    with np.load(yol, allow_pickle=False) as z:
        dz = {k: z[k] for k in z.files}
    return json.loads(str(dz.pop("meta"))), dz


# ------------------------------------------------------------------ düzenek
class Duzenek:
    def __init__(self, sahne, varyant=None, tohum=0, baslangic=None, *, ek_engeller=(), lidar_ayar=None, sonar_acik=True):
        """sahne: ad / JSON yolu / sözlük (`sahne_yukle`). varyant None: `varsayilan_varyant(sahne)`; "V0" bugünkü robot.
        tohum: LiDAR gürültü tohumu. baslangic (x, y, th): robot oraya konur (yoksa sahnenin başlangıcı).
        ek_engeller: haritada OLMAYAN engeller (Harita "engeller" biçimi; fizikte var, Beyin'in haritasında yok)."""
        import lidar as L
        import varyantlar as VR
        from fizik_esp32 import FizikEsp32
        from sahte_esp32.harita import Harita
        from sahte_esp32.tasima import BellekTasima
        from lale_pi.istemci import Esp32Istemci
        self.sahne_ad, self.sahne, veri = sahne_yukle(sahne)
        self.varyant_ad = varyant if varyant is not None else varsayilan_varyant(self.sahne_ad)
        self.tohum = tohum
        self.ek_engeller = list(ek_engeller)
        if self.ek_engeller:
            veri = dict(veri)
            veri["engeller"] = list(veri.get("engeller", [])) + self.ek_engeller
        self.harita = Harita(veri, ad=self.sahne_ad)
        if baslangic is None:
            lab = ((self.sahne.get("labirent") or {}).get("start") or {}).get("poz")
            if lab:                              # labirent: START pozu (x, y, yön rad)
                baslangic = (float(lab[0]), float(lab[1]), float(lab[2]))
            else:
                b = self.sahne.get("baslangic", veri.get("baslangic", {}))
                baslangic = (float(b["x"]), float(b["y"]), math.radians(float(b.get("aci_derece", 0))))
        self.baslangic = tuple(float(v) for v in baslangic)
        self.c = FizikEsp32(self.harita, konum=self.baslangic, sahne=self.sahne, varyant=VR.al(self.varyant_ad),
                            sonar_acik=sonar_acik)
        self.w = self.c.dunya
        self.e = Esp32Istemci(BellekTasima(self.c))
        self.e.baglan()
        self.lidar = L.SanalLidar(self.w, tohum=tohum, **(lidar_ayar or {}))
        self.lidar.bagla()
        self._bekleyen = []
        self.lidar.dinleyiciler.append(lambda tar, ek: self._bekleyen.append(tar))
        # enkoder odometrisi (lidar.DeneyKaydi ile aynı formül), 10 ms dilimde; temas olayları
        self.tik_m = math.pi * self.c.teker_capi / self.c.tik_tur
        self.iz = self.c.fw_iz
        self.odo = list(self.baslangic)
        self._tik = list(self.c.tik)
        self.odo_gecmis = []                     # (t, x, y, th) son 2 s
        self.temas_olay = 0                      # çarpma olayı (1 s içinde yeniden başlayan temas birleşir)
        self.temas_kenar = 0                     # ham temas başlangıcı (10 ms dilimde False -> True)
        self._temas_son_t = -1e9
        self.temas_dilim = 0
        self._temas_onceki = False
        self.temas_simdi = False
        onceki = self.c.kayitci

        def kanca(c):
            if onceki is not None:
                onceki(c)
            self._dilim()
        self.c.kayitci = kanca
        self._devrede = False
        # ek engellerin MuJoCo geom'ları (engel_kolon_* / engel_duvar_*): engel_tasi ile oynatılır
        self._ek_geom = self._ek_geomlari()

    # ------------------------------------------------------------ iç
    def _ek_geomlari(self):
        import mujoco
        m = self.w.m
        n_daire = len(self.harita.daireler)
        ek_daire = sum(1 for e in self.ek_engeller if e.get("tur") == "daire")
        ilk = n_daire - ek_daire
        out = []
        for i in range(ilk, n_daire):
            g = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "engel_kolon_%d" % i)
            if g >= 0:
                out.append(g)
        return out

    def engel_tasi(self, i, x, y):
        """i. ek daire engelini (x, y)'ye taşı (uzağa taşımak = kaldırmak). Fizik ve LiDAR hemen görür."""
        import mujoco
        g = self._ek_geom[i]
        self.w.m.geom_pos[g][0] = x
        self.w.m.geom_pos[g][1] = y
        mujoco.mj_forward(self.w.m, self.w.d)

    def _dilim(self):
        c, w = self.c, self.w
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
        t = w.zaman_s
        self.odo_gecmis.append((t, o[0], o[1], o[2]))
        if len(self.odo_gecmis) > 400:
            del self.odo_gecmis[:200]
        temas = w.temas_engel()
        if temas:
            self.temas_dilim += 1
            if not self._temas_onceki:
                self.temas_kenar += 1
                # önceki temasın bitişinden 1 s içinde yeniden başlayan temas aynı olay (labirent hakemiyle aynı kural)
                if t - self._temas_son_t > TEMAS_BIRLESTIR_S:
                    self.temas_olay += 1
            self._temas_son_t = t
        self._temas_onceki = self.temas_simdi = temas

    def odo_ara(self, t):
        """t anındaki odometri pozu (10 ms satırlardan doğrusal ara değer)."""
        G = self.odo_gecmis
        if not G or t >= G[-1][0]:
            return tuple(self.odo)
        if t <= G[0][0]:
            return G[0][1:]
        lo, hi = 0, len(G) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if G[mid][0] <= t:
                lo = mid
            else:
                hi = mid
        a, b = G[lo], G[hi]
        u = (t - a[0]) / max(b[0] - a[0], 1e-9)
        return (a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u, a[3] + sar(b[3] - a[3]) * u)

    def gercek_poz(self):
        x, y, _, yaw, _, _ = self.w.poz()
        return (x, y, yaw)

    def konum_ayarla(self, x, y, th):
        """Robotu (x, y, th)'ye ışınla (yer gerçeği). Odometri de oraya kurulur (Beyin bunu bilmez)."""
        self.c.konum_ayarla(x, y, th)
        self.lidar._sifirla_tur()                # ışınlanmadan önce başlamış yarım tur atılır
        self.odo = [float(x), float(y), float(th)]
        self._tik = list(self.c.tik)
        self.odo_gecmis.clear()
        self._bekleyen.clear()

    def devreye_al(self):
        if not self._devrede:
            o = self.e.devreye_al_ve_bekle()
            assert o.get("guc") == "devrede", o
            self._devrede = True

    # ------------------------------------------------------------ koşu
    def kos(self, beyin, sure_s, hakem=None, kayit=None, denetim_hz=20, olay=None):
        """Beyin'i sure_s sanal saniye koştur. olay(dz, t) her denetim adımında çağrılır (senaryo betikleri: engel
        taşıma vb.). Döner: sonuç sözlüğü."""
        e, w = self.e, self.w
        self.devreye_al()
        if isinstance(kayit, str):
            kayit = Kayit(kayit)
        adim_ms = int(round(1000.0 / denetim_hz))
        if hasattr(getattr(beyin, "izleyici", None), "ayar"):
            beyin.izleyici.ayar.dt_s = adim_ms / 1000.0
        t0 = w.zaman_s
        duvar0 = time.perf_counter()
        son_odo = tuple(self.odo)
        self._bekleyen.clear()
        temas0, dilim0, kenar0 = self.temas_olay, self.temas_dilim, self.temas_kenar
        yol = 0.0
        onceki_g = self.gercek_poz()
        v = om = 0.0
        bitti_s = None
        bitis = "sure"
        adim = 0
        reddedilen = 0
        durum = {}
        while w.zaman_s - t0 < sure_s:
            t = w.zaman_s
            tarama = None
            if self._bekleyen:
                tarama = dict(self._bekleyen[-1])
                tarama["atlanan"] = len(self._bekleyen) - 1
                self._bekleyen.clear()
                orta = tarama["t"] + 0.5 / self.lidar.ayar.tarama_hz
                o_orta = self.odo_ara(orta)
                tarama["artim_once"] = goreli(son_odo, o_orta)
                tarama["artim_sonra"] = goreli(o_orta, tuple(self.odo))
                if kayit is not None:
                    kayit.tarama(tarama)
            simdi = tuple(self.odo)
            artim = goreli(son_odo, simdi)
            son_odo = simdi
            v, om = beyin.adim(t, tarama, artim)
            v, om = float(v), float(om)
            c = e.istek({"k": "sur", "v": round(v, 4), "w": round(om, 4)}, denetle=False)
            if not c.get("ok"):
                reddedilen += 1
            e.kalp_atisi()
            gecen_ms = int(round((w.zaman_s - t) * 1000.0))      # istek cevabını beklerken geçen sanal süre
            e.bekle(max(10, adim_ms - gecen_ms))
            g = self.gercek_poz()
            yol += math.hypot(g[0] - onceki_g[0], g[1] - onceki_g[1])
            onceki_g = g
            durum = beyin.durum() or {}
            if kayit is not None:
                kayit.adim(w.zaman_s - t0, g, tuple(self.odo), durum, (v, om), w.hiz(), self.temas_simdi)
            if hakem is not None:
                hakem.guncelle(w.zaman_s - t0, g, self.temas_simdi)
                if getattr(hakem, "bitti", False):
                    bitis = "hakem"
                    break
            if olay is not None:
                olay(self, w.zaman_s - t0)
            if durum.get("mod") == "bitti":
                if bitti_s is None:
                    bitti_s = w.zaman_s
                elif w.zaman_s - bitti_s >= 1.0:
                    bitis = "beyin"
                    break
            else:
                bitti_s = None
            adim += 1
        e.istek({"k": "dur"}, denetle=False)
        e.bekle(300)
        sure = w.zaman_s - t0
        duvar = time.perf_counter() - duvar0
        g = self.gercek_poz()
        sonuc = dict(sahne=self.sahne_ad, varyant=self.varyant_ad, tohum=self.tohum, baslangic=list(self.baslangic),
                     sure_s=round(sure, 3), duvar_s=round(duvar, 2), rtf=round(sure / max(duvar, 1e-9), 2),
                     bitis=bitis, adim=adim, yol_m=round(yol, 3), temas_olay=self.temas_olay - temas0, temas_kenar=self.temas_kenar - kenar0,
                     temas_sure_s=round((self.temas_dilim - dilim0) * 0.01, 2), reddedilen_sur=reddedilen,
                     son_gercek=[round(z, 4) for z in g],
                     son_tahmin=([round(z, 4) for z in durum["poz"]] if durum.get("poz") is not None else None),
                     son_mod=durum.get("mod"), hakem=(getattr(hakem, "sonuc", None) if hakem is not None else None))
        if kayit is not None:
            kayit.kaydet(meta=dict(sahne=self.sahne_ad, varyant=self.varyant_ad, tohum=self.tohum,
                                   baslangic=list(self.baslangic), denetim_hz=denetim_hz, sonuc=sonuc,
                                   ek_engeller=self.ek_engeller),
                         acilar=self.lidar.acilar, montaj=self.lidar.montaj)
            sonuc["kayit"] = kayit.yol
        return sonuc


# ------------------------------------------------------------------ hakemler
class HedefHakemi:
    """Yer gerçeğiyle hedef denetimi: robot hedefin `pay_m` içinde `durma_s` boyunca durursa bitti (başarılı)."""

    def __init__(self, hedef, pay_m=0.3, durma_s=1.5, bitince_dur=True):
        self.hedef = (float(hedef[0]), float(hedef[1]))
        self.pay_m, self.durma_s, self.bitince_dur = pay_m, durma_s, bitince_dur
        self.bitti = False
        self._dur_bas = None
        self._son = None
        self.ilk_varis_s = None
        self.en_yakin_m = math.inf
        self.temas = 0
        self._temas_onceki = False
        self.sonuc = {}

    def guncelle(self, t, gercek, temas):
        d = math.hypot(gercek[0] - self.hedef[0], gercek[1] - self.hedef[1])
        self.en_yakin_m = min(self.en_yakin_m, d)
        if temas and not self._temas_onceki:
            self.temas += 1
        self._temas_onceki = temas
        if d < self.pay_m and self.ilk_varis_s is None:
            self.ilk_varis_s = t
        duruyor = self._son is not None and math.hypot(gercek[0] - self._son[0], gercek[1] - self._son[1]) < 0.002
        self._son = gercek
        if d < self.pay_m and duruyor:
            if self._dur_bas is None:
                self._dur_bas = t
            if t - self._dur_bas >= self.durma_s and self.bitince_dur:
                self.bitti = True
        else:
            self._dur_bas = None
        self.sonuc = dict(hata_m=round(d, 4), en_yakin_m=round(self.en_yakin_m, 4), ilk_varis_s=self.ilk_varis_s,
                          vardi=self.bitti, temas=self.temas)
