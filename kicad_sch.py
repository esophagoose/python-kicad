from email.mime import image
from pydantic import BaseModel, Field, BeforeValidator, model_validator
from typing import Optional, List, Any, Union, Dict, Annotated
from enum import Enum
from simp_sexp import Sexp

def _sexp_to_dict(sexp: list) -> dict:
    field = {}
    if not any(isinstance(s, list) for s in sexp):
        return {sexp[0]: sexp[1:]}
    for param in sexp:
        field[param[0]] = param[1:]
        if len(param) == 2:
            field[param[0]] = param[1]
    return field

def _sexp_points(points: list) -> 'Points':
    return Points(points=[Point(x=p[1], y=p[2]) for p in points])


class BaseSexpModel(BaseModel):
    @model_validator(mode='before')
    @classmethod
    def convert(cls, data: Any) -> Any:  
        return _sexp_to_dict(data)

class BaseListModel(BaseModel):
    @model_validator(mode='before')
    @classmethod
    def convert(cls, data: list) -> Any:
        var_names = cls.model_json_schema()['properties'].keys()
        return dict(zip(var_names, data))
    
class NamedSexpModel(BaseModel):
    @model_validator(mode='before')
    @classmethod
    def convert(cls, data: list) -> Any:
        data[0] = ["name", data[0]]
        return _sexp_to_dict(data)

class StrokeType(str, Enum):
    DEFAULT = "default"
    SOLID = "solid"
    DASH = "dash"
    DASHDOT = "dashdot"
    DOT = "dot"

class PinGraphic(str, Enum):
    LINE = "line"
    INVERTED = "inverted"
    CLOCK = "clock"
    INVERTED_CLOCK = "inverted_clock"
    INPUT_LOW = "input_low"
    CLOCK_LOW = "clock_low"
    OUTPUT_LOW = "output_low"
    EDGE_CLOCK_HIGH = "edge_clock_high"
    NON_LOGIC = "non_logic"

class FillType(str, Enum):
    NONE = "none"
    OUTLINE = "outline"
    BACKGROUND = "background"


class FontSize(BaseListModel):
    width: float
    height: float


class Font(BaseSexpModel):
    size: FontSize

class Justify(BaseListModel):
    horizontal: str
    vertical: str

class Effects(BaseSexpModel):
    font: Optional[Font] = None
    justify: Optional[Justify] = None
    hide: bool = False


class Position(BaseListModel):
    x: float
    y: float
    angle: float


class Point(BaseModel):
    x: float
    y: float


class Points(BaseModel):
    points: List[Point]


class Stroke(BaseModel):
    width: float
    type: str


class Fill(BaseModel):
    type: FillType


class Polyline(BaseModel):
    points: Annotated[Points, BeforeValidator(_sexp_points)]
    stroke: Stroke
    fill: Fill
    uuid: Optional[str] = None


class Rectangle(BaseModel):
    start: Point
    end: Point
    stroke: Stroke
    fill: Fill
    uuid: Optional[str] = None


class PinType(str, Enum):
    PASSIVE = "passive"
    INPUT = "input"
    OUTPUT = "output"
    POWER_IN = "power_in"
    POWER_OUT = "power_out"
    BIDIRECTIONAL = "bidirectional"



class Property(BaseModel):
    name: str
    value: str
    at: str
    effects: Optional[Effects] = None


class Pin(BaseSexpModel):
    type: PinType
    line: PinGraphic
    at: Position
    length: float
    name: Property
    number: Property
    effects: Optional[Effects] = None
    hide: Optional[bool] = None

    @model_validator(mode='before')
    @classmethod
    def convert(cls, data: Any) -> Any:
        data[0] = ["type", data[0]]
        data[1] = ["line", data[1]]
        return _sexp_to_dict(data)


class SymbolUnit(BaseModel):
    name: str
    library: str
    polyline: Optional[List[Polyline]] = None
    rectangle: Optional[List[Rectangle]] = None
    pin: Optional[Pin] = None

    @model_validator(mode='before')
    @classmethod
    def convert(cls, data: list) -> dict:
        data[0] = ["name", data[0]]
        return _sexp_to_dict(data)


class LibrarySymbol(BaseModel):
    library: str
    pin_numbers: Optional[Union[str, dict]] = None
    pin_names: Optional[Union[str, dict]] = None
    exclude_from_sim: Optional[str] = None
    in_bom: Optional[str] = None
    on_board: Optional[str] = None
    property: Optional[List[Property]] = None
    symbol: Optional[SymbolUnit] = None

    @model_validator(mode='before')
    @classmethod
    def convert(cls, data: list) -> dict:
        data = data[1:]
        data[0] = ["library", data[0]]
        return _sexp_to_dict(data)

class Wire(BaseModel):
    points: Annotated[Points, BeforeValidator(_sexp_points)] = Field(alias="pts")
    stroke: Annotated[Stroke, BeforeValidator(_sexp_to_dict)]
    uuid: Optional[str] = None


class Junction(BaseModel):
    at: tuple[float, float]
    diameter: float
    color: tuple[int, int, int, int]
    uuid: Optional[str] = None


class Text(BaseModel):
    text: str
    at: str
    effects: Optional[Effects] = None
    uuid: Optional[str] = None


class SchematicSymbol(BaseModel):
    lib_id: str
    at: str
    unit: Optional[int] = None
    value: Optional[str] = None
    footprint: Optional[str] = None
    uuid: Optional[str] = None
    property: Optional[List[Property]] = None


class TitleBlock(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    rev: Optional[str] = None
    company: Optional[str] = None
    comment: Optional[List[dict]] = None


class Paper(BaseModel):
    size: str

class Label(NamedSexpModel):
    name: str
    shape: Optional[str] = None
    at: Position
    fields_autoplaced: bool = False
    effects: Optional[Effects] = None
    uuid: Optional[str] = None

class Schematic(BaseModel):
    version: int
    generator: str
    generator_version: str
    uuid: str
    paper: str
    title_block: Optional[TitleBlock] = None
    symbol: Optional[List[SchematicSymbol]] = None
    wires: List[Wire]
    junctions: List[Junction]
    polyline: Optional[List[Polyline]] = None
    text: Optional[List[Text]] = None
    global_labels: List[Label] = []
    hierarchical_labels: List[Label] = []
    labels: List[Label] = []
    sheet_instances: Optional[List[Any]] = None
    lib_symbols: List[LibrarySymbol] = []


def parse_sexp_to_dict(sexp_list: List) -> Dict:
    """Convert S-expression list to dictionary format"""
    if not isinstance(sexp_list, list):
        return sexp_list
    
    if len(sexp_list) == 0:
        return {}
    
    if len(sexp_list) == 1:
        return sexp_list[0]
    
    result = {}
    i = 0
    
    while i < len(sexp_list):
        item = sexp_list[i]
        
        if isinstance(item, str):
            key = item
            # Check if there's a next item
            if i + 1 < len(sexp_list):
                next_item = sexp_list[i + 1]
                if isinstance(next_item, list):
                    # Parse nested structure
                    parsed_value = parse_sexp_to_dict(next_item)
                    if key in result:
                        if not isinstance(result[key], list):
                            result[key] = [result[key]]
                        result[key].append(parsed_value)
                    else:
                        result[key] = parsed_value
                    i += 2
                else:
                    # Simple value
                    result[key] = next_item
                    i += 2
            else:
                # Key without value
                result[key] = True
                i += 1
        elif isinstance(item, list):
            # Nested list without key - parse it recursively
            return parse_sexp_to_dict(item)
        else:
            i += 1
    
    return result


def parse_simple_sexp(sexp_list: List) -> Dict:
    """Simple S-expression parser for KiCad format"""
    if not isinstance(sexp_list, list):
        return sexp_list
    
    if len(sexp_list) == 0:
        return {}
    
    if len(sexp_list) == 1:
        return sexp_list[0]
    
    result = {}
    i = 0
    
    while i < len(sexp_list):
        item = sexp_list[i]
        
        if isinstance(item, str):
            key = item
            # Check if there's a next item
            if i + 1 < len(sexp_list):
                next_item = sexp_list[i + 1]
                if isinstance(next_item, list):
                    # Parse nested structure
                    parsed_value = parse_simple_sexp(next_item)
                    result[key] = parsed_value
                    i += 2
                else:
                    # Check if there are more values after this one
                    values = [next_item]
                    j = i + 2
                    while j < len(sexp_list) and not isinstance(sexp_list[j], str):
                        values.append(sexp_list[j])
                        j += 1
                    
                    if len(values) == 1:
                        result[key] = values[0]
                    else:
                        result[key] = values
                    i = j
            else:
                # Key without value
                result[key] = True
                i += 1
        elif isinstance(item, list):
            # Nested list without key - parse it recursively
            return parse_simple_sexp(item)
        else:
            i += 1
    
    return result


def parse_sexp_to_dict(sexp_list: List) -> Dict:
    """Convert S-expression list to dictionary format"""
    if not isinstance(sexp_list, list):
        return sexp_list
    
    if len(sexp_list) == 0:
        return {}
    
    if len(sexp_list) == 1:
        return sexp_list[0]
    
    result = {}
    current_key = None
    
    for item in sexp_list:
        if isinstance(item, str) and not current_key:
            current_key = item
        elif isinstance(item, list):
            if current_key:
                if current_key in result:
                    if not isinstance(result[current_key], list):
                        result[current_key] = [result[current_key]]
                    result[current_key].append(parse_sexp_to_dict(item))
                else:
                    result[current_key] = parse_sexp_to_dict(item)
                current_key = None
            else:
                return parse_sexp_to_dict(item)
        else:
            if current_key:
                result[current_key] = item
                current_key = None
    
    return result

def parse_kicad_sch(content: str) -> Schematic:
    """
    Parse a KiCad schematic file content and return a Schematic object.
    """
    # Parse the S-expression content
    sexp = Sexp(content)
    sexp_list = list(sexp)
    
    if not sexp_list or sexp_list[0] != "kicad_sch":
        raise ValueError("Invalid KiCad schematic file")
    
    # The sexp_list is a flat list where each element is a separate S-expression
    # We need to parse each one individually
    data = {}
    
    for item in sexp_list[1:]:  # Skip the first "kicad_sch" element
        if isinstance(item, list) and len(item) >= 1:
            key, value = item[0], item[1:]
            if len(item) == 2:
                # Simple key-value pair
                data[key] = value[0]
            elif key == "lib_symbols":
                # Special handling for lib_symbols - it contains multiple symbol definitions
                # data[key] = value
                continue
                symbols = []
                for sub_item in item[1:]:
                    if isinstance(sub_item, list) and len(sub_item) >= 2 and sub_item[0] == "symbol":
                        symbol_name = sub_item[1]
                        symbol_data = parse_simple_sexp(sub_item[2:])
                        if isinstance(symbol_data, dict):
                            symbol_data["name"] = symbol_name  # Add the symbol name
                            symbols.append(symbol_data)
                        else:
                            # Handle case where symbol_data is not a dict
                            symbols.append({"name": symbol_name, "data": symbol_data})
                data[key] = {"symbol": symbols}
            elif key in ["junction", "wire", "polyline", "text"]:
                key += "s"
                field = {}
                for param in value:
                    field[param[0]] = param[1:]
                    if len(param) == 2:
                        field[param[0]] = param[1]
                if key not in data:
                    data[key] = []
                data[key].append(field)
            elif key in ["global_label", "hierarchical_label", "label"]:
                key += "s"
                if key not in data:
                    data[key] = []
                data[key].append(value)
            else:
                # data[key] = value
                continue
                # Complex structure
                parsed_item = parse_simple_sexp(item[1:])
                if key in data:
                    # If key already exists, make it a list
                    if not isinstance(data[key], list):
                        data[key] = [data[key]]
                    data[key].append(parsed_item)
                else:
                    data[key] = parsed_item

    names = set()
    for i, s in enumerate(sexp_list):
        if isinstance(s, list):
            names.add(s[0])
    print(names)
    print("="*100)

    schematic = Schematic(**data)
    import code
    code.interact(local=locals())
    
    # Parse title block
    if "title_block" in data:
        tb_data = data["title_block"]
        schematic.title_block = TitleBlock(
            title=tb_data.get("title"),
            date=tb_data.get("date"),
            rev=tb_data.get("rev"),
            company=tb_data.get("company"),
            comment=tb_data.get("comment")
        )
    
    # Parse library symbols
    if "lib_symbols" in data:
        lib_symbols = []
        lib_symbols_data = data["lib_symbols"]
        
        # lib_symbols contains a list of symbol definitions
        if isinstance(lib_symbols_data, dict) and "symbol" in lib_symbols_data:
            symbol_list = lib_symbols_data["symbol"]
            if not isinstance(symbol_list, list):
                symbol_list = [symbol_list]
            
            for symbol_data in symbol_list:
                if isinstance(symbol_data, dict):
                    lib_symbol = LibrarySymbol(
                        name=symbol_data.get("name", ""),
                        pin_numbers=symbol_data.get("pin_numbers"),
                        pin_names=symbol_data.get("pin_names"),
                        exclude_from_sim=symbol_data.get("exclude_from_sim"),
                        in_bom=symbol_data.get("in_bom"),
                        on_board=symbol_data.get("on_board")
                    )
                    
                    # Parse properties
                    if "property" in symbol_data:
                        properties = []
                        prop_list = symbol_data["property"]
                        if not isinstance(prop_list, list):
                            prop_list = [prop_list]
                        for prop_data in prop_list:
                            if isinstance(prop_data, dict):
                                properties.append(parse_property(prop_data))
                        lib_symbol.property = properties
                    
                    lib_symbols.append(lib_symbol)
        
        schematic.lib_symbols = lib_symbols
    return schematic
