# ---- Stage 1: Build dependencies ----
FROM python:3.14-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: Production image ----
FROM python:3.14-slim

ARG APP_VERSION=1.0.0
LABEL org.opencontainers.image.title="website-cicd-pipeline" \
      org.opencontainers.image.description="Flask DevOps CI/CD demo application" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.source="https://github.com/YOUR_USERNAME/website-cicd-pipeline"

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder /install /usr/local
COPY app.py wsgi.py ./
COPY website/ website/
COPY templates/ templates/
COPY static/ static/

RUN chown -R appuser:appuser /app
USER appuser

ENV PORT=5000 \
    APP_VERSION=${APP_VERSION} \
    ENVIRONMENT=production \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health/live')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "wsgi:application"]
