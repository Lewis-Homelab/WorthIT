# Homelab server setup

One-time preparation per app on the home server. Generic pipeline docs: [DEPLOY.md](DEPLOY.md).

Configuration arrives via **`config.env` in git** — no manual env setup on the server.

---

## Prerequisites

- Docker and Docker Compose plugin
- Git
- Deploy user with Docker access (recommended)

---

## 1. Create deploy user (once per server)

```bash
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy
```

Add the GitHub Actions SSH public key to `~/.ssh/authorized_keys`. See [secrets.md](secrets.md).

---

## 2. Clone the repository

Use `DEPLOY_PATH` from `config.env` (e.g. `/opt/apps/hello-homelab`):

```bash
sudo mkdir -p /opt/apps
sudo chown deploy:deploy /opt/apps
sudo -u deploy git clone git@github.com:YOUR_USER/Hello-Homelab.git /opt/apps/hello-homelab
```

Set the same path as the GitHub **repository variable** `DEPLOY_PATH`.

---

## 3. First deploy

```bash
cd /opt/apps/hello-homelab
chmod +x scripts/deploy.sh
DEPLOY_PULL=1 ./scripts/deploy.sh
```

Verify:

```bash
source config.env
curl "http://localhost:${HOST_PORT}${HEALTH_PATH}"
```

---

## 4. Enable automated deploy

Org secrets are already configured. Set repo variable `DEPLOY_PATH`, then push to `main`.

---

## What happens on each deploy

```text
ci-cd.yml deploy job
  → SSH over Tailscale
  → git pull origin main          ← always in workflow (not only deploy.sh)
  → DEPLOY_PULL=0 ./scripts/deploy.sh
      → docker compose --env-file config.env up
      → health check
      → rollback on failure
```

---

## Firewall

Ensure `HOST_PORT` from `config.env` is reachable on your LAN, or route through a reverse proxy.
