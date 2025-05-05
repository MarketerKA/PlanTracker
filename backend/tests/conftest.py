import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine)

# Create test database and tables
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Returns a SQLAlchemy session for testing.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    # Clean up
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a FastAPI TestClient that uses the db_session fixture.
    """
    # Override the get_db dependency to use our test database
    def override_get_db():
        try:
            yield db_session
        except Exception as e:
            print(f"Error in db_session: {e}")
            raise e

    # Apply the overrides
    app.dependency_overrides[get_db] = override_get_db

    # Mock the Telegram bot functions to prevent them from being called
    with patch("app.telegram_bot.start_bot"), \
            patch("app.telegram_bot.stop_bot"):
        # Create the test client
        with TestClient(app) as client:
            yield client

    # Clean up
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
def test_user(client):
    """
    Create a test user and return user data
    """
    user_data = {
        "email": "testuser@gmail.com",
        "password": "testpassword123"
    }

    # Create test user
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201

    return {"email": user_data["email"], "password": user_data["password"]}


@pytest.fixture(scope="function")
def auth_headers(client, test_user):
    """
    Get auth headers for the test user
    """
    response = client.post(
        "/users/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def test_activity(client, auth_headers):
    """
    Create a test activity and return it
    """
    activity_data = {
        "title": "Test Activity",
        "description": "Test Description",
        "tags": ["test", "pytest"]
    }

    response = client.post(
        "/activities/",
        json=activity_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    return response.json()
