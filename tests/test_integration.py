import pytest

from pykicad.models.kicad_sch import Schematic
from pykicad.parser.kicad_sexp import (read_in_schematic_from_kicad_sch,
                                       read_in_schematic_from_string)


class TestIntegration:
    """Integration tests for the full parsing pipeline"""

    def test_parse_sample_schematic_integration(self):
        """Test parsing the complete sample schematic file"""
        schematic = read_in_schematic_from_kicad_sch("testdata/sample.kicad_sch")

        # Verify it's a valid Schematic object
        assert isinstance(schematic, Schematic)

        # Test all required fields are present and have correct types
        assert isinstance(schematic.version, int)
        assert isinstance(schematic.generator, str)
        assert isinstance(schematic.generator_version, str)
        assert isinstance(schematic.uuid, str)
        assert isinstance(schematic.paper, str)

        # Test specific values from the sample file
        assert schematic.version == 20250824, "Wrong version"
        assert schematic.generator == "eeschema", "Wrong generator"
        assert schematic.generator_version == "8.0", "Wrong generator version"
        assert schematic.uuid == "11111111-1111-1111-1111-111111111111", "Wrong UUID"
        assert schematic.paper == "A4", "Wrong paper"

    def test_error_handling_invalid_content(self):
        """Test error handling with invalid content"""
        with pytest.raises(Exception):
            read_in_schematic_from_string("invalid content")

    def test_error_handling_empty_content(self):
        """Test error handling with empty content"""
        with pytest.raises(Exception):
            read_in_schematic_from_string("")

    def test_error_handling_missing_required_fields(self):
        """Test error handling with missing required fields"""
        invalid_content = """
        (kicad_sch
          (version 20231120)
          (generator "eeschema")
          (generator_version "8.0")
          (uuid "test-uuid")
          # Missing paper field
        )
        """
        with pytest.raises(Exception):
            read_in_schematic_from_string(invalid_content)
