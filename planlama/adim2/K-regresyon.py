# K kontrolu: analiz JSON'larini git surumuyle karsilastirir (sistem Python'u). Kullanim: python K-regresyon.py
import json, subprocess, sys, os
KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CIFT = [("tasarim/freecad/dirsek/dirsek-analiz.json", "HEAD"), ("tasarim/freecad/omuz/omuz-analiz.json", "HEAD"),
        ("tasarim/freecad/kabuk/kabuk-analiz.json", "HEAD"), ("tasarim/freecad/iskelet/iskelet-analiz.json", "c531c59^")]


def yukle_git(rev, yol):
    return json.loads(subprocess.check_output(["git", "show", "%s:%s" % (rev, yol)], cwd=KOK).decode("utf-8"))


def fark(a, b, yol="", out=None):
    out = [] if out is None else out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a:
                out.append(("+", yol + "/" + str(k), None, _kisa(b[k])))
            elif k not in b:
                out.append(("-", yol + "/" + str(k), _kisa(a[k]), None))
            else:
                fark(a[k], b[k], yol + "/" + str(k), out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(("n", yol, len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)):
            fark(x, y, yol + "[%d]" % i, out)
    elif a != b:
        if isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(a - b) < 1e-9:
            return out
        out.append(("~", yol, _kisa(a), _kisa(b)))
    return out


def _kisa(x):
    s = json.dumps(x, ensure_ascii=False)
    return s if len(s) < 120 else s[:117] + "..."


for yol, rev in CIFT:
    a = yukle_git(rev, yol)
    b = json.load(open(os.path.join(KOK, yol), encoding="utf-8"))
    f = fark(a, b)
    print("=" * 10, yol, "(%s -> calisma) fark sayisi %d" % (rev, len(f)))
    # ust seviye anahtar basina ozet
    ozet = {}
    for t, p, x, y in f:
        k = p.split("/")[1].split("[")[0] if "/" in p else p
        ozet.setdefault(k, []).append((t, p, x, y))
    for k, v in ozet.items():
        print("  [%s] %d fark" % (k, len(v)))
        for t, p, x, y in v[:int(sys.argv[1]) if len(sys.argv) > 1 else 6]:
            print("     %s %s: %s -> %s" % (t, p, x, y))
