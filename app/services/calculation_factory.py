from typing import Protocol


class CalculationOperation(Protocol):
    """Protocol defining the interface for calculation operations"""

    def calculate(self, a: float, b: float) -> float:
        """Perform the calculation operation"""
        ...


class AddOperation:
    """Addition operation implementation"""

    def calculate(self, a: float, b: float) -> float:
        return a + b


class SubOperation:
    """Subtraction operation implementation"""

    def calculate(self, a: float, b: float) -> float:
        return a - b


class MultiplyOperation:
    """Multiplication operation implementation"""

    def calculate(self, a: float, b: float) -> float:
        return a * b


class DivideOperation:
    """Division operation implementation"""

    def calculate(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        return a / b


class CalculationFactory:
    """Factory class for creating calculation operations"""

    _operations = {
        "ADD": AddOperation(),
        "SUB": SubOperation(),
        "MULTIPLY": MultiplyOperation(),
        "DIVIDE": DivideOperation(),
    }

    @classmethod
    def get_operation(cls, operation_type: str) -> CalculationOperation:
        """Get the appropriate operation instance for the given type"""
        operation = cls._operations.get(operation_type)
        if not operation:
            raise ValueError(f"Unsupported operation type: {operation_type}")
        return operation

    @classmethod
    def calculate(cls, a: float, b: float, operation_type: str) -> float:
        """Perform calculation using the factory pattern"""
        operation = cls.get_operation(operation_type)
        return operation.calculate(a, b)

    @classmethod
    def get_supported_operations(cls) -> list:
        """Return list of supported operation types"""
        return list(cls._operations.keys())

    @classmethod
    def is_operation_supported(cls, operation_type: str) -> bool:
        """Check if an operation type is supported"""
        return operation_type in cls._operations
