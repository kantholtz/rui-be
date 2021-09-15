from itertools import islice

from draug.homag.model import Prediction, Relation
from flask import Blueprint, Response, request, jsonify

from src import state
from src.models.entity.entity import Entity
from src.models.node.node import Node
from src.models.prediction.candidate_prediction import CandidatePrediction
from src.models.prediction.candidate_with_predictions import CandidateWithPredictions
from src.models.prediction.prediction_patch import PredictionPatch, PredictionPatchSchema
from src.models.prediction.prediction_response import PredictionResponse, PredictionResponseSchema

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

    candidate_to_predictions_length = len(candidate_to_predictions)

    candidate_to_predictions = _paginate_dict(candidate_to_predictions, offset, limit)

    #
    # Add information about predicted node and build response
    #

    candidate_with_predictions_list = [_get_candidate_with_predictions(candidate, predictions)
                                       for candidate, predictions in candidate_to_predictions.items()]

    prediction_response = PredictionResponse(total_predictions=candidate_to_predictions_length,
                                             predictions=candidate_with_predictions_list)

    return jsonify(PredictionResponseSchema().dump(prediction_response))


def _paginate_dict(dict_: dict, offset: int, limit: int) -> dict:
    items = dict_.items()

    if offset and limit:
        items = islice(items, offset, offset + limit)
    elif offset:
        items = islice(items, offset, None)
    elif limit:
        items = islice(items, 0, limit)

    return {key: value for key, value in items}


def _get_candiate_prediction(prediction: Prediction) -> CandidatePrediction:
    pred_node_id = prediction.predicted_nid

    pred_node_entity_ids = state.graph.node_eids(pred_node_id)
    pred_node_entities = [Entity(id=pred_entity_id,
                                 node_id=pred_node_id,
                                 name=state.graph.entity_name(pred_entity_id),
                                 matches_count=len(state.matches_store.by_eid(pred_entity_id)))
                          for pred_entity_id in pred_node_entity_ids]

    pred_node = Node(id=pred_node_id,
                     parent_id=state.graph.get_parent(pred_node_id),
                     entities=pred_node_entities)

    return CandidatePrediction(score=prediction.score_norm, node=pred_node)


def _get_candidate_with_predictions(candidate: str,
                                    predictions: list[Prediction]
                                    ) -> CandidateWithPredictions:
    parent_predictions = []
    synonym_predictions = []

    for prediction in predictions:
        candidate_prediction = _get_candiate_prediction(prediction)

        if prediction.relation == Relation.PARENT:
            parent_predictions.append(candidate_prediction)
        elif prediction.relation == Relation.SYNONYM:
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
