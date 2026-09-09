#!/usr/bin/env python3
"""Generate minimal step-1 schematic: ESP32 DevKit + AO3401A + NPN driver only."""

from __future__ import annotations
import uuid
from pathlib import Path

ROOT_UUID = "5956fa7a-6761-471d-9407-b7d89429757a"
PROJECT = "tank-level-devkit"
OUT = Path(__file__).with_name("tank-level-devkit.kicad_sch")


def u() -> str:
    return str(uuid.uuid4())


def wire(x1: float, y1: float, x2: float, y2: float) -> str:
    return (
        f'\t(wire (pts (xy {x1} {y1}) (xy {x2} {y2}))'
        f' (stroke (width 0) (type default)) (uuid "{u()}"))'
    )


def junction(x: float, y: float) -> str:
    return f'\t(junction (at {x} {y}) (diameter 0) (color 0 0 0 0) (uuid "{u()}"))'


def global_label(name: str, x: float, y: float, angle: float = 0, shape: str = "input") -> str:
    return (
        f'\t(global_label "{name}"\n'
        f'\t\t(shape {shape})\n'
        f'\t\t(at {x} {y} {angle})\n'
        f'\t\t(fields_autoplaced yes)\n'
        f'\t\t(effects (font (size 1.27 1.27)) (justify left bottom))\n'
        f'\t\t(uuid "{u()}")\n'
        f'\t)'
    )


def text_note(x: float, y: float, content: str, size: float = 1.5) -> str:
    lines = content.split("\n")
    out = []
    for i, line in enumerate(lines):
        out.append(
            f'\t(text "{line}"\n'
            f'\t\t(exclude_from_sim yes)\n'
            f'\t\t(at {x} {y - i * 3.81} 0)\n'
            f'\t\t(effects (font (size {size} {size})) (justify left top))\n'
            f'\t\t(uuid "{u()}")\n'
            f'\t)'
        )
    return "\n".join(out)


def symbol(lib_id: str, ref: str, value: str, x: float, y: float, angle: float = 0) -> str:
    return (
        f'\t(symbol\n'
        f'\t\t(lib_id "{lib_id}")\n'
        f'\t\t(at {x} {y} {angle})\n'
        f'\t\t(unit 1)\n'
        f'\t\t(exclude_from_sim no)\n'
        f'\t\t(in_bom yes)\n'
        f'\t\t(on_board yes)\n'
        f'\t\t(dnp no)\n'
        f'\t\t(fields_autoplaced yes)\n'
        f'\t\t(uuid "{u()}")\n'
        f'\t\t(property "Reference" "{ref}"\n'
        f'\t\t\t(at {x} {y - 5.08} 0)\n'
        f'\t\t\t(effects (font (size 1.27 1.27)))\n'
        f'\t\t)\n'
        f'\t\t(property "Value" "{value}"\n'
        f'\t\t\t(at {x} {y + 5.08} 0)\n'
        f'\t\t\t(effects (font (size 1.27 1.27)))\n'
        f'\t\t)\n'
        f'\t\t(property "Footprint" ""\n'
        f'\t\t\t(at {x} {y} 0)\n'
        f'\t\t\t(effects (font (size 1.27 1.27)) hide)\n'
        f'\t\t)\n'
        f'\t\t(property "Datasheet" ""\n'
        f'\t\t\t(at {x} {y} 0)\n'
        f'\t\t\t(effects (font (size 1.27 1.27)) hide)\n'
        f'\t\t)\n'
        f'\t\t(instances\n'
        f'\t\t\t(project "{PROJECT}"\n'
        f'\t\t\t\t(path "/{ROOT_UUID}"\n'
        f'\t\t\t\t\t(reference "{ref}")\n'
        f'\t\t\t\t\t(unit 1)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)'
    )


def main() -> None:
    parts: list[str] = []

    # Title
    parts.append(
        text_note(
            20,
            30,
            "KROK 1 — ESP32 + AO3401A (sterowanie zasilaniem czujnika)\n"
            "Firmware: GPIO4 HIGH = czujnik ON | sensor_power bez inverted\n"
            "Nastepny krok: MT3608, JSN-SR04T, dzielniki",
            1.6,
        )
    )

    # Connection cheat sheet (right side)
    parts.append(
        text_note(
            200,
            30,
            "Polaczenia (breadboard):\n"
            "+5V (OUT+ MT3608) -> Q1 SOURCE (pin 2)\n"
            "+5V -> R1 (10k) -> Q1 GATE (pin 1)\n"
            "Q1 GATE -> Q2 kolektor\n"
            "Q2 emiter -> GND\n"
            "GPIO4 -> R2 (10k) -> Q2 baza\n"
            "Q1 DRAIN (pin 3) -> VCC czujnika\n"
            "GND czujnika -> GND\n"
            "NIE: OUT+ -> VCC czujnika (obok DRAIN)",
            1.35,
        )
    )

    # --- Symbols (spread out on A3) ---
    # ESP32 left
    parts.append(symbol("tank-level:ESP32_DEVKIT", "U2", "ESP32_DevKit_V1", 55, 120))

    # AO3401A center — user has this in library as Transistor_FET:AO3401A
    parts.append(symbol("Transistor_FET:AO3401A", "Q1", "AO3401A", 130, 120))

    # NPN below AO3401A
    parts.append(symbol("Transistor_BJT:2N3904", "Q2", "2N3904", 130, 165))

    # Resistors
    parts.append(symbol("Device:R", "R1", "10k", 105, 85))
    parts.append(symbol("Device:R", "R2", "10k", 175, 85))

    # Power symbols
    parts.append(symbol("power:+5V", "#PWR01", "+5V", 80, 70))
    parts.append(symbol("power:GND", "#PWR02", "GND", 130, 195))

    # --- Global labels (logical nets) ---
    parts.append(global_label("+5V", 90, 70, 0, "input"))
    parts.append(global_label("+5V", 115, 85, 0, "input"))
    parts.append(global_label("+5V", 115, 120, 0, "input"))
    parts.append(global_label("GPIO4", 70, 120, 0, "output"))
    parts.append(global_label("GPIO4", 165, 85, 180, "input"))
    parts.append(global_label("GATE", 145, 120, 0, "passive"))
    parts.append(global_label("SENSOR_VCC", 165, 120, 0, "output"))
    parts.append(global_label("GND", 130, 195, 0, "passive"))
    parts.append(global_label("GND", 155, 165, 0, "passive"))

    # --- Wires (logical bus layout — refine in KiCad) ---
    # +5V rail top
    parts.append(wire(83.82, 70, 115, 70))
    parts.append(wire(115, 70, 115, 85))
    parts.append(wire(115, 70, 115, 120))
    parts.append(junction(115, 70))

    # R1 between +5V and GATE node
    parts.append(wire(110, 85, 115, 85))
    parts.append(wire(100, 85, 110, 85))
    parts.append(wire(115, 85, 145, 85))
    parts.append(wire(145, 85, 145, 120))
    parts.append(junction(145, 85))

    # GPIO4 -> R2 -> Q2 base area
    parts.append(wire(70, 120, 85, 120))
    parts.append(wire(85, 120, 85, 85))
    parts.append(wire(85, 85, 100, 85))
    parts.append(wire(170, 85, 180, 85))
    parts.append(wire(180, 85, 180, 165))
    parts.append(wire(180, 165, 155, 165))
    parts.append(junction(85, 85))

    # Q2 collector to GATE
    parts.append(wire(130, 155, 145, 155))
    parts.append(wire(145, 155, 145, 120))
    parts.append(junction(145, 120))

    # Q1 drain -> SENSOR_VCC
    parts.append(wire(145, 120, 165, 120))

    # GND
    parts.append(wire(130, 175, 130, 195))
    parts.append(wire(130, 175, 155, 175))
    parts.append(wire(155, 175, 155, 165))

    # AO3401A pinout reminder
    parts.append(
        text_note(
            20,
            175,
            "AO3401A (SOT-23, napis do siebie):\n"
            "pin 1 = GATE | pin 2 = SOURCE (+5V) | pin 3 = DRAIN (SENSOR_VCC)",
            1.35,
        )
    )

    sch = "\n".join(
        [
            "(kicad_sch",
            "\t(version 20231120)",
            '\t(generator "tank-level-docs")',
            '\t(generator_version "1.1-step1")',
            f'\t(uuid "{ROOT_UUID}")',
            '\t(paper "A3")',
            "\t(title_block",
            '\t\t(title "Step 1 — ESP32 + AO3401A")',
            '\t\t(date "2026-09-08")',
            '\t\t(rev "0.2-step1")',
            '\t\t(comment 1 "Minimal schematic — sensor power only")',
            "\t)",
            "\t(lib_symbols)",
            *parts,
            "\t(sheet_instances",
            '\t\t(path "/"',
            '\t\t\t(page "1")',
            "\t\t)",
            "\t)",
            ")",
            "",
        ]
    )

    OUT.write_text(sch, encoding="utf-8")
    print(f"Wrote {OUT} (step 1: ESP + AO3401A only)")


if __name__ == "__main__":
    main()
