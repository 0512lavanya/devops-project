<<<<<<< HEAD
# Stage 1: Build stage
FROM python:3.11-alpine AS builder

WORKDIR /app
COPY requirements.txt .

# Install build dependencies for psycopg2 and other packages
RUN apk update && \
    apk add --no-cache postgresql-dev gcc python3-dev musl-dev && \
    pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Run stage
FROM python:3.11-alpine

WORKDIR /app

# Install runtime dependencies for psycopg2
RUN apk update && apk add --no-cache libpq

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy project files
COPY . .

# Environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost:5000/health || exit 1

# Run Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]
=======
# ---- Stage 1: Build dependencies ----
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: Production image ----
FROM python:3.12-slim

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
>>>>>>> 5961f6c04d0ae3859ddf1b2cdb3b470b10b1b79f
