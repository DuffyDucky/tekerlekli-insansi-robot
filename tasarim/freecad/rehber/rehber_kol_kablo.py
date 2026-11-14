# 3B montaj rehberi: kol içi kablo yolu (F10f, P10.5). FreeCAD İSTEMEZ (standart kütüphane + numpy); tasarım kaynağını yalnız okur.
#   py -3 -X utf8 tasarim/freecad/rehber/rehber_kol_kablo.py            # rehber/veri/rehber-veri.{json,js}'e şemaları yaz + denetim
#   py -3 -X utf8 tasarim/freecad/rehber/rehber_kol_kablo.py --yazma    # yalnız türet + denetle, veriye yazma
#   py -3 -X utf8 tasarim/freecad/rehber/rehber_kol_kablo.py --json <dosya>   # denetim sonucunu ayrıca bu dosyaya
# rehber_uret.py her üretimde (FreeCAD'li ya da --veri-yok) rehber_gorunum'dan sonra isle()'yi, ek denetimlerde denetle()'yi çağırır;
# sonuç planlama/rehber/kontrol.json "kol_kablo" alanına yazılır, sınır aşılırsa üretim çıkışı 2.
#
# Tek kaynak: tasarim/freecad/arayuz.py KOL_KABLO (sağ kol, omuz yereli: X dışarı, Y yukarı, Z ileri, orijin travers merkezi; ev pozu)
# ve tasarim/freecad/dirsek/kablo_yolu.py (düzlemsel elastika, S1 döner U-lop kaseti). Rehberde ayrı ölçü tablosu YOK: her üretimde
# noktalar buradan yeniden hesaplanır. kablo_yolu.py FreeCAD (App.Vector / Placement) ve scipy (fsolve) ister; ikisi bu makinenin
# Python'unda yok. Dosya değiştirilmeden, yalnız import anında en küçük yerine koyucularla yüklenir: Vector (toplama, çarpma, Length,
# dot), kimlik Placement (CAD duruşu: dirsek 0, S2 0, S1 0, dönüşüm yok) ve fsolve yerine sonlu farklı Newton. Doğrulama: aynı
# fonksiyonların dirsek_montaj.py'nin FreeCAD'li koşusunda yazdığı örnek noktalar (dirsek/dirsek-analiz.json "kablo") ile karşılaştırılır
# (KAYNAK_TOL mm).
#
# Kol modülü global yerleşimi: arayuz.MODULLER omuz_sag / dirsek_sag konum (0, S3, 0); sol kol = X aynası (omuz_sol / dirsek_sol ayna).
# Rehberin GLB'si CAD duruşunda (S1 0, S2 0, dirsek 0); şemalar da o duruşta çizilir. S1 yakın karesi için U-lop ayrıca S1 aralığının
# iki ucunda (OMUZ one_arka_aralik) çizilir; parçalar CAD duruşunda kalır (tambur ve kaset S1 ekseni etrafında dönel simetrik).
#
# Parçalar (yol bölümleri) ve döşendikleri adım: rehber_metin.py ADIM[...]["sira"] gruplarının "kolk" alanı (bölüm anahtarları). Her
# bölüm tam bir alt adıma bağlanır; bağlanmayan ya da iki kez bağlanan bölüm denetim hatasıdır. Kaynakta tanımlı olmayan yol parçası
# (S2 servo kablosunun servodan eke kadarki yolu, gövde içi dikey yolun ayrıntısı) çizilmez: TANIMSIZ listesi.
import os, sys, re, json, math, time, types, argparse, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.dirname(HERE)
ROBOT = os.path.dirname(os.path.dirname(FC))
VERI_DIR = os.path.join(ROBOT, "rehber", "veri")
sys.path.insert(0, HERE)
sys.path.insert(0, FC)
import arayuz as A                                                  # noqa: E402  (yalnız math kullanır)

KAYNAK = "kol_kablo"               # semalar[].kaynak öneki (bu betiğin yazdıkları; her koşuda silinip yeniden yazılır)
KAYNAK_TOL = 0.05                  # mm: türetilen nokta ↔ dirsek-analiz.json örnek noktası (FreeCAD'li koşu, 3 ondalık)
AYNA_TOL = 1e-6                    # mm: sol = sağın X aynası
ALT_N = 4                          # elastika: 120 parçalık çözümün her 4. noktası (+ son nokta) çizilir
# F10f düzeltme 1 (kontrol madde 6): uzatma yeşili (#0d8f6f) K2 gövde demeti camgöbeğine (#00a3a3) ΔE76 21 idi (36.4 / 36.5
# karışıyordu); yeni uzatma rengi menekşe, rehberdeki bütün kablo ve şema renklerine ve iki zemine ΔE76 ≥ 51 (F10f-gunluk.md Düzeltme
# turu 1). Bilek eki dirsek ekinden ayrı renkte (48.2 / 48.3: iki ek tek kabloda sırayla iki ek gibi okunuyordu). Kablo bağı (K noktası,
# tambur bağı) ayrı işaret. Uç duruş U-lopları iki karede aynı renk (öbür duruş soluk iz, app.js "iz").
# P10.7b1: kablo bölümlerinin (servo, uzatma, uzatma_b, poz_a, poz_b) veriye yazılan rengi ve yarıçapı artık planlama/adim3/kablolar.json
# devre sınıfından (rehber_kablo.py; isle()); aşağıdaki servo / uzatma / poz renkleri yalnız türetme ara değeri. İşaretler (ek, ek_b, bag,
# ek_nokta) kendi renginde kalır.
RENK = dict(servo="#c47a00",       # servo kabloları (servonun kendi kablosu, ek yerine kadar)
            uzatma="#dd00ff",      # uzatmalar (ek yerinden gövdeye)
            uzatma_b="#8a2be2",    # aynı alt adımda ardışık ikinci uzatma bölümü (40.2: S2 lopu), bölüm sınırı görünsün
            ek="#1a1a1a",          # dirsek eki: JR çifti
            ek_b="#ffd400",        # bilek eki: lehim + makaron
            bag="#ffffff",         # kablo bağı (K noktası, tambur bağı)
            ek_nokta="#ffffff",    # F10f düzeltme 2: ek noktası halkası (lehim ortası, JR birleşimi): iki ek iki ayrı nokta okunsun
            poz_a="#dd00ff", poz_b="#dd00ff")
# lejant adı (app.js): şema türü -> okurun gördüğü ad. Bölüm kendi lejantını taşıyabilir (S2 lopu: S2 0° notu)
LEJANT = dict(servo="Servo kablosu", uzatma="Uzatma (gövdeye)", uzatma_b="Uzatma (gövdeye)", ek="Ek: dirsek JR çifti",
              ek_b="Ek: bilek lehim + makaron", bag="Kablo bağı", ek_nokta="Ek noktası (lehim / JR birleşimi)", poz_a="U-lopu, bu uç duruş", poz_b="U-lopu, bu uç duruş")
R_TUP = 2.5                        # şema tüp yarıçapı (mm, app.js varsayılanı)
R_EK = 5.0                         # ek işareti tüp yarıçapı (mm)


# ------------------------------------------------------------------ kablo_yolu.py'yi FreeCAD'siz yükle
class _V:
    __slots__ = ("x", "y", "z")

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x, self.y, self.z = float(x), float(y), float(z)

    def __add__(self, o):
        return _V(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o):
        return _V(self.x - o.x, self.y - o.y, self.z - o.z)

    def __mul__(self, k):
        return _V(self.x * k, self.y * k, self.z * k)

    __rmul__ = __mul__

    def __getitem__(self, i):
        return (self.x, self.y, self.z)[i]

    def dot(self, o):
        return self.x * o.x + self.y * o.y + self.z * o.z

    @property
    def Length(self):
        return math.sqrt(self.dot(self))

    def t(self):
        return (self.x, self.y, self.z)


class _Rot:
    def multVec(self, v):
        return _V(v.x, v.y, v.z)


class _Pl:                         # kimlik yerleşim: CAD duruşu (eklem açısı 0)
    Rotation = _Rot()

    def multVec(self, v):
        return _V(v.x, v.y, v.z)


def _fsolve(f, x0, xtol=1e-12, maxit=200):
    """scipy.optimize.fsolve yerine: sonlu farklı Jacobian'lı, adımı yarılayan Newton (3 bilinmeyen)."""
    import numpy as np
    x = np.array(x0, float)
    r = np.array(f(x), float)
    for _ in range(maxit):
        J = np.zeros((len(r), len(x)))
        for j in range(len(x)):
            h = 1e-7 * max(1.0, abs(x[j]))
            xx = x.copy(); xx[j] += h
            J[:, j] = (np.array(f(xx), float) - r) / h
        dx = np.linalg.solve(J, -r)
        a = 1.0
        while a > 1e-6:
            xn = x + a * dx
            rn = np.array(f(xn), float)
            if np.abs(rn).max() < np.abs(r).max() or a < 1e-3:
                break
            a *= 0.5
        x, r = xn, rn
        if np.abs(dx * a).max() < xtol * max(1.0, np.abs(x).max()) and np.abs(r).max() < 1e-12:
            break
    return x


def kablo_yolu():
    """dirsek/kablo_yolu.py modülü (dosya değişmez). FreeCAD / Part / scipy yoksa yerine koyucularla yüklenir."""
    yol = os.path.join(FC, "dirsek", "kablo_yolu.py")
    ek = {}
    try:
        import FreeCAD  # noqa: F401
    except ImportError:
        app = types.ModuleType("FreeCAD"); app.Vector = _V; app.Placement = _Pl
        ek["FreeCAD"] = app
        ek["Part"] = types.ModuleType("Part")
    try:
        import scipy.optimize  # noqa: F401
    except ImportError:
        sp = types.ModuleType("scipy"); so = types.ModuleType("scipy.optimize"); so.fsolve = _fsolve; sp.optimize = so
        ek["scipy"], ek["scipy.optimize"] = sp, so
    eski = {k: sys.modules.get(k) for k in ek}
    sys.modules.update(ek)
    try:
        s = importlib.util.spec_from_file_location("kablo_yolu_rehber", yol)
        m = importlib.util.module_from_spec(s)
        s.loader.exec_module(m)
    finally:
        for k, v in eski.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    m._yerine = sorted(ek)
    if "scipy.optimize" in ek:                                      # u_lop scipy'yi çağrı anında import eder: çağrı süresince yerine koy
        _u = m.u_lop

        def u_lop(*a, **k):
            esk = {q: sys.modules.get(q) for q in ("scipy", "scipy.optimize")}
            sys.modules["scipy"], sys.modules["scipy.optimize"] = ek["scipy"], ek["scipy.optimize"]
            try:
                return _u(*a, **k)
            finally:
                for q, v in esk.items():
                    if v is None:
                        sys.modules.pop(q, None)
                    else:
                        sys.modules[q] = v
        m.u_lop = u_lop
    return m


# ------------------------------------------------------------------ yol bölümleri (sağ kol, omuz yereli)
def _t(v):
    return tuple(float(c) for c in (v.t() if hasattr(v, "t") else v))


def _lop(KY, lt):
    r = KY.lop_coz(lt, lambda poz: _Pl(), [0.0])[0]
    pts = [_t(q) for q in r["nokta"]]
    return pts, r


def turet():
    """Sağ kol yol bölümleri (omuz yereli) + türetme bilgisi. Doner (bolumler, bilgi)."""
    KY = kablo_yolu()
    KK = A.KOL_KABLO
    S1 = KK["s1"]
    O = KY.s1_olcu(KK)
    lop_d, rd = _lop(KY, KK["dirsek_lop"])
    lop_s2, rs = _lop(KY, KK["s2_lop"])
    ust = [tuple(p) for p in KK["yol_ustkol"]["nokta"]]
    uz = [tuple(p) for p in KK["yol_uzatma_kol"]["nokta"]]
    bir = tuple(KK["birlesim"])
    gec = [_t(q) for q in KY.s1_gecis(KK, O)]
    s1 = {phi: KY.s1_poz(KK, phi, O) for phi in (0.0,) + tuple(A.OMUZ["one_arka_aralik"])}
    cik = [_t(q) for q in KY.s1_cikis(KK, O)]
    TP = KK["tup_pencere"]
    # tüp penceresinin yol üstündeki noktası: yol_uzatma_kol'un pencere aralığına (y, z) giren ilk köşesi
    ip = next(i for i, p in enumerate(uz) if TP["y"][0] <= p[1] <= TP["y"][1] and TP["z"][0] <= p[2] <= TP["z"][1])
    ncik = 3                                                         # s1_cikis: duvar bağı, ψ_c (duvar boyunca), r_don (radyal), x_ic ...
    jr = KK["jr_eslesik"]
    tup_giris = ust[-1][1]
    bek = KK["bilek_ek"]
    B = []

    def bol(k, ad, kod_ipucu, pts, tur, serit, kaynak, uc, r=R_TUP, renk=None, lejant=None):
        B.append(dict(k=k, ad=ad, pts=[tuple(round(c, 4) for c in p) for p in pts], tur=tur, serit=serit, kaynak=kaynak,
                      uc=uc, r=r, renk=renk or RENK[tur], ipucu=kod_ipucu, lejant=lejant or LEJANT[tur]))

    def isaret(p, q, yari=2.0):                                     # p noktasında, p→q teğeti boyunca 2·yari mm kısa işaret
        d = [b - a for a, b in zip(p, q)]
        n = math.sqrt(sum(x * x for x in d)) or 1.0
        return [tuple(p), tuple(a + 2 * yari * x / n for a, x in zip(p, d))]   # yalnız kablonun üstünde (uçtan dışarı taşmaz)
    L = lambda pts: sum(math.dist(a, b) for a, b in zip(pts[:-1], pts[1:]))   # noqa: E731
    bol("servo_bilek", "Bilek servosu kablosu: mil ucu → ara duvar çentiği → dirsek servosu arkası → tırnak", "H0a",
        KK["yol_bilek_servo"]["nokta"], "servo", 1, "KOL_KABLO yol_bilek_servo", ("Bilek servosu MG996R", "Ön kol gövdesi"))
    bol("servo_dirsek", "Dirsek servosu kablosu: servo üstü → tırnak", "H0a",
        KK["yol_dirsek_servo"]["nokta"], "servo", 1, "KOL_KABLO yol_dirsek_servo", ("Dirsek servosu MG996R", "Ön kol gövdesi"))
    bol("lop_dirsek", "Dirsek lopu (L %g, 2 kablo): tırnak → çatal oluğu → Ø10 delik" % KK["dirsek_lop"]["L"], "H0c",
        lop_d[::ALT_N] + ([lop_d[-1]] if (len(lop_d) - 1) % ALT_N else []) + ust[1:2], "servo", 2,
        "KOL_KABLO dirsek_lop (kablo_yolu.lop_coz, dirsek 0) + yol_ustkol[0:2]", ("Ön kol gövdesi", "Dirsek çatalı"))
    # F10f düzeltme 2 (kontrol B2 3.3): tüp içi yol tüp girişinde biter; iki ek arasındaki parça (bilek kablosu lehimden sonra
    # uzatma) uzatma renginde ayrı bölüm; lehim ortası ve JR birleşimi beyaz halka (iki ek tek kabloda seri değil, iki ayrı nokta)
    bol("tup_ici", "Tüp içi: Ø10 delik → tüp girişi (y %g)" % tup_giris, "H1",
        ust[1:], "servo", 2, "KOL_KABLO yol_ustkol[1:]", ("Dirsek çatalı", "Üst kol tüpü"))
    y_leh = tup_giris + bek["makaron"][1]
    bol("tup_ara", "Tüp içi, iki ek arası (y %g → %g): bilek uzatması (lehimden sonra) yanında dirsek servo kablosu (JR'ye kadar)"
        % (y_leh, bir[1] - jr[2] / 2), "H1", [(ust[-1][0], y_leh, ust[-1][2]), (bir[0], bir[1] - jr[2] / 2, bir[2])], "uzatma", 2,
        "KOL_KABLO bilek_ek makaron ucu → birlesim − jr_eslesik/2 (aynı x, z: düz)", ("Üst kol tüpü", "Üst kol tüpü"))
    bol("ek_jr", "Ek yeri: dirsek kablosu JR çifti (%g mm), tüp içinde birleşimde" % jr[2], "H1",
        [(bir[0], bir[1] - jr[2] / 2, bir[2]), (bir[0], bir[1] + jr[2] / 2, bir[2])], "ek", 2,
        "KOL_KABLO birlesim + jr_eslesik boyu (dirsek_montaj geçit kutusu: boy y yönünde)", ("Üst kol tüpü", "Üst kol tüpü"), r=R_EK)
    bol("ek_bilek", "Ek yeri: bilek kablosu lehim + makaron (%g mm), tüp girişinin üstünde (yer yaklaşık)" % bek["makaron"][1], "H1",
        [(ust[-1][0], tup_giris, ust[-1][2]), (ust[-1][0], tup_giris + bek["makaron"][1], ust[-1][2])], "ek", 1,
        "KOL_KABLO bilek_ek (makaron %g mm; servo kablosu tüp girişine artan ~0,5 mm ile ulaşır, dirsek-analiz boy)" % bek["makaron"][1],
        ("Üst kol tüpü", "Üst kol tüpü"), r=R_EK, renk=RENK["ek_b"], lejant=LEJANT["ek_b"])
    y_lo = tup_giris + bek["makaron"][1] / 2
    bol("nokta_lehim", "Ek noktası: bilek kablosu lehimi (makaron ortası, y %g)" % y_lo, "H1",
        [(ust[-1][0], y_lo - 1.5, ust[-1][2]), (ust[-1][0], y_lo + 1.5, ust[-1][2])], "ek_nokta", 1,
        "KOL_KABLO bilek_ek makaron ortası; halka 3 mm", ("Üst kol tüpü", "Üst kol tüpü"), r=R_EK + 0.8)
    bol("nokta_jr", "Ek noktası: dirsek kablosu JR birleşimi (y %g)" % bir[1], "H1",
        [(bir[0], bir[1] - 1.5, bir[2]), (bir[0], bir[1] + 1.5, bir[2])], "ek_nokta", 1,
        "KOL_KABLO birlesim; halka 3 mm", ("Üst kol tüpü", "Üst kol tüpü"), r=R_EK + 0.8)
    bol("uzatma_tup", "Uzatmalar tüp içinde: birleşim → tüp penceresi", "H1", uz[:ip + 1], "uzatma", 2,
        "KOL_KABLO yol_uzatma_kol[0:%d]" % (ip + 1), ("Üst kol tüpü", "Üst kol tüpü"))
    bol("uzatma_kol", "Uzatmalar: tüp penceresi → tüp cıvatası yanı → K noktası (çatal arka plakası arkası)", "G3", uz[ip:], "uzatma", 2,
        "KOL_KABLO yol_uzatma_kol[%d:]" % ip, ("Üst kol tüpü", "Kol çatalı"))
    # F10f düzeltme 1 (madde 5): lop modeldeki duruşta (S2 0°, aralık dışı) çizilir; lejant ve ad bunu söyler
    bol("lop_s2", "S2 lopu (L %g, 2 kablo): K noktası → göbek arka iç şeridi (G2); çizim S2 0°, aralık dışı" % KK["s2_lop"]["L"], "G3",
        lop_s2[::ALT_N] + ([lop_s2[-1]] if (len(lop_s2) - 1) % ALT_N else []), "uzatma", 2,
        "KOL_KABLO s2_lop (kablo_yolu.lop_coz, S2 0)", ("Kol çatalı", "Omuz göbeği"), renk=RENK["uzatma_b"],
        lejant="S2 lopu: çizim S2 0°, aralık dışı (tasarım S2 %g…%g°)" % tuple(A.OMUZ["yana_aralik"]))
    # F10f düzeltme 1 (madde 6): kablo bağı işaretleri. K noktası: s2_lop M (KOL_KABLO "K: kol çatalı arka plakası arkasında kablo bağı
    # tabanı"); tambur bağı: s1_gecis son noktası (ψ bag_psi, 2 ip)
    bol("bag_k", "Kablo bağı: K noktası (çatal arka plakasının arkası, yapışkan taban)", "G3", isaret(lop_s2[0], lop_s2[1]), "bag", 2,
        "KOL_KABLO s2_lop M (K) + bag_tabani; işaret 4 mm, lop teğeti boyunca", ("Kol çatalı", "Kol çatalı"), r=R_EK - 1.0)
    bol("bag_tambur", "Kablo bağı: tambur bağı (ψ %g, 2 ip)" % S1["tambur"]["bag_psi"], "G3", isaret(gec[-1], gec[-2]), "bag", 3,
        "kablo_yolu.s1_gecis son nokta (tambur bağı); işaret 4 mm, geçiş teğeti boyunca", ("S1 kablo tamburu", "S1 kablo tamburu"), r=R_EK - 1.0)
    bol("gecis_s1", "G2 → tambur bağı (ψ %g, 3 kablo: dirsek, bilek, S2 uzatmaları)" % S1["tambur"]["bag_psi"], "G3", gec, "uzatma", 3,
        "kablo_yolu.s1_gecis", ("Omuz göbeği", "S1 kablo tamburu"))
    bol("s1_lop", "S1 U-lopu (L %g): tambur bağı → iç koşu (tamburda) → U → dış koşu (duvarda) → duvar bağı" % S1["L"], "G4",
        [_t(q) for q in s1[0.0]["nokta"]], "uzatma", 3, "kablo_yolu.s1_poz (S1 0)", ("S1 kablo tamburu", "S1 kaset gövdesi"))
    bol("s1_cikis", "Duvar bağı → duvar boyunca ψ %g → radyal içe (r %g) → kaset arka plakası yarığı" % (S1["cikis"]["psi"], S1["cikis"]["r_don"]),
        "G4", cik[:ncik], "uzatma", 3, "kablo_yolu.s1_cikis[0:%d]" % ncik, ("S1 kaset gövdesi", "S1 kaset gövdesi"))
    bol("govde", "Yarık (ψ %g, %g × %g) → gövde içi → travers arkası" % (S1["cikis"]["psi"], S1["cikis"]["yarik"][0], S1["cikis"]["yarik"][1]),
        "F4", cik[ncik - 1:], "uzatma", 3, "kablo_yolu.s1_cikis[%d:] (x_ic, govde_ici)" % (ncik - 1),
        # F4'te kaset yok (G4): yarık ucu omuz bandının yarığında; iç uç travers arkasında K2 servo uzatma demetine (adım 32 kablo parçası) katılır
        ("Omuz bandı", "Kablo yolu 6"))
    for phi, tur in zip(A.OMUZ["one_arka_aralik"], ("poz_a", "poz_b")):
        bol("s1_%+d" % phi, "S1 %+d°'de U-lopu (uç duruş): tambur bağı ψ %g → U → duvar bağı" % (phi, s1[phi]["psi_bag"]), "G4",
            [_t(q) for q in s1[phi]["nokta"]], tur, 3, "kablo_yolu.s1_poz (S1 %+d)" % phi, ("S1 kablo tamburu", "S1 kaset gövdesi"))
    bilgi = dict(
        yerine_koyucu=KY._yerine, s1_olcu=dict(ri=O["ri"], ro=O["ro"], xc=O["xc"], U_l=O["U"]["l"], U_delta=O["U"]["delta"],
                                                U_uc=O["U"]["pol_max"], U_R_min=O["U"]["R_min"], U_artik=O["U"]["artik"], U_gecerli=O["U"]["gecerli"]),
        s1_poz={("%+d" % k if k else "0"): dict(psi_bag=v["psi_bag"], psi_U=v["psi_U"], a_i=v["a_i"], a_o=v["a_o"], u_uc_psi=v["u_uc_psi"])
                for k, v in s1.items()},
        lop=dict(dirsek=dict(L=KK["dirsek_lop"]["L"], r_min=rd["r_min"], kiris=rd["kiris"], yakinsadi=rd["yakinsadi"]),
                 s2=dict(L=KK["s2_lop"]["L"], r_min=rs["r_min"], kiris=rs["kiris"], yakinsadi=rs["yakinsadi"])),
        boy={b["k"]: round(L(b["pts"]), 1) for b in B})
    return B, bilgi, KY


def kaynak_karsilastir(KY=None):
    """Türetilen noktalar ↔ dirsek/dirsek-analiz.json 'kablo' örnek noktaları (dirsek_montaj.py, FreeCAD'li koşu). Lop: aynı pozda
    (dirsek 0 / S2 5: dosyadaki ilk poz) her 6. nokta; S1: üç pozda her 4. nokta; U ölçüleri. Doner dict (en büyük fark, sayı, geçti)."""
    KY = KY or kablo_yolu()
    KK = A.KOL_KABLO
    D = json.load(open(os.path.join(FC, "dirsek", "dirsek-analiz.json"), encoding="utf-8"))["kablo"]
    out, fark = {}, []

    class _PlR:                                                     # Pr(th): z ekseni, merkez (XR, 0, 0) (omuz_parcalar Pr)
        def __init__(self, th, c):
            a = math.radians(th); self.c, self.s, self.o = math.cos(a), math.sin(a), c
            self.Rotation = types.SimpleNamespace(multVec=lambda v: _V(self.c * v.x - self.s * v.y, self.s * v.x + self.c * v.y, v.z))

        def multVec(self, v):
            x, y = v.x - self.o[0], v.y - self.o[1]
            return _V(self.c * x - self.s * y + self.o[0], self.s * x + self.c * y + self.o[1], v.z)
    for ad, lt, poz, pl in (("dirsek_lop", KK["dirsek_lop"], 0.0, _Pl()),
                            ("s2_lop", KK["s2_lop"], A.OMUZ["yana_aralik"][0], _PlR(A.OMUZ["yana_aralik"][0], (A.DIRSEK["tup_x"], 0.0)))):
        r = KY.lop_coz(lt, lambda p: pl, [poz])[0]
        ref = D[ad]["ornek_nokta"][str(poz)]
        bu = [_t(q) for q in r["nokta"][::6]]
        d = max(math.dist(a, b) for a, b in zip(bu, ref))
        out[ad] = dict(poz=poz, nokta=len(ref), en_buyuk_fark_mm=round(d, 4), r_min=round(r["r_min"], 2), r_min_kaynak=D[ad]["r_min"])
        fark.append(d)
    for phi, ref in D["s1_lop"]["ornek_nokta"].items():
        bu = [_t(q) for q in KY.s1_poz(KK, float(phi))["nokta"][::4]]
        d = max(math.dist(a, b) for a, b in zip(bu, ref)) if len(bu) == len(ref) else float("inf")
        out["s1_lop %s" % phi] = dict(nokta=len(ref), bu=len(bu), en_buyuk_fark_mm=round(d, 4))
        fark.append(d)
    O = KY.s1_olcu(KK)
    u = D["s1_lop"]["u"]
    du = max(abs(O["U"]["l"] - u["l"]), abs(O["U"]["delta"] - u["delta"]), abs(O["U"]["pol_max"] - u["uc"]), abs(O["U"]["R_min"] - D["s1_lop"]["r_min"]))
    out["s1_U"] = dict(l=round(O["U"]["l"], 3), delta=round(O["U"]["delta"], 3), uc=round(O["U"]["pol_max"], 3), R_min=round(O["U"]["R_min"], 3),
                       kaynak=dict(l=u["l"], delta=u["delta"], uc=u["uc"], R_min=D["s1_lop"]["r_min"]), en_buyuk_fark=round(du, 4))
    # U ölçüleri json'da 2-3 ondalık yuvarlı: yuvarlama payı 0,006
    gecti = all(f <= KAYNAK_TOL for f in fark) and du <= 0.006
    return dict(tol_mm=KAYNAK_TOL, karsilastirma=out, en_buyuk_fark_mm=round(max(fark), 4), gecti=bool(gecti))


def glob(p, sol):
    (tx, ty, tz), _ = A.modul_konum("omuz_sol" if sol else "omuz_sag")
    return ((-p[0] if sol else p[0]) + tx, p[1] + ty, p[2] + tz)


# Kaynakta yol olarak tanımlı olmayanlar (çizilmez; metinde yalnız kaynaktaki değer)
TANIMSIZ = [
    "S2 servo kablosu: servodan eke kadar yol (KOL_KABLO s1 s2_birlesim: 'gobek arka ic seridi, G2 oncesi', G2_once 20 mm ve "
    "s2_servo_kablo 40 mm tahmini; nokta yok)",
    "S2 eki (lehim + makaron) yeri: G2'den yaklaşık 20 mm önce; koordinat yok, işaret çizilmedi",
    "Gövde içi dikey yol (KOL_KABLO s1 govde_dikey, travers altı → dağıtım kartı): kol yolu değil, K2 gövde kablolaması (P10.7); çizilmedi",
    "Tüp içinde tüp girişi (y −152) → birleşim (y −105) arası ayrı yol olarak tanımlı değil; iki tanımlı nokta aynı x, z'de, düz çizildi",
    "Bilek eki (lehim + makaron) yeri: kaynakta 'makaron tüp girişinin üstünde serbest'; işaret tüp girişinden başlayan 25 mm (yaklaşık)",
]


# ------------------------------------------------------------------ veriye yazma
def metin_kolk():
    """rehber_metin.py: adım kodu -> [(grup sırası, kolk tuple)]."""
    import importlib
    import rehber_metin as RM
    importlib.reload(RM)
    out = {}
    for kod, mt in RM.ADIM.items():
        for n, g in enumerate(mt.get("sira") or []):
            if g.get("kolk"):
                out.setdefault(kod, []).append((n, tuple(g["kolk"]), tuple(g.get("saydam") or ())))
    return out


def isle(V=None, yazma=False, sessiz=False):
    t0 = time.time()
    kendi = V is None
    if kendi:
        V = json.load(open(os.path.join(VERI_DIR, "rehber-veri.json"), encoding="utf-8"))
    B, bilgi, KY = turet()
    import rehber_kablo as RKB                                      # P10.7b1: tek kablo kaynağı (renk, yarıçap, bilgi)
    TBL = RKB.Tablo()
    kod_i = {a["kod"]: a["i"] for a in V["adimlar"]}
    S = [s for s in V["semalar"] if not str(s.get("kaynak", "")).startswith(KAYNAK + ":")]
    n0 = len(S)
    for a in V["adimlar"]:                                          # eski kol şemalarını grup listelerinden çıkar
        for g in a.get("sira_grup") or []:
            if g.get("sema"):
                g["sema"] = [i for i in g["sema"] if i < n0]
                if not g["sema"]:
                    g.pop("sema")
    KM = metin_kolk()
    bag = {}                                                        # "sag:servo_bilek" -> (adım i, grup n)
    hata = []
    for kod, lst in KM.items():
        if kod not in kod_i:
            hata.append("rehber_metin kolk: adım %s veride yok" % kod)
            continue
        st = V["adimlar"][kod_i[kod]]
        for n, ks, sd in lst:
            if not st.get("sira_grup") or n >= len(st["sira_grup"]):
                hata.append("%s.%d: veride grup yok (FreeCAD'li tam üretim gerekir)" % (kod, n + 1))
                continue
            for k in ks:
                if k in bag:
                    hata.append("%s iki grupta: %s ve %s.%d" % (k, bag[k], kod, n + 1))
                bag[k] = (kod_i[kod], n)
    tablo = []
    for yan, sol in (("sag", False), ("sol", True)):
        for b in B:
            if yan == "sol" and b["k"].startswith("s1_") and b["k"] not in ("s1_lop", "s1_cikis"):
                continue                                            # uç duruş yakın karesi yalnız sağ kol (sol aynı, aynalı)
            anahtar = "%s:%s" % (yan, b["k"])
            if anahtar not in bag:
                hata.append("bölüm adıma bağlı değil: %s" % anahtar)
                continue
            a, n = bag[anahtar]
            i = len(S)
            ad = ("Sağ" if not sol else "Sol") + " kol · " + b["ad"]
            s = dict(ad=ad, kaynak="%s:%s" % (KAYNAK, anahtar), a=a, renk=b["renk"], boy_mm=round(sum(math.dist(p, q) for p, q in zip(b["pts"][:-1], b["pts"][1:]))),
                     pts=[[round(c, 1) for c in glob(p, sol)] for p in b["pts"]], r=b["r"], t=V["adimlar"][a]["tezgah"] or "", kol=yan,
                     tur=b["tur"], lejant=b["lejant"])
            # P10.7b1: kablo bölümünün rengi ve tüp yarıçapı planlama/adim3/kablolar.json'dan (devre sınıfı, kesit; rehber_kablo.py).
            # İşaret bölümleri (ek, ek noktası, kablo bağı) kendi işaret rengini ve yarıçapını korur. Lejant: kendi notu olan bölüm
            # (S2 lopu, uç duruş U-lopu) ve işaretler adıyla; öbür kablo bölümleri lejantta devre sınıfıyla (app.js kablo_sinif).
            ids = RKB.kol_kimlik(anahtar)
            if ids is None:
                hata.append("kablo eşlemesi yok: %s (rehber_kablo.KOL_ESLEME)" % anahtar)
            else:
                isaret = b["tur"] in RKB.KOL_ISARET_TUR
                s.update(TBL.cizim(ids, isaret=isaret))
                if not isaret and b["lejant"] == LEJANT.get(b["tur"]) and b["tur"] not in ("poz_a", "poz_b"):
                    s.pop("lejant")
            S.append(s)
            g = V["adimlar"][a]["sira_grup"][n]
            g["sema"] = sorted(set(g.get("sema") or []) | {i})
            tablo.append(dict(sema=i, anahtar=anahtar, ad=ad, adim=V["adimlar"][a]["kod"], adres="%d.%d" % (a, n + 1), grup=g["ad"],
                              ipucu=b["ipucu"], kaynak=b["kaynak"], tur=b["tur"], serit=b["serit"], uc=list(b["uc"]),
                              bas=[round(c, 3) for c in glob(b["pts"][0], sol)], son=[round(c, 3) for c in glob(b["pts"][-1], sol)],
                              boy_mm=round(sum(math.dist(p, q) for p, q in zip(b["pts"][:-1], b["pts"][1:])), 1), nokta=len(b["pts"])))
    # F10f düzeltme 1 (madde 3): grup "iz" = soluk çizilen öbür şemalar (anahtar listesi, rehber_metin); veride şema numarası
    import rehber_metin as RM
    no = {t["anahtar"]: t["sema"] for t in tablo}
    for kod, mt in RM.ADIM.items():
        for n, g_ in enumerate(mt.get("sira") or []):
            if kod in kod_i and g_.get("iz"):
                e = V["adimlar"][kod_i[kod]]["sira_grup"][n]
                e["iz"] = [no[k] for k in g_["iz"] if k in no]
                hata += ["%s.%d iz bilinmeyen bölüm: %s" % (kod, n + 1, k) for k in g_["iz"] if k not in no]
    fazla = sorted(set(bag) - {t["anahtar"] for t in tablo})
    hata += ["rehber_metin kolk bilinmeyen bölüm: %s" % k for k in fazla]
    V["semalar"] = S
    V["kol_kablo"] = dict(
        betik="tasarim/freecad/rehber/rehber_kol_kablo.py", kaynak="tasarim/freecad/arayuz.py KOL_KABLO + tasarim/freecad/dirsek/kablo_yolu.py",
        koordinat="global mm (omuz yereli + arayuz.MODULLER omuz_sag konum; sol = X aynası); CAD duruşu (S1 0, S2 0, dirsek 0)",
        bolum=tablo, tanimsiz=TANIMSIZ, bilgi=bilgi, hata=hata, sema_ilk=n0, sema_son=len(S) - 1)
    if not sessiz:
        print("kol kablo: %d bölüm (%d şema, ilk %d), bağlanmayan / hata %d%s (%.1f s)" % (
            len(tablo), len(S) - n0, n0, len(hata), (": " + "; ".join(hata[:4])) if hata else "", time.time() - t0))
    if yazma:
        yaz(V)
    return V


# ------------------------------------------------------------------ denetim (kontrol.json "kol_kablo")
VERI_TOL = 0.1          # mm: veri noktaları 0,1 mm'ye yuvarlı; türetmeyle fark (ve sağ ↔ sol ayna) bunu aşarsa hata
UC_TOL = 6.0            # mm: bölüm ucu ↔ beklenen parçanın ağ yüzeyi. Gerekçe: K noktası kablo bağı tabanı (KOL_KABLO bag_tabani 3,5 mm,
                        # modelde yok) + 3 kablo demeti yarı kalınlığı 2,1 mm; ağ (GLB) sapması ayrıca ≤ 0,5 mm
ICINDE_ESIK = 0.2       # mm: merkez çizgisi noktası bir katının bu kadardan derin içindeyse "içinden geçiyor" (ağ üçgenleme payı;
                        # rehber_giris ortak hacim eşiğiyle aynı)
ORNEK = 1.0             # mm: merkez çizgisi örnekleme aralığı
EL_ULASIM = 150.0       # mm: noktadan el bölgesine (rehber_sira EL zarfı, 20 mm) düz, engelsiz ışın; somun lokması ölçütüyle aynı
# Uç noktası ↔ parça: "icinde" = nokta parçanın oyuğunun / borusunun içinde (sınır kutusu içinde ve en yakın parça o), öbürleri yüzey
UC_TIP = {("tup_ici", 1): "icinde", ("ek_jr", 0): "icinde", ("ek_jr", 1): "icinde", ("ek_bilek", 0): "icinde", ("ek_bilek", 1): "icinde",
          ("uzatma_tup", 0): "icinde", ("tup_ara", 0): "icinde", ("tup_ara", 1): "icinde", ("nokta_lehim", 0): "icinde",
          ("nokta_lehim", 1): "icinde", ("nokta_jr", 0): "icinde", ("nokta_jr", 1): "icinde"}
# Elin çalışmadığı noktalar (gerekçe): kablo bu noktalara itilerek / çekilerek gelir, el geçitte çalışır
# F10f düzeltme 1 (madde 4): yalnız kaynakta tanımlı olan: dişi JR Ø10 delikten ve tüp penceresinden geçer (dirsek_montaj 8b geçit),
# eşleşik çift tüp içinde (y −122…−62). JR'nin nerede takıldığı ve bilek lehiminin tüpün hangi tarafında yapıldığı tasarımda tanımlı değil.
EL_YOK = {
    "tup_ici": "tüp içi (servo kablosu Ø10 delikten itilir; dişi JR tüp penceresinden geçebilir; el delikte ve pencerede)",
    "ek_jr": "tüp içi ek (eşleşik JR çifti tüp içinde; takıldığı yer tasarımda tanımlı değil)",
    "ek_bilek": "tüp içi ek (lehim + makaron tüp girişinin üstünde; lehimin yapıldığı yer tasarımda tanımlı değil)",
    "tup_ara": "tüp içi, iki ek arası (kablolar delikten itilir, pencereden çekilir)",
    "nokta_lehim": "tüp içi ek noktası (lehim)",
    "nokta_jr": "tüp içi ek noktası (JR birleşimi)",
}
EL_YOK_NOKTA = {("uzatma_tup", 0): "birleşim (tüp içi)", ("uzatma_tup", 1): "tüp içi"}
# Katı istisnaları (bölüm, parça adı deseni) -> gerekçe. Tasarımda temas yüzeyi olan parçalar; derinlik yine raporlanır.
KATI_ISTISNA = {("govde", "Kablo yolu"): "K2 gövde kablo demeti (adım 32 kablo parçası): kol uzatmaları travers arkasında bu demete katılır; "
                                         "kablo ↔ kablo, katı değil"}


def _geri_dondur(q, phi):
    """Global nokta q'yu S1 ekseni (omuz yereli x, travers merkezi) çevresinde −phi döndür (ψ = atan2(−z, y); uç duruş şemasının tambur
    ucu CAD duruşundaki tambura bakılsın diye). Sağ ve sol aynı (ψ x aynasından etkilenmez)."""
    (tx, ty, tz), _ = A.modul_konum("omuz_sag")
    y, z = q[1] - ty, q[2] - tz
    r, psi = math.hypot(y, z), math.atan2(-z, y) - math.radians(phi)
    return (q[0], ty + r * math.cos(psi), tz - r * math.sin(psi))


def _nokta_ucgen(P, T):
    """P (m, 3) noktaları ile T (n, 3, 3) üçgenleri arası en kısa uzaklık (m,). Ericson, vektörel; n büyükse parça parça."""
    import numpy as np
    best = np.full(len(P), np.inf)
    CH = max(1, 60000 // max(len(P), 1))
    for s in range(0, len(T), CH):
        a, b, c = T[s:s + CH, 0][None], T[s:s + CH, 1][None], T[s:s + CH, 2][None]
        p = P[:, None, :]
        ab, ac, ap = b - a, c - a, p - a
        d1, d2 = (ab * ap).sum(-1), (ac * ap).sum(-1)
        bp = p - b; d3, d4 = (ab * bp).sum(-1), (ac * bp).sum(-1)
        cp = p - c; d5, d6 = (ab * cp).sum(-1), (ac * cp).sum(-1)
        va = d3 * d6 - d5 * d4; vb = d5 * d2 - d1 * d6; vc = d1 * d4 - d3 * d2
        den = va + vb + vc
        den = np.where(np.abs(den) < 1e-18, 1e-18, den)
        v = vb / den; w = vc / den
        q = a + ab * v[..., None] + ac * w[..., None]                 # iç bölge
        # kenar / köşe bölgeleri
        m = (d1 <= 0) & (d2 <= 0); q = np.where(m[..., None], a, q)
        m2 = (d3 >= 0) & (d4 <= d3); q = np.where(m2[..., None], b, q)
        m3 = (d6 >= 0) & (d5 <= d6); q = np.where(m3[..., None], c, q)
        m4 = (vc <= 0) & (d1 >= 0) & (d3 <= 0) & ~m & ~m2
        t = d1 / np.where(np.abs(d1 - d3) < 1e-18, 1e-18, d1 - d3)
        q = np.where(m4[..., None], a + ab * t[..., None], q)
        m5 = (vb <= 0) & (d2 >= 0) & (d6 <= 0) & ~m & ~m3
        t = d2 / np.where(np.abs(d2 - d6) < 1e-18, 1e-18, d2 - d6)
        q = np.where(m5[..., None], a + ac * t[..., None], q)
        m6 = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0) & ~m2 & ~m3
        t = (d4 - d3) / np.where(np.abs((d4 - d3) + (d5 - d6)) < 1e-18, 1e-18, (d4 - d3) + (d5 - d6))
        q = np.where(m6[..., None], b + (c - b) * t[..., None], q)
        d = np.linalg.norm(p - q, axis=-1).min(1)
        best = np.minimum(best, d)
    return best


YONLER = ((0.5773, 0.5779, 0.5767), (0.31, -0.81, 0.5), (-0.7, 0.2, -0.68))


def _icinde3(Q, T):
    """Eğik ışın paritesi üç yönde; nokta yalnız üçünde de tekse içeride. Kapalı olmayan ağda (açık kenarlı; ör. omuz bandı sağ 53
    tek kenar) tek yönlü parite yanılıyor: 36.4'te sağ gövde yolu 27 noktada 'içeride' çıktı, öbür iki yönde 5, en yakın yüzey 2,98 mm."""
    import numpy as np
    v0, e1, e2 = T[:, 0], T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]
    ic = np.ones(len(Q), bool)
    for D in YONLER:
        D = np.array(D) / np.linalg.norm(D)
        h = np.cross(D, e2); a = (e1 * h).sum(1); ok = np.abs(a) > 1e-12
        fa = np.where(ok, 1 / np.where(ok, a, 1), 0)
        n = np.zeros(len(Q), int)
        for c in range(0, len(Q), 40):
            s_ = Q[c:c + 40, None, :] - v0[None]
            uu = fa[None] * np.einsum("mnk,nk->mn", s_, h)
            qq = np.cross(s_, e1[None])
            vv = fa[None] * (qq @ D)
            tt = fa[None] * np.einsum("nk,mnk->mn", e2, qq)
            n[c:c + 40] = (ok[None] & (uu >= 0) & (vv >= 0) & (uu + vv <= 1) & (tt > 1e-9)).sum(1)
        ic &= (n % 2) == 1
    return ic


def _acik_kenar(f):
    import numpy as np
    e = np.sort(np.vstack([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]), 1)
    _, c = np.unique(e, axis=0, return_counts=True)
    return int((c == 1).sum())


def _ornekle(pts, h=ORNEK):
    import numpy as np
    out = [np.array(pts[0], float)]
    for a, b in zip(pts[:-1], pts[1:]):
        a, b = np.array(a, float), np.array(b, float)
        n = max(1, int(math.ceil(np.linalg.norm(b - a) / h)))
        for k in range(1, n + 1):
            out.append(a + (b - a) * k / n)
    return np.array(out)


def _demet_yari(serit):
    return serit * A.KOL_KABLO["serit"][1] / 2.0


def denetle(V=None, D=None, el=True, sessiz=False):
    """Kalıcı denetim. V: rehber-veri (yoksa diskten). D: rehber_sira.Denetim (el bölgesi + ışın sahnesi; yoksa kurulur). Doner dict
    (gecti, sayılar, bölüm tablosu). Sınırlar: kaynak farkı ≤ KAYNAK_TOL, veri ↔ türetme ≤ VERI_TOL, ayna ≤ VERI_TOL, bağlanmayan 0,
    uç parçada değil 0, katı içinden geçen (istisnasız) 0, kablo adımında ulaşılamaz 0, metin ↔ kaynak sayı eksik 0, metinde pin /
    kanal / konnektör eşlemesi 0."""
    import numpy as np
    t0 = time.time()
    if V is None:
        V = json.load(open(os.path.join(VERI_DIR, "rehber-veri.json"), encoding="utf-8"))
    K = V.get("kol_kablo") or {}
    sonuc = dict(sinir=dict(kaynak_tol_mm=KAYNAK_TOL, veri_tol_mm=VERI_TOL, uc_tol_mm=UC_TOL, icinde_esik_mm=ICINDE_ESIK,
                            ornek_mm=ORNEK, el_ulasim_mm=EL_ULASIM))
    hata = list(K.get("hata") or [])
    # 1) kaynak ↔ FreeCAD'li koşunun örnek noktaları
    B, bilgi, KY = turet()
    kk = kaynak_karsilastir(KY)
    sonuc["kaynak"] = kk
    # 2) veri ↔ türetme, 3) ayna
    BK = {b["k"]: b for b in B}
    S = V["semalar"]
    kol = [(i, s) for i, s in enumerate(S) if str(s.get("kaynak", "")).startswith(KAYNAK + ":")]
    vt = []
    for i, s in kol:
        yan, k = s["kaynak"].split(":")[1:]
        b = BK.get(k)
        if not b:
            hata.append("veride bilinmeyen bölüm %s" % s["kaynak"]); continue
        bek = [glob(p, yan == "sol") for p in b["pts"]]
        if len(bek) != len(s["pts"]):
            vt.append((s["kaynak"], float("inf"))); continue
        vt.append((s["kaynak"], max(math.dist(p, q) for p, q in zip(bek, s["pts"]))))
    ay = []
    SK = {s["kaynak"]: s for _, s in kol}
    for _, s in kol:
        if ":sag:" in s["kaynak"]:
            o = SK.get(s["kaynak"].replace(":sag:", ":sol:"))
            if o:
                ay.append((s["kaynak"], max(math.dist((-p[0], p[1], p[2]), q) for p, q in zip(s["pts"], o["pts"])) if len(o["pts"]) == len(s["pts"]) else float("inf")))
    sonuc["veri_turetme"] = dict(bolum=len(vt), en_buyuk_fark_mm=round(max([d for _, d in vt] or [0]), 4),
                                 asan=[k for k, d in vt if d > VERI_TOL])
    sonuc["ayna"] = dict(cift=len(ay), en_buyuk_fark_mm=round(max([d for _, d in ay] or [0]), 4), asan=[k for k, d in ay if d > VERI_TOL],
                         sag_yalniz=[s["kaynak"] for _, s in kol if ":sag:" in s["kaynak"] and s["kaynak"].replace(":sag:", ":sol:") not in SK
                                     and s.get("tur") not in ("poz_a", "poz_b")],
                         yalniz_sag_bilerek=[s["kaynak"] for _, s in kol if s.get("tur") in ("poz_a", "poz_b")])
    # 4) adım bağı: her bölüm tam bir alt adımda, şemanın adımı = grubun adımı
    gr = {}
    for a in V["adimlar"]:
        for n, g in enumerate(a.get("sira_grup") or []):
            for i in g.get("sema") or []:
                gr.setdefault(i, []).append((a["i"], n))
    bag_hata = []
    for i, s in kol:
        y = gr.get(i, [])
        if len(y) != 1 or y[0][0] != s["a"]:
            bag_hata.append("%s: %s" % (s["kaynak"], y))
    beklenen = {"%s:%s" % (yan, b["k"]) for b in B for yan in ("sag", "sol")
                if yan == "sag" or not (b["k"].startswith("s1_") and b["k"] not in ("s1_lop", "s1_cikis"))}
    eksik = sorted(beklenen - {s["kaynak"].split(":", 1)[1] for _, s in kol})
    sonuc["adim_bagi"] = dict(bolum=len(kol), beklenen=len(beklenen), eksik=eksik, hatali=bag_hata,
                              tablo=[dict(sema=t["sema"], anahtar=t["anahtar"], adres=t["adres"], grup=t["grup"]) for t in K.get("bolum", [])])
    # 5) uç parçada, 6) katı içinden geçme (GLB; CAD duruşu: uç duruş şemaları hariç, bkz. not)
    import rehber_gorunum as RG
    M = RG.Mesh(V)
    PP = {p["id"]: p for p in V["parcalar"]}
    yan_mod = lambda pid, yan: (PP[pid]["modul"].endswith("_" + yan) or (PP[pid]["modul"] == "kabuk" and   # noqa: E731
                                (" " + ("sağ" if yan == "sag" else "sol")) in PP[pid]["ad"]) or PP[pid]["modul"] in ("iskelet",))
    tri = {pid: M.P[pid]["v"][M.P[pid]["f"]] for pid in M.P}
    uc_tablo, katı, tek_yon = [], [], []
    for i, s in kol:
        yan, k = s["kaynak"].split(":")[1:]
        b = BK[k]
        poz = k.startswith("s1_") and k not in ("s1_lop", "s1_cikis")
        for j, (ucn, nok) in enumerate(((0, s["pts"][0]), (1, s["pts"][-1]))):
            ad_bek = b["uc"][ucn]
            q = np.array(nok, float)
            if poz and ucn == 0:                                     # tambur bağı tamburla döner: CAD duruşundaki tambura geri çevir
                q = np.array(_geri_dondur(q, float(k[3:])), float)
            aday = [pid for pid, m in M.P.items() if PP[pid]["ad"].startswith(ad_bek) and yan_mod(pid, yan)]
            if not aday:
                aday = [pid for pid, m in M.P.items() if PP[pid]["ad"].startswith(ad_bek)]
            dd = [(float(_nokta_ucgen(q[None], tri[pid])[0]), pid) for pid in aday]
            d, pid = min(dd) if dd else (float("inf"), None)
            tip = UC_TIP.get((k, ucn), "yuzey")
            if tip == "icinde":
                m = M.P[pid] if pid else None
                ok = bool(m is not None and np.all(q >= m["bmin"] - 0.01) and np.all(q <= m["bmax"] + 0.01))
            else:
                ok = bool(d <= UC_TOL or (pid is not None and M.icinde(q[None], pid)[0]))
            # en yakın 3 parça (bilgi)
            yak = []
            for p2, m in M.P.items():
                if np.all(q >= m["bmin"] - 15) and np.all(q <= m["bmax"] + 15):
                    yak.append((float(_nokta_ucgen(q[None], tri[p2])[0]), p2))
            yak.sort()
            uc_tablo.append(dict(sema=i, bolum=s["kaynak"], uc="bas" if ucn == 0 else "son", nokta=[round(float(c), 2) for c in q], beklenen=ad_bek,
                                 tip=tip, parca=pid, uzaklik_mm=round(d, 2), gecti=ok,
                                 en_yakin=[dict(id=p2, ad=PP[p2]["ad"], mm=round(x, 2)) for x, p2 in yak[:3]]))
        if poz:
            continue
        # katı: merkez çizgisi noktaları, bütün parçalar (Referans hariç), eğik ışın paritesi
        Q = _ornekle(s["pts"])
        lo, hi = Q.min(0) - 2, Q.max(0) + 2
        for pid, m in M.P.items():
            if PP[pid]["tur"] == "Referans" or np.any(m["bmax"] < lo) or np.any(m["bmin"] > hi):
                continue
            sec = np.all(Q >= m["bmin"] - 0.5, 1) & np.all(Q <= m["bmax"] + 0.5, 1)
            if not sec.any():
                continue
            Qs = Q[sec]
            ic1 = np.concatenate([M.icinde(Qs[c:c + 40], pid) for c in range(0, len(Qs), 40)])
            if not ic1.any():
                continue
            ic = ic1 & _icinde3(Qs, tri[pid])                       # tek yönlü parite yalnız ön eleme; karar üç yönün ortaklığı
            if not ic.any():
                tek_yon.append(dict(bolum=s["kaynak"], parca=pid, ad=PP[pid]["ad"], tek_yon_nokta=int(ic1.sum()),
                                    acik_kenar=_acik_kenar(M.P[pid]["f"]), en_yakin_yuzey_mm=round(float(_nokta_ucgen(Qs[ic1], tri[pid]).min()), 2)))
                continue
            der = _nokta_ucgen(Qs[ic], tri[pid])
            dmax = float(der.max())
            ist = next((v for (kb, desen), v in KATI_ISTISNA.items() if kb == k and desen in PP[pid]["ad"]), None)
            katı.append(dict(sema=i, bolum=s["kaynak"], parca=pid, ad=PP[pid]["ad"], a=PP[pid]["a"], nokta=int(ic.sum()), derinlik_mm=round(dmax, 3),
                             asan=bool(dmax > ICINDE_ESIK), istisna=ist))
    # en küçük açıklık (bilgi): merkez çizgisinden en yakın parçaya - demet yarı kalınlığı
    acik = []
    for i, s in kol:
        yan, k = s["kaynak"].split(":")[1:]
        if k.startswith("s1_") and k not in ("s1_lop", "s1_cikis"):
            continue
        Q = _ornekle(s["pts"], 2.0)
        lo, hi = Q.min(0) - 8, Q.max(0) + 8
        best = (float("inf"), None)
        for pid, m in M.P.items():
            if PP[pid]["tur"] == "Referans" or np.any(m["bmax"] < lo) or np.any(m["bmin"] > hi):
                continue
            sec = np.all(Q >= m["bmin"] - 8, 1) & np.all(Q <= m["bmax"] + 8, 1)
            if not sec.any():
                continue
            d = float(_nokta_ucgen(Q[sec], tri[pid]).min())
            if d < best[0]:
                best = (d, pid)
        acik.append(dict(bolum=s["kaynak"], en_yakin=best[1] and PP[best[1]]["ad"], merkez_mm=round(best[0], 2),
                         aciklik_mm=round(best[0] - _demet_yari(BK[k]["serit"]), 2)))
    sonuc["uc"] = dict(uc=len(uc_tablo), parcada_degil=[u for u in uc_tablo if not u["gecti"]], tablo=uc_tablo)
    sonuc["kati"] = dict(tek_yon_yanilgi=tek_yon, yontem="merkez çizgisi %g mm aralıkla, GLB ağı, eğik ışın paritesi üç yönde (üçünde de tek: içeride; açık kenarlı ağda tek yön yanılıyor); derinlik = içerdeki noktadan ağ yüzeyine en kısa "
                                "uzaklık; eşik %g mm (ağ üçgenleme payı). S1 uç duruş şemaları hariç (parçalar CAD duruşunda; uç duruşlar "
                                "dirsek_montaj.py s1_lop'ta FreeCAD'le ölçülü)" % (ORNEK, ICINDE_ESIK),
                         temas=len(katı), asan=[x for x in katı if x["asan"] and not x["istisna"]],
                         istisnali=[x for x in katı if x["asan"] and x["istisna"]], liste=katı, aciklik=acik)
    # 7) sıra: kablonun döşendiği alt adımda noktalara el ulaşıyor mu; o anda yerinde duran parça yolu kapatıyor mu; sonra gelen
    #    parça yolu kesiyor mu (katı tablosundan, parçanın adımı / grubu ile)
    sira = []
    if el:
        import rehber_sira as RS
        if D is None:
            D = RS.Denetim(V, os.path.join(VERI_DIR, "robot.glb"))
        for i, s in kol:
            yan, k = s["kaynak"].split(":")[1:]
            a = s["a"]
            n = gr.get(i, [(a, None)])[0][1]
            if n is None:
                continue
            dur = D.durumlar(a)
            izin = dur[n][3]
            E = D.G.el(izin, ("kol", a, n), D.el_mm)
            dirs = []
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        if dx or dy or dz:
                            v = np.array([dx, dy, dz], float); dirs.append(v / np.linalg.norm(v))
            # yalnız köşeler (sabit yollar) ya da elastikanın iki ucu + ortası
            kose = list(range(len(s["pts"])))
            if len(s["pts"]) > 12:
                kose = [0, len(s["pts"]) // 2, len(s["pts"]) - 1]
            for j in kose:
                if k in EL_YOK:
                    sira.append(dict(sema=i, bolum=s["kaynak"], adres="%d.%d" % (a, n + 1), nokta=j, el=None, neden=EL_YOK[k])); continue
                if (k, j) in EL_YOK_NOKTA:
                    sira.append(dict(sema=i, bolum=s["kaynak"], adres="%d.%d" % (a, n + 1), nokta=j, el=None, neden=EL_YOK_NOKTA[(k, j)])); continue
                q = np.array(s["pts"][j], float)
                lo, hi = q - EL_ULASIM - 1, q + EL_ULASIM + 1
                idx = D.S.sec(lo, hi, izin)
                O = np.array([q + d * 0.5 for d in dirs])
                th, _ = D.S.isin(O, np.array(dirs), EL_ULASIM, idx)
                en = None
                for d, tv in zip(dirs, th):
                    tm = min(float(tv), EL_ULASIM)
                    for tt in np.arange(0.5, tm + 1e-9, 1.5):
                        if D.G.elde(E, q + d * tt):
                            if en is None or tt < en[0]:
                                en = (round(float(tt), 1), [round(float(c), 2) for c in d])
                            break
                sira.append(dict(sema=i, bolum=s["kaynak"], adres="%d.%d" % (a, n + 1), nokta=j, el=en is not None,
                                 mm=en[0] if en else None, yon=en[1] if en else None))
    # yerinde / sonra: katı tablosundaki parça kablonun alt adımında yerinde mi
    import rehber_gorunum as RG2
    A_ = V["adimlar"]
    GH = {a["i"]: RG2.grup_harita(a) for a in A_}

    def yerinde(pid, s, j):
        return RG2.durum(PP[pid], s, j, A_, GH) in ("onceki", "simdi", "alt", "hedef")
    for x in katı:
        s_ = S[x["sema"]]
        n = gr.get(x["sema"], [(s_["a"], None)])[0][1]
        x["kablo_adres"] = "%d.%d" % (s_["a"], (n or 0) + 1)
        x["parca_yerinde"] = bool(n is not None and yerinde(x["parca"], s_["a"], n + 1))
    sonuc["sira"] = dict(yontem="kablonun döşendiği alt adımda yerinde olan parçalarla (rehber_sira.Denetim.durumlar) el bölgesi (%g mm "
                                "zarf, 3 mm voksel); köşe noktasından 26 yönde engelsiz ışınla %g mm içinde el bölgesine ulaşan nokta 'ulaşılır'"
                                % (D.el_mm if D else 20.0, EL_ULASIM) if el else "atlandı",
                         nokta=sum(1 for x in sira if x["el"] is not None), ulasilamaz=[x for x in sira if x["el"] is False],
                         el_yok=[x for x in sira if x["el"] is None], liste=sira,
                         yolu_kapatan=[x for x in katı if x["asan"] and not x["istisna"] and x["parca_yerinde"]],
                         sonra_kesen=[x for x in katı if x["asan"] and not x["istisna"] and not x["parca_yerinde"]])
    # 8) metin ↔ kaynak ve pin / kanal / konnektör eşlemesi
    sonuc["metin"] = metin_denetle(V)
    hata += bag_hata + ["eksik bölüm %s" % e for e in eksik]
    gecti = (kk["gecti"] and not sonuc["veri_turetme"]["asan"] and not sonuc["ayna"]["asan"] and not sonuc["ayna"]["sag_yalniz"] and not hata
             and not sonuc["uc"]["parcada_degil"] and not sonuc["kati"]["asan"] and not sonuc["sira"]["ulasilamaz"]
             and not sonuc["metin"]["eksik"] and not sonuc["metin"]["birim_hata"] and not sonuc["metin"]["etiket_hata"]
             and not sonuc["metin"]["pin"])
    sonuc.update(hata=hata, gecti=bool(gecti), bolum=len(kol), sure_s=round(time.time() - t0, 1))
    if not sessiz:
        ozet_yaz(sonuc)
    return sonuc


# metinde kaynaktan gelmesi gereken sayılar (rehber_metin.py; virgüllü ondalık): (adım, sayı metni, birim, kaynak). F10f düzeltme 1
# (kontrol F10f-ç1): birim de sınanır. Birim "mm" -> metinde "<sayı> mm", "°" -> "<sayı>°"; "ψ" -> açı, ψ tanımıyla (ψ önekli, birim
# yazılmaz). Sayı metinde başka bir birimle (mm / ° / cm / derece) geçerse "birim_hata". F10f'te G4 uç duruş koşuları (kablo_yolu.s1_poz
# a_i / a_o: derece) "mm" yazılmıştı; sayı denetimi birime bakmadığı için yakalamamıştı.
# F10f düzeltme 2 (kontrol F10f-kontrol-2 T9): "m" ve "rad" da birim sayılır; doğru geçişin yanında "125,3 m" gibi yanlış birimli
# fazladan bir geçiş birim_hata verir (birimsiz geçiş aralık yazımında meşru olduğu için hata sayılmaz). T4: etiketli sayılarda (G4
# iç / dış koşu) sayıdan önceki en yakın etiket beklenen etiket olmalı; iç ↔ dış değer takası "etiket_hata" verir.
BIRIM_DESEN = r"(\s?mm\b|°|\s?cm\b|\s?derece\b|\s?rad\b|\s?m\b)"
ETIKETLER = ("iç koşu", "dış koşu")


def metin_sayilar():
    KK = A.KOL_KABLO
    S1 = KK["s1"]
    f = lambda x: ("%g" % x).replace(".", ",").replace("-", "−")    # noqa: E731
    d0, d1 = A.DIRSEK["aralik"]; s20, s21 = A.OMUZ["yana_aralik"]; p0, p1 = A.OMUZ["one_arka_aralik"]
    oc = KK["onkol_centik"]
    DA = json.load(open(os.path.join(FC, "dirsek", "dirsek-analiz.json"), encoding="utf-8"))["kablo"]
    uz = {u["servo"].split()[0]: u["uzatma_mm"] for u in DA["s1_boy"]["uzatma"]}
    artan = {b["ad"].split()[0]: b.get("artan_mm") for b in DA["boy"]}
    sp = turet()[1]["s1_poz"]
    poz = []
    for k in ("-45", "+135"):                                        # uç duruş yakın kareleri: bağ ψ, iç / dış koşu yayı (0,1°), U ψ (tam derece)
        x = sp[k]
        poz += [("G4", "ψ %s" % f(round(x["psi_bag"])), "ψ", "kablo_yolu.s1_poz S1 %s psi_bag" % k),
                ("G4", f(round(x["a_i"], 1)), "°", "kablo_yolu.s1_poz S1 %s a_i (iç koşu yayı, derece: psi_U − tambur bağı ψ)" % k,
                 "iç koşu"),
                ("G4", f(round(x["a_o"], 1)), "°", "kablo_yolu.s1_poz S1 %s a_o (dış koşu yayı, derece: psi_U + delta − duvar bağı ψ)" % k,
                 "dış koşu"),
                ("G4", "U ψ ≈ %s" % f(round(x["psi_U"])), "ψ", "kablo_yolu.s1_poz S1 %s psi_U" % k)]
    return poz + [
        ("H1", f(uz["dirsek"]), "mm", "dirsek-analiz.json kablo s1_boy uzatma (dirsek, bilek)"),
        ("G2", f(uz["S2"]), "mm", "dirsek-analiz.json kablo s1_boy uzatma (S2)"),
        ("H1", f(artan["bilek"]), "mm", "dirsek-analiz.json kablo boy bilek artan_mm"),
        ("H1", f(artan["dirsek"]), "mm", "dirsek-analiz.json kablo boy dirsek artan_mm"),
        ("H0a", "%s × %s" % (f(round(oc["x"][1] - oc["x"][0])), f(round(oc["dz"][1] - oc["dz"][0]))), "mm",
         "KOL_KABLO onkol_centik (x genişliği, dz derinliği; tam mm'ye yuvarlı)"),
        ("H0c", "L %s" % f(KK["dirsek_lop"]["L"]), "mm", "KOL_KABLO dirsek_lop L"),
        ("H0c", "%s…%s" % (f(d0), f(d1)), "°", "arayuz DIRSEK aralik"),
        ("H1", "y %s" % f(KK["birlesim"][1]), "mm", "KOL_KABLO birlesim y"),
        ("H1", f(KK["jr_eslesik"][2]), "mm", "KOL_KABLO jr_eslesik boy"),
        ("H1", f(KK["bilek_ek"]["makaron"][1]), "mm", "KOL_KABLO bilek_ek makaron"),
        ("G3", "L %s" % f(KK["s2_lop"]["L"]), "mm", "KOL_KABLO s2_lop L"),
        ("G3", "ψ %s" % f(S1["tambur"]["bag_psi"]), "ψ", "KOL_KABLO s1 tambur bag_psi"),
        ("G3", "%s…%s" % (f(s20), f(s21)), "°", "arayuz OMUZ yana_aralik"),
        ("G4", "L %s" % f(S1["L"]), "mm", "KOL_KABLO s1 L"),
        ("G4", "%s…%s" % (f(S1["L_tol"][0]), f(S1["L_tol"][1])), "mm", "KOL_KABLO s1 L_tol (lop boyu toleransı, tek yönlü)"),
        ("G4", "ψ %s" % f(S1["cikis"]["psi"]), "ψ", "KOL_KABLO s1 cikis psi"),
        ("G4", "ψ %s / %s" % (f(S1["duvar"]["ip_psi"][0]), f(S1["duvar"]["ip_psi"][1])), "ψ", "KOL_KABLO s1 duvar ip_psi"),
        ("G4", "%s…%s" % (f(p0), f(p1)), "°", "arayuz OMUZ one_arka_aralik"),
        ("G4", "S1 ≥ %s° iken S2 ≤ %s" % (f(S1["s2_s1_kosul"]["s1_min"]), f(S1["s2_s1_kosul"]["s2_max"])), "°", "KOL_KABLO s1 s2_s1_kosul"),
        ("F4", "ψ %s" % f(S1["cikis"]["psi"]), "ψ", "KOL_KABLO s1 cikis psi"),
        ("F4", "%s × %s" % (f(S1["cikis"]["yarik"][0]), f(S1["cikis"]["yarik"][1])), "mm", "KOL_KABLO s1 cikis yarik"),
    ]


def birim_bul(metin_, sayi):
    """Sayının metindeki her geçişi ve ardından gelen birim ("" = birim yok)."""
    out = []
    for m in re.finditer(r"(?<![\d,.])" + re.escape(sayi) + r"(?![\d])(?!,\d)" + BIRIM_DESEN + "?", metin_):
        b = (m.group(1) or "").strip()
        out.append("°" if b in ("°", "derece") else b)
    return out


PIN_DESEN = re.compile(r"\b(pin|PWM\s*\d|kanal\s*\d|CH\s*\d|GPIO\s*\d|D\d{1,2}\b|J\d{1,2}\b|konnekt[öo]r\s*\d|soket\s*\d|header)", re.I)


def metin_denetle(V):
    """Kol adımlarının (kolk grubu olan adımlar) metninde kaynak sayıları var mı; pin / kanal / konnektör eşlemesi yok mu."""
    kod_i = {a["kod"]: a for a in V["adimlar"]}
    kodlar = sorted(set(metin_kolk()))

    def metin(a):
        t = [a.get("is_", ""), a.get("baslik", ""), " ".join(a.get("kontrol") or []), " ".join(a.get("kablo") or [])]
        for g in a.get("sira_grup") or []:
            t += [g.get("ad", ""), g.get("is_", "")]
        return "\n".join(t)
    eksik, var, birim_hata, etiket_hata = [], [], [], []
    for t in metin_sayilar():
        kod, s, birim, kay = t[:4]
        etk = t[4] if len(t) > 4 else None
        a = kod_i.get(kod)
        bl = birim_bul(metin(a), s) if a is not None else []
        bek = "" if birim == "ψ" else birim
        yanlis = sorted({b for b in bl if b and b != bek})
        if yanlis:
            birim_hata.append(dict(adim=kod, sayi=s, birim=birim, metinde=yanlis, kaynak=kay))
        if etk and a is not None:                                    # T4: her geçişten önceki en yakın etiket beklenen mi
            mt = metin(a)
            for m in re.finditer(r"(?<![\d,.])" + re.escape(s) + r"(?![\d])(?!,\d)", mt):
                onc = [(mt.rfind(e, 0, m.start()), e) for e in ETIKETLER]
                onc = max(onc)
                if onc[0] < 0 or onc[1] != etk:
                    etiket_hata.append(dict(adim=kod, sayi=s, beklenen=etk, metinde=onc[1] if onc[0] >= 0 else None, kaynak=kay))
        if bek not in bl:
            eksik.append(dict(adim=kod, sayi=s, birim=birim, kaynak=kay, metinde=sorted(set(bl))))
        else:
            var.append(dict(adim=kod, sayi=s, birim=birim, kaynak=kay))
    pin = []
    for kod in kodlar:
        a = kod_i.get(kod)
        if not a:
            continue
        for m in PIN_DESEN.finditer(metin(a)):
            pin.append(dict(adim=kod, eslesen=m.group(0)))
    for s in V["semalar"]:
        if str(s.get("kaynak", "")).startswith(KAYNAK + ":"):
            for m in PIN_DESEN.finditer(s["ad"]):
                pin.append(dict(sema=s["kaynak"], eslesen=m.group(0)))
    return dict(sayi=len(var) + len(eksik), bulunan=var, eksik=eksik, birim_hata=birim_hata, etiket_hata=etiket_hata, pin=pin,
                desen=PIN_DESEN.pattern, birim_desen=BIRIM_DESEN, etiketler=list(ETIKETLER))


def ozet_yaz(r):
    print("kol kablo denetimi: bolum %d; kaynak fark %.4f mm (<= %g) %s; veri <-> turetme %.4f mm, asan %d; ayna %.4f, asan %d; "
          "adim bagi eksik %d, hatali %d" % (
              r["bolum"], r["kaynak"]["en_buyuk_fark_mm"], KAYNAK_TOL, "GECTI" if r["kaynak"]["gecti"] else "KALDI",
              r["veri_turetme"]["en_buyuk_fark_mm"], len(r["veri_turetme"]["asan"]), r["ayna"]["en_buyuk_fark_mm"], len(r["ayna"]["asan"]),
              len(r["adim_bagi"]["eksik"]), len(r["adim_bagi"]["hatali"])))
    print("  uc: %d, parcada degil %d; kati: temas %d, esik ustu istisnasiz %d, istisnali %d; sira: nokta %d, ulasilamaz %d, el yok (gerekceli) %d, "
          "yolu kapatan %d, sonra kesen %d; metin sayi %d, eksik %d, birim hata %d, etiket hata %d, pin %d -> %s (%.0f s)" % (
              r["uc"]["uc"], len(r["uc"]["parcada_degil"]), r["kati"]["temas"], len(r["kati"]["asan"]), len(r["kati"]["istisnali"]),
              r["sira"]["nokta"], len(r["sira"]["ulasilamaz"]), len(r["sira"]["el_yok"]), len(r["sira"]["yolu_kapatan"]),
              len(r["sira"]["sonra_kesen"]), r["metin"]["sayi"], len(r["metin"]["eksik"]), len(r["metin"]["birim_hata"]), len(r["metin"]["etiket_hata"]),
              len(r["metin"]["pin"]),
              "GECTI" if r["gecti"] else "KALDI", r["sure_s"]))
    for x in r["uc"]["parcada_degil"][:8]:
        print("  UC", x["bolum"], x["uc"], x["beklenen"], x["uzaklik_mm"], [(e["ad"], e["mm"]) for e in x["en_yakin"]])
    for x in r["kati"]["asan"][:12]:
        print("  KATI", x["bolum"], x["ad"], x["parca"], "derinlik", x["derinlik_mm"], "nokta", x["nokta"])
    for x in r["sira"]["ulasilamaz"][:8]:
        print("  ULASILAMAZ", x["bolum"], x["adres"], x["nokta"])
    for x in r["metin"]["eksik"][:8]:
        print("  METIN EKSIK", x)
    for x in r["metin"]["pin"][:8]:
        print("  PIN", x)
    for h in r["hata"][:8]:
        print("  HATA", h)


def yaz(V):
    import rehber_gorunum as RG                                     # aynı biçim: rehber-veri.json + rehber-veri.js
    RG.yaz(V)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--yazma", action="store_true", help="veriyi yazma (rehber_gorunum ile aynı anlam)")
    ap.add_argument("--json", default="", help="denetim sonucunu bu dosyaya yaz")
    ap.add_argument("--denetim-yok", action="store_true")
    ap.add_argument("--el-yok", action="store_true", help="el bölgesi (sıra) ölçümünü atla")
    g = ap.parse_args()
    V = isle(yazma=not g.yazma)
    if not g.denetim_yok:
        r = denetle(V, el=not g.el_yok)
        if g.json:
            json.dump(r, open(g.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        sys.exit(0 if r["gecti"] else 2)
