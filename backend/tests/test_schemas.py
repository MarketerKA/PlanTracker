import pytest
from app.schemas import UserBase


def test_userbase_email_validator_forbidden_domain():
    with pytest.raises(ValueError):
        UserBase(email="user@example.com")


def test_userbase_email_validator_invalid_email():
    with pytest.raises(ValueError):
        UserBase(email="not-an-email")
