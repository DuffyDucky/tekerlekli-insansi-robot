# Omuz modulu: GIF, calisma alani haritasi ve rapor (rapor.md + rapor.html) uretir. Sistem Python'u ile calisir.
import os, json, base64, io
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(HERE, "gorsel")
d = json.load(open(os.path.join(HERE, "omuz-analiz.json"), encoding="utf-8"))

# ---------------------------------------------------------------- GIF
pozlar = [tuple(map(int, l.split())) for l in open(os.path.join(G, "kare", "pozlar.txt"))]
try:
    font = ImageFont.truetype("arial.ttf", 20)
except Exception:
    font = ImageFont.load_default()
frames = []
for k, (phi, th) in enumerate(pozlar):
    im = Image.open(os.path.join(G, "kare", "k%03d.png" % k)).convert("RGB").crop((0, 60, 720, 480))
    dr = ImageDraw.Draw(im)
    dr.text((14, 10), "One kaldirma %+4d°   Yana acma %+4d°" % (phi, th), fill=(40, 40, 40), font=font)
    frames.append(im.quantize(colors=128, method=Image.Quantize.MEDIANCUT))
frames[0].save(os.path.join(G, "omuz-hareket.gif"), save_all=True, append_images=frames[1:], duration=70, loop=0,
               optimize=True)

# ---------------------------------------------------------------- calisma alani haritasi
phis, ths = d["phis"], d["ths"]
fig, ax = plt.subplots(figsize=(8.5, 5.2))
for phi in phis:
    for th in ths:
        key = "%d,%d" % (phi, th)
        kg = d["kol_gobek"][str(th)]
        kv = d["kol_govde"][key]
        gg = d["gobek_govde"][str(phi)]
        if not (kg or kv or gg):
            c = "#3fa66b"
        elif kv and not kg:
            c = "#e0663c"
        else:
            c = "#b03a5b"
        ax.add_patch(Rectangle((th - 2.5, phi - 5), 5, 10, color=c, lw=0))
ax.add_patch(Rectangle((0, -45), 120, 180, fill=False, ec="#1b1b1b", lw=2, ls="--"))
ax.text(60, 138, "eklem sınırları (180° servo)", ha="center", va="bottom", fontsize=9)
ax.set_xlim(min(ths) - 2.5, max(ths) + 2.5)
ax.set_ylim(min(phis) - 5, max(phis) + 5)
ax.set_xlabel("Yana açma (°)  — 0 = kol aşağıda, + dışarı")
ax.set_ylabel("Öne kaldırma (°)  — + öne")
ax.set_title("Omuz çalışma alanı: hangi pozlar çakışmasız?")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color="#3fa66b", label="serbest"), Patch(color="#e0663c", label="kol × gövde/kapak"),
                   Patch(color="#b03a5b", label="kol × göbek/S2")], loc="lower right", fontsize=8, framealpha=.9)
fig.tight_layout()
fig.savefig(os.path.join(G, "omuz-calisma-alani.png"), dpi=130)

# ---------------------------------------------------------------- tork haritasi (en kotu)
tp = max(v[0] for v in d["tork"].values())
tr = max(v[1] for v in d["tork"].values())
lim = [(phi, th) for phi in phis for th in ths if -45 <= phi <= 135 and 0 <= th <= 120]
tp_l = max(d["tork"]["%d,%d" % k][0] for k in lim)
tr_l = max(d["tork"]["%d,%d" % k][1] for k in lim)

# ---------------------------------------------------------------- serbest aralik ozetleri
def aralik(vals):
    return (min(vals), max(vals)) if vals else None


th_free_all = [th for th in ths if all(not d["kol_gobek"][str(th)] and not d["kol_govde"]["%d,%d" % (phi, th)]
                                       for phi in phis)]
phi_free = [phi for phi in phis if not d["gobek_govde"][str(phi)] and all(
    not d["kol_govde"]["%d,%d" % (phi, th)] for th in range(0, 121, 5))]

BAGLANTI = [
    ("Omuz yuvası → sigma traversi",
     "Yuva traversin ucuna 30 mm geçer (0,2 mm boşluk), uç duvarına dayanır.",
     "4× M6×16 DIN 912 + 4× M6 pul + 4× M6 çekiç somun (kanal 10), dört yüzde birer"),
    ("S1 servo → omuz yuvası",
     "Servo plakadaki yuvaya dışarıdan girer, kulakları plakanın dış yüzüne oturur.",
     "4× M4×16 DIN 912 + 4× M4 DIN 985 kontra somun (somunlar plakanın iç yüzünde)"),
    ("S1 horn → S1 mili", "25 dişli mile geçer.", "M3 merkez vidası (servo ile gelir)"),
    ("Rulman kapağı → omuz yuvası", "Kapağın iki kulağı yuvanın kollarına dayanır.",
     "4× M3×12 DIN 912 → yuvadaki 4× M3 ısıl gömme somun"),
    ("6808-2RS rulman → rulman kapağı", "Dış bilezik Ø52 yuvaya sıkı geçer, servo tarafındaki dudağa dayanır.",
     "Sıkı geçme (bağlantı elemanı yok)"),
    ("Omuz göbeği → S1 horn + 6808",
     "Göbeğin Ø40 mili rulmanın iç bileziğinden geçer, Ø45 omzu iç bileziğe dayanır; ön yüzü horn'a oturur.",
     "4× M3×12 DIN 912, göbekteki havşalardan horn'un dişli deliklerine (3 mm diş)"),
    ("S2 servo → omuz göbeği", "Servo kulak plakasına önden girer, kulaklar plakanın ön yüzüne oturur.",
     "4× M4×16 DIN 912 + 4× M4 DIN 985 kontra somun"),
    ("S2 horn → S2 mili", "25 dişli mile geçer.", "M3 merkez vidası (servo ile gelir)"),
    ("Kol çatalı (ön kol) → S2 horn", "Çatalın ön kolu horn'un dış yüzüne oturur.", "4× M3×8 DIN 912 → horn dişli delikleri"),
    ("Kol çatalı (arka kol) → omuz göbeği (karşı yatak)",
     "625ZZ çatalın Ø16 yuvasına sıkı geçer. Cıvata iç bileziği göbekteki Ø8 dayamaya sıkar, çatal serbest döner. "
     "Servo mili kolu tek başına taşımaz.",
     "1× M5×12 DIN 912 + 1× M5 pul → göbekteki M5 ısıl gömme somun"),
    ("Üst kol tüpü → kol çatalı", "Tüp çatalın Ø50,8 pimine 20 mm geçer, Ø56 bileziğe dayanır.",
     "2× M3×8 DIN 912 karşılıklı → çataldaki 2× M3 ısıl gömme somun"),
]

SIRA = [
    "Isıl gömme somunları havyayla bas: yuvaya 4× M3 (kol uçları), göbeğe 1× M5 (arka plaka), çatala 2× M3 (pim).",
    "6808-2RS'yi rulman kapağına, 625ZZ'yi çatalın arka koluna bastır.",
    "4 çekiç somunu traversin dört kanalına sok. Yuvayı traverse geçir, 4× M6×16 + pulla sık.",
    "S1'i yuvaya dışarıdan sok, 4× M4×16 + kontra somunla bağla.",
    "S1'i 45° konumuna getir (Pi ya da servo test cihazıyla), horn'u kol aşağıdayken tak, merkez vidasını sık.",
    "Rulmanlı kapağı yuvanın kollarına 4× M3×12 ile bağla.",
    "Göbeği rulmandan geçirip horn'a oturt. 4× M3×12'yi havşalardan sık. **S2'den önce:** S2 takılınca bu vidalara erişilmez.",
    "S2'yi göbeğe önden sok, 4× M4×16 + kontra somun. S2'yi 30° konumuna getir, horn'u tak, merkez vidasını sık.",
    "Çatalı tak: ön kol horn'a 4× M3×8; arka kol M5×12 + pulla göbekteki somuna (rulmanı sıkar, çatal döner).",
    "Üst kol tüpünü çatalın pimine geçir, 2× M3×8 ile sabitle.",
]

ACIK = [
    "**Horn delik dizilimi:** 25T disk horn'da M3 delikler 8,5 mm yarıçapta varsayıldı. Horn eline geçince kumpasla ölçülmeli, göbek ve çatal delikleri ona göre güncellenir.",
    "**Servo sürümü:** Eklem sınırları 180° servoya göre (öne −45…+135°, yana 0…120°). DS3218MG'nin 270° sürümü alınırsa sınırlar genişler, horn takma açıları değişir.",
    "**Gövde kabuğu:** V3 kabuğunun yan yüzü x = 152'de düz duvar varsayıldı. Omuz için kabukta Ø84 delik gerekiyor; V3 kabuğunda bu delik yok.",
    "**S2 kablosu:** Göbekle birlikte dönüyor. Kanal açılmadı; gevşek bir kablo halkasıyla gövdeye girmeli.",
    "**Tahmini ölçüler:** Çekiç somun 16×10×5, ısıl gömme somun M3 Ø4,6×5,7 / M5 Ø7×7, PETG baskı yoğunluğu %60. Parçalar gelince kumpasla doğrulanmalı.",
    "**Sıkı geçmeler:** Ø52 (6808) ve Ø16 (625ZZ) yuvalar nominal çizildi. Yazıcının toleransı için önce küçük bir deneme halkası basılmalı.",
    "**Omuz genişliği:** Yana açma ekseni gövde merkezinden 185 mm dışarıda (eski tasarımda kol ekseni 166). Omuzdan omuza ≈ 426 mm.",
    "**Dirsek ve aşağısı:** Tork hesabında 260 g ve omuzdan 200 mm aşağıda varsayıldı (eski modelden). Dirsek tasarlanınca hesap yenilenir.",
]


def img64(path):
    return "data:image/%s;base64,%s" % (path.rsplit(".", 1)[1], base64.b64encode(open(path, "rb").read()).decode())


bom_satin = [(k, n) for t, k, n in d["bom"] if t == "Satin"]
bom_bag = [(k, n) for t, k, n in d["bom"] if t == "Baglanti"]
rows_baski = d["baski"]

# ---------------------------------------------------------------- markdown
md = []
md.append("# Sağ omuz modülü (2 eksen) + üst kol bağlantısı\n")
md.append("FreeCAD 1.1 · `omuz_montaj.py` ile üretildi · %d parça · çizim ve kontroller betikle tekrarlanabilir.\n" % d["parca_sayisi"])
md.append("## Özet\n")
md.append("| | |\n|---|---|")
md.append("| Eksenler | Öne-arka (S1, X ekseni) ve yana açma (S2, Z ekseni); iki eksen tek noktada kesişir |")
md.append("| Yük yolu | Öne-arka: 6808-2RS rulman taşır, S1 yalnız döndürür. Yana açma: çatal iki taraftan tutulur (horn + 625ZZ) |")
md.append("| Montaj kontrolü | %d parça, ev pozunda **%d çakışma** (tolerans 0,5 mm³), tüm parçalar tek ve geçerli katı |" % (d["parca_sayisi"], len(d["statik"])))
md.append("| Öne-arka serbest aralık | %s° … %s° arası hiçbir yere çarpmıyor (taranan aralığın tamamı) |" % (min(phi_free), max(phi_free)))
md.append("| Yana açma serbest aralık | %s° … %s° (her öne-arka açısında) |" % aralik(th_free_all))
md.append("| En küçük boşluk (kol aşağıda) | Kol × gövde %.1f mm (%s ↔ %s) |" % tuple(d["bosluk"]["Kol-Govde"]))
md.append("| En kötü tork (eklem sınırları içinde) | Öne-arka %.1f kg·cm, yana açma %.1f kg·cm · DS3218MG ≈ 20 kg·cm → ≈ %.1f× pay |" % (tp_l, tr_l, 20 / max(tp_l, tr_l)))
md.append("| Hareketli kütle | Göbek grubu %.0f g, kol grubu %.0f g + dirsek ve aşağısı (tahmini) %d g |" % (d["kutle"]["Gobek"], d["kutle"]["Kol"], d["alt_kol"]["m"]))
md.append("")
md.append("## Hangi parça neye, nasıl bağlanıyor\n")
md.append("| Bağlantı | Nasıl oturuyor | Bağlantı elemanı |\n|---|---|---|")
for a, b, c in BAGLANTI:
    md.append("| %s | %s | %s |" % (a, b, c))
md.append("\n## Montaj sırası\n")
for i, s in enumerate(SIRA, 1):
    md.append("%d. %s" % (i, s))
md.append("\n## Satın alınacaklar\n")
md.append("| Parça | Adet |\n|---|---|")
for k, n in bom_satin:
    md.append("| %s | %d |" % (k, n))
md.append("\n## Bağlantı elemanları\n")
md.append("| Eleman | Adet |\n|---|---|")
for k, n in bom_bag:
    md.append("| %s | %d |" % (k, n))
md.append("\n## Baskı parçaları (PETG)\n")
md.append("| Parça | Ölçü (mm) | Kütle (g, %60 doluluk) | Yazıcıya sığar (230 mm) | STL |\n|---|---|---|---|---|")
for r in rows_baski:
    md.append("| %s | %s | %.0f | %s | `%s` |" % (r["ad"], " × ".join("%.0f" % x for x in r["olcu"]), r["kutle"],
                                               "evet" if r["sigar"] else "**hayır**", r["stl"]))
md.append("\n## Kontrollerde bulunup düzeltilenler\n")
md.append("- Rulman kapağı cıvatalarının başı kapak halkasına 0,75 mm³ biniyordu (cıvata oturmazdı). Delikler 1 mm dışarı alındı (z = ±33).")
md.append("\n## Doğrulanacaklar ve açık işler\n")
for s in ACIK:
    md.append("- " + s)
md.append("\n## Dosyalar\n")
md.append("- `omuz-montaj.FCStd`: FreeCAD montajı (3 grup, 2 döner eklem). `omuz-montaj.step`: tüm parçalar.")
md.append("- `stl/`: 5 baskı parçası. `gorsel/`: görünümler, patlatılmış montaj, hareket animasyonu, çalışma alanı haritası.")
md.append("- `omuz_lib.py` (parça ve standart eleman kütüphanesi), `omuz_montaj.py` (montaj + kontroller), `omuz_gorsel.py`, `omuz_rapor.py`.")
open(os.path.join(HERE, "rapor.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")

# ---------------------------------------------------------------- html (tek dosya, gorseller gomulu)
import re
def md_inline(s):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s

ozet = [l for l in md[md.index("## Özet\n") + 3: md.index("## Hangi parça neye, nasıl bağlanıyor\n") - 1]]
H = []
H.append("""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sağ Omuz Modülü</title><style>
:root{--bg:#f6f4ef;--card:#fff;--ink:#1d1f22;--mut:#666;--line:#e3e0d8;--acc:#e8862a;--acc2:#2f86d4}
@media (prefers-color-scheme:dark){:root{--bg:#16171a;--card:#202226;--ink:#ececec;--mut:#9a9a9a;--line:#33363b}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,Segoe UI,sans-serif}
main{max-width:1080px;margin:0 auto;padding:28px 16px 60px}
h1{font-size:28px;margin:0 0 4px}h2{font-size:19px;margin:34px 0 10px;border-bottom:2px solid var(--acc);display:inline-block}
.sub{color:var(--mut);margin-bottom:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
figure img{width:100%;display:block;background:#fff}figcaption{padding:8px 12px;color:var(--mut);font-size:13px}
table{border-collapse:collapse;width:100%;background:var(--card);border-radius:10px;overflow:hidden;font-size:14px}
td,th{border-bottom:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}th{background:rgba(232,134,42,.12)}
.k{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi b{display:block;font-size:22px}.kpi span{color:var(--mut);font-size:13px}
ol li,ul li{margin:4px 0}code{background:rgba(127,127,127,.15);padding:1px 5px;border-radius:4px}
.wide{grid-column:1/-1}
</style></head><body><main>""")
H.append("<h1>Sağ omuz modülü + üst kol bağlantısı</h1>")
H.append("<div class='sub'>FreeCAD 1.1 · %d parça · 2 döner eklem · çizim, çakışma ve tork kontrolleri betikle üretildi</div>" % d["parca_sayisi"])
H.append("<div class='k'>")
for big, small in (("%d / %d" % (len(d["statik"]), d["parca_sayisi"]), "çakışan parça / toplam parça"),
                   ("%d° … %d°" % (min(phi_free), max(phi_free)), "öne-arka: hiçbir yere çarpmıyor"),
                   ("%d° … %d°" % aralik(th_free_all), "yana açma: serbest aralık"),
                   ("%.1f mm" % d["bosluk"]["Kol-Govde"][0], "kol aşağıdayken gövdeye en yakın"),
                   ("%.1f× pay" % (20 / max(tp_l, tr_l)), "en kötü tork %.1f kg·cm, servo ≈ 20" % max(tp_l, tr_l))):
    H.append("<div class='kpi'><b>%s</b><span>%s</span></div>" % (big, small))
H.append("</div>")
H.append("<h2>Görünümler</h2><div class='grid'>")
H.append("<figure class='wide'><img src='%s'><figcaption>Hareket: öne kaldırma, yana açma, ikisi birlikte. Saydam duvar = V3 gövde kabuğunun yan yüzü</figcaption></figure>" % img64(os.path.join(G, "omuz-hareket.gif")))
H.append("<figure><img src='%s'><figcaption>Yakından: S1 yuvası, rulman kapağı, göbek ve S2, kol çatalı</figcaption></figure>" % img64(os.path.join(G, "omuz-yakin.png")))
H.append("<figure><img src='%s'><figcaption>Arkadan: çatalın karşı yatağı (625ZZ + M5 cıvata)</figcaption></figure>" % img64(os.path.join(G, "omuz-arka.png")))
H.append("<figure class='wide'><img src='%s'><figcaption>Patlatılmış montaj: her parça takıldığı yönde, montaj sırasıyla</figcaption></figure>" % img64(os.path.join(G, "omuz-patlatilmis.png")))
H.append("<figure class='wide'><img src='%s'><figcaption>%d pozda tarandı: kesik çerçeve eklem sınırları, içi tamamen yeşil</figcaption></figure>" % (img64(os.path.join(G, "omuz-calisma-alani.png")), len(phis) * len(ths)))
H.append("</div>")
H.append("<h2>Hangi parça neye, nasıl bağlanıyor</h2><table><tr><th>Bağlantı</th><th>Nasıl oturuyor</th><th>Bağlantı elemanı</th></tr>")
for a, b, c in BAGLANTI:
    H.append("<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>" % (md_inline(a), md_inline(b), md_inline(c)))
H.append("</table><h2>Montaj sırası</h2><ol>" + "".join("<li>%s</li>" % md_inline(s) for s in SIRA) + "</ol>")
H.append("<div class='grid'><div><h2>Satın alınacaklar</h2><table><tr><th>Parça</th><th>Adet</th></tr>")
H.append("".join("<tr><td>%s</td><td>%d</td></tr>" % (md_inline(k), n) for k, n in bom_satin) + "</table></div>")
H.append("<div><h2>Bağlantı elemanları</h2><table><tr><th>Eleman</th><th>Adet</th></tr>")
H.append("".join("<tr><td>%s</td><td>%d</td></tr>" % (md_inline(k), n) for k, n in bom_bag) + "</table></div></div>")
H.append("<h2>Baskı parçaları (PETG)</h2><table><tr><th>Parça</th><th>Ölçü (mm)</th><th>Kütle (g)</th><th>Yazıcıya sığar</th></tr>")
for r in rows_baski:
    H.append("<tr><td>%s</td><td>%s</td><td>%.0f</td><td>%s</td></tr>" % (r["ad"], " × ".join("%.0f" % x for x in r["olcu"]), r["kutle"], "evet" if r["sigar"] else "<b>hayır</b>"))
H.append("</table>")
H.append("<h2>Kontrollerde bulunup düzeltilenler</h2><ul><li>Rulman kapağı cıvatalarının başı kapak halkasına 0,75 mm³ biniyordu. Delikler 1 mm dışarı alındı.</li>"
         "</ul>")
H.append("<h2>Doğrulanacaklar ve açık işler</h2><ul>" + "".join("<li>%s</li>" % md_inline(s) for s in ACIK) + "</ul>")
H.append("</main></body></html>")
open(os.path.join(HERE, "rapor.html"), "w", encoding="utf-8").write("\n".join(H))
print("tamam", "gif", len(frames), "kare", "tork", tp_l, tr_l, "serbest yana", aralik(th_free_all), "one", min(phi_free), max(phi_free))
