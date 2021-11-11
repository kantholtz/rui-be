from rui_be.models.entity.post_entity import PostEntity, PostEntitySchema
from rui_be.models.node.deep_node import DeepNodeSchema
from tests.common import upload, ordered


def test_post_entity(client):
    """
    GIVEN   a server with demo data
    WHEN    posting an entity for a root node
    AND     posting an entity for a child node
    THEN    those entities should be added
    """

    upload(client)

    #
    # POST /entities
    #

    post_root_entity = PostEntity(
        node_id=0,
        name='A-2'
    )

    post_root_entity_json = PostEntitySchema().dump(post_root_entity)

    assert post_root_entity_json == expected_post_root_entity_json

    post_root_entity_response = client.post('http://localhost:5000/api/1.6.0/entities', json=post_root_entity_json)

    assert post_root_entity_response.status_code == 201

    #
    # POST /entities
    #

    post_child_entity = PostEntity(
        node_id=1,
        name='Aa-2'
    )

    post_child_entity_json = PostEntitySchema().dump(post_child_entity)

    assert post_child_entity_json == expected_post_child_entity_json

    post_child_entity_response = client.post('http://localhost:5000/api/1.6.0/entities', json=post_child_entity_json)

    assert post_child_entity_response.status_code == 201

    #
    # GET /nodes
    #

    get_response = client.get('http://localhost:5000/api/1.6.0/nodes')

    nodes = get_response.get_json()

    assert ordered(nodes) == ordered(expected_nodes)

    DeepNodeSchema(many=True).load(nodes)


expected_post_root_entity_json = {
    'nodeId': 0,
    'name': 'A-2'
}

expected_post_child_entity_json = {
    'nodeId': 1,
    'name': 'Aa-2'
}

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
            },
            {
                'id': 12,
                'nodeId': 0,
                'name': 'A-2',
                'matchesCount': 0
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
                    },
                    {
                        'id': 13,
                        'nodeId': 1,
                        'name': 'Aa-2',
                        'matchesCount': 0
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
