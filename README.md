# Website CI/CD Pipeline Project

[![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)](.github/workflows/main.yml)
[![Docker](https://img.shields.io/badge/Docker-Multi--stage-2496ED?logo=docker&logoColor=white)](Dockerfile)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](requirements.txt)
[![Coverage](https://img.shields.io/badge/Coverage-85%25%2B-brightgreen)](pyproject.toml)
[![Security](https://img.shields.io/badge/Scan-Trivy%20%2B%20CodeQL-blue)](.github/workflows/)

Production-grade end-to-end DevOps project: **Flask** → **Git** → **Docker** → **GitHub Actions** → **Docker Hub** → **Render / AWS EC2**.

---

## Highlights (Portfolio / Grading)

| Category | Implementation |
|----------|----------------|
| Application factory pattern | `website/app_factory.py` |
| Security headers | All HTTP responses |
| Health probes | `/health`, `/health/live`, `/health/ready` |
| Metrics | `/metrics` (Prometheus-style text) |
| Tests + 85% coverage gate | `pytest` + `pytest-cov` in CI |
| Linting | `ruff` in CI |
| Vulnerability scanning | Trivy (filesystem + image) |
| Static analysis | CodeQL weekly + on push |
| Dependency updates | Dependabot |
| CD deploy | Render hook + EC2 SSH (optional secrets) |
| Non-root container | Dockerfile `appuser` |
| Nginx reverse proxy | `docker-compose` + prod overlay |

---

## Architecture

```
Developer → git push → GitHub
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
        Lint            Test         Trivy FS
          │               │               │
          └───────────────┴───────────────┘
                          ▼
                   Docker Build & Push
                          ▼
                     Docker Hub
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
    Render (hook)                    AWS EC2 (SSH)
          │                               │
          └───────────────┬───────────────┘
                          ▼
                    Nginx :80 (optional)
                          ▼
                 Gunicorn + Flask :5000
```

---

## Folder Structure

```
├── .github/
│   ├── workflows/main.yml      # Lint → Test → Scan → Build → Deploy
│   ├── workflows/codeql.yml    # CodeQL security analysis
│   └── dependabot.yml
├── website/                    # Application package
│   ├── app_factory.py
│   └── config.py
├── nginx/nginx.conf
├── scripts/run.ps1 | run.sh
├── tests/
├── docs/screenshots/
├── app.py                      # Entry point
├── wsgi.py                     # Gunicorn entry
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── Makefile
├── .env.example
├── SECURITY.md
└── README.md
```

---

## Quick Start

### One-command run (Windows)

```powershell
cd c:\Users\Dell\Desktop\DEVOPS
.\scripts\run.ps1
```

### Manual run

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env
python app.py
```

Open **http://localhost:5000**

### Make targets (Linux/macOS/WSL)

```bash
make install && make test && make run
make docker-up
```

---

## API Endpoints

| Route | Description |
|-------|-------------|
| `GET /` | Home page |
| `GET/POST /login` | Login UI (demo, no DB) |
| `GET /health` | Full health JSON |
| `GET /health/live` | Liveness (Kubernetes/Docker) |
| `GET /health/ready` | Readiness (load balancers) |
| `GET /metrics` | Basic Prometheus-style metrics |

```bash
curl http://localhost:5000/health/ready
```

---

## Testing & Quality

```powershell
.\venv\Scripts\activate
pytest tests/ --cov=website --cov=app --cov-fail-under=85
ruff check website app.py wsgi.py tests
ruff format --check website app.py wsgi.py tests
```

---

## Docker

```powershell
# Start Docker Desktop first
docker build -t website-cicd-pipeline:latest .
docker run -d -p 5000:5000 -e ENVIRONMENT=production --name webapp website-cicd-pipeline:latest

# With Nginx
docker compose up -d --build

# Production overlay
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

## Git & GitHub

```bash
git init
git add .
git commit -m "feat: production-grade Website CI/CD Pipeline"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/website-cicd-pipeline.git
git push -u origin main
```

---

## CI/CD Pipeline

**Workflow:** `.github/workflows/main.yml`

| Job | Purpose |
|-----|---------|
| `lint` | Ruff check + format |
| `test` | Pytest with 85% coverage minimum |
| `security-scan` | Trivy filesystem (CRITICAL/HIGH) |
| `build-push` | Docker build, push to Hub, PR builds without push |
| `deploy` | Render hook and/or EC2 SSH (main branch only) |

### Required secrets

| Secret | Required | Purpose |
|--------|----------|---------|
| `DOCKER_USERNAME` | Yes | Docker Hub login |
| `DOCKER_PASSWORD` | Yes | Docker Hub token |

### Optional secrets (continuous deployment)

| Secret | Purpose |
|--------|---------|
| `RENDER_DEPLOY_HOOK` | POST URL from Render → Deploy Hook |
| `EC2_HOST` | EC2 public IP or DNS |
| `EC2_SSH_KEY` | Private key (PEM contents) |
| `APP_SECRET_KEY` | Production Flask secret on EC2 |

---

## Deployment

### Option A — Render

1. Connect GitHub repo on [render.com](https://render.com)
2. Runtime: **Docker**, health path: `/health/ready`, port `5000`
3. Add **Deploy Hook** → copy URL → save as `RENDER_DEPLOY_HOOK` in GitHub secrets
4. Each push to `main` rebuilds via CI and triggers Render deploy

### Option B — AWS EC2

1. Ubuntu 22.04, open ports 22 + 80
2. Install Docker on the instance
3. Add `EC2_HOST`, `EC2_SSH_KEY`, `APP_SECRET_KEY` to GitHub secrets
4. Push to `main` — workflow pulls latest image and runs container on port 80

---

## Screenshots

See [docs/screenshots/README.md](docs/screenshots/README.md) for the checklist.

| Screenshot | Path |
|------------|------|
| Home | `docs/screenshots/home.png` |
| Login | `docs/screenshots/login.png` |
| GitHub Actions | `docs/screenshots/github-actions.png` |
| Docker Hub | `docs/screenshots/dockerhub.png` |
| Live deploy | `docs/screenshots/deployment.png` |

---

## Environment Variables

Copy `.env.example` to `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | (dev default) | Flask session secret |
| `ENVIRONMENT` | development | `production` enables HSTS |
| `APP_VERSION` | 1.0.0 | Shown in `/health` |
| `PORT` | 5000 | Listen port |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Health shows JSON not HTML | Use `/` for the website; `/health` is for monitoring |
| Docker daemon not running | Start Docker Desktop |
| CI coverage fails | Run `pytest --cov=website --cov=app` locally |
| Deploy skipped | Add `RENDER_DEPLOY_HOOK` or EC2 secrets |

---

## License

MIT — see [LICENSE](LICENSE). Security: [SECURITY.md](SECURITY.md).
