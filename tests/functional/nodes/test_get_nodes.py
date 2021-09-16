from src.models.node.deep_node import DeepNodeSchema
from tests.functional.common import upload, ordered


def test_get_nodes(client):
    upload(client)

    #
    # GET /nodes
    #

    response = client.get('http://localhost:5000/api/1.6.0/nodes')

    assert response.status_code == 200

    nodes = response.get_json()

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
                        'id': 4,
                        'nodeId': 4,
                        'name': 'Ba-1',
                        'matchesCount': 1
                    },
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
                    },
                    {
                        'id': 8,
                        'nodeId': 4,
                        'name': 'Ba-5',
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
