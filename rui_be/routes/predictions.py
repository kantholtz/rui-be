# -*- coding: utf-8 -*-

import re
import logging
from dataclasses import asdict

from draug.homag import graph
from draug.homag import sampling

from rui_be import changelog
from rui_be.state import ctx
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


TOP_K_KWARGS = dict(k=20, norm=True, noskip=True)


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

    with ctx as state:
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

        draug_predictions = state.predictions_store.top_k(nid=nid, **TOP_K_KWARGS)

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
    nid = int(request.args.get("nid"))

    with ctx as state:
        log.info(f"deleting prediction: {pid}")

        pred = state.predictions_store.contexts[pid]
        state.predictions_store.del_prediction(pid=pid)

        changelog.append(
            state=state,
            kind=changelog.Kind.PRED_DEL,
            data={
                "prediction": pred,
                "node": state.graph.node_repr(nid=nid),
            },
        )

        return ""


# --


LIMIT = 1000


@blueprint.route(f"{ENDPOINT}/predictions/<int:pid>/annotate", methods=["POST"])
def ann_prediction(pid: int) -> Response:
    with ctx as state:
        req: Annotation = Annotation.Schema().load(request.get_json())

        log.info(f"got {req.relation} annotation for [{req.nid=}] {pid=}: {req.phrase}")
        log.info(f"predicted was a {req.predicted_relation} for [{req.predicted_nid}]")
        # log.info(f"prediction is specific: {req.specific}")

        rel = graph.Graph.RELATIONS[req.relation]
        pred = state.predictions_store.contexts[pid]
        preds = state.predictions_store.top_k(nid=req.nid, **TOP_K_KWARGS)[rel]

        log.info(f"retrieved prediction {pid} (total: {len(preds)} predictions)")

        # update graph

        ent = graph.Entity(name=req.phrase)

        if req.relation == "synonym":
            state.graph.add_entity(nid=req.nid, ent=ent)
            nid = req.nid

        if req.relation == "parent":
            nid = state.graph.add_node(entities=[ent])
            state.graph.set_parent(nid, req.nid)

        # run matcher

        log.error("matcher deactivated (!)")

        #  for pred in preds[:LIMIT])
        yielder = ((pred.context, {"identifier": pred.pid}) for pred in [])
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
            try:
                removed.add(pid)
                state.predictions_store.del_prediction(pid=pid)
            except KeyError:
                log.error(f"ann_prediction: {pid=} already gone!")

        # update matches

        for match in handler.matches:
            state.matches_store.add_match(match)

        # --

        changelog.append(
            state=state,
            kind=changelog.Kind.PRED_ANN,
            data={
                "request": asdict(req),
                "prediction": pred,
                "node": state.graph.node_repr(nid=nid),
                "matches": [asdict(match) for match in handler.matches],
                "removed": list(removed),
                "predicted_node": state.graph.node_repr(nid=req.predicted_nid),
                "predicted_relation": req.predicted_relation,
            },
        )

        return {"removed": list(removed)}


@blueprint.route(f"{ENDPOINT}/predictions/<int:pid>/filter", methods=["POST"])
def dis_prediction(pid: int) -> Response:
    with ctx as state:
        req: FilterRequest = FilterRequest.Schema().load(request.get_json())

        rel = graph.Graph.RELATIONS[req.relation]
        preds = state.predictions_store.top_k(nid=req.nid, **TOP_K_KWARGS)[rel]

        log.info(f"filtering {req.phrase} from {len(preds)} predictions for {req.nid=}")

        regex = re.compile(".+".join(req.phrase.split()).lower())
        log.info(f"created regex: {regex}")

        removed = {pid}
        for pred in preds:
            if regex.search(pred.context.lower()):
                removed.add(pred.pid)

        removed_contexts = []
        for pid in removed:
            removed_contexts.append(state.predictions_store.contexts[pid])
            state.predictions_store.del_prediction(pid=pid)

        log.info(f"matched and removed {len(removed)} predictions in total")

        # --

        changelog.append(
            state=state,
            kind=changelog.Kind.PRED_FILTER,
            data={
                "request": asdict(req),
                "regex": str(regex),
                "node": state.graph.node_repr(nid=req.nid),
                "prediction": asdict(pred),
                "removed": removed_contexts,
            },
        )

        return {"removed": list(removed)}
