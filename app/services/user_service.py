from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.user_schemas import UserCreate
from app.services.auth_service import hash_password, verify_password


def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user in the database.

    Args:
        db (Session): Database session
        user (UserCreate): User data to create

    Returns:
        User: Created user object

    Raises:
        ValueError: If username or email already exists
    """
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username, email=user.email, password_hash=hashed_password
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        if "username" in str(e.orig):
            raise ValueError("Username already exists")
        elif "email" in str(e.orig):
            raise ValueError("Email already exists")
        else:
            raise ValueError("User creation failed")


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Get a user by username.

    Args:
        db (Session): Database session
        username (str): Username to search for

    Returns:
        Optional[User]: User object if found, None otherwise
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by email.

    Args:
        db (Session): Database session
        email (str): Email to search for

    Returns:
        Optional[User]: User object if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with username and password.

    Args:
        db (Session): Database session
        username (str): Username to authenticate
        password (str): Plain text password

    Returns:
        Optional[User]: User object if authenticated, None otherwise
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Get a user by ID.

    Args:
        db (Session): Database session
        user_id (int): User ID to search for

    Returns:
        Optional[User]: User object if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()
