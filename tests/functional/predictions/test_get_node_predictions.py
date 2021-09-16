from src.models.prediction.prediction_response import PredictionResponseSchema
from tests.functional.common import upload, ordered


def test_get_node_predictions(client):
    """
    GIVEN   a server with demo data
    WHEN    getting a node's predictions
    THEN    those predictions should be returned
    """

    upload(client)

    #
    # GET /nodes/0/predictions
    #

    response = client.get('http://localhost:5000/api/1.6.0/nodes/0/predictions')

    assert response.status_code == 200

    predictions = response.get_json()

    assert ordered(predictions) == ordered(expected_predictions)

    PredictionResponseSchema().load(predictions)


expected_predictions = {
    'totalPredictions': 3,
    'predictions': [
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
        },
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
            'candidate': 'Erat imperdiet sed euismod nisi porta lorem mollis .',
            'dismissed': False,
            'parentPredictions': [
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
            ],
            'synonymPredictions': []
        }
    ]
}
