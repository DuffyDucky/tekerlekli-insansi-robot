# Lale 1,70 m taslak raporu: ANALIZ bolumleri (analiz ajani, 21 Ekim 2026). taslak_rapor.py bunu import eder.
# Girdi: analiz/hesap.json (taslak_hesap.py), analiz/dogrulama.json, analiz/statik-*.json, analiz/kol_*.json, analiz/kolkol-*.json,
# analiz/kafa-*.json, analiz/kafakol_*.json (taslak_analiz.py). Dosya yoksa ilgili bolum "kosulmadi" der.
import os, json, glob, html

HERE = os.path.dirname(os.path.abspath(__file__))
AN = os.path.join(HERE, "analiz")


def _oku(ad):
    p = os.path.join(AN, ad)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def sayi(x, n=1):
    s = ("{:,.%df}" % n).format(x)
    return s.replace(",", " ").replace(".", ",").replace(" ", ".").replace("-", "−")


def esc(s):
    return html.escape(str(s))


def tablo(basliklar, satirlar, sinif=""):
    h = "<div class='tw'><table class='%s'><tr>%s</tr>" % (sinif, "".join("<th>%s</th>" % b for b in basliklar))
    for s in satirlar:
        h += "<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in s)
    return h + "</table></div>"


def pay(x, ok=2.0, uy=1.2, n=2):
    c = "ok" if x >= ok else ("uy" if x >= uy else "no")
    return "<span class='%s'>%s×</span>" % (c, sayi(x, n))


def oran(x):
    c = "ok" if x <= 0.80 else ("uy" if x <= 1.0 else "no")
    return "<span class='%s'>%%%s</span>" % (c, sayi(x * 100, 0))


H = _oku("hesap.json")
D = _oku("dogrulama.json")
ST = {int(os.path.basename(f).split("-")[-1].split(".")[0]): json.load(open(f, encoding="utf-8")) for f in glob.glob(os.path.join(AN, "statik-yeni-*.json"))}
KOL = {t: _oku("kol_%s-yeni.json" % t) for t in ("sag", "sol")}
KOLE = {t: _oku("kol_%s-eski.json" % t) for t in ("sag", "sol")}
KK = _oku("kolkol-yeni.json")
KKE = _oku("kolkol-eski.json")
KAF = _oku("kafa-yeni.json")
KAFE = _oku("kafa-eski.json")
KKL = {t: _oku("kafakol_%s-yeni.json" % t) for t in ("sag", "sol")}
KKLE = {t: _oku("kafakol_%s-eski.json" % t) for t in ("sag", "sol")}
KD = {r: _oku("kol_sag-%s-dirsek.json" % r) for r in ("yeni", "eski")}
KK0 = {r: _oku("kafakol_sag-%s-s2_0.json" % r) for r in ("yeni", "eski")}
R = H["robot"] if H else {}
SV = H["servo"] if H else {}
Y, E = R.get("yeni-444"), R.get("eski-444")
Y5 = R.get("yeni-520")


def yeni_cak_say():
    """(taslaktan gelen, mevcut tasarimdan gelen) cakisma sayilari, eklem araliginda."""
    yeni, eski = [], []
    if 444 in ST:
        for c in ST[444]["cakisma"]:
            (yeni if c["kaynak"].startswith("taslak") else eski).append(("ev pozu", c["a"], c["b"], c["hacim_mm3"]))
    for t, k in KOL.items():
        if k:
            for c in k["cakisma_ciftleri"]:
                (yeni if c["kaynak"].startswith("taslak") else eski).append(("kol %s" % t, c["parca"], c["hedef"], c["en_buyuk_mm3"]))
    if KAF:
        for c in KAF["cakisma"]:
            (yeni if c["kaynak"].startswith("taslak") else eski).append(("kafa", c["parca"], c["hedef"], c["hacim_mm3"]))
    for t, k in KKL.items():
        if k:
            for c in k["cakismalar"]:
                (yeni if c["kaynak"].startswith("taslak") else eski).append(("kafa x kol %s" % t, c["kol_parca"], c["kafa_parca"], c["hacim_mm3"]))
    if KK:
        for s in KK["tip_ozet"].values():
            pass
    return yeni, eski


# ====================================================================== karar kutusu ve kartlar
def kartlar():
    if not H:
        return []
    ys, es = SV["yeni-444"], SV["eski-444"]
    dz = Y["devrilme"]
    k = [("%s× / %s×" % (sayi(dz["izgara_en_kucuk_duz"], 2), sayi(Y5["devrilme"]["izgara_en_kucuk_duz"], 2) if Y5 else "–"),
          "devrilme payı, düz zemin, en kötü yüksüz kol pozu: taban 444 / 520 mm (125 cm: %s×; ölçüt ≥ 2)" % sayi(E["devrilme"]["izgara_en_kucuk_duz"], 2)),
         ("%s× / %s×" % (sayi(dz["izgara_en_kucuk_rampa"], 2), sayi(Y5["devrilme"]["izgara_en_kucuk_rampa"], 2) if Y5 else "–"),
          "aynısı 5° rampada + 1,5 m/s² fren (125 cm: %s×)" % sayi(E["devrilme"]["izgara_en_kucuk_rampa"], 2)),
         ("%%%s" % sayi(Y["motor"]["rampa5"]["oran"] * 100, 0),
          "teker motoru, 5° rampa + 0,5 m/s²: sürekli torkun yüzdesi (125 cm: %%%s); 0,25 m/s² ile %%%s" % (
              sayi(E["motor"]["rampa5"]["oran"] * 100, 0), sayi(Y["motor"]["rampa5_yavas"]["oran"] * 100, 0))),
         ("%s× / %s×" % (sayi(ys["kol"][0]["yuksuz_pay"], 2), sayi(ys["kol"][1]["yuksuz_pay"], 2)),
          "omuz S1 / S2 servo payı, yüksüz kol, statik (125 cm: %s× / %s×)" % (sayi(es["kol"][0]["yuksuz_pay"], 2), sayi(es["kol"][1]["yuksuz_pay"], 2))),
         ("%s× / %s×" % (sayi(ys["kafa"]["tilt"]["pay"], 2), sayi(ys["kafa"]["pan"]["pay"], 2)),
          "kafa tilt / pan servo payı, yerçekimi + ivme (125 cm: %s× / %s×)" % (sayi(es["kafa"]["tilt"]["pay"], 2), sayi(es["kafa"]["pan"]["pay"], 2)))]
    yeni, eski = yeni_cak_say()
    k.append(("%d yeni" % len(yeni), "çakışma (eklem aralığında, taslaktan gelen); mevcut tasarımdan gelen %d çift (125 cm'de de aynı)" % len(set((a, b) for _, a, b, _ in eski))))
    return k


# ====================================================================== devrilme
def devrilme():
    if not H:
        return "<div class='bos'>analiz/hesap.json yok (taslak_hesap.py koşulmadı)</div>"
    h = []
    h.append("<p>Yöntem taban raporuyla aynı (<code>taban/taban_montaj.py</code> <code>denge()</code>): eşik = g · (d · cos θ − h · sin θ) / h; d = AM'den "
             "teker temas hattına yatay uzaklık (teker merkez düzlemleri x ±%s, z ±185), h = AM yüksekliği; pay = eşik ÷ 1,5 m/s² (acil stop freni, "
             "<span class='t'>tahmini</span>). Kütle ve AM parçalardan (<code>taslak_analiz.py</code> → <code>analiz/girdi-*.json</code>), kablo payları "
             "dahil (taban 400 g + gövde uzaması 45 g, <span class='t'>tahmini</span>). 125 cm sütunu aynı betikle güncel modül betiklerinden "
             "(taban raporundaki 21,73 kg / AM y 373 değerinden 0,2 kg ağır: omuz S1 kaseti sonradan eklendi).</p>" % sayi(178, 0))
    h.append("<p><b>Ölçüt:</b> projede pay ≥ 2 yeşil, 1,2–2 uyarı (<code>taban_rapor.pay_sinif</code>, tasarım demosu). Taban raporu bunu düz zemine "
             "uyguluyor; rampa için ölçüt yok. Buradaki ölçüt: <b>düz zeminde tüm yüksüz kol pozlarında ≥ 2,0×</b> (projeninki) ve <b>5° rampada ≥ 1,5×</b> "
             "(gerekçe: rampada robot yavaş ve kollar gövdede tutulur; 1,5× = acil frende 2,25 m/s² eşik, uyarı alt sınırı 1,2'nin %25 üstü). "
             "125 cm tasarım ikisini de rahat geçiyor (en kötü 2,8× / 2,25×).</p>")
    satir = []
    keys = [k for k in ("eski-444", "yeni-444", "yeni-500", "yeni-520") if k in R]
    for i, p in enumerate(R["yeni-444"]["devrilme"]["pozlar"]):
        row = [esc(p["ad"])]
        for k in keys:
            q = R[k]["devrilme"]["pozlar"][i]
            row.append("%s / %s / %s" % (pay(q["duz"]["pay_ileri"]), pay(q["duz"]["pay_geri"]), pay(q["duz"]["pay_yan"])))
        for k in keys:
            q = R[k]["devrilme"]["pozlar"][i]
            row.append("%s / %s / %s" % (pay(q["rampa5"]["pay_ileri"], 1.5), pay(q["rampa5"]["pay_geri"], 1.5), pay(q["rampa5"]["pay_yan"], 1.5)))
        satir.append(row)
    ad = {"eski-444": "125 cm", "yeni-444": "170, 444", "yeni-500": "170, 500", "yeni-520": "170, 520"}
    row = ["<b>Izgara en kötü (yüksüz, iki kol simetrik / tek kol / zıt; S1 15°, S2, dirsek adımları)</b>"]
    for k in keys:
        iz = R[k]["devrilme"]["izgara_en_kotu"]
        row.append("%s / %s / %s" % (pay(iz["duz_ileri"]["pay"]), pay(iz["duz_geri"]["pay"]), pay(iz["duz_yan"]["pay"])))
    for k in keys:
        iz = R[k]["devrilme"]["izgara_en_kotu"]
        row.append("%s / %s / %s" % (pay(iz["rampa5_ileri"]["pay"], 1.5), pay(iz["rampa5_geri"]["pay"], 1.5), pay(iz["rampa5_yan"]["pay"], 1.5)))
    satir.append(row)
    h.append("<h3>Pay: ileri / geri / yana (düz zemin, sonra 5° rampa)</h3>")
    h.append(tablo(["Poz"] + ["Düz, %s" % ad[k] for k in keys] + ["5° rampa, %s" % ad[k] for k in keys], satir))
    sat2 = []
    for k in keys:
        r = R[k]
        ev = r["devrilme"]["ev"]
        sat2.append([ad[k], sayi(r["kutle_g"] / 1000, 2), "(%s; %s; %s)" % (sayi(r["am"][0], 1), sayi(r["am"][1], 0), sayi(r["am"][2], 1)),
                     "±%s" % sayi(r["destek_x"], 0), "%s / %s / %s" % (sayi(ev["duz"]["ileri"], 2), sayi(ev["duz"]["geri"], 2), sayi(ev["duz"]["yan"], 2)),
                     "%s / %s / %s" % (sayi(ev["rampa5"]["ileri"], 2), sayi(ev["rampa5"]["geri"], 2), sayi(ev["rampa5"]["yan"], 2)),
                     "%s° / %s° / %s°" % (sayi(ev["duz"]["egim_ileri"], 0), sayi(ev["duz"]["egim_geri"], 0), sayi(ev["duz"]["egim_yan"], 0))])
    h.append("<h3>Ev pozu: kütle, AM, eşik ivmesi (m/s²) ve statik devrilme eğimi</h3>")
    h.append(tablo(["Robot / taban", "Kütle (kg)", "AM (mm)", "Teker x", "Eşik ileri / geri / yana (düz)", "5° rampada", "Statik eğim"], sat2, "sayi"))
    # onlemler
    if H.get("onlem"):
        sat3 = []
        for o in H["onlem"]:
            if o["taban"] not in ("yeni-444", "yeni-520"):
                continue
            sat3.append([ad[o["taban"]], esc(o["onlem"]), sayi(o["kutle_g"] / 1000, 2), "%s / %s" % (sayi(o["am"][1], 0), sayi(o["am"][2], 1)),
                         " / ".join(pay(x) for x in o["izgara_duz"]), " / ".join(pay(x, 1.5) for x in o["izgara_rampa"]), oran(o["motor_rampa5_025"])])
        h.append("<h3>Önlemler (hesap; geometri değişmedi, <span class='t'>tahmini</span>)</h3>")
        h.append(tablo(["Taban", "Önlem", "Kütle (kg)", "AM y / z", "Izgara en kötü, düz (ileri / geri / yana)", "5° rampa", "Motor 5° rampa, 0,25 m/s²"], sat3))
        h.append("<p class='not'>Akü (2,8 kg, z −121) taban arka panelinde; 75 mm öne almak AM'yi z −11,6 → −3,2'ye getirir (gerçek yerleşim taban "
                 "tasarımında ayrıca çözülmeli). Balast seçeneği motor yükünü büyütür. Nextion kararı açık (göğüs ekranı 535 g, y 1.254).</p>")
    # karar
    y4, y5 = R["yeni-444"]["devrilme"], R.get("yeni-520", R["yeni-444"])["devrilme"]
    h.append("<div class='karar'><b>Karar önerisi: taban 520 mm'ye genişletilsin, ama genişletme tek başına yetmez.</b><ul>"
             "<li>Yana pay yalnız teker iziyle büyür: 444'te düz %s× (en kötü zıt kol pozunda %s×, sınırda), rampada %s×; 520'de düz %s×, rampada %s×. "
             "Ölçütü yana yönde 520 karşılıyor (rampada 1,5 için teker x ≥ ~%s mm gerekir).</li>"
             "<li><b>Asıl darboğaz ileri-geri:</b> aks arası (z ±185) değişmiyor, AM 11,6 mm geride ve 560 mm yüksekte. Geri payı en kötü pozda düz %s×, "
             "rampada %s× (520'de de aynı). Düz zemin ölçütü (≥ 2) kollar geride (S1 −45) iken kıl payı kaçıyor; rampada 1,5 tutmuyor.</li>"
             "<li>Öneri: (1) taban 520 (her yana 38 mm; 500'de de temiz, 480'de motor braketi M4'leri uzun raya biniyor: DX ≥ ~24 mm şart), "
             "(2) AM'yi öne al: akü ~75 mm öne (ya da ön-alt 1,5 kg balast), (3) yazılım: rampada kollar ev pozunda (S1 0…90, S2 ≤ 30) ve rampa ivmesi "
             "aşağıdaki motor sınırıyla. Aks arasını uzatmak (taban boyu) daha kökten çözüm ama taban/etek/iskelet yeniden.</li></ul></div>" % (
                 sayi(y4["ev"]["duz"]["pay_yan"], 2), sayi(y4["izgara_en_kotu"]["duz_yan"]["pay"], 2), sayi(y4["ev"]["rampa5"]["pay_yan"], 2),
                 sayi(y5["ev"]["duz"]["pay_yan"], 2), sayi(y5["ev"]["rampa5"]["pay_yan"], 2),
                 sayi(0.3945 * Y["am"][1] + 1, 0),
                 sayi(y4["izgara_en_kotu"]["duz_geri"]["pay"], 2), sayi(y4["izgara_en_kotu"]["rampa5_geri"]["pay"], 2)))
    return "\n".join(h)


# ====================================================================== motor
def motor():
    if not H:
        return "<div class='bos'>analiz/hesap.json yok</div>"
    keys = [k for k in ("eski-444", "yeni-444", "yeni-520") if k in R]
    ad = {"eski-444": "125 cm", "yeni-444": "170, taban 444", "yeni-520": "170, taban 520"}
    h = ["<p>Yöntem taban raporuyla aynı (<code>taban_montaj.py</code> <code>tork()</code>): F = m (a + g sin θ + Crr g cos θ), Crr 0,03, 4 motor, "
         "teker r 62,5 mm; JGB37-520 60 dev/dk durma 21 kg·cm (satıcı etiketi), sürekli = durmanın %%30'u = %s kg·cm. Yerinde dönüş "
         "<code>taban/donus_hesap.py</code> (Coulomb modeli + Wong üst sınırı), teker düzlemi genişliğe göre.</p>" % sayi(Y["motor"]["surekli_kgcm"], 1)]
    sat = []
    rows = [("Kütle (kg)", lambda m: sayi(m["kutle_kg"], 2)),
            ("Düz zemin, 0,5 m/s²", lambda m: "%s kg·cm (%s)" % (sayi(m["duz"]["T_kgcm"], 2), oran(m["duz"]["oran"]))),
            ("5° rampa, 0,5 m/s²", lambda m: "%s kg·cm (%s)" % (sayi(m["rampa5"]["T_kgcm"], 2), oran(m["rampa5"]["oran"]))),
            ("5° rampa, 0,25 m/s² (mevcut öneri)", lambda m: "%s kg·cm (%s)" % (sayi(m["rampa5_yavas"]["T_kgcm"], 2), oran(m["rampa5_yavas"]["oran"]))),
            ("5° rampa, sabit hız", lambda m: "%s kg·cm (%s)" % (sayi(m["rampa5_durus"]["T_kgcm"], 2), oran(m["rampa5_durus"]["oran"]))),
            ("5° rampa, 0,5 m/s² + 2 kg yük", lambda m: "%s kg·cm (%s)" % (sayi(m["rampa5_yuk2"]["T_kgcm"], 2), oran(m["rampa5_yuk2"]["oran"]))),
            ("Rampada %80 için ivme sınırı", lambda m: "%s m/s²" % sayi(max(m["a_sinir_rampa5_80"], 0), 2)),
            ("Aks yükü ön / arka (N)", lambda m: "%s / %s" % (sayi(m["aks"]["on_N"], 0), sayi(m["aks"]["arka_N"], 0))),
            ("Yerinde dönüş μ 0,4 / 0,5 / 0,6, standart teker (sürekli ×)", lambda m: " / ".join("×%s" % sayi(y["standart_oran"], 2) for y in m["yerinde_donus"])),
            ("  aynısı, üst sınır modeli (durmanın %)", lambda m: " / ".join("%%%s" % sayi(y["ust_sinir_stall"] * 100, 0) for y in m["yerinde_donus"])),
            ("  aynısı, ön omni (sürekli ×)", lambda m: " / ".join("×%s" % sayi(y["omni_oran"], 2) for y in m["yerinde_donus"])),
            ("Yaw ataleti (parçalardan) / kutu formülü (kg·m²)", lambda m: "%s / %s" % (sayi(m["yaw"]["Iy_parca_kgm2"], 3), sayi(m["yaw"]["Iz_kutu_kgm2"], 3))),
            ("Dönüş ivmesi payı (1 rad/s², motor başına)", lambda m: "%s kg·cm" % sayi(m["yaw"]["ivme_payi_kgcm"], 2)),
            ("Durma 9 kg·cm çıkarsa: düz 0,5 / rampa 0,25 / rampa sabit", lambda m: "%s / %s / %s" % (oran(m["stall9"]["duz"]["oran"]), oran(m["stall9"]["rampa5_yavas"]["oran"]),
                                                                                                     oran(m["stall9"]["rampa5_durus"]["oran"])))]
    for ad_, f in rows:
        sat.append([esc(ad_)] + [f(R[k]["motor"]) for k in keys])
    h.append(tablo(["", *[ad[k] for k in keys]], sat))
    m4, me = Y["motor"], E["motor"]
    h.append("<div class='karar'><b>Yazılım ivme sınırı yetmiyor, düşürülmeli.</b><ul>"
             "<li>Düz zeminde 0,5 m/s² hâlâ uygun (%s).</li>"
             "<li>5° rampada mevcut öneri 0,25 m/s² artık sürekli torkun %s'i (125 cm'de %s); %%80 altında kalmak için rampada ivme ≤ <b>%s m/s²</b> "
             "(pratikte 0,1). Sabit hızla tırmanma bile %s.</li>"
             "<li>Yerinde dönüş standart tekerle sürekli değerin ×%s'i (μ 0,5; 125 cm: ×%s); üst sınır modelinde durma torkunu aşıyor. Ön omni (K1 a) ile ×%s: "
             "1,70 m'de omni seçeneği güçlenir.</li>"
             "<li>Yaw ataleti parçalardan %s kg·m² (125 cm: %s); artış küçük (+%%%s), çünkü eklenen kütle (direk, kabuk bantları) eksene yakın. "
             "Dönüş ivmesi payı motor başına %s kg·cm, sınır (1 rad/s²) değişmeden kalabilir.</li>"
             "<li><b>Kritik ölçüm:</b> JGB37 durma torku 9 kg·cm çıkarsa (Aslong tablosu, K3) düz zeminde 0,5 m/s² bile sürekli değerin %s'i: 1,70 m için "
             "motor ölçümü ve gerekirse daha yüksek oranlı JGB37 ya da daha güçlü motor şart.</li></ul></div>" % (
                 oran(m4["duz"]["oran"]), oran(m4["rampa5_yavas"]["oran"]), oran(me["rampa5_yavas"]["oran"]), sayi(max(m4["a_sinir_rampa5_80"], 0), 2),
                 oran(m4["rampa5_durus"]["oran"]), sayi(m4["yerinde_donus"][1]["standart_oran"], 2), sayi(me["yerinde_donus"][1]["standart_oran"], 2),
                 sayi(m4["yerinde_donus"][1]["omni_oran"], 2), sayi(m4["yaw"]["Iy_parca_kgm2"], 2), sayi(me["yaw"]["Iy_parca_kgm2"], 2),
                 sayi((m4["yaw"]["Iy_parca_kgm2"] / me["yaw"]["Iy_parca_kgm2"] - 1) * 100, 0), sayi(m4["yaw"]["ivme_payi_kgcm"], 2), oran(m4["stall9"]["duz"]["oran"])))
    return "\n".join(h)


# ====================================================================== servo
def servo():
    if not H:
        return "<div class='bos'>analiz/hesap.json yok</div>"
    ys, es = SV["yeni-444"], SV["eski-444"]
    h = ["<p>Kol: <code>dirsek/dirsek_montaj.py</code> <code>tork()</code> yöntemi: grup kütleleri ve AM'leri (omuz göbeği, üst kol, dirsek çatalı, ön kol, el) "
         "S1 −45…135 × S2 5…120 × dirsek 0…105 (5°) × bilek −90/0/90 ızgarasında döndürülüp her eksene yerçekimi torku; pay = durma torku ÷ en kötü tork "
         "(DS3218MG 20, MG996R 9,4 kg·cm @4,8 V). 125 cm sütunu aynı kodla; dirsek raporundaki değerleri birebir veriyor (S1 8,14, S2 8,32, dirsek 1,54 kg·cm). "
         "Ek olarak ivme torku: en kötü pozda eksene göre atalet (parça şekillerinden) × α %s rad/s² (kafa yöntemiyle aynı 60° / 0,4 s profil, "
         "<span class='t'>tahmini</span>). Kafa: <code>kafa/kafa_montaj.py</code> yöntemi (tilt = yerçekimi + 25 g kafa içi kablo + I·α; pan = I·α + rulman + "
         "kablo), 125 cm değerlerini birebir veriyor (tilt 4,67 kg·cm / 2,01×).</p>" % sayi(4 * 3.14159265 / 3 / 0.16, 1)]
    sat = []
    for j in range(4):
        a, b = es["kol"][j], ys["kol"][j]
        sat.append([esc(b["eklem"]), b["servo"], "%s → %s" % (sayi(a["yuksuz_kgcm"], 2), sayi(b["yuksuz_kgcm"], 2)),
                    "%s → %s" % (pay(a["yuksuz_pay"]), pay(b["yuksuz_pay"])), "%s → %s" % (pay(a["toplam_pay"]), pay(b["toplam_pay"])),
                    "%s → %s" % (pay(a["yuklu_pay"], 1.0, 0.8), pay(b["yuklu_pay"], 1.0, 0.8)), "%s → %s g" % (sayi(a["izinli_yuk_2x_g"], 0), sayi(b["izinli_yuk_2x_g"], 0)),
                    esc("%s (%s)" % (b["yuksuz_poz"], "S1, S2, dirsek, bilek"))])
    for ad_, k in (("Kafa tilt", "tilt"), ("Kafa pan", "pan")):
        a, b = es["kafa"][k], ys["kafa"][k]
        sat.append([ad_, "MG996R", "%s → %s" % (sayi(a["toplam_kgcm"], 2), sayi(b["toplam_kgcm"], 2)), "–", "%s → %s" % (pay(a["pay"]), pay(b["pay"])), "–", "–",
                    esc(("tilt %s…%s" % tuple(int(x) for x in b["aralik"])) if k == "tilt" else "tilt −15/0/15 en büyük atalet")])
    h.append(tablo(["Eklem", "Servo", "Tork kg·cm (125 → 170; kol: statik yüksüz, kafa: toplam)", "Pay statik", "Pay statik + ivme", "Pay, elde 0,5 kg (statik)",
                    "2× pay için izinli el yükü", "En kötü poz (170)"], sat))
    t, p = ys["kafa"]["tilt"], ys["kafa"]["pan"]
    s1, s2 = ys["kol"][0], ys["kol"][1]
    h.append("<ul><li><b>Omuz:</b> S1 %s → %s kg·cm, S2 %s → %s kg·cm (kol 49 mm uzun, %s g ağır; uzun kol yatayken). Statik pay 2,0 sınırında "
             "(S2 %s×), elde yük taşımak 2× payla <b>mümkün değil</b> (125 cm'de ~50 g'dı). İvmeli payda 125 cm de 2'nin altında (%s×); 1,70'te %s×: kol "
             "hareketleri yumuşak profille (ör. 90° / 1 s) verilmeli. Kol oranı büyürse daha güçlü omuz servosu gerekir (aşağıdaki tablo).</li>"
             "<li><b>Dirsek / bilek:</b> pay %s× / değişmez; sorun yok.</li>"
             "<li><b>Kafa tilt:</b> AM tilt ekseninde (parçalar 0,05 mm; 25 g kablo payıyla %s mm) olduğu için yerçekimi torku ~%s kg·cm; tork neredeyse tamamen ivme (%s kg·cm, atalet "
             "%s kg·m²). Pay %s× (125 cm: %s×): iyileşti.</li>"
             "<li><b>Kafa pan:</b> 10,1\" kafanın ataleti büyük (%s kg·m²), pay %s× (125 cm: %s×), hâlâ ≥ 2. 6808 rulmanlarında radyal yük %s N "
             "(AM pan ekseninden %s mm önde; 125 cm: %s N). Pan hızını yazılımda 60°/0,4 s'den hızlı vermeyin.</li></ul>" % (
                 sayi(es["kol"][0]["yuksuz_kgcm"], 2), sayi(s1["yuksuz_kgcm"], 2), sayi(es["kol"][1]["yuksuz_kgcm"], 2), sayi(s2["yuksuz_kgcm"], 2),
                 sayi(H["kol_orani"]["varyant"][1]["kol_kutle_ek_g"] if H.get("kol_orani") else 0, 0), sayi(s2["yuksuz_pay"], 2),
                 sayi(es["kol"][0]["toplam_pay"], 2), sayi(s1["toplam_pay"], 2), sayi(ys["kol"][2]["yuksuz_pay"], 1),
                 sayi(t["am_eksen_mm"], 2), sayi(t["yercekimi_kgcm"], 2), sayi(t["ivme_kgcm"], 2), sayi(t["I_kgm2"], 4), sayi(t["pay"], 2), sayi(es["kafa"]["tilt"]["pay"], 2),
                 sayi(max(p["I_kgm2"].values()), 4), sayi(p["pay"], 2), sayi(es["kafa"]["pan"]["pay"], 2), sayi(p["rulman_radyal_N"], 0), sayi(p["am_eksen_mm"], 0),
                 sayi(es["kafa"]["pan"]["rulman_radyal_N"], 0)))
    return "\n".join(h)


# ====================================================================== kol orani
def kol_orani():
    if not H or not H.get("kol_orani"):
        return "<div class='bos'>hesap yok</div>"
    ko = H["kol_orani"]
    sat = []
    for v in ko["varyant"]:
        s1, s2, de = v["servo"][0], v["servo"][1], v["servo"][2]
        d4 = v["devrilme"].get("yeni-444")
        d5 = v["devrilme"].get("yeni-520")
        etiket = "×1,00 (125 cm, omuz y 955)" if v["oran"] == 1.0 else ("×%s%s" % (sayi(v["oran"], 2), " (taslak)" if abs(v["oran"] - 1.15) < 1e-9 else ""))
        sat.append([etiket, sayi(v["kol_boy_mm"], 1), sayi(v["el_ucu_y"], 0), ("+%s" % sayi(v["kol_kutle_ek_g"], 0)) if v["oran"] != 1.0 else "–",
                    "%s (%s)" % (pay(s1["yuksuz_pay"]), pay(s1["toplam_pay"])), pay(s2["yuksuz_pay"]), pay(de["yuksuz_pay"]),
                    "%s g" % sayi(s1["izinli_yuk_2x_g"], 0),
                    ("%s / %s" % (pay(d4["izgara_duz"]), pay(d4["izgara_rampa"], 1.5))) if d4 else "%s / %s" % (pay(E["devrilme"]["izgara_en_kucuk_duz"]), pay(E["devrilme"]["izgara_en_kucuk_rampa"], 1.5)),
                    ("%s / %s" % (pay(d5["izgara_duz"]), pay(d5["izgara_rampa"], 1.5))) if d5 else "–",
                    ("%s / %s" % (pay(d4["one_yuk"]["pay_ileri"]), pay(d5["one_yuk"]["pay_ileri"]) if d5 else "–")) if d4 else "–"])
    h = ["<p>Kol boyu omuz ekseninden el ucuna. ×1,25 ve ×1,36 <b>modellenmedi</b>: ×1,15 taslağından doğrusal (ek boy üst kol tüpü ile el yakası arasında "
         "30:19 bölünür, birim kütleler taslaktaki uzatmalardan: tüp %s g/mm, yaka %s g/mm; <span class='t'>tahmini</span>). Gerçek tasarımda ön kol da "
         "uzatılırsa dirsek servosunun payı biraz daha düşer. Kafa × kol yasak bölgesi uzun kolda yeniden taranmalı.</p>" % (
             sayi(ko["birim_kutle"]["tup_g_mm"], 2), sayi(ko["birim_kutle"]["yaka_g_mm"], 2))]
    h.append(tablo(["Kol oranı", "Kol boyu (mm)", "El ucu y (ev pozu)", "Kol başına ek kütle (g)", "S1 pay statik (ivmeli)", "S2 pay", "Dirsek pay",
                    "S1 2× için el yükü", "Devrilme en kötü düz / rampa, taban 444", "Taban 520", "Kollar önde + 0,5 kg, ileri (444 / 520)"], sat))
    v = {round(x["oran"], 2): x for x in ko["varyant"]}
    h.append("<ul><li>Devrilmeye etkisi küçük (en kötü pay en çok %s düşer): kol kütlesi robotun %%2'si.</li>"
             "<li>Asıl bedel omuz servosu: S1 statik payı ×1,15'te %s, ×1,25'te %s, ×1,36'da %s. ×1,25 ve üstü için omuzda ~30–35 kg·cm sınıfı servo "
             "(ör. DS3235 / DS51150 sınıfı, <span class='t'>model ve ölçü doğrulanmadı</span>) ya da daha hafif ön kol/el gerekir; mevcut omuz yuvası 40 × 20 "
             "DS3218 gövdesine göre.</li>"
             "<li>Görünüm: 1,70 m'de el ucu y 1.016 (×1,15) → 947 (×1,36). İnsanda (1,70 m) parmak ucu yerden ~640 mm; ×1,36 bile bel/kalça hizasında kalır. "
             "Karar Duffy'de.</li></ul>" % (
                 sayi(max(0, (v[1.15]["devrilme"]["yeni-444"]["izgara_duz"] - v[1.36]["devrilme"]["yeni-444"]["izgara_duz"])), 2),
                 pay(v[1.15]["servo"][0]["yuksuz_pay"]), pay(v[1.25]["servo"][0]["yuksuz_pay"]), pay(v[1.36]["servo"][0]["yuksuz_pay"])))
    return "\n".join(h)


# ====================================================================== carpisma
def carpisma():
    h = []
    yeni, eski = yeni_cak_say()
    h.append("<p>Bağımsız tarama (<code>taslak_analiz.py</code>): parçalar <code>taslak_parcalar.py</code>'den yeniden kuruldu; kol ve kafa ev pozundaki eklem "
             "eksenleriyle seri zincir olarak sürüldü (125 cm'de modül fonksiyonlarıyla karşılaştırıldı: sapma %s mm). Yöntem <code>carpisma.py</code>'nin "
             "kol zinciri / kafa bölümleriyle aynı: sıkı sınır kutusu ön elemesi, 5 mm altındaki her aday tam ölçüm (distToShape, common hacmi, eşik 0,5 mm³), "
             "hedef başına en küçük boşluk dal-sınırla, 5 mm altı ve çakışan alt pozların çevresi 5° (bilek 15°) ince adımla. Her çakışan parça çiftinin "
             "125 cm robottaki karşılığı aynı pozda ölçüldü: 125 cm'de de çakışıyorsa \"mevcut\", değilse \"yeni\".</p>" % (
                 ("%.0e" % D["kinematik"]["en_buyuk_sapma_mm"]) if D else "?"))
    # ozet tablo
    sat = []
    if 444 in ST:
        s = ST[444]
        n_y = sum(1 for c in s["cakisma"] if c["kaynak"].startswith("taslak"))
        sat.append(["Ev pozu, tüm parça çiftleri (taban 444)", "%d parça, %d aday çift" % (s["parca"], s["aday_cift"]), "<b class='%s'>%d</b>" % ("ok" if not n_y else "no", n_y),
                    "%d (S1 kablo tamburu ↔ kol çatalı 97,9 / üst kol tüpü 65,0; tüp ↔ S1 kaset kapağı 7,6 mm³; iki yanda)" % (len(s["cakisma"]) - n_y), ""])
    for w in sorted(k for k in ST if k != 444):
        s = ST[w]
        n_y = sum(1 for c in s["cakisma"] if c["kaynak"].startswith("taslak"))
        ek = ""
        if n_y:
            ek = "; ".join(sorted(set("%s ↔ %s" % (c["a"].split(" (")[0], c["b"].split(" (")[0]) for c in s["cakisma"] if c["kaynak"].startswith("taslak"))))
        sat.append(["Ev pozu, taban %d" % w, "%d parça" % s["parca"], "<b class='%s'>%d</b>" % ("ok" if not n_y else "no", n_y), "aynı 6", esc(ek)])
    for t in ("sag", "sol"):
        k = KOL.get(t)
        if not k:
            sat.append(["Kol zinciri %s" % t, "koşulmadı", "", "", ""])
            continue
        n_y = sum(1 for c in k["cakisma_ciftleri"] if c["kaynak"].startswith("taslak"))
        mev = [c for c in k["cakisma_ciftleri"] if not c["kaynak"].startswith("taslak")]
        kab = k["en_kucuk_bosluk"].get("kabuk")
        sat.append(["Kol zinciri %s × iskelet, kabuk, taban, omuz gövdeleri/göbek, sabit boyun" % ("sağ" if t == "sag" else "sol"),
                    "%d kaba poz, %d+%d alt poz, %d tam ölçüm" % (k["kaba"]["tam_poz"], k["alt_poz"]["kaba"], k["alt_poz"]["ince"], k["tam_olcum"]),
                    "<b class='%s'>%d</b>" % ("ok" if not n_y else "no", n_y),
                    "%d çift: %s" % (len(mev), esc("; ".join("%s ↔ %s (%d alt poz, ≤ %s mm³)" % (c["parca"], c["hedef"], c["alt_poz"], sayi(c["en_buyuk_mm3"], 1)) for c in mev[:4]))),
                    ("kabuğa en az %s mm (%s ↔ %s, poz %s)" % (sayi(kab["bosluk_mm"], 1), esc(kab["parca"]), esc(kab["hedef"]), kab["poz"])) if kab else ""])
    if KK:
        e = KK["en_kucuk"]
        sat.append(["Kol ↔ kol (simetrik, zıt, birlikte öne)", "%d poz çifti" % KK["poz_cifti"], "<b class='%s'>%d</b>" % ("ok" if not KK["cakisan"] else "no", KK["cakisan"]), "–",
                    "en az %s mm (%s ↔ %s)" % (sayi(e["bosluk_mm"], 1), esc(e["cift"][0]), esc(e["cift"][1]))])
    if KAF:
        n_y = sum(1 for c in KAF["cakisma"] if c["kaynak"].startswith("taslak"))
        eb = KAF["en_kucuk_bosluk"]
        sat.append(["Kafa pan ±90 × tilt ±15 (5°) × iskelet, kabuk, sabit boyun, omuzlar, kollar ev pozunda",
                    "%d poz" % KAF["poz"], "<b class='%s'>%d</b>" % ("ok" if not n_y else "no", n_y), "%d" % (len(KAF["cakisma"]) - n_y),
                    esc("; ".join("%s %s mm" % (m, sayi(v["bosluk_mm"], 1)) for m, v in list(eb.items())[:6]))])
    for t in ("sag", "sol"):
        k = KKL.get(t)
        if not k:
            sat.append(["Kafa × kol %s" % t, "koşulmadı", "", "", ""])
            continue
        n_y = sum(1 for c in k["cakismalar"] if c["kaynak"].startswith("taslak"))
        e = k["en_kucuk_cakismasiz"] or k["en_kucuk"]
        sat.append(["Kafa × kol %s (kafa pan 15°, tilt 5° × kolun 1.755 pozu; sınır yakınsayana dek)" % ("sağ" if t == "sag" else "sol"),
                    "%d kafa × %d kol alt pozu, %d tam ölçüm" % (k["kafa_poz"], k["kol_alt_poz"], k["tam_olcum"]),
                    "<b class='%s'>%d</b>%s" % ("ok" if not k["cakisma_sayisi"] else "no", n_y, (" (%d tam poz çifti)" % k["cakisan_tam_cift"]) if k["cakisma_sayisi"] else ""),
                    "%d" % (k["cakisma_sayisi"] - n_y),
                    ("en az %s mm: %s ↔ %s, kol %s, kafa %s" % (sayi(e["bosluk_mm"], 1), esc(e["kol_parca"]), esc(e["kafa_parca"]), e["kol_poz"], e["kafa_poz"])) if e else ""])
    h.append(tablo(["Tarama", "Kapsam", "Yeni çakışma", "Mevcut tasarımdan (125'te de)", "En dar yer / not"], sat))
    h.append("<p class='not'>0,0 mm boşluklar tasarım temasıdır (horn merkez vidası ↔ servo çıkış mili, S2 horn ↔ S2 mili; hacim ≤ 0,5 mm³). Kol taramasında "
             "S2 ≥ 5° (eklem aralığı): ev pozundaki (S2 0°) tüp ↔ S1 tamburu / kaset kapağı kesişmeleri aralıkta yok, tamburu ↔ kaset kapağı en az 0,5 mm "
             "(S1 kaseti tasarımı, 125 cm ile aynı). Kafa × kol: 125 cm'deki yasak bölge tilt 25…30° istiyordu; tilt ±15 sınırıyla ve 95 mm yukarıdaki kafayla "
             "bu bölge kalkıyor, en dar yer el ↔ yüz kabuğu ~18 mm (kol öne 135°, dirsek 105°).</p>")
    # yasak bolge
    for t in ("sag", "sol"):
        k = KKL.get(t)
        if k and k.get("yasak_bolge"):
            y = k["yasak_bolge"]
            h.append("<p><b>Kafa × kol yasak bölgesi (%s):</b> kol öne %s…%s°, yana %s…%s°, dirsek %s…%s° iken kafa pan %s…%s°, tilt %s…%s°; kafa parçaları %s; "
                     "kol parçaları %s.</p>" % ("sağ" if t == "sag" else "sol", *[sayi(x, 0) for x in y["one_arka"] + y["yana"] + y["dirsek"] + y["pan"] + y["tilt"]],
                                                esc(", ".join(y["kafa_parcalari"])), esc(", ".join(y["kol_parcalari"]))))
    # yontem dogrulamasi: ayni kod 125 cm robotta
    ek = []
    e0 = KK0.get("eski")
    if e0 and e0.get("yasak_bolge"):
        y = e0["yasak_bolge"]
        ek.append("<b>Yöntem doğrulaması:</b> aynı kafa × kol taraması 125 cm robotta, S2 alt sınırı 0° alınarak (kafa raporunun 9 Ekim taramasındaki "
                  "gibi) koşulunca %d çakışan poz çifti ve yasak bölge kol öne %s…%s°, yana %s°, dirsek %s…%s°, pan %s…%s°, tilt %s…%s° çıktı: kafa "
                  "raporundaki bölgeyle (603 çift) birebir aynı yer." % (e0["cakisan_tam_cift"], *[sayi(x, 0) for x in (y["one_arka"] + [y["yana"][0]] + y["dirsek"] + y["pan"] + y["tilt"])]))
    y0 = KK0.get("yeni")
    if y0:
        ek.append("170 cm taslakta S2 = 0° dahil edilse bile çakışma %d; en dar %s mm (%s ↔ %s, kol %s, kafa %s)." % (
            y0["cakisma_sayisi"], sayi(y0["en_kucuk"]["bosluk_mm"], 1), esc(y0["en_kucuk"]["kol_parca"]), esc(y0["en_kucuk"]["kafa_parca"]),
            y0["en_kucuk"]["kol_poz"], y0["en_kucuk"]["kafa_poz"]))
    k5 = KKLE.get("sag")
    if k5:
        ek.append("Yan bulgu (mevcut 125 cm tasarım): S2 alt sınırı 5° olduğu (15 Ekim, S1 kaseti) için 125 cm'de de eklem aralığında kafa × kol çakışması "
                  "kalmıyor (%d; en dar %s mm). OZET'teki yasak bölge kuralı artık gereksiz olabilir; ana taramada (C7) teyit edilmeli." % (
                      k5["cakisma_sayisi"], sayi((k5["en_kucuk_cakismasiz"] or k5["en_kucuk"])["bosluk_mm"], 1)))
    if KAFE:
        ek.append("125 cm kafa × sabit (pan ±90 × tilt −25…30): çakışma %d." % len(KAFE["cakisma"]))
    if ek:
        h.append("<p>" + " ".join(ek) + "</p>")
    if KD["yeni"] and KD["eski"]:
        sat = []
        for m in sorted(set(KD["yeni"]["en_kucuk_bosluk"]) | set(KD["eski"]["en_kucuk_bosluk"])):
            a, b = KD["eski"]["en_kucuk_bosluk"].get(m), KD["yeni"]["en_kucuk_bosluk"].get(m)
            f = lambda v: ("%s mm (%s ↔ %s, poz %s)" % (sayi(v["bosluk_mm"], 1), esc(v["parca"]), esc(v["hedef"]), v["poz"])) if v else "&gt; 150 mm"
            sat.append([esc(m), f(a), f(b)])
        h.append("<h3>Yalnız dirsek parçaları hareketli (125 cm <code>carpisma.py</code> bölüm 4 kapsamı), sağ kol: en küçük boşluk</h3>")
        h.append(tablo(["Hedef", "125 cm (aynı kod)", "170 cm taslak"], sat))
        h.append("<p class='not'>Çakışma: 125 cm %d, 170 cm %d çift (eklem aralığında). 125 cm'nin kayıtlı taraması (8 Ekim, <code>carpisma-sonuc.json</code>) kabuğa ~3,8 mm "
                 "veriyordu; o tarihten sonra omuza S1 kaseti eklendi.</p>" % (len(KD["eski"]["cakisma_ciftleri"]), len(KD["yeni"]["cakisma_ciftleri"])))
    h.append("<p class='not'>Kısa kontrol (tasarım ajanı) yalnız değişen parçaları ve farklı ötelenen çiftleri ölçtüğü için aynı ötelenen iki parça arasındaki "
             "mevcut çakışmayı (S1 kablo tamburu ↔ kol çatalı, 97,9 mm³, 125 cm'de de aynı) listelememişti; tam ev pozu taramasında çıktı. S1 kaseti WIP.</p>")
    return "\n".join(h)


# ====================================================================== dogrulama
def dogrulama():
    if not D:
        return "<div class='bos'>analiz/dogrulama.json yok</div>"
    y, f, s, k = D["yeniden_kurulum"], D["fcstd"], D["step"], D["kafa"]
    o = D["ornek"]
    sat = [["Yeniden kurulum (taslak_parcalar.py)", "%d parça, %s g, AM (%s)" % (y["parca"], sayi(y["kutle_g"], 1), "; ".join(sayi(x, 2) for x in y["am"])),
            "kutle.json ile fark %s g; parça sırası, adı, kütlesi aynı: %s" % (sayi(y["fark_g"], 2), "evet" if y["parca_sirasi_ve_kutle_ayni"] else "HAYIR")],
           ["taslak-170.FCStd (Kutle_g + şekil merkezleri)", "%d nesne, %s g, AM (%s)" % (f["nesne"], sayi(f["kutle_g"], 1), "; ".join(sayi(x, 2) for x in f["am_sekil_merkezleriyle"])),
            "AM her parçanın FCStd şeklinin merkezinden; grup yerleşimleri birim: %s" % ("evet" if f["grup_yerlesimi_birim"] else "hayır")],
           ["taslak-170.step", "%d katı, hacim %s cm³" % (s["kati"], sayi(s["toplam_hacim_mm3"] / 1000, 1)),
            "FCStd ile %d/%d katı eşleşti; STEP geometrisi + FCStd kütlesiyle AM (%s)" % (s["eslesen_kati"], s["kati"], "; ".join(sayi(x, 2) for x in s["step_geometrisi_kutle_agirlikli_am"]))],
           ["Kafa tilt / pan grubu (şekil merkezleriyle)", "%s g, AM eksene %s mm; pan %s g" % (sayi(k["tilt_grubu_g"], 1), sayi(k["tilt_am_eksene_dik_mm_sekil"], 3), sayi(k["pan_grubu_g"], 1)),
            "pan grubu AM'si pan ekseninden %s mm önde" % sayi(k["pan_am_eksene_dik_mm_sekil"], 1)],
           ["Rastgele örnek (%d parça, tohum 170) + değişen/yeni parçalar" % len(o),
            "kütle farkı en çok %s g, merkez farkı en çok %s mm" % (sayi(max(abs(x["kutle_json_g"] - x["fcstd_g"]) for x in o), 2), sayi(max(x["merkez_farki_mm"] for x in o), 2)),
            "taşınan parçalarda hacim ve kütle 125 cm karşılığıyla aynı, öteleme 435 (omuz, travers, üst kabuk) / 405 (dirsek) / 493,3 (tilt çatalı) mm; "
            "direk 2.422,8 g (1.235,5 mm), uzatma bandı 278–296 g (PETG × 0,9)"]]
    h = [tablo(["Kontrol", "Sonuç", "Not"], sat)]
    return "\n".join(h)


# ====================================================================== acik isler
def acik_isler(TA, KF, uzatma_g, ek=()):
    m4 = Y["motor"] if Y else None
    sat = [
        ["Gövde direği boyu", "1.235,5 mm sigma 40×40 ağır; 1 m stok yetmez", "1,5 / 2 m boy ya da özel kesim (Robolink'te özel kesim teyit); olmazsa 2 parça + ek plakası (ek yeri omuz traversinden uzak, y &lt; 900)", "tasarım + satın alma"],
        ["Uzatma bantlarının ağırlığı", "%s g PETG (4 parça, 3 mm duvar, etkin doluluk 0,9) + 4 braket; AM'yi yükseltir" % sayi(uzatma_g, 0),
         "2,4 mm duvar ~%%20 hafif (~%s g; AM y ~1 mm düşer) ya da ızgaralı iç yüz; bindirme dili/boss kuralı yeniden kontrol. Baskı süresi ve filament için de önemli" % sayi(uzatma_g * 0.2, 0), "kabuk"],
        ["Kafa 5 V beslemesi", "Pi 5 (5 V 5 A tepe) + 10,1\" ekran (~5 V 1–2 A, <span class='t'>tahmini</span>) aynı Pololu D36V50F5'ten (5,5 A)",
         "tepe toplam 6–7 A çeviriciyi aşabilir: ekran akımı ölçülsün; gerekirse ekrana ayrı küçük 5 V çevirici ya da ≥ 8 A çevirici. Kafa ısısı (Pi + ekran) yeniden ölçülmeli", "elektrik"],
        ["Kablo uzamaları", "gövde +%s mm (12 V, ESP32 USB, servo uzatmaları), kol tüpü +%s mm, tilt servo +%s mm (adaptör)" % (sayi(TA.DY, 0), sayi(TA.UST_KOL_UZAMA, 0), sayi(KF["adaptor_h_mm"], 0)),
         "servo uzatması ~1,3 → ~1,8 m: 22 AWG'de 2,5 A'de düşüm 0,34 → ~0,46 V (servo ~5,5 V görür, <span class='t'>tahmini</span>); dağıtım kartlarını traverse seviyesine taşımak (E1 açık işi) artık daha anlamlı. Kablo payı 45 g tahmini", "elektrik"],
        ["Kol oranı kararı", "×1,15 taslakta; ×1,25 / ×1,36 omuz servosunu 2× payın altına indirir", "Kol oranı tablosu (yukarıda). ×1,25+ seçilirse omuz servosu ve omuz yuvası değişir; kafa × kol taraması yeniden", "Duffy"],
        ["Yüz ekranı modeli", "hocanın vereceği HDMI ekran belli değil; CAD Waveshare 10.1\" (B), 600 g <span class='t'>tahmini</span>",
         "gelince ölçü/kütle/delik <code>taslak_ayar.EKRAN10</code>'a; <code>kafa10.dengele()</code> kafayı yeniden dengeler; pan payı (%s×) ekran kütlesine duyarlı" % (sayi(SV["yeni-444"]["kafa"]["pan"]["pay"], 2) if H else "?"), "hoca + tasarım"],
        ["Taban genişletme (520)", "yana devrilme payı; 480'de motor braketi M4'leri uzun raya biniyor", "<code>TASLAK_TABAN_W=520</code> ile yeniden üret; braket artık 3 mm plakaya konsol: plaka rijitliği ve etek dolgu şeridi baskı yönü açık", "tasarım"],
        ["AM'yi öne almak", "geri devrilme darboğazı (AM z −11,6)", "akü ~75 mm öne (taban yerleşimi) ya da ön-alt balast; rampada kol pozu sınırı (yazılım)", "taban + yazılım"],
        ["Teker motoru", "rampada ivme %s m/s²'ye inmeli; yerinde dönüş standart tekerle ×%s" % (sayi(max(m4["a_sinir_rampa5_80"], 0), 2) if m4 else "?", sayi(m4["yerinde_donus"][1]["standart_oran"], 2) if m4 else "?"),
         "JGB37 durma torku + zemin μ ölçümü (K1) şimdi daha kritik; ön omni (K1 a) önerisi güçlendi", "ekip"],
        ["Omuz servosu", "S1/S2 yüksüz pay ~2,0×, elde yük yok", "jest profili yumuşak (≤ 90°/1 s); yük taşınacaksa ~30–35 kg·cm servo", "tasarım + yazılım"],
        ["S1 kaseti (mevcut, WIP)", "S1 kablo tamburu ↔ kol çatalı 97,9 / üst kol tüpü 65,0 mm³, tüp ↔ S1 kaset kapağı 7,6 mm³ (iki yanda; 125 cm'de de)", "S1 kaseti tasarımında çözülecek; taslağa özgü değil", "kabuk / omuz"],
        ["Pan rulman yükü", "6808 çiftinde radyal %s N (125 cm: %s N)" % (sayi(SV["yeni-444"]["kafa"]["pan"]["rulman_radyal_N"], 0), sayi(SV["eski-444"]["kafa"]["pan"]["rulman_radyal_N"], 0)) if H else "",
         "6808-2RS yük değerleri doğrulanacak (OZET açık işi); kafa AM'si pan eksenine yaklaştırılabilir", "tasarım"],
    ]
    return tablo(["İş", "Durum / neden", "Öneri", "Kimde"], sat + [list(x) for x in ek])


# ====================================================================== sonuc kutusu (en ustte)
def sonuc_kutusu():
    if not H:
        return ""
    yeni, eski = yeni_cak_say()
    kol_tamam = all(KOL.get(t) for t in ("sag", "sol")) and all(KKL.get(t) for t in ("sag", "sol")) and KAF is not None
    y4, y5 = Y["devrilme"], (Y5 or Y)["devrilme"]
    ys, es = SV["yeni-444"], SV["eski-444"]
    m4 = Y["motor"]
    onl = {(o["taban"], o["onlem"]): o for o in H.get("onlem", [])}
    o5 = onl.get(("yeni-520", "akü 75 mm öne"))
    cak_metin = ("Tam çarpışma taramasında taslaktan gelen <b>yeni çakışma yok</b>%s; mevcut 125 cm tasarımdan gelen S1 kaseti çakışmaları (WIP) aynen duruyor."
                 % ("" if kol_tamam else " (bazı taramalar koşulmadı)")) if not yeni else (
        "Taslaktan gelen <b>%d yeni çakışma</b> var (Çarpışma bölümü); mevcut S1 kaseti çakışmaları ayrıca duruyor." % len(yeni))
    sart = [
        "<b>Taban 520 mm</b> (her yana 38 mm; <code>TASLAK_TABAN_W=520</code>, statik çakışma yok) ve <b>AM öne</b> (akü ~75 mm öne ya da ön-alt balast): "
        "düz zeminde en kötü pay %s× → %s×, 5° rampada %s× → %s× (ölçüt düz ≥ 2, rampa ≥ 1,5)." % (
            sayi(y4["izgara_en_kucuk_duz"], 2), sayi(min(o5["izgara_duz"]) if o5 else y5["izgara_en_kucuk_duz"], 2),
            sayi(y4["izgara_en_kucuk_rampa"], 2), sayi(min(o5["izgara_rampa"]) if o5 else y5["izgara_en_kucuk_rampa"], 2)),
        "<b>Yazılım:</b> rampada ivme ≤ 0,1 m/s² (0,25'te motor %s) ve kollar ev pozunda; yerinde dönüş standart tekerle sürekli torkun ×%s'i → ön omni (K1 a).",
        "<b>JGB37 ölçümü</b> şart: durma 21 değil 9 kg·cm çıkarsa düz zeminde bile %s.",
        "<b>Kollar yüksüz jest:</b> omuz S1/S2 payı %s× / %s× (125 cm: %s× / %s×), elde yük yok, yumuşak hareket profili. Kol ×1,25+ seçilirse omuz servosu büyür.",
        cak_metin,
        "Tedarik / yapım: 1.235,5 mm direk tek parça; uzatma bantları %s; kafa 5 V bütçesi; kablo uzamaları (Açık işler)." % "~1,15 kg PETG",
    ]
    sart[1] = sart[1] % (oran(m4["rampa5_yavas"]["oran"]), sayi(m4["yerinde_donus"][1]["standart_oran"], 2))
    sart[2] = sart[2] % oran(m4["stall9"]["duz"]["oran"])
    sart[3] = sart[3] % (sayi(ys["kol"][0]["yuksuz_pay"], 2), sayi(ys["kol"][1]["yuksuz_pay"], 2), sayi(es["kol"][0]["yuksuz_pay"], 2), sayi(es["kol"][1]["yuksuz_pay"], 2))
    return ("<div class='sonuc'><h2>Sonuç: olur mu?</h2><div class='cevap'>Evet, şartlı: 1,70 m bu modüllerle yapılabilir, ama 125 cm'nin rahat "
            "payları yok; devrilme, teker motoru ve omuz servosu sınırda.</div><ol>%s</ol>"
            "<p class='not'>Kafa tarafı iyi: tilt ekseni kafanın AM'sinde (%s mm), tilt payı %s× (125 cm: %s×); pan %s× (125 cm: %s×). Kütle %s kg, AM y %s mm "
            "(125 cm: %s kg, y %s) bağımsız olarak doğrulandı.</p></div>" % (
                "".join("<li>%s</li>" % s for s in sart), sayi(D["kafa"]["tilt_am_eksene_dik_mm_sekil"], 2) if D else "?",
                sayi(ys["kafa"]["tilt"]["pay"], 2), sayi(es["kafa"]["tilt"]["pay"], 2), sayi(ys["kafa"]["pan"]["pay"], 2), sayi(es["kafa"]["pan"]["pay"], 2),
                sayi(Y["kutle_g"] / 1000, 2), sayi(Y["am"][1], 0), sayi(E["kutle_g"] / 1000, 2), sayi(E["am"][1], 0)))
