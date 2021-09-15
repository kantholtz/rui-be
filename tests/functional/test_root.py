from src.app import create_app


def test_root():
    """
    GIVEN   a Flask application
    WHEN    requesting GET /
    THEN    the response should contain "Server is up"
    """

    app = create_app()

    # Create a test client using the Flask application configured for testing
    with app.test_client() as test_client:
        response = test_client.get('/')

        assert response.status_code == 200
        assert b"Server is up" in response.data
