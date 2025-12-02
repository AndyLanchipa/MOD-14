from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import get_db
from app.models.user_model import User
from app.routers import get_current_active_user
from app.schemas.user_schemas import Token, UserCreate, UserRead
from app.services.auth_service import create_access_token
from app.services.user_service import authenticate_user, create_user

router = APIRouter(prefix="/api/users", tags=["users"])
settings = Settings()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Args:
        user (UserCreate): User registration data
        db (Session): Database session

    Returns:
        UserRead: Created user information

    Raises:
        HTTPException: If username or email already exists
    """
    try:
        db_user = create_user(db, user)
        return db_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=Token)
def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """
    Login a user and return access token.

    Args:
        form_data (OAuth2PasswordRequestForm): Login credentials
        db (Session): Database session

    Returns:
        Token: Access token and token type

    Raises:
        HTTPException: If credentials are invalid
    """
    # Validate presence of credentials to return 422 for empty inputs
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username and password are required",
        )

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Get current authenticated user information.

    Args:
        current_user (User): Current authenticated user from token

    Returns:
        UserRead: Current user information
    """
    return current_user
