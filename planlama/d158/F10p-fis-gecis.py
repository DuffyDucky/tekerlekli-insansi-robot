# F10p: boyun tuneli fis gecis analizi (yalniz analiz; tasarim degismez).
# Girdi: tasarim/freecad/kafa/stl/boyun-tunel-deneme.stl (kablo yolu gercek tunelle ayni, F10o-kontrol.md).
# Yontem: STL -> 0,25 mm voksel (y yonunde isin paritesi). Fis = kati dikdortgen prizma (genislik w x ekseninde,
# kalinlik t, rijit boy L). Durum uzayi: (x0, y, z, egim theta) -- x0 = fisin x'teki sol kenari, theta = boy ekseninin
# y-z duzlemindeki acisi. Her (x0, theta) icin bos alan, fis dikdortgeniyle FFT korelasyonuyla asindirilir (C-uzayi);
# erisilebilirlik eksen boyunca serit doldurmayla bulunur. Baslangic: alt cikisin arkasinda yatay (+z) fis;
# hedef: fisin tamami mil icinde y > 64 (mil penceresinin ustu; oradan duz boru).
# Kullanim (depo kokunden): python planlama/d158/F10p-fis-gecis.py [--parca=k/N] [--yalniz-dogrula]
import sys, struct, math, json, time
import numpy as np

STL = "tasarim/freecad/kafa/stl/boyun-tunel-deneme.stl"
H = 0.25                                   # voksel (mm)
X0, X1 = -20.0, 20.0                       # parca kutusu (kaynak koordinati, boyun-tunel-deneme.json kutu_mm)
YB0, YB1 = 3.0, 96.0
ZB0, ZB1 = -31.0, 20.0
YD0, YD1 = -10.0, 110.0                    # analiz alani (kutu disi uzatma)
ZD0, ZD1 = -80.0, 20.0
CS = 2                                     # C-uzayi alt ornekleme (2 x 0,25 = 0,5 mm)
DTH = 2.0                                  # egim adimi (derece)


def oku_stl(yol):
    raw = open(yol, "rb").read()
    n = struct.unpack("<I", raw[80:84])[0]
    a = np.frombuffer(raw[84:84 + n * 50], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("x", "<u2")]))
    T = a["v"].astype(np.float64)
    S = np.empty_like(T)                   # STL (X, Y, Z) -> kaynak (x, y, z) = (X, Z + 3, -Y)  (stl_olc2 ile ayni)
    S[..., 0] = T[..., 0]; S[..., 1] = T[..., 2] + 3.0; S[..., 2] = -T[..., 1]
    return S


def vokselle(S):
    xs = X0 + H * (np.arange(int(round((X1 - X0) / H))) + 0.5) + 1e-4
    zs = ZB0 + H * (np.arange(int(round((ZB1 - ZB0) / H))) + 0.5) + 1e-4
    ys = YB0 + H * (np.arange(int(round((YB1 - YB0) / H))) + 0.5)
    kol, yk = [], []
    for tri in S:
        px, py, pz = tri[:, 0], tri[:, 1], tri[:, 2]
        d = (px[1] - px[0]) * (pz[2] - pz[0]) - (px[2] - px[0]) * (pz[1] - pz[0])
        if abs(d) < 1e-12:
            continue
        i0 = np.searchsorted(xs, px.min()); i1 = np.searchsorted(xs, px.max())
        k0 = np.searchsorted(zs, pz.min()); k1 = np.searchsorted(zs, pz.max())
        if i1 <= i0 or k1 <= k0:
            continue
        gx, gz = np.meshgrid(xs[i0:i1], zs[k0:k1], indexing="ij")
        l1 = ((px[1] - gx) * (pz[2] - gz) - (px[2] - gx) * (pz[1] - gz)) / d
        l2 = ((px[2] - gx) * (pz[0] - gz) - (px[0] - gx) * (pz[2] - gz)) / d
        l3 = 1 - l1 - l2
        m = (l1 >= 0) & (l2 >= 0) & (l3 >= 0)
        if not m.any():
            continue
        yv = l1 * py[0] + l2 * py[1] + l3 * py[2]
        ii, kk = np.nonzero(m)
        kol.append((ii + i0) * len(zs) + (kk + k0)); yk.append(yv[m])
    kol = np.concatenate(kol); yk = np.concatenate(yk)
    o = np.lexsort((yk, kol)); kol = kol[o]; yk = yk[o]
    dolu = np.zeros((len(xs), len(ys), len(zs)), bool)
    tek = 0
    sinir = np.flatnonzero(np.diff(np.r_[-1, kol, -2]))
    for a, b in zip(sinir[:-1], sinir[1:]):
        c = kol[a]; v = yk[a:b]
        if len(v) % 2:
            tek += 1; continue
        i, k = divmod(int(c), len(zs))
        for y0, y1 in zip(v[0::2], v[1::2]):
            j0 = np.searchsorted(ys, y0); j1 = np.searchsorted(ys, y1)
            dolu[i, j0:j1, k] = True
    return xs, ys, zs, dolu, tek


def alan(xs, ys, zs, dolu):
    """Uzatilmis alan: bos[x, y, z]. Kutu ici STL; z < -31 (alt cikisin arkasi) bos varsayim; y > 96 mil (r < 15,98)
    devam eder; kutu yanlari (x +-20) ve tabani kapali sayilir (temkinli)."""
    yd = YD0 + H * (np.arange(int(round((YD1 - YD0) / H))) + 0.5)
    zd = ZD0 + H * (np.arange(int(round((ZD1 - ZD0) / H))) + 0.5)
    bos = np.zeros((len(xs), len(yd), len(zd)), bool)
    bos[:, :, zd < ZB0] = True
    j0 = int(round((YB0 - YD0) / H)); k0 = int(round((ZB0 - ZD0) / H))
    bos[:, j0:j0 + len(ys), k0:k0 + len(zs)] = ~dolu
    # yalniz gercek kablo yolu (boyun_tunel_deneme.py:93-95 YOL) + parcanin arkasi (z < -30) bos sayilir;
    # yol disindaki parca disi hava / kutu kesimi kullanilmaz
    X = xs[:, None, None]; Y = yd[None, :, None]; Z = zd[None, None, :]
    R = np.sqrt(X ** 2 + Z ** 2)
    kx = (X > -14.0) & (X < 6.0)
    yol = ((kx & (Y > 6) & (Y < 18) & (Z > -31) & (Z < -19.2)) | (kx & (Y > 6) & (Y < 46) & (Z > -27) & (Z < -10.4))
           | (kx & (Y > 44) & (Y < 49) & (Z > -27.5) & (Z < -10.4)) | ((R < 27.5) & (R > 20) & (Y > 46) & (Y < 62))
           | ((X > -10) & (X < 10) & (Y > 53) & (Y < 63) & (Z > -25) & (Z < 0)) | ((R < 16) & (Y > 52.9)))
    bos &= yol | ((Z < -30.0) & (Y < 22.0))      # alt cikisin arkasi: yalniz y < 22 bos varsayim (komsu bilinmiyor, N3)
    ust = yd > YB1
    r2 = xs[:, None] ** 2 + zd[None, :] ** 2
    bos[:, ust, :] = (r2 < 15.98 ** 2)[:, None, :]
    bos[:, :, zd < ZB0] &= (yd < 22.0)[None, :, None]
    return yd, zd, bos


def kablo_engel(bos, xs, yd, zd, serit_mm, pan=True):
    """Birikme (kaba): onceden gecmis yuvarlak kablolar +x duvarina yaslanmis serit (genislik = cap toplami);
    tunelde x in [6 - s, 6], mil penceresinde [10 - s, 10], mil icinde x > 16 - s. Pan servo kablosu (yassi 3,6 x 1,4 mm, kanal dibindeki yariktan
    alt cikisa iner): kanal / alt cikis tabaninda y 6...7,4, x -3...0,6 (yarik x ~ -1, F10o-kontrol Y1)."""
    b = bos.copy()
    if serit_mm > 0:
        mx = (xs > 6 - serit_mm) & (xs < 6 + 0.01)
        b[np.ix_(mx, (yd < 53), zd < -15)] = False                      # alt cikis, kanal, basamak, oda alti
        b[np.ix_(mx, (yd >= 53) & (yd < 66), zd < -25)] = False         # oda (pencere hizasi)
        mw = (xs > 10 - serit_mm) & (xs < 10 + 0.01)                    # mil penceresinde +x duvari x 10
        b[np.ix_(mw, (yd >= 53) & (yd < 66), (zd >= -25) & (zd < -15))] = False
        mx2 = xs > 16 - serit_mm
        b[np.ix_(mx2, yd > 50, zd >= -15)] = False
    if pan:
        b[np.ix_((xs > -3.0) & (xs < 0.6), (yd > 5.9) & (yd < 7.4), (zd > -40) & (zd < -19.2))] = False
    return b


def cekirdek(L, t, th):
    c, s = math.cos(th), math.sin(th)
    ry = abs(L / 2 * c) + abs(t / 2 * s); rz = abs(L / 2 * s) + abs(t / 2 * c)
    ny = int(math.ceil(ry / H)); nz = int(math.ceil(rz / H))
    gy, gz = np.meshgrid(np.arange(-ny, ny + 1) * H, np.arange(-nz, nz + 1) * H, indexing="ij")
    u = gy * c + gz * s; v = -gy * s + gz * c
    return ((np.abs(u) <= L / 2) & (np.abs(v) <= t / 2)), ny, nz


def serit_doldur(reach, free, ax, wrap=False):
    if wrap:
        n = reach.shape[ax]
        r2 = serit_doldur(np.concatenate([reach, reach], ax), np.concatenate([free, free], ax), ax)
        a, b = np.split(r2, 2, axis=ax)
        return a | b
    n = reach.shape[ax]
    sh = [1] * reach.ndim; sh[ax] = n
    pos = np.arange(n, dtype=np.int16).reshape(sh)
    out = np.zeros_like(reach)
    for ters in (False, True):
        f = np.flip(free, ax) if ters else free
        r = np.flip(reach, ax) if ters else reach
        lb = np.maximum.accumulate(np.where(~f, pos, np.int16(-1)), axis=ax)
        lr = np.maximum.accumulate(np.where(r & f, pos, np.int16(-1)), axis=ax)
        g = f & (lr > lb)
        out |= np.flip(g, ax) if ters else g
    return out


def gecis(bos, xs, yd, zd, w, t, L, x0_adim=1.0):
    """Doner kati kutu icin erisilebilirlik. Doner: (gecer, en_yuksek_alt_uc_y, takilma_ozeti)."""
    x0s = list(np.arange(-13.95, 9.95 - w + 1e-6, x0_adim)) or [-13.95]   # kanal sol duvari (x -14) ... mil penceresi sag kenari (x 10)
    ths = np.radians(np.arange(-90.0, 90.0, DTH))
    ny, nz = bos.shape[1], bos.shape[2]
    sh = (ny, nz)
    C = np.zeros((len(x0s), len(ths), (ny + CS - 1) // CS, (nz + CS - 1) // CS), bool)
    K = []
    for th in ths:
        k, ky, kz = cekirdek(L, t, th)
        Kf = np.zeros(sh); Kf[:k.shape[0], :k.shape[1]] = k
        K.append((np.fft.rfft2(Kf), ky, kz, k.sum()))
    for a, x0 in enumerate(x0s):
        m = (xs + H / 2 > x0) & (xs - H / 2 < x0 + w)
        F = bos[m].all(axis=0)
        O = np.fft.rfft2((~F).astype(float))
        for b, (Kh, ky, kz, ks) in enumerate(K):
            cor = np.fft.irfft2(O * np.conj(Kh), s=sh)          # cor[i,j] = sum O[i+p, j+q] K[p,q]
            cor = np.roll(cor, (ky, kz), axis=(0, 1))          # merkeze kaydir
            ok = cor < 0.5
            ok[:ky + 1, :] = False; ok[-ky - 1:, :] = False; ok[:, :kz + 1] = False; ok[:, -kz - 1:] = False
            C[a, b] = ok[::CS, ::CS]
    yc = yd[::CS]; zc = zd[::CS]
    # baslangic: yatay (theta = +-90), fisin tamami z < -31.5, merkez y alt cikis (6...18) icinde
    R = np.zeros_like(C)
    bth = [int(np.argmin(np.abs(np.degrees(ths) - (-90.0))))]
    st_y = (yc > 6 + t / 2) & (yc < 18 - t / 2)
    st_z = zc < -31.5 - L / 2
    for bi in bth:
        ix = np.ix_(np.arange(len(x0s)), [bi], np.flatnonzero(st_y), np.flatnonzero(st_z))
        R[ix] = C[ix]
    for _ in range(200):
        once = R.sum()
        R = serit_doldur(R, C, 2); R = serit_doldur(R, C, 3)
        R = serit_doldur(R, C, 1, wrap=True); R = serit_doldur(R, C, 0)
        if R.sum() == once:
            break
    # hedef: fisin alt ucu y > 64 ve mil icinde
    a_i, b_i, y_i, z_i = np.nonzero(R)
    if len(a_i) == 0:
        return False, None, "baslangic konumu bos degil"
    th = ths[b_i]
    alt = yc[y_i] - (np.abs(L / 2 * np.cos(th)) + np.abs(t / 2 * np.sin(th)))
    gecer = bool(((alt > 64.0) & (np.abs(zc[z_i]) < 6.0)).any())      # mil icinde (eksene yakin) ve pencerenin ustunde
    ust = yc[y_i] + (np.abs(L / 2 * np.cos(th)) + np.abs(t / 2 * np.sin(th)))
    on = zc[z_i] + (np.abs(L / 2 * np.sin(th)) + np.abs(t / 2 * np.cos(th)))
    return gecer, (float(alt.max()), float(ust.max()), float(on.max())), None


def tmax(bos, xs, yd, zd, w, L, lo=1.0, hi=12.0, adim=0.25):
    if not gecis(bos, xs, yd, zd, w, lo, L)[0]:
        return None
    while hi - lo > adim:
        m = (lo + hi) / 2
        if gecis(bos, xs, yd, zd, w, m, L)[0]:
            lo = m
        else:
            hi = m
    return lo


def main():
    t0 = time.time()
    S = oku_stl(STL)
    xs, ys, zs, dolu, tek = vokselle(S)
    yd, zd, bos = alan(xs, ys, zs, dolu)
    sonuc = {"voksel_mm": H, "tek_parite_kolon": tek, "C_uzayi_mm": H * CS, "egim_adimi_derece": DTH}
    # dogrulama: bilinen olculer (boyun-tunel-deneme.json olcu)
    def bos_aralik(x, y):
        i = np.argmin(np.abs(xs - x)); j = np.argmin(np.abs(yd - y))
        idx = np.flatnonzero(bos[i, j] & (zd > -30))
        if len(idx) == 0:
            return None
        par = np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1)
        return [[round(float(zd[p[0]]) - H / 2, 2), round(float(zd[p[-1]]) + H / 2, 2)] for p in par]
    sonuc["dogrulama"] = {"kanal_z_y30_x-4": bos_aralik(-4, 30), "oda_z_y56_x0": bos_aralik(0, 56),
                          "pencere_y58_x0": bos_aralik(0, 58), "basamak_y45_x0": bos_aralik(0, 45),
                          "basamak_y48.5_x0": bos_aralik(0, 48.5)}
    print(json.dumps(sonuc, ensure_ascii=True), flush=True)
    if "--yalniz-dogrula" in sys.argv:
        return
    # fis olculeri VARSAYIM (F10p-fis-gecis-analizi.md tablo 1); serit = once gecmis kablolarin cap toplami (+x duvarinda)
    U03 = [("U03 metal kabuk (kalipsiz alt sinir)", 12.0, 4.5, 14.0), ("U03 ince kalip", 12.5, 5.5, 25.0),
           ("U03 sart ustu", 13.0, 7.0, 30.0), ("U03 tipik kalip", 16.0, 8.0, 35.0)]
    H02 = [("H02 metal uc (kalipsiz alt sinir)", 6.4, 2.8, 8.0), ("H02 ince kalip", 10.0, 4.5, 18.0),
           ("H02 tipik kalip", 11.5, 6.0, 24.0), ("H02 sart ustu", 18.0, 7.0, 30.0)]
    S10 = [("S10 Dupont 3 pin", 7.6, 2.6, 14.0), ("S10 JR 3 pin", 8.0, 3.6, 15.0), ("S10 ust", 8.5, 4.5, 17.0)]
    isler = [("fis", f, s_, True) for grup, s_ in ((U03, 0.0), (H02, 4.5), (S10, 10.5)) for f in grup]
    isler += [("fis", U03[0], 0.0, False), ("fis", H02[0], 0.0, False), ("fis", H02[1], 0.0, False), ("fis", S10[1], 0.0, False),
              ("fis", S10[0], 0.0, False), ("fis", S10[0], 4.5, True)]
    for w, t, L in ((8.0, 3.0, 15.0), (8.0, 4.0, 15.0), (8.0, 5.0, 15.0), (13.0, 3.0, 15.0), (13.0, 3.5, 15.0),
                    (13.0, 4.0, 15.0), (13.0, 3.0, 30.0), (6.0, 3.5, 20.0)):
        isler.append(("fis", ("sinir", w, t, L), 0.0, True))
    k, N = 0, 1
    for a in sys.argv[1:]:
        if a.startswith("--parca="):
            k, N = map(int, a.split("=")[1].split("/"))
    for n, (tur, (ad, w, t, L), serit, birik) in enumerate(isler):
        if n % N != k:
            continue
        b = kablo_engel(bos, xs, yd, zd, serit, pan=birik)
        r = {"tur": tur, "ad": ad, "w": w, "t": t, "L": L, "birikme": birik, "serit_mm": serit}
        if tur == "fis":
            g, uc, hata = gecis(b, xs, yd, zd, w, t, L)
            r.update(gecer=g, hata=hata, alt_uc_en_y=None if uc is None else round(uc[0], 2),
                     ust_uc_en_y=None if uc is None else round(uc[1], 2), on_uc_en_z=None if uc is None else round(uc[2], 2))
        r["s"] = round(time.time() - t0)
        print(json.dumps(r, ensure_ascii=True), flush=True)


if __name__ == "__main__":
    main()
