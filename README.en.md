# Tank Level Sensor

Wireless septic tank level monitor built with **ESP32**, **ESPHome**, and **Home Assistant**. An ultrasonic probe measures the distance to the liquid surface; the firmware converts it to fill percentage and reports over Wi‑Fi. The device runs on a **18650** cell with **deep sleep** between readings to maximize battery life.

## Features

- **Ultrasonic distance** — JSN-SR04T-V3.3 waterproof probe (Mode 0, Trig/Echo)
- **Home Assistant integration** — ESPHome API with encryption
- **Fill level %** — calibrated from empty/full distance thresholds
- **Battery monitoring** — voltage, status text, low/critical binary sensors
- **Power saving** — deep sleep every 4 hours; IRLZ44N MOSFET switches sensor GND between measurements
- **Retry logic** — up to 5 ultrasonic attempts; sleep only after a valid reading (or low-battery cutoff)

## Hardware (active prototype)

| Component | Role |
|-----------|------|
| ESP32 DevKit V1 + 38P expansion board | MCU, Wi‑Fi |
| 18650 Li-ion | Power source |
| MT3608 | Step-up 5 V for ESP and sensor |
| IRLZ44N (Q1) | Low-side switch on sensor GND (GPIO4) |
| JSN-SR04T-V3.3 | Distance measurement |
| R1/R2 (10k/20k) | Echo level shifter 5 V → 3.3 V |
| R5/R6 (100k/100k) | Battery voltage divider → GPIO34 |
| C1 1000 µF, C2 100 nF | Power decoupling |

**Planned:** TP4056 charger + 5 V solar panel, optional migration to DFRobot FireBeetle ESP32-E.

### Documentation

| Language | Link |
|----------|------|
| English | This file |
| Polski | [README.pl.md](README.pl.md) |

See **[docs/schematics/connections-ao3401a.en.md](docs/schematics/connections-ao3401a.en.md)** for connection tables · [KiCad PDF](docs/schematics/tank-level-devkit.pdf)

Additional docs:

- [DevKit wiring](docs/schematics/connections-devkit.en.md) — step-by-step breadboard guide
- [FireBeetle wiring (target)](docs/schematics/connections-firebeetle.en.md)
- [Design spec](docs/superpowers/specs/2026-08-25-tank-level-sensor-design.en.md)
- [Implementation plan](docs/superpowers/plans/2026-08-25-tank-level-sensor.en.md)
- [All docs index](docs/README.md)

## GPIO summary

| GPIO | Function |
|------|----------|
| GPIO4 | Sensor power (MOSFET gate) |
| GPIO25 | Ultrasonic trigger |
| GPIO26 | Ultrasonic echo (via divider) |
| GPIO34 | Battery ADC |
| GPIO33 | Wake button (optional, disabled in firmware until wired) |

## Home Assistant entities

| Entity | Unit | Description |
|--------|------|-------------|
| Tank Distance Raw | m | Raw driver output (meters) |
| Tank Distance | cm | Filtered distance (m×100, median) |
| Tank Fill Level | % | From calibration empty/full |
| Battery Voltage | V | Calibrated cell voltage |
| Battery Status | text | `normal` / `degraded` / `warning` / `stop` / `critical` |
| Battery Low | binary | ON at ≤ 3.3 V |
| Battery Critical | binary | ON at ≤ 2.9 V |

## Firmware

Main config: [`esphome/tank-level-sensor.yaml`](esphome/tank-level-sensor.yaml)

### Key settings

| Setting | Value |
|---------|-------|
| Deep sleep | 4 h |
| Sensor power | GPIO4 → MOSFET |
| Battery cutoff | Stop ultrasonic at ≤ 3.1 V |
| Test calibration | `empty=300 cm`, `full=160 cm` (3 m wall) |
| Production calibration | `empty=180 cm`, `full=40 cm` |

### Build note (ESPHome 2026.8)

Uses `esp32.toolchain: platformio` as a workaround for template instantiation depth errors with native ESP-IDF in the Home Assistant add-on.

### Secrets

Create `esphome/secrets.yaml` (gitignored) with at least:

```yaml
wifi_ssid: "..."
wifi_password: "..."
tank_level__encryption_key: "..."   # from: esphome encryption-key
```

## Flash and logs

```bash
# Flash / OTA
esphome run esphome/tank-level-sensor.yaml

# Serial logs (USB debug)
esphome logs esphome/tank-level-sensor.yaml
```

## Measurement flow

1. Wake from deep sleep (timer, every 4 h)
2. Read battery voltage → publish HA entities
3. If V > 3.1 V: enable MOSFET → wait 1.5 s → ultrasonic (up to 5 retries)
4. Update distance, fill %, sync with Home Assistant
5. Disable MOSFET → deep sleep

## Calibration

ESPHome `ultrasonic` returns **meters**. The YAML multiplies by 100 in a filter — `unit_of_measurement: cm` alone does **not** convert values.

```
fill % = (empty_cm − distance_cm) / (empty_cm − full_cm) × 100
```

## Known limitations

- **MT3608** draws ~2–5 mA continuously while the cell is connected
- **Low-side MOSFET** does not fully power off the sensor (~4.2 V remains via Echo/Trig signal paths when OFF)
- **DevKit** requires an external battery divider; calibrate `battery_adc_multiplier`
- **Expansion board** (38P pin adapter) has no charger — use a separate TP4056 module for solar charging

## License

Private project — see repository owner for usage terms.
