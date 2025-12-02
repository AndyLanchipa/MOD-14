from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CalculationType(str, Enum):
    """Enumeration for supported calculation types"""

    ADD = "ADD"
    SUB = "SUB"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"


class CalculationCreate(BaseModel):
    """Schema for creating a new calculation"""

    a: float = Field(..., description="First operand")
    b: float = Field(..., description="Second operand")
    type: CalculationType = Field(..., description="Type of calculation to perform")

    @model_validator(mode="after")
    def validate_division_by_zero(self):
        """Prevent division by zero"""
        if self.type == CalculationType.DIVIDE and self.b == 0:
            raise ValueError("Division by zero is not allowed")
        return self

    @field_validator("a", "b", mode="before")
    @classmethod
    def validate_operands(cls, v):
        """Basic validation for operands"""
        if not isinstance(v, (int, float, str)):
            raise ValueError("Operands must be numeric")
        return float(v)


class CalculationRead(BaseModel):
    """Schema for reading calculation data"""

    id: int
    a: float
    b: float
    type: str
    result: Optional[float]
    user_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class CalculationUpdate(BaseModel):
    """Schema for updating calculation data"""

    a: Optional[float] = None
    b: Optional[float] = None
    type: Optional[CalculationType] = None

    @model_validator(mode="after")
    def validate_division_by_zero(self):
        """Prevent division by zero on updates"""
        if self.b is not None and self.type == CalculationType.DIVIDE and self.b == 0:
            raise ValueError("Division by zero is not allowed")
        return self

    @field_validator("a", "b", mode="before")
    @classmethod
    def validate_operands(cls, v):
        """Basic validation for operands"""
        if v is not None and not isinstance(v, (int, float, str)):
            raise ValueError("Operands must be numeric")
        return float(v) if v is not None else v


class CalculationResponse(BaseModel):
    """Schema for calculation response with computed result"""

    id: int
    a: float
    b: float
    type: str
    result: float
    user_id: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
