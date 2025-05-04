 # PlanTracker

A full-stack application for tracking and managing tasks and activities.

## Project Structure

```
PlanTracker/
├── frontend/          # React + TypeScript frontend
│   ├── src/          # Source code
│   ├── public/       # Static files
│   └── package.json  # Frontend dependencies
│
└── backend/          # FastAPI backend
    ├── app/          # Application code
    ├── tests/        # Test files
    └── pyproject.toml # Backend dependencies
```

## Prerequisites

- Node.js (v16 or higher)
- Python 3.9 or higher
- Poetry (Python package manager)
- Git

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
poetry install
```

3. Create a `.env` using `.env.example` file.

4. Run the backend server:
```bash
poetry run uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Development

### Backend Development

- API Documentation: `http://localhost:8000/docs`
- Run tests: `poetry run pytest`
- Linting: `poetry run flake8`

### Frontend Development

- Development server: `npm run dev`
- Build: `npm run build`
- Linting: `npm run lint`

## Environment Variables

### Backend (.env)
- `SECRET_KEY`: JWT secret key
- `TELEGRAM_BOT_TOKEN`: Token for Telegram bot

### Frontend (.env)
- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
