# Lale 1,58 m: taban kablolarının gösterim şemaları (P10.7b2c; saf Python, FreeCAD'siz içe aktarılır). Global koordinat, ev pozu, mm;
# +X sağ, +Y yukarı, +Z ileri. kablo_yolu_ekran.py kalıbında: PARÇA DEĞİL, rehber-veri.json "semalar"a girer (rehber_metin.SEMA kaynağı
# "taban"); parça sayısı (1192) ve çarpışma taraması bundan etkilenmez. İzlenen CAD kaynaklarına (taban_parcalar.py, *_lib.py, arayuz.py)
# dokunmaz; yalnız arayuz.TABAN ölçülerini OKUR (kat geçişleri, kart merkezleri): model değişirse şema da birlikte kayar, rehber_kablo.py
# geometrik sınaması uçları taban-analiz.json kutularıyla ayrıca sınar.
#
# Bu çizim şemadır, ÇARPIŞMA TARAMASINDAN GEÇMEDİ (lale158_kontrol yalnız kablo_yolu_ekran.yollar()'ı tarar). Geçiş yerleri modelden:
#   alt plaka: Ø16 motor kablo delikleri (TABAN motor_kablo_delik; ön motor z 200, arka motor z 36, plaka altından),
#   kat: ön kattaki kablo kesiği (TABAN kat_kesik_on, x −60…60, z 150…175: "kablo geçişi XL4016 / BTS → kat"), güç panelindeki akü
#   kablo yarıkları (x ±40…80, z −37…−23; taban_parcalar.py), ray üstü (y 134,5) ile kat altı (y 174,5) arasındaki boşluk.
# TAHMİN (kaynakta yok): kart üstündeki klemens / pin başlığı yeri (uç noktaları kart kutusunun kenarında alındı), kablonun kat üstünde
# kartların arasından geçiş çizgisi, sonar pin bloğundan çıkış, arka motor enkoder kablosunun motordan çıkışı. Dağıtım kartı C
# modelsiz: şemaya özgü nominal nokta DAGITIM_C (rehber_kablo.SEMA_KONUM; yeri yaklaşık).
# P10.7b2k (planlama/d158/F10u-gunluk.md § A4): bara tutucuları P10.7b2j'de modelde (K64 a; arayuz TABAN["bara_tutucu"]). G16 ve
# G22 anahtarlı baradaki kendi saplamasından başlar (kablolar.json bara-pabuc yerleşimi; numara = modeldeki saplama sırası, önden
# bakınca soldan sağa, rehber B5a). Şema uçları rehber_kablo.SEMA_KONUM'daki vekil (Bara tutucusu …) kutusuyla sınanır; ölçüler
# aşağıda sabit (bu dosya arayuz'u yalnız okur, tutucu birleşmeden önce de içe aktarılabilsin), rehber_kablo.bara_tutarlilik arayuz
# TABAN["bara_tutucu"] ile aynı olduklarını sınar.
# Yol uzunluğu boy ölçümü değildir (kablolar.json boy alanları bu dosyadan yazılmadı).
import math
import os
import sys

_UST = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _UST not in sys.path:
    sys.path.insert(0, _UST)
import arayuz as A

T = A.TABAN
Y_PL0, Y_PL1 = A.Y_PL, A.Y_RAIL0                   # alt plaka alt / üst yüzü (91,5 / 94,5)
Y_KAT0, Y_KAT1 = A.Y_DECK0, A.Y_DECK1              # kat alt / üst yüzü (174,5 / 179,5)
Y_ALT = Y_PL0 - 4.5                                # plaka altı kablo hattı (yol 4 ile aynı: y 87)
Y_ARA = Y_KAT0 - 19.5                              # ray üstü ile kat altı arası hat (155; BTS üstünden ≈ 9 mm yukarıda)
Y_UST = Y_KAT1 + 4.5                               # kat üstü hat (184; kartlar 8 mm burçla 188'de)
Y_KART = Y_KAT1 + 16.5                             # kart üstü uç yüksekliği (196; kart kutusunun yan yüzüne yakın)
H_ARKA = T["motor_kablo_delik"][1]                 # (80, 36): arka motor kablosu plaka altından
KK = T["kat_kesik_on"]                             # (x0, x1, z0, z1)
Z_KK = 0.5 * (KK[2] + KK[3])                       # kesik ortası z (162,5)
BTS = dict(zip(("sol", "sag"), T["bts"]))          # (x, z) merkez
XL_CEVRE = T["xl"][1][:2]
XL_C = T["xl_kafa"]["merkez"]
AK = T["arayuz_karti"]
ESP = T["esp"]
RL = T["role"]
ANA = T["ana_anahtar"]
SON = A.SONAR
DX = A.TABAN_DX
# Dağıtım kartı C (modelde yok; kablolar.json karar P7b2a-6: "güç panelinde, XL4016 C'nin yanında"): SV3 şemasının son noktası ve
# rehber_kablo.SEMA_KONUM'daki nominal noktası (P10.7b2c düzeltme turu 1; şema sınaması ikisinin aynı olduğunu sınar). Yer TAHMİN:
# XL4016 C'nin −z yanında, kutusunun −z kenarından 36,5 mm ötede, kart üstü yüksekliğinin 4 mm altında. Yeri yaklaşık.
DAGITIM_C = (XL_C[0] + 2.5, Y_KART - 4.0, -60.0)
# Bara tutucuları (arayuz TABAN["bara_tutucu"], P10.7b2j): saplama x'leri ve tutucu ekseni z; pabuç yığını tutucu üstünde (y 179,5 + 10,
# 4 × 1,2 mm VARSAYIM), şema ucu yığının ortasında, saplamanın 5 mm önünde (+z: pabuç dili).
BARA = dict(yildiz=dict(z=-55.0, saplama_x=(-50.0, -25.0, 0.0, 25.0, 50.0)),
            anahtarli=dict(z=-115.0, saplama_x=(-37.5, -12.5, 12.5, 37.5)))
BARA_H = 10.0
Y_PABUC = Y_KAT1 + BARA_H + 2.4                    # 191,9
Y_BARA_UST = Y_KAT1 + BARA_H + 5.5                 # 195: tutucu üstü + pabuç yığını; bara kabloları bu yükseklikte yatay (F10t § 1.3)


def bara_saplama(bara, no):
    """Baranın no numaralı (1'den, modeldeki sıra) saplamasındaki şema ucu (global)."""
    b = BARA[bara]
    return (b["saplama_x"][no - 1], Y_PABUC, b["z"] + 5.0)


def _ak_kenar(z=None, x=None):
    """Arayüz kartının kenarına 4 mm uzaklıkta, kart üstü yüksekliğinde uç noktası (+x kenarı ya da +z / −z kenarı)."""
    cx, cz = AK["merkez"]
    lx, lz = AK["olcu"]
    if x is None:
        return (cx + lx / 2 + 4.0, Y_KART, z)
    return (x, Y_KART, cz - lz / 2 - 4.0 if z == "arka" else cz + lz / 2 + 4.0)


def _esp_kenar(z):
    """ESP32 taşıyıcı kartının −x kenarına 4 mm uzaklıkta uç noktası (taşıyıcı 70 × 50; ESP32 başlıkları kartın üstünde)."""
    return (ESP["merkez"][0] - ESP["tasiyici"][0] / 2 - 4.0, Y_KART, z)


def yollar():
    xa = H_ARKA[0]
    za = H_ARKA[1]
    # arka sol / sağ motorun kablo çıkışı: yol 4'ün son noktasının (arka sağ) aynası (B2b "motor kablo çıkışı içe"; TAHMİN)
    m_sol = (-(100.0 + DX), 85.0, -185.0)
    s_y = SON["y"] + 17.0                         # sonar PCB'sinin üst kenarının üstü (y 127; tutucunun üst bandı 124'te biter)
    z_s = T["sonar_on_z"] - 1.0                   # PCB ön yüzünün hemen arkası (255; etek iç yüzü önde)
    z_ray = A.L0 / 2 - 15.0                       # ön ara rayın üstü (235; ray z 210…250, üst yüzü y 134,5)
    yol = {
        # T1 taban güç paneli ---------------------------------------------------------------------------------------------------------
        # G07: ana anahtarın çıkış saplaması (anahtar etek üst plakasının altında) → güç paneli üstü → elektronik katı → arayüz kartındaki
        # bölücünün orta noktası. x −56 hattı: sigorta kutusunun (x ≥ −52) ile ön şarj kartının (x ≤ −62) arası.
        "G07": [(ANA["merkez"][0] + ANA["olcu"][0] / 2 - 3.0, 214.0, ANA["merkez"][1] + ANA["olcu"][1] / 2 - 3.0),
                (-56.0, Y_UST, -165.0), (-56.0, Y_UST, 45.0), _ak_kenar(x=-70.0, z="arka")],
        # G16: anahtarlı baranın 2. saplaması (G13 / G16) → hat sigortası (bara ucunda, modelde yok) → XL4016 C IN (−x kenarı). Panel
        # üstünde pabuç yüksekliğinde (y 195) yatay: yıldız barasının 2. ve 3. saplamasının arasından (x −12,5), U06 şeridinin
        # (x 14…40, z −40…−30, y ≥ 205) altından (F10t § 1.3).
        "G16": [bara_saplama("anahtarli", 2), (-12.5, Y_BARA_UST, -95.0), (-12.5, Y_BARA_UST, -30.0), (55.0, Y_BARA_UST, -5.0),
                (XL_C[0] - 32.5 - 4.0, Y_KART, XL_C[1])],
        # G22: anahtarlı baranın 4. saplaması → hat sigortası → PC817 #2 (arayüz kartının +x kenarı); yıldız barasının 1. ve 2.
        # saplamasının arasından (x −37,5) öne, kat üstüne. Düzeltme turu 1 (F10u-kontrol 7): yatay kısım iki baranın ortasında z −80
        # (eskisi −95: anahtarlı somunlarına 10,4 mm). Eksenlere 30 / 25 mm, tutucu kutularına 24 / 14 mm (anahtarlı z −126…−104,
        # yıldız −66…−44); M5 halka pabucun halkası eksenden ≈ 5 mm, dili kablosu yönünde (Echo kararı, geri alınabilir).
        "G22": [bara_saplama("anahtarli", 4), (37.5, Y_BARA_UST, -80.0), (-37.5, Y_BARA_UST, -80.0), (-37.5, Y_BARA_UST, 40.0),
                (-45.0, Y_BARA_UST, 60.0), _ak_kenar(z=70.0)],
        # SV3: XL4016 C OUT (−z kenarı) → dağıtım kartı C (modelde yok; güç panelinde XL4016 C'nin yanında, YERİ YAKLAŞIK)
        "SV3": [(XL_C[0] + 2.5, Y_KART, XL_C[1] - 23.5 - 4.0), (XL_C[0] + 2.5, Y_UST, -40.0), DAGITIM_C],
        # G19: XL4016 çevre OUT (alt kat) → ray üstü hat → ön kat kesiği → kat üstü → arayüz kartının çevre 5 V klemensi (+x kenarı)
        "G19": [(XL_CEVRE[0], Y_PL1 + 33.5, XL_CEVRE[1] + 25.0), (40.0, Y_ARA, 130.0), (40.0, Y_ARA, Z_KK), (40.0, Y_UST, Z_KK),
                _ak_kenar(z=92.0)],
        # T2 alt kat motor ------------------------------------------------------------------------------------------------------------
        # M02: BTS7960 sol M+ / M− (−z yüzü) → XL4016 B'nin dışından (x −88; yol 4'ün aynası XL4016'nın içinden geçiyordu) → arka motor
        # kablo deliği (x −80, z 36) → plaka altı → arka sol motor. Plaka altındaki bölüm yol 4'ün arka sağ bölümünün x aynası.
        "M02": [(-xa, Y_PL1 + 25.5, BTS["sol"][1] - 25.0), (-xa - 8.0, Y_PL1 + 25.5, 105.0), (-xa - 8.0, Y_PL1 + 20.5, za + 9.0),
                (-xa, Y_PL1 + 17.5, za + 4.0), (-xa, Y_PL0 - 3.5, za), (-xa, Y_ALT, -150.0), m_sol],
        # T3 taban sinyal -------------------------------------------------------------------------------------------------------------
        # B02: BTS7960 sağ sinyal başlığı (kart üstü, TAHMİN) → ön kat kesiği → kat üstü → ESP32 taşıyıcı (−x kenarı)
        "B02": [(BTS["sag"][0] - 15.5, Y_PL1 + 53.5, BTS["sag"][1]), (BTS["sag"][0] - 15.5, Y_UST, Z_KK), (40.0, Y_UST, 120.0),
                (40.0, Y_UST, 100.0), _esp_kenar(90.0)],
        # N01 / N02: arka motor enkoderi → plaka altı (motor kablosuyla aynı delik, 5 mm yanında) → ray üstü hat → ön kat kesiği →
        # ESP32 taşıyıcı
        "N01": [(-110.0, 80.0, -183.0), (-xa - 5.0, Y_ALT, -150.0), (-xa - 5.0, Y_ALT, za), (-xa - 5.0, Y_PL1 + 17.5, za + 4.0),
                (-xa - 5.0, Y_ARA, za + 4.0), (-50.0, Y_ARA, Z_KK), (-50.0, Y_UST, Z_KK), (35.0, Y_UST, 140.0), (38.0, Y_UST, 100.0),
                _esp_kenar(66.0)],
        "N02": [(110.0, 80.0, -183.0), (xa + 5.0, Y_ALT, -150.0), (xa + 5.0, Y_ALT, za), (xa + 5.0, Y_PL1 + 17.5, za + 4.0),
                (xa + 5.0, Y_ARA, za + 4.0), (25.0, Y_ARA, Z_KK), (25.0, Y_UST, Z_KK), (38.0, Y_UST, 110.0), (38.0, Y_UST, 90.0),
                _esp_kenar(78.0)],
        # Q01 / Q02: sonar pin bloğu (PCB üst kenarının üstü, TAHMİN) → ön ara rayın üstü → ray üstü hat → ön kat kesiği → arayüz kartı
        # (+z kenarı; bölücü, çevre 5 V, GND; Trig kart üstünden PCA9685'e)
        "Q01": [(SON["x"][2], s_y, z_s), (SON["x"][2], A.Y_RAIL1 + 5.5, z_s), (SON["x"][2], A.Y_RAIL1 + 5.5, z_ray), (10.0, Y_ARA, 200.0),
                (10.0, Y_ARA, Z_KK), (10.0, Y_UST, Z_KK), (-60.0, Y_UST, 115.0), _ak_kenar(x=-100.0, z="on")],
        "Q02": [(SON["x"][1], s_y, z_s), (SON["x"][1], A.Y_RAIL1 + 5.5, z_s), (SON["x"][1], A.Y_RAIL1 + 5.5, z_ray), (-10.0, Y_ARA, 200.0),
                (-10.0, Y_ARA, Z_KK), (-10.0, Y_UST, Z_KK), (-50.0, Y_UST, 118.0), _ak_kenar(x=-75.0, z="on")],
    }
    return yol


# ---------------------------------------------------------------------------------------------------- kat / plaka geçiş denetimi
# Yol bir levhanın (alt plaka, kat) orta düzlemini levhanın içindeki bir noktada geçiyorsa o nokta bilinen bir geçiş yerinde olmalı:
# alt plakada Ø16 kablo deliği (merkeze uzaklık + kablo yarıçapı ≤ delik yarıçapı), katta ön kat kesiği ya da akü kablo yarıkları
# (kenarlara en az kablo yarıçapı). Levha dışından (x / z sınırı dışı) geçiş serbest; levhanın içinde yatay giden bölüm hata.
def _plaka_ici(x, z):
    P = T["plaka"]
    return abs(x) <= P["x"] and abs(z) <= P["z"]


def _kat_ici(x, z):
    return abs(x) <= A.V3_W / 2 and abs(z) <= A.L0 / 2


def _kesik_ici(x, z, r, k=KK, rk=5.0):
    x0, x1, z0, z1 = k
    if not (x0 + r <= x <= x1 - r and z0 + r <= z <= z1 - r):
        return False
    if rk <= 0:
        return True
    cx, cz = min(max(x, x0 + rk), x1 - rk), min(max(z, z0 + rk), z1 - rk)   # yuvarlatılmış köşe (taban_lib.kesik_r, R 5)
    return math.hypot(x - cx, z - cz) <= rk - r + 1e-9 if (cx != x or cz != z) else True


GECIS_KAT = [("ön kat kesiği", KK, 5.0)] + [("akü kablo yarığı %s" % ("sağ" if s > 0 else "sol"),
                                              tuple(sorted((s * 40.0, s * 80.0))) + (-37.0, -23.0), 0.0) for s in (1, -1)]


def gecis_denetle(pts, r=2.5):
    """[(levha, nokta, sonuç)]: her levha geçişi ve levha içinde yatay giden bölüm; sonuç None = bilinen geçiş, yoksa neden."""
    out = []
    levhalar = (("alt plaka", Y_PL0, Y_PL1, _plaka_ici), ("kat", Y_KAT0, Y_KAT1, _kat_ici))
    for a, b in zip(pts[:-1], pts[1:]):
        for ad, y0, y1, ici in levhalar:
            yc = 0.5 * (y0 + y1)
            if a[1] != b[1] and (a[1] - yc) * (b[1] - yc) <= 0:
                t = (yc - a[1]) / (b[1] - a[1])
                x, z = a[0] + (b[0] - a[0]) * t, a[2] + (b[2] - a[2]) * t
                if not ici(x, z):
                    out.append((ad, (x, yc, z), None))
                elif ad == "alt plaka":
                    d = min(math.hypot(x - sx * hx, z - hz) for sx in (-1, 1) for hx, hz in T["motor_kablo_delik"])
                    ok = d + r <= T["kablo_delik_d"] / 2 + 1e-9
                    out.append((ad, (x, yc, z), None if ok else "plakada delik yok (en yakın Ø16 deliğin merkezine %.1f mm, r %.1f)" % (d, r)))
                else:
                    ok = any(_kesik_ici(x, z, r, k, rk) for _n, k, rk in GECIS_KAT)
                    out.append((ad, (x, yc, z), None if ok else "katta kesik yok (x %.1f, z %.1f)" % (x, z)))
            m = tuple(0.5 * (a[k] + b[k]) for k in range(3))
            if y0 - r < a[1] < y1 + r and y0 - r < b[1] < y1 + r and ici(m[0], m[2]) and math.dist(a, b) > 1.0:
                out.append((ad, m, "bölüm levhanın içinde yatay gidiyor"))
    return out


def uzunluk(p):
    return sum(math.dist(a, b) for a, b in zip(p[:-1], p[1:]))


def ozet():
    y = yollar()
    return dict(yol={k: dict(yol_mm=round(uzunluk(v)), nokta=len(v), gecis=[(a, [round(c, 1) for c in n], s) for a, n, s in gecis_denetle(v)])
                     for k, v in y.items()},
                not_="Gösterim şeması; çarpışma taramasından geçmedi. Yol uzunluğu boy ölçümü değil.")


if __name__ == "__main__":
    import json
    print(json.dumps(ozet(), indent=1, ensure_ascii=False))
