# robotdegilim-frontend

React application (Create React App) that consumes published JSON artifacts (courses, departments, musts, status) produced by the backend and renders schedule & course exploration UI.

## Features
- Weekly schedule visualization
- Course / section detail cards
- Add / remove courses interaction
- Export calendar (ICS) functionality
- Advanced settings + musts integration

## Prerequisites
- Node.js 18+ (LTS recommended)
- npm 9+ (or enable `corepack` + use yarn/pnpm if you adapt lockfiles)

## Install & Run (Development)
```bash
cd frontend
npm ci        # installs from package-lock.json
npm start     # launches CRA dev server (hot reload)
```
Open the printed local URL (often http://localhost:3000). If backend runs on another port, set a proxy in `package.json` or use full URLs in fetches.

## Build (Production)
```bash
npm run build
```
Outputs static assets to `build/`. Serve via any static host (Netlify, Vercel, S3+CloudFront, Nginx). The app expects the JSON artifacts (e.g. `data.json`, `musts.json`, `departments.json`, `lastUpdated.json`, `status.json`) to be publicly reachable.

## Environment / Configuration
This frontend currently relies on hardcoded or relative fetch paths. If you introduce environment variables:
- Use CRA pattern: define `REACT_APP_*` variables in a `.env` file (e.g. `REACT_APP_API_BASE`) before running `npm start`.
- Never commit secrets; frontend bundles are fully public.

Example `.env` (frontend):
```
REACT_APP_API_BASE=https://api.robotdegilim.xyz
REACT_APP_CDN_BASE=https://cdn.robotdegilim.xyz
```
Use them in code: `process.env.REACT_APP_API_BASE`.

## Testing
```bash
npm test
```
Runs Jest + React Testing Library in watch mode.

## Linting / Formatting
If you want to add linting:
1. `npm install --save-dev eslint prettier eslint-config-prettier eslint-plugin-react`
2. Add an `.eslintrc` and run `npx eslint src`.
(Current repo does not include an ESLint config yet.)

## Deployment Tips
- Ensure backend publishes new snapshots before redeploying frontend if you rely on freshly generated data.
- Configure proper cache headers (e.g., long cache for content-hashed assets, short for JSON if served via same CDN).

## Future Improvements (Ideas)
- Convert to Vite for faster dev build times.
- Add ESLint + Prettier config.
- Introduce a lightweight state manager (Zustand / Redux Toolkit) if state complexity grows.
- Implement offline caching strategy for JSON artifacts.

## Contributing
1. Keep components small and focused.
2. Prefer functional components + hooks.
3. Keep styling in CSS modules / plain CSS (current pattern) unless migrating.
4. Update this README if build or env patterns change.

## License
MIT (see root `LICENSE`).
