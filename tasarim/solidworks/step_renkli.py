# Lale: FreeCAD montajini (FCStd) SolidWorks'te renkli acilacak STEP AP214 dosyasina cevirir.
#
# Kullanim (normal Python ile; FreeCAD'i kendisi bulup arka planda, pencere acmadan calistirir):
#   python step_renkli.py --kaynak tasarim/freecad/taslak-170 --cikti tasarim/solidworks/Lale-taslak-170-renkli.step
#   python step_renkli.py --kaynak <klasor veya .FCStd> --cikti <yol.step> [--ad "Lale 170 taslak"] [--freecad <freecad.exe>]
#
# Ne yapar: kaynak FCStd'deki Assembly'nin alt gruplarini (App::Part) ve her Part::Feature parcayi aynen korur (Label = STEP urun
# adi), parcanin "Renk" ozelligindeki anahtari RENK tablosuyla RGB'ye cevirip gorunum nesnesine verir, ImportGui.export ile
# renkli STEP yazar, sonra STEP'i yeni belgeye geri alip parca sayisi / renk dagilimi / ad / hacim / sinir kutusu kontrolu yapar.
# Not: headless freecadcmd ve Import.export renkleri atar; renk icin GUI'li freecad.exe (offscreen) + ImportGui sarttir.
# Renk tablosu ve kaynaklari: renkler.md (ayni klasor). Tabloyu degistirirsen renkler.md'yi de guncelle.
#
# Cikis kodu: 0 = dogrulama gecti, 1 = hata, 2 = dogrulama basarisiz. Rapor: <cikti>.rapor.json
import os, sys, json, glob, subprocess, tempfile, time, collections, re

# ---------------------------------------------------------------- renk tablosu (0-1 RGB)
# Birincil kaynak: tasarim/freecad/taslak-170/taslak_gorsel.py RENK (taslak-170 ve Y2a ayni anahtarlari kullanir).
RENK = {
    "alu": (0.78, 0.80, 0.83), "alu2": (0.55, 0.60, 0.68), "celik": (0.50, 0.52, 0.56), "celik2": (0.86, 0.66, 0.22),
    "siyah": (0.13, 0.13, 0.14), "petg": (0.96, 0.55, 0.13), "petg2": (0.18, 0.52, 0.86), "pirinc": (0.86, 0.66, 0.22),
    "kabuk": (0.85, 0.87, 0.90), "gri": (0.60, 0.60, 0.60), "pcb": (0.10, 0.45, 0.25), "pcb_k": (0.10, 0.45, 0.25),
    "pcb_m": (0.15, 0.30, 0.60), "ahsap": (0.80, 0.65, 0.45), "aku": (0.25, 0.30, 0.35), "kirmizi": (0.85, 0.15, 0.12),
    "koyu": (0.25, 0.25, 0.28), "lastik": (0.10, 0.10, 0.10), "motor": (0.62, 0.64, 0.68), "naylon": (0.92, 0.92, 0.88),
    "vizor": (0.05, 0.05, 0.07), "kablo": (0.90, 0.30, 0.20),
}
# taslak tablosunda olmayan ama projede baska yerde tanimli anahtarlar: tasarim/freecad/taban/taban_gorsel.py RENK
RENK_TABAN = {
    "pcb_y": (0.10, 0.45, 0.20),
    "k_kirmizi": (0.95, 0.05, 0.05), "k_siyah": (0.05, 0.05, 0.05), "k_turuncu": (1.0, 0.50, 0.0), "k_sari": (0.95, 0.85, 0.05),
    "k_mavi": (0.10, 0.45, 1.0), "k_yesil": (0.05, 0.75, 0.20), "k_mor": (0.60, 0.20, 0.80), "k_beyaz": (0.92, 0.92, 0.92),
}
VARSAYILAN_ANAHTAR = "gri"      # hicbir tabloda olmayan anahtar -> gri (raporda "varsayilan" olarak sayilir)


def renk_coz(anahtar):
    """-> (rgb, kaynak) ; kaynak: 'taslak' | 'taban' | 'varsayilan'"""
    if anahtar in RENK:
        return RENK[anahtar], "taslak"
    if anahtar in RENK_TABAN:
        return RENK_TABAN[anahtar], "taban"
    return RENK[VARSAYILAN_ANAHTAR], "varsayilan"


def rgb8(c):
    return tuple(int(round(x * 255)) for x in c[:3])


# ---------------------------------------------------------------- baslatici (normal Python)
def freecad_bul(ipucu=None):
    adaylar = []
    if ipucu:
        adaylar.append(ipucu)
    if os.environ.get("FREECAD_BIN"):
        adaylar.append(os.environ["FREECAD_BIN"])
    for kok in (os.environ.get("LOCALAPPDATA", "") + "/Programs", os.environ.get("ProgramFiles", "C:/Program Files")):
        adaylar += sorted(glob.glob(os.path.join(kok, "FreeCAD*", "bin", "freecad.exe")), reverse=True)
    for a in adaylar:
        if a and os.path.isfile(a):
            return a
    raise SystemExit("freecad.exe bulunamadi; --freecad ile ver ya da FREECAD_BIN ayarla")


def baslat(argv):
    import argparse
    ap = argparse.ArgumentParser(description="FreeCAD montajini renkli STEP AP214'e cevir ve dogrula")
    ap.add_argument("--kaynak", required=True, help="FCStd'nin klasoru ya da dogrudan .FCStd yolu")
    ap.add_argument("--cikti", required=True, help="yazilacak .step yolu")
    ap.add_argument("--dosya", help="klasorde birden fazla FCStd varsa kullanilacak dosya adi")
    ap.add_argument("--ad", help="STEP kok montaj adi (varsayilan: Assembly etiketi)")
    ap.add_argument("--grup", help="yalniz etiketi bu metni iceren alt gruplari aktar (kucuk deneme dosyasi icin; ornek: Teker)")
    ap.add_argument("--rapor", help="JSON rapor yolu (varsayilan: gecici klasor)")
    ap.add_argument("--freecad", help="freecad.exe yolu (GUI'li; freecadcmd olmaz)")
    ap.add_argument("--zaman-asimi", type=int, default=1500, help="saniye (varsayilan 1500)")
    a = ap.parse_args(argv)
    kaynak = os.path.abspath(a.kaynak)
    cikti = os.path.abspath(a.cikti)
    os.makedirs(os.path.dirname(cikti), exist_ok=True)
    fc = freecad_bul(a.freecad)
    tmp = tempfile.mkdtemp(prefix="step_renkli_")
    rapor_yol = os.path.abspath(a.rapor) if a.rapor else os.path.join(tmp, "rapor.json")
    # freecad.exe yolunda "u"/"ü" gibi harf olan betigi dogrudan acinca coker: ASCII bir sarmalayici verilir
    sarmal = os.path.join(tmp, "sarmal.py")
    with open(sarmal, "w", encoding="utf-8") as f:
        f.write("import os\np = os.environ['STEP_RENKLI_BETIK']\n"
                "exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, '__name__': '__main__'})\n")
    env = dict(os.environ)
    env.update(QT_QPA_PLATFORM="offscreen", STEP_RENKLI_BETIK=os.path.abspath(__file__),
               STEP_RENKLI_ARG=json.dumps(dict(kaynak=kaynak, cikti=cikti, dosya=a.dosya, ad=a.ad, grup=a.grup, rapor=rapor_yol), ensure_ascii=False))
    if os.path.exists(rapor_yol):
        os.remove(rapor_yol)
    t0 = time.time()
    try:
        p = subprocess.run([fc, sarmal], env=env, cwd=tmp, timeout=a.zaman_asimi, capture_output=True)
    except subprocess.TimeoutExpired:
        print("ZAMAN ASIMI (%d s)" % a.zaman_asimi)
        return 1
    if not os.path.exists(rapor_yol):
        print("rapor yazilmadi; FreeCAD ciktisi:")
        print((p.stdout + p.stderr).decode("utf-8", "replace")[-3000:])
        return 1
    r = json.load(open(rapor_yol, encoding="utf-8"))
    print("sure %.0f s" % (time.time() - t0))
    for s in r.get("ozet", []):
        print(s)
    if r.get("hata"):
        print("HATA:", r["hata"])
        return 1
    return 0 if r.get("dogrulama_gecti") else 2


# ---------------------------------------------------------------- is parcasi (FreeCAD GUI icinde, offscreen)
def isci():
    import FreeCAD as App
    import FreeCADGui as Gui
    import Part
    arg = json.loads(os.environ["STEP_RENKLI_ARG"])
    rapor = dict(ozet=[], hata=None, dogrulama_gecti=False)
    ozet = rapor["ozet"].append
    try:
        _isci(arg, rapor, ozet, App, Gui, Part)
    except Exception:
        import traceback
        rapor["hata"] = traceback.format_exc()
    json.dump(rapor, open(arg["rapor"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sys.stdout.flush()
    os._exit(0)


def _isci(arg, rapor, ozet, App, Gui, Part):
    import ImportGui
    kaynak = arg["kaynak"]
    if os.path.isdir(kaynak):
        fc = sorted(glob.glob(os.path.join(kaynak, "*.FCStd")))
        if arg.get("dosya"):
            fc = [f for f in fc if os.path.basename(f).lower() == arg["dosya"].lower()]
        elif len(fc) > 1:
            es = [f for f in fc if os.path.splitext(os.path.basename(f))[0].lower() == os.path.basename(kaynak.rstrip("/\\")).lower()]
            fc = es or fc
        if len(fc) != 1:
            raise RuntimeError("klasorde tek FCStd secilemedi, --dosya ver: %s" % [os.path.basename(f) for f in fc])
        kaynak = fc[0]
    ozet("kaynak FCStd: %s" % kaynak)

    # STEP AP214 (ayar acikca verilir), birim mm
    App.ParamGet("User parameter:BaseApp/Preferences/Mod/Part/STEP").SetString("Scheme", "AP214")
    App.ParamGet("User parameter:BaseApp/Preferences/Mod/Part/General").SetInt("UnitsSchema", 0)

    doc = App.openDocument(kaynak)
    gd = Gui.getDocument(doc.Name)
    asm = next((o for o in doc.Objects if o.TypeId == "Assembly::AssemblyObject"), None)
    if asm is not None:
        kokler = [o for o in asm.Group if o.TypeId in ("App::Part", "Part::Feature")]
        kok_ad = arg.get("ad") or asm.Label
    else:
        kokler = [o for o in doc.Objects if o.TypeId in ("App::Part", "Part::Feature") and not o.InList]
        kok_ad = arg.get("ad") or doc.Label
    if arg.get("grup"):
        kokler = [k for k in kokler if arg["grup"].lower() in k.Label.lower()]
    if not kokler:
        raise RuntimeError("disa aktarilacak grup/parca yok")
    doc.Label = kok_ad

    # parcalar: agacin altindaki tum Part::Feature (kokler ve torunlari)
    gorulen, parcalar = set(), []

    def gez(o):
        if o.Name in gorulen:
            return
        gorulen.add(o.Name)
        if o.TypeId == "Part::Feature":
            parcalar.append(o)
        for c in getattr(o, "Group", []):
            gez(c)
    for k in kokler:
        gez(k)

    beklenen_renk, beklenen_ad, kaynaklar, anahtar_say = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    bilinmeyen, hacim_kaynak = collections.Counter(), 0.0
    bb_kaynak = App.BoundBox()
    for o in parcalar:
        anahtar = getattr(o, "Renk", "") or VARSAYILAN_ANAHTAR
        rgb, kay = renk_coz(anahtar)
        if kay == "varsayilan":
            bilinmeyen[anahtar] += 1
        vo = gd.getObject(o.Name)
        # renk kesinlikle opak: FreeCAD 1.x'te DiffuseColor'in 4. degeri alfa (1 = opak); saydamlik ayri ozellik ve acikca 0.
        # (STEP'e SURFACE_STYLE_TRANSPARENT yalniz saydamlik > 0 ise yazilir; dogrulama asagida dosya metninde de bunu kontrol eder.)
        vo.ShapeAppearance = (App.Material(DiffuseColor=tuple(rgb) + (1.0,), Transparency=0.0),)
        vo.Transparency = 0
        vo.Visibility = True
        beklenen_renk[rgb8(rgb)] += 1
        beklenen_ad[o.Label] += 1
        kaynaklar[kay] += 1
        anahtar_say[anahtar] += 1
        hacim_kaynak += sum(s.Volume for s in o.Shape.Solids)
        bb_kaynak.add(o.Shape.BoundBox)
    for o in doc.Objects:
        if o.TypeId == "App::Part":
            gd.getObject(o.Name).Visibility = True
    ozet("parca (Part::Feature): %d, grup (App::Part): %d, koklar: %d, renk anahtari: %d, 8-bit renk: %d" % (
        len(parcalar), sum(1 for o in doc.Objects if o.TypeId == "App::Part"), len(kokler), len(anahtar_say), len(beklenen_renk)))
    ozet("renk kaynagi (parca): %s; varsayilana dusen anahtarlar: %s" % (dict(kaynaklar), dict(bilinmeyen) or "yok"))
    Gui.updateGui()

    cikti = arg["cikti"]
    if os.path.exists(cikti):
        os.remove(cikti)
    t0 = time.time()
    ImportGui.export(kokler, cikti)          # Import.export (GUI'siz yol) renkleri yazmaz
    # kok urun adi FreeCAD'de belge adindan gelir (ornek "taslak_170"); anlamli bir ada cevrilir
    with open(cikti, "r", encoding="utf-8", errors="surrogateescape", newline="") as f:
        txt = f.read()
    eski_kok = doc.Name
    kok_kayit = re.search(r"(#\d+ = PRODUCT\()'%s','%s'" % (re.escape(eski_kok), re.escape(eski_kok)), txt)
    if kok_kayit:
        yeni = kok_ad.replace("'", "")
        txt = txt[:kok_kayit.start()] + kok_kayit.group(1) + "'%s','%s'" % (yeni, yeni) + txt[kok_kayit.end():]
        with open(cikti, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
            f.write(txt)
    else:
        ozet("UYARI: kok urun adi bulunamadi (%s), degistirilmedi" % eski_kok)
    boyut = os.path.getsize(cikti)
    ozet("STEP yazildi: %s (%.1f MB, %.0f s)" % (cikti, boyut / 1048576.0, time.time() - t0))

    # ---- metin duzeyi kontrol
    sema = re.search(r"FILE_SCHEMA\(\('([^']*)'", txt)
    birim = "MILLI" if re.search(r"SI_UNIT\(\.MILLI\.,\.METRE\.\)", txt) else "?"
    n_urun = len(re.findall(r"^#\d+ = PRODUCT\(", txt, re.M))
    n_stil = len(re.findall(r"STYLED_ITEM\('color'", txt))
    n_rgb = len(set(re.findall(r"COLOUR_RGB\('[^']*',([^)]*)\)", txt.replace("\n", ""))))
    n_on = len(set(re.findall(r"DRAUGHTING_PRE_DEFINED_COLOUR\('([^']*)'\)", txt)))
    n_saydam = len(re.findall(r"SURFACE_STYLE_TRANSPARENT", txt))
    ozet("saydam stil (SURFACE_STYLE_TRANSPARENT) sayisi: %d (0 olmali)" % n_saydam)
    ozet("STEP: sema=%s, birim=%s, kok=%s, urun=%d, renk stili=%d, ayri COLOUR_RGB=%d (biri cizgi rengi), on tanimli renk=%d" % (
        sema.group(1) if sema else "?", "mm" if birim == "MILLI" else "?", kok_ad, n_urun, n_stil, n_rgb, n_on))

    # ---- geri iceri alma
    App.closeDocument(doc.Name)
    d2 = App.newDocument("GeriAl")
    ImportGui.insert(cikti, d2.Name)
    g2 = Gui.getDocument(d2.Name)
    yaprak = [o for o in d2.Objects if o.TypeId == "Part::Feature" and o.Shape and not o.Shape.isNull() and o.Shape.Solids]
    gri_renk, gri_ad = collections.Counter(), collections.Counter()
    hacim2, bb2, renksiz = 0.0, App.BoundBox(), 0
    for o in yaprak:
        vo = g2.getObject(o.Name)
        try:
            c = rgb8(vo.ShapeAppearance[0].DiffuseColor)
        except Exception:
            c = None
            renksiz += 1
        gri_renk[c] += 1
        gri_ad[o.Label] += 1
        hacim2 += sum(s.Volume for s in o.Shape.Solids)
        bb2.add(o.Shape.BoundBox)
    n_grup2 = sum(1 for o in d2.Objects if o.TypeId == "App::Part")
    # 8-bit yuvarlama / float32 farki: gelen renk, beklenen renklerden kanal basina en fazla 1 seviye farkliysa ayni sayilir
    def yakin(c):
        if c is None:
            return None
        for b in beklenen_renk:
            if max(abs(x - y) for x, y in zip(c, b)) <= 1:
                return b
        return c
    gri_renk_n = collections.Counter()
    for k, v in gri_renk.items():
        gri_renk_n[yakin(k)] += v
    gri_renk = gri_renk_n
    renk_esit = gri_renk == beklenen_renk
    # Label'lar: FreeCAD ice aktarimda "001" gibi sonek ekleyebilir; sonekleri atip say
    def temiz(c):
        out = collections.Counter()
        for k, v in c.items():
            out[re.sub(r"\d{3}$", "", k) if k not in beklenen_ad else k] += v
        return out
    ad_esit = (gri_ad == beklenen_ad) or (temiz(gri_ad) == beklenen_ad)
    hac_fark = abs(hacim2 - hacim_kaynak) / max(hacim_kaynak, 1e-9)
    bb_fark = max(abs(a - b) for a, b in ((bb2.XMin, bb_kaynak.XMin), (bb2.XMax, bb_kaynak.XMax), (bb2.YMin, bb_kaynak.YMin),
                                          (bb2.YMax, bb_kaynak.YMax), (bb2.ZMin, bb_kaynak.ZMin), (bb2.ZMax, bb_kaynak.ZMax)))
    ozet("geri alinan: parca=%d (beklenen %d), renkli parca=%d, renk grubu=%d (beklenen %d), grup=%d" % (
        len(yaprak), len(parcalar), len(yaprak) - gri_renk.get(None, 0), len([k for k in gri_renk if k]), len(beklenen_renk), n_grup2))
    ozet("kontrol: renk dagilimi %s, ad dagilimi %s, hacim farki %.2e, sinir kutusu farki %.3f mm" % (
        "ESIT" if renk_esit else "FARKLI", "ESIT" if ad_esit else "FARKLI", hac_fark, bb_fark))
    if not renk_esit:
        eksik = {k: (beklenen_renk[k], gri_renk.get(k, 0)) for k in set(beklenen_renk) | set(gri_renk) if beklenen_renk.get(k, 0) != gri_renk.get(k, 0)}
        ozet("renk farki (rgb8: beklenen, gelen): %s" % eksik)
    rapor.update(
        step=cikti, boyut_bayt=boyut, sema=sema.group(1) if sema else None, parca_kaynak=len(parcalar), parca_geri=len(yaprak),
        renkli_parca_geri=len(yaprak) - gri_renk.get(None, 0), renk_grubu_kaynak=len(beklenen_renk), renk_grubu_geri=len([k for k in gri_renk if k]),
        renk_anahtari=dict(anahtar_say), renk_kaynagi=dict(kaynaklar), varsayilana_dusen=dict(bilinmeyen), grup_geri=n_grup2,
        hacim_farki=hac_fark, sinir_kutusu_farki_mm=bb_fark,
    )
    rapor["dogrulama_gecti"] = bool(len(yaprak) == len(parcalar) and renk_esit and ad_esit and renksiz == 0 and hac_fark < 1e-4 and bb_fark < 0.01
                                    and birim == "MILLI" and n_saydam == 0 and sema and "214" in sema.group(1))
    ozet("DOGRULAMA: %s" % ("GECTI" if rapor["dogrulama_gecti"] else "BASARISIZ"))


if __name__ == "__main__":
    try:
        import FreeCAD  # noqa: F401
        icinde = True
    except ImportError:
        icinde = False
    if icinde:
        isci()
    else:
        sys.exit(baslat(sys.argv[1:]))
