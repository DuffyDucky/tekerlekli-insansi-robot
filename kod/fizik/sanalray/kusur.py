"""Kusur modeli (dayanıklılık ölçümü): gerçek dünya Beyin'in bildiğinden farklı. FİZİK / SENSÖR tarafı.

Beyin hep NOMİNAL etiket planını ve kameranın kendi bildiği K'sini kullanır (`deney.tum_etiketler`); kusur yalnız
sahneye (gerçek etiket yeri / yönü / varlığı / dokusu), kameraya (montaj eğimi, odak) ve görüntü hattına (gecikme, kare
düşmesi, örtülme, parlama, bulanıklık) uygulanır. Kusurlar sıfırken davranış `Algilayicilar` ile birebir aynıdır (aynı
gürültü dizisi: kusur rastgeleliği ayrı bir üreteçten).

Bütün rastgele kusurlar tohumdan önce birim değerler (u ∈ [-1, 1], işaret, seçim sırası) olarak çekilir ve düzeyle
ölçeklenir: aynı tohumda 1 / 3 / 5 cm düzeyleri aynı yönde, yalnız büyüklükte farklı (kırılma noktası karşılaştırılabilir).

VARSAYIMLAR (sonuc/SONUC.md "Dayanıklılık" bölümünde de yazılı):
  - harita konum hatası: her etiket duvar boyunca ve dikeyde bağımsız U(-e, e) (duvara dik hata yok: etiket duvarda);
  - harita açı hatası: etiket yüz normali (yaw) U(-a, a) (eğik yüzey / kötü yapıştırma); kenarı duvara girmesin diye
    etiket a ile orantılı en çok 1 cm öne alınır (bu da küçük bir konum hatasıdır);
  - odak hatası: Beyin'in K'sindeki fx = fy = f (1 + s o), s = ±1 tohumdan (kalibrasyonsuz belge değeri ya da kötü
    kalibrasyon); asal nokta doğru;
  - montaj eğimi: kamera kendi yatay ekseni çevresinde (pitch) s x eğim, s = ±1 tohumdan; Beyin kamerayı yatay sanar;
  - gecikme: kare çekildiği andan `gecikme_s` sonra Beyin'e varır (Pi algılama süresi + aktarım); Beyin bunu
    bilmez (zaman damgası telafisi yok: bugünkü Beyin'in davranışı);
  - örtülme / parlama: etiket başına iki durumlu zaman süreci (ortalama bölüm 2 s, zamanın p kesri açık); örtülme gri
    (90) bir dikdörtgen, etiket kutusunun bir yanından `ortulme_kesir` kadarı (insan, kapı kanadı, pano); parlama
    etiket içinde rastgele noktada Gauss leke (yarıçap kutu kenarının 0,25'i, genlik `parlama_genlik`, 255'te doyar);
  - hareket bulanıklığı: pozlama süresi uzar (loş koridor) ve kafa titreşimi (açısal hız std, yatay + dikey); gövde
    dönüşünün bulanıklığı zaten vardı;
  - yırtık: etiketlerin bir kesrinin bir köşesi (beyaz pay + siyah karenin `yirtik_boy` kadarı) eksik, duvar görünür;
  - kayıp etiket: haritada olan bir etiket sahnede yok; yanlış yer: bir etiket duvar boyunca `yanlis_yer_m` öteye
    asılmış (harita eski yeri söylüyor)."""

import math
import os

import numpy as np

from sanalray import _yol, etiket as E, kamera as KM
from sanalray.algilayici import Algilayicilar

KUSUR_ALANLARI = dict(
    harita_konum_m=0.0, harita_aci_derece=0.0, odak_orani=0.0, egim_derece=0.0, gecikme_s=0.0, kare_dusme=0.0,
    ortulme=0.0, ortulme_kesir=0.4, parlama=0.0, parlama_genlik=230.0, pozlama_s=None, titresim=0.0,
    yirtik_oran=0.0, yirtik_boy=0.25, kayip_etiket=0, yanlis_yer=0, yanlis_yer_m=1.0,
)
BOLUM_S = 2.0                      # örtülme / parlama bölümünün ortalama süresi
DUVAR_GRI = 185                    # yırtık köşede görünen duvar (opak duvar malzemesi ışıkta ≈ bu gri)


def kusur_tam(k):
    out = dict(KUSUR_ALANLARI)
    for a, v in (k or {}).items():
        if a not in out:
            raise ValueError("bilinmeyen kusur: %s" % a)
        out[a] = v
    return out


class Cekilis:
    """Tohumdan önceden çekilmiş birim kusur değerleri (düzeyden bağımsız)."""

    def __init__(self, tohum, kimlikler):
        r = np.random.default_rng(100003 + 7 * int(tohum))
        n = len(kimlikler)
        self.kimlikler = list(kimlikler)
        self.u_t = dict(zip(kimlikler, r.uniform(-1, 1, n)))
        self.u_z = dict(zip(kimlikler, r.uniform(-1, 1, n)))
        self.u_a = dict(zip(kimlikler, r.uniform(-1, 1, n)))
        self.sira = [kimlikler[i] for i in r.permutation(n)]        # kayıp / yanlış yer / yırtık seçimi
        self.kose = dict(zip(kimlikler, r.integers(0, 4, n)))
        self.s_odak = 1.0 if r.uniform() < 0.5 else -1.0
        self.s_egim = 1.0 if r.uniform() < 0.5 else -1.0
        self.s_yer = 1.0 if r.uniform() < 0.5 else -1.0


def _duvarda(h, x, y, yaw):
    """(x, y) noktası yüz normali yaw olan bir duvar yüzünde mi (2 cm içinde duvar)?"""
    r = h.isin(x + 0.05 * math.cos(yaw), y + 0.05 * math.sin(yaw), yaw + math.pi, 0.2)
    return r is not None and r[0] < 0.07


def gercek_plan(plan, kusur, cek, aday=None, aday_sirali=False):
    """Nominal plandan sahnedeki GERÇEK plan. Döner: (plan, bilgi sözlüğü).

    aday (tamamlama turu): eksik / yanlış yer etiketi yalnız bu kimliklerden seçilir (deney tasarımı: kusursuz koşuda
    robotun rotada gerçekten ölçtüğü etiketler; Beyin bunu görmez). None = bütün plan (ilk dayanıklılık turu; o turda
    seçilen etiket 12 koşunun 6'sında robotun hiç görmediği bir etiketti). aday_sirali: aday listesinin kendi sırası
    (ör. en çok ölçülen önce), değilse tohumdan çekilen sıra. Yırtık seçimi aday'dan etkilenmez."""
    k = kusur
    etk = [dict(e) for e in plan["etiketler"]]
    bilgi = dict(kayip=[], yanlis=[], yirtik={})
    e_m, a_r = float(k["harita_konum_m"]), math.radians(float(k["harita_aci_derece"]))
    for e in etk:
        i = e["id"]
        yaw = e["yaw"]
        rx, ry = math.sin(yaw), -math.cos(yaw)              # duvar boyunca (bakana göre sağ)
        if e_m:
            t = e_m * cek.u_t[i]
            e["x"] += t * rx
            e["y"] += t * ry
            e["z"] += e_m * cek.u_z[i]
        if a_r:
            d = a_r * cek.u_a[i]
            ileri = e["boy_m"] / 2.0 * 10.0 / 8.0 * abs(math.sin(d)) + 0.0005
            e["x"] += ileri * math.cos(yaw)
            e["y"] += ileri * math.sin(yaw)
            e["yaw"] = yaw + d
    sira = [i for i in cek.sira if any(e["id"] == i for e in etk)]
    if aday is None:
        sira_ky = sira
    elif aday_sirali:
        sira_ky = [i for i in aday if i in sira]
    else:
        ad = set(aday)
        sira_ky = [i for i in sira if i in ad]
    kayip = set(sira_ky[:int(k["kayip_etiket"])])
    bilgi["kayip"] = sorted(kayip)
    if int(k["yanlis_yer"]):
        h = E._harita(plan["koridor"])
        kalan = int(k["yanlis_yer"])
        for i in sira_ky[int(k["kayip_etiket"]):]:
            if kalan <= 0:
                break
            e = next(x for x in etk if x["id"] == i)
            rx, ry = math.sin(e["yaw"]), -math.cos(e["yaw"])
            for s in (cek.s_yer, -cek.s_yer):
                nx, ny = e["x"] + s * k["yanlis_yer_m"] * rx, e["y"] + s * k["yanlis_yer_m"] * ry
                if _duvarda(h, nx, ny, e["yaw"]):
                    e["x"], e["y"] = nx, ny
                    bilgi["yanlis"].append(i)
                    kalan -= 1
                    break
    if float(k["yirtik_oran"]) > 0:
        n = int(round(float(k["yirtik_oran"]) * len(etk)))
        for i in [x for x in sira if x not in kayip][:n]:
            bilgi["yirtik"][i] = (float(k["yirtik_boy"]), int(cek.kose[i]))
    etk = [e for e in etk if e["id"] not in kayip]
    p = dict(plan, etiketler=etk, sayi=len(etk))
    return p, bilgi


# ------------------------------------------------------------------ yırtık doku
def yirtik_doku_yolu(kimlik, boy, kose):
    import cv2
    os.makedirs(_yol.ONBELLEK, exist_ok=True)
    yol = os.path.join(_yol.ONBELLEK, "tag36h11_v2_%03d_y%02d_%d.png" % (int(kimlik), round(boy * 100), int(kose)))
    if not os.path.exists(yol):
        im = E.etiket_resmi(kimlik).copy()
        h = E.HUCRE_PX
        s = int(round(h + boy * 8 * h))
        N = im.shape[0]
        ys = slice(0, s) if kose in (0, 1) else slice(N - s, N)
        xs = slice(0, s) if kose in (0, 3) else slice(N - s, N)
        im[ys, xs] = DUVAR_GRI
        im = np.ascontiguousarray(im[::-1])             # MuJoCo satırları ters kaplar (etiket.doku_yolu ile aynı)
        ok, buf = cv2.imencode(".png", cv2.cvtColor(im, cv2.COLOR_GRAY2BGR))
        with open(yol, "wb") as f:
            f.write(buf.tobytes())
    return yol


def kusurlu_sahne(kor, plan_gercek, bilgi):
    """etiket.etiketli_sahne + yırtık dokular (dunya.VARLIK içinde dosya yolu değişimi)."""
    import dunya as D
    s = E.etiketli_sahne(kor, plan_gercek)
    v = D.VARLIK
    for i, (boy, kose) in bilgi["yirtik"].items():
        eski = 'file="%s"' % E.doku_yolu(i).replace("\\", "/")
        yeni = 'file="%s"' % yirtik_doku_yolu(i, boy, kose).replace("\\", "/")
        v = v.replace(eski, yeni)
    D.VARLIK = v
    return s


# ------------------------------------------------------------------ algılayıcı
class KusurluAlgilayici(Algilayicilar):
    def __init__(self, dz, mercek, cozunurluk, tohum, kusur, plan_gercek, cek, **k):
        ku = kusur_tam(kusur)
        poz = ku["pozlama_s"] if ku["pozlama_s"] else KM.POZLAMA_S
        super().__init__(dz, mercek, cozunurluk, tohum=tohum, pozlama_s=poz, **k)
        self.ku = ku
        self.krng = np.random.default_rng(424243 + int(tohum))
        self.K_gercek = self.K.copy()
        if ku["odak_orani"]:
            self.K = self.K.copy()
            f = 1.0 + cek.s_odak * float(ku["odak_orani"])
            self.K[0, 0] *= f
            self.K[1, 1] *= f
        if ku["egim_derece"]:
            import mujoco
            m = dz.w.m
            d = math.radians(cek.s_egim * float(ku["egim_derece"]))
            q = np.array(m.cam_quat[self.kam.cam], float)
            qx = np.array([math.cos(d / 2), math.sin(d / 2), 0.0, 0.0])
            res = np.zeros(4)
            mujoco.mju_mulQuat(res, q, qx)
            m.cam_quat[self.kam.cam] = res
        self.etk = [dict(e, kose=KM.etiket_koseleri(e)) for e in plan_gercek["etiketler"]]
        self._kuyruk = []
        self._simdi = -1e9
        self._ortu = {e["id"]: None for e in self.etk}
        self._parl = {e["id"]: None for e in self.etk}
        self._gorunur_sure = 0.0
        self.dusen = 0
        self.ortu_kare = 0
        self.parl_kare = 0

    # iki durumlu süreç: None = kapalı, aksi halde bölüm parametresi
    def _surec(self, durum, p, dt, yeni):
        if p <= 0:
            return {k: None for k in durum}
        out = {}
        for k, v in durum.items():
            if v is None:
                ac = self.krng.uniform() < (p / max(1e-6, 1.0 - p)) * dt / BOLUM_S
                out[k] = yeni() if ac else None
            else:
                out[k] = None if self.krng.uniform() < dt / BOLUM_S else v
        return out

    def _bolum_ilk(self, p, yeni):
        return {e["id"]: (yeni() if (p > 0 and self.krng.uniform() < p) else None) for e in self.etk}

    def _goruntu_kusur(self, g):
        ku = self.ku
        if ku["ortulme"] <= 0 and ku["parlama"] <= 0:
            return g
        cp, cR = self.kam.poz()
        W, H = g.shape[1], g.shape[0]
        out = None
        for e in self.etk:
            o, pl = self._ortu.get(e["id"]), self._parl.get(e["id"])
            if o is None and pl is None:
                continue
            n = np.array([math.cos(e["yaw"]), math.sin(e["yaw"]), 0.0])
            c = np.array([e["x"], e["y"], e["z"]])
            if float(np.dot(cp - c, n)) <= 0 or np.linalg.norm(cp - c) > 9.0:
                continue
            uv, z = KM.izdusur(self.K_gercek, cp, cR, e["kose"])
            if (z < 0.2).any():
                continue
            u0, v0 = uv.min(0)
            u1, v1 = uv.max(0)
            if u1 < 0 or v1 < 0 or u0 >= W or v0 >= H:
                continue
            # beyaz pay dahil kutu (siyah kare x 10/8)
            cu, cv = (u0 + u1) / 2, (v0 + v1) / 2
            hu, hv = (u1 - u0) / 2 * 1.25, (v1 - v0) / 2 * 1.25
            u0, u1, v0, v1 = cu - hu, cu + hu, cv - hv, cv + hv
            if out is None:
                out = g.astype(np.float32)
            if pl is not None:
                a, b = pl
                pu, pv = cu + a * hu * 0.6, cv + b * hv * 0.6
                r = max(1.5, 0.25 * 2 * hu)
                x0, x1 = int(max(0, pu - 3 * r)), int(min(W, pu + 3 * r + 1))
                y0, y1 = int(max(0, pv - 3 * r)), int(min(H, pv + 3 * r + 1))
                if x1 > x0 and y1 > y0:
                    yy, xx = np.mgrid[y0:y1, x0:x1]
                    out[y0:y1, x0:x1] += float(ku["parlama_genlik"]) * np.exp(-((xx - pu) ** 2 + (yy - pv) ** 2) / (2 * r * r))
                    self.parl_kare += 1
            if o is not None:
                f = float(ku["ortulme_kesir"])
                if o == 0:      # soldan
                    box = (u0, v0, u0 + f * 2 * hu, v1)
                elif o == 1:    # sağdan
                    box = (u1 - f * 2 * hu, v0, u1, v1)
                else:           # alttan
                    box = (u0, v1 - f * 2 * hv, u1, v1)
                x0, y0 = int(max(0, box[0])), int(max(0, box[1]))
                x1, y1 = int(min(W, box[2] + 1)), int(min(H, box[3] + 1))
                if x1 > x0 and y1 > y0:
                    out[y0:y1, x0:x1] = 90.0
                    self.ortu_kare += 1
        if out is None:
            return g
        return np.clip(out, 0, 255).astype(np.uint8)

    def olay(self, dz, t):
        import time
        ku = self.ku
        self._simdi = t
        self.sonar = self._sonar()
        yaw = self._kamera_yaw()
        if self._cam_yaw is not None and t > self._cam_t:
            self.cam_hiz = (math.atan2(math.sin(yaw - self._cam_yaw), math.cos(yaw - self._cam_yaw))) / (t - self._cam_t)
        self._cam_yaw, self._cam_t = yaw, t
        if t - self._son_kare_t >= self.kare_aralik - 1e-6:
            t0 = time.perf_counter()
            dt = self.kare_aralik if self._son_kare_t > -1e8 else 0.0
            self._son_kare_t = t
            if dt == 0.0:
                self._ortu = self._bolum_ilk(ku["ortulme"], lambda: int(self.krng.integers(0, 3)))
                self._parl = self._bolum_ilk(ku["parlama"], lambda: tuple(self.krng.uniform(-1, 1, 2)))
            else:
                self._ortu = self._surec(self._ortu, ku["ortulme"], dt, lambda: int(self.krng.integers(0, 3)))
                self._parl = self._surec(self._parl, ku["parlama"], dt, lambda: tuple(self.krng.uniform(-1, 1, 2)))
            g = self.kam.gri()
            g = self._goruntu_kusur(g)
            b = self.bozulma
            isik = b.get("isik", 1.0)
            poz = min(0.033, self.pozlama_s / isik) if isik < 1 else self.pozlama_s
            wy, wp = self.cam_hiz, 0.0
            if ku["titresim"]:
                wy += float(self.krng.normal(0, ku["titresim"]))
                wp = float(self.krng.normal(0, ku["titresim"]))
            gb = KM.boz(g, self.rng, isik=isik, okuma_gurultu=b.get("okuma_gurultu", 2.0),
                        bulanik_px=math.hypot(wy, wp) * poz * self.K_gercek[0, 0], bulanik_aci=math.atan2(wp, wy) if wp else 0.0)
            self.kare_sayisi += 1
            self.kare_ms.append((time.perf_counter() - t0) * 1000.0)
            if ku["kare_dusme"] and self.krng.uniform() < ku["kare_dusme"]:
                self.dusen += 1
                return
            self._kuyruk.append((t + float(ku["gecikme_s"]), (t, gb)))

    def kare_al(self):
        k = None
        while self._kuyruk and self._kuyruk[0][0] <= self._simdi + 1e-9:
            k = self._kuyruk.pop(0)[1]
        return k
