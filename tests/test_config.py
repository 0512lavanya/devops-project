"""Configuration tests."""

from website.app_factory import create_app
from website.config import Config


def test_config_defaults():
    assert Config.APP_NAME == "website-cicd-pipeline"
    assert Config.PORT == 5000
    assert hasattr(Config, "SECRET_KEY")


def test_custom_config_class():
    class TestConfig(Config):
        APP_VERSION = "2.0.0-test"
        ENVIRONMENT = "testing"

    app = create_app(TestConfig)
    with app.test_client() as client:
        data = client.get("/health").get_json()
        assert data["version"] == "2.0.0-test"
        assert data["environment"] == "testing"
