> **English** · [Polski](connections-firebeetle.pl.md)

# Connections — septic tank level sensor

Simple assembly guide (no CAD schematic).

## 1. Power

| From | To |
|------|-----|
| 18650 (+) | FireBeetle **BAT+** |
| 18650 (+) | **C1 (+)** and **MT3608 IN+** (same BAT+ rail) |
| 18650 (−) | **GND** (FireBeetle BAT−, common ground) |
| C1 (−) | **GND** |
| USB solar panel | FireBeetle **USB** (charging only) |

## 2. MT3608 + MOSFET (5 V for sensor)

| From | To |
|------|-----|
| MT3608 **IN+** | **BAT+** rail |
| MT3608 **IN−** | **GND** |
| MT3608 **OUT−** | **GND** |
| MT3608 **OUT+** | Set to **5.0 V** with multimeter |
| MT3608 **OUT+** | **C2**, **sensor VCC** (JSN-SR04T) |
| **Sensor GND** | **Q1 Drain (D), pin 2** |
| Q1 **Source (S), pin 3** | **GND** |
| Q1 **Gate (G), pin 1** | **GPIO16** + **R3 10k** to GND |

**Logic:** GPIO16 = HIGH enables sensor (Q1 conducts, sensor GND goes to ground).

**Do not connect:** OUT+ to Q1 DRAIN (rejected high-side variant — see spec).

## 3. JSN-SR04T-V3.3 (signals)

**Mode 0:** **MODE** pad open (no bridge on M1/M2/M3). Trig pulse **≥20 µs** in ESPHome.

| Sensor pin | Connection |
|------------|------------|
| **VCC** | +5 V (from MT3608 OUT+) + **C2** |
| **GND** | **Q1 Drain (pin 2)** — target; in USB prototype → **GND** |
| **Trig / RX** | **GPIO25** (no divider) |
| **Echo / TX** | **R1 10k** → **GPIO26** → **R2 20k** → **GND** |

```
Echo/TX ----[R1 10k]---- GPIO26 ----[R2 20k]---- GND
Trig/RX  ---------------- GPIO25
```

**Note:** ESPHome `ultrasonic` returns **meters** — convert to cm in filter `×100` (see firmware spec).

## 4. Wake button

| From | To |
|------|-----|
| **GPIO39** | Button (leg 1) |
| Button (leg 2) | **GND** |
| **GPIO39** | optionally **R4 10k** to **3V3** (no internal pull-up on GPIO39) |

Alternative: **GPIO33** + internal pull-up in ESPHome (no R4).

## 5. Battery (no soldering on divider)

| Pin | Note |
|-----|------|
| **GPIO34** | Battery voltage ADC — built-in divider on FireBeetle |

Cell **must** be on FireBeetle BAT+/BAT−.

## IRLZ44N — orientation (TO-220, front view, pins down)

| Pin | Name | Connection |
|-----|------|------------|
| 1 | GATE | GPIO16 + R3 |
| 2 | DRAIN | Sensor GND |
| 3 | SOURCE | GND |

## Before power-on

1. Multimeter: no short **BAT+ − GND**
2. **C1**: plus on BAT+, minus on GND
3. **MT3608 OUT+** = 5.0 V (GPIO16 HIGH / 3V3 on Gate)
4. **GPIO16 HIGH**: DRAIN (sensor GND) **~0 V** relative to GND (DC voltage, not continuity with VCC powered)
5. No **BMS** — software cutoff in ESPHome

## Components on PCB / breadboard

C1, C2, U2 MT3608, Q1, R1, R2, R3, SW1 + wires to FireBeetle and sensor.
