"""
This module defines the models for user-related operations.

UserCreate:
    Represents the data required to create a new user.

UserUpdate:
    Represents the data that can be updated for a user.

UserRead:
    Represents the data returned when reading a user.

User:
    Represents a user in the system with its associated attributes.

"""

from sqlmodel import Field, SQLModel

from backend.core.base_object import BaseObject


class UserCreate(BaseObject):
    username: str
    password: str
    is_admin: bool = False


class UserUpdate(BaseObject):
    username: str | None = None
    password: str | None = None
    is_admin: bool | None = None


class UserRead(BaseObject):
    id: int
    username: str
    is_admin: bool


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    password: str
    is_admin: bool


class UserView(BaseObject):
    success: bool
    is_admin: bool
    username: str
