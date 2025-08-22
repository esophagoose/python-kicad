from collections import Counter
from typing import Dict, List

from simp_sexp import Sexp

import kicad_sch as sch_types


def _parse_all_strings(sexp: List) -> Dict:
    if isinstance(sexp[0], (int, float)):
        return sexp
    if len(sexp) == 1:
        return sexp[0]
    if len(sexp) == 2:
        return {sexp[0]: sexp[1]}
    return {sexp[0]: sexp[1:]}


def parse(sexp: List) -> Dict:
    if "hide" in sexp:
        i = sexp.index("hide")
        if len(sexp) <= i + 1 or sexp[i + 1] not in ["yes", "no"]:
            sexp[i] = ["hide", "yes"]
    for i, item in enumerate(sexp):
        if isinstance(item, list) and len(item) == 1:
            sexp[i] = item[0]
    is_list_items = [isinstance(s, list) for s in sexp]
    try:
        first = next(i for i, x in enumerate(is_list_items) if x)
    except StopIteration:
        first = None

    if isinstance(sexp, (int, float, str)):
        return sexp
    elif not any(is_list_items):
        return _parse_all_strings(sexp)
    elif not is_list_items[0] and all(is_list_items[1:]):
        return {sexp[0]: parse(sexp[1:])}
    elif first is not None and first > 1 and all(is_list_items[first:]):
        for i, item in enumerate(sexp[1:]):
            if isinstance(item, str):
                sexp[i + 1] = ["_required", item]
        return {sexp[0]: parse(sexp[1:])}
    elif all(is_list_items):
        result = {}
        names = Counter([s[0] for s in sexp])
        for i, item in enumerate(sexp):
            is_list_item = [isinstance(s, list) for s in item]
            if names[item[0]] > 1:
                name = item[0] + "s"
                if name not in result:
                    result[name] = []
                result[name].append(parse(item[1:]))
            elif not any(is_list_item):
                result.update(_parse_all_strings(item))
            else:
                result.update(parse(item))
        return result
    raise ValueError("Invalid sexp to parse: ", sexp)


def parse_kicad_sch(content: str) -> sch_types.Schematic:
    """
    Parse a KiCad schematic file content and return a Schematic object.
    """
    sexp = Sexp(content)
    parsed = parse(sexp)
    schematic = sch_types.Schematic(**parsed.get("kicad_sch"))
    return schematic


def main():
    with open("testdata/sample.kicad_sch", "r") as f:
        content = f.read()

    schematic = parse_kicad_sch(content)

    print("\nKiCad Schematic Analysis:")
    print(f"Version: {schematic.version}")
    print(f"Generator: {schematic.generator}")
    print(f"Generator Version: {schematic.generator_version}")
    print(f"UUID: {schematic.uuid}")
    print(f"Paper Size: {schematic.paper}")

    assert schematic.version == 20231120
    assert schematic.generator == "eeschema"
    assert schematic.generator_version == "8.0"
    assert schematic.uuid == "5ad56ace-e9ba-4651-b929-73675fdbc4ee"
    assert schematic.paper == "USLetter"

    if schematic.title_block:
        print(f"Title: {schematic.title_block.title}")
        print(f"Date: {schematic.title_block.date}")
        print(f"Revision: {schematic.title_block.rev}")
        print(f"Company: {schematic.title_block.company}")

    # Count elements
    wire_count = len(schematic.wires) if schematic.wires else 0
    junction_count = len(schematic.junctions) if schematic.junctions else 0
    polyline_count = len(schematic.polyline) if schematic.polyline else 0
    lib_symbol_count = len(schematic.lib_symbols) if schematic.lib_symbols else 0
    label_count = len(schematic.labels) if schematic.labels else 0
    hierarchical_label_count = (
        len(schematic.hierarchical_labels) if schematic.hierarchical_labels else 0
    )
    global_label_count = len(schematic.global_labels) if schematic.global_labels else 0

    print(f"\nSchematic Elements:")
    print(f"Wires: {wire_count}")
    print(f"Junctions: {junction_count}")
    print(f"Polylines: {polyline_count}")
    print(f"Global Labels: {global_label_count}")
    print(f"Labels: {label_count}")
    print(f"Hierarchical Labels: {hierarchical_label_count}")
    print(f"Library Symbols: {lib_symbol_count}")

    # Show some library symbol details
    if schematic.lib_symbols and len(schematic.lib_symbols) > 0:
        print(f"\nLibrary Symbol Examples:")
        for i, lib_symbol in enumerate(schematic.lib_symbols[:3]):  # Show first 3
            print(f"  {i+1}. {lib_symbol.library}")
            print(f"     pin_numbers: {lib_symbol.pin_numbers}")
            print(f"     exclude_from_sim: {lib_symbol.exclude_from_sim}")
            print(f"     in_bom: {lib_symbol.in_bom}")
            print(f"     on_board: {lib_symbol.on_board}")
            if lib_symbol.property:
                print(f"     properties: {len(lib_symbol.property)}")
            print()

    # Show some wire details
    if schematic.wires and len(schematic.wires) > 0:
        print(f"Wire Examples:")
        for i, wire in enumerate(schematic.wires[:3]):  # Show first 3
            print(f"  {i+1}. UUID: {wire.uuid}")
            print(f"     Points: {len(wire.points)}")
            print(f"     Stroke width: {wire.stroke.width}")
            print(f"     Stroke type: {wire.stroke.type}")
            print()

    # Show some junction details
    if schematic.junctions and len(schematic.junctions) > 0:
        print(f"Junction Examples:")
        for i, junction in enumerate(schematic.junctions[:3]):  # Show first 3
            print(f"  {i+1}. At: {junction.at}")
            print(f"     Diameter: {junction.diameter}")
            print(f"     Color: {junction.color}")
            print(f"     UUID: {junction.uuid}")
            print()

    # Show some label details
    if schematic.labels:
        print(f"\nLabel Examples:")
        for i, label in enumerate(schematic.labels):
            print(f"  {i+1}. Name: {label.name}")
            print(f"     Position: {label.at}")
            print(f"     Fields Autoplaced: {label.fields_autoplaced}")
            print(f"     Effects: {label.effects}")
            print(f"     UUID: {label.uuid}")
            print()


if __name__ == "__main__":
    main()
