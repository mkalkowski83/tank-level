# Polaczenia — czujnik poziomu szamba

Prosty przewodnik montazowy (bez schematu CAD).

## 1. Zasilanie

| Od | Do |
|----|-----|
| 18650 (+) | FireBeetle **BAT+** |
| 18650 (+) | **C1 (+)** i **MT3608 IN+** (ta sama szyna BAT+) |
| 18650 (-) | **GND** (FireBeetle BAT-, masa wspolna) |
| C1 (-) | **GND** |
| Panel solarny USB | FireBeetle **USB** (tylko ladowanie) |

## 2. MT3608 + MOSFET (5 V dla czujnika)

| Od | Do |
|----|-----|
| MT3608 **IN+** | Szyna **BAT+** |
| MT3608 **IN-** | **GND** |
| MT3608 **OUT-** | **GND** |
| MT3608 **OUT+** | Ustaw multimetrem na **5,0 V** |
| MT3608 **OUT+** | **C2**, **VCC czujnika** (JSN-SR04T) |
| **GND czujnika** | **Q1 Drain (D), pin 2** |
| Q1 **Source (S), pin 3** | **GND** |
| Q1 **Gate (G), pin 1** | **GPIO16** + **R3 10k** do GND |

**Logika:** GPIO16 = HIGH wlacza czujnik (Q1 przewodzi, GND czujnika idzie do masy).

**Nie lacz:** OUT+ na DRAIN Q1 (odrzucony wariant high-side — patrz spec).

## 3. JSN-SR04T-V3.3 (sygnaly)

**Mode 0:** pad **MODE** otwarty (bez mostka M1/M2/M3). Impuls Trig **≥20 µs** w ESPHome.

| Pin czujnika | Polaczenie |
|--------------|------------|
| **VCC** | +5 V (z MT3608 OUT+) + **C2** |
| **GND** | **Q1 Drain (pin 2)** — docelowo; w prototypie USB → **GND** |
| **Trig / RX** | **GPIO25** (bez dzielnika) |
| **Echo / TX** | **R1 10k** → **GPIO26** → **R2 20k** → **GND** |

```
Echo/TX ----[R1 10k]---- GPIO26 ----[R2 20k]---- GND
Trig/RX  ---------------- GPIO25
```

**Uwaga:** ESPHome `ultrasonic` zwraca **metry** — konwersja do cm w filtrze `×100` (patrz spec firmware).

## 4. Przycisk wake

| Od | Do |
|----|-----|
| **GPIO39** | Przycisk (1 nog) |
| Przycisk (2 nog) | **GND** |
| **GPIO39** | opcjonalnie **R4 10k** do **3V3** (brak wew. pull-up na GPIO39) |

Alternatywa: **GPIO33** + pull-up wewnetrzny w ESPHome (bez R4).

## 5. Bateria (bez lutowania)

| Pin | Uwaga |
|-----|-------|
| **GPIO34** | ADC napiecia baterii — wbudowany dzielnik na FireBeetle |

Ogniwo **musi** byc na BAT+/BAT- FireBeetle.

## IRLZ44N — orientacja (TO-220, od frontu, piny w dol)

| Pin | Nazwa | Polaczenie |
|-----|-------|------------|
| 1 | GATE | GPIO16 + R3 |
| 2 | DRAIN | GND czujnika |
| 3 | SOURCE | GND |

## Przed wlaczeniem

1. Multimetrem: brak zwarcia **BAT+ - GND**
2. **C1**: plus na BAT+, minus na GND
3. **MT3608 OUT+** = 5,0 V (GPIO16 HIGH / 3V3 na Gate)
4. **GPIO16 HIGH**: DRAIN (GND czujnika) **~0 V** wzgledem GND (V DC, nie ciaglosc przy zasilonym VCC)
5. Brak **BMS** — software cutoff w ESPHome

## Elementy na PCB / stykowce

C1, C2, U2 MT3608, Q1, R1, R2, R3, SW1 + przewody do FireBeetle i czujnika.
