#!/bin/bash
# kullanim: R=<depo kok, unix> zincir.sh <betik (repo goreli)>...
SS="${SS:-<gecici>}"  # B'nin gecici oturum klasoru; makine yolu commit oncesi kaldirildi (P10.8d C)
FCX="$LOCALAPPDATA/Programs/FreeCAD 1.1/bin/freecadcmd.exe"
cd "$R" || { echo "cd R basarisiz"; exit 9; }
for b in "$@"; do
  ad=$(basename "$b" .py)
  printf 'P10.8d B (kontrol): %s, 20.11 %s' "$ad" "$(date +%H:%M)" > planlama/d158/FREECAD-KILIT.txt
  st=$(date +%s); echo "[$(date +%T)] $ad basladi"
  d="$(dirname "$b")"
  (cd "$d" && FC_SCRIPT="$(pwd -W)/$(basename "$b")" "$FCX" "$HOME/.robot-cad/run_fc.py" > "$SS/log/$ad.log" 2>&1)
  rc=$?
  ex=$(grep -c "Exception while processing" "$SS/log/$ad.log")
  echo "[$(date +%T)] $ad bitti rc=$rc istisna=$ex $(( $(date +%s)-st ))s"
done
printf 'boş' > planlama/d158/FREECAD-KILIT.txt
