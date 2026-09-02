# Wiring Diagram — ESP32 DevKit Tank Level Sensor

Active prototype: **ESP32 DevKit V1** + **18650** + **MT3608** + **IRLZ44N** + **JSN-SR04T-V3.3**.

Detailed connection tables (Polish): [`polaczenia-devkit-usb.md`](polaczenia-devkit-usb.md)

---

## Block diagram

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    18650 Li-ion                         │
                    │                   (+) BAT+  (−) GND                     │
                    └────────────┬──────────────────────────┬─────────────────┘
                                 │                          │
                    ┌────────────▼────────────┐               │
                    │   C1  1000 µF / 6.3V  │               │
                    │   (+ on BAT+, − GND)  │               │
                    └────────────┬──────────┘               │
                                 │                          │
         ┌───────────────────────┼──────────────────────────┼──────────────────┐
         │                       │                          │                  │
         │  R5 100k              │                          │                  │
         │    ┌──────────────────┼──► GPIO34 (ADC battery)  │                  │
         │    │                  │         ▲                │                  │
         │    └── R6 100k ───────┼─────────┘                │                  │
         │           │           │                          │                  │
         │          GND          │                          │                  │
         │                       │                          │                  │
         │              ┌────────▼────────┐                 │                  │
         │              │    MT3608       │                 │                  │
         │              │  IN+ ◄── BAT+   │                 │                  │
         │              │  IN− ──► GND    │                 │                  │
         │              │  OUT− ─► GND    │                 │                  │
         │              │  OUT+ ~5.0 V    │                 │                  │
         │              └────────┬────────┘                 │                  │
         │                       │                          │                  │
         │         ┌─────────────┼─────────────┐            │                  │
         │         │             │             │            │                  │
         │        C2          ESP32         JSN VCC         │                  │
         │       100nF      5V/VIN          (+5V)           │                  │
         │         │             │             │            │                  │
         │        GND         DevKit      ┌────┴────┐       │                  │
         │                      │         │ JSN-SR04T      │                  │
         │                   GPIO25 ─────►│ TRIG           │                  │
         │                   GPIO26 ◄─────│ ECHO           │                  │
         │                      │         │ GND ──► Q1 D   │                  │
         │                   GPIO4 ───┐   └────────┘       │                  │
         │                      │     │                     │                  │
         │                      │  ┌──▼──────────────┐      │                  │
         │                      │  │ Q1  IRLZ44N     │      │                  │
         │                      └──│ G  (pin 1)      │      │                  │
         │                         │ D  (pin 2) ◄────┘      │                  │
         │                    R3   │ S  (pin 3) ──────────┼──► GND (common)  │
         │                   10k   └─────────────────────┘                  │
         │                    │                                               │
         └────────────────────┴───────────────────────────────────────────────┘

  Echo divider:  ECHO ──[R1 10k]── GPIO26 ──[R2 20k]── GND
  Gate pulldown: GPIO4 ── GATE ──[R3 10k]── GND
```

---

## Power rails

| Rail | Voltage | Source | Loads |
|------|---------|--------|-------|
| **BAT+** | 3.0–4.2 V | 18650 (+) | MT3608 IN+, C1+, battery divider R5 |
| **+5 V** | ~5.0 V | MT3608 OUT+ | ESP 5V/VIN, JSN VCC, C2 |
| **GND** | 0 V | 18650 (−) | Common ground for all modules |

> **Do not** power the ESP from USB and MT3608 OUT+ at the same time.

---

## GPIO map (ESP32 DevKit)

| GPIO | Function | Connection |
|------|----------|------------|
| **GPIO4** | `sensor_power` | IRLZ44N Gate + R3 10k → GND |
| **GPIO25** | Ultrasonic Trig | JSN TRIG (no resistor) |
| **GPIO26** | Ultrasonic Echo | Via R1/R2 voltage divider |
| **GPIO34** | Battery ADC | Midpoint of R5/R6 divider from BAT+ |
| GPIO33 | Wake button | Optional SW1 → GND (disabled in firmware until wired) |

GPIO16 is **not used** (marked as U2_RXD on many DevKit pinout cards).

---

## MOSFET (IRLZ44N) — low-side on sensor GND

| Pin | Name | Connection |
|-----|------|------------|
| 1 | GATE | GPIO4 + R3 10k → GND |
| 2 | DRAIN | JSN GND (metal tab = DRAIN) |
| 3 | SOURCE | GND |

| GPIO4 | Q1 | Sensor GND (Drain) vs GND | VCC vs Drain |
|-------|-----|---------------------------|--------------|
| LOW (OFF) | Off | ~0.5–1 V (signal bleed via Echo/Trig) | ~4.2 V |
| HIGH (ON) | On | ~0 V | ~5 V |

Full power cut-off requires a **P-MOS on VCC** (planned: AO3401A).

---

## JSN-SR04T-V3.3

| Requirement | Value |
|-------------|-------|
| Mode | **Mode 0** — MODE pad open (no bridge to M1/M2/M3) |
| VCC | 5 V from MT3608 OUT+ |
| Trigger pulse | ≥ 20 µs (`ultrasonic_pulse_time: 20us`) |
| Dead zone | ~25 cm from membrane |

---

## Echo voltage divider (5 V → ~3.3 V)

```
JSN ECHO/TX ──[R1  10 kΩ]── GPIO26 ──[R2  20 kΩ]── GND
```

---

## Battery voltage divider (DevKit only)

```
BAT+ ──[R5  100 kΩ]── GPIO34 ──[R6  100 kΩ]── GND
```

Firmware: `battery_adc_multiplier = V_battery / V_GPIO34` (calibrate with a multimeter).

FireBeetle (future): built-in divider, use `multiply: 2.0`.

---

## Bill of materials (prototype)

| Part | Value / type |
|------|----------------|
| ESP32 DevKit V1 + 38P expansion board | — |
| JSN-SR04T-V3.3 | Waterproof ultrasonic |
| MT3608 | Step-up to 5 V |
| IRLZ44N | Logic-level N-MOSFET, TO-220 |
| C1 | 1000 µF / 6.3 V electrolytic |
| C2 | 100 nF ceramic |
| R1, R3, R5, R6 | 10 kΩ, 10 kΩ, 100 kΩ, 100 kΩ |
| R2 | 20 kΩ |
| 18650 holder + cell | Li-ion 1S |

**Planned:** TP4056 charger module (with DW01 protection), 5 V USB solar panel.

---

## Rejected wiring (do not use)

| Wiring | Result |
|--------|--------|
| Q1 on MT3608 IN− | Boost cannot be disabled; module overheats |
| Q1 high-side on VCC (OUT+ → DRAIN) | ~0.9 V on sensor with 3.3 V gate |
| OUT+ connected to Q1 DRAIN | Wrong topology |
| Floating GPIO33 as `wakeup_pin` | Immediate wake from deep sleep |
