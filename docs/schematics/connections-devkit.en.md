> **English** · [Polski](connections-devkit.pl.md)

# Connections — ESP32 DevKit V1 + expansion board

Module: **ESP32-DevKitC / DevKit V1** (38 pin) + **38P expansion board** — ESP plugs into the adapter; pins on headers / screw terminals.

**Active state (2026-09):** powered from **18650**, MOSFET on sensor GND, battery monitoring on GPIO34. USB for flashing only.

---

## 1. Battery power (active)

| From | To |
|------|-----|
| **18650 (+)** | **BAT+** — MT3608 **IN+**, **C1 (+)**, **R5** (GPIO34 divider) |
| **18650 (−)** | **GND** — holder −, MT3608 IN−/OUT−, ESP GND, C1 (−), R6, R2, R3 |
| MT3608 **OUT+** (~5 V) | **ESP 5V/VIN**, **C2**, **sensor VCC** |
| MT3608 **IN−** / **OUT−** | **GND** |

**USB:** disconnected in operation. Connect only for flashing (do not power USB + cell in parallel without a charger module).

### Switching USB ↔ battery (one-time rewiring)

| Element | USB (debug) | Battery (operation) |
|---------|-------------|---------------------|
| ESP 5V/VIN | USB | MT3608 OUT+ |
| MT3608 IN+ | +5 V USB rail | BAT+ |
| C1 (+) | +5 V USB | BAT+ |
| GPIO34 | free | R5/R6 divider from BAT+ |

Everything else (Trig, Echo, Q1) **unchanged**.

---

## 2. MT3608 + MOSFET (Q1)

| From | To |
|------|-----|
| MT3608 **IN+** | **BAT+** |
| MT3608 **IN−** / **OUT−** | **GND** |
| MT3608 **OUT+** | **~5.0 V** — ESP 5V/VIN, **C2**, **sensor VCC** |
| **Sensor GND** | **Q1 Drain (pin 2)** — **not** directly to GND |
| Q1 **Source (pin 3)** | **GND** |
| Q1 **Gate (pin 1)** | **GPIO4** + **R3 10k** → **GND** |

**Logic:** GPIO4 = HIGH → Q1 ON → sensor GND to ground → measurement. GPIO4 = LOW → sensor partially disconnected (VCC still 5 V; bleed via Echo/Trig).

**Do not connect:** OUT+ to Q1 Drain; Q1 on MT3608 IN−.

### IRLZ44N orientation (TO-220, front view, pins down)

| Pin | Name | Connection |
|-----|------|------------|
| 1 | GATE | GPIO4 + R3 |
| 2 | DRAIN | Sensor GND |
| 3 | SOURCE | GND |

Metal tab = **DRAIN**.

---

## 3. Battery divider (DevKit)

```
BAT+ ──[R5 100k]── GPIO34 ──[R6 100k]── GND
```

Firmware: `battery_adc_multiplier` = V_bat / V_GPIO34 (calibrate with a multimeter).

FireBeetle: built-in divider — no R5/R6, `multiply: 2.0`.

---

## 4. ESP32 — GPIO map

| Function | GPIO | Notes |
|----------|------|-------|
| sensor_power (Q1 Gate) | **GPIO4** | Not GPIO16 (U2_RXD on pinout) |
| TRIG | **GPIO25** | no divider |
| ECHO + divider | **GPIO26** | R1 10k → GPIO26 → R2 20k → GND |
| Battery ADC | **GPIO34** | input only |
| Wake (optional) | **GPIO33** | SW1 → GND; **disabled** in YAML without button |

**Do not use GPIO6–11** (flash).

---

## 5. JSN-SR04T-V3.3 sensor (Mode 0)

**MODE open** (no bridge on M1/M2/M3).

| Module pin | Connection |
|------------|------------|
| **VCC** | MT3608 OUT+ + C2 |
| **GND** | **Q1 Drain** (not directly GND) |
| **Trig / RX** | GPIO25 |
| **Echo / TX** | R1 → GPIO26 → R2 → GND |

---

## 6. Wake button (optional — not connected)

```
GPIO33 ----[ SW1 ]---- GND
```

Uncomment `wakeup_pin` in YAML only after connecting SW1.

---

## 7. Hardware tests

### Without cell
- BAT+ ↔ GND: no short circuit

### With cell
1. MT3608 OUT+ = **~5.0 V**
2. GPIO34 ≈ **half** of cell voltage (with 100k/100k)
3. **Q1 OFF** (GPIO4 LOW): VCC–DRAIN ≈ **4–4.5 V**; DRAIN–GND ≈ **0.5–1 V** (Echo bleed)
4. **Q1 ON** (GPIO4 HIGH): DRAIN–GND ≈ **0 V**; VCC–DRAIN ≈ **5 V**
5. Log / HA: `Ultrasonic OK`, `Battery Voltage` ≈ multimeter on holder

### Q1 test — do not use Ω on Drain with VCC=5 V
With Gate shorted to Source: D–S should be **OL**. Reading ~0.04 Ω with floating Gate = meter charging the gate.

---

## 8. Firmware

- File: `esphome/tank-level-sensor.yaml`
- `enable_deep_sleep: true`, `sleep_duration: 4h`
- `enable_sensor_power: true`, `pin_sensor_power: GPIO4`
- `enable_battery_check: true`
- ESPHome 2026.8: `toolchain: platformio`

---

## 9. Target hardware

| Element | When |
|---------|------|
| Solar panel + TP4056 | 18650 charging |
| FireBeetle | smaller board, built-in charger + ADC |
| P-MOS AO3401A on VCC | full sensor power cut-off |

FireBeetle details: [`connections-firebeetle.en.md`](connections-firebeetle.en.md).
