"""kod/ortak/eklem_sinirlari.json uretici (duzeltme plani C3; yazilim plani "tek kaynak").

Sinirlar elle yazilmaz: tasarim/freecad/arayuz.py (OMUZ, DIRSEK, KAFA, KAFA_KOL_YASAK) -> eklem_sinirlari() -> JSON.
Calistir (FreeCAD gerekmez):  python kod/ortak/eklem_sinirlari_uret.py          # JSON'u yazar
                              python kod/ortak/eklem_sinirlari_uret.py --kontrol # dosya guncel mi (cikis kodu 0/1), yazmaz
JSON'u elle duzenleme; sayi degisecekse arayuz.py'yi degistirip bu betigi yeniden calistir.
"""
import json
import os
import sys

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(KOK, "tasarim", "freecad"))
import arayuz  # noqa: E402  (saf Python, FreeCAD'siz import edilir)

CIKTI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eklem_sinirlari.json")


def uret():
    return json.dumps(arayuz.eklem_sinirlari(), ensure_ascii=False, indent=2) + "\n"


def kontrol_et(d):
    """Temel tutarlilik: min < max, yasak kutu eklem araligi icinde, sol kutu sagin aynasi."""
    e = d["eklemler"]
    for ad, j in e.items():
        if "min" in j:
            assert j["min"] < j["max"], ad
    y = d["kafa_kol_yasak"]
    pan, tilt = y["sag_kol"]["kutu"]["pan"], y["sag_kol"]["kutu"]["tilt"]
    assert e["pan"]["min"] <= pan[0] < pan[1] <= e["pan"]["max"]
    assert e["tilt"]["min"] <= tilt[0] < tilt[1] <= e["tilt"]["max"]
    assert y["sol_kol"]["kutu"]["pan"] == [-pan[1], -pan[0]] and y["sol_kol"]["kutu"]["tilt"] == tilt
    for k, v in y["sag_kol"]["kol_kosulu"].items():
        s = {"one_arka": "r_s1", "yana": "r_s2", "dirsek": "r_dirsek", "bilek": "r_bilek"}[k]
        assert e[s]["min"] <= v[0] <= v[1] <= e[s]["max"], k


def main():
    metin = uret()
    kontrol_et(json.loads(metin))
    if "--kontrol" in sys.argv:
        guncel = os.path.exists(CIKTI) and open(CIKTI, encoding="utf-8").read() == metin
        print("eklem_sinirlari.json", "guncel" if guncel else "ESKI ya da yok")
        sys.exit(0 if guncel else 1)
    with open(CIKTI, "w", encoding="utf-8", newline="\n") as f:
        f.write(metin)
    print("yazildi:", CIKTI)


if __name__ == "__main__":
    main()
