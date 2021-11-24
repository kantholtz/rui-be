from rui_be.models.match.match import MatchSchema
from tests.common import upload
from tests.fixtures.fixtures import entity_a1, match_a12, match_a11


def test_get_matches(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    getting an entity's matches

    response = client.get(f'http://localhost:5000/api/1.6.0/matches?entity={entity_a1.id}')

    ### THEN    the backend should respond with an HTTP 200
    ### AND     the response should contain all matches

    assert response.status_code == 200

    matches = response.get_json()
    matches = MatchSchema(many=True).load(matches)

    assert sorted(matches) == sorted([match_a11, match_a12])
