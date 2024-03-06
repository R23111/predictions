"""
This module defines the models for tokens used in authentication.

Token:
    Represents an access token with its associated token type.

TokenData:
    Represents the data contained in a token, including the username and role.

"""

from backend.core.base_object import BaseObject


class Token(BaseObject):
    """
    Represents a token used in authentication.

    Attributes:
        access_token (str): The access token value.
        token_type (str): The type of the token.

    """

    access_token: str
    token_type: str


class TokenData(BaseObject):
    """
    Represents the data contained in a token.

    Attributes:
        username (str): The username associated with the token.
        role (str): The role associated with the token.

    """

    username: str
    role: str
