# -*- coding: utf-8 -*-
"""
Lale tasarim demosunu uretir (1,58 m ana tasarim; F9b / P9.2, 09.11.2026).

  viewer-template.html + kaynak JSON'lar + planlama/maliyet.json  ->  ../Robot-Tasarim-Demosu.html
  3B model: sayfa rehber/veri/robot-glb.js (GLB) ve rehber/veri/rehber-veri.js (parcalar) dosyalarini goreli <script> ile
  yukler (F7b ciktisi; bu betik onlari yazmaz, yalniz okur).

Sayfadaki her sayi asagidaki SAYILAR tablosundan gelir: (anahtar, kaynak, JSON yolu, bicim). Sayi elle yazilmaz.
Sablonda {{anahtar}} yer tutucusu <span data-k="anahtar"> olur; {{K:K44}} karar kuyrugundaki durumu yazar
("karar bekliyor"). Uretilen sayfaya <script id="kaynak"> icinde her anahtarin dosyasi, yolu, degeri ve metni gomulur;
planlama/d158/F9b-dogrula.py bunlari kaynak dosyalardan bagimsiz olarak yeniden okur.

Calistirma (depo kokunden ya da buradan; yalniz standart kutuphane, FreeCAD / CadQuery gerekmez):
  py -3 tasarim/cad/demo_uret.py
Fiyat degisince planlama/maliyet.json duzenlenir ve bu betik kosulur. robot_cad.py sonunda build(model_json) cagirir;
eski CadQuery modeli (V1-V3) artik demoda kullanilmaz, arguman yok sayilir.

Model neden goreli baglanti (kopya degil): KT-F9b-2, orkestrator karari b (duzeltme turu 1). .js sarmalayicilari
file:// altinda <script> ile okunur (fetch gerekmez). Eski kopya tasarim/cad/lale158-model.js artik uretilmez.
F9b-dogrula.py tutarliligi o anki rehber dosyalarindan denetler (sabit sha yok): robot-glb.js = robot.glb,
rehber-veri.js = rehber-veri.json, her GLB dugumu parcalar'da.
"""
from decimal import Decimal, ROUND_HALF_EVEN
import hashlib
import html
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.normpath(os.path.join(HERE, "..", ".."))
TPL = os.path.join(HERE, "viewer-template.html")
DEMO = os.path.join(KOK, "tasarim", "Robot-Tasarim-Demosu.html")
# sayfanin (tasarim/) yukledigi goreli model dosyalari
MODEL_SCRIPT = ["../rehber/veri/rehber-veri.js", "../rehber/veri/robot-glb.js"]

# kisa ad -> depo kokune gore yol
KAYNAK = {
    "kontrol": "tasarim/freecad/lale158/lale158-kontrol.json",
    "montaj": "tasarim/freecad/montaj/montaj-analiz.json",
    "carpisma": "tasarim/freecad/carpisma-sonuc.json",
    "reg": "planlama/d158/regresyon-son-kosu.json",
    "baski": "tasarim/freecad/lale158/baski-analiz.json",
    "y2b": "planlama/y2/Y2b-baski.json",
    "eklem": "planlama/d158/F6a-eklem_sinirlari-oneri.json",
    "maliyet": "planlama/maliyet.json",
    "glb": "rehber/veri/robot.glb",
    "rehber": "rehber/veri/rehber-veri.json",
}
KUYRUK = "planlama/d158/karar-kuyrugu.md"

# Bicim: ("s") metin aynen; (d) d ondalik; (d, olcek) deger*olcek, d ondalik. Turkce: binlik ".", ondalik ",", eksi "−".
REG = [  # regresyon-son-kosu.json degerleri: (anahtar, deger ondaligi, esik ondaligi)
    ("boy_mm", 1, 1), ("cakisma_kafa_ici", 0, 0), ("cakisma_kabuk_ici", 0, 0), ("cakisma_kabuk_x_iskelet", 0, 0),
    ("cakisma_ev_pozu", 0, 0), ("rampa_yuksuz", 3, 1), ("tilt_payi", 2, 1), ("pan_payi", 2, 1),
    ("mik_hoparlor_mm", 1, 0), ("sy8205_x_usb_mm3", 0, 0),
]
MODULLER = ["iskelet", "taban", "kabuk", "kafa", "omuz_sag", "omuz_sol", "dirsek_sag", "dirsek_sol"]
EKLEMLER = ["r_s1", "r_s2", "r_dirsek", "r_bilek", "pan", "tilt"]
KAFA_EKRAN = "parcalar[ad=Yuz ekrani WaveShare 10,1in QLED HDMI]"
GOGUS_EKRAN = "parcalar[ad=Gogus ekrani 11,6 in HDMI 1920x1080 kasali]"

SAYILAR = [
    # boy, kutle, parca
    ("boy", "kontrol", "toplam_boy_mm", 0),
    ("boy_m", "kontrol", "toplam_boy_mm", (2, 0.001)),
    ("kutle_kg", "montaj", "kutle_g", (2, 0.001)),
    ("kutle_g", "montaj", "kutle_g", 2),
    ("am_y", "montaj", "agirlik_merkezi.1", 1),
    ("parca", "montaj", "parca_sayisi", 0),
    ("p_baski", "montaj", "parcalar[tur=Baski]#say", 0),
    ("p_satin", "montaj", "parcalar[tur=Satin]#say", 0),
    ("p_satin_bom", "montaj", "bom_ozet.Satin.adet", 0),
    ("p_bag", "montaj", "parcalar[tur=Baglanti]#say", 0),
    ("p_lazer", "montaj", "parcalar[tur=Lazer]#say", 0),
    ("p_imalat", "montaj", "parcalar[tur=Imalat]#say", 0),
    # servo
    ("servo", "eklem", "eklemler#say", 0),
    ("s_ds", "montaj", "parcalar[kod=DS3235 servo]#say", 0),
    ("s_mg", "montaj", "parcalar[kod=MG996R servo]#say", 0),
    # ekranlar
    ("kafa_in", "montaj", KAFA_EKRAN + ".kod#re:(\\d+,\\d+) in", "s"),
    ("kafa_w", "montaj", KAFA_EKRAN + ".kod#re:(\\d+)x\\d+", "s"),
    ("kafa_h", "montaj", KAFA_EKRAN + ".kod#re:\\d+x(\\d+)", "s"),
    ("kafa_kod", "montaj", KAFA_EKRAN + ".kod", "s"),
    ("gogus_in", "montaj", GOGUS_EKRAN + ".ad#re:(\\d+,\\d+) in", "s"),
    ("gogus_w", "montaj", GOGUS_EKRAN + ".kod#re:(\\d+)x\\d+", "s"),
    ("gogus_h", "montaj", GOGUS_EKRAN + ".kod#re:\\d+x(\\d+)", "s"),
    ("gogus_kod", "montaj", GOGUS_EKRAN + ".kod", "s"),
    # 3B model (rehber GLB)
    ("glb_dugum", "glb", "nodes#say", 0),
    ("glb_ref", "rehber", "parcalar[tur=Referans]#say", 0),
    ("glb_kablo", "rehber", "parcalar[tur=Referans][r=kablo]#say", 0),
    ("rehber_adim", "rehber", "adimlar#say", 0),
    # regresyon kosusu
    ("reg_tarih", "reg", "tarih#re:^(\\d{4}-\\d\\d-\\d\\d)", "s"),
    ("reg_saat", "reg", "tarih#re:T(\\d\\d:\\d\\d)", "s"),
    ("reg_cikis", "reg", "cikis_kodu", 0),
    # tam carpisma taramasi
    ("tarama_eklem", "carpisma", "toplam.eklem_araliginda", 0),
    ("tarama_kutle", "carpisma", "kutle_toplam_g", (2, 0.001)),
    # eklem
    ("bag_s1", "eklem", "bagimli.0.kosul.r_s1.0", 0),
    ("bag_s2", "eklem", "bagimli.0.sinir.r_s2.1", 0),
    ("iv_duz", "eklem", "teker.ivme_sinir_m_s2.duz_surus", 1),
    ("iv_fren", "eklem", "teker.ivme_sinir_m_s2.duz_fren", 1),
    ("iv_rampa", "eklem", "teker.ivme_sinir_m_s2.rampa_surus", 1),
    ("iv_rampa_fren", "eklem", "teker.ivme_sinir_m_s2.rampa_fren", 1),
    # baski
    ("b_adet", "baski", "toplam.adet", 0),
    ("b_g0", "baski", "toplam.toplam_g.0", 1),
    ("b_g1", "baski", "toplam.toplam_g.1", 1),
    ("b_destek", "baski", "toplam.destek_g.0", 1),
    ("b_sa0", "baski", "toplam.sure_sa.0", 2),
    ("b_sa1", "baski", "toplam.sure_sa.1", 2),
    ("b_destekli", "baski", "toplam.destekli_adet", 0),
    ("b_destekli_tur", "baski", "toplam.destekli_tur", 0),
    ("b_sigmayan", "baski", "toplam.x2d_sigmayan#say", 0),
    ("x2d_0", "baski", "yontem.x2d.0", 0),
    ("x2d_1", "baski", "yontem.x2d.1", 0),
    ("x2d_2", "baski", "yontem.x2d.2", 0),
    ("cf0", "y2b", "toplam.cf_g.0", 1),
    ("cf1", "y2b", "toplam.cf_g.1", 1),
    ("petg", "y2b", "toplam.petg_g.0", 1),
]
for _k, _d, _e in REG:
    SAYILAR += [("reg_%s_etiket" % _k, "reg", "degerler.%s.etiket" % _k, "s"),
                ("reg_%s" % _k, "reg", "degerler.%s.deger" % _k, _d),
                ("reg_%s_esik" % _k, "reg", "degerler.%s.esik" % _k, _e),
                ("reg_%s_durum" % _k, "reg", "degerler.%s.esik_durumu" % _k, "s")]
for _m in MODULLER:
    SAYILAR += [("mod_%s_parca" % _m, "montaj", "moduller[ad=%s].parca" % _m, 0),
                ("mod_%s_kg" % _m, "montaj", "moduller[ad=%s].kutle_g" % _m, (2, 0.001))]
for _e in EKLEMLER:
    SAYILAR += [("ek_%s_min" % _e, "eklem", "eklemler.%s.min" % _e, 0),
                ("ek_%s_max" % _e, "eklem", "eklemler.%s.max" % _e, 0),
                ("ek_%s_servo" % _e, "eklem", "eklemler.%s.servo" % _e, "s")]

# Sayfada "karar bekliyor" diye gorunen kararlar: kendi kisa etiketimiz (sayisiz); durum karar-kuyrugu.md ozet tablosundan.
KARARLAR = [
    ("K2", "AI HAT+ ile kafa arka üst bağlantı yuvası (boss)", "tilt payı bu kararla yeniden ölçülür"),
    ("K3", "Düz zeminde elde yük sınırı", "rampa payı yüksüz değerdir"),
    ("K9", "El yükü: servo değişimi mi, yük sınırı mı", "kol servo modelleri"),
    ("K28", "Bütçe farkının hocaya bildirilmesi (sipariş onayı)", "maliyet ve takvim"),
    ("K29", "Erken alım (kupon parçaları)", "takvim"),
    ("K32", "Kafa ekranı: hocadan mı, satın alma mı", "kafa ekranı ve maliyet"),
    ("K34", "Baskı hizmeti ücreti", "maliyet ve baskı"),
    ("K38", "S2 alt bölge hız sınırı ve kapanma sırası", "eklem aralıkları"),
    ("K41", "S1 yazılım aralığı (kod ile CAD)", "eklem aralıkları"),
    ("K42", "PETG-CF makara sayısı", "baskı ve maliyet"),
    ("K44", "Eklem sınırları dosyasının kod/ klasörüne yazılması", "eklem aralıkları"),
    ("K45", "S2 darbe hız sınırı", "eklem aralıkları"),
    ("K46", "Destek azaltma geometri önerileri", "baskı"),
]

# maliyet.json notlarinda F9b'den sonra yanlis kalan cumle: maliyet.json dokunulmaz (F9b brief), sayfada isaretlenir.
NOT_DUZELTME = [{"bul": "Demodaki 3B model",
                 "ek": "F9b notu: bu cümle önceki demoya ait. Demodaki 3B model artık ana tasarımın FreeCAD modeli "
                       "(rehber GLB); notun düzeltilmesi maliyet.json sahibinde."}]


# maliyet.json kalemlerine sayfada eklenen isaret (F9b duzeltme turu 1, O-1): maliyet.json dokunulmaz.
#   kalem: indeks; ad / bul: koruma (kalemin adi ve not ya da modelinde gecen metin; tutmazsa uretim durur);
#   tur "eski": notun yanina "eski tasarim notu"; tur "duzeltme": satira F9b notu. ek metninde rakam yok; sayi {{anahtar}} ile.
KALEM_ISARET = [
    {"kalem": 33, "ad": "Yüz ekranı", "bul": "LCD (B)", "tur": "duzeltme",
     "ek": "F9b notu: K32'ye bağlı; CAD'deki kafa ekranı QLED {{kafa_in}}\""},
    {"kalem": 36, "ad": "Ekran kablosu", "bul": "Nextion", "tur": "eski"},
    {"kalem": 78, "ad": "Direnç seti", "bul": "Nextion", "tur": "eski"},
]


# maliyet.json kalem notlarinda onceki tasarima (eski govde, 125 cm V3) ait metin: sayfada "eski tasarim notu" diye isaretlenir.
ESKI_DESEN = "1[,.]65 ?m(?![0-9])|125 ?cm"


# ---------------------------------------------------------------- okuma
def yol(ad):
    return os.path.join(KOK, *KAYNAK[ad].split("/"))


def sha12(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]


def glb_oku(p):
    with open(p, "rb") as f:
        b = f.read()
    magic, _ver, _uz = struct.unpack("<III", b[:12])
    assert magic == 0x46546C67, "GLB degil: " + p
    cl, ct = struct.unpack("<II", b[12:20])
    assert ct == 0x4E4F534A
    return b, json.loads(b[20:20 + cl].decode("utf-8"))


_ONB = {}


def veri(ad):
    if ad not in _ONB:
        if ad == "glb":
            _ONB[ad] = glb_oku(yol(ad))[1]
        else:
            with open(yol(ad), encoding="utf-8") as f:
                _ONB[ad] = json.load(f)
    return _ONB[ad]


def coz(obj, ifade):
    """a.b.0  |  liste[alan=deger] (tek eleman ya da #say)  |  #say  |  #re:DESEN (1. grup)."""
    op = None
    if "#" in ifade:
        ifade, op = ifade.split("#", 1)
    suzgec = False
    for t in re.findall(r"\[[^\]]*\]|[^.\[\]]+", ifade):
        if t.startswith("["):
            k, v = t[1:-1].split("=", 1)
            obj = [x for x in obj if str(x.get(k)) == v]
            suzgec = True
            continue
        if suzgec:
            if len(obj) != 1:
                raise KeyError("%s: %d eleman (1 bekleniyor)" % (ifade, len(obj)))
            obj = obj[0]
            suzgec = False
        obj = obj[int(t)] if isinstance(obj, list) else obj[t]
    if op == "say":
        return len(obj)
    if suzgec:
        if len(obj) != 1:
            raise KeyError("%s: %d eleman (1 bekleniyor)" % (ifade, len(obj)))
        obj = obj[0]
    if op and op.startswith("re:"):
        m = re.search(op[3:], obj)
        if not m:
            raise KeyError("%s: desen bulunamadi" % op)
        return m.group(1)
    if op:
        raise ValueError("bilinmeyen islem: " + op)
    return obj


def sayi(v, d):
    q = Decimal(repr(abs(float(v)))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_EVEN)
    s = "{:,.{}f}".format(q, d).replace(",", " ").replace(".", ",").replace(" ", ".")
    return ("−" if v < 0 and s.strip("0,.") else "") + s


def bicimle(v, b):
    if b == "s":
        if not isinstance(v, str):
            raise TypeError("metin bekleniyor: %r" % (v,))
        return v
    d, k = (b if isinstance(b, tuple) else (b, 1))
    return sayi(float(v) * k, d)


# ---------------------------------------------------------------- karar kuyrugu
def kuyruk_durum():
    """Ozet tablosu: | K44 | baslik | **acik** (...) | ... -> {K44: 'açık'|'kapandı'|...}"""
    out = {}
    with open(os.path.join(KOK, *KUYRUK.split("/")), encoding="utf-8") as f:
        for satir in f:
            m = re.match(r"\|\s*(K\d+)\s*\|[^|]*\|\s*([^|]*)\|", satir)
            if m and m.group(1) not in out:
                d = m.group(2).strip()
                out[m.group(1)] = "açık" if d.startswith("**açık**") else ("kapandı" if d.startswith("kapandı") else d)
    return out


# ---------------------------------------------------------------- model (goreli baglanti)
def model_bilgi():
    """Sayfanin yukledigi rehber dosyalari hakkinda bilgi (dosyalari yazmaz)."""
    _b, j = glb_oku(yol("glb"))
    par = {p["id"] for p in veri("rehber")["parcalar"]}
    eksik = [n["name"] for n in j["nodes"] if n["name"] not in par]
    if eksik:
        raise SystemExit("rehber-veri.json parcalar GLB dugumlerini kapsamiyor: %s" % eksik[:5])
    for s_ in MODEL_SCRIPT:
        if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(DEMO), *s_.split("/")))):
            raise SystemExit("model dosyasi yok: " + s_)
    print("model: goreli", ", ".join(MODEL_SCRIPT), "·", len(j["nodes"]), "dugum")
    return {"script": MODEL_SCRIPT, "glb": KAYNAK["glb"], "parcalar_kaynak": KAYNAK["rehber"] + " parcalar",
            "dugum": len(j["nodes"])}


def kalem_isaret(md):
    """KALEM_ISARET korumalarini maliyet.json ile denetler; sayfaya gomulecek listeyi dondurur."""
    out = []
    for z in KALEM_ISARET:
        it = md["kalemler"][z["kalem"]]
        if it.get("ad") != z["ad"] or z["bul"] not in (it.get("not", "") + " " + it.get("model", "")):
            raise SystemExit("KALEM_ISARET korumasi tutmuyor (maliyet.json degismis): %s" % z)
        y = {k: v for k, v in z.items() if k != "ek"}
        if "ek" in z:  # metin parcalari: ["t", metin] ya da ["k", anahtar] (sayfa JS'i data-k span'i yazar)
            y["ek"] = [["k", x] if i % 2 else ["t", x] for i, x in enumerate(re.split(r"\{\{([a-z0-9_]+)\}\}", z["ek"])) if x]
            if re.search(r"(?<![\w])\d+(?:[.,]\d+)*(?![\w])", re.sub(r"\{\{[a-z0-9_]+\}\}", "", z["ek"])):
                raise SystemExit("KALEM_ISARET ek metninde bagsiz rakam: " + z["ek"])
        out.append(y)
    return out


# ---------------------------------------------------------------- uretim
def build(model_json=None):
    if model_json:
        print("not: eski CadQuery model.json artik demoda kullanilmiyor; yok sayildi:", model_json)
    anahtar = {}
    for k, src, ifade, b in SAYILAR:
        v = coz(veri(src), ifade)
        anahtar[k] = {"dosya": KAYNAK[src], "yol": ifade, "bicim": list(b) if isinstance(b, tuple) else b,
                      "deger": v, "metin": bicimle(v, b)}
    durum = kuyruk_durum()
    kararlar = {}
    for kno, etiket, etki in KARARLAR:
        if kno not in durum:
            raise SystemExit("karar kuyrugunda yok: " + kno)
        kararlar[kno] = {"etiket": etiket, "etki": etki, "durum": durum[kno]}
        if durum[kno] != "açık":
            print("UYARI: %s artik '%s' - sayfa metnini guncelle" % (kno, durum[kno]))
    model = model_bilgi()
    isaret = kalem_isaret(veri("maliyet"))

    with open(TPL, encoding="utf-8") as f:
        h = f.read()

    def deg(m):
        k = m.group(1)
        if k.startswith("K:"):
            kno = k[2:]
            kd = kararlar[kno]
            yazi = "karar bekliyor" if kd["durum"] == "açık" else "kuyrukta: " + kd["durum"]
            return '<span class="kb" data-karar="%s" title="%s">%s · %s</span>' % (
                kno, html.escape(kd["etiket"] + " (" + KUYRUK + ")"), yazi, kno)
        a = anahtar[k]
        return '<span class="v" data-k="%s" title="%s">%s</span>' % (
            k, html.escape(a["dosya"] + " · " + a["yol"]), html.escape(a["metin"]))

    h = re.sub(r"\{\{([A-Za-z0-9_:]+)\}\}", deg, h)
    # karar listesi
    satir = []
    for kno, etiket, etki in KARARLAR:
        kd = kararlar[kno]
        satir.append('<tr><td><span class="kb" data-karar="%s">%s · %s</span></td><td>%s</td><td>%s</td></tr>' % (
            kno, "karar bekliyor" if kd["durum"] == "açık" else "kuyrukta: " + kd["durum"], kno,
            html.escape(etiket), html.escape(etki)))
    h = h.replace("<!--KARAR_SATIRLARI-->", "\n".join(satir))
    dosyalar = {v: sha12(os.path.join(KOK, *v.split("/"))) for v in sorted(set(KAYNAK.values()) | {KUYRUK})}
    kaynak = {"uretici": "tasarim/cad/demo_uret.py", "dosyalar": dosyalar, "anahtarlar": anahtar,
              "kararlar": kararlar, "model": model, "not_duzeltme": NOT_DUZELTME,
              "kalem_isaret": isaret, "eski_desen": ESKI_DESEN}
    js = json.dumps(kaynak, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    with open(yol("maliyet"), encoding="utf-8") as f:
        cost = json.dumps(json.load(f), ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    h = h.replace("/*KAYNAK_JSON*/", js).replace("/*COST_JSON*/", cost)
    kalan = re.findall(r"\{\{[^}]*\}\}|/\*[A-Z_]+_JSON\*/", h)
    if kalan:
        raise SystemExit("doldurulmamis yer tutucu: %s" % kalan[:5])
    with open(DEMO, "w", encoding="utf-8", newline="\n") as f:
        f.write(h)
    print("sayi anahtari:", len(anahtar), "· karar:", len(kararlar), "· maliyet:", len(veri("maliyet")["kalemler"]), "kalem")
    print("demo:", os.path.relpath(DEMO, KOK), os.path.getsize(DEMO) // 1024, "KB")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else None)
