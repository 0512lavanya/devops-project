"""Flask application factory."""

import logging
from datetime import UTC, datetime
from pathlib import Path

from flask import Flask, current_app, jsonify, render_template, request

from website.config import Config

PROJECT_ROOT = Path(__file__).resolve().parent.parent

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure structured application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        force=True,
    )


def create_app(config_class: type = Config) -> Flask:
    """Create and configure the Flask application."""
    configure_logging()

    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "templates"),
        static_folder=str(PROJECT_ROOT / "static"),
    )
    app.config.from_object(config_class)

    @app.after_request
    def set_security_headers(response):
        """Add security headers to every response."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if app.config["ENVIRONMENT"] == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        message = None
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            logger.info("Login attempt for user: %s", username or "(empty)")
            if username and password:
                message = f"Welcome, {username}! (Demo mode — no authentication backend)"
            else:
                message = "Please enter both username and password."
        return render_template("login.html", message=message)

    @app.route("/health")
    def health():
        """Full health status (monitoring dashboards)."""
        return jsonify(_health_payload()), 200

    @app.route("/health/live")
    def health_live():
        """Liveness probe — process is running."""
        return jsonify({"status": "alive"}), 200

    @app.route("/health/ready")
    def health_ready():
        """Readiness probe — app can serve traffic."""
        return jsonify(_health_payload()), 200

    @app.route("/metrics")
    def metrics():
        """Basic application metrics (Prometheus-style text, simplified)."""
        version = app.config["APP_VERSION"]
        environment = app.config["ENVIRONMENT"]
        lines = [
            "# HELP app_info Application metadata",
            "# TYPE app_info gauge",
            f'app_info{{version="{version}",environment="{environment}"}} 1',
        ]
        return "\n".join(lines) + "\n", 200, {"Content-Type": "text/plain; version=0.0.4"}

    logger.info(
        "Application started: %s v%s [%s]",
        app.config["APP_NAME"],
        app.config["APP_VERSION"],
        app.config["ENVIRONMENT"],
    )
    return app


def _health_payload() -> dict:
    return {
        "status": "healthy",
        "service": current_app.config["APP_NAME"],
        "version": current_app.config["APP_VERSION"],
        "environment": current_app.config["ENVIRONMENT"],
        "timestamp": datetime.now(UTC).isoformat(),
    }
