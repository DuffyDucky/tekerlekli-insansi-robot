"""Y0f: dönüş karşılaştırma varyantları (`varyantlar.py`; V0 bugünkü robot, öbürleri VARSAYIM). Başsız, belirlenimci, protokol
üzerinden.

    "%LALE_SIM_VENV%\\Scripts\\python.exe" kod/fizik/olcum_varyantlar.py      # -> planlama/d158/Y0f-olcum/donus-varyantlar.json + .md

Her varyant x µ 0,5 / 0,8 x durma torku 21 / 9 kg·cm:
  - yerinde dönüş: sur v 0, w = varyantın w tavanı (V0 / V2 / V3 / V4: 1, V1: 3); 3 s sonra 1,5 s ortalaması; 90° süresi
  - yay: sur v 0,25, w = aynı tavan; gerçekleşen w, v, yarıçap
  - motor torku / sürekli tork (sürekli = durmanın %30'u, TAHMİN), yerinde dönüşte dört teker ortalamasının en büyüğü
  - kolonun etrafından dolaşma: oda_engelli, kolonun (3,2; 1,4) 0,9 m önünden üç ara noktaya (2,6; 2,25), (3,8; 2,25),
    (4,3; 1,4); basit yönlendirme (yön hatası > 20°: yerinde dön, değilse v 0,25 + orantılı w), 60 s, sonar kuralı açık
Yan etkiler (µ 0,8, 21 kg·cm): düz gidişte sapma (0,25 m/s, 6 s), `dur` ve acil stop (0,39 m/s'den) yolu ve yön sapması,
5° yan eğimde duruşta ve düz gidişte yan kayma.
"""

import json
import math
import os
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)
import olcumler as O  # noqa: E402
import varyantlar as VR  # noqa: E402

KOK = os.path.dirname(os.path.dirname(BURASI))
CIKTI = os.path.join(KOK, "planlama", "d158", "Y0f-olcum")
DURMA = {"21kgcm": 2.059, "9kgcm": 0.883}
SUREKLI_ORAN = 0.30          # sürekli tork = durmanın %30'u (fizik_parametreleri.json'daki gibi TAHMİN)
ARA_NOKTALAR = [(2.6, 2.25), (3.8, 2.25), (4.3, 1.4)]


def deney(vad, mu, durma, **kw):
    return O.Deney(degis={"teker_zemin_surtunme": mu, "motor_durma_torku_Nm": durma}, varyant=VR.al(vad), **kw)


def w_tavan(vad):
    v = VR.al(vad)
    return float(v["fw_w_giris"]) if v and v.get("fw_w_giris") else 1.0


def donus_kos(vad, mu, durma, v):
    dn = deney(vad, mu, durma)
    dn.devreye_al()
    w = w_tavan(vad)
    dn.e.sur_tut(v, w, 3000)
    dn.kayit_ac()
    dn.e.sur_tut(v, w, 1500)
    k = dn.kayit
    w_ort = sum(r["w"] for r in k) / len(k)
    v_ort = sum(r["v"] for r in k) / len(k)
    tork = [sum(abs(r["tork"][i]) for r in k) / len(k) for i in range(4)]
    r = dict(v_komut=v, w_komut=w, v_gercek=v_ort, w_gercek=w_ort,
             tork_ort_Nm=tork, tork_surekli_orani=max(tork) / (SUREKLI_ORAN * durma), tork_durma_orani=max(tork) / durma)
    if abs(w_ort) >= 0.01:                    # altı: dönmüyor (90° süresi ve yarıçap anlamsız)
        r.update(sure_90_s=(math.pi / 2) / abs(w_ort), yaricap_m=v_ort / w_ort)
    else:
        r.update(sure_90_s=None, yaricap_m=None)
    return r


def dolas_kos(vad, mu, durma, sinir_s=60.0):
    from sahte_esp32.harita import Harita
    harita = Harita.dosyadan(os.path.join(os.path.dirname(BURASI), "araclar", "haritalar", "oda_engelli.json"))
    dn = deney(vad, mu, durma, harita=harita, konum=(2.3, 1.4, 0.0), sonar_acik=True)
    dn.devreye_al()
    wmax = w_tavan(vad)
    i = 0
    t = 0.0
    while t < sinir_s and i < len(ARA_NOKTALAR):
        x, y, _, yaw, _, _ = dn.w.poz()
        hx, hy = ARA_NOKTALAR[i]
        if math.hypot(hx - x, hy - y) < 0.25:
            i += 1
            continue
        hata = math.atan2(hy - y, hx - x) - yaw
        hata = math.atan2(math.sin(hata), math.cos(hata))
        if abs(hata) > math.radians(20):
            v, w = 0.0, math.copysign(wmax, hata)
        else:
            v, w = 0.25, max(-wmax, min(wmax, 2.0 * hata))
        dn.e.sur_tut(v, w, 100)
        t += 0.1
    x, y, _, yaw, _, _ = dn.w.poz()
    return dict(basarili=i == len(ARA_NOKTALAR), ulasilan_ara_nokta=i, sure_s=t, son_konum=[x, y],
                carpisma=dn.c.carpisma_sayisi)


def yan_etki(vad):
    mu, durma = 0.8, 2.059
    r = {}
    # düz gidiş
    dn = deney(vad, mu, durma, konum=(10.0, 40.0, 0.0))
    dn.devreye_al()
    dn.e.sur_tut(0.25, 0.0, 6000)
    x, y, _, yaw, _, _ = dn.w.poz()
    r["duz_6s"] = dict(yol_m=x - 10.0, yan_sapma_m=y - 40.0, yon_sapmasi_derece=math.degrees(yaw))
    # dur ve acil stop, 0,39 m/s'den
    for durus in ("dur", "acil_stop"):
        dn = deney(vad, mu, durma, konum=(10.0, 40.0, 0.0))
        dn.devreye_al()
        dn.e.sur_tut(1.0, 0.0, 2500)
        x0, y0, _, yaw0, _, _ = dn.w.poz()
        v0 = dn.w.hiz()[0]
        if durus == "dur":
            dn.e.istek({"k": "dur"})
        else:
            dn.c.mantar = True
        dn.e.bekle(3000)
        x, y, _, yaw, _, _ = dn.w.poz()
        r[durus] = dict(v0_m_s=v0, yol_m=math.hypot(x - x0, y - y0), yan_sapma_m=y - y0,
                        yon_sapmasi_derece=math.degrees(yaw - yaw0))
    # yanal itme: düz gidişte (0,25 m/s) ön aks hizasına 0,3 s yanal 10 N (model simetrik olduğundan düz gidiş ve frenin
    # yön sütunları bozucu olmadan 0 çıkar; yön kararlılığını bu sütun gösterir)
    dn = deney(vad, mu, durma, konum=(10.0, 40.0, 0.0))
    dn.devreye_al()
    dn.e.sur_tut(0.25, 0.0, 2000)
    _, y0, _, yaw0, _, _ = dn.w.poz()
    xf = dn.w.d.xfrc_applied[dn.w.taban]
    xf[:] = [0.0, 10.0, 0.0, 0.0, 0.0, 10.0 * 0.185]   # kuvvet taban orijininde + ön aksa taşıma momenti (yaklaşık)
    dn.e.sur_tut(0.25, 0.0, 300)
    xf[:] = 0.0
    dn.e.sur_tut(0.25, 0.0, 3000)
    _, y, _, yaw, _, _ = dn.w.poz()
    r["yanal_itme"] = dict(kuvvet_N=10.0, sure_s=0.3, yan_kayma_m=y - y0, yon_sapmasi_derece=math.degrees(yaw - yaw0))
    # 5° yan eğim (yerçekimi -y'ye eğik: robotun sağı yokuş aşağı)
    g = 9.81
    for ad, v in (("yan_egim_5_durus", 0.0), ("yan_egim_5_duz_gidis", 0.25)):
        dn = deney(vad, mu, durma, konum=(10.0, 40.0, 0.0))
        dn.w.m.opt.gravity[:] = [0.0, -g * math.sin(math.radians(5)), -g * math.cos(math.radians(5))]
        dn.devreye_al()
        x0, y0, _, yaw0, _, _ = dn.w.poz()
        if v:
            dn.e.sur_tut(v, 0.0, 5000)
        else:
            dn.e.istek({"k": "dur"})
            for _ in range(10):
                dn.e.ping()
                dn.e.bekle(500)
        x, y, _, yaw, _, _ = dn.w.poz()
        r[ad] = dict(yol_m=x - x0, yan_kayma_m=y - y0, yon_sapmasi_derece=math.degrees(yaw - yaw0), sure_s=5.0)
    return r


def main():
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    sonuc = dict(varyantlar={k: dict(ad=v["ad"], aciklama=v["aciklama"]) for k, v in VR.VARYANTLAR.items()}, kosular=[], yan_etki={})
    for vad in VR.SIRA:
        for dad, st in DURMA.items():
            for mu in (0.5, 0.8):
                yer = donus_kos(vad, mu, st, 0.0)
                yay = donus_kos(vad, mu, st, 0.25)
                dol = dolas_kos(vad, mu, st)
                sonuc["kosular"].append(dict(varyant=vad, durma=dad, mu=mu, yerinde=yer, yay=yay, dolasma=dol))
                print("%-6s %s mu %.1f | yerinde w %.3f (tork/surekli %.1f) | yay v %.3f w %.3f | dolasma %s %.1f s"
                      % (vad, dad, mu, yer["w_gercek"], yer["tork_surekli_orani"], yay["v_gercek"], yay["w_gercek"],
                         "BASARILI" if dol["basarili"] else "basarisiz(%d/3)" % dol["ulasilan_ara_nokta"], dol["sure_s"]), flush=True)
        sonuc["yan_etki"][vad] = yan_etki(vad)
        print("%-6s yan etki %s" % (vad, json.dumps(sonuc["yan_etki"][vad], sort_keys=True)), flush=True)
    os.makedirs(CIKTI, exist_ok=True)
    with open(os.path.join(CIKTI, "donus-varyantlar.json"), "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=1, sort_keys=True)
    with open(os.path.join(CIKTI, "donus-varyantlar.md"), "w", encoding="utf-8") as f:
        f.write(md(sonuc))
    print("yazıldı: planlama/d158/Y0f-olcum/donus-varyantlar.json + .md")


def s(x, f="%.2f"):
    return "-" if x is None else (f % x).replace(".", ",")


def md(o):
    L = ["# Dönüş varyantları (Y0f, `kod/fizik/olcum_varyantlar.py`)", "",
         "V0 bugünkü robot; öbürleri **VARSAYIM** (`kod/fizik/varyantlar.py`, modelleme yöntemi orada). Başsız, protokol üzerinden; "
         "3 s sonra 1,5 s ortalaması. w komutu varyantın tavanı (V1: 3, öbürleri 1). Tork oranı: yerinde dönüşte en yüklü tekerin "
         "ortalama torku / sürekli tork (durmanın %30'u, TAHMİN); > 1 ısınma, ≈ 3,3 durma.", ""]
    for k, v in o["varyantlar"].items():
        L.append("- **%s**: %s" % (k, v["aciklama"]))
    L += ["", "| varyant | durma | µ | yerinde w rad/s | 90° s | tork / sürekli | yay (v 0,25) v / w | yarıçap m | kolon dolaşma |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in o["kosular"]:
        y, a, d = r["yerinde"], r["yay"], r["dolasma"]
        L.append("| %s | %s | %s | %s | %s | %s | %s / %s | %s | %s |" % (
            r["varyant"], r["durma"], s(r["mu"], "%.1f"), s(y["w_gercek"], "%.3f"), s(y["sure_90_s"], "%.1f"),
            s(y["tork_surekli_orani"], "%.1f"), s(a["v_gercek"], "%.3f"), s(a["w_gercek"], "%.3f"), s(a["yaricap_m"]),
            ("başarılı, %s s" % s(d["sure_s"], "%.1f")) if d["basarili"] else "başarısız (%d / 3 ara nokta, 60 s)" % d["ulasilan_ara_nokta"]))
    L += ["", "## Yan etkiler (µ 0,8, 21 kg·cm)", "",
          "Model sol-sağ simetrik: düz gidiş, dur ve acil stopta yön sapması bozucu olmadan 0 çıkar (gerçek robotta motor ve "
          "zemin farkı sapma yaratır). Yön kararlılığını yanal itme sütunu gösterir. Yan eğim: yerçekimi robotun sağına eğik.", "",
          "| varyant | düz 6 s: yan sapma m / yön ° | yanal itme 10 N 0,3 s, 3 s sonra: yan m / yön ° | dur (0,39'dan): yol m / yön ° | acil stop: yol m / yön ° | 5° yan eğim duruş 5 s: yan kayma m / yön ° | 5° yan eğim düz 5 s: yan kayma m / yön ° |",
          "| --- | --- | --- | --- | --- | --- | --- |"]
    for k, e in o["yan_etki"].items():
        L.append("| %s | %s / %s | %s / %s | %s / %s | %s / %s | %s / %s | %s / %s |" % (
            k, s(e["duz_6s"]["yan_sapma_m"], "%.3f"), s(e["duz_6s"]["yon_sapmasi_derece"], "%.1f"),
            s(e["yanal_itme"]["yan_kayma_m"], "%.3f"), s(e["yanal_itme"]["yon_sapmasi_derece"], "%.1f"),
            s(e["dur"]["yol_m"], "%.3f"), s(e["dur"]["yon_sapmasi_derece"], "%.1f"),
            s(e["acil_stop"]["yol_m"], "%.3f"), s(e["acil_stop"]["yon_sapmasi_derece"], "%.1f"),
            s(e["yan_egim_5_durus"]["yan_kayma_m"], "%.3f"), s(e["yan_egim_5_durus"]["yon_sapmasi_derece"], "%.1f"),
            s(e["yan_egim_5_duz_gidis"]["yan_kayma_m"], "%.3f"), s(e["yan_egim_5_duz_gidis"]["yon_sapmasi_derece"], "%.1f")))
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
