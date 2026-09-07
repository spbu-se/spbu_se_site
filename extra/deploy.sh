#!/bin/sh

set -e

systemctl stop spbu_se_site
cd /srv/spbu_se_site/repo

# Repo preparation part
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=http.version GIT_CONFIG_VALUE_0=HTTP/1.1 git fetch
git checkout current
git rebase origin/current
if [ "${COMMIT_SHA}" != "" ]; then
  git checkout "${COMMIT_SHA}"
  echo "Using ${COMMIT_SHA} as HEAD"
else
  echo "Using current as HEAD"
fi
SE_SITE_LASTMOD=$(git describe --dirty --abbrev=6 --tags)

# App configuration
# Very old versions do not use uv, pure requirements.txt only
if [ -f "uv.lock" ]; then
  UV_PYTHON_INSTALL_DIR=${PWD}/../uv-python UV_PROJECT_ENVIRONMENT=${PWD}/../venv /opt/uv/bin/uv sync --frozen
else
  ../venv/bin/pip install --upgrade pip
  ../venv/bin/pip install -r requirements.txt
fi
echo "SE_SITE_LASTMOD=$SE_SITE_LASTMOD" | tee > ../env
cd src
../../venv/bin/flask db upgrade
systemctl start spbu_se_site
