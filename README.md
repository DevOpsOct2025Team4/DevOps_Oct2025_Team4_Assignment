# DevOps_Oct2025_Team4_Assignment

React (Vite) frontend + Express backend in a pnpm workspace.

## Prerequisites
- Node.js 18+ (or newer)
- pnpm installed globally (`npm i -g pnpm`)

## Setup (simple command)
From the repo root:

```powershell
pnpm run setup
```

## Manual setup (optional)
```powershell
pnpm install
Copy-Item server\\.env.example server\\.env
```

## Environment variables
- Server env is loaded from `server/.env`.
- Example env files: `server/.env.example` (server) and `.env.example` (root reference).

## Run in dev mode
Run both frontend and backend:

```powershell
pnpm dev
```

Or run separately:

```powershell
pnpm dev:server
pnpm dev:client
```

Frontend: http://localhost:5173  
Backend: http://localhost:5000

## Lint
Lint all packages:

```powershell
pnpm lint
```

## Build
Build the frontend:

```powershell
pnpm build
```

## Tech Stack
Frontend - React + Vite, Tailwind
Backend - Node.js + Express
Containerization - Docker
Database - Supabase, Prisma
CI/CD - GitHub Actions

## Project Onboarding
