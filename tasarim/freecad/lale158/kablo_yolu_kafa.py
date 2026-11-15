# Lale 1,58 m: kafa içi ve ses kablolarının gösterim şemaları (P10.7b2c ikinci yarı; saf Python, FreeCAD'siz içe aktarılır).
# kablo_yolu_ekran.py / kablo_yolu_taban.py kalıbında: PARÇA DEĞİL, rehber-veri.json "semalar"a girer (rehber_metin.SEMA kaynağı
# "kafa_ici"; kaynak ad = ana kablo kimliği); parça sayısı ve çarpışma taraması bundan etkilenmez. İzlenen CAD kaynaklarına dokunmaz;
# yalnız arayuz.py ölçülerini OKUR (kafanın ev pozundaki yeri).
#
# Çerçeve: noktalar kafa-analiz.json'un kafa yerel çerçevesinde yazıldı (kutularla aynı çerçeve; +X sağ, +Y yukarı, +Z ileri, mm);
# yollar() global ev pozuna çevirir: (x, S3 + SG / 2 + y, z) = kafa-analiz.json yerlesim.konum (0; 1290; 0) eklenir. kablo_yolu_ekran
# kafa_ici_qled() aynı kafanın tilt ekseni çerçevesidir (yerel = tilt + (0; 188,878; 25)); bas() bu dosyanın noktalarını o çerçeveye
# çevirir.
#
# Bu çizim şemadır, ÇARPIŞMA TARAMASINDAN GEÇMEDİ. Uçların ve geçişlerin dayanağı:
#   tabla üstü: modüllerin köpük bandı y 220,9…221,9 (kafa-analiz.json): tabla üst yüzü y 220,9; tabla üstündeki tel ekseni y 224…226.
#   SY8205: kutu x 14,2…57,8; çıkış (K04) kartın +x ucunda (kablo_yolu_ekran "Power USB" başı x 58): giriş ucu −x ucu varsayıldı (TAHMİN).
#   D24V50F5: kutu x −88,9…−71,1, z 20,9…41,1; VIN / GND ve VOUT / GND pinlerinin kenarı kaynakta yok: +x kenarı alındı (TAHMİN).
#   Pi 5: kart kenarı (y = 0 kenarı) önde, z −1,2; USB-C kart kenarının 11,2 mm'sinde, CSI x 47…57'de (kafa_lib.py PI5_BILESEN, port
#         tablosu; micro HDMI 0 / 1 x −16,7 / −3,3 ile aynı kart referansı x −42,5): USB-C x −31,3, CSI ortası x 9,5.
#   Kamera: kutu x ±12,5, y 261,6…285,5, z 61,9…73,5 (yüz kabuğunda, QLED'in üstünde); şerit QLED'in üst kenarının (y 251,8) üstünden
#         geçer. Kamera kartındaki konnektörün yeri kaynakta yok: kartın alt kenarı alındı (TAHMİN).
#   ReSpeaker: kutu x 4,6…75,6, y 273,8…286,9; 3,5 mm jakın yeri kaynakta yok: USB'nin yanında, kartın +x kenarında alındı (TAHMİN;
#         kablo_yolu_ekran "Dizi USB" başı (95; 282,9; 1,8) USB fişinin arka ucu).
#   PAM8403: kutu x −131,5…−126,5, y 251,9…269,9, z −6,5…17,5 (sol yan duvar); giriş pedlerinin yeri kaynakta yok (TAHMİN).
# Modelsiz uçlar (rehber_kablo.SEMA_KONUM):
#   kafa giriş kartı (P6KE18A + 3 klemens, K01 / K02'nin başı): modelde yok; GIRIS_KARTI noktası yaklaşık (boyun geçişinin x −50…−37
#         solunda, D24V50F5'e ve Pi'ye > 10 mm). Yeri kaynakta yok (E3a kartın yerini yazmaz): "yeri yaklaşık".
#   ses bölücüsü (AU1 sonu, AU2 başı): kayıtta "PAM giriş pedlerinin dibinde, kablo üstünde" (kablolar.json O-9); varlığı ve yeri masa
#         denemesine (KT2) bağlı: şemada PAM'ın dibinde, ayrı nokta yok (vekil PAM8403 kutusu).
# Yol uzunluğu boy ölçümü değildir (kablolar.json sema_boy alanı "gösterim şeması yolu; ölçüm değil" etiketiyle bu dosyadan türer).
import math
import os
import sys

_UST = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _UST not in sys.path:
    sys.path.insert(0, _UST)
import arayuz as A

Y0 = A.S3 + A.SG / 2                               # kafa yerel çerçevesinin global y'si (kafa-analiz.json yerlesim.konum 1290)
TILT = A.KAFA["tilt_nokta"]                        # (26,9; 188,878; 25): tilt ekseni, kafa yerel
Y_TABLA = 224.0                                    # tabla üstündeki 18 AWG telin ekseni (tabla 220,9 + yarıçap 3,1)
GIRIS_KARTI = (-58.0, Y_TABLA, 30.0)               # kafa giriş kartının çıkış klemensleri (modelde yok; yeri yaklaşık)
PI_USBC = (-31.3, 231.0, 3.0)                      # Pi 5 USB-C fişinin arka ucu (kart kenarı z −1,2; fiş TAHMİN)
PI_CSI = (9.5, 236.0, 1.0)                         # Pi 5 CSI konnektörünün üstü (kart kenarı)
D24_SAG = -69.0                                    # D24V50F5'in +x kenarına 2,1 mm (kutu x −71,1)
SY_GIRIS = (12.0, 225.0, 39.0)                     # SY8205'in −x ucu (kutu x 14,2), giriş klemensi TAHMİN
JAK = (82.0, 280.0, -9.0)                          # ReSpeaker 3,5 mm jakı (TAHMİN)
PAM_GIRIS = (-121.0, 262.0, 8.0)                   # PAM8403 giriş pedleri (kutu x −126,5; TAHMİN); ses bölücüsü burada


def yerel():
    """Kafa yerel çerçevesinde (kafa-analiz.json) noktalar: {kaynak ad: [(x, y, z)]}."""
    return {
        # Kafa giriş kartı → D24V50F5 VIN / GND (K01, 18 AWG): kısa çift, tabla üstünde
        "K01": [GIRIS_KARTI, (-64.0, Y_TABLA, 36.0), (D24_SAG, 226.0, 36.0)],
        # Kafa giriş kartı → SY8205 IN+ / IN− (K02): tabla üstünde, Pi'nin önünden (z 30…39), boyun kablolarının (z 12) önünden
        "K02": [GIRIS_KARTI, (-30.0, Y_TABLA, 36.0), (0.0, Y_TABLA, 39.0), SY_GIRIS],
        # D24V50F5 VOUT / GND → Pi 5 USB-C (K03): D24'ün +x kenarının arka ucundan Pi'nin kart kenarına
        "K03": [(D24_SAG, 226.0, 24.0), (-50.0, 226.0, 10.0), (-31.3, 228.0, 6.0), PI_USBC],
        # Pi CSI → kamera (C01, 300 mm FPC): kart kenarından yukarı ve öne, QLED'in üst kenarının üstünden kameranın alt kenarına
        "C01": [PI_CSI, (9.5, 240.0, 30.0), (5.0, 256.0, 50.0), (0.0, 259.0, 64.0)],
        # ReSpeaker 3,5 mm → ses bölücüsü → PAM8403 sol girişi (AU1, AU2): ReSpeaker kartının altından sola, Pi'nin üstünden
        "AU1": [JAK, (82.0, 266.0, -9.0), (-100.0, 264.0, -2.0), PAM_GIRIS],
    }


def yollar():
    """Global ev pozu noktaları: {kaynak ad: [(x, y, z)]} (rehber_kablo.sema_noktalari "kafa_ici")."""
    return {k: [(p[0], Y0 + p[1], p[2]) for p in v] for k, v in yerel().items()}


def bas():
    """Aynı noktalar tilt ekseni (Baş) çerçevesinde (kablo_yolu_ekran.kafa_ici_qled ile aynı çerçeve)."""
    return {k: [(p[0], p[1] - TILT[1], p[2] - TILT[2]) for p in v] for k, v in yerel().items()}


def giris_karti_global():
    return (GIRIS_KARTI[0], Y0 + GIRIS_KARTI[1], GIRIS_KARTI[2])


def uzunluk(p):
    return sum(math.dist(a, b) for a, b in zip(p[:-1], p[1:]))


def ozet():
    return dict(yol={k: dict(yol_mm=round(uzunluk(v)), nokta=len(v)) for k, v in yollar().items()},
                not_="Gösterim şeması; çarpışma taramasından geçmedi. Yol uzunluğu boy ölçümü değil.")


if __name__ == "__main__":
    import json
    print(json.dumps(ozet(), indent=1, ensure_ascii=False))
