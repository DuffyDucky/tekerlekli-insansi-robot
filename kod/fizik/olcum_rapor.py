"""Y0f ölçüm sonuçlarını (olcum.json) okunur Markdown'a çevirir. olcumler.py çağırır."""


def yaz(o, yol):
    with open(yol, "w", encoding="utf-8") as f:
        f.write("# Y0f fizik ölçümleri (üretilir: `kod/fizik/olcumler.py`; ham sayılar `olcum.json`)\n\n")
        f.write("Elle düzenleme. Yorum ve hüküm `kod/SIMULASYON.md` fizik bölümünde ve `planlama/d158/Y0f-gunluk.md`'de.\n\n")
        for b, v in o.items():
            if b.startswith("_"):
                continue
            f.write("## %s\n\n```json\n" % b)
            import json
            f.write(json.dumps(v, ensure_ascii=False, indent=1)[:200000])
            f.write("\n```\n\n")
