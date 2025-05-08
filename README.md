# PlanTracker

A full-stack web application for tracking and managing tasks and activities.

**Live Demo:** [http://158.160.23.164/](http://158.160.23.164/)

---

## Project Overview

- **Frontend:** React + TypeScript
- **Backend:** FastAPI (Python)

```
PlanTracker/
├── frontend/   # React + TypeScript app
├── backend/    # FastAPI app
```

---

## Prerequisites
- Node.js v16+
- Python 3.9+
- Poetry (Python package manager)
- Git

---

## Getting Started

### Backend
1. Go to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Copy `.env.example` to `.env` and update as needed.
4. Start the backend server:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```
   - API: [http://localhost:8000](http://localhost:8000)
   - Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Frontend
1. Go to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   - App: [http://localhost:3000](http://localhost:3000)

---

## Development & Testing

### Backend
- Run tests: `poetry run pytest`
- Lint: `poetry run flake8`

### Frontend
- Lint: `npm run lint`
- Build: `npm run build`

---

## Environment Variables

### Backend (`.env`)
- `SECRET_KEY`: JWT secret key
- `TELEGRAM_BOT_TOKEN`: Telegram bot token

### Frontend (`.env`)
- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)

---

## Container Security

Container security scanning is integrated in CI/CD:
- **Trivy**: Docker/image vulnerability scanning
- **Snyk**: Dependency and image scanning
- **Docker Scout**: Security insights

See [CONTAINER_SCANNING.md](CONTAINER_SCANNING.md) for details.

---

## Contributing
1. Fork the repo
2. Create a feature branch
3. Commit and push your changes
4. Open a Pull Request

---

## License
MIT License. See `LICENSE` for details.
