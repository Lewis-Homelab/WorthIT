# WorthIT

High-value experience planning — rank adventures by joy per pound, not just cost or popularity.

Phase 1 stack: **PostgreSQL** + **FastAPI** + **Next.js**, with data from Google Places API and OpenStreetMap.

---

## Quick start

```bash
cp .env.example .env   # optional: add GOOGLE_PLACES_API_KEY
make dev
```

Open http://homelab:3050 from any device on your Tailscale network (e.g. your Mac).
Set your budget and interests, then click **Show me ideas**.
The first request can take 1–2 minutes while the API loads the walking graph.
Ensure `data/raw/` contains the Camden parquet files (see sandbox notebooks).

After changing `NEXT_PUBLIC_API_URL` in config.env, restart the web container:
`docker compose --env-file config.env -f compose.yaml -f compose.dev.yaml up -d --build web`

| URL | Purpose |
|-----|---------|
| http://homelab:3050 | Web UI — browse ranked day plans |
| http://homelab:8000/docs | API docs (Swagger) |
| http://homelab:8000/health | API health |
| http://homelab:8000/recommendations/day-plans | Ranked day-plan cards (API) |
| http://homelab:8000/places | Places CRUD |

`homelab` is the Tailscale MagicDNS name from [config.env](config.env) (`TAILNET_HOST`).
Ports are configured in config.env (`HOST_PORT`, `WEB_HOST_PORT`).

### Access via Tailscale

Docker runs on the homelab server. Browse using the MagicDNS hostname (not `localhost` on your Mac):

- **Web UI:** http://homelab:3050
- **API:** http://homelab:8000

`NEXT_PUBLIC_API_URL` is set to `http://homelab:8000` so the browser on your Mac calls the API over Tailscale, not `localhost`.

If your MagicDNS name differs, update `TAILNET_HOST` and `NEXT_PUBLIC_API_URL` in `config.env`, then rebuild the web service.

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
