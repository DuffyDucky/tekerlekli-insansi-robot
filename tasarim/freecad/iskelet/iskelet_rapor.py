# Iskelet modulu raporu (rapor.html, gorseller gomulu). Sistem Python'u ile calisir (FreeCAD gerekmez).
# Girdiler: iskelet-analiz.json (iskelet_montaj.py), ../carpisma-sonuc.json (carpisma.py),
#           ../omuz/regresyon/fark.json (omuz_regresyon.py), ../arayuz.py, gorsel/*.png (iskelet_gorsel.py)
import os, sys, json, base64, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
sys.path.insert(0, UST)
import arayuz as A

G = os.path.join(HERE, "gorsel")
d = json.load(open(os.path.join(HERE, "iskelet-analiz.json"), encoding="utf-8"))
c = json.load(open(os.path.join(UST, "carpisma-sonuc.json"), encoding="utf-8"))
r = json.load(open(os.path.join(UST, "omuz", "regresyon", "fark.json"), encoding="utf-8"))


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
    return ("-" if neg else "") + ".".join(gr) + ("," + ond if ond else "")


TR = [(r"\bSase\b", "Şase"), (r"\bsag\b", "sağ"), (r"\bon yuz\b", "ön yüz"), (r"\barka yuz\b", "arka yüz"),
      (r"\brayi\b", "rayı"), (r"\bGovde diregi\b", "Gövde direği"), (r"\bGovde kabugu yan yuzu\b", "Gövde kabuğu yan yüzü"),
      (r"\bUst kol tupu\b", "Üst kol tüpü"), (r"\bagir\b", "ağır"), (r"\bgenis kose baglanti\b", "geniş köşe bağlantı"),
      (r"\bIc kose baglanti\b", "İç köşe bağlantı"), (r"\bcekic somun\b", "çekiç somun"), (r"\bolcu\b", "ölçü"),
      (r"^Baglanti$", "Bağlantı eleman"), (r"^Satin$", "Satın alınan"), (r"\bparca\b", "parça"), (r"\bsayisi\b", "sayısı"),
      (r"\badlari\b", "adları"), (r"\bsirasi\b", "sırası"), (r"\bbuyuk\b", "büyük"), (r"\bsinir kutusu\b", "sınır kutusu"),
      (r"\bkutlesi\b", "kütlesi"), (r"\bagirlik\b", "ağırlık"), (r"\bkati\b", "katı"), (r"\bgecerli\b", "geçerli"),
      (r"\bcakisma\b", "çakışma"), (r"\bbosluk\b", "boşluk"), (r"\bcakisan\b", "çakışan"), (r"\bGobek\b", "Göbek"),
      (r"\bGovde\b", "Gövde"), (r"\bdeger\b", "değer"), (r"\btarama\b", "tarama"), (r"\bkol_gobek\b", "kol × göbek"),
      (r"\bgobek_govde\b", "göbek × gövde"), (r"\bkol_govde\b", "kol × gövde"), (r"\bpoz\b", "poz"),
      (r"\bDirek-ray\b", "Direk-ray"), (r"\bkose\b", "köşe"), (r"\bparcasi\b", "parçası"), (r"\buyumu\b", "uyumu"),
      (r"\bayrica\b", "ayrıca"), (r"\bduvari\b", "duvarı"), (r"\bmodulunun\b", "modülünün"), (r"\btutucusu\b", "tutucusu"),
      (r"\bone-arka\b", "öne-arka"), (r"\btaramasi\b", "taraması"), (r"\badim\b", "adım"), (r"\bderece\b", "derece"),
      (r"\bcercevesi\b", "çerçevesi"), (r"\bdiregi\b", "direği"), (r"\bbaglantilari\b", "bağlantıları"),
      (r"\byuvasi\b", "yuvası"), (r"\bplakasi\b", "plakası"), (r"\bkati\b", "katı"), (r"\bburc\b", "burç"),
      (r"\baku\b", "akü"), (r"\btasiyici\b", "taşıyıcı"), (r"\bkontrplak\b", "kontrplak"), (r"\bsol\b", "sol"),
      (r"\buzun\b", "uzun"), (r"\byatik\b", "yatık")]


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


E = d["egilme"]
ek = E["en_kotu"]
son = E["sonuc"]
tarama = c["tarama"]
n_poz = sum(t["poz_sayisi"] for t in tarama.values())
bag_ok = sum(1 for b in d["baglanti_kontrol"] if b["tamam"])
CG = d["agirlik_merkezi"]
kesim = d["kesim"]
el_max = max(a["el_dususu_mm"] for a in E["adli"])

# ---------------------------------------------------------------- baglanti tablosu (gruplu)
gruplar = {}
for b in d["baglanti"]:
    if b["tip"] == "kose":
        anah = ("Gövde direği → orta ara ray (şase)" if "ray" in b["ad"] else "Omuz traversi → gövde direği", b["tip"])
    else:
        ray = b["profiller"][0].replace("Sase ara rayi ", "")
        anah = ("Şase %s ara rayı → sağ ve sol uzun ray" % {"arka": "arka", "orta": "orta", "on": "ön"}[ray], b["tip"])
    gruplar.setdefault(anah, []).append(b)
bag_satir = []
for (ad, tip), bl in gruplar.items():
    n = len(bl)
    if tip == "kose":
        nasil = ("Direk orta ara rayın üst yüzüne alın dayanır. Direğin iki yan (±X) yüzünde birer 40×40 geniş köşe bağlantı: "
                 "A ayağı rayın üst yüzüne, B ayağı direğin yan yüzüne; 9 mm kamalar kanal ağzına girer."
                 if "ray" in bl[0]["ad"] else
                 "Travers direğin üst ucuna alın dayanır. Direğin iki yan yüzünde birer köşe bağlantı: A ayağı traversin alt "
                 "yüzüne, B ayağı direğe.")
        el = "%d× 40×40 geniş köşe bağlantı (Robolink, 75 g) · %d× M6×16 DIN 912 · %d× M6 DIN 125 pul · %d× M6 çekiç somun (kanal 10)" % (
            n, 2 * n, 2 * n, 2 * n)
    else:
        nasil = ("Ara ray uzun rayların iç yüzüne alın alın dayanır. %d iç köşe: ayak 1 ara rayın %s kanalında, ayak 2 uzun rayın "
                 "iç yüz kanalında; flans dudakların altına oturur, dışarı taşmaz." % (n, "iki yan" if n == 4 else "iç yan"))
        el = "%d× iç köşe bağlantı kanal 10 (tahmini ölçü) · %d× M6×10 DIN 913 set vida (uçları kanal tabanına dayanır)" % (n, 2 * n)
    bag_satir.append(["<b>%s</b>" % esc(ad), esc(nasil), esc(el), "%d" % n])
bag_satir.append(["<b>Omuz yuvası → travers ucu</b> (omuz modülü, arayüz)",
                  esc("Yuva traversin x 70…103 ucuna geçer (0,2 mm boşluk), uç duvarına dayanır; iki omuzda aynı."),
                  esc("Omuz başına 4× M6×16 DIN 912 + 4× M6 pul + 4× M6 çekiç somun, dört yüzde x = 86'da"), "2"])

# ---------------------------------------------------------------- baglanti kontrol ozeti
kont_satir = []
for b in d["baglanti_kontrol"]:
    detay = []
    for ad, deger, ok in b["kontroller"]:
        if "civata ucu" in ad:
            detay.append("cıvata ucu %s mm (somun altı %s, kanal tabanı %s)" % (sayi(deger), sayi(A.LIP + A.CEKIC_SOMUN["T"]), sayi(A.KANAL_TABAN)))
    n = len(b["kontroller"])
    m = sum(1 for k in b["kontroller"] if k[2])
    kont_satir.append([esc(b["ad"]), "köşe bağlantı" if b["tip"] == "kose" else "iç köşe",
                       "%d / %d" % (m, n), esc("; ".join(sorted(set(detay))) or "gövde iki profile ve set vidalar kanal tabanına dayalı (0,00 mm)"),
                       "<span class='ok'>tamam</span>" if b["tamam"] else "<span class='no'>HATA</span>"])

# ---------------------------------------------------------------- regresyon
reg_satir = []
for s in r["satirlar"]:
    f = "–" if s["fark"] is None else ("0" if s["fark"] == 0 else "%.2e" % s["fark"])
    reg_satir.append([esc(s["olcut"]), esc(s["once"]), esc(s["sonra"]), f,
                      "<span class='ok'>aynı</span>" if s["ayni"] else "<span class='no'>farklı</span>"])

# ---------------------------------------------------------------- egilme tablolari
eg_satir = []
for a in E["adli"]:
    tmax = max(a["travers"], key=lambda t: t["sigma_MPa"])
    eg_satir.append([esc(a["ad"]), sayi(a["Mx_Nm"], 2), sayi(a["Mz_Nm"], 2), sayi(a["sigma_direk_MPa"], 2),
                     sayi(a["sehim_tepe_mm"], 3), sayi(tmax["sigma_MPa"], 2), sayi(tmax["sehim_uc_mm"], 4),
                     sayi(max(abs(t["Mt_Nmm"]) for t in a["travers"]) / 1000, 2), sayi(a["el_dususu_mm"], 3)])

# ---------------------------------------------------------------- moduller
mod_satir = []
for m in c["moduller"]:
    mod_satir.append([esc(m["ad"]), "(%s)" % ", ".join(sayi(x, 0) for x in m["konum"]), "X aynası" if m["ayna"] else "–",
                      "%d" % m["parca"], "hareketli (2 eksen)" if m["hareketli"] else "sabit",
                      esc(", ".join(m["haric"]) or "–")])
tar_satir = []
for ad, t in tarama.items():
    yk = t["en_yakin"]
    tar_satir.append([esc(ad), "%d" % t["poz_sayisi"], "%d" % t["cakisan_poz"], "%d" % t["eklem_araliginda_cakisan"],
                      sayi(t["en_kucuk_bosluk_mm"]) + " mm",
                      esc("%s ↔ %s / %s, poz (öne %s°, yana %s°)" % (yk[1], yk[2], yk[3], yk[0][0], yk[0][1])) if yk else "–"])

# ---------------------------------------------------------------- ayrilmis bolgeler
bol_satir = []
for z in A.BOLGELER:
    k = z["kutu"]
    bol_satir.append([esc(z["sahip"]), esc(z["ad"]), "x %s…%s · y %s…%s · z %s…%s" % tuple(sayi(v, 1) for v in k),
                      esc(z["kaynak"]), esc(z["not_"])])

# ---------------------------------------------------------------- BOM ve kesim
bom_satir = [[esc(t), esc(k), "%d" % n, sayi(m, 0)] for t, k, n, m in d["bom"]]
cub_satir = []
for i, cb in enumerate(kesim["cubuklar"], 1):
    cub_satir.append(["%d" % i, esc(" + ".join("%s (%s)" % (sayi(L, 1).rstrip("0").rstrip(","), ad) for L, ad in cb["parcalar"])),
                      sayi(cb["artik"], 1) + " mm"])

KARAR = [
    "**Şase T birleşimlerinde iç köşe bağlantı:** Ara raylar uzun rayların arasına aynı yükseklikte girdiği için dış köşe bağlantı "
    "yalnız iç köşelere (yatay düzlemde) konabilir. Bu 8 iç köşenin hepsinde taban modülüne ayrılmış bir hacim var: arkada akü "
    "(uzun raya 4,5 mm), önde BTS7960, ortada akü ve XL4016. 37 mm'lik köşe bağlantı bunlara giriyor. Kanal içi iç köşe bağlantı "
    "dışarı taşmıyor, ayrılmış bölgelerle çakışmıyor.",
    "**Köşe bağlantı delik düzeni robot_cad'den farklı:** `robot_cad.py` `corner_br()` ayak başına z = ±9'da iki delik çiziyor. "
    "40×40 yüzde tek kanal (10,2) olduğu için bu delikler kanala denk gelmez. Robolink çiziminde her ayakta ortada tek oval delik ve 9 mm "
    "genişlikte kama var (çizimdeki 9 kama genişliği). Burada çizim izlendi; `robot_cad.py`'ye dokunulmadı.",
    "**Direk ve travers bağlantısı robot_cad V3 düzeninde:** Direğin iki yan yüzünde ikişer köşe bağlantı (tabanda 2, traverste 2). "
    "Elektronik katı ile direk dibi köşe bağlantıları arasında 3 mm boşluk var (174,5 − 171,5).",
]

ACIK = [
    "**İç köşe bağlantı ölçüleri tahmini:** ayak 26 mm, boyun 9,6, flanş 17 × 3, 2× M6 set vida. Satın alınacak ürün seçilince `arayuz.IC_KOSE` "
    "güncellenmeli, iskelet yeniden çalıştırılmalı. Yerine uç bağlantı (ara ray ucuna diş + uzun raya delik) da düşünülebilir.",
    "**Köşe bağlantı ayrıntıları tahmini:** ayak kalınlığı 4,5, yan duvar 3, oval delik 6,6 × 10, kama yüksekliği 2 mm (dış ölçü, kama genişliği "
    "ve kütle üreticiden). Ürün gelince kumpasla ölçülmeli.",
    "**Çekiç somun 16 × 10 × 5 ve kanal tabanı (13 mm genişlik, yüzden 11,8) tahmini:** cıvata ucu payı (1,9 mm) buna bağlı. Kanal tabanı "
    "üretici çiziminden ölçülmedi; kesit alanı 732 mm²'ye göre seçildi (modelde 726 mm², −0,8 %).",
    "**Bağlantı rijitliği hesaplanmadı:** Kollar öndeyken direk dibinde ve travers-direk birleşiminde X ekseni etrafında ≈ %s N·m moment "
    "var. Dört köşe bağlantının cıvataları z = 0'da, yani bu momentin nötr ekseninde. Moment yalnız köşe bağlantının 37,7 mm genişliğindeki "
    "sıkma sürtünmesiyle taşınır. Profil hesabı bu esnekliği içermez." % sayi(max(abs(a["Mx_Nm"]) for a in E["adli"]), 1),
    "**Öneri (tasarım değişmedi):** Kollar öne açıkken sallanma görülürse direk ile orta ara rayın ön ve arka yüzlerine (aynı düzlemde, "
    "z = ±20) birer düz T bağlantı plakası, direk ile traversin ön ve arka yüzlerine de birer T plaka eklenebilir. Tabanda plaka elektronik "
    "katının altında kalmalı (direk kesiği ±22 mm, plaka ≤ 2 mm kalınlıkta değilse kesik büyütülmeli).",
    "**Taban modülü:** Alt plaka (3 mm Al) raylara cıvatalanınca şase düzlem içinde rijitleşir; iç köşe bağlantılar tek başına bunu "
    "sağlamaz. Plaka, burç, akü, motor ve elektronik yerleri `arayuz.BOLGELER`'de (31 bölge).",
    "**Dirsek ve aşağısı çizilmedi:** Modüller arası tarama üst kol tüpünün ucuna (omuzdan 140 mm) kadar. Tork ve eğilme hesabında alt kol "
    "260 g ve el ucu %s mm (tahmini). Dirsek modülü `carpisma.py` içindeki `KONTROL` listesine eklenince tam kol taranır." % sayi(306, 0),
    "**Kabuk ve kafa:** Gövde kabuğu (torso3) ve kafa henüz FreeCAD'de yok. Kafa için traversin üst yüzü x −35…35 (boyun plakası) ayrıldı. "
    "Omuzdaki kabuk duvarı x = 152 varsayımı sürüyor.",
    "**Direk boyu 800,5 mm:** robot_cad V3 ölçüsü (Y_RAIL1 134,5 → S3 − 20 = 935). Kesimde ±0,5 mm tolerans traversin yüksekliğini aynı "
    "miktarda değiştirir.",
]

H = []
H.append("""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>İskelet Modülü V3</title><style>
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
.not{color:var(--mut);font-size:13px}
</style></head><body><main>""")
H.append("<h1>İskelet modülü (V3): şase, gövde direği, omuz traversi</h1>")
H.append("<div class='sub'>FreeCAD 1.1 · <code>iskelet_montaj.py</code> · %d parça · ölçüler <code>arayuz.py</code>'den (robot_cad V3) · "
         "plakalar, motorlar, akü ve elektronik taban modülünde</div>" % d["parca_sayisi"])

kpi = [
    ("%d / %d" % (len(d["cakisma"]), d["parca_sayisi"]), "iskelet içi çakışma / parça (hepsi geçerli, tek katı)"),
    ("%d / %d" % (bag_ok, len(d["baglanti_kontrol"])), "bağlantı oturma kontrolü tamam"),
    ("%d" % c["toplam"]["cakisma"], "modüller arası çakışma (ev pozu + %d poz tarama)" % n_poz),
    ("birebir aynı" if r["hepsi_ayni"] else "FARK VAR", "omuz regresyonu (%d ölçüt)" % len(r["satirlar"])),
    ("%s kg" % sayi(d["kutle_g"] / 1000, 2), "iskelet kütlesi · AM yerden %s mm, x %s, z %s" % (sayi(CG[1], 0), sayi(CG[0], 1), sayi(CG[2], 1))),
    ("%s mm" % sayi(ek["sehim_tepe_mm"], 2), "direk tepe sehimi, en kötü poz (sınır %s, tahmini)" % sayi(E["sinir"]["direk_mm"], 1)),
    ("%s MPa" % sayi(ek["direk_sigma_MPa"], 2), "direk en büyük gerilme · emniyet ≈ %s×" % sayi(son["direk_emniyet"], 0)),
    ("%s m" % sayi(kesim["toplam_mm"] / 1000, 2), "sigma toplam boy · %d × %s mm çubuktan" % (len(kesim["cubuklar"]), sayi(kesim["stok_mm"], 0))),
]
H.append("<div class='k'>" + "".join("<div class='kpi'><b>%s</b><span>%s</span></div>" % (a, esc(b)) for a, b in kpi) + "</div>")

H.append("<h2>Görünümler</h2><div class='grid'>")
for ad, cap, w in (("iskelet-omuzlar.png", "İskelet + sağ omuz + aynalı sol omuz (arayuz.py yerleşimi)", "wide"),
                   ("iskelet-izometrik.png", "İzometrik", ""), ("iskelet-on.png", "Önden (+Z'den bakış)", ""),
                   ("iskelet-yan.png", "Yandan (+X'ten bakış)", ""),
                   ("iskelet-omuzlar-on.png", "Önden: travers, omuz yuvaları ve direk-travers köşe bağlantıları", "wide"),
                   ("detay-direk-ray.png", "Direk dibi: köşe bağlantı (A ayağı orta ara rayda, B ayağı direkte), M6×16 + pul; arkada orta rayın iç köşe bağlantıları", ""),
                   ("detay-direk-travers.png", "Travers-direk: köşe bağlantı traversin alt yüzünde", ""),
                   ("detay-direk-ray-kesit.png", "Saydam profil: çekiç somunlar dudak altında, kamalar kanal ağzında", ""),
                   ("detay-sase-ic-kose.png", "Saydam profil: şase T birleşiminde iç köşe bağlantı ve set vidalar", ""),
                   ("iskelet-patlatilmis.png", "Patlatılmış montaj", ""),
                   ("iskelet-patlatilmis-taban.png", "Patlatılmış: direk dibi ve şase birleşimleri", "")):
    H.append("<figure class='%s'><img src='%s' alt='%s'><figcaption>%s</figcaption></figure>" % (w, img64(ad), esc(cap), esc(cap)))
H.append("</div>")

H.append("<h2>Hangi parça neye, nasıl bağlanıyor</h2><div class='tw'>")
H.append(tablo(["Bağlantı", "Nasıl oturuyor", "Bağlantı elemanı (toplam)", "Yer"], bag_satir))
H.append("</div><h3>Bağlantı oturma kontrolleri (her bağlantı ayrı)</h3><div class='tw'>")
H.append(tablo(["Bağlantı", "Tip", "Kontrol", "Ölçü", "Sonuç"], kont_satir))
H.append("</div><p class='not'>Köşe bağlantı kontrolleri: gövde iki profile dayalı (0,00 mm), çekiç somun dudak altına dayalı, cıvata ekseni "
         "somun deliğinde, pul ayağa dayalı, cıvata ucu somunu tam geçip kanal tabanına değmiyor. İç köşe: flanş iki profilin dudaklarına "
         "dayalı, set vida uçları kanal tabanında. Çakışma eşiği %s mm³.</p>" % sayi(d["tolerans_mm3"], 1))

H.append("<h2>Kararlar</h2><ul>" + "".join("<li>%s</li>" % esc(s) for s in KARAR) + "</ul>")

H.append("<h2>Omuz regresyonu (ortak kütüphane + arayüz bağlantısı)</h2>")
H.append("<p>Omuz betikleri genel elemanları artık <code>ortak_lib.py</code>'den, travers boyunu, yuva bölgesini ve dudak derinliğini "
         "<code>arayuz.py</code>'den okuyor; sigma kesiti <code>sigma_profil.py</code>'den geliyor. Değişiklikten önce ve sonra "
         "<code>omuz_montaj.py</code> çalıştırılıp karşılaştırıldı (<code>omuz/omuz_regresyon.py</code>):</p><div class='tw'>")
H.append(tablo(["Ölçüt", "Önce", "Sonra", "En büyük fark", "Sonuç"], reg_satir))
H.append("</div><p class='not'>Taramada çakışan pozlar omuzun kendi eklem sınırlarının dışında (yana −20…−5°) ve değişiklikten önce de "
         "aynıydı. Sonuç: <b>%s</b>.</p>" % ("birebir aynı" if r["hepsi_ayni"] else "fark var"))

H.append("<h2>Eğilme kontrolü: direk ve travers</h2>")
H.append("<p>Kesit (FreeCAD, sigma_profil kesiti): alan %s mm² (üretici %s), I = %s mm⁴, W = %s mm³. Direk %s mm, travers yarısı %s mm konsol.</p>" % (
    sayi(E["kesit"]["alan_mm2"]), sayi(E["kesit"]["uretici_alan_mm2"], 0), sayi(E["kesit"]["Ixx_mm4"], 0), sayi(E["kesit"]["W_mm3"], 0),
    sayi(A.DIREK_L), sayi(A.TRAVERS_L / 2 - A.SG / 2, 0)))
H.append("<div class='tw'>" + tablo(["Durum", "Mx N·m", "Mz N·m", "Direk σ MPa", "Direk tepe sehimi mm", "Travers σ MPa",
                                     "Travers uç sehimi mm", "Travers burulma N·m", "El ucu düşey mm"], eg_satir, "sayi") + "</div>")
H.append("<p><b>En kötü durum</b> (%s poz çifti tarandı, her kol öne 0…180°, yana 0…120°, 0,5 kg yüklü): direk σ = %s MPa (sağ kol öne %s° / yana %s°, sol kol öne %s° / yana %s°), "
         "tepe sehimi %s mm; travers σ = %s MPa. 6063 Rp0,2 ≈ %s MPa (tahmini) ile emniyet direkte ≈ %s×, traverste ≈ %s×. "
         "Direk sehimi %s, el ucu %s (sınırlar tahmini).</p>" % (
             sayi(ek["izgara_poz"], 0), sayi(ek["direk_sigma_MPa"], 2), ek["direk_poz"][0][0], ek["direk_poz"][0][1], ek["direk_poz"][1][0],
             ek["direk_poz"][1][1], sayi(ek["sehim_tepe_mm"], 3),
             sayi(ek["travers_sigma_MPa"], 2), sayi(A.SG_RP02, 0), sayi(son["direk_emniyet"], 0), sayi(son["travers_emniyet"], 0),
             "uygun (≤ %s mm)" % sayi(E["sinir"]["direk_mm"], 1) if son["direk_sehim_uygun"] else "<b>sınırı aşıyor</b>",
             "uygun (≤ %s mm, en çok %s mm)" % (sayi(E["sinir"]["el_mm"], 1), sayi(el_max, 2)) if son["el_uygun"] else "<b>sınırı aşıyor</b>"))
H.append("<p><b>Değerlendirme:</b> Profil kesiti bu yükler için çok güçlü; gerilme ve sehim ihmal edilebilir. Asıl esneklik bağlantılarda "
         "(aşağıda açık işler: cıvatalar X momentinin nötr ekseninde). Tasarım değiştirilmedi.</p>")
H.append("<h3>Varsayımlar</h3><ul>" + "".join("<li>%s</li>" % esc(v) for v in E["varsayim"]) + "</ul>")

H.append("<h2>Modüller arası çakışma (carpisma.py)</h2>")
H.append("<p>Modüller <code>arayuz.MODULLER</code> yerleşimiyle global koordinata kondu. Sol omuz sağ omuzun X aynası. Henüz çizilmemiş "
         "modüllerin ayrılmış bölgeleri (%d kutu: %s) de sabit engel olarak tarandı.</p><div class='tw'>" % (
             c["ayrilmis_bolge"]["sayi"], ", ".join(c["ayrilmis_bolge"]["sahipler"])))
H.append(tablo(["Modül", "Yerel orijin (global)", "Dönüş", "Parça", "Hareket", "Kontrol dışı (neden: aşağıda)"], mod_satir))
H.append("</div><ul><li>Arayüz uyumu: omuzun kendi traversi ile iskeletin traversi global koordinatta %s (ortak hacim = hacim, sınır kutusu farkı 0).</li>"
         % ("aynı" if all(u["ayni"] for u in c["arayuz_uyumu"]) else "<b>FARKLI</b>"))
H.append("<li>Kontrol dışı: %s.</li>" % esc(c["moduller"][1]["haric_neden"]))
H.append("<li>Ev pozu: <b>%d çakışma</b> (%d sınır kutusu kesişen çift gerçek kesişimle sınandı: yuva-travers, çekiç somunlar, köşe bağlantılar).</li></ul>"
         % (len(c["ev_pozu_cakisma"]), c["ev_pozu_kesisen_cift"]))
H.append("<div class='tw'>" + tablo(["Hareketli modül", "Poz", "Çakışan poz", "Eklem aralığında çakışan", "En küçük boşluk", "En yakın çift"], tar_satir) + "</div>")
H.append("<p>Toplam: <b>%d çakışma</b>. İskelet + iki omuz kütlesi %s kg, ağırlık merkezi (%s, %s, %s) mm. Tarama aralığı: %s.</p>" % (
    c["toplam"]["cakisma"], sayi(c["kutle_toplam_g"] / 1000, 2), sayi(c["agirlik_merkezi"][0], 1), sayi(c["agirlik_merkezi"][1], 0),
    sayi(c["agirlik_merkezi"][2], 1), esc(list(tarama.values())[0]["aciklama"])))

H.append("<h2>Kesim listesi ve malzeme</h2><div class='grid'><div>")
H.append(tablo(["Çubuk (%s mm, testere %s mm)" % (sayi(kesim["stok_mm"], 0), sayi(kesim["testere_mm"], 0)), "Kesilecek parçalar", "Artık"], cub_satir))
H.append("<p class='not'>Toplam %s mm sigma: modelde %s g, üretici 1,99 kg/m ile %s g. Robolink özel boy kesimi de yapıyor; o durumda bu tablo "
         "sipariş listesidir. 1. çubukta artık 3,5 mm: çubuk kısa gelirse 190 mm'lik parça 3. çubuğa alınır (artık 111 mm).</p></div><div>" % (sayi(kesim["toplam_mm"], 1), sayi(kesim["kutle_model_g"], 0), sayi(kesim["kutle_uretici_g"], 0)))
H.append(tablo(["Tür", "Kalem", "Adet", "Kütle g"], bom_satir, "sayi"))
H.append("</div></div>")

H.append("<h2>Ayrılmış bölgeler (arayuz.py)</h2><p>Sonraki modüllerin girmemesi gereken hacimler; iskelet bu bölgelerle %d ihlal verdi "
         "(taban ve kafa bölgeleri, %d kutu).</p><div class='tw'>" % (len(d["bolge"]["ihlal"]), d["bolge"]["kontrol_edilen"]))
H.append(tablo(["Sahip", "Bölge", "Global kutu (mm)", "Kaynak", "Not"], bol_satir))
H.append("</div>")

H.append("<h2>Açık işler ve varsayımlar</h2><ul>" + "".join("<li>%s</li>" % esc(s) for s in ACIK) + "</ul>")
H.append("<h2>Dosyalar</h2><ul>"
         "<li><code>iskelet-montaj.FCStd</code> (3 grup: şase, direk, travers) · <code>iskelet-montaj.step</code> (geri okuma: %d katı) · "
         "<code>iskelet-bom.csv</code> · <code>iskelet-analiz.json</code> · <code>gorsel/</code></li>"
         "<li><code>iskelet_parcalar.py</code> (parçalar) · <code>iskelet_montaj.py</code> (kontroller, eğilme, kayıt) · "
         "<code>iskelet_gorsel.py</code> · <code>iskelet_rapor.py</code> · <code>../carpisma.py</code> · <code>../arayuz.py</code> · "
         "<code>../ortak_lib.py</code></li></ul>" % d["step_kati"])
H.append("</main></body></html>")
open(os.path.join(HERE, "rapor.html"), "w", encoding="utf-8").write("\n".join(H))
print("rapor.html yazildi", os.path.getsize(os.path.join(HERE, "rapor.html")) // 1024, "kB")
