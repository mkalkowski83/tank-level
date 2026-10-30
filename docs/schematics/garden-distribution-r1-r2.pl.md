# Schemat połączeń — rozdzielnica ogrodowa (minimum → rozbudowa)

Spec: [`../superpowers/specs/2026-10-10-garden-distribution-r1-r2-design.md`](../superpowers/specs/2026-10-10-garden-distribution-r1-r2-design.md)  
Lista zakupów: [`../bom/garden-distribution-r1-r2.xlsx`](../bom/garden-distribution-r1-r2.xlsx)  
Czujnik: [`../superpowers/specs/2026-09-24-tank-level-mains-design.md`](../superpowers/specs/2026-09-24-tank-level-mains-design.md)

> Instalacja 230 V zewnętrzna — montaż i odbiór zgodnie z przepisami. Ten dokument to intencja projektowa, nie projekt uprawniony.

---

## Minimum (teraz) — 1 skrzynka

```
                         BUDYNEK
                    uziemienie budynku
                            │
              dopływ 3×2,5 (L N PE) ── już jest
                            │
                            ▼
┌────────────────── R1 (jedyna skrzynka) ──────────────────┐
│                                                           │
│   L,N,PE IN ──► [Q0 rozłącznik 2P / 2 mod.]               │
│                      │                                    │
│                      ▼                                    │
│               szyna L / N / PE                            │
│                      │                                    │
│        [F-CZ  RCBO 1P+N  6–10 A  30 mA  typ A]            │
│                      │                                    │
│                      └── L N ──► kabel 2×1,5 ~13–15 m     │
│                                                           │
│        (puste miejsca: pompy / gniazda / smart — później) │
└───────────────────────────────────────────────────────────┘
                            │
                            ▼
                 ┌──── czujnik szamba (tank-level-mains) ────┐
                 │  J1 L/N → F1 → MOV → HLK → +5V NODE       │
                 │  always-on; bez smart                     │
                 └───────────────────────────────────────────┘
```

### Połączenia — minimum

| Od | Do | Przewody |
|----|-----|----------|
| Dopływ z budynku | Wejście Q0 (L, N); PE → szyna PE | 3×2,5 (istniejący) |
| Wyjście Q0 | Szyna L, N | — |
| Szyna L/N | Wejście F-CZ | — |
| Wyjście F-CZ | Dławik → czujnik | **2×1,5** ~15 m |
| Szyna PE | PE obudowy R1 | — |

### Aparaty — minimum

| ID | Rola | Spec |
|----|------|------|
| Q0 | Rozłącznik główny | **2P / 2 mod.**, In ≥ 40 A |
| F-CZ | RCBO czujnika | **1P+N**, 6–10 A (albo 16 A), **30 mA typ A**, charakterystyka B lub C |

---

## Docelowo (później) — ta sama R1 + opcjonalnie R2

Na tej samej szynie w R1 (kolejne RCBO → smart DIN → obciążenie):

| ID | Obciążenie | HA |
|----|------------|-----|
| F-P1 → S-P1 | pompa przy domu | tak |
| F-G1 → S-G1 | gniazdo przy R1 | tak |

Opcjonalna **R2** (~10 m, kabel 3×4 z R1) — gdy zechcesz podstację przy szambie; szczegóły w starszej wersji planu (arkusz Excel „Docelowo R1+R2”).

Kolejność na obwodzie sterowanym: **RCBO → smart DIN → obciążenie**.
