import pytest
from sqlalchemy.orm import Session

from app.models.calculation_model import Calculation
from app.models.user_model import User
from app.schemas.calculation_schemas import CalculationCreate
from app.services.calculation_factory import CalculationFactory


class TestCalculationIntegration:
    """Integration tests for calculation database operations"""

    def test_create_calculation_in_db(self, db_session: Session):
        """Test creating and storing calculation in database"""
        # Create calculation using schema
        calc_data = CalculationCreate(a=10.0, b=5.0, type="ADD")
        result = CalculationFactory.calculate(calc_data.a, calc_data.b, calc_data.type)

        # Create database record
        db_calc = Calculation(
            a=calc_data.a, b=calc_data.b, type=calc_data.type, result=result
        )
        db_session.add(db_calc)
        db_session.commit()
        db_session.refresh(db_calc)

        # Verify stored data
        assert db_calc.id is not None
        assert db_calc.a == 10.0
        assert db_calc.b == 5.0
        assert db_calc.type == "ADD"
        assert db_calc.result == 15.0
        assert db_calc.created_at is not None

    def test_calculation_with_user_relationship(self, db_session: Session):
        """Test calculation with user foreign key relationship"""
        # Create a test user first
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashedpassword123",
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create calculation linked to user
        calc = Calculation(
            a=20.0, b=4.0, type="DIVIDE", result=5.0, user_id=test_user.id
        )
        db_session.add(calc)
        db_session.commit()
        db_session.refresh(calc)

        # Verify relationship
        assert calc.user_id == test_user.id
        assert calc.user.username == "testuser"
        assert len(test_user.calculations) == 1
        assert test_user.calculations[0].id == calc.id

    def test_calculation_model_calculate_result_method(self, db_session: Session):
        """Test the calculate_result method in Calculation model"""
        calc = Calculation(a=8.0, b=2.0, type="MULTIPLY")
        result = calc.calculate_result()
        assert result == 16.0

        # Test save_result method
        calc.save_result()
        assert calc.result == 16.0

    def test_calculation_model_division_by_zero(self, db_session: Session):
        """Test division by zero handling in model"""
        calc = Calculation(a=5.0, b=0.0, type="DIVIDE")
        with pytest.raises(ValueError, match="Division by zero is not allowed"):
            calc.calculate_result()

    def test_calculation_model_invalid_operation(self, db_session: Session):
        """Test invalid operation type in model"""
        calc = Calculation(a=5.0, b=3.0, type="InvalidOperation")
        with pytest.raises(ValueError, match="Unsupported operation type"):
            calc.calculate_result()

    def test_multiple_calculations_per_user(self, db_session: Session):
        """Test multiple calculations for same user"""
        # Create user
        user = User(
            username="mathuser", email="math@example.com", password_hash="password123"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create multiple calculations
        calculations_data = [
            {"a": 5, "b": 3, "type": "ADD"},
            {"a": 10, "b": 2, "type": "DIVIDE"},
            {"a": 4, "b": 6, "type": "MULTIPLY"},
        ]

        for calc_data in calculations_data:
            calc = Calculation(
                a=calc_data["a"],
                b=calc_data["b"],
                type=calc_data["type"],
                result=CalculationFactory.calculate(
                    calc_data["a"], calc_data["b"], calc_data["type"]
                ),
                user_id=user.id,
            )
            db_session.add(calc)

        db_session.commit()

        # Verify all calculations are linked to user
        user_calculations = (
            db_session.query(Calculation).filter(Calculation.user_id == user.id).all()
        )
        assert len(user_calculations) == 3

        # Verify results
        results = [calc.result for calc in user_calculations]
        expected_results = [8.0, 5.0, 24.0]  # 5+3, 10/2, 4*6
        assert set(results) == set(expected_results)

    def test_calculation_without_user(self, db_session: Session):
        """Test calculation without user relationship (anonymous calculation)"""
        calc = Calculation(a=7.0, b=3.0, type="SUB", result=4.0)
        db_session.add(calc)
        db_session.commit()
        db_session.refresh(calc)

        assert calc.user_id is None
        assert calc.user is None
        assert calc.result == 4.0

    def test_calculation_timestamps(self, db_session: Session):
        """Test that timestamps are properly set"""
        calc = Calculation(a=1.0, b=1.0, type="ADD", result=2.0)
        db_session.add(calc)
        db_session.commit()
        db_session.refresh(calc)

        assert calc.created_at is not None
        # updated_at should be None initially since no updates were made
        original_created_at = calc.created_at

        # Update the calculation
        calc.a = 2.0
        calc.result = 3.0
        db_session.commit()
        db_session.refresh(calc)

        assert calc.created_at == original_created_at  # Should not change
        assert calc.updated_at is not None  # Should be set after update

    def test_calculation_query_operations(self, db_session: Session):
        """Test various database query operations on calculations"""
        # Create test data
        calculations = [
            Calculation(a=5.0, b=2.0, type="ADD", result=7.0),
            Calculation(a=10.0, b=3.0, type="MULTIPLY", result=30.0),
            Calculation(a=15.0, b=5.0, type="DIVIDE", result=3.0),
            Calculation(a=20.0, b=8.0, type="SUB", result=12.0),
        ]

        for calc in calculations:
            db_session.add(calc)
        db_session.commit()

        # Test query by type
        add_calcs = (
            db_session.query(Calculation).filter(Calculation.type == "ADD").all()
        )
        assert len(add_calcs) == 1
        assert add_calcs[0].result == 7.0

        # Test query by result range
        high_results = (
            db_session.query(Calculation).filter(Calculation.result > 10).all()
        )
        assert len(high_results) == 2  # 30.0 and 12.0

        # Test count operations
        total_count = db_session.query(Calculation).count()
        assert total_count == 4

    def test_calculation_repr_method(self, db_session: Session):
        """Test the string representation of Calculation model"""
        calc = Calculation(a=5.0, b=3.0, type="ADD", result=8.0)
        expected_repr = "<Calculation(id=None, a=5.0, b=3.0, type='ADD', result=8.0)>"
        assert repr(calc) == expected_repr

        db_session.add(calc)
        db_session.commit()
        db_session.refresh(calc)

        # After saving, id should be present
        expected_repr_with_id = (
            f"<Calculation(id={calc.id}, a=5.0, b=3.0, type='ADD', result=8.0)>"
        )
        assert repr(calc) == expected_repr_with_id
