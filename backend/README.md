# Backend: FastAPI + SQLite

A robust backend service for the PlanTracker application, built with FastAPI and SQLite.

**Live Demo:** [http://158.160.23.164/](http://158.160.23.164/)

## Features
- User authentication with JWT tokens
- Activity tracking with start/end times
- Tag management
- Pagination support
- CORS enabled for frontend integration

## Prerequisites
- Python 3.9+
- Poetry (Python package manager)

## Setup
1. Install Poetry:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
2. Navigate to the backend directory:
   ```bash
   cd backend
   ```
3. Install dependencies:
   ```bash
   poetry install
   ```
4. Create a `.env` file:
   ```env
   SECRET_KEY=
   TELEGRAM_BOT_TOKEN=
   ```
5. Run the application:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```
   The API will be available at [http://localhost:8000](http://localhost:8000).

## Development
- **Tests:** `poetry run pytest`
- **Linting:** `poetry run flake8`

## API Documentation
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Authentication
All endpoints except `/users/` and `/users/login` require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

### Endpoints
#### Users
- `POST /users/` - Create a new user
- `POST /users/login` - Login a user
- `GET /users/me` - Get current user

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