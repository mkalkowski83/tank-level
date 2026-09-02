> **English** · [Polski](2026-08-25-szambo-level-sensor.pl.md)

# Szambo Level Sensor — implementation plan

**Goal:** Wireless septic tank level sensor (ESP32 + JSN-SR04T) reporting to Home Assistant, powered by 18650, deep sleep between measurements.

**Architecture:** DevKit V1 → ESPHome → WiFi → HA API (encrypted). MT3608 from BAT+ provides 5 V for ESP and sensor. IRLZ44N low-side disconnects sensor GND between measurements. ADC GPIO34 + divider monitors battery. Deep sleep 4 h; measurement only after wake.

**Tech Stack:** ESPHome 2026.8, ESP32 Arduino (toolchain: platformio), JSN-SR04T-V3.3, MT3608, IRLZ44N, Home Assistant.

**Agent note:** When changing hardware/firmware, update [`docs/superpowers/specs/2026-08-25-szambo-level-sensor-design.en.md`](../specs/2026-08-25-szambo-level-sensor-design.en.md) first, then this plan.

---

## Phase 1 — Basic prototype

- [x] DevKit + JSN-SR04T wiring (Trig GPIO25, Echo GPIO26 + divider)
- [x] MT3608 OUT+ = 5.0 V; m→cm conversion in firmware
- [x] HA entities: Tank Distance, Tank Distance Raw (m), Tank Fill Level
- [x] ESPHome build: `toolchain: platformio` (template depth workaround)
- [x] Measurement test (wall / object); empty/full calibration

## Phase 2 — Battery power

- [x] 18650 wiring: BAT+ → MT3608 IN+, C1; BAT− → GND
- [x] ESP from MT3608 OUT+ (5V/VIN); USB for flashing only
- [x] Battery divider 100k/100k → GPIO34
- [x] `enable_battery_check: true`; Battery Voltage, Status, Low, Critical entities
- [x] `battery_adc_multiplier` calibration (V_bat / V_GPIO34)
- [x] Software cutoff thresholds (3.7 / 3.3 / 3.1 / 2.9 V)

## Phase 3 — Energy saving

- [x] Deep sleep `sleep_duration: 4h`
- [x] `boot_measure_then_sleep` script — sleep after valid reading (`sleep_until_valid`)
- [x] Disable `wakeup_pin` (GPIO33 without button caused false wakes)
- [x] `wifi.power_save_mode: light`
- [x] IRLZ44N MOSFET low-side on sensor GND
- [x] `pin_sensor_power: GPIO4` (GPIO16 used by UART on board)
- [x] `enable_sensor_power: true` — Q1 ON/OFF in `measure_cycle`
- [x] Q1 verification with multimeter (OFF: VCC–DRAIN ~4.2 V; ON: ~5 V, DRAIN ~0 V)

## Phase 4 — Safety and HA integration

- [x] API encryption (`!secret szambo_level__encryption_key`)
- [x] Tank Distance Raw without `device_class` (HA shows meters, not cm)
- [x] `publish_state()` for battery template entities (not `component.update`)
- [x] Debug buttons (Sensor Power, Run Measurement) — `internal: true` in production mode

## Phase 5 — Field tests (in progress)

- [ ] Observe **Battery Voltage** in HA for several days on battery
- [ ] Confirm cycle: wake every ~4 h, one measurement, deep sleep
- [ ] 3 m test calibration: `distance_empty_cm: 300`, `distance_full_cm: 160` — OK

## Phase 6 — Charging and autonomy

- [ ] USB 5 V solar panel
- [ ] Charging module: TP4056 (DevKit) **or** migration to FireBeetle (built-in charger)
- [ ] Test replenishment vs consumption (target: ~1 month autonomy)

## Phase 7 — Final installation

- [ ] Waterproof enclosure; probe facing down (membrane outside dead zone <25 cm)
- [ ] Production calibration: `distance_empty_cm: 180`, `distance_full_cm: 40`
- [ ] Tank installation; verify readings in HA

## Phase 8 — Optional improvements

- [ ] P-MOS high-side on sensor VCC (AO3401A) — full power cut-off (Echo bleed workaround)
- [ ] Wake button GPIO33 + uncomment `wakeup_pin` in YAML
- [ ] 1S BMS (DW01 + 8205A)
- [ ] DevKit → FireBeetle migration (built-in GPIO34, lower draw)
- [ ] Return to `esp32.toolchain: esp-idf` after ESPHome fix (~2027.2)

---

## Files

| File | Role |
|------|------|
| `esphome/szambo-level-sensor.yaml` | ESPHome firmware |
| `docs/schematics/connections-devkit.en.md` | DevKit wiring |
| `docs/schematics/connections-firebeetle.en.md` | FireBeetle wiring (target) |
| `docs/superpowers/specs/2026-08-25-szambo-level-sensor-design.en.md` | Specification |

## Verification after changes

```bash
# Compile / flash (manually when needed):
esphome run esphome/szambo-level-sensor.yaml

# USB logs (debug):
esphome logs esphome/szambo-level-sensor.yaml
```

Expected log after wake: `Battery: X.XX V` → `Ultrasonic OK: raw=…` → `Beginning sleep`.

## Known risks

| Risk | Mitigation |
|------|------------|
| MT3608 continuous draw ~2–5 mA | Solar panel; target P-MOS / FireBeetle |
| Q1 does not fully cut off (Echo bleed) | Acceptable on prototype; AO3401A later |
| Battery ADC drifts with WiFi | Multiplier calibration; measure at cycle start |
| Floating GPIO33 | wakeup_pin disabled until SW1 installed |
