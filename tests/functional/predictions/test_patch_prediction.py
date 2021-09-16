from src.models.prediction.prediction_patch import PredictionPatch, PredictionPatchSchema
from src.models.prediction.prediction_response import PredictionResponseSchema
from tests.functional.common import upload, ordered


def test_patch_prediction(client):
    """
    GIVEN   a server with demo data
    WHEN    patching a prediction
    THEN    the prediction should be patched
    """

    upload(client)

    #
    # PATCH /predictions/Erat%20imperdiet%20sed%20euismod%20nisi%20porta%20lorem%20mollis%20.
    #

    prediction_patch = PredictionPatch(dismissed=True)
    prediction_patch = PredictionPatchSchema().dump(prediction_patch)

    assert prediction_patch == expected_prediction_patch

    url = 'http://localhost:5000/api/1.6.0/predictions/Erat%20imperdiet%20sed%20euismod%20nisi%20porta%20lorem%20mollis%20.'
    patch_prediction_response = client.patch(url, json=prediction_patch)

    assert patch_prediction_response.status_code == 200

    #
    # GET /predictions
    #

    get_response = client.get('http://localhost:5000/api/1.6.0/nodes/0/predictions')

    prediction_response = get_response.get_json()

    assert ordered(prediction_response) == ordered(expected_prediction_response)

    PredictionResponseSchema().load(prediction_response)


expected_prediction_patch = {
    'dismissed': True
}

expected_prediction_response = {
    'totalPredictions': 2,
    'predictions': [
        {
            'candidate': 'Tempor orci dapibus ultrices in iaculis nunc sed .',
            'dismissed': False,
            'parentPredictions': [],
            'synonymPredictions': [
                {
                    'score': 1.0,
                    'node': {
                        'id': 0,
                        'parentId': None,
                        'entities': [
                            {
                                'id': 0,
                                'nodeId': 0,
                                'name': 'A-1',
                                'matchesCount': 2
                            }
                        ]
                    }
                }
            ]
        },
        {
            'candidate': 'Porta lorem mollis aliquam ut porttitor leo a diam .',
            'dismissed': False,
            'parentPredictions': [],
            'synonymPredictions': [
                {
                    'score': 1.0,
                    'node': {
                        'id': 0,
                        'parentId': None,
                        'entities': [
                            {
                                'id': 0,
                                'nodeId': 0,
                                'name': 'A-1',
                                'matchesCount': 2
                            }
                        ]
                    }
                }
            ]
        }
    ]
}
