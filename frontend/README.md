<div align="center">

# Robot Değilim Frontend

React UI for exploring METU course schedules, must courses, and NTE availability using JSON snapshots produced by the backend.

</div>

## Getting Started
```pwsh
npm ci
npm start
```
The CRA dev server typically runs at http://localhost:3000. Configure the backend or static data path in `src/Client.js` (see `docs/frontend-guide.md`).

## Available Scripts
- `npm start` – Run development server with hot reload.
- `npm test` – Launch Jest watch mode.
- `npm run build` – Produce production bundle in `build/`.
- `npm run lint` *(optional)* – If you add custom lint scripts to `package.json`.

## Folder Highlights
- `src/App.js` – App shell and data bootstrapping.
- `src/Controls.js` – Filter and settings panel.
- `src/WeeklyProgram.js` – Timetable renderer.
- `src/slices/` – Redux-style state management.
- `public/data/` – Optional local JSON copies for offline development.

Detailed structure and integration guidance live in `../docs/frontend-guide.md`.

## Environment Variables
Define CRA vars prefixed with `REACT_APP_` to swap endpoints across environments:

- `REACT_APP_S3_BASE_URL` (default: `https://s3.amazonaws.com/cdn.robotdegilim.xyz`)
- `REACT_APP_BACKEND_BASE_URL` (default: `https://robotdegilim-xyz.fly.dev`)
- `REACT_APP_API_TIMEOUT_MS` (default: `15000`)

Create `.env.development` or `.env.production` files as needed.

## Deployment
1. `npm run build`
2. Upload `build/` contents to static hosting (Netlify, Vercel, S3/CloudFront, etc.).
3. Ensure data fetch URLs reference the published backend artifacts.

## Contributing
- Update documentation when adding screens or environment knobs.
- Add tests under `src/` alongside components or slices.
- Coordinate with backend team on JSON schema changes.
