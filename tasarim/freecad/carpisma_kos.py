# carpisma.py bolumlu kosu surucusu ve birlestirici (sistem Python'u; FreeCAD import etmez, carpisma.py de bunu import eder).
# Her bolum ayri bir freecadcmd surecinde, SIRAYLA kosar (bellek her bolumden sonra isletim sistemine doner), sonucunu
# carpisma-bolum/<bolum>.json'a yazar; sonunda birlestir() tam carpisma-sonuc.json'u uretir.
#   python carpisma_kos.py                    -> tum bolumler + birlestirme (~1,5-2 saat)
#   python carpisma_kos.py kafa_sag taban     -> yalniz bu bolumler + birlestirme (digerleri onceki dosyalarindan; not edilir)
#   python carpisma_kos.py birlestir          -> yalniz birlestirme
#   python carpisma_kos.py kontrol            -> sonuc eskidi mi? (izlenen dosyalarin ozetleri kayitla karsilastirilir; eskiyse cikis kodu 1)
# Gunluk: %TEMP%/carpisma-<bolum>.log
import os, sys, json, time, hashlib, datetime, subprocess, glob, html

HERE = os.path.dirname(os.path.abspath(__file__))
BOLUM_DIZIN = os.path.join(HERE, "carpisma-bolum")
SONUC = os.path.join(HERE, "carpisma-sonuc.json")
BOLUMLER = ["statik", "omuz", "kol_sag", "kol_sol", "kolkol", "kafa_sabit", "kafa_sag", "kafa_sol", "taban"]
KISALTMA = {"kol": ["kol_sag", "kol_sol"], "kafa": ["kafa_sabit", "kafa_sag", "kafa_sol"], "hepsi": BOLUMLER}
_SABIT = ["iskelet", "omuz_sag", "omuz_sol", "kabuk", "taban"]
GEREK_MODUL = {
    "statik": ["iskelet", "omuz_sag", "omuz_sol", "kabuk", "dirsek_sag", "dirsek_sol", "kafa", "taban"],
    "omuz": _SABIT,                                   # omuz pozlari x sabit moduller (iskelet, kabuk, taban)
    "kol_sag": _SABIT + ["dirsek_sag"], "kol_sol": _SABIT + ["dirsek_sol"],
    "kolkol": ["omuz_sag", "omuz_sol", "dirsek_sag", "dirsek_sol"],
    "kafa_sabit": _SABIT + ["kafa"],
    "kafa_sag": ["omuz_sag", "dirsek_sag", "kafa"], "kafa_sol": ["omuz_sol", "dirsek_sol", "kafa"],
    "taban": ["iskelet", "omuz_sag", "omuz_sol", "kabuk", "dirsek_sag", "dirsek_sol", "kafa", "taban"],
}
# Sonucun eskidigini anlamak icin izlenen dosyalar (md5 ozeti sonuc dosyasina 'kaynak' olarak yazilir). Geometriyi ya da taramayi
# etkileyen her sey burada olmali: kosucu, arayuz, ortak/modul kutuphaneleri (*_lib.py), sigma kesiti, modul parca betikleri ve
# kafa taramasinin okudugu kafa/kafa-analiz.json (yasak bolge / eklem verisi).
KAYNAK_SABIT = ["carpisma.py", "arayuz.py", "ortak_lib.py", "sigma_profil.py",
                "iskelet/iskelet_parcalar.py", "omuz/omuz_parcalar.py", "kabuk/kabuk_parcalar.py",
                "dirsek/dirsek_parcalar.py", "kafa/kafa_parcalar.py", "taban/taban_parcalar.py", "kafa/kafa-analiz.json"]


def kaynak_listesi():
    """Sabit liste + tum *_lib.py dosyalari (kok ve modul klasorleri; yeni kutuphane kendiliginden izlenir)."""
    out = list(KAYNAK_SABIT)
    for desen in ("*_lib.py", os.path.join("*", "*_lib.py")):
        for p in sorted(glob.glob(os.path.join(HERE, desen))):
            r = os.path.relpath(p, HERE).replace(os.sep, "/")
            if r not in out:
                out.append(r)
    return out


KAYNAK = kaynak_listesi()
FC = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "FreeCAD 1.1", "bin", "freecadcmd.exe")
BASLATICI = r"C:\Users\Victus\.robot-cad\run_fc.py"


def bolum_coz(metin):
    out = []
    for b in [x.strip().lower() for x in metin.replace(" ", ",").split(",") if x.strip()]:
        for x in KISALTMA.get(b, [b]):
            if x not in BOLUMLER:
                raise SystemExit("bilinmeyen bolum: %s (gecerli: %s, kol, kafa, hepsi)" % (x, ", ".join(BOLUMLER)))
            if x not in out:
                out.append(x)
    return sorted(out, key=BOLUMLER.index)


def bolum_dosyasi(b):
    return os.path.join(BOLUM_DIZIN, "%s.json" % b)


def kaynak_ozeti():
    """Girdi dosyalarinin kisa ozeti (md5, 10 hane): birlestirmede tum bolumlerin ayni kaynakla kostugu dogrulanir."""
    out = {}
    for f in kaynak_listesi():
        p = os.path.join(HERE, f)
        out[f] = hashlib.md5(open(p, "rb").read()).hexdigest()[:10] if os.path.exists(p) else None
    return out


def _oku(b):
    f = bolum_dosyasi(b)
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else None


def eskime(sonuc=None):
    """Sonuc dosyasi eskidi mi? Kayitli 'kaynak' ozetleri bugunku dosyalarla karsilastirilir.
    Doner: dict(eski, degisen, kayitta_yok, eski_bolumler, sonuc_yok). 'kayitta_yok' = izleme listesine sonradan eklenmis dosya
    (kosu onun eski halini gormus olabilir; tam kosu sonrasi temizlenir). eski_bolumler: kendi kaynak kaydi bugunkunden farkli bolumler."""
    guncel = kaynak_ozeti()
    if sonuc is None:
        if not os.path.exists(SONUC):
            return dict(eski=True, degisen=[], kayitta_yok=[], eski_bolumler=[], sonuc_yok=True)
        sonuc = json.load(open(SONUC, encoding="utf-8"))
    kayit = sonuc.get("kaynak") or {}
    degisen = sorted(f for f, h in guncel.items() if f in kayit and kayit[f] != h)
    yok = sorted(f for f in guncel if f not in kayit)
    eski_b = []
    for b in BOLUMLER:
        v = _oku(b)
        if v is None:
            continue
        kb = v.get("kaynak") or {}
        if any(kb.get(f) != h for f, h in guncel.items()):
            eski_b.append(b)
    return dict(eski=bool(degisen or yok or eski_b or not kayit), degisen=degisen, kayitta_yok=yok, eski_bolumler=eski_b, sonuc_yok=False)


def eskime_metni(e=None):
    """Kisa uyari metni (eskimediyse bos dize)."""
    e = e or eskime()
    if not e["eski"]:
        return ""
    if e["sonuc_yok"]:
        return "carpisma-sonuc.json yok: modüller arası tarama koşulmadı."
    parca = []
    if e["degisen"]:
        parca.append("kosudan sonra degisen dosyalar: " + ", ".join(e["degisen"]))
    if e["kayitta_yok"]:
        parca.append("kosu kaydinda ozeti olmayan (izlemeye sonradan eklenen) dosyalar: " + ", ".join(e["kayitta_yok"]))
    if e["eski_bolumler"]:
        parca.append("kaynagi eskimis bolumler: " + ", ".join(e["eski_bolumler"]))
    return ("UYARI: carpisma-sonuc.json eskimis olabilir; " + "; ".join(parca) +
            ". Rapordaki cakisma/bosluk sayilari bu degisikliklerden once olculdu; 'python carpisma_kos.py' ile yeniden kosun.")


def eskime_html():
    """Rapor betikleri icin HTML uyari kutusu (eskimediyse bos dize). Satir ici stil: her raporun kendi CSS'inden bagimsiz."""
    m = eskime_metni()
    if not m:
        return ""
    print(m, file=sys.stderr)
    return ("<div style='border:2px solid #c0392b;background:rgba(192,57,43,.12);border-radius:8px;padding:10px 14px;margin:12px 0'>"
            "<b>Çakışma taraması eskimiş olabilir.</b> %s</div>" % html.escape(m))


def birlestir():
    B = {b: _oku(b) for b in BOLUMLER}
    eksik = [b for b, v in B.items() if v is None]
    S = {b: (v or {}).get("sonuc") for b, v in B.items()}
    st, om = S["statik"] or {}, S["omuz"] or {}
    kol = {t: S["kol_" + t] for t in ("sag", "sol") if S["kol_" + t]}
    kk = S["kolkol"]
    kafa = None
    if S["kafa_sabit"] or S["kafa_sag"] or S["kafa_sol"]:
        kafa = dict(next(S[b] for b in ("kafa_sabit", "kafa_sag", "kafa_sol") if S[b]))
        kafa["sabit"] = (S["kafa_sabit"] or {}).get("sabit")
        kafa["kol"] = {t: S["kafa_" + t]["kol"][t] for t in ("sag", "sol") if S["kafa_" + t]}
        kafa["kisimlar"] = [k for b in ("kafa_sabit", "kafa_sag", "kafa_sol") if S[b] for k in S[b]["kisimlar"]]
        kafa["sure_s"] = round(sum(S[b]["sure_s"] for b in ("kafa_sabit", "kafa_sag", "kafa_sol") if S[b]), 1)
    tb = S["taban"]
    statik = st.get("ev_pozu_cakisma", [])
    tarama = om.get("tarama", {})
    ks = kafa["sabit"] if kafa and kafa.get("sabit") else dict(cakisan_alt_poz_aralikta=0, cakisan_alt_poz_aralik_disi=0)
    kafa_top = (ks["cakisan_alt_poz_aralikta"] + ks["cakisan_alt_poz_aralik_disi"]
                + sum(k["cakisan_cift_aralikta"] + k["cakisan_cift_aralik_disi"] for k in (kafa or {}).get("kol", {}).values()),
                ks["cakisan_alt_poz_aralikta"] + sum(k["cakisan_cift_aralikta"] for k in (kafa or {}).get("kol", {}).values()))
    taban_top = ((tb or {}).get("toplam") or {}).get("cakisma", 0), ((tb or {}).get("toplam") or {}).get("eklem_araliginda", 0)
    toplam = dict(
        cakisma=len(statik) + sum(t["cakisan_poz"] for t in tarama.values())
        + sum(k["cakisan_tam_poz_aralikta"] + k["cakisan_tam_poz_aralik_disi"] for k in kol.values())
        + (kk["cakisan"] if kk else 0) + kafa_top[0] + taban_top[0],
        eklem_araliginda=len(statik) + sum(t["eklem_araliginda_cakisan"] for t in tarama.values())
        + sum(k["cakisan_tam_poz_aralikta"] + k["cakisan_alt_poz_aralikta"] for k in kol.values())
        + (kk["cakisan"] if kk else 0) + kafa_top[1] + taban_top[1],
        kafa=dict(toplam=kafa_top[0], eklem_araliginda=kafa_top[1]),
        taban=dict(toplam=taban_top[0], eklem_araliginda=taban_top[1]),
        not_="kol taramasinda eklem araliginda = kaba izgarada cakisan tam poz + cakisan (kaba ve ince) alt poz; kafa taramasinda "
             "cakisan kafa alt pozu (sabit hedefler) + cakisan (kol alt pozu, kafa alt pozu) cifti (iki kol); taban taramasinda "
             "kol x taban cakisan kol alt pozu (taban statik cakismalari ev pozu sayisinda)")
    kosular = sorted(set(v["kosu"] for v in B.values() if v))
    kaynaklar = [json.dumps(v.get("kaynak"), sort_keys=True) for v in B.values() if v]
    kaynak_ayni = len(set(kaynaklar)) == 1
    guncel = kaynak_ozeti()
    kaynak_guncel = kaynak_ayni and bool(kaynaklar) and json.loads(kaynaklar[0]) == guncel
    bolumler = {b: (dict(durum="tamam", kosu=v["kosu"], baslangic=v["baslangic"], bitis=v["bitis"], sure_s=v["sure_s"],
                         yukleme_s=v["yukleme_s"], tepe_bellek_mb=v["tepe_bellek_mb"], tepe_sayfa_mb=v.get("tepe_sayfa_mb"),
                         ayni_surec=v["ayni_surec"], moduller=v["moduller"]) if v else dict(durum="eksik")) for b, v in B.items()}
    tek = not eksik and len(kosular) == 1 and kaynak_ayni
    tarih = datetime.date.today().isoformat()
    if tek:
        ilk = min(v["baslangic"] for v in B.values())
        son = max(v["bitis"] for v in B.values())
        notu = ("%s: birlestirilmemis, tek seferlik tam kosu (kosu %s, %s ... %s). Dokuz bolum (%s) ayri freecadcmd sureclerinde "
                "sirayla kostu; her bolumun suresi ve tepe bellegi 'bolumler'de. Tum bolumler ayni kaynak dosyalarla (md5 ozetleri "
                "'kaynak') kostu%s; onceki kosulardan veri alinmadi." % (
                    tarih, kosular[0], ilk, son, ", ".join(BOLUMLER), "" if kaynak_guncel else " (UYARI: kaynak dosyalar kosudan sonra degisti)"))
    else:
        notu = ("%s: EKSIK / KARISIK birlestirme: eksik bolum %s; kosu kimlikleri %s; kaynak ayni: %s. Tam sonuc icin "
                "'python carpisma_kos.py' ile tum bolumleri yeniden kos." % (tarih, eksik or "yok", kosular, kaynak_ayni))
    out = dict(
        moduller=st.get("moduller"), ayrilmis_bolge=st.get("ayrilmis_bolge"), arayuz_uyumu=st.get("arayuz_uyumu"),
        ev_pozu_cakisma=statik, ev_pozu_kesisen_cift=st.get("ev_pozu_kesisen_cift"),
        ev_pozu_poz=st.get("ev_pozu_poz"), ev_pozu_cakisma_s2_0=st.get("ev_pozu_cakisma_s2_0"),   # K6: S2 0 yalniz bilgi
        zarf=om.get("zarf"), tarama=tarama, kol_tarama=kol, kol_kol=kk, kafa_tarama=kafa, taban_tarama=tb,
        toplam=toplam, kutle_g=st.get("kutle_g"), kutle_toplam_g=st.get("kutle_toplam_g"), agirlik_merkezi=st.get("agirlik_merkezi"),
        tolerans_mm3=0.5, sure_s=round(sum(v["sure_s"] + v["yukleme_s"] for v in B.values() if v), 1),
        bolumler=bolumler, kaynak=json.loads(kaynaklar[0]) if kaynaklar else None, tek_kosu=tek, birlestirme_notu=notu)
    json.dump(out, open(SONUC, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("birlestirildi:", SONUC, "| tek kosu:", tek, "| eksik:", eksik, "| TOPLAM cakisma", toplam["cakisma"],
          "eklem araliginda", toplam["eklem_araliginda"])
    if eskime_metni(eskime(out)):
        print(eskime_metni(eskime(out)))
    return out


def kos(bolumler):
    kosu = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    gunluk = os.environ.get("TEMP", HERE)
    os.makedirs(BOLUM_DIZIN, exist_ok=True)
    ozet = []
    for b in bolumler:
        env = dict(os.environ, FC_SCRIPT=os.path.join(HERE, "carpisma.py"), CARPISMA_BOLUM=b, CARPISMA_KOSU=kosu)
        log = os.path.join(gunluk, "carpisma-%s.log" % b)
        t = time.time()
        print("[%s] %s basladi (gunluk %s)" % (datetime.datetime.now().strftime("%H:%M:%S"), b, log), flush=True)
        with open(log, "w", encoding="utf-8", errors="replace") as f:
            rc = subprocess.call([FC, BASLATICI], env=env, stdout=f, stderr=subprocess.STDOUT)
        v = _oku(b)
        ok = v is not None and v.get("kosu") == kosu
        ozet.append((b, rc, ok, round(time.time() - t), v and v.get("tepe_bellek_mb")))
        print("[%s] %s bitti: rc %s, sonuc %s, %d s, tepe bellek %s MB" % (
            datetime.datetime.now().strftime("%H:%M:%S"), b, rc, "yazildi" if ok else "YOK", time.time() - t,
            v and v.get("tepe_bellek_mb")), flush=True)
    birlestir()
    return ozet


if __name__ == "__main__":
    arg = sys.argv[1:]
    if arg == ["birlestir"]:
        birlestir()
    elif arg == ["kontrol"]:
        m = eskime_metni()
        print(m or "carpisma-sonuc.json guncel: izlenen %d dosyanin ozetleri kayitla ayni." % len(kaynak_listesi()))
        sys.exit(1 if m else 0)
    else:
        kos(bolum_coz(",".join(arg) or "hepsi"))
