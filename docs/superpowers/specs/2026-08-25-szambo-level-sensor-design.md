# Czujnik poziomu szamba — specyfikacja hardware + ESPHome

**Data:** 2026-08-25  
**Ostatnia aktualizacja:** 2026-09-01  
**Status:** Prototyp **DevKit V1 + 18650 + MOSFET** — pomiar ultrasonics, deep sleep, monitoring baterii **działają**. Docelowo: panel solarny, ładowanie, montaż w szambo, migracja na FireBeetle.

**Powiązane dokumenty:**
- Połączenia DevKit (USB / bateria): [`docs/schematics/polaczenia-devkit-usb.md`](../../schematics/polaczenia-devkit-usb.md)
- Połączenia docelowe (FireBeetle): [`docs/schematics/polaczenia.md`](../../schematics/polaczenia.md)
- Plan implementacji: [`docs/superpowers/plans/2026-08-25-szambo-level-sensor.md`](../plans/2026-08-25-szambo-level-sensor.md)
- Firmware: [`esphome/szambo-level-sensor.yaml`](../../esphome/szambo-level-sensor.yaml)

## Cel

Bezprzewodowy (Wi‑Fi) pomiar poziomu w szambie kilka razy dziennie, integracja z Home Assistant przez ESPHome. Zasilanie: ogniwo 18650 (panel solarny i ładowanie — kolejny krok). Oszczędzanie energii: deep sleep 4 h między pomiarami, MOSFET low-side na GND czujnika.

## Komponenty

| Element | Model / parametr | Uwagi |
|---------|------------------|-------|
| Mikrokontroler (aktywny) | **ESP32 DevKit V1** (38 pin) + expansion board | Zasilanie z MT3608 OUT+ (~5 V); USB tylko do flash |
| Mikrokontroler (docelowo) | DFRobot FireBeetle ESP32-E (DFR0654) | Wbudowany charger, ADC baterii na GPIO34 |
| Czujnik | **JSN-SR04T-V3.3** | Mode 0 (Trig/Echo); VCC 5 V; **Trig ≥20 µs**; martwa strefa ~20–25 cm |
| Akumulator | 18650 Li-ion **bez** PCB protected | Holder; software cutoff; **bez ładowania** w prototypie |
| Step-up | MT3608 | IN+ ← BAT+; OUT+ = **5,0 V** → ESP 5V/VIN + VCC czujnika |
| MOSFET | IRLZ44N (logic level, TO-220) | **Low-side na GND czujnika**; Gate → **GPIO4** + R3 10 kΩ → GND |
| Kondensator elektrolit. | 1000 µF / 6,3 V | BAT+ (C1) |
| Kondensator ceramiczny | 100 nF | 5 V przy czujniku (C2) |
| Rezystory | 10 kΩ + 20 kΩ | Dzielnik Echo (5 V → ~3,3 V na GPIO26) |
| Rezystory | 100 kΩ ×2 | Dzielnik baterii BAT+ → GPIO34 → GND (DevKit) |
| Rezystor | 10 kΩ | Pulldown bramki MOSFET (R3) |
| Przycisk | Tact switch (opcjonalnie) | GPIO33 → GND (wake — **wyłączony** w YAML bez podłączenia) |
| Montaż | Stykówka / płytka uniwersalna | MT3608, Q1, C1, C2, rezystory |
| Ładowanie (plan) | Panel solarny USB 5 V + TP4056 lub FireBeetle | **Nie podłączone** |

## Prototyp aktywny (DevKit V1 + bateria — 2026-09)

Montaż zgodny z [`polaczenia-devkit-usb.md`](../../schematics/polaczenia-devkit-usb.md) (sekcja bateria).

| Element | Stan |
|---------|------|
| Zasilanie ESP | **MT3608 OUT+** (~5 V) z ogniwa 18650 |
| MT3608 IN+ | **BAT+** (holder + C1) |
| MOSFET Q1 | **Aktywny** — GND czujnika przez Drain; Gate → **GPIO4** |
| Czujnik | **JSN-SR04T-V3.3**, Mode 0 |
| ADC baterii | **GPIO34** + dzielnik 100k/100k; `battery_adc_multiplier` skalibrowany |
| Deep sleep | **4 h**; `wakeup_pin` **wyłączony** (luźny GPIO33 budził natychmiast) |
| Kalibracja test | `distance_empty_cm: 300`, `distance_full_cm: 160` (ściana 3 m) |
| USB | Tylko do flash; w eksploatacji **odłączony** |

### JSN-SR04T-V3.3 — wymagania

| Parametr | Wartość |
|----------|---------|
| Tryb | **Mode 0** — pad **MODE** bez mostka do M1/M2/M3 |
| Piny na PCB | **Trig/RX** = trigger, **Echo/TX** = echo |
| Impuls Trig | **≥20 µs** (`ultrasonic_pulse_time: 20us`) |
| Zasięg | ~20 cm – 600 cm (od **membrany** sondy) |
| Echo | Dzielnik **10 kΩ / 20 kΩ** na GPIO26 |

### Okablowanie sygnałów

```
Trig (RX)  ────────────────────── GPIO25
Echo (TX)  ──[R1 10k]── GPIO26 ──[R2 20k]── GND

BAT+ ──[R5 100k]── GPIO34 ──[R6 100k]── GND

GND czujnika ──► Q1 DRAIN (pin 2)
Q1 SOURCE (pin 3) ──► GND
Q1 GATE (pin 1) ──┬── GPIO4
                  └── R3 10k ──► GND
```

**GPIO16** nie używany — na DevKit oznaczony jako U2_RXD; sterowanie Q1 na **GPIO4**.

## Architektura zasilania

### DevKit + 18650 (bez ładowania)

```
18650 (+) ──► BAT+ ──┬──► MT3608 IN+
                     ├──► C1 (+)
                     └──► R5 (dzielnik → GPIO34)

18650 (−) ──► GND (wspólna masa)

MT3608 OUT+ (~5 V) ──┬──► ESP 5V/VIN
                     ├──► C2, VCC czujnika
                     └── (stałe gdy ogniwo podłączone)

JSN GND ◄── Q1 DRAIN
Q1 SOURCE ──► GND
Q1 GATE ──► GPIO4 + R3 10k → GND
```

MT3608 **pracuje cały czas** (~2–5 mA jałowego). Q1 **odcina masę czujnika** między pomiarami — **częściowo** (patrz sekcja MOSFET).

### Docelowo: FireBeetle + panel

```
18650 (+) ──► FireBeetle BAT+ ──┬──► MT3608 IN+ ──► C1
Panel USB ──► FireBeetle USB (ładowanie)
GPIO34 ── wbudowany dzielnik (multiply: 2.0)
```

### MOSFET low-side — zachowanie potwierdzone testami

| Stan Q1 | DRAIN ↔ GND | VCC ↔ DRAIN | Uwagi |
|---------|-------------|-------------|-------|
| **OFF** (GPIO4 LOW) | ~0,8 V | **~4,2 V** | Obejście przez Echo/Trig → GPIO → GND; czujnik nadal częściowo zasilony |
| **ON** (GPIO4 HIGH) | **~0 V** | **~5 V** | Pełne zasilanie; pomiar OK |

**Wniosek:** Q1 **działa** (sterowanie Gate potwierdzone). Low-side GND **nie wyłącza** czujnika całkowicie — prąd wraca liniami sygnałowymi. Docelowe pełne odcięcie: **P-MOS na VCC** (AO3401A).

### Orientacja IRLZ44N (TO-220, od frontu, piny w dół)

| Pin | Nazwa | Połączenie |
|-----|-------|------------|
| 1 | GATE | **GPIO4** + R3 10 kΩ → GND |
| 2 | DRAIN | GND czujnika |
| 3 | SOURCE | GND |

Metalowa płytka (tab) = **DRAIN**.

### Odrzucone warianty (potwierdzone testami)

#### 1. IRLZ44N na IN− MT3608

**Wynik:** **Nie działa** — IN− i OUT− wspólna masa modułu; boost się grzeje.

#### 2. IRLZ44N high-side na VCC (OUT+ → DRAIN)

**Wynik:** **Nie działa** — przy Gate 3,3 V VCC czujnika ≈ 0,94 V zamiast 5 V.

#### 3. wakeup_pin GPIO33 bez przycisku

**Wynik:** Natychmiastowe wybudzenie z deep sleep (~32 s cykl zamiast 4 h). **Fix:** `wakeup_pin` zakomentowany do czasu podłączenia SW1.

### Plan docelowy (oszczędzanie energii)

| Wariant | Kiedy | Uwaga |
|---------|-------|-------|
| **AO3401A** P-MOS na VCC | Po testach baterii | Pełne odcięcie 5 V czujnika |
| **Panel + TP4056** lub FireBeetle | Kolejny krok | Uzupełnianie 18650 |
| **BMS 1S** | Opcjonalnie | Twarda ochrona ogniwa |

## Pomiar napięcia baterii

### DevKit (aktywny)

Zewnętrzny dzielnik **100 kΩ / 100 kΩ**: BAT+ → GPIO34 → GND.

ESPHome:
- `pin: GPIO34`, `attenuation: 12db`
- `battery_adc_multiplier` — kalibracja: **V_bat / V_GPIO34** (przykład: 4,13 / 1,94 ≈ **2,13**)

Kalibracja: jednoczesny pomiar miernikiem na holderze i na węźle GPIO34 (ESP może odłączyć na czas pomiaru referencyjnego).

### FireBeetle (docelowo)

Wbudowany dzielnik 1 MΩ / 1 MΩ → `multiply: 2.0`, bez dodatkowych rezystorów.

## Mapa GPIO (DevKit — aktywny)

| GPIO | Funkcja | Kierunek | ESPHome |
|------|---------|----------|---------|
| **GPIO4** | `sensor_power` — Gate Q1 | Output | `switch` gpio |
| GPIO25 | Trig ultrasonicu | Output | `ultrasonic` trigger_pin |
| GPIO26 | Echo (po dzielniku) | Input | `ultrasonic` echo_pin |
| GPIO33 | Przycisk wake (opcjonalnie) | Input | `wakeup_pin` — **wyłączony** |
| GPIO34 | ADC baterii | ADC input | `adc` + `battery_adc_multiplier` |

## Sekwencja pomiaru (firmware)

1. Wybudzenie timerem (**4 h**) lub boot po flash.
2. Odczyt baterii → encje **Battery Voltage**, **Battery Status**, **Battery Low/Critical**.
3. Jeśli V > 3,1 V: **GPIO4 HIGH** → stabilizacja 1,5 s → ultrasonik (do 5 prób) → **GPIO4 LOW**.
4. Jeśli V ≤ 3,1 V: pomijaj ultrasonik, wejdź w deep sleep.
5. Aktualizacja **Tank Distance**, **Tank Fill Level**; sync z HA (WiFi, max 45 s).
6. Deep sleep **4 h** (lub retry do 20 cykli przy NAN, jeśli `sleep_until_valid`).

Skrypt `boot_measure_then_sleep` — sen dopiero po prawidłowym odczycie (lub niskiej baterii / limit prób).

## Weryfikacja hardware

### Przed włożeniem ogniwa

| Pomiar | OK |
|--------|-----|
| BAT+ ↔ GND | brak zwarcia |
| OUT+ ↔ GND | brak zwarcia |

### Z ogniwem (V DC) — MOSFET

| Stan | Pomiar | OK |
|------|--------|-----|
| GPIO4 LOW | DRAIN ↔ GND | ~0,5–1 V (obejście Echo) lub ~4–5 V (idealnie odcięte) |
| GPIO4 LOW | VCC ↔ DRAIN | ~4–4,5 V (częściowe zasilanie) |
| GPIO4 HIGH | DRAIN ↔ GND | **~0–0,3 V** |
| GPIO4 HIGH | VCC ↔ DRAIN | **~5 V** |

**Nie testuj Q1 w trybie Ω na Drain przy zasilonym VCC** — używaj napięcia DC.

### Test multimetrem Ω na D–S

Przy **Gate zwartym do Source** (OFF): D–S powinno być **OL** (wysoka rezystancja). Odczyt ~0,04 Ω przy luźnym Gate może wynikać z ładowania bramki przez miernik — nie oznacza uszkodzenia.

## Software cutoff (bez BMS)

| Napięcie | Akcja |
|----------|-------|
| ≥ 3,7 V | Status `normal` |
| 3,3–3,7 V | Status `degraded` |
| ≤ 3,3 V | **Battery Low** ON; status `warning` |
| ≤ 3,1 V | Status `stop`; **brak pomiaru** ultrasonicu; deep sleep |
| ≤ 2,9 V | **Battery Critical** ON |

## Home Assistant / ESPHome

Plik: `esphome/szambo-level-sensor.yaml`

### Encje

| Encja | Jednostka | Znaczenie |
|-------|-----------|-----------|
| **Tank Distance Raw** | m | Surowe metry z drivera (bez `device_class` — HA nie konwertuje na cm) |
| **Tank Distance** | cm | Po ×100, filtrach, medianie |
| **Tank Fill Level** | % | Z kalibracji empty/full |
| **Battery Voltage** | V | ADC GPIO34 × multiplier |
| **Battery Status** | text | `normal` / `degraded` / `warning` / `stop` / `critical` |
| **Battery Low** | binary | ON przy ≤ 3,3 V |
| **Battery Critical** | binary | ON przy ≤ 2,9 V |

### Substitutions (stan produkcyjny prototypu)

| Klucz | Wartość |
|-------|---------|
| `enable_deep_sleep` | `true` |
| `sleep_duration` | `4h` |
| `enable_battery_check` | `true` |
| `enable_sensor_power` | `true` |
| `pin_sensor_power` | **GPIO4** |
| `battery_adc_multiplier` | skalibrowany (~2,11–2,13) |
| `sleep_until_valid` | `true` |
| `sleep_max_measure_cycles` | `20` |
| `distance_empty_cm` / `distance_full_cm` | **300 / 160** (test 3 m); produkcja **180 / 40** |

### Build (ESPHome 2026.8 w HA)

| Ustawienie | Powód |
|------------|-------|
| `esp32.toolchain: platformio` | Obejście `template instantiation depth` (GCC 14 / IDF) |
| Brak `captive_portal`, `web_server`, `wifi.ap` | Mniejszy build |
| `wifi.power_save_mode: light` | Oszczędzanie energii |
| `api.encryption.key` | Szyfrowanie API (`!secret szambo_level__encryption_key`) |

### Konwersja m→cm

Komponent `ultrasonic` zwraca **metry**. Obowiązkowy filtr `return x * 100.0f` w pipeline **Tank Distance**.

## Rozwiązywanie problemów

| Objaw | Przyczyna | Działanie |
|-------|-----------|-----------|
| Odczyt **0,8 cm** przy ~80 cm | Metry bez ×100 | Filtr ×100; Raw w m |
| **Tank Distance Raw** = cm w HA | `device_class: distance` | Usunąć device_class z Raw |
| Restart co ~32 s | `wakeup_pin` GPIO33 luźny | Wyłączyć wakeup_pin |
| Battery HA ≠ miernik | ADC + niedokładny dzielnik | `battery_adc_multiplier = V_bat/V_GPIO34` |
| Odczyty przy Q1 OFF | Obejście Echo/Trig | Oczekiwane; docelowo P-MOS na VCC |
| `template instantiation depth` | ESPHome 2026.8 + IDF | `toolchain: platformio` |
| ID `battery_low` PollingComponent | `component.update` na template | `publish_state()` w lambda |

## Zużycie energii (szacunek)

| Konfiguracja | Średni pobór | 2500 mAh |
|--------------|--------------|----------|
| Bez MOSFET, MT3608 + czujnik 24/7 | ~15–20 mA | ~5–7 dni |
| Z MOSFET low-side (obecny) | ~8–12 mA | ~10–14 dni |
| + panel solarny (plan) | doładowanie | cel ~1 miesiąc |

MT3608 pozostaje włączony; Q1 redukuje pobór czujnika, nie boostera.

## Decyzje projektowe

| Temat | Decyzja |
|-------|---------|
| Czujnik | **JSN-SR04T-V3.3** |
| Prototyp aktywny | **DevKit V1 + 18650 + Q1 na GPIO4** |
| sensor_power | **GPIO4** (nie GPIO16 — UART) |
| MOSFET | Low-side GND — **działa**, częściowe odcięcie |
| Deep sleep | **4 h**; wakeup_pin wyłączony bez SW1 |
| Bateria DevKit | Dzielnik 100k + `battery_adc_multiplier` |
| Ładowanie | **Następny krok** (panel / TP4056 / FireBeetle) |
| Kalibracja | Test 300/160; produkcja 180/40 |
| Build | `toolchain: platformio` do fix ESPHome |
| Odrzucone | Q1 na IN− MT3608; high-side N-MOS na VCC |

## Następny krok

1. Obserwacja zużycia baterii przez kilka dni (HA: **Battery Voltage**).
2. Panel solarny + moduł ładowania (TP4056 lub FireBeetle).
3. Montaż sondy w obudowie / szambo → kalibracja **180/40**.
4. Opcjonalnie: P-MOS na VCC (AO3401A) dla pełnego odcięcia czujnika.
5. Migracja na FireBeetle + native ESP-IDF po stabilizacji ESPHome.
