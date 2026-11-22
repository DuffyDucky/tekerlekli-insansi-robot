#!/usr/bin/env bash
# P10.8g üretim sonrası zincir (P108f-zincir.sh kopyası, yalnız log yolu P108g-olcum; P108c-gunluk.md § 12 sırası). Depo kökünden: bash planlama/d158/P108g-zincir.sh [adim ...]
# Her adımın logu planlama/d158/P108g-olcum/zincir/<ad>.log; ilerleme ve çıkış kodları planlama/d158/P108g-olcum/zincir.durum.
# Hiçbir adım CAD kaynağına yazmaz; regresyon --yazma kipinde (dosyaya yazmaz).
cd "$(dirname "$0")/../.." || exit 9
export PYTHONIOENCODING=utf-8
O=planlama/d158/P108g-olcum/zincir; D=planlama/d158/P108g-olcum/zincir.durum
mkdir -p "$O"
V=rehber/veri/rehber-veri.json
R=tasarim/freecad/rehber
kos() {   # ad, komut...
  local ad=$1; shift
  local s; s=$(date +%s)
  echo "$(date '+%H:%M:%S') basladi $ad" >> "$D"
  "$@" > "$O/$ad.log" 2>&1
  local c=$?
  echo "$(date '+%H:%M:%S') bitti $ad cikis $c sure $(( $(date +%s) - s ))s" >> "$D"
}
P="py -3 -B -X utf8"
ADIMLAR=("$@"); [ $# -eq 0 ] && ADIMLAR=(0a t1 t2 2a 2b 2c 3 4 5 6 6g 7 8 9 10)
echo "zincir basladi $(date '+%d.%m %H:%M:%S'): ${ADIMLAR[*]}" > "$D"
for a in "${ADIMLAR[@]}"; do
  case $a in
    0a) kos 0a-carpisma bash -c "cd tasarim/freecad && $P carpisma_kos.py kontrol" ;;
    t1) kos t1-kupon $P tasarim/freecad/test/kupon_tazelik.py ;;
    t2) kos t2-kupon-bozma $P tasarim/freecad/test/kupon_tazelik.py --bozma-denemesi ;;
    2a) kos 2a-kablo $P $R/rehber_kablo.py --veri $V ;;
    2b) kos 2b-kablo-bozma $P $R/rehber_kablo.py --bozma-denemesi --veri $V ;;
    2c) kos 2c-kaynak $P $R/rehber_denetim.py --kaynak ;;
    3) kos 3-denetim $P $R/rehber_denetim.py ;;
    4) kos 4-F10f $P planlama/d158/F10f-dogrula.py ;;
    5) kos 5-F10e $P planlama/d158/F10e-dogrula.py --goruntu-yok ;;
    6) kos 6-F10d $P planlama/d158/F10d-dogrula.py --goruntu-yok ;;
    6g) kos 6g-F10d-gizli $P planlama/d158/F10d-dogrula.py --gizli planlama/rehber/kontrol.json ;;
    7) kos 7-F10a $P planlama/d158/F10a-dogrula.py --kanit-yok ;;
    8) kos 8-F9b $P planlama/d158/F9b-dogrula.py ;;
    9) kos 9-carpisma bash -c "cd tasarim/freecad && $P carpisma_kos.py kontrol" ;;
    10) kos 10-regresyon $P planlama/d158/regresyon.py --yazma ;;
    *) echo "bilinmeyen adim $a" >> "$D" ;;
  esac
done
echo "zincir bitti $(date '+%d.%m %H:%M:%S')" >> "$D"
