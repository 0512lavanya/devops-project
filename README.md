# LifeStream - Blood Donation Management System (DevOps Lab)

LifeStream is a production-ready Blood Donation Management System wrapped in a comprehensive DevOps pipeline. This project serves as a practical demonstration of modern software delivery practices, including containerization, CI/CD, and Infrastructure as Code.

## 🚀 Project Overview

The core application is built with **Python (Flask)** and **Vanilla CSS/JS** on the frontend, focusing on a premium UI/UX design.

### Features:
- Find Donors based on blood type and location.
- Register as a new Donor.
- Broadcast Urgent Blood Requests.
- RESTful Health Check Endpoint (`/health`).

## 🏗️ Advanced Architecture (100/10)

This project has been upgraded to a FAANG-tier microservices architecture:
- **Web Tier**: Flask (Python) + HTML/CSS/JS.
- **Data Tier**: PostgreSQL (Primary DB) + Redis (In-memory Cache for blazing fast queries).
- **Reverse Proxy**: Nginx (Handles incoming traffic on port 80 and serves static files).
- **Observability**: Prometheus (Scrapes metrics) + Grafana (Visualizes metrics).
- **Containerization**: Docker & Docker Compose (6 interconnected containers).
- **CI/CD Pipeline**: GitHub Actions.
- **Deployment**: Render (Infrastructure as Code via `render.yaml`).
- **DevEx**: `Makefile` for streamlined developer operations.

## 📁 Project Structure

```
/app                # Flask Backend Application
  __init__.py       # App factory with Prometheus Middleware
  models.py         # Database schema
  routes.py         # App routes with Redis caching
/nginx              # Reverse Proxy Config
  nginx.conf
/static             # Frontend static assets
/templates          # HTML Templates
/tests              # Pytest Unit Tests
Dockerfile          # Multi-stage container build
docker-compose.yml  # Full production stack (App, DB, Redis, Nginx, Prometheus, Grafana)
prometheus.yml      # Metrics scraping config
Makefile            # Developer Experience tooling
render.yaml         # Render IaC deployment config
.github/workflows/  # CI/CD Pipeline definition
```

## 🛠️ Setup Instructions (Local & Docker)

### Option 1: Docker (Highly Recommended)
You can spin up the entire enterprise stack (App, PostgreSQL, Redis, Nginx, Prometheus, Grafana) using the included Makefile.

1. Ensure Docker Desktop is running.
2. Build and start the containers using the Makefile:
   ```bash
   make up
   ```
3. Access the services:
   - **Main App (via Nginx)**: `http://localhost`
   - **Grafana Dashboards**: `http://localhost:3000` (User: admin / Pass: admin)
   - **Prometheus Metrics**: `http://localhost:9090`
4. Stop the application:
   ```bash
   make down
   ```

### Option 2: Local Python Environment
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python run.py
   ```

## 🔄 CI/CD Pipeline

The project uses GitHub Actions (`.github/workflows/ci-cd.yml`) to ensure code quality and automate deployments.

**Workflow Stages:**
1. **Test**: Triggers on `push` and `pull_request` to `main`. Installs dependencies and runs `pytest`.
2. **Build & Deploy**: Only triggers if tests pass on the `main` branch. Builds the Docker Image and theoretically deploys it (simulated in this lab).

## 🚀 Deployment (Render)

This project is configured for automated deployment to Render using the `render.yaml` Blueprint.

1. Push your repository to GitHub.
2. Sign in to [Render](https://render.com/).
3. Go to the **Blueprints** tab and connect your GitHub repository.
4. Render will automatically detect `render.yaml`, provision a PostgreSQL database, build the Docker image, and deploy the web service.

---
*Built as a demonstration of CI/CD, Containerization, and production-level Python web development.*
