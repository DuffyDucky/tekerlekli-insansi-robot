# -*- coding: utf-8 -*-
"""F6b (P6.2): butun baski parcalari icin TEK baski analizi -> tasarim/freecad/lale158/baski-analiz.json

Iki kip:
  1) FreeCAD kipi (modul basina bir surec; geometri modulun *_parcalar.py'sinden, yukari yonu modulun BASKI tablosundan):
       BASKI_MODUL=<taban|kabuk|kafa|dirsek|omuz> BASKI_ARA=<ara klasor> FC_SCRIPT=<bu dosya> freecadcmd.exe run_fc.py
     -> <ara>/baski-<modul>.json. kabuk kipinde ayrica ust arka servis kapagi tanisi (eski iki yontemin katman dokumu + yuz olcumu).
  2) Birlestirme (sistem Python'u, FreeCAD istemez):  py -3 tasarim/freecad/lale158/baski_analiz_ortak.py birlestir <ara klasor>
     -> baski-analiz.json (parca listesi, toplamlar, eski modul JSON'lariyla parca parca fark, kapak tanisi).

YONTEM (her parca, her aday yon icin ayni islev `kolon_analizi`):
  - Mesh (LinearDeflection 0,1 mm, AngularDeflection 0,3 rad) baski cercevesine dondurulur (yukari -> +Z; kabuk/kafa/dirsek/taban
    analizleriyle ayni App.Rotation(yukari, Z)).
  - Dikey kolon taramasi: XY'de 0,5 mm izgara (kenar cakismasin diye kesirli kaydirma); her kolonda mesh'in butun kesisimleri
    z'ye gore sirali. Alt yuzey (normal asagi) kesisimi bir malzeme baslangicidir. Altinda hava varsa (bir onceki ust yuzey ya da
    tabla 0,3 mm'den asagida) ve yuzey yataydan 45 dereceden az egimliyse (n_z < -cos 44: 1 derece mesh toleransi) o kolon destek ister; destek kolon boyu =
    alttaki malzemenin ust yuzeyine ya da tablaya kadar. (Katman kesiti / boolean yok: eski yontemlerin kesit hatalari burada olusmaz.)
  - Kopru / ince serit kurali (eski dort yontemle ayni sayilar): destek isteyen kolonlar (i, j, 1 mm z dilimi) komsulugunda 3B
    bolgelere ayrilir (farkli yukseklikteki kucuk cikintilar XY izdusumunde birlesmesin); bolgenin XY boyu <= 15 mm ise ya da
    yaklasik 1 mm yaricapli diskle icten daraltinca hic hucre kalmiyorsa (<= 2 mm serit) serbest (kopru / kirinti) sayilir.
  - Destek filamenti = destek hacmi x DESTEK_DOLULUK (0,15, omuz_baski.py ile ayni, tahmini) x yogunluk. Parca filamenti =
    hacim x yogunluk x doluluk x 1,05 (+ destek). Sure = (hacim x doluluk + destek hacmi x 0,15) / 10 mm3/s.
    Doluluk modulun kendi degeri (tasarim girdisi, degistirilmedi): kabuk 0,90 (A.KABUK_DOLULUK), kafa parca basina doluluk_baski,
    dirsek / taban 0,80, omuz PETG-CF 0,80-0,90 (duzeltme plani M4) ve PETG 0,80.
  - X2D: tabla 246 x 246 x 250 (A.YAZICI kullanilabilir); Z etrafinda 0...90 derece donusle sigan bir yerlesim var mi.
  - YON SECME KURALI (tek kural): tasarim yonu esastir = modulun BASKI tablosundaki `yukari` (omuzda omuz_baski.py'nin yuk uyumuyla
    sectigi `secilen_yon`). Bu yon X2D'ye sigmiyorsa sigan adaylar arasindan en az destek hacimli yon alinir. Adaylar: tasarim
    yonu + parca cercevesinin 6 eksen yonu; en az destek hacimli sigan aday ayrica `en_az_destek` olarak yazilir (oneri, uygulanmaz).
Kaynak: geometri *_parcalar.py'den uretilir; ayni ada sahip FCStd nesnesinin (Tur == "Baski") hacmiyle karsilastirilir (kaynak.hacim_esit).
Tarama kaynaklarina (carpisma_kos.kaynak_listesi) ve geometriye dokunmaz; yalniz okur. Analiz kodu buraya yazildi (kafa_lib /
kabuk_montaj'daki eski katman yontemi yalniz kapak tanisi icin kopyalandi).
"""
import os, sys, json, math, time, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
FCD = os.path.dirname(HERE)                       # tasarim/freecad
KOK = os.path.normpath(os.path.join(FCD, "..", ".."))
CIKTI = os.path.join(HERE, "baski-analiz.json")

# ---------------------------------------------------------------- parametreler (tek yerde)
H = 0.5                 # mm, kolon izgarasi
JIT = (0.4865, 0.3172)  # izgara kaydirmasi (h kesri): ucgen kenarlarina denk gelmesin
ACI = 45.0              # derece, cikinti esigi
ACI_TOL = 1.0           # derece: 45 dereceye 1 dereceden yakin yuzey serbest (45 derece koni / pah mesh'te 44,x-45,x derece ucgen verir)
ZTOL = 0.3              # mm, bundan kisa hava boslugu destek sayilmaz (ilk katman / temas)
ZDILIM = 1.0            # mm, bolge ayirmada z dilimi (eski katman yontemlerindeki 1 mm katman)
KOPRU = 15.0            # mm, bu boydan kisa bolge serbest (kabuk_montaj / kafa_lib / dirsek_lib / omuz_baski ile ayni)
INCE = 1.0              # mm, 1 mm icten daraltinca kaybolan bolge (<= 2 mm serit) serbest (ayni)
DESTEK_DOLULUK = 0.15   # destek etkin dolulugu (omuz_baski.py ile ayni, tahmini)
RHO = 1.27              # g/cm3, PETG ve PETG-CF (arayuz.PETG_RHO; omuz_baski RHO)
HIZ = 10.0              # mm3/s (arayuz.PETG_HACIM_HIZI)
FIRE = 1.05             # filament = kutle x 1,05 (eski yontemlerle ayni)
X2D = (246.0, 246.0, 250.0)
MESH = (0.1, 0.3)
MODULLER = ("taban", "kabuk", "kafa", "dirsek", "omuz")
ADET2 = {"dirsek": {"Dirsek catali", "On kol govdesi", "Bilek flansi", "El"}}   # sag kol analizi, sol ayna (Y2b ile ayni)
EKSEN = {"+X": (1, 0, 0), "-X": (-1, 0, 0), "+Y": (0, 1, 0), "-Y": (0, -1, 0), "+Z": (0, 0, 1), "-Z": (0, 0, -1)}


def log(*a):
    print(*a, flush=True)


# ================================================================ cekirdek: kolon analizi (numpy; FreeCAD'siz da calisir)
def dondur_matris(yukari):
    """App.Rotation(yukari, Z) ile ayni donus (Rodrigues): yukari -> +Z."""
    import numpy as np
    u = np.array(yukari, float)
    u = u / np.linalg.norm(u)
    z = np.array([0.0, 0.0, 1.0])
    c = float(u.dot(z))
    if c > 1 - 1e-12:
        return np.eye(3)
    if c < -1 + 1e-12:                         # 180 derece: FreeCAD X ekseni etrafinda cevirir
        return np.diag([1.0, -1.0, -1.0])
    v = np.cross(u, z)
    s = np.linalg.norm(v)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K.dot(K) * ((1 - c) / (s * s))


def yerlesim(X):
    """Z etrafinda 0...90 derece: en kisa uzun kenar (kabuk/kafa yontemiyle ayni olcu) ve X2D'ye sigan bir aci var mi."""
    import numpy as np
    en, sig = None, None
    H_ = float(X[:, 2].max() - X[:, 2].min())
    for th in range(0, 91):
        c, s_ = math.cos(math.radians(th)), math.sin(math.radians(th))
        x = X[:, 0] * c - X[:, 1] * s_
        y = X[:, 0] * s_ + X[:, 1] * c
        w, h = float(x.max() - x.min()), float(y.max() - y.min())
        w, h = max(w, h), min(w, h)
        if en is None or w < en[1]:
            en = (th, w, h)
        if sig is None and w <= X2D[0] and h <= X2D[1] and H_ <= X2D[2]:
            sig = th
    return dict(olcu=[round(en[1], 1), round(en[2], 1), round(H_, 1)], tabla_aci=en[0], x2d_sigar=sig is not None, x2d_aci=sig)


def _etiketle(mask):
    """4-komsu bilesen etiketi (scipy varsa onunla)."""
    import numpy as np
    try:
        from scipy import ndimage
        lab, n = ndimage.label(mask)
        return lab, n
    except Exception:
        pass
    lab = np.zeros(mask.shape, int)
    n = 0
    nx, ny = mask.shape
    for i0, j0 in zip(*np.nonzero(mask)):
        if lab[i0, j0]:
            continue
        n += 1
        st = [(i0, j0)]
        lab[i0, j0] = n
        while st:
            i, j = st.pop()
            for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= a < nx and 0 <= b < ny and mask[a, b] and not lab[a, b]:
                    lab[a, b] = n
                    st.append((a, b))
    return lab, n


def _etiketle3(di, dj, dk):
    """Destek hucreleri (i, j, z dilimi): ayni dilimde 4-komsu ya da komsu dilimde ayni / 4-komsu hucre -> ayni bolge. Etiket 1..n."""
    import numpy as np
    anah = {}
    for t, key in enumerate(zip(di.tolist(), dj.tolist(), dk.tolist())):
        anah.setdefault(key, []).append(t)
    lab = {}
    n = 0
    for key in anah:
        if key in lab:
            continue
        n += 1
        lab[key] = n
        st = [key]
        while st:
            i, j, k = st.pop()
            for dk_ in (-1, 0, 1):
                for a, b in ((i, j), (i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                    q = (a, b, k + dk_)
                    if q != (i, j, k) and q in anah and q not in lab:
                        lab[q] = n
                        st.append(q)
    out = np.zeros(len(di), np.int64)
    for key, ts in anah.items():
        out[ts] = lab[key]
    return out


def _asindir_disk(m, r):
    """Disk (yaricap r hucre) ile asindirma: hucre, merkezine r'den yakin butun hucreler maskedeyse kalir. r = INCE/H + 0,5:
    0,5 mm izgarada 4-komsu asindirma capraz yonde 2 mm'lik seridi (or. r 20 -> 22 basamak halkasi) genis sanir; disk her yonde ~1 mm."""
    import numpy as np
    k = int(math.ceil(r))
    out = m.copy()
    nx, ny = m.shape
    for a in range(-k, k + 1):
        for b in range(-k, k + 1):
            if a * a + b * b > r * r or (a == 0 and b == 0):
                continue
            sh = np.zeros_like(m)
            xs0, xs1 = max(0, -a), min(nx, nx - a)
            ys0, ys1 = max(0, -b), min(ny, ny - b)
            sh[xs0:xs1, ys0:ys1] = m[xs0 + a:xs1 + a, ys0 + b:ys1 + b]
            out &= sh
    return out


def _asindir(m, k):
    import numpy as np
    for _ in range(k):
        e = m.copy()
        e[1:, :] &= m[:-1, :]
        e[:-1, :] &= m[1:, :]
        e[:, 1:] &= m[:, :-1]
        e[:, :-1] &= m[:, 1:]
        e[0, :] = e[-1, :] = False
        e[:, 0] = e[:, -1] = False
        m = e
    return m


def kolon_analizi(X0, T, R, R_inv=None):
    """X0: mesh noktalari (parca cercevesi), T: ucgenler, R: 3x3 donus (yukari -> +Z). Destek alani / hacmi ve bolgeler."""
    import numpy as np
    X = X0.dot(R.T)
    zmin = float(X[:, 2].min())
    X = X - np.array([0.0, 0.0, zmin])
    yer = yerlesim(X)
    a, b, c = X[T[:, 0]], X[T[:, 1]], X[T[:, 2]]
    cr = np.cross(b - a, c - a)
    A2 = np.linalg.norm(cr, axis=1)
    nz = cr[:, 2] / np.maximum(A2, 1e-12)
    zc = (a[:, 2] + b[:, 2] + c[:, 2]) / 3
    cos = math.cos(math.radians(ACI))
    cik = (nz < -cos) & (zc > 0.05)
    cikinti45 = float(0.5 * A2[cik].sum())
    temas = float(0.5 * A2[(nz < -0.99) & (zc < 0.05)].sum())
    # izgara
    x0, y0 = float(X[:, 0].min()), float(X[:, 1].min())
    gx0, gy0 = x0 + JIT[0] * H, y0 + JIT[1] * H
    nx = int((X[:, 0].max() - gx0) / H) + 2
    ny = int((X[:, 1].max() - gy0) / H) + 2
    sec = np.abs(cr[:, 2]) > 1e-9
    ti = np.nonzero(sec)[0]
    tx = np.stack([a[ti, 0], b[ti, 0], c[ti, 0]], 1)
    ty = np.stack([a[ti, 1], b[ti, 1], c[ti, 1]], 1)
    i0 = np.ceil((tx.min(1) - gx0) / H).astype(int)
    i1 = np.floor((tx.max(1) - gx0) / H).astype(int)
    j0 = np.ceil((ty.min(1) - gy0) / H).astype(int)
    j1 = np.floor((ty.max(1) - gy0) / H).astype(int)
    wi = np.maximum(i1 - i0 + 1, 0)
    wj = np.maximum(j1 - j0 + 1, 0)
    n = wi * wj
    hc, hz, hs, hn = [], [], [], []
    bas = 0
    cs = np.cumsum(n)
    while bas < len(ti):
        # parca parca: aday sayisi ~4e6'yi gecmesin
        hedef = (cs[bas - 1] if bas else 0) + 4000000
        son = int(np.searchsorted(cs, hedef, side="right"))
        son = max(son, bas + 1)
        sl = slice(bas, son)
        nn = n[sl]
        tot = int(nn.sum())
        bas = son
        if tot == 0:
            continue
        k = np.repeat(np.arange(len(nn)), nn)
        off = np.arange(tot) - np.repeat(np.cumsum(nn) - nn, nn)
        wii = wi[sl][k]
        ii = i0[sl][k] + off % np.maximum(wii, 1)
        jj = j0[sl][k] + off // np.maximum(wii, 1)
        t = ti[sl][k]
        px = gx0 + ii * H
        py = gy0 + jj * H
        ax, ay, az = a[t, 0], a[t, 1], a[t, 2]
        bx, by, bz = b[t, 0], b[t, 1], b[t, 2]
        cx, cy, cz = c[t, 0], c[t, 1], c[t, 2]
        w0 = (bx - px) * (cy - py) - (by - py) * (cx - px)
        w1 = (cx - px) * (ay - py) - (cy - py) * (ax - px)
        w2 = (ax - px) * (by - py) - (ay - py) * (bx - px)
        s = np.sign(cr[t, 2])
        ic = (w0 * s >= 0) & (w1 * s >= 0) & (w2 * s >= 0)
        if not ic.any():
            continue
        ws = (w0 + w1 + w2)[ic]
        z = (w0[ic] * az[ic] + w1[ic] * bz[ic] + w2[ic] * cz[ic]) / ws
        hc.append((ii[ic] * ny + jj[ic]).astype(np.int64))
        hz.append(z)
        hs.append(s[ic])
        hn.append(nz[t[ic]])
    if not hc:
        return dict(yer, destek_alan_mm2=0.0, destek_hacim_mm3=0.0, serbest_alan_mm2=0.0, bolge=[], bolge_sayi=0,
                    cikinti45_mm2=round(cikinti45, 1), temas_mm2=round(temas, 1), kesisim=0)
    col = np.concatenate(hc)
    z = np.concatenate(hz)
    s = np.concatenate(hs)
    nzh = np.concatenate(hn)
    o = np.lexsort((-s, z, col))          # ayni z'de once ust yuzey
    col, z, s, nzh = col[o], z[o], s[o], nzh[o]
    base = col.astype(float) * 1.0e5
    val = np.where(s > 0, base + z + 1000.0, base)
    run = np.maximum.accumulate(val)
    onceki = np.concatenate([[-1.0], run[:-1]])
    ayni = onceki >= base + 999.0                 # ayni kolonda alttan bir ust yuzey var
    alt_ust = np.where(ayni, onceki - base - 1000.0, 0.0)
    bosluk = z - alt_ust
    cos_d = math.cos(math.radians(ACI - ACI_TOL))
    dest = (s < 0) & (nzh < -cos_d) & (bosluk > ZTOL)
    tek = int(np.unique(col).size)
    if not dest.any():
        return dict(yer, destek_alan_mm2=0.0, destek_hacim_mm3=0.0, serbest_alan_mm2=0.0, bolge=[], bolge_sayi=0,
                    cikinti45_mm2=round(cikinti45, 1), temas_mm2=round(temas, 1), kesisim=int(len(z)), kolon=tek,
                    parite_hatasi=int(np.count_nonzero(np.bincount(col.astype(np.int64)) % 2)))
    dc, dz, dg = col[dest], z[dest], bosluk[dest]
    di, dj = dc // ny, dc % ny
    # bolgeler 3B: (i, j, 1 mm z dilimi) hucreleri 6-komsu + capraz z ile birlesir; XY izdusumunde ust uste dusen ama farkli
    # yukseklikteki kucuk cikintilar (or. dik basilan bantta boss altlari) tek bolge sayilmasin
    dk = np.floor(dz / ZDILIM).astype(np.int64)
    hl = _etiketle3(di, dj, dk)
    nlab = int(hl.max()) if len(hl) else 0
    genis = np.zeros(nlab + 1, bool)
    r_ = int(round(INCE / H))
    for L in range(1, nlab + 1):
        m = hl == L
        ci, cj = di[m] - di[m].min() + 1, dj[m] - dj[m].min() + 1
        if ci.max() + 2 <= 2 * r_ + 1 or cj.max() + 2 <= 2 * r_ + 1:
            continue
        mm = np.zeros((ci.max() + 2, cj.max() + 2), bool)
        mm[ci, cj] = True
        genis[L] = bool(_asindir_disk(mm, r_ + 0.5).any())
    n_ = np.bincount(hl, minlength=nlab + 1).astype(float)
    hac_ = np.bincount(hl, weights=dg, minlength=nlab + 1) * H * H
    mx_ = np.bincount(hl, weights=gx0 + di * H, minlength=nlab + 1)
    my_ = np.bincount(hl, weights=gy0 + dj * H, minlength=nlab + 1)
    mz_ = np.bincount(hl, weights=dz, minlength=nlab + 1)
    big = 1e9
    imin = np.full(nlab + 1, big); imax = np.full(nlab + 1, -big)
    jmin = np.full(nlab + 1, big); jmax = np.full(nlab + 1, -big)
    zmn = np.full(nlab + 1, big); zmx = np.full(nlab + 1, -big); gmx = np.full(nlab + 1, -big)
    np.minimum.at(imin, hl, di); np.maximum.at(imax, hl, di)
    np.minimum.at(jmin, hl, dj); np.maximum.at(jmax, hl, dj)
    np.minimum.at(zmn, hl, dz); np.maximum.at(zmx, hl, dz); np.maximum.at(gmx, hl, dg)
    bolgeler = []
    for L in range(1, nlab + 1):
        if n_[L] == 0:
            continue
        boy = max(imax[L] - imin[L] + 1, jmax[L] - jmin[L] + 1) * H
        kabul = bool(boy > KOPRU and genis[L])
        bolgeler.append(dict(kabul=kabul, alan_mm2=round(float(n_[L] * H * H), 1), hacim_mm3=round(float(hac_[L]), 0), boy_mm=round(float(boy), 1),
                             z_mm=[round(float(zmn[L]), 1), round(float(zmx[L]), 1)], kolon_mm=round(float(gmx[L]), 1),
                             _m=(mx_[L] / n_[L], my_[L] / n_[L], mz_[L] / n_[L])))
    if R_inv is not None:
        for bb in bolgeler:
            p = np.array(bb.pop("_m")) + np.array([0.0, 0.0, zmin])
            bb["merkez_parca"] = [round(float(v), 1) for v in R_inv.dot(p)]
    else:
        for bb in bolgeler:
            bb.pop("_m")
    kab = [bb for bb in bolgeler if bb["kabul"]]
    kab.sort(key=lambda r: -r["hacim_mm3"])
    serb = [bb for bb in bolgeler if not bb["kabul"]]
    return dict(yer, destek_alan_mm2=round(sum(r["alan_mm2"] for r in kab), 1), destek_hacim_mm3=round(sum(r["hacim_mm3"] for r in kab), 0),
                serbest_alan_mm2=round(sum(r["alan_mm2"] for r in serb), 1), serbest_bolge_sayi=len(serb), bolge=kab[:8], bolge_sayi=len(kab),
                cikinti45_mm2=round(cikinti45, 1), temas_mm2=round(temas, 1), kesisim=int(len(z)), kolon=tek,
                parite_hatasi=int(np.count_nonzero(np.bincount(col.astype(np.int64)) % 2)))


def kutle(hacim_mm3, dol, destek_hacim_mm3):
    k = hacim_mm3 / 1000.0 * RHO * dol
    dg = destek_hacim_mm3 / 1000.0 * RHO * DESTEK_DOLULUK
    return dict(parca_g=round(k * FIRE, 1), destek_g=round(dg, 1), toplam_g=round(k * FIRE + dg, 1),
                sure_sa=round((hacim_mm3 * dol + destek_hacim_mm3 * DESTEK_DOLULUK) / HIZ / 3600.0, 2))


# ================================================================ FreeCAD kipi
def _yon_temiz(t):
    """omuz tabla_yuzu metni: '152.0' -> '152', '1.5' -> '1,5' (F4c-partiler.py'nin eski donusumu)."""
    import re
    return re.sub(r"(\d)\.(\d)", r"\1,\2", re.sub(r"\.0\b", "", t))


def _fc_parcalar(modul):
    """[(ad, shape, yukari, yon_metni, malzeme, doluluk listesi, adet, yon_kaynak)] modulun montaj betigiyle ayni yoldan."""
    import FreeCAD as App
    for p_ in (FCD, os.path.join(FCD, modul)):
        if p_ not in sys.path:
            sys.path.insert(0, p_)
    import arayuz as A
    out = []
    if modul == "taban":
        import taban_parcalar as TP
        idx = {p["ad"]: k for k, p in enumerate(TP.P)}
        for ad, bd in TP.BASKI.items():
            p = TP.P[idx[ad]]
            out.append((ad, p["shape"], tuple(bd["yukari"]), bd["yon"], p["malzeme"], [TP.DOLULUK], 1, "taban_parcalar.BASKI"))
    elif modul == "dirsek":
        import dirsek_parcalar as DP
        idx = {p["ad"]: k for k, p in enumerate(DP.P)}
        for ad, bd in DP.BASKI.items():
            p = DP.P[idx[ad]]
            out.append((ad, p["shape"], tuple(bd["yukari"]), bd["yon"], p["malzeme"], [DP.DOLULUK], 2 if ad in ADET2["dirsek"] else 1,
                        "dirsek_parcalar.BASKI"))
    elif modul == "kafa":
        import kafa_parcalar as KP
        idx = {}
        for k, p in enumerate(KP.P):
            idx.setdefault(p["ad"], k)
        for ad, bd in KP.BASKI.items():
            p = KP.P[idx[ad]]
            out.append((ad, p["shape"], tuple(bd["yukari"]), bd["yon"], p["malzeme"], [p["doluluk_baski"]], 1, "kafa_parcalar.BASKI"))
    elif modul == "kabuk":
        import kabuk_parcalar as K
        for ad, d in K.PARCA.items():
            p = K.P[d["indeks"]]
            out.append((ad, p["shape"], tuple(d["yukari"]), d["yon"], p["malzeme"], [A.KABUK_DOLULUK], 1, "kabuk_parcalar.PARCA"))
    elif modul == "omuz":
        import omuz_parcalar as OP
        ob = json.load(open(os.path.join(FCD, "omuz", "omuz-baski.json"), encoding="utf-8"))
        sec = {q["ad"]: q for q in ob["parcalar"]}
        for p in OP.P:
            if p["tur"] != "Baski":
                continue
            q = sec[p["ad"]]
            y = q["yonler"][q["secilen_yon"]]
            ty = _yon_temiz(y["tabla_yuzu"].split(" (")[0])
            mal = q["malzeme"]
            dol = [0.80, 0.90] if mal == "PETG-CF" else [0.80]
            out.append((p["ad"], p["shape"], tuple(y["yukari"]), "%s: %s" % (q["secilen_yon"], ty), mal, dol, q["adet"],
                        "omuz-baski.json secilen_yon (yuk uyumu)"))
    return out


def _fcstd_hacim(modul):
    import FreeCAD as App
    yol = os.path.join(FCD, modul, modul + "-montaj.FCStd")
    doc = App.openDocument(yol)
    h = {}
    for o in doc.Objects:
        if o.TypeId == "Part::Feature" and getattr(o, "Tur", "") == "Baski":
            h.setdefault(o.Label, (o.Name, o.Shape.Volume))
    App.closeDocument(doc.Name)
    return h, datetime.datetime.fromtimestamp(os.stat(yol).st_mtime).isoformat(timespec="seconds")


def _mesh_np(sh):
    import numpy as np
    import MeshPart
    m = MeshPart.meshFromShape(Shape=sh, LinearDeflection=MESH[0], AngularDeflection=MESH[1])
    pts, tris = m.Topology
    return np.array([[p.x, p.y, p.z] for p in pts]), np.array(tris, dtype=np.int64)


def fc_matris(yukari):
    """App.Rotation(yukari, Z) -- eski analizlerle ayni donus (Z etrafindaki aci da ayni, olcu karsilastirilabilir)."""
    import numpy as np
    import FreeCAD as App
    m = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(*yukari), App.Vector(0, 0, 1))).toMatrix()
    return np.array([[m.A11, m.A12, m.A13], [m.A21, m.A22, m.A23], [m.A31, m.A32, m.A33]])


def parca_analiz(ad, sh, yukari, yon_metni):
    import numpy as np
    X0, T = _mesh_np(sh)
    aday = {"tasarim": tuple(float(v) for v in yukari)}
    for k, v in EKSEN.items():
        if max(abs(v[i] - aday["tasarim"][i]) for i in range(3)) > 1e-6:
            aday[k] = v
        else:
            aday["tasarim"] = v
            aday_ad = k
    sonuc = {}
    for k, y in aday.items():
        R = fc_matris(y)
        r = kolon_analizi(X0, T, R, R.T)
        r["yukari"] = [round(float(v), 4) for v in y]
        sonuc[k] = r
    t = sonuc["tasarim"]
    secilen = "tasarim"
    if not t["x2d_sigar"]:
        sig = [k for k in sonuc if sonuc[k]["x2d_sigar"]]
        if sig:
            secilen = min(sig, key=lambda k: (sonuc[k]["destek_hacim_mm3"], sonuc[k]["destek_alan_mm2"]))
    sig = [k for k in sonuc if sonuc[k]["x2d_sigar"]] or list(sonuc)
    en_az = min(sig, key=lambda k: (sonuc[k]["destek_hacim_mm3"], sonuc[k]["destek_alan_mm2"], 0 if k == "tasarim" else 1))
    return dict(ucgen=int(len(T)), secilen=secilen, en_az_destek=en_az, yonler=sonuc)


# ---------------------------------------------------------------- kapak tanisi: eski iki yontemin katman dokumu (kopya) + yuz olcumu
def kapak_tani(sh, yukari):
    import numpy as np
    import FreeCAD as App
    import Part
    import MeshPart
    V = App.Vector
    rot = App.Rotation(V(*yukari), V(0, 0, 1))
    s = sh.copy()
    s.transformShape(App.Placement(V(0, 0, 0), rot).toMatrix(), True)
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.25, AngularDeflection=0.35)   # kabuk_montaj ile ayni mesh
    zmin_k = min(p.z for p in m.Topology[0])
    m2 = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.1, AngularDeflection=0.3)    # kafa_lib ile ayni mesh
    zmin_l = min(p.z for p in m2.Topology[0])
    out = dict(bb_zmin=round(s.BoundBox.ZMin, 4), mesh_zmin_kabuk=round(zmin_k, 4), mesh_zmin_kafalib=round(zmin_l, 4),
               bb_z=round(s.BoundBox.ZLength, 3), hacim_mm3=round(sh.Volume, 1), gecerli=s.isValid())
    # yatay duzlem yuzler (baski cercevesinde) ve egik yuzler
    yz = []
    for i, f in enumerate(s.Faces):
        try:
            u0, u1, v0, v1 = f.ParameterRange
            n = f.normalAt(0.5 * (u0 + u1), 0.5 * (v0 + v1))
        except Exception:
            continue
        tip = f.Surface.TypeId.replace("Part::Geom", "")
        if tip == "Plane" and abs(abs(n.z) - 1) < 1e-6:
            yz.append(dict(yuz=i, tip=tip, nz=round(n.z, 6), z_tabladan=round(f.BoundBox.ZMin - zmin_k, 4), alan_mm2=round(f.Area, 1)))
    yz.sort(key=lambda r: (r["z_tabladan"], -r["alan_mm2"]))
    out["yatay_yuzler"] = yz
    egik = []
    for i, f in enumerate(s.Faces):
        tip = f.Surface.TypeId.replace("Part::Geom", "")
        if tip == "Plane":
            try:
                u0, u1, v0, v1 = f.ParameterRange
                n = f.normalAt(0.5 * (u0 + u1), 0.5 * (v0 + v1))
            except Exception:
                continue
            if 1e-6 < abs(n.z) < 1 - 1e-6:
                egik.append(dict(yuz=i, nz=round(n.z, 4), z=[round(f.BoundBox.ZMin - zmin_k, 3), round(f.BoundBox.ZMax - zmin_k, 3)], alan_mm2=round(f.Area, 1)))
    out["egik_duz_yuzler"] = egik[:20]

    def katmanlar(z0_ofset, zmin, ofset_kontrol):
        onceki, kat = None, []
        n_kat = int((s.BoundBox.ZMax - zmin) // 1.0) + 1
        for kk in range(n_kat):
            z = zmin + z0_ofset + kk * 1.0
            r = dict(z=round(z - zmin, 2))
            try:
                ws = s.slice(V(0, 0, 1), z)
            except Exception as e:
                ws = None
                r["kesit_hata"] = repr(e)[:60]
            if not ws:
                r["tel"] = 0
                kat.append(r)
                onceki = None
                continue
            r["tel"] = len(ws)
            r["kapali"] = all(w.isClosed() for w in ws)
            yuz = None
            try:
                yuz = Part.makeFace(ws, "Part::FaceMakerBullseye")
            except Exception as e:
                r["yuz_hata"] = repr(e)[:60]
            if yuz is not None:
                r["yuz_alan"] = round(yuz.Area, 2)
                r["yuz_sayi"] = len(yuz.Faces)
                r["yuz_gecerli"] = yuz.isValid()
                r["tel_uzunluk"] = [round(w.Length, 1) for w in ws][:10]
            if yuz is not None and onceki is not None:
                dl = []
                for f in onceki.Faces:
                    try:
                        o = f.makeOffset2D(1.0, 0)
                        dl.append(o if (not ofset_kontrol or o.Area > f.Area) else f)
                    except Exception:
                        dl.append(f)
                dest = dl[0].fuse(dl[1:]) if len(dl) > 1 else dl[0]
                dest.translate(V(0, 0, 1.0))
                r["dest_alan"] = round(dest.Area, 2)
                acik = yuz.cut(dest)
                r["acik"] = [(round(f.Area, 2), round(max(f.BoundBox.XLength, f.BoundBox.YLength), 1)) for f in acik.Faces if f.Area >= 0.5][:8]
                o2 = onceki.copy()
                o2.translate(V(0, 0, 1.0))
                try:
                    r["ofsetsiz_tasma_mm2"] = round(yuz.cut(o2).Area, 2)
                except Exception as e:
                    r["ofsetsiz_tasma_mm2"] = repr(e)[:40]
            kat.append(r)
            onceki = yuz
        return kat

    out["kabuk_montaj_yontemi"] = dict(not_="kabuk_montaj.baski_analiz kopyasi: z = mesh zmin + 0,5 + k, ofset kontrolsuz", katman=katmanlar(0.5, zmin_k, False))
    out["kafa_lib_yontemi"] = dict(not_="kafa_lib.baski_analiz kopyasi: z = mesh zmin + 0,47 + k, ofset alani buyumezse ofsetsiz", katman=katmanlar(0.47, zmin_l, True))
    out["kabuk_yontemi_bb_zmin"] = dict(not_="uygulama_tani.py gibi: z = BoundBox.ZMin + 0,5 + k", katman=katmanlar(0.5, s.BoundBox.ZMin, False))
    # ince tarama: 0,05 mm adimla kesit alani (yatay yuz duzlemlerini ve kesit kaymasini gosterir)
    ince = []
    zz = 0.05
    while zz < 4.0:
        try:
            ws = s.slice(V(0, 0, 1), zmin_k + zz)
            f = Part.makeFace(ws, "Part::FaceMakerBullseye") if ws else None
            ince.append((round(zz, 2), len(ws) if ws else 0, round(f.Area, 1) if f is not None else None))
        except Exception as e:
            ince.append((round(zz, 2), -1, repr(e)[:30]))
        zz += 0.05
    out["ince_kesit"] = ince
    out["boolean_deneme"] = boolean_deneme(s, zmin_k)
    return out


def boolean_deneme(s, zmin):
    """Ayni kesit (z 1,5 ve 2,5; ikisi de plaka) uzerinde eski yontemin boolean'i: bir yuzu ozdesine dusurunce ne kaliyor."""
    import FreeCAD as App
    import Part
    V = App.Vector

    def yuz(z):
        return Part.makeFace(s.slice(V(0, 0, 1), zmin + z), "Part::FaceMakerBullseye")

    def bilgi(f):
        u0, u1, v0, v1 = f.ParameterRange
        n = f.normalAt(0.5 * (u0 + u1), 0.5 * (v0 + v1))
        return dict(alan=round(f.Area, 3), normal_z=round(n.z, 6), z=round(f.BoundBox.ZMin - zmin, 6), dz=round(f.BoundBox.ZLength, 9),
                    tel=len(f.Wires), kenar=len(f.Edges), gecerli=f.isValid(), tolerans=round(max(e.Tolerance for e in f.Edges), 9))
    out = {}
    for z1, z2 in ((1.5, 2.5), (1.47, 2.47), (1.6, 2.6), (1.9, 2.9), (0.5, 1.5), (2.0, 2.5)):
        a, b = yuz(z1), yuz(z2)
        t = a.copy()
        t.translate(V(0, 0, z2 - z1))
        r = dict(alt=bilgi(a), ust=bilgi(b))
        for ad, f in (("cut_ust_eksi_alt", lambda: b.cut(t)), ("common", lambda: b.common(t)),
                      ("cut_alt_eksi_ust", lambda: t.cut(b))):
            try:
                x = f()
                r[ad] = round(x.Area, 3)
            except Exception as e:
                r[ad] = repr(e)[:60]
        t2 = a.copy()
        t2.translate(V(0, 0, z2 - z1 + 1e-4))       # duzlemler 0,1 mikron ayrik: koplanar degil -> 2B cut anlamsiz, kontrol icin
        try:
            r["cut_1e-4_kaydirma"] = round(b.cut(t2).Area, 3)
        except Exception as e:
            r["cut_1e-4_kaydirma"] = repr(e)[:60]
        # 2B dogrulama: iki teli XY'de karsilastir (z'yi sifirla) -> ayni cokgen mi
        pa = sorted((round(v.X, 3), round(v.Y, 3)) for v in a.Vertexes)
        pb = sorted((round(v.X, 3), round(v.Y, 3)) for v in b.Vertexes)
        r["koseler_ayni"] = pa == pb
        r["kose_sayi"] = [len(pa), len(pb)]
        out["%g-%g" % (z1, z2)] = r
    return out


def fc_ana(modul, ara):
    t0 = time.time()
    log("modul", modul)
    parcalar = _fc_parcalar(modul)
    log("parca", len(parcalar), "%.1fs" % (time.time() - t0))
    fh, ftar = _fcstd_hacim(modul)
    sonuc = []
    tani = kars = None
    for ad, sh, yukari, yon, mal, dol, adet, ykay in parcalar:
        tp = time.time()
        r = parca_analiz(ad, sh, yukari, yon)
        hac = sh.Volume
        fn = fh.get(ad)
        r.update(modul=modul, ad=ad, adet=adet, malzeme=mal, doluluk=dol, yon=yon, yon_kaynak=ykay, hacim_mm3=round(hac, 1),
                 kaynak=dict(fcstd="tasarim/freecad/%s/%s-montaj.FCStd" % (modul, modul), fcstd_nesne=fn[0] if fn else None,
                             fcstd_degistirilme=ftar, step="tasarim/freecad/%s/%s-montaj.step" % (modul, modul),
                             fcstd_hacim_mm3=round(fn[1], 1) if fn else None,
                             hacim_esit=bool(fn and abs(fn[1] - hac) <= 1e-3 * max(hac, 1.0)), geometri="%s/%s_parcalar.py" % (modul, modul)))
        sonuc.append(r)
        y = r["yonler"][r["secilen"]]
        log("%-34s %s olcu %s sigar %s destek %.0f mm2 %.1f cm3 (serbest %.0f) en az %s %.1f cm3  %.1fs" % (
            ad, r["secilen"], y["olcu"], y["x2d_sigar"], y["destek_alan_mm2"], y["destek_hacim_mm3"] / 1000, y["serbest_alan_mm2"],
            r["en_az_destek"], r["yonler"][r["en_az_destek"]]["destek_hacim_mm3"] / 1000, time.time() - tp))
        if modul == "kabuk" and ad == "Arka servis kapagi":          # karsilastirma: 3 mm duz kapak (eski yontem 0 sorun)
            try:
                import FreeCAD as App
                s2 = sh.copy()
                s2.transformShape(App.Placement(App.Vector(), App.Rotation(App.Vector(*yukari), App.Vector(0, 0, 1))).toMatrix(), True)
                kars = boolean_deneme(s2, s2.BoundBox.ZMin)
            except Exception as e:
                kars = dict(hata=repr(e)[:200])
        if modul == "kabuk" and ad == "Ust arka servis kapagi":
            try:
                tani = kapak_tani(sh, yukari)
            except Exception as e:
                tani = dict(hata=repr(e)[:200])
            log("kapak tanisi", json.dumps({k: tani[k] for k in tani if k not in ("kabuk_montaj_yontemi", "kafa_lib_yontemi", "kabuk_yontemi_bb_zmin", "ince_kesit", "yatay_yuzler", "egik_duz_yuzler")}, ensure_ascii=False))
    out = dict(modul=modul, tarih=datetime.datetime.now().isoformat(timespec="seconds"), sure_s=round(time.time() - t0, 1), parcalar=sonuc)
    if tani is not None:
        if kars is not None:
            tani["karsilastirma_arka_servis_kapagi"] = kars
        out["kapak_tani"] = tani
    os.makedirs(ara, exist_ok=True)
    json.dump(out, open(os.path.join(ara, "baski-%s.json" % modul), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log("bitti", modul, "%.1fs" % (time.time() - t0))


# ================================================================ birlestirme (FreeCAD'siz)
def _eski():
    """Eski baski sonuclari: (modul, ad) -> liste [(kaynak anahtari, dict)]."""
    e = {}
    for mod in ("taban", "kabuk", "kafa", "dirsek"):
        for i, p in enumerate(json.load(open(os.path.join(FCD, mod, mod + "-analiz.json"), encoding="utf-8"))["baski"]):
            e.setdefault((mod, p["ad"]), []).append(("%s/%s-analiz.json baski[%d]" % (mod, mod, i), dict(
                filament_g=[p["filament_g"], p["filament_g"]], sure_saat=[p["sure_saat"], p["sure_saat"]], desteksiz=p["desteksiz"],
                destek_sorun_sayi=p.get("destek_sorun_sayi"), destek_sorun=p.get("destek_sorun", [])[:3], olcu=p["olcu"],
                cikinti_orani=p.get("cikinti_orani"), destek_g=None, yontem="katman 1 mm, onceki katman 1 mm ofset, kopru 15 mm; destek g sayilmaz")))
    ob = json.load(open(os.path.join(FCD, "omuz", "omuz-baski.json"), encoding="utf-8"))
    for i, p in enumerate(ob["parcalar"]):
        y = p["yonler"][p["secilen_yon"]]
        fg, ss = p["filament_g"], p["sure_saat"]
        e.setdefault(("omuz", p["ad"]), []).append(("omuz/omuz-baski.json parcalar[%d]" % i, dict(
            filament_g=[fg["0.80"], fg.get("0.90", fg["0.80"])], sure_saat=[ss["0.80"], ss.get("0.90", ss["0.80"])], desteksiz=p["desteksiz"],
            destek_alan_mm2=y["destek_alan_mm2"], destek_hacim_cm3=y["destek_hacim_cm3"], destek_g=p["destek_filament_g"], olcu=y["olcu"],
            yontem="katman 0,5 mm + egim yuzleri, destek g sayilir (x0,15)")))
    om = json.load(open(os.path.join(FCD, "omuz", "omuz-analiz.json"), encoding="utf-8"))
    for i, p in enumerate(om.get("baski", [])):
        e.setdefault(("omuz", p["ad"]), []).append(("omuz/omuz-analiz.json baski[%d]" % i, dict(
            filament_g=[p.get("filament_g"), p.get("filament_g")], sure_saat=[p.get("sure_saat"), p.get("sure_saat")], desteksiz=p.get("desteksiz"),
            destek_sorun_sayi=p.get("destek_sorun_sayi"), olcu=p.get("olcu"), destek_g=None, yontem="omuz_montaj ic analizi")))
    ky = os.path.join(HERE, "kafa-yerlesim", "uygulama-baski.json")
    d = json.load(open(ky, encoding="utf-8"))
    for k_, p in d.get("parca", {}).items():
        mod = "kabuk" if ("servis" in p["ad"] or "Hoparlor" in p["ad"] or "bandi" in p["ad"]) else "kafa"
        e.setdefault((mod, p["ad"]), []).append(("lale158/kafa-yerlesim/uygulama-baski.json parca[%s]" % k_, dict(
            filament_g=[round(p["kutle_g"] * FIRE, 1)] * 2, sure_saat=[p.get("sure_saat")] * 2, desteksiz=p.get("desteksiz"),
            destek_sorun_sayi=p.get("destek_sorun_sayi"), olcu=p.get("olcu"), destek_g=None,
            yontem="kafa_lib.baski_analiz (KL, 05.11; kutle x 1,05)")))
    return e


def birlestir(ara):
    parca = []
    tani = None
    sure = {}
    for mod in MODULLER:
        d = json.load(open(os.path.join(ara, "baski-%s.json" % mod), encoding="utf-8"))
        sure[mod] = dict(tarih=d["tarih"], sure_s=d["sure_s"])
        if "kapak_tani" in d:
            tani = d["kapak_tani"]
        for r in d["parcalar"]:
            y = r["yonler"][r["secilen"]]
            dol = r["doluluk"]
            k = [kutle(r["hacim_mm3"], x, y["destek_hacim_mm3"]) for x in dol]
            k = k + [k[0]] if len(k) == 1 else k
            ea = r["yonler"][r["en_az_destek"]]
            ke = kutle(r["hacim_mm3"], dol[0], ea["destek_hacim_mm3"])
            parca.append(dict(
                modul=r["modul"], ad=r["ad"], adet=r["adet"], malzeme=r["malzeme"], doluluk=dol,
                yon=_yon_temiz(r["yon"]) if r["modul"] == "omuz" else r["yon"], yon_kaynak=r["yon_kaynak"], yon_aday=r["secilen"], yukari=y["yukari"],
                olcu=y["olcu"], tabla_aci=y["tabla_aci"], x2d_sigar=y["x2d_sigar"],
                desteksiz=y["destek_hacim_mm3"] <= 0, destek_alan_mm2=y["destek_alan_mm2"], destek_hacim_cm3=round(y["destek_hacim_mm3"] / 1000, 2),
                destek_g=[k[0]["destek_g"], k[1]["destek_g"]], parca_g=[k[0]["parca_g"], k[1]["parca_g"]],
                toplam_g=[k[0]["toplam_g"], k[1]["toplam_g"]], sure_sa=[k[0]["sure_sa"], k[1]["sure_sa"]],
                destek_orani=round(k[0]["destek_g"] / k[0]["toplam_g"], 4) if k[0]["toplam_g"] else 0.0,
                destek_bolge=y["bolge"][:5], serbest_alan_mm2=y["serbest_alan_mm2"], cikinti45_mm2=y["cikinti45_mm2"], temas_mm2=y["temas_mm2"],
                parite_hatasi=y.get("parite_hatasi"), kolon=y.get("kolon"),
                hacim_cm3=round(r["hacim_mm3"] / 1000, 2), ucgen=r["ucgen"],
                en_az_destek=dict(aday=r["en_az_destek"], yukari=ea["yukari"], destek_alan_mm2=ea["destek_alan_mm2"],
                                  destek_hacim_cm3=round(ea["destek_hacim_mm3"] / 1000, 2), destek_g=ke["destek_g"], olcu=ea["olcu"],
                                  x2d_sigar=ea["x2d_sigar"], temas_mm2=ea["temas_mm2"]),
                adaylar={a: dict(yukari=v["yukari"], destek_alan_mm2=v["destek_alan_mm2"], destek_hacim_cm3=round(v["destek_hacim_mm3"] / 1000, 2),
                                 olcu=v["olcu"], x2d_sigar=v["x2d_sigar"], temas_mm2=v["temas_mm2"]) for a, v in r["yonler"].items()},
                kaynak=r["kaynak"]))
    # eski sonuclarla fark
    E = _eski()
    fark = []
    for i, p in enumerate(parca):
        for key, o in E.get((p["modul"], p["ad"]), []):
            g_eski = o["filament_g"][0]
            g_yeni = p["toplam_g"][0]
            yuzde = (g_yeni - g_eski) / g_eski * 100 if g_eski else None
            dv = (not p["desteksiz"]) != (not o["desteksiz"]) if o["desteksiz"] is not None else None
            fark.append(dict(i=i, modul=p["modul"], ad=p["ad"], eski_kaynak=key, eski_g=o["filament_g"], yeni_g=p["toplam_g"],
                             fark_yuzde=round(yuzde, 1) if yuzde is not None else None, eski_desteksiz=o["desteksiz"], yeni_desteksiz=p["desteksiz"],
                             destek_var_yok_degisti=dv, eski_destek_g=o.get("destek_g"), yeni_destek_g=p["destek_g"][0],
                             eski_destek_sorun=o.get("destek_sorun_sayi"), eski_destek_alan_mm2=o.get("destek_alan_mm2"),
                             yeni_destek_alan_mm2=p["destek_alan_mm2"], eski_olcu=o.get("olcu"), yeni_olcu=p["olcu"], eski_yontem=o["yontem"],
                             buyuk=(yuzde is not None and abs(yuzde) > 10) or bool(dv)))
    top = dict(adet=0, toplam_g=[0.0, 0.0], destek_g=[0.0, 0.0], sure_sa=[0.0, 0.0], destekli_adet=0, destekli_tur=0)
    for p in parca:
        top["adet"] += p["adet"]
        for j in (0, 1):
            top["toplam_g"][j] += p["adet"] * p["toplam_g"][j]
            top["destek_g"][j] += p["adet"] * p["destek_g"][j]
            top["sure_sa"][j] += p["adet"] * p["sure_sa"][j]
        if not p["desteksiz"]:
            top["destekli_adet"] += p["adet"]
            top["destekli_tur"] += 1
    for k in ("toplam_g", "destek_g", "sure_sa"):
        top[k] = [round(x, 2) for x in top[k]]
    top["x2d_sigmayan"] = [p["ad"] for p in parca if not p["x2d_sigar"]]
    top["fcstd_hacim_esit_degil"] = [p["ad"] for p in parca if not p["kaynak"]["hacim_esit"]]
    out = dict(
        tarih=datetime.date.today().isoformat(), betik="tasarim/freecad/lale158/baski_analiz_ortak.py", paket="F6b (P6.2)",
        yontem=dict(izgara_mm=H, aci_derece=ACI, aci_tolerans_derece=ACI_TOL, hava_esik_mm=ZTOL, kopru_mm=KOPRU, ince_serit_mm=2 * INCE, destek_doluluk=DESTEK_DOLULUK,
                    rho_g_cm3=RHO, hiz_mm3_s=HIZ, fire=FIRE, x2d=list(X2D), mesh=list(MESH),
                    yon_kurali="tasarim yonu (modul BASKI.yukari; omuzda omuz-baski secilen_yon); X2D'ye sigmazsa sigan adaylardan en az destek. "
                               "Adaylar: tasarim + 6 eksen; en az destek yonu oneri olarak yazilir.",
                    not_="destek = 45 dereceden yatik alt yuzeyin altindaki hava kolonu (tabla ya da alttaki malzemeye kadar); <= 15 mm bolge ve <= 2 mm serit serbest. "
                         "Destek g = hacim x 0,15 x 1,27 (tahmini; dilimleyici esastir). g ve sure alt/ust: doluluk araligi (yalniz omuz PETG-CF 0,8-0,9)."),
        moduller=sure, parcalar=parca, toplam=top, fark=fark, kapak_tani=tani)
    json.dump(out, open(CIKTI, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    print("yazildi", CIKTI, "parca turu", len(parca), "adet", top["adet"], "g", top["toplam_g"], "destek g", top["destek_g"], "sa", top["sure_sa"])
    return 0


if __name__ == "__main__":
    if os.environ.get("BASKI_MODUL"):
        fc_ana(os.environ["BASKI_MODUL"], os.environ.get("BASKI_ARA") or os.path.join(HERE, "_ara"))
    elif len(sys.argv) >= 3 and sys.argv[1] == "birlestir":
        raise SystemExit(birlestir(sys.argv[2]))
    else:
        print(__doc__)
