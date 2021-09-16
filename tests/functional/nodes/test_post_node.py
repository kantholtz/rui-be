from src.models.entity.post_node_entity import PostNodeEntity
from src.models.node.deep_node import DeepNodeSchema
from src.models.node.post_node import PostNode, PostNodeSchema
from tests.functional.common import upload


def test_post_node(client):
    upload(client)

    #
    # POST /nodes
    #

    post_node = PostNode(
        parent_id=None,
        entities=[
            PostNodeEntity('D-1'),
            PostNodeEntity('D-2')
        ]
    )

    post_node_json = PostNodeSchema().dump(post_node)

    assert post_node_json == expected_post_node_json

    response = client.post('http://localhost:5000/api/1.6.0/nodes', json=post_node_json)

    assert response.status_code == 201

    #
    # GET /nodes
    #

    get_response = client.get('http://localhost:5000/api/1.6.0/nodes')

    get_response_json = get_response.get_json()

    assert len(get_response_json) == 4
    assert get_response_json[-1] == expected_get_response_json

    DeepNodeSchema(many=True).load(get_response_json)


expected_post_node_json = {
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

expected_get_response_json = {
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
