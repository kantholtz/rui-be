from flask import Flask
from flask_cors import CORS


def test_root():
    """
    GIVEN a Flask application
    WHEN  the '/' page is requested (GET)
    THEN  check that the response is valid
    """

    app = Flask(__name__)
    CORS(app)
    app.config['JSON_SORT_KEYS'] = False

    @app.route('/')
    def get_root():
        return 'Server is up'

    # Create a test client using the Flask application configured for testing
    with app.test_client() as test_client:
        response = test_client.get('/')

        assert response.status_code == 200
        assert b"Server is up" in response.data
