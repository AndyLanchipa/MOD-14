from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.calculation_model import Calculation
from app.schemas.calculation_schemas import CalculationCreate, CalculationUpdate


def create_calculation(
    db: Session, calculation: CalculationCreate, user_id: int
) -> Calculation:
    """
    Create a new calculation in the database.

    Args:
        db (Session): Database session
        calculation (CalculationCreate): Calculation data to create
        user_id (int): ID of the user creating the calculation

    Returns:
        Calculation: Created calculation object
    """
    db_calculation = Calculation(
        a=calculation.a,
        b=calculation.b,
        type=calculation.type.value,
        user_id=user_id,
    )
    # Calculate and save the result
    db_calculation.save_result()

    db.add(db_calculation)
    db.commit()
    db.refresh(db_calculation)
    return db_calculation


def get_calculations(
    db: Session, user_id: int, skip: int = 0, limit: int = 20
) -> List[Calculation]:
    """
    Get all calculations for a user with pagination.

    Args:
        db (Session): Database session
        user_id (int): ID of the user
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return

    Returns:
        List[Calculation]: List of calculation objects
    """
    return (
        db.query(Calculation)
        .filter(Calculation.user_id == user_id)
        .order_by(Calculation.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_calculation_by_id(
    db: Session, calculation_id: int, user_id: int
) -> Optional[Calculation]:
    """
    Get a specific calculation by ID for a user.

    Args:
        db (Session): Database session
        calculation_id (int): ID of the calculation
        user_id (int): ID of the user

    Returns:
        Optional[Calculation]: Calculation object if found and owned by user,
            None otherwise
    """
    return (
        db.query(Calculation)
        .filter(Calculation.id == calculation_id, Calculation.user_id == user_id)
        .first()
    )


def update_calculation(
    db: Session,
    calculation_id: int,
    user_id: int,
    calculation_update: CalculationUpdate,
) -> Optional[Calculation]:
    """
    Update a calculation.

    Args:
        db (Session): Database session
        calculation_id (int): ID of the calculation to update
        user_id (int): ID of the user
        calculation_update (CalculationUpdate): Updated calculation data

    Returns:
        Optional[Calculation]: Updated calculation object if found and owned
            by user, None otherwise
    """
    db_calculation = get_calculation_by_id(db, calculation_id, user_id)
    if not db_calculation:
        return None

    # Update only provided fields
    update_data = calculation_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "type" and value is not None:
            setattr(db_calculation, field, value.value)
        else:
            setattr(db_calculation, field, value)

    # Validate division by zero after applying updates
    if update_data:
        if db_calculation.type == "DIVIDE" and db_calculation.b == 0:
            raise ValueError("Division by zero is not allowed")
        db_calculation.save_result()

    db.commit()
    db.refresh(db_calculation)
    return db_calculation


def delete_calculation(db: Session, calculation_id: int, user_id: int) -> bool:
    """
    Delete a calculation.

    Args:
        db (Session): Database session
        calculation_id (int): ID of the calculation to delete
        user_id (int): ID of the user

    Returns:
        bool: True if deleted successfully, False if not found or not owned by user
    """
    db_calculation = get_calculation_by_id(db, calculation_id, user_id)
    if not db_calculation:
        return False

    db.delete(db_calculation)
    db.commit()
    return True


def get_calculation_count(db: Session, user_id: int) -> int:
    """
    Get the total count of calculations for a user.

    Args:
        db (Session): Database session
        user_id (int): ID of the user

    Returns:
        int: Total number of calculations
    """
    return db.query(Calculation).filter(Calculation.user_id == user_id).count()
