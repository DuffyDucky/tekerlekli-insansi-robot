"""Aşağı bakan lazerli mesafe sensörü modeli (VL53L1X türü; VARSAYIM'lar aşağıda) ve sensör yerleşimleri.

Bir sensör = robot gövde çerçevesinde konum (x, y, z m) + bakış yönü (dikeyden `egim_derece` kadar `yon_derece`
yönüne yatık; yon 0 = ileri +x, 180 = geri) + görüş konisi (`koni_derece` tam açı; VL53L1X 27, ROI ile 15).

Ölçüm (her örnekte, MuJoCo ışın sorgusu `mj_ray`, yalnız sahne geom grubu 0; robotun kendi gövdesi görülmez):
  - koni 17 ışınla örneklenir: eksen (ağırlık 1), yarım açının yarısında 8 ışın (ağırlık 1), kenarda 8 ışın (0,5).
  - menzil dışı ışın (isabet yok ya da > menzil_maks) sinyal vermez.
  - DÖNEN DEĞER (VARSAYIM, kötümser): ışın mesafeleri 30 mm boşlukla öbeklere ayrılır; toplam ağırlığın en az
    %25'ini taşıyan EN YAKIN öbeğin ağırlıklı ortalaması. Gerçek VL53L1X histogramda ilk güçlü tepeyi verir; koninin
    çoğu boşluğu görse de yakın zemin yeterli sinyal verdikçe "zemin" der. Hiçbir öbek %25'e ulaşmazsa dönüş yok (None).
  - gürültü: Gauss, sigma = 2,5 mm + %0,2 x mesafe (VARSAYIM; veri sayfası kısa menzilde ±mm mertebesi), 1 mm'ye
    yuvarlanır. Koyu yüzey (`zemin_koyu_*` geom'u): sigma x 2 ve ek %5 dönüşsüz örnek (VARSAYIM).
  - parlak zemin / güneş: her örnek `yok_orani` olasılıkla dönüşsüz (None).
  - örnekleme 50 Hz (20 ms; sensör başına faz 0 ya da 10 ms, tohumla), ölçüm bir örnek SONRA (20 ms) kullanılabilir.
  - arıza: "sabit" (hep kalibrasyon değerini verir: ölü sensör, donmuş çıktı), "yok" (hep dönüşsüz).
Modellenmeyen: çapraz konuşma (iki sensör aynı anda), sensör camında toz / çizik, eğik gelişte sinyal kaybı, ayna /
cam zemin, ışığın kenarda saçılması, I2C hatası, gerçek histogram işleme. Bunlar masada denenmeli.
"""

import math

KONI_HALKA = ((0.0, 1, 1.0), (0.5, 8, 1.0), (1.0, 8, 0.5))   # (yarım açı oranı, ışın sayısı, ağırlık)
OBEK_BOSLUK_M = 0.03
OBEK_ESIK = 0.25


class SensorAyar:
    def __init__(self, ad, x, y, z, egim_derece=0.0, yon_derece=0.0, koni_derece=27.0, menzil_min_m=0.04,
                 menzil_maks_m=4.0, sigma_taban_m=0.0025, sigma_oran=0.002, yok_orani=0.0, ariza=None):
        self.ad, self.x, self.y, self.z = ad, float(x), float(y), float(z)
        self.egim_derece, self.yon_derece, self.koni_derece = float(egim_derece), float(yon_derece), float(koni_derece)
        self.menzil_min_m, self.menzil_maks_m = menzil_min_m, menzil_maks_m
        self.sigma_taban_m, self.sigma_oran = sigma_taban_m, sigma_oran
        self.yok_orani = yok_orani
        self.ariza = ariza

    def eksen(self):
        e, a = math.radians(self.egim_derece), math.radians(self.yon_derece)
        return (math.sin(e) * math.cos(a), math.sin(e) * math.sin(a), -math.cos(e))

    def isinlar(self):
        """Gövde çerçevesinde [(yön (3), ağırlık)]."""
        d = self.eksen()
        # eksene dik iki birim vektör
        yard = (0.0, 0.0, 1.0) if abs(d[2]) < 0.9 else (1.0, 0.0, 0.0)
        u = _norm(_vek(d, yard))
        v = _vek(d, u)
        yarim = math.radians(self.koni_derece / 2.0)
        out = []
        for oran, n, w in KONI_HALKA:
            al = yarim * oran
            for k in range(n):
                f = 2 * math.pi * k / n + (math.pi / 8 if oran == 1.0 else 0.0)
                c, s = math.cos(al), math.sin(al)
                yon = tuple(c * d[i] + s * (math.cos(f) * u[i] + math.sin(f) * v[i]) for i in range(3))
                out.append((_norm(yon), w))
        return out


def _vek(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _norm(a):
    n = math.sqrt(sum(x * x for x in a)) or 1.0
    return tuple(x / n for x in a)


def obek_degeri(isabetler, toplam_agirlik):
    """isabetler [(mesafe, ağırlık)] -> en yakın yeterli öbeğin ağırlıklı ortalaması ya da None (saf; test edilir)."""
    if not isabetler:
        return None
    s = sorted(isabetler)
    obekler = [[s[0]]]
    for h in s[1:]:
        if h[0] - obekler[-1][-1][0] <= OBEK_BOSLUK_M:
            obekler[-1].append(h)
        else:
            obekler.append([h])
    for ob in obekler:
        w = sum(a for _, a in ob)
        if w >= OBEK_ESIK * toplam_agirlik:
            return sum(t * a for t, a in ob) / w
    return None


# ------------------------------------------------------------------ yerleşimler (robot çerçevesi, m)
# Gövde sınırları (lale.xml, ölçüm BENIOKU): etek kutusu x +-0,2625, y +-0,26, z 0,035-0,265; ön / arka teker merkezi
# x +-0,185, iz y +-0,216; teker yarıçapı 0,0625, genişlik 0,058 (y 0,187-0,245); teker x kapsamı 0,1225-0,2475.
# Sensör modülü (VL53L1X kartı ~ 13 x 18 mm) etek içinde, eteğin alt açıklığından aşağı bakar: x <= 0,255 (ön yüzden
# 7,5 mm içeri), |y| <= 0,250. Köşe sensörü tekerin önünde (x 0,255 > 0,2475) ve dışında (y 0,250 > 0,245).
ON_X, ARKA_X, KOSE_Y, IC_Y = 0.255, -0.255, 0.250, 0.085


def yerlesim(ad, z=0.06, egim=15.0, koni=27.0):
    """Adlandırılmış aday yerleşim -> [SensorAyar]. Ön sensörler öne (yon 0), arka sensörler geriye (yon 180) yatık."""
    on = {"2K": [("on_sol", ON_X, KOSE_Y), ("on_sag", ON_X, -KOSE_Y)],
          "3KO": [("on_sol", ON_X, KOSE_Y), ("on_orta", ON_X, 0.0), ("on_sag", ON_X, -KOSE_Y)],
          "4O": [("on_sol", ON_X, KOSE_Y), ("on_ic_sol", ON_X, IC_Y), ("on_ic_sag", ON_X, -IC_Y), ("on_sag", ON_X, -KOSE_Y)],
          "2I": [("on_ic_sol", ON_X, 0.120), ("on_ic_sag", ON_X, -0.120)]}
    # "D" soneki: köşe sensörleri çapraz dışa yatık (yon ±45°, arkada ±135°): eğim yanal kenarı ve yerinde dönüşü de görür
    parca = ad.split("+")
    capraz = parca[0].endswith("D")
    L = []
    for nm, x, y in on[parca[0].rstrip("D")]:
        yon = (45.0 if y > 0 else -45.0) if (capraz and abs(y) >= KOSE_Y) else 0.0
        L.append(SensorAyar(nm, x, y, z, egim, yon, koni))
    if len(parca) > 1 and parca[1] in ("2A", "2AD"):
        for nm, x, y in (("arka_sol", ARKA_X, KOSE_Y), ("arka_sag", ARKA_X, -KOSE_Y)):
            yon = (135.0 if y > 0 else -135.0) if parca[1] == "2AD" else 180.0
            L.append(SensorAyar(nm, x, y, z, egim, yon, koni))
    return L


def yerlesim_adi(ad, z, egim, koni=27.0):
    return "%s_z%d_e%d%s" % (ad, round(z * 1000), round(egim), "" if koni == 27.0 else "_k%d" % round(koni))


# ------------------------------------------------------------------ MuJoCo'ya bağlı dizi
class SensorDizisi:
    """Bir dünyaya bağlı sensörler. `ornekle(t_ms)` 10 ms dilim başında çağrılır; o dilimde örneği düşen sensörleri
    ölçer, bir örnek (20 ms) sonra `hazir(t_ms)` ile verir."""

    PERIYOT_MS = 20

    def __init__(self, dunya, ayarlar, rng):
        import mujoco
        import numpy as np
        self.mj, self.np = mujoco, np
        self.w = dunya
        self.ayarlar = list(ayarlar)
        self.rng = rng
        self.faz = [int(rng.integers(0, 2)) * 10 for _ in self.ayarlar]
        self.isin = [a.isinlar() for a in self.ayarlar]
        self.toplam = [sum(w for _, w in L) for L in self.isin]
        m = dunya.m
        adlar = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or "" for g in range(m.ngeom)]
        self.koyu = {g for g, n in enumerate(adlar) if n.startswith("zemin_koyu")}
        self._grup = np.array([1, 0, 0, 0, 0, 0], dtype=np.uint8)
        self._gid = np.zeros(1, dtype=np.int32)
        self._kuyruk = []                 # (hazır ms, sensör i, değer)
        self.sabit = [None] * len(self.ayarlar)   # "sabit" arızasında verilecek değer (kalibrasyondan)
        self.son_ham = [None] * len(self.ayarlar)  # son ölçümün gürültüsüz değeri (yalnız kayıt / hakem)

    def dunya_poz(self, i):
        np = self.np
        a = self.ayarlar[i]
        R = self.w.d.xmat[self.w.taban].reshape(3, 3)
        p = self.w.d.xpos[self.w.taban] + R @ np.array((a.x, a.y, a.z))
        return p, R

    def olc(self, i, gurultu=True):
        """i. sensörün şimdiki ölçümü (m) ya da None. gurultu False: ideal öbek değeri (test / kalibrasyon denetimi)."""
        np, mj = self.np, self.mj
        a = self.ayarlar[i]
        if a.ariza == "yok":
            return None
        if a.ariza == "sabit" and self.sabit[i] is not None:
            return self.sabit[i]
        p, R = self.dunya_poz(i)
        isabet = []
        koyu = False
        for yon, w in self.isin[i]:
            y = R @ np.asarray(yon)
            t = mj.mj_ray(self.w.m, self.w.d, p, y, self._grup, 1, -1, self._gid)
            if t < 0 or t > a.menzil_maks_m:
                continue
            isabet.append((max(t, a.menzil_min_m), w))
            if int(self._gid[0]) in self.koyu:
                koyu = True
        d = obek_degeri(isabet, self.toplam[i])
        self.son_ham[i] = d
        if not gurultu or d is None:
            return d
        sig = a.sigma_taban_m + a.sigma_oran * d
        yok = a.yok_orani
        if koyu:
            sig *= 2.0
            yok = 1.0 - (1.0 - yok) * 0.95
        if yok > 0.0 and self.rng.random() < yok:
            return None
        return round(d + float(self.rng.normal(0.0, sig)), 3)

    def ornekle(self, t_ms):
        for i in range(len(self.ayarlar)):
            if (t_ms - self.faz[i]) % self.PERIYOT_MS == 0:
                self._kuyruk.append((t_ms + self.PERIYOT_MS, i, self.olc(i)))

    def hazir(self, t_ms):
        out = [(i, v) for (h, i, v) in self._kuyruk if h <= t_ms]
        if out:
            self._kuyruk = [k for k in self._kuyruk if k[0] > t_ms]
        return out

    def teker_ortusmesi(self):
        """Koninin ışınları robotun kendi tekerlerine çarpıyor mu (yerleşim sığma denetimi). Döner: [ışın sayısı]."""
        np, mj = self.np, self.mj
        out = []
        for i in range(len(self.ayarlar)):
            p, R = self.dunya_poz(i)
            n = 0
            for yon, _ in self.isin[i]:
                y = R @ np.asarray(yon)
                for g in self.w.tum_teker_geom:
                    t = mj.mju_rayGeom(self.w.d.geom_xpos[g], self.w.d.geom_xmat[g], self.w.m.geom_size[g], p, y,
                                       int(self.w.m.geom_type[g]))
                    if 0 <= t < 0.5:
                        n += 1
                        break
            out.append(n)
        return out
