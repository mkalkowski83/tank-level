> **English** · [Polski](2026-08-25-szambo-level-sensor-design.pl.md)

# Septic tank level sensor — hardware + ESPHome specification

**Date:** 2026-08-25  
**Last updated:** 2026-09-01  
**Status:** **DevKit V1 + 18650 + MOSFET** prototype — ultrasonic measurement, deep sleep, battery monitoring **working**. Target: solar panel, charging, tank installation, migration to FireBeetle.

**Related documents:**
- DevKit connections (USB / battery): [`docs/schematics/connections-devkit.en.md`](../../schematics/connections-devkit.en.md)
- Target connections (FireBeetle): [`docs/schematics/connections-firebeetle.en.md`](../../schematics/connections-firebeetle.en.md)
- Implementation plan: [`docs/superpowers/plans/2026-08-25-szambo-level-sensor.en.md`](../plans/2026-08-25-szambo-level-sensor.en.md)
- Firmware: [`esphome/szambo-level-sensor.yaml`](../../../esphome/szambo-level-sensor.yaml)

## Goal

Wireless (Wi‑Fi) level measurement in the septic tank several times a day, integrated with Home Assistant via ESPHome. Power: 18650 cell (solar panel and charging — next step). Energy saving: 4 h deep sleep between measurements, MOSFET low-side on sensor GND.

## Components

| Element | Model / parameter | Notes |
|---------|-------------------|-------|
| Microcontroller (active) | **ESP32 DevKit V1** (38 pin) + expansion board | Powered from MT3608 OUT+ (~5 V); USB for flashing only |
| Microcontroller (target) | DFRobot FireBeetle ESP32-E (DFR0654) | Built-in charger, battery ADC on GPIO34 |
| Sensor | **JSN-SR04T-V3.3** | Mode 0 (Trig/Echo); VCC 5 V; **Trig ≥20 µs**; dead zone ~20–25 cm |
| Battery | 18650 Li-ion **without** PCB protected | Holder; software cutoff; **no charging** in prototype |
| Step-up | MT3608 | IN+ ← BAT+; OUT+ = **5.0 V** → ESP 5V/VIN + sensor VCC |
| MOSFET | IRLZ44N (logic level, TO-220) | **Low-side on sensor GND**; Gate → **GPIO4** + R3 10 kΩ → GND |
| Electrolytic capacitor | 1000 µF / 6.3 V | BAT+ (C1) |
| Ceramic capacitor | 100 nF | 5 V at sensor (C2) |
| Resistors | 10 kΩ + 20 kΩ | Echo divider (5 V → ~3.3 V on GPIO26) |
| Resistors | 100 kΩ ×2 | Battery divider BAT+ → GPIO34 → GND (DevKit) |
| Resistor | 10 kΩ | MOSFET gate pulldown (R3) |
| Button | Tact switch (optional) | GPIO33 → GND (wake — **disabled** in YAML without wiring) |
| Mounting | Breadboard / perfboard | MT3608, Q1, C1, C2, resistors |
| Charging (planned) | USB 5 V solar panel + TP4056 or FireBeetle | **Not connected** |

## Active prototype (DevKit V1 + battery — 2026-09)

Wiring per [`connections-devkit.en.md`](../../schematics/connections-devkit.en.md) (battery section).

| Element | State |
|---------|-------|
| ESP power | **MT3608 OUT+** (~5 V) from 18650 cell |
| MT3608 IN+ | **BAT+** (holder + C1) |
| MOSFET Q1 | **Active** — sensor GND through Drain; Gate → **GPIO4** |
| Sensor | **JSN-SR04T-V3.3**, Mode 0 |
| Battery ADC | **GPIO34** + 100k/100k divider; calibrated `battery_adc_multiplier` |
| Deep sleep | **4 h**; `wakeup_pin` **disabled** (floating GPIO33 woke immediately) |
| Test calibration | `distance_empty_cm: 300`, `distance_full_cm: 160` (3 m wall) |
| USB | Flashing only; **disconnected** in operation |

### JSN-SR04T-V3.3 — requirements

| Parameter | Value |
|-----------|-------|
| Mode | **Mode 0** — **MODE** pad without bridge to M1/M2/M3 |
| PCB pins | **Trig/RX** = trigger, **Echo/TX** = echo |
| Trig pulse | **≥20 µs** (`ultrasonic_pulse_time: 20us`) |
| Range | ~20 cm – 600 cm (from probe **membrane**) |
| Echo | **10 kΩ / 20 kΩ** divider on GPIO26 |

### Signal wiring

```
Trig (RX)  ────────────────────── GPIO25
Echo (TX)  ──[R1 10k]── GPIO26 ──[R2 20k]── GND

BAT+ ──[R5 100k]── GPIO34 ──[R6 100k]── GND

Sensor GND ──► Q1 DRAIN (pin 2)
Q1 SOURCE (pin 3) ──► GND
Q1 GATE (pin 1) ──┬── GPIO4
                  └── R3 10k ──► GND
```

**GPIO16** not used — on DevKit marked as U2_RXD; Q1 control on **GPIO4**.

## Power architecture

### DevKit + 18650 (no charging)

```
18650 (+) ──► BAT+ ──┬──► MT3608 IN+
                     ├──► C1 (+)
                     └──► R5 (divider → GPIO34)

18650 (−) ──► GND (common ground)

MT3608 OUT+ (~5 V) ──┬──► ESP 5V/VIN
                     ├──► C2, sensor VCC
                     └── (always on when cell connected)

JSN GND ◄── Q1 DRAIN
Q1 SOURCE ──► GND
Q1 GATE ──► GPIO4 + R3 10k → GND
```

MT3608 **runs continuously** (~2–5 mA idle). Q1 **cuts sensor ground** between measurements — **partially** (see MOSFET section).

### Target: FireBeetle + panel

```
18650 (+) ──► FireBeetle BAT+ ──┬──► MT3608 IN+ ──► C1
USB panel ──► FireBeetle USB (charging)
GPIO34 ── built-in divider (multiply: 2.0)
```

### MOSFET low-side — confirmed behavior

| Q1 state | DRAIN ↔ GND | VCC ↔ DRAIN | Notes |
|----------|-------------|-------------|-------|
| **OFF** (GPIO4 LOW) | ~0.8 V | **~4.2 V** | Bleed via Echo/Trig → GPIO → GND; sensor still partially powered |
| **ON** (GPIO4 HIGH) | **~0 V** | **~5 V** | Full power; measurement OK |

**Conclusion:** Q1 **works** (gate control confirmed). Low-side GND **does not** fully cut sensor power — current returns through signal lines. Full cut-off target: **P-MOS on VCC** (AO3401A).

### IRLZ44N orientation (TO-220, front view, pins down)

| Pin | Name | Connection |
|-----|------|------------|
| 1 | GATE | **GPIO4** + R3 10 kΩ → GND |
| 2 | DRAIN | Sensor GND |
| 3 | SOURCE | GND |

Metal tab = **DRAIN**.

### Rejected variants (confirmed by tests)

#### 1. IRLZ44N on MT3608 IN−

**Result:** **Does not work** — IN− and OUT− share module ground; boost overheats.

#### 2. IRLZ44N high-side on VCC (OUT+ → DRAIN)

**Result:** **Does not work** — with 3.3 V gate, sensor VCC ≈ 0.94 V instead of 5 V.

#### 3. wakeup_pin GPIO33 without button

**Result:** Immediate wake from deep sleep (~32 s cycle instead of 4 h). **Fix:** `wakeup_pin` commented out until SW1 is wired.

### Target energy saving plan

| Variant | When | Note |
|---------|------|------|
| **AO3401A** P-MOS on VCC | After battery tests | Full 5 V sensor cut-off |
| **Panel + TP4056** or FireBeetle | Next step | 18650 replenishment |
| **1S BMS** | Optional | Hard cell protection |

## Battery voltage measurement

### DevKit (active)

External **100 kΩ / 100 kΩ** divider: BAT+ → GPIO34 → GND.

ESPHome:
- `pin: GPIO34`, `attenuation: 12db`
- `battery_adc_multiplier` — calibration: **V_bat / V_GPIO34** (example: 4.13 / 1.94 ≈ **2.13**)

Calibration: simultaneous multimeter reading on holder and GPIO34 node (ESP can disconnect for reference measurement).

### FireBeetle (target)

Built-in 1 MΩ / 1 MΩ divider → `multiply: 2.0`, no extra resistors.

## GPIO map (DevKit — active)

| GPIO | Function | Direction | ESPHome |
|------|----------|-----------|---------|
| **GPIO4** | `sensor_power` — Q1 Gate | Output | `switch` gpio |
| GPIO25 | Ultrasonic Trig | Output | `ultrasonic` trigger_pin |
| GPIO26 | Echo (after divider) | Input | `ultrasonic` echo_pin |
| GPIO33 | Wake button (optional) | Input | `wakeup_pin` — **disabled** |
| GPIO34 | Battery ADC | ADC input | `adc` + `battery_adc_multiplier` |

## Measurement sequence (firmware)

1. Wake by timer (**4 h**) or boot after flash.
2. Read battery → entities **Battery Voltage**, **Battery Status**, **Battery Low/Critical**.
3. If V > 3.1 V: **GPIO4 HIGH** → 1.5 s stabilization → ultrasonic (up to 5 attempts) → **GPIO4 LOW**.
4. If V ≤ 3.1 V: skip ultrasonic, enter deep sleep.
5. Update **Tank Distance**, **Tank Fill Level**; sync with HA (WiFi, max 45 s).
6. Deep sleep **4 h** (or retry up to 20 cycles on NAN if `sleep_until_valid`).

Script `boot_measure_then_sleep` — sleep only after valid reading (or low battery / retry limit).

## Hardware verification

### Before inserting cell

| Measurement | OK |
|-------------|-----|
| BAT+ ↔ GND | no short |
| OUT+ ↔ GND | no short |

### With cell (DC V) — MOSFET

| State | Measurement | OK |
|-------|-------------|-----|
| GPIO4 LOW | DRAIN ↔ GND | ~0.5–1 V (Echo bleed) or ~4–5 V (ideally cut off) |
| GPIO4 LOW | VCC ↔ DRAIN | ~4–4.5 V (partial power) |
| GPIO4 HIGH | DRAIN ↔ GND | **~0–0.3 V** |
| GPIO4 HIGH | VCC ↔ DRAIN | **~5 V** |

**Do not test Q1 in Ω mode on Drain with VCC powered** — use DC voltage.

### Multimeter Ω test on D–S

With **Gate shorted to Source** (OFF): D–S should be **OL** (high resistance). Reading ~0.04 Ω with floating Gate may be meter charging the gate — not necessarily damage.

## Software cutoff (no BMS)

| Voltage | Action |
|---------|--------|
| ≥ 3.7 V | Status `normal` |
| 3.3–3.7 V | Status `degraded` |
| ≤ 3.3 V | **Battery Low** ON; status `warning` |
| ≤ 3.1 V | Status `stop`; **no ultrasonic** measurement; deep sleep |
| ≤ 2.9 V | **Battery Critical** ON |

## Home Assistant / ESPHome

File: `esphome/szambo-level-sensor.yaml`

### Entities

| Entity | Unit | Meaning |
|--------|------|---------|
| **Tank Distance Raw** | m | Raw meters from driver (no `device_class` — HA does not convert to cm) |
| **Tank Distance** | cm | After ×100, filters, median |
| **Tank Fill Level** | % | From empty/full calibration |
| **Battery Voltage** | V | ADC GPIO34 × multiplier |
| **Battery Status** | text | `normal` / `degraded` / `warning` / `stop` / `critical` |
| **Battery Low** | binary | ON at ≤ 3.3 V |
| **Battery Critical** | binary | ON at ≤ 2.9 V |

### Substitutions (prototype production state)

| Key | Value |
|-----|-------|
| `enable_deep_sleep` | `true` |
| `sleep_duration` | `4h` |
| `enable_battery_check` | `true` |
| `enable_sensor_power` | `true` |
| `pin_sensor_power` | **GPIO4** |
| `battery_adc_multiplier` | calibrated (~2.11–2.13) |
| `sleep_until_valid` | `true` |
| `sleep_max_measure_cycles` | `20` |
| `distance_empty_cm` / `distance_full_cm` | **300 / 160** (3 m test); production **180 / 40** |

### Build (ESPHome 2026.8 in HA)

| Setting | Reason |
|---------|--------|
| `esp32.toolchain: platformio` | Workaround for `template instantiation depth` (GCC 14 / IDF) |
| No `captive_portal`, `web_server`, `wifi.ap` | Smaller build |
| `wifi.power_save_mode: light` | Energy saving |
| `api.encryption.key` | API encryption (`!secret szambo_level__encryption_key`) |

### m→cm conversion

`ultrasonic` component returns **meters**. Mandatory filter `return x * 100.0f` in **Tank Distance** pipeline.

## Troubleshooting

| Symptom | Cause | Action |
|---------|-------|--------|
| Reading **0.8 cm** at ~80 cm | Meters without ×100 | ×100 filter; Raw in m |
| **Tank Distance Raw** = cm in HA | `device_class: distance` | Remove device_class from Raw |
| Restart every ~32 s | `wakeup_pin` GPIO33 floating | Disable wakeup_pin |
| Battery HA ≠ multimeter | ADC + inaccurate divider | `battery_adc_multiplier = V_bat/V_GPIO34` |
| Readings with Q1 OFF | Echo/Trig bleed | Expected; target P-MOS on VCC |
| `template instantiation depth` | ESPHome 2026.8 + IDF | `toolchain: platformio` |
| ID `battery_low` PollingComponent | `component.update` on template | `publish_state()` in lambda |

## Power consumption (estimate)

| Configuration | Average draw | 2500 mAh |
|---------------|--------------|----------|
| No MOSFET, MT3608 + sensor 24/7 | ~15–20 mA | ~5–7 days |
| With MOSFET low-side (current) | ~8–12 mA | ~10–14 days |
| + solar panel (planned) | replenishment | target ~1 month |

MT3608 stays on; Q1 reduces sensor draw, not boost idle.

## Design decisions

| Topic | Decision |
|-------|----------|
| Sensor | **JSN-SR04T-V3.3** |
| Active prototype | **DevKit V1 + 18650 + Q1 on GPIO4** |
| sensor_power | **GPIO4** (not GPIO16 — UART) |
| MOSFET | Low-side GND — **works**, partial cut-off |
| Deep sleep | **4 h**; wakeup_pin disabled without SW1 |
| DevKit battery | 100k divider + `battery_adc_multiplier` |
| Charging | **Next step** (panel / TP4056 / FireBeetle) |
| Calibration | Test 300/160; production 180/40 |
| Build | `toolchain: platformio` for ESPHome fix |
| Rejected | Q1 on MT3608 IN−; high-side N-MOS on VCC |

## Next steps

1. Observe battery consumption over several days (HA: **Battery Voltage**).
2. Solar panel + charging module (TP4056 or FireBeetle).
3. Probe installation in enclosure / tank → calibration **180/40**.
4. Optional: P-MOS on VCC (AO3401A) for full sensor cut-off.
5. Migration to FireBeetle + native ESP-IDF after ESPHome stabilizes.
