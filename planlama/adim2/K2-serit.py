# K2 (3. ajan): S1 U lopu R_min sert kablo kalinligina (tek tel / serit kalinligi d, 3 serit radyal yigin) gore. Yalniz hesap
# (K2-u.py bagimsiz cozucu; geometri arayuz.KOL_KABLO["s1"]: tambur r 39, duvar r 75,2, bag psi 145, duvar bagi 228,3, L 171,4).
# Ayrica duvar disa kaydirilmis (h buyuk) varyant: L, U ucu/kosu acisi korunsun diye dis kosu yay boyu kadar uzatilir (yaklasik).
import os, math, json, time, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("k2u", os.path.join(HERE, "K2-u.py"))
U = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(U)
R_T, R_D, BAG, PSI_W, L = 39.0, 75.2, 145.0, 228.3, 171.4
out = dict(tarih=time.strftime("%Y-%m-%dT%H:%M:%S"), satir=[])
for dr in (0.0, 3.0, 4.6, 6.0):
    for d in (1.4, 1.5, 1.6, 1.7, 1.8):
        if dr and d not in (1.6, 1.7):
            continue
        ri, ro = R_T + 1.5 * d, R_D + dr - 1.5 * d
        Ld = L + dr * math.radians(110.0)            # dis kosu ~110 derece yay (yaklasik) + U yari cevre farki kucuk
        Ld += dr * math.pi / 2 * 0.8
        for phi in (-45, 45, 135):
            c = U.coz(ri, ro, BAG + phi, PSI_W, Ld, N=240)
            o = U.ozet(c)
            sinir = 7.5 * d + d                     # 3 serit: 7,5 d + (n-1) d/2
            out["satir"].append(dict(d=d, duvar_dr=dr, phi=phi, L=round(Ld, 1), ok=c["ok"], R_min=round(o["R_min"], 3),
                                     sinir_7_5d=round(sinir, 2), a_ic=round(o["a_ic"], 1), a_dis=round(o["a_dis"], 1),
                                     u_uc_psi=round(o["u_uc_psi"], 1), eksenel_3d=round(3 * d, 2)))
            print(out["satir"][-1], flush=True)
json.dump(out, open(os.path.join(HERE, "K2-serit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("bitti")
