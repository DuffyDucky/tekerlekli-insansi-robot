# P10.8b görev 1: bant dikişlerinde dil / dudak yönü (depo dışında koşuldu; FreeCAD istemez).
# Kaynak: rehber/veri/robot.glb + rehber-veri.json. Yalnız dil ölçümü: YALNIZ_DIL=1 py -3 bant_dil.py <robot> <cikti.json>
# (yol bölümü bant_profil.py / bant_iki.py ile yeniden yazıldı; buradaki yol kodu kullanılmadı)
import os, sys, json, time
import numpy as np, functools
print = functools.partial(print, flush=True)
ROBOT, OUT = sys.argv[1], sys.argv[2]
REH = os.path.join(ROBOT, "tasarim", "freecad", "rehber")
sys.path.insert(0, REH)
import rehber_sira as RS
import rehber_giris as RG

VERI = os.path.join(ROBOT, "rehber", "veri")
V = json.load(open(os.path.join(VERI, "rehber-veri.json"), encoding="utf-8"))
t0 = time.time()
D = RS.Denetim(V, os.path.join(VERI, "robot.glb"))
print("yukleme %.1f s, %d parca" % (time.time() - t0, D.N))
K = D.ID
P = D.P
sonuc = dict(kutu={}, dil={}, yol=[])

ilgili = ["p0205", "p0206", "p0207", "p0208", "p0209", "p0210", "p0211", "p0212", "p0213", "p0214", "p0215", "p0216",
          "p0219", "p0220", "p0221", "p0222", "p0223", "p0224", "p0229", "p0230"]
for i in ([] if os.environ.get("YALNIZ_YOL") else ilgili):
    p = P[K[i]]
    sonuc["kutu"][i] = dict(ad=p["ad"], bmin=[round(float(x), 1) for x in p["bmin"]], bmax=[round(float(x), 1) for x in p["bmax"]])
    print(i, p["ad"][:34].ljust(34), np.round(p["bmin"], 1), np.round(p["bmax"], 1))

# ---------------------------------------------------------------- dil / dudak: radyal ışınla hangisi içte
I = RG.Isinlar(P, 1.0, np.min([p["bmin"] for p in P], 0), np.max([p["bmax"] for p in P], 0))


def dil(a, b, eks, dis_isaret, kos, ad, tmin=None):
    if os.environ.get("YALNIZ_YOL"):
        return
    """a, b parçaları; eks: radyal ışın ekseni (dış = dis_isaret yönü); kos(x, y, z ışın satır merkezi) True ise satır sayılır.
    Her iki parçanın da bulunduğu ışın satırlarında hangisinin dış yüzü daha dışarıda. Döner sayımlar + örnek."""
    a1, a2 = [q for q in range(3) if q != eks]
    ra = I.ara(K[a], eks); rb = I.ara(K[b], eks)
    def tablo(r):
        t = {}
        for i_, j_, t0_, t1_ in zip(*r):
            t.setdefault((int(i_), int(j_)), []).append((float(t0_), float(t1_)))
        return t
    ta, tb = tablo(ra), tablo(rb)
    say = dict(a_dista=0, b_dista=0)
    ornek = None
    for key in ta.keys() & tb.keys():
        c = np.zeros(3)
        c[a1] = I.lo[a1] + (key[0] + RG.KAYDIR) * I.h
        c[a2] = I.lo[a2] + (key[1] + RG.KAYDIR) * I.h
        if not kos(c):
            continue
        if tmin is not None:                                   # yalnız bu yüzün aralıkları (ön: t > tmin; arka: t < -tmin)
            sa = [x for x in ta[key] if (x[1] > tmin if dis_isaret > 0 else x[0] < -tmin)]
            sb = [x for x in tb[key] if (x[1] > tmin if dis_isaret > 0 else x[0] < -tmin)]
            if not sa or not sb:
                continue
            ta_k, tb_k = sa, sb
        else:
            ta_k, tb_k = ta[key], tb[key]
        # dış yüz: dış yöndeki en uç nokta
        fa = max(x[1] for x in ta_k) if dis_isaret > 0 else -min(x[0] for x in ta_k)
        fb = max(x[1] for x in tb_k) if dis_isaret > 0 else -min(x[0] for x in tb_k)
        if abs(fa - fb) < 0.3:
            continue
        if fa > fb:
            say["a_dista"] += 1
        else:
            say["b_dista"] += 1
        if ornek is None:
            ornek = dict(satir=[round(float(v), 1) for v in c], a=ta[key], b=tb[key])
    r = dict(ad=ad, a=P[K[a]]["ad"], b=P[K[b]]["ad"], eksen="xyz"[eks], dis=dis_isaret, **say,
             ornek=None if ornek is None else dict(satir=ornek["satir"], a=[[round(x, 2) for x in q] for q in ornek["a"]],
                                                   b=[[round(x, 2) for x in q] for q in ornek["b"]]))
    print("DIL", ad, r)
    sonuc["dil"][ad] = r


if not os.environ.get("YALNIZ_YOL"):
  pass
# yüz başına: ön (z ışını, t > 40), arka (z ışını, t < -40), yan (x ışını, |x| > 100)
for (a, b, y0, ad) in (("p0211", "p0213", 1005, "y1005 sağ (orta sağ / göğüs sağ)"), ("p0212", "p0214", 1005, "y1005 sol (orta sol / göğüs sol)"),
                       ("p0213", "p0215", 1198, "y1198 sağ (göğüs sağ / omuz sağ)"), ("p0214", "p0216", 1198, "y1198 sol (göğüs sol / omuz sol)")):
    sx = 1 if "sağ" in ad else -1
    k = lambda c, y0=y0: y0 + 1 <= c[1] <= y0 + 11
    dil(a, b, 2, +1, k, ad + " ön", tmin=40)
    dil(a, b, 2, -1, k, ad + " arka", tmin=40)
    dil(a, b, 0, sx, k, ad + " yan", tmin=100)
for (a, b, ad, sx) in (("p0221", "p0223", "z88 sağ (etek orta sağ / etek ön sağ)", 1), ("p0222", "p0224", "z88 sol (etek orta sol / etek ön sol)", -1)):
    dil(a, b, 0, sx, lambda c: 89 <= c[2] <= 99, ad + " yan", tmin=200)
    dil(a, b, 1, +1, lambda c: 89 <= c[2] <= 99, ad + " üst", tmin=200)
# çerçeve ↔ göğüs bandı: ön yüzde (t > 40) üst üste gelen satırlar; hangisi önde
dil("p0213", "p0229", 2, +1, lambda c: True, "çerçeve sağ / göğüs sağ ön", tmin=40)
dil("p0214", "p0230", 2, +1, lambda c: True, "çerçeve sol / göğüs sol ön", tmin=40)
if not os.environ.get("YALNIZ_YOL"):
    json.dump(sonuc, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
if os.environ.get("YALNIZ_DIL"):
    sys.exit(0)

# ---------------------------------------------------------------- giriş yolu: band kendi alt adımında, o ana kadar takılanlar engel
G = RG.Giris(P, h=0.5)
A = V["adimlar"]


def adim(kod):
    return next(s for s, a in enumerate(A) if a["kod"] == kod)


def yol(kod, grup_ad, pid, yonler, azami=260.0):
    s = adim(kod)
    for ad, tz, ids, izin in D.durumlar(s):
        if ad == grup_ad:
            break
    else:
        raise SystemExit("grup yok " + grup_ad)
    h = K[pid]
    E = [int(k) for k in np.nonzero(izin)[0] if k != h and k not in set(int(x) for x in ids)]
    # grubun öteki parçaları (braket, bağlantı) bantla birlikte takılır sayılmaz: bant önce gelir. Bunları ayrı raporla
    E2 = [int(x) for x in ids if int(x) != h]
    for u in yonler:
        t = time.time()
        r = G.yon([h], E, u, azami_mm=azami, tum=True)
        r2 = None                                                # grup içi (braket, cıvata) ölçülmedi: süre
        kayit = dict(adim=kod, grup=grup_ad, parca=P[h]["ad"], yon=list(u), serbest=r["serbest"], yol_mm=r["yol_mm"],
                     carpan=r["carpan"][:10], dinlenme=r["dinlenme"][:6], grup_ici=None if r2 is None else r2["carpan"][:6],
                     sure_s=round(time.time() - t, 1))
        sonuc["yol"].append(kayit)
        print("YOL", kod, P[h]["ad"], u, "serbest" if r["serbest"] else "carpar", r["yol_mm"],
              [(c["engel"][:38], c["derinlik_mm"], c["isin"]) for c in r["carpan"][:6]],
              "| dinlenme", [(c["engel"][:30], c["derinlik_mm"]) for c in r["dinlenme"][:3]],
              "| grup ici", None if r2 is None else [(c["engel"][:30], c["derinlik_mm"]) for c in r2["carpan"][:3]],
              "%.1f s" % (time.time() - t), flush=True)
        json.dump(sonuc, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


SEC = os.environ.get("SEC", "")
_yol = yol
def yol(kod, grup_ad, pid, yonler, azami=260.0):
    if SEC and pid not in SEC.split(","):
        return
    _yol(kod, grup_ad, pid, yonler, azami)
yol("F3", "Göğüs bandı sağ + y 1095 braketi", "p0213", [(1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, -1)])
yol("F3", "Göğüs bandı sol + y 1095 braketi", "p0214", [(-1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, -1)])
yol("F1", "Ön sağ bant", "p0223", [(1, 0, 1), (1, 0, 0), (0, 1, 0), (0, 0, 1)])
yol("F1", "Ön sol bant", "p0224", [(-1, 0, 1), (-1, 0, 0), (0, 1, 0), (0, 0, 1)])
yol("F3", "Göğüs ekranı çerçevesi", "p0229", [(0, 0, 1), (1, 0, 0), (0, 1, 0)])
yol("F3", "Göğüs ekranı çerçevesi", "p0230", [(0, 0, 1), (-1, 0, 0), (0, 1, 0)])
yol("F4", "Omuz bandı sağ", "p0215", [(1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, -1)])
yol("F4", "Omuz bandı sol, ön dikiş", "p0216", [(-1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, -1)])
json.dump(sonuc, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("bitti %.1f s" % (time.time() - t0))
