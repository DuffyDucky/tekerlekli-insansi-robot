# -*- coding: utf-8 -*-
# Lale 1,58 m - secim B + R1: uygulama-notu.md ve rapor.html uretir (sistem Python'u, FreeCAD gerekmez). Sayilar yalniz JSON dosyalarindan okunur; iki cikti ayni degerleri kullanir.
# py -3 uygulama_rapor.py   (zincirin son adimi)
import os, sys, json, html, datetime, csv
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
LALE = os.path.dirname(HERE)
UST = os.path.dirname(LALE)
sys.path[:0] = [LALE, UST]
import arayuz as A
import kablo_yolu_ekran as KY


def oku(*p):
    return json.load(open(os.path.join(*p), encoding="utf-8"))


def tr(x, n=1):
    if x is None:
        return "-"
    s = "%.*f" % (n, x)
    bas, _, kes = s.partition(".")
    neg = bas.startswith("-")
    bas = bas.lstrip("-")
    gr = ""
    while len(bas) > 3:
        gr = "." + bas[-3:] + gr
        bas = bas[:-3]
    return ("-" if neg else "") + bas + gr + ("," + kes if kes else "")


KAFA = oku(UST, "kafa", "kafa-analiz.json")
KABUK = oku(UST, "kabuk", "kabuk-analiz.json")
MON = oku(UST, "montaj", "montaj-analiz.json")
KON = oku(LALE, "lale158-kontrol.json")
OLC = oku(HERE, "uygulama-olcum.json")
BSK = oku(HERE, "uygulama-baski.json")
IK = oku(HERE, "uygulama-ikinci.json")
IV = oku(HERE, "uygulama-ivme.json")
CRP = oku(UST, "carpisma-sonuc.json")
TAB = oku(UST, "taban", "taban-analiz.json")

TT, TP = KAFA["tork"]["tilt"], KAFA["tork"]["pan"]
GEC = {g["ad"]: g for g in OLC["boyun"]["gecis"]}
GEC_K = [g for g in OLC["boyun"]["gecis"] if g["ad"].startswith("Servo yuvasi arka kanali")][0]
KABLO = OLC["kablo_listesi"]
SY = OLC["kablo_sy8205"]
SY_V = sum(v["sy8205_kesisim_mm3"] for v in SY.values()) + sum(v["sy8205_kesisim_mm3"] for v in OLC["kafa_ici_qled_kablo"].values())
SY_M = min(v["sy8205_mm"] for k, v in SY.items())            # boyun yollari; kafa ici QLED Power kablosu SY8205'e bilerek gider
HUB_SY = SY["Hub uzatmasi"]["sy8205_mm"]
MH = OLC["mic_hoparlor"]


def tilt_ilk(isaret):
    ad = [int(k) for k in IK["tilt"] if k != "moment" and (int(k) < 0) == (isaret < 0)]
    for th in sorted(ad, key=abs):
        if IK["tilt"][str(th)]["cakisma_sayisi"] > 0:
            return th
    return None


def kol_sayi(t):
    return IK["kol"]["sonuc"][t]["cakisma_sayisi"]


def kol_s2(t, s2):
    return IK["kol"]["sonuc"][t]["s2_en_kucuk"][s2]["min_mm"]


def s2_hepsi_alt(t):
    """Kol cakismalarinin S2 degerleri."""
    return sorted(set(c[3] for c in IK["kol"]["sonuc"][t]["cakisma"]))


def catal_s2(t, s2):
    return IK["catal"]["sonuc"][t]["s2"][s2][0][0]


def kafa_kol():
    m = [IK["kafa"]["sonuc"][t]["en_kucuk_20"][0] for t in ("sag", "sol")]
    return sum(IK["kafa"]["sonuc"][t]["cakisma_sayisi"] for t in ("sag", "sol")), min(q[0] for q in m), min(m, key=lambda q: q[0])


POZ = {p["kod"]: p for p in TAB["robot"]["pozlar"]}
Y0, Y100, Y500 = IV["izgara_yuk_0g"], IV["izgara_yuk_100g"], IV["izgara_yuk_500g"]


def rampa_en(y):
    return min(v for k, v in y["a_sinir_pay15"].items() if k.startswith("rampa5"))


KK = kafa_kol()
BOY = KON["toplam_boy_mm"]
IZG = rampa_en(Y0)
EV_R = POZ["ev"]["rampa5"]["pay_geri"]
EV_IV = IV["ev"]["rampa5"]["geri"] / 1.5
ESIK_ALTI = IZG < 1.5

K_YENI = KON["kablo_tup_cakisma"]

# ---------------------------------------------------------------------------------- satirlar: (olcut, onceki, beklenen, olculen, kaynak)
J_K, J_B, J_M, J_C, J_O, J_I, J_V, J_T = "kafa/kafa-analiz.json", "kabuk/kabuk-analiz.json", "montaj/montaj-analiz.json", "lale158/lale158-kontrol.json", "kafa-yerlesim/uygulama-olcum.json", "kafa-yerlesim/uygulama-ikinci.json", "kafa-yerlesim/uygulama-ivme.json", "taban/taban-analiz.json"
ROW = [
    ("Toplam boy, mm", "1.580,0", "en çok 1.580,0", tr(BOY, 1), J_C + " toplam_boy_mm"),
    ("Parça sayısı (kablo gösterimi hariç)", "1.168", "-", tr(KON["parca"], 0), J_C + " parca"),
    ("Toplam kütle, g (400 g kablo payı dahil)", "25.836,9", "-", tr(IV["ev"]["kutle_g"], 1), J_V + " ev.kutle_g"),
    ("Kafa grubu kütlesi, g", "1.531,3", "1.570,8", tr(TT["kutle_g"], 1), J_K + " tork.tilt.kutle_g"),
    ("Tilt payı, ±15", "3,89", "3,64", tr(TT["pay_tilt15"], 2), J_K + " tork.tilt.pay_tilt15"),
    ("Tilt statik, ±15, kg·cm", "0,083", "0,152", tr(TT["statik_tilt15_kgcm"], 3), J_K + " tork.tilt.statik_tilt15_kgcm"),
    ("Pan payı", "2,20", "2,21", tr(TP["pay_iki_hane"], 2), J_K + " tork.pan.pay_iki_hane"),
    ("Mikrofon-hoparlör, tüm pozlarda en az, mm", "yok (dizi modelde değildi)", "574,3", tr(MH["poz_min_mm"], 1), J_O + " mic_hoparlor.poz_min_mm"),
    ("Dizi-hoparlör, ev pozu, mm", "yok", "595,7", tr(MH["ev_min_mm"], 1), J_O + " mic_hoparlor.ev_min_mm"),
    ("Boyun yuva kanalı doluluğu", "%44,8", "%44,8", "%" + tr(GEC_K["doluluk"] * 100, 1), J_O + " boyun.gecis"),
    ("SY8205 × USB çakışması, mm³", "249,7", "0", tr(SY_V, 2), J_O + " kablo_sy8205 + kafa_ici_qled_kablo"),
    ("SY8205 × boyuna inen USB açıklığı, mm", "-", "15,45", tr(HUB_SY, 2), J_O + " kablo_sy8205[Hub uzatmasi]"),
    ("Kafa × kol, çakışma (tilt ±13, ±15)", "0", "-", tr(KK[0], 0), J_I + " kafa"),
    ("Kafa × kol, en yakın, mm", "11,046", "-", tr(KK[1], 3), J_I + " kafa"),
    ("Tilt ilk çakışma, derece", "-17 / +18", "-", "%s / +%s" % (tilt_ilk(-1), tilt_ilk(1)), J_I + " tilt"),
    ("Kol, S2 0-3 çakışma, sağ + sol", "684 + 684", "-", "%d + %d" % (kol_sayi("sag"), kol_sayi("sol")), J_I + " kol"),
    ("Kol, S2 5 en yakın, mm", "1,358", "-", tr(min(kol_s2("sag", "5.0"), kol_s2("sol", "5.0")), 3), J_I + " kol"),
    ("Çatal, S2 5 en yakın, mm", "12,306", "-", tr(min(catal_s2("sag", "5.0"), catal_s2("sol", "5.0")), 3), J_I + " catal"),
    ("Devrilme payı, ev pozu, rampa 5°", "1,62", "en az 1,5", tr(EV_R, 2), J_T + " robot.pozlar[ev].rampa5.pay_geri"),
    ("Devrilme payı, ızgara, yüksüz, rampa 5°", "1,523", "en az 1,5", tr(IZG, 3), J_V + " izgara_yuk_0g.a_sinir_pay15"),
    ("Tarama, eklem aralığında çakışma (omuz bölümü eski)", "0", "0", tr(CRP["toplam"]["eklem_araliginda"], 0), "carpisma-sonuc.json toplam.eklem_araliginda"),
    ("Kafa iç çakışma (0,799 mm³ dahil, eşik 0,5 mm³)", "1 (0,799 mm³, düzeltme öncesi)", "0", tr(len(KAFA["statik"]), 0), J_K + " statik"),
    ("Dizi × arka kabuk, eşiksiz kesişim, mm³", "0,799", "0", tr(OLC["dizi"]["kabuk_kesisim_mm3"], 4), J_O + " dizi.kabuk_kesisim_mm3"),
    ("Kabuk iç çakışma / kabuk × iskelet", "0 / 0", "0 / 0", "%d / %d" % (len(KABUK["cakisma"]), len(KABUK["iskelet_cakisma"])), J_B + " cakisma, iskelet_cakisma"),
]

# kablo satirlari: (ad, nereden -> nereye, yol, siparis, liste durumu)
K_BILGI = [
    ("Hub uzatmasi", "Pi 3 → hub (boyundan, koridor z ≈ -14)", "Hub 130 mm + ~1 m USB-A uzatma: listede yok"),
    ("Ses karti uzatmasi", "Pi 2 → L dirsek → ses kartı", "~30 cm USB-A uzatma + L dirsek: listede yok"),
    ("Dizi USB", "Pi 1 → ReSpeaker micro B", "Kısa micro USB: listede yok"),
    ("USB dokunmatik", "Hub → göğüs ekranı TOUCH", "v4 satır 58, 2 m: yeter"),
    ("ESP32 USB", "Hub → ESP32 (taban), VBUS'ta 1N5819", "v4, 2 m: yeter"),
    ("Hoparlor", "PAM8403 → hoparlör (boyundan)", "~1,1 m: robot için listede yok"),
    ("3,5 mm -> PAM", "Ses kartı L 3,5 mm → PAM girişi", "L 3,5 mm fişli kısa kablo: listede yok"),
    ("PAM 5 V", "D24V50F5 → PAM (VARSAYIM)", "Sarf; besleme noktası doğrulanmadı"),
    ("HDMI", "Pi HDMI 1 → göğüs ekranı (boyundan)", "v4, 1,5 m: yeter"),
    ("12 V", "Taban → göğüs ekranı (boyundan)", "Değişmedi"),
]
K_AD = {"Hub uzatmasi": "Hub uzatması", "Ses karti uzatmasi": "Ses kartı uzatması", "USB dokunmatik": "Göğüs dokunmatik USB", "Hoparlor": "Hoparlör", "3,5 mm -> PAM": "3,5 mm → PAM"}
KI_BILGI = {"Touch USB (kutu kablosu)": "Pi 4 → kafa ekranı TOUCH", "HDMI (serit, 2 lehimsiz fis)": "Pi HDMI 0 → kafa ekranı", "Power USB (30 cm, A ucu kesik)": "SY8205 → kafa ekranı Power"}
KI_AD = {"HDMI (serit, 2 lehimsiz fis)": "HDMI (şerit, 2 lehimsiz fiş)", "Touch USB (kutu kablosu)": "Touch USB (kutu kablosu)", "Power USB (30 cm, A ucu kesik)": "Power USB (30 cm, A ucu kesik)"}
PORT = [("Pi 1", "ReSpeaker Mic Array v2.0"), ("Pi 2", "USB ses kartı (uzatma + L dirsek)"), ("Pi 3", "Hub (hub 130 mm + uzatma)"), ("Pi 4", "Kafa ekranı dokunmatik"),
        ("Hub 1", "Göğüs ekranı dokunmatik"), ("Hub 2", "ESP32"), ("Hub 3", "Boş"), ("Hub 4", "Boş")]

# ---------------------------------------------------------------------------------- 5 V butcesi (elektrik.md satir 24, 245; hoparlor 3 W tepe, verim VARSAYIM)
VERIM = 0.85
PI_HAT = 2.67
PAM_TEPE = 3.0 / VERIM / 5.0
AMF_N = 0.5 / 5.0
B_DAHIL = PI_HAT - AMF_N + PAM_TEPE
B_HARIC = PI_HAT + PAM_TEPE

BK = BSK["parca"]
AH = OLC["ai_hat_zarfi"]
HU = OLC["hub"]
BOSS_FIX = OLC["dizi"]

# ---------------------------------------------------------------------------------- metin (el ile, bulgu sonrasi yazildi; sayilar yukaridan)
exec(compile(open(os.path.join(HERE, "uygulama_metin.py"), encoding="utf-8").read(), "uygulama_metin.py", "exec"))


# ---------------------------------------------------------------------------------- md
def md_tablo(bas, satir):
    o = ["| " + " | ".join(bas) + " |", "|" + "---|" * len(bas)]
    for s in satir:
        o.append("| " + " | ".join(str(c) for c in s) + " |")
    return "\n".join(o)


def kablo_sat():
    r = []
    for ad, yer, liste in K_BILGI:
        k = KABLO[ad]
        r.append((K_AD.get(ad, ad), yer, tr(k["yol_mm"], 0), tr(k["onerilen_mm"], 0), tr(k["kapak_sokme_pay_mm"], 0) if k["kapak_sokme_pay_mm"] else "-", liste))
    return r


def kablo_ic_sat():
    return [(KI_AD.get(ad, ad), KI_BILGI.get(ad, ""), tr(v["yol_mm"], 0), tr(v["liste_boyu_mm"], 0), tr(v["kalan_mm"], 0)) for ad, v in OLC["kafa_ici_kablo_listesi"].items()]


K_BAS = ("Kablo", "Nereden, nereye", "Yol mm", "Sipariş mm", "Kapak payı mm", "Listede")
KI_BAS = ("Kafa içi kablo", "Nereden, nereye", "Yol mm", "Boy mm", "Kalan mm")
SON_BAS = ("Ölçüt", "Önceki", "Beklenen", "Ölçülen", "Kaynak")

MD = [
    "# Kafa içi ses ve USB: B + R1 uygulaması", "", "Tarih: %s. Seçim: Ahmet Yorulmaz, 05.11.2026. Sayılar son koşuların JSON dosyalarından okundu (`uygulama_rapor.py`)." % datetime.date.today().strftime("%d.%m.%Y"), "",
    "## Özet", "", *[x for u in UYARI if u.startswith("**Yüksüz") for x in ("> " + u, "")], OZET_MD, "", "\n".join("- " + u for u in UYARI if not u.startswith("**Yüksüz")), "",
    "## Sonuç tablosu", "", KAYNAK_NOT, "", md_tablo(SON_BAS, [(a, b, c, d, "`%s`" % e) for a, b, c, d, e in ROW]), "",
    "## Ne değişti", "", "\n".join("- " + q for q in DEGISEN), "",
    "## Yeni parça ölçümleri", "", "\n".join("- " + q for q in OLCUM), "",
    "## Baskı", "", BASKI_MD, "",
    "## Hangi koşu hangi JSON", "", md_tablo(("Koşu", "Üretilen dosya"), KOSU), "",
    "## Atlananlar", "", "\n".join("- " + q for q in ATLANAN), "",
    "## 5 V ve `elektrik.md`", "", "\n".join("- " + q for q in ELEKTRIK), "",
    "## Güncel kablo listesi", "", md_tablo(K_BAS, kablo_sat()), "", md_tablo(KI_BAS, kablo_ic_sat()), "", md_tablo(("Port", "Bağlı"), PORT), "",
    "**Listede olmayan 6 kalem (BOM v4 değişmedi, karar Ahmet Yorulmaz'da):** " + LISTE_DISI, "",
    "## Kalan varsayımlar", "", "\n".join("- " + q for q in VARSAYIM), "",
    "## Karar gereken noktalar", "", "\n".join("- " + q for q in KARAR), "",
]
open(os.path.join(HERE, "uygulama-notu.md"), "w", encoding="utf-8", newline="\n").write("\n".join(MD))


# ---------------------------------------------------------------------------------- html
def esc(x):
    return html.escape(str(x))


def inl(s):
    """`kod` ve **kalin** isaretlerini HTML'e cevirir."""
    out, kod = [], False
    for i, p in enumerate(esc(s).split("`")):
        if i % 2:
            out.append("<code>%s</code>" % p)
        else:
            q = p.split("**")
            out.append("".join(("<b>%s</b>" % t) if j % 2 else t for j, t in enumerate(q)))
    return "".join(out)


def tablo(bas, sat):
    b = "".join("<th>%s</th>" % esc(h) for h in bas)
    r = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inl(str(c)) for c in s) for s in sat)
    return '<div class="ts"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (b, r)


def kart(b, d, n=""):
    return '<div class="kart"><div class="k-b">%s</div><div class="k-d">%s</div><div class="k-n">%s</div></div>' % (esc(b), esc(d), esc(n))


def gorsel(ad, alt):
    if not os.path.exists(os.path.join(HERE, "gorsel", ad)):
        return '<figure class="yok"><figcaption>%s: görsel üretilmedi (%s)</figcaption></figure>' % (esc(alt), esc(ad))
    return '<figure><a href="gorsel/%s"><img src="gorsel/%s" alt="%s" loading="lazy"></a><figcaption>%s</figcaption></figure>' % (ad, ad, esc(alt), esc(alt))


KART = [("Boy", tr(BOY, 1) + " mm", "sınır 1.580,0"), ("Kafa grubu", tr(TT["kutle_g"], 1) + " g", "beklenen 1.570,8"), ("Toplam kütle", tr(IV["ev"]["kutle_g"], 1) + " g", "önceki 25.836,9"),
        ("Tilt / pan payı", "%s / %s" % (tr(TT["pay_tilt15"], 2), tr(TP["pay_iki_hane"], 2)), "beklenen 3,64 / 2,21"), ("Mikrofon-hoparlör", tr(MH["poz_min_mm"], 1) + " mm", "tüm pozlarda en az; H1 ≥ 400"),
        ("Boyun kanalı", "%" + tr(GEC_K["doluluk"] * 100, 1), "önceki %44,8"), ("SY8205 × USB", tr(SY_V, 2) + " mm³", "önceki 249,7; açıklık %s mm" % tr(HUB_SY, 2)),
        ("Devrilme, ızgara yüksüz", tr(IZG, 3), "eşik 1,5; önceki 1,523"), ("Devrilme, ev", tr(EV_R, 2), "rampa 5°; önceki 1,62"), ("Parça", tr(KON["parca"], 0), "önceki 1.168")]
GOR = [("SON-kafa-arka-acik.png", "Kafa, arka kabuk sökülmüş: dizi, ses kartı, PAM, koridor"), ("SON-kafa-kesit.png", "Mikrofon deliğinden yan kesit"), ("SON-govde.png", "Üst gövde yandan: dizi, hoparlör, hub, mikrofon-hoparlör mesafesi"), ("SON-hub-kapak.png", "Hub, üst arka servis kapağının iç yüzünde")]
CSS = """:root{--z:#f7f8f9;--y:#1a1d21;--i:#5c6670;--c:#d8dde2;--k:#fff;--v:#0b6bcb;--u:#b45309}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--z:#14171a;--y:#e8eaed;--i:#9aa4ae;--c:#2c3238;--k:#1c2024;--v:#6db3f2;--u:#f0a94a}}
*{box-sizing:border-box}body{margin:0;padding:24px 16px;background:var(--z);color:var(--y);font:15px/1.55 system-ui,Segoe UI,Arial,sans-serif}
main{max-width:1120px;margin:auto}h1{font-size:26px;margin:0 0 4px}h2{font-size:19px;margin:32px 0 10px;border-bottom:1px solid var(--c);padding-bottom:6px}
.alt{color:var(--i);margin:0 0 20px}.kartlar{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:10px}
.kart{background:var(--k);border:1px solid var(--c);border-radius:8px;padding:12px}.k-b{font-size:12px;color:var(--i)}.k-d{font-size:20px;font-weight:600;margin:2px 0}.k-n{font-size:12px;color:var(--i)}
.ts{overflow-x:auto}table{border-collapse:collapse;width:100%;background:var(--k);font-size:13.5px}th,td{border:1px solid var(--c);padding:6px 8px;text-align:left;vertical-align:top}th{font-weight:600}
.gor{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:12px}figure{margin:0;background:#fff;border:1px solid var(--c);border-radius:8px;overflow:hidden}figure img{width:100%;display:block}
figcaption{padding:6px 8px;font-size:12.5px;color:#444;background:#fff}li{margin:4px 0}code{font-size:13px}.uyari{border-left:4px solid var(--u);padding:8px 12px;background:var(--k);margin:12px 0}
@media (max-width:520px){.gor{grid-template-columns:1fr}}"""


def ul(ls):
    return "<ul>%s</ul>" % "".join("<li>%s</li>" % inl(q) for q in ls)


H = ['<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Lale Kafa Yerleşimi</title><style>', CSS, "</style></head><body><main>",
     "<h1>Lale: kafa içi ses ve USB, B + R1</h1><p class=\"alt\">Sayılar <code>uygulama-notu.md</code> ile aynı JSON dosyalarından okunur. %s</p>" % esc(datetime.date.today().strftime("%d.%m.%Y")),
     "<p>%s</p>" % inl(OZET_MD), "".join('<div class="uyari">%s</div>' % inl(u) for u in UYARI),
     '<div class="kartlar">%s</div>' % "".join(kart(*k) for k in KART),
     "<h2>Son model</h2><div class=\"gor\">%s</div>" % "".join(gorsel(a, b) for a, b in GOR),
     "<h2>Bağlantılar</h2>" + tablo(("Port", "Bağlı"), PORT),
     "<h2>Kablolar</h2><p>Yollar şema, sipariş boyu yol × 1,25, kapağa bağlı kablolarda +150 mm (tahmin). Çaplar tahmini.</p>" + tablo(K_BAS, kablo_sat()) + '<div style="height:10px"></div>' + tablo(KI_BAS, kablo_ic_sat()),
     "<p><b>Listede olmayan 6 kalem:</b> %s</p>" % inl(LISTE_DISI),
     "<h2>Önceki, beklenen, ölçülen</h2><p>%s</p>" % inl(KAYNAK_NOT) + tablo(SON_BAS, [(a, b, c, d, "`%s`" % e) for a, b, c, d, e in ROW]),
     "<h2>Yeni parça ölçümleri</h2>" + ul(OLCUM), "<h2>Baskı</h2><p>%s</p>" % inl(BASKI_MD),
     "<h2>5 V ve elektrik planı</h2>" + ul(ELEKTRIK),
     "<h2>Atlananlar</h2>" + ul(ATLANAN), "<h2>Kalan varsayımlar</h2>" + ul(VARSAYIM), "<h2>Açık işler ve kararlar</h2>" + ul(KARAR),
     "<h2>Ne değişti</h2>" + ul(DEGISEN), "<h2>Koşular</h2>" + tablo(("Koşu", "Üretilen dosya"), KOSU), "</main></body></html>"]
open(os.path.join(HERE, "rapor.html"), "w", encoding="utf-8", newline="\n").write("".join(H))
print("yazildi", "boy", BOY, "kafa", TT["kutle_g"], "izgara", IZG, "esik alti", ESIK_ALTI)
