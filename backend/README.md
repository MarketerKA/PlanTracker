# PlanTracker Backend

env

SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MAIL_USERNAME=youremail@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=youremail@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME=PlanTracker App
FRONTEND_URL=http://localhost:3000
VERIFICATION_URL_BASE=http://localhost:8000 

This is the backend service for the PlanTracker application, built with FastAPI and SQLite.

## Features

- User authentication with JWT tokens
- Activity tracking with start/end times
- Tag management
- Pagination support
- CORS enabled for frontend integration

## Prerequisites

- Python 3.9 or higher
- Poetry (Python package manager)

## Setup

1. Install Poetry if you haven't already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Clone the repository and navigate to the backend directory:
```bash
cd backend
```

3. Install dependencies:
```bash
poetry install
```

4. Activate the virtual environment:
```bash
poetry shell
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Development

### Running Tests
```bash
poetry run pytest
```

### Linting
```bash
poetry run flake8
```

### Adding New Dependencies
```bash
poetry add <package-name>  # For production dependencies
poetry add --group dev <package-name>  # For development dependencies
```

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Authentication

All endpoints except `/users/` and `/token` require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

### Endpoints

#### Users
- `POST /users/` - Register a new user
- `POST /token` - Get JWT token for authentication

#### Activities
- `POST /activities/` - Create a new activity
- `GET /activities/` - List activities (paginated)
- `PUT /activities/{activity_id}` - Update an activity
- `DELETE /activities/{activity_id}` - Delete an activity

#### Tags
- `POST /tags/` - Create a new tag
- `GET /tags/` - List tags (paginated)

## Development Guidelines

- Follow PEP 8 style guide
- Run flake8 for linting
- Write tests for new features
- Update API documentation when adding new endpoints
- Use Poetry for dependency management 