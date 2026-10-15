# K3 bagimsiz kontrol: E0 donus hesabini donus_hesap.py'yi KULLANMADAN yeniden kurar.
# Yontem: yerinde donuste sag/sol simetri -> vz = 0; bilinmeyenler (vx, w). Ic dongu: verilen w icin Fx(vx) = 0 (bisection,
# monoton), dis dongu: M(w) = 0 (bisection). Coulomb surtunme dairesi, eps = lastik kayma olcegi (0 ~ rijit Coulomb).
# Girdiler elle yazildi (arayuz'dan okunmadi): kutle 21,7144 kg, AM z -13,8 (taban-analiz.json robot.pozlar[0]),
# teker x 178, aks z 185, r 62,5, Crr 0,03. Omni: on tekerde yanal mu 0,05, r 63,5.
# Kullanim: py -3 planlama/adim3/K3_donus.py  -> K3_donus_sonuc.json
import math, json, os

G = 9.81
M_KG, AMZ, AMX = 21.7144, -13.8, -0.2
XW, ZW, RW = 0.178, 0.185, 0.0625
CRR = 0.03


def tekerler(mu, omni=False, mu_omni=0.05, r_omni=0.0635):
    W = M_KG * G
    out = []
    for sz in (1, -1):
        for sx in (1, -1):
            fz = 0.5 + sz * (AMZ / 1000) / (2 * ZW)
            fx = 0.5 + sx * (AMX / 1000) / (2 * XW)
            om = omni and sz > 0
            out.append(dict(x=sx * XW, z=sz * ZW, N=W * fz * fx, my=(mu_omni if om else mu), mb=mu,
                            r=(r_omni if om else RW), u=(1.0 if sx > 0 else -1.0), ad=("on" if sz > 0 else "arka") + (" sag" if sx > 0 else " sol")))
    return out


def kuvvet(t, vx, w, eps):
    # temas noktasi hizi: v = (vx + w z, -w x) ; teker cevre hizi u * r/RW (z yonu)
    sx = vx + w * t["z"]
    sz = -w * t["x"] - t["u"] * t["r"] / RW
    n = math.sqrt((t["my"] * sx) ** 2 + (t["mb"] * sz) ** 2 + eps ** 2)
    return -t["N"] * t["my"] ** 2 * sx / n, -t["N"] * t["mb"] ** 2 * sz / n


def toplam(T, vx, w, eps):
    Fx = M = 0.0
    for t in T:
        fx, fz = kuvvet(t, vx, w, eps)
        Fx += fx
        M += t["x"] * fz - t["z"] * fx
    return Fx, M


def bisect(f, a, b, n=200):
    fa = f(a)
    for _ in range(n):
        m = 0.5 * (a + b)
        fm = f(m)
        if (fm > 0) == (fa > 0):
            a, fa = m, fm
        else:
            b = m
    return 0.5 * (a + b)


def coz(T, eps):
    def vx_of(w):
        return bisect(lambda vx: toplam(T, vx, w, eps)[0], -5.0, 5.0)
    w = bisect(lambda w: toplam(T, vx_of(w), w, eps)[1], -1.0 / XW * 3, -1e-6)
    vx = vx_of(w)
    res = []
    for t in T:
        fx, fz = kuvvet(t, vx, w, eps)
        Tm = (fz + t["u"] * CRR * t["N"]) * t["r"] * 10.197
        res.append((t["ad"], round(t["N"], 1), round(abs(Tm), 2)))
    return dict(w=w, ani_merkez_z_mm=round(-vx / w * 1000, 1), tekerler=res, en_cok=max(r[2] for r in res),
                artik=toplam(T, vx, w, eps))


def ust_sinir(mu, R=0.0):
    # Wong: M = mu_t sum N |z|, mu_t = mu / (0,925 + 0,15 R/B); dis yan kuvvet M/B paylastirilir N oraninda
    T = tekerler(mu)
    B = 2 * XW
    mut = mu / (0.925 + 0.15 * R / B)
    Mr = mut * sum(t["N"] * abs(t["z"]) for t in T)
    Ny = sum(t["N"] for t in T if t["x"] > 0)
    return max((Mr / B * t["N"] / Ny + CRR * t["N"]) * RW * 10.197 for t in T if t["x"] > 0)


if __name__ == "__main__":
    out = {}
    for mu in (0.4, 0.5, 0.6):
        out[str(mu)] = dict(
            rijit=coz(tekerler(mu), 1e-7),
            kayma_005=coz(tekerler(mu), 0.05),
            omni_kayma_005=coz(tekerler(mu, omni=True), 0.05),
            omni_rijit=coz(tekerler(mu, omni=True), 1e-7),
            ust_sinir_R0=round(ust_sinir(mu), 2))
        o = out[str(mu)]
        print("mu %.1f rijit %.2f  kayma0.05 %.2f  omni %.2f (rijit %.2f)  ust %.2f  merkez z %.1f" % (
            mu, o["rijit"]["en_cok"], o["kayma_005"]["en_cok"], o["omni_kayma_005"]["en_cok"], o["omni_rijit"]["en_cok"],
            o["ust_sinir_R0"], o["kayma_005"]["ani_merkez_z_mm"]))
        print("   ", o["kayma_005"]["tekerler"], o["omni_kayma_005"]["tekerler"])
    # el hesabi kontrolu: esit yuk, rijit, merkezde donme -> F_boy = mu N sin(a), tan a = ZW/XW
    N = M_KG * G / 4
    s = ZW / math.hypot(XW, ZW)
    for mu in (0.4, 0.5, 0.6):
        print("el hesabi esit yuk mu %.1f: %.2f kg cm" % (mu, (mu * N * s + CRR * N) * RW * 10.197))
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "K3_donus_sonuc.json"), "w"), indent=1)
