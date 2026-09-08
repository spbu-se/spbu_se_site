#!/bin/sh

set -e

systemctl stop spbu_se_site
cd /srv/spbu_se_site/repo

# Repo preparation part
# --tags --force: release tags are re-created when published history is
# rewritten (secret/LFS purge); plain fetch would keep stale tag -> old SHA.
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=http.version GIT_CONFIG_VALUE_0=HTTP/1.1 \
  git fetch --tags --force origin
# LFS: configure the smudge filter BEFORE any checkout so LFS-tracked files
# (thesis PDFs/PPTs, PracticesGuide.pdf) materialize as content, not pointers.
git lfs install --local
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=http.version GIT_CONFIG_VALUE_0=HTTP/1.1 \
  git lfs fetch

# Bring the deploy checkout to origin/current. After a published-history
# rewrite (filter-repo / LFS migration, all SHAs replaced) the local history
# no longer shares ancestry with origin/current, so rebase would replay every
# superseded commit onto the rewritten history and fail. Detect that case and
# reset instead; the deploy checkout never carries local commits.
if git merge-base --is-ancestor current origin/current 2>/dev/null; then
  git rebase origin/current
else
  echo "History divergence detected (history rewrite); resetting to origin/current"
  git checkout -B current origin/current
  # Drop superseded pre-rewrite objects (may contain purged secrets) from disk.
  git reflog expire --expire=now --all
  git gc --prune=now
fi
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
