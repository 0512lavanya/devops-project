"""Application configuration from environment variables."""

import os


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    APP_NAME = os.environ.get("APP_NAME", "website-cicd-pipeline")
    APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
    PORT = int(os.environ.get("PORT", 5000))
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

    # Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PREFERRED_URL_SCHEME = "https" if ENVIRONMENT == "production" else "http"
