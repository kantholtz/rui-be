from src.models.node.deep_node import DeepNodeSchema
from tests.functional.common import upload, ordered


def test_delete_node(client):
    """
    GIVEN   a server with demo data
    WHEN    deleting a root node
    AND     deleting a child node
    THEN    those nodes should be deleted
    """

    upload(client)

    #
    # DELETE /nodes/0
    # DELETE /nodes/4
    #

    delete_0_response = client.delete('http://localhost:5000/api/1.6.0/nodes/0')
    delete_4_response = client.delete('http://localhost:5000/api/1.6.0/nodes/4')

    assert delete_0_response.status_code == 200
    assert delete_4_response.status_code == 200

    #
    # GET /nodes
    #

    get_response = client.get('http://localhost:5000/api/1.6.0/nodes')

    nodes = get_response.get_json()

    assert ordered(nodes) == ordered(expected_nodes)

    DeepNodeSchema(many=True).load(nodes)


expected_nodes = [
    {
        'id': 3,
        'parentId': None,
        'entities': [
            {
                'id': 3,
                'nodeId': 3,
                'name': 'B-1',
                'matchesCount': 1
            }
        ],
        'children': [
            {
                'id': 5,
                'parentId': 3,
                'entities': [
                    {
                        'id': 9,
                        'nodeId': 5,
                        'name': 'Bb-1',
                        'matchesCount': 1
                    },
                    {
                        'id': 10,
                        'nodeId': 5,
                        'name': 'Bb-2',
                        'matchesCount': 1
                    }
                ],
                'children': []
            }
        ]
    },
    {
        'id': 6,
        'parentId': None,
        'entities': [
            {
                'id': 11,
                'nodeId': 6,
                'name': 'C-1',
                'matchesCount': 1
            }
        ],
        'children': []
    }
]
