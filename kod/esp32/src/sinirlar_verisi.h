// OTOMATIK URETILDI: kod/jestler/jest_uret.py -- ELLE DUZENLEME.
// Kaynak: kod/ortak/eklem_sinirlari.json teker.ivme_sinir_m_s2 (Ahmet'in CAD betiginden; karar 29 Ekim 2026)
// Degistirmek icin JSON'u tazele (git show origin/lale-duzeltme:kod/ortak/eklem_sinirlari.json),
// sonra: py -3 kod/jestler/jest_uret.py
// Bu dosya yalniz motorlar.cpp tarafindan include edilir. Birim: m/s^2 (teker cizgisel ivmesi).
#pragma once

static constexpr float IVME_DUZ_SURUS = 0.5f;   // duz zeminde hizlanma
static constexpr float IVME_DUZ_FREN = 1.8f;   // duz zeminde yavaslama / fren (dur, bekci)
static constexpr float IVME_RAMPA_SURUS = 0.1f;   // rampa kipinde hizlanma
static constexpr float IVME_RAMPA_FREN = 0.1f;   // rampa kipinde yavaslama / fren
