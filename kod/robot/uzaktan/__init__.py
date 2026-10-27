# Ne yapıyor: telefondan kumanda paketi. Pi'de robotla birlikte çalışan küçük web sunucusu (sunucu.py),
# robotun bileşenlerine güvenli erişim (kopru.py) ve telefonda açılan sayfa (sayfa.html, manifest.json).
# Deneme (robotsuz): py -3 -m robot.uzaktan   (kod/ klasöründen)

from robot.uzaktan.kopru import KopruHatasi, RobotKoprusu
from robot.uzaktan.sunucu import UzaktanSunucu

__all__ = ["KopruHatasi", "RobotKoprusu", "UzaktanSunucu"]
