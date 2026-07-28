# FastAPI Task Manager API

> **Portfolio backend project** — not a production product.  
> This repository demonstrates backend engineering practices through a progressive, level-based Task Manager API built with FastAPI.

The API was designed to replace the `localStorage` logic of an existing frontend task manager, moving persistence to the server. Each level adds real-world concerns: validation, auth, testing, containerization, observability, and (planned) PostgreSQL and VPS deployment.

**Repository:** https://github.com/raulbarreiroz/fastapi-task-api

---

## Deployment Disclosure

Although this project includes `docker-compose.yml` and `docker-compose.prod.yml` for local development and prod-like testing, **the current live deployment is on [Render](https://render.com)** (managed PaaS).

| Level | Deployment target |
|-------|-------------------|
| **1 / 1.5 (current)** | Render — zero-ops hosting for portfolio demos |
| **Final level** | VPS or AWS using `docker-compose.prod.yml` — full infrastructure ownership |

Docker Compose is configured from Level 1.5 onward to ensure dev/prod parity and to prepare for the final self-hosted deployment.

---

## What This Project Demonstrates

| Area | What you will find here |
|------|-------------------------|
| **API design** | RESTful CRUD, versioned routes (`/api/v1`), OpenAPI docs |
| **Validation** | Pydantic v2 schemas, field validators, structured 422 errors |
| **Auth** | Bearer token dependency injection (`Depends`) |
| **Business logic** | Domain rule enforced in the router, not in schemas |
| **Testing** | Async tests with `httpx.AsyncClient`, AAA pattern, DB isolation fixture, 100% line coverage |
| **DevOps** | Multi-stage Docker, dev/prod compose, Gunicorn + Uvicorn workers |
| **Observability** | Structured JSON request logging, Prometheus metrics |
| **Performance** | k6 load and breakpoint scripts |
| **CI/CD** | GitHub Actions: tests + coverage + Docker build smoke test |

> **Study materials** (design decisions, interviewer guide, Q&A): see `.study/level1/` in the local workspace.

---

## Current Status: Level 1.5

### Level 1 — Core API (MVP)

- In-memory task store (simulating a database)
- Pydantic v2: `TaskCreate` (input) and `TaskResponse` (output)
- Input sanitization: auto-trim on `title` and `description`
- Business rule: titles containing `URGENTE` (case-insensitive) are forced to `completed=false`
- Fake Bearer authentication via FastAPI dependency injection
- Global validation exception handler with consistent error shape
- Interactive OpenAPI docs at `/docs` and `/redoc`

### Level 1.5 — Docker & Observability

- Production-ready `Dockerfile` (Gunicorn + Uvicorn workers)
- `docker-compose.yml` (dev with hot-reload) and `docker-compose.prod.yml` (healthcheck, restart policy)
- Environment-based settings with `pydantic-settings`
- Structured JSON access logs (`LoggingMiddleware`)
- Prometheus metrics via `prometheus-fastapi-instrumentator` (`/api/v1/metrics/`)
- k6 load test (`tests/load-test.js`) and breakpoint test (`tests/breakpoint.js`)
- Postman collection (`postman/FastAPI Task Manager.postman_collection.json`)

### Roadmap

| Level | Planned additions |
|-------|-------------------|
| **2** | PostgreSQL + SQLAlchemy 2.0 async + Alembic migrations |
| **3** | Redis cache + background tasks (e.g. email notifications) |
| **Final** | VPS/AWS deployment with `docker-compose.prod.yml` |

---

## Tech Stack

- **Python** 3.11+
- **FastAPI** 0.140+
- **Pydantic** v2 + `pydantic-settings`
- **Server** Uvicorn (dev) / Gunicorn + Uvicorn workers (prod)
- **Testing** pytest, pytest-asyncio, httpx, pytest-cov
- **Observability** prometheus-fastapi-instrumentator
- **Containers** Docker, Docker Compose
- **Load testing** Grafana k6
- **CI** GitHub Actions
- **Hosting (current)** Render

---

## API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/v1/health/` | No | Health check |
| `GET` | `/api/v1/metrics/` | No | Prometheus metrics |
| `POST` | `/api/v1/tasks/` | Yes | Create a task |
| `GET` | `/api/v1/tasks/` | Yes | List all tasks |
| `GET` | `/api/v1/tasks/{id}` | Yes | Get task by ID |
| `DELETE` | `/api/v1/tasks/` | Yes | Delete all tasks |

**Interactive docs:** `http://localhost:8000/docs`

### Authentication (Level 1 — fake JWT)

All task endpoints require:

```http
Authorization: Bearer <token>
```

Rules:
1. Scheme must be `Bearer` (case-insensitive)
2. Token must contain the substring `valid`

Examples:
- ✅ `Bearer valid-token`
- ✅ `Bearer my-valid-token-123`
- ❌ `Bearer bad-token` → `401 Unauthorized`

### Business Rule Example

```bash
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer valid-token" \
  -H "Content-Type: application/json" \
  -d '{"title": "URGENTE: fix production bug", "completed": true}'
```

### Validation Error Format

```json
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "body.title",
      "message": "String should have at least 3 characters",
      "type": "string_too_short"
    }
  ]
}
```

---

## Quick Start (Recommended: Docker)

### Prerequisites

- Docker & Docker Compose
- (Optional) Python 3.11+ for local development without Docker

### 1. Run the API

```bash
# Development (hot-reload, code mounted)
docker compose up --build

# Production-like (Gunicorn, healthcheck, no volume mount)
docker compose -f docker-compose.prod.yml up --build
```

API available at: **http://localhost:8000**

### 2. Smoke Test (30 seconds)

```bash
curl http://localhost:8000/api/v1/health/

curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer valid-token" \
  -H "Content-Type: application/json" \
  -d '{"title": "Interview demo task", "description": "Created via curl"}'

curl http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer valid-token"

curl http://localhost:8000/api/v1/metrics/
```

### 3. Postman

Import `postman/FastAPI Task Manager.postman_collection.json` and set:

- `base_url` → `http://localhost:8000/api/v1`
- `token` → `valid-token`

---

## Local Development (Without Docker)

```bash
python -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Optional `.env`:

```env
PORT=8000
WORKERS=4
ENABLE_METRICS=true
APP_ENV=development
```

---

## Running Tests

```bash
pytest tests/ -v --cov=app --cov-report=term

pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html
```

**Coverage:** 100% line coverage on `app/` (16 automated scenarios).  
See `QA_coverage.md` for the full traceability matrix.

---

## Load Testing (k6)

Start the API first, then run k6 from Docker.

### Load test (~35s, 10 concurrent users)

```bash
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "$(pwd)/tests:/tests" \
  -e API_TOKEN="valid-token" \
  -e K6_OUT=json=/tests/results.json \
  grafana/k6 run --summary-export=/tests/summary.json /tests/load-test.js
```

> **Windows (Git Bash):** use `MSYS_NO_PATHCONV=1`. The script targets `host.docker.internal:8000`.

**Thresholds:** `p(95) < 500ms`, error rate `< 1%`.

### Breakpoint test

```bash
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "$(pwd)/tests:/tests" \
  -e API_TOKEN="valid-token" \
  grafana/k6 run --summary-export=/tests/summary-breakpoint.json /tests/breakpoint.js
```

---

## Project Structure

```
fastapi-task-api/
├── app/
│   ├── main.py              # App factory, exception handler, metrics, middleware
│   ├── config.py            # pydantic-settings (env-based config)
│   ├── routers/tasks.py     # Task CRUD + business rules
│   ├── schemas/task.py      # Pydantic v2 input/output models
│   ├── dependencies/auth.py # Bearer token dependency
│   └── middleware/logging.py
├── tests/
│   ├── test_tasks.py
│   ├── load-test.js
│   └── breakpoint.js
├── postman/
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
└── docker-compose.prod.yml
```

---

## CI/CD

GitHub Actions runs on every push/PR to `develop`:

1. Install dependencies (Python 3.11)
2. Run `pytest` with coverage (`--cov=app`)
3. Build Docker image (smoke test)

---

## License

Portfolio / educational project. Use and reference freely for interview or learning purposes.
