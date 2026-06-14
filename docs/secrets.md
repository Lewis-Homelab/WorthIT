# GitHub secrets and variables

Homelab deploy credentials are configured **once at the organization level** and reused by every app repo. Each new project only needs its own `DEPLOY_PATH`.

---

## Organization level (set once, shared by all apps)

Configure under **GitHub → Your org → Settings → Secrets and variables → Actions**.

### Organization secrets

| Name | Description |
|------|-------------|
| `TS_OAUTH_CLIENT_ID` | Tailscale OAuth client ID |
| `TS_OAUTH_SECRET` | Tailscale OAuth client secret |
| `HOMELAB_SSH_KEY` | Private SSH key for the deploy user |
| `HOMELAB_HOST` | Server Tailscale IP or MagicDNS hostname |
| `HOMELAB_USER` | SSH username on the server (e.g. `deploy`) |

### Organization variables

| Name | Description | Example |
|------|-------------|---------|
| `TS_TAGS` | Tailscale tags for CI runner nodes | `tag:ci` |

> **Use Tailscale addresses for `HOMELAB_HOST`**, not LAN IP. GitHub Actions runners reach your server over Tailscale.

Workflows access org secrets/variables automatically — no per-repo duplication.

---

## Repository level (set once per app)

Configure under **Repo → Settings → Secrets and variables → Actions → Variables**.

| Name | Description | Example |
|------|-------------|---------|
| `DEPLOY_PATH` | Absolute path where this repo is cloned on the server | `/opt/apps/my-api` |

This is the **only** GitHub setting that differs between homelab apps.

Match `DEPLOY_PATH` to the `DEPLOY_PATH` value in the app's **`config.env`** (committed).

---

## Tailscale one-time setup

### 1. Create a tag

In [Tailscale admin → Access controls](https://login.tailscale.com/admin/acls):

```json
"tagOwners": {
  "tag:ci": ["autogroup:admin"]
}
```

### 2. Create an OAuth client

1. [OAuth clients](https://login.tailscale.com/admin/settings/oauth) → create with **`auth_keys`** scope
2. Tag it with `tag:ci` (same as org variable `TS_TAGS`)
3. Add client ID and secret as org secrets `TS_OAUTH_CLIENT_ID` and `TS_OAUTH_SECRET`

### 3. Allow CI runners to SSH to the server

```json
{
  "src": ["tag:ci"],
  "dst": ["tag:server"],
  "ip": ["22"]
}
```

### 4. Server address

From [Machines](https://login.tailscale.com/admin/machines), use Tailscale IP or MagicDNS for org secret `HOMELAB_HOST`.

---

## SSH key

Reuse the private key you SSH with from your laptop:

```bash
ssh deploy@homelab.tailnet-name.ts.net "echo ok"
```

Public key → server `authorized_keys`. Private key → org secret `HOMELAB_SSH_KEY`.

---

## Checklist

### Once (organization)

```text
Org secrets:  TS_OAUTH_CLIENT_ID, TS_OAUTH_SECRET, HOMELAB_SSH_KEY, HOMELAB_HOST, HOMELAB_USER
Org variable: TS_TAGS=tag:ci
```

### Per new app (repository)

```text
Repo variable: DEPLOY_PATH=/opt/apps/<app-name>
Server:        git clone at that path, cp .env.example .env, run deploy.sh once
```

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `requested tags are invalid or not permitted` | OAuth client tags ≠ `TS_TAGS` | Align OAuth client and org variable |
| Tailscale ping timeout | ACL blocks SSH | Allow `tag:ci` → server port 22 |
| `Permission denied (publickey)` | Key or user mismatch | Check `HOMELAB_USER` and `HOMELAB_SSH_KEY` |
| `cd: no such file or directory` | Wrong `DEPLOY_PATH` | Match repo variable to server clone path |
| Deploy failed, rollback succeeded | Bad commit failed health check | Fix code and push again |
| Rollback failed | Previous version also unhealthy | `docker logs <APP_NAME>` on server |

Read by [.github/workflows/ci-cd.yml](../.github/workflows/ci-cd.yml).
