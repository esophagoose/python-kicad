from enum import Enum
from typing import Annotated, Any, Dict, List, Optional, Union

from pydantic import BaseModel, BeforeValidator, Field, model_validator

ColorType = tuple[int, int, int, int]


def _get_points(points: list) -> List["Point"]:
    print(points)
    return points["xy"]

def _get_required(prop: Dict[str, str]) -> str:
    return prop["_required"]

def _get_property(prop: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    key = list(prop.keys())[0]
    return {
        "name": key,
        "value": prop[key]["_required"],
        "at": prop[key]["at"],
        "effects": prop[key]["effects"],
    }

def _correct_dict(symbol: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    key = list(symbol.keys())[0]
    symbol[key]["key"] = key
    return symbol[key]


class BaseListModel(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def convert(cls, data: list) -> Any:
        var_names = cls.model_json_schema()["properties"].keys()
        return dict(zip(var_names, data))


class NamedModel(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def convert(cls, data: list) -> Any:
        name = list(data.keys())[0]
        content = data[name]
        content.update({"name": name})
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


class Font(BaseModel):
    size: FontSize


class Justify(BaseListModel):
    horizontal: str
    vertical: str


class Effects(BaseModel):
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

    @model_validator(mode="before")
    @classmethod
    def convert(cls, data: Any) -> Any:
        return {"x": data[0], "y": data[1]}


class Points(BaseModel):
    points: List[Point]


class Stroke(BaseModel):
    width: float
    type: str


class Fill(BaseModel):
    type: FillType


class Polyline(BaseModel):
    points: Annotated[List[Point], BeforeValidator(_get_points)] = Field(alias="pts")
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
    at: Position
    effects: Optional[Effects] = None


class Pin(BaseModel):
    type: PinType = Field(alias="key")
    line: PinGraphic = Field(alias="_required")
    at: Position
    length: float
    name: Annotated[str, BeforeValidator(_get_required)]
    number: Annotated[str, BeforeValidator(_get_required)]
    effects: Optional[Effects] = None
    hide: Optional[bool] = None


class SymbolUnit(BaseModel):
    name: str = Field(alias="key")
    polyline: Optional[Polyline] = None
    rectangle: Optional[Rectangle] = None
    pins: List[Annotated[Pin, BeforeValidator(_correct_dict)]] = []


class LibrarySymbol(NamedModel):
    library: str = Field(alias="name")
    pin_numbers: Optional[Union[str, dict]] = None
    pin_names: Optional[Union[str, dict]] = None
    exclude_from_sim: Optional[bool] = None
    in_bom: Optional[bool] = None
    on_board: Optional[bool] = None
    properties: List[Annotated[Property, BeforeValidator(_get_property)]] = []
    symbols: List[Annotated[SymbolUnit, BeforeValidator(_correct_dict)]] = []


class Wire(BaseModel):
    points: Annotated[List[Point], BeforeValidator(_get_points)] = Field(alias="pts")
    stroke: Stroke
    uuid: Optional[str] = None


class Junction(BaseModel):
    at: Point
    diameter: float
    color: ColorType
    uuid: Optional[str] = None


class Text(BaseModel):
    text: str
    at: Point
    effects: Optional[Effects] = None
    uuid: Optional[str] = None


class SchematicSymbol(BaseModel):
    lib_id: str
    at: Point
    unit: Optional[int] = None
    value: Optional[str] = None
    footprint: Optional[str] = None
    uuid: Optional[str] = None
    properties: List[Annotated[Property, BeforeValidator(_get_property)]] = []


class TitleBlock(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    rev: Optional[str] = None
    company: Optional[str] = None
    comments: Optional[List[Any]] = None


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
    lib_symbols: Optional[
        Annotated[List[LibrarySymbol], BeforeValidator(lambda x: x["symbols"])]
    ] = []
    symbols: Optional[List[SchematicSymbol]] = []
    wires: Optional[List[Wire]] = []
    junctions: Optional[List[Junction]] = []
    polyline: Optional[List[Polyline]] = []
    text: Optional[List[Text]] = []
    global_labels: List[Label] = []
    hierarchical_labels: List[Label] = []
    labels: List[Label] = []
    sheet_instances: Optional[Any] = None
