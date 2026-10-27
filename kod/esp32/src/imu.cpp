// imu.cpp -- bkz. imu.h. İSKELET: gerçek sürücü yok, hep "IMU yok" der.
#include "imu.h"

#include <math.h>

#if IMU_VAR
#warning "IMU_VAR=1 ama IMU surucusu henuz yazilmadi (imu.cpp); yaw yine null gonderilecek."
#endif

namespace {

bool imu_hazir = false;

}  // namespace

bool imu_baslat() {
#if IMU_VAR
  // TODO(IMU): seçilen IMU'yu (MPU6050 ya da BNO055) Wire üzerinden bul, kur, imu_hazir = true.
  //            Bulamazsa false dön; robot IMU'suz (yalnız enkoderle) çalışmaya devam eder.
#endif
  imu_hazir = false;
  return imu_hazir;
}

bool imu_var() { return imu_hazir; }

float imu_yaw_derece() {
  if (!imu_hazir) return NAN;
  // TODO(IMU): son okunan yaw açısını döndür (derece, sola +).
  return NAN;
}
