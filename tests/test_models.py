import pytest

from pykicad.models.kicad_sch import (Effects, Fill, FillType, Font, FontSize,
                                      Junction, Justify, Label, LibrarySymbol,
                                      Pin, PinGraphic, PinType, Point, Points,
                                      Polyline, Position, Property, Rectangle,
                                      Schematic, SchematicSymbol, Stroke,
                                      StrokeType, SymbolUnit, Text, TitleBlock,
                                      Wire)


class TestFont:
    """Test the Font model"""

    def test_font_creation(self):
        """Test creating a Font with size"""
        font_size = FontSize.model_validate([1.5, 2.0])
        font = Font(size=font_size)
        assert font.size.width == 1.5
        assert font.size.height == 2.0


class TestJustify:
    """Test the Justify model"""

    def test_justify_creation(self):
        """Test creating a Justify with horizontal and vertical alignment"""
        justify = Justify.model_validate(["left", "top"])
        assert justify.horizontal == "left"
        assert justify.vertical == "top"

    def test_justify_from_list(self):
        """Test creating Justify from a list"""
        justify = Justify.model_validate(["center", "middle"])
        assert justify.horizontal == "center"
        assert justify.vertical == "middle"


class TestEffects:
    """Test the Effects model"""

    def test_effects_creation(self):
        """Test creating Effects with optional fields"""
        effects = Effects()
        assert effects.hide is False

    def test_effects_with_font(self):
        """Test creating Effects with font"""
        font = Font(size=FontSize.model_validate([1.0, 1.5]))
        effects = Effects(font=font, hide=True)
        assert effects.font.size.width == 1.0
        assert effects.hide is True

    def test_effects_with_justify(self):
        """Test creating Effects with justify"""
        justify = Justify.model_validate(["right", "bottom"])
        effects = Effects(justify=justify)
        assert effects.justify.horizontal == "right"
        assert effects.justify.vertical == "bottom"


class TestPosition:
    """Test the Position model"""

    def test_position_creation(self):
        """Test creating a Position with x, y, and angle"""
        position = Position.model_validate([10.0, 20.0, 45.0])
        assert position.x == 10.0
        assert position.y == 20.0
        assert position.angle == 45.0


class TestPoint:
    """Test the Point model"""

    def test_point_creation(self):
        """Test creating a Point with x and y"""
        point = Point.model_validate([10.0, 20.0])
        assert point.x == 10.0
        assert point.y == 20.0


class TestPoints:
    """Test the Points model"""

    def test_points_creation(self):
        """Test creating Points with a list of Point objects"""
        points = Points(
            points=[
                Point.model_validate([0.0, 0.0]),
                Point.model_validate([10.0, 10.0]),
                Point.model_validate([20.0, 0.0]),
            ]
        )
        assert len(points.points) == 3
        assert points.points[0].x == 0.0
        assert points.points[1].y == 10.0


class TestStroke:
    """Test the Stroke model"""

    def test_stroke_creation(self):
        """Test creating a Stroke with width and type"""
        stroke = Stroke(width=0.25, type="solid")
        assert stroke.width == 0.25
        assert stroke.type == "solid"


class TestFill:
    """Test the Fill model"""

    def test_fill_creation(self):
        """Test creating a Fill with type"""
        fill = Fill(type=FillType.NONE)
        assert fill.type == FillType.NONE

    def test_fill_types(self):
        """Test all fill types"""
        assert FillType.NONE == "none"
        assert FillType.OUTLINE == "outline"
        assert FillType.BACKGROUND == "background"


class TestPolyline:
    """Test the Polyline model"""

    def test_polyline_creation(self):
        """Test creating a Polyline"""
        data = {
            "pts": {"xys": [[0.0, 0.0], [10.0, 10.0], [20.0, 20.0]]},
            "stroke": {"width": 0.25, "type": "solid"},
            "fill": {"type": "none"},
            "uuid": "test-uuid",
        }
        polyline = Polyline(**data)
        assert len(polyline.points) == 3
        assert polyline.stroke.width == 0.25
        assert polyline.fill.type == FillType.NONE
        assert polyline.uuid == "test-uuid"


class TestRectangle:
    """Test the Rectangle model"""

    def test_rectangle_creation(self):
        """Test creating a Rectangle"""
        start = Point.model_validate([0.0, 0.0])
        end = Point.model_validate([10.0, 10.0])
        stroke = Stroke(width=0.25, type="solid")
        fill = Fill(type=FillType.OUTLINE)

        rectangle = Rectangle(
            start=start, end=end, stroke=stroke, fill=fill, uuid="test-uuid"
        )

        assert rectangle.start.x == 0.0
        assert rectangle.end.y == 10.0
        assert rectangle.stroke.type == "solid"
        assert rectangle.fill.type == FillType.OUTLINE
        assert rectangle.uuid == "test-uuid"


class TestProperty:
    """Test the Property model"""

    def test_property_creation(self):
        """Test creating a Property"""
        property_obj = Property(name="Value", value="10k", at="(10, 20) 0")
        assert property_obj.name == "Value"
        assert property_obj.value == "10k"
        assert property_obj.at == "(10, 20) 0"

    def test_property_with_effects(self):
        """Test creating a Property with effects"""
        effects = Effects(hide=False)
        property_obj = Property(
            name="Value", value="10k", at="(10, 20) 0", effects=effects
        )
        assert property_obj.effects.hide is False


class TestPin:
    """Test the Pin model"""

    def test_pin_creation(self):
        """Test creating a Pin"""
        position = Position.model_validate([0.0, 0.0, 0.0])
        name = Property(name="Name", value="VCC", at="(0, 0) 0")
        number = Property(name="Number", value="1", at="(0, 0) 0")

        pin = Pin(
            type=PinType.POWER_IN,
            line=PinGraphic.LINE,
            at=position,
            length=2.54,
            name=name,
            number=number,
        )

        assert pin.type == PinType.POWER_IN
        assert pin.line == PinGraphic.LINE
        assert pin.length == 2.54
        assert pin.name.value == "VCC"
        assert pin.number.value == "1"

    def test_pin_types(self):
        """Test all pin types"""
        assert PinType.PASSIVE == "passive"
        assert PinType.INPUT == "input"
        assert PinType.OUTPUT == "output"
        assert PinType.POWER_IN == "power_in"
        assert PinType.POWER_OUT == "power_out"
        assert PinType.BIDIRECTIONAL == "bidirectional"

    def test_pin_graphics(self):
        """Test all pin graphics"""
        assert PinGraphic.LINE == "line"
        assert PinGraphic.INVERTED == "inverted"
        assert PinGraphic.CLOCK == "clock"
        assert PinGraphic.INVERTED_CLOCK == "inverted_clock"
        assert PinGraphic.INPUT_LOW == "input_low"
        assert PinGraphic.CLOCK_LOW == "clock_low"
        assert PinGraphic.OUTPUT_LOW == "output_low"
        assert PinGraphic.EDGE_CLOCK_HIGH == "edge_clock_high"
        assert PinGraphic.NON_LOGIC == "non_logic"


class TestSymbolUnit:
    """Test the SymbolUnit model"""

    def test_symbol_unit_creation(self):
        """Test creating a SymbolUnit"""
        symbol_unit = SymbolUnit(name="test_symbol", library="test_lib")
        assert symbol_unit.name == "test_symbol"
        assert symbol_unit.library == "test_lib"


class TestLibrarySymbol:
    """Test the LibrarySymbol model"""

    def test_library_symbol_creation(self):
        """Test creating a LibrarySymbol"""
        lib_symbol = LibrarySymbol.model_validate(
            {
                "test_symbol": {
                    "pin_numbers": "hide",
                    "exclude_from_sim": "yes",
                    "in_bom": "yes",
                    "on_board": "yes",
                }
            }
        )

        assert (
            lib_symbol.library == "test_symbol"
        )  # NamedModel uses the key as the library name
        assert lib_symbol.pin_numbers == "hide"
        assert lib_symbol.exclude_from_sim == "yes"
        assert lib_symbol.in_bom == "yes"
        assert lib_symbol.on_board == "yes"


class TestWire:
    """Test the Wire model"""

    def test_wire_creation(self):
        """Test creating a Wire"""
        data = {
            "pts": {"xys": [[0.0, 0.0], [10.0, 10.0]]},
            "stroke": {"width": 0.25, "type": "solid"},
            "uuid": "test-uuid",
        }

        wire = Wire(**data)

        assert len(wire.points) == 2
        assert wire.points[0].x == 0.0
        assert wire.points[1].y == 10.0
        assert wire.stroke.width == 0.25
        assert wire.uuid == "test-uuid"


class TestJunction:
    """Test the Junction model"""

    def test_junction_creation(self):
        """Test creating a Junction"""
        at = Point.model_validate([5.0, 5.0])
        color = (0, 0, 0, 255)

        junction = Junction(at=at, diameter=0.5, color=color, uuid="test-uuid")

        assert junction.at.x == 5.0
        assert junction.at.y == 5.0
        assert junction.diameter == 0.5
        assert junction.color == (0, 0, 0, 255)
        assert junction.uuid == "test-uuid"


class TestText:
    """Test the Text model"""

    def test_text_creation(self):
        """Test creating a Text"""
        at = Point.model_validate([10.0, 20.0])
        effects = Effects(hide=False)

        text = Text(text="Test Text", at=at, effects=effects, uuid="test-uuid")

        assert text.text == "Test Text"
        assert text.at.x == 10.0
        assert text.at.y == 20.0
        assert text.effects.hide is False
        assert text.uuid == "test-uuid"


class TestSchematicSymbol:
    """Test the SchematicSymbol model"""

    def test_schematic_symbol_creation(self):
        """Test creating a SchematicSymbol"""
        at = Point.model_validate([10.0, 20.0])

        symbol = SchematicSymbol(
            lib_id="test_lib:test_symbol",
            at=at,
            unit=1,
            value="Test Value",
            footprint="test_footprint",
            uuid="test-uuid",
        )

        assert symbol.lib_id == "test_lib:test_symbol"
        assert symbol.at.x == 10.0
        assert symbol.at.y == 20.0
        assert symbol.unit == 1
        assert symbol.value == "Test Value"
        assert symbol.footprint == "test_footprint"
        assert symbol.uuid == "test-uuid"


class TestTitleBlock:
    """Test the TitleBlock model"""

    def test_title_block_creation(self):
        """Test creating a TitleBlock"""
        title_block = TitleBlock(
            title="Test Schematic", date="2024-01-01", rev="1.0", company="Test Company"
        )

        assert title_block.title == "Test Schematic"
        assert title_block.date == "2024-01-01"
        assert title_block.rev == "1.0"
        assert title_block.company == "Test Company"


class TestLabel:
    """Test the Label model"""

    def test_label_creation(self):
        """Test creating a Label"""
        Position.model_validate([10.0, 20.0, 0.0])
        effects = Effects(hide=False)

        label = Label.model_validate(
            {
                "test_label": {
                    "shape": "input",
                    "at": [10.0, 20.0, 0.0],
                    "fields_autoplaced": True,
                    "effects": {"hide": False},
                    "uuid": "test-uuid",
                }
            }
        )

        assert label.name == "test_label"
        assert label.shape == "input"
        assert label.at.x == 10.0
        assert label.at.y == 20.0
        assert label.fields_autoplaced is True
        assert label.effects.hide is False
        assert label.uuid == "test-uuid"


class TestSchematic:
    """Test the Schematic model"""

    def test_schematic_creation(self):
        """Test creating a Schematic with minimal required fields"""
        schematic = Schematic(
            version=20231120,
            generator="eeschema",
            generator_version="8.0",
            uuid="test-uuid",
            paper="USLetter",
        )

        assert schematic.version == 20231120
        assert schematic.generator == "eeschema"
        assert schematic.generator_version == "8.0"
        assert schematic.uuid == "test-uuid"
        assert schematic.paper == "USLetter"

    def test_schematic_with_optional_fields(self):
        """Test creating a Schematic with optional fields"""
        title_block = TitleBlock(title="Test", date="2024-01-01")

        schematic = Schematic(
            version=20231120,
            generator="eeschema",
            generator_version="8.0",
            uuid="test-uuid",
            paper="USLetter",
            title_block=title_block,
            global_labels=[],
            hierarchical_labels=[],
            labels=[],
        )

        assert schematic.title_block.title == "Test"
        assert len(schematic.global_labels) == 0
        assert len(schematic.hierarchical_labels) == 0
        assert len(schematic.labels) == 0

    def test_stroke_types(self):
        """Test all stroke types"""
        assert StrokeType.DEFAULT == "default"
        assert StrokeType.SOLID == "solid"
        assert StrokeType.DASH == "dash"
        assert StrokeType.DASHDOT == "dashdot"
        assert StrokeType.DOT == "dot"
