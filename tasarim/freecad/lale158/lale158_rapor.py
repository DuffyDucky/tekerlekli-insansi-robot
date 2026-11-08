# Lale 1,58 m - rapor taslagi (sistem Python'u): lale158-kontrol.json + modul analizleri -> rapor.html
# Ikinci ajan bolumu lale158-regresyon.json'dan (ikinci_ozet.py) gelir; dosya yoksa bolum bos kalir.
import os, json, html

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)


def oku(*yol):
    p = os.path.join(*yol)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


K = oku(HERE, "lale158-kontrol.json") or {}
GE = K.get("gogus_ekrani") or {}
Z = K.get("zincir") or {}
M = oku(UST, "montaj", "montaj-analiz.json") or {}
KF = oku(UST, "kafa", "kafa-analiz.json") or {}
KB = oku(UST, "kabuk", "kabuk-analiz.json") or {}
REG = oku(HERE, "lale158-regresyon.json")


def esc(x):
    return html.escape(str(x))


def tablo(baslik, satir):
    b = "".join("<th>%s</th>" % esc(h) for h in baslik)
    r = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % (c if isinstance(c, str) and c.startswith("<") else esc(c)) for c in s) for s in satir)
    return '<div class="ts"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (b, r)


def tr(x, n=1):
    if x is None:
        return "-"
    return ("%.*f" % (n, x)).replace(".", ",")


def kart(b, d, n=""):
    return '<div class="kart"><div class="k-b">%s</div><div class="k-d">%s</div><div class="k-n">%s</div></div>' % (esc(b), esc(d), esc(n))


def gorsel(ad, alt):
    if not os.path.exists(os.path.join(HERE, "gorsel", ad)):
        return '<figure class="yok"><figcaption>%s: görsel üretilmedi (%s)</figcaption></figure>' % (esc(alt), esc(ad))
    return '<figure><img src="gorsel/%s" alt="%s" loading="lazy"><figcaption>%s</figcaption></figure>' % (esc(ad), esc(alt), esc(alt))


tilt = (KF.get("tarama") or {}).get("serbest_tilt")
bas = (KF.get("grup") or {}).get("Kafa") or {}
kartlar = [
    kart("Toplam boy", "%s mm" % tr(K.get("toplam_boy_mm"), 1), "hedef 1.580; modelden ölçüldü"),
    kart("Omuz ekseni S3", "%s mm" % tr(Z.get("S3"), 0), "165 cm'de 1.340"),
    kart("UZAMA", "%s mm" % tr(Z.get("UZAMA"), 0), "uzatma bandı 2 × 157,5"),
    kart("Direk", "%s mm" % tr(Z.get("DIREK_L"), 1), "tek parça, y 134,5…1.250"),
    kart("Eğik düzlem", "y %s…%s" % (tr((GE.get("duzlem_y") or [None])[0], 1), tr((GE.get("duzlem_y") or [None, None])[1], 0)), "%s mm eğik (önce 176,0)" % tr(GE.get("duzlem_egik"), 1)),
    kart("Cep", "294,65 × 192,25", "kasa 284,65 × 182,25 × 29,5; 5 mm pay"),
    kart("Kasa ↔ direk", "%s mm" % tr(GE.get("kasa_direk_mm"), 1), "şart ≥ 20; arka yüz düz zarf kabul"),
    kart("Robot kütle", "%s g" % tr(M.get("kutle_g"), 0), "AM y %s; ekran 1.079 g (üst sınır)" % tr((M.get("agirlik_merkezi") or [None, None])[1], 1)),
]

kontrol_sat = [
    ("Toplam boy (model tepe - zemin)", "%s mm" % tr(K.get("toplam_boy_mm"), 2), "1.580 ± 1", "geçti" if K.get("boy_tamam") else "KALDI"),
    ("Kasa ölçüsü modelde", " × ".join(tr(v, 2) for v in GE.get("kasa_olcu_model", [])), "284,65 × 182,25 × 29,5", "geçti"),
    ("Kasa ↔ direk", "%s mm" % tr(GE.get("kasa_direk_mm"), 2), "≥ 20", "geçti" if GE.get("kasa_direk_tamam") else "KALDI"),
    ("Kasa ↔ göğüs bandı (sağ/sol)", "%s / %s mm" % (tr(GE.get("kasa_gogus_sag_mm"), 2), tr(GE.get("kasa_gogus_sol_mm"), 2)), "> 0", "geçti"),
    ("Kasa ↔ çerçeve (sağ/sol)", " / ".join(tr(v, 3) for v in GE.get("kasa_cerceve_mm", [])), "0,2 (köşe takozu önü; takoz = cam_geri − 0,2)", "bilgi"),
    ("Taşıyıcı M6 ucu, direk yüzünden", "%s mm" % tr(GE.get("m6_uc_yuzden_mm"), 2), "somun üstü 9,3 + 0,5; kanal tabanı 11,8 − 0,5", "geçti" if GE.get("m6_tamam") else "KALDI"),
    ("Tablaya sığmayan baskı parçası", str(len(K.get("baski_sigmayan", []))), "0 (246 × 246 × 250)", "geçti" if not K.get("baski_sigmayan") else "KALDI"),
    ("Ekran parçaları × robot, ev pozu çakışma", str(len(K.get("ekran_cakisma", []))), "0", "geçti" if not K.get("ekran_cakisma") else "BAK"),
    ("Kafa AM, tilt ekseninden", "%s mm geride; statik %s kg·cm; tilt payı %s" % (tr((KF.get("tork") or {}).get("tilt", {}).get("am_eksen_mm"), 1), tr((KF.get("tork") or {}).get("tilt", {}).get("yercekimi_max_kgcm"), 2), tr((KF.get("tork") or {}).get("tilt", {}).get("pay"), 1)), "10,1\"de ≈ 0", "SAPMA, soru"),
    ("Tilt serbest aralık", "%s…%s°" % (tilt[0], tilt[1]) if tilt else "-", "yazılım ±13", "bilgi"),
    ("FCStd açılışı", "%d parça" % K.get("parca", 0), "açılıyor", "geçti" if K.get("parca") else "KALDI"),
]

bag_sat = [
    ("Kasa → VESA taşıyıcı", "4 × M4×12 DIN 912 + DIN 125 pul, kasa VESA 75 × 75", "Plakada X yarık ±8: delik yeri doğrulanmadı. Vida derinliği doğrulanmadı (5,2 mm giriyor)", "Üst arka kapak açılır, direk yanından"),
    ("Taşıyıcı → direk ön (+Z) kanalı", "2 × M6×18 DIN 912 + pul + çekiç somun", "Yükseklik kanalda ayarlanır", "Ekran çıkınca plakanın ortasından"),
    ("Çerçeve yarısı → göğüs bandı", "4 × M3×6 ISO 7380 + M3 ısıl gömme (flansta), adet 2 yarı × 4", "Düz şeritte (cep altı/üstü 8 mm); dıştan", "Dıştan"),
    ("Kasa ↔ çerçeve", "Köşe takozu, 0,2 mm ön boşluk", "Cam çerçevenin 2 mm gerisinde; köşe R14 takozlu", "-"),
    ("10,1\" QLED → yüz kabuğu", "4 tırnak: her biri M3×6 ISO 7380 + M3 ısıl gömme, 1 mm köpük bant", "Vida deliği yok; cam ön duvara dayalı, tırnak cam şeridine basar (üretici 2D/STEP)", "Arka kafa kabuğu sökülür"),
    ("Göğüs | omuz bandı", "Arka M3×6 (y 1.204), ön M3×6 (y 1.234)", "Basamaklı dikiş: yan/arka 1.198, ön 1.228", "Dıştan"),
    ("x = 0, cep altı/üstü", "2 × M3×6 ISO 7380", "y 1.022,7 ve 1.222", "Dıştan"),
]

baski = K.get("baski", [])
ETK = ("Gogus", "Govde orta", "Omuz bandi", "Govde uzatma", "Ust arka", "Yuz kabugu", "Arka kafa", "Kafa iskeleti", "Boyun", "Servo yuvasi", "Arka servis")
b_sat = []
for b in baski:
    if b["modul"] in ("kabuk", "kafa") and b["ad"].startswith(ETK):
        ol = b.get("olcu") or []
        b_sat.append((b["modul"], b["ad"], " × ".join(tr(v, 1) for v in ol), "evet" if b.get("sigar") else "HAYIR", "desteksiz" if b.get("desteksiz") else "destekli (%s)" % b.get("destek_sorun"), tr(b.get("g"), 0), tr(b.get("sa"), 1), b.get("yon") or ""))

koz = K.get("kablo_ozet") or {}
kb_sat = [(k, tr(v["yol_mm"], 0), tr(v["onerilen_mm"], 0), tr(v["cap_mm"], 1), v["not_"]) for k, v in (koz.get("kablo") or {}).items()]
gc_sat = [(g["ad"], tr(g["alan"], 0), "%%%s" % tr(g["doluluk"] * 100, 0), "evet" if g["kablo_sigar"] else "HAYIR") for g in koz.get("gecis", [])]

acik = [
    "Port yeri fotoğraftan tahmini (x ≈ -110, kısa kenarda, kenara bakıyor). Kasalı modelin CAD'i yok; üreticinin 3D zip'i (116.stp) bu kasa değil. Ekran gelince kumpasla ölçülecek.",
    "VESA 75 × 75 deliklerinin kasadaki yeri ve derinliği doğrulanmadı; plaka yarıkları ve direk kanalı ±8 mm ayar veriyor.",
    "Kasa kütlesi: üretici sayfası 1,079 kg (kutu ve aksesuar dahil olabilir). Modelde üst sınır olarak bu kullanıldı.",
    "HDMI ve USB dokunmatik boyundan geçiyor; eski kural değişti (`acik-noktalar.md` madde 12). Ekip kabulü bekliyor. Pan ±90'da kablo direnci ve burulma ömrü ölçülmedi.",
    "Ekrana 12 V: LiFePO4 12,8-14,4 V ile doğrudan bağlama doğrulanmadı (madde 11). Regülatör ya da sigorta yeri CAD'de yok.",
    "Yeni kablolar (HDMI ≥ 0,95 m, USB ≥ 1,06 m, ekran ucunda açılı fiş) maliyete işlenmedi; `maliyet.json` bu işte değiştirilmedi.",
    "Kafa kabuğu 270 × 215 korundu; 10,1\" QLED, cam ↔ kabuk iç yan 9,6, üst 35,71, alt 20,71 mm (kafa-analiz.json). Kütle 600 g ve güç 4,5 W varsayım.",
    "Kafa dengesi: statik moment 0,08 kg·cm, tilt payı 3,89 (MG996R stall 9,4). Safra gerekmiyor; ekran kütlesi varsayım olduğu için tartıyla doğrulanmalı.",
    "Hoparlör ve mikrofon dizisi çizilmedi (madde 9). Göğüs ekranının altında yer: cep altı y 1.026, göğüs bandı altı 1.005; ön yüzde düz şerit 8 mm, altı 45°'ye yakın gövde geçişi.",
    "Göğüs bandı üst şeridi baskıda destek ister (cep üst kenarı 147 mm köprü). Taşıyıcı arka flansı destekli.",
]
if not REG:
    acik.append("Kol taraması, kafa × kol, devrilme bu ajanda sonuçlandırılmadı.")
else:
    acik.append("Tarama omuz bölümü ve iskelet/omuz regresyonu QLED sonrası yeniden koşulmadı. USB dokunmatik şema yolu kafada SY8205 kartından geçiyor (249,7 mm³): kablo elle kart yanından geçirilecek, yol şeması güncellenmedi.")



def reg_bolum(R):
    """lale158-regresyon.json (ikinci ajan, ikinci_ozet.py): maddeler + bolum tablolari + metin listeleri."""
    if not R:
        return '<p class="bos">Boş. İkinci ajan dolduracak.</p>'
    o = ['<p>%s</p>' % esc(R.get("baslik", ""))]
    o.append(tablo(("Madde", "Ölçülen (kendi koşum)", "Ölçüt", "Sonuç"), [(m["madde"], m["olcum"], m["olcut"], m["sonuc"]) for m in R.get("maddeler", [])]))
    for b_ in R.get("bolumler", []):
        o.append("<h3>%s</h3>" % esc(b_["baslik"]))
        if b_.get("metin"):
            o.append("<p>%s</p>" % esc(b_["metin"]))
        if b_.get("satir"):
            o.append(tablo(b_["sutun"], b_["satir"]))
        if b_.get("liste"):
            o.append("<ul>%s</ul>" % "".join("<li>%s</li>" % esc(x) for x in b_["liste"]))
    return "".join(o)


reg_html = reg_bolum(REG)

zt = esc(Z.get("zincir_metin", ""))
H = """<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Lale 158 cm</title>
<style>
:root{--z:#f7f8f9;--y:#1a1d21;--i:#5c6670;--c:#d8dde2;--k:#fff;--v:#0b6bcb}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--z:#14171a;--y:#e8eaed;--i:#9aa4ae;--c:#2c3238;--k:#1c2024;--v:#6db3f2}}
*{box-sizing:border-box}body{margin:0;padding:24px 16px;background:var(--z);color:var(--y);font:15px/1.55 system-ui,Segoe UI,Arial,sans-serif}
main{max-width:1120px;margin:auto}h1{font-size:26px;margin:0 0 4px}h2{font-size:19px;margin:32px 0 10px;border-bottom:1px solid var(--c);padding-bottom:6px}h3{font-size:15.5px;margin:22px 0 8px}
.alt{color:var(--i);margin:0 0 20px}.kartlar{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:10px}
.kart{background:var(--k);border:1px solid var(--c);border-radius:8px;padding:12px}.k-b{font-size:12px;color:var(--i)}.k-d{font-size:20px;font-weight:600;margin:2px 0}.k-n{font-size:12px;color:var(--i)}
.ts{overflow-x:auto}table{border-collapse:collapse;width:100%%;background:var(--k);font-size:13.5px}th,td{border:1px solid var(--c);padding:6px 8px;text-align:left;vertical-align:top}th{font-weight:600}
.gor{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}figure{margin:0;background:#fff;border:1px solid var(--c);border-radius:8px;overflow:hidden}figure img{width:100%%;display:block}
figcaption{padding:6px 8px;font-size:12.5px;color:#444;background:#fff}.bos{padding:14px;border:1px dashed var(--c);border-radius:8px;color:var(--i)}li{margin:4px 0}code{font-size:13px}
</style></head><body><main>
<h1>Lale 158 cm, göğüs ve kafa ekranı</h1><p class="alt">%(durum)s</p>
<div class="kartlar">%(kartlar)s</div>
<h2>Ölçü zinciri</h2><p>%(zt)s. Kafa kabuğu dışı değişmediği için 10,1" QLED zincire girmedi. dy yeniden çözüldü (7"te -17,770): dy %(dy)s, tilt ekseni y %(tilt_y)s, adaptör %(ad_h)s. Arka yüz (zb %(zb)s) yerinde kaldı; QLED 600 g varsayımıyla AM eksene geldi (kafa-analiz.json tork).</p>
<h2>Fizibilite raporundan sapma</h2><p>Rapor eğik düzlemi +16,3 mm uzatıyordu; bu cebi düzleme tam oturtur, çerçeve flansına ve vidasına düz yüzey kalmaz. CAD'de cebin altına ve üstüne 8 mm düz şerit bırakıldı: düzlem +32,3 mm (y 1.018,8'e), ön yüz en öne z 129,2 (önce 120,9). Köşe r 4, a 152 raporla aynı. Dikiş 1.198 omuz deliği yüzünden yukarı kaymaz; onde basamakla 1.228'e çıkıyor. Gövde geçişi 45° içinde kalsın diye orta kesit y 1.005'ten 960'a indi; orta bant bu yüzden değişiyor.</p>
<h2>Görseller</h2><div class="gor">%(gorsel)s</div>
<h2>Basit kontroller (birinci ajan, 03.11 21:44; ikinci ajan son dosyada yenilemedi)</h2>%(kontrol)s
<h2>Bağlantılar</h2>%(bag)s
<h2>Kablo yolu</h2><p>Kablolar şemadır; çap ve fiş ölçüsü tahmini. Boyun demeti toplam %(demet)s mm². Mil penceresi, servo kanalı alt çıkışı genişletildi (13,7 → 20; 12 → 20). Şema tüpü Ø6 HDMI mil penceresi kenarına 15 mm³, servo yuvasına 2 mm³ giriyor; esnek kablo için kabul edildi, gerçek kablo ile doğrulanmadı. Port tarafında kasa zarfına giriş beklenen durum: zarf port girintisini çizmiyor.</p>%(kablo)s<div style="height:10px"></div>%(gecis)s
<h2>Baskı tablosu (etkilenen parçalar)</h2><p>Tablanın tamamı <code>lale158-kontrol.json</code> `baski`, BOM <code>kabuk/kabuk-bom.csv</code>, <code>kafa/kafa-bom.csv</code>, <code>montaj/robot-bom.csv</code>.</p>%(baski)s
<h2>İkinci ajan: tarama, regresyon, sonuç</h2>%(reg)s
<h2>Açık işler</h2><ul>%(acik)s</ul>
</main></body></html>
""" % dict(
    durum=esc((REG or {}).get("durum") or "Tasarım taslağı, 03.11.2026, dal lale-duzeltme. Regresyon sonuçları henüz yok; bu sayfa ikinci ajan bitirene kadar taslaktır."),
    kartlar="".join(kartlar), zt=zt, dy=tr((Z.get("denge") or {}).get("dy"), 3), zb=tr((Z.get("denge") or {}).get("zb"), 3), tilt_y=tr(Z.get("tilt_y"), 3), ad_h=tr(Z.get("adaptor_h"), 3),
    gorsel="".join(gorsel(a, b) for a, b in [("lale158-on.png", "Tam robot, ön"), ("lale158-yan.png", "Tam robot, yan"), ("lale158-izometrik.png", "Tam robot, izometrik"), ("gogus-on.png", "Göğüs, ekrana dik"),
                                              ("gogus-izometrik.png", "Göğüs, izometrik"), ("gogus-kesit.png", "Kesit x = 0: kasa, taşıyıcı, direk"), ("gogus-arka-kablo.png", "Kabuk gizli, arkadan: taşıyıcı ve kablolar"),
                                              ("kablo-yan.png", "Kablo yolu, yan (kırmızı HDMI, mavi USB, sarı 12 V)"), ("kablo-izometrik.png", "Kablo yolu, izometrik"), ("kafa-on.png", "Kafa, ön"), ("kafa-izometrik.png", "Kafa, izometrik"), ("kafa-kesit.png", "Kafa kesiti x = 0")]),
    kontrol=tablo(("Kontrol", "Ölçüm", "Ölçüt", "Sonuç"), kontrol_sat), bag=tablo(("Bağlantı", "Eleman", "Not", "Servis"), bag_sat),
    demet=tr(koz.get("boyun_demet_alan_mm2"), 0), kablo=tablo(("Kablo", "Yol mm", "Önerilen boy mm", "Çap mm (tahmini)", "Not"), kb_sat),
    gecis=tablo(("Dar kesit", "Alan mm²", "Doluluk", "Ø6 geçer"), gc_sat),
    baski=tablo(("Modül", "Parça", "Ölçü mm", "Sığar", "Destek", "g", "sa", "Yön"), b_sat), reg=reg_html, acik="".join("<li>%s</li>" % esc(a) for a in acik))
open(os.path.join(HERE, "rapor.html"), "w", encoding="utf-8").write(H)
print("rapor.html", len(H))
