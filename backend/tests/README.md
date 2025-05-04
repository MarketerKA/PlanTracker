# PlanTracker Backend Tests

This directory contains automated tests for the PlanTracker backend application.

## Running Tests

From the `backend` directory, run:

```bash
poetry run pytest tests/ -v
```

To run tests with coverage report:

```bash
poetry run pytest tests/ --cov=app --cov-report=term --cov-report=html -v
```

This will generate a coverage report in the terminal and a detailed HTML report in the `htmlcov` directory.

## Test Structure

- `conftest.py`: Contains pytest fixtures for database, client, authentication, and test data
- `test_users.py`: Tests for user registration, authentication, and profile management
- `test_activities.py`: Tests for activity creation, retrieval, modification, and timer operations
- `test_tags.py`: Tests for tag creation and retrieval
- `test_auth.py`: Tests for authentication module

## CI Integration

These tests are designed to be run in a CI/CD environment, targeting the minimum 70% code coverage requirement specified in the project requirements.