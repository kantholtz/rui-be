# -*- coding: utf-8 -*-

import logging
from dataclasses import asdict

from draug.homag import graph
from draug.homag import sampling
from draug.homag.model import PID

from rui_be import state
from rui_be import changelog
from rui_be.models.entities import Entity

from rui_be.routes import ENDPOINT

from rui_be.models.nodes import Node
from rui_be.models.predictions import Annotation
from rui_be.models.predictions import Prediction
from rui_be.models.predictions import Predictions

from flask import Blueprint, Response, request, jsonify


log = logging.getLogger(__name__)
blueprint = Blueprint("predictions", __name__)


@blueprint.route(f"{ENDPOINT}/nodes/<int:nid>/predictions", methods=["GET"])
def get_predictions(nid: int) -> Response:

    # params

    offset = request.args.get("offset")
    if offset:
        offset = int(offset)

    limit = request.args.get("limit")
    if limit:
        limit = int(limit)

    # prepare datastructure

    entities = [
        Entity(
            eid=ent.eid,
            nid=nid,
            name=ent.name,
            matches_count=len(state.matches_store.by_eid(ent.eid)),
        )
        for ent in state.graph.get_entities(nid=nid).values()
    ]

    node = Node(
        nid=nid,
        pid=state.graph.get_parent(nid=nid),
        entities=entities,
    )

    # retrieve and assemble data

    draug_predictions = state.predictions_store.by_nid(nid=nid)

    def create_predictions(rel: graph.Graph.RELATIONS):
        return [
            Prediction.from_draug(pred=pred, node=node)
            for pred in draug_predictions[rel][offset:limit]
        ]

    preds = Predictions(
        total_synonyms=len(draug_predictions[graph.Graph.RELATIONS.synonym]),
        total_children=len(draug_predictions[graph.Graph.RELATIONS.parent]),
        synonyms=create_predictions(graph.Graph.RELATIONS.synonym),
        children=create_predictions(graph.Graph.RELATIONS.parent),
    )

    return jsonify(Predictions.Schema().dump(preds))


@blueprint.route(f"{ENDPOINT}/predictions/<int:pid>", methods=["DELETE"])
def del_prediction(pid: int) -> Response:
    log.info(f"deleting prediction: {pid}")

    pred = state.predictions_store.by_pid(pid=pid)
    state.predictions_store.del_prediction(pid=pid)

    changelog.append(
        kind=changelog.Kind.PRED_DEL,
        data={"prediction": asdict(pred)},
    )

    return ""


# --


@blueprint.route(f"{ENDPOINT}/predictions/<int:pid>/annotate", methods=["POST"])
def ann_prediction(pid: int) -> Response:

    req: Annotation = Annotation.Schema().load(request.get_json())
    log.info(f"got {req.relation} annotation for {req.nid=} {pid=}: {req.phrase}")

    rel = graph.Graph.RELATIONS[req.relation]

    pred = state.predictions_store.by_pid(pid=pid)
    preds = state.predictions_store.by_nid(nid=req.nid)[rel]

    log.info(f"retrieved prediction {pid} (total: {len(preds)} predictions)")

    # update graph

    ent = graph.Entity(name=req.phrase)

    if req.relation == "synonym":
        state.graph.add_entity(nid=req.nid, ent=ent)
        nid = req.nid

    if req.relation == "parent":
        nid = state.graph.add_node(entities=[ent])

    # run matcher

    yielder = ((pred.context, {"identifier": pred.pid}) for pred in preds)
    handler = sampling.SimpleHandler()

    log.info("running the matcher")
    sampling.match(
        entities={ent.eid: ent},
        yielder=yielder,
        handler=handler,
        procs=1,
    )

    log.info(
        f"matcher finished, "
        f"matches={len(handler.matches)}, "
        f"filtered={len(handler.filtered)}, "
        f"nomatches={len(handler.nomatches)}"
    )

    # update predictions

    removed = set()
    for pid in {pid} | {match.identifier for match in handler.matches}:
        removed.add(state.predictions_store.by_pid(pid=pid))
        state.predictions_store.del_prediction(pid=pid)

    # update matches

    for match in handler.matches:
        state.matches_store.add_match(match)

    # --

    changelog.append(
        kind=changelog.Kind.PRED_ANN,
        data={
            "prediction": asdict(pred),
            "node": state.graph.nxg.nodes[nid],
            "matches": [asdict(match) for match in handler.matches],
        },
    )

    return {"removed": [pred.pid for pred in removed]}


@blueprint.route(f"{ENDPOINT}/predictions/<int:pid>/dismiss", methods=["POST"])
def dis_prediction(pid: int) -> Response:
    # TODO
    return ""
