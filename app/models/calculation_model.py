from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    type = Column(String(20), nullable=False)  # ADD, SUB, MULTIPLY, DIVIDE
    result = Column(Float, nullable=True)  # Store result or compute on demand
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to User model
    user = relationship("User", back_populates="calculations")

    def __repr__(self):
        return (
            f"<Calculation(id={self.id}, a={self.a}, b={self.b}, "
            f"type='{self.type}', result={self.result})>"
        )

    def calculate_result(self):
        """Calculate and return the result based on operation type"""
        if self.type == "ADD":
            return self.a + self.b
        elif self.type == "SUB":
            return self.a - self.b
        elif self.type == "MULTIPLY":
            return self.a * self.b
        elif self.type == "DIVIDE":
            if self.b == 0:
                raise ValueError("Division by zero is not allowed")
            return self.a / self.b
        else:
            raise ValueError(f"Unsupported operation type: {self.type}")

    def save_result(self):
        """Calculate and store the result in the database"""
        self.result = self.calculate_result()
        return self.result
