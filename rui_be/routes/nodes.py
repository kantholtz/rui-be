import logging

import draug.homag.graph
from flask import Blueprint, Response, request, jsonify

from rui_be import state
from rui_be.models.nodes import PostNode
from rui_be.models.nodes import DeepNode
from rui_be.models.nodes import NodePatch
from rui_be.models.entities import Entity


log = logging.getLogger(__name__)
blueprint = Blueprint("nodes", __name__)


@blueprint.route("/api/1.6.0/nodes", methods=["GET"])
def get_nodes() -> Response:
    root_nids = state.graph.roots

    # Build and return list of recusively populated nodes

    def deep_node_from_nid(nid: int) -> DeepNode:
        eids = state.graph.get_entities(nid)

        return DeepNode(
            nid=nid,
            pid=state.graph.get_parent(nid),
            entities=[
                Entity(
                    eid=eid,
                    nid=nid,
                    name=state.graph.get_entity(eid).name,
                    matches_count=len(state.matches_store.by_eid(eid)),
                )
                for eid in eids
            ],
            children=[
                deep_node_from_nid(child) for child in state.graph.get_children(nid)
            ],
        )

    deep_nodes: list[DeepNode] = [
        deep_node_from_nid(root_nid) for root_nid in root_nids
    ]

    return jsonify(DeepNode.Schema(many=True).dump(deep_nodes))


@blueprint.route("/api/1.6.0/nodes", methods=["POST"])
def post_node() -> tuple[str, int]:
    request_data: dict = request.get_json()

    new_node: PostNode = PostNode.Schema().load(request_data)

    new_nid = state.graph.add_node(
        entities=[draug.homag.graph.Entity(ent.name) for ent in new_node.entities]
    )

    if new_node.pid is not None:
        state.graph.set_parent(new_nid, new_node.pid)

    return "", 201


@blueprint.route("/api/1.6.0/nodes/<int:nid>", methods=["PATCH"])
def patch_node(nid: int) -> str:
    request_data: dict = request.get_json()

    node_patch: NodePatch = NodePatch.Schema().load(request_data)

    if node_patch.pid is None and state.graph.get_parent(nid) is not None:
        state.graph.del_parent(nid)

    elif node_patch.pid is not None:
        state.graph.set_parent(nid, node_patch.pid)

    return ""


@blueprint.route("/api/1.6.0/nodes/<int:nid>", methods=["DELETE"])
def delete_node(nid: int) -> str:
    state.graph.del_node(nid)
    return ""
