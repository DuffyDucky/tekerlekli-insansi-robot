# Lale 1,58 m - gogus ekrani kablo yollari (saf Python; FreeCAD'siz import edilir). Global koordinat, ev pozu (pan 0, tilt 0), mm.
# Pi 5 kafada; gogus ekrani HDMI + USB dokunmatik boyundan iner (eski kural "HDMI boyundan gecmez" yazilim-plani.md:64 bu nedenle degisti, karar Duffy/ekip: acik-noktalar madde 12).
# Kafa ici ve boyun: kafa7_parcalar.YOL hatti (tabla kablo gecisi x -50...-37 -> sol yanak disi -> catal tabani -> adaptor + mil O32 -> mil penceresi -> kablo odasi ->
# servo yuvasi arka kanali -> alt cikis). Govdede: traversin arkasi -> direk solu -> ekran arkasi -> port girintisi (-X; port yeri DOGRULANMADI, arayuz.GOGUS_EKRAN port).
# Bu cizim semadir: kablo capi tahmini, kablo gercek bukum yaricapi ve fis olcusu dogrulanmadi.
# Secim B + R1 (Duffy 05.11.2026; lale158/kafa-yerlesim): hub gogus ust arka kapaginin icinde. Boyundan HDMI, Hub uzatmasi, Hoparlor, 12 V, tilt iner; gogus dokunmatigi ve ESP32 USB hub'dan, kafaya girmez.
# Pi portlari: 1 ReSpeaker, 2 ses karti, 3 hub, 4 kafa dokunmatik. Hub: gogus dokunmatik, ESP32, 2 bos. Boyuna inen USB z ~ -14'te SY8205'in onunden (A.SES_USB koridor).
import math
import os
import sys

_UST = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _UST not in sys.path:
    sys.path.insert(0, _UST)
import arayuz as A

KABLO = {
    # ad: (dis cap mm (TAHMINI), not)
    "HDMI": (6.0, "ince micro HDMI -> HDMI A, Pi HDMI1 -> ekran; ekran ucunda 90 derece fis/adaptor gerekir"),
    "USB dokunmatik": (4.0, "USB A -> micro B, HUB -> gogus ekrani TOUCH; kutudaki kablo 35 cm, yetmez; v4 satir 58, 2 m"),
    "Hub uzatmasi": (4.0, "Pi port 3 -> hub: hub'in sabit 130 mm kablosu + ~1 m USB-A uzatma; listede yok"),
    "ESP32 USB": (4.0, "Hub -> ESP32 (taban), VBUS'ta 1N5819; govde ici sema, v4'te 2 m"),
    "Hoparlor": (4.0, "PAM8403 -> hoparlor, boyundan iner; listede robot icin yok (2 x 0,75 kordon test duzeneginin sarfi)"),
    "Ses karti uzatmasi": (4.0, "Pi port 2 -> L dirsek -> ses karti; USB-A erkek -> disi, listede yok"),
    "Dizi USB": (4.0, "Pi port 1 -> ReSpeaker micro B; kisa kablo listede yok"),
    "3,5 mm -> PAM": (3.5, "ses karti L 3,5 mm fis -> PAM girisi; AUX kablosu kesilir, listede robot icin yok"),
    "PAM 5 V": (3.0, "D24V50F5 ustu -> PAM 5 V; besleme noktasi ONERI, elektrik.md'de dogrulanmadi"),
    "12 V": (5.0, "ekran 12 V ~0,5 A, taban guc panelinden; LiFePO4 12,8-14,4 V ile dogrudan baglama dogrulanmadi: regulator/sigorta karari acik"),
}
# Mevcut boyun demeti (planlama/adim3/elektrik.md): 12 V cift 18 AWG + ESP32 USB + tilt servo serit
# B (05.11.2026): ESP32 USB ve gogus dokunmatik boyundan cikti; yerlerine Hub uzatmasi ve Hoparlor indi (ozet: yeni)
MEVCUT = [("12 V cift 18 AWG", math.pi / 4 * 2.6 ** 2 * 2), ("tilt servo 3 tel", 4.2 * 1.4)]
# Dar kesitler (kafa7_parcalar, 03.11.2026 genisletmeden sonra). alan mm2; kisa = dar kenar mm
GECIS = [
    dict(ad="Boyun mili O32", alan=math.pi * 16.0 ** 2, kisa=32.0),
    dict(ad="Egme catali deligi O28", alan=math.pi * 14.0 ** 2, kisa=28.0),
    dict(ad="Mil arka penceresi 20 x 10, ust 45 derece", alan=175.0, kisa=10.0),
    dict(ad="Servo yuvasi arka kanali 20 x 7,8", alan=20.0 * 7.8, kisa=7.8),
    dict(ad="Servo yuvasi alt cikisi 20 x 12, ust 45 derece", alan=204.0, kisa=12.0),
]


def gp(x, Y, Z):
    """Gogus ekrani yerel (X, duzlem boyunca Y, normal Z; orijin cep merkezi) -> global."""
    a = math.radians(A.GOGUS_EGIM)
    c, s = math.cos(a), math.sin(a)
    yc = A.GOGUS_EKRAN_Y
    return (x, yc + Y * c + Z * s, A.gogus_z(yc) - Y * s + Z * c)


def hoparlor_merkez():
    """Hoparlor duvar merkezi C (orta bant ic yuzu) ve duvar dis normali n, global (A.SES_USB hoparlor; isin olcumu kabuk modelinden)."""
    H_ = A.SES_USB["hoparlor"]
    (y0, z0), (y1, z1) = H_["ic"]
    t = (z1 - z0) / (y1 - y0)
    al = math.atan(t)
    return dict(C=(H_["x"], H_["y"], z0 + (H_["y"] - y0) * t), n=(0.0, -math.sin(al), math.cos(al)), alfa=al)


def yollar():
    K = A.KAFA
    YT, ZT = K["tilt_nokta"][1], K["tilt_nokta"][2]
    H = K["adaptor_h"]
    Y0 = A.S3 + A.SG / 2
    Y_KOSE = A.S3 - 65.0   # direk-travers kose baglantilarinin (y >= S3 - 57) altindan direk yanina gecis

    def bas(x, y, z):      # Bas cercevesi (tilt ekseni orijin) -> global
        return (x, Y0 + YT + y, ZT + z)

    def yer(x, y, z):      # kafa yereli -> global
        return (x, Y0 + y, z)

    trunk = [bas(-43.5, 38.0, 10.0), bas(-43.5, 38.0, -13.0), bas(-43.5, 10.0, -13.0), yer(-40.0, 112.0 + H, 18.0), yer(-18.0, 108.0 + H, 2.0),
             yer(-8.0, 100.0 + H, -6.0), yer(0.0, 96.0 + H, 0.0), yer(0.0, 58.5, 0.0), yer(0.0, 58.0, -18.0), yer(-10.0, 56.5, -22.0),
             yer(-4.0, 44.0, -20.0), yer(-4.0, 39.0, -23.1), yer(-4.0, 15.0, -23.1), yer(-4.0, 10.0, -33.0), yer(-4.0, -40.0, -36.0)]
    P = A.GOGUS_EKRAN["port"]
    xd = P["x_duvar"]
    dz = A.GOGUS_EKRAN["cam_geri"] - P.get("cam_geri_ref", A.GOGUS_EKRAN["cam_geri"])   # 04.11.2026: kasa cam_geri kadar geri; port ve kablo ucu birlikte kayar
    z_ort = 0.5 * sum(P["z"]) - dz

    def ekran_ucu(Y, dx):
        return [(-32.0 - dx, Y_KOSE, -32.0), (-32.0 - dx, Y_KOSE, 30.0), gp(-60.0 - dx, 40.0, -60.0), gp(xd - 18.0, Y, -42.0 - dz), gp(xd - 18.0, Y, z_ort),
                gp(xd, Y, z_ort)]

    pi_hdmi = [bas(-3.3, 43.0, -0.35), bas(-3.3, 43.0, 25.0)]
    inis = [(0.0, Y_KOSE + 3.0, -36.0)]
    S = A.SES_USB
    PI, HB = S["pi_usb"], S["hub"]
    koridor = [bas(*q) for q in S["koridor"]]
    x_ic = K["kafa_kutu"][0] / 2 - 2.5
    D_, SK, PM = S["dizi"], S["ses"], S["pam"]
    y_pcb = K["denge"]["dy"] + K["govde_y"][1] - 2.5 - D_["gap_jak"] - D_["jak_ust"]
    d_uc = (D_["cx"] + 35.0 + D_["fis"]["boy"], y_pcb + 1.4, D_["cz"] - D_["usb_x"])
    fz = SK["zc"] - SK["olcu"][0] / 2
    s_uc = (-(x_ic - 43.0), SK["y"], fz - 20.0)
    j_uc = (-(x_ic - 12.0), SK["y"] - 5.0, SK["zc"] + SK["olcu"][0] / 2 + 8.0)
    ym, lz = 0.5 * sum(HB["y"]), HB["lz"]
    hc = hoparlor_merkez()
    a_ = tuple(hc["C"][k] - hc["n"][k] * (0.5 + S["hoparlor"]["boy"]) for k in range(3))    # hoparlor arka yuzu
    # F1a P1.7 (08.11.2026): arka yuzun ortasinda e2 +-5 seridinde hoparlor kelepcesinin koprusu var (kabuk_parcalar KEL); kablo ucu
    # koprunun altina, hoparlor kenarina yakin (e2 -14; e2 = n x X) alindi. Uc yeri / lehim tirnagi VARSAYIM (urun elde yok).
    e2_ = (0.0, hc["n"][2], -hc["n"][1])
    hop_uc = [(30.0, 1190.0, -32.0), (62.0, 1185.0, -32.0), (62.0, 1185.0, 35.0), (62.0, 1060.0, 35.0), (62.0, 1003.0, 62.0),
              tuple(a_[k] + (4.0, 0.0, 0.0)[k] - 14.0 * e2_[k] - 2.5 * hc["n"][k] for k in range(3))]
    p1, p2, p3 = PI["p1"], PI["p2"], PI["p3"]
    yol = {
        "HDMI": pi_hdmi + trunk + inis + ekran_ucu(5.0, 0.0),
        "Hub uzatmasi": [bas(*p3)] + koridor + trunk[2:] + inis + [(30.0, 1190.0, -40.0), (47.5, HB["y"][1] + 4.0, lz + 10.0)],
        "USB dokunmatik": [(47.5, ym, lz + 60.0), (24.0, 1190.0, -30.0)] + ekran_ucu(-15.0, 7.0),
        "ESP32 USB": [(47.5, ym - 20.0, lz + 60.0), (14.0, 1060.0, -26.0), (14.0, 300.0, -26.0), (14.0, 262.0, -40.0), (40.0, 195.0, -100.0), (51.6, 190.0, -120.0)],
        "Hoparlor": [bas(-(x_ic - 7.0), PM["y"], -28.0), bas(-100.0, 60.0, -13.0), bas(-50.0, 42.0, -13.0), bas(-43.5, 38.0, -13.0)] + trunk[2:] + inis + hop_uc,
        "Ses karti uzatmasi": [bas(*p2), bas(60.0, 52.0, -25.0), bas(40.0, 58.0, -14.0), bas(-60.0, 58.0, -14.0), bas(-80.0, 58.0, -60.0), bas(*s_uc)],
        "Dizi USB": [bas(*d_uc), bas(d_uc[0] + 6.0, 72.0, d_uc[2] - 6.0), bas(68.0, 55.0, p1[2]), bas(p1[0] + 16.0, p1[1], p1[2]), bas(*p1)],
        "3,5 mm -> PAM": [bas(*j_uc), bas(-(x_ic - 8.0), 50.0, 4.0), bas(-(x_ic - 7.0), PM["y"], -8.0)],
        "PAM 5 V": [bas(-(x_ic - 12.0), PM["y"], -32.0), bas(-100.0, 50.0, -13.0), bas(*S["d24_5v"])],
        "12 V": [(45.0, 215.0, -160.0), (8.0, 262.0, -40.0), (8.0, 300.0, -28.0), (8.0, Y_KOSE - 15.0, -28.0), (-46.0, Y_KOSE - 15.0, -28.0)] + ekran_ucu(-27.0, 14.0)[1:],
    }
    return yol


def kafa_ici_qled():
    """10,1" QLED kafa ici kablolari (Bas cercevesi: tilt ekseni orijin, mm). Konnektorler +X kenarinda (arayuz.KAFA_EKRAN_QLED port). Sema: fis ucundan U donus -> panel arkasi / tabla onu gecidi -> tabla ustu.
    Doner: ad -> (nokta listesi, liste kablo boyu mm). HDMI yolu fis ucundan basliyor (30 cm serit fislerin arasinda). Bukum R ve fis boyu TAHMIN."""
    E = A.KAFA["ekran"]
    if "port" not in E:
        return {}
    dy = A.KAFA["denge"]["dy"]
    zg = 44.5 - 6.3 - 5.0                       # gecit ortasi: panel arkasi ile tabla onu arasi (z ~33)
    F, PT = E["fis"], E["port"]
    y_gecit = 40.0                               # tabla ust yuzu 32 + bilesen payi
    hdmi0 = (-16.7, 43.0, -0.35)                 # Pi micro HDMI 0 fis ucu (HDMI 1 x -3,3; Pi 5 cizimi: HDMI0 25,8, HDMI1 39,2 kenardan)
    p4 = A.SES_USB["pi_usb"]["p4"]               # B: Pi port 4 (Touch dogrudan Pi'de); yol koridora girmez
    sy = (58.0, 40.0, 14.0)                      # SY8205 cikis kenari
    x_h = PT["hdmi"]["x"][1] + F["hdmi"][0]
    x_u = PT["power"]["x"][1] + F["usb"][0]
    return {
        "HDMI (serit, 2 lehimsiz fis)": ([(x_h, dy + PT["hdmi"]["y"], zg), (x_h + 15.0, dy + PT["hdmi"]["y"] + 15.0, zg), (x_h, dy + PT["hdmi"]["y"] + 30.0, zg),
                                          (75.0, dy + PT["hdmi"]["y"] + 30.0, zg), (75.0, y_gecit, zg), (75.0, y_gecit, 20.0), (-16.7, y_gecit + 3.0, 20.0), hdmi0], 300.0),
        "Touch USB (kutu kablosu)": ([(PT["touch"]["x"][1], dy + PT["touch"]["y"], zg), (x_u, dy + PT["touch"]["y"], zg), (80.0, y_gecit, zg), (80.0, y_gecit + 5.0, 20.0), (64.0, y_gecit + 18.0, 0.0), (64.0, p4[1], p4[2]), p4], 350.0),
        "Power USB (30 cm, A ucu kesik)": ([(PT["power"]["x"][1], dy + PT["power"]["y"], zg), (x_u, dy + PT["power"]["y"], zg), (70.0, y_gecit, zg), (70.0, y_gecit, 20.0), sy], 300.0),
    }


def uzunluk(p):
    return sum(math.dist(a, b) for a, b in zip(p[:-1], p[1:]))


KAPAK_KABLO = ("Hub uzatmasi", "USB dokunmatik", "ESP32 USB")     # hub kapakla birlikte sokulur: bu kablolara kapak sokme payi eklenir
GM = dict(usb=30.0, diger=15.0)                                     # g/m VARSAYIM (secenekler.md)


def kafa_ici_kablo_kutle():
    """B kablolarinin kafa ici kismi: (ad, boy mm, kutle g, merkez kafa yereli). Kafa alt duvarinin ustundeki segmentler. Mevcut 59 g payinin ustune eklenir (biraz kotumser)."""
    K = A.KAFA
    Y0, YT = A.S3 + A.SG / 2, K["tilt_nokta"][1]
    y_alt = Y0 + YT + K["denge"]["dy"] + K["govde_y"][0]
    out = []
    for ad, yol in yollar().items():
        if ad in ("HDMI", "12 V", "USB dokunmatik", "ESP32 USB"):
            continue                                                # HDMI ve 12 V payin icinde; dokunmatik ve ESP32 kafaya girmez
        gm = GM["usb"] if ("USB" in ad or "Hub" in ad or "uzatma" in ad) else GM["diger"]
        L, c = 0.0, [0.0, 0.0, 0.0]
        for a, b in zip(yol[:-1], yol[1:]):
            if a[1] > y_alt and b[1] > y_alt:
                l_ = math.dist(a, b)
                L += l_
                for k in range(3):
                    c[k] += (a[k] + b[k]) * 0.5 * l_
        if L > 0:
            out.append((ad, round(L, 0), round(L / 1000.0 * gm, 1), (c[0] / L, c[1] / L - Y0, c[2] / L)))
    return out


def ozet():
    y = yollar()
    pay = A.SES_USB["kablo_pay"]   # pan +-90 halkasi + servis payi + bukum: %25 (tahmini)
    kp = A.SES_USB["kapak_sokme_pay"]
    bo = {k: dict(yol_mm=round(uzunluk(v), 0), onerilen_mm=round(uzunluk(v) * pay + (kp if k in KAPAK_KABLO else 0.0), -1), kapak_sokme_pay_mm=(kp if k in KAPAK_KABLO else 0.0), cap_mm=KABLO[k][0], not_=KABLO[k][1]) for k, v in y.items()}
    yeni = [("HDMI", math.pi / 4 * KABLO["HDMI"][0] ** 2), ("Hub uzatmasi", math.pi / 4 * KABLO["Hub uzatmasi"][0] ** 2), ("Hoparlor", math.pi / 4 * KABLO["Hoparlor"][0] ** 2)]
    top = sum(a for _, a in MEVCUT) + sum(a for _, a in yeni)
    gc = [dict(g, doluluk=round(top / g["alan"], 3), kablo_sigar=bool(KABLO["HDMI"][0] <= g["kisa"])) for g in GECIS]
    ki = {k: dict(yol_mm=round(uzunluk(v[0]), 0), liste_boyu_mm=v[1], kalan_mm=round(v[1] - uzunluk(v[0]), 0)) for k, v in kafa_ici_qled().items()}
    return dict(kablo=bo, kafa_ici_qled=ki, boyun_demet_alan_mm2=round(top, 1), mevcut=[(a, round(b, 1)) for a, b in MEVCUT], gecis=gc,
                not_="Kablo capi ve fis olcusu tahmini (kablo secilince olculur). Mil penceresi + kanal + alt cikis 03.11.2026 genisletildi (13,7 -> 20; 12 -> 20).")


if __name__ == "__main__":
    import json
    print(json.dumps(ozet(), indent=1, ensure_ascii=False))
