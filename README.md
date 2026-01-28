# DevOps_Oct2025_Team4_Assignment

React (Vite) frontend + Express backend in a pnpm workspace, with Docker and Prisma.

## Prerequisites
- Node.js 18+
- pnpm (`npm i -g pnpm`)
- Docker Desktop (for local DB/containers)

## Quick Start (local dev)
From the repo root:

```powershell
pnpm run setup
pnpm start
pnpm dev
```

Frontend: http://localhost:5173  
Backend: http://localhost:5000

## One-command Docker + migrations
This builds and starts the server + DB containers, then runs Prisma migrations:

```powershell
pnpm start
```

## Environment variables
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

## Prisma
Create/apply migrations (also generates client):

```powershell
pnpm prisma:migrate
```

Open Prisma Studio:

```powershell
pnpm prisma:studio
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

## Lint
```powershell
pnpm lint
```

## Build
```powershell
pnpm build
```

## Deploy (migrations only)
Production-safe migrations:

```powershell
pnpm deploy
```

## Scripts (summary)
- `pnpm setup` install deps + create `server/.env` if missing
- `pnpm dev` run frontend + backend locally
- `pnpm start` docker up + prisma migrate dev
- `pnpm deploy` prisma migrate deploy

## Tech Stack
Frontend: React + Vite  
Backend: Node.js + Express  
Database: Postgres (local), Supabase (prod)  
ORM: Prisma  
Containerization: Docker + Compose



#Testing Pipeline V7 - Marcus