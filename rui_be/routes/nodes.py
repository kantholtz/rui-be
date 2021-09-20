import draug.homag.graph
from flask import Blueprint, Response, request, jsonify

from rui_be import state
from rui_be.models.entity.entity import Entity
from rui_be.models.node.deep_node import DeepNode, DeepNodeSchema
from rui_be.models.node.node_patch import NodePatch, NodePatchSchema
from rui_be.models.node.post_node import PostNode, PostNodeSchema

nodes = Blueprint('nodes', __name__)


@nodes.route('/api/1.6.0/nodes', methods=['GET'])
def get_nodes() -> Response:
    root_node_ids = state.graph.roots

    #
    # Build and return list of recusively populated nodes
    #

    def deep_node_from_node_id(node_id: int) -> DeepNode:
        entity_ids = state.graph.get_entities(node_id)

        return DeepNode(id=node_id,
                        parent_id=state.graph.get_parent(node_id),
                        entities=[Entity(entity_id, node_id, state.graph.get_entity(entity_id).name,
                                         len(state.matches_store.by_eid(entity_id)))
                                  for entity_id in entity_ids],
                        children=[deep_node_from_node_id(child)
                                  for child in state.graph.get_children(node_id)])

    deep_nodes: list[DeepNode] = [deep_node_from_node_id(root_node_id)
                                  for root_node_id in root_node_ids]

    return jsonify(DeepNodeSchema(many=True).dump(deep_nodes))


@nodes.route('/api/1.6.0/nodes', methods=['POST'])
def post_node() -> tuple[str, int]:
    request_data: dict = request.get_json()

    new_node: PostNode = PostNodeSchema().load(request_data)

    new_node_id = state.graph.add_node(entities=[draug.homag.graph.Entity(ent.name) for ent in new_node.entities])

    if new_node.parent_id is not None:
        state.graph.set_parent(new_node_id, new_node.parent_id)

    return '', 201


@nodes.route('/api/1.6.0/nodes/<int:node_id>', methods=['PATCH'])
def patch_node(node_id: int) -> str:
    request_data: dict = request.get_json()

    node_patch: NodePatch = NodePatchSchema().load(request_data)

    state.graph.set_parent(node_id, node_patch.parent_id)

    return ''


@nodes.route('/api/1.6.0/nodes/<int:node_id>', methods=['DELETE'])
def delete_node(node_id: int) -> str:
    state.graph.delete_node(node_id)

    return ''
