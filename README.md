# WorthIT

High-value experience planning — rank adventures by joy per pound, not just cost or popularity.

Phase 1 stack: **PostgreSQL** + **FastAPI** + **Next.js**, with data from Google Places API and OpenStreetMap.

---

## Quick start

```bash
cp .env.example .env   # optional: add GOOGLE_PLACES_API_KEY
make dev
```

| URL | Purpose |
|-----|---------|
| http://localhost:3050 | Web UI |
| http://localhost:8000/docs | API docs (Swagger) |
| http://localhost:8000/health | API health |
| http://localhost:8000/places | Places CRUD |
| localhost:5432 | PostgreSQL |

Ports are configured in [config.env](config.env).

---

## Local development (without Docker)

**API**

```bash
uv sync
# Start Postgres separately, then:
export DATABASE_URL=postgresql+asyncpg://worthit:worthit@localhost:5432/worthit
uv run uvicorn app.main:app --reload --port 8000
```

**Web**

```bash
cd frontend && npm install && npm run dev
```

**Tests**

```bash
make test
```

---

## Configuration

**[config.env](config.env)** — committed project config (ports, database name, deploy path).

**`.env`** — optional, gitignored. Secrets such as `GOOGLE_PLACES_API_KEY` ([.env.example](.env.example)).

| Variable | Default |
|----------|---------|
| `APP_NAME` | `worthit` |
| `HOST_PORT` | `8000` (API) |
| `WEB_HOST_PORT` | `3050` |
| `POSTGRES_*` | `worthit` / `worthit` / `worthit` |

---

## Data model

Places are stored in PostgreSQL with types:

- `attraction`
- `restaurant`
- `hike`
- `viewpoint`

Each record tracks name, location, cost, rating, source (`google_places` or `openstreetmap`), and raw metadata JSON.

Tables are created automatically on API startup (experimentation-friendly; add Alembic migrations later).

---

## Project layout

```text
app/                  # FastAPI backend
  models.py           # Place model + enums
  routers/            # /health, /places
frontend/             # Next.js web UI
compose.yaml          # db + api + web (dev)
compose.prod.yaml     # production overrides
config.env            # committed config
```

---

## CI/CD

Homelab deploy pipeline: [docs/DEPLOY.md](docs/DEPLOY.md). Set GitHub repo variable `DEPLOY_PATH` to match `config.env`.

---

## License

MIT — see [LICENSE](LICENSE).
