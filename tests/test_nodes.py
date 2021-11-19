from rui_be.models.node.deep_node import DeepNodeSchema
from rui_be.models.node.node_patch import NodePatch, NodePatchSchema
from tests.common import upload, ordered
from tests.fixtures.fixtures import node_a, node_c, node_b, node_ba


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

    post_root_node_response = client.post('http://localhost:5000/api/1.6.0/nodes',
                                          json=post_root_node)

    ### THEN    the backend should respond with an HTTP 201

    assert post_root_node_response.status_code == 201

    ### THEN    the backend should have persisted the node

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

    post_child_node_response = client.post('http://localhost:5000/api/1.6.0/nodes',
                                           json=post_child_node)

    ### THEN    the backend should respond with an HTTP 201

    assert post_child_node_response.status_code == 201

    ### THEN    the backend should have persisted the node

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


def test_patch_root_node(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    patching a root node

    root_node_patch = {'parentId': 0}

    patch_root_node_response = client.patch('http://localhost:5000/api/1.6.0/nodes/3',
                                            json=root_node_patch)

    ### THEN    the backend should respond with an HTTP 200

    assert patch_root_node_response.status_code == 200

    ### THEN    the backend should have persisted the patch

    get_response = client.get('http://localhost:5000/api/1.6.0/nodes')
    nodes = get_response.get_json()

    expected_node_a = node_a.copy()
    expected_node_b = node_b.copy()
    expected_node_b['parentId'] = 0
    expected_node_a['children'].append(expected_node_b)

    expected_nodes = [expected_node_a, node_c]

    assert ordered(nodes) == ordered(expected_nodes)


def test_patch_child_node(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    patching a child node

    child_node_patch = {'parentId': 0}

    patch_child_node_response = client.patch('http://localhost:5000/api/1.6.0/nodes/4',
                                             json=child_node_patch)

    ### THEN    the backend should respond with an HTTP 200

    assert patch_child_node_response.status_code == 200

    ### THEN    the backend should have persisted the patch

    get_response = client.get('http://localhost:5000/api/1.6.0/nodes')
    nodes = get_response.get_json()

    expected_node_b = node_b.copy()
    del expected_node_b['children'][0]

    expected_node_a = node_a.copy()
    expected_node_a['children'].append(node_ba)
    expected_node_a['children'][-1]['parentId'] = 0

    expected_nodes = [expected_node_a, expected_node_b, node_c]

    assert ordered(nodes) == ordered(expected_nodes)


def test_delete_root_node(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    deleting a root node

    delete_0_response = client.delete('http://localhost:5000/api/1.6.0/nodes/0')

    ### THEN    the backend should respond with an HTTP 200

    assert delete_0_response.status_code == 200

    ### THEN    the backend should have deleted the node

    get_response = client.get('http://localhost:5000/api/1.6.0/nodes')

    nodes = get_response.get_json()

    expected_nodes = [node_b, node_c]

    assert ordered(nodes) == ordered(expected_nodes)


def test_delete_child_node(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    deleting a child node

    delete_0_response = client.delete('http://localhost:5000/api/1.6.0/nodes/1')

    ### THEN    the backend should respond with an HTTP 200

    assert delete_0_response.status_code == 200

    ### THEN    the backend should have deleted the node

    get_response = client.get('http://localhost:5000/api/1.6.0/nodes')

    nodes = get_response.get_json()

    expected_node_a = node_a.copy()
    del expected_node_a['children'][0]

    expected_nodes = [expected_node_a, node_b, node_c]

    assert ordered(nodes) == ordered(expected_nodes)
