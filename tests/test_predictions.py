import urllib

from rui_be.models.prediction.prediction_patch import PredictionPatch, PredictionPatchSchema
from rui_be.models.prediction.prediction_response import PredictionResponseSchema, PredictionResponse
from tests.common import upload
from tests.fixtures.fixtures import deep_node_a


def test_get_predictions(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    getting a node's predictions

    response = client.get(f'http://localhost:5000/api/1.6.0/nodes/{deep_node_a.id}/predictions')

    ### THEN    the backend should respond with an HTTP 200
    ### AND     the response should contain the node's predictions

    assert response.status_code == 200

    prediction_response: dict = response.get_json()
    prediction_response: PredictionResponse = PredictionResponseSchema().load(prediction_response)

    assert prediction_response.total_predictions == 3
    assert prediction_response.predictions[0].total_score > prediction_response.predictions[1].total_score
    assert prediction_response.predictions[1].total_score > prediction_response.predictions[2].total_score


def test_patch_prediction(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    patching a prediction

    prediction_patch = PredictionPatch(dismissed=True)
    candidate = 'Erat imperdiet sed euismod nisi porta lorem mollis .'
    url_candidate = urllib.parse.quote(candidate)

    patch_prediction_response = client.patch(f'http://localhost:5000/api/1.6.0/predictions/{url_candidate}',
                                             json=PredictionPatchSchema().dump(prediction_patch))

    ### THEN    the backend should respond with an HTTP 200
    ### AND     the backend should have persisted the patch

    assert patch_prediction_response.status_code == 200

    prediction_response: dict = client.get('http://localhost:5000/api/1.6.0/nodes/0/predictions').get_json()
    prediction_response: PredictionResponse = PredictionResponseSchema().load(prediction_response)

    assert prediction_response.total_predictions == 2
