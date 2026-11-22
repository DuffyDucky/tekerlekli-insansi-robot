"""Y0f: öneri firmware (dal oneri/donus-omni, `motorlar.cpp`) + ön omni teker ölçümü. VARSAYIM; varsayılan V0 değişmez.
Başsız, belirlenimci, protokol üzerinden.

    "%LALE_SIM_VENV%\\Scripts\\python.exe" kod/fizik/olcum_oneri.py      # -> planlama/d158/Y0f-olcum/donus-oneri.json + .md

Varyantlar: V0 (bugünkü), ONERI (öneri firmware + ön omni, makara yanal sürtünmesi 0,05), ONERI-T (öneri firmware + bugünkü
lastikler). µ 0,5 / 0,8 x 21 / 9 kg·cm:
  - yerinde dönüş, w komutu 0,5 / 1 / 1,5 (firmware w'yi 1'e kırpar): 3 s sonra 1,5 s ortalaması; tork / sürekli (durma x 0,3)
  - yay v 0,25 + w 0,5 / 1
  - 90°: yerinde w 1, yön 90°'yi geçince `dur`; süre, 2 s sonra son yön (aşma), açısal hızın tepe / kararlı oranı
  - kolonu dolaşma (olcum_varyantlar.dolas_kos ile aynı)
Yan etkiler, rampa (5° / 10° tutma, rampa kipi), eşik (5 / 10 / 15 mm, v 0,2 ve 0,39) µ 0,8, 21 kg·cm (eşik ayrıca 9 kg·cm).
Duyarlılık (ONERI, yerinde w 1 ve 5° yan eğimde düz gidiş, µ 0,8, 21 kg·cm): makara yanal sürtünmesi 0 / 0,05 / 0,15, kazançlar,
integral sınırı, enkoder tekeri ve çözünürlüğü, temas / çözücü ayarları (B'nin § 11 yöntemi).
"""

import json
import math
import os
import statistics as st
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)
import mujoco  # noqa: E402
import olcumler as O  # noqa: E402
import olcum_varyantlar as OV  # noqa: E402
import varyantlar as VR  # noqa: E402

CIKTI = OV.CIKTI
DURMA = OV.DURMA
VARS = ["V0", "ONERI", "ONERI-T", "ONERI-ADAY"]
# Yanlış alarm gözlemi (enkoder arızası koruması): ölçümleri değiştirmez, yalnız koruma tetiklenirse hangi ölçümde kaydeder.
import fizik_esp32 as FE  # noqa: E402
ALARM = []
AKTIF = ["-"]
_oneri_adim_asil = FE.FizikEsp32._oneri_adim


def _oneri_adim_izle(self):
    once = list(self._oneri["arizali"])
    _oneri_adim_asil(self)
    for k in range(2):
        if self._oneri["arizali"][k] and not once[k]:
            ALARM.append(dict(olcum=AKTIF[0], yan=("sol", "sag")[k], ms=self.ms))


FE.FizikEsp32._oneri_adim = _oneri_adim_izle
ACIK_ADAY = dict(VR.VARYANTLAR["V3"], **VR.ADAY_TEKER)     # bugünkü açık çevrim firmware + aday omni (karşılaştırma)
MAKARA_TARAMA = (0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.60)


def duz_kos(var, mu=0.8, durma=2.059):
    """Düz 0,25 m/s, 4 s sonra 2 s: hız, aks başına ortalama |tork|, ön / arka tekerin çevre hızı / gövde hızı."""
    dn = OV.deney(var, mu, durma)
    dn.devreye_al()
    dn.e.sur_tut(0.25, 0.0, 4000)
    dn.kayit_ac()
    dn.e.sur_tut(0.25, 0.0, 2000)
    k = dn.kayit
    r_on = float(dn.w.m.geom_size[dn.w.teker_geom[0], 0])
    r_arka = float(dn.w.m.geom_size[dn.w.teker_geom[1], 0])
    v = st.mean(r["v"] for r in k)
    return dict(v=v, tork_on_Nm=st.mean((abs(r["tork"][0]) + abs(r["tork"][2])) / 2 for r in k),
                tork_arka_Nm=st.mean((abs(r["tork"][1]) + abs(r["tork"][3])) / 2 for r in k),
                on_cevre_orani=st.mean((r["wt"][0] + r["wt"][2]) / 2 for r in k) * r_on / v,
                arka_cevre_orani=st.mean((r["wt"][1] + r["wt"][3]) / 2 for r in k) * r_arka / v,
                yon_derece=math.degrees(dn.w.poz()[3]))


def devrilme_payi(var):
    """Statik devrilme eğimi (geometri): yerleşmiş robotta tekerlerin temas noktalarından destek dörtgeni, AM'nin ona uzaklığı /
    AM yüksekliği. Silindir tekerde dış temas noktası, kürede tek nokta. (olcumler statik devrilmesi gövde döndürerek ölçer;
    burada yalnız karşılaştırma için.)"""
    dn = OV.deney(var, 0.8, 2.059)
    w = dn.w
    x0, y0 = w.poz()[0], w.poz()[1]              # robot (10, 40)'da: her şey robota göre
    am = [w.am()[0] - x0, w.am()[1] - y0, w.am()[2]]
    noktalar = {}
    for i in range(w.d.ncon):
        c = w.d.contact[i]
        for k, g in enumerate(w.teker_geom):
            if g in (c.geom1, c.geom2):
                p = (float(c.pos[0]) - x0, float(c.pos[1]) - y0)
                o = noktalar.get(k)
                if o is None or abs(p[1]) > abs(o[1]):
                    noktalar[k] = p
    on = [noktalar[0], noktalar[2]]
    arka = [noktalar[1], noktalar[3]]
    z = am[2]
    ileri = math.degrees(math.atan2(min(p[0] for p in on) - am[0], z))
    geri = math.degrees(math.atan2(am[0] - max(p[0] for p in arka), z))

    def kenar(a, b):
        (x1, y1), (x2, y2) = a, b
        return abs((x2 - x1) * (y1 - am[1]) - (x1 - am[0]) * (y2 - y1)) / math.hypot(x2 - x1, y2 - y1)
    yana = math.degrees(math.atan2(min(kenar(noktalar[0], noktalar[1]), kenar(noktalar[2], noktalar[3])), z))
    return dict(am_mm=[a * 1000 for a in am], ileri_derece=ileri, geri_derece=geri, yana_derece=yana,
                on_temas_y_mm=abs(on[0][1]) * 1000, kutle_kg=float(sum(w.m.body_mass)))


def makara_tarama():
    """ONERI-ADAY, yerinde w komutu 1: makara yanal sürtünmesi taranır (üretici değeri yok; rulmanlı / pirinç borulu)."""
    r = []
    n_teker = None
    for mu_yan in MAKARA_TARAMA:
        var = dict(VR.VARYANTLAR["ONERI-ADAY"], makara_mu_yan=mu_yan)
        for dad, durma in DURMA.items():
            for mu in (0.5, 0.8):
                y = yerinde(var, mu, durma, 0.0, 1.0)
                if n_teker is None:
                    dn = OV.deney(var, mu, durma)
                    n_teker = float(sum(dn.w.m.body_mass)) * 9.81 / 4.0
                r.append(dict(makara_mu_yan=mu_yan, yanal_kuvvet_N=mu_yan * n_teker, durma=dad, mu=mu, w_gercek=y["w_gercek"],
                              tork_surekli_orani=y["tork_surekli_orani"]))
                print("makara %.2f (%.1f N) %s mu %.1f | w %.3f tork/surekli %.1f" % (
                    mu_yan, mu_yan * n_teker, dad, mu, y["w_gercek"], y["tork_surekli_orani"]), flush=True)
    return r


def yerinde(var, mu, durma, v, w, degis=None, ayar=None):
    dn = OV.deney(var, mu, durma, degis=degis)
    if ayar:
        ayar(dn)
    dn.devreye_al()
    dn.e.sur_tut(v, w, 3000)
    dn.kayit_ac()
    dn.e.sur_tut(v, w, 1500)
    k = dn.kayit
    w_ort = st.mean(r["w"] for r in k)
    v_ort = st.mean(r["v"] for r in k)
    tork = max(st.mean(abs(r["tork"][i]) for r in k) for i in range(4))
    return dict(v_komut=v, w_komut=w, v_gercek=v_ort, w_gercek=w_ort, w_std=st.pstdev(r["w"] for r in k),
                tork_surekli_orani=tork / (0.3 * durma), yaricap_m=(v_ort / w_ort) if abs(w_ort) >= 0.01 else None)


def doksan(var, mu, durma):
    dn = OV.deney(var, mu, durma)
    dn.devreye_al()
    yaw0 = dn.w.poz()[3]
    dn.kayit_ac()

    def don(e):
        return abs(math.atan2(math.sin(dn.w.poz()[3] - yaw0), math.cos(dn.w.poz()[3] - yaw0))) >= math.radians(90)
    dn.e.sur_tut(0.0, 1.0, 20000, aralik_ms=10, dur_kosul=don)   # yön 10 ms'de bir denetlenir (200 ms'de aşmaya ≈ 6° eklenir)
    t90 = dn.kayit[-1]["t"] - dn.kayit[0]["t"]
    ulasti = don(None)
    n_dur = len(dn.kayit)
    dn.e.istek({"k": "dur"})
    dn.e.bekle(2000)
    k = dn.kayit
    son = math.degrees(dn.w.poz()[3] - yaw0)
    ws = [r["w"] for r in k[:n_dur]]                  # dur'a dek (dönerken)
    tepe = max(ws)
    kararli = st.mean(ws[len(ws) // 2:]) if ulasti else None   # dönüşün ikinci yarısı
    return dict(ulasti=ulasti, sure_90_s=t90 if ulasti else None, son_yon_derece=son, asma_derece=(son - 90.0) if ulasti else None,
                w_tepe=tepe, w_tepe_kararli_orani=(tepe / kararli) if kararli and kararli > 0.05 else None)


def aktif_deney(var):
    """olcumler'in rampa_kos / esik_kos'u Deney'i kendisi kurar: varyantı enjekte eden alt sınıf."""
    class _D(O.Deney):
        def __init__(self, *a, **k):
            k.setdefault("varyant", OV._var(var))
            super().__init__(*a, **k)
    return _D


def olcumler_ile(var, fn, *a):
    eski = O.Deney
    O.Deney = aktif_deney(var)
    try:
        return fn(*a)
    finally:
        O.Deney = eski


def yan_egim(var, degis=None):
    dn = OV.deney(var, 0.8, 2.059, degis=degis)
    g = 9.81
    dn.w.m.opt.gravity[:] = [0.0, -g * math.sin(math.radians(5)), -g * math.cos(math.radians(5))]
    dn.devreye_al()
    x0, y0, _, yaw0, _, _ = dn.w.poz()
    dn.e.sur_tut(0.25, 0.0, 5000)
    x, y, _, yaw, _, _ = dn.w.poz()
    return dict(yan_kayma_m=y - y0, yon_sapmasi_derece=math.degrees(yaw - yaw0))


def duyarlilik():
    r = []

    def ekle(ad, var, degis=None, ayar=None):
        y = yerinde(var, 0.8, 2.059, 0.0, 1.0, degis=degis, ayar=ayar)
        e = yan_egim(var, degis=degis) if ayar is None else None
        r.append(dict(ayar=ad, w_gercek=y["w_gercek"], w_std=y["w_std"], tork_surekli_orani=y["tork_surekli_orani"],
                      yan_egim_kayma_m=e["yan_kayma_m"] if e else None, yan_egim_yon_derece=e["yon_sapmasi_derece"] if e else None))
        print("duyarlilik %-34s w %.3f  yan egim %s" % (ad, y["w_gercek"], "-" if e is None else "%.3f m" % e["yan_kayma_m"]), flush=True)
    ekle("ana (makara 0,05, kp 4, ki 20)", "ONERI")
    ekle("makara yanal sürtünmesi 0 (ideal)", VR.oneri_varyanti(makara_mu_yan=0.0))
    ekle("makara yanal sürtünmesi 0,15", VR.oneri_varyanti(makara_mu_yan=0.15))
    ekle("makara yanal sürtünmesi 0,30", VR.oneri_varyanti(makara_mu_yan=0.30))
    ekle("kp 2, ki 10", VR.oneri_varyanti(kp=2.0, ki=10.0))
    ekle("kp 8, ki 40", VR.oneri_varyanti(kp=8.0, ki=40.0))
    ekle("kp 4, ki 0 (yalnız P)", VR.oneri_varyanti(ki=0.0))
    ekle("integral sınırı 0,3 (0.5.0 değeri)", VR.oneri_varyanti(integral_siniri=0.3))
    ekle("enkoder arızası koruması yok", VR.oneri_varyanti(duzeltme_orani=None))
    ekle("enkoder arka tekerde", "ONERI", degis={"enkoder_teker": "arka"})

    def yari_tik(dn):
        dn.c.tik_tur = 990
    ekle("enkoder çözünürlüğü yarı (990 tik/tur)", "ONERI", ayar=yari_tik)
    ekle("dt 0,5 ms", "ONERI", degis={"zaman_adimi_s": 0.0005})
    ekle("temas solref 0,002", "ONERI", degis={"temas_solref_s": 0.002})
    ekle("temas solref 0,008", "ONERI", degis={"temas_solref_s": 0.008})

    def piramit(dn):
        dn.w.m.opt.cone = mujoco.mjtCone.mjCONE_PYRAMIDAL

    def noslip(dn):
        dn.w.m.opt.noslip_iterations = 5

    def impratio(dn):
        dn.w.m.opt.impratio = 10.0
    ekle("piramit koni", "ONERI", ayar=piramit)
    ekle("noslip 5", "ONERI", ayar=noslip)
    ekle("impratio 10", "ONERI", ayar=impratio)

    def cap127(dn):
        dn.c.teker_capi = 0.127
    ekle("ADAY, firmware TEKER_CAPI_M 0,125 (ana)", "ONERI-ADAY")
    ekle("ADAY, firmware TEKER_CAPI_M 0,127", "ONERI-ADAY", ayar=cap127)
    ekle("ADAY, enkoder arka (lastik) tekerde", "ONERI-ADAY", degis={"enkoder_teker": "arka"})
    return r


def main():
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    o = dict(varyantlar={k: dict(ad=VR.VARYANTLAR[k]["ad"], aciklama=VR.VARYANTLAR[k]["aciklama"]) for k in VARS},
             oneri_fw=VR.ONERI_FW, makara_mu_yan=VR.MAKARA_MU_YAN, kosular=[], yan_etki={}, rampa={}, esik={})
    for var in VARS:
        for dad, durma in DURMA.items():
            for mu in (0.5, 0.8):
                r = dict(varyant=var, durma=dad, mu=mu)
                AKTIF[0] = "%s %s µ %.1f dönüş / yay / 90° / kolon" % (var, dad, mu)
                r["yerinde"] = {str(w): yerinde(var, mu, durma, 0.0, w) for w in (0.5, 1.0, 1.5)}
                r["yay"] = {str(w): yerinde(var, mu, durma, 0.25, w) for w in (0.5, 1.0)}
                r["doksan"] = doksan(var, mu, durma)
                r["dolasma"] = OV.dolas_kos(var, mu, durma)
                o["kosular"].append(r)
                print("%-8s %s mu %.1f | yerinde %s | yay w %.3f | 90: %s | kolon %s" % (
                    var, dad, mu, " ".join("%.3f" % r["yerinde"][k]["w_gercek"] for k in ("0.5", "1.0", "1.5")),
                    r["yay"]["1.0"]["w_gercek"], "-" if not r["doksan"]["ulasti"] else "%.1f s asma %.1f" % (
                        r["doksan"]["sure_90_s"], r["doksan"]["asma_derece"]),
                    "%.1f s" % r["dolasma"]["sure_s"] if r["dolasma"]["basarili"] else "basarisiz"), flush=True)
        AKTIF[0] = "%s yan etkiler" % var
        o["yan_etki"][var] = OV.yan_etki(var)
        AKTIF[0] = "%s rampa" % var
        o["rampa"][var] = {str(e): olcumler_ile(var, O.rampa_kos, e, "ana") for e in (5, 10)}
        AKTIF[0] = "%s eşik" % var
        o["esik"][var] = [olcumler_ile(var, O.esik_kos, h, t, v) for t in ("ana", "durma_9kgcm") for v in (0.2, 1.0)
                          for h in (5, 10, 15)]
        print("%-8s yan etki / rampa / esik bitti" % var, flush=True)
    AKTIF[0] = "duyarlılık"
    o["duyarlilik"] = duyarlilik()
    AKTIF[0] = "düz gidiş / devrilme"
    o["duz"] = {ad: duz_kos(v) for ad, v in (("V0", "V0"), ("ONERI", "ONERI"), ("ONERI-ADAY", "ONERI-ADAY"),
                                              ("acik cevrim + aday omni", ACIK_ADAY))}
    o["devrilme"] = {ad: devrilme_payi(ad) for ad in ("V0", "ONERI", "ONERI-ADAY")}
    print("duz / devrilme bitti", flush=True)
    AKTIF[0] = "makara taraması"
    o["makara_tarama"] = makara_tarama()
    o["yanlis_alarm"] = ALARM
    print("enkoder arizasi korumasi tetiklendi: %d (%s)" % (len(ALARM), sorted(set(a["olcum"] for a in ALARM))), flush=True)
    os.makedirs(CIKTI, exist_ok=True)
    with open(os.path.join(CIKTI, "donus-oneri.json"), "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, indent=1, sort_keys=True)
    with open(os.path.join(CIKTI, "donus-oneri.md"), "w", encoding="utf-8") as f:
        f.write(md(o))
    print("yazıldı: planlama/d158/Y0f-olcum/donus-oneri.json + .md")


def s(x, f="%.2f"):
    return "-" if x is None else (f % x).replace(".", ",")


def md(o):
    fw = o["oneri_fw"]
    L = ["# Öneri firmware + ön omni (Y0f, `kod/fizik/olcum_oneri.py`)", "",
         "**VARSAYIM**, bugünkü robot değil (V0 hariç). ONERI = öneri firmware (dal `oneri/donus-omni`, `motorlar.cpp`: PI kp %s, ki %s, "
         "integral sınırı %s, w girişi %s, 20 ms döngü, enkoder tik farkından hız, enkoder arızası koruması; masada PI açıldıktan "
         "sonraki durum: dalda PI ilk yüklemede kapalı) + ön iki teker omni (makara yanal sürtünmesi %s, "
         "TAHMİN). ONERI-T = öneri firmware + bugünkü lastikler. ONERI-ADAY = ONERI, ön teker aday omni ölçüleriyle (Ø127 x 29, "
         "480 g; seçilmedi). Başsız, protokol üzerinden; 3 s sonra 1,5 s ortalaması. Tork / "
         "sürekli: en yüklü tekerin ortalama torku / (durma x 0,3, TAHMİN)." % (
             s(fw["kp"], "%.0f"), s(fw["ki"], "%.0f"), s(fw["integral_siniri"], "%.1f"), s(fw["w_giris"], "%.1f"),
             s(o["makara_mu_yan"])), "",
         "## Dönüş", "",
         "| varyant | durma | µ | yerinde w (komut 0,5 / 1 / 1,5) | tork / sürekli (w 1) | yay v 0,25 + w 0,5: w / yarıçap m | yay + w 1: w / yarıçap m | 90°: s / aşma ° / tepe oranı | kolon |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    L.append("")
    L.append("90°: yön 10 ms'de bir denetlenir, 90°'yi geçince `dur`; aşma = `dur` sonrası fren (+ en çok bir 10 ms dilim). "
             "200 ms denetimle aşmaya ortalama ≈ 6° daha eklenir (ilk sürümün 8–15°'si buydu).")
    for r in o["kosular"]:
        y, a, d, k = r["yerinde"], r["yay"], r["doksan"], r["dolasma"]
        L.append("| %s | %s | %s | %s / %s / %s | %s | %s / %s | %s / %s | %s | %s |" % (
            r["varyant"], r["durma"], s(r["mu"], "%.1f"), s(y["0.5"]["w_gercek"], "%.3f"), s(y["1.0"]["w_gercek"], "%.3f"),
            s(y["1.5"]["w_gercek"], "%.3f"), s(y["1.0"]["tork_surekli_orani"], "%.1f"),
            s(a["0.5"]["w_gercek"], "%.3f"), s(a["0.5"]["yaricap_m"]), s(a["1.0"]["w_gercek"], "%.3f"), s(a["1.0"]["yaricap_m"]),
            ("%s / %s / %s" % (s(d["sure_90_s"], "%.1f"), s(d["asma_derece"], "%.1f"), s(d["w_tepe_kararli_orani"], "%.2f")))
            if d["ulasti"] else "ulaşmadı (20 s)",
            ("başarılı, %s s" % s(k["sure_s"], "%.1f")) if k["basarili"] else "başarısız (%d / 3)" % k["ulasilan_ara_nokta"]))
    L += ["", "## Yan etkiler (µ 0,8, 21 kg·cm)", "",
          "Model sol-sağ simetrik: düz gidiş ve frende yön sapması bozucu olmadan 0; yön kararlılığını yanal itme gösterir.", "",
          "| varyant | düz 6 s yol m | yanal itme 10 N 0,3 s: yan m / yön ° | dur (0,39'dan) m | acil stop m | 5° yan eğim duruş: yan m / yön ° | 5° yan eğim düz 5 s: yan m / yön ° |",
          "| --- | --- | --- | --- | --- | --- | --- |"]
    for k, e in o["yan_etki"].items():
        L.append("| %s | %s | %s / %s | %s | %s | %s / %s | %s / %s |" % (
            k, s(e["duz_6s"]["yol_m"]), s(e["yanal_itme"]["yan_kayma_m"], "%.3f"), s(e["yanal_itme"]["yon_sapmasi_derece"], "%.1f"),
            s(e["dur"]["yol_m"], "%.3f"), s(e["acil_stop"]["yol_m"], "%.3f"),
            s(e["yan_egim_5_durus"]["yan_kayma_m"], "%.3f"), s(e["yan_egim_5_durus"]["yon_sapmasi_derece"], "%.1f"),
            s(e["yan_egim_5_duz_gidis"]["yan_kayma_m"], "%.3f"), s(e["yan_egim_5_duz_gidis"]["yon_sapmasi_derece"], "%.1f")))
    L += ["", "## Rampa (rampa kipi, sonar kapalı, µ 0,8, 21 kg·cm): `dur` sonrası süzülme bittikten sonra 5 s", "",
          "| varyant | eğim | ortasına ulaştı | rampada hız m/s | 5 s geri kayma m | tutuyor |", "| --- | --- | --- | --- | --- | --- |"]
    for k, rr in o["rampa"].items():
        for e, r in rr.items():
            L.append("| %s | %s° | %s | %s | %s | %s |" % (k, e, "evet" if r["rampanin_ortasina_ulasti"] else "hayır",
                                                       s(r["rampada_hiz_m_s"], "%.3f"), s(r["suzulme_sonrasi_5s_geri_kayma_m"], "%.3f"),
                                                       "evet" if r["dur_sonrasi_tutuyor"] else "hayır"))
    L += ["", "## Eşik (sonar kapalı, µ 0,8)", "",
          "Düşük hızda eşik kazancı PI'dan (lastikli ONERI-T de geçiyor). Ön omni küre olarak modellendi (sürekli çember): "
          "omni makaralarıyla eşik geçişi modellenmedi, masada denenmeli.", "", "| varyant | durma | v komutu | 5 mm | 10 mm | 15 mm |", "| --- | --- | --- | --- | --- | --- |"]
    for k, liste in o["esik"].items():
        for t in ("ana", "durma_9kgcm"):
            for v in (0.2, 1.0):
                h = {r["yukseklik_mm"]: r for r in liste if r["takim"] == t and r["v_komut"] == v}
                L.append("| %s | %s | %s | %s |" % (k, "21 kg·cm" if t == "ana" else "9 kg·cm", s(min(v, 0.39)),
                                                    " | ".join("geçti" if h[mm]["gecti"] else ("ön çıktı" if h[mm]["on_teker_cikti"] else "geçmedi")
                                                               for mm in (5, 10, 15))))
    L += ["", "## Enkoder arızası koruması: yanlış alarm", "",
          "Koruma (PI düzeltme payı + makullük denetimi, `motorlar.cpp` DUZELTME_* / KUSKU_*) bu dosyadaki bütün ölçümlerde "
          "(kalkış, dönüş, 9 kg·cm doyum, rampa, eşik, yan eğim, duyarlılık, makara taraması) izlendi. Tetiklenme: %d." % len(o["yanlis_alarm"]), ""]
    for a in o["yanlis_alarm"]:
        L.append("- %s: %s teker, %d ms" % (a["olcum"], a["yan"], a["ms"]))
    L += ["", "## Düz gidiş, aks uyumu (v 0,25, µ 0,8, 21 kg·cm; 4 s sonra 2 s)", "",
          "Aday omni Ø127, arka lastik Ø125; bir yandaki iki motor aynı PWM'i alır (aynı BTS7960), firmware iki aksı ayrı süremez. "
          "Çevre oranı = teker çevre hızı / gövde hızı (1 = kaymasız).", "",
          "| durum | v m/s | ön aks |tork| N·m | arka aks |tork| N·m | ön çevre oranı | arka çevre oranı | 6 s'de yön ° |",
          "| --- | --- | --- | --- | --- | --- | --- |"]
    for ad, r in o["duz"].items():
        L.append("| %s | %s | %s | %s | %s | %s | %s |" % (ad, s(r["v"], "%.3f"), s(r["tork_on_Nm"], "%.3f"), s(r["tork_arka_Nm"], "%.3f"),
                                                       s(r["on_cevre_orani"], "%.3f"), s(r["arka_cevre_orani"], "%.3f"),
                                                       s(r["yon_derece"], "%.2f")))
    L += ["", "## Statik devrilme payı (geometri: temas noktaları ve AM; karşılaştırma için)", "",
          "| varyant | kütle kg | AM x / y / z mm | ön temas y mm | ileri ° | geri ° | yana ° |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for ad, r in o["devrilme"].items():
        L.append("| %s | %s | %s / %s / %s | %s | %s | %s | %s |" % (
            ad, s(r["kutle_kg"], "%.2f"), s(r["am_mm"][0], "%.1f"), s(r["am_mm"][1], "%.1f"), s(r["am_mm"][2], "%.1f"),
            s(r["on_temas_y_mm"], "%.1f"), s(r["ileri_derece"], "%.1f"), s(r["geri_derece"], "%.1f"), s(r["yana_derece"], "%.1f")))
    L += ["", "## Makara yanal sürtünmesi taraması (ONERI-ADAY, yerinde w komutu 1)", "",
          "Üretici değeri yok (rulmanlı / pirinç borulu sürüm). Yanal kuvvet = katsayı x ortalama teker yükü (eklemde sabit Coulomb; "
          "masada yüklü tekeri yana çekme ölçümüyle karşılaştırılacak sayı).", "",
          "| katsayı | yanal kuvvet N / teker | 21 kg·cm µ 0,5 | 21 kg·cm µ 0,8 | 9 kg·cm µ 0,5 | 9 kg·cm µ 0,8 |", "| --- | --- | --- | --- | --- | --- |"]
    tar = {}
    for r in o["makara_tarama"]:
        tar.setdefault(r["makara_mu_yan"], {})[(r["durma"], r["mu"])] = r
    for mu_yan, d in tar.items():
        kuv = next(iter(d.values()))["yanal_kuvvet_N"]
        L.append("| %s | %s | %s |" % (s(mu_yan), s(kuv, "%.1f"), " | ".join(
            "%s (%s)" % (s(d[(dd, mu)]["w_gercek"], "%.2f"), s(d[(dd, mu)]["tork_surekli_orani"], "%.1f"))
            for dd in ("21kgcm", "9kgcm") for mu in (0.5, 0.8))))
    L.append("")
    L.append("Hücre: gerçekleşen w rad/s (tork / sürekli).")
    L += ["", "## Duyarlılık (ONERI, µ 0,8, 21 kg·cm; yerinde w komutu 1 ve 5° yan eğimde 5 s düz gidiş)", "",
          "| ayar | yerinde w | w std | tork / sürekli | yan eğim kayma m / yön ° |", "| --- | --- | --- | --- | --- |"]
    for r in o["duyarlilik"]:
        L.append("| %s | %s | %s | %s | %s |" % (r["ayar"], s(r["w_gercek"], "%.3f"), s(r["w_std"], "%.3f"),
                                                s(r["tork_surekli_orani"], "%.1f"),
                                                "-" if r["yan_egim_kayma_m"] is None else "%s / %s" % (
                                                    s(r["yan_egim_kayma_m"], "%.3f"), s(r["yan_egim_yon_derece"], "%.1f"))))
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
