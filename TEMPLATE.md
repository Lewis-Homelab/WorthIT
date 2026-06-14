# Using this as a template

Homelab CI/CD template. **Edit `config.env`, set GitHub `DEPLOY_PATH`, replace `app/`.**

Enable **Template repository** in GitHub Settings for one-click "Use this template".

---

## New project

```bash
./scripts/init-project.sh my-api 8080
# Replace app/ and tests/
# Commit config.env, push
# Set GitHub repo variable DEPLOY_PATH (match config.env)
# Clone on server — no manual config on server required
```

---

## What to customize

| File | Action |
|------|--------|
| **`config.env`** | **App name, ports, paths** (committed) |
| `app/` | Your application |
| `tests/` | At least one health test |
| `pyproject.toml` | Dependencies (`init-project.sh` updates `name`) |
| `README.md` | App description |
| `.env` | Optional secrets only (gitignored) |

## Copy unchanged

| File | Purpose |
|------|---------|
| `.github/workflows/ci-cd.yml` | Pipeline |
| `scripts/deploy.sh`, `scripts/load-env.sh` | Deploy + rollback |
| `compose.yaml`, `compose.prod.yaml` | Docker (reads `config.env`) |
| `docs/` | Generic documentation |
| `Makefile`, `.gitignore`, `.dockerignore` | Tooling |

---

## GitHub setup

| Scope | Settings |
|-------|----------|
| **Organization** | Secrets: `TS_OAUTH_*`, `HOMELAB_*` — Variable: `TS_TAGS` |
| **Repository** | Variable: `DEPLOY_PATH` (must match `config.env`) |

See [docs/secrets.md](docs/secrets.md).

---

## Checklist

```text
[ ] ./scripts/init-project.sh <name> [port]
[ ] Edit config.env if needed, commit and push
[ ] Replace app/ and tests/
[ ] GitHub repo variable DEPLOY_PATH = config.env DEPLOY_PATH
[ ] git clone on server, push to main
```
