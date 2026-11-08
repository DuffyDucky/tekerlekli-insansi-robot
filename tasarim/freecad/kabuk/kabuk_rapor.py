# Kabuk modulu raporu (rapor.html, gorseller gomulu). Sistem Python'u ile calisir (FreeCAD gerekmez).
# Girdiler: kabuk-analiz.json (kabuk_montaj.py), ../carpisma-sonuc.json (carpisma_kos.py birlestir), ../montaj/montaj-analiz.json
# (ana_montaj.py), ../omuz/omuz-analiz.json, ../arayuz.py, gorsel/*.png (kabuk_gorsel.py).
# F1b P1.5 (08.11.2026): 1,58 m ve guncel duzene getirildi: Nextion (125 cm / V3) yerine 11,6" kasali gogus ekrani
# (kabuk-analiz.json 'gogus_ekrani'; eski 'ekran_kontrol' anahtari artik yok), ses ve USB grubu (hoparlor kabi + kelepce, hub);
# kabuk oncesi karsilastirmasi (onceki/*.json) ve omuz/iskelet regresyonu (Ekim 2026, V3 kabuk calismasi) rapordan cikti.
import os, sys, json, base64, re, html
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
sys.path.insert(0, UST)
import arayuz as A

G = os.path.join(HERE, "gorsel")


def js(*p):
    return json.load(open(os.path.join(*p), encoding="utf-8"))


d = js(HERE, "kabuk-analiz.json")
c = js(UST, "carpisma-sonuc.json")
m = js(UST, "montaj", "montaj-analiz.json")
omz = js(UST, "omuz", "omuz-analiz.json")
GE = A.GOGUS_EKRAN
ge = d["gogus_ekrani"]


def sayi(x, n=1):
    s = ("%." + str(n) + "f") % x
    tam, _, ond = s.partition(".")
    neg = tam.startswith("-")
    tam = tam.lstrip("-")
    gr = []
    while len(tam) > 3:
        gr.insert(0, tam[-3:])
        tam = tam[:-3]
    gr.insert(0, tam)
    return ("-" if neg and s.strip("-0.,") else "") + ".".join(gr) + ("," + ond if ond else "")


TR = [(r"\bGovde\b", "Gövde"), (r"\bGogus\b", "Göğüs"), (r"\bbandi\b", "bandı"), (r"\bsag\b", "sağ"), (r"\bkapagi\b", "kapağı"),
      (r"\bEtek on\b", "Etek ön"), (r"\bbraketi\b", "braketi"), (r"\bcivatasi\b", "cıvatası"), (r"\bIsil gomme somun\b", "Isıl gömme somun"),
      (r"\bcekic\b", "çekiç"), (r"\bdayali\b", "dayalı"), (r"\bucu\b", "ucu"), (r"\biceride\b", "içeride"), (r"\bkanal tabani\b", "kanal tabanı"),
      (r"\bsomun alti\b", "somun altı"), (r"\bdeligi\b", "deliği"), (r"\bekseninde\b", "ekseninde"), (r"\bkavramasi\b", "kavraması"),
      (r"\bucundan\b", "ucundan"), (r"\bdis yuzune\b", "dış yüzüne"), (r"\bayni\b", "aynı"), (r"\boturuyor\b", "oturuyor"),
      (r"\bbrakete\b", "brakete"), (r"\bboss'una\b", "boss'una"), (r"\bdudak altina\b", "dudak altına"), (r"\bkati\b", "katı"),
      (r"\bplakasi\b", "plakası"), (r"\bustu\b", "üstü"), (r"\balti\b", "altı"), (r"\bgovdesi\b", "gövdesi"), (r"\bmantari\b", "mantarı"),
      (r"\bboslugu\b", "boşluğu"), (r"\bkonnektor\b", "konnektör"), (r"\baku\b", "akü"), (r"\byatik\b", "yatık"), (r"\bburc\b", "burç"),
      (r"\bkati\b", "katı"), (r"\bpan servosu\b", "pan servosu"), (r"\bkontrplak\b", "kontrplak"), (r"\btasiyici\b", "taşıyıcı"),
      (r"\bduz\b", "düz"), (r"\bbaski\b", "baskı"), (r"\byan yuzu\b", "yan yüzü"), (r"\btablada\b", "tablada"),
      (r"\bdik\b", "dik"), (r"\bters\b", "ters"), (r"\bdis yuzu\b", "dış yüzü"), (r"\bust plakasi\b", "üst plakası"),
      (r"\balt kenari\b", "alt kenarı"), (r"\bomuz duvari\b", "omuz duvarı"), (r"\bcatali\b", "çatalı"), (r"\btupu\b", "tüpü"),
      (r"\bUst kol\b", "Üst kol"), (r"\bRulman kapagi\b", "Rulman kapağı"), (r"\bgobegi\b", "göbeği"), (r"\bkulak\b", "kulak"),
      (r"\bOmuz yuvasi\b", "Omuz yuvası"), (r"\bdiregi\b", "direği"), (r"\brayi\b", "rayı"), (r"\bSase\b", "Şase"),
      (r"\bparca\b", "parça"), (r"\bsayisi\b", "sayısı"), (r"\badlari\b", "adları"), (r"\bsirasi\b", "sırası"), (r"\bbuyuk\b", "büyük"),
      (r"\bsinir kutusu\b", "sınır kutusu"), (r"\bkutlesi\b", "kütlesi"), (r"\bagirlik\b", "ağırlık"), (r"\bgecerli\b", "geçerli"),
      (r"\bcakisma\b", "çakışma"), (r"\bbosluk\b", "boşluk"), (r"\bcakisan\b", "çakışan"), (r"\bGobek\b", "Göbek"), (r"\bdeger\b", "değer"),
      (r"\bkol_gobek\b", "kol × göbek"), (r"\bgobek_govde\b", "göbek × gövde"), (r"\bkol_govde\b", "kol × gövde"),
      (r"\bgruplari\b", "grupları"), (r"\bici\b", "içi"), (r"\bbaglantilar\b", "bağlantılar"), (r"\belemanlar\b", "elemanlar"),
      (r"\bihlali\b", "ihlali"), (r"\bayrilmis\b", "ayrılmış"), (r"\bbolge\b", "bölge"), (r"\btoplam\b", "toplam"),
      (r"\bkabuk\b", "kabuk"), (r"\bkol\b", "kol"), (r"^Baglanti$", "Bağlantı eleman"), (r"^Satin$", "Satın alınan"), (r"^Baski$", "Baskı")]


def tr(s):
    s = str(s)
    for a, b in TR:
        s = re.sub(a, b, s)
    return s


def esc(s):
    s = html.escape(tr(s))
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def img64(ad):
    return "data:image/png;base64," + base64.b64encode(open(os.path.join(G, ad), "rb").read()).decode()


def tablo(baslik, satirlar, sinif=""):
    h = ["<table class='%s'><tr>" % sinif + "".join("<th>%s</th>" % esc(b) for b in baslik) + "</tr>"]
    for s in satirlar:
        h.append("<tr>" + "".join("<td>%s</td>" % x for x in s) + "</tr>")
    h.append("</table>")
    return "".join(h)


OK = "<span class='ok'>tamam</span>"
NO = "<span class='no'>HATA</span>"
Y = A.YAZICI
UX, UY, UZ = Y["kullanilabilir"]

# ---------------------------------------------------------------- tarama ozeti (kol - kabuk)
tar = c["tarama"]
poz_say = sum(t["poz_sayisi"] for t in tar.values())
kol_kabuk = {}
for ad, t in tar.items():
    b = t.get("modul_bosluk_eklem_araliginda", {}).get("kabuk")
    kol_kabuk[ad] = b
omuz_ic = set()
for k in ("kol_govde",):
    for pz, hits in omz[k].items():
        if any("referans" not in h[1] for h in hits):
            omuz_ic.add(tuple(int(x) for x in pz.split(",")))
for k in ("kol_gobek",):
    for th, hits in omz[k].items():
        if hits:
            for phi in omz["phis"]:
                omuz_ic.add((phi, int(th)))
for k in ("gobek_govde",):
    for phi, hits in omz[k].items():
        if hits:
            for th in omz["ths"]:
                omuz_ic.add((int(phi), th))
kabuk_poz = {ad: set(tuple(p) for p in t.get("modul_cakisan_poz", {}).get("kabuk", [])) for ad, t in tar.items()}
kabuk_ek = {ad: sorted(v - omuz_ic) for ad, v in kabuk_poz.items()}
OA, YA = A.OMUZ["one_arka_aralik"], A.OMUZ["yana_aralik"]
eklem_ici = lambda pz: OA[0] <= pz[0] <= OA[1] and YA[0] <= pz[1] <= YA[1]
aralik_metni = "öne %s…%s°, yana %s…%s°" % tuple(sayi(v, 0) for v in (OA[0], OA[1], YA[0], YA[1]))
kabuk_eklem = {ad: [p for p in v if eklem_ici(p)] for ad, v in kabuk_poz.items()}
min_bosluk = min((b[0] for b in kol_kabuk.values() if b), default=None)
min_yer = next((b for b in kol_kabuk.values() if b and b[0] == min_bosluk), None)

baski = d["baski"]
desteksiz_degil = [b for b in baski if not b["desteksiz"]]
sigmayan = [b for b in baski if not b["sigar"]]
bag_ok = sum(1 for b in d["baglanti_kontrol"] if b["tamam"])
vida_ok = sum(1 for v in d["vida_kontrol"] if v["tamam"])
# gogus ekrani kontrolleri (kabuk_montaj 6b, 'gogus_ekrani'): olcu, sart, sonuc
_on = ge.get("cerceve_on", {})
ge_kont = [
    ("Kasa ↔ gövde direği", "%s mm" % sayi(ge["kasa_direk_mm"], 2), "≥ %s mm" % sayi(ge["kasa_direk_sart"], 0), ge["kasa_direk_tamam"]),
    ("Kasa ↔ göğüs bandı sağ / sol", "%s / %s mm" % (sayi(ge["kasa_gogus_sag_mm"], 2), sayi(ge["kasa_gogus_sol_mm"], 2)), "> 0",
     min(ge["kasa_gogus_sag_mm"], ge["kasa_gogus_sol_mm"]) > 0),
    ("Kasa ↔ çerçeve sağ / sol", "%s / %s mm" % tuple(sayi(v, 2) for v in ge["kasa_cerceve_mm"]), "> 0 (köşe takozu önü)", min(ge["kasa_cerceve_mm"]) > 0),
    ("VESA taşıyıcı ↔ direk / kasa", "%s / %s mm" % (sayi(ge["tasiyici_direk_mm"], 2), sayi(ge["tasiyici_kasa_mm"], 2)), "0 (dayalı)",
     ge["tasiyici_direk_mm"] < 0.01 and ge["tasiyici_kasa_mm"] < 0.01),
    ("Çerçeve flanşı ↔ göğüs bandı sağ / sol", "%s / %s mm" % tuple(sayi(v, 2) for v in ge["cerceve_flans_kabuk_mm"]), "0 (dayalı)",
     max(ge["cerceve_flans_kabuk_mm"]) < 0.01),
    ("M6 cıvata ucu (taşıyıcı flanşı → direk kanalı)", "%s mm" % sayi(ge["m6_uc_yuzden_mm"], 1), "%s…%s mm" % tuple(sayi(v, 1) for v in ge["m6_uc_sinir"]),
     ge["m6_tamam"]),
    ("Aktif alana önden giren parça", "%d" % len(_on.get("aktif_alana_giren_parca", {})), "0", not _on.get("aktif_alana_giren_parca")),
]
ekr_ok = sum(1 for k in ge_kont if k[3])
CG = d["agirlik_merkezi"]
kut_baski = sum(b["kutle_g"] for b in baski)
fil = sum(b["filament_g"] for b in baski)
sure = sum(b["sure_saat"] for b in baski)

# ---------------------------------------------------------------- tablolar
yz_satir = [
    ["Model", esc(Y["model"]) + " · " + esc(Y["nozul"])],
    ["Baskı hacmi (ana nozül)", "%s × %s × %s mm" % tuple(sayi(v, 0) for v in Y["hacim_ana"])],
    ["Yardımcı nozül / çift nozül", "%s × %s × %s mm" % tuple(sayi(v, 1).replace(",0", "") for v in Y["hacim_cift"])],
    ["Kullanılabilir (her eksende %s mm pay, tahmini)" % sayi(Y["pay"], 0),
     "<b>%s × %s × %s mm</b> (tek malzeme PETG, ana nozül) · çift nozülde %s × %s × %s" % (
         tuple(sayi(v, 0) for v in Y["kullanilabilir"]) + tuple(sayi(v, 1).replace(",0", "") for v in Y["kullanilabilir_cift"]))],
    ["Hazne / sıcaklık", "aktif ısıtmalı hazne en çok 65 °C · nozül 300 °C · tabla 120 °C"],
    ["Malzeme", "PLA, PETG, ABS, ASA, TPU, PA, PC, PET, PVA ve PLA/PETG destek malzemesi (her iki hotend)"],
    ["Kaynak", "<a href='%s'>%s</a> · %s" % (Y["kaynak"], Y["kaynak"], esc(Y["durum"]))],
]
bs_satir = []
for b in baski:
    o = b["olcu"]
    bs_satir.append([
        "<b>%s</b>" % esc(b["ad"]),
        "%s × %s × %s" % (sayi(o[0], 0), sayi(o[1], 0), sayi(o[2], 0)),
        (OK.replace("tamam", "sığıyor") if b["sigar"] else NO.replace("HATA", "SIĞMIYOR")) +
        ("<br><span class='not'>tabla açısı %d°%s</span>" % (b["tabla_aci"], "" if b["sigar_cift"] else " · çift nozülde sığmaz")),
        esc(b["yon"]),
        ("hayır" if b["desteksiz"] else "<b>evet</b> (%d katman)" % b["destek_sorun_sayi"]) +
        "<br><span class='not'>45° üstü çıkıntı %s %% (%s cm²)</span>" % (sayi(100 * b["cikinti_orani"], 1), sayi(b["cikinti_alan_cm2"], 1)),
        "%s g<br><span class='not'>filament %s g</span>" % (sayi(b["kutle_g"], 0), sayi(b["filament_g"], 0)),
        "%s sa" % sayi(b["sure_saat"], 1),
    ])
bs_satir.append(["<b>Toplam (%d parça)</b>" % len(baski), "", "%d / %d" % (len(baski) - len(sigmayan), len(baski)), "",
                 "%d parça destekli" % len(desteksiz_degil), "<b>%s g</b><br><span class='not'>filament %s g</span>" % (sayi(kut_baski, 0), sayi(fil, 0)),
                 "<b>%s sa</b>" % sayi(sure, 0)])

M6P = d["m6_vida_pay"]["kalemler"]      # kabuk_montaj.py: M6 vida ucu payi (somun ustu / kanal tabani)
GB_M6 = [x for x in M6P if x["tip"] == "govde"]
EB_M6 = [x for x in M6P if x["tip"] == "etek"]


def eleman_metni(tip):
    """kabuk-analiz.json 'baglanti' listesinden bu tipteki braketlerin baglanti elemanlari (adet x kalem)."""
    say = Counter(e for b in d["baglanti"] if b["tip"] == tip for e in b["eleman"])
    return " + ".join("%d× %s" % (n, k) for k, n in sorted(say.items(), key=lambda x: (-x[1], x[0])))


def braket_yerleri(tip):
    return sorted(set(b["ad"].split()[-1] for b in d["baglanti"] if b["tip"] == tip), key=lambda s_: float(s_.lstrip("yz").replace("+", "")))


N_GB = sum(1 for b in d["baglanti"] if b["tip"] == "govde")
N_EB = sum(1 for b in d["baglanti"] if b["tip"] == "etek")
HP, HB = A.SES_USB["hoparlor"], A.SES_USB["hub"]
bag_satir = [
    ["<b>Gövde kabuğu → gövde direği</b>",
     esc("%d adet 3 mm Al U braket (sağ ve sol; %s). Braket direğin yan kanalına 2× M6 ve çekiç somunla, kabuk yan duvarındaki "
         "damla boss'a M5 perçin somunla bağlanır." % (N_GB, ", ".join(braket_yerleri("govde")))),
     esc(eleman_metni("govde")), "%d" % N_GB],
    ["<b>Taban eteği → şase uzun rayları</b>",
     esc("%d adet 2 mm Al L braket (sağ ve sol; %s): yatay ayak uzun rayın üst kanalına M6 ve çekiç somunla, bükülü uç eteğin "
         "dik duvarına M3 perçin somunla bağlanır." % (N_EB, ", ".join(braket_yerleri("etek")))),
     esc(eleman_metni("etek")), "%d" % N_EB],
    ["<b>Baskı parçaları arası (bindirme)</b>",
     esc("Bir parçanın iç yarısı (1,5 mm) komşusunun dış yarısının arkasına 12 mm dil olarak uzanır. Dilde Ø8 damla boss + M3 ısıl gömme "
         "somun, komşunun dudağından M3 bombe başlı cıvata. Ust kapak ve etek ust plakasında alın birleşim (plakada dil havada kalırdı)." +
         ((" Dil ↔ komşu dış yarı boşluğu ölçüldü: %d dil çifti, en az %s mm (şart ≥ %s mm, tasarım %s mm)%s." % (
             len(d["bindirme_bosluk"]["ciftler"]), sayi(d["bindirme_bosluk"]["en_az_mm"], 4), sayi(d["bindirme_bosluk"]["sart_min_mm"], 2),
             sayi(d["bindirme_bosluk"]["tasarim_mm"], 2), "" if not d["bindirme_bosluk"]["ihlal"] else "; İHLAL %d" % len(d["bindirme_bosluk"]["ihlal"])))
          if d.get("bindirme_bosluk") and d["bindirme_bosluk"]["ciftler"] else "")),
     esc("%d× M3×6 ISO 7380 + %d× M3 ısıl gömme somun" % (len(d["vida_kontrol"]), len(d["vida_kontrol"]))), "%d" % len(d["vida_kontrol"])],
    ["<b>Göğüs ekranı (11,6\" kasalı) → göğüs bandı ve direk</b>",
     esc("Kasa (%s × %s × %s mm, zarf) eğik göğüs düzlemindeki cebe gömülü (cep %s × %s); önde iki yarım baskı çerçeve göğüs bandına "
         "cıvatalı, kasa önü çerçeve önünün %s mm gerisinde. Arkada VESA %s taşıyıcı: kasaya 4× M%d, direğin ön kanalına M%d ve çekiç somun." % (
             sayi(GE["kasa"][0], 2), sayi(GE["kasa"][1], 2), sayi(GE["kasa"][2], 1), sayi(GE["cep"][0], 2), sayi(GE["cep"][1], 2),
             sayi(GE["cam_geri"], 1), sayi(GE["vesa"], 0), GE["tasiyici"]["m4"][0], GE["tasiyici"]["m6"][0])),
     esc("%d× çerçeve cıvatası + ısıl gömme somun · 4× M%d×%d (VESA) · M%d×%d + çekiç somun (direk)" % (
         ge["vida_sayi"], GE["tasiyici"]["m4"][0], GE["tasiyici"]["m4"][1], GE["tasiyici"]["m6"][0], GE["tasiyici"]["m6"][1])), "%d" % ge["vida_sayi"]],
    ["<b>Hoparlör → gövde orta bandı sağ (iç yüz)</b>",
     esc("Hoparlör Ø%s × %s mm, orta bandın iç yüzünde (x %s, y %s), eksen duvara dik (K6 açık). Kap: ön halka + flanşlı arka tüp; "
         "arkada baskı kelepçe (köprü + iki bacak) ve 1 mm köpük ped hoparlörü kaba bastırır (F1a P1.7). Kap, kelepçe ve hoparlör ölçüsü VARSAYIM." % (
             sayi(HP["cap"], 0), sayi(HP["boy"], 0), sayi(HP["x"], 0), sayi(HP["y"], 1))),
     esc("2× M3×20 DIN 912 (kelepçe + flanş) + 2× M3 ısıl gömme somun (orta bant boss'u) + köpük ped 20 × 10"), "2"],
    ["<b>USB hub → üst arka servis kapağının içi</b>",
     esc("4 portlu hub (%s g) üst arka servis kapağının iç yüzünde (y %s…%s), raylı yuvada köpük bantla; kapakla birlikte sökülür. "
         "Ölçü satıcı sayfasından, port yönü VARSAYIM." % (sayi(HB["kutle_g"], 0), sayi(HB["y"][0], 0), sayi(HB["y"][1], 0))),
     esc("1 mm çift taraflı köpük bant"), "–"],
]
kont_satir = []
for b in d["baglanti_kontrol"]:
    det = []
    for ad, deger, ok in b["kontroller"]:
        if "civata ucu yuzden" in ad or "kavramasi" in ad or "kalan et" in ad:
            det.append(ad)
    kont_satir.append([esc(b["ad"]), esc(b["parca"]), "%d / %d" % (sum(1 for k in b["kontroller"] if k[2]), len(b["kontroller"])),
                       esc("; ".join(sorted(set(det)))), OK if b["tamam"] else NO])
vida_ozet = {}
for v in d["vida_kontrol"]:
    key = v["etiket"]
    vida_ozet.setdefault(key, []).append(v)
vk_satir = []
for k, vs in vida_ozet.items():
    vk_satir.append([esc(k), "%d" % len(vs), esc(", ".join(sorted(set(v["ic"] for v in vs)))), esc(", ".join(sorted(set(v["dis"] for v in vs)))),
                     sayi(min(v["kavrama"] for v in vs), 1) + " mm", sayi(min(v["dudak"] for v in vs), 2) + " mm",
                     OK if all(v["tamam"] for v in vs) else NO])

car_satir = []
for ad, t in tar.items():
    b = kol_kabuk[ad]
    car_satir.append([esc(ad), "%d" % t["poz_sayisi"], "%d" % len(kabuk_poz[ad]), "<b>%d</b>" % len(kabuk_eklem[ad]),
                      "%d" % len(kabuk_ek[ad]),
                      ("<b>%s mm</b><br><span class='not'>%s ↔ %s, öne %s° / yana %s°</span>" % (
                          sayi(b[0], 1), esc(b[1][1]), esc(b[1][2]), b[1][0][0], b[1][0][1])) if b else "–"])

bol_satir = [[esc(s), esc(a), sayi(dd, 1) + " mm", esc(p)] for s, a, dd, p in d["bolge"]["en_yakin"]]

# kutle ve AM (guncel ana montaj ve kabuk modulu)
am1 = m["agirlik_merkezi"]
km_satir = [
    ["Ana montaj (<code>montaj-analiz.json</code>)", "%d parça · <b>%s g</b>" % (m["parca_sayisi"], sayi(m["kutle_g"], 1)),
     "(%s; %s; %s)" % tuple(sayi(v, 1) for v in am1)],
    ["Kabuk modülü (<code>kabuk-analiz.json</code>)", "%d parça · <b>%s g</b>" % (d["parca_sayisi"], sayi(d["kutle_g"], 1)),
     "(%s; %s; %s)" % tuple(sayi(v, 1) for v in CG)],
    ["Çakışma taraması toplamı (<code>carpisma-sonuc.json</code>)", "%s g" % sayi(c["kutle_toplam_g"], 1),
     "(%s; %s; %s)" % tuple(sayi(v, 1) for v in c["agirlik_merkezi"])],
]
kg_satir = [[esc(k), sayi(v, 0) + " g"] for k, v in sorted(d["kutle_grup"].items(), key=lambda x: -x[1])]


AK, AK2, OD = A.ARKA_KAPAK, A.M6["arka_kapak_ust"], A.OMUZ_DUVAR
destekli = [b for b in baski if b["destek_sorun_sayi"]]
KARAR = [
    "**Yazıcı Bambu Lab X2D (doğrulandı):** üretici teknik sayfasında ana nozül 256 × 256 × 260 mm, yardımcı ve çift nozül 235,5 × 256 × 256 mm, "
    "aktif ısıtmalı hazne 65 °C. Parçalar tek malzeme PETG (VESA taşıyıcı PETG-CF) ile ana nozülde basılacak; her eksende 10 mm pay (tahmini).",
    "**Duvar %s mm:** bindirmede her yarı %s mm. Eğik yüzlerde yatay ofset kullanıldı; eğik göğüs duvarının normal kalınlığı daha incedir." % (
        sayi(A.KABUK_T, 1), sayi(A.KABUK_T / 2, 2)),
    "**Kesit:** yuvarlatılmış dikdörtgen, çizgisel loft (`arayuz.GOVDE_KESIT`). Omuz bölgesinde yan duvar %s mm düz (x %s…%s, R%s ped) ve Ø%s delik; "
    "omuz modülündeki referans duvarla birebir." % (sayi(OD["x1"] - OD["x0"], 0), sayi(OD["x0"], 0), sayi(OD["x1"], 0), sayi(OD["ped_r"], 0), sayi(2 * OD["delik_r"], 0)),
    "**1,58 m boyu:** gövde %s mm uzatıldı (UZAMA); araya sabit kesitli %d uzatma bandı girdi (%s mm her biri). Toplam boy %s mm (`lale158-kontrol.json`)." % (
        sayi(A.UZAMA, 0), A.UZATMA_BANT, sayi(A.UZAMA / A.UZATMA_BANT, 1), sayi(A.BOY, 1)),
    "**Bölme ve dikiş yerleri:** gövdede yatay dikişler y = %s; dikey dikiş x = 0 simetri çizgisi. Gövde %d, etek %d baskı parçası (servis kapakları dahil)." % (
        ", ".join(sayi(v, 1).replace(",0", "") for v in A.GOVDE_DIKIS), sum(1 for b in baski if b["grup"] == "Govde kabugu"),
        sum(1 for b in baski if b["grup"] == "Taban etegi")),
    "**Eğik göğüs ve 11,6\" ekran:** göğüs ön duvarı %s° eğik düzlem (y %s…%s); kasalı ekran düzlemdeki cebe gömülü, iki yarım çerçeve ve "
    "VESA taşıyıcıyla tutulur (yukarıdaki bağlantı tablosu ve göğüs ekranı kontrolleri)." % (
        sayi(A.GOGUS_EGIM, 0), sayi(A.GOGUS_ALT_Y, 1), sayi(A.GOGUS_UST_Y, 1)),
    "**Ses ve USB (yerleşim B + R1, 05.11.2026):** hoparlör gövde orta bandı sağ iç yüzünde, kap + kelepçeyle; USB hub üst arka servis kapağının "
    "içinde. Ses yükseltici PAM8403 ve USB ses kartı kafada (sol duvar), kabukta değil (K16, 04.11.2026).",
    "**Baskı yönleri:** gövde bantları dik (alt kenar tablada), omuz bandı ters (üst kapak tablada), servis kapakları dış yüzü tablada, "
    "etek ters (üst plaka tablada). Boss'lar baskı yönünde 45° damla şekilli; kontrol katman katman (1 mm, 45° kuralı).",
    "**İskelete bağlantı:** gövde %d U braket ile direğe, etek %d L braket ile uzun raylara. Teker ↔ etek en az %s mm." % (
        N_GB, N_EB, sayi(d["bosluk"]["teker_etek_mm"], 1)),
    "**Üst kapakta omuz yuvası erişim delikleri (Ø%s, x = ±%s):** omuz yuvasının üst M6 cıvatası başı için; anahtar da buradan girer. "
    "Boyun açıklığı R%s." % (sayi(2 * A.UST_KAPAK_ERISIM["r"], 0), sayi(A.UST_KAPAK_ERISIM["x"], 0), sayi(A.BOYUN_ACIKLIK_R, 0)),
    "**Servis kapakları:** arka servis kapağı %s × %s (y %s…%s), üst arka servis kapağı %s × %s (y %s…%s); üst kenarları dikişe alın dayanır." % (
        sayi(2 * AK["x"], 0), sayi(AK["y1"] - AK["y0"], 0), sayi(AK["y0"], 0), sayi(AK["y1"], 0),
        sayi(2 * AK2["x"], 0), sayi(AK2["y1"] - AK2["y0"], 0), sayi(AK2["y0"], 0), sayi(AK2["y1"], 0)),
]
ACIK = [
    "**Kol yana alt sınırın altına inerse kabuğa çarpar:** eklem aralığında (%s) kabuk çakışması %d. Tarama aralığının dışındaki pozlarda kol kabuğa "
    "çarpıyor (sağ %d, sol %d poz); bunların %d'i omuzun kendi parçalarına çarpmadığı pozlar (kabuk kaynaklı). Servo sınırı yazılımda tutulmalı. "
    "Omuz bölümü 03.11.2026 koşusundan (yeniden tarama P2.2/P6)." % (
        aralik_metni, sum(len(v) for v in kabuk_eklem.values()), len(kabuk_poz.get("omuz_sag", [])), len(kabuk_poz.get("omuz_sol", [])),
        len(kabuk_ek.get("omuz_sag", []))),
    "**Göğüs ekranı doğrulanacak:** kasa zarf modeli (arka yüz düz kabul; gerçek kasa kenara doğru eğimli, port girintisi var); port yeri fotoğraftan "
    "tahmini; kütle %s g üretici sayfasındaki \"Actual Weight\" (kutu dahil olabilir); VESA delik derinliği doğrulanmadı." % sayi(GE["kutle_g"], 0),
    "**Destek isteyen baskılar:** %s. Katman kontrolü kaba (1 mm katman, 45°); dilimleyicide yeniden bakılmalı." % (
        ", ".join("%s (%d katman)" % (b["ad"], b["destek_sorun_sayi"]) for b in destekli) if destekli else "yok"),
    "**Hoparlör, kap, kelepçe, köpük ped ve hub VARSAYIM:** ürünler elde yok (%s; hub: %s). Hoparlör ekseni K6'da açık." % (HP["durum"], HB["durum"]),
    "**Kütle, filament ve süre tahmini:** PETG yoğunluğu × doluluk, filament +%5 atık, süre ortalama debiyle. Gerçek değerler dilimleyiciden alınmalı.",
    "**Isıl gömme somun ve perçin somun ölçüleri tahmini** (`arayuz.INSERT`). Alınacak ürünün ölçüsüyle boss ve delik güncellenmeli.",
    "**Bindirme cıvataları dışarıdan görünür** (bombe baş).",
    "**Braket ayrıntıları tahmini:** Al sac kalınlığı (3 ve 2 mm), büküm yarıçapı modelde yok.",
    "**Görseller 03.11.2026 kabuk koşusundan:** `gorsel/*.png` K23 ara çıktısı (çerçeve, hoparlör kelepçesi ve P1.7 öncesi); `kabuk_gorsel.py` "
    "P6.1'de yeniden koşulacak. 125 cm ekran yuvasının iki eski görseli (`kabuk-nextion-on.png`, `kabuk-nextion-ic.png`) rapora alınmadı.",
]

# ---------------------------------------------------------------- HTML
H = []
H.append("""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kabuk Modülü 1,58 m</title><style>
:root{--bg:#f6f4ef;--card:#fff;--ink:#1d1f22;--mut:#666;--line:#e3e0d8;--acc:#7b8794;--acc2:#2f86d4;--ok:#2e8b57;--no:#c0392b}
@media (prefers-color-scheme:dark){:root{--bg:#16171a;--card:#202226;--ink:#ececec;--mut:#9a9a9a;--line:#33363b}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,Segoe UI,sans-serif}
main{max-width:1120px;margin:0 auto;padding:28px 16px 60px}
h1{font-size:28px;margin:0 0 4px}h2{font-size:19px;margin:34px 0 10px;border-bottom:2px solid var(--acc2);display:inline-block}
h3{font-size:16px;margin:18px 0 8px}.sub{color:var(--mut);margin-bottom:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
figure img{width:100%;display:block;background:#fff}figcaption{padding:8px 12px;color:var(--mut);font-size:13px}
.tw{overflow-x:auto}table{border-collapse:collapse;width:100%;background:var(--card);border-radius:10px;overflow:hidden;font-size:14px}
td,th{border-bottom:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}th{background:rgba(47,134,212,.12)}
table.sayi td:not(:first-child){text-align:right;white-space:nowrap}
.k{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi b{display:block;font-size:21px}.kpi span{color:var(--mut);font-size:13px}
ol li,ul li{margin:5px 0}code{background:rgba(127,127,127,.15);padding:1px 5px;border-radius:4px}
.ok{color:var(--ok);font-weight:600}.no{color:var(--no);font-weight:600}.wide{grid-column:1/-1}
.not{color:var(--mut);font-size:13px}a{color:var(--acc2)}
</style></head><body><main>""")
H.append("<h1>Kabuk modülü (1,58 m): gövde kabuğu + taban eteği</h1>")
H.append(__import__("carpisma_kos").eskime_html())   # C6: carpisma-sonuc.json eskidiyse uyari kutusu (bos dize = guncel)
H.append("<div class='sub'>FreeCAD 1.1 · <code>kabuk_montaj.py</code> · %d parça (%d baskı) · PETG %s mm duvar · boy %s mm · göğüste %s · "
         "ölçüler <code>arayuz.py</code>'den · yazıcı %s</div>" % (
             d["parca_sayisi"], d["baski_sayisi"], sayi(A.KABUK_T, 1), sayi(A.BOY, 0), esc(GE["model"]), esc(Y["model"])))
kpi = [
    ("%d / %d" % (d["baski_sayisi"], d["parca_sayisi"]), "baskı parçası / toplam parça · hepsi geçerli, tek katı" if not d["gecersiz"] and not d["coklu_kati"] else "GEÇERSİZ PARÇA VAR"),
    ("%d" % len(d["cakisma"]), "kabuk içi çakışma (%d çift sınandı)" % d["cakisma_cift_sayisi"]),
    ("%d" % len(d["iskelet_cakisma"]), "kabuk ↔ iskelet çakışma · ayrılmış bölge ihlali %d" % len(d["bolge"]["ihlal"])),
    ("%d" % sum(len(v) for v in kabuk_eklem.values()), "kol ↔ kabuk çakışma, eklem aralığında (iki omuz, %d poz)" % poz_say),
    ("%s mm" % (sayi(min_bosluk, 1) if min_bosluk is not None else "–"), "en küçük kol-kabuk boşluğu (eklem aralığında)"),
    ("%d / %d" % (len(baski) - len(sigmayan), len(baski)), "X2D'ye sığan parça (%s × %s × %s) · desteksiz basılamayan %d" % (
        sayi(UX, 0), sayi(UY, 0), sayi(UZ, 0), len(desteksiz_degil))),
    ("%d / %d" % (bag_ok, len(d["baglanti_kontrol"])), "iskelete bağlantı kontrolü · bindirme %d/%d, göğüs ekranı %d/%d" % (
        vida_ok, len(d["vida_kontrol"]), ekr_ok, len(ge_kont))),
    ("%s kg" % sayi(d["kutle_g"] / 1000, 2), "kabuk kütlesi (baskı %s kg, göğüs ekranı %s kg) · AM yerden %s mm" % (
        sayi(kut_baski / 1000, 2), sayi(GE["kutle_g"] / 1000, 2), sayi(CG[1], 0))),
]
H.append("<div class='k'>" + "".join("<div class='kpi'><b>%s</b><span>%s</span></div>" % (a, esc(b)) for a, b in kpi) + "</div>")

H.append("<h2>Görünümler</h2><div class='grid'>")
for ad, cap, w in (("kabuk-izometrik.png", "İzometrik: kabuk, iskelet, iki omuz, göğüs ekranı", ""), ("kabuk-on.png", "Önden", ""),
                   ("kabuk-yan.png", "Yandan (+X)", ""),
                   ("kabuk-arka-kapak-acik.png", "Arkadan: servis kapağı açık (dışarı çekilmiş); direk ve alt braketler görünür", ""),
                   ("kabuk-kesit.png", "Kesit x = 0: gövde, eğik göğüs, direk, etek", ""),
                   ("kabuk-kesit-gogus.png", "Kesit yakın: gövde duvarı, boss'lar, dikişler", ""),
                   ("kabuk-patlatilmis.png", "Patlatılmış: her baskı parçası ayrı renk", "wide"),
                   ("kabuk-patlatilmis-on.png", "Patlatılmış, önden", ""),
                   ("kabuk-omuz-duvari.png", "Omuz bölgesi: düz yan duvar, omuz deliği (kabuk yarı saydam)", ""),
                   ("kabuk-baglanti-govde.png", "Gövde braketi: direğe 2× M6 + çekiç somun, gövde boss'una M5 (kabuk yarı saydam)", ""),
                   ("kabuk-baglanti-etek.png", "Etek braketi: uzun ray üst kanalına M6, etek boss'una M3 (kabuk yarı saydam)", "")):
    if os.path.exists(os.path.join(G, ad)):
        H.append("<figure class='%s'><img src='%s' alt='%s'><figcaption>%s</figcaption></figure>" % (w, img64(ad), esc(cap), esc(cap)))
H.append("</div><p class='not'>Görseller 03.11.2026 kabuk koşusundan (K23 ara çıktısı): çerçeve, hoparlör kelepçesi ve sonraki "
         "değişiklikleri göstermez; <code>kabuk_gorsel.py</code> P6.1'de yeniden koşulacak.</p>")

H.append("<h2>3D yazıcı</h2><div class='tw'>" + tablo(["", ""], yz_satir) + "</div>")
H.append("<h2>Baskı parçaları</h2><div class='tw'>")
H.append(tablo(["Parça", "Ölçü (baskı yönünde, mm)", "Tablaya sığıyor mu", "Baskı yönü", "Destek gerekir mi / çıkıntı", "Kütle (tahmini)", "Süre (tahmini)"], bs_satir))
H.append("</div><p class='not'>Ölçü: tabla düzleminde en iyi açıyla (0…90°) yerleşimin genişlik × derinliği ve baskı yüksekliği. Destek kontrolü: parça "
         "baskı yönüne çevrilip 1 mm katmanlara kesildi; her katmanın, bir alttaki katmanın 1 mm (45°) büyütülmüş izinin dışında kalan kısmı "
         "desteksiz sayıldı. 2 mm'den dar şeritler (bindirme basamakları) ve 15 mm'den kısa açıklıklar (Ø17 sonar delikleri) köprülenebilir "
         "kabul edildi (tahmini). Çıkıntı oranı: tabla yüzeyi dışında, normali aşağıya 45°'den dik bakan yüzey alanı / toplam yüzey.</p>")

H.append("<h2>Bağlantılar</h2><div class='tw'>")
H.append(tablo(["Bağlantı", "Nasıl oturuyor", "Bağlantı elemanı (toplam)", "Adet"], bag_satir))
H.append("</div><h3>İskelete bağlantı kontrolleri (her braket ayrı)</h3><div class='tw'>")
H.append(tablo(["Braket", "Kabuk parçası", "Kontrol", "Ölçü", "Sonuç"], kont_satir))
H.append("</div><p class='not'>Her braket: braket profile ve kabuk boss'una dayalı (0,00 mm), çekiç somun dudak altına dayalı, M6 cıvata ucu "
         "somunu en az %s mm geçiyor ve kanal tabanına en az %s mm kalıyor (uç %s…%s mm; gerçek: gövde braketi uç %s mm, somun payı %s / taban payı %s; etek braketi uç %s mm, %s / %s), cıvata ve somun aynı eksende, pul (varsa) ya da pulsuz baş brakete dayalı; kabuk tarafında cıvata "
         "kavraması ≥ cıvata çapı ve ≤ ısıl gömme somun deliği, cıvata ucundan dış yüzeye ≥ 1 mm et, ısıl gömme somun boss'ta.</p>" % (
             sayi(d["m6_vida_pay"]["sart_somun_gecme_mm"], 1), sayi(d["m6_vida_pay"]["sart_taban_pay_mm"], 1),
             sayi(A.LIP + A.CEKIC_SOMUN["T"] + d["m6_vida_pay"]["sart_somun_gecme_mm"], 1), sayi(A.KANAL_TABAN - d["m6_vida_pay"]["sart_taban_pay_mm"], 1),
             sayi(GB_M6[0]["uc_mm"], 1), sayi(min(x["somun_pay_mm"] for x in GB_M6), 1), sayi(min(x["taban_pay_mm"] for x in GB_M6), 1),
             sayi(EB_M6[0]["uc_mm"], 1), sayi(min(x["somun_pay_mm"] for x in EB_M6), 1), sayi(min(x["taban_pay_mm"] for x in EB_M6), 1)))
H.append("<h3>Bindirme cıvataları</h3><div class='tw'>")
H.append(tablo(["Dikiş", "Adet", "Isıl gömme somun (dil)", "Cıvata (dudak)", "En kısa kavrama", "Dudak", "Sonuç"], vk_satir))
H.append("</div><p class='not'>Cıvata başı dudağa dayalı, ısıl gömme somun boss'ta oturuyor, kavrama 3…5,7 mm, dudak ≥ 1,2 mm.</p>")
H.append("<h3>Göğüs ekranı kontrolleri (<code>kabuk-analiz.json</code> → <code>gogus_ekrani</code>)</h3><div class='tw'>")
H.append(tablo(["Kontrol", "Ölçülen", "Şart", "Sonuç"], [[esc(a), b, esc(c_), OK if ok else NO] for a, b, c_, ok in ge_kont]))
H.append("</div><p class='not'>%s. Kasa ölçüsü üreticinin kasalı ekranı için zarf (%s); port girintisi modelde yok, port yeri fotoğraftan tahmini "
         "(<code>arayuz.GOGUS_EKRAN['port']</code>: %s).</p>" % (esc(ge["not_"]), esc(GE["model"]), esc(GE["port"]["durum"])))

H.append("<h2>Çakışma sonuçları</h2><ul>")
H.append("<li>Kabuk içi: <b>%d çakışma</b> (%d parça, %d sınır kutusu kesişen çift gerçek kesişimle sınandı, eşik %s mm³).</li>" % (
    len(d["cakisma"]), d["parca_sayisi"], d["cakisma_cift_sayisi"], sayi(d["tolerans_mm3"], 1)))
H.append("<li>Kabuk ↔ iskelet: <b>%d çakışma</b> (%d çift). Gövde iç yüzü ile direk arasında en az %s mm.</li>" % (
    len(d["iskelet_cakisma"]), d["iskelet_cift_sayisi"], sayi(d["bosluk"]["direk_govde_mm"], 1)))
H.append("<li>Ayrılmış bölgeler: %d bölge, <b>%d ihlal</b>. Teker ↔ etek en az %s mm.</li>" % (
    d["bolge"]["kontrol_edilen"], len(d["bolge"]["ihlal"]), sayi(d["bosluk"]["teker_etek_mm"], 1)))
H.append("<li>Modüller arası (<code>carpisma.py</code>, ev pozu): <b>%d çakışma</b> (%d sınır kutusu kesişen çift).</li></ul>" % (
    len(c["ev_pozu_cakisma"]), c["ev_pozu_kesisen_cift"]))
H.append("<div class='tw'>" + tablo(["Omuz", "Taranan poz", "Kabuğa çarpan poz (tümü)", "Eklem aralığında", "Kabuk kaynaklı (omuz kendine çarpmıyor)",
                                     "En küçük kol-kabuk boşluğu (eklem aralığında)"], car_satir) + "</div>")
H.append("<p class='not'>Tarama: %s; her omuz %d poz. Eklem aralığı %s. Kabuğa çarpan pozların yana açıları: %s. Omuz bölümü "
         "03.11.2026 koşusundan (<code>carpisma-sonuc.json</code> <code>bolumler.omuz</code>); yeniden tarama P2.2/P6.</p>" % (
             esc(list(tar.values())[0].get("aciklama", "")), list(tar.values())[0]["poz_sayisi"], aralik_metni,
             ", ".join(sorted(set("%d°" % p[1] for v in kabuk_poz.values() for p in v), key=lambda x: int(x[:-1])))))
H.append("<h3>Kabuğun ayrılmış bölgelere en yakın noktası</h3><div class='tw'>" + tablo(["Sahip", "Bölge", "En küçük boşluk", "Kabuk parçası"], bol_satir) + "</div>")

H.append("<h2>Kütle ve ağırlık merkezi</h2><div class='grid'><div>")
H.append(tablo(["", "Parça · kütle", "AM (x; y; z) mm"], km_satir))
H.append("</div><div>" + tablo(["Grup", "Kütle"], kg_satir, "sayi") + "</div></div>")
H.append("<p class='not'>Ana montaj modülleri: %s. Parça: %s. Kütle karşılaştırması %s g fark (analiz JSON'ları 0,1 g yuvarlı). "
         "Çakışma taraması toplamı birleştirilen bölüm koşularından; ana montajdan farklıysa tarama, son kütle değişikliğinden önce koşulmuştur.</p>" % (
    esc(", ".join(x["ad"] for x in m["moduller"])), esc(m["karsilastirma"]["parca"]["formul"]), sayi(m["karsilastirma"]["kutle"]["fark_analiz"], 2)))

H.append("<p class='not'>Robotun korunan değerleri (boy, çakışmalar, rampa, tilt/pan payı, mikrofon–hoparlör, SY8205): "
         "<code>planlama/d158/regresyon.py</code>.</p>")

H.append("<h2>Kararlar</h2><ul>" + "".join("<li>%s</li>" % esc(s) for s in KARAR) + "</ul>")
H.append("<h2>Açık işler ve varsayımlar</h2><ul>" + "".join("<li>%s</li>" % esc(s) for s in ACIK) + "</ul>")
H.append("<h2>Dosyalar</h2><ul>"
         "<li><code>kabuk-montaj.FCStd</code> · <code>kabuk-montaj.step</code> (geri okuma %d katı) · <code>kabuk-bom.csv</code> · "
         "<code>kabuk-analiz.json</code> · <code>gorsel/</code></li>"
         "<li><code>kabuk_lib.py</code> (kesit, zarf, damla boss, ISO 7380) · <code>kabuk_parcalar.py</code> · <code>kabuk_montaj.py</code> "
         "(kontroller, baskı analizi, kayıt) · <code>kabuk_gorsel.py</code> · <code>kabuk_rapor.py</code></li>"
         "<li>Ortak: <code>../arayuz.py</code> (YAZICI, KABUK_*, GOVDE_KESIT, ETEK_KESIT, GOGUS_EKRAN, SES_USB, bölgeler) · <code>../carpisma.py</code> · "
         "<code>../montaj/moduller.py</code></li></ul>" % d["step_kati"])
H.append("</main></body></html>")
open(os.path.join(HERE, "rapor.html"), "w", encoding="utf-8").write("\n".join(H))
print("rapor.html yazildi", os.path.getsize(os.path.join(HERE, "rapor.html")) // 1024, "kB")
