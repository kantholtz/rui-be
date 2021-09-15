from src.models.node.deep_node import DeepNodeSchema
from tests.functional.common import upload


def test_get_nodes(client):
    """
    GIVEN   a server with data
    WHEN    requesting all nodes
    THEN    the server should respond with 200 OK
    AND     return the nodes
    """

    upload(client)

    response = client.get('http://localhost:5000/api/1.6.0/nodes')

    nodes_json = response.get_json()
    nodes = DeepNodeSchema(many=True).load(nodes_json)

    assert response.status_code == 200
    assert len(nodes) == 3

    assert nodes[0].id == 0
    assert nodes[0].parent_id is None

    assert len(nodes[0].entities) == 1
    assert nodes[0].entities[0].id == 0
    assert nodes[0].entities[0].node_id == 0
    assert nodes[0].entities[0].name == 'A-1'
    assert nodes[0].entities[0].matches_count == 2

    assert len(nodes[0].children) == 2
    assert nodes[0].children[0].entities[0].name == 'Aa-1'
