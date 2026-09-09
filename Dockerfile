FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
RUN pip install --no-cache-dir wheel uwsgi
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./src /app

# LFS-aware: fail fast if LFS-tracked files were copied as pointers instead of
# content. Builder must run `git lfs install && git lfs pull` first (README §Setup).
RUN if grep -rls "version https://git-lfs.github.com/spec/v1" \
        /app/static/thesis /app/static/files; then \
        echo "ERROR: LFS pointers copied into the image — run 'git lfs install' and 'git lfs pull' on the build host first"; \
        exit 1; \
    fi

# requirements.txt is only needed at build time.
RUN rm -f /app/requirements.txt

COPY ./docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uwsgi", "--ini", "/app/app.ini"]
