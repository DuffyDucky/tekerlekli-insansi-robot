# Lale 1,58 m - gogus ekrani kablo yollari (saf Python; FreeCAD'siz import edilir). Global koordinat, ev pozu (pan 0, tilt 0), mm.
# Pi 5 kafada; gogus ekrani HDMI + USB dokunmatik boyundan iner (eski kural "HDMI boyundan gecmez" yazilim-plani.md:64 bu nedenle degisti, karar Duffy/ekip: acik-noktalar madde 12).
# Kafa ici ve boyun: kafa7_parcalar.YOL hatti (tabla kablo gecisi x -50...-37 -> sol yanak disi -> catal tabani -> adaptor + mil O32 -> mil penceresi -> kablo odasi ->
# servo yuvasi arka kanali -> alt cikis). Govdede: traversin arkasi -> direk solu -> ekran arkasi -> port girintisi (-X; port yeri DOGRULANMADI, arayuz.GOGUS_EKRAN port).
# Bu cizim semadir: kablo capi tahmini, kablo gercek bukum yaricapi ve fis olcusu dogrulanmadi.
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
    "USB dokunmatik": (4.0, "USB A -> micro B, Pi USB -> ekran TOUCH; kutudaki kablo 35 cm, yetmez"),
    "12 V": (5.0, "ekran 12 V ~0,5 A, taban guc panelinden; LiFePO4 12,8-14,4 V ile dogrudan baglama dogrulanmadi: regulator/sigorta karari acik"),
}
# Mevcut boyun demeti (planlama/adim3/elektrik.md): 12 V cift 18 AWG + ESP32 USB + tilt servo serit
MEVCUT = [("12 V cift 18 AWG", math.pi / 4 * 2.6 ** 2 * 2), ("ESP32 USB", math.pi / 4 * 4.0 ** 2), ("tilt servo 3 tel", 4.2 * 1.4)]
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
    pi_usb = [bas(42.5, 47.0, -20.0), bas(50.0, 47.0, -20.0), bas(50.0, 38.0, 20.0)]
    inis = [(0.0, Y_KOSE + 3.0, -36.0)]
    yol = {
        "HDMI": pi_hdmi + trunk + inis + ekran_ucu(5.0, 0.0),
        "USB dokunmatik": pi_usb + trunk + inis + ekran_ucu(-15.0, 7.0),
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
    pi_usb = (50.0, 47.0, -30.0)                 # Pi USB-A fis ucu (x 45,6 + fis) veya hub
    sy = (58.0, 40.0, 14.0)                      # SY8205 cikis kenari
    x_h = PT["hdmi"]["x"][1] + F["hdmi"][0]
    x_u = PT["power"]["x"][1] + F["usb"][0]
    return {
        "HDMI (serit, 2 lehimsiz fis)": ([(x_h, dy + PT["hdmi"]["y"], zg), (x_h + 15.0, dy + PT["hdmi"]["y"] + 15.0, zg), (x_h, dy + PT["hdmi"]["y"] + 30.0, zg),
                                          (75.0, dy + PT["hdmi"]["y"] + 30.0, zg), (75.0, y_gecit, zg), (75.0, y_gecit, 20.0), (-16.7, y_gecit + 3.0, 20.0), hdmi0], 300.0),
        "Touch USB (kutu kablosu)": ([(PT["touch"]["x"][1], dy + PT["touch"]["y"], zg), (x_u, dy + PT["touch"]["y"], zg), (80.0, y_gecit, zg), (80.0, y_gecit + 5.0, 20.0), (50.0, y_gecit + 7.0, 0.0), pi_usb], 350.0),
        "Power USB (30 cm, A ucu kesik)": ([(PT["power"]["x"][1], dy + PT["power"]["y"], zg), (x_u, dy + PT["power"]["y"], zg), (70.0, y_gecit, zg), (70.0, y_gecit, 20.0), sy], 300.0),
    }


def uzunluk(p):
    return sum(math.dist(a, b) for a, b in zip(p[:-1], p[1:]))


def ozet():
    y = yollar()
    pay = 1.25   # pan +-90 halkasi + servis payi + bukum: %25 (tahmini)
    bo = {k: dict(yol_mm=round(uzunluk(v), 0), onerilen_mm=round(uzunluk(v) * pay, -1), cap_mm=KABLO[k][0], not_=KABLO[k][1]) for k, v in y.items()}
    yeni = [("HDMI", math.pi / 4 * KABLO["HDMI"][0] ** 2), ("USB dokunmatik", math.pi / 4 * KABLO["USB dokunmatik"][0] ** 2)]
    top = sum(a for _, a in MEVCUT) + sum(a for _, a in yeni)
    gc = [dict(g, doluluk=round(top / g["alan"], 3), kablo_sigar=bool(KABLO["HDMI"][0] <= g["kisa"])) for g in GECIS]
    ki = {k: dict(yol_mm=round(uzunluk(v[0]), 0), liste_boyu_mm=v[1], kalan_mm=round(v[1] - uzunluk(v[0]), 0)) for k, v in kafa_ici_qled().items()}
    return dict(kablo=bo, kafa_ici_qled=ki, boyun_demet_alan_mm2=round(top, 1), mevcut=[(a, round(b, 1)) for a, b in MEVCUT], gecis=gc,
                not_="Kablo capi ve fis olcusu tahmini (kablo secilince olculur). Mil penceresi + kanal + alt cikis 03.11.2026 genisletildi (13,7 -> 20; 12 -> 20).")


if __name__ == "__main__":
    import json
    print(json.dumps(ozet(), indent=1, ensure_ascii=False))
