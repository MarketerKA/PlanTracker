def test_create_user(client):
    """Test user creation"""
    response = client.post(
        "/users/", json={"email": "newuser@gmail.com", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "newuser@gmail.com"
    assert "hashed_password" not in data
    assert data["is_active"] is True


def test_create_user_duplicate_email(client, test_user):
    """Test creating user with duplicate email fails"""
    response = client.post(
        "/users/", json={"email": test_user["email"], "password": "anotherpassword"}
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_create_user_invalid_email(client):
    """Test creating user with invalid email fails"""
    response = client.post(
        "/users/", json={"email": "invalid-email", "password": "password123"}
    )
    assert response.status_code == 422
    error_response = response.json()
    assert "email" in str(error_response)
    assert "invalid" in str(error_response).lower()


def test_login_valid_credentials(client, test_user):
    """Test logging in with valid credentials"""
    response = client.post(
        "/users/login",
        json={"email": test_user["email"], "password": test_user["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_user):
    """Test logging in with invalid credentials fails"""
    response = client.post(
        "/users/login", json={"email": test_user["email"], "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_get_user_profile(client, auth_headers):
    """Test getting user profile with valid token"""
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    user = response.json()
    assert "email" in user
    assert "id" in user


def test_get_user_profile_no_token(client):
    """Test getting user profile without token fails"""
    response = client.get("/users/me")
    assert response.status_code == 401


def test_get_telegram_status(client, auth_headers):
    """Test getting telegram status"""
    response = client.get("/users/me/telegram-status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "is_linked" in data
    assert data["is_linked"] is False


def test_unlink_telegram(client, auth_headers):
    """Test unlinking telegram account"""
    response = client.delete("/users/me/telegram", headers=auth_headers)
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "Telegram account not linked" in response.json()["detail"]
