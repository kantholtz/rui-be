from src.models.entity.post_node_entity import PostNodeEntity
from src.models.node.deep_node import DeepNodeSchema
from src.models.node.post_node import PostNode, PostNodeSchema
from tests.functional.common import upload, ordered


def test_post_node(client):
    """
    GIVEN   a server with demo data
    WHEN    posting a root node
    AND     posting a child node
    THEN    those nodes should be added
    """

    upload(client)

    #
    # POST /nodes
    #

    post_root_node = PostNode(
        parent_id=None,
        entities=[
            PostNodeEntity('D-1'),
            PostNodeEntity('D-2')
        ]
    )

    post_root_node = PostNodeSchema().dump(post_root_node)

    assert post_root_node == expected_post_root_node

    post_root_node_response = client.post('http://localhost:5000/api/1.6.0/nodes', json=post_root_node)

    assert post_root_node_response.status_code == 201

    #
    # POST /nodes
    #

    post_child_node = PostNode(
        parent_id=0,
        entities=[
            PostNodeEntity('Ac-1')
        ]
    )

    post_child_node = PostNodeSchema().dump(post_child_node)

    assert post_child_node == expected_post_child_node

    post_child_node_response = client.post('http://localhost:5000/api/1.6.0/nodes', json=post_child_node)

    assert post_child_node_response.status_code == 201

    #
    # GET /nodes
    #

    get_response = client.get('http://localhost:5000/api/1.6.0/nodes')

    nodes = get_response.get_json()

    assert ordered(nodes) == ordered(expected_nodes)

    DeepNodeSchema(many=True).load(nodes)


expected_post_root_node = {
    'parentId': None,
    'entities': [
        {
            'name': 'D-1'
        },
        {
            'name': 'D-2'
        }
    ]
}

expected_post_child_node = {
    'parentId': 0,
    'entities': [
        {
            'name': 'Ac-1'
        }
    ]
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
                'id': 8,
                'parentId': 0,
                'entities': [
                    {
                        'id': 14,
                        'nodeId': 8,
                        'name': 'Ac-1',
                        'matchesCount': 0
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
    },
    {
        'id': 7,
        'parentId': None,
        'entities': [
            {
                'id': 12,
                'nodeId': 7,
                'name': 'D-1',
                'matchesCount': 0
            },
            {
                'id': 13,
                'nodeId': 7,
                'name': 'D-2',
                'matchesCount': 0
            }
        ],
        'children': []
    }
]
