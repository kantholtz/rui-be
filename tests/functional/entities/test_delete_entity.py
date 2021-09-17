from src.rui_be.models.node.deep_node import DeepNodeSchema
from tests.functional.common import upload, ordered


def test_delete_entity(client):
    """
    GIVEN   a server with demo data
    WHEN    deleting a node's first entity
    AND     deleting a node's last entity
    THEN    those entities should be deleted
    """

    upload(client)

    #
    # DELETE /entities/4
    #

    delete_entity_4_response = client.delete('http://localhost:5000/api/1.6.0/entities/4')

    assert delete_entity_4_response.status_code == 200

    #
    # DELETE /entities/8
    #

    delete_entity_8_response = client.delete('http://localhost:5000/api/1.6.0/entities/8')

    assert delete_entity_8_response.status_code == 200

    #
    # GET /nodes
    #

    get_response = client.get('http://localhost:5000/api/1.6.0/nodes')

    nodes = get_response.get_json()

    assert ordered(nodes) == ordered(expected_nodes)

    DeepNodeSchema(many=True).load(nodes)


expected_nodes = [
    {
        'id': 0,
        'parentId': None,
        'entities': [
            {
                'id': 0,
                'nodeId': 0,
                'name': 'A-1',
                'matchesCount': 2
            }
        ],
        'children': [
            {
                'id': 1,
                'parentId': 0,
                'entities': [
                    {
                        'id': 1,
                        'nodeId': 1,
                        'name': 'Aa-1',
                        'matchesCount': 2
                    }
                ],
                'children': []
            },
            {
                'id': 2,
                'parentId': 0,
                'entities': [
                    {
                        'id': 2,
                        'nodeId': 2,
                        'name': 'Ab-1',
                        'matchesCount': 2
                    }
                ],
                'children': []
            }
        ]
    },
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
                'id': 4,
                'parentId': 3,
                'entities': [
                    {
                        'id': 5,
                        'nodeId': 4,
                        'name': 'Ba-2',
                        'matchesCount': 1
                    },
                    {
                        'id': 6,
                        'nodeId': 4,
                        'name': 'Ba-3',
                        'matchesCount': 0
                    },
                    {
                        'id': 7,
                        'nodeId': 4,
                        'name': 'Ba-4',
                        'matchesCount': 1
                    }
                ],
                'children': []
            },
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
