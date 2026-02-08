```bash
echo "POSTGRES_PASSWORD=<postgres_password>
POSTGRES_USER=<postgres_user>
POSTGRES_DB=<postgres_db>
POSTGRES_PORT=<POSTGRES_PORT>" > .env
podman compose --env-file .env -f compose.yaml up -d
podman logs postgres-db
podman compose down
```