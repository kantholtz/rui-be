from src.models.match.match import MatchSchema
from tests.functional.common import upload, ordered


def test_get_matches(client):
    """
    GIVEN   a server with demo data
    WHEN    getting all matches
    THEN    all matches should be returned
    """

    upload(client)

    #
    # GET /matches
    #

    response = client.get('http://localhost:5000/api/1.6.0/matches?entity=0')

    assert response.status_code == 200

    matches = response.get_json()

    assert ordered(matches) == ordered(expected_matches)

    MatchSchema(many=True).load(matches)


expected_matches = [
    {
        'entityId': 0,
        'ticket': 1000,
        'context': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua .',
        'mention': 'dolor',
        'mentionIndexes': [
            2,
            3
        ]
    },
    {
        'entityId': 0,
        'ticket': 1011,
        'context': 'Viverra tellus in hac habitasse platea dictumst .',
        'mention': 'habitasse platea',
        'mentionIndexes': [
            4,
            6
        ]
    }
]
