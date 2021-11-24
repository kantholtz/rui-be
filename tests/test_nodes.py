from copy import deepcopy

from rui_be.models.entity.entity import Entity
from rui_be.models.entity.post_node_entity import PostNodeEntity
from rui_be.models.node.deep_node import DeepNodeSchema, DeepNode
from rui_be.models.node.node_patch import NodePatch, NodePatchSchema
from rui_be.models.node.post_node import PostNode, PostNodeSchema
from tests.common import upload
from tests.fixtures.fixtures import node_a, node_c, node_b, node_ba, next_node_id, next_entity_id, node_aa


def test_get_nodes(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    getting all nodes

    response = client.get('http://localhost:5000/api/1.6.0/nodes')

    ### THEN    the backend should respond with an HTTP 200
    ### AND     the response should contain all nodes

    assert response.status_code == 200

    nodes = response.get_json()
    nodes = DeepNodeSchema(many=True).load(nodes)

    assert sorted(nodes) == sorted([node_a, node_b, node_c])


def test_post_root_node(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    posting a root node

    post_node = PostNode(
        parent_id=None,
        entities=[
            PostNodeEntity(name='D-1'),
            PostNodeEntity(name='D-2')
        ]
    )

    response = client.post('http://localhost:5000/api/1.6.0/nodes',
                           json=PostNodeSchema().dump(post_node))

    ### THEN    the backend should respond with an HTTP 201
    ### AND     the backend should have persisted the node

    assert response.status_code == 201

    nodes = client.get('http://localhost:5000/api/1.6.0/nodes').get_json()
    nodes = DeepNodeSchema(many=True).load(nodes)

    expected_new_node = DeepNode(
        id=next_node_id,
        parent_id=None,
        entities=[
            Entity(id=next_entity_id, node_id=next_node_id, name='D-1', matches_count=0),
            Entity(id=next_entity_id + 1, node_id=next_node_id, name='D-2', matches_count=0)
        ],
        children=[]
    )

    assert sorted(nodes) == sorted([node_a, node_b, node_c, expected_new_node])


def test_post_child_node(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    posting a child node

    post_node = PostNode(
        parent_id=node_a.id,
        entities=[PostNodeEntity(name='Ac-1')]
    )

    response = client.post('http://localhost:5000/api/1.6.0/nodes',
                           json=PostNodeSchema().dump(post_node))

    ### THEN    the backend should respond with an HTTP 201
    ### AND     the backend should have persisted the node

    assert response.status_code == 201

    nodes = client.get('http://localhost:5000/api/1.6.0/nodes').get_json()
    nodes = DeepNodeSchema(many=True).load(nodes)

    expected_new_node = DeepNode(
        id=next_node_id,
        parent_id=node_a.id,
        entities=[Entity(id=next_entity_id, node_id=next_node_id, name='Ac-1', matches_count=0)],
        children=[]
    )

    expected_node_a = deepcopy(node_a)
    expected_node_a.children.append(expected_new_node)

    assert sorted(nodes) == sorted([expected_node_a, node_b, node_c])


def test_patch_root_node(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    patching a root node

    node_patch = NodePatch(parent_id=node_a.id)

    response = client.patch(f'http://localhost:5000/api/1.6.0/nodes/{node_b.id}',
                            json=NodePatchSchema().dump(node_patch))

    ### THEN    the backend should respond with an HTTP 200
    ### AND     the backend should have persisted the patch

    assert response.status_code == 200

    nodes = client.get('http://localhost:5000/api/1.6.0/nodes').get_json()
    nodes = DeepNodeSchema(many=True).load(nodes)

    expected_node_b = deepcopy(node_b)
    expected_node_b.parent_id = node_a.id

    expected_node_a = deepcopy(node_a)
    expected_node_a.children.append(expected_node_b)

    assert sorted(nodes) == sorted([expected_node_a, node_c])


def test_patch_child_node(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    patching a child node

    child_node_patch = NodePatch(parent_id=node_a.id)

    response = client.patch(f'http://localhost:5000/api/1.6.0/nodes/{node_ba.id}',
                            json=NodePatchSchema().dump(child_node_patch))

    ### THEN    the backend should respond with an HTTP 200
    ### AND     the backend should have persisted the patch

    assert response.status_code == 200

    nodes = client.get('http://localhost:5000/api/1.6.0/nodes').get_json()
    nodes = DeepNodeSchema(many=True).load(nodes)

    expected_node_a: DeepNode = deepcopy(node_a)
    expected_node_b: DeepNode = deepcopy(node_b)

    expected_node_ba: DeepNode = expected_node_b.children[0]
    del expected_node_b.children[0]
    expected_node_a.children.append(expected_node_ba)
    expected_node_ba.parent_id = expected_node_a.id

    assert sorted(nodes) == sorted([expected_node_a, expected_node_b, node_c])


def test_delete_root_node(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    deleting a root node

    response = client.delete(f'http://localhost:5000/api/1.6.0/nodes/{node_a.id}')

    ### THEN    the backend should respond with an HTTP 200
    ### AND     the backend should have deleted the node

    assert response.status_code == 200

    nodes = client.get('http://localhost:5000/api/1.6.0/nodes').get_json()
    nodes = DeepNodeSchema(many=True).load(nodes)

    assert sorted(nodes) == sorted([node_b, node_c])


def test_delete_child_node(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    deleting a child node

    response = client.delete(f'http://localhost:5000/api/1.6.0/nodes/{node_aa.id}')

    ### THEN    the backend should respond with an HTTP 200
    ### AND     the backend should have deleted the node

    assert response.status_code == 200

    nodes = client.get('http://localhost:5000/api/1.6.0/nodes').get_json()
    nodes = DeepNodeSchema(many=True).load(nodes)

    expected_node_a = deepcopy(node_a)
    del expected_node_a.children[0]

    assert sorted(nodes) == sorted([expected_node_a, node_b, node_c])
