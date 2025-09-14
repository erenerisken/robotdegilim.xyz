# Robot Değilim

A full-stack project with a Python/Flask backend and a React frontend. The backend scrapes and publishes data to S3; the frontend consumes public JSON endpoints and provides a UI.

## Project Structure

- `backend/`: Flask REST API and scraping logic
- `frontend/`: React app (Create React App)

## Quick Start

### Backend

- Requirements: Python 3.12+
- Install dependencies:

```
python -m venv backend/.venv
backend/.venv/Scripts/Activate.ps1   # PowerShell (Windows)
# source backend/.venv/bin/activate  # Bash (macOS/Linux)
python -m pip install -r backend/requirements.txt
```

- Environment variables: copy `backend/.env.example` to `.env` (or set in your shell) and provide values for mail + AWS credentials.

- Run (example):
```
python -m flask --app backend/src/app run --port 3000
```

### Frontend

- Requirements: Node.js 18+
- Install and start:
```
cd frontend
npm ci
npm start
```
- Build production assets: `npm run build`

## Deployment Notes

- Backend writes artifacts to S3 bucket configured via env vars.
- Frontend reads public JSON from S3 and calls the backend’s `/run-scrape` endpoint.

## Environment Variables

See `backend/.env.example` for expected variables:
- `MAIL_USERNAME`, `MAIL_PASSWORD`
- `ACCESS_KEY`, `SECRET_ACCESS_KEY`

## Packaging (Backend)

Python packaging uses setuptools with `src/` layout.

## License

See `LICENSE`.