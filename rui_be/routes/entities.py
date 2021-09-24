import draug.homag.graph
from flask import Blueprint, request

from rui_be import state
from rui_be.models.entity.post_entity import PostEntity, PostEntitySchema

entities = Blueprint('entities', __name__)


@entities.route('/api/1.6.0/entities', methods=['POST'])
def post_entity() -> tuple[str, int]:
    request_data: dict = request.get_json()

    new_entity: PostEntity = PostEntitySchema().load(request_data)

    state.graph.add_entity(new_entity.node_id, draug.homag.graph.Entity(new_entity.name))

    return '', 201


@entities.route('/api/1.6.0/entities/<int:entity_id>', methods=['DELETE'])
def delete_entity(entity_id: int) -> str:
    state.graph.del_entity(entity_id)

    return ''
