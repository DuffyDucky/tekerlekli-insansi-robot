"""Y0s testleri (unittest). Tek komut: `py -3 kod/testler/kos.py` (ayrıntı `kod/SIMULASYON.md`)."""

import os
import sys

KOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _y in (os.path.join(KOD, "ortak"), os.path.join(KOD, "pi"), os.path.join(KOD, "araclar")):
    if _y not in sys.path:
        sys.path.insert(0, _y)
