> [English](2026-08-25-tank-level-sensor.en.md) · **Polski**

# Tank Level Sensor — plan implementacji

**Goal:** Bezprzewodowy czujnik poziomu tanku (ESP32 + JSN-SR04T) z raportowaniem do Home Assistant, zasilany 18650, deep sleep między pomiarami.

**Architecture:** DevKit V1 → ESPHome → WiFi → HA API (szyfrowane). MT3608 z BAT+ daje 5 V dla ESP i czujnika. IRLZ44N low-side odłącza GND czujnika między pomiarami. ADC GPIO34 + dzielnik monitoruje baterię. Deep sleep 4 h; pomiar tylko po wybudzeniu.

**Tech Stack:** ESPHome 2026.8, ESP32 Arduino (toolchain: platformio), JSN-SR04T-V3.3, MT3608, IRLZ44N, Home Assistant.

**Agent note:** Przy zmianach hardware/firmware najpierw zaktualizuj [`docs/superpowers/specs/2026-08-25-tank-level-sensor-design.pl.md`](../specs/2026-08-25-tank-level-sensor-design.pl.md), potem ten plan.

---

## Faza 1 — Prototyp podstawowy

- [x] Okablowanie DevKit + JSN-SR04T (Trig GPIO25, Echo GPIO26 + dzielnik)
- [x] MT3608 OUT+ = 5,0 V; konwersja m→cm w firmware
- [x] Encje HA: Tank Distance, Tank Distance Raw (m), Tank Fill Level
- [x] Build ESPHome: `toolchain: platformio` (obejście template depth)
- [x] Test pomiaru (ściana / obiekt); kalibracja empty/full

## Faza 2 — Zasilanie bateryjne

- [x] Okablowanie 18650: BAT+ → MT3608 IN+, C1; BAT− → GND
- [x] ESP z MT3608 OUT+ (5V/VIN); USB tylko do flash
- [x] Dzielnik baterii 100k/100k → GPIO34
- [x] `enable_battery_check: true`; encje Battery Voltage, Status, Low, Critical
- [x] Kalibracja `battery_adc_multiplier` (V_bat / V_GPIO34)
- [x] Progi software cutoff (3,7 / 3,3 / 3,1 / 2,9 V)

## Faza 3 — Oszczędzanie energii

- [x] Deep sleep `sleep_duration: 4h`
- [x] Skrypt `boot_measure_then_sleep` — sen po prawidłowym odczycie (`sleep_until_valid`)
- [x] Wyłączenie `wakeup_pin` (GPIO33 bez przycisku powodował fałszywe wybudzenia)
- [x] `wifi.power_save_mode: light`
- [x] MOSFET IRLZ44N low-side na GND czujnika
- [x] `pin_sensor_power: GPIO4` (GPIO16 zajęty przez UART na płytce)
- [x] `enable_sensor_power: true` — Q1 ON/OFF w `measure_cycle`
- [x] Weryfikacja Q1 multimetrem (OFF: VCC–DRAIN ~4,2 V; ON: ~5 V, DRAIN ~0 V)

## Faza 4 — Bezpieczeństwo i integracja HA

- [x] API encryption (`!secret tank_level__encryption_key`)
- [x] Tank Distance Raw bez `device_class` (HA pokazuje metry, nie cm)
- [x] `publish_state()` dla encji template baterii (nie `component.update`)
- [x] Przyciski debug (Sensor Power, Run Measurement) — `internal: true` w trybie produkcyjnym

## Faza 5 — Testy terenowe (w toku)

- [ ] Obserwacja **Battery Voltage** w HA przez kilka dni na baterii
- [ ] Potwierdzenie cyklu: wybudzenie co ~4 h, jeden pomiar, deep sleep
- [ ] Kalibracja test 3 m: `distance_empty_cm: 300`, `distance_full_cm: 160` — OK

## Faza 6 — Ładowanie i autonomia

- [ ] Panel solarny USB 5 V
- [ ] Moduł ładowania: TP4056 (DevKit) **lub** migracja na FireBeetle (wbudowany charger)
- [ ] Test doładowania vs zużycie (cel: ~1 miesiąc autonomii)

## Faza 7 — Montaż docelowy

- [ ] Obudowa wodoodporna; sonda skierowana w dół (membrana poza martwą strefą <25 cm)
- [ ] Kalibracja produkcyjna: `distance_empty_cm: 180`, `distance_full_cm: 40`
- [ ] Montaż w tanku; weryfikacja odczytów w HA

## Faza 8 — Ulepszenia opcjonalne

- [ ] P-MOS high-side na VCC czujnika (AO3401A) — pełne odcięcie zasilania (obejście Echo)
- [ ] Przycisk wake GPIO33 + odkomentowanie `wakeup_pin` w YAML
- [ ] BMS 1S (DW01 + 8205A)
- [ ] Migracja DevKit → FireBeetle (GPIO34 wbudowany, mniejszy pobór)
- [ ] Powrót na `esp32.toolchain: esp-idf` po fix ESPHome (~2027.2)

---

## Pliki

| Plik | Rola |
|------|------|
| `esphome/tank-level-sensor.yaml` | Firmware ESPHome |
| `docs/schematics/connections-devkit.pl.md` | Okablowanie DevKit |
| `docs/schematics/connections-firebeetle.pl.md` | Okablowanie FireBeetle (docelowo) |
| `docs/superpowers/specs/2026-08-25-tank-level-sensor-design.pl.md` | Specyfikacja |

## Weryfikacja po zmianach

```bash
# Kompilacja / flash (ręcznie, gdy potrzebne):
esphome run esphome/tank-level-sensor.yaml

# Logi USB (debug):
esphome logs esphome/tank-level-sensor.yaml
```

Oczekiwany log po wybudzeniu: `Battery: X.XX V` → `Ultrasonic OK: raw=…` → `Beginning sleep`.

## Ryzyka znane

| Ryzyko | Mitygacja |
|--------|-----------|
| MT3608 ciągły pobór ~2–5 mA | Panel solarny; docelowo P-MOS / FireBeetle |
| Q1 nie odcina całkowicie (Echo bleed) | Akceptowalne na prototyp; AO3401A później |
| ADC baterii dryfuje przy WiFi | Kalibracja multiplier; pomiar na początku cyklu |
| Luźny GPIO33 | wakeup_pin wyłączony do montażu SW1 |
