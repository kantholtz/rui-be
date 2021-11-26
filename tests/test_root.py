def test_root(client):
    ### WHEN    getting /

    response = client.get('/')

    ### THEN    the backend should respond with an HTTP 200
    ### AND     the response should state "Server is up"

    assert response.status_code == 200
    assert b"Server is up" in response.data
