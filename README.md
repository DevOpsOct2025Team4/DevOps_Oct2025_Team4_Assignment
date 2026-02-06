# DevOps_Oct2025_Team4_Assignment

React (Vite) frontend + Flask backend, with Docker for the server and database.

## Prerequisites

- Node.js 18+
- pnpm (`npm i -g pnpm`)
- Docker Desktop (for backend containers)

## Quick Start (local dev)

From the repo root:

```powershell
pnpm run setup
pnpm dev
```

What `pnpm dev` does:

- Starts the local Postgres container (`pnpm create-local-db`)
- Runs Alembic migrations (autogenerate + upgrade)
- Runs backend + frontend locally

Frontend: http://localhost:5173
Backend (local): http://127.0.0.1:5000

## Start backend containers (Docker)

This builds and starts the server + DB containers and runs Alembic migrations on container start:

```powershell
pnpm start
```

## Environment variables

- Client env file: `client/.env`
- Example: `client/.env.example`
- `VITE_API_BASE_URL` should include the `/api` prefix (example: `http://127.0.0.1:5000/api`)

- Server env file: `server/.env`
- Example: `server/.env.example`

Server database and storage:

- `DATABASE_URL` is required (local Postgres or Supabase Postgres)
- `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` are required for auth + file storage
- `SUPABASE_BUCKET` (default: `UserUploads`)

Local DB (host machine) default:

```
DATABASE_URL=postgres://app:app@localhost:5432/app
```

When the server runs inside Docker via compose, it should use:

```
postgres://app:app@db:5432/app
```

## Docker

Start DB only:

```powershell
pnpm create-local-db
```

Start server only:

```powershell
pnpm create-docker-server
```

Start both:

```powershell
pnpm create-docker
```

## DB Studio (web UI)

Start the Adminer web UI:

```powershell
pnpm dbstudio
```

Open http://localhost:8080 and connect with:

- System: PostgreSQL
- Server: db
- Username: app
- Password: app
- Database: app

## Lint

```powershell
pnpm lint
```

## Build

```powershell
pnpm build
```

## Deploy (migrations)

- Docker: migrations run on container start via `server/entrypoint.sh`
- Local dev: `pnpm dev` runs `pnpm migrate` before starting services

## Scripts (summary)

- `pnpm setup` install deps, create env files, build Docker images
- `pnpm dev` start local DB, run migrations, run backend + frontend
- `pnpm dev:client` run frontend only
- `pnpm dev:server` run backend only
- `pnpm start` start backend + DB containers (Docker)
- `pnpm migrate` autogenerate + apply migrations (Docker)

## Tech Stack

Frontend: React + Vite
Backend: Python + Flask
Database: Postgres (local or Supabase Postgres)
Storage/Auth: Supabase
Containerization: Docker + Compose
Migrations: Alembic

#Testing Pipeline V12 - Marcus
