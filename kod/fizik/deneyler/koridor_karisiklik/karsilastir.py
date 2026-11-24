"""v1 / v2 / v2-360 / v3 / v3-360 karşılaştırması -> sonuc_v3/karsilastirma.json + gorsel_v3/karsilastirma_*.png.

    py -3 kod\\fizik\\deneyler\\koridor_karisiklik\\karsilastir.py      (önce analiz.py --etiket v2, v2_360, v3, v3_360)

Sürümler: v1 = c34618b konumlayıcısı (ham/, sonuc/; commit'li, yeniden üretilmez), v2 = düzeltilmiş konumlayıcı,
v3 = v2 + U dönüşü düzeltmesi (çapraz enjeksiyon yok, odometri noktası çeker dingilde); _360 = kör sektör yok.
sonuc_v2/karsilastirma.json v2'nin (v1 / v2 / v2-360) commit'li karşılaştırmasıdır, dokunulmaz. Bütün sayılar sonuç /
ham dosyalarından okunur. İki hata türü ayrı sayılır (olaylar): yanlış koridora kesin karar ve doğru koridorda kesin
ama > 0,5 m yanlış yer.
"""

import glob
import json
import math
import os
import sys

import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)
import analiz as AN  # noqa: E402

K = AN.K
KS = AN.KS
SURUMLER = ["v1", "v2", "v2_360", "v3", "v3_360"]
CIZ = ["v1", "v2", "v3", "v3_360"]              # görsellerdeki sürümler (v2-360 ek tabloda)
SURUM_AD = {"v1": "v1 (düzeltme öncesi)", "v2": "v2 (düzeltilmiş)", "v2_360": "v2-360 (kör sektör yok)",
            "v3": "v3 (U dönüşü düzeltmesi)", "v3_360": "v3-360 (kör sektör yok)"}
SURUM_RENK = {"v1": AN.SERI[0], "v2": AN.SERI[1], "v2_360": AN.SERI[4], "v3": AN.SERI[2], "v3_360": AN.SERI[3]}


def dizin(tur, s):
    return os.path.join(BURASI, tur if s == "v1" else tur + "_" + s)


def ozet(s):
    with open(os.path.join(dizin("sonuc", s), "ozet.json"), encoding="utf-8") as f:
        return json.load(f)


def ham(s, bolum):
    out = []
    for f in sorted(glob.glob(os.path.join(dizin("ham", s), bolum, "*.json"))):
        with open(f, encoding="utf-8") as g:
            r = json.load(g)
        if "hata" not in r:
            out.append(r)
    return out


def ist(v):
    v = [x for x in v if x is not None]
    if not v:
        return None
    return dict(n=len(v), ort=float(np.mean(v)), med=float(np.median(v)), min=float(np.min(v)), max=float(np.max(v)))


def a_bolum(s, oz):
    A = oz["A"]
    hata_buyuk = {k: 0 for k in K}
    for r in ham(s, "A"):
        if r["gorev"]["tur"] != "rastgele":
            continue
        for p in r["pozlar"]:
            if p["dogru_poz_hata_m"] > 0.5:
                hata_buyuk[r["gorev"]["kor"]] += 1
    yog = A["yogun"]
    return dict(toplam=A["toplam"], oranlar=A["oranlar"], ikili=A["ikili"], yanlislar=A["yanlislar"],
                yogun={k: {x: yog[k][x] for x in ("n", "dogru", "kararsiz", "yanlis")} for k in yog},
                konum_hata_05=hata_buyuk, sure_ort=A["sure_ort"])


def hareket(s, oz, bolum):
    E = oz.get(bolum)
    if not E:
        return None
    runs = ham(s, bolum)
    out = dict(n=E["n"], yanlislar=E["yanlislar"], konum_yanlislar=E["konum_yanlislar"], koridor={})
    for k in K:
        v = E["koridor"].get(k)
        if not v:
            continue
        T = E["adim_tablo"][k]
        n_adim = sum(T.values())
        rs = [r for r in runs if r["gorev"]["kor"] == k]
        # toplam (ileri-geri + yan) konum hatası, konum kararından sonra
        xy = []
        for r in rs:
            i0, il, yn = AN.konum_karari(r)
            if i0 is not None:
                xy.extend(np.hypot(il, yn).tolist())
        out["koridor"][k] = dict(
            n=v["n"], yanlis_kosu=v["yanlis_kosu"], yanlis_adim=v["yanlis_adim"], kararsiz_adim=T["kararsiz"],
            adim=n_adim, karar_med=v["karar_med"], karar_min=v["karar_min"], karar_max=v["karar_max"],
            karar_yok=v["karar_yok"], konum_karar_med=v["konum_karar_med"], konum_karar_max=v["konum_karar_max"],
            konum_karar_yok=v["konum_karar_yok"], konum_kararsiz_oran=v["konum_kararsiz_oran"],
            kk_ileri_ort=v["kk_ileri_ort"], kk_ileri_max=v["kk_ileri_max"], kk_yan_ort=v["kk_yan_ort"],
            kk_yan_max=v["kk_yan_max"], kk_xy_max=(max(xy) if xy else None),
            son_dogru=v["son_dogru"], son_kararsiz=v["son_kararsiz"], son_yanlis=v.get("son_yanlis", 0),
            konum_yanlis_adim=v["konum_yanlis_adim"], temas=v["temas"], bitmedi=v["bitmedi"])
    if "benzer_cift" in E:
        bc = {}
        for kor in ("koridor_5", "koridor_6"):
            for b in ("bas", "son", "orta"):
                xs = [x for x in E["benzer_cift"] if x["kor"] == kor and x["baslangic"] == b]
                if not xs:
                    continue
                bc["%s_%s" % (kor, b)] = dict(
                    n=len(xs), karar=ist([x["karar_yol"] for x in xs]), fark_60=ist([x["fark_60_yol"] for x in xs]),
                    fark_500=ist([x["fark_menzil_yol"] for x in xs]),
                    once_karar=sum(1 for x in xs if x["karar_yol"] is not None and x["fark_60_yol"] is not None
                                   and x["karar_yol"] < x["fark_60_yol"]),
                    yanlis_kosu=sum(1 for x in xs if x["yanlis_cift"] > 0), yanlis_adim=sum(x["yanlis_cift"] for x in xs),
                    p_es_max=max(x["p_es_en_cok"] for x in xs), karar_yok=sum(1 for x in xs if x["karar_yol"] is None))
        out["benzer_cift"] = bc
    if bolum == "D":
        out.update({x: E[x] for x in ("yanlis_koridor_adim", "konum_kararsiz_adim", "adim_top", "en_kucuk_p_dogru")})
    out["islenen"] = E.get("islenen")
    out["sure_top_s"] = E["sure_top_s"]
    out["son_tablo"] = E["son_tablo"]
    return out


ESIK_KONUM_YANLIS = 0.5   # m; ortak.ESIK_KONUM_YANLIS ile aynı (ortak.py'yi burada içe aktarmamak için)


def _aci(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def olaylar(s, oz):
    """Kendinden emin yanlış olan her B / C koşusu (yanlış koridor ya da doğru koridorda > 0,5 m yanlış yer), ham adımlardan.

    Alanlar gözlemdir, yorum değil: ilk kötü adımda gerçek / tahmin yönü farkı, ilk kötü adım U dönüşü sırasında mı,
    sonrasında mı (kaç m sonra), insan var mı, benzer çiftte fark konumlayıcının ışınlarında görünmeden mi. `neden` bu gözlemlerden kurulan
    kısa etikettir."""
    out = []
    u_kosu = {"B": 0, "C": 0}
    for bolum in ("B", "C"):
        fark = {x["id"]: x for x in oz[bolum].get("benzer_cift", [])}
        for r in ham(s, bolum):
            a = r["adimlar"]
            kor = r["gorev"]["kor"]
            n = len(a["i"])
            kk = [i for i in range(n) if not a["kararsiz"][i] and a["en"][i] != kor]
            kp = [i for i in range(n) if a["en"][i] == kor and not a["kararsiz"][i] and not a["konum_kararsiz"][i]
                  and math.hypot(a["ileri"][i], a["yan"][i]) > ESIK_KONUM_YANLIS]
            yol = a["yol"]
            # U dönüşleri: yer gerçeğinde yol başına dönüşün 2 rad/m'yi aştığı ardışık adımlar, toplam > 2,5 rad
            dl = []
            m = 0
            while m < n - 1:
                if abs(_aci(a["gth"][m + 1] - a["gth"][m])) > max(0.002, 2.0 * (yol[m + 1] - yol[m])):
                    b0, top = m, 0.0
                    while m < n - 1 and abs(_aci(a["gth"][m + 1] - a["gth"][m])) > max(0.002, 2.0 * (yol[m + 1] - yol[m])):
                        top += abs(_aci(a["gth"][m + 1] - a["gth"][m]))
                        m += 1
                    if top > 2.5:
                        dl.append((b0, m))
                m += 1
            if dl:
                u_kosu[bolum] += 1
            if not kk and not kp:
                continue
            i0 = min(kk + kp)
            u_once = [(b0, b1) for b0, b1 in dl if b0 <= i0]
            if u_once and i0 <= u_once[-1][1]:
                u_durum, u_m = "sirasinda", 0.0
            elif u_once:
                u_durum, u_m = "sonra", round(yol[i0] - yol[u_once[-1][1]], 2)
            else:
                u_durum, u_m = "yok", None
            # yön karşılaştırması yalnız aynı harita çerçevesinde anlamlı: doğru koridor ya da benzer çift (K5 / K6 aynı çerçeve)
            ayni_cerceve = a["en"][i0] == kor or {a["en"][i0], kor} <= {"koridor_5", "koridor_6"}
            dth = abs(_aci(a["th"][i0] - a["gth"][i0])) if ayni_cerceve else None
            ters = dth is not None and dth > 2.5
            f = fark.get(r["gorev"]["id"])
            f60 = f["fark_60_yol"] if f else None
            haritalar = sorted({a["en"][i] for i in kk})
            if ters and u_durum == "sirasinda":
                neden = "U dönüşü sırasında poz 180° ters döndü (koridorun uçtan uca eşi)"
            elif ters and u_durum == "sonra" and u_m <= 3.0:
                neden = "U dönüşünden %s m sonra poz 180° ters (koridorun uçtan uca eşi)" % ("%.1f" % u_m).replace(".", ",")
            elif ters:
                neden = "poz 180° ters (koridorun uçtan uca eşi)"
            elif kk and set(haritalar) <= {"koridor_5", "koridor_6"} and kor in ("koridor_5", "koridor_6") \
                    and (f60 is None or yol[min(kk)] < f60):
                neden = "benzer çift: fark ışınlarda görünmeden eşine kesin"
            elif kk:
                neden = "yanlış koridora kesin"
            else:
                neden = "doğru koridorda yanlış yere kesin"
            if r.get("insanlar"):
                neden += "; insanlar var"
            if kk and kp and min(kp) < min(kk):
                neden += "; yanlış koridor, yer kaymasından sonra"
            son_e = math.hypot(a["ileri"][-1], a["yan"][-1]) if a["en"][-1] == kor else None
            # ilk kötü adımda robota en yakın insan (yüzeye uzaklık, m) ve robotun önünde mi
            insan_m, insan_on = None, None
            for ins in r.get("insanlar") or []:
                dx, dy = ins["x"] - a["gx"][i0], ins["y"] - a["gy"][i0]
                d = math.hypot(dx, dy) - ins.get("r", 0.0)
                if insan_m is None or d < insan_m:
                    insan_m = d
                    insan_on = (dx * math.cos(a["gth"][i0]) + dy * math.sin(a["gth"][i0])) > 0
            # insan, sanılan pozdan bakınca sanılan haritada nereye düşüyor: benzer çiftin fark bölgesine mi
            # (K5 / K6 harita x 17,50-19,05: kapı kaydırma + yangın dolabı; ortak.FARKLAR)
            fark_insan = None
            if a["en"][i0] in ("koridor_5", "koridor_6"):
                for ins in r.get("insanlar") or []:
                    dx, dy = ins["x"] - a["gx"][i0], ins["y"] - a["gy"][i0]
                    c, sn = math.cos(-a["gth"][i0]), math.sin(-a["gth"][i0])
                    rx, ry = c * dx - sn * dy, sn * dx + c * dy
                    c, sn = math.cos(a["th"][i0]), math.sin(a["th"][i0])
                    ex, ey = a["x"][i0] + c * rx - sn * ry, a["y"][i0] + sn * rx + c * ry
                    if 17.5 <= ex <= 19.05 and (fark_insan is None or math.hypot(dx, dy) < fark_insan["menzil_m"]):
                        fark_insan = dict(menzil_m=round(math.hypot(dx, dy), 2), x=round(ex, 2), y=round(ey, 2))
            out.append(dict(
                id=r["gorev"]["id"], bolum=bolum, kor=kor, baslangic=r["gorev"]["baslangic"], tohum=r["gorev"]["tohum"],
                insan=len(r.get("insanlar") or []), koridor_adim=len(kk), konum_adim=len(kp),
                haritalar=haritalar, koridor_yol=([round(yol[min(kk)], 2), round(yol[max(kk)], 2)] if kk else None),
                konum_yol=([round(yol[min(kp)], 2), round(yol[max(kp)], 2)] if kp else None),
                ilk_yol=round(yol[i0], 2), ilk_hata_m=(round(math.hypot(a["x"][i0] - a["gx"][i0], a["y"][i0] - a["gy"][i0]), 2) if ayni_cerceve else None),
                ilk_yon_farki_derece=(round(math.degrees(dth), 1) if dth is not None else None), u_donusu=u_durum, u_sonrasi_yol_m=u_m,
                fark_60_yol=f60, son_harita=a["en"][-1], son_kararsiz=bool(a["kararsiz"][-1]),
                son_hata_m=(round(son_e, 2) if son_e is not None else None), neden=neden,
                insan_uzaklik_m=(round(insan_m, 2) if insan_m is not None else None), insan_onde=insan_on, insan_fark_bolgesinde=fark_insan))
    return out, u_kosu


def u_atlama(o):
    """U dönüşü sırasında ya da en çok 3 m sonra pozun 180° ters dönmesi."""
    return (o["u_donusu"] == "sirasinda" or (o["u_donusu"] == "sonra" and o["u_sonrasi_yol_m"] <= 3.0)) \
        and (o["ilk_yon_farki_derece"] or 0) > 150


def tani(s):
    yol = os.path.join(dizin("sonuc", s), "tani_ikiz.json")
    if not os.path.exists(yol):
        return None
    with open(yol, encoding="utf-8") as f:
        T = json.load(f)
    out = {}
    for kor in ("koridor_5", "koridor_6"):
        xs = T[kor]
        out[kor] = dict(n=len(xs), yanlis_tohum=sum(1 for x in xs if x["yanlis_kesin_adim"] > 0),
                        yanlis_adim=sum(x["yanlis_kesin_adim"] for x in xs), es_max=max(x["es_max_6m_once"] for x in xs),
                        ilk_kesin=ist([x["ilk_kesin_dogru_yol"] for x in xs]))
    xs = T["ikiz"]
    out["ikiz"] = dict(n=len(xs), kesin_tohum=sum(1 for x in xs if x["kesin_adim"] > 0),
                       kesin_adim=sum(x["kesin_adim"] for x in xs), adim=sum(x["adim"] for x in xs),
                       p_max=max(x["en_buyuk_p"] for x in xs))
    return out


def v1_esitlik(s="v2"):
    """v2 / v3 koşularının v1 ile aynı veri olduğunun kanıtı (kos.py'nin yazdığı alanlardan)."""
    yol_max, adim_esit, adim_n, tar_n, tar_fark = 0.0, 0, 0, 0, 0
    kaynak = {}
    for b in "BCD":
        for r in ham(s, b):
            kaynak[r.get("veri_kaynagi", "fizik")] = kaynak.get(r.get("veri_kaynagi", "fizik"), 0) + 1
            e = r.get("v1_esitlik")
            if not e:
                continue
            adim_n += 1
            adim_esit += e["adim_v1"] == e["adim_v2"]
            yol_max = max(yol_max, e["en_buyuk_yol_farki_m"])
            tar_n += e["saklanan_tarama"]
            tar_fark += sum(e["farkli_isin"])
    a_n = a_fark = 0
    for r in ham(s, "A"):
        for p in r["pozlar"]:
            if p.get("v1_farkli_isin") is not None:
                a_n += 1
                a_fark += p["v1_farkli_isin"]
    return dict(hareket_kosu=adim_n, adim_sayisi_esit=adim_esit, en_buyuk_yol_farki_m=yol_max,
                saklanan_tarama=tar_n, farkli_isin=tar_fark, a_poz=a_n, a_farkli_isin=a_fark, veri_kaynagi=kaynak)


def c_kosular(s):
    """C koşu koşu: iki hata türü (adım), karar yolu, sonda durum."""
    out = []
    for r in ham(s, "C"):
        o = r["olcutler"]
        out.append(dict(id=r["gorev"]["id"], kor=r["gorev"]["kor"], baslangic=r["gorev"]["baslangic"],
                        koridor_adim=o["yanlis_adim"], yer_adim=o["konum_yanlis_adim"], karar_yol=o["karar_yol_m"],
                        son_durum=o["son_durum"], son_p=o["son_p_dogru"]))
    return sorted(out, key=lambda x: x["id"])


# ------------------------------------------------------------------ görseller
def ciz_ozet(plt, S, yol):
    fig, axs = plt.subplots(3, 2, figsize=(13, 11.5))
    x = np.arange(len(K))
    w = 0.8 / len(CIZ)
    panel = [
        (axs[0, 0], "B: doğru karara kadar yol (m)\nçubuk ortanca, çizgi en az–en çok", "B", "karar"),
        (axs[0, 1], "B: koridorun neresinde olduğu kesinleşene kadar yol (m)\nçubuk ortanca, çizgi en çok",
         "B", "konum"),
        (axs[1, 0], "B + C: yanlış koridora kesin karar (adım)", "BC", "yanlis"),
        (axs[1, 1], "B + C: doğru koridorda kesin ama > 0,5 m yanlış yer (adım)", "BC", "yer"),
        (axs[2, 0], "D (başlangıç biliniyor): konum kararı sonrası ileri-geri hata (cm)\nçubuk ortalama, çizgi en çok",
         "D", "dhata"),
        (axs[2, 1], "B + C: U dönüşünde poz çevrilmesi (koşu; koridor başına 6 U dönüşlü koşu)", "BC", "ucev"),
    ]
    for ax, bas, bol, tur in panel:
        for j, s in enumerate(CIZ):
            xs = x + (j - (len(CIZ) - 1) / 2.0) * w
            if tur in ("yanlis", "yer", "ucev"):
                if tur == "yanlis":
                    v = [sum((S[s][b] or {}).get("koridor", {}).get(k, {}).get("yanlis_adim", 0) for b in "BC") for k in K]
                elif tur == "yer":
                    v = [sum(o["konum_adim"] for o in S[s]["olaylar"] if o["kor"] == k) for k in K]
                else:
                    v = [sum(1 for o in S[s]["olaylar"] if o["kor"] == k and u_atlama(o)) for k in K]
                ax.bar(xs, v, w * 0.92, color=SURUM_RENK[s], label=SURUM_AD[s])
                for xi, vi in zip(xs, v):
                    if vi:
                        ax.text(xi, vi, str(vi), ha="center", va="bottom", fontsize=7.5, color=AN.IKINCIL)
                continue
            E = S[s][bol]["koridor"]
            if tur == "karar":
                m = [E[k]["karar_med"] or 0 for k in K]
                lo = [E[k]["karar_min"] or 0 for k in K]
                hi = [E[k]["karar_max"] or 0 for k in K]
            elif tur == "konum":
                m = [E[k]["konum_karar_med"] or 0 for k in K]
                lo = m
                hi = [E[k]["konum_karar_max"] or 0 for k in K]
            else:
                m = [100 * (E[k]["kk_ileri_ort"] or 0) for k in K]
                lo = m
                hi = [100 * (E[k]["kk_ileri_max"] or 0) for k in K]
            ax.bar(xs, m, w * 0.92, color=SURUM_RENK[s], label=SURUM_AD[s])
            ax.vlines(xs, lo, hi, color=AN.MUREKKEP if hasattr(AN, "MUREKKEP") else "#333333", lw=1.2)
        ax.set_xticks(x)
        ax.set_xticklabels([KS[k] for k in K])
        ax.set_title(bas, fontsize=10)
        ax.grid(axis="y", alpha=0.3)
    axs[0, 0].legend(loc="upper left", fontsize=8.5)
    fig.suptitle("v1 / v2 / v3 / v3-360 karşılaştırması (aynı sürüşler, aynı tohumlar)", fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(yol)
    plt.close(fig)


def ciz_cift(plt, yol):
    """Benzer çift, başlangıç ucundan: p(gerçek koridor) – yol, sürüm başına; fark 60 ışında görünür çizgisi."""
    fig, axs = plt.subplots(2, len(CIZ), figsize=(15, 6.4), sharey=True, sharex=True)
    for i, kor in enumerate(("koridor_5", "koridor_6")):
        for j, s in enumerate(CIZ):
            ax = axs[i, j]
            ki = K.index(kor)
            rs = [r for r in ham(s, "B") if r["gorev"]["kor"] == kor and r["gorev"]["baslangic"] == "bas"]
            for r in sorted(rs, key=lambda r: r["gorev"]["tohum"]):
                a = r["adimlar"]
                ax.plot(a["yol"], [p[ki] for p in a["p"]], color=SURUM_RENK[s], lw=1.2, alpha=0.85)
            oz = ozet(s)
            f60 = [x["fark_60_yol"] for x in oz["B"]["benzer_cift"] if x["kor"] == kor and x["baslangic"] == "bas"]
            if f60:
                ax.axvline(float(np.median(f60)), color="#6250d6", ls="--", lw=1.1)
            ax.axhline(0.5, color=AN.IKINCIL, lw=0.8, alpha=0.6)
            ax.set_xlim(0, 14)
            ax.set_title("%s · %s" % (SURUM_AD[s], "gerçek " + KS[kor]), fontsize=9)
            if j == 0:
                ax.set_ylabel("p(gerçek koridor)")
            if i == 1:
                ax.set_xlabel("gidilen yol (m)")
    fig.suptitle("Benzer çift, başlangıç ucundan: doğru koridorun olasılığı (her çizgi bir tohum; kesikli mor = fark "
                 "konumlayıcının ışınlarında görünür)", fontsize=10.5, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(yol)
    plt.close(fig)


def main():
    S = {}
    for s in SURUMLER:
        oz = ozet(s)
        S[s] = dict(A=a_bolum(s, oz), B=hareket(s, oz, "B"), C=hareket(s, oz, "C"), D=hareket(s, oz, "D"), tani=tani(s),
                    olaylar=None)
        S[s]["olaylar"], S[s]["u_donuslu_kosu"] = olaylar(s, oz)
        S[s]["C_kosular"] = c_kosular(s)
    S["v1_esitlik"] = v1_esitlik("v2")
    S["v1_esitlik_v3"] = v1_esitlik("v3")
    from konumlama import LidarOzellik
    from konumlama.olcum import OlcumParametreleri
    lo = LidarOzellik.varsa_dosyadan()
    sek = [list(map(float, x)) for x in lo.kor_sektorler_derece]
    S["kor"] = dict(sektorler=sek, pay=float(lo.kor_pay_derece), genislik=sum((b - a) % 360.0 for a, b in sek),
                    isin_mcl=OlcumParametreleri().isin_sayisi)
    for ad, yol in (("tani_donus", os.path.join(dizin("sonuc", "v2"), "tani_donus.json")),
                    ("tani_donus_v3", os.path.join(dizin("sonuc", "v3"), "tani_donus_v3.json")),
                    ("odometri_noktasi", os.path.join(dizin("sonuc", "v3"), "odometri_noktasi.json"))):
        if os.path.exists(yol):
            with open(yol, encoding="utf-8") as f:
                S[ad] = json.load(f)
    hedef = dizin("sonuc", "v3")
    with open(os.path.join(hedef, "karsilastirma.json"), "w", encoding="utf-8") as f:
        json.dump(S, f, ensure_ascii=False, indent=1)
    plt = AN.plt_kur()
    g = dizin("gorsel", "v3")
    ciz_ozet(plt, S, os.path.join(g, "karsilastirma_ozet.png"))
    ciz_cift(plt, os.path.join(g, "karsilastirma_benzer_cift.png"))
    print("tamam", hedef)


if __name__ == "__main__":
    main()
