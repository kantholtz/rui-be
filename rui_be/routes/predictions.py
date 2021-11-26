import draug.homag.model
from draug.homag.graph import Graph
from flask import Blueprint, Response, request, jsonify

from rui_be import state
from rui_be.models.entity.entity import Entity
from rui_be.models.node.node import Node
from rui_be.models.prediction.prediction import Prediction
from rui_be.models.prediction.prediction_item import PredictionItem
from rui_be.models.prediction.prediction_patch import PredictionPatch, PredictionPatchSchema
from rui_be.models.prediction.predictions_page import PredictionsPage, PredictionsPageSchema

predictions = Blueprint('predictions', __name__)


@predictions.route('/api/1.6.0/nodes/<int:node_id>/predictions', methods=['GET'])
def get_predictions(node_id: int) -> Response:
    ### Parse query params

    offset = request.args.get('offset')
    if offset:
        offset = int(offset)

    limit = request.args.get('limit')
    if limit:
        limit = int(limit)

    ### Get predictions from draug and apply pagination

    candidate_to_predictions: dict[str, list[Prediction]] = \
        state.predictions_store.by_nid(node_id, filter_out_dismissed=True)

    predictions = [_build_prediction(candidate, predictions)
                   for candidate, predictions in candidate_to_predictions.items()]

    # Sort candidates with predictions by score
    predictions.sort(key=lambda cwp: (cwp.total_score_norm, cwp.total_score), reverse=True)

    candidate_to_predictions_page = _paginate(predictions, offset, limit)

    ### Add information about predicted node and build response

    predictions_page = PredictionsPage(total_predictions=len(predictions),
                                       predictions=candidate_to_predictions_page)

    return jsonify(PredictionsPageSchema().dump(predictions_page))


def _paginate(list_: list, offset: int = None, limit: int = None) -> list:
    if offset and limit:
        return list_[offset: offset + limit]
    elif offset:
        return list_[offset: None]
    elif limit:
        return list_[0: limit]
    else:
        return list_


def _get_prediction_item(prediction: draug.homag.model.Prediction) -> PredictionItem:
    pred_node_id = prediction.predicted_nid

    eid_to_draug_entity = state.graph.get_entities(pred_node_id)
    entities = [Entity(id=entity_id,
                       node_id=pred_node_id,
                       name=entity.name,
                       matches_count=len(state.matches_store.by_eid(entity_id)))
                for (entity_id, entity) in eid_to_draug_entity.items()]

    pred_node = Node(id=pred_node_id,
                     parent_id=state.graph.get_parent(pred_node_id),
                     entities=entities)

    return PredictionItem(score=prediction.score, score_norm=prediction.score_norm, node=pred_node)


def _build_prediction(candidate: str,
                      predictions: list[draug.homag.model.Prediction]
                      ) -> Prediction:
    parent_predictions: list[PredictionItem] = []
    synonym_predictions: list[PredictionItem] = []

    for prediction in predictions:
        prediction_item = _get_prediction_item(prediction)

        if prediction.relation == Graph.RELATIONS.parent:
            parent_predictions.append(prediction_item)
        elif prediction.relation == Graph.RELATIONS.synonym:
            synonym_predictions.append(prediction_item)

    total_score_norm, total_score = _calc_total_scores(synonym_predictions, parent_predictions)

    return Prediction(candidate=candidate,
                      dismissed=False,
                      total_score=total_score,
                      total_score_norm=total_score_norm,
                      parent_predictions=parent_predictions,
                      synonym_predictions=synonym_predictions)


def _calc_total_scores(synonym_predictions: list[PredictionItem], parent_predictions: list[PredictionItem]):
    if len(synonym_predictions) > 0 and len(parent_predictions) > 0:
        return ((synonym_predictions[0].score_norm + parent_predictions[0].score_norm) / 2,
                (synonym_predictions[0].score + parent_predictions[0].score) / 2)

    elif len(synonym_predictions) > 0:
        return synonym_predictions[0].score_norm, synonym_predictions[0].score

    elif len(parent_predictions) > 0:
        return parent_predictions[0].score_norm, parent_predictions[0].score

    else:
        raise AssertionError


@predictions.route('/api/1.6.0/predictions/<string:candidate>', methods=['PATCH'])
def patch_prediction(candidate: str) -> tuple[str, int]:
    request_data: dict = request.get_json()

    prediction_patch: PredictionPatch = PredictionPatchSchema().load(request_data)

    if prediction_patch.dismissed and candidate in state.predictions_store.get_canidates():
        state.predictions_store.dismiss_candidate(candidate)
        return '', 200

    else:
        return '', 400
