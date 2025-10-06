# Frontend Guide

## Overview
The frontend is a Create React App project that renders schedules, must courses, and NTE availability using JSON artifacts produced by the backend. This guide explains project structure, data dependencies, and development workflow.

## Quick Start
```pwsh
cd frontend
npm ci           # install exact dependencies from package-lock
npm start        # launch CRA dev server (defaults to http://localhost:3000)
```

The app expects backend JSON artifacts to be accessible via the `public/data/` folder during development. For production, configure static hosting or environment to point to the published S3 bucket.

## Project Structure
```
frontend/
├── public/
│   ├── data/                 # Development copies of JSON artifacts (optional)
│   └── manifest/static assets
├── src/
│   ├── App.js                # App shell + route orchestration
│   ├── App.css               # Global styles
│   ├── Controls.js/css       # Filters and global controls
│   ├── WeeklyProgram.js/css  # Timetable visualization
│   ├── AddCourseWidget.js    # Course lookup widget
│   ├── slices/               # Redux-style state slices
│   ├── helpers/              # Utility functions (date/time helpers, formatting)
│   └── data/                 # Static metadata used by the UI
├── package.json
└── README.md
```

Key components:
- **`App.js`** – bootstraps global state, loads initial JSON, routes to feature dialogs.
- **`Controls`** – toggles filters (departments, sections, modes).
- **`WeeklyProgram`** – renders weekly timetable grid using loaded schedule data.
- **`AddCourseWidget` / `AddDontFillWidget`** – modals for adding/removing courses or blocking timeslots.
- **`NTEDialog`** – displays elective course availability.

## Data Loading
- JSON endpoints by default originate from the S3 bucket populated by the backend (`cdn.robotdegilim.xyz`).
- During development you can copy snapshots into `frontend/public/data/` and adjust fetch paths accordingly, or configure a proxy to the backend if serving assets locally.
- `src/Client.js` centralizes fetch helpers; adjust base URLs here when changing environments.

## State Management
- Lightweight Redux Toolkit pattern inside `src/slices/` (`scheduleSlice`, `nteSlice`, etc.).
- Components dispatch actions to add/remove courses, toggle settings, or refresh datasets.
- Derived selectors compute filtered schedules and aggregated views.

## Styling & UX
- CSS modules per component (`*.css` co-located with React files).
- Color palettes defined in `Colorset.js` and shared across timetable widgets.
- Dialog components live under `LoadingDialog/`, `WelcomeDialog/`, etc. for consistent UX.

## Testing & Quality
- Run unit tests (CRA defaults): `npm test` (Jest in watch mode).
- Build production bundle: `npm run build` (outputs to `build/`).
- Linting is surfaced by ESLint via CRA; customize rules in `package.json` if needed.

## Environment Configuration
- Create `.env` files (e.g., `.env.development`) to override CRA vars such as:
  - `REACT_APP_DATA_BASE_URL` – base URL for JSON artifacts.
  - `REACT_APP_STATUS_ENDPOINT` – optional status endpoint for in-app health indicators.
- Remember to prefix custom environment variables with `REACT_APP_` to expose them to the client bundle.

## Integration Tips
- When deploying alongside the backend, ensure CORS settings (`ALLOWED_ORIGINS` in backend) allow the frontend domain.
- If serving static files from the same domain as the backend, leverage the `/status` endpoint for in-app health banners.
- Schedule refresh intervals in the frontend thoughtfully to avoid overloading the backend; respect `lastUpdated.json` timestamp to detect new data.

## Deploying the Frontend
1. Run `npm run build`.
2. Deploy the contents of `build/` to your hosting provider (Netlify, Vercel, S3/CloudFront, Fly Static, etc.).
3. Configure environment variables or rewrite rules to direct data fetches to the correct bucket/domain.
4. Optionally enable service worker (`serviceWorker.js`) for offline caching—disabled by default.

## Extending the UI
- Introduce new slices for additional datasets to keep Redux logic cohesive.
- Store API contracts in a dedicated module so fetch logic remains centralized.
- Update documentation (`docs/frontend-guide.md`) when adding major features or environment knobs.
