> [English](wiring-diagram.en.md) · **Polski**

# Schemat połączeń — ESP32 DevKit, czujnik poziomu tanku

Aktywny prototyp: **ESP32 DevKit V1** + **18650** + **MT3608** + **IRLZ44N** + **JSN-SR04T-V3.3**.

Szczegółowe tabele połączeń: [`connections-devkit.pl.md`](connections-devkit.pl.md)

---

## Schemat blokowy

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    18650 Li-ion                         │
                    │                   (+) BAT+  (−) GND                     │
                    └────────────┬──────────────────────────┬─────────────────┘
                                 │                          │
                    ┌────────────▼────────────┐               │
                    │   C1  1000 µF / 6.3V  │               │
                    │   (+ na BAT+, − GND)  │               │
                    └────────────┬──────────┘               │
                                 │                          │
         ┌───────────────────────┼──────────────────────────┼──────────────────┐
         │                       │                          │                  │
         │  R5 100k              │                          │                  │
         │    ┌──────────────────┼──► GPIO34 (ADC baterii)  │                  │
         │    │                  │         ▲                │                  │
         │    └── R6 100k ───────┼─────────┘                │                  │
         │           │           │                          │                  │
         │          GND          │                          │                  │
         │                       │                          │                  │
         │              ┌────────▼────────┐                 │                  │
         │              │    MT3608       │                 │                  │
         │              │  IN+ ◄── BAT+   │                 │                  │
         │              │  IN− ──► GND    │                 │                  │
         │              │  OUT− ─► GND    │                 │                  │
         │              │  OUT+ ~5,0 V    │                 │                  │
         │              └────────┬────────┘                 │                  │
         │                       │                          │                  │
         │         ┌─────────────┼─────────────┐            │                  │
         │         │             │             │            │                  │
         │        C2          ESP32         JSN VCC         │                  │
         │       100nF      5V/VIN          (+5V)           │                  │
         │         │             │             │            │                  │
         │        GND         DevKit      ┌────┴────┐       │                  │
         │                      │         │ JSN-SR04T      │                  │
         │                   GPIO25 ─────►│ TRIG           │                  │
         │                   GPIO26 ◄─────│ ECHO           │                  │
         │                      │         │ GND ──► Q1 D   │                  │
         │                   GPIO4 ───┐   └────────┘       │                  │
         │                      │     │                     │                  │
         │                      │  ┌──▼──────────────┐      │                  │
         │                      │  │ Q1  IRLZ44N     │      │                  │
         │                      └──│ G  (pin 1)      │      │                  │
         │                         │ D  (pin 2) ◄────┘      │                  │
         │                    R3   │ S  (pin 3) ──────────┼──► GND (wspólna) │
         │                   10k   └─────────────────────┘                  │
         │                    │                                               │
         └────────────────────┴───────────────────────────────────────────────┘

  Dzielnik Echo:  ECHO ──[R1 10k]── GPIO26 ──[R2 20k]── GND
  Pulldown bramki: GPIO4 ── GATE ──[R3 10k]── GND
```

---

## Szyny zasilania

| Szyna | Napięcie | Źródło | Odbiorniki |
|-------|----------|--------|------------|
| **BAT+** | 3,0–4,2 V | 18650 (+) | MT3608 IN+, C1+, dzielnik baterii R5 |
| **+5 V** | ~5,0 V | MT3608 OUT+ | ESP 5V/VIN, JSN VCC, C2 |
| **GND** | 0 V | 18650 (−) | Wspólna masa wszystkich modułów |

> **Nie** zasilaj ESP jednocześnie z USB i MT3608 OUT+.

---

## Mapa GPIO (ESP32 DevKit)

| GPIO | Funkcja | Połączenie |
|------|---------|------------|
| **GPIO4** | `sensor_power` | IRLZ44N Gate + R3 10k → GND |
| **GPIO25** | Trig ultrasonicu | JSN TRIG (bez rezystora) |
| **GPIO26** | Echo ultrasonicu | Przez dzielnik R1/R2 |
| **GPIO34** | ADC baterii | Punkt środkowy dzielnika R5/R6 z BAT+ |
| GPIO33 | Przycisk wake | Opcjonalnie SW1 → GND (wyłączony w firmware bez podłączenia) |

GPIO16 **nie jest używany** (na wielu kartach pinout DevKit oznaczony jako U2_RXD).

---

## MOSFET (IRLZ44N) — low-side na GND czujnika

| Pin | Nazwa | Połączenie |
|-----|-------|------------|
| 1 | GATE | GPIO4 + R3 10k → GND |
| 2 | DRAIN | JSN GND (metalowa blaszka = DRAIN) |
| 3 | SOURCE | GND |

| GPIO4 | Q1 | GND czujnika (Drain) vs GND | VCC vs Drain |
|-------|-----|---------------------------|--------------|
| LOW (OFF) | Wył. | ~0,5–1 V (obejście przez Echo/Trig) | ~4,2 V |
| HIGH (ON) | Wł. | ~0 V | ~5 V |

Pełne odcięcie zasilania wymaga **P-MOS na VCC** (planowany: AO3401A).

---

## JSN-SR04T-V3.3

| Wymaganie | Wartość |
|-----------|---------|
| Tryb | **Mode 0** — pad MODE otwarty (bez mostka do M1/M2/M3) |
| VCC | 5 V z MT3608 OUT+ |
| Impuls Trig | ≥ 20 µs (`ultrasonic_pulse_time: 20us`) |
| Martwa strefa | ~25 cm od membrany |

---

## Dzielnik Echo (5 V → ~3,3 V)

```
JSN ECHO/TX ──[R1  10 kΩ]── GPIO26 ──[R2  20 kΩ]── GND
```

---

## Dzielnik baterii (tylko DevKit)

```
BAT+ ──[R5  100 kΩ]── GPIO34 ──[R6  100 kΩ]── GND
```

Firmware: `battery_adc_multiplier = V_baterii / V_GPIO34` (kalibracja miernikiem).

FireBeetle (docelowo): wbudowany dzielnik, użyj `multiply: 2.0`.

---

## Lista części (prototyp)

| Element | Wartość / typ |
|---------|---------------|
| ESP32 DevKit V1 + expansion board 38P | — |
| JSN-SR04T-V3.3 | Ultrasonik wodoodporny |
| MT3608 | Step-up do 5 V |
| IRLZ44N | N-MOSFET logic level, TO-220 |
| C1 | 1000 µF / 6,3 V elektrolityczny |
| C2 | 100 nF ceramiczny |
| R1, R3, R5, R6 | 10 kΩ, 10 kΩ, 100 kΩ, 100 kΩ |
| R2 | 20 kΩ |
| Holder 18650 + ogniwo | Li-ion 1S |

**Planowane:** moduł ładowania TP4056 (z ochroną DW01), panel solarny USB 5 V.

---

## Odrzucone okablowanie (nie używać)

| Okablowanie | Wynik |
|-------------|-------|
| Q1 na MT3608 IN− | Boost nie da się wyłączyć; moduł się grzeje |
| Q1 high-side na VCC (OUT+ → DRAIN) | ~0,9 V na czujniku przy bramce 3,3 V |
| OUT+ podłączony do DRAIN Q1 | Zła topologia |
| Luźny GPIO33 jako `wakeup_pin` | Natychmiastowe wybudzenie z deep sleep |
