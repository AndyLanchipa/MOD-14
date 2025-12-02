import pytest
from pydantic import ValidationError

from app.schemas.calculation_schemas import (
    CalculationCreate,
    CalculationType,
    CalculationUpdate,
)


class TestCalculationSchemas:
    """Test cases for Pydantic calculation schemas"""

    def test_calculation_create_valid(self):
        """Test valid calculation creation"""
        calc_data = {"a": 5.0, "b": 3.0, "type": "ADD"}
        calc = CalculationCreate(**calc_data)
        assert calc.a == 5.0
        assert calc.b == 3.0
        assert calc.type == CalculationType.ADD

    def test_calculation_create_division_by_zero(self):
        """Test that division by zero is prevented in schema validation"""
        with pytest.raises(ValidationError) as exc_info:
            CalculationCreate(a=5.0, b=0.0, type="DIVIDE")
        assert "Division by zero is not allowed" in str(exc_info.value)

    def test_calculation_create_invalid_type(self):
        """Test that invalid calculation type raises validation error"""
        with pytest.raises(ValidationError):
            CalculationCreate(a=5.0, b=3.0, type="InvalidType")

    def test_calculation_create_string_numbers(self):
        """Test that string numbers are converted to float"""
        calc = CalculationCreate(a="5.5", b="3.2", type="ADD")
        assert calc.a == 5.5
        assert calc.b == 3.2
        assert isinstance(calc.a, float)
        assert isinstance(calc.b, float)

    def test_calculation_update_valid(self):
        """Test valid calculation update"""
        update_data = {"a": 10.0, "type": "MULTIPLY"}
        calc_update = CalculationUpdate(**update_data)
        assert calc_update.a == 10.0
        assert calc_update.b is None
        assert calc_update.type == CalculationType.MULTIPLY

    def test_calculation_update_division_by_zero(self):
        """Test division by zero prevention in update schema"""
        with pytest.raises(ValidationError) as exc_info:
            CalculationUpdate(b=0.0, type="DIVIDE")
        assert "Division by zero is not allowed" in str(exc_info.value)

    def test_calculation_type_enum_values(self):
        """Test that all expected calculation types are available"""
        expected_types = ["ADD", "SUB", "MULTIPLY", "DIVIDE"]
        actual_types = [t.value for t in CalculationType]
        assert set(actual_types) == set(expected_types)

    def test_calculation_create_negative_numbers(self):
        """Test calculation with negative numbers"""
        calc = CalculationCreate(a=-5.0, b=3.0, type="SUB")
        assert calc.a == -5.0
        assert calc.b == 3.0

    def test_calculation_create_zero_operands(self):
        """Test calculation with zero operands (except for division denominator)"""
        calc = CalculationCreate(a=0.0, b=5.0, type="ADD")
        assert calc.a == 0.0
        assert calc.b == 5.0

        calc = CalculationCreate(a=5.0, b=0.0, type="MULTIPLY")
        assert calc.a == 5.0
        assert calc.b == 0.0
