# T2 (15 Ekim 2026): JGB37 durma torku 9 kg*cm senaryosu (Aslong tablosu, 1:90; raporlar/kaynaklar/06-aku-secimi.md satir 15).
# donus_hesap.py'yi import eder, arayuz.TABAN['donus'] DEGISMEZ: yalniz bellekte *_olculen alanlari doldurulur.
# Uc durum: mevcut (21 kg*cm, 2,8 A), 9 kg*cm + 1,2 A (Aslong: ayni motor, durma akimi redukturden bagimsiz), 9 kg*cm + 2,8 A.
# Not: durmanin uzerindeki torklarda yazilan akim dogrusal disdegerdir; gercekte motor durur, akim = durma akimi.
# Calistir: python planlama/adim3/T2_donus_9kg.py
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tasarim", "freecad", "taban"))
import donus_hesap as DH

ta = json.load(open(os.path.join(os.path.dirname(DH.__file__), "taban-analiz.json"), encoding="utf-8"))
ev = ta["robot"]["pozlar"][0]
for st, sa in ((None, None), (9.0, 1.2), (9.0, None)):
    DH.D["stall_kgcm_olculen"] = st
    DH.D["stall_A_olculen"] = sa
    r = DH.hesapla(ev["kutle_g"] / 1000.0, ev["am"])
    m = r["motor"]
    print("== durma %.1f kg cm, surekli %.2f, durma akimi %.2f A" % (m["stall_kgcm"], m["surekli_kgcm"], m["stall_A"]))
    for a, o, oe in zip(r["yerinde"], r["yerinde_omni"], r["yerinde_omni_cap_esit"]):
        b = next(b for b in r["ust_sinir"] if b["mu"] == a["mu"] and b["R_mm"] == 0)
        print("mu %.1f: yerinde %.2f kgcm surekli x%.2f stall %%%.0f akim %.2f | ust %.2f stall %%%.0f | omni %.2f x%.2f stall %%%.0f "
              "akim %.2f | omniO125 %.2f" % (
                  a["mu"], a["en_cok_kgcm"], a["en_cok_oran_surekli"], a["en_cok_oran_stall"] * 100, a["en_cok_akim_A"], b["en_cok_kgcm"],
                  b["oran_stall"] * 100, o["en_cok_kgcm"], o["en_cok_oran_surekli"], o["en_cok_oran_stall"] * 100, o["en_cok_akim_A"],
                  oe["en_cok_kgcm"]))
    for d in r["duz_omni"]:
        print("  duz omni mu %.1f en cok %.2f (surekli x%.2f)" % (d["mu"], d["en_cok_kgcm"], d["en_cok_oran_surekli"]))
    print(r["karar"]["sonuc"])
DH.D["stall_kgcm_olculen"] = None
DH.D["stall_A_olculen"] = None
