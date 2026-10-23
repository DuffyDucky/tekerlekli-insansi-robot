# Lale 1,70 m taslak - KOL ANALIZI raporu (sistem Python'u): kol-analiz.json -> rapor.html
#   python kol_analiz.py && python kol_rapor.py
import os, json, html

HERE = os.path.dirname(os.path.abspath(__file__))
TS = os.path.dirname(HERE)
D = json.load(open(os.path.join(HERE, "kol-analiz.json"), encoding="utf-8"))
H = json.load(open(os.path.join(TS, "analiz", "hesap.json"), encoding="utf-8"))
REC = (1.25, "DS3235")
SV = ("DS3218MG", "DS3235")


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


SINIF = {"guvenli": ("ok", "güvenli"), "sinirda": ("uy", "sınırda"), "yetersiz": ("no", "yetersiz"), "bilinmiyor": ("t", "bilinmiyor")}


def sf_html(sf, sinif):
    c, t = SINIF[sinif]
    v = "≥ 99" if sf >= 99 else sayi(sf, 2)
    return "<span class='%s'>%s</span>" % (c, v)


def pay_html(p, esik=2.0, uy=1.2):
    c = "ok" if p >= esik else ("uy" if p >= uy else "no")
    return "<span class='%s'>%s×</span>" % (c, sayi(p, 2))


def var(oran):
    return [v for v in D["varyant"] if abs(v["oran"] - oran) < 1e-9][0]


def ek(oran, sv, j):
    return [e for e in var(oran)["servo"][sv]["eklem"] if e["eklem"] == j][0]


DUR = {"L1": "L1 statik", "L2": "L2 ivmeli", "L3": "L3 stall", "L4": "L4 darbe"}
eski = {s["eklem"].split(" ")[0]: s for s in H["servo"]["eski-444"]["kol"]}

CSS = open(os.path.join(TS, "rapor.html"), encoding="utf-8").read().split("<style>")[1].split("</style>")[0]
o = ["<!doctype html><html lang='tr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>",
     "<title>Lale Kol Analizi</title><style>%s\ndetails{margin:8px 0}summary{cursor:pointer;font-weight:600}</style></head><body><main>" % CSS]
o.append("<h1>Kol analizi: uzun kol + DS3235 <span class='rozet'>TASLAK</span></h1>")
o.append("<div class='sub'>Lale 1,70 m taslağı (<code>taslak-170/</code>), 24 Ekim 2026, kol analiz ajanı. Soru (Duffy): kolu uzatıp omuz servolarını "
         "DS3218MG'den DS3235'e yükseltmek; kol malzemesi bu ağırlığı kaldırır mı, parçalara binen yükler ne? Kol oranları ×1,15 (taslak) / ×1,25 / ×1,36; "
         "omuzda DS3218MG ve DS3235 karşılaştırmalı. Ana taslak dosyaları değiştirilmedi. <span class='t'>Tahmini</span> işaretli değerler ölçülmedi ya da "
         "kaynaktan türetildi. <a href='../rapor.html'>← taslak raporu</a></div>")

R = var(REC[0])
Rs = R["servo"][REC[1]]
r_s1, r_s2 = ek(REC[0], REC[1], "S1"), ek(REC[0], REC[1], "S2")
o.append("<div class='sonuc'><h2>Sonuç</h2><div class='cevap'>Evet: kol malzemesi (PETG / PETG-CF) bu yükleri rahat taşır; zayıf halka plastik değil, "
         "servo çıkışları (mil, horn kanalı) ve dirsek servosu. Öneri: <b>kol ×1,25 + omuzda DS3235</b> (4 adet + 1 yedek).</div><ol>")
o.append("<li><b>DS3218MG uzun kolda yetmez:</b> ×1,15'te bile statik pay %s, ivmeli %s ve elde yük yok; ×1,25'te %s / %s. DS3235 ile ×1,25'te "
         "statik %s, ivmeli %s, elde ~%s g (2× pay). ×1,36'da DS3235 statik %s ama ivmeli %s: ancak yavaş profil (60°/0,5 s) ile.</li>" % (
             pay_html(ek(1.15, "DS3218MG", "S1")["pay_statik"]), pay_html(ek(1.15, "DS3218MG", "S1")["pay_ivmeli"], 1.5, 1.0),
             pay_html(ek(1.25, "DS3218MG", "S1")["pay_statik"]), pay_html(ek(1.25, "DS3218MG", "S1")["pay_ivmeli"], 1.5, 1.0),
             pay_html(r_s1["pay_statik"]), pay_html(r_s1["pay_ivmeli"], 1.5, 1.0), sayi(r_s1["yuk_2x_g"], 0),
             pay_html(ek(1.36, "DS3235", "S1")["pay_statik"]), pay_html(ek(1.36, "DS3235", "S1")["pay_ivmeli"], 1.5, 1.0)))
mn = {}
for v in D["varyant"]:
    for sv in SV:
        for dur in DUR:
            sat = [r for r in v["servo"][sv]["yapisal"]["satir"] if r["durum"] == dur]
            mn[(v["oran"], sv, dur)] = min(sat, key=lambda r: r["sf"])
o.append("<li><b>Baskı parçaları:</b> statik, ivmeli ve servo stall durumlarında her kesitte emniyet ≥ 2 (×1,25 + DS3235'te en düşük: %s, %s). "
         "Katman yönü (Z), sürünme (×0,45) ve 40–50 °C (×0,75–0,85) düşümü dahil. Yalnız <b>tam hızda sert darbede</b> dirsek çatalı dış kolu ve el "
         "yakası vidaları sınırı aşar.</li>" % (esc(mn[(REC[0], REC[1], "L3")]["eleman"]), sf_html(mn[(REC[0], REC[1], "L3")]["sf"], mn[(REC[0], REC[1], "L3")]["sinif"])))
o.append("<li><b>DS3235 kendi parçalarını kırar mı?</b> Plastik parçaları hayır. Ama stall'da 25T alüminyum horn kanalı sınırda (%s), S2 servo miline ~%s N "
         "radyal yük biner ve el bir yere takılırsa omuz <b>dirseği geri sürer</b> (MG996R stall'ının %s katı). Kelepçeli 25T horn + merkez vidaya "
         "vida sabitleyici, S2 horn tarafına destek rulmanı ve yazılımda hız / temas sınırı.</li>" % (
             sf_html([b for b in Rs["yapisal"]["baglanti"] if b["durum"] == "L3" and b["eleman"].startswith("S1 horn")][0]["sf"], "sinirda"),
             sayi([b for b in Rs["yapisal"]["baglanti"] if b["durum"] == "L3" and b["eleman"].startswith("S2 servo mili")][0]["deger"], 0),
             sayi(Rs["dirsek_geri_surme_kati"], 2)))
o.append("<li><b>Akım:</b> DS3235 aynı torku daha az akımla verir; hat A yoğun %s A (XL4016 sürekli önerisi 5 A: <span class='uy'>sınırda</span>, ölç), "
         "gerçekçi tepe %s A (8 A modül içinde), giriş sigortası 7,5 A yeter. Kablo düşümüyle servo 5,5 V görür (DS3235 listesi 6–7,4 V): "
         "<b>S1/S2 uzatması 20 AWG + XL4016 çıkışı 6,4 V</b> → S1 statik %s, ivmeli %s.</li>" % (
             sayi(Rs["hat"]["yogun_A"], 2), sayi(Rs["hat"]["tepe_A"], 2), pay_html(Rs["secenek_64V_20AWG"]["pay_statik"]),
             pay_html(Rs["secenek_64V_20AWG"]["pay_ivmeli"], 1.5, 1.0)))
o.append("<li><b>Maliyet / kütle:</b> 5 servo farkı +%s TL (indirimli; liste fiyatıyla +%s TL); servo kütlesi aynı (60 g). Kol ×1,25 her kolda +%s g, "
         "devrilme payı %s → %s (etkisi küçük).</li>" % (
             sayi(D["maliyet"]["fark_indirimli"], 0), sayi(D["maliyet"]["fark_liste"], 0), sayi(var(1.25)["kol_kutle_g"] - var(1.15)["kol_kutle_g"], 1),
             sayi(var(1.15)["devrilme"]["yeni-444"]["izgara_duz"], 2), sayi(var(1.25)["devrilme"]["yeni-444"]["izgara_duz"], 2)))
o.append("<li><b>Satın almadan önce:</b> Robocombo sayfası başlıkta DS3235 diyor, açıklamada \"RDS3235 … U braket dahil\" geçiyor. Gelen ürün çift milli "
         "RDS3235 ise gövde ve kulaklar farklı olabilir: satıcıya model ve kulak delik aralığı (49,5 × 10) sorulsun.</li></ol>")
o.append("<p class='not'>×1,15 + DS3235 en rahat seçenek (statik %s, ivmeli %s, ~%s g, hat %s A); ×1,36 boyla tam orantılı ama ivme sınırı ve daha uzun yaka "
         "(bilek milinde konsol) ister. Uzatmayı yakaya değil üst kol tüpüne vermek bilek yükünü azaltır (Düzeltmeler).</p></div>" % (
             pay_html(ek(1.15, "DS3235", "S1")["pay_statik"]), pay_html(ek(1.15, "DS3235", "S1")["pay_ivmeli"], 1.5, 1.0),
             sayi(ek(1.15, "DS3235", "S1")["yuk_2x_g"], 0), sayi(var(1.15)["servo"]["DS3235"]["hat"]["yogun_A"], 2)))

# ------------------------------------------------------------------ KPI
kp = [("×1,25 + DS3235", "önerilen kombinasyon: kol %s mm (×1,15: %s, ×1,36: %s)" % (sayi(R["kol_boy_mm"], 1), sayi(var(1.15)["kol_boy_mm"], 1), sayi(var(1.36)["kol_boy_mm"], 1))),
      ("%s× / %s×" % (sayi(r_s1["pay_statik"], 2), sayi(r_s1["pay_ivmeli"], 2)), "S1 statik / ivmeli pay, servo gerilimi %s V (DS3218: %s× / %s×)" % (
          sayi(Rs["hat"]["V_servo_S1_stall"]["22AWG"], 2), sayi(ek(1.25, "DS3218MG", "S1")["pay_statik"], 2), sayi(ek(1.25, "DS3218MG", "S1")["pay_ivmeli"], 2))),
      ("%s g" % sayi(r_s1["yuk_2x_g"], 0), "elde taşınabilecek yük, 2× statik pay (DS3218: 0 g)"),
      ("%s" % sayi(mn[(REC[0], REC[1], "L3")]["sf"], 2), "baskı parçalarında en düşük emniyet, servo stall (ölçüt ≥ 2)"),
      ("%s A" % sayi(Rs["hat"]["yogun_A"], 2), "servo hattı A yoğun (tepe %s A; XL4016 8 A, sürekli 5 A)" % sayi(Rs["hat"]["tepe_A"], 2)),
      ("+%s TL" % sayi(D["maliyet"]["fark_indirimli"], 0), "5 × DS3235 farkı (indirimli 1.171,50 TL; liste 1.255 TL)"),
      ("%s kg·cm" % sayi(Rs["yapisal"]["darbe"]["S1"]["M_omuz_kgcm"], 0), "tam hızda sert darbede omuz momenti (stall'ın %s katı, tahmini)" % sayi(Rs["yapisal"]["darbe"]["S1"]["stall_kati"], 1)),
      ("+%s g" % sayi(R["kol_kutle_g"] - var(1.15)["kol_kutle_g"], 1), "kol başına kütle (×1,15'e göre); servo değişimi 0 g")]
o.append("<div class='k'>%s</div>" % "".join("<div class='kpi'><b>%s</b><span>%s</span></div>" % (a, esc(b)) for a, b in kp))

# ------------------------------------------------------------------ 1 servo verisi
S = D["servo"]
o.append("<h2>1. DS3235 verisi (DS3218MG ile)</h2>")
o.append(tablo(["", "DS3218MG (mevcut)", "DS3235 (Robocombo)", "MG996R (dirsek, bilek)"], [
    ["Stall torku", "19 @5 V · 21,5 @6,8 V → <b>20,4 @6 V</b> (proje 20)", "29 @5 V · <b>32 @6 V</b> · 35 @7,4 V", "9,4 @4,8 V · <b>11 @6 V</b>"],
    ["Hız (yüksüz)", "~0,16 s/60° @5 V <span class='t'>tahmini</span>", "0,13 / 0,12 / 0,11 s/60° @5 / 6 / 7,4 V", "0,17 → 0,14 s/60°"],
    ["Çalışma gerilimi", "4,8–6,8 V", "6–7,4 V (Robocombo) · 5–7,4 V (datasheet)", "4,8–7,2 V"],
    ["Stall akımı", "1,8 @5 V · 2,6 @6,8 V → 2,24 @6 V", "datasheet 1,9 / 2,1 / 2,3 A; satıcı tabloları 2,2–3,9 A → <b>tasarımda 3,0 A @6 V</b> <span class='t'>tahmini</span>", "2,5 A @6 V"],
    ["Boşta akım", "4–5 mA (DS3218 PRO datasheet)", "veri yok (benzer, <span class='t'>tahmini</span>)", "–"],
    ["Kütle", "60 g", "60 g (datasheet, probots)", "55 g"],
    ["Gövde", "40 × 20 × 40,4; kulakla 54,5; delik 49,5 × 10; kulak altı 27,7; 25T", "40 × 20 × 40 (Robocombo) / 38,5 (datasheet) / 40,5 (probots); delik dizilimi aynı <span class='t'>varsayıldı</span>; 25T", "40,7 × 19,7 × 42,9; 25T"],
    ["Dişli oranı / motor", "236 / 3 kutuplu", "373 / coreless (datasheet)", "–"],
    ["Fiyat (24.10.2026)", "964,50 TL (maliyet.json)", "<b>1.171,50 TL</b> indirimli · 1.255 TL liste, stok 134 (KDV dahil)", "199 TL"],
]))
o.append("<p class='not'>Kaynaklar: <a href='https://www.robocombo.com/dsservo-ds3235-35kg-servo-motor-180-derece-su-4148'>Robocombo DS3235</a> · "
         "<a href='https://hajim.rochester.edu/me/sites/kelley/me240/DS3235-270_datasheet.pdf'>DS3235 datasheet (Rochester ME240 kopyası)</a> · "
         "<a href='https://probots.co.in/servo-ds3235-35kg-180-degrees-high-torque-high-speed-digital-steering-gear.html'>probots DS3235</a> · "
         "<a href='https://itgresa.com/wp-content/uploads/2025/10/DS-Servo-20kg-DS3218-PRO-datasheet-PDF.pdf'>DS3218 datasheet</a> · MG996R Tower Pro datasheet "
         "(04-parca-olculeri.md). <b>Model uyarısı:</b> Robocombo sayfasının başlığı \"DS3235 … Su Geçirmez\", teknik tablosu DS3235 (40 × 20 × 40, 32 kg·cm @6 V), "
         "ama açıklama metni \"RDS3235 35KG … U Servo Braket Dahil\" diyor. Aynı mağazada ayrı ürünler: Coreles DS3235 (1.796,50 TL), Coreles RDS3235 "
         "(1.707 TL). RDS3235 çift milli \"robot\" sürümüdür; omuz yuvası ve göbek DS gövdesine göre çizildi: siparişten önce satıcıya sorulmalı. "
         "Stall akımı kaynaklar arasında tutarsız; hat hesabı ihtiyatlı 3,0 A ile yapıldı (datasheet 2,1 A ile tepe ~2 A düşer).</p>")

# ------------------------------------------------------------------ 2 kol kutleleri
o.append("<h2>2. Kol kütleleri (sağ kol; sol aynı)</h2>")
rows = []
for v in D["varyant"]:
    rows.append(["×%s" % sayi(v["oran"], 2), sayi(v["kol_boy_mm"], 1), sayi(v["el_ucu_y"], 0), sayi(v["tup_boy_mm"], 1), sayi(v["yaka_boy_mm"], 1),
                 sayi(v["kol_kutle_g"], 1), sayi(v["S1_ile_donen_g"], 1), sayi(v["kol_am_s_mm"], 1), sayi(v["I_S1_kgm2"] * 1e4, 1), sayi(v["I_S2_kgm2"] * 1e4, 1)])
o.append(tablo(["Oran", "Kol boyu (S1 → el ucu) mm", "El ucu y (yerden) mm", "Üst kol tüpü mm", "El boynu (yaka) mm", "S2 altı kol g",
                "S1 ile dönen g (göbek 175,2 dahil)", "Kol AM'si S1'den mm", "I (S1) kg·cm²", "I (S2) kg·cm²"], rows, "sayi"))
o.append("<p class='not'>×1,15 = taslak geometrisi (<code>kutle.json</code>, parça parça). ×1,25 / ×1,36 = <code>taslak_hesap.py</code> yöntemi: ek boy tüp : yaka = 30 : 19, "
         "birim kütleler taslak uzatmalarından (tüp %s g/mm, yaka %s g/mm); geometri modellenmedi, <span class='t'>tahmini</span>. Atalet en kötü statik pozda "
         "(kol öne / yana düz), parça ataletleri dahil. DS3235 ve DS3218 ikisi de 60 g: servo değişimi kütleyi değiştirmez.</p>" % (
             sayi(H["kol_orani"]["birim_kutle"]["tup_g_mm"], 3), sayi(H["kol_orani"]["birim_kutle"]["yaka_g_mm"], 3)))

# ------------------------------------------------------------------ 3 servo paylari
o.append("<h2>3. Servo payları (en kötü poz, yüksüz kol; elde yük 2× pay ile)</h2>")
rows = []
for j in ("S1", "S2"):
    e = eski[j]
    rows.append(["125 cm (×1,00)", j, "DS3218MG", sayi(e["yuksuz_kgcm"], 2), sayi(e["ivme_kgcm"], 2), "20 (proje)", pay_html(e["yuksuz_pay"]),
                 pay_html(e["toplam_pay"], 1.5, 1.0), sayi(e["izinli_yuk_2x_g"], 0), "–"])
for v in D["varyant"]:
    for sv in SV:
        for e in v["servo"][sv]["eklem"]:
            if e["eklem"] == "Bilek" and sv == "DS3235":
                continue
            if e["eklem"] in ("Dirsek", "Bilek") and sv == "DS3235":
                continue
            rows.append(["×%s" % sayi(v["oran"], 2), e["eklem"], e["servo"], sayi(e["statik_kgcm"], 2), sayi(e["ivme_kgcm"], 2),
                         "%s (6 V: %s)" % (sayi(e["stall_eff"], 1), sayi(e["stall_6V"], 1)), pay_html(e["pay_statik"]), pay_html(e["pay_ivmeli"], 1.5, 1.0),
                         sayi(e["yuk_2x_g"], 0) if e["eklem"] != "Bilek" else "– (kanca)", sayi(e["yuk_ivmeli_15x_g"], 0) if e["eklem"] != "Bilek" else "–"])
o.append(tablo(["Kol", "Eklem", "Servo", "Statik kg·cm", "İvme kg·cm", "Stall kg·cm (servo gerilimi)", "Statik pay", "İvmeli pay",
                "Elde yük g (2× statik)", "Elde yük g (1,5× ivmeli)"], rows, "sayi"))
o.append("<p class='not'>Statik: <code>taslak_hesap.kol_servo</code> ızgarası (S1 −45…135 × S2 5…120 × dirsek 0…105, 5°; bilek −90/0/90); bu betikte kopyalanıp "
         "<code>analiz/hesap.json</code> ile aynı olduğu doğrulandı. İvme: 60°/0,4 s üçgen profil (α 26,2 rad/s², <span class='t'>tahmini</span>), en kötü pozda "
         "eksen ataleti × α. Stall, S1 kalkış anındaki servo gerilimiyle (hat 6,0 V − 16 AWG − 22 AWG uzatma düşümü: DS3235 %s V, DS3218 %s V) datasheet "
         "noktaları arasında doğrusal. Ölçüt (proje): statik pay ≥ 2 yeşil, 1,2–2 sarı; ivmeli için bu raporda ≥ 1,5 yeşil, 1,0–1,5 sarı. Bilek her durumda "
         "yüzlerce kat pay (yükü kanca taşır, bilek ekseni kol boyunca). <b>Dirsek MG996R</b> uzayan önkolda yeter: statik %s… %s×, 2× payla %s… %s g; elde yükü "
         "sınırlayan omuz. Dirsekte sorun yük değil geri sürme (Bölüm 5).</p>" % (
             sayi(var(1.25)["servo"]["DS3235"]["hat"]["V_servo_S1_stall"]["22AWG"], 2), sayi(var(1.25)["servo"]["DS3218MG"]["hat"]["V_servo_S1_stall"]["22AWG"], 2),
             sayi(ek(1.36, "DS3235", "Dirsek")["pay_statik"], 2), sayi(ek(1.15, "DS3235", "Dirsek")["pay_statik"], 2),
             sayi(ek(1.36, "DS3235", "Dirsek")["yuk_2x_g"], 0), sayi(ek(1.15, "DS3235", "Dirsek")["yuk_2x_g"], 0)))
rows = []
for v in D["varyant"]:
    for sv in SV:
        s = v["servo"][sv]["secenek_64V_20AWG"]
        e = ek(v["oran"], sv, "S1")
        iv05 = e["statik_kgcm"] + e["ivme_kgcm"] * (0.4 / 0.5) ** 2
        rows.append(["×%s" % sayi(v["oran"], 2), sv, sayi(s["V_servo"], 2), sayi(s["stall"], 1), pay_html(s["pay_statik"]), pay_html(s["pay_ivmeli"], 1.5, 1.0),
                     sayi(s["yuk_2x_g"], 0), pay_html(e["stall_eff"] / iv05, 1.5, 1.0)])
o.append("<h3>İyileştirme: XL4016 çıkışı 6,4 V + S1/S2 uzatması 20 AWG; yavaş profil</h3>")
o.append(tablo(["Kol", "Omuz servosu", "S1 kalkışta servo gerilimi V", "Stall kg·cm", "Statik pay", "İvmeli pay", "Elde yük g (2×)",
                "İvmeli pay, 60°/0,5 s profil (6 V hat)"], rows, "sayi"))
o.append("<p class='not'>6,4 V tüm hattın sınırları içinde: DS3235 6–7,4 V, MG996R 4,8–7,2 V, DS3218 ≤ 6,8 V (DS3218 kalacaksa 6,4 V yine uygun). Servo ısısı ve "
         "boşta akım biraz artar (<span class='t'>tahmini</span>). Yavaş profil: α ∝ 1/t², 0,5 s'de ivme torku %64'e iner.</p>")

# ------------------------------------------------------------------ 4 akim
o.append("<h2>4. Akım bütçesi (servo hattı A: sağ kol 4 servo + pan; B simetrik, tilt ile)</h2>")
rows = []
for v in D["varyant"]:
    for sv in SV:
        h = v["servo"][sv]["hat"]
        c = lambda st: "<span class='%s'>%s</span>" % ({"yeter": "ok", "sinirda": "uy"}.get(st, "no"), {"yeter": "yeter", "sinirda": "sınırda (ölç)", "yetmez": "yetmez"}.get(st, st))
        rows.append(["×%s" % sayi(v["oran"], 2), sv, sayi(h["tutma_A"], 2), sayi(h["yogun_A"], 2), c(h["xl_yogun"]), sayi(h["tepe_A"], 2),
                     "<span class='ok'>yeter</span>" if h["tepe_A"] <= 8.0 else "<span class='uy'>8 A sınırına çarpar</span>", sayi(h["teorik_A"], 2),
                     sayi(h["giris_tepe_A"], 2), "%s / %s" % (sayi(h["V_servo_S1_stall"]["22AWG"], 2), sayi(h["V_servo_S1_stall"]["20AWG"], 2))])
o.append(tablo(["Kol", "Omuz servosu", "Uzanmış tutma A", "Yoğun A", "XL4016 (sürekli ≤ 5 A)", "Gerçekçi tepe A", "XL4016 (8 A)", "Teorik (hepsi stall) A",
                "Giriş akımı (7,5 A sigorta) A", "S1 kalkışta servo V (22 / 20 AWG)"], rows, "sayi"))
o.append("<p class='not'>Model (<span class='t'>tahmini</span>): servo akımı torkla doğrusal, I = I₀ + (I_stall − I₀) · T / T_stall (I₀ 0,15 A hareket, 0,01 A tutma). "
         "Yoğun = S1 ve S2 aynı anda en kötü statik + ivme torkunda, dirsek statik + ivme, bilek 0,4 A, pan 0,6 A (E1). Aynı model 125 cm / DS3218 için E1'in "
         "4,4 A'ini verir (kalibrasyon). Gerçekçi tepe = iki omuz servosu kalkışta (stall akımı) + diğerleri yoğunda. Teorik tepe XL4016'nın akım sınırına çarpar "
         "(gerilim düşer, servo resetlenebilir; E1'de kabul edilmiş). <b>DS3235 aynı torku daha az akımla verir</b> (datasheet: 32 kg·cm / 2,1 A; DS3218 "
         "20 kg·cm / 2,2 A): yoğun akım DS3218'den düşük, yalnız tepe (ihtiyatlı 3,0 A stall) yüksek. 16 AWG (0,6 m, 8 mΩ) ve 7,5 A giriş sigortası her "
         "durumda yeter. ×1,25 / ×1,36'da yoğun akım 5 A'i geçiyor: E1'deki kural geçerli: <b>ölçümde hat sürekli > 5 A ise o hatta 20 A / 300 W "
         "düşürücü</b> (ör. 6–40 V giriş, 1,2–36 V çıkış modülü; Türkiye fiyatı bulunamadı, ~400–600 TL <span class='t'>tahmini</span>). Kablo: S1/S2 "
         "uzatmaları 1,45–1,55 m (taslakta +0,435 m), 22 AWG'de S1 kalkışında 0,5 V düşüm; 20 AWG ile 0,35 V.</p>")

# ------------------------------------------------------------------ 5 yapisal
o.append("<h2>5. Yapısal yükler ve emniyet katsayıları</h2>")
o.append("<div class='karar'><b>Yük durumları.</b> L1 statik: en kötü yatay poz (kol öne ya da yana düz), sürekli (sürünme ×0,45). L2: L1 + 60°/0,4 s ivme "
         "(kısa). L3: servo stall, el ucu engelde (masaya bastırma, biri kolu tutuyor): S1 ve S2 aynı anda, iki düzlem vektörel; dirsekte omuzun geri sürme "
         "torku; sürünme ×0,7 (dakikalar). L4 darbe: kol jest tepe hızında (ω 5,24 rad/s, el ucu ~2 m/s) sert bir engele çarpar; enerji yöntemi "
         "F = v·√(m_eff·k), k = servo dişli esnemesi (stall torkunda 1°) + tüp eğilmesi + temas 20 N/mm, hepsi <span class='t'>tahmini</span>; "
         "gerekçe: masa kenarı / kapı pervazı / duvara jest sırasında çarpma, sınıf ortamında en olası kaza.<br><b>İzinli gerilme</b> = malzeme dayanımı "
         "(katman yönüne göre) × doluluk (PETG-CF 0,9, PETG 0,8) × sıcaklık (0,85 gövde içi 40 °C; 0,75 servoya değen parça 50 °C) × sürünme. "
         "<b>Ölçüt:</b> SF ≥ 2 güvenli, 1,2–2 sınırda, &lt; 1,2 yetersiz (projenin servo / devrilme ölçütüyle aynı).</div>")
o.append(tablo(["Malzeme", "X-Y (katman düzleminde)", "Z (katmanlar arası)", "E", "Kaynak"], [
    ["PETG-CF (Polymaker Fiberon PETG-rCF08)", "59,8 MPa", "41,1 MPa", "3,71 / 2,65 GPa", "<a href='https://fiberon.polymaker.com/wp-content/uploads/TDS_FIBERON-PETG-rCF08_V1.0_EN.pdf'>TDS V1.0</a>; HDT 65,7 °C @1,8 MPa, Tg 69,7 °C"],
    ["PETG (Microzey HS PETG; değerler Prusament PETG)", "47 MPa (akma)", "18 ± 4 MPa (katman yapışması)", "1,5 GPa", "<a href='https://www.3dprintergear.com.au/assets/files/technical-data-sheet%20(1).pdf'>Prusament PETG TDS v1.1</a>; HDT 68 °C. Microzey verisi yok: <span class='t'>temsili</span>"],
]))
o.append("<p class='not'>Baskı yönleri (modül baskı analizinden): üst kol tüpü +Y (eksen dik → eğilme katmanlar arası), kol çatalı −Z (katman düzleminde), dirsek çatalı −Y "
         "(kollar katmanlar arası), ön kol −Z (katman düzleminde), bilek flanşı −Y, el +Y (yaka katmanlar arası). Sürünme ve sıcaklık katsayıları "
         "<span class='t'>tahmini</span> (PETG uzun süreli sürünme-kopma dayanımı kısa sürelinin ~%40–50'si; HDT 66–68 °C).</p>")

# en zayif halka matrisi (baski parcalari)
o.append("<h3>Baskı parçaları: her durumda en düşük emniyet</h3>")
rows = []
for v in D["varyant"]:
    for sv in SV:
        r = ["×%s" % sayi(v["oran"], 2), sv]
        for dur in DUR:
            m = mn[(v["oran"], sv, dur)]
            r.append("%s<br><span class='not'>%s</span>" % (sf_html(m["sf"], m["sinif"]), esc(m["eleman"])))
        rows.append(r)
o.append(tablo(["Kol", "Omuz servosu"] + list(DUR.values()), rows))

# baglanti / satin alinan en zayif
o.append("<h3>Bağlantılar ve satın alınan parçalar: her durumda en düşük üç</h3>")
rows = []
for v in D["varyant"]:
    for sv in SV:
        r = ["×%s" % sayi(v["oran"], 2), sv]
        for dur in DUR:
            b = sorted([x for x in v["servo"][sv]["yapisal"]["baglanti"] if x["durum"] == dur], key=lambda x: x["sf"])[:3]
            r.append("<br>".join("%s <span class='not'>%s</span>" % (sf_html(x["sf"], x["sinif"]), esc(x["eleman"])) for x in b))
        rows.append(r)
o.append(tablo(["Kol", "Omuz servosu"] + list(DUR.values()), rows))

# ayrintili tablolar
for v in D["varyant"]:
    for sv in SV:
        ys = v["servo"][sv]["yapisal"]
        acik = " open" if (abs(v["oran"] - REC[0]) < 1e-9 and sv == REC[1]) else ""
        rows = []
        for r in ys["satir"]:
            rows.append([esc(r["eleman"]), DUR[r["durum"]], "%s (%s)" % (r["malzeme"], r["yon"]), esc(r["yuk"]), "%s MPa" % sayi(r["gerilme"], 2),
                         "%s MPa" % sayi(r["izin"], 2), sf_html(r["sf"], r["sinif"]), "<span class='not'>%s</span>" % esc(r["not_"])])
        for r in ys["baglanti"]:
            rows.append([esc(r["eleman"]), DUR[r["durum"]], "–", esc(r["yuk"]), "%s %s" % (sayi(r["deger"], 2), r["birim"]),
                         "%s %s" % (sayi(r["kapasite"], 1), r["birim"]), sf_html(r["sf"], r["sinif"]),
                         "<span class='not'>%s%s</span>" % (esc(r["not_"]), " · <span class='t'>tahmini</span>" if r["tahmini"] else "")])
        rows.sort(key=lambda x: 0)
        o.append("<details%s><summary>Ayrıntılı tablo: kol ×%s + %s (uç kuvveti stall %s N, darbe %s N; S2 altı kol ağırlığı %s N)</summary>%s</details>" % (
            acik, sayi(v["oran"], 2), sv, sayi(ys["F_stall_N"], 1), sayi(ys["darbe"]["S1"]["F_N"], 1), sayi(ys["W_kol_N"], 2),
            tablo(["Eleman", "Durum", "Malzeme (yön)", "Yük", "Gerilme / yük", "İzinli / kapasite", "SF", "Not"], rows)))

# darbe
o.append("<h3>Darbe (L4) ayrıntısı ve güvenli hız</h3>")
rows = []
for v in D["varyant"]:
    for sv in SV:
        dz = v["servo"][sv]["yapisal"]["darbe"]["S1"]
        rows.append(["×%s" % sayi(v["oran"], 2), sv, sayi(dz["m_eff_kg"] * 1000, 0), sayi(dz["v_uc"], 2), sayi(dz["k_servo"] / 1000, 2), sayi(dz["k_kol"] / 1000, 1),
                     sayi(dz["k_top"] / 1000, 2), sayi(dz["F_N"], 1), sayi(dz["M_omuz_kgcm"], 0), sayi(dz["stall_kati"], 1),
                     "%s rad/s (%s°/s)" % (sayi(dz["omega_guvenli"], 2), sayi(dz["omega_guvenli"] * 57.2958, 0))])
o.append(tablo(["Kol", "Servo", "m_eff g (el ucunda)", "v el ucu m/s", "k servo N/mm", "k kol N/mm", "k toplam N/mm", "F darbe N", "M omuz kg·cm",
                "× stall", "Güvenli hız (M ≤ stall)"], rows, "sayi"))
o.append("<p class='not'>Darbede en yumuşak eleman servo dişlisi olduğu için kuvveti o belirler; DS3235 daha rijit ve güçlü olduğundan darbe kuvveti ~%%20 büyür ama "
         "stall'a oranı küçülür. Motor rotorunun dişli oranıyla büyüyen ataleti hesaba katılmadı: gerçek darbe biraz daha büyük olabilir. Sonuç sayısal olarak "
         "<span class='t'>tahmini</span>, ama yön açık: tam jest hızında sert bir engele çarpma omuzda stall'ın 3–5 katı moment üretir; yük önce 25T horn kanalına, "
         "servo millerine ve dirsek bölgesine gelir. Engel yakınında ya da insan yanında jest hızı ~%s rad/s (~%s°/s) altında tutulmalı.</p>" % (
             sayi(Rs["yapisal"]["darbe"]["S1"]["omega_guvenli"], 1), sayi(Rs["yapisal"]["darbe"]["S1"]["omega_guvenli"] * 57.2958, 0)))

# ------------------------------------------------------------------ 6 en zayif halka + duzeltmeler
o.append("<h2>6. En zayıf halkalar ve düzeltmeler</h2>")
b3 = {x["eleman"]: x for x in Rs["yapisal"]["baglanti"] if x["durum"] == "L3"}
b2 = {x["eleman"]: x for x in Rs["yapisal"]["baglanti"] if x["durum"] == "L2"}
s4 = {x["eleman"]: x for x in Rs["yapisal"]["satir"] if x["durum"] == "L4"}
b4 = {x["eleman"]: x for x in Rs["yapisal"]["baglanti"] if x["durum"] == "L4"}
g = lambda dct, k: [x for n, x in dct.items() if n.startswith(k)][0]
zay = [
    ["1", "S2 servo mili (horn tarafı) radyal yükü", "kol öne uzanınca S1 yönündeki moment kol çatalında horn ile 625ZZ arasında (58,5 mm) çift kuvvete dönüşür; "
     "horn tarafını servo mili taşır: ivmeli %s N, stall %s N (referans 40 N, <span class='t'>tahmini</span>)" % (sayi(g(b2, "S2 servo mili")["deger"], 0), sayi(g(b3, "S2 servo mili")["deger"], 0)),
     "S2 horn tarafına ince destek rulmanı: kol çatalı ön kolu ile göbek ön plakası arasında servo miliyle eş eksenli, horn'u çevreleyen ince "
     "rulman (ör. 6806-2RS 30 × 42 × 7); servo yalnız tork verir. Kısa vadede: yazılımda ivme ≤ 60°/0,5 s, kol öne uzanmış beklemesin"],
    ["2", "25T alüminyum horn kanalı (S1, S2)", "DS3235 stall'ında diş yanak basıncı SF %s (DS3218: %s); darbede %s" % (
        sayi(g(b3, "S1 horn")["sf"], 2), sayi(g({x["eleman"]: x for x in var(REC[0])["servo"]["DS3218MG"]["yapisal"]["baglanti"] if x["durum"] == "L3"}, "S1 horn")["sf"], 2), sayi(g(b4, "S1 horn")["sf"], 2)),
     "kelepçeli (sıkma vidalı) 25T alüminyum horn (maliyet.json'daki Robiz kelepçeli tip), merkez M3'e orta mukavemet vida sabitleyici; yedek horn bulundur. "
     "Darbede ilk kayan horn olursa diğer parçaları korur (ucuz sigorta)"],
    ["3", "Dirsek MG996R'ın geri sürülmesi", "el takılırsa DS3235 stall'ı dirsekte MG996R stall'ının %s katı tork yapar (DS3218: %s); dişli zorlanır, dirsek çatalı dış kolu "
     "L3'te SF %s" % (sayi(Rs["dirsek_geri_surme_kati"], 2), sayi(var(REC[0])["servo"]["DS3218MG"]["dirsek_geri_surme_kati"], 2), sayi(g({x["eleman"]: x for x in Rs["yapisal"]["satir"] if x["durum"] == "L3"}, "Dirsek çatalı")["sf"], 2)),
     "yazılım: omuz servolarında hedefe ulaşamama (konum hatası > 5° ve 0,5 s) → komutu geri al (PCA9685 akım okumaz; dağıtım kartına hat akım sensörü "
     "INA219 ~60 TL <span class='t'>tahmini</span> ile aşırı akımda kes). Donanım seçeneği: dirseği DS3218MG yapmak (+1.531 TL / 2 kol; ön kol yeniden çizilir)"],
    ["4", "Bilek MG996R mili (el konsol)", "bilekte karşı yatak yok; el ve yaka konsolu mili eğer: stall'da eşdeğer %s N (referans 30 N, <span class='t'>tahmini</span>); yaka uzadıkça artar" % sayi(g(b3, "Bilek MG996R")["deger"], 0),
     "uzatmayı yakaya değil üst kol tüpüne / ön kola ver (yaka 32,6 mm kalsın); ya da bilek flanşını ön kolda ince rulmanla (6806-2RS 30 × 42 × 7) destekle"],
    ["5", "S1 servo mili + 6808 (omuz göbeği)", "S1 horn ile 6808 arası yalnız 8,15 mm: göbeğe gelen eğilme momenti (S2 torku + ağırlık) 6808 boşluğu kapanana dek S1 milinde; "
     "üst sınır %s, boşluk sınırlı tahmin %s N (<span class='t'>tahmini</span>, 125 cm tasarımda da var)" % (
         esc(g(b3, "S1 servo mili")["yuk"].split("üst sınır ")[1]), sayi(g(b3, "S1 servo mili")["deger"], 0)),
     "rulman kapağını 7 mm uzatıp ikinci 6808-2RS (2 × 106,80 TL) ile çift rulman (arası ≥ 10 mm): moment rulman çiftinde kalır, S1 yalnız döndürür (omuz raporundaki tasarım niyeti)"],
    ["6", "Darbe: dirsek çatalı dış kolu (5 mm, katmanlar arası)", "L4 SF %s; el yakası vidaları (yaka duvarı 2,85 mm) %s; üst kol tüpü penceresi %s" % (
        sayi(g(s4, "Dirsek çatalı")["sf"], 2), sayi(g(b4, "El yakası")["sf"], 2), sayi(g(s4, "Üst kol tüpü, kablo")["sf"], 2)),
     "dış kolu 5 → 7 mm dışa doğru (çakışma taraması yeniden) ya da PETG-CF; yaka vidası 2 → 4 adet ve yaka duvarı "
     "kalınlaştırma; tüp penceresi uçlarına R2 yuvarlatma. Asıl önlem hız sınırı (Bölüm 5)"],
]
o.append(tablo(["#", "Halka", "Neden / sayı (×%s + %s)" % (sayi(REC[0], 2), REC[1]), "Düzeltme"], zay))
o.append("<p class='not'>Kontrol edilip sorunsuz çıkanlar (her oran ve servoda, L1–L3): kol çatalı pimi ve ön kolu, üst kol tüpü (katmanlar arası dahil; en kötü SF "
         "pencerede), ön kol U kesiti, el boynu, horn cıvatalarında PETG ezilmesi, servo kulak cıvataları, rulman kapağı ısıl gömme somunları, M5 mafsal somunu, "
         "tüp ↔ pim vidaları, dirsek sıkma bileziği (sürtünme 20 N·m), 6808-2RS ve 625ZZ statik yük (C0'ın küçük bir kesri). Cıvata kesmesi hiçbir yerde "
         "belirleyici değil (M3 8.8 kesme ~1,9 kN).</p>")

# ------------------------------------------------------------------ 7 maliyet / kutle / devrilme
o.append("<h2>7. Maliyet, kütle ve devrilme özeti</h2>")
rows = []
dkg = lambda v: v["kol_kutle_g"] - var(1.15)["kol_kutle_g"]
for v in D["varyant"]:
    for sv in SV:
        servo_tl = 0.0 if sv == "DS3218MG" else D["maliyet"]["fark_indirimli"]
        fil = 2 * dkg(v) / 1000 * D["maliyet"]["filament_tl_kg"]
        dv = v["devrilme"]
        rows.append(["×%s" % sayi(v["oran"], 2), sv, "+%s" % sayi(servo_tl, 0), "+%s" % sayi(fil, 0), "%s%s" % ("+" if dkg(v) >= 0 else "", sayi(2 * dkg(v), 1)),
                     sayi(dv["yeni-444"]["izgara_duz"], 2), sayi(dv["yeni-444"]["izgara_rampa"], 2), sayi(dv["yeni-520"]["izgara_duz"], 2),
                     sayi(dv["yeni-444"]["one_yuk"]["pay_ileri"], 2)])
o.append(tablo(["Kol", "Omuz servosu", "Servo farkı TL (5 adet)", "Filament farkı TL", "Robot kütle farkı g (iki kol)", "Devrilme düz 444", "Devrilme 5° rampa 444",
                "Devrilme düz 520", "Kollar önde + 0,5 kg/el, ileri"], rows, "sayi"))
o.append("<p class='not'>Referans ×1,15 + DS3218MG (taslak). Devrilme: <code>taslak_hesap.py</code> yöntemi (en kötü yüksüz kol pozu ızgarası, pay = eşik / 1,5 m/s², "
         "ölçüt düz ≥ 2, rampa ≥ 1,5); kol uzaması etkisi küçük, belirleyici taban genişliği ve AM (taslak raporu). Servo değişimi kütleyi değiştirmez. "
         "Ek kalemler (öneriye bağlı, <span class='t'>tahmini</span>): S1/S2 uzatması 20 AWG (~6,5 m, ~200 TL), kelepçeli horn (mevcut horn satırının tipi, fark yok), "
         "ikinci 6808-2RS ×2 (213,60 TL), S2 destek rulmanı 6806-2RS ×2 (~150 TL), koşullu 20 A düşürücü ×2 (~800–1.200 TL, ölçüme bağlı). "
         "Önerilen paket (×1,25 + DS3235 + 20 AWG + 6808 çifti + S2 destek rulmanı) ≈ +%s TL, düşürücü gerekirse ≈ +%s TL.</p>" % (
             sayi(D["maliyet"]["fark_indirimli"] + 200 + 213.6 + 150, 0), sayi(D["maliyet"]["fark_indirimli"] + 200 + 213.6 + 150 + 1000, 0)))

# ------------------------------------------------------------------ 8 acik isler
o.append("<h2>Açık işler</h2>")
o.append(tablo(["İş", "Neden", "Öneri", "Kimde"], [
    ["DS3235 modelini teyit", "Robocombo açıklamasında RDS3235 / U braket geçiyor; gövde 38,5 / 40 / 40,5 mm farklı kaynaklarda", "satıcıya sor; gelince kumpas: gövde, kulak deliği 49,5 × 10, mil konumu, 25T", "satın alma"],
    ["Kol oranı kararı", "×1,25 önerildi; ×1,36 yavaş profil ister", "Duffy karar verince <code>taslak_ayar.py</code> (UST_KOL_UZAMA / EL_UZAMA) güncellenir, taslak montaj + kafa × kol çarpışma taraması yeniden (×1,25 / ×1,36 modellenmedi)", "Duffy + tasarım"],
    ["Uzatma dağılımı", "yaka uzadıkça bilek mili konsolu büyür", "×1,25'te ek 32,4 mm'yi tüpe / ön kola ver (yaka 32,6 kalsın); ön kol uzatılırsa bilek servosu yerini koru", "tasarım"],
    ["S2 horn tarafı destek rulmanı", "S2 mili radyal yükü (ivmeli ~40 N, stall ~80 N)", "omuz modülünde göbek ön plakası + kol çatalı ön koluna eş eksenli ince rulman (ör. 6806-2RS); çakışma ve tarama yeniden", "omuz"],
    ["Omuz 6808 çifti", "S1 mili ile 6808 arası 8,15 mm", "rulman kapağı + ikinci 6808; S1 servoyu tork-only yap", "omuz"],
    ["Servo hattı ölçümü", "yoğun akım 5 A'i geçebilir (×1,25+)", "E1 / E7 ölçümü (yük direnci ya da kollar uzanmış); > 5 A sürekli ise 20 A düşürücü; XL çıkışı 6,4 V", "elektrik"],
    ["Uzatma kablosu", "22 AWG'de S1 kalkışında 0,5 V düşüm, DS3235 6 V altına iner", "S1/S2 uzatmaları 20 AWG (ya da dağıtım kartları traverse seviyesine)", "elektrik"],
    ["Yazılım sınırları", "darbe stall'ın 3–5 katı; geri sürme", "jest hızı insan yakınında ≤ ~1,4 rad/s; ivme profili; konum hatası izleme ve tork geri alma; hat akım sensörü (INA219)", "yazılım"],
    ["Horn kanalı ölçümü", "25T horn diş boyu ve alaşımı bilinmiyor (spline hesabı 3,3 mm boy, 0,25 mm diş, 6061 varsayımı)", "horn gelince kumpas; kelepçeli tip seç", "satın alma"],
    ["Servo mili radyal kapasitesi", "DS / MG996R üreticisi vermiyor; 40 / 30 N referans XM430'dan", "basit test: servo kilitliyken horn'dan 10 mm'de el kantarıyla 40 N radyal, boşluk ve ses gözlemi", "ekip"],
    ["PETG malzeme kuponu", "Microzey HS PETG için TDS yok; katman yapışması 18 MPa varsayıldı", "aynı ayarla dikey basılmış çekme kuponu (tolerans kuponlarıyla birlikte)", "üretim"],
]))

# ------------------------------------------------------------------ varsayimlar
o.append("<h2>Varsayımlar</h2><ul>")
for t in [
    "Servo hattı 6,0 V (E1), XL4016 8 A / sürekli 5 A, hat sigortası 7,5 A, 16 AWG 8 mΩ; uzatmalar S1 1,45, S2 1,55, dirsek/bilek 2,0 m 22 AWG (taslak +0,435 m) <span class='t'>tahmini</span>.",
    "DS3235 stall akımı tasarımda 3,0 A @6 V (datasheet 2,1 A, satıcılar 2,2–3,9 A) <span class='t'>tahmini</span>; DS3218 6 V'ta 20,4 kg·cm (19 @5 V, 21,5 @6,8 V arası doğrusal; proje 20 kullanır).",
    "×1,25 / ×1,36 kolları modellenmedi: <code>taslak_hesap.py</code> yöntemiyle doğrusal uzatma (tüp : yaka = 30 : 19), <span class='t'>tahmini</span>.",
    "İvme profili 60°/0,4 s üçgen (α 26,2 rad/s², tepe 5,24 rad/s), <span class='t'>tahmini</span>; yük ataleti el ucunda nokta kütle.",
    "Yapısal model 1 boyutlu: kesit momenti kesit altındaki kütlelerden ve el ucu kuvvetinden; kesit modülleri parça betiklerindeki ölçülerden sayısal; gerilme yığılması Kt 1,5–2,5 <span class='t'>tahmini</span>.",
    "Sürünme ×0,45 (sürekli), ×0,7 (stall, dakikalar), sıcaklık ×0,85 / ×0,75, doluluk PETG-CF 0,9 / PETG 0,8: hepsi <span class='t'>tahmini</span>.",
    "Isıl gömme somun çekme kapasitesi π·D·L·τ, τ = 9 MPa (katman yapışmasının yarısı): M3 ~740 N, <span class='t'>tahmini</span> (kaynaklı test verisi bulunamadı).",
    "25T horn kanalı: diş yanak basıncı, yük paylaşımı 0,5, diş 0,25 mm, boy 3,3 mm, izinli 138 MPa (6061-T6 akmasının yarısı), <span class='t'>tahmini</span>.",
    "Servo mili radyal kapasitesi referansı ROBOTIS XM430: 40 N horn'dan 10 mm (<a href='https://emanual.robotis.com/docs/en/dxl/x/xm430-w350'>e-Manual</a>); MG996R 30 N; ikisi de <span class='t'>tahmini</span>.",
    "6808 eğilme boşluğu 10′, S1 mil radyal rijitliği 2 N/µm; rulman yük değerleri SKF 61808-2RS1 (C0 3,75 kN) × 0,7 ve SKF 625-2Z (C0 0,38 kN) (RS Online), KWC/BGR eşdeğeri <span class='t'>tahmini</span>.",
    "Darbe: servo stall torkunda 1° esneme, temas 20 N/mm, tüp eğilmesi E 1,5 GPa; motor rotoru ataleti dahil değil: <span class='t'>tahmini</span>.",
]:
    o.append("<li>%s</li>" % t)
o.append("</ul>")
o.append("<h2>Dosyalar ve çalıştırma</h2><ul><li><code>kol_analiz.py</code> (sistem Python'u, ~2 dk; <code>taslak_hesap.py</code> ve <code>analiz/girdi-yeni-*.json</code>, "
         "<code>kutle.json</code> okur) → <code>kol-analiz.json</code></li><li><code>kol_rapor.py</code> → bu rapor (<code>rapor.html</code>)</li>"
         "<li><code>NOTLAR.md</code>: çalışma notları ve kaynak listesi</li><li>Ana taslak dosyaları, modüller, <code>arayuz.py</code>, <code>maliyet.json</code> değişmedi.</li></ul>")
o.append("</main></body></html>")
open(os.path.join(HERE, "rapor.html"), "w", encoding="utf-8").write("\n".join(o))
print("rapor.html yazildi")
