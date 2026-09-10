> English · [Polski](connections-ao3401a.pl.md)

# Connections — ESP32 DevKit V1 + AO3401A (P-MOS high-side)

Module: **ESP32-DevKitC / DevKit V1** (38 pin), **without expansion board** — ESP wired directly to breadboard / perfboard.

**Active state (2026-09):** powered from **18650**, **AO3401A** on sensor VCC (P-MOS + NPN), battery monitoring on GPIO34. Deep sleep **8 h**. USB for flashing and stage 1 tests only.

Previous variant (IRLZ44N low-side): [`connections-devkit.en.md`](connections-devkit.en.md).

Migration spec: [`../superpowers/specs/2026-09-02-ao3401a-migration-design.en.md`](../superpowers/specs/2026-09-02-ao3401a-migration-design.en.md).

**Schematic (KiCad export):** [tank-level-devkit.pdf](tank-level-devkit.pdf) — source project: [`../kicad/tank-level-devkit/`](../kicad/tank-level-devkit/).

---

## 1. Battery power

| From | To |
|------|-----|
| **18650 (+)** | **BAT+** — MT3608 **IN+**, **C1 (+)**, **R5** (GPIO34 divider) |
| **18650 (−)** | **GND** — holder −, MT3608 IN−/OUT−, ESP GND, C1 (−), R6, R2 |
| MT3608 **OUT+** (~5 V) | **ESP 5V/VIN**, **R1** (Gate pull-up), AO3401A **SOURCE** |
| MT3608 **IN−** / **OUT−** | **GND** |

**USB:** disconnected in production. Use only for flash / stage 1 tests (do not power USB + cell in parallel without a charger module).

---

## 2. MT3608 + AO3401A (Q1) + NPN (Q2)

### Logic diagram

```
OUT+ (5 V) ───────────── SOURCE (S) AO3401A
DRAIN (D) AO3401A ────── sensor VCC (+ C2 → GND)
sensor GND ───────────── GND

GATE (G) ──┬── R1 10k ── OUT+ (5 V)
           └── Q2 collector (2N3904 / BC547)
Q2 emitter ───────────── GND
Q2 base ─── R2 10k ─── GPIO4
```

| From | To |
|------|-----|
| MT3608 **IN+** | **BAT+** |
| MT3608 **IN−** / **OUT−** | **GND** |
| MT3608 **OUT+** | **~5.0 V** — ESP 5V/VIN, **R1**, AO3401A **SOURCE** |
| AO3401A **DRAIN** | **sensor VCC** + **C2** |
| AO3401A **SOURCE** | **OUT+** (5 V) |
| AO3401A **GATE** | **R1** (10k → OUT+) + **Q2 collector** |
| **sensor GND** | **GND** (direct) |
| Q2 **base** | **GPIO4** via **R2 10k** |
| Q2 **emitter** | **GND** |

**Logic:** GPIO4 = **HIGH** → sensor **ON** (~5 V on VCC). GPIO4 = **LOW** → sensor **OFF** (~0 V on VCC).

**Do not connect:**
- OUT+ directly to DRAIN without SOURCE (IRLZ44N high-side mistake).
- Q1 / Q2 on MT3608 IN−.
- Sensor GND through MOSFET (that was the IRLZ44N layout).

### AO3401A on SOT-23 → DIP adapter

Component marking facing you, pins down:

| SOT-23 pin | Name | Connection |
|------------|------|------------|
| 1 | GATE | R1 + Q2 collector |
| 2 | SOURCE | OUT+ (5 V) |
| 3 | DRAIN | sensor VCC |

Verify **G / S / D** labels on the adapter board.

### NPN (2N3904 / BC547) — TO-92

Flat side facing you, pins down (typical):

| Pin | Name | Connection |
|-----|------|------------|
| 1 | Emitter | GND |
| 2 | Base | GPIO4 via R2 10k |
| 3 | Collector | AO3401A GATE |

Verify pinout on your part (multimeter diode mode B–E / B–C).

---

## 3. Battery divider (DevKit)

```
BAT+ ──[R5 100k]── GPIO34 ──[R6 100k]── GND
```

Firmware: `battery_adc_multiplier` = V_bat / V_GPIO34 (calibrate with a multimeter).

---

## 4. ESP32 — GPIO map

| Function | GPIO | Notes |
|----------|------|-------|
| sensor_power (Q2 base) | **GPIO4** | HIGH = sensor ON |
| TRIG | **GPIO25** | no divider |
| ECHO + divider | **GPIO26** | R1 10k → GPIO26 → R2 20k → GND |
| Battery ADC | **GPIO34** | input only |
| Wake (optional) | **GPIO33** | SW1 → GND; **disabled** in YAML without button |

**Do not use GPIO6–11** (flash).

---

## 5. JSN-SR04T-V3.3 sensor (Mode 0)

**MODE open** (no M1/M2/M3 bridge).

| Module pin | Connection |
|------------|------------|
| **VCC** | AO3401A **DRAIN** + C2 |
| **GND** | **GND** (direct) |
| **Trig / RX** | GPIO25 |
| **Echo / TX** | R1 → GPIO26 → R2 → GND |

---

## 6. Hardware tests

### Stage 0 — no cell

| Step | Measurement | OK |
|------|-------------|-----|
| 0.1 | BAT+ ↔ GND | no short |
| 0.2 | SOURCE ↔ OUT+ | ~0 Ω |
| 0.3 | DRAIN ↔ sensor VCC | ~0 Ω |
| 0.4 | sensor GND ↔ GND | ~0 Ω |

### Stage 1 — USB, deep sleep OFF (`enable_deep_sleep: false`)

| Step | Action | OK |
|------|--------|-----|
| 1.1 | MT3608 OUT+ | **~5.0 V** |
| 1.2 | GPIO4 LOW (sensor OFF) | **sensor VCC ≈ 0 V** |
| 1.3 | GPIO4 HIGH (sensor ON) | **sensor VCC ≈ 4.8–5 V** |
| 1.4 | ESPHome logs | `Ultrasonic OK`, sensible distance |
| 1.5 | GPIO34 | ≈ half cell voltage (if BAT+ connected) |

**Do not use Ω mode on DRAIN with power applied** — use DC voltage.

### Stage 2 — battery, 8 h deep sleep

| Step | Action | OK |
|------|--------|-----|
| 2.1 | `enable_deep_sleep: true`, `sleep_duration: 8h` | — |
| 2.2 | After ~8 h | new reading in Home Assistant |
| 2.3 | Battery Voltage | matches multimeter (± ADC) |

### Failure criteria — disconnect power immediately

| Symptom | Likely cause |
|---------|--------------|
| sensor VCC > 5.5 V | MT3608 wiring error |
| sensor VCC ≈ 5 V with GPIO4 LOW | wrong AO3401A orientation or missing NPN |
| MT3608 hot | short or Q1 on IN− (rejected variant) |
| No reading with VCC ≈ 5 V | Trig/Echo, not MOSFET |

---

## 7. Firmware

- File: `esphome/tank-level-sensor.yaml`
- Stage 1: `enable_deep_sleep: false`
- Stage 2: `enable_deep_sleep: true`, `sleep_duration: 8h`
- `enable_sensor_power: true`, `pin_sensor_power: GPIO4`
- `sensor_power`: **no** `inverted`
- `enable_battery_check: true`

---

## 8. BOM (delta vs IRLZ44N)

| Part | Qty | Notes |
|------|-----|-------|
| AO3401A | 1 | P-MOS, SOT-23 on DIP adapter |
| SOT-23 → DIP adapter | 1 | — |
| 2N3904 or BC547 | 1 | NPN, Gate driver |
| R1 10k | 1 | Gate pull-up → 5 V |
| R2 10k | 1 | NPN base ← GPIO4 |
| IRLZ44N | 0 | Replaced — do not mount in parallel |

---

## 9. Field results (limitations)

| Configuration | Runtime without charging |
|---------------|--------------------------|
| IRLZ44N + expansion board + 4 h sleep | **~3 days** (confirmed) |
| AO3401A + no expansion board + 8 h sleep | **TBD** |

MT3608 runs continuously (~2–5 mA) — multi-week autonomy requires charging (solar panel — next step).
