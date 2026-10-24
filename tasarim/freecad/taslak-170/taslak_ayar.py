# Lale 1,70 m TASLAK varyanti - tek parametre kaynagi (saf Python; FreeCAD olmadan import edilir)
#
# Kararlar (21 Ekim 2026, hoca + ekip): boy 1700 mm (yerden kafa tepesine), yuz kafada, yuz ekrani 10" sinifi HDMI
# (kesin model belli degil), otonomi yok (lidar / lidar diregi / haritalama kapsam disi), kumanda telefondan.
# Bu klasor mevcut modulleri ve ana montaji DEGISTIRMEZ: modul betikleri (../<modul>/*_parcalar.py) oldugu gibi import edilir,
# varyant farklari (uzayan direk, uzatma kabuk bantlari, yeni kafa, uzun kol) burada ve taslak_parcalar.py'de uygulanir.
# Kararlar (24 Ekim 2026, Duffy): kol x1,25 (ek on kola), omuz S1/S2 servolari DS3235 (bolum 2).
# Koordinat: global (../arayuz.py): orijin zemin + robot merkezi, +X sag, +Y yukari, +Z ileri (yuz), mm.
# Kaynagi olmayan deger "tahmini".
import os, sys, math

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
if UST not in sys.path:
    sys.path.insert(0, UST)
import arayuz as A

# =====================================================================================================
# 1) Boy zinciri
# =====================================================================================================
BOY = 1700.0                                # yerden kafa tepesine (karar, 21 Ekim 2026)
# Yeni kafa (kafa10.py): govde (ekran merkezine gore) y -100 ... +115 -> 215 mm; kafa yerelinde (traversin ust yuzu = 0)
# alt yuzu y 75'te (pan suprulmesinde omuz S1 kaseti tepesi y ~57 + 18 mm pay; eski kafa altta y 95).
KAFA_GOVDE_Y = (-100.0, 115.0)              # ekran merkezine gore kafa kabugu alt / ust dis yuzu
KAFA_ALT_YEREL = 75.0                       # kafa kabugu alt yuzu, kafa yerelinde
KAFA_UST_YEREL = KAFA_ALT_YEREL + (KAFA_GOVDE_Y[1] - KAFA_GOVDE_Y[0])     # 290 (eski HEAD_UP 275)
S3_YENI = BOY - A.SG / 2 - KAFA_UST_YEREL   # omuz ekseni = travers merkezi (1390; eski 955)
DY = S3_YENI - A.S3                         # uzama: omuz ve ustu bu kadar yukari (435)
assert abs(DY - round(DY)) < 1e-9

# Uzama nereye: govde kabugunun ilk yatay dikisinde (A.GOVDE_DIKIS[0] = 476,5) sabit kesitli iki uzatma bandi.
# Dikisin altindaki her sey (taban, etek, govde alt bandi, alt govde braketleri) yerinde; ustundekiler DY yukari.
UZATMA_Y0 = A.GOVDE_DIKIS[0]                # 476,5
UZATMA_BANT = 2                             # baski tablasi 250 (hedef <= 230): 435 / 2 = 217,5 mm
UZATMA_DIKIS = [UZATMA_Y0 + DY * k / UZATMA_BANT for k in range(UZATMA_BANT + 1)]   # 476,5 / 694 / 911,5
UST_ESIK_Y = UZATMA_Y0 + A.KABUK_BINDIRME + 1.0     # sinir kutusu merkezi bunun ustundeki kabuk parcalari DY tasinir (489,5)
# Uzatma bandi govde braketleri (3 mm Al U, direk +-X kanalina 2x M6 + cekic somun, kabuga M5 + isil gomme): bant basina bir cift
UZATMA_BRAKET_Y = [UZATMA_DIKIS[k] + DY / UZATMA_BANT / 2 - A.KABUK_GOVDE_BRAKET["m5_y"] for k in range(UZATMA_BANT)]

DIREK_Y1_YENI = A.DIREK_Y1 + DY             # 1370
DIREK_L_YENI = DIREK_Y1_YENI - A.DIREK_Y0   # 1235,5 (1 m stok yetmez: 1,5 / 2 m boy ya da ozel kesim; acik is)

# =====================================================================================================
# 2) Kol (boyla orantili x1,36 yerine). KARAR (Duffy, 24 Ekim 2026): x1,25 (kol analizi kol-analiz/rapor.html onerisi).
#    Eski x1,15 secenegi geri alinabilir: TASLAK_KOL=115 ortam degiskeniyle yeniden uretilir (varsayilan 125).
#    Uzatma uc yere dagitilir (omuz ekseninden el ucuna):
#      UST_KOL_UZAMA: ust kol tupu (omuz Kol grubu, PETG tup), dirsek ekseni bu kadar asagi
#      ON_KOL_UZAMA : on kol govdesi, dirsek servosu ile bilek servosu arasindaki U bolum (s = 42,75'te kesilip uzatilir);
#                     bilek servosu + bilek flansi + el (bilek ekseni) bu kadar daha asagi; dirsek servosu yerinde
#      EL_UZAMA     : bilek yakasi (el boynu) 13,6 -> 32,6 mm (O34 / O22 bos tup); kol analizi: yaka uzadikca bilek mili
#                     konsolu buyur, yakadaki 2x M3 zayif halka -> x1,25'te yaka 32,6'da kalir
#    x1,25 dagilim gerekcesi (KOL125-NOTLAR.md, rapor): ek 32,4 mm on kola. S1 sinirlayici eklem (DS3235 x1,25 ivmeli pay ~1,6);
#    ek tupe verilseydi tum dirsek grubu (~380 g) uzaklasirdi, on kola verilince yalniz bilek servosu + el (~160 g): S1 momenti
#    daha az artar. Tup +Y basili (egilme katmanlar arasi), uzatilmadi. Dirsek MG996R payi genis (statik ~2 / stall 9,4 kg.cm).
# =====================================================================================================
KOL_BOY_ESKI = -A.DIRSEK["el_ucu"][1]       # omuz ekseninden el ucuna 325,5
KOL_SECENEK = {
    "115": dict(oran=1.15, ust_kol=30.0, on_kol=0.0, el=19.0, karar="21 Ekim 2026 taslak (tasarim ajani): 374,5 mm, x1,1505"),
    "125": dict(oran=1.25, ust_kol=30.0, on_kol=32.4, el=19.0, karar="Duffy, 24 Ekim 2026: x1,25 + omuz DS3235; ek 32,4 mm on kola (406,9 mm, x1,2501)"),
}
KOL_SECIM = os.environ.get("TASLAK_KOL", "125")
assert KOL_SECIM in KOL_SECENEK, "TASLAK_KOL 115 ya da 125 olmali"
_KS = KOL_SECENEK[KOL_SECIM]
KOL_ORAN_HEDEF = _KS["oran"]
UST_KOL_UZAMA = _KS["ust_kol"]              # ust kol tupu 100 -> 130 mm
ON_KOL_UZAMA = _KS["on_kol"]                # on kol (dirsek ekseni -> bilek ekseni) 83,1 -> 115,5 mm (x1,25)
EL_UZAMA = _KS["el"]                        # el yakasi +19 (degismez)
KOL_KARAR = _KS["karar"]
KOL_BOY_YENI = KOL_BOY_ESKI + UST_KOL_UZAMA + ON_KOL_UZAMA + EL_UZAMA     # x1,25: 406,9 (x1,15: 374,5)
KOL_ORAN = KOL_BOY_YENI / KOL_BOY_ESKI
ON_KOL_KES_S = 42.75                        # on kol kesit yeri: dirsek ekseninden on kol boyunca (ara duvar alti 42,0 ile bilek servosu tabani 43,5 arasi)

# Omuz servolari (S1 one-arka, S2 yana acma; iki kol). KARAR (Duffy, 24 Ekim 2026): DS3218MG -> DS3235.
# Govde DS3218 ile ayni kabul (40 x 20 x 40, kulak delikleri 49,5 x 10, 25T cikis): geometri DEGISMEDI, yalniz ad / kod / not.
# Govde yuksekligi kaynaklarda 38,5 (DS3235 datasheet, Rochester ME240 kopyasi) / 40 (Robocombo tablosu) / 40,5 (probots) ->
# servo gelince kumpasla dogrulanacak. Kutle 60 g (datasheet; DS3218 ile ayni). Veri: kol-analiz/NOTLAR.md "1) Servo verisi".
OMUZ_SERVO_SECENEK = {
    "DS3218MG": dict(ad="DS3218MG", kod="DS3218MG servo", kutle_g=60.0, tork_kgcm="20 (6 V civari, tahmini; proje degeri)", not_=""),
    "DS3235": dict(ad="DS3235", kod="DS3235 servo", kutle_g=60.0, tork_kgcm="29 / 32 / 35 @ 5 / 6 / 7,4 V (satici tablosu + datasheet)",
                   not_="DS3235 (karar 24 Ekim 2026; eski DS3218MG). Govde DS3218 ile ayni kabul: 40x20x40, kulak delikleri 49,5x10, 25T. "
                        "Govde yuksekligi kaynaklarda 38,5 / 40 / 40,5 mm: servo gelince kumpasla dogrulanacak. 60 g (datasheet)"),
}
OMUZ_SERVO = OMUZ_SERVO_SECENEK[os.environ.get("TASLAK_OMUZ_SERVO", "DS3235")]
OMUZ_SERVO_ESKI = OMUZ_SERVO_SECENEK["DS3218MG"]

# =====================================================================================================
# 3) Kafa: yuz ekrani 10,1" 1280x800 HDMI (TAHMINI MODEL), tilt ekseni kafa AM'sinden, +-15 derece
# =====================================================================================================
# Hoca HDMI girisli bir ekran verecek, model belli degil. Olcu icin Waveshare 10.1inch HDMI LCD (B) (1280x800, kapasitif):
# raporlar/kaynaklar/04-parca-olculeri.md satiri ve tasarim/cad/robot_cad.py l10_* (Waveshare 2D PDF). Kasa on plakasi kullanilmaz;
# cerceveyi kafa on kabugu yapar. Kutle dogrulanmadi: robot_cad m_l10 = 0,60 kg (tahmini) aynen alindi.
EKRAN10 = dict(
    model="Waveshare 10.1inch HDMI LCD (B) 1280x800 (TAHMINI MODEL: hocanin verecegi ekran gelince olculecek)",
    cam=(253.96, 168.60), cam_pencere=(217.96, 136.60), aktif=(216.96, 135.60), kalinlik=18.0,
    panel_t=4.0, kart_ic=6.0, kart_t=5.0, konnektor=(45.0, 12.0, 30.0),   # robot_cad lcd10(): panel 4, arka kart kenardan 6 iceride, 5 kalin; konnektor x l/2-45...l/2-12, y +-30
    kutle_g=600.0,
    kaynak="04-parca-olculeri.md (Waveshare 10.1inch HDMI LCD (B) 2D PDF) + robot_cad.py l10_*; kutle robot_cad m_l10 0,60 (tahmini)",
)
TILT_ARALIK = (-15.0, 15.0)                 # karar: +-15 derece (eski -25...30)
PAN_ARALIK = tuple(A.KAFA["pan_aralik"])    # degismez (-90...90)
KAFA_TILT_Z = A.KAFA["tilt_nokta"][2]       # 25: tilt ekseninin pan eksenine one kaciklik (mevcut catal, degismez)
TILT_ESKI_Y = A.KAFA["tilt_nokta"][1]       # 130 (kafa yereli)
# Boyun yukseltme adaptoru (yeni, PETG): boyun mili flansi (y 96) ile egme catali arasina girer, catal + tilt servosu + pim bu
# kadar yukari kalkar. Yukseklik kafa10.dengele() sonucundan: tilt ekseni = KAFA_ALT_YEREL - (ekran merkezi - kafa alti) - dy.

# =====================================================================================================
# 4) Taban genisligi PARAMETRESI (karar analiz ajaninda). Varsayilan = mevcut taban (etek 2 x 222 = 444 mm; teker merkezi x +-178)
# =====================================================================================================
TABAN_W_ESKI = 2 * A.ETEK_A                 # 444
TABAN_W = float(os.environ.get("TASLAK_TABAN_W", TABAN_W_ESKI))      # ortam degiskeniyle denenebilir: TASLAK_TABAN_W=520
TABAN_DX = (TABAN_W - TABAN_W_ESKI) / 2     # her yana; 0 = mevcut taban birebir
assert TABAN_DX >= 0.0, "taban daraltma tanimli degil"
assert TABAN_DX <= 70.0, "etek ust plakasinin duz bolgesi (|x| < 90) dolgu seridine yetmez"

# =====================================================================================================
# 5) 3D yazici: okul yazicisi tablasi 25 x 25 x 25 cm (hoca; model dogrulanmadi). Parca hedefi <= 230 (README: pay icin <= 23 cm)
# =====================================================================================================
TABLA = (250.0, 250.0, 250.0)
TABLA_HEDEF = 230.0

# =====================================================================================================
# 6) Payli kutleler (parca listesinde yok, tahmini)
# =====================================================================================================
KABLO_PAY_TABAN = dict(kutle_g=400.0, merkez=(0.0, 150.0, -60.0), kaynak="taban_parcalar.KABLO_PAY (mevcut tahmin)")
KABLO_PAY_UZAMA = dict(kutle_g=45.0, merkez=(0.0, UZATMA_Y0 + DY / 2, -26.0),
                       not_="tahmini: govde kablo demeti 435 mm uzar (12 V cift 18 AWG, iki kolun 3'er servo uzatmasi, ESP32 USB, tilt "
                            "servosu: ~14 damar x 0,435 m x ~7 g/m); direk arkasindan (z -26) gecer")
KABLO_PAY_KAFA = dict(kutle_g=25.0, kaynak="kafa-analiz.json tork.tilt.kablo_payi (FPC, micro HDMI, USB-C, 12 V); kafa AM'sine dahil edilmedi")

KOORDINAT = "orijin zemin + robot merkezi; +X robotun sagi, +Y yukari, +Z ileri (yuz); mm"

if __name__ == "__main__":
    print("S3 yeni %.1f (eski %.1f), uzama %.1f, direk %.1f, uzatma dikisleri %s" % (S3_YENI, A.S3, DY, DIREK_L_YENI, UZATMA_DIKIS))
    print("kol [%s] %.1f -> %.1f (x%.4f; tup +%.1f, on kol +%.1f, yaka +%.1f), omuz servosu %s, taban %.0f (dx %.1f)" % (
        KOL_SECIM, KOL_BOY_ESKI, KOL_BOY_YENI, KOL_ORAN, UST_KOL_UZAMA, ON_KOL_UZAMA, EL_UZAMA, OMUZ_SERVO["ad"], TABAN_W, TABAN_DX))
    print("uzatma braketleri y", UZATMA_BRAKET_Y)
