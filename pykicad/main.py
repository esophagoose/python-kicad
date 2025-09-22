from parser.kicad_sexp import read_in_schematic_from_kicad_sch

def main():
    schematic = read_in_schematic_from_kicad_sch("testdata/sample.kicad_sch")

    print("\nKiCad Schematic Analysis:")
    print(f"Version: {schematic.version}")
    print(f"Generator: {schematic.generator}")
    print(f"Generator Version: {schematic.generator_version}")
    print(f"UUID: {schematic.uuid}")
    print(f"Paper Size: {schematic.paper}")

    assert schematic.version == 20250824
    assert schematic.generator == "eeschema"
    assert schematic.generator_version == "8.0"
    assert schematic.uuid == "11111111-1111-1111-1111-111111111111"
    assert schematic.paper == "A4"

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
            if lib_symbol.properties:
                print(f"     properties: {len(lib_symbol.properties)}")
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
    return schematic


if __name__ == "__main__":
    sch = main()
