def test_root(client):
    """
    GIVEN   a Flask application
    WHEN    requesting GET /
    THEN    the response should contain "Server is up"
    """

    response = client.get('/')

    assert response.status_code == 200
    assert b"Server is up" in response.data
