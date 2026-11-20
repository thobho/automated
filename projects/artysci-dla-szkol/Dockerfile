# Multi-arch (amd64/arm64): only multi-arch base images and pure-wheel dependencies.
FROM docker.io/library/python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# ffmpeg/ffprobe for video and audio materials (US-2.3B); Debian's build is multi-arch.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 10001 app
WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev

COPY --chown=app:app . .
RUN mkdir -p /app/staticfiles && chown app:app /app/staticfiles

USER app
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
