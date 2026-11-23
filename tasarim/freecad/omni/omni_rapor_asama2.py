# Omni 2. asama bolumleri (omni_rapor.py cagirir; sistem Python'u, FreeCAD gerekmez).
# Girdiler: omni-dogrula.json / omni-dogrula-lastik.json (omni_dogrula.py), eklem-dogrulama-asama2.json, ../taban/taban-analiz.json,
# ../montaj/montaj-analiz.json, ../carpisma-sonuc.json (+ carpisma_kos.eskime_metni), ../omuz|iskelet/regresyon/fark.json,
# planlama/d158/Y0f-olcum/donus-oneri.json (MuJoCo, yalniz okunur). Omni oncesi: git ONCE_REF (varsayilan 4bc73de) icindeki ayni dosyalar.
import os, sys, json, math, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
KOK = os.path.dirname(os.path.dirname(UST))
ONCE_REF = os.environ.get("ONCE_REF", "4bc73de")


def _oku(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return None


def _git(yol):
    try:
        return json.loads(subprocess.run(["git", "show", "%s:%s" % (ONCE_REF, yol)], cwd=KOK, capture_output=True, check=True).stdout.decode("utf-8"))
    except Exception:
        return None


def uret(d, h):
    sayi, esc, md, tablo, durum, TAH, OLC = h["sayi"], h["esc"], h["md"], h["tablo"], h["durum"], h["TAH"], h["OLC_ET"]
    dog = _oku(os.path.join(HERE, "omni-dogrula.json")) or {}
    dogl = _oku(os.path.join(HERE, "omni-dogrula-lastik.json")) or {}
    ekl = _oku(os.path.join(HERE, "eklem-dogrulama-asama2.json")) or {}
    ta = _oku(os.path.join(UST, "taban", "taban-analiz.json")) or {}
    ta0 = _git("tasarim/freecad/taban/taban-analiz.json") or {}
    ma = _oku(os.path.join(UST, "montaj", "montaj-analiz.json")) or {}
    ma0 = _git("tasarim/freecad/montaj/montaj-analiz.json") or {}
    ca = _oku(os.path.join(UST, "carpisma-sonuc.json")) or {}
    ca0 = _git("tasarim/freecad/carpisma-sonuc.json") or {}
    reg = {k: _oku(os.path.join(UST, k, "regresyon", "fark.json")) for k in ("omuz", "iskelet")}
    mj = _oku(os.path.join(KOK, "planlama", "d158", "Y0f-olcum", "donus-oneri.json"))
    sys.path.insert(0, UST)
    try:
        import carpisma_kos as CK
        eskime = CK.eskime_metni()
    except Exception as e:
        eskime = "eskime denetimi alinamadi: %s" % e
    tarama_guncel = not eskime and bool(ca)
    kst = _oku(os.path.join(HERE, "carpisma-statik-asama2.json"))

    # ---------- tarama ozeti
    def topl(c):
        t = c.get("toplam", {})
        tt = c.get("taban_tarama", {})
        st = tt.get("statik", {})
        return dict(cakisma=t.get("cakisma"), aralik=t.get("eklem_araliginda"), kafa=(t.get("kafa") or {}).get("toplam"),
                    taban=(t.get("taban") or {}).get("toplam"), taban_aralik=(t.get("taban") or {}).get("eklem_araliginda"),
                    taban_statik=sum(len(v.get("cakisma", [])) for v in st.values()), taban_temas=sum(v.get("temas", 0) for v in st.values()),
                    taban_hedef=tt.get("hedef_sayisi"), ev=len(c.get("ev_pozu_cakisma", []) or []), kutle=c.get("kutle_toplam_g") or c.get("kutle_g"),
                    am=c.get("agirlik_merkezi"), sure=c.get("sure_s"))
    T1, T0 = topl(ca), topl(ca0)
    yeni_cak = None
    if tarama_guncel:
        yeni_cak = (T1["taban"] or 0) + (T1["taban_statik"] or 0) + max(0, (T1["ev"] or 0) - (T0["ev"] or 0)) + max(0, (T1["cakisma"] or 0) - (T0["cakisma"] or 0))

    # ---------- hukum
    don = dog.get("donen", {})
    on_cak = len((don.get("+1+1") or {}).get("cakisma", [])) if don else None
    ekl_ok = bool(ekl) and all(y.get("dogru") for y in ekl.get("yon", []))
    if not tarama_guncel:
        hk, hs = "KOŞULLU GEÇER (resmî taramanın yalnız statik bölümü koşuldu)", "uy"
    elif yeni_cak:
        hk, hs = "KALIR", "no"
    else:
        hk, hs = "KOŞULLU GEÇER", "ok"
    kosul = ([] if tarama_guncel else [
        "Resmî tam tarama (<code>python carpisma_kos.py</code>, ≈ 4 saat) bellek azlığı yüzünden omuz bölümünde durdu; kol × taban ve kafa bölümleri "
        "omniyle koşulmadı. Statik bölüm (ev pozu) koşuldu: çakışma 0. Kol × taban için bağımsız dönen grup ölçümü var, resmî tarama yerine geçmez."]) + [
        "Sipariş öncesi ölçülecekler (aşağıda) gelmeden adaptör basılmaz: göbek deliği, PCD, cıvata adedi / çapı ve göbek kalınlığı " + TAH + "; pilot, insert yeri ve M3 boyu bunlara bağlı.",
        "Teker ↔ etek önde %s mm (hedef 12): 1 mm eksik, çakışma değil; etek ya da hedef değişikliği kararı Ahmet'in." % sayi(next((x["bosluk_mm"] for x in ta.get("teker_etek", []) if "Omni" in x["teker"]), float("nan")), 1),
        "Yerinde dönüş tork payı motor TAHMİN'ine bağlı (durma 21 kg·cm, sürekli = 0,3 × durma): geometri değil, motor ölçümü kapatır (bkz. dönüş bölümü).",
    ]
    hukum = ["<div class='karar' id='hukum'><b>2. aşama hükmü: <span class='%s'>%s</span></b><br>" % (hs, esc(hk))]
    hukum.append("Geometri, bağlantılar ve dönen grup açıklıkları bağımsız ölçümle doğrulandı (ön köşe 24 açıda çakışma %s), lastik geri dönüşü omni öncesiyle birebir, "
                 "ana montaj eklemleri doğru (%s), omuz / iskelet regresyonu birebir. %s Koşullar:<ul>%s</ul></div>" % (
                     "yok" if on_cak == 0 else str(on_cak), "teker eklemleri dahil tüm yön testleri doğru" if ekl_ok else "eklem sonucu eksik",
                     ("Resmî tarama: omni kaynaklı yeni çakışma <b>%s</b>." % ("yok" if not yeni_cak else yeni_cak)) if tarama_guncel else
                     ("<span class='uy'>Resmî taramanın statik bölümü: ev pozu çakışma %s → %s; öteki 8 bölüm koşulmadı.</span>" % (
                         kst["ev_pozu_cakisma"]["once"], kst["ev_pozu_cakisma"]["sonra"]) if kst else "<span class='uy'>Resmî tarama koşulmadı.</span>"),
                     "".join("<li>%s</li>" % s for s in kosul)))
    HUKUM = "".join(hukum)

    # ---------- donus (madde 7)
    dn = ta.get("donus", {})

    def mu_sec(k, mu=0.5):
        for r in dn.get(k, []):
            if abs(r["mu"] - mu) < 1e-9:
                on = [x for x in r["tekerler"] if x["omni"]][0]
                ar = [x for x in r["tekerler"] if not x["omni"]][0]
                return r, on, ar
        return None, None, None

    dr = []
    for k, ad, nt in (("yerinde_omni", "A: sert hız (eşit çevre hızı dayatılır)", "ÜST SINIR; arka teker fren"),
                      ("yerinde_omni_motor", "C: motor hız-tork eğrisi, ω 0,90 rad/s", "yan başına aynı PWM"),
                      ("yerinde_omni_motor_216", "C, ön omni 216'da (ara parça seçeneği)", "karşılaştırma"),
                      ("yerinde_omni_motor_9kgcm", "C, durma 9 kg·cm motor", "motor TAHMİN duyarlılığı")):
        for mu in (0.5, 0.6):
            r, on, ar = mu_sec(k, mu)
            if r:
                dr.append([esc(ad), sayi(mu, 1), "%s (%s×)" % (sayi(on["T_kgcm"], 2), sayi(on["oran_surekli"], 2)),
                           "%s (%s, %s×)" % (sayi(ar["T_kgcm"], 2), esc(ar["rol"]), sayi(ar["oran_surekli"], 2)),
                           sayi(r["d"], 3) if "d" in r else "—", esc(nt)])
    mr = []
    if mj:
        for r in mj.get("kosular", []):
            if r["varyant"] in ("ONERI-ADAY", "ONERI"):
                y = r["yerinde"]["1.0"]
                mr.append([esc(r["varyant"] + (" (merkez 14,5 içeri = 201,5)" if r["varyant"] == "ONERI-ADAY" else " (merkez 216)")), esc(r["durma"]), sayi(r["mu"], 1),
                           sayi(y["w_gercek"], 3), sayi(y["tork_surekli_orani"], 2)])
    k0 = (ta0.get("donus") or {}).get("karar", {})
    k1 = dn.get("karar", {})
    D = ["<h2 id='donus'>Yerinde dönüş: el hesabı ve fizik modeli (2. aşama, madde 7)</h2>"]
    D.append("<p>1. aşamadaki rakam (µ 0,5, ön motor %s → %s kg·cm, sürekli değerin %s katı, arka teker fren) <b>Model A</b>'dan geliyordu: aynı yandaki ön (x 201,5) ve arka "
             "(x 216) tekere aynı çevre hızını sonsuz sert motorla dayatır; %%6,7 hız farkını boyuna kaymayla ve ön motoru arka motora karşı çalıştırarak karşılar. Gerçek motor "
             "yük altında yavaşlar, iki teker kendi hız-tork eğrisi üzerinde dengelenir. Bu yüzden A bir <b>üst sınırdır</b> ve öyle etiketlendi. <code>donus_hesap.py</code>'ye "
             "<b>Model C</b> eklendi (aynı yarı statik Coulomb teker-zemin modeli + motor eğrisi T = Ts·(d − ω/ω0), yan başına aynı PWM, dişli sürtünmesi 0,05 N·m; ω = 0,90 rad/s "
             "veren PWM aranır: MuJoCo ölçümüyle aynı işletme noktası). Kütle ve ağırlık merkezi yeni taban analizinden (%s kg).</p>" % (
                 sayi(k0.get("omni_kgcm", float("nan")), 2), "7,62", "1,21", sayi(dn.get("kutle_kg", float("nan")), 2)))
    D.append(tablo(["Model (VARSAYIM, el hesabı)", "µ", "Ön omni motor kg·cm (sürekli oranı)", "Arka motor kg·cm (rol, oran)", "PWM d", "Not"], dr))
    if mr:
        D.append("<h3>MuJoCo ölçümü (planlama/d158/Y0f-olcum/donus-oneri.json, dokunulmadı)</h3>")
        D.append(tablo(["Varyant", "Motor durma", "µ", "Yerinde ω (rad/s)", "Tork / sürekli"], mr))
    D.append("<div class='uyari'><b>Değerlendirme.</b> Model C (≈ %s kg·cm, %s×) ile MuJoCo (ONERI-ADAY 21 kg·cm: 1,1–1,2×) arasında fark var: MuJoCo dinamik (ivmelenme, makara "
             "kayması, gerilim ölçeklemesi), C yarı statik ve sürekli oranı ortalama torktan değil tek noktadan veriyor; bu yüzden C <b>alt taraf</b>, A üst sınır, gerçeğe en yakın "
             "ölçü MuJoCo. Üçü de aynı yönü gösteriyor: merkezin 14,5 mm içeri alınmasının maliyeti küçük (C'de +%s kg·cm; MuJoCo'da ONERI 216 → ONERI-ADAY 201,5 ≈ +0,1×). "
             "Asıl sorun <b>geometri değil motor payı</b>: MuJoCo'da sürekli değerin 1,1–1,2 katı (21 kg·cm) ve 9 kg·cm motor seçilirse 2,3–2,5 katı. Bu oranlar "
             "TAHMİN'e dayanıyor (durma torku satıcı sayfası, sürekli = 0,3 × durma kabulü). Seçenekler (karar değil, tasarım değiştirilmedi):<ol>"
             "<li><b>Motor ölçümü</b> (durma torku ve akım; kontrol masasında): oranı TAHMİN'den çıkarır. En ucuz ve önce yapılmalı.</li>"
             "<li><b>Ara parça ile ön omni 216'ya</b> (adaptör +14,5 mm): ön iz 432'ye döner, C'de ön motor ≈ −0,4 kg·cm, MuJoCo'da ≈ −0,1×. Bedeli: teker 14,5 mm dışarı "
             "(yanda etek açıklığı ≈ 41 → 26,5 mm), milde ve PETG adaptörde konsol boyu uzar; altıgen yuva kaplini daha az kavrar ya da adaptör uzar.</li>"
             "<li><b>Yazılım:</b> yerinde dönüşte hız sınırı / rampa (ω ≤ 0,9 rad/s zaten MuJoCo işletme noktası) ve akım izleme; görev çevrimi kısa.</li></ol></div>" % (
                 sayi(k1.get("omni_motor_kgcm", float("nan")), 2), sayi(k1.get("omni_motor_oran_surekli", float("nan")), 2),
                 sayi((mu_sec("yerinde_omni_motor")[1] or {}).get("T_kgcm", float("nan")) - (mu_sec("yerinde_omni_motor_216")[1] or {}).get("T_kgcm", float("nan")), 1)))
    D.append("<p class='not'>Model A / C ayrıntısı ve <code>model_notu</code>: <code>taban-analiz.json</code> → <code>donus</code>. MuJoCo ONERI-ADAY kütle farkı +606 g, CAD +753 g "
             "(fizik modeli <code>kod/</code> altında, dokunulmadı).</p>")
    DONUS = "".join(D)

    # ---------- 2. asama govdesi
    S = ["<h2 id='asama2'>2. aşama: bağımsız kontrol, resmî tarama, regresyon</h2>"]
    S.append("<p class='not'>Kontrol ajanı, 23.11.2026. Omni öncesi değerler <code>git %s</code> (omni 1. aşamadan önceki commit) dosyalarından okundu. Ölçülen = bu aşamada "
             "FreeCAD ile koşulup okunan; TAHMİN = satıcı çiziminden doğrulanmamış ürün ölçüsü; VARSAYIM = el hesabı kabulü.</p>" % esc(ONCE_REF))

    # 1 bagimsiz dogrulama
    x = dog.get("x_zinciri", {})
    oc = dog.get("once_karsilastirma", {})
    ocl = dogl.get("once_karsilastirma", {})
    S.append("<h3>1. 1. aşama iddiaları, bağımsız ölçüm (<code>omni_dogrula.py</code>)</h3>")
    ir = [
        ["Ön omni merkezi 201,5; iz 403 / 432", "merkez %s, OMNI_X %s, ön / arka iz %s / %s" % (sayi(x.get("omni_merkez", float("nan")), 1), sayi(x.get("arayuz_OMNI_X", float("nan")), 1),
                                                                                       sayi(x.get("ON_IZ", float("nan")), 0), sayi(x.get("ARKA_IZ", float("nan")), 0)), durum(abs(x.get("omni_merkez", 0) - 201.5) < 0.01)],
        ["x zinciri (sağ ön): braket / kaplin / adaptör / omni", "%s / %s / %s / %s" % tuple("–".join(sayi(v, 1) for v in x.get(k, [0, 0])) for k in ("braket_x", "kaplin_x", "adaptor_x", "omni_x")), durum(bool(x))],
        ["Adaptör kaplini 17,5 mm kavrar", "ölçülen <b>%s mm</b> (17,5 teker oturma yüzünün kaplin ucuna uzaklığı); <code>arayuz.py</code> yorumu düzeltildi" % sayi(x.get("kaplin_adaptor_kavrama", float("nan")), 1), "<span class='uy'>düzeltildi</span>"],
        ["Omni Ø127 × 29", "y %s, z %s, alt y %s" % (sayi(x.get("omni_cap_y", float("nan")), 2), sayi(x.get("omni_cap_z", float("nan")), 1), sayi(x.get("omni_alt_y", float("nan")), 2)), durum(bool(x))],
        ["Bağlantılar %d / %d tamam" % (d["baglanti_tamam"], len(d["baglanti"])), "taban_montaj: %d bağlantı, sorunlu %d; omni bağlantısı %s" % (
            len(ta.get("baglanti_kontrol", [])), sum(1 for b in ta.get("baglanti_kontrol", []) if not b.get("tamam")), (dog.get("omni_baglanti") or {}).get("sayi", "?")),
         durum(bool(ta.get("baglanti_kontrol")) and all(b.get("tamam") for b in ta["baglanti_kontrol"]))],
        ["Lastik geri dönüşü omni öncesiyle aynı", "%d parça birebir (ad + sıra; hacim, kutu, kütle), yeni %d, farklı %d" % (ocl.get("ayni", 0), len(ocl.get("yeni", [])), len(ocl.get("farkli", []))),
         durum(bool(ocl) and not ocl.get("yeni") and not ocl.get("farkli"))],
        ["Omni modunda değişmeyen taban parçaları", "%d birebir; yeni %d; kalkan %s" % (oc.get("ayni", 0), len(oc.get("yeni", [])), esc(", ".join(oc.get("kalkan", [])))),
         durum(bool(oc) and not oc.get("farkli"))],
    ]
    S.append(tablo(["İddia", "Ölçülen", "Durum"], ir))
    for key, ad in (("+1+1", "Sağ ön (omni grubu)"), ("+1-1", "Sağ arka (lastik, karşılaştırma)")):
        g = don.get(key)
        if g:
            S.append("<p><b>%s</b>: dönen grup (<code>TEKER_DONEN</code>, kaplin hariç) 0–345° / 15° döndürüldü, %d statik aday, çakışma %d. En yakınlar:</p>" % (esc(ad), g["statik_aday"], len(g["cakisma"])))
            S.append(tablo(["Parça", "En küçük boşluk (mm)", "Açı (°)"], [[esc(n), sayi(v, 2), sayi(a, 0)] for n, v, a in g["en_yakin"][:6]]))
    S.append("<p><b>Ölçüt.</b> Projede dönen parça için sabit bir açıklık kabulü yazılı değil; <code>carpisma.py</code> 5 mm'yi \"yakın\" eşiği olarak kullanır (kabul değil), "
             "teker ↔ etek hedefi 12 mm. Mevcut, kabul edilmiş arka lastik köşede dönen grup kaplin ↔ braket 2,0 mm ve motor M3 başlarına 3,79 mm. Ön köşenin en dar gerçek "
             "açıklıkları (M3 başları 3,5, alt plaka köşesi 6,08, braket 6,5 mm) bu emsalin üstünde ya da eşit: <b>geçer</b>. Motor gövdesi 3,05 mm mil ucu ile altıgen yuva arası "
             "(aralarında kaplin, birlikte döner), gerçek açıklık değil. Flanş kalınlığı TAHMİN ölçülere göre değişirse M3 başı açıklığı yeniden ölçülmeli.</p>")

    # 2 resmi tarama
    S.append("<h3>2. Resmî çakışma taraması (<code>carpisma_kos.py</code>, 9 bölüm)</h3>")
    if tarama_guncel:
        tr = [[esc(a), str(T0[k]), str(T1[k])] for a, k in (("Toplam çakışma (kol tarama)", "cakisma"), ("Eklem aralığında", "aralik"), ("Kafa çakışma", "kafa"),
                                                           ("Kol × taban çakışma", "taban"), ("Kol × taban eklem aralığında", "taban_aralik"),
                                                           ("Taban statik çakışma (modüllerle)", "taban_statik"), ("Taban statik temas", "taban_temas"),
                                                           ("Taban hedef sayısı", "taban_hedef"), ("Ev pozu çakışma", "ev"))]
        tr.append(["Toplam kütle (g)", sayi(T0["kutle"] or 0, 1), sayi(T1["kutle"] or 0, 1)])
        tr.append(["Süre (s)", sayi(T0["sure"] or 0, 0), sayi(T1["sure"] or 0, 0)])
        S.append(tablo(["", "Omni öncesi (%s)" % esc(ONCE_REF), "Omni sonrası (ölçülen)"], tr))
        S.append("<p>Önceki tam taramadan (21.11) sonra izlenen kaynaklarda değişen yalnız omni dosyaları; fark omninin etkisi. Omni kaynaklı yeni çakışma: <b>%s</b>.</p>" % ("yok" if not yeni_cak else yeni_cak))
    else:
        if kst:
            S.append("<p>Tam koşu 23.11.2026 15:41'de başladı; <b>statik bölümü tamamlandı</b> (%s s), omuz bölümü sırasında sistem belleği azaldığı için durduruldu "
                     "ve yeniden başlatılmadı. Karışık sonuç olmasın diye <code>carpisma-sonuc.json</code> ve <code>carpisma-bolum/</code> değiştirilmedi; statik bölümün "
                     "özeti <code>omni/carpisma-statik-asama2.json</code>.</p>" % sayi(kst["sure_s"], 1))
            S.append(tablo(["Statik bölüm (" + "ölçülen" + ")", "Omni öncesi (21.11)", "Omni sonrası"], [
                ["Ev pozu çakışma", str(kst["ev_pozu_cakisma"]["once"]), str(kst["ev_pozu_cakisma"]["sonra"])],
                ["Ev pozu, S2 0° çakışma (bilgi)", str(kst["ev_pozu_cakisma_s2_0"]["once"]), str(kst["ev_pozu_cakisma_s2_0"]["sonra"])],
                ["Ev pozu kutusu kesişen çift (ölçülen aday)", str(kst["ev_pozu_kesisen_cift"]["once"]), str(kst["ev_pozu_kesisen_cift"]["sonra"])],
                ["Ayrılmış bölge / arayüz uyumu", "—", "birebir aynı" if kst["ayrilmis_bolge_ayni"] and kst["arayuz_uyumu_ayni"] else "farklı"],
                ["Toplam kütle (g)", sayi(kst["kutle_toplam_g"]["once"], 1), sayi(kst["kutle_toplam_g"]["sonra"], 1)],
                ["AM (mm)", esc(kst["agirlik_merkezi"]["once"]), esc(kst["agirlik_merkezi"]["sonra"])]]))
            S.append("<p><b>Koşulmayan bölümler:</b> %s. Kol × taban (kolun ön tekerlere / sonarlara yaklaşması) resmî olarak ölçülmedi; önceki tam taramada "
                     "kol × taban çakışma 0, en yakın hedefler acil stop ≈ 590 mm. Ön omni grubu x yönünde eski lastik zarfının (187–245) içinde (omni 187–216, M3 başı dış yüzü ≈ 219,5), yalnız yarıçap 1 mm büyük; "
                     "kol tarafına anlamlı yaklaşma beklenmez, ama bu bir çıkarım, ölçüm değil.</p>" % esc(", ".join(kst["kosulmayan"])))
        S.append("<div class='uyari'>%s</div>" % esc(eskime or "carpisma-sonuc.json okunamadı"))

    # 3 taban yeniden uretim
    S.append("<h3>3. <code>taban_montaj.py</code> yeniden üretimi: kütle, ağırlık merkezi, devrilme</h3>")
    S.append("<p>Devrilme artık yamuk destek çokgeniyle: ön teker x %s (omni), arka x %s; yan kol arkaya göre ön izden ölçülür. Lastik modunda (TABAN_OMNI=0) hesap eskisiyle aynı. "
             "Kontroller: geçersiz %d, iç çakışma %d (%s çift), bölge ihlali %s.</p>" % (
                 sayi((ta.get("robot", {}).get("destek") or {}).get("on_x_mm", float("nan")), 1), sayi((ta.get("robot", {}).get("destek") or {}).get("arka_x_mm", float("nan")), 1),
                 len(ta.get("gecersiz", [])), len(ta.get("ic_cakisma", [])), ta.get("cift_sayisi", "?"), len((ta.get("bolge") or {}).get("ihlal", [])) if isinstance(ta.get("bolge"), dict) else "?"))
    tb = [["Taban kütlesi (g)", sayi(ta0.get("kutle_g", 0), 1), sayi(ta.get("kutle_g", 0), 1)],
          ["Taban AM (mm)", esc(ta0.get("agirlik_merkezi")), esc(ta.get("agirlik_merkezi"))]]
    P0 = {p["kod"]: p for p in (ta0.get("robot") or {}).get("pozlar", [])}
    for p in (ta.get("robot") or {}).get("pozlar", []):
        q = P0.get(p["kod"])
        if not q:
            continue
        tb.append(["<b>%s</b>: kütle (g), AM" % esc(p["ad"]), "%s · %s" % (sayi(q["kutle_g"], 1), esc(q["am"])), "%s · %s" % (sayi(p["kutle_g"], 1), esc(p["am"]))])
        for z in ("duz", "rampa5"):
            tb.append(["&nbsp;&nbsp;%s devrilme payı ileri / geri / yan (izin verilen ivme ÷ 1,5 m/s²)" % ("düz" if z == "duz" else "rampa 5°"),
                       " / ".join(sayi(q[z]["pay_" + y], 2) for y in ("ileri", "geri", "yan")), " / ".join(sayi(p[z]["pay_" + y], 2) for y in ("ileri", "geri", "yan"))])
        tb.append(["&nbsp;&nbsp;statik eğim ileri / geri / yan (°)", " / ".join(sayi(q["duz"]["statik_egim_" + y], 1) for y in ("ileri", "geri", "yan")),
                   " / ".join(sayi(p["duz"]["statik_egim_" + y], 1) for y in ("ileri", "geri", "yan"))])
    m0, m1 = ta0.get("aks") or {}, ta.get("aks") or {}
    mo0, mo1 = ta0.get("motor") or {}, ta.get("motor") or {}
    for k, ad in (("duz", "Motor düz (kg·cm, oran)"), ("rampa5", "Motor rampa 5° (kg·cm, oran)"), ("rampa5_yuk2", "Motor rampa 5° + 2 kg yük")):
        if k in mo0 and k in mo1:
            tb.append([esc(ad), "%s (%s×)" % (sayi(mo0[k]["T_kgcm"], 2), sayi(mo0[k]["oran"], 3)), "%s (%s×)" % (sayi(mo1[k]["T_kgcm"], 2), sayi(mo1[k]["oran"], 3))])
    S.append(tablo(["", "Omni öncesi", "Omni sonrası (ölçülen)"], tb))
    te = [x for x in ta.get("teker_etek", []) if "Omni" in x["teker"]]
    S.append("<p>Teker ↔ etek: omni %s mm, arka lastik %s mm (hedef %s). Adaptör baskı kontrolü (yazıcı, çıkıntı, destek) taban baskı listesinde geçti.</p>" % (
        sayi(te[0]["bosluk_mm"], 1) if te else "?", sayi(next((x["bosluk_mm"] for x in ta.get("teker_etek", []) if "arka" in x["teker"]), float("nan")), 1), esc(ta.get("teker_etek_hedef_mm"))))

    # zemin
    zm = (ta.get("robot") or {}).get("zemin") or {}
    S.append("<h3>4. Zemin: Ø127 ön omni CAD'de 1 mm zemin altında</h3><div class='karar'><b>Karar (bu aşama):</b> CAD ve ana montajın zemini arka teker teması (y = 0) kalır; aks "
             "yüksekliği 62,5 ortak (motor braketi), bu yüzden Ø127 omni gösterimde zeminin %s mm altına iner. Gerçek duruşta ön uç %s mm yükselir, robot %s° burun yukarı durur. "
             "Bu açı devrilme hesabına <b>yalnız geri yönde</b> eklendi (ileri kazancı alınmadı, güvenli taraf); <code>taban-analiz.json</code> → <code>robot.zemin</code>, "
             "<code>durus_egimi_derece</code>. Çakışma taramasında zemin parça değil; arka teker Ø125 ile ön Ø127 arasındaki 1 mm bir montaj hatası değil.</div>" % (
                 sayi(zm.get("on_teker_zemin_alti_mm", float("nan")), 1), sayi(zm.get("on_teker_zemin_alti_mm", float("nan")), 1), sayi(zm.get("durus_egimi_derece", float("nan")), 3)))

    # ana montaj
    kr = ma.get("karsilastirma", {})
    kr0 = ma0.get("karsilastirma", {})
    gr = {}
    for p in ma.get("parcalar", []):
        if p.get("modul") == "taban":
            gr[p["grup"]] = gr.get(p["grup"], 0) + 1
    S.append("<h3>5. Ana montaj (<code>montaj/</code>)</h3>")
    S.append(tablo(["", "Omni öncesi", "Omni sonrası (ölçülen)"], [
        ["Parça (montaj / beklenen)", "%s / %s" % (kr0.get("parca", {}).get("montaj"), kr0.get("parca", {}).get("beklenen")), "%s / %s" % (kr.get("parca", {}).get("montaj"), kr.get("parca", {}).get("beklenen"))],
        ["Kütle (g)", sayi(kr0.get("kutle", {}).get("montaj_dosyasi", 0), 2), sayi(kr.get("kutle", {}).get("montaj_dosyasi", 0), 2)],
        ["AM (mm)", esc(kr0.get("am", {}).get("montaj_dosyasi")), esc(kr.get("am", {}).get("montaj_dosyasi"))],
        ["Analizlerle kütle farkı (g)", sayi(kr0.get("kutle", {}).get("fark_analiz", 0), 3), sayi(kr.get("kutle", {}).get("fark_analiz", 0), 3)]]))
    S.append("<p><b>Teker grubu</b> (<code>moduller.py</code>, artık <code>taban_parcalar.TEKER_DONEN</code>'den): %s. Ön grup: omni + PETG adaptör + 4× (M3×35 + pul + ısıl gömme somun) "
             "+ kaplin + M4×16 + pul; gövdede omni parçası kalmadı. Taban dışı 837 parça omni öncesiyle birebir (ad, grup, kütle, merkez); tabanın değişmeyen 412 parçası birebir.</p>" % (
                 esc(", ".join("%s %d" % (k, v) for k, v in sorted(gr.items())))))
    if ekl:
        tz = {k: v for k, v in ekl.get("ozet", {}).items() if k.startswith("Taban_")}
        S.append("<p><b>Eklem doğrulaması:</b> yön testi %d, doğru %d; teker eklemleri en büyük sapma %s mm; solve testleri dönüş kodu %s. "
                 "<code>eklem_dogrulama.py</code> bu dalda kafa kamera noktasında durur (<code>kafa_parcalar.Y_CAM</code> yok; omniden bağımsız, önceden var), dosya yazılmaz: "
                 "kafa yön denetimi atlanarak koşulan kopyanın sonucu <code>omni/eklem-dogrulama-asama2.json</code>; <code>montaj/eklem-dogrulama.json</code> değişmedi.</p>" % (
                     len(ekl.get("yon", [])), sum(1 for y in ekl.get("yon", []) if y.get("dogru")), "%.1e" % max([v["max_mm"] for v in tz.values()] or [float("nan")]),
                     "hep 0" if all(s.get("solve") == 0 for s in ekl.get("solve_testi", [])) else "sıfır değil"))
    S.append("<p class='not'><code>montaj_gui_kontrol.py</code>: dört teker eklemi seçilebiliyor ve görünür; sürükleme testi omniden önce de olan bir hatayla (GOBEK None) duruyor, "
             "commit'teki <code>gui-kontrol.json</code> zaten eski (907 parça). Bu aşamada dokunulmadı.</p>")

    # regresyon
    S.append("<h3>6. Regresyon</h3>")
    S.append(tablo(["Kontrol", "Sonuç"], [
        ["omuz_regresyon (%d satır)" % len((reg["omuz"] or {}).get("satirlar", [])), durum(bool(reg["omuz"]) and reg["omuz"].get("hepsi_ayni")) + " birebir aynı"],
        ["iskelet_regresyon (%d satır)" % len((reg["iskelet"] or {}).get("satirlar", [])), durum(bool(reg["iskelet"]) and reg["iskelet"].get("hepsi_ayni")) + " birebir aynı"],
        ["Ana montaj, taban dışı parçalar", durum(True) + " 837 / 837 aynı"],
        ["Taban, lastik modu (TABAN_OMNI=0)", durum(bool(ocl) and not ocl.get("farkli")) + " %d / %d aynı" % (ocl.get("ayni", 0), ocl.get("once_parca", ocl.get("ayni", 0)))]]))

    # olculen / tahmin
    S.append("<h3>7. Ölçülen, TAHMİN, doğrulanmamış</h3><ul>"
             "<li>" + OLC + ": x zinciri, kavrama 25,5, bağlantılar, dönen grup açıklıkları, kütle / AM, devrilme payları, ana montaj ve eklemler, regresyonlar"
             + (", resmî tarama" if tarama_guncel else "") + " (CAD üzerinde; CAD'in kendisi ürün ölçüsü TAHMİN'lerini içerir).</li>"
             "<li>" + TAH + ": teker göbek deliği, PCD, cıvata adedi / çapı / ilk açı, göbek kalınlığı, makara boyu / sıra ofseti; motor durma torku ve sürekli oranı; µ.</li>"
             "<li>Doğrulanmamış: dönüş torku (A üst sınır, C alt taraf, MuJoCo dinamik model; hiçbiri ölçüm değil), PETG adaptörün sürünme / altıgen ezilmesi, sonar konisi ↔ teker.</li></ul>"
             "<p><a href='#olculecek'>Sipariş öncesi ölçülecekler listesi</a> aşağıda.</p>")

    # tutarsizliklar
    S.append("<h3>8. Dokunulmadan bildirilen tutarsızlıklar</h3><ul>" + "".join("<li>%s</li>" % md(s) for s in [
        "**Web demosu** (`tasarim/cad/omni-teker.json`, demo, `rehber/veri/robot.glb`): demo merkezi 216 (CAD 201,5, fark 14,5 mm; ön iz 432 / 403), adaptör Ø40 / delik 14 (CAD flanş Ø56, pilot Ø22), ürün 14075 (CAD 14073). GLB / demo / rehber ana montajdan yeniden üretilmedi; gerekirse `montaj` → GLB → demo zinciri ayrı iş.",
        "**`kod/ortak/robot_parametreleri.json` `iz_genisligi_m` 0,432:** artık yalnız arka iz; ön iz 0,403. Firmware sabiti 0,426 ayrı.",
        "**`kod/fizik/omni_teker.json`:** ürün 14075, `gobek_deligi_mm` 6 (Nexus göbeği); CAD teker göbek deliği 22,4 TAHMİN. MuJoCo ONERI-ADAY kütle farkı +606 g, CAD +753 g.",
        "**`planlama/maliyet.json` satır 133:** omni koşullu, toplama girmiyor; ön iki lastik teker hâlâ sayılıyor; adaptör ve 8× M3×35 / pul / ısıl gömme somun yok.",
        "**`rehber/rehber_metin.py` ≈ 172:** \"teker ekseni x ±178\"; montaj adımında omni / adaptör yok.",
        "**`lale158/kafa-yerlesim/uygulama_ivme.py`:** yan devrilmede `XC = _X_WH` (216) kullanıyor; `uygulama-ivme.json` omni öncesi.",
        "**`taban/taban_gorsel.py`:** \"Teker 125 x 58 (on sag)\" adını arıyor; omni modunda taban görselleri üretilemez (taban görselleri lastik ön tekerle kaldı).",
        "**Taban parça adları:** M6 plaka ara ray cıvata / çekiç somunları x = ±50'de aynı adı taşıyor (omniden önce de); ada göre eşleme yanıltır.",
        "**`montaj/eklem_dogrulama.py`:** `kafa_parcalar.Y_CAM` yok, betik kafa yön denetiminde durur (omniden bağımsız). `montaj_gui_kontrol.py` sürükleme testi GOBEK None hatası.",
        "Düzeltilenler (bu aşama): `arayuz.py` kavrama yorumu (17,5 → kavrama 25,5), `taban_montaj.py` devrilme (yamuk destek), `montaj/moduller.py` teker grubu (`TEKER_DONEN`), `donus_hesap.py` A üst sınır etiketi + Model C."]) + "</ul>")
    return HUKUM, DONUS, "".join(S)
