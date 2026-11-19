# P10.8b görev 1: iki parçalı yol (önce bant yerinden L mm "kalk" yönünde, sonra "cik" yönünde çekilir); bant_profil.py ile aynı yöntem.
# Kullanım: py -3 bant_iki.py <robot> <cikti.json>
import os, sys, json, time, functools
import numpy as np
print = functools.partial(print, flush=True)
ROBOT, OUT = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(ROBOT, "tasarim", "freecad", "rehber"))
import rehber_sira as RS
import rehber_giris as RG

VERI = os.path.join(ROBOT, "rehber", "veri")
V = json.load(open(os.path.join(VERI, "rehber-veri.json"), encoding="utf-8"))
D = RS.Denetim(V, os.path.join(VERI, "robot.glb"))
P, K, A = D.P, D.ID, V["adimlar"]
G = RG.Giris(P, h=0.5)
ADIM = 4
sonuc = []


def engel(kod, grup_ad, pid):
    s = next(i for i, a in enumerate(A) if a["kod"] == kod)
    for ad, tz, ids, izin in D.durumlar(s):
        if ad == grup_ad:
            grup = set(int(x) for x in ids)
            return K[pid], [int(k) for k in np.nonzero(izin)[0] if k != K[pid] and k not in grup]
    raise SystemExit(grup_ad)


def yol(h, E, kay0, d, azami=300.0):
    """kay0 (ızgara) kaydırılmış bandı d yönünde çek; döner (ayrıldı mm, {engel: [ilk, son]})."""
    d = np.asarray(d, np.int64)
    adim_mm = G.h * float(np.linalg.norm(d)) * ADIM
    hlo, hhi = P[h]["bmin"], P[h]["bmax"]
    dinlenme = G.carpisma([h], E, np.zeros(3, np.int64))
    ar = {}
    for n in range(0, int(azami / adim_mm) + 2):
        kay = kay0 + d * n * ADIM
        Ek = [e for e in E if RG._kesisir(P[e]["bmin"], P[e]["bmax"], hlo + kay * G.h, hhi + kay * G.h, 0.5)]
        if not Ek:
            return round(n * adim_mm, 1), ar
        for (_, e), v in G.carpisma([h], Ek, kay).items():
            if (h, e) in dinlenme:
                continue
            a = ar.setdefault(P[e]["ad"], [n * adim_mm, n * adim_mm])
            a[1] = n * adim_mm
    return None, ar


def iki(kod, g, pid, kalk, cik, L_list):
    h, E = engel(kod, g, pid)
    for L in L_list:
        kalk_ = np.asarray(kalk, np.int64)
        # 1. parça: yerinden L mm kalk (0..L)
        ar1 = {}
        for n in range(1, int(L / (G.h * ADIM)) + 1):
            for (_, e), v in G.carpisma([h], E, kalk_ * n * ADIM).items():
                ar1.setdefault(P[e]["ad"], [n * G.h * ADIM, 0])[1] = n * G.h * ADIM
        kay0 = kalk_ * int(round(L / G.h))
        ayr, ar2 = yol(h, E, kay0, cik)
        r = dict(adim=kod, parca=P[h]["ad"], kalk=list(kalk), L_mm=L, cik=list(cik), kalk_engel=ar1, cik_ayrildi_mm=ayr, cik_engel=ar2)
        sonuc.append(r)
        json.dump(sonuc, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("IKI", kod, P[h]["ad"], "kalk", list(kalk), L, "mm:", "; ".join("%s %s-%s" % (k[:30], a[0], a[1]) for k, a in ar1.items()) or "serbest",
              "| sonra", list(cik), "ayrildi", ayr, ":", "; ".join("%s %s-%s" % (k[:30], a[0], a[1]) for k, a in ar2.items()) or "serbest")


iki("F3", "Göğüs bandı sağ + y 1095 braketi", "p0213", (0, 1, 0), (1, 0, 0), [16, 24])
iki("F3", "Göğüs bandı sol + y 1095 braketi", "p0214", (0, 1, 0), (-1, 0, 0), [16, 24])
iki("F4", "Omuz bandı sağ", "p0215", (0, 1, 0), (1, 0, 0), [16, 24])
iki("F4", "Omuz bandı sol, ön dikiş", "p0216", (0, 1, 0), (-1, 0, 0), [16, 24])
iki("F1", "Ön sağ bant", "p0223", (0, 0, 1), (1, 0, 0), [10])
iki("F1", "Ön sol bant", "p0224", (0, 0, 1), (-1, 0, 0), [10])
print("bitti")
