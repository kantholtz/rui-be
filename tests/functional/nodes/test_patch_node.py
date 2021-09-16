from src.models.node.deep_node import DeepNodeSchema
from src.models.node.node_patch import NodePatch, NodePatchSchema
from tests.functional.common import upload


def test_patch_node(client):
    upload(client)

    #
    # PATCH /nodes/3
    #

    node_patch = NodePatch(parent_id=0)
    node_patch_json = NodePatchSchema().dump(node_patch)

    assert node_patch_json == expected_node_patch_json

    response = client.patch('http://localhost:5000/api/1.6.0/nodes/3', json=node_patch_json)

    assert response.status_code == 200

    #
    # GET /nodes
    #

    get_response = client.get('http://localhost:5000/api/1.6.0/nodes')

    get_response_json = get_response.get_json()

    assert get_response_json == expected_get_response_json

    DeepNodeSchema(many=True).load(get_response_json)


expected_node_patch_json = {
    'parentId': 0
}

expected_get_response_json = [
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
            },
            {
                'id': 3,
                'parentId': 0,
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
