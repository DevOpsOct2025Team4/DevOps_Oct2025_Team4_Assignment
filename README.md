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
pnpm start
pnpm dev
```

Frontend: http://localhost:5173
Backend (Docker): http://localhost:5000

## Start backend containers

This builds and starts the server + DB containers and runs Alembic migrations:

```powershell
pnpm start
```

## Environment variables

- Client env file: `client/.env`
- Example: `client/.env.example`
- `VITE_API_BASE_URL` should include the `/api` prefix (example: `http://localhost:5000/api`)

- Server env file: `server/.env`
- Example: `server/.env.example`

Local DB (host machine) default:

```
DATABASE_URL=postgres://app:app@localhost:5432/app
```

When the server runs inside Docker via compose, it uses:

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

## Deploy (migrations only)

Not applicable (migrations run on container start).

## Scripts (summary)

- `pnpm setup` install frontend deps, create env files, build Docker images
- `pnpm dev` run frontend only
- `pnpm start` start backend + DB containers

## Tech Stack

Frontend: React + Vite
Backend: Python + Flask
Database: Postgres (local), Supabase (prod)
Containerization: Docker + Compose
Migrations: Alembic

#Testing Pipeline V7 - Marcus
#Testing Pipeline V9 - Marcus
