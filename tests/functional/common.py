def upload(client):
    with open('fixtures/symptax_upload_v6_2_random.zip', 'rb') as fd:
        data = {'symptaxUploadZip': (fd, 'symptax_upload_v6_2_random.zip')}

        response = client.put('http://localhost:5000/api/1.6.0/upload',
                              content_type='multipart/form-data',
                              data=data)

    assert response.status_code == 200
