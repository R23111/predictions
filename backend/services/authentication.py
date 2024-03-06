"""
This module provides functions for password hashing, authentication token generation, and token decoding.

It utilizes bcrypt for secure password hashing, the jose library for JWT token handling, and settings from the application configuration.

**Key Functions:**

- `encrypt_password`: Hashes a plaintext password using bcrypt.
- `check_password`: Verifies a password against a hashed password using bcrypt.
- `generate_token`: Creates a JWT authentication token with user information and an expiration time.
- `decode_token`: Decodes a JWT authentication token and extracts its payload.
"""

from datetime import datetime, timedelta
from datetime import timezone
from typing import Any

import bcrypt
from jose import jwt, JWTError
from starlette import status
from starlette.exceptions import HTTPException

from backend.core.config import settings


def encrypt_password(password: str) -> str:
    """
    Encrypts a password using bcrypt hashing algorithm.

    Args:
        password (str): The password to be encrypted.

    Returns:
        str: The encrypted password.

    """
    if not isinstance(password, str):
        raise TypeError(f"Password must be a string, not {str(type(password))}")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    """
    Checks if a password matches a hashed password using bcrypt hashing algorithm.

    Args:
        password (str): The password to be checked.
        hashed (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches the hashed password, False otherwise.

    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def generate_token(username: Any, is_admin: bool, expires_delta: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    """
    Generates a JSON Web Token (JWT) for authentication.

    Args:
        username (str): The username of the user.
        role (str): The role of the user.
        expires_delta (int, optional): The expiration time of the token in minutes. Defaults to settings.ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        str: The generated JWT.

    """
    role = "admin" if is_admin else "user"
    data: dict = {"user": username, "role": role}
    expires: datetime = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    data |= {"exp": expires}

    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decodes a JSON Web Token (JWT) and returns the payload as a dictionary.

    Args:
        token (str): The JWT to decode.

    Returns:
        dict: The decoded payload of the JWT.

    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
