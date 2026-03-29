import pytest
import pandas as pd
from unittest.mock import MagicMock


@pytest.fixture
def sample_df():
    """Minimal retail orders DataFrame for unit tests."""
    return pd.DataFrame({
        "order_id": [1, 2, 3, 4, 5],
        "customer_id": ["C1", "C2", "C1", "C3", "C2"],
        "category": ["Electronics", "Clothing", "Electronics", "Food", "Clothing"],
        "order_total": [150.0, 75.0, 200.0, 50.0, 125.0],
        "order_date": pd.to_datetime([
            "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"
        ]),
    })


@pytest.fixture
def app():
    """Flask test app using the enhanced factory."""
    try:
        from app_enhanced import create_app
        application = create_app("testing")
        application.config.update({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "test-secret-key",
        })
        return application
    except Exception:
        import flask
        application = flask.Flask(__name__)
        application.config["TESTING"] = True
        return application


@pytest.fixture
def client(app):
    return app.test_client()
