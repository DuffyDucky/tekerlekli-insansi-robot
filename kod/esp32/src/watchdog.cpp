// watchdog.cpp -- bkz. watchdog.h
#include "watchdog.h"

#include <Arduino.h>
#include <esp_task_wdt.h>

#include "motorlar.h"

namespace {

constexpr uint32_t KOMUT_ZAMAN_ASIMI_MS = 500;   // seri.py'deki sözleşme: 500 ms
constexpr uint32_t DONGU_ZAMAN_ASIMI_S = 2;

uint32_t son_sur_ms = 0;
bool tetikli = true;          // açılışta motorlar zaten duruk; ilk "sur" gelene kadar tetikli say
bool dongu_bekcisi_var = false;

}  // namespace

void watchdog_baslat() {
  // ESP-IDF görev bekçisi: süre dolunca panik + yeniden başlatma (true).
  // Arduino-ESP32 2.x (IDF 4.4) ile 3.x (IDF 5) arasında işlev imzası değişti.
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  esp_task_wdt_config_t ayar = {};
  ayar.timeout_ms = DONGU_ZAMAN_ASIMI_S * 1000;
  ayar.idle_core_mask = 0;
  ayar.trigger_panic = true;
  esp_err_t sonuc = esp_task_wdt_reconfigure(&ayar);
  if (sonuc == ESP_ERR_INVALID_STATE) sonuc = esp_task_wdt_init(&ayar);
#else
  esp_err_t sonuc = esp_task_wdt_init(DONGU_ZAMAN_ASIMI_S, true);
#endif
  if (sonuc == ESP_OK) sonuc = esp_task_wdt_add(nullptr);   // nullptr = bu görev (loop)
  dongu_bekcisi_var = (sonuc == ESP_OK);
}

void watchdog_besle(uint32_t simdi_ms) {
  son_sur_ms = simdi_ms;
  tetikli = false;
}

void watchdog_kontrol(uint32_t simdi_ms) {
  // İşaretsiz çıkarma: millis() 49 günde bir sıfıra döner, bu yazım o anda da doğru çalışır.
  if (!tetikli && (simdi_ms - son_sur_ms) >= KOMUT_ZAMAN_ASIMI_MS) {
    motorlar_dur();
    tetikli = true;
  }
  if (dongu_bekcisi_var) esp_task_wdt_reset();
}

bool watchdog_tetikli() { return tetikli; }
