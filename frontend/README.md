# Robot Değilim Frontend

The feature-complete React frontend for building METU schedules. The original interface, color system, section controls, editable course and “don't fill” blocks, NTE flow, save/load support, and exports are preserved.

## Requirements

- Node.js 20.19 or newer (Node.js 24 LTS recommended)
- npm

## Run locally

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

## Checks

```bash
npm test
npm run build
npm run preview
```

## Environment variables

Vite exposes browser settings with a `VITE_` prefix:

```env
VITE_S3_BASE_URL=https://s3.amazonaws.com/cdn.robotdegilim.xyz
VITE_BACKEND_BASE_URL=https://robotdegilim-xyz.fly.dev
VITE_API_TIMEOUT_MS=15000
VITE_SCENARIO_BATCH_SIZE=5000
```

Defaults are provided for the S3 and backend URLs. If the remote course snapshot is unavailable, the client falls back to the repository's bundled course data. Course refreshes use the current backend endpoint: `POST /api/v1/jobs/scrape_courses`.

## Updated platform

- Vite 7 instead of Create React App
- React 18 with `createRoot`
- Material UI 5 compatibility mode, retaining the v4 theme behavior
- DevExpress Scheduler 4
- Redux Toolkit 2 and React Redux 9
- Axios 1
- Vitest 4
