"""Labirent denemesinin puanı (ödül - ceza). Formülün TEK yeri; hakem.py ve parametre araması buradan çağırır.

Kaynak: planlama/labirent-kesif-arastirmasi.md § 4 (önerilen formül), BENIOKU.md "Puan" (gerekçe, oyunlanabilirlik).

Ana tur (T = süre sınırı, 900 s):
    basari        S1 = 1000 + 500 * (1 - t / T)                 t = FINISH çizgisini geçiş anı
    fail_sure     S1 = 400 * p_en
    fail_sikisma  S1 = 400 * p_en - 100
    fail_start    S1 = -200                                     (ilerleme sayılmaz: kural ihlali)
    her durumda   - 50 * carpma_sayisi - 10 * carpma_suresi_s    (çarpma olayı ayrık; 1 s içindeki yeniden temas aynı olay)
p_en = max_t (1 - g(x_t) / g(START)), g = gerçek labirent grafiğinde FINISH çizgisine jeodezik uzaklık (hakem hesaplar).

Ek tur (yalnız ana tur başarılıysa; robot öğrendiği haritayla START'tan yeniden koşar):
    basari        S2 = 300 * min(1, t_yildiz / t2) - 50 * carpma_sayisi,  t_yildiz = cozum_uzunlugu_m / v_maks
    değilse       S2 = 0
Toplam S = S1 + S2.  Ölçek: tek tur 0-1500 (başarı 1000-1500, başarısızlık en çok 400), ek turla en çok 1800.
"""

T_VARSAYILAN_S = 900.0
V_MAKS_M_S = 0.39            # teker azamisi (robot_parametreleri.json teker_azami_hiz_m_s, TAHMIN)

AGIRLIK = {
    "basari_taban": 1000.0,
    "basari_sure": 500.0,
    "kismi_ilerleme": 400.0,
    "sikisma_ceza": 100.0,
    "start_puani": -200.0,
    "carpma_olay": 50.0,
    "temas_saniye": 10.0,
    "ek_tur": 300.0,
    "ek_tur_carpma": 50.0,
}

DURUMLAR = ("basari", "fail_start", "fail_sure", "fail_sikisma")


def puan(durum, sure_s, p_en, carpma_sayisi, carpma_suresi_s, T=T_VARSAYILAN_S, agirlik=None):
    """(toplam, döküm sözlüğü). Döküm terimlerinin toplamı = toplam (yuvarlamasız)."""
    w = dict(AGIRLIK, **(agirlik or {}))
    if durum not in DURUMLAR:
        raise ValueError("bilinmeyen durum: %r" % (durum,))
    p = min(1.0, max(0.0, float(p_en or 0.0)))
    t = min(T, max(0.0, float(sure_s)))
    d = {}
    if durum == "basari":
        d["basari_taban"] = w["basari_taban"]
        d["sure_primi"] = w["basari_sure"] * (1.0 - t / T)
    elif durum == "fail_start":
        d["start_cikisi"] = w["start_puani"]
    else:
        d["ilerleme"] = w["kismi_ilerleme"] * p
        if durum == "fail_sikisma":
            d["sikisma_cezasi"] = -w["sikisma_ceza"]
    d["carpma_cezasi"] = -w["carpma_olay"] * int(carpma_sayisi)
    d["temas_cezasi"] = -w["temas_saniye"] * max(0.0, float(carpma_suresi_s))
    return sum(d.values()), d


def ek_tur_puani(basarili, t2_s, carpma_sayisi, cozum_uzunlugu_m, v_maks=V_MAKS_M_S, agirlik=None):
    """(S2, döküm). Ana tur başarılı değilse çağıran S2 = 0 kullanır (ek tur koşulmaz)."""
    w = dict(AGIRLIK, **(agirlik or {}))
    if not basarili:
        return 0.0, {"ek_tur": 0.0}
    t_yildiz = cozum_uzunlugu_m / v_maks
    d = {"ek_tur_hiz": w["ek_tur"] * min(1.0, t_yildiz / max(1e-9, float(t2_s))),
         "ek_tur_carpma": -w["ek_tur_carpma"] * int(carpma_sayisi)}
    return sum(d.values()), d
