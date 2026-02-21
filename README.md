# Meeting Memo Tracker

AI-powered meeting management: paste or upload a transcript, get a structured summary, tracked decisions, and action items — all in one multi-tenant workspace.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![Next.js](https://img.shields.io/badge/Next.js-15-black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Tests](https://img.shields.io/badge/tests-68%20passing-brightgreen)

---

## Features

- **AI summaries** — GPT-4o extracts management summary, decisions, action items, risks, next agenda, and a follow-up email draft from any meeting transcript
- **Meeting versioning** — every AI generation is saved as a version; approve to lock it
- **Action item tracker** — Kanban board (drag-and-drop) + table view; filter by status, priority, owner, due date
- **Full-text search** — PostgreSQL `TSVECTOR` search across meeting content
- **PII redaction** — strip emails and UK phone numbers before saving
- **File upload** — `.txt` / `.docx` transcripts; optional S3 storage
- **Multi-tenant** — Organisations → Teams → Members with role-based access (`org_admin`, `team_admin`, `member`)
- **Tags & categories** — Work / Home / Private with free-form tags
- **JWT auth** — access + refresh tokens in `httpOnly` cookies

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, shadcn/ui, Tailwind CSS, React Query 5, dnd-kit |
| Backend | FastAPI 0.115, SQLAlchemy 2.0 async, Alembic, Pydantic v2 |
| Database | PostgreSQL 16 (TSVECTOR, ARRAY, UUID) |
| AI | OpenAI GPT-4o (two-pass JSON → Markdown pipeline) |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Infra | Docker Compose (3 containers), optional AWS S3 |

---

## Quick Start

### Prerequisites
- Docker Desktop (with Compose v2)
- An OpenAI API key (GPT-4o)

### 1. Copy and configure environment files

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
```

Edit `apps/api/.env` and set:
- `SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- `OPENAI_API_KEY` — your OpenAI key

### 2. Build and start all services

```bash
make build
make up
```

### 3. Run database migrations

```bash
make migrate
```

### 4. Seed demo data

```bash
make seed
```

### 5. Open the app

```
http://localhost:3000
```

---

## Demo Credentials

| User | Email | Password | Role |
|------|-------|----------|------|
| Admin User | admin@acme-demo.com | demo1234 | Org Admin |
| Alice Smith | alice@acme-demo.com | demo1234 | Member |
| Bob Jones | bob@acme-demo.com | demo1234 | Team Admin |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Docker Compose                          │
│                                                                  │
│  ┌──────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │          │    │                  │    │                  │  │
│  │ Postgres │◄───│  FastAPI (api)   │◄───│ Next.js (web)    │  │
│  │   :5432  │    │     :8000        │    │     :3000        │  │
│  │          │    │                  │    │                  │  │
│  └──────────┘    │ • JWT auth       │    │ • App Router     │  │
│                  │ • SQLAlchemy 2.0 │    │ • shadcn/ui      │  │
│                  │ • Alembic        │    │ • React Query    │  │
│                  │ • OpenAI gpt-4o  │    │ • dnd-kit        │  │
│                  │ • SlowAPI        │    │                  │  │
│                  └──────────────────┘    └──────────────────┘  │
│                                                                  │
│  ┌─────────────────────────────────────┐                       │
│  │  ./data/uploads (mounted volume)     │                       │
│  └─────────────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

### Data Model

```
Organisation
  └── Teams (1..n)
  └── Users (1..n)
        └── UserTeams (join table)

Meeting
  ├── category: work | home | private
  ├── tags: string[]
  ├── transcript_text
  ├── search_vector (TSVECTOR — full-text search)
  ├── MeetingVersions (1..n)
  │     ├── ai_output_json
  │     └── rendered_markdown
  └── ActionItems (1..n)
        ├── status: todo | doing | done | blocked
        └── priority: low | medium | high
```

### AI Pipeline (Two-Pass)

```
Transcript
    │
    ▼
Pass 1: GPT-4o JSON extraction
  (response_format: json_object, temperature: 0.2)
    │
    ▼
Pass 2: Pydantic validation + Markdown render
    │
    ├──► MeetingVersion (ai_output_json + rendered_markdown)
    └──► ActionItems (bulk insert)
```

---

## Testing

The project has three layers of test coverage (68 tests total).

### Backend — pytest (25 unit + 37 integration)

```bash
# Pure unit tests — no database required, run locally
cd apps/api
python -m pytest tests/test_security.py tests/test_ai_service.py -v

# Full suite (unit + integration) — requires Docker stack
make test-api
```

Integration tests need a `meetingmemo_test` database. Create it once:

```bash
make shell-db
# Inside psql:
CREATE DATABASE meetingmemo_test;
\q
```

### Frontend unit — vitest + React Testing Library (43 tests)

```bash
cd apps/web
npm run test         # run once
npm run test:watch   # watch mode
```

No Docker required — runs entirely in jsdom.

### E2E — Playwright (requires full stack)

```bash
make up && make migrate && make seed
make test-e2e
```

### All at once

```bash
make test          # backend unit + frontend unit (no stack needed for frontend)
make test-e2e      # E2E (stack must be running)
```

---

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make build` | Build all Docker images |
| `make up` | Start all services in background |
| `make down` | Stop all services |
| `make migrate` | Run Alembic migrations |
| `make seed` | Seed demo data |
| `make logs` | Follow all container logs |
| `make shell-api` | Open bash in api container |
| `make shell-db` | Open psql in db container |
| `make test-api` | Run backend tests (inside Docker) |
| `make test-web` | Run frontend unit tests |
| `make test-e2e` | Run Playwright E2E tests |
| `make test` | Run backend + frontend unit tests |

---

## Environment Variables

### `apps/api/.env`

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Async PostgreSQL URL (asyncpg) | — |
| `DATABASE_URL_SYNC` | Sync PostgreSQL URL (psycopg2, Alembic only) | — |
| `SECRET_KEY` | JWT signing secret (32+ hex chars) | — |
| `OPENAI_API_KEY` | OpenAI API key | — |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4o` |
| `UPLOAD_DIR` | Local file upload directory | `./data/uploads` |
| `ALLOWED_ORIGINS` | JSON array of allowed CORS origins | `["http://localhost:3000"]` |
| `APP_ENV` | Environment (`development` / `production`) | `development` |
| `AWS_S3_BUCKET` | S3 bucket for file uploads (optional) | — |

### `apps/web/.env`

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | API URL used by the browser | `http://localhost:8000` |
| `INTERNAL_API_URL` | API URL used by Next.js server-side | `http://api:8000` |

---

## API Documentation

Swagger UI: `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`

---

## Deployment Notes

### Cookie Security
Set `APP_ENV=production` in `apps/api/.env` to enable `Secure=True` on auth cookies.

### CORS
```
ALLOWED_ORIGINS=["https://app.yourdomain.com"]
```

### S3 File Storage
```
AWS_S3_BUCKET=your-bucket
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_ENDPOINT_URL=...  # optional, for S3-compatible storage
```

### Rate Limiting
The AI generation endpoint is rate-limited to 10 requests/hour per user. Adjust `RATE_LIMIT_GENERATE` in `apps/api/.env` if needed.

### Next.js Standalone Build
`next.config.ts` uses `output: "standalone"` for optimised Docker deployment.
