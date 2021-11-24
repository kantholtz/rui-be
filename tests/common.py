def upload(client):
    with open('fixtures/symptax_upload_v7_random.zip', 'rb') as fd:
        data = {'symptaxUploadZip': (fd, 'symptax_upload_v7_random.zip')}

        response = client.put('http://localhost:5000/api/1.6.0/upload',
                              content_type='multipart/form-data',
                              data=data)

    assert response.status_code == 200


def ordered(obj):
    """ Recursively compare dicts ignoring order """

    ### See https://stackoverflow.com/questions/25851183/how-to-compare-two-json-objects-with-the-same-elements-in-a-different-order-equa

    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())

    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)

    else:
        return obj
