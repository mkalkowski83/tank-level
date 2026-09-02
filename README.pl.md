# Czujnik poziomu szamba

Bezprzewodowy monitor poziomu szamba oparty na **ESP32**, **ESPHome** i **Home Assistant**. Sonda ultrasoniczna mierzy odległość do lustra cieczy; firmware przelicza ją na procent zapełnienia i raportuje przez Wi‑Fi. Urządzenie działa na ogniwie **18650** z **deep sleep** między pomiarami.

## Funkcje

- **Pomiar ultrasoniczny** — sonda JSN-SR04T-V3.3 (Mode 0, Trig/Echo)
- **Integracja z Home Assistant** — API ESPHome ze szyfrowaniem
- **Poziom %** — kalibracja z progów empty/full
- **Monitoring baterii** — napięcie, status tekstowy, sensory Low/Critical
- **Oszczędzanie energii** — deep sleep co 4 h; MOSFET IRLZ44N przełącza GND czujnika
- **Logika retry** — do 5 prób ultrasonicu; sen po prawidłowym odczycie (lub cutoff baterii)

## Hardware (aktywny prototyp)

| Element | Rola |
|---------|------|
| ESP32 DevKit V1 + expansion board 38P | MCU, Wi‑Fi |
| 18650 Li-ion | Zasilanie |
| MT3608 | Step-up 5 V dla ESP i czujnika |
| IRLZ44N (Q1) | Low-side na GND czujnika (GPIO4) |
| JSN-SR04T-V3.3 | Pomiar odległości |
| R1/R2 (10k/20k) | Dzielnik Echo 5 V → 3,3 V |
| R5/R6 (100k/100k) | Dzielnik baterii → GPIO34 |
| C1 1000 µF, C2 100 nF | Filtracja zasilania |

**Planowane:** TP4056 + panel solarny 5 V USB, opcjonalnie FireBeetle ESP32-E.

### Dokumentacja

| Język | Link |
|-------|------|
| Polski | Ten plik |
| English | [README.en.md](README.en.md) |

Schemat połączeń: **[docs/schematics/wiring-diagram.pl.md](docs/schematics/wiring-diagram.pl.md)**

Dodatkowe dokumenty:

- [Okablowanie DevKit](docs/schematics/connections-devkit.pl.md)
- [Okablowanie FireBeetle (docelowo)](docs/schematics/connections-firebeetle.pl.md)
- [Specyfikacja](docs/superpowers/specs/2026-08-25-szambo-level-sensor-design.pl.md)
- [Plan implementacji](docs/superpowers/plans/2026-08-25-szambo-level-sensor.pl.md)
- [Indeks dokumentacji](docs/README.md)

## Mapa GPIO

| GPIO | Funkcja |
|------|---------|
| GPIO4 | Zasilanie czujnika (bramka MOSFET) |
| GPIO25 | Trig ultrasonicu |
| GPIO26 | Echo (przez dzielnik) |
| GPIO34 | ADC baterii |
| GPIO33 | Przycisk wake (opcjonalnie, wyłączony w firmware) |

## Encje Home Assistant

| Encja | Jednostka | Opis |
|-------|-----------|------|
| Tank Distance Raw | m | Surowe metry z drivera |
| Tank Distance | cm | Po ×100 i filtrach |
| Tank Fill Level | % | Z kalibracji empty/full |
| Battery Voltage | V | Napięcie ogniwa |
| Battery Status | text | `normal` / `degraded` / `warning` / `stop` / `critical` |
| Battery Low | binary | ON przy ≤ 3,3 V |
| Battery Critical | binary | ON przy ≤ 2,9 V |

## Firmware

Główny plik: [`esphome/szambo-level-sensor.yaml`](esphome/szambo-level-sensor.yaml)

| Ustawienie | Wartość |
|------------|---------|
| Deep sleep | 4 h |
| Zasilanie czujnika | GPIO4 → MOSFET |
| Cutoff baterii | Brak ultrasonicu przy ≤ 3,1 V |
| Kalibracja test | `empty=300 cm`, `full=160 cm` (ściana 3 m) |
| Kalibracja produkcja | `empty=180 cm`, `full=40 cm` |

### Build (ESPHome 2026.8)

`esp32.toolchain: platformio` — obejście błędu template instantiation depth.

### Sekrety

Plik `esphome/secrets.yaml` (gitignore):

```yaml
wifi_ssid: "..."
wifi_password: "..."
szambo_level__encryption_key: "..."
```

## Flash i logi

```bash
esphome run esphome/szambo-level-sensor.yaml
esphome logs esphome/szambo-level-sensor.yaml
```

## Przepływ pomiaru

1. Wybudzenie z deep sleep (co 4 h)
2. Odczyt baterii → encje HA
3. Przy V > 3,1 V: MOSFET ON → 1,5 s → ultrasonik (do 5 prób)
4. Aktualizacja dystansu, %, sync z HA
5. MOSFET OFF → deep sleep

## Kalibracja

Driver `ultrasonic` zwraca **metry**. Filtr `×100` w YAML jest obowiązkowy.

## Ograniczenia

- MT3608 pobiera ~2–5 mA cały czas
- MOSFET low-side nie odcina czujnika całkowicie (~4,2 V przez Echo/Trig)
- DevKit wymaga zewnętrznego dzielnika baterii (`battery_adc_multiplier`)
- Expansion board 38P **nie ma** ładowarki — osobny TP4056
