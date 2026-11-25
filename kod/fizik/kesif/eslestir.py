"""Tarama-harita eşleştirme: odometri önseli + kaba ilintisel arama (Olson 2009 hilesi) + Gauss-Newton inceltme.

Amaç (en küçüklenen, "nat"):
    E(p) = us * sum_i min(d_i(p), d_maks)^2 / (2 sigma^2) + 1/2 (p - p0)^T Omega (p - p0)
  d_i(p): i. tarama noktasının (gövde çerçevesinde b_i, poz p = (x, y, th) ile haritaya konunca) en yakın dolu
  hücreye uzaklığı (UzaklikAlani, çift doğrusal). d_maks'ta kırpma = sağlam (robust) kesme: yeni görülen duvar ya da
  haritada olmayan engel eşleşmeyi çekmez. Önsel terim odometri tahmini p0 ve bilgisi Omega: koridor boyunca tarama
  bilgi taşımadığında (Hessian'ın o yöndeki özdeğeri ~0) çözümü odometri belirler ("odometriye yaslanma").
Kaba arama: açı ± (3° + 0,15 |Δθ_odo|) (en çok ±20°), 0,5° adım; öteleme ±0,15 m, 1 hücre adım (her açı için nokta
hücreleri bir kez hesaplanır, ötelemeler tamsayı kaydırma). Aynı amacın (önsel dahil) en iyisi GN'nin başlangıcıdır.
"""

import math
from dataclasses import dataclass

import numpy as np


@dataclass
class EslestirmeAyari:
    sigma: float = 0.05            # m, nokta-yüzey uzaklığı std (gürültü 1 cm + 15 mm yuvarlama + 5 cm hücre)
    us: float = 0.5                # komşu ışınlar bağımsız değil: tavlama
    d_maks: float = 0.15           # m, kesme (uzaklık alanı da burada kırpılır). 0,30 -> 0,15: 9x9 sınamasında poz
                                   # hatası maks 0,3-1,3 m -> 0,06-0,21 m (yakın ama yanlış duvar eşleşmeyi çekmesin)
    nokta_sayisi: int = 180        # eşleştirmede kullanılan nokta
    kaba: bool = True
    kaba_oteleme_m: float = 0.15
    kaba_aci_taban_der: float = 3.0
    kaba_aci_oran: float = 0.15
    kaba_aci_maks_der: float = 20.0
    kaba_aci_adim_der: float = 0.5
    gn_tur: int = 8
    inlier_m: float = 0.08


@dataclass
class EslestirmeSonucu:
    poz: tuple
    kalite: float                  # eşleşen (d < inlier_m) / alan içindeki nokta
    eslesebilir: float             # d < d_maks olanların oranı (harita bu noktaları tanıyor mu)
    nokta: int
    H_tarama: np.ndarray           # 3x3, tarama teriminin Hessian'ı (bilgi)
    oz_min: float                  # H_tarama ötelemesinin en küçük özdeğeri (yozlaşma göstergesi)
    duzeltme: tuple                # (dx, dy, dth) = sonuç - önsel
    enerji: float


def _sar(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def noktalari_sec(bx, by, n, rng=None):
    """Eşit aralıklı alt örnek (tarama sırası açıya göre olduğu için açıda düzgün)."""
    m = bx.size
    if m <= n:
        return bx, by
    sec = np.linspace(0, m - 1, n).round().astype(np.int64)
    return bx[sec], by[sec]


def eslestir(alan, bx, by, onsel, omega, ayar=None, dth_odo=0.0):
    """alan: UzaklikAlani; bx, by: gövde çerçevesinde tarama noktaları (çarpıklığı giderilmiş); onsel: (x, y, th);
    omega: 3x3 önsel bilgi matrisi. -> EslestirmeSonucu."""
    a = ayar or EslestirmeAyari()
    bx, by = noktalari_sec(np.asarray(bx, float), np.asarray(by, float), a.nokta_sayisi)
    p0 = np.array(onsel, dtype=float)
    k = a.us / (a.sigma ** 2)
    p = p0.copy()
    if a.kaba:
        p = _kaba_arama(alan, bx, by, p0, omega, a, k, dth_odo)
    H_tarama = np.zeros((3, 3))
    for _ in range(a.gn_tur):
        c, s = math.cos(p[2]), math.sin(p[2])
        px = p[0] + c * bx - s * by
        py = p[1] + s * bx + c * by
        d, gx, gy, ic = alan.deger_egim(px, py)
        w = (d < a.d_maks * 0.95) & ic
        jx = gx
        jy = gy
        jt = gx * (-s * bx - c * by) + gy * (c * bx - s * by)
        J = np.stack([jx, jy, jt], axis=1)[w]
        r = d[w]
        H_tarama = k * (J.T @ J)
        dp = p - p0
        dp[2] = _sar(dp[2])
        g = k * (J.T @ r) + omega @ dp
        H = H_tarama + omega + np.eye(3) * 1e-6
        try:
            adim = -np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            break
        # adım sınırı (kesme yüzünden yerel modelin geçerli olduğu bölge)
        n_t = math.hypot(adim[0], adim[1])
        if n_t > 0.10:
            adim[:2] *= 0.10 / n_t
        adim[2] = max(-0.05, min(0.05, adim[2]))
        p = p + adim
        if n_t < 1e-4 and abs(adim[2]) < 1e-4:
            break
    c, s = math.cos(p[2]), math.sin(p[2])
    px = p[0] + c * bx - s * by
    py = p[1] + s * bx + c * by
    d, _, _, ic = alan.deger_egim(px, py)
    n_ic = max(int(ic.sum()), 1)
    kalite = float(((d < a.inlier_m) & ic).sum()) / n_ic
    eslesebilir = float(((d < a.d_maks * 0.95) & ic).sum()) / n_ic
    dp = p - p0
    dp[2] = _sar(dp[2])
    enerji = float(k * 0.5 * np.minimum(d, a.d_maks) @ np.minimum(d, a.d_maks) + 0.5 * dp @ omega @ dp)
    try:
        oz_min = float(np.linalg.eigvalsh(H_tarama[:2, :2])[0])
    except np.linalg.LinAlgError:
        oz_min = 0.0
    p[2] = _sar(p[2])
    return EslestirmeSonucu(poz=(float(p[0]), float(p[1]), float(p[2])), kalite=kalite, eslesebilir=eslesebilir,
                            nokta=int(bx.size), H_tarama=H_tarama, oz_min=oz_min,
                            duzeltme=(float(dp[0]), float(dp[1]), float(dp[2])), enerji=enerji)


def _kaba_arama(alan, bx, by, p0, omega, a, k, dth_odo):
    c0 = alan.coz
    pen = min(math.radians(a.kaba_aci_taban_der) + a.kaba_aci_oran * abs(dth_odo), math.radians(a.kaba_aci_maks_der))
    adim = math.radians(a.kaba_aci_adim_der)
    na = int(math.ceil(pen / adim))
    acilar = p0[2] + np.arange(-na, na + 1) * adim
    nt = int(round(a.kaba_oteleme_m / c0))
    kay = np.arange(-nt, nt + 1)
    # amaç tablosu: hücre başına -min(d, dmaks)^2 k / 2 (kenar payı nt hücre, dışarısı d_maks)
    pay = nt + 2
    dm = np.minimum(alan.d, a.d_maks)
    tablo = np.full((alan.nx + 2 * pay, alan.ny + 2 * pay), a.d_maks, dtype=np.float32)
    tablo[pay:pay + alan.nx, pay:pay + alan.ny] = dm
    tablo = (0.5 * k) * tablo.astype(np.float64) ** 2
    NY = tablo.shape[1]
    flat = tablo.ravel()
    c = np.cos(acilar)[:, None]
    s = np.sin(acilar)[:, None]
    px = p0[0] + c * bx[None, :] - s * by[None, :]        # (A, N)
    py = p0[1] + s * bx[None, :] + c * by[None, :]
    i = np.floor((px - alan.x0) / c0).astype(np.int64) + pay
    j = np.floor((py - alan.y0) / c0).astype(np.int64) + pay
    i = np.clip(i, nt, tablo.shape[0] - nt - 1)
    j = np.clip(j, nt, NY - nt - 1)
    taban = i * NY + j                                      # (A, N)
    DI, DJ = np.meshgrid(kay, kay, indexing="ij")
    ofs = (DI * NY + DJ).ravel()                            # (T,)
    E = flat[taban[:, :, None] + ofs[None, None, :]].sum(axis=1)   # (A, T)
    # önsel terim
    dx = (DI.ravel() * c0)[None, :]
    dy = (DJ.ravel() * c0)[None, :]
    dt = (acilar - p0[2])[:, None]
    E = E + 0.5 * (omega[0, 0] * dx * dx + omega[1, 1] * dy * dy + omega[2, 2] * dt * dt
                   + 2 * omega[0, 1] * dx * dy + 2 * omega[0, 2] * dx * dt + 2 * omega[1, 2] * dy * dt)
    ai, ti = np.unravel_index(int(np.argmin(E)), E.shape)
    return np.array([p0[0] + DI.ravel()[ti] * c0, p0[1] + DJ.ravel()[ti] * c0, acilar[ai]])
