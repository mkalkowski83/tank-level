> [English](connections-devkit.en.md) · **Polski**

# Polaczenia — ESP32 DevKit V1 + expansion board

Modul: **ESP32-DevKitC / DevKit V1** (38 pin) + **expansion board 38P** — ESP wchodzi w adapter, piny na goldpinach / terminalach.

**Stan aktywny (2026-09):** zasilanie z **18650**, MOSFET na GND czujnika, monitoring baterii na GPIO34. USB tylko do flash.

---

## 1. Zasilanie z baterii (aktywny)

| Od | Do |
|----|-----|
| **18650 (+)** | **BAT+** — MT3608 **IN+**, **C1 (+)**, **R5** (dzielnik GPIO34) |
| **18650 (−)** | **GND** — holder −, MT3608 IN−/OUT−, ESP GND, C1 (−), R6, R2, R3 |
| MT3608 **OUT+** (~5 V) | **ESP 5V/VIN**, **C2**, **VCC czujnika** |
| MT3608 **IN−** / **OUT−** | **GND** |

**USB:** odłączony w eksploatacji. Podłącz tylko do flash (nie zasilaj równolegle USB + ogniwo bez modułu ładowania).

### Przełączenie USB ↔ bateria (jednorazowa zmiana okablowania)

| Element | USB (debug) | Bateria (eksploatacja) |
|---------|-------------|------------------------|
| ESP 5V/VIN | USB | MT3608 OUT+ |
| MT3608 IN+ | szyna +5 V USB | BAT+ |
| C1 (+) | +5 V USB | BAT+ |
| GPIO34 | wolny | dzielnik R5/R6 z BAT+ |

Reszta (Trig, Echo, Q1) **bez zmian**.

---

## 2. MT3608 + MOSFET (Q1)

| Od | Do |
|----|-----|
| MT3608 **IN+** | **BAT+** |
| MT3608 **IN−** / **OUT−** | **GND** |
| MT3608 **OUT+** | **~5,0 V** — ESP 5V/VIN, **C2**, **VCC czujnika** |
| **GND czujnika** | **Q1 Drain (pin 2)** — **nie** bezpośrednio na GND |
| Q1 **Source (pin 3)** | **GND** |
| Q1 **Gate (pin 1)** | **GPIO4** + **R3 10k** → **GND** |

**Logika:** GPIO4 = HIGH → Q1 ON → GND czujnika do masy → pomiar. GPIO4 = LOW → czujnik częściowo odcięty (VCC nadal 5 V; obejście przez Echo/Trig).

**Nie łącz:** OUT+ na Drain Q1; Q1 na IN− MT3608.

### Orientacja IRLZ44N (TO-220, od frontu, piny w dół)

| Pin | Nazwa | Polaczenie |
|-----|-------|------------|
| 1 | GATE | GPIO4 + R3 |
| 2 | DRAIN | GND czujnika |
| 3 | SOURCE | GND |

Metalowa blaszka = **DRAIN**.

---

## 3. Dzielnik baterii (DevKit)

```
BAT+ ──[R5 100k]── GPIO34 ──[R6 100k]── GND
```

Firmware: `battery_adc_multiplier` = V_bat / V_GPIO34 (kalibracja miernikiem).

FireBeetle: wbudowany dzielnik — bez R5/R6, `multiply: 2.0`.

---

## 4. ESP32 — mapa GPIO

| Funkcja | GPIO | Uwagi |
|---------|------|-------|
| sensor_power (Q1 Gate) | **GPIO4** | Nie GPIO16 (U2_RXD na pinoucie) |
| TRIG | **GPIO25** | bez dzielnika |
| ECHO + dzielnik | **GPIO26** | R1 10k → GPIO26 → R2 20k → GND |
| ADC baterii | **GPIO34** | tylko wejście |
| Wake (opcjonalnie) | **GPIO33** | SW1 → GND; w YAML **wyłączony** bez przycisku |

**Nie używaj GPIO6–11** (flash).

---

## 5. Czujnik JSN-SR04T-V3.3 (Mode 0)

**MODE otwarty** (bez mostka M1/M2/M3).

| Pin modułu | Polaczenie |
|------------|------------|
| **VCC** | MT3608 OUT+ + C2 |
| **GND** | **Q1 Drain** (nie bezpośrednio GND) |
| **Trig / RX** | GPIO25 |
| **Echo / TX** | R1 → GPIO26 → R2 → GND |

---

## 6. Przycisk wake (opcjonalnie — nie podłączony)

```
GPIO33 ----[ SW1 ]---- GND
```

W YAML odkomentuj `wakeup_pin` dopiero po podłączeniu SW1.

---

## 7. Testy hardware

### Bez ogniwa
- BAT+ ↔ GND: brak zwarcia

### Z ogniwem
1. OUT+ MT3608 = **~5,0 V**
2. GPIO34 ≈ **połowa** napięcia ogniwa (przy 100k/100k)
3. **Q1 OFF** (GPIO4 LOW): VCC–DRAIN ≈ **4–4,5 V**; DRAIN–GND ≈ **0,5–1 V** (obejście Echo)
4. **Q1 ON** (GPIO4 HIGH): DRAIN–GND ≈ **0 V**; VCC–DRAIN ≈ **5 V**
5. Log / HA: `Ultrasonic OK`, `Battery Voltage` ≈ miernik na holderze

### Test Q1 — nie używaj Ω na Drain przy VCC=5 V
Przy Gate zwartym do Source: D–S powinno być **OL**. Odczyt ~0,04 Ω przy luźnym Gate = ładowanie bramki przez miernik.

---

## 8. Firmware

- Plik: `esphome/szambo-level-sensor.yaml`
- `enable_deep_sleep: true`, `sleep_duration: 4h`
- `enable_sensor_power: true`, `pin_sensor_power: GPIO4`
- `enable_battery_check: true`
- ESPHome 2026.8: `toolchain: platformio`

---

## 9. Docelowo

| Element | Kiedy |
|---------|--------|
| Panel solarny + TP4056 | ładowanie 18650 |
| FireBeetle | mniejsza płytka, wbudowany charger + ADC |
| P-MOS AO3401A na VCC | pełne odcięcie czujnika |

Szczegóły FireBeetle: [`connections-firebeetle.pl.md`](connections-firebeetle.pl.md).
