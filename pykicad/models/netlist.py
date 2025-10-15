from typing import Annotated, Dict, List, Optional

from pydantic import BaseModel, BeforeValidator, Field, model_validator


def _get_fields(data: dict) -> Dict[str, str]:
    cleaned = {}
    for field in data["fields"]:
        if list(field.keys())[0] != "name":
            continue
        cleaned.update(field)
    return cleaned


def _get_properties(data: dict) -> Dict[str, str]:
    return {p["name"]: p["value"] for p in data}


def _get_footprints(data: dict) -> List[str]:
    if "fp" in data:
        return [data["fp"]]
    elif "fps" in data:
        return data["fps"]
    return []


class Comment(BaseModel):
    number: str
    value: str


class TitleBlock(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    rev: Optional[str] = None
    date: Optional[str] = None
    source: Optional[str] = None
    comments: List[Comment] = []


class Sheet(BaseModel):
    number: str
    name: str
    tstamps: str
    title_block: TitleBlock


class Design(BaseModel):
    source: str
    date: str
    tool: str
    sheet: Sheet


class LibSource(BaseModel):
    lib: str
    part: str
    description: str


class SheetPath(BaseModel):
    names: str
    tstamps: str


class Component(BaseModel):
    refdes: str = Field(alias="ref")
    value: str
    footprint: Optional[str] = None
    datasheet: Optional[str] = None
    fields: Annotated[Dict[str, str], BeforeValidator(_get_fields)] = {}
    libsource: LibSource
    property: Annotated[Dict[str, str], BeforeValidator(_get_properties)] = {}
    sheetpath: SheetPath


class Pin(BaseModel):
    name: str
    index: str = Field(alias="num")
    type: str


class LibPart(BaseModel):
    lib: str
    part: str
    description: str
    docs: Optional[str] = None
    footprints: Annotated[List[str], BeforeValidator(_get_footprints)] = []
    fields: Annotated[Dict[str, str], BeforeValidator(_get_fields)] = []
    pins: Annotated[List[Pin], BeforeValidator(lambda x: x["pins"])] = []


class Library(BaseModel):
    logical: str
    uri: str


class Node(BaseModel):
    ref: str
    pin: str
    pinfunction: Optional[str] = None
    pintype: Optional[str] = None


class Net(BaseModel):
    code: str
    name: str
    class_name: str
    nodes: List[Node] = []

    @model_validator(mode="before")
    @classmethod
    def convert_class_field(cls, data):
        if isinstance(data, dict) and "class" in data:
            data["class_name"] = data.pop("class")
        return data


class Netlist(BaseModel):
    design: Design
    components: Annotated[List[Component], BeforeValidator(lambda x: x["comps"])] = []
    libparts: Annotated[List[LibPart], BeforeValidator(lambda x: x["libparts"])] = []
    libraries: Annotated[Library, BeforeValidator(lambda x: x["library"])]
    nets: Annotated[List[Net], BeforeValidator(lambda x: x["nets"])]
    version: str
