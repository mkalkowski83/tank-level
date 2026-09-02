> [English](README.en.md) · **Polski**

# Firmware ESPHome — `szambo-level-sensor.yaml`

Jeden plik YAML dla czujnika poziomu szamba: ESP32 DevKit V1, ultrasonik JSN-SR04T-V3.3, bateria 18650, deep sleep co 4 godziny.

## Co robi

1. Wybudza się z deep sleep (timer lub po flashu).
2. Odczytuje napięcie baterii na GPIO34 (z skalibrowanym mnożnikiem).
3. Jeśli napięcie > 3,1 V: zasila czujnik przez GPIO4 (MOSFET), mierzy odległość, oblicza poziom zapełnienia.
4. Synchronizuje z Home Assistant przez WiFi (szyfrowane API).
5. Wraca do deep sleep na 4 godziny.

Główne encje: **Tank Distance** (cm), **Tank Fill Level** (%), **Battery Voltage**, **Battery Status**.

## Sekrety

Utwórz `esphome/secrets.yaml` (poza repozytorium):

```yaml
wifi_guest_ssid: "twoj-ssid"
wifi_guest_password: "twoje-haslo"
szambo_level__encryption_key: "klucz-base64-z-esphome-dashboard"
```

Klucz szyfrowania wygeneruj w ESPHome Dashboard lub przez `esphome secrets`.

## Kluczowe substitutions

| Klucz | Domyślnie | Znaczenie |
|-------|-----------|-----------|
| `distance_empty_cm` / `distance_full_cm` | 300 / 160 (test) | Kalibracja: odległość pustego / pełnego zbiornika |
| `enable_deep_sleep` | `true` | Sen 4 h między pomiarami |
| `enable_battery_check` | `true` | Progi software cutoff |
| `enable_sensor_power` | `true` | MOSFET na GPIO4 |
| `battery_adc_multiplier` | 2.11 | Kalibracja: V_bat / V_GPIO34 |
| `pin_sensor_power` | GPIO4 | DevKit; docelowo FireBeetle GPIO16 |
| `sleep_until_valid` | `true` | Ponawiaj do poprawnego odczytu ultrasonicu |

Wartości produkcyjne (szambo): `distance_empty_cm: 180`, `distance_full_cm: 40`.

## Polecenia

```bash
esphome run esphome/szambo-level-sensor.yaml    # kompilacja + flash
esphome logs esphome/szambo-level-sensor.yaml   # logi USB
```

## Dokumentacja

Pełna specyfikacja hardware, okablowanie i troubleshooting: [`docs/README.md`](../docs/README.md).
