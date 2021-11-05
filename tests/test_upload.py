from tests.common import upload


def test_upload(client):
    """
    GIVEN   a server with no data
    WHEN    uploading a Symptax Upload ZIP
    THEN    the server should respond with 200 OK
    """

    upload(client)
