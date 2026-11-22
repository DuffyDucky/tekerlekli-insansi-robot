# Y0f fizik ölçümleri (üretilir: `kod/fizik/olcumler.py`; ham sayılar `olcum.json`)

Elle düzenleme. Yorum ve hüküm `kod/SIMULASYON.md` fizik bölümünde ve `planlama/d158/Y0f-gunluk.md`'de.

## model

```json
{
 "mujoco_toplam_kutle_kg": 26.2761,
 "model_uret_kutle_kg": 26.2761,
 "mujoco_am_m": [
  -0.0105,
  0.0,
  0.5205
 ],
 "model_uret_am_m": [
  -0.0105,
  0.0,
  0.5205
 ],
 "aks_yuk_N": {
  "on": 121.5879,
  "arka": 136.1811,
  "el_hesabi_taban_analiz": {
   "on_N": 121.6,
   "arka_N": 136.2,
   "mu_gereken_rampa5": 0.169
  }
 },
 "pozlar": [
  {
   "kod": "ev",
   "ad": "Ev pozu (kollar asagida)",
   "cad_eklem_sag_sol": [
    [
     0,
     0,
     0
    ],
    [
     0,
     0,
     0
    ]
   ],
   "model_am_mm": [
    -10.4753,
    0.034,
    520.4562
   ],
   "taban_analiz_am_mm": [
    -10.5,
    0.0,
    520.5
   ],
   "fark_mm": [
    0.0247,
    0.034,
    -0.0438
   ]
  },
  {
   "kod": "one",
   "ad": "Iki kol one uzanmis (S1 90, duz)",
   "cad_eklem_sag_sol": [
    [
     90,
     0,
     0
    ],
    [
     90,
     0,
     0
    ]
   ],
   "model_am_mm": [
    -2.0139,
    0.034,
    528.7719
   ],
   "taban_analiz_am_mm": [
    -2.0,
    0.0,
    528.8
   ],
   "fark_mm": [
    -0.0139,
    0.034,
    -0.0281
   ]
  },
  {
   "kod": "one_yukari",
   "ad": "Iki kol one-yukari (S1 135)",
   "cad_eklem_sag_sol": [
    [
     135,
     0,
     0
    ],
    [
     135,
     0,
     0
    ]
   ],
   "model_am_mm": [
    -4.4193,
    0.034,
    534.7249
   ],
   "taban_analiz_am_mm": [
    -4.4,
    0.0,
    534.7
   ],
   "fark_mm": [
    -0.0193,
    0.034,
    0.0249
   ]
  },
  {
   "kod": "geri",
   "ad": "Iki kol geride (S1 -45)",
   "cad_eklem_sag_sol": [
    [
     -45,
     0,
     0
    ],
    [
     -45,
     0,
     0
    ]
   ],
   "model_am_mm": [
    -16.3856,
    0.034,
    522.9647
   ],
   "taban_analiz_am_mm": [
    -16.4,
    0.0,
    523.0
   ],
   "fark_mm": [
    0.0144,
    0.034,
    -0.0353
   ]
  },
  {
   "kod": "yan_tek",
   "ad": "Sag kol yana acik (S2 90), sol asagida",
   "cad_eklem_sag_sol": [
    [
     0,
     90,
     0
    ],
    [
     0,
     0,
     0
    ]
   ],
   "model_am_mm": [
    -10.4753,
    4.2027,
    524.7789
   ],
   "taban_analiz_am_mm": [
    -10.5,
    4.2,
    524.8
   ],
   "fark_mm": [
    0.0247,
    0.0027,
    -0.0211
   ]
  }
 ]
}
```

## statik

```json
{
 "ev": {
  "ileri": {
   "fizik_derece": 20.7,
   "el_hesabi_derece": 20.5837,
   "fark_derece": 0.1163,
   "am_yuksekligi_m": 0.5205,
   "d_m": 0.1955
  },
  "geri": {
   "fizik_derece": 18.6,
   "el_hesabi_derece": 18.5363,
   "fark_derece": 0.0637,
   "am_yuksekligi_m": 0.5205,
   "d_m": 0.1745
  },
  "yan_sol": {
   "fizik_derece": 25.3,
   "el_hesabi_derece": 22.5345,
   "fark_derece": 2.7655,
   "am_yuksekligi_m": 0.5205,
   "d_m": 0.216
  },
  "yan_sag": {
   "fizik_derece": 25.3,
   "el_hesabi_derece": 22.5345,
   "fark_derece": 2.7655,
   "am_yuksekligi_m": 0.5205,
   "d_m": 0.216
  }
 },
 "kollar_one": {
  "ileri": {
   "fizik_derece": 19.6,
   "el_hesabi_derece": 19.4819,
   "fark_derece": 0.1181,
   "am_yuksekligi_m": 0.5288,
   "d_m": 0.1871
  },
  "geri": {
   "fizik_derece": 19.2,
   "el_hesabi_derece": 19.0842,
   "fark_derece": 0.1158,
   "am_yuksekligi_m": 0.5288,
   "d_m": 0.1829
  },
  "yan_sol": {
   "fizik_derece": 24.9,
   "el_hesabi_derece": 22.2166,
   "fark_derece": 2.6834,
   "am_yuksekligi_m": 0.5288,
   "d_m": 0.216
  },
  "yan_sag": {
   "fizik_derece": 24.9,
   "el_hesabi_derece": 22.2166,
   "fark_derece": 2.6834,
   "am_yuksekligi_m": 0.5288,
   "d_m": 0.216
  }
 },
 "kollar_one_yukari": {
  "ileri": {
   "fizik_derece": 19.6,
   "el_hesabi_derece": 19.5102,
   "fark_derece": 0.0898,
   "am_yuksekligi_m": 0.5347,
   "d_m": 0.1895
  },
  "geri": {
   "fizik_derece": 18.8,
   "el_hesabi_derece": 18.6582,
   "fark_derece": 0.1418,
   "am_yuksekligi_m": 0.5347,
   "d_m": 0.1805
  },
  "yan_sol": {
   "fizik_derece": 24.7,
   "el_hesabi_derece": 21.9941,
   "fark_derece": 2.7059,
   "am_yuksekligi_m": 0.5347,
   "d_m": 0.216
  },
  "yan_sag": {
   "fizik_derece": 24.7,
   "el_hesabi_derece": 21.9941,
   "fark_derece": 2.7059,
   "am_yuksekligi_m": 0.5347,
   "d_m": 0.216
  }
 },
 "kollar_geri": {
  "ileri": {
   "fizik_derece": 21.2,
   "el_hesabi_derece": 21.0566,
   "fark_derece": 0.1434,
   "am_yuksekligi_m": 0.523,
   "d_m": 0.2014
  },
  "geri": {
   "fizik_derece": 18.0,
   "el_hesabi_derece": 17.8725,
   "fark_derece": 0.1275,
   "am_yuksekligi_m": 0.523,
   "d_m": 0.1686
  },
  "yan_sol": {
   "fizik_derece": 25.2,
   "el_hesabi_derece": 22.4377,
   "fark_derece": 2.7623,
   "am_yuksekligi_m": 0.523,
   "d_m": 0.216
  },
  "yan_sag": {
   "fizik_derece": 25.2,
   "el_hesabi_derece": 22.4377,
   "fark_derece": 2.7623,
   "am_yuksekligi_m": 0.523,
   "d_m": 0.216
  }
 }
}
```

## fren

```json
{
 "kosular": [
  {
   "durus": "dur",
   "yon": "ileri",
   "poz": "ev",
   "takim": "ana",
   "fren_degeri": null,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 1.7667,
   "tepe_yavaslama_2ms_m_s2": 1.8371,
   "ort_yavaslama_m_s2": 1.2076,
   "durma_suresi_s": 0.328,
   "durma_yolu_m": 0.0601,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 69.1036,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0028,
   "en_buyuk_egim_derece": 0.0009,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 2.0853,
    "bosalan_aks_beklenen_N": 70.8764,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "dur",
   "yon": "geri",
   "poz": "ev",
   "takim": "ana",
   "fren_degeri": null,
   "v0_m_s": -0.3961,
   "tepe_yavaslama_m_s2": 1.7666,
   "tepe_yavaslama_2ms_m_s2": 1.837,
   "ort_yavaslama_m_s2": 1.2076,
   "durma_suresi_s": 0.328,
   "durma_yolu_m": 0.0601,
   "son_hiz_m_s": -0.0,
   "bosalan_aks_statik_N": 121.5874,
   "bosalan_aks_en_az_N": 54.5119,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0031,
   "en_buyuk_egim_derece": 0.0009,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.2893,
    "pay": 1.8619,
    "bosalan_aks_beklenen_N": 56.2846,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "bekci",
   "yon": "ileri",
   "poz": "ev",
   "takim": "ana",
   "fren_degeri": null,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 3.2377,
   "tepe_yavaslama_2ms_m_s2": 7.6507,
   "ort_yavaslama_m_s2": 1.6643,
   "durma_suresi_s": 0.238,
   "durma_yolu_m": 0.0322,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 0.0,
   "bosalan_aks_sifir_ms": 61.0,
   "teker_kalkma_mm": 0.0373,
   "en_buyuk_egim_derece": 0.0065,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 1.1379,
    "bosalan_aks_beklenen_N": 16.5011,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "bekci",
   "yon": "geri",
   "poz": "ev",
   "takim": "ana",
   "fren_degeri": null,
   "v0_m_s": -0.3961,
   "tepe_yavaslama_m_s2": 3.0977,
   "tepe_yavaslama_2ms_m_s2": 6.1702,
   "ort_yavaslama_m_s2": 1.63,
   "durma_suresi_s": 0.243,
   "durma_yolu_m": 0.0335,
   "son_hiz_m_s": -0.0,
   "bosalan_aks_statik_N": 121.5874,
   "bosalan_aks_en_az_N": 0.0,
   "bosalan_aks_sifir_ms": 79.0,
   "teker_kalkma_mm": 0.0266,
   "en_buyuk_egim_derece": 0.0048,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.2893,
    "pay": 1.0619,
    "bosalan_aks_beklenen_N": 7.0835,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "acil_stop",
   "yon": "ileri",
   "poz": "ev",
   "takim": "ana",
   "fren_degeri": null,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 0.3459,
   "tepe_yavaslama_2ms_m_s2": 0.3463,
   "ort_yavaslama_m_s2": 0.3565,
   "durma_suresi_s": 1.111,
   "durma_yolu_m": 0.2182,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 122.9425,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0006,
   "en_buyuk_egim_derece": 0.0002,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6834,
    "pay": 10.6489,
    "bosalan_aks_beklenen_N": 123.396,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "acil_stop",
   "yon": "geri",
   "poz": "ev",
   "takim": "ana",
   "fren_degeri": null,
   "v0_m_s": -0.3961,
   "tepe_yavaslama_m_s2": 0.346,
   "tepe_yavaslama_2ms_m_s2": 0.3463,
   "ort_yavaslama_m_s2": 0.3565,
   "durma_suresi_s": 1.111,
   "durma_yolu_m": 0.2182,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 121.5874,
   "bosalan_aks_en_az_N": 108.3325,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0006,
   "en_buyuk_egim_derece": 0.0002,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.2896,
    "pay": 9.5088,
    "bosalan_aks_beklenen_N": 108.7994,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "dur",
   "yon": "ileri",
   "poz": "kollar_one",
   "takim": "ana",
   "fren_degeri": null,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 1.7658,
   "tepe_yavaslama_2ms_m_s2": 1.8363,
   "ort_yavaslama_m_s2": 1.2076,
   "durma_suresi_s": 0.328,
   "durma_yolu_m": 0.06,
   "son_hiz_m_s": -0.0,
   "bosalan_aks_statik_N": 121.3241,
   "bosalan_aks_en_az_N": 62.2586,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0024,
   "en_buyuk_egim_derece": 0.001,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.472,
    "pay": 1.9662,
    "bosalan_aks_beklenen_N": 55.0423,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "dur",
   "yon": "geri",
   "poz": "kollar_one",
   "takim": "ana",
   "fren_degeri": null,
   "v0_m_s": -0.3961,
   "tepe_yavaslama_m_s2": 1.7659,
   "tepe_yavaslama_2ms_m_s2": 1.8363,
   "ort_yavaslama_m_s2": 1.2076,
   "durma_suresi_s": 0.328,
   "durma_yolu_m": 0.06,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 140.492,
   "bosalan_aks_en_az_N": 59.3811,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0039,
   "en_buyuk_egim_derece": 0.0009,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.3953,
    "pay": 1.9228,
    "bosalan_aks_beklenen_N": 74.2099,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "bekci",
   "yon": "ileri",
   "poz": "kollar_one",
   "takim": "ana",
   "fren_degeri": null,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 3.1705,
   "tepe_yavaslama_2ms_m_s2": 7.76,
   "ort_yavaslama_m_s2": 1.6436,
   "durma_suresi_s": 0.241,
   "durma_yolu_m": 0.0331,
   "son_hiz_m_s": -0.0,
   "bosalan_aks_statik_N": 121.3241,
   "bosalan_aks_en_az_N": 0.0,
   "bosalan_aks_sifir_ms": 69.0,
   "teker_kalkma_mm": 0.0375,
   "en_buyuk_egim_derece": 0.0067,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.472,
    "pay": 1.0951,
    "bosalan_aks_beklenen_N": 2.3172,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "bekci",
   "yon": "geri",
   "poz": "kollar_one",
   "takim": "ana",
   "fren_degeri": null,
   "v0_m_s": -0.3961,
   "tepe_yavaslama_m_s2": 3.1006,
   "tepe_yavaslama_2ms_m_s2": 6.8525,
   "ort_yavaslama_m_s2": 1.6368,
   "durma_suresi_s": 0.242,
   "durma_yolu_m": 0.0334,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 140.492,
   "bosalan_aks_en_az_N": 0.0,
   "bosalan_aks_sifir_ms": 72.0,
   "teker_kalkma_mm": 0.0276,
   "en_buyuk_egim_derece": 0.0047,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.3953,
    "pay": 1.0951,
    "bosalan_aks_beklenen_N": 24.1101,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "acil_stop",
   "yon": "ileri",
   "poz": "kollar_one",
   "takim": "ana",
   "fren_degeri": null,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 0.3774,
   "tepe_yavaslama_2ms_m_s2": 0.3774,
   "ort_yavaslama_m_s2": 0.3565,
   "durma_suresi_s": 1.111,
   "durma_yolu_m": 0.2267,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 121.3241,
   "bosalan_aks_en_az_N": 109.1709,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0005,
   "en_buyuk_egim_derece": 0.0004,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.7001,
    "pay": 9.8051,
    "bosalan_aks_beklenen_N": 107.3736,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "acil_stop",
   "yon": "geri",
   "poz": "kollar_one",
   "takim": "ana",
   "fren_degeri": null,
   "v0_m_s": -0.3961,
   "tepe_yavaslama_m_s2": 0.3793,
   "tepe_yavaslama_2ms_m_s2": 0.3793,
   "ort_yavaslama_m_s2": 0.3556,
   "durma_suresi_s": 1.114,
   "durma_yolu_m": 0.2097,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 140.492,
   "bosalan_aks_en_az_N": 97.9444,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0021,
   "en_buyuk_egim_derece": 0.0003,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.2676,
    "pay": 8.6152,
    "bosalan_aks_beklenen_N": 126.4698,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "dur",
   "yon": "ileri",
   "poz": "ev",
   "takim": "mu_0.5",
   "fren_degeri": null,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 1.7667,
   "tepe_yavaslama_2ms_m_s2": 1.8371,
   "ort_yavaslama_m_s2": 1.2076,
   "durma_suresi_s": 0.328,
   "durma_yolu_m": 0.0601,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 69.1036,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0028,
   "en_buyuk_egim_derece": 0.0009,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 2.0853,
    "bosalan_aks_beklenen_N": 70.8764,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "dur",
   "yon": "geri",
   "poz": "ev",
   "takim": "mu_0.5",
   "fren_degeri": null,
   "v0_m_s": -0.3961,
   "tepe_yavaslama_m_s2": 1.7666,
   "tepe_yavaslama_2ms_m_s2": 1.837,
   "ort_yavaslama_m_s2": 1.2076,
   "durma_suresi_s": 0.328,
   "durma_yolu_m": 0.0601,
   "son_hiz_m_s": -0.0,
   "bosalan_aks_statik_N": 121.5874,
   "bosalan_aks_en_az_N": 54.5119,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0031,
   "en_buyuk_egim_derece": 0.0009,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.2893,
    "pay": 1.8619,
    "bosalan_aks_beklenen_N": 56.2846,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "bekci",
   "yon": "ileri",
   "poz": "ev",
   "takim": "mu_0.5",
   "fren_degeri": null,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 2.9872,
   "tepe_yavaslama_2ms_m_s2": 6.4667,
   "ort_yavaslama_m_s2": 1.63,
   "durma_suresi_s": 0.243,
   "durma_yolu_m": 0.0336,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 0.0,
   "bosalan_aks_sifir_ms": 81.0,
   "teker_kalkma_mm": 0.0418,
   "en_buyuk_egim_derece": 0.007,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 1.2333,
    "bosalan_aks_beklenen_N": 25.762,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "bekci",
   "yon": "geri",
   "poz": "ev",
   "takim": "mu_0.5",
   "fren_degeri": null,
   "v0_m_s": -0.3961,
   "tepe_yavaslama_m_s2": 3.0115,
   "tepe_yavaslama_2ms_m_s2": 5.8287,
   "ort_yavaslama_m_s2": 1.5844,
   "durma_suresi_s": 0.25,
   "durma_yolu_m": 0.0353,
   "son_hiz_m_s": -0.0,
   "bosalan_aks_statik_N": 121.5874,
   "bosalan_aks_en_az_N": 0.0,
   "bosalan_aks_sifir_ms": 98.0,
   "teker_kalkma_mm": 0.0391,
   "en_buyuk_egim_derece": 0.0064,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.2893,
    "pay": 1.0923,
    "bosalan_aks_beklenen_N": 10.2701,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "acil_stop",
   "yon": "ileri",
   "poz": "ev",
   "takim": "mu_0.5",
   "fren_degeri": null,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 0.3459,
   "tepe_yavaslama_2ms_m_s2": 0.3463,
   "ort_yavaslama_m_s2": 0.3565,
   "durma_suresi_s": 1.111,
   "durma_yolu_m": 0.2182,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 122.9425,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0006,
   "en_buyuk_egim_derece": 0.0002,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6834,
    "pay": 10.6489,
    "bosalan_aks_beklenen_N": 123.396,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "acil_stop",
   "yon": "geri",
   "poz": "ev",
   "takim": "mu_0.5",
   "fren_degeri": null,
   "v0_m_s": -0.3961,
   "tepe_yavaslama_m_s2": 0.346,
   "tepe_yavaslama_2ms_m_s2": 0.3463,
   "ort_yavaslama_m_s2": 0.3565,
   "durma_suresi_s": 1.111,
   "durma_yolu_m": 0.2182,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 121.5874,
   "bosalan_aks_en_az_N": 108.3325,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0006,
   "en_buyuk_egim_derece": 0.0002,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.2896,
    "pay": 9.5088,
    "bosalan_aks_beklenen_N": 108.7994,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "dur",
   "yon": "ileri",
   "poz": "ev",
   "takim": "durma_9kgcm",
   "fren_degeri": null,
   "v0_m_s": 0.3527,
   "tepe_yavaslama_m_s2": 1.221,
   "tepe_yavaslama_2ms_m_s2": 1.2417,
   "ort_yavaslama_m_s2": 0.7961,
   "durma_suresi_s": 0.443,
   "durma_yolu_m": 0.0717,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 90.402,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.002,
   "en_buyuk_egim_derece": 0.0006,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 3.0173,
    "bosalan_aks_beklenen_N": 91.0475,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "dur",
   "yon": "geri",
   "poz": "ev",
   "takim": "durma_9kgcm",
   "fren_degeri": null,
   "v0_m_s": -0.3527,
   "tepe_yavaslama_m_s2": 1.221,
   "tepe_yavaslama_2ms_m_s2": 1.2417,
   "ort_yavaslama_m_s2": 0.7961,
   "durma_suresi_s": 0.443,
   "durma_yolu_m": 0.0717,
   "son_hiz_m_s": -0.0,
   "bosalan_aks_statik_N": 121.5874,
   "bosalan_aks_en_az_N": 75.8089,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0022,
   "en_buyuk_egim_derece": 0.0007,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.2893,
    "pay": 2.6939,
    "bosalan_aks_beklenen_N": 76.4536,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "bekci",
   "yon": "ileri",
   "poz": "ev",
   "takim": "durma_9kgcm",
   "fren_degeri": null,
   "v0_m_s": 0.3527,
   "tepe_yavaslama_m_s2": 1.8832,
   "tepe_yavaslama_2ms_m_s2": 1.898,
   "ort_yavaslama_m_s2": 0.9716,
   "durma_suresi_s": 0.363,
   "durma_yolu_m": 0.0471,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 65.4,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0028,
   "en_buyuk_egim_derece": 0.0009,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 1.9563,
    "bosalan_aks_beklenen_N": 66.57,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "bekci",
   "yon": "geri",
   "poz": "ev",
   "takim": "durma_9kgcm",
   "fren_degeri": null,
   "v0_m_s": -0.3527,
   "tepe_yavaslama_m_s2": 1.8832,
   "tepe_yavaslama_2ms_m_s2": 1.898,
   "ort_yavaslama_m_s2": 0.9716,
   "durma_suresi_s": 0.363,
   "durma_yolu_m": 0.0471,
   "son_hiz_m_s": -0.0,
   "bosalan_aks_statik_N": 121.5874,
   "bosalan_aks_en_az_N": 50.8156,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0031,
   "en_buyuk_egim_derece": 0.0009,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.2893,
    "pay": 1.7467,
    "bosalan_aks_beklenen_N": 51.976,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "acil_stop",
   "yon": "ileri",
   "poz": "ev",
   "takim": "durma_9kgcm",
   "fren_degeri": null,
   "v0_m_s": 0.3527,
   "tepe_yavaslama_m_s2": 0.3459,
   "tepe_yavaslama_2ms_m_s2": 0.3463,
   "ort_yavaslama_m_s2": 0.357,
   "durma_suresi_s": 0.988,
   "durma_yolu_m": 0.1731,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 122.9424,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0006,
   "en_buyuk_egim_derece": 0.0002,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6834,
    "pay": 10.649,
    "bosalan_aks_beklenen_N": 123.396,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "acil_stop",
   "yon": "geri",
   "poz": "ev",
   "takim": "durma_9kgcm",
   "fren_degeri": null,
   "v0_m_s": -0.3527,
   "tepe_yavaslama_m_s2": 0.346,
   "tepe_yavaslama_2ms_m_s2": 0.3463,
   "ort_yavaslama_m_s2": 0.357,
   "durma_suresi_s": 0.988,
   "durma_yolu_m": 0.1731,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 121.5874,
   "bosalan_aks_en_az_N": 108.3323,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0006,
   "en_buyuk_egim_derece": 0.0002,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.2896,
    "pay": 9.5088,
    "bosalan_aks_beklenen_N": 108.7994,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "dur",
   "yon": "ileri",
   "poz": "ev",
   "takim": "disli_0.2",
   "fren_degeri": null,
   "v0_m_s": 0.3675,
   "tepe_yavaslama_m_s2": 1.7667,
   "tepe_yavaslama_2ms_m_s2": 1.8371,
   "ort_yavaslama_m_s2": 1.3172,
   "durma_suresi_s": 0.279,
   "durma_yolu_m": 0.0516,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 69.1036,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0028,
   "en_buyuk_egim_derece": 0.0009,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 2.0853,
    "bosalan_aks_beklenen_N": 70.8764,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "dur",
   "yon": "geri",
   "poz": "ev",
   "takim": "disli_0.2",
   "fren_degeri": null,
   "v0_m_s": -0.3675,
   "tepe_yavaslama_m_s2": 1.7666,
   "tepe_yavaslama_2ms_m_s2": 1.837,
   "ort_yavaslama_m_s2": 1.3172,
   "durma_suresi_s": 0.279,
   "durma_yolu_m": 0.0516,
   "son_hiz_m_s": -0.0,
   "bosalan_aks_statik_N": 121.5874,
   "bosalan_aks_en_az_N": 54.5119,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0031,
   "en_buyuk_egim_derece": 0.0009,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.2893,
    "pay": 1.8619,
    "bosalan_aks_beklenen_N": 56.2845,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "bekci",
   "yon": "ileri",
   "poz": "ev",
   "takim": "disli_0.2",
   "fren_degeri": null,
   "v0_m_s": 0.3675,
   "tepe_yavaslama_m_s2": 3.2342,
   "tepe_yavaslama_2ms_m_s2": 7.633,
   "ort_yavaslama_m_s2": 1.9547,
   "durma_suresi_s": 0.188,
   "durma_yolu_m": 0.026,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 0.0,
   "bosalan_aks_sifir_ms": 60.0,
   "teker_kalkma_mm": 0.0369,
   "en_buyuk_egim_derece": 0.0065,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 1.1391,
    "bosalan_aks_beklenen_N": 16.6316,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "bekci",
   "yon": "geri",
   "poz": "ev",
   "takim": "disli_0.2",
   "fren_degeri": null,
   "v0_m_s": -0.3675,
   "tepe_yavaslama_m_s2": 3.0977,
   "tepe_yavaslama_2ms_m_s2": 6.0781,
   "ort_yavaslama_m_s2": 1.8943,
   "durma_suresi_s": 0.194,
   "durma_yolu_m": 0.0275,
   "son_hiz_m_s": -0.0,
   "bosalan_aks_statik_N": 121.5874,
   "bosalan_aks_en_az_N": 0.0,
   "bosalan_aks_sifir_ms": 77.0,
   "teker_kalkma_mm": 0.0266,
   "en_buyuk_egim_derece": 0.0048,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.2893,
    "pay": 1.0619,
    "bosalan_aks_beklenen_N": 7.0838,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "acil_stop",
   "yon": "ileri",
   "poz": "ev",
   "takim": "disli_0.2",
   "fren_degeri": null,
   "v0_m_s": 0.3675,
   "tepe_yavaslama_m_s2": 0.6496,
   "tepe_yavaslama_2ms_m_s2": 0.6503,
   "ort_yavaslama_m_s2": 0.667,
   "durma_suresi_s": 0.551,
   "durma_yolu_m": 0.0999,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 111.313,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.001,
   "en_buyuk_egim_derece": 0.0003,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6834,
    "pay": 5.67,
    "bosalan_aks_beklenen_N": 112.1687,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "acil_stop",
   "yon": "geri",
   "poz": "ev",
   "takim": "disli_0.2",
   "fren_degeri": null,
   "v0_m_s": -0.3675,
   "tepe_yavaslama_m_s2": 0.6497,
   "tepe_yavaslama_2ms_m_s2": 0.6504,
   "ort_yavaslama_m_s2": 0.667,
   "durma_suresi_s": 0.551,
   "durma_yolu_m": 0.0999,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 121.5874,
   "bosalan_aks_en_az_N": 96.7004,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0012,
   "en_buyuk_egim_derece": 0.0004,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.2896,
    "pay": 5.0633,
    "bosalan_aks_beklenen_N": 97.5716,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "dur",
   "yon": "ileri",
   "poz": "ev",
   "takim": "atalet_0",
   "fren_degeri": null,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 1.8417,
   "tepe_yavaslama_2ms_m_s2": 1.9361,
   "ort_yavaslama_m_s2": 1.3337,
   "durma_suresi_s": 0.297,
   "durma_yolu_m": 0.056,
   "son_hiz_m_s": -0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 65.7575,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.003,
   "en_buyuk_egim_derece": 0.001,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 2.0004,
    "bosalan_aks_beklenen_N": 68.1048,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "dur",
   "yon": "geri",
   "poz": "ev",
   "takim": "atalet_0",
   "fren_degeri": null,
   "v0_m_s": -0.3961,
   "tepe_yavaslama_m_s2": 1.8416,
   "tepe_yavaslama_2ms_m_s2": 1.936,
   "ort_yavaslama_m_s2": 1.3337,
   "durma_suresi_s": 0.297,
   "durma_yolu_m": 0.056,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 121.5874,
   "bosalan_aks_en_az_N": 51.1642,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0033,
   "en_buyuk_egim_derece": 0.001,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.2893,
    "pay": 1.7861,
    "bosalan_aks_beklenen_N": 53.5143,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "bekci",
   "yon": "ileri",
   "poz": "ev",
   "takim": "atalet_0",
   "fren_degeri": null,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 3.2499,
   "tepe_yavaslama_2ms_m_s2": 5.2709,
   "ort_yavaslama_m_s2": 1.8772,
   "durma_suresi_s": 0.211,
   "durma_yolu_m": 0.0301,
   "son_hiz_m_s": -0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 0.0,
   "bosalan_aks_sifir_ms": 38.0,
   "teker_kalkma_mm": 0.0198,
   "en_buyuk_egim_derece": 0.0036,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 1.1336,
    "bosalan_aks_beklenen_N": 16.0527,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "bekci",
   "yon": "geri",
   "poz": "ev",
   "takim": "atalet_0",
   "fren_degeri": null,
   "v0_m_s": -0.3961,
   "tepe_yavaslama_m_s2": 3.4369,
   "tepe_yavaslama_2ms_m_s2": 5.2587,
   "ort_yavaslama_m_s2": 1.8087,
   "durma_suresi_s": 0.219,
   "durma_yolu_m": 0.0322,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 121.5874,
   "bosalan_aks_en_az_N": 0.0,
   "bosalan_aks_sifir_ms": 55.0,
   "teker_kalkma_mm": 0.0343,
   "en_buyuk_egim_derece": 0.0059,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.2893,
    "pay": 0.9571,
    "bosalan_aks_beklenen_N": -5.4549,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "acil_stop",
   "yon": "ileri",
   "poz": "ev",
   "takim": "atalet_0",
   "fren_degeri": null,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 0.4107,
   "tepe_yavaslama_2ms_m_s2": 0.4107,
   "ort_yavaslama_m_s2": 0.425,
   "durma_suresi_s": 0.932,
   "durma_yolu_m": 0.183,
   "son_hiz_m_s": -0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 120.4693,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0007,
   "en_buyuk_egim_derece": 0.0002,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6834,
    "pay": 8.9695,
    "bosalan_aks_beklenen_N": 121.002,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "acil_stop",
   "yon": "geri",
   "poz": "ev",
   "takim": "atalet_0",
   "fren_degeri": null,
   "v0_m_s": -0.3961,
   "tepe_yavaslama_m_s2": 0.4107,
   "tepe_yavaslama_2ms_m_s2": 0.4107,
   "ort_yavaslama_m_s2": 0.425,
   "durma_suresi_s": 0.932,
   "durma_yolu_m": 0.183,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 121.5874,
   "bosalan_aks_en_az_N": 105.8616,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0007,
   "en_buyuk_egim_derece": 0.0002,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.2896,
    "pay": 8.0106,
    "bosalan_aks_beklenen_N": 106.4077,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  }
 ],
 "fren_egrisi": [
  {
   "durus": "dur",
   "yon": "ileri",
   "poz": "ev",
   "takim": "ana",
   "fren_degeri": 1.0,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 1.0819,
   "tepe_yavaslama_2ms_m_s2": 1.1253,
   "ort_yavaslama_m_s2": 0.8921,
   "durma_suresi_s": 0.444,
   "durma_yolu_m": 0.0888,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 95.0651,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0018,
   "en_buyuk_egim_derece": 0.0006,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 3.4053,
    "bosalan_aks_beklenen_N": 96.191,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "dur",
   "yon": "ileri",
   "poz": "ev",
   "takim": "ana",
   "fren_degeri": 1.8,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 1.7667,
   "tepe_yavaslama_2ms_m_s2": 1.8371,
   "ort_yavaslama_m_s2": 1.2076,
   "durma_suresi_s": 0.328,
   "durma_yolu_m": 0.0601,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 69.1036,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0028,
   "en_buyuk_egim_derece": 0.0009,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 2.0853,
    "bosalan_aks_beklenen_N": 70.8764,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "dur",
   "yon": "ileri",
   "poz": "ev",
   "takim": "ana",
   "fren_degeri": 2.5,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 2.1908,
   "tepe_yavaslama_2ms_m_s2": 2.2771,
   "ort_yavaslama_m_s2": 1.3565,
   "durma_suresi_s": 0.292,
   "durma_yolu_m": 0.0499,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 52.9779,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0035,
   "en_buyuk_egim_derece": 0.0011,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 1.6817,
    "bosalan_aks_beklenen_N": 55.2014,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "dur",
   "yon": "ileri",
   "poz": "ev",
   "takim": "ana",
   "fren_degeri": 3.0,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 2.4695,
   "tepe_yavaslama_2ms_m_s2": 2.5661,
   "ort_yavaslama_m_s2": 1.4248,
   "durma_suresi_s": 0.278,
   "durma_yolu_m": 0.0457,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 42.4164,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0039,
   "en_buyuk_egim_derece": 0.0013,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 1.4919,
    "bosalan_aks_beklenen_N": 44.8986,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "dur",
   "yon": "ileri",
   "poz": "ev",
   "takim": "ana",
   "fren_degeri": 4.0,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 2.7075,
   "tepe_yavaslama_2ms_m_s2": 3.4849,
   "ort_yavaslama_m_s2": 1.5118,
   "durma_suresi_s": 0.262,
   "durma_yolu_m": 0.0407,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 0.0,
   "bosalan_aks_sifir_ms": 10.0,
   "teker_kalkma_mm": 0.0071,
   "en_buyuk_egim_derece": 0.0018,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 1.3607,
    "bosalan_aks_beklenen_N": 36.1006,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  }
 ],
 "bekci_duyarlilik": [
  {
   "durus": "bekci",
   "yon": "ileri",
   "poz": "ev",
   "takim": "ana",
   "fren_degeri": null,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 3.2377,
   "tepe_yavaslama_2ms_m_s2": 7.6507,
   "ort_yavaslama_m_s2": 1.6643,
   "durma_suresi_s": 0.238,
   "durma_yolu_m": 0.0322,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 0.0,
   "bosalan_aks_sifir_ms": 61.0,
   "teker_kalkma_mm": 0.0373,
   "en_buyuk_egim_derece": 0.0065,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 1.1379,
    "bosalan_aks_beklenen_N": 16.5011,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "bekci",
   "yon": "ileri",
   "poz": "ev",
   "takim": "durma_15kgcm",
   "fren_degeri": null,
   "v0_m_s": 0.3831,
   "tepe_yavaslama_m_s2": 2.868,
   "tepe_yavaslama_2ms_m_s2": 4.1451,
   "ort_yavaslama_m_s2": 1.3681,
   "durma_suresi_s": 0.28,
   "durma_yolu_m": 0.0364,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 0.0,
   "bosalan_aks_sifir_ms": 25.0,
   "teker_kalkma_mm": 0.0093,
   "en_buyuk_egim_derece": 0.0021,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 1.2845,
    "bosalan_aks_beklenen_N": 30.1668,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "bekci",
   "yon": "ileri",
   "poz": "ev",
   "takim": "durma_9kgcm",
   "fren_degeri": null,
   "v0_m_s": 0.3527,
   "tepe_yavaslama_m_s2": 1.8832,
   "tepe_yavaslama_2ms_m_s2": 1.898,
   "ort_yavaslama_m_s2": 0.9716,
   "durma_suresi_s": 0.363,
   "durma_yolu_m": 0.0471,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 65.4,
   "bosalan_aks_sifir_ms": 0.0,
   "teker_kalkma_mm": 0.0028,
   "en_buyuk_egim_derece": 0.0009,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 1.9563,
    "bosalan_aks_beklenen_N": 66.57,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "bekci",
   "yon": "ileri",
   "poz": "ev",
   "takim": "solref_0.002",
   "fren_degeri": null,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 3.9361,
   "tepe_yavaslama_2ms_m_s2": 10.7312,
   "ort_yavaslama_m_s2": 1.6643,
   "durma_suresi_s": 0.238,
   "durma_yolu_m": 0.0323,
   "son_hiz_m_s": 0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 0.0,
   "bosalan_aks_sifir_ms": 71.0,
   "teker_kalkma_mm": 0.0626,
   "en_buyuk_egim_derece": 0.01,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 0.936,
    "bosalan_aks_beklenen_N": -9.3152,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "bekci",
   "yon": "ileri",
   "poz": "ev",
   "takim": "solref_0.008",
   "fren_degeri": null,
   "v0_m_s": 0.396,
   "tepe_yavaslama_m_s2": 3.4319,
   "tepe_yavaslama_2ms_m_s2": 6.0814,
   "ort_yavaslama_m_s2": 1.664,
   "durma_suresi_s": 0.238,
   "durma_yolu_m": 0.0322,
   "son_hiz_m_s": -0.0,
   "bosalan_aks_statik_N": 136.1818,
   "bosalan_aks_en_az_N": 0.0,
   "bosalan_aks_sifir_ms": 48.0,
   "teker_kalkma_mm": 0.0581,
   "en_buyuk_egim_derece": 0.0108,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 1.0735,
    "bosalan_aks_beklenen_N": 9.3238,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  },
  {
   "durus": "bekci",
   "yon": "ileri",
   "poz": "ev",
   "takim": "dt_0.5ms",
   "fren_degeri": null,
   "v0_m_s": 0.3961,
   "tepe_yavaslama_m_s2": 3.4876,
   "tepe_yavaslama_2ms_m_s2": 7.8798,
   "ort_yavaslama_m_s2": 1.6608,
   "durma_suresi_s": 0.2385,
   "durma_yolu_m": 0.0323,
   "son_hiz_m_s": -0.0,
   "bosalan_aks_statik_N": 136.1815,
   "bosalan_aks_en_az_N": 0.0,
   "bosalan_aks_sifir_ms": 60.0,
   "teker_kalkma_mm": 0.0149,
   "en_buyuk_egim_derece": 0.0031,
   "govde_zemine_degdi": false,
   "el_hesabi": {
    "devrilme_ivmesi_m_s2": 3.6841,
    "pay": 1.0563,
    "bosalan_aks_beklenen_N": 7.2649,
    "formul": "a_dev = g d / h; N_aks = N0 - m a h / L (L = 0,37 m dingil)"
   }
  }
 ],
 "acil_stop_araligi": [
  {
   "yansiyan_atalet_kgm2": 0.0,
   "disli_surtunme_Nm": 0.05,
   "v0_m_s": 0.3961,
   "durma_yolu_m": 0.183,
   "durma_suresi_s": 0.932,
   "ort_yavaslama_m_s2": 0.425
  },
  {
   "yansiyan_atalet_kgm2": 0.0,
   "disli_surtunme_Nm": 0.2,
   "v0_m_s": 0.3675,
   "durma_yolu_m": 0.0837,
   "durma_suresi_s": 0.463,
   "ort_yavaslama_m_s2": 0.7937
  },
  {
   "yansiyan_atalet_kgm2": 0.005,
   "disli_surtunme_Nm": 0.05,
   "v0_m_s": 0.3961,
   "durma_yolu_m": 0.2182,
   "durma_suresi_s": 1.111,
   "ort_yavaslama_m_s2": 0.3565
  },
  {
   "yansiyan_atalet_kgm2": 0.005,
   "disli_surtunme_Nm": 0.2,
   "v0_m_s": 0.3675,
   "durma_yolu_m": 0.0999,
   "durma_suresi_s": 0.551,
   "ort_yavaslama_m_s2": 0.667
  },
  {
   "yansiyan_atalet_kgm2": 0.01,
   "disli_surtunme_Nm": 0.05,
   "v0_m_s": 0.3961,
   "durma_yolu_m": 0.2537,
   "durma_suresi_s": 1.291,
   "ort_yavaslama_m_s2": 0.3068
  },
  {
   "yansiyan_atalet_kgm2": 0.01,
   "disli_surtunme_Nm": 0.2,
   "v0_m_s": 0.3675,
   "durma_yolu_m": 0.116,
   "durma_suresi_s": 0.639,
   "ort_yavaslama_m_s2": 0.5751
  },
  {
   "yansiyan_atalet_kgm2": 0.015,
   "disli_surtunme_Nm": 0.05,
   "v0_m_s": 0.3961,
   "durma_yolu_m": 0.2889,
   "durma_suresi_s": 1.471,
   "ort_yavaslama_m_s2": 0.2693
  },
  {
   "yansiyan_atalet_kgm2": 0.015,
   "disli_surtunme_Nm": 0.2,
   "v0_m_s": 0.3675,
   "durma_yolu_m": 0.1321,
   "durma_suresi_s": 0.727,
   "ort_yavaslama_m_s2": 0.5055
  }
 ],
 "not_": "tepe yavaşlama AM hızının 10 ms (±5 adım) merkezi farkından, tepe_yavaslama_2ms ±1 adımdan; boşalan aks = frende yükü azalan aks (ileri giderken arka); teker_kalkma_mm boşalan aks tekerlerinin merkez yüksekliği artışı"
}
```

## kol

```json
{
 "izgara": [
  {
   "tek_kol": false,
   "s1": -45,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0164,
    0.0,
    0.523
   ],
   "d_on": 0.2014,
   "d_arka": 0.1686,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.7768,
    "geri": 3.1634,
    "yan": 4.0509
   },
   "pay_fren_1_8": {
    "ileri": 2.0982,
    "geri": 1.7574,
    "yan": 2.2505
   },
   "rampa5_geri_a_dev": 2.2963
  },
  {
   "tek_kol": false,
   "s1": -45,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0135,
    0.0,
    0.5234
   ],
   "d_on": 0.1985,
   "d_arka": 0.1715,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.7197,
    "geri": 3.2151,
    "yan": 4.0478
   },
   "pay_fren_1_8": {
    "ileri": 2.0665,
    "geri": 1.7862,
    "yan": 2.2488
   },
   "rampa5_geri_a_dev": 2.3478
  },
  {
   "tek_kol": false,
   "s1": -45,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0103,
    0.0,
    0.5291
   ],
   "d_on": 0.1953,
   "d_arka": 0.1747,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6207,
    "geri": 3.2397,
    "yan": 4.0044
   },
   "pay_fren_1_8": {
    "ileri": 2.0115,
    "geri": 1.7999,
    "yan": 2.2247
   },
   "rampa5_geri_a_dev": 2.3724
  },
  {
   "tek_kol": false,
   "s1": -45,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.009,
    0.0,
    0.5278
   ],
   "d_on": 0.194,
   "d_arka": 0.176,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6061,
    "geri": 3.2705,
    "yan": 4.0138
   },
   "pay_fren_1_8": {
    "ileri": 2.0034,
    "geri": 1.8169,
    "yan": 2.2299
   },
   "rampa5_geri_a_dev": 2.403
  },
  {
   "tek_kol": false,
   "s1": -30,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0146,
    0.0,
    0.5217
   ],
   "d_on": 0.1996,
   "d_arka": 0.1704,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.7543,
    "geri": 3.2038,
    "yan": 4.0613
   },
   "pay_fren_1_8": {
    "ileri": 2.0857,
    "geri": 1.7799,
    "yan": 2.2563
   },
   "rampa5_geri_a_dev": 2.3366
  },
  {
   "tek_kol": false,
   "s1": -30,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0119,
    0.0,
    0.5228
   ],
   "d_on": 0.1969,
   "d_arka": 0.1731,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6957,
    "geri": 3.2472,
    "yan": 4.0525
   },
   "pay_fren_1_8": {
    "ileri": 2.0531,
    "geri": 1.804,
    "yan": 2.2514
   },
   "rampa5_geri_a_dev": 2.3798
  },
  {
   "tek_kol": false,
   "s1": -30,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0103,
    0.0,
    0.5291
   ],
   "d_on": 0.1953,
   "d_arka": 0.1747,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6217,
    "geri": 3.2384,
    "yan": 4.0042
   },
   "pay_fren_1_8": {
    "ileri": 2.0121,
    "geri": 1.7991,
    "yan": 2.2245
   },
   "rampa5_geri_a_dev": 2.3711
  },
  {
   "tek_kol": false,
   "s1": -30,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0088,
    0.0,
    0.5282
   ],
   "d_on": 0.1938,
   "d_arka": 0.1762,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5995,
    "geri": 3.272,
    "yan": 4.0108
   },
   "pay_fren_1_8": {
    "ileri": 1.9997,
    "geri": 1.8178,
    "yan": 2.2282
   },
   "rampa5_geri_a_dev": 2.4046
  },
  {
   "tek_kol": false,
   "s1": -15,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0126,
    0.0,
    0.5208
   ],
   "d_on": 0.1976,
   "d_arka": 0.1724,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.7226,
    "geri": 3.2468,
    "yan": 4.068
   },
   "pay_fren_1_8": {
    "ileri": 2.0681,
    "geri": 1.8038,
    "yan": 2.26
   },
   "rampa5_geri_a_dev": 2.3794
  },
  {
   "tek_kol": false,
   "s1": -15,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0103,
    0.0,
    0.5226
   ],
   "d_on": 0.1953,
   "d_arka": 0.1747,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6667,
    "geri": 3.2788,
    "yan": 4.054
   },
   "pay_fren_1_8": {
    "ileri": 2.037,
    "geri": 1.8215,
    "yan": 2.2522
   },
   "rampa5_geri_a_dev": 2.4113
  },
  {
   "tek_kol": false,
   "s1": -15,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0104,
    0.0,
    0.5291
   ],
   "d_on": 0.1954,
   "d_arka": 0.1746,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6229,
    "geri": 3.2371,
    "yan": 4.0041
   },
   "pay_fren_1_8": {
    "ileri": 2.0127,
    "geri": 1.7984,
    "yan": 2.2245
   },
   "rampa5_geri_a_dev": 2.3697
  },
  {
   "tek_kol": false,
   "s1": -15,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0087,
    0.0,
    0.5287
   ],
   "d_on": 0.1937,
   "d_arka": 0.1763,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5946,
    "geri": 3.2713,
    "yan": 4.0076
   },
   "pay_fren_1_8": {
    "ileri": 1.997,
    "geri": 1.8174,
    "yan": 2.2264
   },
   "rampa5_geri_a_dev": 2.4039
  },
  {
   "tek_kol": false,
   "s1": 0,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0105,
    0.0,
    0.5205
   ],
   "d_on": 0.1955,
   "d_arka": 0.1745,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6842,
    "geri": 3.2893,
    "yan": 4.0704
   },
   "pay_fren_1_8": {
    "ileri": 2.0468,
    "geri": 1.8274,
    "yan": 2.2613
   },
   "rampa5_geri_a_dev": 2.4218
  },
  {
   "tek_kol": false,
   "s1": 0,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0087,
    0.0,
    0.5228
   ],
   "d_on": 0.1937,
   "d_arka": 0.1763,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6348,
    "geri": 3.3076,
    "yan": 4.0522
   },
   "pay_fren_1_8": {
    "ileri": 2.0193,
    "geri": 1.8376,
    "yan": 2.2512
   },
   "rampa5_geri_a_dev": 2.44
  },
  {
   "tek_kol": false,
   "s1": 0,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0105,
    0.0,
    0.5291
   ],
   "d_on": 0.1955,
   "d_arka": 0.1745,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6243,
    "geri": 3.2358,
    "yan": 4.0042
   },
   "pay_fren_1_8": {
    "ileri": 2.0135,
    "geri": 1.7977,
    "yan": 2.2246
   },
   "rampa5_geri_a_dev": 2.3685
  },
  {
   "tek_kol": false,
   "s1": 0,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0087,
    0.0,
    0.5291
   ],
   "d_on": 0.1937,
   "d_arka": 0.1763,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5917,
    "geri": 3.2684,
    "yan": 4.0042
   },
   "pay_fren_1_8": {
    "ileri": 1.9954,
    "geri": 1.8158,
    "yan": 2.2246
   },
   "rampa5_geri_a_dev": 2.401
  },
  {
   "tek_kol": false,
   "s1": 15,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0083,
    0.0,
    0.5208
   ],
   "d_on": 0.1933,
   "d_arka": 0.1767,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6416,
    "geri": 3.3283,
    "yan": 4.0683
   },
   "pay_fren_1_8": {
    "ileri": 2.0231,
    "geri": 1.8491,
    "yan": 2.2602
   },
   "rampa5_geri_a_dev": 2.4607
  },
  {
   "tek_kol": false,
   "s1": 15,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0072,
    0.0,
    0.5235
   ],
   "d_on": 0.1922,
   "d_arka": 0.1778,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6022,
    "geri": 3.3316,
    "yan": 4.0472
   },
   "pay_fren_1_8": {
    "ileri": 2.0012,
    "geri": 1.8509,
    "yan": 2.2485
   },
   "rampa5_geri_a_dev": 2.464
  },
  {
   "tek_kol": false,
   "s1": 15,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0105,
    0.0,
    0.5291
   ],
   "d_on": 0.1955,
   "d_arka": 0.1745,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6257,
    "geri": 3.2348,
    "yan": 4.0044
   },
   "pay_fren_1_8": {
    "ileri": 2.0143,
    "geri": 1.7971,
    "yan": 2.2247
   },
   "rampa5_geri_a_dev": 2.3675
  },
  {
   "tek_kol": false,
   "s1": 15,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0088,
    0.0,
    0.5295
   ],
   "d_on": 0.1938,
   "d_arka": 0.1762,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5911,
    "geri": 3.2635,
    "yan": 4.001
   },
   "pay_fren_1_8": {
    "ileri": 1.9951,
    "geri": 1.813,
    "yan": 2.2228
   },
   "rampa5_geri_a_dev": 2.3961
  },
  {
   "tek_kol": false,
   "s1": 30,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0063,
    0.0,
    0.5216
   ],
   "d_on": 0.1913,
   "d_arka": 0.1787,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5979,
    "geri": 3.3611,
    "yan": 4.0619
   },
   "pay_fren_1_8": {
    "ileri": 1.9988,
    "geri": 1.8673,
    "yan": 2.2566
   },
   "rampa5_geri_a_dev": 2.4933
  },
  {
   "tek_kol": false,
   "s1": 30,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0059,
    0.0,
    0.5245
   ],
   "d_on": 0.1909,
   "d_arka": 0.1791,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5713,
    "geri": 3.3492,
    "yan": 4.0395
   },
   "pay_fren_1_8": {
    "ileri": 1.9841,
    "geri": 1.8607,
    "yan": 2.2442
   },
   "rampa5_geri_a_dev": 2.4815
  },
  {
   "tek_kol": false,
   "s1": 30,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0106,
    0.0,
    0.529
   ],
   "d_on": 0.1956,
   "d_arka": 0.1744,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.627,
    "geri": 3.2341,
    "yan": 4.0047
   },
   "pay_fren_1_8": {
    "ileri": 2.015,
    "geri": 1.7967,
    "yan": 2.2249
   },
   "rampa5_geri_a_dev": 2.3668
  },
  {
   "tek_kol": false,
   "s1": 30,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0091,
    0.0,
    0.5299
   ],
   "d_on": 0.1941,
   "d_arka": 0.1759,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5928,
    "geri": 3.2569,
    "yan": 3.9981
   },
   "pay_fren_1_8": {
    "ileri": 1.996,
    "geri": 1.8094,
    "yan": 2.2212
   },
   "rampa5_geri_a_dev": 2.3895
  },
  {
   "tek_kol": false,
   "s1": 45,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0046,
    0.0,
    0.5229
   ],
   "d_on": 0.1896,
   "d_arka": 0.1804,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5562,
    "geri": 3.3853,
    "yan": 4.0517
   },
   "pay_fren_1_8": {
    "ileri": 1.9757,
    "geri": 1.8807,
    "yan": 2.251
   },
   "rampa5_geri_a_dev": 2.5175
  },
  {
   "tek_kol": false,
   "s1": 45,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.005,
    0.0,
    0.5258
   ],
   "d_on": 0.19,
   "d_arka": 0.18,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5443,
    "geri": 3.3591,
    "yan": 4.0295
   },
   "pay_fren_1_8": {
    "ileri": 1.969,
    "geri": 1.8662,
    "yan": 2.2386
   },
   "rampa5_geri_a_dev": 2.4914
  },
  {
   "tek_kol": false,
   "s1": 45,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0106,
    0.0,
    0.529
   ],
   "d_on": 0.1956,
   "d_arka": 0.1744,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6281,
    "geri": 3.2336,
    "yan": 4.0052
   },
   "pay_fren_1_8": {
    "ileri": 2.0156,
    "geri": 1.7965,
    "yan": 2.2251
   },
   "rampa5_geri_a_dev": 2.3663
  },
  {
   "tek_kol": false,
   "s1": 45,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0094,
    0.0,
    0.5302
   ],
   "d_on": 0.1944,
   "d_arka": 0.1756,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5966,
    "geri": 3.2491,
    "yan": 3.9958
   },
   "pay_fren_1_8": {
    "ileri": 1.9981,
    "geri": 1.805,
    "yan": 2.2199
   },
   "rampa5_geri_a_dev": 2.3817
  },
  {
   "tek_kol": false,
   "s1": 60,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0032,
    0.0,
    0.5246
   ],
   "d_on": 0.1882,
   "d_arka": 0.1818,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5195,
    "geri": 3.3993,
    "yan": 4.0385
   },
   "pay_fren_1_8": {
    "ileri": 1.9553,
    "geri": 1.8885,
    "yan": 2.2436
   },
   "rampa5_geri_a_dev": 2.5314
  },
  {
   "tek_kol": false,
   "s1": 60,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0044,
    0.0,
    0.5273
   ],
   "d_on": 0.1894,
   "d_arka": 0.1806,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5228,
    "geri": 3.3608,
    "yan": 4.0179
   },
   "pay_fren_1_8": {
    "ileri": 1.9571,
    "geri": 1.8671,
    "yan": 2.2322
   },
   "rampa5_geri_a_dev": 2.493
  },
  {
   "tek_kol": false,
   "s1": 60,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0107,
    0.0,
    0.5289
   ],
   "d_on": 0.1957,
   "d_arka": 0.1743,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.629,
    "geri": 3.2336,
    "yan": 4.0056
   },
   "pay_fren_1_8": {
    "ileri": 2.0161,
    "geri": 1.7964,
    "yan": 2.2254
   },
   "rampa5_geri_a_dev": 2.3663
  },
  {
   "tek_kol": false,
   "s1": 60,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0098,
    0.0,
    0.5304
   ],
   "d_on": 0.1948,
   "d_arka": 0.1752,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6024,
    "geri": 3.2405,
    "yan": 3.9942
   },
   "pay_fren_1_8": {
    "ileri": 2.0013,
    "geri": 1.8003,
    "yan": 2.219
   },
   "rampa5_geri_a_dev": 2.3732
  },
  {
   "tek_kol": false,
   "s1": 75,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0024,
    0.0,
    0.5266
   ],
   "d_on": 0.1874,
   "d_arka": 0.1826,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.4903,
    "geri": 3.4022,
    "yan": 4.0231
   },
   "pay_fren_1_8": {
    "ileri": 1.939,
    "geri": 1.8901,
    "yan": 2.2351
   },
   "rampa5_geri_a_dev": 2.5343
  },
  {
   "tek_kol": false,
   "s1": 75,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0042,
    0.0,
    0.5289
   ],
   "d_on": 0.1892,
   "d_arka": 0.1808,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5084,
    "geri": 3.3541,
    "yan": 4.0056
   },
   "pay_fren_1_8": {
    "ileri": 1.9491,
    "geri": 1.8634,
    "yan": 2.2253
   },
   "rampa5_geri_a_dev": 2.4863
  },
  {
   "tek_kol": false,
   "s1": 75,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0107,
    0.0,
    0.5288
   ],
   "d_on": 0.1957,
   "d_arka": 0.1743,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6297,
    "geri": 3.2338,
    "yan": 4.0062
   },
   "pay_fren_1_8": {
    "ileri": 2.0165,
    "geri": 1.7966,
    "yan": 2.2257
   },
   "rampa5_geri_a_dev": 2.3665
  },
  {
   "tek_kol": false,
   "s1": 75,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0102,
    0.0,
    0.5305
   ],
   "d_on": 0.1952,
   "d_arka": 0.1748,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6096,
    "geri": 3.2319,
    "yan": 3.9934
   },
   "pay_fren_1_8": {
    "ileri": 2.0054,
    "geri": 1.7955,
    "yan": 2.2185
   },
   "rampa5_geri_a_dev": 2.3646
  },
  {
   "tek_kol": false,
   "s1": 90,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0021,
    0.0,
    0.5288
   ],
   "d_on": 0.1871,
   "d_arka": 0.1829,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.4704,
    "geri": 3.394,
    "yan": 4.0067
   },
   "pay_fren_1_8": {
    "ileri": 1.928,
    "geri": 1.8855,
    "yan": 2.2259
   },
   "rampa5_geri_a_dev": 2.5261
  },
  {
   "tek_kol": false,
   "s1": 90,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0044,
    0.0,
    0.5305
   ],
   "d_on": 0.1894,
   "d_arka": 0.1806,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.502,
    "geri": 3.3396,
    "yan": 3.9934
   },
   "pay_fren_1_8": {
    "ileri": 1.9456,
    "geri": 1.8554,
    "yan": 2.2186
   },
   "rampa5_geri_a_dev": 2.4719
  },
  {
   "tek_kol": false,
   "s1": 90,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0107,
    0.0,
    0.5288
   ],
   "d_on": 0.1957,
   "d_arka": 0.1743,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.63,
    "geri": 3.2344,
    "yan": 4.0067
   },
   "pay_fren_1_8": {
    "ileri": 2.0166,
    "geri": 1.7969,
    "yan": 2.2259
   },
   "rampa5_geri_a_dev": 2.3671
  },
  {
   "tek_kol": false,
   "s1": 90,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0107,
    0.0,
    0.5305
   ],
   "d_on": 0.1957,
   "d_arka": 0.1743,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6179,
    "geri": 3.2237,
    "yan": 3.9934
   },
   "pay_fren_1_8": {
    "ileri": 2.01,
    "geri": 1.791,
    "yan": 2.2186
   },
   "rampa5_geri_a_dev": 2.3565
  },
  {
   "tek_kol": false,
   "s1": 105,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0023,
    0.0,
    0.5309
   ],
   "d_on": 0.1873,
   "d_arka": 0.1827,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.4612,
    "geri": 3.3753,
    "yan": 3.9904
   },
   "pay_fren_1_8": {
    "ileri": 1.9229,
    "geri": 1.8751,
    "yan": 2.2169
   },
   "rampa5_geri_a_dev": 2.5074
  },
  {
   "tek_kol": false,
   "s1": 105,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.005,
    0.0,
    0.532
   ],
   "d_on": 0.19,
   "d_arka": 0.18,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.504,
    "geri": 3.3184,
    "yan": 3.9822
   },
   "pay_fren_1_8": {
    "ileri": 1.9467,
    "geri": 1.8436,
    "yan": 2.2123
   },
   "rampa5_geri_a_dev": 2.4508
  },
  {
   "tek_kol": false,
   "s1": 105,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0106,
    0.0,
    0.5287
   ],
   "d_on": 0.1956,
   "d_arka": 0.1744,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6299,
    "geri": 3.2353,
    "yan": 4.0072
   },
   "pay_fren_1_8": {
    "ileri": 2.0166,
    "geri": 1.7974,
    "yan": 2.2262
   },
   "rampa5_geri_a_dev": 2.368
  },
  {
   "tek_kol": false,
   "s1": 105,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0111,
    0.0,
    0.5304
   ],
   "d_on": 0.1961,
   "d_arka": 0.1739,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6267,
    "geri": 3.2166,
    "yan": 3.9944
   },
   "pay_fren_1_8": {
    "ileri": 2.0148,
    "geri": 1.787,
    "yan": 2.2191
   },
   "rampa5_geri_a_dev": 2.3493
  },
  {
   "tek_kol": false,
   "s1": 120,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0031,
    0.0,
    0.533
   ],
   "d_on": 0.1881,
   "d_arka": 0.1819,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.4631,
    "geri": 3.3475,
    "yan": 3.9753
   },
   "pay_fren_1_8": {
    "ileri": 1.9239,
    "geri": 1.8597,
    "yan": 2.2085
   },
   "rampa5_geri_a_dev": 2.4797
  },
  {
   "tek_kol": false,
   "s1": 120,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.006,
    0.0,
    0.5333
   ],
   "d_on": 0.191,
   "d_arka": 0.179,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5141,
    "geri": 3.2919,
    "yan": 3.9726
   },
   "pay_fren_1_8": {
    "ileri": 1.9523,
    "geri": 1.8288,
    "yan": 2.207
   },
   "rampa5_geri_a_dev": 2.4244
  },
  {
   "tek_kol": false,
   "s1": 120,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0106,
    0.0,
    0.5287
   ],
   "d_on": 0.1956,
   "d_arka": 0.1744,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6295,
    "geri": 3.2365,
    "yan": 4.0076
   },
   "pay_fren_1_8": {
    "ileri": 2.0164,
    "geri": 1.798,
    "yan": 2.2264
   },
   "rampa5_geri_a_dev": 2.3692
  },
  {
   "tek_kol": false,
   "s1": 120,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0115,
    0.0,
    0.5302
   ],
   "d_on": 0.1965,
   "d_arka": 0.1735,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6353,
    "geri": 3.2109,
    "yan": 3.9961
   },
   "pay_fren_1_8": {
    "ileri": 2.0196,
    "geri": 1.7839,
    "yan": 2.2201
   },
   "rampa5_geri_a_dev": 2.3437
  },
  {
   "tek_kol": false,
   "s1": 135,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0045,
    0.0,
    0.5347
   ],
   "d_on": 0.1895,
   "d_arka": 0.1805,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.4759,
    "geri": 3.3125,
    "yan": 3.9623
   },
   "pay_fren_1_8": {
    "ileri": 1.931,
    "geri": 1.8403,
    "yan": 2.2013
   },
   "rampa5_geri_a_dev": 2.4449
  },
  {
   "tek_kol": false,
   "s1": 135,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0073,
    0.0,
    0.5343
   ],
   "d_on": 0.1923,
   "d_arka": 0.1777,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5316,
    "geri": 3.262,
    "yan": 3.9653
   },
   "pay_fren_1_8": {
    "ileri": 1.962,
    "geri": 1.8122,
    "yan": 2.203
   },
   "rampa5_geri_a_dev": 2.3945
  },
  {
   "tek_kol": false,
   "s1": 135,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0105,
    0.0,
    0.5286
   ],
   "d_on": 0.1955,
   "d_arka": 0.1745,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6287,
    "geri": 3.2378,
    "yan": 4.0079
   },
   "pay_fren_1_8": {
    "ileri": 2.0159,
    "geri": 1.7988,
    "yan": 2.2266
   },
   "rampa5_geri_a_dev": 2.3705
  },
  {
   "tek_kol": false,
   "s1": 135,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0118,
    0.0,
    0.5299
   ],
   "d_on": 0.1968,
   "d_arka": 0.1732,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6432,
    "geri": 3.2072,
    "yan": 3.9985
   },
   "pay_fren_1_8": {
    "ileri": 2.024,
    "geri": 1.7818,
    "yan": 2.2214
   },
   "rampa5_geri_a_dev": 2.34
  },
  {
   "tek_kol": true,
   "s1": -45,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0134,
    0.0,
    0.5217
   ],
   "d_on": 0.1984,
   "d_arka": 0.1716,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.7306,
    "geri": 3.2262,
    "yan": 4.0606
   },
   "pay_fren_1_8": {
    "ileri": 2.0726,
    "geri": 1.7923,
    "yan": 2.2559
   },
   "rampa5_geri_a_dev": 2.3589
  },
  {
   "tek_kol": true,
   "s1": -45,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.012,
    0.0001,
    0.522
   ],
   "d_on": 0.197,
   "d_arka": 0.173,
   "d_yan": 0.2159,
   "a_dev": {
    "ileri": 3.702,
    "geri": 3.2521,
    "yan": 4.0571
   },
   "pay_fren_1_8": {
    "ileri": 2.0567,
    "geri": 1.8067,
    "yan": 2.254
   },
   "rampa5_geri_a_dev": 2.3847
  },
  {
   "tek_kol": true,
   "s1": -45,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0104,
    -0.0038,
    0.5248
   ],
   "d_on": 0.1954,
   "d_arka": 0.1746,
   "d_yan": 0.2122,
   "a_dev": {
    "ileri": 3.6522,
    "geri": 3.2643,
    "yan": 3.9673
   },
   "pay_fren_1_8": {
    "ileri": 2.029,
    "geri": 1.8135,
    "yan": 2.2041
   },
   "rampa5_geri_a_dev": 2.3969
  },
  {
   "tek_kol": true,
   "s1": -45,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0098,
    -0.0026,
    0.5242
   ],
   "d_on": 0.1948,
   "d_arka": 0.1752,
   "d_yan": 0.2134,
   "a_dev": {
    "ileri": 3.6449,
    "geri": 3.2798,
    "yan": 3.994
   },
   "pay_fren_1_8": {
    "ileri": 2.0249,
    "geri": 1.8221,
    "yan": 2.2189
   },
   "rampa5_geri_a_dev": 2.4123
  },
  {
   "tek_kol": true,
   "s1": -30,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0126,
    0.0,
    0.5211
   ],
   "d_on": 0.1976,
   "d_arka": 0.1724,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.7193,
    "geri": 3.2465,
    "yan": 4.0658
   },
   "pay_fren_1_8": {
    "ileri": 2.0663,
    "geri": 1.8036,
    "yan": 2.2588
   },
   "rampa5_geri_a_dev": 2.3791
  },
  {
   "tek_kol": true,
   "s1": -30,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0112,
    0.0001,
    0.5216
   ],
   "d_on": 0.1962,
   "d_arka": 0.1738,
   "d_yan": 0.2159,
   "a_dev": {
    "ileri": 3.6899,
    "geri": 3.2682,
    "yan": 4.0595
   },
   "pay_fren_1_8": {
    "ileri": 2.05,
    "geri": 1.8157,
    "yan": 2.2553
   },
   "rampa5_geri_a_dev": 2.4008
  },
  {
   "tek_kol": true,
   "s1": -30,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0104,
    -0.0038,
    0.5248
   ],
   "d_on": 0.1954,
   "d_arka": 0.1746,
   "d_yan": 0.2122,
   "a_dev": {
    "ileri": 3.6527,
    "geri": 3.2636,
    "yan": 3.9673
   },
   "pay_fren_1_8": {
    "ileri": 2.0293,
    "geri": 1.8131,
    "yan": 2.204
   },
   "rampa5_geri_a_dev": 2.3962
  },
  {
   "tek_kol": true,
   "s1": -30,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0096,
    -0.0026,
    0.5244
   ],
   "d_on": 0.1946,
   "d_arka": 0.1754,
   "d_yan": 0.2134,
   "a_dev": {
    "ileri": 3.6415,
    "geri": 3.2806,
    "yan": 3.9925
   },
   "pay_fren_1_8": {
    "ileri": 2.0231,
    "geri": 1.8226,
    "yan": 2.218
   },
   "rampa5_geri_a_dev": 2.4131
  },
  {
   "tek_kol": true,
   "s1": -15,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0116,
    0.0,
    0.5207
   ],
   "d_on": 0.1966,
   "d_arka": 0.1734,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.7034,
    "geri": 3.268,
    "yan": 4.0692
   },
   "pay_fren_1_8": {
    "ileri": 2.0574,
    "geri": 1.8156,
    "yan": 2.2606
   },
   "rampa5_geri_a_dev": 2.4006
  },
  {
   "tek_kol": true,
   "s1": -15,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0104,
    0.0001,
    0.5216
   ],
   "d_on": 0.1954,
   "d_arka": 0.1746,
   "d_yan": 0.2159,
   "a_dev": {
    "ileri": 3.6754,
    "geri": 3.284,
    "yan": 4.0602
   },
   "pay_fren_1_8": {
    "ileri": 2.0419,
    "geri": 1.8245,
    "yan": 2.2557
   },
   "rampa5_geri_a_dev": 2.4165
  },
  {
   "tek_kol": true,
   "s1": -15,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0104,
    -0.0038,
    0.5248
   ],
   "d_on": 0.1954,
   "d_arka": 0.1746,
   "d_yan": 0.2122,
   "a_dev": {
    "ileri": 3.6533,
    "geri": 3.263,
    "yan": 3.9672
   },
   "pay_fren_1_8": {
    "ileri": 2.0296,
    "geri": 1.8128,
    "yan": 2.204
   },
   "rampa5_geri_a_dev": 2.3955
  },
  {
   "tek_kol": true,
   "s1": -15,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0096,
    -0.0026,
    0.5246
   ],
   "d_on": 0.1946,
   "d_arka": 0.1754,
   "d_yan": 0.2134,
   "a_dev": {
    "ileri": 3.639,
    "geri": 3.2802,
    "yan": 3.9908
   },
   "pay_fren_1_8": {
    "ileri": 2.0217,
    "geri": 1.8224,
    "yan": 2.2171
   },
   "rampa5_geri_a_dev": 2.4128
  },
  {
   "tek_kol": true,
   "s1": 0,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0105,
    0.0,
    0.5205
   ],
   "d_on": 0.1955,
   "d_arka": 0.1745,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6842,
    "geri": 3.2893,
    "yan": 4.0704
   },
   "pay_fren_1_8": {
    "ileri": 2.0468,
    "geri": 1.8274,
    "yan": 2.2613
   },
   "rampa5_geri_a_dev": 2.4218
  },
  {
   "tek_kol": true,
   "s1": 0,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0096,
    0.0001,
    0.5217
   ],
   "d_on": 0.1946,
   "d_arka": 0.1754,
   "d_yan": 0.2159,
   "a_dev": {
    "ileri": 3.6594,
    "geri": 3.2985,
    "yan": 4.0593
   },
   "pay_fren_1_8": {
    "ileri": 2.033,
    "geri": 1.8325,
    "yan": 2.2552
   },
   "rampa5_geri_a_dev": 2.4309
  },
  {
   "tek_kol": true,
   "s1": 0,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0105,
    -0.0038,
    0.5248
   ],
   "d_on": 0.1955,
   "d_arka": 0.1745,
   "d_yan": 0.2122,
   "a_dev": {
    "ileri": 3.654,
    "geri": 3.2624,
    "yan": 3.9673
   },
   "pay_fren_1_8": {
    "ileri": 2.03,
    "geri": 1.8124,
    "yan": 2.204
   },
   "rampa5_geri_a_dev": 2.3949
  },
  {
   "tek_kol": true,
   "s1": 0,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0096,
    -0.0026,
    0.5248
   ],
   "d_on": 0.1946,
   "d_arka": 0.1754,
   "d_yan": 0.2134,
   "a_dev": {
    "ileri": 3.6376,
    "geri": 3.2788,
    "yan": 3.9891
   },
   "pay_fren_1_8": {
    "ileri": 2.0209,
    "geri": 1.8215,
    "yan": 2.2162
   },
   "rampa5_geri_a_dev": 2.4113
  },
  {
   "tek_kol": true,
   "s1": 15,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0094,
    0.0,
    0.5206
   ],
   "d_on": 0.1944,
   "d_arka": 0.1756,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6629,
    "geri": 3.3088,
    "yan": 4.0693
   },
   "pay_fren_1_8": {
    "ileri": 2.0349,
    "geri": 1.8382,
    "yan": 2.2607
   },
   "rampa5_geri_a_dev": 2.4412
  },
  {
   "tek_kol": true,
   "s1": 15,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0088,
    0.0001,
    0.522
   ],
   "d_on": 0.1938,
   "d_arka": 0.1762,
   "d_yan": 0.2159,
   "a_dev": {
    "ileri": 3.6431,
    "geri": 3.3105,
    "yan": 4.0568
   },
   "pay_fren_1_8": {
    "ileri": 2.0239,
    "geri": 1.8392,
    "yan": 2.2538
   },
   "rampa5_geri_a_dev": 2.4429
  },
  {
   "tek_kol": true,
   "s1": 15,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0105,
    -0.0038,
    0.5248
   ],
   "d_on": 0.1955,
   "d_arka": 0.1745,
   "d_yan": 0.2122,
   "a_dev": {
    "ileri": 3.6547,
    "geri": 3.2618,
    "yan": 3.9674
   },
   "pay_fren_1_8": {
    "ileri": 2.0304,
    "geri": 1.8121,
    "yan": 2.2041
   },
   "rampa5_geri_a_dev": 2.3944
  },
  {
   "tek_kol": true,
   "s1": 15,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0097,
    -0.0026,
    0.525
   ],
   "d_on": 0.1947,
   "d_arka": 0.1753,
   "d_yan": 0.2134,
   "a_dev": {
    "ileri": 3.6372,
    "geri": 3.2763,
    "yan": 3.9875
   },
   "pay_fren_1_8": {
    "ileri": 2.0207,
    "geri": 1.8202,
    "yan": 2.2153
   },
   "rampa5_geri_a_dev": 2.4088
  },
  {
   "tek_kol": true,
   "s1": 30,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0084,
    0.0,
    0.521
   ],
   "d_on": 0.1934,
   "d_arka": 0.1766,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.641,
    "geri": 3.3252,
    "yan": 4.0661
   },
   "pay_fren_1_8": {
    "ileri": 2.0228,
    "geri": 1.8474,
    "yan": 2.259
   },
   "rampa5_geri_a_dev": 2.4576
  },
  {
   "tek_kol": true,
   "s1": 30,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0082,
    0.0001,
    0.5225
   ],
   "d_on": 0.1932,
   "d_arka": 0.1768,
   "d_yan": 0.2159,
   "a_dev": {
    "ileri": 3.6275,
    "geri": 3.3194,
    "yan": 4.0529
   },
   "pay_fren_1_8": {
    "ileri": 2.0153,
    "geri": 1.8441,
    "yan": 2.2516
   },
   "rampa5_geri_a_dev": 2.4517
  },
  {
   "tek_kol": true,
   "s1": 30,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0105,
    -0.0038,
    0.5248
   ],
   "d_on": 0.1955,
   "d_arka": 0.1745,
   "d_yan": 0.2122,
   "a_dev": {
    "ileri": 3.6553,
    "geri": 3.2615,
    "yan": 3.9675
   },
   "pay_fren_1_8": {
    "ileri": 2.0307,
    "geri": 1.8119,
    "yan": 2.2042
   },
   "rampa5_geri_a_dev": 2.3941
  },
  {
   "tek_kol": true,
   "s1": 30,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0098,
    -0.0026,
    0.5252
   ],
   "d_on": 0.1948,
   "d_arka": 0.1752,
   "d_yan": 0.2134,
   "a_dev": {
    "ileri": 3.6381,
    "geri": 3.2729,
    "yan": 3.9861
   },
   "pay_fren_1_8": {
    "ileri": 2.0211,
    "geri": 1.8183,
    "yan": 2.2145
   },
   "rampa5_geri_a_dev": 2.4055
  },
  {
   "tek_kol": true,
   "s1": 45,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0075,
    0.0,
    0.5217
   ],
   "d_on": 0.1925,
   "d_arka": 0.1775,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.62,
    "geri": 3.3374,
    "yan": 4.061
   },
   "pay_fren_1_8": {
    "ileri": 2.0111,
    "geri": 1.8541,
    "yan": 2.2561
   },
   "rampa5_geri_a_dev": 2.4697
  },
  {
   "tek_kol": true,
   "s1": 45,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0077,
    0.0001,
    0.5231
   ],
   "d_on": 0.1927,
   "d_arka": 0.1773,
   "d_yan": 0.2159,
   "a_dev": {
    "ileri": 3.6139,
    "geri": 3.3244,
    "yan": 4.0479
   },
   "pay_fren_1_8": {
    "ileri": 2.0077,
    "geri": 1.8469,
    "yan": 2.2488
   },
   "rampa5_geri_a_dev": 2.4567
  },
  {
   "tek_kol": true,
   "s1": 45,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0106,
    -0.0038,
    0.5247
   ],
   "d_on": 0.1956,
   "d_arka": 0.1744,
   "d_yan": 0.2122,
   "a_dev": {
    "ileri": 3.6559,
    "geri": 3.2612,
    "yan": 3.9677
   },
   "pay_fren_1_8": {
    "ileri": 2.0311,
    "geri": 1.8118,
    "yan": 2.2043
   },
   "rampa5_geri_a_dev": 2.3938
  },
  {
   "tek_kol": true,
   "s1": 45,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0099,
    -0.0026,
    0.5254
   ],
   "d_on": 0.1949,
   "d_arka": 0.1751,
   "d_yan": 0.2134,
   "a_dev": {
    "ileri": 3.64,
    "geri": 3.269,
    "yan": 3.9849
   },
   "pay_fren_1_8": {
    "ileri": 2.0222,
    "geri": 1.8161,
    "yan": 2.2138
   },
   "rampa5_geri_a_dev": 2.4016
  },
  {
   "tek_kol": true,
   "s1": 60,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0068,
    0.0,
    0.5226
   ],
   "d_on": 0.1918,
   "d_arka": 0.1782,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.6015,
    "geri": 3.3445,
    "yan": 4.0544
   },
   "pay_fren_1_8": {
    "ileri": 2.0008,
    "geri": 1.8581,
    "yan": 2.2524
   },
   "rampa5_geri_a_dev": 2.4768
  },
  {
   "tek_kol": true,
   "s1": 60,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0074,
    0.0001,
    0.5239
   ],
   "d_on": 0.1924,
   "d_arka": 0.1776,
   "d_yan": 0.2159,
   "a_dev": {
    "ileri": 3.603,
    "geri": 3.3253,
    "yan": 4.042
   },
   "pay_fren_1_8": {
    "ileri": 2.0016,
    "geri": 1.8474,
    "yan": 2.2456
   },
   "rampa5_geri_a_dev": 2.4576
  },
  {
   "tek_kol": true,
   "s1": 60,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0106,
    -0.0038,
    0.5247
   ],
   "d_on": 0.1956,
   "d_arka": 0.1744,
   "d_yan": 0.2122,
   "a_dev": {
    "ileri": 3.6564,
    "geri": 3.2612,
    "yan": 3.968
   },
   "pay_fren_1_8": {
    "ileri": 2.0313,
    "geri": 1.8118,
    "yan": 2.2044
   },
   "rampa5_geri_a_dev": 2.3938
  },
  {
   "tek_kol": true,
   "s1": 60,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0101,
    -0.0026,
    0.5255
   ],
   "d_on": 0.1951,
   "d_arka": 0.1749,
   "d_yan": 0.2134,
   "a_dev": {
    "ileri": 3.6429,
    "geri": 3.2647,
    "yan": 3.9841
   },
   "pay_fren_1_8": {
    "ileri": 2.0238,
    "geri": 1.8137,
    "yan": 2.2134
   },
   "rampa5_geri_a_dev": 2.3973
  },
  {
   "tek_kol": true,
   "s1": 75,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0064,
    0.0,
    0.5236
   ],
   "d_on": 0.1914,
   "d_arka": 0.1786,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5866,
    "geri": 3.3461,
    "yan": 4.0466
   },
   "pay_fren_1_8": {
    "ileri": 1.9926,
    "geri": 1.8589,
    "yan": 2.2481
   },
   "rampa5_geri_a_dev": 2.4784
  },
  {
   "tek_kol": true,
   "s1": 75,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0073,
    0.0001,
    0.5247
   ],
   "d_on": 0.1923,
   "d_arka": 0.1777,
   "d_yan": 0.2159,
   "a_dev": {
    "ileri": 3.5956,
    "geri": 3.322,
    "yan": 4.0358
   },
   "pay_fren_1_8": {
    "ileri": 1.9975,
    "geri": 1.8455,
    "yan": 2.2421
   },
   "rampa5_geri_a_dev": 2.4543
  },
  {
   "tek_kol": true,
   "s1": 75,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0106,
    -0.0038,
    0.5247
   ],
   "d_on": 0.1956,
   "d_arka": 0.1744,
   "d_yan": 0.2122,
   "a_dev": {
    "ileri": 3.6567,
    "geri": 3.2613,
    "yan": 3.9682
   },
   "pay_fren_1_8": {
    "ileri": 2.0315,
    "geri": 1.8119,
    "yan": 2.2046
   },
   "rampa5_geri_a_dev": 2.3939
  },
  {
   "tek_kol": true,
   "s1": 75,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0103,
    -0.0026,
    0.5255
   ],
   "d_on": 0.1953,
   "d_arka": 0.1747,
   "d_yan": 0.2134,
   "a_dev": {
    "ileri": 3.6465,
    "geri": 3.2603,
    "yan": 3.9837
   },
   "pay_fren_1_8": {
    "ileri": 2.0259,
    "geri": 1.8113,
    "yan": 2.2132
   },
   "rampa5_geri_a_dev": 2.3929
  },
  {
   "tek_kol": true,
   "s1": 90,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0063,
    0.0,
    0.5246
   ],
   "d_on": 0.1913,
   "d_arka": 0.1787,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5764,
    "geri": 3.3421,
    "yan": 4.0383
   },
   "pay_fren_1_8": {
    "ileri": 1.9869,
    "geri": 1.8567,
    "yan": 2.2435
   },
   "rampa5_geri_a_dev": 2.4743
  },
  {
   "tek_kol": true,
   "s1": 90,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0074,
    0.0001,
    0.5255
   ],
   "d_on": 0.1924,
   "d_arka": 0.1776,
   "d_yan": 0.2159,
   "a_dev": {
    "ileri": 3.5922,
    "geri": 3.3147,
    "yan": 4.0296
   },
   "pay_fren_1_8": {
    "ileri": 1.9957,
    "geri": 1.8415,
    "yan": 2.2387
   },
   "rampa5_geri_a_dev": 2.4471
  },
  {
   "tek_kol": true,
   "s1": 90,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0106,
    -0.0038,
    0.5246
   ],
   "d_on": 0.1956,
   "d_arka": 0.1744,
   "d_yan": 0.2122,
   "a_dev": {
    "ileri": 3.6568,
    "geri": 3.2617,
    "yan": 3.9685
   },
   "pay_fren_1_8": {
    "ileri": 2.0316,
    "geri": 1.812,
    "yan": 2.2047
   },
   "rampa5_geri_a_dev": 2.3942
  },
  {
   "tek_kol": true,
   "s1": 90,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0106,
    -0.0026,
    0.5255
   ],
   "d_on": 0.1956,
   "d_arka": 0.1744,
   "d_yan": 0.2134,
   "a_dev": {
    "ileri": 3.6507,
    "geri": 3.2562,
    "yan": 3.9837
   },
   "pay_fren_1_8": {
    "ileri": 2.0282,
    "geri": 1.809,
    "yan": 2.2132
   },
   "rampa5_geri_a_dev": 2.3888
  },
  {
   "tek_kol": true,
   "s1": 105,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0064,
    0.0,
    0.5257
   ],
   "d_on": 0.1914,
   "d_arka": 0.1786,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5716,
    "geri": 3.3327,
    "yan": 4.03
   },
   "pay_fren_1_8": {
    "ileri": 1.9842,
    "geri": 1.8515,
    "yan": 2.2389
   },
   "rampa5_geri_a_dev": 2.465
  },
  {
   "tek_kol": true,
   "s1": 105,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0078,
    0.0001,
    0.5263
   ],
   "d_on": 0.1928,
   "d_arka": 0.1772,
   "d_yan": 0.2159,
   "a_dev": {
    "ileri": 3.5931,
    "geri": 3.304,
    "yan": 4.0239
   },
   "pay_fren_1_8": {
    "ileri": 1.9962,
    "geri": 1.8356,
    "yan": 2.2355
   },
   "rampa5_geri_a_dev": 2.4364
  },
  {
   "tek_kol": true,
   "s1": 105,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0106,
    -0.0038,
    0.5246
   ],
   "d_on": 0.1956,
   "d_arka": 0.1744,
   "d_yan": 0.2122,
   "a_dev": {
    "ileri": 3.6568,
    "geri": 3.2621,
    "yan": 3.9687
   },
   "pay_fren_1_8": {
    "ileri": 2.0316,
    "geri": 1.8123,
    "yan": 2.2049
   },
   "rampa5_geri_a_dev": 2.3947
  },
  {
   "tek_kol": true,
   "s1": 105,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0108,
    -0.0026,
    0.5255
   ],
   "d_on": 0.1958,
   "d_arka": 0.1742,
   "d_yan": 0.2134,
   "a_dev": {
    "ileri": 3.6551,
    "geri": 3.2526,
    "yan": 3.9842
   },
   "pay_fren_1_8": {
    "ileri": 2.0306,
    "geri": 1.807,
    "yan": 2.2134
   },
   "rampa5_geri_a_dev": 2.3852
  },
  {
   "tek_kol": true,
   "s1": 120,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0068,
    0.0,
    0.5267
   ],
   "d_on": 0.1918,
   "d_arka": 0.1782,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5723,
    "geri": 3.3187,
    "yan": 4.0222
   },
   "pay_fren_1_8": {
    "ileri": 1.9846,
    "geri": 1.8437,
    "yan": 2.2346
   },
   "rampa5_geri_a_dev": 2.4511
  },
  {
   "tek_kol": true,
   "s1": 120,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0083,
    0.0001,
    0.5269
   ],
   "d_on": 0.1933,
   "d_arka": 0.1767,
   "d_yan": 0.2159,
   "a_dev": {
    "ileri": 3.5981,
    "geri": 3.2906,
    "yan": 4.019
   },
   "pay_fren_1_8": {
    "ileri": 1.9989,
    "geri": 1.8281,
    "yan": 2.2328
   },
   "rampa5_geri_a_dev": 2.4231
  },
  {
   "tek_kol": true,
   "s1": 120,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0105,
    -0.0038,
    0.5246
   ],
   "d_on": 0.1955,
   "d_arka": 0.1745,
   "d_yan": 0.2122,
   "a_dev": {
    "ileri": 3.6566,
    "geri": 3.2627,
    "yan": 3.969
   },
   "pay_fren_1_8": {
    "ileri": 2.0314,
    "geri": 1.8126,
    "yan": 2.205
   },
   "rampa5_geri_a_dev": 2.3953
  },
  {
   "tek_kol": true,
   "s1": 120,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.011,
    -0.0026,
    0.5253
   ],
   "d_on": 0.196,
   "d_arka": 0.174,
   "d_yan": 0.2134,
   "a_dev": {
    "ileri": 3.6595,
    "geri": 3.2498,
    "yan": 3.9851
   },
   "pay_fren_1_8": {
    "ileri": 2.0331,
    "geri": 1.8054,
    "yan": 2.2139
   },
   "rampa5_geri_a_dev": 2.3824
  },
  {
   "tek_kol": true,
   "s1": 135,
   "s2": 5,
   "dirsek": 0,
   "am_m": [
    -0.0075,
    0.0,
    0.5276
   ],
   "d_on": 0.1925,
   "d_arka": 0.1775,
   "d_yan": 0.216,
   "a_dev": {
    "ileri": 3.5786,
    "geri": 3.3011,
    "yan": 4.0156
   },
   "pay_fren_1_8": {
    "ileri": 1.9881,
    "geri": 1.8339,
    "yan": 2.2309
   },
   "rampa5_geri_a_dev": 2.4335
  },
  {
   "tek_kol": true,
   "s1": 135,
   "s2": 5,
   "dirsek": 105,
   "am_m": [
    -0.0089,
    0.0001,
    0.5274
   ],
   "d_on": 0.1939,
   "d_arka": 0.1761,
   "d_yan": 0.2159,
   "a_dev": {
    "ileri": 3.6069,
    "geri": 3.2755,
    "yan": 4.0153
   },
   "pay_fren_1_8": {
    "ileri": 2.0038,
    "geri": 1.8197,
    "yan": 2.2307
   },
   "rampa5_geri_a_dev": 2.408
  },
  {
   "tek_kol": true,
   "s1": 135,
   "s2": 90,
   "dirsek": 0,
   "am_m": [
    -0.0105,
    -0.0038,
    0.5246
   ],
   "d_on": 0.1955,
   "d_arka": 0.1745,
   "d_yan": 0.2122,
   "a_dev": {
    "ileri": 3.6562,
    "geri": 3.2633,
    "yan": 3.9691
   },
   "pay_fren_1_8": {
    "ileri": 2.0312,
    "geri": 1.813,
    "yan": 2.2051
   },
   "rampa5_geri_a_dev": 2.3959
  },
  {
   "tek_kol": true,
   "s1": 135,
   "s2": 90,
   "dirsek": 105,
   "am_m": [
    -0.0111,
    -0.0026,
    0.5252
   ],
   "d_on": 0.1961,
   "d_arka": 0.1739,
   "d_yan": 0.2134,
   "a_dev": {
    "ileri": 3.6635,
    "geri": 3.2479,
    "yan": 3.9863
   },
   "pay_fren_1_8": {
    "ileri": 2.0353,
    "geri": 1.8044,
    "yan": 2.2146
   },
   "rampa5_geri_a_dev": 2.3805
  }
 ],
 "en_kotu": {
  "ileri": {
   "poz": [
    105,
    5,
    0
   ],
   "tek_kol": false,
   "a_dev": 3.4612,
   "pay": 1.9229
  },
  "geri": {
   "poz": [
    75,
    120,
    0
   ],
   "tek_kol": false,
   "a_dev": 3.1516,
   "pay": 1.7509
  },
  "yan": {
   "poz": [
    135,
    5,
    35
   ],
   "tek_kol": false,
   "a_dev": 3.9586,
   "pay": 2.1992
  },
  "rampa5_geri": {
   "poz": [
    75,
    120,
    0
   ],
   "tek_kol": false,
   "a_dev": 2.2846
  }
 },
 "dinamik": [
  {
   "takim": "ana",
   "hareket": "iki kol S1 -45 -> 135 -> -45 -> 135 (85 derece/s, protokol servo)",
   "teker_yuk_en_az_N": [
    50.4834,
    61.9136,
    50.4581,
    61.9278
   ],
   "teker_yuk_statik_N": [
    60.237,
    69.2832,
    60.2099,
    69.2728
   ],
   "taban_en_buyuk_egim_derece": 0.0002,
   "yer_degistirme_mm": 0.0013
  },
  {
   "takim": "mu_0.5",
   "hareket": "iki kol S1 -45 -> 135 -> -45 -> 135 (85 derece/s, protokol servo)",
   "teker_yuk_en_az_N": [
    50.4834,
    61.9136,
    50.4581,
    61.9278
   ],
   "teker_yuk_statik_N": [
    60.237,
    69.2832,
    60.2099,
    69.2728
   ],
   "taban_en_buyuk_egim_derece": 0.0002,
   "yer_degistirme_mm": 0.0013
  }
 ],
 "izgara_ozet": {
  "poz_sayisi": 520,
  "am_x_aralik_mm": [
   -16.3532,
   -2.0596
  ],
  "am_z_aralik_mm": [
   520.5019,
   535.1953
  ]
 }
}
```

## carpisma

```json
{
 "yontem": "Y0f: kol - gövde / kol - kafa / kol - kol çarpışması, CAD parçalarının DIŞBÜKEY ZARFLARIYLA (MuJoCo temas denetimi).",
 "zarf_sayisi": 1225,
 "montaj_temasi_cift": 71,
 "montaj_temasi_ornek": [
  "Kabuk:Omuz bandi sag / OmuzSag_Gobek:Gobek-horn civatasi M3x12 (sag)",
  "Kabuk:Omuz bandi sag / OmuzSag_Gobek:Gobek-horn civatasi M3x12 (sag)001",
  "Kabuk:Omuz bandi sag / OmuzSag_Gobek:Gobek-horn civatasi M3x12 (sag)002",
  "Kabuk:Omuz bandi sag / OmuzSag_Gobek:Gobek-horn civatasi M3x12 (sag)003",
  "Kabuk:Omuz bandi sag / OmuzSag_Gobek:Omuz gobegi (sag)",
  "Kabuk:Omuz bandi sag / OmuzSag_Gobek:S1 horn 25T aluminyum disk (sag)",
  "Kabuk:Omuz bandi sag / OmuzSag_Gobek:S1 horn merkez vidasi M3 (sag)",
  "Kabuk:Omuz bandi sol / OmuzSol_Gobek:Gobek-horn civatasi M3x12 (sol)",
  "Kabuk:Omuz bandi sol / OmuzSol_Gobek:Gobek-horn civatasi M3x12 (sol)001",
  "Kabuk:Omuz bandi sol / OmuzSol_Gobek:Gobek-horn civatasi M3x12 (sol)002"
 ],
 "dalma_esigi_mm": 0.5,
 "adim_derece": 15,
 "kollar": {
  "sag": {
   "poz": 2760,
   "temasli_poz": 2424,
   "en_derin_mm": 6.5354,
   "dirsek_el_ya_da_kafa_temasli_poz": 0,
   "ciftler": [
    [
     "OmuzSol_Govde:Rulman kapagi (sol) / OmuzSol_Kol:Kol catali (sol)",
     6.5,
     [
      75,
      35,
      0,
      -90
     ]
    ],
    [
     "Kabuk:S1 kaset kapagi sol / OmuzSol_Kol:Kol catali (sol)",
     6.4,
     [
      15,
      35,
      0,
      -90
     ]
    ],
    [
     "OmuzSol_Govde:6808-2RS rulman (dis bilezik) (sol) / OmuzSol_Kol:Kol catali (sol)",
     5.6,
     [
      75,
      35,
      0,
      -90
     ]
    ],
    [
     "Kabuk:S1 kaset govdesi sol / OmuzSol_Kol:Kol catali (sol)",
     5.2,
     [
      -15,
      35,
      0,
      -90
     ]
    ],
    [
     "Kabuk:S1 kaset govdesi sol / OmuzSol_Gobek:S1 tambur baglama ipi (sol)",
     5.1,
     [
      75,
      5,
      0,
      -90
     ]
    ],
    [
     "Kabuk:S1 kaset govdesi sol / OmuzSol_Gobek:S1 tambur baglama ipi (sol)001",
     5.1,
     [
      105,
      5,
      0,
      -90
     ]
    ],
    [
     "OmuzSol_Gobek:Omuz gobegi (sol) / OmuzSol_Govde:Kapak civatasi M3x12 (sol)003",
     5.0,
     [
      -45,
      5,
      0,
      -90
     ]
    ],
    [
     "OmuzSol_Gobek:Omuz gobegi (sol) / OmuzSol_Govde:Kapak civatasi M3x12 (sol)002",
     5.0,
     [
      105,
      5,
      0,
      -90
     ]
    ],
    [
     "OmuzSol_Gobek:Omuz gobegi (sol) / OmuzSol_Govde:Kapak civatasi M3x12 (sol)",
     5.0,
     [
      135,
      5,
      0,
      -90
     ]
    ],
    [
     "Kabuk:S1 kaset kapagi sol / OmuzSol_Gobek:S1 tambur baglama ipi (sol)",
     3.6,
     [
      90,
      5,
      0,
      -90
     ]
    ],
    [
     "Kabuk:S1 kaset kapagi sol / OmuzSol_Gobek:S1 tambur baglama ipi (sol)001",
     3.6,
     [
      90,
      5,
      0,
      -90
     ]
    ],
    [
     "OmuzSol_Gobek:S1 kablo tamburu (sol) / OmuzSol_Govde:Kapak civatasi M3x12 (sol)",
     2.5,
     [
      90,
      5,
      0,
      -90
     ]
    ],
    [
     "OmuzSol_Gobek:S1 kablo tamburu (sol) / OmuzSol_Govde:Kapak civatasi M3x12 (sol)002",
     2.5,
     [
      60,
      5,
      0,
      -90
     ]
    ],
    [
     "Kabuk:S1 kaset kapagi sol / OmuzSol_Gobek:Tambur civatasi M3x8 (sol)001",
     2.0,
     [
      -45,
      5,
      0,
      -90
     ]
    ],
    [
     "OmuzSol_Gobek:Tambur civatasi M3x8 (sol) / OmuzSol_Govde:Rulman kapagi (sol)",
     1.3,
     [
      105,
      5,
      0,
      -90
     ]
    ]
   ]
  },
  "sol": {
   "poz": 2760,
   "temasli_poz": 2184,
   "en_derin_mm": 5.1059,
   "dirsek_el_ya_da_kafa_temasli_poz": 0,
   "ciftler": [
    [
     "Kabuk:S1 kaset govdesi sag / OmuzSag_Gobek:S1 tambur baglama ipi (sag)",
     5.1,
     [
      120,
      5,
      0,
      -90
     ]
    ],
    [
     "Kabuk:S1 kaset govdesi sag / OmuzSag_Gobek:S1 tambur baglama ipi (sag)001",
     5.1,
     [
      120,
      5,
      0,
      -90
     ]
    ],
    [
     "OmuzSag_Gobek:Omuz gobegi (sag) / OmuzSag_Govde:Kapak civatasi M3x12 (sag)",
     5.0,
     [
      -45,
      5,
      0,
      -90
     ]
    ],
    [
     "OmuzSag_Gobek:Omuz gobegi (sag) / OmuzSag_Govde:Kapak civatasi M3x12 (sag)001",
     5.0,
     [
      120,
      5,
      0,
      -90
     ]
    ],
    [
     "OmuzSag_Gobek:Omuz gobegi (sag) / OmuzSag_Govde:Kapak civatasi M3x12 (sag)003",
     5.0,
     [
      135,
      5,
      0,
      -90
     ]
    ],
    [
     "Kabuk:S1 kaset kapagi sag / OmuzSag_Gobek:S1 tambur baglama ipi (sag)",
     3.6,
     [
      60,
      5,
      0,
      -90
     ]
    ],
    [
     "Kabuk:S1 kaset kapagi sag / OmuzSag_Gobek:S1 tambur baglama ipi (sag)001",
     3.6,
     [
      60,
      5,
      0,
      -90
     ]
    ],
    [
     "OmuzSag_Gobek:Omuz gobegi (sag) / OmuzSag_Govde:Kapak civatasi M3x12 (sag)002",
     3.0,
     [
      -45,
      5,
      0,
      -90
     ]
    ],
    [
     "OmuzSag_Gobek:S1 kablo tamburu (sag) / OmuzSag_Govde:Kapak civatasi M3x12 (sag)",
     2.5,
     [
      90,
      5,
      0,
      -90
     ]
    ],
    [
     "OmuzSag_Gobek:S1 kablo tamburu (sag) / OmuzSag_Govde:Kapak civatasi M3x12 (sag)002",
     2.5,
     [
      75,
      5,
      0,
      -90
     ]
    ],
    [
     "Kabuk:S1 kaset kapagi sag / OmuzSag_Kol:Kol catali (sag)",
     2.2,
     [
      15,
      120,
      0,
      -90
     ]
    ],
    [
     "Kabuk:S1 kaset kapagi sag / OmuzSag_Gobek:Tambur civatasi M3x8 (sag)001",
     2.0,
     [
      -45,
      5,
      0,
      -90
     ]
    ],
    [
     "OmuzSag_Govde:Rulman kapagi (sag) / OmuzSag_Kol:Kol catali (sag)",
     1.8,
     [
      -45,
      120,
      0,
      -90
     ]
    ],
    [
     "OmuzSag_Gobek:Tambur civatasi M3x8 (sag) / OmuzSag_Govde:Rulman kapagi (sag)",
     1.3,
     [
      105,
      5,
      0,
      -90
     ]
    ],
    [
     "OmuzSag_Gobek:Tambur civatasi M3x8 (sag)002 / OmuzSag_Govde:Rulman kapagi (sag)",
     1.3,
     [
      75,
      5,
      0,
      -90
     ]
    ]
   ]
  }
 },
 "kol_kol": {
  "poz": 96,
  "temasli_poz": 0
 },
 "yorum": "zarf temasları omuz mekanizmasında (göbek, kol çatalı, tambur ipi <-> omuz gövdesi, rulman kapağı, S1 kaseti): bunlar iç içe dönen eş eksenli parçalar, içbükey çatal / halkanın zarfı mili yutuyor. dirsek_el_ya_da_kafa_temasli_poz = üst kol / ön kol / el ya da kafa parçasının karıştığı poz sayısı.",
 "eklem_sinirlari_kaynak": "tasarim/freecad/arayuz.py (OMUZ, DIRSEK, KAFA, KAFA_KOL_YASAK, KOL_KABLO s1 s2_s1_kosul)",
 "cad_kesin_tarama": "P10.8d FreeCAD katı taraması: kol sağ / sol aralıkta çakışan tam poz 0 / 1755, kol-kol 0 (planlama/d158/P108d-kontrol-olcum/b2-log)"
}
```

## rampa

```json
{
 "kosular": [
  {
   "egim_derece": 3,
   "takim": "ana",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": false,
   "rampanin_ortasina_ulasti": true,
   "sonar_yavaslatti": false,
   "son_x_m": 12.5732,
   "rampada_hiz_m_s": 0.3559,
   "rampada_tork_Nm_teker_ort": 0.3816,
   "tepe_tork_Nm": 0.4965,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": 0.1211,
   "dur_sonrasi_suzulme_suresi_s": 0.465,
   "suzulme_sonrasi_5s_geri_kayma_m": 0.0376,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": -0.0077,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0077,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 3.0098,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 0.2108,
    "eklem_surtunmesi_Nm": 0.1708,
    "teker_basi_cikis_torku_Nm": 0.3815,
    "durma_torku_orani": 0.1853,
    "surekli_tork_orani": 0.6172,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.0076
   }
  },
  {
   "egim_derece": 5,
   "takim": "ana",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": false,
   "rampanin_ortasina_ulasti": true,
   "sonar_yavaslatti": false,
   "son_x_m": 12.5267,
   "rampada_hiz_m_s": 0.3291,
   "rampada_tork_Nm_teker_ort": 0.5218,
   "tepe_tork_Nm": 0.7256,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": 0.1084,
   "dur_sonrasi_suzulme_suresi_s": 0.431,
   "suzulme_sonrasi_5s_geri_kayma_m": 0.1683,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": -0.0344,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0344,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 5.0298,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 0.351,
    "eklem_surtunmesi_Nm": 0.1708,
    "teker_basi_cikis_torku_Nm": 0.5214,
    "durma_torku_orani": 0.2532,
    "surekli_tork_orani": 0.8437,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.0344
   }
  },
  {
   "egim_derece": 8,
   "takim": "ana",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": false,
   "rampanin_ortasina_ulasti": true,
   "sonar_yavaslatti": false,
   "son_x_m": 12.5275,
   "rampada_hiz_m_s": 0.2891,
   "rampada_tork_Nm_teker_ort": 0.7313,
   "tepe_tork_Nm": 1.0732,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": 0.0915,
   "dur_sonrasi_suzulme_suresi_s": 0.396,
   "suzulme_sonrasi_5s_geri_kayma_m": 0.3616,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": -0.0744,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0744,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 8.0759,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 0.5605,
    "eklem_surtunmesi_Nm": 0.1708,
    "teker_basi_cikis_torku_Nm": 0.7302,
    "durma_torku_orani": 0.3546,
    "surekli_tork_orani": 1.1815,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.0743
   }
  },
  {
   "egim_derece": 10,
   "takim": "ana",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": false,
   "rampanin_ortasina_ulasti": true,
   "sonar_yavaslatti": false,
   "son_x_m": 12.5512,
   "rampada_hiz_m_s": 0.2626,
   "rampada_tork_Nm_teker_ort": 0.8702,
   "tepe_tork_Nm": 1.3023,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": 0.081,
   "dur_sonrasi_suzulme_suresi_s": 0.379,
   "suzulme_sonrasi_5s_geri_kayma_m": 0.4877,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": -0.1009,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0022,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 10.1163,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 0.6994,
    "eklem_surtunmesi_Nm": 0.1708,
    "teker_basi_cikis_torku_Nm": 0.8684,
    "durma_torku_orani": 0.4218,
    "surekli_tork_orani": 1.4052,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.1008
   }
  },
  {
   "egim_derece": 12,
   "takim": "ana",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": false,
   "rampanin_ortasina_ulasti": true,
   "sonar_yavaslatti": false,
   "son_x_m": 12.5404,
   "rampada_hiz_m_s": 0.2363,
   "rampada_tork_Nm_teker_ort": 1.0082,
   "tepe_tork_Nm": 1.5648,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": 0.071,
   "dur_sonrasi_suzulme_suresi_s": 0.364,
   "suzulme_sonrasi_5s_geri_kayma_m": 0.6107,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": -0.1273,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0021,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 12.183,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 0.8374,
    "eklem_surtunmesi_Nm": 0.1708,
    "teker_basi_cikis_torku_Nm": 1.0056,
    "durma_torku_orani": 0.4884,
    "surekli_tork_orani": 1.6272,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.1271
   }
  },
  {
   "egim_derece": 15,
   "takim": "ana",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": false,
   "rampanin_ortasina_ulasti": true,
   "sonar_yavaslatti": false,
   "son_x_m": 12.5062,
   "rampada_hiz_m_s": 0.1889,
   "rampada_tork_Nm_teker_ort": 1.2218,
   "tepe_tork_Nm": 1.9895,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": 0.056,
   "dur_sonrasi_suzulme_suresi_s": 0.345,
   "suzulme_sonrasi_5s_geri_kayma_m": 0.9468,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": -0.2233,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0074,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 15.3182,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 1.0424,
    "eklem_surtunmesi_Nm": 0.1708,
    "teker_basi_cikis_torku_Nm": 1.2091,
    "durma_torku_orani": 0.5872,
    "surekli_tork_orani": 1.9565,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.1662
   }
  },
  {
   "egim_derece": 20,
   "takim": "ana",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": false,
   "rampanin_ortasina_ulasti": false,
   "sonar_yavaslatti": true,
   "son_x_m": 11.1596,
   "rampada_hiz_m_s": null,
   "rampada_tork_Nm_teker_ort": null,
   "tepe_tork_Nm": 2.3909,
   "geri_devrildi": true,
   "dur_sonrasi_yukari_suzulme_m": null,
   "dur_sonrasi_suzulme_suresi_s": null,
   "suzulme_sonrasi_5s_geri_kayma_m": null,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": null,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": 0.0,
   "devrildi_ya_da_govde_degdi": true,
   "en_buyuk_egim_derece": 89.9998,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 1.3775,
    "eklem_surtunmesi_Nm": 0.1708,
    "teker_basi_cikis_torku_Nm": 1.5411,
    "durma_torku_orani": 0.7485,
    "surekli_tork_orani": 2.4937,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.2301
   }
  },
  {
   "egim_derece": 5,
   "takim": "mu_0.5",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": false,
   "rampanin_ortasina_ulasti": true,
   "sonar_yavaslatti": false,
   "son_x_m": 12.5267,
   "rampada_hiz_m_s": 0.3291,
   "rampada_tork_Nm_teker_ort": 0.5218,
   "tepe_tork_Nm": 0.7256,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": 0.1088,
   "dur_sonrasi_suzulme_suresi_s": 0.433,
   "suzulme_sonrasi_5s_geri_kayma_m": 0.1683,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": -0.0344,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0344,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 5.0298,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 0.351,
    "eklem_surtunmesi_Nm": 0.1708,
    "teker_basi_cikis_torku_Nm": 0.5214,
    "durma_torku_orani": 0.2532,
    "surekli_tork_orani": 0.8437,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.0344
   }
  },
  {
   "egim_derece": 10,
   "takim": "mu_0.5",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": false,
   "rampanin_ortasina_ulasti": true,
   "sonar_yavaslatti": false,
   "son_x_m": 12.551,
   "rampada_hiz_m_s": 0.2626,
   "rampada_tork_Nm_teker_ort": 0.8702,
   "tepe_tork_Nm": 1.3023,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": 0.081,
   "dur_sonrasi_suzulme_suresi_s": 0.379,
   "suzulme_sonrasi_5s_geri_kayma_m": 0.4877,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": -0.1009,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0023,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 10.1167,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 0.6994,
    "eklem_surtunmesi_Nm": 0.1708,
    "teker_basi_cikis_torku_Nm": 0.8684,
    "durma_torku_orani": 0.4218,
    "surekli_tork_orani": 1.4052,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.1008
   }
  },
  {
   "egim_derece": 15,
   "takim": "mu_0.5",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": false,
   "rampanin_ortasina_ulasti": true,
   "sonar_yavaslatti": false,
   "son_x_m": 12.5039,
   "rampada_hiz_m_s": 0.0689,
   "rampada_tork_Nm_teker_ort": 1.2064,
   "tepe_tork_Nm": 1.9895,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": 0.0189,
   "dur_sonrasi_suzulme_suresi_s": 0.318,
   "suzulme_sonrasi_5s_geri_kayma_m": 1.3471,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": -0.2928,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0506,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 15.8461,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 1.0424,
    "eklem_surtunmesi_Nm": 0.1708,
    "teker_basi_cikis_torku_Nm": 1.2091,
    "durma_torku_orani": 0.5872,
    "surekli_tork_orani": 1.9565,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.1662
   }
  },
  {
   "egim_derece": 5,
   "takim": "durma_9kgcm",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": false,
   "rampanin_ortasina_ulasti": true,
   "sonar_yavaslatti": false,
   "son_x_m": 12.5065,
   "rampada_hiz_m_s": 0.1965,
   "rampada_tork_Nm_teker_ort": 0.5218,
   "tepe_tork_Nm": 0.5218,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": 0.0658,
   "dur_sonrasi_suzulme_suresi_s": 0.426,
   "suzulme_sonrasi_5s_geri_kayma_m": 0.3819,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": -0.0802,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0802,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 5.0159,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 0.351,
    "eklem_surtunmesi_Nm": 0.1708,
    "teker_basi_cikis_torku_Nm": 0.5214,
    "durma_torku_orani": 0.5905,
    "surekli_tork_orani": 0.8437,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.0801
   }
  },
  {
   "egim_derece": 10,
   "takim": "durma_9kgcm",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": false,
   "rampanin_ortasina_ulasti": false,
   "sonar_yavaslatti": false,
   "son_x_m": 12.0496,
   "rampada_hiz_m_s": 0.0416,
   "rampada_tork_Nm_teker_ort": 0.8702,
   "tepe_tork_Nm": 0.8702,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": null,
   "dur_sonrasi_suzulme_suresi_s": null,
   "suzulme_sonrasi_5s_geri_kayma_m": null,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": null,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0642,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 10.0622,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 0.6994,
    "eklem_surtunmesi_Nm": 0.1708,
    "teker_basi_cikis_torku_Nm": 0.8684,
    "durma_torku_orani": 0.9834,
    "surekli_tork_orani": 1.4052,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.2351
   }
  },
  {
   "egim_derece": 15,
   "takim": "durma_9kgcm",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": false,
   "rampanin_ortasina_ulasti": false,
   "sonar_yavaslatti": false,
   "son_x_m": 11.1867,
   "rampada_hiz_m_s": null,
   "rampada_tork_Nm_teker_ort": null,
   "tepe_tork_Nm": 1.0287,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": null,
   "dur_sonrasi_suzulme_suresi_s": null,
   "suzulme_sonrasi_5s_geri_kayma_m": null,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": null,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0019,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 15.1591,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 1.0424,
    "eklem_surtunmesi_Nm": 0.1708,
    "teker_basi_cikis_torku_Nm": 1.2091,
    "durma_torku_orani": 1.3694,
    "surekli_tork_orani": 1.9565,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.3876
   }
  },
  {
   "egim_derece": 3,
   "takim": "disli_0.2",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": false,
   "rampanin_ortasina_ulasti": true,
   "sonar_yavaslatti": false,
   "son_x_m": 12.551,
   "rampada_hiz_m_s": 0.3273,
   "rampada_tork_Nm_teker_ort": 0.5316,
   "tepe_tork_Nm": 0.5978,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": 0.1053,
   "dur_sonrasi_suzulme_suresi_s": 0.428,
   "suzulme_sonrasi_5s_geri_kayma_m": 0.0123,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": -0.0025,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0025,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 3.0067,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 0.2108,
    "eklem_surtunmesi_Nm": 0.3208,
    "teker_basi_cikis_torku_Nm": 0.5315,
    "durma_torku_orani": 0.2581,
    "surekli_tork_orani": 0.86,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.0
   }
  },
  {
   "egim_derece": 5,
   "takim": "disli_0.2",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": false,
   "rampanin_ortasina_ulasti": true,
   "sonar_yavaslatti": false,
   "son_x_m": 12.5535,
   "rampada_hiz_m_s": 0.3005,
   "rampada_tork_Nm_teker_ort": 0.6718,
   "tepe_tork_Nm": 0.8386,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": 0.0967,
   "dur_sonrasi_suzulme_suresi_s": 0.411,
   "suzulme_sonrasi_5s_geri_kayma_m": 0.0288,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": -0.0058,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0058,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 5.0237,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 0.351,
    "eklem_surtunmesi_Nm": 0.3208,
    "teker_basi_cikis_torku_Nm": 0.6714,
    "durma_torku_orani": 0.3261,
    "surekli_tork_orani": 1.0864,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.0058
   }
  },
  {
   "egim_derece": 10,
   "takim": "disli_0.2",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": false,
   "rampanin_ortasina_ulasti": true,
   "sonar_yavaslatti": false,
   "son_x_m": 12.5113,
   "rampada_hiz_m_s": 0.234,
   "rampada_tork_Nm_teker_ort": 1.0202,
   "tepe_tork_Nm": 1.3932,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": 0.0707,
   "dur_sonrasi_suzulme_suresi_s": 0.367,
   "suzulme_sonrasi_5s_geri_kayma_m": 0.3493,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": -0.0723,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0723,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 10.0978,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 0.6994,
    "eklem_surtunmesi_Nm": 0.3208,
    "teker_basi_cikis_torku_Nm": 1.0184,
    "durma_torku_orani": 0.4946,
    "surekli_tork_orani": 1.6479,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.0722
   }
  },
  {
   "egim_derece": 15,
   "takim": "disli_0.2",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": false,
   "rampanin_ortasina_ulasti": true,
   "sonar_yavaslatti": false,
   "son_x_m": 12.5027,
   "rampada_hiz_m_s": 0.1629,
   "rampada_tork_Nm_teker_ort": 1.3648,
   "tepe_tork_Nm": 2.0529,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": 0.046,
   "dur_sonrasi_suzulme_suresi_s": 0.336,
   "suzulme_sonrasi_5s_geri_kayma_m": 0.7472,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": -0.1723,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0019,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 15.2681,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 1.0424,
    "eklem_surtunmesi_Nm": 0.3208,
    "teker_basi_cikis_torku_Nm": 1.3591,
    "durma_torku_orani": 0.6601,
    "surekli_tork_orani": 2.1993,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.1376
   }
  },
  {
   "egim_derece": 5,
   "takim": "ana",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": true,
   "rampanin_ortasina_ulasti": true,
   "sonar_yavaslatti": false,
   "son_x_m": 12.5267,
   "rampada_hiz_m_s": 0.3291,
   "rampada_tork_Nm_teker_ort": 0.5218,
   "tepe_tork_Nm": 0.7256,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": 0.1084,
   "dur_sonrasi_suzulme_suresi_s": 0.431,
   "suzulme_sonrasi_5s_geri_kayma_m": 0.1683,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": -0.0344,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0344,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 5.0298,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 0.351,
    "eklem_surtunmesi_Nm": 0.1708,
    "teker_basi_cikis_torku_Nm": 0.5214,
    "durma_torku_orani": 0.2532,
    "surekli_tork_orani": 0.8437,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.0344
   }
  },
  {
   "egim_derece": 10,
   "takim": "ana",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": true,
   "rampanin_ortasina_ulasti": true,
   "sonar_yavaslatti": false,
   "son_x_m": 12.5512,
   "rampada_hiz_m_s": 0.2626,
   "rampada_tork_Nm_teker_ort": 0.8702,
   "tepe_tork_Nm": 1.3023,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": 0.081,
   "dur_sonrasi_suzulme_suresi_s": 0.379,
   "suzulme_sonrasi_5s_geri_kayma_m": 0.4877,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": -0.1009,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0022,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 10.1163,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 0.6994,
    "eklem_surtunmesi_Nm": 0.1708,
    "teker_basi_cikis_torku_Nm": 0.8684,
    "durma_torku_orani": 0.4218,
    "surekli_tork_orani": 1.4052,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.1008
   }
  },
  {
   "egim_derece": 15,
   "takim": "ana",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": true,
   "rampanin_ortasina_ulasti": false,
   "sonar_yavaslatti": true,
   "son_x_m": 10.7225,
   "rampada_hiz_m_s": null,
   "rampada_tork_Nm_teker_ort": null,
   "tepe_tork_Nm": 0.228,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": null,
   "dur_sonrasi_suzulme_suresi_s": null,
   "suzulme_sonrasi_5s_geri_kayma_m": null,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": null,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 0.0001,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 1.0424,
    "eklem_surtunmesi_Nm": 0.1708,
    "teker_basi_cikis_torku_Nm": 1.2091,
    "durma_torku_orani": 0.5872,
    "surekli_tork_orani": 1.9565,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.1662
   }
  },
  {
   "egim_derece": 20,
   "takim": "ana",
   "v_komut": 1.0,
   "rampa_kipi": true,
   "sonar_acik": true,
   "rampanin_ortasina_ulasti": false,
   "sonar_yavaslatti": true,
   "son_x_m": 10.7225,
   "rampada_hiz_m_s": null,
   "rampada_tork_Nm_teker_ort": null,
   "tepe_tork_Nm": 0.228,
   "geri_devrildi": false,
   "dur_sonrasi_yukari_suzulme_m": null,
   "dur_sonrasi_suzulme_suresi_s": null,
   "suzulme_sonrasi_5s_geri_kayma_m": null,
   "suzulme_sonrasi_surekli_kayma_hizi_m_s": null,
   "dur_sonrasi_tutuyor": false,
   "dur_sonrasi_son_hiz_m_s": -0.0,
   "devrildi_ya_da_govde_degdi": false,
   "en_buyuk_egim_derece": 0.0001,
   "el_hesabi": {
    "teker_basi_tutma_torku_Nm": 1.3775,
    "eklem_surtunmesi_Nm": 0.1708,
    "teker_basi_cikis_torku_Nm": 1.5411,
    "durma_torku_orani": 0.7485,
    "surekli_tork_orani": 2.4937,
    "kisa_devre_freninde_kayma_hizi_m_s": 0.2301
   }
  }
 ],
 "not_": "rampa kipi açık (firmware ivme / fren 0,1 m/s2), sur v = 1 (teker azamisi); 3 m rampa + platform; sonar_acik False = mekanik sığa (firmware sonar yavaşlatması kapalı), True = firmware sonar kuralı açık"
}
```

## esik

```json
{
 "kosular": [
  {
   "yukseklik_mm": 5,
   "takim": "ana",
   "v_komut": 0.2,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.6091,
   "tepe_tork_Nm": 1.1191,
   "en_buyuk_egim_derece": 0.7747
  },
  {
   "yukseklik_mm": 10,
   "takim": "ana",
   "v_komut": 0.2,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": false,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.4721,
   "tepe_tork_Nm": 1.5711,
   "en_buyuk_egim_derece": 1.5493
  },
  {
   "yukseklik_mm": 15,
   "takim": "ana",
   "v_komut": 0.2,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": false,
   "on_teker_cikti": false,
   "arka_teker_cikti": false,
   "govde_degdi": false,
   "son_x_m": 10.7744,
   "tepe_tork_Nm": 1.6839,
   "en_buyuk_egim_derece": 0.2126
  },
  {
   "yukseklik_mm": 20,
   "takim": "ana",
   "v_komut": 0.2,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": false,
   "on_teker_cikti": false,
   "arka_teker_cikti": false,
   "govde_degdi": false,
   "son_x_m": 10.7692,
   "tepe_tork_Nm": 1.6398,
   "en_buyuk_egim_derece": 0.2019
  },
  {
   "yukseklik_mm": 25,
   "takim": "ana",
   "v_komut": 0.2,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": false,
   "on_teker_cikti": false,
   "arka_teker_cikti": false,
   "govde_degdi": false,
   "son_x_m": 10.765,
   "tepe_tork_Nm": 1.598,
   "en_buyuk_egim_derece": 0.2013
  },
  {
   "yukseklik_mm": 30,
   "takim": "ana",
   "v_komut": 0.2,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": false,
   "on_teker_cikti": false,
   "arka_teker_cikti": false,
   "govde_degdi": false,
   "son_x_m": 10.7616,
   "tepe_tork_Nm": 1.5442,
   "en_buyuk_egim_derece": 0.1985
  },
  {
   "yukseklik_mm": 40,
   "takim": "ana",
   "v_komut": 0.2,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": false,
   "on_teker_cikti": false,
   "arka_teker_cikti": false,
   "govde_degdi": true,
   "son_x_m": 10.7375,
   "tepe_tork_Nm": 1.2759,
   "en_buyuk_egim_derece": 0.2038
  },
  {
   "yukseklik_mm": 5,
   "takim": "ana",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.6576,
   "tepe_tork_Nm": 1.323,
   "en_buyuk_egim_derece": 1.2309
  },
  {
   "yukseklik_mm": 10,
   "takim": "ana",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.6765,
   "tepe_tork_Nm": 1.6781,
   "en_buyuk_egim_derece": 3.0903
  },
  {
   "yukseklik_mm": 15,
   "takim": "ana",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.6658,
   "tepe_tork_Nm": 2.2626,
   "en_buyuk_egim_derece": 2.7911
  },
  {
   "yukseklik_mm": 20,
   "takim": "ana",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.6214,
   "tepe_tork_Nm": 2.9986,
   "en_buyuk_egim_derece": 3.1007
  },
  {
   "yukseklik_mm": 25,
   "takim": "ana",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.6754,
   "tepe_tork_Nm": 2.9881,
   "en_buyuk_egim_derece": 3.877
  },
  {
   "yukseklik_mm": 30,
   "takim": "ana",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.6233,
   "tepe_tork_Nm": 2.908,
   "en_buyuk_egim_derece": 4.6586
  },
  {
   "yukseklik_mm": 40,
   "takim": "ana",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": false,
   "on_teker_cikti": true,
   "arka_teker_cikti": false,
   "govde_degdi": true,
   "son_x_m": 11.1324,
   "tepe_tork_Nm": 2.6979,
   "en_buyuk_egim_derece": 7.2469
  },
  {
   "yukseklik_mm": 5,
   "takim": "mu_0.5",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.6578,
   "tepe_tork_Nm": 1.3159,
   "en_buyuk_egim_derece": 1.231
  },
  {
   "yukseklik_mm": 10,
   "takim": "mu_0.5",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.6766,
   "tepe_tork_Nm": 1.6538,
   "en_buyuk_egim_derece": 3.0903
  },
  {
   "yukseklik_mm": 15,
   "takim": "mu_0.5",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.6655,
   "tepe_tork_Nm": 2.2629,
   "en_buyuk_egim_derece": 2.7908
  },
  {
   "yukseklik_mm": 20,
   "takim": "mu_0.5",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.6173,
   "tepe_tork_Nm": 2.958,
   "en_buyuk_egim_derece": 3.1009
  },
  {
   "yukseklik_mm": 25,
   "takim": "mu_0.5",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.6706,
   "tepe_tork_Nm": 2.6221,
   "en_buyuk_egim_derece": 3.8784
  },
  {
   "yukseklik_mm": 30,
   "takim": "mu_0.5",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.6172,
   "tepe_tork_Nm": 2.2839,
   "en_buyuk_egim_derece": 4.6677
  },
  {
   "yukseklik_mm": 40,
   "takim": "mu_0.5",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": false,
   "on_teker_cikti": true,
   "arka_teker_cikti": false,
   "govde_degdi": true,
   "son_x_m": 11.1324,
   "tepe_tork_Nm": 2.6011,
   "en_buyuk_egim_derece": 8.0391
  },
  {
   "yukseklik_mm": 5,
   "takim": "durma_9kgcm",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.6346,
   "tepe_tork_Nm": 0.7159,
   "en_buyuk_egim_derece": 1.227
  },
  {
   "yukseklik_mm": 10,
   "takim": "durma_9kgcm",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": false,
   "on_teker_cikti": true,
   "arka_teker_cikti": false,
   "govde_degdi": false,
   "son_x_m": 10.7811,
   "tepe_tork_Nm": 1.1769,
   "en_buyuk_egim_derece": 1.6858
  },
  {
   "yukseklik_mm": 15,
   "takim": "durma_9kgcm",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": false,
   "on_teker_cikti": false,
   "arka_teker_cikti": false,
   "govde_degdi": false,
   "son_x_m": 10.7744,
   "tepe_tork_Nm": 1.408,
   "en_buyuk_egim_derece": 0.8219
  },
  {
   "yukseklik_mm": 20,
   "takim": "durma_9kgcm",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": false,
   "on_teker_cikti": false,
   "arka_teker_cikti": false,
   "govde_degdi": false,
   "son_x_m": 10.7692,
   "tepe_tork_Nm": 1.3789,
   "en_buyuk_egim_derece": 0.7628
  },
  {
   "yukseklik_mm": 25,
   "takim": "durma_9kgcm",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": false,
   "on_teker_cikti": false,
   "arka_teker_cikti": false,
   "govde_degdi": false,
   "son_x_m": 10.765,
   "tepe_tork_Nm": 1.3209,
   "en_buyuk_egim_derece": 0.7296
  },
  {
   "yukseklik_mm": 30,
   "takim": "durma_9kgcm",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": false,
   "on_teker_cikti": false,
   "arka_teker_cikti": false,
   "govde_degdi": false,
   "son_x_m": 10.7616,
   "tepe_tork_Nm": 1.2598,
   "en_buyuk_egim_derece": 0.7166
  },
  {
   "yukseklik_mm": 40,
   "takim": "durma_9kgcm",
   "v_komut": 1.0,
   "sonar_acik": false,
   "sonar_yavaslatti": false,
   "gecti": false,
   "on_teker_cikti": false,
   "arka_teker_cikti": false,
   "govde_degdi": true,
   "son_x_m": 10.7375,
   "tepe_tork_Nm": 1.0605,
   "en_buyuk_egim_derece": 0.7607
  },
  {
   "yukseklik_mm": 5,
   "takim": "ana",
   "v_komut": 0.2,
   "sonar_acik": true,
   "sonar_yavaslatti": false,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.6297,
   "tepe_tork_Nm": 1.1183,
   "en_buyuk_egim_derece": 0.7747
  },
  {
   "yukseklik_mm": 15,
   "takim": "ana",
   "v_komut": 0.2,
   "sonar_acik": true,
   "sonar_yavaslatti": false,
   "gecti": false,
   "on_teker_cikti": false,
   "arka_teker_cikti": false,
   "govde_degdi": false,
   "son_x_m": 10.7744,
   "tepe_tork_Nm": 1.6985,
   "en_buyuk_egim_derece": 0.2327
  },
  {
   "yukseklik_mm": 30,
   "takim": "ana",
   "v_komut": 0.2,
   "sonar_acik": true,
   "sonar_yavaslatti": false,
   "gecti": false,
   "on_teker_cikti": false,
   "arka_teker_cikti": false,
   "govde_degdi": false,
   "son_x_m": 10.7616,
   "tepe_tork_Nm": 1.5406,
   "en_buyuk_egim_derece": 0.1964
  },
  {
   "yukseklik_mm": 40,
   "takim": "ana",
   "v_komut": 0.2,
   "sonar_acik": true,
   "sonar_yavaslatti": true,
   "gecti": false,
   "on_teker_cikti": false,
   "arka_teker_cikti": false,
   "govde_degdi": false,
   "son_x_m": 10.4556,
   "tepe_tork_Nm": 0.4489,
   "en_buyuk_egim_derece": 0.0003
  },
  {
   "yukseklik_mm": 5,
   "takim": "ana",
   "v_komut": 1.0,
   "sonar_acik": true,
   "sonar_yavaslatti": false,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.6324,
   "tepe_tork_Nm": 1.3158,
   "en_buyuk_egim_derece": 1.2329
  },
  {
   "yukseklik_mm": 15,
   "takim": "ana",
   "v_komut": 1.0,
   "sonar_acik": true,
   "sonar_yavaslatti": false,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.6364,
   "tepe_tork_Nm": 2.2719,
   "en_buyuk_egim_derece": 2.7138
  },
  {
   "yukseklik_mm": 30,
   "takim": "ana",
   "v_komut": 1.0,
   "sonar_acik": true,
   "sonar_yavaslatti": true,
   "gecti": true,
   "on_teker_cikti": true,
   "arka_teker_cikti": true,
   "govde_degdi": false,
   "son_x_m": 11.631,
   "tepe_tork_Nm": 2.9158,
   "en_buyuk_egim_derece": 4.6545
  },
  {
   "yukseklik_mm": 40,
   "takim": "ana",
   "v_komut": 1.0,
   "sonar_acik": true,
   "sonar_yavaslatti": true,
   "gecti": false,
   "on_teker_cikti": false,
   "arka_teker_cikti": false,
   "govde_degdi": false,
   "son_x_m": 10.4555,
   "tepe_tork_Nm": 0.4538,
   "en_buyuk_egim_derece": 0.0003
  }
 ],
 "el_hesabi": {
  "mu_0.5": {
   "on_teker_h_mm": 6.5983,
   "aciklama": "yalnız basamağa dayanan teker kendi sürtünmesiyle (itilmeden): h = r (1 - cos atan mu)"
  },
  "mu_0.8": {
   "on_teker_h_mm": 13.6957,
   "aciklama": "yalnız basamağa dayanan teker kendi sürtünmesiyle (itilmeden): h = r (1 - cos atan mu)"
  },
  "etek_yuksekligi_mm": 35.0,
  "not_": "arkadaki tahrikli tekerlerin itmesi öndekini kolaylaştırır; etek alt kenarı 35 mm (Kabuk 'Etek' parçaları)"
 }
}
```

## donus

```json
{
 "kosular": [
  {
   "v_komut": 0.0,
   "w_komut": 1.0,
   "takim": "ana",
   "teker_hedef_m_s": [
    -0.213,
    0.213
   ],
   "v_hedef": 0.0,
   "w_hedef_rad_s": 0.9861,
   "v_olculen": 0.0,
   "w_olculen_rad_s": 0.0013,
   "w_orani": 0.0013,
   "yanal_ivme_m_s2": 0.0,
   "en_buyuk_yatma_derece": 0.0,
   "teker_yuk_en_az_N": 60.7809,
   "tork_ort_Nm": [
    1.225,
    1.2251,
    1.225,
    1.2251
   ]
  },
  {
   "v_komut": 1.0,
   "w_komut": 1.0,
   "takim": "ana",
   "teker_hedef_m_s": [
    0.253,
    0.39
   ],
   "v_hedef": 0.3215,
   "w_hedef_rad_s": 0.3171,
   "v_olculen": 0.3208,
   "w_olculen_rad_s": 0.0004,
   "w_orani": 0.0013,
   "yanal_ivme_m_s2": 0.0,
   "en_buyuk_yatma_derece": 0.0,
   "teker_yuk_en_az_N": 60.7829,
   "tork_ort_Nm": [
    0.223,
    0.223,
    0.5647,
    0.5647
   ]
  },
  {
   "v_komut": 0.3,
   "w_komut": 0.5,
   "takim": "ana",
   "teker_hedef_m_s": [
    0.1856,
    0.39
   ],
   "v_hedef": 0.2878,
   "w_hedef_rad_s": 0.473,
   "v_olculen": 0.2838,
   "w_olculen_rad_s": 0.0006,
   "w_orani": 0.0013,
   "yanal_ivme_m_s2": 0.0,
   "en_buyuk_yatma_derece": 0.0,
   "teker_yuk_en_az_N": 60.7835,
   "tork_ort_Nm": [
    0.4168,
    0.4168,
    0.7584,
    0.7585
   ]
  },
  {
   "v_komut": 0.0,
   "w_komut": 1.0,
   "takim": "mu_0.5",
   "teker_hedef_m_s": [
    -0.213,
    0.213
   ],
   "v_hedef": 0.0,
   "w_hedef_rad_s": 0.9861,
   "v_olculen": 0.0,
   "w_olculen_rad_s": 0.0013,
   "w_orani": 0.0013,
   "yanal_ivme_m_s2": 0.0,
   "en_buyuk_yatma_derece": 0.0,
   "teker_yuk_en_az_N": 60.7826,
   "tork_ort_Nm": [
    1.225,
    1.2251,
    1.225,
    1.2251
   ]
  },
  {
   "v_komut": 1.0,
   "w_komut": 1.0,
   "takim": "mu_0.5",
   "teker_hedef_m_s": [
    0.253,
    0.39
   ],
   "v_hedef": 0.3215,
   "w_hedef_rad_s": 0.3171,
   "v_olculen": 0.3208,
   "w_olculen_rad_s": 0.0004,
   "w_orani": 0.0013,
   "yanal_ivme_m_s2": 0.0,
   "en_buyuk_yatma_derece": 0.0,
   "teker_yuk_en_az_N": 60.7829,
   "tork_ort_Nm": [
    0.223,
    0.223,
    0.5647,
    0.5647
   ]
  },
  {
   "v_komut": 0.3,
   "w_komut": 0.5,
   "takim": "mu_0.5",
   "teker_hedef_m_s": [
    0.1856,
    0.39
   ],
   "v_hedef": 0.2878,
   "w_hedef_rad_s": 0.473,
   "v_olculen": 0.2838,
   "w_olculen_rad_s": 0.0006,
   "w_orani": 0.0013,
   "yanal_ivme_m_s2": 0.0,
   "en_buyuk_yatma_derece": 0.0,
   "teker_yuk_en_az_N": 60.7835,
   "tork_ort_Nm": [
    0.4168,
    0.4168,
    0.7584,
    0.7585
   ]
  },
  {
   "v_komut": 0.0,
   "w_komut": 1.0,
   "takim": "durma_9kgcm",
   "teker_hedef_m_s": [
    -0.213,
    0.213
   ],
   "v_hedef": 0.0,
   "w_hedef_rad_s": 0.9861,
   "v_olculen": 0.0,
   "w_olculen_rad_s": 0.0005,
   "w_orani": 0.0006,
   "yanal_ivme_m_s2": 0.0,
   "en_buyuk_yatma_derece": 0.0,
   "teker_yuk_en_az_N": 60.7809,
   "tork_ort_Nm": [
    0.526,
    0.526,
    0.526,
    0.526
   ]
  },
  {
   "v_komut": 1.0,
   "w_komut": 1.0,
   "takim": "durma_9kgcm",
   "teker_hedef_m_s": [
    0.253,
    0.39
   ],
   "v_hedef": 0.3215,
   "w_hedef_rad_s": 0.3171,
   "v_olculen": 0.2774,
   "w_olculen_rad_s": 0.0002,
   "w_orani": 0.0006,
   "yanal_ivme_m_s2": 0.0,
   "en_buyuk_yatma_derece": 0.0,
   "teker_yuk_en_az_N": 60.7815,
   "tork_ort_Nm": [
    0.0017,
    0.0017,
    0.3399,
    0.3399
   ]
  },
  {
   "v_komut": 0.3,
   "w_komut": 0.5,
   "takim": "durma_9kgcm",
   "teker_hedef_m_s": [
    0.1856,
    0.39
   ],
   "v_hedef": 0.2878,
   "w_hedef_rad_s": 0.473,
   "v_olculen": 0.2404,
   "w_olculen_rad_s": 0.0003,
   "w_orani": 0.0006,
   "yanal_ivme_m_s2": 0.0,
   "en_buyuk_yatma_derece": 0.0,
   "teker_yuk_en_az_N": 60.7817,
   "tork_ort_Nm": [
    0.0815,
    0.0815,
    0.4231,
    0.4231
   ]
  }
 ],
 "yerinde_donus_mu_esigi": [
  {
   "mu": 0.2,
   "durma_torku_Nm": 2.059,
   "w_olculen_rad_s": 0.2417,
   "w_hedef_rad_s": 0.9861
  },
  {
   "mu": 0.2,
   "durma_torku_Nm": 0.883,
   "w_olculen_rad_s": 0.0008,
   "w_hedef_rad_s": 0.9861
  },
  {
   "mu": 0.3,
   "durma_torku_Nm": 2.059,
   "w_olculen_rad_s": 0.1313,
   "w_hedef_rad_s": 0.9861
  },
  {
   "mu": 0.3,
   "durma_torku_Nm": 0.883,
   "w_olculen_rad_s": 0.0005,
   "w_hedef_rad_s": 0.9861
  },
  {
   "mu": 0.35,
   "durma_torku_Nm": 2.059,
   "w_olculen_rad_s": 0.085,
   "w_hedef_rad_s": 0.9861
  },
  {
   "mu": 0.35,
   "durma_torku_Nm": 0.883,
   "w_olculen_rad_s": 0.0005,
   "w_hedef_rad_s": 0.9861
  },
  {
   "mu": 0.4,
   "durma_torku_Nm": 2.059,
   "w_olculen_rad_s": 0.0505,
   "w_hedef_rad_s": 0.9861
  },
  {
   "mu": 0.4,
   "durma_torku_Nm": 0.883,
   "w_olculen_rad_s": 0.0005,
   "w_hedef_rad_s": 0.9861
  },
  {
   "mu": 0.45,
   "durma_torku_Nm": 2.059,
   "w_olculen_rad_s": 0.0028,
   "w_hedef_rad_s": 0.9861
  },
  {
   "mu": 0.45,
   "durma_torku_Nm": 0.883,
   "w_olculen_rad_s": 0.0005,
   "w_hedef_rad_s": 0.9861
  },
  {
   "mu": 0.5,
   "durma_torku_Nm": 2.059,
   "w_olculen_rad_s": 0.0013,
   "w_hedef_rad_s": 0.9861
  },
  {
   "mu": 0.5,
   "durma_torku_Nm": 0.883,
   "w_olculen_rad_s": 0.0005,
   "w_hedef_rad_s": 0.9861
  },
  {
   "mu": 0.6,
   "durma_torku_Nm": 2.059,
   "w_olculen_rad_s": 0.0013,
   "w_hedef_rad_s": 0.9861
  },
  {
   "mu": 0.6,
   "durma_torku_Nm": 0.883,
   "w_olculen_rad_s": 0.0005,
   "w_hedef_rad_s": 0.9861
  },
  {
   "mu": 0.8,
   "durma_torku_Nm": 2.059,
   "w_olculen_rad_s": 0.0013,
   "w_hedef_rad_s": 0.9861
  },
  {
   "mu": 0.8,
   "durma_torku_Nm": 0.883,
   "w_olculen_rad_s": 0.0005,
   "w_hedef_rad_s": 0.9861
  }
 ],
 "yerinde_firmware_ve_tam_pwm": [
  {
   "mu": 0.4,
   "durma_torku_Nm": 2.059,
   "surus": "firmware_u0.55",
   "w_olculen_rad_s": 0.0505,
   "tork_ort_Nm": [
    1.0276,
    1.0651,
    0.995,
    1.0771
   ]
  },
  {
   "mu": 0.4,
   "durma_torku_Nm": 2.059,
   "surus": "tam_pwm_u1",
   "w_olculen_rad_s": 0.2989,
   "tork_ort_Nm": [
    1.1309,
    1.1965,
    1.005,
    1.3234
   ]
  },
  {
   "mu": 0.4,
   "durma_torku_Nm": 0.883,
   "surus": "firmware_u0.55",
   "w_olculen_rad_s": 0.0005,
   "tork_ort_Nm": [
    0.526,
    0.526,
    0.526,
    0.526
   ]
  },
  {
   "mu": 0.4,
   "durma_torku_Nm": 0.883,
   "surus": "tam_pwm_u1",
   "w_olculen_rad_s": 0.001,
   "tork_ort_Nm": [
    0.9631,
    0.9631,
    0.9631,
    0.9631
   ]
  },
  {
   "mu": 0.5,
   "durma_torku_Nm": 2.059,
   "surus": "firmware_u0.55",
   "w_olculen_rad_s": 0.0013,
   "tork_ort_Nm": [
    1.225,
    1.2251,
    1.225,
    1.2251
   ]
  },
  {
   "mu": 0.5,
   "durma_torku_Nm": 2.059,
   "surus": "tam_pwm_u1",
   "w_olculen_rad_s": 0.1593,
   "tork_ort_Nm": [
    1.2543,
    0.8212,
    0.7488,
    1.2895
   ]
  },
  {
   "mu": 0.5,
   "durma_torku_Nm": 0.883,
   "surus": "firmware_u0.55",
   "w_olculen_rad_s": 0.0005,
   "tork_ort_Nm": [
    0.526,
    0.526,
    0.526,
    0.526
   ]
  },
  {
   "mu": 0.5,
   "durma_torku_Nm": 0.883,
   "surus": "tam_pwm_u1",
   "w_olculen_rad_s": 0.001,
   "tork_ort_Nm": [
    0.9631,
    0.9631,
    0.9631,
    0.9631
   ]
  },
  {
   "mu": 0.8,
   "durma_torku_Nm": 2.059,
   "surus": "firmware_u0.55",
   "w_olculen_rad_s": 0.0013,
   "tork_ort_Nm": [
    1.225,
    1.2251,
    1.225,
    1.2251
   ]
  },
  {
   "mu": 0.8,
   "durma_torku_Nm": 2.059,
   "surus": "tam_pwm_u1",
   "w_olculen_rad_s": 0.1165,
   "tork_ort_Nm": [
    1.3508,
    0.9956,
    0.8849,
    1.4575
   ]
  },
  {
   "mu": 0.8,
   "durma_torku_Nm": 0.883,
   "surus": "firmware_u0.55",
   "w_olculen_rad_s": 0.0005,
   "tork_ort_Nm": [
    0.526,
    0.526,
    0.526,
    0.526
   ]
  },
  {
   "mu": 0.8,
   "durma_torku_Nm": 0.883,
   "surus": "tam_pwm_u1",
   "w_olculen_rad_s": 0.001,
   "tork_ort_Nm": [
    0.9631,
    0.9631,
    0.9631,
    0.9631
   ]
  }
 ],
 "el_hesabi_taban_analiz_yerinde": [
  {
   "mu": 0.4,
   "en_cok_kgcm": 13.11,
   "oran_stall": 0.62,
   "omni": false
  },
  {
   "mu": 0.5,
   "en_cok_kgcm": 16.19,
   "oran_stall": 0.77,
   "omni": false
  },
  {
   "mu": 0.6,
   "en_cok_kgcm": 19.26,
   "oran_stall": 0.92,
   "omni": false
  }
 ],
 "el_hesabi_tek_formul": "sürekli yerinde dönüşte teker başına F = mu N 0,65 (L/T = 0,37/0,432; Coulomb), T = F r; firmware w = 1 rad/s'de u = 0,213/0,39 = 0,55 -> durmada T = 0,55 x 1,09 x T_durma"
}
```

## tork

```json
{
 "kosular": [
  {
   "takim": "ana",
   "egim_derece": 0,
   "rampa_kipi": false,
   "v_komut": 0.3,
   "tepe_tork_Nm": 0.4558,
   "tepe_durma_orani": 0.2214,
   "tepe_surekli_orani": 0.7376,
   "sabit_hizda_tork_Nm": 0.1708,
   "sabit_hiz_m_s": 0.2972,
   "kalkista_geri_kayma_hizi_m_s": 0.0,
   "el_hesabi_tork_Nm": 0.3761,
   "el_hesabi_formul": "T = m (g sin a + a_firmware + g cos a crr) r / 4 + disli"
  },
  {
   "takim": "ana",
   "egim_derece": 0,
   "rampa_kipi": false,
   "v_komut": 1.0,
   "tepe_tork_Nm": 0.4566,
   "tepe_durma_orani": 0.2218,
   "tepe_surekli_orani": 0.7389,
   "sabit_hizda_tork_Nm": 0.1708,
   "sabit_hiz_m_s": 0.3961,
   "kalkista_geri_kayma_hizi_m_s": 0.0,
   "el_hesabi_tork_Nm": 0.3761,
   "el_hesabi_formul": "T = m (g sin a + a_firmware + g cos a crr) r / 4 + disli"
  },
  {
   "takim": "ana",
   "egim_derece": 5,
   "rampa_kipi": true,
   "v_komut": 1.0,
   "tepe_tork_Nm": 0.579,
   "tepe_durma_orani": 0.2812,
   "tepe_surekli_orani": 0.937,
   "sabit_hizda_tork_Nm": 0.5218,
   "sabit_hiz_m_s": 0.3291,
   "kalkista_geri_kayma_hizi_m_s": -0.0198,
   "el_hesabi_tork_Nm": 0.5625,
   "el_hesabi_formul": "T = m (g sin a + a_firmware + g cos a crr) r / 4 + disli"
  },
  {
   "takim": "ana",
   "egim_derece": 5,
   "rampa_kipi": false,
   "v_komut": 1.0,
   "tepe_tork_Nm": 0.8073,
   "tepe_durma_orani": 0.3921,
   "tepe_surekli_orani": 1.3063,
   "sabit_hizda_tork_Nm": 0.5218,
   "sabit_hiz_m_s": 0.3291,
   "kalkista_geri_kayma_hizi_m_s": -0.0096,
   "el_hesabi_tork_Nm": 0.7267,
   "el_hesabi_formul": "T = m (g sin a + a_firmware + g cos a crr) r / 4 + disli"
  },
  {
   "takim": "ana",
   "egim_derece": 10,
   "rampa_kipi": true,
   "v_komut": 1.0,
   "tepe_tork_Nm": 0.9274,
   "tepe_durma_orani": 0.4504,
   "tepe_surekli_orani": 1.5006,
   "sabit_hizda_tork_Nm": 0.8702,
   "sabit_hiz_m_s": 0.2626,
   "kalkista_geri_kayma_hizi_m_s": -0.0767,
   "el_hesabi_tork_Nm": 0.9094,
   "el_hesabi_formul": "T = m (g sin a + a_firmware + g cos a crr) r / 4 + disli"
  },
  {
   "takim": "durma_9kgcm",
   "egim_derece": 0,
   "rampa_kipi": false,
   "v_komut": 0.3,
   "tepe_tork_Nm": 0.4144,
   "tepe_durma_orani": 0.4693,
   "tepe_surekli_orani": 0.6706,
   "sabit_hizda_tork_Nm": 0.1708,
   "sabit_hiz_m_s": 0.2538,
   "kalkista_geri_kayma_hizi_m_s": 0.0,
   "el_hesabi_tork_Nm": 0.3761,
   "el_hesabi_formul": "T = m (g sin a + a_firmware + g cos a crr) r / 4 + disli"
  },
  {
   "takim": "durma_9kgcm",
   "egim_derece": 0,
   "rampa_kipi": false,
   "v_komut": 1.0,
   "tepe_tork_Nm": 0.4338,
   "tepe_durma_orani": 0.4913,
   "tepe_surekli_orani": 0.7019,
   "sabit_hizda_tork_Nm": 0.1708,
   "sabit_hiz_m_s": 0.3527,
   "kalkista_geri_kayma_hizi_m_s": 0.0,
   "el_hesabi_tork_Nm": 0.3761,
   "el_hesabi_formul": "T = m (g sin a + a_firmware + g cos a crr) r / 4 + disli"
  },
  {
   "takim": "durma_9kgcm",
   "egim_derece": 5,
   "rampa_kipi": true,
   "v_komut": 1.0,
   "tepe_tork_Nm": 0.5775,
   "tepe_durma_orani": 0.654,
   "tepe_surekli_orani": 0.9344,
   "sabit_hizda_tork_Nm": 0.5218,
   "sabit_hiz_m_s": 0.1965,
   "kalkista_geri_kayma_hizi_m_s": -0.0454,
   "el_hesabi_tork_Nm": 0.5625,
   "el_hesabi_formul": "T = m (g sin a + a_firmware + g cos a crr) r / 4 + disli"
  },
  {
   "takim": "durma_9kgcm",
   "egim_derece": 5,
   "rampa_kipi": false,
   "v_komut": 1.0,
   "tepe_tork_Nm": 0.7444,
   "tepe_durma_orani": 0.8431,
   "tepe_surekli_orani": 1.2046,
   "sabit_hizda_tork_Nm": 0.5218,
   "sabit_hiz_m_s": 0.1965,
   "kalkista_geri_kayma_hizi_m_s": -0.0201,
   "el_hesabi_tork_Nm": 0.7267,
   "el_hesabi_formul": "T = m (g sin a + a_firmware + g cos a crr) r / 4 + disli"
  },
  {
   "takim": "durma_9kgcm",
   "egim_derece": 10,
   "rampa_kipi": true,
   "v_komut": 1.0,
   "tepe_tork_Nm": 0.915,
   "tepe_durma_orani": 1.0363,
   "tepe_surekli_orani": 1.4806,
   "sabit_hizda_tork_Nm": 0.8702,
   "sabit_hiz_m_s": 0.0416,
   "kalkista_geri_kayma_hizi_m_s": -0.1742,
   "el_hesabi_tork_Nm": 0.9094,
   "el_hesabi_formul": "T = m (g sin a + a_firmware + g cos a crr) r / 4 + disli"
  }
 ],
 "el_hesabi_taban_analiz": {
  "duz": {
   "rampa": 0.0,
   "a": 0.5,
   "F_N": 20.9,
   "T_kgcm": 3.33,
   "oran": 0.528
  },
  "rampa5": {
   "rampa": 5.0,
   "a": 0.5,
   "F_N": 43.3,
   "T_kgcm": 6.9,
   "oran": 1.095
  },
  "rampa5_yavas": {
   "rampa": 5.0,
   "a": 0.25,
   "F_N": 36.7,
   "T_kgcm": 5.85,
   "oran": 0.929
  },
  "rampa5_durus": {
   "rampa": 5.0,
   "a": 0.0,
   "F_N": 30.2,
   "T_kgcm": 4.81,
   "oran": 0.763
  },
  "rampa5_yuk2": {
   "rampa": 5.0,
   "a": 0.5,
   "F_N": 46.6,
   "T_kgcm": 7.43,
   "oran": 1.179
  },
  "v3": {
   "kutle_kg": 18.6,
   "T_kgcm": 4.9,
   "oran": 0.77,
   "kaynak": "README V3 farki (rampa 5 derece, a 0,5)"
  }
 },
 "birim_not_": "1 N*m = 10,197 kg*cm; durma 2,059 N*m = 21 kg*cm; sürekli 0,618 N*m = 6,3 kg*cm (TAHMİN)"
}
```

