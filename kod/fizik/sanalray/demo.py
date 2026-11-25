"""Sanal ray 3B gösterimi: MuJoCo penceresinde LiDAR'sız gezinme (kamera + etiket + enkoder + ön sonar).

    kod\\sanalray.bat [koridor_3] [ab|kayip] [--kafa tarayan] [--aralik 5] [--donus 0.14]
    %V% kod\\fizik\\sanalray\\demo.py --koridor koridor_3 --gorev ab [--ekran klasor] [--sure 40]

Pencerede: etiketler duvarda; yeşil küre hedef, mavi küre Beyin'in tahmini (gövde merkezi), sarı noktalar rota; sol
üstte mod, süre, konum hatası (yer gerçeği; yalnız gösterim), konum std, etiket ölçüm sayısı, sonar. Kafa kamerasının
işlenen görüntüsü (algılanan etiketler çerçeveli) pencerenin sağ altında; ayrıca `sonuc/ham/demo_kamera.png`
(saniyede bir). Gerçek zamanlı akar; pencere kapanınca biter. gorunum3b.py DEĞİŞMEDİ: yalnız pencere yakalama işlevi
(`pencere_yakala`) kullanılır."""

import argparse
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sanalray import _yol  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--koridor", default="koridor_3")
    ap.add_argument("--gorev", default="ab", choices=["ab", "kayip"])
    ap.add_argument("--kafa", default="sabit", choices=["sabit", "tarayan"])
    ap.add_argument("--aralik", default="5")
    ap.add_argument("--donus", type=float, default=0.14)
    ap.add_argument("--birak", type=int, default=0)
    ap.add_argument("--hedef", default=None)
    ap.add_argument("--hiz", type=float, default=1.0, help="sanal / gerçek süre")
    ap.add_argument("--ekran", default=None, help="ekran görüntüsü klasörü (5. / 15. / 30. sanal saniye)")
    ap.add_argument("--sure", type=float, default=None, help="bu kadar sanal saniye sonra kapat")
    a = ap.parse_args()
    _yol.dusuk_oncelik()
    import cv2
    import mujoco
    import mujoco.viewer
    import numpy as np
    from gezinme import rota as R, senaryo_ab as SA, senaryo_ortak as SO
    from gezinme.duzenek import Duzenek
    from sanalray import deney as DN, etiket as E, kamera as KM
    from sanalray.algilayici import Algilayicilar, SensorBeyni
    from sanalray.beyin import SanalRayBeyni
    import dunya as D
    import random
    ar = a.aralik if a.aralik == "kavsak" else int(float(a.aralik))
    kor = a.koridor
    plan = E.plan_oku(kor, ar, 0.15, "goz")
    etk = DN.tum_etiketler(ar, 0.15, "goz")
    if a.gorev == "ab":
        s = D.sahne_oku(kor)
        b = s["baslangic"]
        bilinen = (float(b["x"]), float(b["y"]), math.radians(float(b.get("aci_derece", 0))))
        bas = SO.baslangic_sapmasi(bilinen, random.Random(10000 + 31 + 7 * SO.KORIDORLAR.index(kor)))
        tam, hxy = R.durak_coz(kor, a.hedef or SA.hedefler(kor)[-1])
    else:
        rng = random.Random(20000 + 100 * SO.KORIDORLAR.index(kor) + a.birak)
        bas = SO.rastgele_birak(kor, rng)
        goreli = "kapi_%d" % rng.randint(1, 3)
        tam, hxy = R.durak_coz(kor, goreli)
    dz = Duzenek(E.etiketli_sahne(kor, plan), tohum=1, baslangic=bas)
    k_d, k_o = DN.odometri_oranlari()
    alg = Algilayicilar(dz, "std", "1152x648", tohum=5, donus_fazlasi=a.donus, dogal_donus=k_d, dogal_oteleme=k_o)
    if a.gorev == "ab":
        beyin = SanalRayBeyni(etk, alg.K, gorev="ab", koridor=kor, baslangic=bilinen, hedef=tam, kafa=a.kafa)
    else:
        beyin = SanalRayBeyni(etk, alg.K, gorev="kayip", hedef=goreli, kafa=a.kafa)
    sb = SensorBeyni(beyin, alg)
    hakem = DN.YanalHakem(hxy, beyin.yol, beyin)
    m, d = dz.w.m, dz.w.d
    bul = KM.Bulucu()
    durum = {"duvar0": None, "t0": None, "son_png": -1e9, "ekran": set(), "kare": None}
    viewer = mujoco.viewer.launch_passive(m, d, show_left_ui=False, show_right_ui=False)
    viewer.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    viewer.cam.distance, viewer.cam.elevation = 9.0, -72.0     # 2,7 m görsel duvarların üstünden bakar
    viewer.opt.geomgroup[2] = 1
    if a.ekran:
        os.makedirs(a.ekran, exist_ok=True)

    def kamera_resmi():
        k = alg._kare
        if k is None and durum["kare"] is None:
            return None
        g = (k or durum["kare"])[1]
        durum["kare"] = (0, g)
        im = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
        for kimlik, c in bul.bul(g):
            cv2.polylines(im, [c.astype(np.int32)], True, (0, 255, 0), 3)
            cv2.putText(im, str(kimlik), tuple(int(v) for v in c[0]), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        return im

    def isaret(scn, p, rgba, r=0.08):
        if scn.ngeom >= scn.maxgeom:
            return
        mujoco.mjv_initGeom(scn.geoms[scn.ngeom], mujoco.mjtGeom.mjGEOM_SPHERE, np.array([r, 0, 0]),
                            np.array(p, float), np.eye(3).ravel(), np.array(rgba, np.float32))
        scn.ngeom += 1

    def olay(dz_, t):
        alg.olay(dz_, t)
        hakem_g = dz_.gercek_poz()
        if durum["t0"] is None:
            durum["t0"], durum["duvar0"] = t, time.perf_counter()
        # gerçek zaman
        hedef_duvar = durum["duvar0"] + (t - durum["t0"]) / a.hiz
        bekle = hedef_duvar - time.perf_counter()
        if bekle > 0:
            time.sleep(min(bekle, 0.2))
        if not viewer.is_running():
            raise KeyboardInterrupt
        with viewer.lock():
            viewer.cam.lookat[:] = (hakem_g[0], hakem_g[1], 0.8)
            scn = viewer.user_scn
            scn.ngeom = 0
            isaret(scn, (hxy[0], hxy[1], 0.05), (0.1, 0.9, 0.2, 0.9), 0.12)
            p = beyin.ekf.govde()
            if p is not None:
                isaret(scn, (p[0], p[1], 1.7), (0.2, 0.4, 1.0, 0.8), 0.1)
            for q in (beyin.yol or [])[:60]:
                isaret(scn, (q[0], q[1], 0.03), (1.0, 0.85, 0.1, 0.9), 0.04)
            st = beyin.ekf.std()
            hata = math.hypot(p[0] - hakem_g[0], p[1] - hakem_g[1]) if p else float("nan")
            metin = ("sanal ray (LiDAR YOK) %s %s, kafa %s, etiket %s m\nmod %s  t %.1f s\nkonum hatasi (yer gercegi) %.3f m\n"
                     "konum std %s m, donus olcegi %s\netiket olcum %d, ret %d\nsonar %.2f m" %
                     (kor, a.gorev, a.kafa, ar, beyin.durum()["mod"], t, hata, ("%.3f" % st[0]) if st else "-",
                      ("%.3f" % beyin.ekf.olcek()) if beyin.ekf.hazir else "-", beyin.olcum_sayisi, beyin.ret_sayisi,
                      alg.sonar if alg.sonar is not None and math.isfinite(alg.sonar) else -1))
            try:
                viewer.set_texts((mujoco.mjtFontScale.mjFONTSCALE_150, mujoco.mjtGridPos.mjGRID_TOPLEFT, metin, ""))
            except Exception:
                pass
            if t - durum["son_png"] >= 1.0:
                durum["son_png"] = t
                im = kamera_resmi()
                if im is not None:
                    ok, buf = cv2.imencode(".png", im)
                    with open(os.path.join(_yol.HAM, "demo_kamera.png"), "wb") as f:
                        f.write(buf.tobytes())
                    try:
                        kucuk = cv2.resize(cv2.cvtColor(im, cv2.COLOR_BGR2RGB), (480, 270))
                        viewer.set_images((mujoco.MjrRect(0, 0, 480, 270), np.ascontiguousarray(np.flipud(kucuk))))
                    except Exception:
                        pass
        viewer.sync()
        if a.ekran:
            for s_ in (5, 15, 30):
                if t >= s_ and s_ not in durum["ekran"]:
                    durum["ekran"].add(s_)
                    import gorunum3b as G
                    G.pencere_yakala(os.path.join(a.ekran, "sanalray-%s-%03ds-pencere.png" % (kor, s_)))
        if a.sure is not None and t >= a.sure:
            raise KeyboardInterrupt

    os.makedirs(_yol.HAM, exist_ok=True)
    try:
        sonuc = dz.kos(sb, 400.0, hakem=hakem, olay=olay)
        print({k: sonuc[k] for k in ("bitis", "sure_s", "temas_olay", "son_gercek", "son_tahmin")})
    except KeyboardInterrupt:
        pass
    finally:
        try:
            viewer.close()
        except Exception:
            pass
        alg.kapat()
    return 0


if __name__ == "__main__":
    sys.exit(main())
