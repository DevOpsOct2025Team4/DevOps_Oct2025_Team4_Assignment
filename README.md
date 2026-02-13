# DevOps_Oct2025_Team4_Assignment

React (Vite) frontend + Flask backend with Postgres. Docker is used for the server and database.

## Clone and Setup (Local Dev)

Prerequisites:

- Node.js 18+
- pnpm (via `corepack` or `npm i -g pnpm`)
- Python 3.12+
- Docker Desktop

Steps:

1. `git clone <repo-url>`
2. `cd DevOps_Oct2025_Team4_Assignment`
3. `pnpm run setup`
4. `pnpm dev`

What `pnpm run setup` does:

- Installs Node.js dependencies
- Creates `server/.env` and `client/.env` from the example files (if missing)
- Installs Python dependencies
- Builds Docker images

Local URLs:

- Frontend: http://localhost:5173
- Backend: http://127.0.0.1:5000

## Common Commands

- `pnpm dev` Starts local DB, runs migrations, and runs backend + frontend
- `pnpm dev:client` Runs frontend only
- `pnpm dev:server` Runs backend only
- `pnpm start` Builds and starts backend + DB containers (Docker)
- `pnpm create-local-db` Starts DB container only
- `pnpm create-docker` Starts backend + DB containers
- `pnpm migrate` Autogenerates + applies Alembic migrations (Docker)
- `pnpm lint` Lints frontend and backend
- `pnpm test` Runs backend pytest + Robot tests
- `pnpm build` Builds the frontend
- `pnpm dbstudio` Starts Adminer at http://localhost:8080

## Environment Variables

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

## CI/CD Pipeline

### Workflow Map

- `Push CI (Shallow)` runs on pushes to non-main/develop branches and executes common CI
- `PR CI (Deep)` runs on PRs to `develop`/`main` and on pushes to `main`
- `PR Security` runs SAST and SCA on PRs to `develop`
- `Staging Testing & Release Candidate` runs on pushes to `develop` and includes staging checks, migrations, tests, DAST, and RC drafting
- `K8s Smoke Test` runs on pushes to `develop` or manual dispatch and deploys to a kind cluster for smoke tests
- `Deploy Staging` is a manual workflow with a placeholder deploy command
- `Post Merge Security` runs on pushes to `main` (CodeQL + Semgrep)
- `Promote Release Candidate` runs when a release with a `-rc.N` tag is published
- `Main Guard` enforces that only `develop -> main` PRs are allowed

### Pipeline Setup (GitHub Actions)

1. Create GitHub Environments named `staging` and `review`.
2. Add secrets and variables (tables below). Prefer environment-level values for `staging` and `review`.
3. Configure branch protections for `main` and require PRs. `main-guard.yml` enforces `develop -> main` only.
4. Ensure GitHub Actions is enabled for the repository.

### Required Secrets

| Name                        | Used By               | Notes                                   |
| --------------------------- | --------------------- | --------------------------------------- |
| `SUPABASE_URL`              | `k8s-smoke.yml`       | Required for K8s smoke tests            |
| `SUPABASE_SERVICE_ROLE_KEY` | `k8s-smoke.yml`       | Required for K8s smoke tests            |
| `SUPABASE_DIRECT`           | `k8s-smoke.yml`       | Optional (only if used by your backend) |
| `STAGING_DATABASE_URL`      | `staging_testing.yml` | Required for Alembic migrations         |
| `ROBOT_USERNAME`            | `staging_testing.yml` | Required for Robot tests                |
| `ROBOT_PASSWORD`            | `staging_testing.yml` | Required for Robot tests                |
| `ROBOT_ADMIN_USERNAME`      | `staging_testing.yml` | Required for Robot tests                |
| `ROBOT_ADMIN_PASSWORD`      | `staging_testing.yml` | Required for Robot tests                |
| `ZAP_USERNAME`              | `dast-zap-auth.yml`   | Required for authenticated ZAP scan     |
| `ZAP_PASSWORD`              | `dast-zap-auth.yml`   | Required for authenticated ZAP scan     |
| `DISCORD_WEBHOOK`           | `staging_testing.yml` | Approval notifications                  |
| `DISCORD_WEBHOOK_DEV`       | `staging_testing.yml` | Build failure notifications             |
| `DISCORD_WEBHOOK_DEVOPS`    | `staging_testing.yml` | Deploy success/failure notifications    |
| `DISCORD_WEBHOOK_BACKEND`   | `staging_testing.yml` | Migration and smoke notifications       |
| `DISCORD_WEBHOOK_QA`        | `staging_testing.yml` | Security and integration notifications  |

### Required Variables (staging environment)

| Name                   | Used By                                    | Notes                                                               |
| ---------------------- | ------------------------------------------ | ------------------------------------------------------------------- |
| `STAGING_URL`          | `staging_testing.yml`, `dast-zap-auth.yml` | Base URL for API health checks (e.g. `https://staging.example.com`) |
| `STAGING_WEBSITE_URL`  | `staging_testing.yml`, `dast-zap-auth.yml` | Base URL for UI tests (e.g. `https://staging.example.com`)          |
| `ZAP_USERNAME_FIELD`   | `dast-zap-auth.yml`                        | JSON field name for username/email                                  |
| `ZAP_PASSWORD_FIELD`   | `dast-zap-auth.yml`                        | JSON field name for password                                        |
| `ZAP_LOGGED_IN_REGEX`  | `dast-zap-auth.yml`                        | Regex that indicates a logged-in response                           |
| `ZAP_LOGGED_OUT_REGEX` | `dast-zap-auth.yml`                        | Regex that indicates a logged-out response                          |

### Execute the Pipeline

1. Feature branch push triggers `Push CI (Shallow)`.
2. Open a PR into `develop` to trigger `PR CI (Deep)` and `PR Security`.
3. Merge into `develop` to trigger `Staging Testing & Release Candidate`.
4. Approve the manual checkpoint in the `review` environment.
5. A draft RC release is created with a tag like `vX.Y.Z-rc.N`.
6. Publish the RC release to trigger `Promote Release Candidate`, which merges `develop` into `main` and tags `vX.Y.Z`.
7. Optional manual runs: use Actions -> Run workflow for `Deploy Staging` (provide the `ref` input) and `K8s Smoke Test`.

Notes:

- `deploy-staging.yml` has a placeholder command and must be replaced with your staging deploy command.
- `staging_testing.yml` only validates staging health and SHA; it assumes deployment has already occurred.

## Observability

See `OBSERVABILITY.md` for dashboards and metrics.
