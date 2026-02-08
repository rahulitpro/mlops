```bash
cd $PREPROCESSOR_HOME
export GIT_USERNAME=<yourgitusername>
export GIT_TOKEN=<yourgittoken>
export GIT_REPO=<yourgitreponame>
podman login --username ${GIT_USERNAME} --password ${GIT_TOKEN} ghcr.io
podman build . --squash-all -t ghcr.io/${GIT_USERNAME}/${GIT_REPO}/taxi-preprocessor:1.0
podman push ghcr.io/${GIT_USERNAME}/${GIT_REPO}/taxi-preprocessor:1.0
```

```bash
echo "RAW_DATA_PATH=<RAW_DATA_PATH>
PREPROCESSED_DATA_PATH=<PREPROCESSED_DATA_PATH>
GIT_USERNAME=<yourgitusername>
GIT_REPO=<yourgitreponame>
PODMAN_USERNS=keep-id" > .env
podman compose --env-file .env -f compose.yaml up -d
podman logs taxi-preprocessor
podman compose down
```