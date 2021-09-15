import pytest

from src.app import create_app


@pytest.fixture
def client():
    app = create_app({'TESTING': True})

    return app.test_client()
