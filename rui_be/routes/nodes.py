import logging
from dataclasses import asdict

import draug.homag.graph

from flask import Blueprint, Response, request, jsonify

from rui_be import state
from rui_be import changelog
from rui_be.models.nodes import PostNode
from rui_be.models.nodes import DeepNode
from rui_be.models.nodes import NodePatch
from rui_be.models.entities import Entity

from rui_be.routes import ENDPOINT


log = logging.getLogger(__name__)
blueprint = Blueprint("nodes", __name__)


@blueprint.route(f"{ENDPOINT}/nodes", methods=["GET"])
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


@blueprint.route(f"{ENDPOINT}/nodes", methods=["POST"])
def post_node() -> tuple[str, int]:
    req: PostNode = PostNode.Schema().load(request.get_json())

    nid = state.graph.add_node(
        entities=[draug.homag.graph.Entity(ent.name) for ent in req.entities]
    )

    parent = None
    if req.pid is not None:
        state.graph.set_parent(nid, req.pid)
        parent = state.graph.node_repr(nid=req.pid)

    changelog.append(
        kind=changelog.Kind.NODE_ADD,
        data={
            "nid": nid,
            "node": state.graph.node_repr(nid=nid),
            "parent": parent,
            "request": asdict(req),
        },
    )

    return "", 201


# currently unused?
@blueprint.route(f"{ENDPOINT}/nodes/<int:nid>", methods=["PATCH"])
def patch_node(nid: int) -> str:
    req: NodePatch = NodePatch.Schema().load(request.get_json())

    if req.pid is None and state.graph.get_parent(nid) is not None:
        state.graph.del_parent(nid)

    elif req.pid is not None:
        state.graph.set_parent(nid=nid, pid=req.pid)

    changelog.append(
        kind=changelog.Kind.NODE_CNG,
        data={
            "request": asdict(req),
            "node": state.graph.node_repr(nid=nid),
        },
    )

    return ""


@blueprint.route(f"{ENDPOINT}/nodes/<int:nid>", methods=["DELETE"])
def delete_node(nid: int) -> str:
    node_rep = state.graph.node_repr(nid=nid)
    nids = state.graph.del_node(nid)

    changelog.append(
        kind=changelog.Kind.NODE_DEL,
        data={
            "nid": nid,
            "node": node_rep,
            "deleted_nids": nids,
        },
    )

    return ""
