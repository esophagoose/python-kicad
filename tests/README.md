# PyKiCad Tests

This directory contains comprehensive unit tests for the PyKiCad library.

## Test Structure

- `test_parser.py` - Tests for the main parsing functions in `main.py`
- `test_models.py` - Tests for the Pydantic data models in `kicad_sch.py`
- `test_integration.py` - Integration tests for the full parsing pipeline
- `test_edge_cases.py` - Tests for edge cases, error handling, and boundary conditions
- `conftest.py` - Shared test fixtures and configuration

## Running Tests

### Prerequisites

Install the development dependencies:

```bash
pip install -e ".[dev]"
```

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=. --cov-report=html
```

This will generate an HTML coverage report in `htmlcov/index.html`.

### Run Specific Test Files

```bash
# Run only parser tests
pytest tests/test_parser.py

# Run only model tests
pytest tests/test_models.py

# Run only integration tests
pytest tests/test_integration.py

# Run only edge case tests
pytest tests/test_edge_cases.py
```

### Run Specific Test Classes

```bash
# Run only TestParseAllStrings class
pytest tests/test_parser.py::TestParseAllStrings

# Run only TestSchematic class
pytest tests/test_models.py::TestSchematic
```

### Run Specific Test Methods

```bash
# Run a specific test method
pytest tests/test_parser.py::TestParseAllStrings::test_single_value_list
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests with Detailed Output

```bash
pytest -vv
```

### Run Tests and Stop on First Failure

```bash
pytest -x
```

### Run Tests and Show Local Variables on Failure

```bash
pytest -l
```

## Test Categories

### Unit Tests (`test_parser.py`)

Tests for individual functions:
- `_parse_all_strings()` - Parsing simple lists
- `_normalized_bools()` - Boolean normalization
- `_strip_single_element_lists()` - List simplification
- `parse()` - Main parsing function
- `parse_kicad_sch()` - KiCad schematic parsing

### Model Tests (`test_models.py`)

Tests for Pydantic data models:
- Basic model creation and validation
- List-to-dict conversion for BaseListModel
- Named model conversion for NamedModel
- Enum values and validation
- Nested model relationships

### Integration Tests (`test_integration.py`)

End-to-end tests using real KiCad schematic files:
- Full parsing pipeline validation
- Data consistency across different files
- Element parsing verification
- Round-trip parsing consistency

### Edge Case Tests (`test_edge_cases.py`)

Tests for unusual scenarios:
- Empty and malformed inputs
- Extreme values and boundary conditions
- Error handling and exception cases
- Unicode and special characters
- Deep nesting and large datasets

## Test Data

Tests use the following KiCad schematic files from the `testdata/` directory:
- `sample.kicad_sch` - A comprehensive schematic with many elements
- `two.kicad_sch` - A simpler schematic for basic testing
- `sample_new.kicad_sch` - Another schematic for additional coverage

## Coverage

The tests aim to achieve high code coverage across:
- All public functions and methods
- All data model classes and validators
- Error handling paths
- Edge cases and boundary conditions

## Continuous Integration

These tests are designed to run in CI/CD pipelines and provide:
- Fast execution for unit tests
- Comprehensive coverage reporting
- Clear failure messages
- Consistent results across environments

## Adding New Tests

When adding new functionality:

1. Add unit tests for individual functions
2. Add model tests for new data structures
3. Add integration tests for end-to-end scenarios
4. Add edge case tests for error conditions
5. Update fixtures in `conftest.py` if needed

Follow the existing patterns for:
- Test class and method naming
- Docstrings and comments
- Assertion patterns
- Error handling tests
