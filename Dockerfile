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
