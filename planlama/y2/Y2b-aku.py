# -*- coding: utf-8 -*-
"""Y2b (29 Ekim 2026): E8 aku sureleri 1,65 m tasarimla yeniden (kopya: planlama/adim5/e8_aku.py, yontem ayni).
Degisen yukler (hepsi tahmini): gogus Nextion yok; yuz ekrani 7" -> 10,1" (5 V ~0,75 A); mikrofon ReSpeaker -> XVF3800 (~1 W, belgesiz);
servo jest akimi x1,19 (kol x1,25 + DS3235: hat yogun 5,43 A / E1 ortalama 4,55 A; taslak-170 KOL125-KONTROL-NOTLAR); tahrik duz/ivme/rampa
akimi x1,14 (robot 21,73 -> 24,80 kg), yerinde donus 2,12 A/motor (taban-analiz.json donus mu 0,5). Cikti Y2b-aku.json.
Eski aciklama: E8 (5. adim): aku sureleri, aku raporu yontemiyle (raporlar/aku-secimi, 06-aku-secimi.md) + 3. adim tuketicileri.
Kullanilabilir = nominal x 0,90 (DoD) x 0,90 (yaslanma/soguk/BMS) = 0,81. Sure = Wh x 0,81 / W.
Yuk tarafi W (tahmini; kaynak sutunu). Hat verimi: kafa Pololu 0,90, XL4016 5 V / 6 V 0,88, BTS 0,95 (elektrik.md).
  py -3 planlama/y2/Y2b-aku.py
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
KUL = 0.81
AKU = {"Victron SuperPack 12,8/20 (K3)": 256.0, "24 Ah (eski Limacell)": 307.2, "30 Ah": 384.0}
V = 12.8
# motor akimi A/motor (aku raporu + taban-analiz donus): duz 0,24, ivme 0,47, rampa 0,86, yerinde donus standart (mu 0,5) 2,0, omni 0,45
KM = 24.80 / 21.73   # robot kutlesi orani (taban-analiz.json robot / elektrik.md E0)
def surus(duz, ivme, rampa, donus, donus_A=2.12):
    return 4 * V * (KM * (duz * 0.24 + ivme * 0.47 + rampa * 0.86) + donus * donus_A)
SURUS_YOGUN = surus(0.40, 0.20, 0.25, 0.15)          # %40 duz, %20 ivme, %25 rampa, %15 yerinde donus
SURUS_YOGUN_OMNI = surus(0.40, 0.20, 0.25, 0.15, 0.50)
SERVO_BEKLE = (0.3 + 0.4) * 6.0                       # E1 bekleme A + B
SERVO_JEST = (2.8 + 2.9) * 6.0 * 5.43 / 4.55          # E1 jest ani A + B, x1,19 (1,65 m kol + DS3235, tahmini)
# kalem: (ad, hat, bosta, normal, yogun, kaynak)
KALEM = [
    ("Pi 5 + Active Cooler (kafa)", "kafa", 4.0, 6.5, 12.0, "aku raporu 4/6,5; yogun = taban-analiz 12 W tam yuk"),
    ("10,1\" yuz ekrani (kafa, Pi USB)", "kafa", 2.0, 3.0, 3.75, "tahmini: Waveshare 10.1 (B) 5 V ~0,75 A (maliyet.json notu); olculecek"),
    ("Kamera + mikrofon + amfi (kafa)", "kafa", 1.7, 2.2, 3.2, "kamera 0,7 + XVF3800 ~1,0 (belgesiz, tahmini) + amfi 0 / 0,5 / 1,5"),
    ("ESP32 + sensor + PCA/BNO mantik", "5V", 0.8, 1.0, 1.3, "ESP32 Wi-Fi ~0,5 W + sonar/BNO/PCA/enkoder (tahmini)"),
    ("Servolar A + B", "6V", SERVO_BEKLE, 0.2 * SERVO_JEST + 0.8 * SERVO_BEKLE, SERVO_JEST,
     "E1: bekleme 0,7 A, jest 5,7 A x 6 V; normal %20 jest; yogun surekli jest"),
    ("Tahrik 4 x JGB37", "12V", 0.3, 5.0, SURUS_YOGUN,
     "bosta/normal aku raporu; yogun %40 duz/%20 ivme/%25 rampa/%15 yerinde donus (2,0 A/motor, mu 0,5)"),
]
VERIM = {"kafa": 0.90, "5V": 0.88, "6V": 0.88, "12V": 0.95}
SABIT = [  # aku tarafi, her senaryoda
    ("Role K1 bobini", 0.15 * V, "elektrik.md ~0,15 A (aku raporunda 1,5 W, taban-analiz 0,3 W)"),
    ("XL4016 x3 bosta", 0.4, "aku raporu (tahmini)"),
    ("PC817 girisleri x2 + aku ADC bolucu", 2 * 0.005 * V + 0.0015, "E2 (~5 mA x 2)"),
]
FAN = (0.1 * 12.0, "E7 kosullu 40 mm fan ~0,1 A (tahmini)")
sen = {}
for i, ad in enumerate(("bosta", "normal", "yogun")):
    yuk = sum(k[2 + i] for k in KALEM)
    aku = sum(k[2 + i] / VERIM[k[1]] for k in KALEM) + sum(s[1] for s in SABIT)
    sen[ad] = {"yuk_W": round(yuk, 1), "aku_W": round(aku, 1), "A": round(aku / V, 2)}
# yogun, omni ile
aku_omni = sen["yogun"]["aku_W"] - (SURUS_YOGUN - SURUS_YOGUN_OMNI) / 0.95
sen["yogun_omni"] = {"aku_W": round(aku_omni, 1), "A": round(aku_omni / V, 2)}
karisim = {"ders (3 sa; %40 bosta, %50 normal, %10 yogun)": (0.4, 0.5, 0.1),
           "fuar (8 sa; %35 / %50 / %15)": (0.35, 0.5, 0.15)}
for ad, (a, b, c) in karisim.items():
    sen[ad] = {"aku_W": round(a * sen["bosta"]["aku_W"] + b * sen["normal"]["aku_W"] + c * sen["yogun"]["aku_W"], 1)}
sure = {}
for akuad, wh in AKU.items():
    sure[akuad] = {k: round(wh * KUL / v["aku_W"], 1) for k, v in sen.items()}
gerek = {}
for ad, saat in (("ders (3 sa; %40 bosta, %50 normal, %10 yogun)", 3), ("fuar (8 sa; %35 / %50 / %15)", 8)):
    wh = sen[ad]["aku_W"] * saat / KUL
    gerek[ad] = {"nominal_Wh": round(wh), "Ah": round(wh / V, 1)}
fan_etki = {k: round(256 * KUL / (v["aku_W"] + FAN[0]), 2) for k, v in sen.items()}
res = {"kullanilabilir": KUL, "aku_Wh": AKU, "verim": VERIM, "kalemler": KALEM, "sabit": SABIT, "fan": FAN,
       "surus_yogun_W": round(SURUS_YOGUN, 1), "surus_yogun_omni_W": round(SURUS_YOGUN_OMNI, 1),
       "senaryo": sen, "sure_sa": sure, "gereken": gerek, "victron_fan_ile_sa": fan_etki}
with open(os.path.join(HERE, "Y2b-aku.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print(json.dumps({"senaryo": sen, "sure_sa": sure, "gereken": gerek, "surus_yogun_W": res["surus_yogun_W"],
                  "fan": fan_etki}, ensure_ascii=False, indent=1))
