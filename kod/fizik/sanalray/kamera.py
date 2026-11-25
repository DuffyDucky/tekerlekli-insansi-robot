"""Kafa kamerası: mercekler (üretici belgesi), MuJoCo görüntü üretimi, bozulmalar, AprilTag algılama ve solvePnP.

Mercekler (Raspberry Pi belgeleri, Camera Module 3 donanım tablosu; 2026-11-25'te okundu,
raspberrypi.com/documentation/accessories/camera.html):
    Camera Module 3       yatay 66°, dikey 41°, odak 4,74 mm
    Camera Module 3 Wide  yatay 102°, dikey 67°, odak 2,75 mm
    ikisi: IMX708, 4608 x 2592, 1,4 µm, 6,45 x 3,63 mm (16:9); video kipleri 2304 x 1296p56, 1536 x 864p120.
MuJoCo iğne deliği kamerası `fovy` = dikey görüş açısı ve kare piksel kullanır: 16:9 görüntüde yatay açı standartta
67,2° (belge 66°), genişte 99,4° (belge 102°; farkı geniş merceğin bozulması, burada YOK: gerçekte kalibrasyon ve
düzeltme gerekir, kenarda çözünürlük kaybı modellenmedi).

İşleme çözünürlüğü (VARSAYIM, Pi 5): sensör 1536 x 864 kipinde (2x2 birleştirme, tam görüş alanı) okunur, ISP aynı ya
da küçültülmüş boyutta verir; algılama 768 x 432, 1152 x 648 ya da 1536 x 864'te. Görünürlük haritasında
(gorunurluk.py) görüntü 1536 x 864'te üretilip INTER_AREA ile küçültülür (ISP ölçeklemesine yakın); navigasyonda
(algilayici.py) görüntü doğrudan işleme çözünürlüğünde üretilir."""

import math

import numpy as np

MERCEK_KAYNAK = "raspberrypi.com/documentation/accessories/camera.html (Camera Module 3 donanım tablosu, 2026-11-25)"
MERCEKLER = {
    "std": dict(ad="Camera Module 3", yatay_fov_derece=66.0, dikey_fov_derece=41.0, odak_mm=4.74),
    "genis": dict(ad="Camera Module 3 Wide", yatay_fov_derece=102.0, dikey_fov_derece=67.0, odak_mm=2.75),
}
COZUNURLUKLER = {"768x432": (768, 432), "1152x648": (1152, 648), "1536x864": (1536, 864)}
POZLAMA_S = 0.010          # VARSAYIM: aydınlık koridorda otomatik pozlama ≈ 1/100 s; loş ışıkta uzar (bozulma)


def ic_parametre(mercek, W, H):
    """K matrisi (iğne deliği; MuJoCo: fovy dikey, kare piksel, asal nokta görüntü ortası)."""
    fovy = math.radians(MERCEKLER[mercek]["dikey_fov_derece"])
    f = (H / 2.0) / math.tan(fovy / 2.0)
    return np.array([[f, 0, W / 2.0], [0, f, H / 2.0], [0, 0, 1.0]])


def yatay_fov_iğne(mercek, W=16, H=9):
    fovy = math.radians(MERCEKLER[mercek]["dikey_fov_derece"])
    return math.degrees(2 * math.atan(W / H * math.tan(fovy / 2)))


# ------------------------------------------------------------------ görüntü üretimi
class Kamera:
    """Modeldeki bir kameradan gri görüntü. Robotun kendi görsel ağları (grup 1) çizilmez (kamera kafa kabuğunun
    8 mm gerisinde; kollar ev pozunda kameranın altında). Grup 0 (zemin) ve 2 (görsel duvar, etiket) çizilir."""

    def __init__(self, m, d, mercek="std", W=1536, H=864, kamera="kafa_kamera"):
        import mujoco
        self.mujoco = mujoco
        self.m, self.d = m, d
        self.W, self.H = W, H
        self.mercek = mercek
        m.vis.global_.offwidth = max(int(m.vis.global_.offwidth), W)
        m.vis.global_.offheight = max(int(m.vis.global_.offheight), H)
        self.cam = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_CAMERA, kamera) if isinstance(kamera, str) else int(kamera)
        if self.cam < 0:
            raise KeyError("kamera yok: %s" % kamera)
        m.cam_fovy[self.cam] = MERCEKLER[mercek]["dikey_fov_derece"]
        # aydınlatma (VARSAYIM: tavan lambalı koridor, yaygın ışık): sahnenin tek ışığı tepeden yönlü olduğu için dikey
        # duvarlar yalnız kafa ışığıyla aydınlanır ve sıyırarak bakılan yan duvarlar kararır; ortam ışığı artırılır
        m.vis.headlight.ambient[:] = (0.55, 0.55, 0.55)
        m.vis.headlight.diffuse[:] = (0.35, 0.35, 0.35)
        m.vis.headlight.specular[:] = (0.0, 0.0, 0.0)
        self.r = mujoco.Renderer(m, H, W)
        self.opt = mujoco.MjvOption()
        self.opt.geomgroup[:] = [1, 0, 1, 0, 0, 0]
        self.opt.sitegroup[:] = [0, 0, 0, 0, 0, 0]
        self.K = ic_parametre(mercek, W, H)

    def mercek_ayarla(self, mercek):
        self.mercek = mercek
        self.m.cam_fovy[self.cam] = MERCEKLER[mercek]["dikey_fov_derece"]
        self.K = ic_parametre(mercek, self.W, self.H)

    def rgb(self):
        self.r.update_scene(self.d, camera=self.cam, scene_option=self.opt)
        return self.r.render()

    def gri(self):
        import cv2
        return cv2.cvtColor(self.rgb(), cv2.COLOR_RGB2GRAY)

    def poz(self):
        """Kameranın dünya konumu ve OpenCV dönüşü (sütunlar: x sağ, y aşağı, z ileri)."""
        p = self.d.cam_xpos[self.cam].copy()
        R = self.d.cam_xmat[self.cam].reshape(3, 3) @ np.diag([1.0, -1.0, -1.0])
        return p, R

    def kapat(self):
        try:
            self.r.close()
        except Exception:
            pass


def kucult(gri, W, H):
    import cv2
    if gri.shape[1] == W and gri.shape[0] == H:
        return gri
    return cv2.resize(gri, (W, H), interpolation=cv2.INTER_AREA)


def izdusur(K, cam_p, cam_R, P):
    """Dünya noktaları (N x 3) -> piksel (N x 2), derinlik (N)."""
    Q = (np.asarray(P, float) - cam_p) @ cam_R
    z = Q[:, 2]
    u = K[0, 0] * Q[:, 0] / z + K[0, 2]
    v = K[1, 1] * Q[:, 1] / z + K[1, 2]
    return np.stack([u, v], 1), z


def etiket_koseleri(e):
    """Etiketin siyah karesinin 4 köşesi (dünya), aruco sırası: sol üst, sağ üst, sağ alt, sol alt (bakana göre)."""
    yaw = e["yaw"]
    nx, ny = math.cos(yaw), math.sin(yaw)
    rx, ry = ny, -nx
    h = e["boy_m"] / 2.0
    c = np.array([e["x"], e["y"], e["z"]])
    r = np.array([rx, ry, 0.0])
    u = np.array([0, 0, 1.0])
    return np.array([c - h * r + h * u, c + h * r + h * u, c + h * r - h * u, c - h * r - h * u])


# ------------------------------------------------------------------ bozulmalar
def bulanik(gri, uzunluk_px, aci_rad=0.0):
    """Doğrusal hareket bulanıklığı (çekirdek boyu piksel; dönüşte yatay)."""
    import cv2
    L = float(uzunluk_px)
    if L < 1.0:
        return gri
    n = int(math.ceil(L)) | 1
    k = np.zeros((n, n), np.float32)
    c = n // 2
    for i in range(4 * n):
        t = (i / (4 * n - 1) - 0.5) * L
        x, y = c + t * math.cos(aci_rad), c + t * math.sin(aci_rad)
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < n and 0 <= yi < n:
            k[yi, xi] += 1.0
    k /= k.sum()
    return cv2.filter2D(gri, -1, k, borderType=cv2.BORDER_REPLICATE)


def boz(gri, rng, isik=1.0, okuma_gurultu=2.0, atis_k=0.05, bulanik_px=0.0, bulanik_aci=0.0, parlama=None, kapanma=None):
    """Sensör bozulmaları (sırayla): hareket bulanıklığı; ışık düzeyi `isik` (1 = normal): sensöre isik x görüntü düşer,
    atış (Poisson yaklaşık, ISP gürültü azaltması sonrası: atis_k x düzey) + okuma gürültüsü eklenir, ISP 1 / isik ile
    yeniden kazanç verir (loşta gürültü büyür; VARSAYIM: normal ışıkta σ ≈ 3-4 DN, isik 0,12'de ≈ 19 DN);
    parlama = (u, v, yarıçap px, genlik): parlak leke, 255'te doyar; kapanma = [(u0, v0, u1, v1), ...] gri dikdörtgenler
    (önde duran nesne). rng: numpy Generator (gürültü tohumu). Çıktı uint8."""
    import cv2
    g = gri
    if kapanma:
        g = g.copy()
        for (u0, v0, u1, v1) in kapanma:
            cv2.rectangle(g, (int(u0), int(v0)), (int(u1), int(v1)), 90, -1)
    if bulanik_px and bulanik_px >= 1.0:
        g = bulanik(g, bulanik_px, bulanik_aci)
    y = g.astype(np.float32) * float(isik)
    if parlama is not None:
        u, v, r, A = parlama
        yy, xx = np.mgrid[0:g.shape[0], 0:g.shape[1]]
        y = y + float(A) * float(isik) * np.exp(-((xx - u) ** 2 + (yy - v) ** 2) / (2.0 * r * r)).astype(np.float32)
    sig = np.sqrt(okuma_gurultu ** 2 + atis_k * np.maximum(y, 0.0))
    n = np.empty(y.shape, np.float32)
    cv2.setRNGSeed(int(rng.integers(0, 2 ** 31 - 1)))
    cv2.randn(n, 0.0, 1.0)                           # numpy'dan ≈ 5 kat hızlı; tohum rng'den
    y = y + n * sig
    y = y / float(isik)
    return np.clip(y, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ algılama
class Bulucu:
    """OpenCV aruco (AprilTag 36h11 sözlüğü), alt piksel köşe iyileştirme; poz solvePnP IPPE_SQUARE."""

    def __init__(self, sozluk="DICT_APRILTAG_36h11", iyilestirme="subpix"):
        import cv2
        self.cv2 = cv2
        d = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, sozluk))
        p = cv2.aruco.DetectorParameters()
        p.cornerRefinementMethod = {"subpix": cv2.aruco.CORNER_REFINE_SUBPIX, "yok": cv2.aruco.CORNER_REFINE_NONE,
                                    "apriltag": cv2.aruco.CORNER_REFINE_APRILTAG}[iyilestirme]
        self.det = cv2.aruco.ArucoDetector(d, p)

    def bul(self, gri):
        koseler, kimlikler, _ = self.det.detectMarkers(gri)
        if kimlikler is None:
            return []
        return [(int(k), np.asarray(c, float).reshape(4, 2)) for k, c in zip(kimlikler.ravel(), koseler)]

    def poz(self, kose, boy_m, K):
        """Etiketin kamera çerçevesindeki pozu: (R 3x3, t 3) ya da None."""
        cv2 = self.cv2
        h = boy_m / 2.0
        obj = np.array([[-h, h, 0], [h, h, 0], [h, -h, 0], [-h, -h, 0]], float)
        ok, rv, tv = cv2.solvePnP(obj, kose.astype(float), K, None, flags=cv2.SOLVEPNP_IPPE_SQUARE)
        if not ok:
            return None
        R, _ = cv2.Rodrigues(rv)
        return R, tv.ravel()


def olcum_2b(R, t):
    """Kamera çerçevesindeki etiket pozundan yatay düzlem ölçümü: (menzil m, kerteriz rad (sol +), etiket normalinin
    kamera yönüne göre açısı psi rad). Etiket yüzüne dik bakarken psi ≈ pi."""
    f, l = float(t[2]), -float(t[0])
    n = R[:, 2]                           # aruco: etiket z ekseni etiketten dışarı (kameraya doğru)
    return math.hypot(f, l), math.atan2(l, f), math.atan2(-float(n[0]), float(n[2]))
