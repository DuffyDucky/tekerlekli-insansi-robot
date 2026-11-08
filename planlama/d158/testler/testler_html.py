"""Test kâğıtlarını (00-genel.md, T1..T9 .md) tek, yazdırılabilir testler.html'ye çevirir.

Kullanım (bu klasörde):
    py -3 testler_html.py            # testler.html'yi yeniden üretir
    py -3 testler_html.py --kontrol  # dosyayı değiştirmeden tutarlılığı denetler

Yalnız standart kütüphane. Markdown'ın küçük bir alt kümesini çevirir: başlık, paragraf, liste (iç içe),
tablo, kod bloğu, kalın, satır içi kod, bağlantı. .md dosyaları asıl kaynaktır; HTML elle düzenlenmez.
"""
import html
import re
import sys
from pathlib import Path

KLASOR = Path(__file__).resolve().parent
CIKTI = KLASOR / "testler.html"


def md_dosyalari():
    dosyalar = sorted(KLASOR.glob("*.md"), key=lambda p: (0 if p.name.startswith("00") else 1, _t_sira(p.name)))
    return dosyalar


def _t_sira(ad):
    m = re.match(r"T(\d+)-", ad)
    return int(m.group(1)) if m else 0


def bolum_id(ad):
    m = re.match(r"(T\d+)-", ad)
    if m:
        return m.group(1).lower()
    return "genel"


TR = str.maketrans("çğıöşüÇĞİÖŞÜâÂ", "cgiosuCGIOSUaA")


def slug(metin):
    s = metin.translate(TR).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "baslik"


def satir_ici(metin, bag_haritasi):
    """Kaçış + satır içi kod + kalın + bağlantı."""
    kodlar = []

    def kod_ayir(m):
        kodlar.append("<code>" + html.escape(m.group(1), quote=False) + "</code>")
        return "\x00%d\x00" % (len(kodlar) - 1)

    e = re.sub(r"`([^`]*)`", kod_ayir, metin)  # kod önce ayrılır; kalın/bağlantı kodun dışına uygulanır
    e = html.escape(e, quote=False)
    e = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", e)
    e = re.sub(r"\*(\S.*?)\*", r"<em>\1</em>", e)

    def bag(m):
        yazi, hedef = m.group(1), m.group(2)
        if hedef in bag_haritasi:
            return '<a href="#%s">%s</a>' % (bag_haritasi[hedef], yazi)
        return "%s (%s)" % (yazi, hedef)  # bilinmeyen hedef: düz metin, dış bağlantı yok

    e = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", bag, e)
    return re.sub(r"\x00(\d+)\x00", lambda m: kodlar[int(m.group(1))], e)


LISTE_RE = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")


def liste_cevir(satirlar, bag_haritasi):
    """Girintiye göre iç içe liste."""
    ogeler = []  # (girinti, sirali, numara, metin)
    for s in satirlar:
        m = LISTE_RE.match(s)
        if m:
            girinti = len(m.group(1).expandtabs(4))
            isaret = m.group(2)
            sirali = isaret[0].isdigit()
            numara = int(isaret[:-1]) if sirali else None
            ogeler.append([girinti, sirali, numara, m.group(3)])
        elif ogeler:
            ogeler[-1][3] += " " + s.strip()
    out = []
    yigin = []  # (girinti, etiket)
    for girinti, sirali, numara, metin in ogeler:
        while yigin and girinti < yigin[-1][0]:
            out.append("</li></%s>" % yigin.pop()[1])
        if not yigin or girinti > yigin[-1][0]:
            etiket = "ol" if sirali else "ul"
            bas = ' start="%d"' % numara if sirali and numara and numara != 1 else ""
            out.append("<%s%s>" % (etiket, bas))
            yigin.append((girinti, etiket))
            out.append("<li>" + satir_ici(metin, bag_haritasi))
        else:
            out.append("</li><li>" + satir_ici(metin, bag_haritasi))
    while yigin:
        out.append("</li></%s>" % yigin.pop()[1])
    return "".join(out)


def tablo_hucreleri(satir):
    s = satir.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    # satır içi kod içindeki | ayırıcı sayılmasın
    hucreler, buf, kodda = [], "", False
    for ch in s:
        if ch == "`":
            kodda = not kodda
        if ch == "|" and not kodda:
            hucreler.append(buf.strip())
            buf = ""
        else:
            buf += ch
    hucreler.append(buf.strip())
    return hucreler


def tablo_cevir(satirlar, bag_haritasi):
    bas = tablo_hucreleri(satirlar[0])
    govde = [tablo_hucreleri(s) for s in satirlar[2:]] if len(satirlar) > 1 and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", satirlar[1]) else [tablo_hucreleri(s) for s in satirlar[1:]]
    out = ['<div class="tablo"><table><thead><tr>']
    out += ["<th>%s</th>" % satir_ici(h, bag_haritasi) for h in bas]
    out.append("</tr></thead><tbody>")
    for r in govde:
        r = r + [""] * (len(bas) - len(r))
        out.append("<tr>" + "".join("<td>%s</td>" % satir_ici(h, bag_haritasi) for h in r[: len(bas)]) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def md_cevir(metin, bolum, bag_haritasi):
    satirlar = metin.splitlines()
    out, idler = [], set()
    i = 0
    while i < len(satirlar):
        s = satirlar[i]
        if not s.strip():
            i += 1
            continue
        if s.startswith("```"):
            j, buf = i + 1, []
            while j < len(satirlar) and not satirlar[j].startswith("```"):
                buf.append(satirlar[j])
                j += 1
            out.append("<pre><code>%s</code></pre>" % html.escape("\n".join(buf), quote=False))
            i = j + 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            seviye = len(m.group(1))
            yazi = m.group(2).strip()
            if seviye == 1:
                hid = bolum
            else:
                hid = bolum + "-" + slug(yazi)
                k, temel = 2, hid
                while hid in idler:
                    hid = "%s-%d" % (temel, k)
                    k += 1
            idler.add(hid)
            out.append('<h%d id="%s">%s</h%d>' % (seviye, hid, satir_ici(yazi, bag_haritasi), seviye))
            i += 1
            continue
        if s.lstrip().startswith("|"):
            j = i
            while j < len(satirlar) and satirlar[j].lstrip().startswith("|"):
                j += 1
            out.append(tablo_cevir(satirlar[i:j], bag_haritasi))
            i = j
            continue
        if LISTE_RE.match(s):
            j = i
            while j < len(satirlar) and satirlar[j].strip() and (LISTE_RE.match(satirlar[j]) or satirlar[j].startswith(" ")):
                j += 1
            out.append(liste_cevir(satirlar[i:j], bag_haritasi))
            i = j
            continue
        j, buf = i, []
        while j < len(satirlar) and satirlar[j].strip() and not re.match(r"^(#{1,6}\s|```|\s*\|)", satirlar[j]) and not LISTE_RE.match(satirlar[j]):
            buf.append(satirlar[j].strip())
            j += 1
        out.append("<p>%s</p>" % satir_ici(" ".join(buf), bag_haritasi))
        i = j
    return "\n".join(out)


CSS = """
:root{--bg:#ffffff;--fg:#1a1a1a;--soluk:#5a5a5a;--cizgi:#9a9a9a;--bas:#eef1f4;--vurgu:#0b5394;--kod:#f3f3f3;--uyari:#8a1c1c}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#15181c;--fg:#e6e6e6;--soluk:#a6a6a6;--cizgi:#4c535b;--bas:#232a31;--vurgu:#8ab8e6;--kod:#22272d;--uyari:#f08a8a}}
:root[data-theme="dark"]{--bg:#15181c;--fg:#e6e6e6;--soluk:#a6a6a6;--cizgi:#4c535b;--bas:#232a31;--vurgu:#8ab8e6;--kod:#22272d;--uyari:#f08a8a}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
.ust{position:sticky;top:0;z-index:2;display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between;padding:10px 16px;background:var(--bas);border-bottom:1px solid var(--cizgi)}
.ust h1{font-size:16px;margin:0}
.ust button{font:inherit;padding:4px 10px;border:1px solid var(--cizgi);background:var(--bg);color:var(--fg);border-radius:4px;cursor:pointer}
main,nav{max-width:1000px;margin:0 auto;padding:0 16px}
nav ol{padding-left:22px}
.kagit{border-top:3px solid var(--vurgu);margin-top:28px;padding-top:8px}
h1{font-size:22px;margin:12px 0}
h2{font-size:18px;margin:20px 0 8px;border-bottom:1px solid var(--cizgi);padding-bottom:2px}
h3{font-size:16px;margin:16px 0 6px}
a{color:var(--vurgu)}
code{background:var(--kod);padding:0 3px;border-radius:3px;font:13px/1.4 ui-monospace,Consolas,"Courier New",monospace;overflow-wrap:anywhere}
pre{background:var(--kod);padding:8px;border-radius:4px;overflow-x:auto;white-space:pre-wrap}
pre code{padding:0;background:none}
.tablo{overflow-x:auto;margin:8px 0}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{border:1px solid var(--cizgi);padding:4px 6px;text-align:left;vertical-align:top;overflow-wrap:anywhere}
th{background:var(--bas)}
td:empty{height:1.9em}
li{margin:2px 0}
@page{size:A4;margin:12mm}
@media print{
 :root,:root[data-theme="dark"],:root:not([data-theme="light"]){--bg:#fff;--fg:#000;--soluk:#333;--cizgi:#777;--bas:#e8e8e8;--vurgu:#000;--kod:#f2f2f2;--uyari:#000}
 body{font-size:10pt}
 .ust,nav{display:none}
 main{max-width:none;padding:0}
 .kagit{break-before:page;border-top:none;margin-top:0}
 .kagit:first-of-type{break-before:auto}
 h2,h3{break-after:avoid}
 table{font-size:8.5pt}
 tr,pre{break-inside:avoid}
 td:empty{height:8mm}
 a{color:#000;text-decoration:none}
 .tablo{overflow:visible}
}
"""

JS = """
(function(){
 var k='lale-testler-tema',r=document.documentElement;
 try{var t=localStorage.getItem(k);if(t){r.setAttribute('data-theme',t);}}catch(e){}
 var b=document.getElementById('tema');
 if(b){b.addEventListener('click',function(){
  var koyu=r.getAttribute('data-theme')==='dark'||(!r.getAttribute('data-theme')&&window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches);
  var y=koyu?'light':'dark';r.setAttribute('data-theme',y);
  try{localStorage.setItem(k,y);}catch(e){}
 });}
 var p=document.getElementById('yazdir');if(p){p.addEventListener('click',function(){window.print();});}
})();
"""


def uret():
    dosyalar = md_dosyalari()
    bag_haritasi = {d.name: bolum_id(d.name) for d in dosyalar}
    bolumler, icindekiler = [], []
    for d in dosyalar:
        metin = d.read_text(encoding="utf-8")
        bid = bolum_id(d.name)
        ilk = re.search(r"^#\s+(.*)$", metin, re.M)
        baslik = ilk.group(1).strip() if ilk else d.name
        icindekiler.append('<li><a href="#%s">%s</a></li>' % (bid, satir_ici(baslik, bag_haritasi)))
        bolumler.append('<section class="kagit" id="%s-kagit" data-kaynak="%s">\n%s\n</section>' % (bid, d.name, md_cevir(metin, bid, bag_haritasi)))
    return (
        '<!doctype html>\n<html lang="tr">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>Lale test kâğıtları</title>\n<style>%s</style>\n</head>\n<body>\n"
        '<header class="ust"><h1>Lale 1,58 m · ölçüm ve test kâğıtları (P8.3)</h1>'
        '<span><button id="yazdir" type="button">Yazdır</button> <button id="tema" type="button">Tema</button></span></header>\n'
        '<nav id="icindekiler"><h2>İçindekiler</h2><ol>%s</ol>'
        "<p>Bu sayfa <code>planlama/d158/testler/*.md</code> dosyalarından <code>testler_html.py</code> ile üretildi; "
        "asıl kaynak .md dosyalarıdır. Yazdırınca her kâğıt yeni A4 sayfasında başlar.</p></nav>\n"
        "<main>\n%s\n</main>\n<script>%s</script>\n</body>\n</html>\n"
    ) % (CSS, "".join(icindekiler), "\n".join(bolumler), JS)


def kontrol():
    hatalar = []
    if not CIKTI.exists():
        print("HATA: testler.html yok")
        return 1
    h = CIKTI.read_text(encoding="utf-8")
    dosyalar = md_dosyalari()
    adlar = [d.name for d in dosyalar]
    # 1) her .md HTML'de bir bölüm olarak var
    for ad in adlar:
        if 'data-kaynak="%s"' % ad not in h:
            hatalar.append("md HTML'de yok: " + ad)
    for ad in re.findall(r'data-kaynak="([^"]+)"', h):
        if ad not in adlar:
            hatalar.append("HTML'de olup klasörde olmayan md: " + ad)
    t_sayisi = sum(1 for a in adlar if re.match(r"T\d+-", a))
    # 2) iç bağlantılar
    idler = set(re.findall(r'\bid="([^"]+)"', h))
    hrefler = re.findall(r'\bhref="([^"]*)"', h)
    for hr in hrefler:
        if not hr.startswith("#"):
            hatalar.append("iç olmayan bağlantı: " + hr)
        elif hr[1:] not in idler:
            hatalar.append("hedefi olmayan bağlantı: " + hr)
    # 3) harici kaynak yok
    for desen in (r"<link\b", r"\bsrc\s*=", r"@import", r"url\(\s*['\"]?https?:"):
        if re.search(desen, h, re.I):
            hatalar.append("harici kaynak izi: " + desen)
    # 4) .md içindeki göreli bağlantıların hedef dosyası var
    for d in dosyalar:
        for hedef in re.findall(r"\]\(([^)\s]+)\)", d.read_text(encoding="utf-8")):
            if not (KLASOR / hedef).exists():
                hatalar.append("%s: bağlantı hedefi yok: %s" % (d.name, hedef))
    # 5) HTML güncel mi (md'lerden yeniden üretilen ile aynı)
    if uret() != h:
        hatalar.append("testler.html güncel değil: py -3 testler_html.py ile yeniden üret")
    # 6) tema ve yazdırma kuralları
    for parca in ("prefers-color-scheme: dark", 'data-theme="dark"', "@page{size:A4", "break-before:page"):
        if parca not in h:
            hatalar.append("CSS parçası yok: " + parca)
    print("md dosyası: %d (kâğıt T: %d), HTML bölümü: %d, iç bağlantı: %d, id: %d"
          % (len(adlar), t_sayisi, len(re.findall(r'data-kaynak="', h)), len(hrefler), len(idler)))
    if hatalar:
        for x in hatalar:
            print("HATA:", x)
        return 1
    print("KONTROL GEÇTİ")
    return 0


if __name__ == "__main__":
    if "--kontrol" in sys.argv:
        sys.exit(kontrol())
    CIKTI.write_text(uret(), encoding="utf-8", newline="\n")
    print("yazıldı:", CIKTI)
