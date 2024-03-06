from typing import Any
import pytest
from backend.services.authentication import encrypt_password
import bcrypt


# Parametrized test for happy path with various realistic test values
@pytest.mark.parametrize(
    "test_input, test_id",
    [
        ("simplepassword", "HP1"),
        ("12345678", "HP2"),
        ("P@ssw0rd!", "HP3"),
        ("longpassword" * 5, "HP4"),
        ("short", "HP5"),
    ],
)
def test_encrypt_password_happy_path(test_input: str, test_id: Any) -> None:
    # Act
    encrypted_password = encrypt_password(test_input)

    # Assert
    assert bcrypt.checkpw(test_input.encode("utf-8"), encrypted_password.encode("utf-8")), f"Test ID: {test_id}"


# Parametrized test for error cases
# Note: bcrypt does not raise errors for any string input, so there are no traditional error cases.
# However, we can test for incorrect usage such as passing non-string types.
@pytest.mark.parametrize(
    "test_input, expected_exception, test_id",
    [
        (None, TypeError, "EC1"),  # None input
        (12345, TypeError, "EC2"),  # Integer input
        (["password"], TypeError, "EC3"),  # List input
        ({"password": "password"}, TypeError, "EC4"),  # Dict input
    ],
)
def test_encrypt_password_error_cases(test_input: str, expected_exception: Any, test_id: Any) -> None:
    # Assert
    with pytest.raises(expected_exception):
        # Act
        encrypt_password(test_input)
