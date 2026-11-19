# P10.8b görev 1: bandın giriş yolu boyunca engel profili (depo dışı, salt okunur; FreeCAD istemez).
# Kaynak: rehber/veri/robot.glb + rehber-veri.json. Yöntem rehber_giris.Giris.carpisma (ışın aralıkları h 0,5 mm, ortak hacim
# eşiği 0,2 mm; temas sayılmaz), F10d § 11.5 ile aynı; adım 2 mm (tam sayı ızgara kaydırması). Engel = bandın alt adımında yerinde
# olanlar (rehber_sira.Denetim.durumlar izin kümesi), bandın kendi grubu hariç. Çıktı: yön başına engel → [ilk, son] mm aralıkları.
# Kullanım: py -3 bant_profil.py <robot> <cikti.json> [pid,...]
import os, sys, json, time, functools
import numpy as np
print = functools.partial(print, flush=True)
ROBOT, OUT = sys.argv[1], sys.argv[2]
SEC = sys.argv[3].split(",") if len(sys.argv) > 3 else None
sys.path.insert(0, os.path.join(ROBOT, "tasarim", "freecad", "rehber"))
import rehber_sira as RS
import rehber_giris as RG

VERI = os.path.join(ROBOT, "rehber", "veri")
V = json.load(open(os.path.join(VERI, "rehber-veri.json"), encoding="utf-8"))
t0 = time.time()
D = RS.Denetim(V, os.path.join(VERI, "robot.glb"))
P, K, A = D.P, D.ID, V["adimlar"]
G = RG.Giris(P, h=0.5)
ADIM = 4                         # ızgara adımı (h 0,5 mm) → 2 mm
AZAMI = 300.0
sonuc = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else []


def profil(kod, grup_ad, pid, yonler):
    s = next(i for i, a in enumerate(A) if a["kod"] == kod)
    for ad, tz, ids, izin in D.durumlar(s):
        if ad == grup_ad:
            break
    else:
        raise SystemExit("grup yok " + grup_ad)
    h = K[pid]
    grup = set(int(x) for x in ids)
    E0 = [int(k) for k in np.nonzero(izin)[0] if k != h and k not in grup]
    for d in yonler:
        d = np.asarray(d, np.int64)
        adim_mm = G.h * float(np.linalg.norm(d)) * ADIM
        hlo, hhi = P[h]["bmin"], P[h]["bmax"]
        n_max = int(AZAMI / adim_mm) + 1
        D_ = d * G.h * ADIM
        clo = np.minimum(hlo, hlo + D_ * n_max); chi = np.maximum(hhi, hhi + D_ * n_max)
        E = [e for e in E0 if RG._kesisir(P[e]["bmin"], P[e]["bmax"], clo, chi, 1.0)]
        dinlenme = G.carpisma([h], E, np.zeros(3, np.int64))
        aralik = {}
        serbest_mm = None
        t = time.time()
        for n in range(1, n_max + 1):
            kay = d * n * ADIM
            Ek = [e for e in E if RG._kesisir(P[e]["bmin"], P[e]["bmax"], hlo + kay * G.h, hhi + kay * G.h, 0.5)]
            if not Ek:
                serbest_mm = round(n * adim_mm, 1)
                break
            c = G.carpisma([h], Ek, kay)
            for (_, e), (der, isin) in c.items():
                if (h, e) in dinlenme:
                    continue
                mm = round(n * adim_mm, 1)
                a = aralik.setdefault(e, [mm, mm, 0.0])
                a[1] = mm
                a[2] = max(a[2], der)
        r = dict(adim=kod, grup=grup_ad, parca=P[h]["ad"], pid=pid, yon=[int(x) for x in d], adim_mm=round(adim_mm, 2),
                 ayrildi_mm=serbest_mm, dinlenme=[P[e]["ad"] for (_, e) in dinlenme],
                 engel=[dict(ad=P[e]["ad"], id=P[e]["id"], ilk_mm=a[0], son_mm=a[1]) for e, a in sorted(aralik.items(), key=lambda x: x[1][0])],
                 sure_s=round(time.time() - t, 1))
        sonuc.append(r)
        json.dump(sonuc, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("PROFIL", kod, P[h]["ad"], list(r["yon"]), "ayrildi", serbest_mm, "|",
              "; ".join("%s %s-%s" % (x["ad"][:34], x["ilk_mm"], x["son_mm"]) for x in r["engel"]), "| %.0f s" % r["sure_s"])


IS = [("F3", "Göğüs bandı sağ + y 1095 braketi", "p0213", [(1, 0, 0), (0, 1, 0)]),
      ("F1", "Ön sağ bant", "p0223", [(0, 0, 1), (1, 0, 1)]),
      ("F4", "Omuz bandı sağ", "p0215", [(1, 0, 0), (0, 1, 0)]),
      ("F3", "Göğüs ekranı çerçevesi", "p0229", [(0, 0, 1)]),
      ("F3", "Göğüs bandı sol + y 1095 braketi", "p0214", [(-1, 0, 0), (0, 1, 0)]),
      ("F1", "Ön sol bant", "p0224", [(0, 0, 1)]),
      ("F4", "Omuz bandı sol, ön dikiş", "p0216", [(-1, 0, 0), (0, 1, 0)])]
print("yukleme %.1f s" % (time.time() - t0))
for kod, g, pid, y in IS:
    if SEC and pid not in SEC:
        continue
    profil(kod, g, pid, y)
print("bitti %.0f s" % (time.time() - t0))
