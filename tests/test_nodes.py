from rui_be.models.entity.post_node_entity import PostNodeEntity
from rui_be.models.node.deep_node import DeepNodeSchema
from rui_be.models.node.node_patch import NodePatch, NodePatchSchema
from rui_be.models.node.post_node import PostNode, PostNodeSchema
from tests.common import upload, ordered
from tests.fixtures.fixtures import node_a, node_c, node_b


def test_get_nodes(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    getting all nodes

    response = client.get('http://localhost:5000/api/1.6.0/nodes')

    ### THEN    the backend should respond with an HTTP 200
    ### AND     the response should contain all nodes

    assert response.status_code == 200

    nodes = response.get_json()

    assert ordered(nodes) == ordered([node_a, node_b, node_c])

    DeepNodeSchema(many=True).load(nodes)


def test_post_root_node(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    posting a root node

    post_root_node = {
        'parentId': None,
        'entities': [
            {'name': 'D-1'},
            {'name': 'D-2'}
        ]
    }

    post_root_node_response = client.post('http://localhost:5000/api/1.6.0/nodes', json=post_root_node)

    ### THEN    the backend should respond with an HTTP 201

    assert post_root_node_response.status_code == 201

    ### THEN    the backend should have persisted the root node

    get_response = client.get('http://localhost:5000/api/1.6.0/nodes')
    nodes = get_response.get_json()

    expected_node_d = {
        'id': 7,
        'parentId': None,
        'entities': [
            {'id': 12, 'nodeId': 7, 'name': 'D-1', 'matchesCount': 0},
            {'id': 13, 'nodeId': 7, 'name': 'D-2', 'matchesCount': 0}
        ],
        'children': []
    }

    expected_nodes = [node_a, node_b, node_c, expected_node_d]

    assert ordered(nodes) == ordered(expected_nodes)


def test_post_child_node(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    posting a child node

    post_child_node = {
        'parentId': 0,
        'entities': [{'name': 'Ac-1'}]
    }

    post_child_node_response = client.post('http://localhost:5000/api/1.6.0/nodes', json=post_child_node)

    ### THEN    the backend should respond with an HTTP 201

    assert post_child_node_response.status_code == 201

    ### THEN    the backend should have persisted the root node

    get_response = client.get('http://localhost:5000/api/1.6.0/nodes')
    nodes = get_response.get_json()

    expected_node_ac = {
        'id': 7,
        'parentId': 0,
        'entities': [
            {'id': 12, 'nodeId': 7, 'name': 'Ac-1', 'matchesCount': 0}
        ],
        'children': []
    }

    expected_node_a = node_a.copy()
    expected_node_a['children'].append(expected_node_ac)

    expected_nodes = [expected_node_a, node_b, node_c]

    assert ordered(nodes) == ordered(expected_nodes)


def test_patch_node(client):
    """
    GIVEN   a server with demo data
    WHEN    patching a root node
    AND     patching a child node
    THEN    those nodes should be patched
    """

    upload(client)

    #
    # PATCH /nodes/3
    #

    root_node_patch = NodePatch(parent_id=0)
    root_node_patch = NodePatchSchema().dump(root_node_patch)

    assert root_node_patch == expected_root_node_patch

    patch_root_node_response = client.patch('http://localhost:5000/api/1.6.0/nodes/3', json=root_node_patch)

    assert patch_root_node_response.status_code == 200

    #
    # PATCH /nodes/4
    #

    child_node_patch = NodePatch(parent_id=None)
    child_node_patch = NodePatchSchema().dump(child_node_patch)

    assert child_node_patch == expected_child_node_patch

    patch_child_node_response = client.patch('http://localhost:5000/api/1.6.0/nodes/4', json=child_node_patch)

    assert patch_child_node_response.status_code == 200

    #
    # GET /nodes
    #

    get_response = client.get('http://localhost:5000/api/1.6.0/nodes')

    nodes = get_response.get_json()

    assert ordered(nodes) == ordered(expected_nodes)

    DeepNodeSchema(many=True).load(nodes)


expected_root_node_patch = {
    'parentId': 0
}

expected_child_node_patch = {
    'parentId': None
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
        'id': 4,
        'parentId': None,
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
