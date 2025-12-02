from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User
from app.routers import get_current_active_user
from app.schemas.calculation_schemas import (
    CalculationCreate,
    CalculationResponse,
    CalculationUpdate,
)
from app.services import calculation_service

router = APIRouter(prefix="/api/calculations", tags=["calculations"])


@router.post(
    "", response_model=CalculationResponse, status_code=status.HTTP_201_CREATED
)
def create_calculation(
    calculation: CalculationCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Create a new calculation (Add).

    Args:
        calculation (CalculationCreate): Calculation data
        current_user (User): Current authenticated user
        db (Session): Database session

    Returns:
        CalculationResponse: Created calculation with result
    """
    db_calculation = calculation_service.create_calculation(
        db, calculation, current_user.id
    )
    return db_calculation


@router.get("", response_model=List[CalculationResponse])
def get_calculations(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records"),
):
    """
    Get all calculations for the current user (Browse).

    Args:
        current_user (User): Current authenticated user
        db (Session): Database session
        skip (int): Number of records to skip for pagination
        limit (int): Maximum number of records to return

    Returns:
        List[CalculationResponse]: List of user's calculations
    """
    calculations = calculation_service.get_calculations(
        db, current_user.id, skip=skip, limit=limit
    )
    return calculations


@router.get("/{calculation_id}", response_model=CalculationResponse)
def get_calculation(
    calculation_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Get a specific calculation by ID (Read).

    Args:
        calculation_id (int): ID of the calculation
        current_user (User): Current authenticated user
        db (Session): Database session

    Returns:
        CalculationResponse: Calculation details

    Raises:
        HTTPException: If calculation not found or not owned by user
    """
    calculation = calculation_service.get_calculation_by_id(
        db, calculation_id, current_user.id
    )
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found",
        )
    return calculation


@router.patch("/{calculation_id}", response_model=CalculationResponse)
def update_calculation(
    calculation_id: int,
    calculation_update: CalculationUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Update a calculation (Edit).

    Args:
        calculation_id (int): ID of the calculation to update
        calculation_update (CalculationUpdate): Updated calculation data
        current_user (User): Current authenticated user
        db (Session): Database session

    Returns:
        CalculationResponse: Updated calculation

    Raises:
        HTTPException: If calculation not found or not owned by user
    """
    try:
        updated_calculation = calculation_service.update_calculation(
            db, calculation_id, current_user.id, calculation_update
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    if not updated_calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found",
        )
    return updated_calculation


@router.delete("/{calculation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(
    calculation_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Delete a calculation (Delete).

    Args:
        calculation_id (int): ID of the calculation to delete
        current_user (User): Current authenticated user
        db (Session): Database session

    Raises:
        HTTPException: If calculation not found or not owned by user
    """
    success = calculation_service.delete_calculation(
        db, calculation_id, current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found",
        )
    return None
