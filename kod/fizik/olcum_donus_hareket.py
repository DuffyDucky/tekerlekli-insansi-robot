"""Y0f: hareket hâlinde dönüş (yay) ve ileri-geri manevra ölçümü. Başsız, belirlenimci; protokol üzerinden (Pi istemcisi ->
bellek taşıması -> sahte ESP32 firmware modeli -> MuJoCo). Robotun / firmware'in davranışı değişmez.

    "%LALE_SIM_VENV%\\Scripts\\python.exe" kod/fizik/olcum_donus_hareket.py      # -> planlama/d158/Y0f-olcum/donus-hareket.json + .md

1. Yay tablosu: v 0,1 / 0,2 / 0,3 / -0,2 m/s x w 0,1 / 0,25 / 0,5 / 1,0 rad/s x µ 0,5 / 0,8 x durma torku 21 / 9 kg·cm. 3 s sür,
   sonraki 1,5 s ortalaması: gerçekleşen w ve v, yarıçap, 90° süresi ve yolu; firmware'in teker hedefleri, PWM, teker hızları,
   yan torkları (karışımın nereye gittiği).
2. Manevra: oda_engelli haritasında kolonun önünde, 1,5 s ileri-sol + 1,5 s geri-sağ tekrarı (penceredeki tuşlarla aynı komut:
   Yukarı+Sol = v 0,25 / w +1, Aşağı+Sağ = v -0,25 / w -1) ve yönü tutarlı karşılaştırma (geri-sol: v -0,25 / w +1); 45° ve 90°'ye
   kaç tekrar ve kaç saniye.
"""

import json
import math
import os
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)
import olcumler as O  # noqa: E402

KOK = os.path.dirname(os.path.dirname(BURASI))
CIKTI = os.path.join(KOK, "planlama", "d158", "Y0f-olcum")
DURMA = {"21kgcm": 2.059, "9kgcm": 0.883}
IZ = 0.432                       # fiziksel iz (teker merkezleri); firmware karışımı 0,426 ile


def yay_kos(v, w, mu, durma, sure=3000, olc=1500):
    O.TAKIM["_g"] = {"teker_zemin_surtunme": mu, "motor_durma_torku_Nm": durma}
    dn = O.Deney(degis=O.TAKIM["_g"])
    del O.TAKIM["_g"]
    dn.devreye_al()
    dn.e.sur_tut(v, w, sure)
    dn.kayit_ac()
    dn.e.sur_tut(v, w, olc)
    k = dn.kayit
    w_ort = sum(r["w"] for r in k) / len(k)
    v_ort = sum(r["v"] for r in k) / len(k)
    rt = dn.c.teker_capi / 2.0
    tv = dn.w.teker_hizlari()                         # on_sol, arka_sol, on_sag, arka_sag (rad/s)
    yuzey = [(tv[0] + tv[1]) / 2 * rt, (tv[2] + tv[3]) / 2 * rt]
    zemin = [v_ort - w_ort * IZ / 2, v_ort + w_ort * IZ / 2]
    tork = dn.w.son_tork
    sur, pwm = dn.c._surucu()
    w_fw = (dn.c.hedef[1] - dn.c.hedef[0]) / dn.c.fw_iz
    sonuc = dict(v_komut=v, w_komut=w, mu=mu, durma_torku_Nm=durma,
                 firmware_teker_hedefi_m_s=list(dn.c.hedef), firmware_pwm=list(pwm),
                 firmware_hedef_v=(dn.c.hedef[0] + dn.c.hedef[1]) / 2, firmware_hedef_w=w_fw,
                 v_gercek=v_ort, w_gercek=w_ort, w_orani=(w_ort / w_fw) if w_fw else None,
                 teker_yuzey_hizi_m_s=yuzey, teker_altinda_zemin_hizi_m_s=zemin,
                 yan_tork_Nm=[(tork[0] + tork[1]) / 2, (tork[2] + tork[3]) / 2])
    if abs(w_ort) > 1e-3:
        sonuc.update(yaricap_m=v_ort / w_ort, sure_90_s=(math.pi / 2) / abs(w_ort), yol_90_m=abs(v_ort) * (math.pi / 2) / abs(w_ort))
    else:
        sonuc.update(yaricap_m=None, sure_90_s=None, yol_90_m=None)
    return sonuc


def manevra_kos(ikinci_w, faz_ms=1500, en_cok=20, mu=0.8, durma=2.059, sonar_acik=True):
    """Kolonun (oda_engelli, (3,2; 1,4), r 0,25) 0,9 m önünde, kolona dönük. Tekrar: faz_ms ileri-sol (v 0,25, w +1), faz_ms
    geri (v -0,25, w = ikinci_w). Pencerenin komutu (tuşa basılı tutunca 200 ms'de bir sur), arada tuş bırakılır (dur)."""
    from sahte_esp32.harita import Harita
    harita = Harita.dosyadan(os.path.join(os.path.dirname(BURASI), "araclar", "haritalar", "oda_engelli.json"))
    O.TAKIM["_g"] = {"teker_zemin_surtunme": mu, "motor_durma_torku_Nm": durma}
    dn = O.Deney(degis=O.TAKIM["_g"], harita=harita, konum=(2.3, 1.4, 0.0), sonar_acik=sonar_acik)
    del O.TAKIM["_g"]
    dn.devreye_al()
    yaw0 = dn.w.poz()[3]
    t = 0.0
    tekrarlar = []
    ulasti = {}
    carpisma = 0
    for n in range(1, en_cok + 1):
        for v, w in ((0.25, 1.0), (-0.25, ikinci_w)):
            dn.e.sur_tut(v, w, faz_ms)
            dn.e.istek({"k": "dur"})
            dn.e.bekle(300)                       # tuşu bırakıp öbürüne geçme
            t += (faz_ms + 300) / 1000.0
        x, y, _, yaw, _, _ = dn.w.poz()
        d = math.degrees(math.atan2(math.sin(yaw - yaw0), math.cos(yaw - yaw0)))
        carpisma = dn.c.carpisma_sayisi
        tekrarlar.append(dict(tekrar=n, yon_degisimi_derece=d, x=x, y=y, sure_s=t, carpisma=carpisma))
        for hedef in (45, 90):
            if hedef not in ulasti and abs(d) >= hedef:
                ulasti[hedef] = dict(tekrar=n, sure_s=t)
    return dict(ikinci_faz=dict(v=-0.25, w=ikinci_w), faz_ms=faz_ms, mu=mu, durma_torku_Nm=durma, sonar_acik=sonar_acik,
                tekrarlar=tekrarlar, ulasilan=ulasti, en_cok_tekrar=en_cok)


def pencere_dizisi_kos(sonar_acik):
    """Pencere sınamasındaki tuş dizisi başsız (oda_engelli, başlangıç (1,5; 1,5; 0)): Yukarı 3 s, bırak 1,5 s, Sol 2 s, bırak
    1 s, Yukarı+Sol 2,5 s. Sonar kuralı (firmware TASLAK) açık / kapalı."""
    from sahte_esp32.harita import Harita
    harita = Harita.dosyadan(os.path.join(os.path.dirname(BURASI), "araclar", "haritalar", "oda_engelli.json"))
    dn = O.Deney(harita=harita, konum=(1.5, 1.5, 0.0), sonar_acik=sonar_acik)
    dn.devreye_al()
    for kom, ms in (((0.25, 0.0), 3000), (None, 1500), ((0.0, 1.0), 2000), (None, 1000), ((0.25, 1.0), 2500)):
        if kom is None:
            dn.e.istek({"k": "dur"})
            dn.e.bekle(ms)
        else:
            dn.e.sur_tut(kom[0], kom[1], ms)
    h = dn.c.hakem()
    return dict(sonar_acik=sonar_acik, x=dn.c.x, v_gercek=h["v"], w_gercek=h["w"], firmware_teker_hedefi_m_s=list(dn.c.hedef),
                firmware_ileri_sinir_m_s=dn.c._ileri_sinir(), sonar_cm=dict(dn.c.sonar))


def main():
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    yay = []
    for ad, st in DURMA.items():
        for mu in (0.5, 0.8):
            for v in (0.1, 0.2, 0.3, -0.2):
                for w in (0.1, 0.25, 0.5, 1.0):
                    r = yay_kos(v, w, mu, st)
                    r["durma"] = ad
                    yay.append(r)
                    print("yay %s mu %.1f v %+.2f w %.2f -> v %+.3f w %+.3f (fw w %.3f) pwm %s"
                          % (ad, mu, v, w, r["v_gercek"], r["w_gercek"], r["firmware_hedef_w"],
                             ["%.2f" % p for p in r["firmware_pwm"]]), flush=True)
    # dönmenin başladığı µ: hangi komut en iyi dönüşü verir (21 kg·cm)
    dusuk_mu = []
    for mu in (0.2, 0.3, 0.4):
        for v, w in ((0.0, 1.0), (0.1, 1.0), (0.2, 1.0), (0.2, 0.5), (0.3, 1.0)):
            r = yay_kos(v, w, mu, 2.059)
            dusuk_mu.append(r)
            print("dusuk mu %.1f v %+.2f w %.2f -> v %+.3f w %+.3f" % (mu, v, w, r["v_gercek"], r["w_gercek"]), flush=True)
    pencere = yay_kos(0.25, 1.0, 0.8, 2.059)        # penceredeki Yukarı+Sol, başsız
    pencere_dizisi = [pencere_dizisi_kos(s) for s in (True, False)]
    manevra = []
    for ikinci in (-1.0, 1.0):
        for mu in (0.5, 0.8):
            r = manevra_kos(ikinci, mu=mu)
            manevra.append(r)
            print("manevra ikinci w %+.1f mu %.1f -> %s, 20 tekrarda %.1f derece" % (ikinci, mu, r["ulasilan"], r["tekrarlar"][-1]["yon_degisimi_derece"]), flush=True)
    sonuc = dict(yay=yay, dusuk_mu=dusuk_mu, pencere_yukari_sol_bassiz=pencere, pencere_dizisi_bassiz=pencere_dizisi, manevra=manevra,
                 not_="ana parametreler (fizik_parametreleri.json) + µ ve durma torku değişkeni; 3 s sürüşten sonraki 1,5 s ortalaması; "
                      "firmware karışımı motorlar.cpp motorlar_hedef (v, w ±1 kırpma, iz 0,426, büyük teker 0,39'u aşarsa ikisi "
                      "birlikte ölçeklenir), teker_adim u = rampa_hiz / 0,39 (KP = 0)")
    os.makedirs(CIKTI, exist_ok=True)
    with open(os.path.join(CIKTI, "donus-hareket.json"), "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=1, sort_keys=True)
    with open(os.path.join(CIKTI, "donus-hareket.md"), "w", encoding="utf-8") as f:
        f.write(md(sonuc))
    print("yazıldı: planlama/d158/Y0f-olcum/donus-hareket.json + .md")


def s(x, f="%.3f"):
    return "-" if x is None else (f % x).replace(".", ",")


def md(o):
    L = ["# Hareket hâlinde dönüş (Y0f, `kod/fizik/olcum_donus_hareket.py`)", "",
         "Başsız, protokol üzerinden; 3 s sürüşten sonraki 1,5 s ortalaması. fw = firmware'in teker hedeflerinden (iz 0,426) "
         "beklediği. Yarıçap v / w; 90° süresi ve yolu gerçekleşen hızlarla.", "",
         "| durma | µ | v komut | w komut | fw sol / sağ hedef m/s | PWM sol / sağ | v gerçek | w gerçek | w / fw | yarıçap m | 90° s | 90° yol m |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in o["yay"]:
        L.append("| %s | %s | %s | %s | %s / %s | %s / %s | %s | %s | %s | %s | %s | %s |" % (
            r["durma"], s(r["mu"], "%.1f"), s(r["v_komut"], "%+.2f"), s(r["w_komut"], "%.2f"),
            s(r["firmware_teker_hedefi_m_s"][0]), s(r["firmware_teker_hedefi_m_s"][1]),
            s(r["firmware_pwm"][0], "%.2f"), s(r["firmware_pwm"][1], "%.2f"), s(r["v_gercek"]), s(r["w_gercek"]),
            s(r["w_orani"], "%.2f"), s(r["yaricap_m"], "%.2f"), s(r["sure_90_s"], "%.1f"), s(r["yol_90_m"], "%.2f")))
    p = o["pencere_yukari_sol_bassiz"]
    L += ["", "## Penceredeki Yukarı+Sol (v 0,25, w 1), başsız", "",
          "fw hedef %s / %s m/s, PWM %s / %s; v gerçek %s, w gerçek %s; teker yüzey hızı sol / sağ %s / %s m/s, teker altındaki "
          "zemin hızı %s / %s m/s; yan torku sol / sağ %s / %s N·m." % (
              s(p["firmware_teker_hedefi_m_s"][0]), s(p["firmware_teker_hedefi_m_s"][1]), s(p["firmware_pwm"][0], "%.2f"),
              s(p["firmware_pwm"][1], "%.2f"), s(p["v_gercek"]), s(p["w_gercek"]), s(p["teker_yuzey_hizi_m_s"][0]),
              s(p["teker_yuzey_hizi_m_s"][1]), s(p["teker_altinda_zemin_hizi_m_s"][0]), s(p["teker_altinda_zemin_hizi_m_s"][1]),
              s(p["yan_tork_Nm"][0]), s(p["yan_tork_Nm"][1]))]
    L += ["", "Aynı tuş dizisi başsız (Yukarı 3 s, bırak, Sol 2 s, bırak, Yukarı+Sol 2,5 s; oda_engelli, kolona doğru):", ""]
    for r in o["pencere_dizisi_bassiz"]:
        L.append("- sonar kuralı %s: x %s m, v gerçek %s, w gerçek %s, firmware ileri sınırı %s m/s, sonar %s cm" % (
            "açık" if r["sonar_acik"] else "kapalı", s(r["x"], "%.2f"), s(r["v_gercek"]), s(r["w_gercek"]),
            s(r["firmware_ileri_sinir_m_s"], "%.2f"), r["sonar_cm"]))
    L += ["", "## Dönmenin başladığı µ (21 kg·cm)", "", "| µ | v komut | w komut | v gerçek | w gerçek | yarıçap m |",
          "| --- | --- | --- | --- | --- | --- |"]
    for r in o["dusuk_mu"]:
        L.append("| %s | %s | %s | %s | %s | %s |" % (s(r["mu"], "%.1f"), s(r["v_komut"], "%+.2f"), s(r["w_komut"], "%.2f"),
                                                  s(r["v_gercek"]), s(r["w_gercek"]), s(r["yaricap_m"], "%.2f")))
    L += ["", "## Manevra (kolonun önünde, 1,5 s ileri-sol + 1,5 s geri, 20 tekrara dek)", "",
          "| ikinci faz | µ | 45° | 90° | 20 tekrar sonunda yön ° | çarpışma |", "| --- | --- | --- | --- | --- | --- |"]
    for r in o["manevra"]:
        u = r["ulasilan"]
        f = lambda h: ("%d tekrar, %.0f s" % (u[h]["tekrar"], u[h]["sure_s"])) if h in u else "ulaşılmadı"
        L.append("| v -0,25 / w %s | %s | %s | %s | %s | %d |" % (s(r["ikinci_faz"]["w"], "%+.0f"), s(r["mu"], "%.1f"), f(45), f(90),
                                                         s(r["tekrarlar"][-1]["yon_degisimi_derece"], "%.1f"), r["tekrarlar"][-1]["carpisma"]))
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
