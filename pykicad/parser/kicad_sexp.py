from collections import Counter
from typing import Dict, List

from simp_sexp import Sexp

import pykicad.models.kicad_sch as sch_types


def _parse_all_strings(sexp: List) -> Dict:
    # If all items are not lists, return them
    # If list starts with a number, it's meant to be an array. Just return it.
    if isinstance(sexp[0], (int, float)):
        return sexp
    # Single value lists can be returned as the value
    if len(sexp) == 1:
        return sexp[0]
    # Two value lists can be returned as a key-value pair
    if len(sexp) == 2:
        return {sexp[0]: sexp[1]}
    # Many length lists return a key-value pair
    return {sexp[0]: sexp[1:]}


def _normalized_bools(sexp: List) -> List:
    # Some booleans are default False and True if the name is present
    # Other booleans have the subsequent value be yes or no
    # This function normalizes to yes or no to work with the parser
    BOOLEANS = ["hide"]
    for boolean in BOOLEANS:
        if boolean in sexp:
            i = sexp.index(boolean)
            if len(sexp) <= i + 1 or sexp[i + 1] not in ["yes", "no"]:
                sexp[i] = [boolean, "yes"]
    return sexp


def _strip_single_element_lists(sexp: List) -> List:
    # Parser will sometimes have a single element list (ex: ["value"])
    # This function strips them to their value (ex: "value")
    for i, item in enumerate(sexp):
        if isinstance(item, list) and len(item) == 1:
            sexp[i] = item[0]
    return sexp


def parse_sexp(sexp: List) -> Dict:
    sexp = _normalized_bools(sexp)
    sexp = _strip_single_element_lists(sexp)
    is_list_items = [isinstance(s, list) for s in sexp]
    first = is_list_items.index(True) if True in is_list_items else None

    if isinstance(sexp, (int, float, str)):
        return sexp
    elif not any(is_list_items):
        # Nothing is a list, so parse the values
        return _parse_all_strings(sexp)
    elif not is_list_items[0] and all(is_list_items[1:]):
        # First values is string and the rest are lists
        # Named object where the first value is the name and the rest are the content
        return {sexp[0]: parse_sexp(sexp[1:])}
    elif first is not None and first > 1 and all(is_list_items[first:]):
        # Sometimes objects have required fields that aren't key, value pairs
        # First value is the name of the object, then the args are strings
        # and the remaining lists are key value pairs
        for i, item in enumerate(sexp[1:]):
            if isinstance(item, str):
                sexp[i + 1] = ["_required", item]
        return {sexp[0]: parse_sexp(sexp[1:])}
    elif all(is_list_items):
        # If all items are lists, then convert to key value pairs
        result = {}
        names = Counter([s[0] for s in sexp])
        for i, item in enumerate(sexp):
            is_list_item = [isinstance(s, list) for s in item]
            if names[item[0]] > 1:
                name = item[0] + "s"
                if name not in result:
                    result[name] = []
                result[name].append(parse_sexp(item[1:]))
            elif not any(is_list_item):
                result.update(_parse_all_strings(item))
            else:
                result.update(parse_sexp(item))
        return result
    raise ValueError("Invalid sexp to parse: ", sexp)


def read_in_schematic_from_kicad_sch(file_path: str) -> sch_types.Schematic:
    with open(file_path, "r") as f:
        content = f.read()

    sexp = Sexp(content)
    parsed = parse_sexp(sexp)
    return sch_types.Schematic(**parsed.get("kicad_sch"))


def read_in_schematic_from_string(content: str) -> sch_types.Schematic:
    sexp = Sexp(content)
    parsed = parse_sexp(sexp)
    return sch_types.Schematic(**parsed.get("kicad_sch"))
