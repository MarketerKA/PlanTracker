from jose import jwt
from app import auth, config
import pytest
from fastapi import HTTPException


def test_password_hashing():
    """Test password hashing and verification"""
    password = "testpassword123"
    hashed = auth.get_password_hash(password)

    # Hashed password should be different from original
    assert hashed != password

    # Verification should work
    assert auth.verify_password(password, hashed) is True

    # Wrong password should fail
    assert auth.verify_password("wrongpassword", hashed) is False


def test_token_creation_and_decoding():
    """Test JWT token creation and decoding"""
    # Create token
    user_data = {"sub": "test@example.com"}
    token = auth.create_access_token(data=user_data)

    # Token should be a string
    assert isinstance(token, str)

    # Decode token
    payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])

    # Check payload
    assert payload["sub"] == "test@example.com"
    assert "exp" in payload


def test_authenticate_user_nonexistent(db_session):
    """Test authenticate_user returns None for non-existent user"""
    from app import auth
    user = auth.authenticate_user(db_session, "noone@nowhere.com", "password")
    assert user is None


def test_get_current_user_invalid_token(db_session):
    """Test get_current_user raises for invalid token"""
    from app import auth
    import asyncio
    with pytest.raises(HTTPException):
        asyncio.run(auth.get_current_user(token="invalid.token.here", db=db_session))


def test_get_current_active_user_inactive(db_session, test_user):
    """Test get_current_active_user raises for inactive user"""
    from app import auth, models
    import asyncio
    user = db_session.query(models.User).filter_by(email=test_user["email"]).first()
    user.is_active = False
    db_session.commit()
    with pytest.raises(HTTPException):
        asyncio.run(auth.get_current_active_user(current_user=user))
