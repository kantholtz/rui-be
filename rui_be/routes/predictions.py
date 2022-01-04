# -*- coding: utf-8 -*-

import re
import logging
from dataclasses import asdict

from draug.homag import graph
from draug.homag import sampling

from rui_be import state
from rui_be import changelog
from rui_be.models.entities import Entity

from rui_be.routes import ENDPOINT

from rui_be.models.nodes import Node
from rui_be.models.predictions import Annotation
from rui_be.models.predictions import Prediction
from rui_be.models.predictions import Predictions
from rui_be.models.predictions import FilterRequest

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
        state.nlp,
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
            "request": asdict(req),
            "prediction": asdict(pred),
            "node": dict(state.graph.nxg.nodes[nid]),
            "matches": [asdict(match) for match in handler.matches],
            "removed": [asdict(pred) for pred in removed],
        },
    )

    return {"removed": [pred.pid for pred in removed]}


@blueprint.route(f"{ENDPOINT}/predictions/<int:pid>/filter", methods=["POST"])
def dis_prediction(pid: int) -> Response:
    req: FilterRequest = FilterRequest.Schema().load(request.get_json())

    rel = graph.Graph.RELATIONS[req.relation]
    pred = state.predictions_store.by_pid(pid=pid)
    preds = state.predictions_store.by_nid(req.nid)[rel]

    log.info(f"filtering {req.phrase} from {len(preds)} predictions for {req.nid=}")

    regex = re.compile(".+".join(req.phrase.split()).lower())
    log.info(f"created regex: {regex}")

    removed = {pred}
    for pred in preds:
        if regex.search(pred.context.lower()):
            removed.add(pred)

    for pred in removed:
        state.predictions_store.del_prediction(pid=pred.pid)

    log.info(f"matched and removed {len(removed)} predictions in total")

    # --

    changelog.append(
        kind=changelog.Kind.PRED_FILTER,
        data={
            "request": asdict(req),
            "regex": str(regex),
            "node": dict(state.graph.nxg.nodes[req.nid]),
            "prediction": asdict(pred),
            "removed": [asdict(pred) for pred in removed],
        },
    )

    return {"removed": [pred.pid for pred in removed]}
