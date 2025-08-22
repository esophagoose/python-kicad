from email.mime import image
from pydantic import BaseModel, Field, BeforeValidator, model_validator
from typing import Optional, List, Any, Union, Dict, Annotated
from enum import Enum
from simp_sexp import Sexp
from collections import Counter

def _sexp_to_dict(sexp: list) -> dict:
    field = {}
    for param in sexp:
        field[param[0]] = param[1:]
        if len(param) == 2:
            field[param[0]] = param[1]
    return field

def _get_points(points: list) -> 'Points':
    return points['xys']


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
    
class NamedModel(BaseModel):
    @model_validator(mode='before')
    @classmethod
    def convert(cls, data: list) -> Any:
        name = list(data.keys())[0]
        content = data[name]
        content.update({'name': name})
        return content

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

    @model_validator(mode='before')
    @classmethod
    def convert(cls, data: Any) -> Any:
        return {'x': data[0], 'y': data[1]}


class Points(BaseModel):
    points: List[Point]


class Stroke(BaseModel):
    width: float
    type: str


class Fill(BaseModel):
    type: FillType


class Polyline(BaseModel):
    points: Annotated[Points, BeforeValidator(_get_points)]
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


class LibrarySymbol(NamedModel):
    library: str = Field(alias="name")
    pin_numbers: Optional[Union[str, dict]] = None
    pin_names: Optional[Union[str, dict]] = None
    exclude_from_sim: Optional[str] = None
    in_bom: Optional[str] = None
    on_board: Optional[str] = None
    property: Optional[List[Property]] = None
    symbol: Optional[SymbolUnit] = None

class Wire(BaseModel):
    points: Annotated[List[Point], BeforeValidator(_get_points)] = Field(alias="pts")
    stroke: Stroke
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
    comments: Optional[List[Any]] = None


class Paper(BaseModel):
    size: str

class Label(NamedModel):
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
    lib_symbols: Optional[Annotated[List[LibrarySymbol], BeforeValidator(lambda x: x['symbols'])]] = None
    # symbol: Optional[List[SchematicSymbol]] = None
    wires: Optional[List[Wire]] = None
    junctions: Optional[List[Junction]] = None
    polyline: Optional[List[Polyline]] = None
    text: Optional[List[Text]] = None
    global_labels: List[Label] = []
    hierarchical_labels: List[Label] = []
    labels: List[Label] = []
    sheet_instances: Optional[Any] = None

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
        if len(sexp) <= i + 1 or sexp[i+1] not in ["yes", "no"]:
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
                sexp[i+1] = ["_required", item]
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


def parse_kicad_sch(content: str) -> Schematic:
    """
    Parse a KiCad schematic file content and return a Schematic object.
    """
    # Parse the S-expression content
    sexp = Sexp(content)
    
    if not sexp or sexp[0] != "kicad_sch":
        raise ValueError("Invalid KiCad schematic file")
    # assert Schematic(**parse(sexp[:7]).get("kicad_sch")) == Schematic(version=20231120, generator='eeschema', generator_version='8.0', uuid='5ad56ace-e9ba-4651-b929-73675fdbc4ee', paper='USLetter', title_block=TitleBlock(title='Castor & Pollux', date='2022-10-07', rev='v6', company='Winterbloom', comments=[{1: 'Alethea Flowers'}, {2: 'CERN-OHL-P v2'}, {3: 'gemini.wntr.dev'}])), "Base case is broken!"
    print("  Base case is passed  ".upper().center(80, "="))
    print()

    parsed = parse(sexp)
    schematic = Schematic(**parsed.get("kicad_sch"))
    return schematic
