# Installation

This guide walks through running the Odoo stack locally with Docker Compose.

## Prerequisites

- **Docker** and **Docker Compose** (Compose v2 plugin is fine).
- Enough disk space for a Postgres volume, Odoo filestore, and an Odoo source tree.
- **Odoo source** for the version you intend to run (for example 19.0), placed in `odoo/` at the repository root so paths such as `odoo/requirements.txt` exist before build.

## 1. Obtain Odoo source

Clone the official Odoo repository (or your fork) into `odoo/`:

```bash
# Example: from the repository root, with the correct branch for your Odoo version
git clone --depth 1 --branch 19.0 https://github.com/odoo/odoo.git odoo
```

Adjust branch or remote to match your policy. The `Dockerfile` copies `./odoo` into the image at `/opt/odoo/odoo`.

## 2. Environment file

Copy the example file and edit values:

```bash
cp .example.env .env
```

Set at least:

- `POSTGRES_DB` — database name Postgres will create (for example `odoo`).
- `POSTGRES_USER` — database role (for example `odoo`).
- `POSTGRES_PASSWORD` — a strong password.

The `HOST`, `USER`, and `PASSWORD` entries in `.example.env` are informational mirrors for Odoo; **Odoo still reads database credentials from `config/odoo.conf`** unless you change how the container is configured.

Never commit `.env`; it is listed in `.gitignore`.

## 3. Align `config/odoo.conf` with Postgres

The `odoo` service mounts `config/odoo.conf` read-only. Odoo uses the `[options]` section for the database connection:

- `db_host` — use `db` (the Compose service name on the default network).
- `db_port` — `5432` unless you change the database service.
- `db_user` — must match `POSTGRES_USER` in `.env`.
- `db_password` — must match `POSTGRES_PASSWORD` in `.env`.

If these disagree, Odoo will fail to connect even when Postgres is healthy.

## 4. Build and start

From the repository root:

```bash
docker compose build
docker compose up -d
```

The `odoo` service waits for the `db` health check before starting.

## 5. First access

Open **http://localhost:8069** in a browser.

- If this is a new database, use the Odoo UI to create one (master password, database name, etc.).
- Install applications and optional custom modules (for example **Apps Pins**) from **Apps** as needed.

Port **8072** is mapped for longpolling; keep it exposed if you use features that rely on it behind a proxy.

## Troubleshooting

### Build fails: missing `odoo/`

Ensure the `odoo` directory exists and contains the Odoo checkout. The build context expects `./odoo` relative to the `Dockerfile`.

### Odoo exits or shows database connection errors

- Confirm `db_host`, `db_user`, and `db_password` in `config/odoo.conf` match `.env` for Postgres.
- Check logs: `docker compose logs db` and `docker compose logs odoo`.

### Port 8069 already in use

Change the host mapping in `docker-compose.yml` (for example `"8070:8069"`) or stop the conflicting process.

### Permission or empty filestore issues

Filestore lives in the `odoo-data` volume. The entrypoint ensures `/var/lib/odoo` is owned by the `odoo` user. If you bind-mount over `data_dir`, ensure host permissions are compatible.

### Module changes not visible

After pulling code changes for a custom module, upgrade it (replace `YOUR_DB`):

```bash
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d YOUR_DB -u MODULE_NAME --stop-after-init
```

Restart Odoo if the server was not stopped for the upgrade.
