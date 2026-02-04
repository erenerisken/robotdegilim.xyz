# Robotdegilim Frontend

React frontend for building METU schedules from backend-produced JSON snapshots.

## Requirements

- Node.js 18+ (recommended)
- npm

## Setup

From `frontend/`:

```powershell
npm ci
```

## Run (development)

```powershell
npm start
```

App runs on `http://localhost:3000` by default.

## Build (production)

```powershell
npm run build
```

Build output is written to `frontend/build/`.

## Tests

```powershell
npm test
```

## Environment Variables

Create `frontend/.env` (or `.env.development` / `.env.production`) with:

```env
REACT_APP_S3_BASE_URL=https://s3.amazonaws.com/cdn.robotdegilim.xyz
REACT_APP_BACKEND_BASE_URL=https://robotdegilim-xyz.fly.dev
REACT_APP_API_TIMEOUT_MS=15000
```

Notes:

- `REACT_APP_S3_BASE_URL` is used to read:
  - `data.json`
  - `lastUpdated.json`
  - `musts.json`
  - `departments.json`
  - `nteAvailable.json`
  - `status.json`
- `REACT_APP_BACKEND_BASE_URL` is used for `GET /run-scrape`.
- Frontend checks `status.json` first and only triggers scrape when `status === "idle"`.

## Backend Integration Contract

The frontend expects:

- Publicly readable S3 JSON files listed above.
- `status.json` shape:

```json
{
  "status": "idle",
  "updated_at": "2026-02-04T12:34:56Z"
}
```

`status` values used by frontend logic:

- `idle`: scrape trigger allowed
- any other value: scrape trigger skipped

## Useful Files

- `src/Client.js`: all backend/S3 interaction logic
- `src/Controls.js`: triggers data load and scrape update request
- `src/data/Course.js`: data adapters and NTE filtering helpers

