# -*- coding: utf-8 -*-
"""
Tarayici demosunu uretir:
  viewer-template.html + model.json + ../../planlama/maliyet.json -> ../Robot-Tasarim-Demosu.html

robot_cad.py sonunda bunu cagirir. Yalniz fiyat ya da arayuz degistiyse CadQuery gerekmez:
  python demo_uret.py [model_json_yolu]
model.json verilmezse (ya da yoksa) model mevcut demodan alinir. Yalniz standart kutuphane.
"""
import sys, os, json

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "viewer-template.html")
DEMO = os.path.join(HERE, "..", "Robot-Tasarim-Demosu.html")
COST = os.path.join(HERE, "..", "..", "planlama", "maliyet.json")
TAG = '<script id="model" type="application/json">'


def model_from_demo():
    with open(DEMO, encoding="utf-8") as f:
        html = f.read()
    i = html.index(TAG) + len(TAG)
    return html[i:html.index("</script>", i)]


def build(model_json=None):
    if model_json and os.path.exists(model_json):
        with open(model_json, encoding="utf-8") as f:
            js = f.read()
    else:
        js = model_from_demo()
    cost = "null"
    if os.path.exists(COST):
        with open(COST, encoding="utf-8") as f:
            data = json.load(f)
        # "<" kacisi: veri <script> etiketini kapatamaz
        cost = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
        print("maliyet:", len(data["kalemler"]), "kalem,", os.path.abspath(COST))
    assert "</script" not in js
    with open(TPL, encoding="utf-8") as f:
        html = f.read()
    html = html.replace("/*COST_JSON*/", cost).replace("/*MODEL_JSON*/", js)
    with open(DEMO, "w", encoding="utf-8") as f:
        f.write(html)
    print("demo:", os.path.abspath(DEMO), os.path.getsize(DEMO) // 1024, "KB")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else None)
