# EvoPay AI Project Audit

Date: 2026-08-26

## 1. Current Architecture

- `frontend/` is a Vite React TypeScript app with Framer Motion, Recharts, Lucide React, and Tailwind CSS.
- `backend/` is a FastAPI app using the stdlib `sqlite3` module and Pydantic request schemas.
- `backend/services/` contains deterministic `risk_engine.py`, `attack_engine.py`, and `investigator.py` services.
- Client routing is a lightweight browser-history router in `frontend/src/App.tsx`.
- SQLite is initialized by `backend/database.py` and stores synthetic customers, merchants, devices, transactions, attacks, incidents, patterns, simulations, and audit events.

## 2. Working Features

- FastAPI health, dashboard, transaction, attack, network, simulation, incident, analytics, threat-library, and investigation route definitions exist.
- CORS includes local Vite origins.
- Deterministic risk scoring combines ML-style, behavioral, anomaly, and graph heuristics.
- Deterministic attack generation/evolution supports ten attack families and can create `DEFENSE BLIND SPOT` patterns.
- Investigator returns explanation-only reports and does not execute payment actions.
- Command Center, Red Team Lab, Blue Team, Fraud Network, Adversarial Arena, and Demo Mode have substantial local UI flows.
- TypeScript/Python source diagnostics and Python compilation have passed during prior implementation work.

## 3. Broken or Disconnected Features

- Frontend transaction actions update local React state but do not call `POST /api/transactions/{id}/action`.
- Red Team generation/evolution calls API endpoints, but its generated attack state and backend persistence are not fully synchronized.
- Simulation is currently a frontend-only timer and does not start or poll the FastAPI simulation API.
- Network visualization uses hardcoded nodes and edges rather than `/api/network`; frontend/backend IDs differ.
- Blue Team mitigation/adaptation is local UI state and does not call backend action/adaptation endpoints.
- `/transactions`, `/incidents`, `/analytics`, and `/settings` still render generic placeholder states.
- Backend routes mostly return untyped `dict`/`list[dict]` values rather than response models.
- SQLite seed logic is not independently idempotent per table and has no migration/version tracking.
- No backend or frontend automated tests exist.
- Dependencies are not pinned and frontend has no committed lockfile.
- Direct production refreshes on client-side routes require SPA fallback configuration.

## 4. Missing Features

- Reproducible 100,000-row synthetic dataset pipeline.
- Shared feature engineering between training and inference.
- Persisted trained fraud and anomaly models with evaluation metrics.
- NetworkX graph risk computation in the backend.
- Attack generations table and model versions table.
- Server-backed full simulation with generated attack transactions, detection, incidents, blind spots, adaptation, and re-test comparison.
- Incident lifecycle actions and audit-trail UI.
- Loading/error states for API-backed page flows.
- Environment examples and production deployment instructions.
- At least ten meaningful backend tests and a frontend production build verification.

## 5. Required Fixes

1. Stabilize SQLite schema, migrations, and idempotent synthetic seeding.
2. Add typed backend response models and complete server-side action/simulation/adaptation flows.
3. Add a deterministic ML-compatible pipeline using a reproducible synthetic dataset, with lightweight fallbacks if optional packages are unavailable.
4. Route every interactive UI action through the API while keeping local demo fallbacks.
5. Replace placeholder routes with functional data-backed pages.
6. Add loading, error, retry, and offline synthetic-data states.
7. Add backend tests, frontend build checks, environment examples, and deployment documentation.
8. Validate local startup, API routes, database creation, and the three-minute demo flow; mark any environment-blocked checks as not verified.
