SS="${SS:-<gecici>}"  # B'nin gecici oturum klasoru; makine yolu commit oncesi kaldirildi (P10.8d C)
timeout ${1:-175} bash -c "until grep -qE 'YOK|surucu rc' $SS/log/tarama-surucu.log; do sleep 20; done"
L=$(ls -t $SS/tarama/*.log | head -1)
echo "$(date +%T) | $(tail -1 $SS/log/tarama-surucu.log | cut -c1-110) | $(basename $L) $(grep -E ' poz, |tam olcum|bitti|kaba|ince' $L | tail -1 | cut -c1-90) | log yasi $(( $(date +%s)-$(stat -c %Y $L) ))s | cpu $(powershell -NoProfile -c '(Get-Process freecadcmd -ErrorAction SilentlyContinue).CPU' | head -1)"
