# 3B montaj rehberi: parça → adım seçicileri, 1,58 m modeli (F7a, 09.11.2026). Saf Python; FreeCAD'siz import edilir ve test edilir.
#
# Neden ayrı dosya (planlama/adim4/M6_erisim.py ADIMLAR yerine): M6_erisim.py 125 cm erişim analizidir; çıktısı M6_erisim_sonuc.json ve
# M6-montaj-sirasi.md tablosu o seçicilerle üretildi. Seçicileri orada değiştirmek, analizi 1,58 m'de yeniden koşmadan (FreeCAD, uzun,
# paylaşılan makine) betik / JSON / tablo üçlüsünü birbirinden koparırdı. Burada değiştirmek yalnız rehberi etkiler; M6 dosyaları 125 cm
# kaydı olarak tutarlı kalır. M6_erisim.py 1,58 m'de yeniden koşulacaksa ADIMLAR buradan alınmalı (planlama/d158/F7a-gunluk.md).
#
# Kural: ADIMLAR listesinde ilk eşleşen satır kazanır. Satır = (rehber adım kodu, tezgâh anahtarı ya da None, seçici).
# Seçici parça sözlüğü alır: modul, grup, ad, kod, tur, bb (global sınır kutusu: xmin, xmax, ymin, ymax, zmin, zmax; y zeminden yukarı).
# Adım kodları M6-montaj-sirasi.md tablosundaki kodlardır (48 satır + F5). Referans parçalar (kablo şemaları) burada değil, rehber_veri.py'de.
import re


def _m(*mods):
    return lambda p: p["modul"] in mods


def _ad(*parcalar):
    return lambda p: any(s in p["ad"] for s in parcalar)


def _ve(*f):
    return lambda p: all(x(p) for x in f)


def _veya(*f):
    return lambda p: any(x(p) for x in f)


def _g(*gr):
    return lambda p: any(p["grup"].startswith(x) for x in gr)


def _degil(f):
    return lambda p: not f(p)


def _bag(p):
    return p["tur"] == "Baglanti"


def _y(p):
    return 0.5 * (p["bb"][2] + p["bb"][3])


def _z(p):
    return 0.5 * (p["bb"][4] + p["bb"][5])


def _etiket_y(p):
    """Gövde kabuğu bindirme etiketindeki dikiş yüksekliği: "(govde y476 on)" -> 476; yoksa None."""
    m = re.search(r"\(govde y(\d+)", p["ad"])
    return int(m.group(1)) if m else None


def _braket_y(p):
    """Gövde braketi etiketi: "(Govde braketi sag y1095)" -> 1095."""
    m = re.search(r"braketi (?:sag|sol) y(\d+)", p["ad"])
    return int(m.group(1)) if m else None


_O = _m("omuz_sag", "omuz_sol")
_D = _m("dirsek_sag", "dirsek_sol")
_K = _m("kabuk")
_T = _m("taban")
_KF = _m("kafa")

# ---------------------------------------------------------------- gövde kabuğu bölgeleri (kabuk_parcalar.py, lale158_rapor.py)
# Bant sırası F2 (alt, uzatma 1, uzatma 2, orta) -> F3 (göğüs) -> F4 (omuz). Dikiş etiketleri: y476 / y634 / y792 F2'nin kendi
# dikişleri, y1005 göğüs|orta (F3), y1198 göğüs|omuz (F4; ön basamak 1228). x = 0 dikişi: y < 1000 alt bantlar (F2); 1000…1240 göğüs
# bandının cep altı / üstü (y 1022,7 ve 1222; F3); üstü omuz bandı (F4). Gövde braketi M5: y 400 / 530 / 688 F2, y 1095 F3.
F2_DIKIS, F3_DIKIS, F4_DIKIS = (476, 634, 792), (1005,), (1198,)


def _x0_bant(p):
    if "(govde x0" not in p["ad"]:
        return None
    y = _y(p)
    return "F2" if y < 1000.0 else ("F3" if y < 1240.0 else "F4")


def _kabuk_bag(kod):
    def f(p):
        if not (_K(p) and p["grup"] == "Govde_kabugu" and _bag(p)):
            return False
        ey = _etiket_y(p)
        if ey is not None and "(govde x0" not in p["ad"]:
            return (kod == "F2" and ey in F2_DIKIS) or (kod == "F3" and ey in F3_DIKIS) or (kod == "F4" and ey in F4_DIKIS)
        if _x0_bant(p):
            return _x0_bant(p) == kod
        by = _braket_y(p)
        if by is not None:
            return (kod == "F2" and by < 1000) or (kod == "F3" and by >= 1000)
        return False
    return f


# Kafa: tabla (kafa iskeleti) üstündekiler E3a tezgâhında; yüz kabuğuna (QLED + tırnaklar, kamera) ve arka kabuğa (ReSpeaker, USB ses
# kartı, PAM8403) bağlananlar kabukla birlikte E4'te (kafa10_lib.py BAG listesi). Kabuk dikişi ve tabla → arka kabuk rafı cıvataları E4.
_KAFA_KABUK = ("Yuz kabugu", "Arka kafa kabugu", "Vizor", "Kabuk civatasi", "Yuz ekrani", "Ekran tirnagi", "Tirnak civatasi",
               "tirnak boss", "Kopuk bant (tirnak", "Kamera", "ReSpeaker", "Dizi vidasi", "USB ses karti", "PAM8403",
               "Kopuk bant (USB ses", "Kopuk bant (PAM", "Tabla civatasi", "(tabla rafi", "(kafa on/arka", "(kafa sag/sol")

ADIMLAR = [
    # ------------------------------------------------ iskelet
    ("A1", None, _ve(_m("iskelet"), _g("Sase"))),
    ("A2", None, _ve(_m("iskelet"), _g("Govde_diregi"))),
    ("A3", None, _ve(_m("iskelet"), _g("Omuz_traversi"))),
    # ------------------------------------------------ taban
    # Güç paneli katındaki kartlar (XL4016 C, ön şarj kartı; y > 170, Y3 yerleşimi) burç ve vidalarıyla B5a tezgâhında.
    ("B5a", "guc", _ve(_T, _g("Guc_aku"), lambda p: p["bb"][2] > 170.0, _degil(_ad("Ana anahtar")))),   # ana anahtar F1'de
    ("B1a", "plaka", _ve(_T, _veya(_ve(_g("Guc_aku"), _ad("naylon burc", " alt)")), _ad("takoz", "Isil gomme"),
                                   _ad("Alt plaka")))),
    ("B1", None, _ve(_T, _ad("(plaka,"))),
    ("B2a", None, _ve(_T, _g("Tahrik"), _veya(_ad("braketi", "(braket", "Cekic somun M4")))),
    ("B2b", None, _ve(_T, _g("Tahrik"), _ad("Motor JGB", "(motor"))),
    ("B2", None, _ve(_T, _g("Tahrik"))),                                       # kaplin, teker, eksenel M4 + pul
    ("B3", None, _ve(_T, _g("Guc_aku"), _veya(_ad("BTS7960", "XL4016", "Aku"), _ad(" ust)")))),
    ("B4", None, _ve(_T, _ad("Burc M5x40", "Saplama", "Cekic somun M5"))),
    ("C0", None, _ve(_K, _g("Etek_braket"))),                                  # L braket + M6 + M3 perçin somun (brakette)
    ("B5a", "guc", _ve(_T, _veya(_ad("Guc paneli", "Sigorta", "sigorta", "Role", "role", "Somun M4"),
                                 lambda p: p["ad"].startswith("Pul M4") and p["grup"].startswith("Guc")))),
    ("B5", None, _ve(_T, _ad("(kat "), lambda p: _z(p) < 0)),
    ("B6a", "kat", _ve(_T, _veya(_g("Elektronik"), _ad("Elektronik kati")))),
    ("B6", None, _ve(_T, _ad("(kat "), lambda p: _z(p) >= 0)),
    ("B7", None, _ve(_T, _g("Sonar"), _degil(_ad("Acil")))),
    # ------------------------------------------------ kabuk braketleri (8 gövde braketi: y 400 / 530,25 / 687,75 / 1095; M5 perçin somun brakette)
    ("C1", None, _ve(_K, _g("Govde_braket"))),
    # ------------------------------------------------ omuz (tezgâh D1a-D1c, robota D1)
    ("D1a", "omuz", _ve(_O, _ad("Omuz yuvasi", "S1 servo", "S1 kulak", "S1 kontra"))),
    ("D1b", "omuz", _ve(_O, _g("Govde_sabit"), _ad("6808", "Rulman kapagi", "Kapak civatasi", "Isil gomme somun M3 (yuvada)"))),
    ("D1c", "omuz", _ve(_O, _ad("S1 horn"))),
    ("D1", None, _ve(_O, _g("Govde_sabit"))),
    # ------------------------------------------------ kafa
    ("E1a", "boyun", _ve(_KF, _g("Boyun"), _degil(_ad("Boyun civata", "Cekic somun")))),
    ("E1", None, _ve(_KF, _g("Boyun"))),
    ("E2a", None, _ve(_KF, _ad("Pan horn"))),
    # İç bilezik eşleşmesi yalnız 6808'ler: Pan grubundaki 625ZZ (tilt pimi, çatal yanağı) E2'de takılır (F7a-kontrol O-1).
    ("E2b", None, _ve(_KF, _g("Pan"), _veya(_ad("Boyun mili", "Mil-horn"), _ve(_ad("6808"), _ad("ic bilezik"))))),
    # 1,58 m: boyun yükseltme adaptörü + 4 M3 saplama (DIN 976) + pul + DIN 985 çatalla birlikte (kafa10_lib.py başlık notu)
    ("E2c", None, _ve(_KF, _g("Pan"), _ad("Egme catali", "Catal-mil", "Isil gomme somun M3", "Boyun yukseltme", "Saplama M3",
                                          "(saplama"))),
    ("E2", None, _ve(_KF, _g("Pan"))),
    ("E3", None, _ve(_KF, _ad("Yanak-horn"))),
    ("E4", None, _ve(_KF, _g("Kafa_tilt"), _ad(*_KAFA_KABUK))),
    ("E3a", "kafa", _ve(_KF, _g("Kafa_tilt"))),
    # ------------------------------------------------ kabuk ve etek
    # Etek servis kapakları H1 / H2 (cıvata + ısıl gömme dahil) devreye alma testinden sonra, F5'te.
    ("F5", None, _ve(_K, _ad("Etek servis kapagi"))),
    # Ana anahtar ASW-A01 gövdesi etek üst plakasının altında, acil stobun aynası (taban_parcalar.py:10, :392, :444): F1 (F7a-kontrol O-2).
    ("F1", None, _veya(_ve(_K, _g("Taban_etegi")), _ve(_T, _ad("Acil stop", "Ana anahtar ASW")))),
    ("F2", None, _ve(_K, _veya(_ad("Govde alt bandi", "Govde uzatma bandi", "Govde orta bandi"), _kabuk_bag("F2"),
                               _ve(_g("Ses_ve_USB"), _ad("Hoparlor", "hoparlor"))))),      # hoparlör orta bant sağ ön duvarında
    ("F3", None, _ve(_K, _veya(_ad("Gogus bandi"), _g("Gogus_ekrani"), _kabuk_bag("F3")))),
    ("F4", None, _ve(_K, _veya(_ad("Omuz bandi"), _kabuk_bag("F4")))),
    # ------------------------------------------------ kollar
    ("G0", "gobek", _ve(_O, _ad("Omuz gobegi", "S1 kablo tamburu", "Tambur civatasi", "Isil gomme somun M3 (gobekte)"))),
    ("G1", None, _ve(_O, _g("Omuz_gobegi"), _degil(_ad("S2", "625ZZ", "Mafsal", "M5 (gobekte)")))),
    ("G2", None, _ve(_O, _g("Omuz_gobegi"))),
    ("G3", None, _ve(_O, _g("Ust_kol"))),
    ("G4", None, _ve(_K, _ad("aset", "Kaset"))),
    ("H0a", "dirsek", _ve(_D, _ad("On kol govdesi", "Dirsek servosu", "Bilek servosu"), _degil(_ad("horn")))),
    ("H0b", "dirsek", _ve(_D, _ad("Dirsek horn"))),
    ("H0c", "dirsek", _ve(_D, _veya(_g("Dirsek_ust"), _g("On_kol")), _degil(_ad("Bilezik")))),
    ("H0d", "dirsek", _ve(_D, _ad("Bilek horn"))),
    ("H0e", "dirsek", _ve(_D, _ad("Bilek flansi", "Flans-horn"))),
    ("H0f", "dirsek", _ve(_D, _g("El"))),
    ("H1", None, _D),
    # ------------------------------------------------ son: arka servis kapağı, üst arka servis kapağı (hub takozlu) + içindeki 4'lü hub
    ("F5", None, _ve(_K, _veya(_ad("Arka servis kapagi", "Ust arka servis kapagi", "(arka kapak)", "(ust arka kapak)"),
                               _ve(_g("Ses_ve_USB"), _ad("USB Hub"))))),
]

TEZGAH = {k: t for k, t, _f in ADIMLAR if t}                 # adım kodu -> tezgâh anahtarı
# Tezgâh alt montajının robota bağlandığı adım
BAGLANIR = {"plaka": "B1", "guc": "B5", "kat": "B6", "omuz": "D1", "boyun": "E1", "kafa": "E3", "gobek": "G1", "dirsek": "H1"}


def adim_bul(p):
    """Parçanın rehber adım kodu; hiçbir seçici tutmazsa None (atanmamış)."""
    for kod, _t, f in ADIMLAR:
        if f(p):
            return kod
    return None
