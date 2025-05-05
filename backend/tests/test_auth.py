from jose import jwt
from app import auth, config


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
