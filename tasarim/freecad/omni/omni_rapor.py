# On omni teker + gobek adaptoru raporu (rapor.html TASLAGI, gorseller gomulu). Sistem Python'u ile calisir (FreeCAD gerekmez).
# Girdiler: omni-kontrol.json (omni_kontrol.py), lastik-geri-donus.json (OMNI_KIP=lastik), gorsel/*.png (omni_gorsel.py), ../arayuz.py,
# ../taban/donus_hesap.py (yari statik donus el hesabi; saf Python). 2. asama (kontrol ajani, 23.11.2026): omni-dogrula*.json (omni_dogrula.py),
# eklem-dogrulama-asama2.json, ../taban/taban-analiz.json, ../montaj/montaj-analiz.json, ../carpisma-sonuc.json, omuz / iskelet regresyon
# fark.json, fizik olcumu planlama/d158/Y0f-olcum/donus-oneri.json; omni oncesi degerler git ONCE_REF'ten (git show, yalniz okuma).
import os, sys, json, base64, html, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (UST, os.path.join(UST, "taban")):
    sys.path.insert(0, _p)
import arayuz as A

G = os.path.join(HERE, "gorsel")
d = json.load(open(os.path.join(HERE, "omni-kontrol.json"), encoding="utf-8"))
O = A.TABAN["omni"]
Tm, Ad = O["tahmin"], O["adaptor"]
OL = d["olcu"]
M = d["merkez"]
B = d["bosluk"]


def esc(s):
    return html.escape(str(s))


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
    return ("−" if neg and s.strip("-0.,") else "") + ".".join(gr) + ("," + ond if ond else "")


def img64(ad):
    return "data:image/png;base64," + base64.b64encode(open(os.path.join(G, ad), "rb").read()).decode()


def tablo(baslik, satirlar, sinif=""):
    h = ["<div class='tw'><table class='%s'><tr>" % sinif + "".join("<th>%s</th>" % esc(b) for b in baslik) + "</tr>"]
    for s in satirlar:
        h.append("<tr>" + "".join("<td>%s</td>" % x for x in s) + "</tr>")
    h.append("</table></div>")
    return "".join(h)


def md(s):
    s = esc(s)
    out, b, c, i = [], False, False, 0
    while i < len(s):
        if s.startswith("**", i):
            out.append("</b>" if b else "<b>")
            b = not b
            i += 2
        elif s[i] == "`":
            out.append("</code>" if c else "<code>")
            c = not c
            i += 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def durum(ok):
    return "<span class='ok'>tamam</span>" if ok else "<span class='no'>sorun</span>"


TAH = "<span class='tah'>TAHMİN</span>"
OLC_ET = "<span class='olc'>ölçülen</span>"

sys.path.insert(0, HERE)
import omni_rapor_asama2 as A2
HUKUM_HTML, DONUS_HTML, ASAMA2_HTML = A2.uret(d, dict(sayi=sayi, esc=esc, md=md, tablo=tablo, durum=durum, TAH=TAH, OLC_ET=OLC_ET))

H = []
H.append("""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ön Omni Teker</title><style>
:root{--bg:#f6f4ef;--card:#fff;--ink:#1d1f22;--mut:#666;--line:#e3e0d8;--acc:#7b8794;--acc2:#2f86d4;--ok:#2e8b57;--no:#c0392b;--uy:#b7791f} @media (prefers-color-scheme:dark){:root{--bg:#16171a;--card:#202226;--ink:#ececec;--mut:#9a9a9a;--line:#33363b}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,Segoe UI,sans-serif}
main{max-width:1120px;margin:0 auto;padding:28px 16px 60px}
h1{font-size:28px;margin:0 0 4px}h2{font-size:19px;margin:34px 0 10px;border-bottom:2px solid var(--acc2);display:inline-block}
h3{font-size:16px;margin:18px 0 8px}.sub{color:var(--mut);margin-bottom:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
figure img{width:100%;display:block;background:#fff}figcaption{padding:8px 12px;color:var(--mut);font-size:13px}
.tw{overflow-x:auto}table{border-collapse:collapse;width:100%;background:var(--card);border-radius:10px;overflow:hidden;font-size:14px}
td,th{border-bottom:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}th{background:rgba(47,134,212,.12)}
.k{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi b{display:block;font-size:21px}.kpi span{color:var(--mut);font-size:13px}
ol li,ul li{margin:5px 0}code{background:rgba(127,127,127,.15);padding:1px 5px;border-radius:4px}
.ok{color:var(--ok);font-weight:600}.no{color:var(--no);font-weight:600}.uy{color:var(--uy);font-weight:600}.wide{grid-column:1/-1}
.not{color:var(--mut);font-size:13px}a{color:var(--acc2)}
.tah{background:rgba(183,121,31,.18);color:var(--uy);font-weight:700;font-size:12px;padding:1px 6px;border-radius:4px}
.olc{background:rgba(46,139,87,.15);color:var(--ok);font-weight:700;font-size:12px;padding:1px 6px;border-radius:4px}
.bos{border:2px dashed var(--line);border-radius:10px;padding:18px;color:var(--mut);background:var(--card)}
.uyari{border-left:4px solid var(--uy);background:var(--card);padding:10px 14px;border-radius:6px}
.karar{border-left:4px solid var(--ok);background:var(--card);padding:10px 14px;border-radius:6px}
</style></head><body><main>""")
H.append("<h1>Ön omni teker ve göbek adaptörü</h1>")
H.append("<div class='sub'>1. aşama (tasarım) + 2. aşama (bağımsız kontrol, resmî tarama, ana montaj, regresyon) · FreeCAD 1.1 · ön iki teker Nexus 127 mm "
         "çift sıra omni, arka iki teker lastik · ölçüler <code>arayuz.TABAN['omni']</code> ve <code>arayuz.OMNI_X</code> · 2. aşamanın hükmü ve sayıları "
         "<a href='#asama2'>aşağıda</a></div>")
H.append(HUKUM_HTML)
H.append("<div class='karar'><b>Karar (Ahmet, 23.11.2026; K75):</b> ön iki teker omni, arka iki teker, arka motorlar ve arka enkoderler aynen kalır. "
         "Teker: Nexus 14073 (rulmanlı makara; 14075 aynı dış ölçü), Ø127 × 29 mm, 2 sıra × 11 = 22 makara, 480 g, yük 30 kg. Teker merkezi motor mili ve "
         "kaplinin oturma düzleminin geometrik sonucu; Nexus göbeği (6 mm delik) yerine 12 mm altıgen kapline uyan PETG adaptör.</div>")

bag = d["baglanti"]
kpi = [
    ("%s mm" % sayi(M["omni_x"], 1), "ön omni merkezi x (lastik %s): %s mm içeri · beklenti 14,5, fark %s" % (sayi(M["lastik_x"], 0), sayi(M["iceri_mm"], 1), sayi(M["fark_iceri"], 1))),
    ("%s / %s mm" % (sayi(M["on_iz"], 0), sayi(M["arka_iz"], 0)), "ön iz / arka iz · ön iz %s mm daralır (beklenti 29, fark %s)" % (sayi(M["arka_iz"] - M["on_iz"], 0), sayi(M["fark_daralma"], 1))),
    ("%d / %d" % (d["baglanti_tamam"], len(bag)), "bağlantı kontrolü (dayanma, eksen hizası, diş / insert kavraması), iki ön köşe"),
    ("%d" % len(d["yeni_x_taban"]["cakisma"]), "yeni parçalar × taban parçaları çakışma (%d çift, > 0,5 mm³)" % d["yeni_x_taban"]["cift"]),
    ("%s mm" % sayi(B["yon"]["on (+z, aks yuksekliginde)"]["bosluk_mm"], 1), "teker ↔ etek önde (lastikte %s) · yanda %s mm (lastikte %s)" % (
        sayi(B["lastik_karsilastirma"]["on_mm"], 1), sayi(B["yon"]["yan (+x, teker dis yuzunden, aks yuksekliginde)"]["bosluk_mm"], 1), sayi(B["lastik_karsilastirma"]["yan_mm"], 1))),
    ("%s mm" % sayi(B["ic_yuz"]["flans_m3_bas_bosluk"], 1), "adaptör flanşı ↔ motor M3 cıvata başları (en yakın statik parça; braket %s mm)" % sayi(B["ic_yuz"]["flans_braket_bosluk"], 1)),
    ("%s mm" % sayi(OL["zemin_y"], 1), "omni alt noktası, aks 62,5 sabit (Ø127 > Ø125): gerçekte ön uç 1 mm yükselir"),
    ("%s g · %s sa" % (sayi(d["baski"]["filament_g"], 1), sayi(d["baski"]["sure_saat"], 2)), "adaptör baskısı (tek parça, PETG, desteksiz %s, X2D'ye sığar %s)" % (
        "evet" if d["baski"]["desteksiz"] else "hayır", "evet" if d["baski"]["sigar"] else "hayır")),
    ("+%s g" % sayi(d["kutle"]["on_iki_kose_fark_g"], 0), "ön iki köşe kütle farkı (omni + adaptör + cıvatalar − iki lastik teker)"),
]
H.append("<div class='k'>" + "".join("<div class='kpi'><b>%s</b><span>%s</span></div>" % (a, esc(b)) for a, b in kpi) + "</div>")

GOR = [("omni-izometrik.png", "Sağ ön köşe: omni + adaptör, etek yarı saydam"), ("omni-kesit.png", "Kesit, aks düzlemi (z 185): mil → kaplin → adaptörün altıgen yuvası → göğüs + M4×16; pilot teker göbek deliğinde"),
       ("omni-kesit-ceyrek.png", "Kesit, çeyrek bakış"), ("omni-on.png", "Önden: iki ön omni, sonarlar, etek (yarı saydam)"),
       ("omni-yan.png", "Yandan: ön omni (Ø127 × 29) ve arka lastik (Ø125 × 58)"), ("omni-teker-dis.png", "Teker dış yüzü: 4× M3×35 + pul, göbek deliğinde M4×16, fıçı makaralar"),
       ("omni-adaptor-dis.png", "Teker gizli: adaptör (pilot, flanşta 4 ısıl gömme somun), kaplin, braket"), ("omni-adaptor-motor.png", "Adaptör flanşı ↔ braket / motor M3 başları"),
       ("omni-patlatilmis.png", "Patlatılmış: motor, braket, kaplin, adaptör + somunlar, teker, M4 ve 4× M3")]
H.append("<h2>Görseller</h2><div class='grid'>" + "".join("<figure><img src='%s' alt='%s'><figcaption>%s</figcaption></figure>" % (img64(a), esc(c), esc(c))
                                                         for a, c in GOR if os.path.exists(os.path.join(G, a))) + "</div>")

# --- merkez zinciri
H.append("<h2>Teker merkezi: kaplin oturma düzleminden</h2>")
H.append("<p>Mil ve kaplin değişmez. Adaptör lastik tekerin göbeğini taklit eder: altıgen yuvası kaplini 17,5 mm'den fazla kavrar, kaplin ucu adaptörün göğsüne "
         "(6 mm) dayanır, aynı M4×16 + pul. Adaptörün teker oturma yüzü kaplin ucundan 17,5 mm içeride, yani lastik tekerin iç yüzünde. Merkez bundan çıkar. "
         "Aşağıdaki x değerleri CAD'den okundu (sağ ön köşe, mm; sol köşe ayna).</p>")
zr = [["Motor mili ucu (Ø6 D, CAD boyu 15 mm tahmini)", sayi(M["cad_mil_ucu_x"], 1), OLC_ET + " CAD"],
      ["Kaplin teker tarafı ucu = oturma düzlemi", sayi(M["cad_kaplin_ucu_x"], 1), OLC_ET + " CAD (171 + 1,5 + 2 + 30)"],
      ["Adaptör flanşı motor yüzü", sayi(M["cad_adaptor_x"][0], 1), OLC_ET + " CAD"],
      ["Omni iç yüzü = adaptör oturma yüzü (lastik iç yüzü 187)", sayi(M["cad_teker_ic_yuz_x"], 1), OLC_ET + " CAD (kaplin ucu − 17,5)"],
      ["<b>Omni merkezi</b> (lastik 216)", "<b>%s</b>" % sayi(M["cad_teker_merkez_x"], 1), OLC_ET + " CAD; <code>arayuz.OMNI_X</code>"],
      ["Adaptör göğsü dış yüzü (M4 pulu)", sayi(OL["gogus_dis_x"], 1), "lastik tekerin göğsüyle aynı"],
      ["M4×16 başı dış yüzü (göbek deliğinin içinde)", sayi(OL["m4_bas_dis_x"], 1), "teker dış yüzünün %s mm içinde" % sayi(OL["teker_dis_yuz_x"] - OL["m4_bas_dis_x"], 1)],
      ["Omni dış yüzü", sayi(M["cad_teker_dis_yuz_x"], 1), OLC_ET + " CAD"],
      ["M3 cıvata başı dış yüzü (en dış nokta)", sayi(OL["m3_bas_dis_x"], 1), "göbek kalınlığı " + TAH]]
H.append(tablo(["Nokta", "x (mm)", "Kaynak"], zr))
H.append("<p><b>Sonuç:</b> merkez %s mm içeri, ön iz %s → %s mm (%s mm daralır). Beklentiyle (14,5 / 29) fark <b>%s / %s mm</b>. Tek değer: "
         "<code>arayuz.OMNI_X</code> (<code>kaplin_ucu_x − kavrama + en / 2</code>); <code>taban_lib.omni_local()</code>, <code>taban_parcalar</code> ve "
         "<code>taban/donus_hesap.py</code> bunu okur, <code>taban_lib</code> zinciri assert ile denetler. Eski çelişki (yorum \"merkez içeri kayar\", kod "
         "\"aynı merkez + 14,5 mm adaptör\") kalktı.</p>" % (
             sayi(M["iceri_mm"], 1), sayi(M["arka_iz"], 0), sayi(M["on_iz"], 0), sayi(M["arka_iz"] - M["on_iz"], 0), sayi(M["fark_iceri"], 1), sayi(M["fark_daralma"], 1)))

# --- adaptor
H.append("<h2>Göbek adaptörü</h2>")
H.append("<p>Tek parça PETG baskı, iki adet (sağ ve sol aynı parça). Tork altıgenden (12 mm altıgen kaplin, yuva %s mm anahtar ağzı), teker 4× M3 ile flanştaki ısıl gömme "
         "somunlara, merkezleme pilotun teker göbek deliğine girmesiyle. Nexus göbeği 18007 alınmaz. Parametreler <code>arayuz.TABAN['omni']['adaptor']</code>, "
         "ürüne bağlı ölçüler tek yerde <code>arayuz.TABAN['omni']['tahmin']</code>; değer değişince adaptör ve teker oradan yeniden üretilir.</p>" % sayi(12.0 + Ad["altigen_pay"], 1))
ar = [["Flanş", "Ø%s × %s" % (sayi(Ad["flans_d"], 0), sayi(Ad["flans_t"], 0)), "tasarım"],
      ["Pilot (göbek deliğine)", "Ø%s, flanştan %s mm" % (sayi(OL["pilot_d"], 1), sayi(OL["gogus_dis_x"] - OL["teker_ic_yuz_x"], 1)), "göbek deliği " + TAH + " − %s boşluk" % sayi(Ad["pilot_bosluk"], 1)],
      ["Altıgen yuva", "%s mm AA, kaplini %s mm kavrar" % (sayi(12.0 + Ad["altigen_pay"], 1), sayi(OL["kaplin_kavrama"], 1)), "lastik tekerde 17,5"],
      ["Pilot et kalınlığı (altıgen köşesinden)", "%s mm" % sayi(OL["pilot_et"], 2), "göbek deliği " + TAH],
      ["Göğüs + M4 deliği", "%s mm, Ø%s" % (sayi(Ad["gogus"], 0), sayi(Ad["m4_delik"], 1)), "lastik tekerle aynı"],
      ["Isıl gömme somun", "4× M3 (Ø4,0 delik × 6,2), flanş tabanı %s mm" % sayi(OL["insert_taban"], 1), "PCD " + TAH],
      ["Flanş kenarına et (insert deliği)", "%s mm" % sayi(OL["flans_et_insert"], 1), "PCD " + TAH],
      ["Kaplinin açıkta kalan boyu (braket ↔ flanş)", "%s mm" % sayi(OL["kaplin_acik"], 1), "set vidasına erişim"],
      ["Kütle", "%s g / adet" % sayi(d["baski"]["kutle_g"], 1), "PETG %%%d doluluk kabulü" % 80]]
H.append(tablo(["Öğe", "Değer", "Not"], ar))

H.append("<h3>Ölçülen ile TAHMİN ayrımı</h3>")
olc_r = [["Teker çapı, genişlik", "Ø127 × 29 mm", "ürün sayfası (14073 / 14075)"], ["Makara", "2 sıra × 11 = 22, Ø19, kauçuk", "ürün sayfası"],
         ["Kütle, yük", "480 g, 30 kg", "ürün sayfası"], ["Kaplin, mil, braket, M4×16", "CAD'deki mevcut değerler (değişmedi)", "taban_lib (mil boyu 15 mm CAD tahmini, lastikle ortak)"],
         ["Teker merkezi zinciri", "yukarıdaki tablo", "CAD'den okundu"]]
H.append(tablo(["Ölçü", "Değer", "Kaynak"], olc_r))
TAH_AD = {"gobek_delik_d": "Teker merkez (göbek) deliği çapı", "pcd": "Göbek cıvata dairesi (PCD)", "civata_n": "Göbek cıvata adedi",
          "civata_d": "Göbek cıvata dış çapı (M)", "civata_aci0": "İlk cıvata açısı (°)", "gobek_t": "Cıvatanın geçtiği göbek kalınlığı",
          "govde_r": "Alüminyum gövde yarıçapı (gösterim)", "makara_boy": "Makara boyu", "sira_ofset": "Makara sırası ekseni ± (orta düzlemden)"}
H.append(tablo(["TAHMİN (satıcı çiziminden doğrulanmadı)", "Değer", "Etkilediği"],
               [[esc(TAH_AD.get(k, k)), sayi(v, 1) if isinstance(v, float) else esc(v), {"gobek_delik_d": "pilot çapı, M4 başına erişim",
                                                                                         "pcd": "insert yeri, flanş eti", "civata_n": "M3 adedi",
                                                                                         "civata_d": "insert ve vida", "civata_aci0": "delik yeri",
                                                                                         "gobek_t": "M3 boyu (35)", "govde_r": "yalnız görsel",
                                                                                         "makara_boy": "görsel, boşluk", "sira_ofset": "görsel"}.get(k, "")]
                for k, v in Tm.items()]))

# --- baglantilar
H.append("<h2>Bağlantılar (ön iki köşe)</h2>")
br = []
for s in bag:
    o = s["olcu"]
    ol = ", ".join("%s %s" % (k, v) for k, v in o.items())
    br.append([esc(s["ad"]), esc(s["tip"]), esc(ol), esc(", ".join(str(x) for x in s.get("temas_mm", []))), esc(", ".join(str(x) for x in (s.get("eksen_mm") or []))),
               durum(s["tamam"]), esc(s["aciklama"])])
H.append(tablo(["Bağlantı", "Tip", "Ölçü (mm)", "Dayanma (mm)", "Eksen sapması (mm)", "Durum", "Açıklama"], br))
H.append("<p class='not'>Ölçüt <code>taban_montaj.py</code> ile aynı: dayanma ≤ 0,01 mm, eksen sapması ≤ 0,0001 mm, diş kavraması ≥ d ve ≤ delik − 0,5, insert "
         "kavraması ≥ d ve ≤ insert boyu + 2,5. M3 kavraması (5,5 mm) göbek kalınlığı TAHMİN'ine bağlı.</p>")

# --- parca listesi
H.append("<h2>Parça listesi (robot başına değişim)</h2>")
H.append(tablo(["Değişim", "Tür", "Kalem", "Malzeme", "Adet", "Toplam kütle (g)"],
               [[esc(b["degisim"]), esc(b["tur"]), esc(b["kalem"]), esc(b["malzeme"]), str(b["adet"]), "" if b["kutle_g"] is None else sayi(b["kutle_g"], 1)] for b in d["bom"]]))
H.append("<p class='not'>Dosya: <code>omni-bom.csv</code>. <code>planlama/maliyet.json</code> değiştirilmedi (satır 133 hâlâ \"K1 seçeneği, Nexus 14075, koşullu\").</p>")

# --- baski
bs = d["baski"]
H.append("<h2>Baskı tablosu</h2>")
H.append(tablo(["Parça", "Adet", "Malzeme", "Yön", "Destek", "Ölçü (mm)", "Süre / adet", "Filament / adet", "Not"],
               [[esc("Omni göbek adaptörü"), "2", esc(Ad["malzeme"]), esc(bs["yon"]),
                 "yok (desteksiz: %s; çıkıntı oranı %s, sorunlu katman %d)" % ("evet" if bs["desteksiz"] else "hayır", sayi(bs["cikinti_orani"], 3), bs["destek_sorun_sayi"]),
                 esc(" × ".join(sayi(x, 1) for x in bs["olcu"])), "%s sa" % sayi(bs["sure_saat"], 2), "%s g" % sayi(bs["filament_g"], 1),
                 "Göğüs, altıgen yuvanın tavanı: 12,1 mm köprü (≤ 15 desteksiz). 5 duvar, %40+ dolgu önerilir; ısıl gömme somunlar teker yüzünden. "
                 "STL: <code>stl/omni-gobek-adaptoru.stl</code> (baskı yönünde)"]]))
H.append("<p class='not'>İmalat seçeneği (karar değil): aynı geometri 6061 alüminyumdan tornalanabilir (altıgen yuva tel erozyon ya da broş; M3 delikleri diş açılır, insert kalkar). "
         "PETG'de sürünme ve altıgen ezilmesi ilk denemede gözlenmeli: durma torku 21 kg·cm (2,1 N·m, tahmini) altıgen yüzlerine taşınır.</p>")

# --- bosluklar
H.append("<h2>Teker çevresi açıklıkları (1. aşama, dönen zarf; 2. aşama ölçümü aşağıda)</h2>")
H.append("<p>Dönen zarf: her yeni dönen parça (omni, adaptör, M4, M3, pullar, somunlar) eksen etrafında süpürdüğü halka olarak alındı; statik parçalara "
         "uzaklık bu zarftan ölçüldü (dönüş konumundan bağımsız). Kabuk ve iskelet kendi STEP dosyalarından (%s; %s), taban parçaları <code>taban_parcalar</code>'dan.</p>" % (
             esc(B["kaynak"]["kabuk"]), esc(B["kaynak"]["iskelet"])))
YON_AD = {"yan (+x, teker dis yuzunden, aks yuksekliginde)": "Yan, dışa (+x): teker dış yüzünden, aks yüksekliğinde",
          "yan (+x, M3 basi dis yuzunden)": "Yan, dışa (+x): M3 başının dış yüzünden",
          "on (+z, aks yuksekliginde)": "Ön (+z): teker önünden, aks yüksekliğinde",
          "ust (+y, teker tepesinden)": "Yukarı (+y): teker tepesinden",
          "ic (-x, teker ic yuzunden, aks ustu 45)": "İçe (−x): teker iç yüzünden, aksın 45 mm üstü"}
yr = []
for k, v in B["yon"].items():
    yr.append([esc(YON_AD.get(k, k)), "—" if v is None else sayi(v["bosluk_mm"], 1), "—" if v is None else esc(v["parca"])])
H.append(tablo(["Işın (sağ ön teker)", "Boşluk (mm)", "İlk değdiği"], yr))
H.append("<p class='not'>Lastik ön tekerle (analitik): yanda %s mm, önde %s mm. Omni dar olduğu için yanda %s mm açıklık kaldı; ön boşluk çap farkı kadar azaldı (yarıçap +1 mm).</p>" % (
    sayi(B["lastik_karsilastirma"]["yan_mm"], 1), sayi(B["lastik_karsilastirma"]["on_mm"], 1), sayi(B["yon"]["yan (+x, teker dis yuzunden, aks yuksekliginde)"]["bosluk_mm"], 1)))
ty = [[esc(t["parca"]), sayi(t["bosluk_mm"], 2), esc(t["nokta_teker"]), esc(t["nokta_diger"])] for t in B["taban_zarf"][:8]]
ty += [[esc(t["parca"]), sayi(t["bosluk_mm"], 2), esc(t["nokta_teker"]), esc(t["nokta_diger"])] for t in B["etek_zarf"][:3]]
ty += [[esc(t["parca"]), sayi(t["bosluk_mm"], 2), esc(t["nokta_teker"]), esc(t["nokta_diger"])] for t in B["iskelet_zarf"][:2]]
H.append(tablo(["En yakın statik parçalar (zarftan)", "Boşluk (mm)", "Zarf noktası", "Parça noktası"], ty))
H.append("<ul>" + "".join("<li>%s</li>" % md(s) for s in [
    "**Motor JGB37 %s mm:** mil ucu (Ø6, x ≤ 186) ile adaptörün altıgen yuvası arası; aralarında kaplin var, gerçek bir boşluk değil. Motor gövdesine en yakın nokta M3 başları." % sayi(B["taban_zarf"][0]["bosluk_mm"], 2) if B["taban_zarf"] and B["taban_zarf"][0]["parca"].startswith("Motor") else "",
    "**Motor M3×6 başları %s mm** (braket iç yüzünde, x 175,5): en yakın gerçek boşluk; flanş 1 mm kalınlaşırsa 2,5 mm kalır. Alt plaka köşesine %s mm, braket plakasına %s mm." % (
        sayi(B["ic_yuz"]["flans_m3_bas_bosluk"], 1), sayi(next((t["bosluk_mm"] for t in B["taban_zarf"] if t["parca"] == "Alt plaka"), float("nan")), 2), sayi(B["ic_yuz"]["flans_braket_bosluk"], 1)),
    ("**Ön sensörler:** en yakın %s, zarftan %s mm (sağ ön teker; sol ayna). Sonar ışın konisi ile teker ilişkisi ölçülmedi." % (
        B["sensor"][0]["parca"], sayi(B["sensor"][0]["bosluk_mm"], 1)) if B.get("sensor") else "**Ön sensörler:** ölçülmedi."),
    "**Zemin:** aks yüksekliği 62,5 ortak (motor braketi); Ø127 omni CAD'de zeminin %s mm altına iner (CAD alt noktası y %s). Gerçekte ön uç %s mm yükselir, "
    "eğim ≈ %s° (fizik modeli ONERI-ADAY ile aynı kabul); çakışma taramasında zemin parça değil." % (
        sayi(-OL["zemin_y"], 1), sayi(B["zemin"]["teker_alt_y"], 2), sayi(-OL["zemin_y"], 1), sayi(__import__("math").degrees(__import__("math").atan(-OL["zemin_y"] / 370.0)), 2)),
    "**Yeni parçalar × kabuk / iskelet çakışma:** %d / %d." % (len(B["kabuk_cakisma"]), len(B["iskelet_cakisma"]))] if s) + "</ul>")

# --- donus: el hesabi ve fizik modeli (2. asama, madde 7)
H.append(DONUS_HTML)

# --- olculecekler
H.append("<h2 id='olculecek'>Sipariş öncesi ölçülecekler / sorulacaklar</h2><ol>" + "".join("<li>%s</li>" % esc(s) for s in O["olculecek"]) + "</ol>")
H.append("<p class='not'>Ölçüler gelince yalnız <code>arayuz.TABAN['omni']['tahmin']</code> güncellenir, <code>omni_kontrol.py</code> → <code>omni_gorsel.py</code> → <code>omni_rapor.py</code> "
         "yeniden koşulur. Göbek deliği pilotun alt sınırından (altıgen köşe Ø%s + 2 × 2,5 et ≈ Ø%s) küçük çıkarsa bu yerleşim olmaz: adaptör flanşı tekerin dışına "
         "alınır, merkez dışarı kayar (yeniden tasarım).</p>" % (sayi(2 * (12.1 / 3 ** 0.5), 1), sayi(2 * (12.1 / 3 ** 0.5) + 5, 1)))

# --- geri donus
gd = d.get("geri_donus")
H.append("<h2>Lastik ön teker seçeneği (geri dönüş)</h2>")
if gd:
    H.append("<p><code>TABAN_OMNI=0</code> (ya da <code>arayuz.TABAN['omni']['aktif'] = False</code>) ile taban bugünkü dört lastik tekerle kurulur. Denendi: "
             "%d parça (%d gerçek), %d bağlantı, %s g, ön tekerler %s, geçersiz %d. Commit'teki <code>taban/taban-analiz.json</code> (lastik) ile aynı sayılar: 414 gerçek + 13 referans, "
             "148 bağlantı, 8.272,5 g.</p>" % (gd["parca"], gd["gercek"], gd["baglanti"], sayi(gd["toplam_kutle_g"], 1), esc(", ".join(gd["on_tekerler"])), len(gd["gecersiz"])))
else:
    H.append("<p class='not'>lastik-geri-donus.json yok (OMNI_KIP=lastik koşulmadı).</p>")

# --- 2. asama
H.append(ASAMA2_HTML)

H.append("<h2>Dosyalar</h2><ul>"
         "<li><code>../arayuz.py</code>: <code>TABAN['omni']</code> (aktif, ürün, kaplin_ucu_x, kavrama, adaptor, tahmin, olculecek), <code>OMNI_AKTIF</code>, <code>OMNI_X</code>, <code>ON_IZ</code>, <code>ARKA_IZ</code></li>"
         "<li><code>../taban/taban_lib.py</code>: <code>omni_local()</code> (fıçı makaralı teker), <code>omni_adaptor_local()</code>, <code>omni_olcu()</code>; zincir assert'leri</li>"
         "<li><code>../taban/taban_parcalar.py</code>: ön köşelerde omni + adaptör + 4× M3 + ısıl gömme somun, bağlantılar, baskı listesi, <code>TEKER_DONEN</code>, <code>OMNI_I</code></li>"
         "<li><code>../taban/donus_hesap.py</code>: <code>X_OMNI = arayuz.OMNI_X</code>; 2. aşamada Model C (motor hız-tork eğrisi) eklendi</li>"
         "<li><code>../taban/taban_montaj.py</code>: yamuk destek çokgeni (ön x OMNI_X, arka x 216), duruş eğimi; <code>../montaj/moduller.py</code>: teker grubu <code>TEKER_DONEN</code>'den</li>"
         "<li><code>omni_dogrula.py</code> (2. aşama bağımsız doğrulama) → <code>omni-dogrula.json</code>, <code>OMNI_KIP=lastik</code> → <code>omni-dogrula-lastik.json</code>; "
         "<code>eklem-dogrulama-asama2.json</code> (ana montaj eklem doğrulaması, kafa yön denetimi atlanarak; bkz. 2. aşama)</li>"
         "<li><code>omni_kontrol.py</code> → <code>omni-kontrol.json</code>, <code>omni-bom.csv</code>, <code>omni-montaj.FCStd</code>, <code>omni-on-teker.step</code>, <code>stl/</code>; "
         "<code>OMNI_KIP=lastik</code> → <code>lastik-geri-donus.json</code></li>"
         "<li><code>omni_gorsel.py</code> (FreeCAD GUI) → <code>gorsel/</code>; <code>omni_rapor.py</code> → bu sayfa</li></ul>")
H.append("<p class='not'>Üretildi: omni_rapor.py · 1. aşama kontrol süresi %s s · 2. aşama 23.11.2026</p>" % sayi(d["sure_s"], 1))
H.append("</main></body></html>")
open(os.path.join(HERE, "rapor.html"), "w", encoding="utf-8").write("\n".join(H))
print("rapor.html", round(os.path.getsize(os.path.join(HERE, "rapor.html")) / 1024), "KB")
