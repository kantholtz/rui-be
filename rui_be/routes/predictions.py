# -*- coding: utf-8 -*-

from draug.homag.graph import Graph

from rui_be import state
from rui_be.models.entities import Entity

from rui_be.models.nodes import Node
from rui_be.models.predictions import Prediction
from rui_be.models.predictions import Predictions

from flask import Blueprint, Response, request, jsonify

import logging


log = logging.getLogger(__name__)
blueprint = Blueprint("predictions", __name__)


@blueprint.route("/api/1.6.0/nodes/<int:nid>/predictions", methods=["GET"])
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

    def create_predictions(rel: Graph.RELATIONS):
        return [
            Prediction.from_draug(pred=pred, node=node)
            for pred in draug_predictions[rel][offset:limit]
        ]

    preds = Predictions(
        total_synonyms=len(draug_predictions[Graph.RELATIONS.synonym]),
        total_children=len(draug_predictions[Graph.RELATIONS.parent]),
        synonyms=create_predictions(Graph.RELATIONS.synonym),
        children=create_predictions(Graph.RELATIONS.parent),
    )

    return jsonify(Predictions.Schema().dump(preds))


@blueprint.route("/api/1.6.0/predictions/<int:pid>", methods=["DELETE"])
def del_prediction(pid: int) -> Response:
    log.info(f"deleting prediction: {pid}")
    state.predictions_store.del_prediction(pid=pid)
    return ""
