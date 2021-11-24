from copy import deepcopy

from rui_be.models.entity.entity import Entity
from rui_be.models.entity.post_entity import PostEntity, PostEntitySchema
from rui_be.models.node.deep_node import DeepNodeSchema, DeepNode
from tests.common import upload, ordered
from tests.fixtures.fixtures import deep_node_a, entity_a1, deep_node_c, deep_node_b, next_entity_id


def test_post_entity(client):
    ### GIVEN   a backend with data

    upload(client)

    ### WHEN    posting an entity

    post_entity = PostEntity(node_id=deep_node_a.id, name='A-2')

    response = client.post('http://localhost:5000/api/1.6.0/entities',
                           json=PostEntitySchema().dump(post_entity))

    ### THEN    the backend should respond with an HTTP 201
    ### AND     the backend should have persisted the entity

    assert response.status_code == 201

    nodes: list[dict] = client.get('http://localhost:5000/api/1.6.0/nodes').get_json()
    nodes: list[DeepNode] = DeepNodeSchema(many=True).load(nodes)

    expected_deep_node_a = deepcopy(deep_node_a)
    expected_deep_node_a.entities.append(Entity(id=next_entity_id,
                                                node_id=post_entity.node_id,
                                                name=post_entity.name,
                                                matches_count=0))

    assert ordered(nodes) == ordered([expected_deep_node_a, deep_node_b, deep_node_c])


def test_delete_entity(client):
    ### GIVEN   a backend with entities

    upload(client)

    ### WHEN    deleting a node's entity

    delete_response = client.delete(f'http://localhost:5000/api/1.6.0/entities/{entity_a1.id}')

    ### THEN    the backend should respond with an HTTP 200
    ### AND     the backend should have deleted the entity

    assert delete_response.status_code == 200

    nodes: list[dict] = client.get('http://localhost:5000/api/1.6.0/nodes').get_json()
    nodes: list[DeepNode] = DeepNodeSchema(many=True).load(nodes)

    expected_deep_node_a = deepcopy(deep_node_a)
    expected_deep_node_a.entities = [entity for entity in expected_deep_node_a.entities if entity.id != entity_a1.id]

    assert ordered(nodes) == ordered([expected_deep_node_a, deep_node_b, deep_node_c])
