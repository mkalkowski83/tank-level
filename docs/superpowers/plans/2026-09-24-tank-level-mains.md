# Tank Level Mains — Implementation Plan

> **Superseded (sensor power):** 2026-09-25 always-on — see [`2026-09-25-tank-level-mains-always-on.md`](2026-09-25-tank-level-mains-always-on.md) and updated spec. No AO3401A / GPIO4 gating.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mains-powered tank level (HLK 5 V) — KiCad schematic + ESPHome always-on HA (hourly measure). Sensor VCC always on.

**Architecture:** Second hardware/firmware variant (mains), parallel to battery `tank-level-devkit` — **additive only**. Own KiCad folder + own YAML; battery project files are read-only reference. One sheet AC | NODE; ESPHome without sensor power switch.

**Tech Stack:** KiCad 8/9, ESPHome (Arduino / `toolchain: platformio`), HLK-2M05, ESP32 DevKit V1, JSN-SR04T, Echo divider 10k/20k, C2 100 nF.

**Spec:** [`docs/superpowers/specs/2026-09-24-tank-level-mains-design.md`](../specs/2026-09-24-tank-level-mains-design.md)  
**Prior art (read-only):** [`docs/kicad/tank-level-devkit/`](../../kicad/tank-level-devkit/), [`esphome/tank-level-sensor.yaml`](../../../esphome/tank-level-sensor.yaml), [`docs/schematics/connections-ao3401a.pl.md`](../../schematics/connections-ao3401a.pl.md)

## Global Constraints

- Work on a **feature branch** (never commit/push to `main`)
- **Additive only:** do **not** delete, edit, rename, or “clean up” battery/devkit files (`docs/kicad/tank-level-devkit/**`, `esphome/tank-level-sensor.yaml`, existing `esphome/README*`, `docs/schematics/connections-*`, battery plans/specs). Copy symbols **into** the new tree; never patch the source tree.
- KiCad v1 agent pass: **place symbols + zone notes only; no wires** (user wires in KiCad)
- Do not place on mains sheet: 18650, TP4056, solar USB, MT3608, battery divider (GPIO34)
- Do not parallel USB 5 V and HLK 5 V
- YAML: **new file** `esphome/tank-level-mains.yaml` from scratch — not a copy/`strip` of the battery YAML
- Fixed behaviour: always-on, no battery entities, `pin_sensor_power: GPIO4` (HIGH = sensor ON, no `inverted`)
- Commit only when user explicitly asks

## Files

| Path | Role |
|------|------|
| Create: `docs/kicad/tank-level-mains/tank-level-mains.kicad_pro` | New KiCad project |
| Create: `docs/kicad/tank-level-mains/tank-level-mains.kicad_sch` | One sheet, AC \| NODE |
| Create: `docs/kicad/tank-level-mains/sym-lib-table` | Point at local `symbols/` |
| Create: `docs/kicad/tank-level-mains/symbols/tank-level.kicad_sym` | Copy of `ESP32_DEVKIT` + `JSN_SR04T` into **new** lib |
| Create: `docs/kicad/tank-level-mains/README.pl.md` | Mains KiCad docs only |
| Optional create: `docs/kicad/tank-level-mains/generate_schematic.py` | Place-only generator |
| Create: `esphome/tank-level-mains.yaml` | Minimal mains config |
| Create: `esphome/README-mains.pl.md` (+ optional `.en.md`) | Docs for mains YAML only — **do not** edit existing `esphome/README.pl.md` / `.en.md` |

---

### Task 1: KiCad schematic (place-only)

**Files:** paths under `docs/kicad/tank-level-mains/` above  
**Interfaces:** Produces labeled zones + refs from spec table; no nets required for agent Done.

- [ ] **Step 1:** Create feature branch `feature/tank-level-mains` from current HEAD.

- [ ] **Step 2:** Scaffold **new** project under `docs/kicad/tank-level-mains/` only. Read (do not edit) `tank-level-devkit` for patterns; copy `ESP32_DEVKIT` + `JSN_SR04T` into the **new** `symbols/tank-level.kicad_sym`.

- [ ] **Step 3:** Place symbols on one sheet in two text-labeled zones (left **AC**, right **NODE**). Stock KiCad libs where possible:

| Zone | Ref | Symbol / value |
|------|-----|----------------|
| AC | J1 | Screw terminal 2P — L/N |
| AC | F1 | Fuse ~1 A |
| AC | RV1 | MOV (varistor) L–N |
| AC | U1 | HLK / Hi-Link 5 V 3 W (KiCad stock PSU module symbol; Value `HLK-PM01` or equivalent 5 V / 0.6 A) |
| AC | J2 | Screw terminal 2P — +5V / GND out |
| NODE | J3 | Screw terminal 2P — +5V / GND in |
| NODE | U2 | `tank-level:ESP32_DEVKIT` |
| NODE | Q1 | `Transistor_FET:AO3401A` |
| NODE | Q2 | `Transistor_BJT:2N3904` |
| NODE | R1 | 10k — Gate pull-up |
| NODE | R2 | 10k — GPIO4 → base |
| NODE | R3 | 10k — Echo divider |
| NODE | R4 | 20k — Echo divider |
| NODE | C2 | 100 nF — SENSOR_VCC |
| NODE | J4 | `tank-level:JSN_SR04T` |

Text notes on sheet (not wires):

- AC board: mains → F1 → MOV → HLK → J2; creepage on board 1 only
- Cable J2↔J3: `+5V`, `GND`
- NODE: HLK +5V → ESP 5V/VIN; GPIO4→R2→Q2→Gate; AO3401A SOURCE=+5V, DRAIN=`SENSOR_VCC`→J4 VCC + C2; Echo divider R3/R4 → GPIO26; Trig GPIO25
- USB program only with HLK disconnected

Prefer `generate_schematic.py` place-only (no `wire()` calls) over hand-edited huge `.kicad_sch`, matching `docs/kicad/tank-level-devkit/generate_schematic.py`.

- [ ] **Step 4:** Write `README.pl.md` — open project path, ref table, “agent left unwired; user connects”, safety (no USB∥HLK).

- [ ] **Step 5:** Verify — open in KiCad Schematic Editor; all refs from table present; two zone labels visible; **zero** intentional wires. Done when that checklist holds.

---

### Task 2: ESPHome YAML — new minimal mains config

**Files:** create only `esphome/tank-level-mains.yaml`, `esphome/README-mains.pl.md` (optional EN twin)  
**Consumes:** NODE pins: GPIO4 power, GPIO25 trig, GPIO26 echo.  
**Produces:** Small always-on device YAML; HA sees distance + fill % + optional manual measure.

**Do not** touch `esphome/tank-level-sensor.yaml` or existing `esphome/README*`. Battery variant remains the first version; this is the second (mains).

- [ ] **Step 1:** Create `esphome/tank-level-mains.yaml` from scratch with this shape:

```yaml
substitutions:
  device_name: tank-level-mains
  friendly_name: Tank Level Mains
  sensor_min_distance_cm: "25"
  distance_empty_cm: "180"   # production; adjust after install
  distance_full_cm: "40"
  measure_interval: 1h
  sensor_stabilize: 1500ms
  pin_sensor_power: GPIO4
  pin_ultrasonic_trig: GPIO25
  pin_ultrasonic_echo: GPIO26

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}
  on_boot:
    then:
      - switch.turn_off: sensor_power

esp32:
  board: esp32dev
  toolchain: platformio
  framework:
    type: arduino
    version: recommended

logger:
api:
  encryption:
    key: !secret tank_level_mains__encryption_key
ota:
  - platform: esphome
wifi:
  ssid: !secret wifi_guest_ssid
  password: !secret wifi_guest_password

switch:
  - platform: gpio
    pin: ${pin_sensor_power}
    id: sensor_power
    name: "Sensor Power"
    restore_mode: ALWAYS_OFF
    # HIGH = ON; no inverted

button:
  - platform: template
    name: "Measure Now"
    on_press:
      - script.execute: measure_cycle

script:
  - id: measure_cycle
    mode: restart
    then:
      - switch.turn_on: sensor_power
      - delay: ${sensor_stabilize}
      - component.update: tank_distance
      - component.update: tank_fill_level
      - switch.turn_off: sensor_power

interval:
  - interval: ${measure_interval}
    then:
      - script.execute: measure_cycle

sensor:
  - platform: ultrasonic
    trigger_pin: ${pin_ultrasonic_trig}
    echo_pin: ${pin_ultrasonic_echo}
    timeout: 4m
    name: "Tank Distance"
    id: tank_distance
    unit_of_measurement: cm
    update_interval: never
    filters:
      - multiply: 100   # m → cm
      # optional: median / min-distance filter if needed later
  - platform: template
    name: "Tank Fill Level"
    id: tank_fill_level
    unit_of_measurement: "%"
    update_interval: never
    lambda: |-
      if (isnan(id(tank_distance).state)) return NAN;
      const float empty = ${distance_empty_cm};
      const float full = ${distance_full_cm};
      const float min_d = ${sensor_min_distance_cm};
      const float d = id(tank_distance).state;
      if (d < min_d) return 100.0f;
      if (d >= empty) return 0.0f;
      float pct = (empty - d) / (empty - full) * 100.0f;
      if (pct < 0) return 0.0f;
      if (pct > 100) return 100.0f;
      return pct;
```

Omit entirely: `deep_sleep`, battery ADC/`GPIO34`, `enable_*` flags, sleep-retry scripts, raw-distance entity, battery buttons/sensors.

- [ ] **Step 2:** Create `esphome/README-mains.pl.md` — purpose, secrets key, flash with HLK unplugged, pointer that battery config lives in `tank-level-sensor.yaml` (unchanged).

- [ ] **Step 3:** Verify — `esphome config esphome/tank-level-mains.yaml`. Expect valid; no deep_sleep/battery/GPIO34; interval 1h + `sensor_power` + fill %. Confirm `git status` shows **no** modifications under `docs/kicad/tank-level-devkit/` or to `esphome/tank-level-sensor.yaml` / existing READMEs.

---

## Done when

- [ ] New KiCad tree under `docs/kicad/tank-level-mains/` only; AC + NODE placed; no agent wires
- [ ] New `esphome/tank-level-mains.yaml` + `esphome/README-mains*.md` only
- [ ] **Zero** edits/deletes to battery/devkit project files
- [ ] Mains YAML validates; hourly measure; GPIO4; no sleep/battery

## Out of scope (this plan)

PCB layout, enclosure, ERC-clean wiring, physical build/test, production empty/full calibration, any change to the battery variant.
