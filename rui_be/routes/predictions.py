import draug.homag.model
from draug.homag.graph import Graph
from flask import Blueprint, Response, request, jsonify

from rui_be import state
from rui_be.models.entity.entity import Entity
from rui_be.models.node.node import Node
from rui_be.models.prediction.partial_prediction import PartialPrediction
from rui_be.models.prediction.partial_prediction_item import PartialPredictionItem
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

    ### Get draug predictions for candidate

    candidate_to_homag_predictions: dict[str, list[draug.homag.model.Prediction]] = \
        state.predictions_store.by_nid(node_id, filter_out_dismissed=True)

    ### Build partial predictions that contain score information to be sorted by

    partial_predictions = [_build_partial_prediction(candidate, homag_predictions)
                           for candidate, homag_predictions in candidate_to_homag_predictions.items()]

    partial_predictions.sort(key=lambda it: (it.total_score_norm, it.total_score), reverse=True)

    ### Count total synonym and child predictions

    total_synonym_predictions = 0
    total_child_predictions = 0

    for partial_prediction in partial_predictions:
        total_synonym_predictions += len(partial_prediction.synonym_predictions)
        total_child_predictions += len(partial_prediction.parent_predictions)

    ### Paginate partial predictions

    paged_partial_predictions = _paginate(partial_predictions, offset, limit)

    ### Complete partial predictions to full predictions with node and entity information

    predictions = [_build_prediction(partial_prediction)
                   for partial_prediction in paged_partial_predictions]

    ### Add information about predicted node and build response

    predictions_page = PredictionsPage(total_predictions=len(partial_predictions),
                                       total_synonym_predictions=total_synonym_predictions,
                                       total_child_predictions=total_child_predictions,
                                       predictions=predictions)

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


def _build_partial_prediction(
        candidate: str,
        homag_predictions: list[draug.homag.model.Prediction]
) -> PartialPrediction:
    """ Transform draug.homag.model.Prediction -> PartialPrediction """

    parent_predictions: list[PartialPredictionItem] = []
    synonym_predictions: list[PartialPredictionItem] = []

    for homag_prediction in homag_predictions:
        partial_prediction_item = _build_partial_prediction_item(homag_prediction)

        if homag_prediction.relation == Graph.RELATIONS.parent:
            parent_predictions.append(partial_prediction_item)
        elif homag_prediction.relation == Graph.RELATIONS.synonym:
            synonym_predictions.append(partial_prediction_item)

    total_score_norm, total_score = _calc_total_scores(synonym_predictions, parent_predictions)

    return PartialPrediction(candidate=candidate,
                             dismissed=False,
                             total_score=total_score,
                             total_score_norm=total_score_norm,
                             parent_predictions=parent_predictions,
                             synonym_predictions=synonym_predictions)


def _build_partial_prediction_item(
        homag_prediction: draug.homag.model.Prediction
) -> PartialPredictionItem:
    """ Transform draug.homag.model.Prediction -> PartialPredictionItem """

    return PartialPredictionItem(score=homag_prediction.score,
                                 score_norm=homag_prediction.score_norm,
                                 node_id=homag_prediction.predicted_nid)


def _calc_total_scores(
        synonym_predictions: list[PartialPredictionItem],
        parent_predictions: list[PartialPredictionItem]
) -> tuple[float, float]:
    """ Calc mean of top synonym/child prediction scores """

    if len(synonym_predictions) > 0 and len(parent_predictions) > 0:
        return ((synonym_predictions[0].score_norm + parent_predictions[0].score_norm) / 2,
                (synonym_predictions[0].score + parent_predictions[0].score) / 2)

    elif len(synonym_predictions) > 0:
        return synonym_predictions[0].score_norm, synonym_predictions[0].score

    elif len(parent_predictions) > 0:
        return parent_predictions[0].score_norm, parent_predictions[0].score

    else:
        raise AssertionError


def _build_prediction(partial_prediction: PartialPrediction) -> Prediction:
    parent_predictions = [_build_prediction_item(partial_prediction_item)
                          for partial_prediction_item in partial_prediction.parent_predictions]

    synonym_predictions = [_build_prediction_item(partial_prediction_item)
                           for partial_prediction_item in partial_prediction.synonym_predictions]

    return Prediction(candidate=partial_prediction.candidate,
                      dismissed=partial_prediction.dismissed,
                      total_score=partial_prediction.total_score,
                      total_score_norm=partial_prediction.total_score_norm,
                      parent_predictions=parent_predictions,
                      synonym_predictions=synonym_predictions)


def _build_prediction_item(partial_prediction_item: PartialPredictionItem) -> PredictionItem:
    pred_node_id = partial_prediction_item.node_id

    eid_to_draug_entity = state.graph.get_entities(pred_node_id)
    entities = [Entity(id=entity_id,
                       node_id=pred_node_id,
                       name=entity.name,
                       matches_count=len(state.matches_store.by_eid(entity_id)))
                for (entity_id, entity) in eid_to_draug_entity.items()]

    pred_node = Node(id=pred_node_id,
                     parent_id=state.graph.get_parent(pred_node_id),
                     entities=entities)

    return PredictionItem(score=partial_prediction_item.score,
                          score_norm=partial_prediction_item.score_norm,
                          node=pred_node)


@predictions.route('/api/1.6.0/predictions/<string:candidate>', methods=['PATCH'])
def patch_prediction(candidate: str) -> tuple[str, int]:
    request_data: dict = request.get_json()

    prediction_patch: PredictionPatch = PredictionPatchSchema().load(request_data)

    if prediction_patch.dismissed and candidate in state.predictions_store.get_canidates():
        state.predictions_store.dismiss_candidate(candidate)
        return '', 200

    else:
        return '', 400
