import pytest

from src.parser.kicad_sexp import (_normalized_bools, _parse_all_strings,
                                   _strip_single_element_lists, parse_sexp,
                                   read_in_schematic_from_kicad_sch)


class TestParseAllStrings:
    """Test the _parse_all_strings function"""

    def test_single_value_list(self):
        """Test parsing a single value list"""
        result = _parse_all_strings(["value"])
        assert result == "value"

    def test_key_value_pair(self):
        """Test parsing a key-value pair"""
        result = _parse_all_strings(["key", "value"])
        assert result == {"key": "value"}

    def test_many_value_list(self):
        """Test parsing a list with many values"""
        result = _parse_all_strings(["key", "value1", "value2", "value3"])
        assert result == {"key": ["value1", "value2", "value3"]}

    def test_numeric_array(self):
        """Test parsing a numeric array"""
        result = _parse_all_strings([1, 2, 3, 4])
        assert result == [1, 2, 3, 4]

    def test_float_array(self):
        """Test parsing a float array"""
        result = _parse_all_strings([1.5, 2.7, 3.1])
        assert result == [1.5, 2.7, 3.1]


class TestNormalizedBools:
    """Test the _normalized_bools function"""

    def test_hide_boolean_normalization(self):
        """Test that 'hide' boolean is normalized to ['hide', 'yes']"""
        sexp = ["component", "hide", "other_value"]
        result = _normalized_bools(sexp)
        assert result == ["component", ["hide", "yes"], "other_value"]

    def test_hide_with_existing_yes(self):
        """Test that 'hide' with existing 'yes' is not changed"""
        sexp = ["component", "hide", "yes", "other_value"]
        result = _normalized_bools(sexp)
        assert result == ["component", "hide", "yes", "other_value"]

    def test_hide_with_existing_no(self):
        """Test that 'hide' with existing 'no' is not changed"""
        sexp = ["component", "hide", "no", "other_value"]
        result = _normalized_bools(sexp)
        assert result == ["component", "hide", "no", "other_value"]

    def test_no_boolean_keywords(self):
        """Test that lists without boolean keywords are unchanged"""
        sexp = ["component", "value1", "value2"]
        result = _normalized_bools(sexp)
        assert result == ["component", "value1", "value2"]


class TestStripSingleElementLists:
    """Test the _strip_single_element_lists function"""

    def test_strip_single_element_list(self):
        """Test stripping a single element list"""
        sexp = ["component", ["value"], "other"]
        result = _strip_single_element_lists(sexp)
        assert result == ["component", "value", "other"]

    def test_multiple_single_element_lists(self):
        """Test stripping multiple single element lists"""
        sexp = ["component", ["value1"], ["value2"], "other"]
        result = _strip_single_element_lists(sexp)
        assert result == ["component", "value1", "value2", "other"]

    def test_no_single_element_lists(self):
        """Test that lists without single element lists are unchanged"""
        sexp = ["component", "value1", "value2"]
        result = _strip_single_element_lists(sexp)
        assert result == ["component", "value1", "value2"]

    def test_mixed_lists(self):
        """Test with mixed single element and multi-element lists"""
        sexp = ["component", ["value"], ["multi", "element"], "other"]
        result = _strip_single_element_lists(sexp)
        assert result == ["component", "value", ["multi", "element"], "other"]


class TestParse:
    """Test the main parse function"""

    def test_primitive_values(self):
        """Test parsing primitive values"""
        # The parse function expects lists, not primitive values
        # These should be handled by the caller
        # Numeric arrays are returned as arrays
        assert parse_sexp([42]) == [42]
        assert parse_sexp([3.14]) == [3.14]
        # String arrays with single element are returned as the element
        assert parse_sexp(["string"]) == "string"

    def test_simple_list_no_nested_lists(self):
        """Test parsing a simple list with no nested lists"""
        result = parse_sexp(["key", "value1", "value2"])
        assert result == {"key": ["value1", "value2"]}

    def test_key_with_list_values(self):
        """Test parsing a key with list values"""
        result = parse_sexp(["key", ["item1"], ["item2"]])
        assert result == {"key": ["item1", "item2"]}

    def test_all_list_items(self):
        """Test parsing when all items are lists"""
        result = parse_sexp([["key1", "value1"], ["key2", "value2"]])
        assert result == {"key1": "value1", "key2": "value2"}

    def test_duplicate_keys(self):
        """Test parsing with duplicate keys (should create pluralized key)"""
        result = parse_sexp([["key", "value1"], ["key", "value2"]])
        assert "keys" in result
        assert result["keys"] == ["value1", "value2"]

    def test_complex_nested_structure(self):
        """Test parsing a complex nested structure"""
        sexp = [
            "schematic",
            ["version", 20231120],
            ["generator", "eeschema"],
            ["components", ["comp1", "value1"], ["comp2", "value2"]],
        ]
        result = parse_sexp(sexp)
        assert result["schematic"]["version"] == 20231120
        assert result["schematic"]["generator"] == "eeschema"
        assert "components" in result["schematic"]

    def test_invalid_sexp_raises_error(self):
        """Test that invalid sexp raises ValueError"""
        with pytest.raises(ValueError):
            parse_sexp([["key", "value"], "unexpected"])


class TestParseKiCadSch:
    """Test the parse_sexp function"""

    def test_parse_sample_schematic(self):
        """Test parsing the sample schematic file"""
        schematic = read_in_schematic_from_kicad_sch("testdata/sample.kicad_sch")

        # Test basic properties
        assert schematic.version == 20231120
        assert schematic.generator == "eeschema"
        assert schematic.generator_version == "8.0"
        assert schematic.uuid == "5ad56ace-e9ba-4651-b929-73675fdbc4ee"
        assert schematic.paper == "USLetter"

    def test_wires_parsing(self):
        """Test that wires are properly parsed"""
        schematic = read_in_schematic_from_kicad_sch("testdata/sample.kicad_sch")

        if schematic.wires:
            for wire in schematic.wires:
                assert hasattr(wire, "points")
                assert hasattr(wire, "stroke")
                assert hasattr(wire, "uuid")
                if wire.stroke:
                    assert hasattr(wire.stroke, "width")
                    assert hasattr(wire.stroke, "type")

    def test_junctions_parsing(self):
        """Test that junctions are properly parsed"""
        schematic = read_in_schematic_from_kicad_sch("testdata/sample.kicad_sch")

        if schematic.junctions:
            for junction in schematic.junctions:
                assert hasattr(junction, "at")
                assert hasattr(junction, "diameter")
                assert hasattr(junction, "color")
                assert hasattr(junction, "uuid")

    def test_labels_parsing(self):
        """Test that labels are properly parsed"""
        schematic = read_in_schematic_from_kicad_sch("testdata/sample.kicad_sch")

        if schematic.labels:
            for label in schematic.labels:
                assert hasattr(label, "name")
                assert hasattr(label, "at")
                assert hasattr(label, "fields_autoplaced")
                assert hasattr(label, "effects")
                assert hasattr(label, "uuid")
