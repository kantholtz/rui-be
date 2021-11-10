from draug.homag.graph import Graph
from draug.homag.model import Prediction
from flask import Blueprint, Response, request, jsonify

from rui_be import state
from rui_be.models.entity.entity import Entity
from rui_be.models.node.node import Node
from rui_be.models.prediction.candidate_prediction import CandidatePrediction
from rui_be.models.prediction.candidate_with_predictions import CandidateWithPredictions
from rui_be.models.prediction.prediction_patch import PredictionPatch, PredictionPatchSchema
from rui_be.models.prediction.prediction_response import PredictionResponse, PredictionResponseSchema

predictions = Blueprint('predictions', __name__)


@predictions.route('/api/1.6.0/nodes/<int:node_id>/predictions', methods=['GET'])
def get_predictions(node_id: int) -> Response:
    #
    # Parse query params
    #

    offset = request.args.get('offset')
    if offset:
        offset = int(offset)

    limit = request.args.get('limit')
    if limit:
        limit = int(limit)

    #
    # Get predictions from draug and apply pagination
    #

    candidate_to_predictions: dict[str, list[Prediction]] = \
        state.predictions_store.by_nid(node_id, filter_out_dismissed=True)

    candidate_with_predictions_list = [_get_candidate_with_predictions(candidate, predictions)
                                       for candidate, predictions in candidate_to_predictions.items()]

    def calc_scores(candidate_with_predictions: CandidateWithPredictions):
        cwp = candidate_with_predictions

        if len(cwp.synonym_predictions) > 0 and len(cwp.parent_predictions) > 0:
            return ((cwp.synonym_predictions[0].score_norm + cwp.parent_predictions[0].score_norm) / 2,
                    (cwp.synonym_predictions[0].score + cwp.parent_predictions[0].score) / 2)

        elif len(cwp.synonym_predictions) > 0:
            return cwp.synonym_predictions[0].score_norm, cwp.synonym_predictions[0].score

        elif len(cwp.parent_predictions) > 0:
            return cwp.parent_predictions[0].score_norm, cwp.parent_predictions[0].score

        else:
            raise AssertionError

    # Sort candidates with predictions by score
    candidate_with_predictions_list.sort(key=lambda cwp: calc_scores(cwp), reverse=True)

    candidate_to_predictions_page = _paginate(candidate_with_predictions_list, offset, limit)

    #
    # Add information about predicted node and build response
    #

    prediction_response = PredictionResponse(total_predictions=len(candidate_with_predictions_list),
                                             predictions=candidate_to_predictions_page)

    return jsonify(PredictionResponseSchema().dump(prediction_response))


def _paginate(list_: list, offset: int = None, limit: int = None) -> list:
    if offset and limit:
        return list_[offset: offset + limit]
    elif offset:
        return list_[offset: None]
    elif limit:
        return list_[0: limit]
    else:
        return list_


def _get_candiate_prediction(prediction: Prediction) -> CandidatePrediction:
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

    return CandidatePrediction(score=prediction.score, score_norm=prediction.score_norm, node=pred_node)


def _get_candidate_with_predictions(candidate: str,
                                    predictions: list[Prediction]
                                    ) -> CandidateWithPredictions:
    parent_predictions: list[CandidatePrediction] = []
    synonym_predictions: list[CandidatePrediction] = []

    for prediction in predictions:
        candidate_prediction = _get_candiate_prediction(prediction)

        if prediction.relation == Graph.RELATIONS.parent:
            parent_predictions.append(candidate_prediction)
        elif prediction.relation == Graph.RELATIONS.synonym:
            synonym_predictions.append(candidate_prediction)

    return CandidateWithPredictions(candidate, False, parent_predictions, synonym_predictions)


@predictions.route('/api/1.6.0/predictions/<string:candidate>', methods=['PATCH'])
def patch_prediction(candidate: str) -> tuple[str, int]:
    request_data: dict = request.get_json()

    prediction_patch: PredictionPatch = PredictionPatchSchema().load(request_data)

    if prediction_patch.dismissed and candidate in state.predictions_store.get_canidates():
        state.predictions_store.dismiss_candidate(candidate)
        return '', 200

    else:
        return '', 400
