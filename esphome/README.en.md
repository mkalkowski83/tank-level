> **English** · [Polski](README.pl.md)

# ESPHome firmware — `tank-level-sensor.yaml`

Single YAML file for the septic tank level sensor: ESP32 DevKit V1, JSN-SR04T-V3.3 ultrasonic, 18650 battery, deep sleep every 4 hours.

## What it does

1. Wakes from deep sleep (timer or after flash).
2. Reads battery voltage on GPIO34 (with calibrated multiplier).
3. If voltage > 3.1 V: powers sensor via GPIO4 (MOSFET), measures distance, computes fill level.
4. Syncs with Home Assistant over WiFi (encrypted API).
5. Returns to deep sleep for 4 hours.

Key entities: **Tank Distance** (cm), **Tank Fill Level** (%), **Battery Voltage**, **Battery Status**.

## Secrets

Create `esphome/secrets.yaml` (not in repo) with:

```yaml
wifi_guest_ssid: "your-ssid"
wifi_guest_password: "your-password"
tank_level__encryption_key: "base64-key-from-esphome-dashboard"
```

Generate the encryption key in ESPHome Dashboard or with `esphome secrets`.

## Key substitutions

| Key | Default | Purpose |
|-----|---------|---------|
| `distance_empty_cm` / `distance_full_cm` | 300 / 160 (test) | Calibration: empty tank distance / full tank distance |
| `enable_deep_sleep` | `true` | 4 h sleep between measurements |
| `enable_battery_check` | `true` | Software cutoff thresholds |
| `enable_sensor_power` | `true` | MOSFET on GPIO4 |
| `battery_adc_multiplier` | 2.11 | Calibrate: V_bat / V_GPIO34 |
| `pin_sensor_power` | GPIO4 | DevKit; FireBeetle target uses GPIO16 |
| `sleep_until_valid` | `true` | Retry until valid ultrasonic reading |

Production tank values: `distance_empty_cm: 180`, `distance_full_cm: 40`.

## Commands

```bash
esphome run esphome/tank-level-sensor.yaml    # compile + flash
esphome logs esphome/tank-level-sensor.yaml   # USB serial logs
```

## Documentation

Full hardware spec, wiring, and troubleshooting: [`docs/README.md`](../docs/README.md).
