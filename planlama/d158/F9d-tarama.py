# -*- coding: utf-8 -*-
"""F9d (P9.4): izlenen dosyalarda yerel kullanıcı klasörü yolu taraması.

Yalnız okur; hiçbir dosyaya yazmaz. Kullanım (depo kökünden ya da herhangi bir yerden):

    py -3 planlama/d158/F9d-tarama.py            # liste + alan sayıları; yazılabilir alanda eşleşme varsa çıkış 1
    py -3 planlama/d158/F9d-tarama.py --ozet     # yalnız sayılar

Desen: sürücü harfi (C:) ya da POSIX sürücü biçimi (/c), ardından ters / düz eğik çizgi (JSON kaçışlı \\\\ dahil),
"Users", ayraç ve harfle başlayan bir kullanıcı adı. Kullanıcı adı desende sabit değildir (herhangi bir ad yakalanır);
çıktıda maskelenir. Zaten kısaltılmış "C:\\Users\\..." biçimi kullanıcı adı taşımadığı için eşleşmez.

Ek olarak TAKMA_AD ortam değişkeni verilirse aynı dosya kümesinde büyük/küçük harf duyarsız takma ad sayımı yapılır;
ad hiçbir yere basılmaz, yalnız dosya listesi ve sayı basılır.

Son olarak README'deki sayılar (rehber, demo, boy, "Güncel tasarım" tablosu, baskı, maliyet) kaynak JSON'larla karşılaştırılır;
her satırın anahtar yolu basılır. Bütün dosyalar çalışma ağacından okunur (HEAD'den değil).

Çıkış: 0 = yazılabilir alanda yerel yol 0 ve README = JSON; 1 = eşleşme ya da README uyuşmazlığı; 2 = git çalışmadı.
"""
import fnmatch
import glob
import json
import os
import re
import subprocess
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.normpath(os.path.join(BURASI, "..", ".."))
FC_DIZIN = os.path.join(KOK, "tasarim", "freecad")

ON_SUZGEC = "users"   # git grep -i -F ön süzgeci: "Users" geçen her satır; kesin eşleşme PY_DESEN ile
PY_DESEN = re.compile(r"(?i)(?:^|(?<=[^A-Za-z]))(?:[A-Za-z]:|/[a-z])(?:\\\\|\\|/)+Users(?:\\\\|\\|/)+([A-Za-z][A-Za-z0-9._-]*)")

DOKUNULMAZ_ONEK = ["kod/", "tubitak-2209b/", "kvkk/", "rapor/", "raporlar/", "tasarim/solidworks/",
                   "tasarim/freecad/lale158/kafa-yerlesim/kaynak/"]
DOKUNULMAZ_DOSYA = ["CLAUDE.md", "planlama/d158/karar-kuyrugu.md", "planlama/dongu-158.md"]
PARALEL_ONEK = ["rehber/", "tasarim/freecad/rehber/", "planlama/rehber/", "tasarim/cad/"]
PARALEL_DOSYA = ["tasarim/Robot-Tasarim-Demosu.html"]
PARALEL_DESEN = ["planlama/d158/F7c-*"]
# Yolu ürettiği HTML'e yazan betik: yolu değiştirmek çıktıyı değiştirir (brief: "değişiklik çıktıyı değiştirmiyorsa düzelt").
URETICI_BETIK = {"tasarim/freecad/taslak-170/taslak_rapor.py"}
# Bir betiğin ürettiği belge (elle değil, yeniden üretimle değişir).
URETILMIS_BELGE = {"tasarim/freecad/taslak-170/rapor.html"}


def tarama_kaynaklari():
    """carpisma_kos.kaynak_listesi() ile aynı kural (KAYNAK_SABIT + *_lib.py, */*_lib.py), depo köküne göre."""
    sys.path.insert(0, FC_DIZIN)
    try:
        import carpisma_kos  # FreeCAD import etmez
        liste = carpisma_kos.kaynak_listesi()
    finally:
        sys.path.pop(0)
    return {"tasarim/freecad/" + r for r in liste}


def tur(yol):
    uz = os.path.splitext(yol)[1].lower()
    if uz == ".json":
        return "JSON"
    if uz in (".py", ".bat", ".sh", ".ps1", ".js", ".fcmacro"):
        return "betik"
    if "/yavaslik/prof-" in yol or yol in URETILMIS_BELGE:
        return "üretilmiş çıktı"
    return "belge"


def alan(yol, kaynaklar):
    if yol in DOKUNULMAZ_DOSYA or os.path.basename(yol) == "maliyet.json" or any(yol.startswith(o) for o in DOKUNULMAZ_ONEK):
        return "dokunulmaz"
    if yol in PARALEL_DOSYA or any(yol.startswith(o) for o in PARALEL_ONEK) or any(fnmatch.fnmatch(yol, d) for d in PARALEL_DESEN):
        return "paralel alan"
    if yol in kaynaklar:
        return "tarama kaynağı"
    if yol in URETICI_BETIK:
        return "üretici betik"
    t = tur(yol)
    if t == "JSON":
        return "üretilmiş JSON"
    if t == "üretilmiş çıktı":
        return "üretilmiş çıktı"
    if yol == "README.md" or yol.startswith("planlama/d158/"):
        return "yazılabilir"
    if t == "betik":
        return "yazılabilir"          # tarama kaynağı olmayan betik (yalnız yol değişikliği)
    return "brief listesinde yok"


def git_grep(desen, harf_duyarsiz=True, sabit=False):
    komut = ["git", "-C", KOK, "grep", "-n", "-I"]
    if harf_duyarsiz:
        komut.append("-i")
    komut += ["-F", "-e", desen] if sabit else ["-E", "-e", desen]
    s = subprocess.run(komut, capture_output=True)
    if s.returncode not in (0, 1):
        raise RuntimeError(s.stderr.decode("utf-8", "replace"))
    satirlar = []
    for ham in s.stdout.decode("utf-8", "replace").splitlines():
        yol, no, metin = ham.split(":", 2)
        satirlar.append((yol, int(no), metin))
    return satirlar


def ek_dosyalar():
    """Henüz izlenmeyen kendi paket dosyalarım (planlama/d158/F9d-*): commit'e girecekleri için onlar da taranır."""
    out = []
    for p in sorted(glob.glob(os.path.join(BURASI, "F9d-*"))):
        yol = os.path.relpath(p, KOK).replace(os.sep, "/")
        with open(p, "rb") as f:
            veri = f.read()
        if b"\0" in veri:
            continue
        for i, satir in enumerate(veri.decode("utf-8", "replace").splitlines(), 1):
            out.append((yol, i, satir))
    return out


def maskele(metin):
    return PY_DESEN.sub(lambda m: m.group(0)[: m.start(1) - m.start(0)] + "<kullanıcı>", metin)


def _tr(n):
    """1192 -> '1.192' (README binlik ayracı)."""
    return "{:,}".format(int(n)).replace(",", ".")


def _s(x, ondalik=0, isaret=False):
    """Türkçe sayı: 25720.55 -> '25.720,55'; eksi işareti README'deki gibi U+2212; isaret=True ise artıya '+'."""
    t = "{:,.{o}f}".format(abs(x), o=ondalik).replace(",", "_").replace(".", ",").replace("_", ".")
    return ("−" if x < 0 else ("+" if isaret and x > 0 else "")) + t


def _bom(rel):
    """robot-bom.csv (';' ayraçlı, BOM'lu): {kalem: (adet, toplam_kutle_g)}"""
    import csv
    with open(os.path.join(KOK, *rel.split("/")), encoding="utf-8-sig", newline="") as f:
        return {r["Kalem"]: (float(r["Adet"]), float(r["Toplam kutle (g)"])) for r in csv.DictReader(f, delimiter=";")}


def _maliyet(md):
    """planlama/adim5/maliyet_toplam.py ve demo sayfasıyla aynı kural (V3, yazıcı, yedek dahil, %pay)."""
    def on(it, kosullu=False):
        s = it.get("secenek")
        if s and s != md.get("baski", "yazici") and not (kosullu and s == "kosullu"):
            return False
        return not it.get("ver") or "v3" in it["ver"].split(",")
    p = 1 + md["pay"]
    ara = sum(it["adet"] * it["tl"] for it in md["kalemler"] if on(it))
    araK = sum(it["adet"] * it["tl"] for it in md["kalemler"] if on(it, True))
    elde = sum(it["adet"] * it["tl"] for it in md["kalemler"] if on(it) and it.get("elde"))
    return {"genel": ara * p, "kosullu": araK * p, "elde_dusulmus": (ara - elde) * p,
            "ara_elde": ara - elde}


def _yuz(x, adim=100):
    """≈ yuvarlama: 118666 -> 118700"""
    return int(round(x / adim) * adim)


def readme_kontrol():
    """README'deki sayılar kaynak JSON'larla aynı mı? Her satır: README metni, kaynak, anahtar, değer, README'de var mı.
    Dosyalar ÇALIŞMA AĞACINDAN okunur (HEAD'den değil): README ile JSON'un o anki hâli karşılaştırılır."""
    def js(rel):
        with open(os.path.join(KOK, *rel.split("/")), encoding="utf-8") as f:
            return json.load(f)
    with open(os.path.join(KOK, "README.md"), encoding="utf-8") as f:
        rd = f.read()
    kj = "planlama/rehber/kontrol.json"
    k = js(kj)
    lk = "tasarim/freecad/lale158/lale158-kontrol.json"
    boy = js(lk)["toplam_boy_mm"]
    esleme = k["yazdir"]["sayfa_esleme"]
    son_sayfa = max(max(v) for v in esleme.values())
    with open(os.path.join(KOK, "tasarim", "Robot-Tasarim-Demosu.html"), encoding="utf-8") as f:
        demo = f.read()
    m = re.search(r'<script id="kaynak"[^>]*>(.*?)</script>', demo, re.S)
    dk = json.loads(m.group(1))
    MA, UI = "tasarim/freecad/montaj/montaj-analiz.json", "tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json"
    KA, UO = "tasarim/freecad/kafa/kafa-analiz.json", "tasarim/freecad/lale158/kafa-yerlesim/uygulama-olcum.json"
    YI, BA = "planlama/y2/Y2b-ivme.json", "tasarim/freecad/lale158/baski-analiz.json"
    ES, BOM = "kod/ortak/eklem_sinirlari.json", "tasarim/freecad/montaj/robot-bom.csv"
    ML, SP = "planlama/maliyet.json", "planlama/d158/F8a-siparis.json"
    ma, ui, ka, uo, yi, ba, es = js(MA), js(UI), js(KA), js(UO), js(YI), js(BA), js(ES)
    bom = _bom(BOM)
    sigma = [a for a in bom if a.startswith("Sigma") and "1115.5 mm" in a]
    aku = [a for a in bom if "Victron" in a]
    am = ui["ev"]["am"]
    bt = ba["toplam"]
    iv = es["teker"]["ivme_sinir_m_s2"]
    ml = _maliyet(js(ML))
    qled = [s for s in js(SP)["kalemler"] if s.get("ad") == 'Kafa ekranı 10,1" QLED'][0]["birincil"]["fiyat"]
    qled_genel = (ml["ara_elde"] + qled) * (1 + js(ML)["pay"])
    satirlar = [
        # rehber + demo (F9d madde 3)
        ("%s adım" % k["ozet"]["adim"], kj, "ozet.adim", k["ozet"]["adim"]),
        ("%s parça" % _tr(k["ozet"]["parca_rehber"]), kj, "ozet.parca_rehber", k["ozet"]["parca_rehber"]),
        ("(%s sayfa)" % k["yazdir"]["pdf_sayfa"], kj, "yazdir.pdf_sayfa (sayfa_esleme son sayfa %d)" % son_sayfa, k["yazdir"]["pdf_sayfa"]),
        ("%s JSON anahtarından" % len(dk["anahtarlar"]), "tasarim/Robot-Tasarim-Demosu.html", "script#kaynak anahtarlar (say)", len(dk["anahtarlar"])),
        ("boy %s mm" % _tr(boy), lk, "toplam_boy_mm", boy),
        ("**%s mm**" % _s(boy, 1), lk, "toplam_boy_mm (MA boy_mm %s)" % ma["boy_mm"], boy),
        # "Güncel tasarım" tablosu (düzeltme turu 1, O-2: her sayı tek tek)
        ("gövde direği %s mm" % _s(float(sigma[0].split(", ")[-1].split()[0]), 1), BOM, "Kalem '%s'" % sigma[0], len(sigma)),
        ("merkezi y %s mm" % _s(ma["s3_mm"]), MA, "s3_mm", ma["s3_mm"]),
        ("uzatması %s mm" % _s(ma["uzama_mm"]), MA, "uzama_mm", ma["uzama_mm"]),
        ("%s parça (MA `parca_sayisi`)" % _s(ma["parca_sayisi"]), MA, "parca_sayisi", ma["parca_sayisi"]),
        ("ana montaj %s g" % _s(ma["kutle_g"], 2), MA, "kutle_g", ma["kutle_g"]),
        ("%s g kablo payıyla" % _s(ui["kablo_payi"]["kutle_g"]), UI, "kablo_payi.kutle_g", ui["kablo_payi"]["kutle_g"]),
        ("**%s g**" % _s(ui["ev"]["kutle_g"], 1), UI, "ev.kutle_g", ui["ev"]["kutle_g"]),
        ("AM (%s; %s; %s) mm" % (_s(am[0], 2), _s(am[1], 2), _s(am[2], 2)), UI, "ev.am", am),
        ("%s mm (MA `taban_w_mm`)" % _s(ma["taban_w_mm"]), MA, "taban_w_mm", ma["taban_w_mm"]),
        ("teker izi %s mm (x ±%s" % (_s(yi["teker_hatti"]["iz_genisligi"]), _s(yi["teker_hatti"]["x"])), YI, "teker_hatti.iz_genisligi / .x",
         yi["teker_hatti"]["iz_genisligi"]),
        ("**%s kg**" % _s(bom[aku[0]][1] / 1000, 1), BOM, "Kalem '%s' toplam kütle" % aku[0][:40], bom[aku[0]][1]),
        ("pay **%s**" % _s(ui["izgara_yuk_0g"]["a_sinir_pay15"]["rampa5_geri"], 3), UI, "izgara_yuk_0g.a_sinir_pay15.rampa5_geri",
         ui["izgara_yuk_0g"]["a_sinir_pay15"]["rampa5_geri"]),
        ("düz zeminde %s" % _s(ui["izgara_yuk_0g"]["a_sinir_pay15"]["duz_geri"], 3), UI, "izgara_yuk_0g.a_sinir_pay15.duz_geri",
         ui["izgara_yuk_0g"]["a_sinir_pay15"]["duz_geri"]),
        ("DS3235 × %d, MG996R × %d" % (bom["DS3235 servo"][0], bom["MG996R servo"][0]), BOM, "Kalem 'DS3235 servo' / 'MG996R servo' adet",
         bom["DS3235 servo"][0] + bom["MG996R servo"][0]),
        ("**toplam %d servo**" % (bom["DS3235 servo"][0] + bom["MG996R servo"][0]), BOM, "DS3235 + MG996R adet",
         bom["DS3235 servo"][0] + bom["MG996R servo"][0]),
        ("Kafa grubu %s g" % _s(ka["tork"]["tilt"]["kutle_g"], 1), KA, "tork.tilt.kutle_g", ka["tork"]["tilt"]["kutle_g"]),
        ("tilt payı (±15) %s" % _s(ka["tork"]["tilt"]["pay_tilt15"], 2), KA, "tork.tilt.pay_tilt15", ka["tork"]["tilt"]["pay_tilt15"]),
        ("pan payı %s" % _s(ka["tork"]["pan"]["pay_iki_hane"], 2), KA, "tork.pan.pay_iki_hane", ka["tork"]["pan"]["pay_iki_hane"]),
        ("tilt sınırı ±%s°" % _s(es["eklemler"]["tilt"]["max"]), ES, "eklemler.tilt.min / max", es["eklemler"]["tilt"]["max"]),
        ("en az %s mm" % _s(uo["mic_hoparlor"]["poz_min_mm"], 1), UO, "mic_hoparlor.poz_min_mm", uo["mic_hoparlor"]["poz_min_mm"]),
        ("ivme ve fren ≤ %s m/s²" % _s(iv["rampa_surus"], 1), ES, "teker.ivme_sinir_m_s2.rampa_surus / rampa_fren", iv["rampa_fren"]),
        ("ivme ≤ %s, fren ≤ %s m/s²" % (_s(iv["duz_surus"], 1), _s(iv["duz_fren"], 1)), ES, "teker.ivme_sinir_m_s2.duz_surus / duz_fren",
         iv["duz_fren"]),
        ("S2 ≥ %s°" % _s(es["eklemler"]["r_s2"]["min"], 0, True), ES, "eklemler.r_s2.min (= l_s2.min %s)" % es["eklemler"]["l_s2"]["min"],
         es["eklemler"]["r_s2"]["min"]),
        ("| Baskı | %d parça (%d'ü destekli)" % (bt["adet"], bt["destekli_adet"]), BA, "toplam.adet / toplam.destekli_adet", bt["adet"]),
        ("1,58 m, %d parça; 09.11" % bt["adet"], BA, "toplam.adet (klasör tablosu)", bt["adet"]),
        ("destek dahil %s–%s g" % (_s(bt["toplam_g"][0], 1), _s(bt["toplam_g"][1], 1)), BA, "toplam.toplam_g.0 / .1", bt["toplam_g"]),
        ("%s–%s sa" % (_s(bt["sure_sa"][0], 1), _s(bt["sure_sa"][1], 2)), BA, "toplam.sure_sa.0 / .1", bt["sure_sa"]),
        ("**≈ %s TL**" % _s(_yuz(ml["genel"])), ML, "hesap: genel (V3, yazıcı, yedek, %%15) = %.2f" % ml["genel"], ml["genel"]),
        ("koşullularla ≈ %s" % _s(_yuz(ml["kosullu"])), ML, "hesap: kosullu dahil genel = %.2f" % ml["kosullu"], ml["kosullu"]),
        ("düşülürse ≈ %s TL" % _s(_yuz(ml["elde_dusulmus"])), ML, "hesap: genel − elde (Pi 5, kart, yüz ekranı) = %.2f" % ml["elde_dusulmus"],
         ml["elde_dusulmus"]),
        ("(QLED, K32) ≈ %s" % _s(_yuz(qled_genel)), SP, "hesap: (ara − elde + S76 birincil.fiyat %.2f) × 1,15 = %.2f" % (qled, qled_genel),
         qled_genel),
        ("pay dahil) ≈ %s TL" % _s(_yuz(js(SP)["toplamlar"]["okul_butcesi_dahil_pay15"])), SP, "toplamlar.okul_butcesi_dahil_pay15",
         js(SP)["toplamlar"]["okul_butcesi_dahil_pay15"]),
    ]
    hata = 0
    if son_sayfa != k["yazdir"]["pdf_sayfa"]:
        hata += 1
    print("README sayıları:")
    for metin, kaynak, anahtar, deger in satirlar:
        var = metin in rd
        hata += 0 if var else 1
        print("  %-5s %-40s %s : %s = %s" % ("var" if var else "YOK", metin, kaynak, anahtar, deger))
    print("README sayı uyuşmazlığı: %d" % hata)
    return hata


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ozet = "--ozet" in sys.argv[1:]
    try:
        izlenen = git_grep(ON_SUZGEC, sabit=True)   # geniş ön süzgeç; kesin karar PY_DESEN ile
    except Exception as e:  # noqa: BLE001
        print("git grep çalışmadı:", e)
        return 2
    izlenen_yollar = {y for y, _, _ in izlenen}
    ek = [(y, n, m) for (y, n, m) in ek_dosyalar() if y not in izlenen_yollar and PY_DESEN.search(m)]
    kaynaklar = tarama_kaynaklari()
    eslesme = [(y, n, m) for (y, n, m) in izlenen + ek if PY_DESEN.search(m)]

    sayim = {}
    dosyalar = {}
    for y, n, m in eslesme:
        a = alan(y, kaynaklar)
        sayim[a] = sayim.get(a, 0) + 1
        dosyalar.setdefault(a, set()).add(y)
    if not ozet:
        for y, n, m in eslesme:
            print("%s:%d\t%s\t%s\t%s" % (y, n, tur(y), alan(y, kaynaklar), maskele(m.strip())[:160]))
        print()
    toplam = len(eslesme)
    print("Yerel kullanıcı yolu: %d satır, %d dosya (izlenen + F9d-*)" % (toplam, len({y for y, _, _ in eslesme})))
    for a in sorted(sayim):
        print("  %-22s %3d satır  %3d dosya" % (a, sayim[a], len(dosyalar[a])))
    yaz = sayim.get("yazılabilir", 0)
    print("Yazılabilir alanda: %d" % yaz)

    ad = os.environ.get("TAKMA_AD", "").strip()
    if ad:
        ta = git_grep(ad, sabit=True)
        say = {}
        for y, _, _ in ta:
            say[y] = say.get(y, 0) + 1
        print()
        print("Takma ad (izlenen, harf duyarsız): %d satır, %d dosya" % (len(ta), len(say)))
        if not ozet:
            for y in sorted(say):
                print("  %s\t%d" % (y, say[y]))
    print()
    rh = readme_kontrol()
    return 1 if (yaz or rh) else 0


if __name__ == "__main__":
    sys.exit(main())
