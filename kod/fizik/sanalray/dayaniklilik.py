"""Dayanıklılık turu: sanal ray sonuçları kusurlu dünyada ne kadar dayanıyor? (etiket planı 5 m ve süzgeç ayarı
DEĞİŞMEDEN; kusur modeli `kusur.py`.)

    %V% kod\\fizik\\sanalray\\dayaniklilik.py kos --grup tek_agir --parca 0/2      (en çok 2 süreç)
    %V% kod\\fizik\\sanalray\\dayaniklilik.py kos --grup ara --kosullar konum3,aci2 --parca 1/2
    %V% kod\\fizik\\sanalray\\dayaniklilik.py rapor        # ham -> sonuc/dayaniklilik_*.csv, sonuc/dayaniklilik.md

Ham kayıtlar `sonuc/ham/dayaniklilik/` (git dışı); eski `sonuc/ham/kosu/` ve eski CSV'lere dokunulmaz.

Kümeler (DÜRÜST AYRIM):
  - kusur ölçümleri: sınama koridorları (koridor_2, 4, 5, 6), tohum 1, 2, 3. Kusur düzeyleri ölçülür, hiçbir ayar
    bunlara göre seçilmedi. Tohum 1 + kusursuz = ilk turdaki koşunun birebir tekrarı (denetim).
  - doğrulamalı başlatma: tasarım ve eşikler GELİŞTİRME kümesinde (koridor_1, koridor_3, bırakma 0-3, +500 tohumu);
    hüküm AYRI tohumlarda (sınama koridorları, bırakma 10-13: ilk turda ve kusur ölçümlerinde kullanılmayan
    noktalar).
Ölçütler: başarı (varış < 0,3 m ve hakem / Beyin bitti), gerçek varış hatası, raydan yanal sapma (ham en büyük;
başlangıç sapmasından arındırılmış: rayda ilk 2 m'den sonraki en büyük ve ortalama), temas olayı, temas süresi
(duvara dayalı kalma)."""

import argparse
import csv
import glob
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sanalray import _yol  # noqa: E402

HAM = os.path.join(_yol.HAM, "dayaniklilik")
SINAMA = ["koridor_2", "koridor_4", "koridor_5", "koridor_6"]
GELISTIRME = ["koridor_1", "koridor_3"]
TOHUMLAR = (1, 2, 3)
ARINMA_M = 2.0
VARSAYILAN = dict(mercek="std", cozunurluk="1152x648", boy_m=0.15, yukseklik="goz", aralik=5, donus_fazlasi=0.14)

# kusur koşulları: (etken, düzey etiketi, kusur sözlüğü)
TEK = {
    "temiz": ("temiz", "-", {}),
    "konum1": ("harita konum", "±1 cm", dict(harita_konum_m=0.01)),
    "konum3": ("harita konum", "±3 cm", dict(harita_konum_m=0.03)),
    "konum5": ("harita konum", "±5 cm", dict(harita_konum_m=0.05)),
    "konum10": ("harita konum", "±10 cm", dict(harita_konum_m=0.10)),
    "konum20": ("harita konum", "±20 cm", dict(harita_konum_m=0.20)),
    "aci1": ("harita açı", "±1°", dict(harita_aci_derece=1.0)),
    "aci2": ("harita açı", "±2°", dict(harita_aci_derece=2.0)),
    "aci5": ("harita açı", "±5°", dict(harita_aci_derece=5.0)),
    "aci10": ("harita açı", "±10°", dict(harita_aci_derece=10.0)),
    "odak05": ("odak", "%0,5", dict(odak_orani=0.005)),
    "odak1": ("odak", "%1", dict(odak_orani=0.01)),
    "odak2": ("odak", "%2", dict(odak_orani=0.02)),
    "odak5": ("odak", "%5", dict(odak_orani=0.05)),
    "egim1": ("montaj eğimi", "±1°", dict(egim_derece=1.0)),
    "egim2": ("montaj eğimi", "±2°", dict(egim_derece=2.0)),
    "egim5": ("montaj eğimi", "±5°", dict(egim_derece=5.0)),
    "gecikme50": ("gecikme", "50 ms", dict(gecikme_s=0.05)),
    "gecikme100": ("gecikme", "100 ms", dict(gecikme_s=0.10)),
    "gecikme200": ("gecikme", "200 ms", dict(gecikme_s=0.20)),
    "dusme20": ("kare düşmesi", "%20", dict(kare_dusme=0.2)),
    "dusme50": ("kare düşmesi", "%50", dict(kare_dusme=0.5)),
    "ortulme20": ("örtülme", "%20 zaman", dict(ortulme=0.2)),
    "ortulme50": ("örtülme", "%50 zaman", dict(ortulme=0.5)),
    "parlama_hafif": ("parlama", "%20 zaman, genlik 120", dict(parlama=0.2, parlama_genlik=120.0)),
    "parlama_agir": ("parlama", "%50 zaman, genlik 230", dict(parlama=0.5, parlama_genlik=230.0)),
    "bulanik_hafif": ("bulanıklık", "20 ms, titreşim 0,3 rad/s", dict(pozlama_s=0.020, titresim=0.3)),
    "bulanik_agir": ("bulanıklık", "33 ms, titreşim 0,6 rad/s", dict(pozlama_s=0.033, titresim=0.6)),
    "yirtik_hafif": ("yırtık", "etiketlerin 1/3'ü, köşe %15", dict(yirtik_oran=0.34, yirtik_boy=0.15)),
    "yirtik_agir": ("yırtık", "hepsi, köşe %25", dict(yirtik_oran=1.0, yirtik_boy=0.25)),
    "kayip1": ("eksik etiket", "1 etiket yok", dict(kayip_etiket=1)),
    "yanlis1": ("yanlış yer", "1 etiket 1 m kaymış", dict(yanlis_yer=1, yanlis_yer_m=1.0)),
}
BIRLESIK = {
    "hafif": ("birleşik", "hafif", dict(harita_konum_m=0.01, harita_aci_derece=1.0, odak_orani=0.005, egim_derece=0.5,
                                         gecikme_s=0.05, kare_dusme=0.05, ortulme=0.05, parlama=0.05,
                                         parlama_genlik=120.0, titresim=0.1)),
    "orta": ("birleşik", "orta", dict(harita_konum_m=0.03, harita_aci_derece=2.0, odak_orani=0.01, egim_derece=1.0,
                                       gecikme_s=0.10, kare_dusme=0.10, ortulme=0.15, parlama=0.15, parlama_genlik=180.0,
                                       pozlama_s=0.020, titresim=0.3, yirtik_oran=0.34, yirtik_boy=0.15)),
    "agir": ("birleşik", "ağır", dict(harita_konum_m=0.05, harita_aci_derece=5.0, odak_orani=0.02, egim_derece=2.0,
                                       gecikme_s=0.20, kare_dusme=0.30, ortulme=0.30, parlama=0.30, parlama_genlik=230.0,
                                       pozlama_s=0.033, titresim=0.6, yirtik_oran=1.0, yirtik_boy=0.25, kayip_etiket=1,
                                       yanlis_yer=1)),
}
KOSULLAR = dict(TEK, **BIRLESIK)
# Tamamlama turu (bağımsız inceleme): ilk turda eksik / yanlış yer etiketi bütün plandan seçildi ve 12 koşunun 6'sında
# robotun rotada hiç görmediği bir etiket oldu (koşu temizle birebir aynı). Burada etiket, AYNI koridor / hedef / tohumun
# kusursuz koşusunda süzgecin en az bir ölçümünü KABUL ettiği etiketlerden seçilir ("rota": tohumdan çekilen sırayla;
# "kritik": en çok kabul edilen ölçümü olan). Ham `sonuc/ham/dayaniklilik_rota/`; eski ham ve CSV'lere dokunulmaz.
HAM_ROTA = os.path.join(_yol.HAM, "dayaniklilik_rota")
ROTA = {
    "kayip1_rota": ("eksik etiket", "1 etiket yok (rotada ölçülenlerden, rastgele)", dict(kayip_etiket=1)),
    "kayip1_kritik": ("eksik etiket", "1 etiket yok (en çok ölçülen)", dict(kayip_etiket=1)),
    "yanlis1_rota": ("yanlış yer", "1 etiket 1 m kaymış (rotada ölçülenlerden, rastgele)",
                     dict(yanlis_yer=1, yanlis_yer_m=1.0)),
    "yanlis1_kritik": ("yanlış yer", "1 etiket 1 m kaymış (en çok ölçülen)", dict(yanlis_yer=1, yanlis_yer_m=1.0)),
    "yanlis05_rota": ("yanlış yer", "1 etiket 0,5 m kaymış (rotada ölçülenlerden, rastgele)",
                      dict(yanlis_yer=1, yanlis_yer_m=0.5)),
    # 0,5 m de kırınca (20/24) sonradan eklendi: kırılma noktası 0,25 ile 0,5 m arasında mı?
    "yanlis025_rota": ("yanlış yer", "1 etiket 0,25 m kaymış (rotada ölçülenlerden, rastgele)",
                       dict(yanlis_yer=1, yanlis_yer_m=0.25)),
}
ROTA_SECIM = {"kayip1_rota": "rota", "kayip1_kritik": "kritik", "yanlis1_rota": "rota", "yanlis1_kritik": "kritik",
              "yanlis05_rota": "rota", "yanlis025_rota": "rota"}
ROTA_TOHUMLAR = (1, 2, 3, 4, 5, 6)


def _kosul(ad):
    return KOSULLAR[ad] if ad in KOSULLAR else ROTA[ad]
TEK_AGIR = ["konum5", "aci5", "odak2", "egim2", "gecikme200", "dusme50", "ortulme50", "parlama_agir", "bulanik_agir",
            "yirtik_agir", "kayip1", "yanlis1"]
KAYIP_TEK = ["gecikme200", "ortulme50"]          # süre bütçesi: 4 etkenden 2'si (aci5, parlama_agir atıldı);
                                                 # dayanıklılık turunda bu ikisi de kilitlenip atlandı (hiç koşulmadı)


# ------------------------------------------------------------------ hakem
def _yanal_hakem(hedef, yol, beyin):
    from sanalray.deney import YanalHakem, _cizgi_uzaklik

    class H(YanalHakem):
        def __init__(self):
            super().__init__(hedef, yol, beyin)
            self.d0 = None
            self.yol_bas = None
            self.en_arin = 0.0
            self.top = 0.0
            self.n = 0

        def yol_ayarla(self, y):
            super().yol_ayarla(y)
            self.yol_bas = None

        def guncelle(self, t, g, temas):
            super().guncelle(t, g, temas)
            if self.sapma_aktif and len(self.yol) >= 2:
                d = _cizgi_uzaklik(self.yol, g[0], g[1])
                if self.yol_bas is None:
                    self.yol_bas, self.d0 = self.h.yol_m, d
                if self.h.yol_m - self.yol_bas >= ARINMA_M:
                    self.en_arin = max(self.en_arin, d)
                    self.top += d
                    self.n += 1
    return H()


def _ortak_cikti(hakem, sonuc, beyin, alg):
    return dict(en_yanal_sapma_m=round(hakem.en_sapma, 4), yanal_bas_m=round(hakem.d0 or 0.0, 4),
                yanal_en_arinmis_m=round(hakem.en_arin, 4), yanal_ort_arinmis_m=round(hakem.top / max(1, hakem.n), 4),
                temas_olay=sonuc["temas_olay"], temas_sure_s=sonuc["temas_sure_s"],
                konum_hata_en_m=round(hakem.konum_hata_en, 4),
                konum_hata_ort_m=round(hakem.konum_hata_top / max(1, hakem.konum_n), 4),
                etiket_olcum=beyin.olcum_sayisi, etiket_ret=beyin.ret_sayisi, kare=alg.kare_sayisi,
                dusen_kare=getattr(alg, "dusen", 0), ortulu_kare=getattr(alg, "ortu_kare", 0),
                parlamali_kare=getattr(alg, "parl_kare", 0), bitis=sonuc["bitis"], rtf=sonuc["rtf"],
                olaylar=beyin.olaylar[-40:])


def _kurulum(kor, plan_tohum, kusur, aday=None, aday_sirali=False):
    from sanalray import etiket as E, kusur as KU
    plan = E.plan_oku(kor, VARSAYILAN["aralik"], VARSAYILAN["boy_m"], VARSAYILAN["yukseklik"])
    cek = KU.Cekilis(plan_tohum, [e["id"] for e in plan["etiketler"]])
    pg, bilgi = KU.gercek_plan(plan, KU.kusur_tam(kusur), cek, aday=aday, aday_sirali=aday_sirali)
    return plan, pg, bilgi, cek


def _temiz_id(kor, hedef, tohum, kafa="sabit"):
    return "ab_temiz_%s_%s_%s_t%d" % (kor, hedef, kafa, int(tohum))


def rota_adaylari(kor, hedef, tohum, secim, ham_dir=None):
    """Aynı koridor / hedef / tohumun kusursuz koşusunda (HAM_ROTA, `izle` ile koşulmuş) süzgecin kabul ettiği
    etiketler. secim "rota": küme (sıra tohumdan); "kritik": kabul sayısına göre azalan (eşitlikte kimlik)."""
    y = os.path.join(ham_dir or HAM_ROTA, _temiz_id(kor, hedef, tohum) + ".json")
    with open(y, encoding="utf-8") as f:
        s = json.load(f)
    kabul = {int(k): int(v) for k, v in (s.get("izle_kabul") or {}).items() if int(v) > 0}
    if not kabul:
        raise RuntimeError("kusursuz koşuda kabul edilen etiket yok: %s" % y)
    if secim == "kritik":
        return sorted(kabul, key=lambda i: (-kabul[i], i)), True, kabul
    return sorted(kabul), False, kabul


def _izle_tak(beyin):
    """Ölçüm sayacı (yalnız deney tasarımı için; Beyin'in davranışını değiştirmez): algılanan ve süzgeçte kabul
    edilen ölçümleri kimlik başına sayar."""
    algi, kabul = {}, {}
    bul0, olcum0 = beyin.bul.bul, beyin.ekf.olcum

    def bul(g):
        r = bul0(g)
        for kimlik, _ in r:
            algi[int(kimlik)] = algi.get(int(kimlik), 0) + 1
        return r

    def olcum(kimlik, *a, **k):
        s = olcum0(kimlik, *a, **k)
        if s == "kabul":
            kabul[int(kimlik)] = kabul.get(int(kimlik), 0) + 1
        return s
    beyin.bul.bul = bul
    beyin.ekf.olcum = olcum
    return algi, kabul


# ------------------------------------------------------------------ A'dan B'ye
def ab_kos(g):
    from gezinme import rota as R, senaryo_ortak as SO
    from gezinme.duzenek import Duzenek
    from sanalray import kusur as KU
    from sanalray.algilayici import SensorBeyni
    from sanalray.beyin import SanalRayBeyni
    from sanalray.deney import odometri_oranlari, tum_etiketler
    import dunya as D
    kor, tohum = g["koridor"], int(g["tohum"])
    kusur = _kosul(g["kosul"])[2]
    s = D.sahne_oku(kor)
    b = s["baslangic"]
    bilinen = (float(b["x"]), float(b["y"]), math.radians(float(b.get("aci_derece", 0))))
    rng = random.Random(10000 + 31 * tohum + 7 * SO.KORIDORLAR.index(kor))      # deney.ab_kos ile aynı
    gercek = SO.baslangic_sapmasi(bilinen, rng)
    tam, hxy = R.durak_coz(kor, g["hedef"])
    aday, sirali, aday_kabul = None, False, None
    if g.get("secim"):
        aday, sirali, aday_kabul = rota_adaylari(kor, g["hedef"], tohum, g["secim"])
    plan, pg, bilgi, cek = _kurulum(kor, 1000 * tohum + SO.KORIDORLAR.index(kor), kusur, aday, sirali)
    dz = Duzenek(KU.kusurlu_sahne(kor, pg, bilgi), tohum=1000 * tohum + SO.KORIDORLAR.index(kor), baslangic=gercek)
    k_d, k_o = odometri_oranlari()
    alg = KU.KusurluAlgilayici(dz, VARSAYILAN["mercek"], VARSAYILAN["cozunurluk"], 77 * tohum + 5, kusur, pg, cek,
                               donus_fazlasi=g["donus_fazlasi"], dogal_donus=k_d, dogal_oteleme=k_o)
    etk = tum_etiketler(VARSAYILAN["aralik"], VARSAYILAN["boy_m"], VARSAYILAN["yukseklik"])
    beyin = SanalRayBeyni(etk, alg.K, gorev="ab", koridor=kor, baslangic=bilinen, hedef=tam, kafa=g["kafa"])
    izle = _izle_tak(beyin) if g.get("izle") else None
    sb = SensorBeyni(beyin, alg)
    rota_m = R.yol_boyu(beyin.yol)
    hakem = _yanal_hakem(hxy, beyin.yol, beyin)
    sure = rota_m / 0.25 * 1.8 + 40.0
    sonuc = dz.kos(sb, sure, hakem=hakem, olay=alg.olay)
    son = sonuc["son_gercek"]
    hata = math.hypot(son[0] - hxy[0], son[1] - hxy[1])
    basari = hata < SO.VARIS_PAYI and (hakem.bitti or sonuc["bitis"] == "beyin")
    neden = "" if basari else ("sure doldu (hedefe %.2f m)" % hata if sonuc["bitis"] == "sure" else
                               "beyin bitti dedi, hedefe %.2f m" % hata)
    if sonuc["temas_olay"]:
        neden = (neden + "; " if neden else "") + "temas %d" % sonuc["temas_olay"]
    alg.kapat()
    out = dict(g, hedef_tam=tam, etiket_sayisi=plan["sayi"], sahnedeki_etiket=pg["sayi"], kusur_bilgi=bilgi,
               basari=bool(basari), neden=neden, sure_s=sonuc["sure_s"], yol_m=round(hakem.h.yol_m, 3),
               rota_m=round(rota_m, 3), varis_hatasi_m=round(hata, 4))
    if izle is not None:
        out["izle_algi"] = {str(k): v for k, v in sorted(izle[0].items())}
        out["izle_kabul"] = {str(k): v for k, v in sorted(izle[1].items())}
    if aday_kabul is not None:
        sec = bilgi["kayip"] + bilgi["yanlis"]
        out["aday"] = sorted(aday_kabul)
        out["secilen"] = sec
        out["secilen_temiz_kabul"] = sum(aday_kabul.get(int(i), 0) for i in sec)
        out["temiz_kabul_toplam"] = sum(aday_kabul.values())
    out.update(_ortak_cikti(hakem, sonuc, beyin, alg))
    return out


# ------------------------------------------------------------------ rastgele bırakılma
def kayip_kos(g):
    from gezinme import rota as R, senaryo_ortak as SO
    from gezinme.duzenek import Duzenek
    from sanalray import kusur as KU
    from sanalray.algilayici import SensorBeyni
    from sanalray.beyin import SanalRayBeyni
    from sanalray.deney import odometri_oranlari, tum_etiketler
    kor, i, tohum = g["koridor"], int(g["birak"]), int(g["tohum"])
    kusur = KOSULLAR[g["kosul"]][2]
    k = SO.KORIDORLAR.index(kor)
    rng = random.Random(20000 + 100 * k + i + (500 if g["kume"] == "gelistirme" else 0))   # deney.kayip_kos ile aynı
    bas = SO.rastgele_birak(kor, rng)
    goreli = "kapi_%d" % rng.randint(1, 3)
    tam, hxy = R.durak_coz(kor, goreli)
    plan, pg, bilgi, cek = _kurulum(kor, 5000 + 1000 * tohum + 10 * k + i, kusur)
    dz = Duzenek(KU.kusurlu_sahne(kor, pg, bilgi), tohum=3000 + 10 * k + i, baslangic=bas)
    k_d, k_o = odometri_oranlari()
    alg = KU.KusurluAlgilayici(dz, VARSAYILAN["mercek"], VARSAYILAN["cozunurluk"], 900 + 10 * k + i, kusur, pg, cek,
                               donus_fazlasi=g["donus_fazlasi"], dogal_donus=k_d, dogal_oteleme=k_o)
    etk = tum_etiketler(VARSAYILAN["aralik"], VARSAYILAN["boy_m"], VARSAYILAN["yukseklik"])
    beyin = SanalRayBeyni(etk, alg.K, gorev="kayip", hedef=goreli, kafa=g["kafa"], baslatma=g.get("baslatma", "tek"))
    sb = SensorBeyni(beyin, alg)
    hakem = _yanal_hakem(hxy, [], beyin)
    iz = {"m": None, "t": None, "hata": None, "yon": None}

    def olay(dz_, t):
        alg.olay(dz_, t)
        if beyin.lokalize_t is not None and iz["m"] is None and beyin.ekf.hazir:
            p, gg = beyin.ekf.govde(), dz_.gercek_poz()
            iz.update(m=round(hakem.h.yol_m, 3), t=round(t, 2), hata=round(math.hypot(p[0] - gg[0], p[1] - gg[1]), 4),
                      yon=round(math.degrees(abs(math.atan2(math.sin(p[2] - gg[2]), math.cos(p[2] - gg[2])))), 2))
        if beyin.yol and not hakem.sapma_aktif:
            hakem.yol_ayarla(beyin.yol)
    sonuc = dz.kos(sb, g.get("sure_s", 300.0), hakem=hakem, olay=olay)
    son = sonuc["son_gercek"]
    hata = math.hypot(son[0] - hxy[0], son[1] - hxy[1])
    basari = hata < SO.VARIS_PAYI and (hakem.bitti or sonuc["bitis"] == "beyin") and beyin.koridor == kor
    if basari:
        neden = ""
    elif beyin.lokalize_t is None:
        neden = "etiket bulunamadi (%.0f s arama)" % sonuc["sure_s"]
    elif beyin.koridor != kor:
        neden = "yanlis koridor %s" % beyin.koridor
    elif sonuc["bitis"] == "sure":
        neden = "sure doldu (hedefe %.2f m)" % hata
    else:
        neden = "beyin bitti dedi, hedefe %.2f m" % hata
    if sonuc["temas_olay"]:
        neden = (neden + "; " if neden else "") + "temas %d" % sonuc["temas_olay"]
    alg.kapat()
    t_bas = dz.w.zaman_s - sonuc["sure_s"]
    out = dict(g, hedef_tam=tam, bas_x=bas[0], bas_y=bas[1], bas_yon_derece=round(math.degrees(bas[2]), 1),
               etiket_sayisi=plan["sayi"], sahnedeki_etiket=pg["sayi"], kusur_bilgi=bilgi, basari=bool(basari),
               neden=neden, sure_s=sonuc["sure_s"], yol_m=round(hakem.h.yol_m, 3),
               ilk_etiket_s=(round(beyin.ilk_etiket_t - t_bas, 2) if beyin.ilk_etiket_t else None),
               lokalize_s=iz["t"], lokalize_yol_m=iz["m"], baslatma_hata_m=iz["hata"], baslatma_yon_hata_derece=iz["yon"],
               karar_koridor=beyin.koridor, varis_hatasi_m=round(hata, 4),
               dogrulama_ret=getattr(beyin, "dogrulama_ret", 0), birakma=getattr(beyin, "birakma_sayisi", 0),
               takilma=getattr(beyin, "takilma_sayisi", 0), kafa_tarama_s=round(getattr(beyin, "kafa_tarama_s", 0.0), 2))
    out.update(_ortak_cikti(hakem, sonuc, beyin, alg))
    return out


# ------------------------------------------------------------------ görev listeleri
def _ab(kosul, hedef_sec, tohumlar=TOHUMLAR, kafa="sabit"):
    from gezinme import senaryo_ab as SA
    out = []
    for tohum in tohumlar:
        for kor in SINAMA:
            hs = SA.hedefler(kor)
            for h in (hs[1:2] if hedef_sec == "orta" else hs[1:]):
                out.append(dict(tur="ab", kume="sinama", kosul=kosul, koridor=kor, hedef=h, tohum=tohum, kafa=kafa,
                                donus_fazlasi=0.25,
                                id="ab_%s_%s_%s_%s_t%d" % (kosul, kor, h, kafa, tohum)))
    return out


def _kayip(kosul, kafalar=("sabit",), baslatma="tek", kume="sinama", birak=None, tohumlar=TOHUMLAR):
    out = []
    korlar = SINAMA if kume == "sinama" else GELISTIRME
    for tohum in tohumlar:
        for kor in korlar:
            bl = [tohum - 1] if birak is None else birak
            for i in bl:
                for kafa in kafalar:
                    out.append(dict(tur="kayip", kume=kume, kosul=kosul, koridor=kor, birak=i, tohum=tohum, kafa=kafa,
                                    baslatma=baslatma, donus_fazlasi=0.14,
                                    id="kayip_%s_%s_%s_b%d_%s_%s_t%d" % (kume[:3], kosul, kor, i, kafa, baslatma, tohum)))
    return out


def gorevler(grup, kosullar=None):
    g = []
    if grup == "temiz":
        g += _ab("temiz", "orta")
    elif grup == "tek_agir":
        for k in TEK_AGIR:
            g += _ab(k, "orta")
    elif grup == "ara":
        for k in kosullar:
            g += _ab(k, "orta")
    elif grup == "kayip_tek":
        for k in (kosullar or KAYIP_TEK):
            g += _kayip(k)
    elif grup == "birlesik":
        for k in (kosullar or ["hafif", "orta", "agir"]):
            g += _ab(k, "orta")                          # süre bütçesi: orta hedef (12 koşu)
            g += _kayip(k, kafalar=("sabit", "tarayan"))
    elif grup == "birlesik_dog":
        # doğrulamalı başlatma, birleşik kusurlu kurulumda (sınama; ilk sürüm başlatmayla aynı bırakma / tohumlar)
        for k in (kosullar or ["orta"]):
            g += _kayip(k, kafalar=("sabit",), baslatma="dogrulamali")
    elif grup == "birlesik_temiz_kayip":
        g += _kayip("temiz", kafalar=("sabit", "tarayan"))
    elif grup == "baslatma_gel":
        for b in ("tek", "dogrulamali"):
            g += _kayip("temiz", kafalar=("sabit",), baslatma=b, kume="gelistirme", birak=range(0, 4),
                        tohumlar=(1,))
    elif grup == "baslatma_sin":
        for k in (kosullar or ["temiz"]):
            for b in ("tek", "dogrulamali"):
                g += _kayip(k, kafalar=("sabit",), baslatma=b, birak=range(10, 14), tohumlar=(1,))
    elif grup == "rota_temiz":
        # tamamlama turu: kusursuz koşu + ölçüm sayacı (aday etiketler bundan; tohum 1-3 ilk turla birebir aynı olmalı)
        for x in _ab("temiz", "orta", tohumlar=ROTA_TOHUMLAR):
            x["izle"] = True
            g.append(x)
    elif grup == "rota":
        for k in (kosullar or list(ROTA)):
            for x in _ab(k, "orta", tohumlar=ROTA_TOHUMLAR):
                x["secim"] = ROTA_SECIM[k]
                g.append(x)
    else:
        raise ValueError(grup)
    return g


def gorev_kos(liste, parca=None, ham_dir=None):
    """parca i/n: önce kendi payı, sonra (iş çalma) diğer süreçlerin henüz başlamadığı koşular; her koşu bir kilit
    dosyasıyla (ham/<id>.kilit, atomik oluşturma) tek sürece düşer."""
    if parca:
        i, n = [int(v) for v in parca.split("/")]
        liste = [x for j, x in enumerate(liste) if j % n == i] + [x for j, x in enumerate(liste) if j % n != i]
    ham_dir = ham_dir or HAM
    os.makedirs(ham_dir, exist_ok=True)
    for j, g in enumerate(liste):
        y = os.path.join(ham_dir, g["id"] + ".json")
        if os.path.exists(y):
            continue
        try:
            fd = os.open(y[:-5] + ".kilit", os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
        except FileExistsError:
            continue
        t0 = time.time()
        try:
            s = (ab_kos if g["tur"] == "ab" else kayip_kos)(g)
        except Exception as h:
            import traceback
            s = dict(g, basari=False, neden="istisna: %r" % h, iz=traceback.format_exc())
        s["duvar_s"] = round(time.time() - t0, 1)
        with open(y, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=1, default=str)
        _yol.durum_yaz("dayan %d/%d %s basari=%s hata=%s arin=%s temas_s=%s duvar=%.0fs" % (
            j + 1, len(liste), g["id"], s.get("basari"), s.get("varis_hatasi_m"), s.get("yanal_en_arinmis_m"),
            s.get("temas_sure_s"), s["duvar_s"]))
        print(g["id"], s.get("basari"), s.get("neden"), s.get("varis_hatasi_m"), s["duvar_s"], flush=True)


# ------------------------------------------------------------------ rapor
AB_ALAN = ["id", "kosul", "koridor", "hedef", "tohum", "kafa", "basari", "neden", "sure_s", "yol_m", "rota_m",
           "varis_hatasi_m", "en_yanal_sapma_m", "yanal_bas_m", "yanal_en_arinmis_m", "yanal_ort_arinmis_m",
           "temas_olay", "temas_sure_s", "konum_hata_en_m", "konum_hata_ort_m", "etiket_olcum", "etiket_ret",
           "sahnedeki_etiket", "etiket_sayisi", "kare", "dusen_kare", "ortulu_kare", "parlamali_kare", "bitis", "duvar_s"]
KAYIP_ALAN = ["id", "kume", "kosul", "koridor", "birak", "tohum", "kafa", "baslatma", "basari", "neden", "sure_s", "yol_m",
              "ilk_etiket_s", "lokalize_s", "lokalize_yol_m", "baslatma_hata_m", "baslatma_yon_hata_derece",
              "dogrulama_ret", "birakma", "takilma", "kafa_tarama_s", "karar_koridor", "varis_hatasi_m", "en_yanal_sapma_m", "yanal_en_arinmis_m",
              "yanal_ort_arinmis_m", "temas_olay", "temas_sure_s", "konum_hata_en_m", "etiket_olcum", "etiket_ret",
              "bas_x", "bas_y", "bas_yon_derece", "bitis", "duvar_s"]


def ham():
    out = []
    for y in sorted(glob.glob(os.path.join(HAM, "*.json"))):
        with open(y, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def _csv(yol, satir, alan):
    with open(yol, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=alan, extrasaction="ignore")
        w.writeheader()
        for s in satir:
            w.writerow(s)


def _f(x, n=3):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else ("%.*f" % (n, x)).replace(".", ",")


def _ort(a):
    a = [x for x in a if x is not None]
    return sum(a) / len(a) if a else None


def _en(a):
    a = [x for x in a if x is not None]
    return max(a) if a else None


def ozet_ab(r):
    return dict(n=len(r), b=sum(1 for s in r if s.get("basari")),
                varis_ort=_ort([s.get("varis_hatasi_m") for s in r]), varis_en=_en([s.get("varis_hatasi_m") for s in r]),
                ham_en=_en([s.get("en_yanal_sapma_m") for s in r]),
                arin_ort=_ort([s.get("yanal_ort_arinmis_m") for s in r]),
                arin_en=_en([s.get("yanal_en_arinmis_m") for s in r]),
                temas=sum(s.get("temas_olay") or 0 for s in r), temas_s=sum(s.get("temas_sure_s") or 0 for s in r),
                kh_en=_en([s.get("konum_hata_en_m") for s in r]))


def tablo_ab(H, sira):
    out = ["| koşul | etken | düzey | başarı | varış hatası ort / en (m) | yanal sapma ham en (m) | yanal, ilk 2 m'den sonra "
           "ort / en (m) | temas olayı | temas süresi (s) | konum hatası en (m) |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k in sira:
        r = [s for s in H if s.get("tur") == "ab" and s.get("kosul") == k]
        if not r:
            continue
        o = ozet_ab(r)
        et, dz, _ = KOSULLAR[k]
        out.append("| %s | %s | %s | %d/%d | %s / %s | %s | %s / %s | %d | %s | %s |" % (
            k, et, dz, o["b"], o["n"], _f(o["varis_ort"]), _f(o["varis_en"]), _f(o["ham_en"]), _f(o["arin_ort"]),
            _f(o["arin_en"]), o["temas"], _f(o["temas_s"], 1), _f(o["kh_en"])))
    return "\n".join(out)


def tablo_kayip(H, filtre, anahtar):
    g = {}
    for s in H:
        if s.get("tur") == "kayip" and filtre(s):
            g.setdefault(anahtar(s), []).append(s)
    out = ["| koşul | başarı | varış hatası ort (m) | başlatma hatası ort / en (m) | başlatma > 0,5 m | konumlanma ort / en "
           "(s) | toplam süre ort (s) | doğrulama reddi | konum bırakma | takılma | temas olayı | temas süresi (s) |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k in sorted(g, key=str):
        r = g[k]
        out.append("| %s | %d/%d | %s | %s / %s | %d | %s / %s | %s | %d | %d | %d | %d | %s |" % (
            k, sum(1 for s in r if s.get("basari")), len(r),
            _f(_ort([s.get("varis_hatasi_m") for s in r if s.get("basari")])),
            _f(_ort([s.get("baslatma_hata_m") for s in r])), _f(_en([s.get("baslatma_hata_m") for s in r])),
            sum(1 for s in r if (s.get("baslatma_hata_m") or 0) > 0.5),
            _f(_ort([s.get("lokalize_s") for s in r]), 1), _f(_en([s.get("lokalize_s") for s in r]), 1),
            _f(_ort([s.get("sure_s") for s in r]), 1), sum(s.get("dogrulama_ret") or 0 for s in r),
            sum(s.get("birakma") or 0 for s in r), sum(s.get("takilma") or 0 for s in r),
            sum(s.get("temas_olay") or 0 for s in r),
            _f(sum(s.get("temas_sure_s") or 0 for s in r), 1)))
    return "\n".join(out)


def rapor():
    H = ham()
    ab = [s for s in H if s.get("tur") == "ab"]
    ky = [s for s in H if s.get("tur") == "kayip"]
    _csv(os.path.join(_yol.SONUC, "dayaniklilik_ab.csv"), ab, AB_ALAN)
    _csv(os.path.join(_yol.SONUC, "dayaniklilik_kayip.csv"), ky, KAYIP_ALAN)
    sira = list(KOSULLAR)
    s = ["# Dayanıklılık tabloları (üretildi: dayaniklilik.py rapor)", "",
         "## A'dan B'ye (sınama koridorları; her koşul, temiz ve birleşik dahil: orta hedef x 4 koridor x 3 tohum = 12), "
         "kafa sabit, dönüş fazlası %25", tablo_ab(ab, sira), "",
         "## Rastgele bırakılma, birleşik kurulumlar (sınama koridorları, bırakma = tohum - 1; ilk sürüm \"tek\" ve "
         "doğrulamalı başlatma)",
         tablo_kayip(H, lambda x: x.get("kume") == "sinama" and x.get("birak", 0) < 10,
                     lambda x: "%s, %s, kafa %s" % (x["kosul"], x["baslatma"], x["kafa"])), "",
         "## Doğrulamalı başlatma, GELİŞTİRME (koridor_1, koridor_3, bırakma 0-3)",
         tablo_kayip(H, lambda x: x.get("kume") == "gelistirme",
                     lambda x: "%s, %s, kafa %s" % (x["kosul"], x["baslatma"], x["kafa"])), "",
         "## Doğrulamalı başlatma, SINAMA (ayrı tohumlar: sınama koridorları, bırakma 10-13)",
         tablo_kayip(H, lambda x: x.get("kume") == "sinama" and x.get("birak", 0) >= 10,
                     lambda x: "%s, %s, kafa %s" % (x["kosul"], x["baslatma"], x["kafa"])), ""]
    bas = [x for x in H if str(x.get("neden", "")).startswith("istisna")]
    if bas:
        s += ["## İstisnalar", ""] + ["- %s: %s" % (x["id"], x["neden"]) for x in bas] + [""]
    metin = "\n".join(s) + "\n"
    with open(os.path.join(_yol.SONUC, "dayaniklilik.md"), "w", encoding="utf-8") as f:
        f.write(metin)
    try:
        print(metin)
    except UnicodeEncodeError:
        print(metin.encode("ascii", "replace").decode("ascii"))


AYNI_ALAN = ("varis_hatasi_m", "etiket_olcum", "etiket_ret", "sure_s", "en_yanal_sapma_m")
ROTA_ALAN = AB_ALAN + ["secim", "aday", "secilen", "secilen_temiz_kabul", "temiz_kabul_toplam", "temizle_ayni"]


def _ayni(a, b):
    return all(str(a.get(x)) == str(b.get(x)) for x in AYNI_ALAN)


def etkisiz_say(satirlar, temiz):
    """satirlar ile aynı koridor / tohumun temiz koşusu AYNI_ALAN'da birebir aynıysa etkisiz (kusur koşuya dokunmadı)."""
    t = {(s["koridor"], int(s["tohum"])): s for s in temiz}
    etkili, etkisiz = [], []
    for s in satirlar:
        c = t.get((s["koridor"], int(s["tohum"])))
        (etkisiz if c is not None and _ayni(s, c) else etkili).append(s)
    return etkili, etkisiz


def _basari(s):
    return s.get("basari") in (True, "True")


def rapor_rota():
    """Tamamlama turu: HAM_ROTA -> sonuc/dayaniklilik_rota_ab.csv, sonuc/dayaniklilik_rota.md (eski dosyalara dokunmaz)."""
    H = []
    for y in sorted(glob.glob(os.path.join(HAM_ROTA, "*.json"))):
        with open(y, encoding="utf-8") as f:
            H.append(json.load(f))
    temiz = [s for s in H if s.get("kosul") == "temiz"]
    for s in H:
        if s.get("secim"):
            c = next((x for x in temiz if x["koridor"] == s["koridor"] and x["tohum"] == s["tohum"]), None)
            s["temizle_ayni"] = bool(c is not None and _ayni(s, c))
    _csv(os.path.join(_yol.SONUC, "dayaniklilik_rota_ab.csv"), H, ROTA_ALAN)
    # denetim: tohum 1-3 temiz koşuları ilk dayanıklılık turuyla (sayaç takılı) birebir aynı mı
    eski = {(s["koridor"], s["tohum"]): s for s in ham() if s.get("tur") == "ab" and s.get("kosul") == "temiz"}
    den = [(s["id"], _ayni(s, eski[(s["koridor"], s["tohum"])])) for s in temiz if (s["koridor"], s["tohum"]) in eski]
    out = ["# Dayanıklılık tamamlama turu: rotada ölçülen etiketten seçilen eksik / yanlış yer (üretildi: "
           "dayaniklilik.py rapor_rota)", "",
           "Sınama koridorları koridor_2/4/5/6, orta hedef, kafa sabit, dönüş fazlası %25, tohum 1-6 (tohum 1-3 ilk turla "
           "aynı başlangıç sapması ve kusur çekilişi). Aday etiketler: aynı koridor / tohumun kusursuz koşusunda süzgecin "
           "en az bir ölçümünü kabul ettiği etiketler (deney tasarımı; Beyin bunu görmez, hep nominal planı kullanır). "
           "\"etkisiz\" = koşu temiz koşuyla birebir aynı (" + ", ".join(AYNI_ALAN) + ").", "",
           "Denetim (sayaç takılı kusursuz koşu, tohum 1-3, ilk turla birebir aynı): %d/%d" % (
               sum(1 for _, a in den if a), len(den)), ""]
    out += ["| koşul | düzey | tohum | başarı | etkisiz | varış ort / en (m) | yanal ham en (m) | yanal ilk 2 m sonrası "
            "ort / en (m) | konum hatası en (m) | temas olay / süre (s) | seçilen etiketin temiz koşudaki kabul payı ort |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k in ["temiz"] + list(ROTA):
        for ad, ts in (("1-3", (1, 2, 3)), ("1-6", ROTA_TOHUMLAR)):
            r = [s for s in H if s.get("kosul") == k and int(s["tohum"]) in ts]
            if not r:
                continue
            o = ozet_ab(r)
            et = sum(1 for s in r if s.get("temizle_ayni"))
            pay = _ort([s["secilen_temiz_kabul"] / max(1, s["temiz_kabul_toplam"]) for s in r if "secilen_temiz_kabul" in s])
            out.append("| %s | %s | %s | %d/%d | %s | %s / %s | %s | %s / %s | %s | %d / %s | %s |" % (
                k, _kosul(k)[1], ad, o["b"], o["n"], ("%d" % et) if k != "temiz" else "-", _f(o["varis_ort"]),
                _f(o["varis_en"]), _f(o["ham_en"]), _f(o["arin_ort"]), _f(o["arin_en"]), _f(o["kh_en"]), o["temas"],
                _f(o["temas_s"], 1), _f(pay, 2)))
    out += ["", "## Başarısız koşular", ""]
    for s in H:
        if not _basari(s):
            out.append("- %s: %s; seçilen %s (temiz koşuda %s / %s kabul)" % (
                s["id"], s.get("neden"), s.get("secilen"), s.get("secilen_temiz_kabul"), s.get("temiz_kabul_toplam")))
    # ilk turun tek etiketlik koşullarının etkili / etkisiz ayrımı (ilk turun ham kayıtlarından)
    E0 = [s for s in ham() if s.get("tur") == "ab"]
    t0 = [s for s in E0 if s.get("kosul") == "temiz"]
    out += ["", "## İlk turun tek etiketlik koşulları: etkili / etkisiz (yeniden sayım, ilk turun ham kayıtları)", "",
            "| koşul | başarı (12) | etkisiz | etkili koşularda başarı |", "| --- | --- | --- | --- |"]
    for k in ("kayip1", "yanlis1", "yirtik_hafif"):
        r = [s for s in E0 if s.get("kosul") == k]
        if not r:
            continue
        ek, es = etkisiz_say(r, t0)
        out.append("| %s | %d/%d | %d | %d/%d |" % (k, sum(1 for s in r if _basari(s)), len(r), len(es),
                                                     sum(1 for s in ek if _basari(s)), len(ek)))
    bas = [x for x in H if str(x.get("neden", "")).startswith("istisna")]
    if bas:
        out += ["", "## İstisnalar", ""] + ["- %s: %s" % (x["id"], x["neden"]) for x in bas]
    metin = "\n".join(out) + "\n"
    with open(os.path.join(_yol.SONUC, "dayaniklilik_rota.md"), "w", encoding="utf-8") as f:
        f.write(metin)
    try:
        print(metin)
    except UnicodeEncodeError:
        print(metin.encode("ascii", "replace").decode("ascii"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("is_", choices=["kos", "rapor", "rapor_rota", "liste"])
    ap.add_argument("--grup", default="tek_agir")
    ap.add_argument("--kosullar", default=None)
    ap.add_argument("--parca", default=None)
    a = ap.parse_args()
    ks = a.kosullar.split(",") if a.kosullar else None
    if a.is_ == "rapor":
        rapor()
        return 0
    if a.is_ == "rapor_rota":
        rapor_rota()
        return 0
    L = gorevler(a.grup, ks)
    if a.is_ == "liste":
        for g in L:
            print(g["id"])
        print(len(L))
        return 0
    _yol.dusuk_oncelik()
    gorev_kos(L, a.parca, HAM_ROTA if a.grup.startswith("rota") else HAM)
    return 0


if __name__ == "__main__":
    sys.exit(main())
