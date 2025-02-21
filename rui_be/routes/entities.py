import draug.homag.graph
from flask import Blueprint, request

from rui_be.state import ctx
from rui_be import changelog
from rui_be.models.entities import PostEntity

from rui_be.routes import ENDPOINT


import logging
from dataclasses import asdict


log = logging.getLogger(__name__)
blueprint = Blueprint("entities", __name__)


@blueprint.route(f"{ENDPOINT}/entities", methods=["POST"])
def post_entity() -> tuple[str, int]:
    req: PostEntity = PostEntity.Schema().load(request.get_json())

    with ctx as state:
        eid = state.graph.add_entity(
            nid=req.nid,
            ent=draug.homag.graph.Entity(name=req.name),
        )

        ent = state.graph.get_entity(eid=eid)

        changelog.append(
            state=state,
            kind=changelog.Kind.ENTITY_ADD,
            data={
                "nid": req.nid,
                "entity": asdict(ent),
                "node": state.graph.node_repr(nid=ent.nid),
            },
        )

    return "", 201


@blueprint.route(f"{ENDPOINT}/entities/<int:eid>", methods=["DELETE"])
def delete_entity(eid: int) -> str:
    with ctx as state:
        ent = state.graph.get_entity(eid=eid)
        state.graph.del_entity(eid=eid)

        changelog.append(
            kind=changelog.Kind.ENTITY_DEL,
            data={
                "eid": eid,
                "entity": asdict(ent),
                "node": state.graph.node_repr(nid=ent.nid),
            },
        )

    return ""
