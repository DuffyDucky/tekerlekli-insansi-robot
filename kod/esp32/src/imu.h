// imu.h -- IMU (ivme + jiroskop) arayüzü. ŞİMDİLİK İSKELET: robotta IMU yok (27 Ekim 2026).
//
// Ne yapıyor: Odometri telemetrisindeki "yaw" (robotun yukarıdan bakınca dönüş açısı, derece)
// alanını dolduracak modülün yeri. IMU yokken imu_var() false döner ve "yaw" null gönderilir;
// Pi tarafı (kod/robot/konum/odometri.py) o zaman dönüşü yalnız tekerlek tiklerinden hesaplar.
//
// Açmak için: platformio.ini build_flags'e -DIMU_VAR=1 (varsayılan 0). Bugün 1 yapılırsa derleme
// uyarı verir ve imu_baslat() yine false döner: sürücü henüz yazılmadı.
//
// İleride doldurulacak adaylar (ikisi de PCA9685 ile AYNI I2C hattında, SDA 21 / SCL 22):
//   - MPU6050 (adres 0x68, AD0=3,3 V ise 0x69): ucuz; yalnız ham jiroskop verir. Yaw = jiroskop
//     z hızının zamanla toplanması -> yavaş yavaş kayar (drift). Açılışta robot dururken jiroskop
//     sıfır kayması ölçülüp çıkarılmalı. Bu durumda düzenli çağrılan bir güncelleme işlevi gerekir.
//   - BNO055 (adres 0x28, ADR=3,3 V ise 0x29): kendi içinde füzyon yapar, doğrudan yaw verir,
//     kayması az. Dikkat: BNO055 I2C saat uzatma (clock stretching) yapar; ESP32 ile sorun
//     çıkarabilir -> Wire.setClock(100000) ve Wire.setTimeOut ile dene.
// Kütüphane seçimi (ör. Adafruit BNO055) platformio.ini'ye SABİT sürümle eklenecek; şimdi eklenmedi.
#pragma once

#ifndef IMU_VAR
#define IMU_VAR 0
#endif

// IMU'yu bulmaya ve kurmaya çalışır. I2C (Wire) servolar_baslat() içinde açıldığı için ONDAN SONRA
// çağrılır. IMU bulunduysa true. IMU_VAR 0 iken hiçbir şey yapmaz, false döner.
bool imu_baslat();

// IMU kurulu ve veri veriyor mu?
bool imu_var();

// Robotun yaw açısı, derece (açılıştaki yön = 0, sola dönüş +; sur komutundaki w ile aynı işaret).
// IMU yoksa NAN döner; çağıran önce imu_var()'a bakmalı.
float imu_yaw_derece();
