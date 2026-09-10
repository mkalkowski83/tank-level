> [English](connections-ao3401a.en.md) · **Polski**

# Połączenia — ESP32 DevKit V1 + AO3401A (P-MOS high-side)

Moduł: **ESP32-DevKitC / DevKit V1** (38 pin), **bez expansion board** — ESP podłączony bezpośrednio do płytki stykowej / uniwersalnej.

**Stan aktywny (2026-09):** zasilanie z **18650**, **AO3401A** na VCC czujnika (P-MOS + NPN), monitoring baterii na GPIO34. Deep sleep **8 h**. USB tylko do flash i testów (etap 1).

Poprzedni wariant (IRLZ44N low-side): [`connections-devkit.pl.md`](connections-devkit.pl.md).

Spec migracji: [`../superpowers/specs/2026-09-02-ao3401a-migration-design.pl.md`](../superpowers/specs/2026-09-02-ao3401a-migration-design.pl.md).

**Schemat ideowy (KiCad):** [tank-level-devkit.pdf](tank-level-devkit.pdf) — projekt źródłowy: [`../kicad/tank-level-devkit/`](../kicad/tank-level-devkit/).

---

## 1. Zasilanie z baterii

| Od | Do |
|----|-----|
| **18650 (+)** | **BAT+** — MT3608 **IN+**, **C1 (+)**, **R5** (dzielnik GPIO34) |
| **18650 (−)** | **GND** — holder −, MT3608 IN−/OUT−, ESP GND, C1 (−), R6, R2 |
| MT3608 **OUT+** (~5 V) | **ESP 5V/VIN**, **R1** (pull-up Gate), **SOURCE** AO3401A |
| MT3608 **IN−** / **OUT−** | **GND** |

**USB:** odłączony w eksploatacji. Podłącz tylko do flash / testów etapu 1 (nie zasilaj równolegle USB + ogniwo bez modułu ładowania).

---

## 2. MT3608 + AO3401A (Q1) + NPN (Q2)

### Schemat logiczny

```
OUT+ (5 V) ───────────── SOURCE (S) AO3401A
DRAIN (D) AO3401A ────── VCC czujnika (+ C2 → GND)
GND czujnika ─────────── GND

GATE (G) ──┬── R1 10k ── OUT+ (5 V)
           └── kolektor Q2 (2N3904 / BC547)
Emiter Q2 ────────────── GND
Baza Q2 ─── R2 10k ─── GPIO4
```

| Od | Do |
|----|-----|
| MT3608 **IN+** | **BAT+** |
| MT3608 **IN−** / **OUT−** | **GND** |
| MT3608 **OUT+** | **~5,0 V** — ESP 5V/VIN, **R1**, **SOURCE** AO3401A |
| AO3401A **DRAIN** | **VCC czujnika** + **C2** |
| AO3401A **SOURCE** | **OUT+** (5 V) |
| AO3401A **GATE** | **R1** (10k → OUT+) + **kolektor Q2** |
| **GND czujnika** | **GND** (bezpośrednio) |
| Q2 **baza** | **GPIO4** przez **R2 10k** |
| Q2 **emiter** | **GND** |

**Logika:** GPIO4 = **HIGH** → czujnik **ON** (~5 V na VCC). GPIO4 = **LOW** → czujnik **OFF** (~0 V na VCC).

**Nie łącz:**
- OUT+ bezpośrednio na DRAIN bez SOURCE (błąd high-side z IRLZ44N).
- Q1 / Q2 na IN− MT3608.
- GND czujnika przez MOSFET (to był układ IRLZ44N).

### AO3401A na adapterze SOT-23 → DIP

Patrząc na element od strony napisu, piny w dół:

| Pin SOT-23 | Nazwa | Połączenie |
|------------|-------|------------|
| 1 | GATE | R1 + kolektor Q2 |
| 2 | SOURCE | OUT+ (5 V) |
| 3 | DRAIN | VCC czujnika |

Sprawdź oznaczenia **G / S / D** na adapterze.

### NPN (2N3904 / BC547) — TO-92

Od płaskiej strony z napisem, piny w dół (typowo):

| Pin | Nazwa | Połączenie |
|-----|-------|------------|
| 1 | Emiter | GND |
| 2 | Baza | GPIO4 przez R2 10k |
| 3 | Kolektor | GATE AO3401A |

Zweryfikuj pinout na swoim egzemplarzu (multimetr, tryb diody B–E / B–C).

---

## 3. Dzielnik baterii (DevKit)

```
BAT+ ──[R5 100k]── GPIO34 ──[R6 100k]── GND
```

Firmware: `battery_adc_multiplier` = V_bat / V_GPIO34 (kalibracja miernikiem).

---

## 4. ESP32 — mapa GPIO

| Funkcja | GPIO | Uwagi |
|---------|------|-------|
| sensor_power (baza Q2) | **GPIO4** | HIGH = czujnik ON |
| TRIG | **GPIO25** | bez dzielnika |
| ECHO + dzielnik | **GPIO26** | R1 10k → GPIO26 → R2 20k → GND |
| ADC baterii | **GPIO34** | tylko wejście |
| Wake (opcjonalnie) | **GPIO33** | SW1 → GND; w YAML **wyłączony** bez przycisku |

**Nie używaj GPIO6–11** (flash).

---

## 5. Czujnik JSN-SR04T-V3.3 (Mode 0)

**MODE otwarty** (bez mostka M1/M2/M3).

| Pin modułu | Połączenie |
|------------|------------|
| **VCC** | **DRAIN** AO3401A + C2 |
| **GND** | **GND** (bezpośrednio) |
| **Trig / RX** | GPIO25 |
| **Echo / TX** | R1 → GPIO26 → R2 → GND |

---

## 6. Testy hardware

### Etap 0 — bez ogniwa

| Krok | Pomiar | OK |
|------|--------|-----|
| 0.1 | BAT+ ↔ GND | brak zwarcia |
| 0.2 | SOURCE ↔ OUT+ | ~0 Ω |
| 0.3 | DRAIN ↔ VCC czujnika | ~0 Ω |
| 0.4 | GND czujnika ↔ GND | ~0 Ω |

### Etap 1 — USB, deep sleep OFF (`enable_deep_sleep: false`)

| Krok | Akcja | OK |
|------|-------|-----|
| 1.1 | OUT+ MT3608 | **~5,0 V** |
| 1.2 | GPIO4 LOW (czujnik OFF) | **VCC czujnika ≈ 0 V** |
| 1.3 | GPIO4 HIGH (czujnik ON) | **VCC czujnika ≈ 4,8–5 V** |
| 1.4 | Logi ESPHome | `Ultrasonic OK`, sensowny dystans |
| 1.5 | GPIO34 | ≈ połowa napięcia ogniwa (jeśli BAT+ podłączone) |

**Nie testuj Ω na DRAIN przy zasilonym układzie** — używaj napięcia DC.

### Etap 2 — bateria, deep sleep 8 h

| Krok | Akcja | OK |
|------|-------|-----|
| 2.1 | `enable_deep_sleep: true`, `sleep_duration: 8h` | — |
| 2.2 | Po ~8 h | nowy pomiar w Home Assistant |
| 2.3 | Battery Voltage | zgodne z miernikiem (± ADC) |

### Kryteria awarii — natychmiast odłącz zasilanie

| Objaw | Prawdopodobna przyczyna |
|-------|-------------------------|
| VCC czujnika > 5,5 V | błąd okablowania MT3608 |
| VCC czujnika ≈ 5 V przy GPIO4 LOW | zła orientacja AO3401A lub brak NPN |
| MT3608 gorący | zwarcie lub Q1 na IN− (odrzucony wariant) |
| Brak pomiaru przy VCC ≈ 5 V | Trig/Echo, nie MOSFET |

---

## 7. Firmware

- Plik: `esphome/tank-level-sensor.yaml`
- Etap 1: `enable_deep_sleep: false`
- Etap 2: `enable_deep_sleep: true`, `sleep_duration: 8h`
- `enable_sensor_power: true`, `pin_sensor_power: GPIO4`
- `sensor_power`: **bez** `inverted`
- `enable_battery_check: true`

---

## 8. BOM (delta względem IRLZ44N)

| Element | Ilość | Uwagi |
|---------|-------|-------|
| AO3401A | 1 | P-MOS, SOT-23 na adapterze DIP |
| Adapter SOT-23 → DIP | 1 | — |
| 2N3904 lub BC547 | 1 | NPN, sterowanie Gate |
| R1 10k | 1 | Pull-up Gate → 5 V |
| R2 10k | 1 | Baza NPN ← GPIO4 |
| IRLZ44N | 0 | Zastąpiony — nie montować równolegle |

---

## 9. Wyniki terenowe (ograniczenia)

| Konfiguracja | Czas bez ładowania |
|--------------|-------------------|
| IRLZ44N + expansion board + sleep 4h | **~3 dni** (potwierdzone) |
| AO3401A + bez expansion board + sleep 8h | **do weryfikacji** |

MT3608 pracuje cały czas (~2–5 mA) — pełna autonomia tygodniowa wymaga ładowania (panel — kolejny krok).
