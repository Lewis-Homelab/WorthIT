# Hello-Homelab

Minimal Flask app proving **laptop → GitHub Actions → homelab** CI/CD over Tailscale.

Pipeline docs: [docs/DEPLOY.md](docs/DEPLOY.md). New projects: [TEMPLATE.md](TEMPLATE.md).

---

## Quick start

```bash
uv sync
make test
make dev
```

| URL | Purpose |
|-----|---------|
| http://localhost:5050 | Home |
| http://localhost:5050/health | Health check |

Ports come from [config.env](config.env).

---

## Configuration

**[config.env](config.env)** — committed project config (ports, names, paths). Edit on your laptop, push to git; the server uses it automatically on deploy.

**`.env`** — optional, gitignored. Only for secrets or local overrides ([.env.example](.env.example)).

| Variable | This project |
|----------|--------------|
| `APP_NAME` | `hello-homelab` |
| `HOST_PORT` | `5050` |
| `APP_PORT` | `5001` |
| `DEPLOY_PATH` | `/opt/apps/hello-homelab` |

Set GitHub repo variable `DEPLOY_PATH` to match `DEPLOY_PATH` in `config.env`.

---

## CI/CD

[`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml) — test + build → deploy on `main`.

- **Org secrets** (shared): [docs/secrets.md](docs/secrets.md)
- **Repo variable** (this app only): `DEPLOY_PATH`

---

## Project layout

```text
config.env            # ← committed config (edit this)
.env                  # optional secrets (gitignored)
app/                  # Sample Flask app
scripts/deploy.sh     # Deploy + rollback
.github/workflows/ci-cd.yml
docs/DEPLOY.md        # Generic pipeline (copy unchanged)
```

---

## New project

```bash
./scripts/init-project.sh <app-name> [host-port]
```

See [TEMPLATE.md](TEMPLATE.md).

---

## License

MIT — see [LICENSE](LICENSE).
