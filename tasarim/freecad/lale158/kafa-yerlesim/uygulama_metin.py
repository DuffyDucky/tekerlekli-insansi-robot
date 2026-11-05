# -*- coding: utf-8 -*-
# uygulama_rapor.py icinde calisir (exec): metinler. Sayilar rapor betiginin okudugu JSON degiskenlerinden gelir, burada elle sayi yazilmaz (kabuk_montaj ve tani degerleri dahil).
TANI = oku(HERE, "uygulama-tani.json")
_k_b = [b for b in KABUK["baski"] if b["ad"] == "Ust arka servis kapagi"][0]
_t_25 = [q for q in TANI["kapak_katman"] if q["z"] == 2.5][0]
_ai = TANI["ai_kafa"]
_bos = OLC["hub"]["en_yakin"]


def _yak(ls, ad):
    return [q[1] for q in ls if q[0].startswith(ad)][0]


_ev_tamam = "Yeni çakışma yok" if (len(KAFA["statik"]) == 0 and not KABUK["cakisma"] and not KABUK["iskelet_cakisma"] and CRP["toplam"]["eklem_araliginda"] == 0 and KK[0] == 0 and not CRP["ev_pozu_cakisma"] and not KON["ekran_cakisma"]) else "Çakışma var, tabloya bakın"

OZET_MD = ("B + R1 modele işlendi, zincir omuz bölümü hariç koştu. %s: kafa içi 0, kabuk içi 0, kabuk × iskelet 0, ev pozu %d, eklem aralığındaki tarama %d (omuz bölümü eski kayıttan). "
           "Boy %s mm, %s parça, %s g (400 g kablo payı dahil). Kafa grubu %s g, tilt payı ±15 %s, pan payı %s, mikrofon-hoparlör en az %s mm, boyun yuva kanalı %%%s, SY8205 × USB %s mm³ ve açıklık %s mm. "
           "Yüksüz ızgara devrilme payı %s, ev pozu %s; eşik 1,5." % (
               _ev_tamam, len(CRP["ev_pozu_cakisma"]), CRP["toplam"]["eklem_araliginda"], tr(BOY, 1), tr(KON["parca"], 0), tr(IV["ev"]["kutle_g"], 1), tr(TT["kutle_g"], 1), tr(TT["pay_tilt15"], 2), tr(TP["pay_iki_hane"], 2),
               tr(MH["poz_min_mm"], 1), tr(GEC_K["doluluk"] * 100, 1), tr(SY_V, 2), tr(HUB_SY, 2), tr(IZG, 3), tr(EV_R, 2)))

KAYNAK_NOT = ("**Önceki** sütunu: `secenekler.md` (Bugün sütunu), `lale158/ikinci-kontrol.json`, `lale158/ikinci/ivme-qled.json`, 04.11 tarihli `lale158-kontrol.json` değerleri. 0,799 mm³ önceki ajanın 16:20 bildirimi; dosyası yok, düzeltme öncesi `kafa-analiz.json` üzerine yazıldı. "
              "**Beklenen** sütunu `secenekler.md` B değerleri ve iş tanımındaki eşikler; \"-\" olan satırda hedef yok, önceki değerle karşılaştır.")
UYARI = []
if ESIK_ALTI:
    UYARI.append("**Yüksüz devrilme payı eşiğin altında:** ızgara rampa 5° en kötü %s, eşik 1,5." % tr(IZG, 3))
UYARI.append("**AI HAT+ zarfı mevcut bir cıvata boss'una giriyor:** %s mm³ `%s`, %s mm³ somun, %s mm³ cıvata (x %s...%s, z %s...%s). Boss bu işte değişmedi, seçim ölçümleri bu çifti taramamıştı. Zarf varsayım; AI HAT+ modele eklenmedi." % (
    tr(_ai[0]["v"], 2), _ai[0]["ad"], tr(_ai[1]["v"], 2), tr(_ai[2]["v"], 2), tr(_ai[0]["bb_bas"][0], 1), tr(_ai[0]["bb_bas"][1], 1), tr(_ai[0]["bb_bas"][4], 2), tr(_ai[0]["bb_bas"][5], 2)))

DEGISEN = [
    "`arayuz.py`: yeni `SES_USB` (dizi, ses kartı, PAM, koridor, hoparlör, hub, Pi portları, kablo payı).",
    "`kafa/kafa10_lib.py`, `kafa/kafa_lib.py`, `kafa/kafa_parcalar.py`: üretici STEP'inden ReSpeaker, tavanda 4 Ø3 delik ve 3 boss, 3 M2 × 8 PT vida; MAX98357A ve kafa içi hub çıktı; ses kartı ve PAM sol duvarda. Önceki ajanın 0,799 mm³ boss düzeltmesi korundu ve doğrulandı.",
    "`kafa/kafa_montaj.py`: kablo ve fiş kütleleri tilt ve pan hesabına nokta kütle; ±15 payı raporlanıyor.",
    "`kabuk/kabuk_parcalar.py`: orta bant sağ duvara hoparlör (19 Ø3,5 delik, 2 boss), kap iki parça (ön halka + flanşlı arka), üst arka kapağa hub takozu + 2 yan dayama, köpük bant.",
    "`lale158/kablo_yolu_ekran.py`: B yolları, koridor, kapak söküm payı, kafa içi kablo kütlesi.",
    "`kafa-yerlesim/uygulama_olc.py` (bu turda: eşiksiz dizi kesişimi eklendi, AI HAT+ zarfı `yerlesim_lib` ile aynı yüksekliğe indirildi), `uygulama_gorsel.py` (bu turda: göğüs dokunmatik kablosu çizime eklendi), `uygulama_baski.py`, yeni `uygulama_ivme.py`, `uygulama_tani.py`, `uygulama_rapor.py`, `uygulama_metin.py`.",
    "Bu turda model kaynak dosyalarına dokunulmadı: gereksinimler kaynakta tek tek kontrol edildi, eksik çıkmadı.",
    "`secenekler.md` başına seçim satırı eklendi. Üretilen model dosyaları: kafa, kabuk, montaj, taban FCStd + STEP + BOM + analiz JSON.",
]

_h = OLC["hub"]
_hop = OLC["hop_Hoparlor 40 x 20"]
_kon = OLC["hop_Hoparlor kabi on halka"]
OLCUM = [
    "**Dizi:** PCB üstü y %s (hedef 92,62), bas çerçevesi kutusu x %s...%s, z %s...%s; kabuk ve kendi vidaları dışında en yakın parça yüz kabuğu, %s mm; arka kabuk tek katı, geçerli. Eşiksiz dizi × kabuk kesişimi %s mm³: 0,5 mm³ eşiğinin altında, temas büyüklüğünde; konumu ayrıca ölçülmedi." % (
        tr(OLC["dizi"]["bb_bas"][3] - 5.4, 2), tr(OLC["dizi"]["bb_bas"][0], 2), tr(OLC["dizi"]["bb_bas"][1], 2), tr(OLC["dizi"]["bb_bas"][4], 2), tr(OLC["dizi"]["bb_bas"][5], 2), tr(_yak(OLC["dizi"]["en_yakin"], "Yuz kabugu"), 2), tr(OLC["dizi"]["kabuk_kesisim_mm3"], 4)),
    "**Ses kartı:** y %s...%s, z %s...%s; kabuğa %s mm, PAM'e %s mm. **PAM8403:** y %s...%s, z %s...%s; kabuğa %s mm." % (
        tr(OLC["USB ses karti"]["bb_bas"][2], 1), tr(OLC["USB ses karti"]["bb_bas"][3], 1), tr(OLC["USB ses karti"]["bb_bas"][4], 1), tr(OLC["USB ses karti"]["bb_bas"][5], 1), tr(_yak(OLC["USB ses karti"]["en_yakin"], "Arka kafa"), 2), tr(_yak(OLC["USB ses karti"]["en_yakin"], "PAM"), 2),
        tr(OLC["PAM8403 amfi"]["bb_bas"][2], 1), tr(OLC["PAM8403 amfi"]["bb_bas"][3], 1), tr(OLC["PAM8403 amfi"]["bb_bas"][4], 1), tr(OLC["PAM8403 amfi"]["bb_bas"][5], 1), tr(_yak(OLC["PAM8403 amfi"]["en_yakin"], "Arka kafa"), 2)),
    "**MAX98357A:** modelde %d parça, `kafa-bom.csv`'de yok." % len(OLC["model_adlar"]["max98357a"]),
    "**Hub:** x %s...%s, y %s...%s, z %s...%s (global). Kapak dayamasına %s mm, göğüs bandına %s mm, kapak somununa %s mm. 40 mm fiş payı: gövde braketine %s mm, direğe %s mm, çakışma %d. 2 port boş." % (
        tr(_h["bb_g"][0], 1), tr(_h["bb_g"][1], 1), tr(_h["bb_g"][2], 1), tr(_h["bb_g"][3], 1), tr(_h["bb_g"][4], 2), tr(_h["bb_g"][5], 2), tr(_yak(_h["en_yakin"], "Ust arka"), 2), tr(_yak(_h["en_yakin"], "Gogus bandi"), 2), tr(_yak(_h["en_yakin"], "Isil gomme"), 2),
        tr(_yak(_h["fis_payi_en_yakin"], "Govde braketi"), 2), tr(_yak(_h["fis_payi_en_yakin"], "Govde diregi"), 2), len(_h["fis_payi_cakisma"])),
    "**Hoparlör:** duvar merkezi (%s; %s; %s), eksen yatayın %s° altında, kama yok. Duvara %s mm; ön halka duvara %s mm, göğüs bandına %s mm." % (
        tr(OLC["hoparlor_duvar"]["C"][0], 1), tr(OLC["hoparlor_duvar"]["C"][1], 1), tr(OLC["hoparlor_duvar"]["C"][2], 2), tr(OLC["hoparlor_duvar"]["yatay_alti_derece"], 1), tr(_yak(_hop["en_yakin"], "Govde orta"), 3), tr(_yak(_kon["en_yakin"], "Govde orta"), 3), tr(_yak(_kon["en_yakin"], "Gogus bandi"), 3)),
    "**USB koridoru:** tablaya %s mm, Pi'ye %s mm. Hub kablosu boyundan iniyor, göğüs dokunmatiği ve ESP32 kablosu kafaya girmiyor." % (tr(_yak(OLC["koridor_en_yakin"], "Kafa iskeleti"), 2), tr(_yak(OLC["koridor_en_yakin"], "Raspberry"), 2)),
    "**Dizi USB'sinin güç kablolarına uzaklığı:** SY8205 %s, D24V50F5 %s, TVS %s, PAM 5 V %s, hoparlör kablosu %s mm." % tuple(tr(OLC["dizi_usb_guc_mm"][k], 2) for k in ("SY8205", "D24V50F5", "TVS", "PAM 5 V", "Hoparlor kablosu")),
    "**Kablo tüpü × parça (`lale158-kontrol.json`):** Hub uzatması Pi %s, mil %s; dizi USB Pi %s; ses kartı uzatması Pi %s; 3,5 mm PAM %s mm³. Port ucu ve mil temasları şema kaynaklı, HDMI ve 12 V satırları önceki koşuyla aynı. SY8205 listede yok." % (
        tr(dict(K_YENI["Hub uzatmasi"])["Raspberry Pi 5 4GB + Active Cooler"], 1), tr(dict(K_YENI["Hub uzatmasi"])["Boyun mili"], 1), tr(dict(K_YENI["Dizi USB"])["Raspberry Pi 5 4GB + Active Cooler"], 1), tr(dict(K_YENI["Ses karti uzatmasi"])["Raspberry Pi 5 4GB + Active Cooler"], 1), tr(dict(K_YENI["3,5 mm -> PAM"])["PAM8403 amfi"], 1)),
    "**Devrilme, ızgara, rampa 5° (a_sınır, pay 1,5):** yüksüz %s; elde 100 g %s (önceki 1,482); elde 500 g %s (önceki 1,331). Elde yük bu işin dışında, eşik altı değerler önceki modelde de vardı. Düz zeminde 1,8 m/s² fren payı yüksüz %s (önceki 1,751). Ev pozu kütle %s g, AM y %s (önceki 25.836,9; 524,01)." % (tr(IZG, 3), tr(rampa_en(Y100), 3), tr(rampa_en(Y500), 3), tr(Y0["fren_pay"]["duz_min"], 3), tr(IV["ev"]["kutle_g"], 1), tr(IV["ev"]["am"][1], 2)),
    "**AI HAT+ yeri:** CAD'de yok, eklenmedi. Dizi ile zarf arası %s mm (seçimde 24,97). Zarf, yeni parçalardan hiçbirine girmiyor; yalnız mevcut arka üst cıvata boss'una giriyor (üstteki uyarı)." % tr(AH["dizi_mm"], 2),
]

_bk = BK["Ust arka servis kapagi"]
_on, _ar, _ob = BK["Hoparlor kabi on halka"], BK["Hoparlor kabi arka (flansli)"], BK["Govde orta bandi sag"]
BASKI_MD = ("`KL.baski_analiz` (`uygulama-baski.json`): üst arka kapak hub takozuyla %d destek sorunu, %s × %s × %s mm, %s g, %s sa. Hoparlör kabı ikiye bölününce sorun kalktı: ön halka %d, flanşlı arka %d destek sorunu (%s + %s g, varsayım kap). Orta bant sağ %d destek sorunu, ofset uyarısı %d, %s g. "
            "**Farklı sonuç:** `kabuk_montaj.py`'nin kendi analizi kapak için z %s'te %s mm² ile %d sorun yazıyor (`kabuk-analiz.json`). Katman katman tanı (`uygulama-tani.json`) bu katmanın bir alttaki katmana ofsetsiz taşmasını %s mm² buldu, ofsetli açık alan yok; bu yüzden hesap artığı olarak değerlendirdim. Analiz kodunu değiştirmedim, deneme baskısı kesin söyler." % (
                _bk["destek_sorun_sayi"], tr(_bk["olcu"][0], 1), tr(_bk["olcu"][1], 1), tr(_bk["olcu"][2], 1), tr(_bk["kutle_g"], 1), tr(_bk["sure_saat"], 2), _on["destek_sorun_sayi"], _ar["destek_sorun_sayi"], tr(_on["kutle_g"], 1), tr(_ar["kutle_g"], 1), _ob["destek_sorun_sayi"], _ob["ofset_uyari"], tr(_ob["kutle_g"], 1),
                tr(_k_b["destek_sorun"][0]["z"], 1) if _k_b["destek_sorun"] else "-", tr(_k_b["destek_sorun"][0]["alan"], 1) if _k_b["destek_sorun"] else "-", _k_b["destek_sorun_sayi"], tr(_t_25["ofsetsiz_tasma_mm2"], 2)))

KOSU = [
    ("`kafa/kafa_montaj.py`", "`kafa/kafa-analiz.json`, `kafa-bom.csv`, `kafa-montaj.FCStd`, `.step`, `kafa-zarf.brep`"),
    ("`kabuk/kabuk_montaj.py`", "`kabuk/kabuk-analiz.json`, `kabuk-bom.csv`, `kabuk-montaj.FCStd`, `.step`"),
    ("`montaj/ana_montaj.py` (iki kez; ikincisi çarpışmadan sonra)", "`montaj/montaj-analiz.json`, `robot-bom.csv`, `robot-montaj.FCStd`, `.step`"),
    ("`lale158/lale158_kontrol.py` (kablo yolu dahil)", "`lale158/lale158-kontrol.json`"),
    ("`kafa-yerlesim/uygulama_olc.py`", "`kafa-yerlesim/uygulama-olcum.json`"),
    ("`kafa-yerlesim/uygulama_baski.py`", "`kafa-yerlesim/uygulama-baski.json`"),
    ("`kafa-yerlesim/uygulama_tani.py` (betiğin scratchpad kopyasıyla koştu)", "`kafa-yerlesim/uygulama-tani.json`"),
    ("`carpisma_kos.py statik kol_sag kol_sol kolkol kafa_sabit kafa_sag kafa_sol taban` (koşu %s)" % CRP["bolumler"]["taban"]["kosu"], "`carpisma-bolum/*.json` (omuz hariç), `carpisma-sonuc.json`"),
    ("`taban/taban_montaj.py`", "`taban/taban-analiz.json`, `taban-bom.csv`, `taban-montaj.FCStd`, `.step`"),
    ("`lale158/ikinci_kontrol.py`, `IK_CIKTI` ile: model, tilt, kafa, catal, kol", "`kafa-yerlesim/uygulama-ikinci.json` (`ikinci-kontrol.json` önceki kayıt olarak duruyor)"),
    ("`kafa-yerlesim/uygulama_ivme.py` (`planlama/y2/Y2b-ivme.py` kopyası, yalnız yol farklı)", "`kafa-yerlesim/uygulama-ivme.json`"),
    ("`kafa-yerlesim/uygulama_gorsel.py`", "`kafa-yerlesim/gorsel/SON-*.png`"),
    ("`kafa-yerlesim/uygulama_rapor.py`", "`uygulama-notu.md`, `rapor.html`"),
]

_om = CRP["bolumler"]["omuz"]
ATLANAN = [
    "**`carpisma_kos` omuz bölümü ve omuz regresyonu koşmadı** (karar Ahmet Yorulmaz'da, ~4,8 saat). `carpisma-sonuc.json` omuz sonucu koşu %s'ten, yeni kabuktan önce; dosyada `tek_kosu` %s. Kol × kabuk ince ızgarası `uygulama-ikinci.json` içinde yeni modelle koştu." % (_om["kosu"], "false" if not CRP["tek_kosu"] else "true"),
    "`kafa_gorsel`, `kabuk_gorsel`, `montaj_gorsel`, modül `*_rapor.py` betikleri ve `yerlesim_kontrol.py` koşmadı: `kabuk/gorsel/*.png` ve `montaj/yerlesim-kontrol.json` değişmedi, modül `rapor.html` dosyaları eski. `montaj_gorsel` koşmadığı için `robot-montaj.FCStd` içinde eklem görünüm nesneleri yok.",
    "`lale158-regresyon.json`, `2209b-cad-sonuclar.json`, `lale158/rapor.html`, `ikinci-kontrol.json`, `ikinci/ivme-qled.json` yeniden üretilmedi: önceki değerleri taşıyor. Y2b-baskı listesi ve `planlama/baski-listesi.md` güncellenmedi (yazma sınırı).",
    "Hava akışı, ısı ve akustik yeniden hesaplanmadı; kablo bükümü modellenmedi.",
]

ELEKTRIK = [
    "**Çelişki yok, doğrulama da yok.** `elektrik.md` satır 21 PAM8403 besleme noktası ve akımı için \"doğrulanmadı\" diyor; satır 39 D24V50F5'i \"Pi + diğer kafa yükleri\" diye tanımlıyor; satır 315 amfiyi kafa yüküne sayıyor. Bu yüzden PAM 5 V D24V50F5'ten modellendi, **varsayım olarak işaretli**, elektrik planı değişmedi. Satır 301'deki \"USB ses kartı ── PAM8403\" sinyal yolu olarak okundu.",
    "**Akım bütçesi (hesap, ölçüm değil):** Pi hattı %s A (5 A'nın %%%s'i, satır 24). 3 W hoparlör, verim %%%s varsayımıyla PAM tepesi %s A. Satır 364'teki normal amfi 0,5 W bütçeye girmişse tepede %s A (%%%s), girmemişse %s A (%%%s). 2,67 A'nın kalem dökümü dosyada yok, hangisi olduğunu söyleyemem. Normal kullanımda 2,67 A aynı kalır; Pi tam yük tepesi bu hesapta yok, satır 22 de tepeyi \"hesaplanmadı\" diyor." % (
        tr(PI_HAT, 2), tr(PI_HAT / 5 * 100, 0), tr(VERIM * 100, 0), tr(PAM_TEPE, 2), tr(B_DAHIL, 2), tr(B_DAHIL / 5 * 100, 0), tr(B_HARIC, 2), tr(B_HARIC / 5 * 100, 0)),
    "**`elektrik.md` şimdi modelin gerisinde (salt okunur, değiştirmedim):** satır 12, 30, 58, 242, 272, 301, 481 hâlâ hub'ın kafa içi yerini açık, boyunda ESP32 USB + göğüs dokunmatik yazıyor. Modelde boyun demeti 12 V + tilt + HDMI + hub uzatması + hoparlör.",
    "Hub USB'den besleniyor, yeni yol ~1,1 m. Göğüs dokunmatiği ve ESP32 tek hub kablosuna bağlı; hub girişindeki gerilim ölçülmedi.",
]

LISTE_DISI = "USB-A uzatma ~30 cm (Pi → ses kartı), USB-A uzatma ~1 m (Pi → hub), L USB-A dirsek, kısa micro USB (dizi), hoparlör kablosu ~1,1 m, L 3,5 mm fişli kısa kablo."

VARSAYIM = [
    "ReSpeaker kütlesi 30 g, mikrofon deliği Ø3, M2 × 8 PT vida; LED dışarıdan görünmeyebilir, ışık borusu yok. Dizi geometrisi üretici STEP'i.",
    "Ses kartı 48 × 24 × 11, USB-A fişi, L dirsek, uzatma dişi ucu, L 3,5 mm fiş zarfları ve kütleleri. Ürün seçilmedi.",
    "PAM8403 modeli 24 × 18 × 5 (sayfa 21 × 18 × 3,4), 3 g; **5 V besleme noktası varsayım**.",
    "Hoparlör kütlesi 27 g başka üründen. **Kap varsayım:** ürün elde görülmedi, arka tüp açık çizimde, hoparlörü arkadan tutan yüzey ve kelepçe modelde yok.",
    "Hub 72 × 25 × 19, 25 g, port yönü varsayım. Bağlantı köpük bant + 2 yan dayama; ayrı tutucu yok. Kablolara kapak söküm payı 150 mm tahmin. Fiş payı 40 mm tahmin.",
    "Kablo yolları şema, çap ve g/m tahmin. Pi USB ağzı konumu ±2 mm varsayım. Kablo kütlesi 59 g payının üstüne eklendi, biraz kötümser.",
    "AI HAT+ 65 × 56,5, yığın 16 mm, 30 g: CAD'de yok. Altıncı USB cihazı bilinmiyor; hub'daki 2 port boş.",
]

KARAR = [
    "**Omuz bölümü ve omuz regresyonu** (~4,8 saat) koşulsun mu? Yeni parçalar omuza yakın değil, ama sonuç dosyası bu haliyle karışık.",
    "**AI HAT+ zarfı × arka üst cıvata boss'u:** HAT gelince gerçekse boss mu taşınır, HAT yönü mü değişir? Zarf ölçüsü doğrulanmadı.",
    "**Listede olmayan 6 kablo kalemi** v4'e eklensin mi? Liste bu işte değişmedi.",
    "**Altıncı USB cihazı:** kafadaysa B zayıflar (`secenekler.md`).",
    "**PAM 5 V:** D24V50F5 onaylanırsa `elektrik.md` güncellenmeli; akım ölçülmeli.",
    "**`elektrik.md` boyun ve hub satırları** ile baskı listesi yeni düzene göre güncellensin mi? Kapak hub takozlu, 2 yeni kap parçası var.",
    "**Efe teyidi:** boyun demeti değişti; önceki teyit maddesi HDMI + göğüs dokunmatikti.",
    "Ölçülmesi gerekenler (`secenekler.md` §7) açık: Ø3 deliklerin akustiği, hoparlör-mikrofon yankısı, servo gürültüsü, hub girişi gerilimi.",
]
