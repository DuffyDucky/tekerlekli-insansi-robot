# Lale 1,58 m - ikinci ajan ozeti (sistem Python'u, FreeCAD acmaz). Olcumler kendi kosulardan okunur:
# carpisma-sonuc.json, ikinci/ivme-qled.json, taban-analiz.json, kafa/kabuk-analiz.json, ikinci-kontrol.json, ikinci/baski-qled.json, ikinci/regresyon, ikinci/yavaslik.
# Cikti lale158-regresyon.json; lale158_rapor.py bunu rapor.html'e isler.
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
KOK = os.path.dirname(os.path.dirname(UST))


def oku(*y):
    return json.load(open(os.path.join(*y), encoding="utf-8"))


def t(x, n=2):
    return ("%.*f" % (n, x)).replace(".", ",")


C = oku(UST, "carpisma-sonuc.json")
Y = oku(HERE, "ikinci", "ivme-qled.json")     # planlama/y2/Y2b-ivme.py kopyasi, son modelde (planlama yenilenmedi)
TB = oku(UST, "taban", "taban-analiz.json")
KF = oku(UST, "kafa", "kafa-analiz.json")
KB = oku(UST, "kabuk", "kabuk-analiz.json")
BK = oku(HERE, "ikinci", "baski-qled.json")   # planlama/y2/Y2b-baski.py kopyasi, son analizlerden
IK = oku(HERE, "ikinci-kontrol.json")
MD = IK["model"]
GE = MD["ekran"]
BOY = MD["boy"]
ev = Y["ev"]
TT = KF["tork"]["tilt"]
KS, KL = C["kol_tarama"]["sag"], C["kol_tarama"]["sol"]
KFK = C["kafa_tarama"]["kol"]
g0, g1, g5 = Y["izgara_yuk_0g"], Y["izgara_yuk_100g"], Y["izgara_yuk_500g"]
P = {p["kod"]: p for p in TB["robot"]["pozlar"]}
ct = IK["catal"]["sonuc"]["sag"]["s2"]
ks = IK["kol"]["sonuc"]["sag"]["s2_en_kucuk"]
kf_min = min(IK["kafa"]["sonuc"]["sag"]["en_kucuk_20"], key=lambda r: r[0])
BOL = C["bolumler"]


def catal(s2, h):
    v = [r[0] for r in ct.get(s2, []) if h in r[2]]
    return min(v) if v else None


def t2(x):
    return "-" if x is None else t(x)


def reg(ad):
    a = oku(HERE, "ikinci", "regresyon", ad + "-once-head.json")
    b = oku(HERE, "ikinci", "regresyon", ad + "-sonra.json")
    # ayni adli parcalar var (omuz 75 parca, 38 ad): sira ile karsilastir
    A, B = a["parcalar"], b["parcalar"]
    fark = [y["ad"] for x, y in zip(A, B) if x != y] + [x["ad"] for x in A[len(B):]] + [y["ad"] for y in B[len(A):]]
    diger = sorted(k for k in a if k != "parcalar" and a[k] != b.get(k))
    return dict(n=len(B), fark=fark, diger=diger, A=A, B=B)


RO, RI = reg("omuz"), reg("iskelet")
dA = next(v for v in RI["A"] if v["ad"].startswith("Govde diregi"))
dB = next(v for v in RI["B"] if v["ad"].startswith("Govde diregi"))

maddeler = [
    dict(madde="1. Toplam boy (tüm parçalarda optimalBoundingBox)",
         olcum="zemin %s, tepe %s (%s), boy %s mm. BoundBox şişkin olurdu: %s / %s."
         % (t(BOY["zemin_y"], 1), t(BOY["tepe_y"], 1), BOY["tepe_parca"], t(BOY["boy_mm"], 1), t(BOY["boundbox_zemin"]), t(BOY["boundbox_tepe"])),
         olcut="zemin 0, tepe 1.580,0", sonuc="GEÇTİ"),
    dict(madde="2. Kol taraması",
         olcum="Tarama: eklem aralığında %d çakışma (sağ %d, sol %d tam poz); aralık dışı %d'er tam poz. Kol × kol %d. Kendi ince ızgaram: sağ %d, sol %d çakışma, hepsi S2 0-3; S2=5 en küçük %s mm (%s ↔ %s). Çatal ↔ göğüs bandı S2=5: %s mm, ↔ M5 cıvata %s mm."
         % (C["toplam"]["eklem_araliginda"], KS["cakisan_tam_poz_aralikta"], KL["cakisan_tam_poz_aralikta"], KS["cakisan_tam_poz_aralik_disi"], C["kol_kol"]["cakisan"],
            IK["kol"]["sonuc"]["sag"]["cakisma_sayisi"], IK["kol"]["sonuc"]["sol"]["cakisma_sayisi"], t(ks["5.0"]["min_mm"], 3), ks["5.0"]["hareketli"], ks["5.0"]["hedef"], t2(catal("5.0", "Gogus bandi")), t2(catal("5.0", "Civata M5x18"))),
         olcut="eklem aralığında 0 (yazılım S2 ≥ 5)", sonuc="GEÇTİ (sınır yazılımda, mekanik değil)"),
    dict(madde="3. Kafa × kol",
         olcum="Tarama: %d kol × %d kafa pozu, %d aday, %d tam ölçüm (sol %d), aralıkta 0. Tilt ±13 ve ±15 kendi ızgaram: sağ %d, sol %d ölçüm, çakışma 0, en küçük %s mm (%s ↔ %s)."
         % (KFK["sag"]["kol_pozu"], KFK["sag"]["kafa_pozu"], KFK["sag"]["aday"], KFK["sag"]["tam_olcum"], KFK["sol"]["tam_olcum"], IK["kafa"]["sonuc"]["sag"]["olcum"], IK["kafa"]["sonuc"]["sol"]["olcum"], t(kf_min[0], 3), kf_min[2], kf_min[3]),
         olcut="eklem aralığında 0", sonuc="GEÇTİ"),
    dict(madde="4. Devrilme (kafa ekranı 600 g varsayım, göğüs ekranı 1,079 kg)",
         olcum="Kütle %s g (kablo payı 400 g dahil), AM y %s. Ev pozu rampa 5° geri a_dev %s, pay %s. En kötü yüksüz kol pozu %s. Fren 1,8 düz: yüksüz %s, 100 g %s, 500 g %s."
         % (t(ev["kutle_g"], 1), t(ev["am"][1], 2), t(ev["rampa5"]["geri"], 3), t(ev["rampa5"]["geri"] / 1.5, 3), t(g0["a_sinir_pay15"]["rampa5_geri"], 3), t(g0["fren_pay"]["duz_min"], 3), t(g1["fren_pay"]["duz_min"], 3), t(g5["fren_pay"]["duz_min"], 3)),
         olcut="pay ≥ 1,5", sonuc="GEÇTİ yüksüz, elde yükte KALIYOR (aşağıya bak)"),
    dict(madde="5. Tilt",
         olcum="Pay %s (toplam %s kg·cm, stall %s), statik %s, AM %s mm; parçalardan kendi momentim %s kg·cm, %s mm. Serbest ±15 çakışmasız; ilk çakışma -17° ve +18°."
         % (t(TT["pay"], 1), t(TT["toplam_kgcm"]), t(TT["stall_kgcm"], 1), t(TT["yercekimi_max_kgcm"]), t(TT["am_eksen_mm"], 1), t(IK["tilt"]["moment"]["statik_kgcm"], 3), t(IK["tilt"]["moment"]["am_eksen_mm"])),
         olcut="pay için belgede sayısal ölçüt yok; serbest ±15, yazılım ±13", sonuc="GEÇTİ (pay > 1; ölçüt sayısı yok)"),
    dict(madde="6. Regresyon",
         olcum="03:03 koşusu: omuz %d parça, %d fark; iskelet %d parça, %d parça farklı, beklenen 70 mm (direk %s → %s g). QLED ve çerçeve düzenlemesinden sonra yeniden koşulmadı."
         % (RO["n"], len(RO["fark"]), RI["n"], len(RI["fark"]), t(dA["kutle"]), t(dB["kutle"])),
         olcut="omuz değişmez; iskelette yalnız 70 mm kısalma", sonuc="SON DOSYADA KOŞULMADI"),
    dict(madde="7. Göğüs ekranı",
         olcum="kabuk_montaj: kabuk içi %d, kabuk × iskelet %d, geçersiz %d. Tam model: ekran çakışması %d (%d çift), kasa ↔ direk %s mm, kasa ↔ göğüs bandı %s mm. Çerçeve payı %s mm, cam %s mm geride, aktif alana giren parça %d, takoz kalınlığı %s mm. Takoz ve köşe flanşı boss'lara %d çakışma (hacim ≤ 0,5 mm³ eşiği)."
         % (len(KB["cakisma"]), len(KB["iskelet_cakisma"]), len(KB["gecersiz"]), len(GE["cakisma"]), GE["cift_kontrol"], t(GE["kasa_direk_mm"]), t(GE["kasa_bant"]["Gogus bandi sag"], 1),
            t(KB["gogus_ekrani"]["cerceve_on"]["aktif_cerceve_pay_mm"], 3), t(KB["gogus_ekrani"]["cerceve_on"]["cam_geri"], 1), len(KB["gogus_ekrani"]["cerceve_on"]["aktif_alana_giren_parca"]), t(KB["gogus_ekrani"]["cerceve_on"]["takoz_kalinlik_mm"], 1), len(KB["cakisma"])),
         olcut="≥ 20; çakışma 0; bölge ihlali 0", sonuc="GEÇTİ"),
    dict(madde="8. Baskı",
         olcum="%d adet, filament %s–%s g, süre %s–%s sa (Y2b betiğinin kopyası; planlama yenilenmedi). Sığmayan %d; en büyük Göğüs bandı 217,2 × 164 × 235. Çerçeve 207,2 × 147 × 10 (31 g), taşıyıcı 106,2 × 100 × 63,4 (113 g, destekli)."
         % (BK["toplam"]["adet"], t(BK["toplam"]["g"][0], 0), t(BK["toplam"]["g"][1], 0), t(BK["toplam"]["sa"][0], 1), t(BK["toplam"]["sa"][1], 1), len(MD["baski"]["sigmayan_model_durusu"])),
         olcut="246 × 246 × 250", sonuc="GEÇTİ"),
]

bolumler = [
    dict(baslik="Durum",
         metin="1–5, 7 ve 8 son modelde ölçüldü. Açık kalanlar aşağıda: tarama omuz bölümü ve iskelet/omuz regresyonu QLED sonrası yeniden koşulmadı."),
    dict(baslik="Sıra ve koşu notları", liste=[
        "taban_montaj ile ana_montaj birbirini okuyor. Doğru sıra: taban → ana → taban. ana_montaj carpisma-sonuc.json da okuduğu için taramadan sonra yeniden koşuldu; karşılaştırma farkı 369 g → 0,035 g, AM 13,76 → 0,007 mm.",
        "kabuk_montaj 4.250,8 s; 16 satır Wire is not closed 3 Kasım logundakiyle aynı sayıda. Parçaları yükleyen taban ve ana montaj loglarında 0; kaynak baskı analizi (ofset), çerçeve kodu değil. Gövde bandı desteksizlik sonucu bu yüzden temkinli okunmalı.",
        "Tarama bölümleri bu kez tek tek, paralel değil: statik, kol, kol-kol, kafa, taban. Eklem aralığında toplam %d çakışma." % C["toplam"]["eklem_araliginda"],
    ]),
    dict(baslik="Çatal ve kol boşlukları, S2'ye göre (kendi ince ızgaram)",
         metin="S2=0'daki 3,8 mm artık geçerli değil: o 165 cm'nin değeri (3,76). 158 cm'de çatal ↔ bant 2,0 mm ve çatal M5 cıvataya 20,53 mm³ giriyor. S2 ≥ 5 yazılım sınırı bu yüzden zorunlu. Aralıkta en dar boşluk ekranla ilgili değil: üst kol tüpü ↔ S1 kaset kapağı 1,36 mm.",
         sutun=("S2", "Çatal ↔ göğüs bandı mm", "Çatal ↔ M5 cıvata mm", "Tüm kol en küçük mm", "Çift", "Aralıkta mı"),
         satir=[(s.split(".")[0], t2(catal(s, "Gogus bandi")), t2(catal(s, "Civata M5x18")), t(ks[s]["min_mm"]), "%s ↔ %s" % (ks[s]["hareketli"], ks[s]["hedef"]), "evet" if float(s) >= 5 else "hayır") for s in ("0.0", "1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "8.0") if s in ks]),
    dict(baslik="Devrilme, poz bazında (son taban-analiz; kablo payı 400 g dahil)",
         sutun=("Poz", "Kütle g", "AM y", "Rampa 5° pay ileri", "Rampa 5° pay geri", "Pay yan"),
         satir=[(p["ad"], t(p["kutle_g"], 1), t(p["am"][1], 1), t(p["rampa5"]["pay_ileri"]), t(p["rampa5"]["pay_geri"]), t(p["rampa5"]["pay_yan"])) for p in TB["robot"]["pozlar"]]),
    dict(baslik="Devrilmede dikkat", liste=[
        "Elde yük varken rampa ölçütü tutmuyor: iki kol önde + elde 0,5 kg pay ileri %s; 500 g ızgara en kötü %s (önceki 7\" modelde 1,362); 100 g ızgara en kötü %s, bu da eşik altına indi (önceki modelde 1,521). Yüksüz en kötü %s, eşiğe 0,02 kala geçiyor. Elde yük sınırı Duffy'nin kararı."
        % (t(P["one_yuk"]["rampa5"]["pay_ileri"]), t(g5["a_sinir_pay15"]["rampa5_geri"], 3), t(g1["a_sinir_pay15"]["rampa5_geri"], 3), t(g0["a_sinir_pay15"]["rampa5_geri"], 3)),
        "400 g kablo payına yeni göğüs kabloları (HDMI, USB, 12 V) eklenmedi. Formül elle de doğrulandı (ev pozu rampa geri kendi hesabım 2,492).",
        "Rampa payı 1,5 m/s² frene göre; fren 1,8 ölçümü yalnız düz zemin için.",
    ]),
    dict(baslik="Yavaşlık: kabuk_montaj neden 3 saat",
         metin="Darboğaz çakışma değil, katman katman baskı kontrolündeki makeOffset2D. Profil (kendi koşum): toplam 8.293,9 s, makeOffset2D 5.622 çağrı 6.934,7 s (%84, çağrı başına 1,233 s). HEAD aynı işlem: 1.401,9 s, 5.147 çağrı 205,6 s (0,040 s). Çağrı sayısı neredeyse aynı, çağrı başına süre 31 kat.",
         sutun=("Parça", "Çağrı", "≥ 10 s süren", "Bunların süresi", "Toplam süre", "Sonuç"),
         satir=[("Göğüs bandı sağ", "406", "16", "1.638,7 s", "1.691 s", "hepsi hatayla bitiyor"), ("Omuz bandı sağ", "280", "14", "951,6 s", "974 s", "hepsi hatayla bitiyor")]),
    dict(baslik="Yavaşlık, ölçülen ve ölçülmeyen", liste=[
        "Altı bant (göğüs, orta, omuz) 8.192 s'nin 7.176 s'si. Göğüs sağ 3.255, sol 1.698, orta 548/472, omuz 575/627 s.",
        "Her yavaş çağrı 14–277 s OCC içinde dönüp istisna atıyor; kod sonra ofsetsiz yüze düşüyor. Sonuç muhafazakâr, yanlış değil, yalnız pahalı.",
        "Ofset değeri neden değil: aynı yüzler 0,5–1,2 mm arası her değerde 60–240 s sonra başarısız. '1,0 mm iç yarıçap = 1,0 mm ofset' varsayımım bu ölçümle çürüdü.",
        "Korelasyon, kanıt değil: GOGUS_R 16 → 4, 3 mm et düşünce iç yarıçap 1 mm; dört örnek katmanın üçünde en küçük yarıçap 1,0, dördüncüde 3,776. Geometrik kök neden kanıtlanmadı. Sorun katmanların yalnız 16/235'inde görülüyor.",
        "Süre makine yüküne bağlı: aynı işlem 4.518 / 8.192 / 10.838 s. sure_s ~100 s içe aktarmayı içermiyor. Git geçmişinde 349–1.305 s; README'deki ~6 dk eski.",
        "Tarama omuz bölümü de pahalılaştı: %s s (daha önce 1.733 s), poz başına 10–19 s. Nedenini ölçmedim." % t(BOL["omuz"]["sure_s"], 0),
        "Yan bulgu: göğüs bandında iç ofset 143'te 139 kez hatalı (dar alan 0 sayılıyor, destek sorununa yazılmıyor), 16 katman 'Wire is not closed' ile atlanıyor. HEAD'de de var. 'Desteksiz' sonuçları temkinli okunmalı. Düzeltme yapılmadı.",
    ]),
    dict(baslik="Koşulmayan ve doğrulanmayan", liste=[
        "Tarama omuz bölümü yeniden koşulmadı (%s s sürmüştü); kaynak özeti eski, carpisma-sonuc.json tek_kosu false. Kol + dirsek × tüm kabuk kendi ızgaramda yeni modelde ölçüldü, ama omuz göbeği hareketi × yeni çerçeve ölçülmedi." % t(BOL["omuz"]["sure_s"], 0),
        "omuz ve iskelet regresyonu (ikinci/regresyon) 04.11 03:03 koşusu, QLED ve çerçeve düzenlemesinden önce. Yeniden koşulmadı.",
        "planlama/y2/Y2b-ivme.json ve Y2b-baski.json yenilenmedi (planlama klasörüne dokunulmadı). Aynı betiklerin geçici kopyası koşuldu, sonuç ikinci/ivme-qled.json ve ikinci/baski-qled.json.",
        "Kol taraması kabuk için aralık içi kesin en küçük boşluk vermiyor (dal-sınır aralık içi ve dışı ortak). 5 mm altı her aday ölçüldü; kesin sayılar kendi ızgaramdan, sürekli tarama değil.",
        "Kafa × kol ızgarası aralıkta yalnız tilt -10, 0, 10 içeriyor; ±13 ve ±15 pan 15° adımla ayrı ölçüldü.",
        "montaj_gorsel.py, eklem_dogrulama.py, kafa_gorsel.py ve modül raporları koşulmadı. robot-montaj.FCStd içinde GUI görünümü yok; görseller için qled_gorsel.py ve sekil4_gorsel.py görünümü kendi kurar.",
        "Repodaki omuz/regresyon ve iskelet/regresyon once.json Ekim tasarımından; betiğin kendi farkı bu yüzden FARK VAR der.",
        "Akü modelde 2,8 kg, malzeme listesindeki Victron 3,0 kg: devrilme ve kütle 2,8 kg ile. Kafa ekranı 600 g ve 4,5 W varsayım.",
    ]),
]

R = dict(
    durum="Kontrol, 04.11.2026, dal lale-duzeltme. Son robot-montaj.FCStd uzerinde: boy, ekran, kol, kafa, tilt, baski gecti. Omuz bolumu ve iskelet/omuz regresyonu QLED sonrasi yeniden kosulmadi.",
    baslik="Bu bolumdeki sayilar 04.11.2026 kosularindan. Tarama kosu kimligi " + BOL["statik"]["kosu"] + " (omuz bolumu haric: " + BOL["omuz"]["kosu"] + ").",
    maddeler=maddeler, bolumler=bolumler)
json.dump(R, open(os.path.join(HERE, "lale158-regresyon.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for m in maddeler:
    print(m["madde"], "|", m["olcum"], "|", m["sonuc"])
for b in bolumler:
    if b.get("satir"):
        print(b["baslik"], b["satir"])
print("omuz diger", RO["diger"], "iskelet diger", RI["diger"], "iskelet fark", RI["fark"])
