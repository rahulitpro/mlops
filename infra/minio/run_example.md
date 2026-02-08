```bash
echo "MINIO_ROOT_USER=<miniorootuser>
MINIO_ROOT_PASSWORD=<miniorootpassword>
MINIO_API_PORT=<MINIO_API_PORT>
MINIO_CONSOLE_PORT=<MINIO_CONSOLE_PORT>
MINIO_STORAGE_USE_HTTPS=<True/False>" > .env
podman compose --env-file .env -f compose.yaml up -d
podman logs minio
podman compose down
```