# Firmware ESPHome — `tank-level-mains.yaml`

Czujnik poziomu tanku zasilany **z sieci AC** (HLK → 5 V, ESP32 NODE + JSN-SR04T).
ESP i czujnik **zawsze włączone** — bez deep sleep, bez baterii, bez przełączania zasilania czujnika (GPIO4).

## Co robi

1. Co `measure_interval` (oraz przyciskiem **Measure Now**) uruchamia `measure_cycle`: pomiar odległości, obliczenie **Tank Fill Level** (%).
2. Synchronizuje z Home Assistant przez WiFi (szyfrowane API).

Główne encje: **Tank Distance** (cm), **Tank Fill Level** (%), opcjonalnie ręczny pomiar.

Wariant na baterię: [`tank-level-sensor.yaml`](tank-level-sensor.yaml) — bez zmian; szczegóły: [`README.pl.md`](README.pl.md).

## Sekrety

Utwórz `esphome/secrets.yaml` (poza repozytorium):

```yaml
wifi_guest_ssid: "twoj-ssid"
wifi_guest_password: "twoje-haslo"
tank_level__encryption_key: "klucz-base64-z-esphome-dashboard"
```

## Flash i bezpieczeństwo

Przed flashowaniem **odłącz HLK** od NODE — programuj tylko z USB. Nie łącz równolegle 5 V USB i 5 V HLK.

## Kluczowe substitutions

| Klucz | Domyślnie | Znaczenie |
|-------|-----------|-----------|
| `distance_empty_cm` / `distance_full_cm` | 300 / 40 | Kalibracja pusty / pełny (test; produkcja np. 180 / 40) |
| `sensor_min_distance_cm` | 20 | Poniżej → 100% fill |
| `measure_interval` | `1s` | Automatyczny pomiar (debug; produkcja np. `1h`) |
| `pin_ultrasonic_trig` / `echo` | GPIO25 / GPIO26 | Ultrasonik (Echo przez dzielnik 10k/20k) |

Ultrasonik: `pulse_time: 20us` (JSN-SR04T Mode 0), `timeout: 4m`.

## Hardware (NODE)

+5 V → ESP VIN + JSN VCC + C2 100 nF; Trig GPIO25; Echo → 10k → GPIO26 → 20k → GND.

## Polecenia

```bash
esphome config esphome/tank-level-mains.yaml
esphome run esphome/tank-level-mains.yaml
esphome logs esphome/tank-level-mains.yaml
```
