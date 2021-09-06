import os
import zipfile

from draug.homag.graph import Graph
from draug.homag.model import Predictions
from draug.homag.text import Matches
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from src.models.entity.entity import Entity
from src.models.entity.post_entity import PostEntitySchema, PostEntity
from src.models.match.match import MatchSchema, Match
from src.models.node.deep_node import DeepNode, DeepNodeSchema
from src.models.node.node import Node
from src.models.node.node_patch import NodePatch, NodePatchSchema
from src.models.node.post_node import PostNodeSchema, PostNode

#
# Set up app object
#
from src.models.prediction.prediction import Prediction, PredictionSchema

app = Flask(__name__)

CORS(app)

app.config['JSON_SORT_KEYS'] = False  # Simplify debugging in frontend

#
# Create initial taxonomy
#

meta = {
    'name': 'symptax.v6',
    'reflexive': [Graph.RELATIONS.synonym.value],
    'relmap': {m.value: m.name for m in Graph.RELATIONS}
}

graph = Graph(meta)
matches_store = Matches(graph)
predictions_store = Predictions()


#
# Root Route
#

@app.route('/')
def get_root():
    return 'Server is up'


#
# Upload
#

@app.route('/api/1.6.0/upload', methods=['PUT'])
def put_upload() -> str:
    global graph, matches_store, predictions_store

    symptax_upload_zip: FileStorage = request.files['symptaxUploadZip']

    upload_filename = secure_filename(symptax_upload_zip.filename)
    upload_dir = os.getcwd()
    upload_path = os.path.join(upload_dir, upload_filename)

    symptax_upload_zip.save(upload_path)

    with zipfile.ZipFile(os.path.join(upload_dir, upload_filename), 'r') as zip_ref:
        zip_ref.extractall(upload_dir)

    extracted_dir = os.path.splitext(upload_path)[0]

    graph = Graph.from_dir(extracted_dir)

    match_txt: str = os.path.join(extracted_dir, 'match.txt')
    matches_store = Matches.from_file(match_txt, graph)

    parent_csv: str = os.path.join(extracted_dir, 'parent.csv')
    synonym_csv: str = os.path.join(extracted_dir, 'synonym.csv')
    predictions_store = Predictions.from_files({parent_csv, synonym_csv})

    return ''


#
# Nodes
#

@app.route('/api/1.6.0/nodes', methods=['GET'])
def get_nodes() -> Response:
    root_node_ids = graph.find_root_ents()

    #
    # Build and return list of recusively populated nodes
    #

    def deep_node_from_node_id(node_id: int) -> DeepNode:
        entity_ids = graph.node_eids(node_id)

        return DeepNode(id=node_id,
                        parent_id=graph.get_parent(node_id),
                        entities=[Entity(entity_id, node_id, graph.entity_name(entity_id),
                                         len(matches_store.by_eid(entity_id)))
                                  for entity_id in entity_ids],
                        children=[deep_node_from_node_id(child)
                                  for child in graph.get_children(node_id)])

    deep_nodes: list[DeepNode] = [deep_node_from_node_id(root_node_id)
                                  for root_node_id in root_node_ids]

    return jsonify(DeepNodeSchema(many=True).dump(deep_nodes))


@app.route('/api/1.6.0/nodes', methods=['POST'])
def post_node() -> tuple[str, int]:
    request_data: dict = request.get_json()

    new_node: PostNode = PostNodeSchema().load(request_data)

    graph.add_node(names=[ent.name for ent in new_node.entities],
                   parent=new_node.parent_id)

    return '', 201


@app.route('/api/1.6.0/nodes/<int:node_id>', methods=['PATCH'])
def patch_node(node_id: int) -> str:
    request_data: dict = request.get_json()

    node_patch: NodePatch = NodePatchSchema().load(request_data)

    graph.set_parent(node_id, node_patch.parent_id)

    return ''


@app.route('/api/1.6.0/nodes/<int:node_id>', methods=['DELETE'])
def delete_node(node_id: int) -> str:
    graph.delete_node(node_id)

    return ''


#
# Entities
#

@app.route('/api/1.6.0/entities', methods=['POST'])
def post_entity() -> tuple[str, int]:
    request_data: dict = request.get_json()

    new_entity: PostEntity = PostEntitySchema().load(request_data)

    graph.add_name(new_entity.node_id, new_entity.name)

    return '', 201


@app.route('/api/1.6.0/entities/<int:entity_id>', methods=['DELETE'])
def delete_entity(entity_id: int) -> str:
    graph.delete_name(entity_id)

    return ''


#
# Matches
#

@app.route('/api/1.6.0/matches', methods=['GET'])
def get_matches() -> Response:
    global matches_store

    #
    # Parse query params
    #

    entity = int(request.args.get('entity'))

    offset = request.args.get('offset')
    if offset:
        offset = int(offset)

    limit = request.args.get('limit')
    if limit:
        limit = int(limit)

    #
    # Get matches from draug and apply pagination
    #

    draug_matches = matches_store.by_eid(entity)
    matches: list[Match] = [Match(m.eid, m.ticket, m.context, m.mention, list(m.mention_idxs))
                            for m in draug_matches]

    if offset and limit:
        matches = matches[offset:(offset + limit)]
    elif offset:
        matches = matches[offset:]
    elif limit:
        matches = matches[:limit]

    return jsonify(MatchSchema(many=True).dump(matches))


#
# Predictions
#

@app.route('/api/1.6.0/nodes/<int:node_id>/predictions', methods=['GET'])
def get_predictions(node_id: int) -> Response:
    global predictions_store

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

    draug_predictions = list(predictions_store.by_nid(node_id))

    if offset and limit:
        draug_predictions = draug_predictions[offset:(offset + limit)]
    elif offset:
        draug_predictions = draug_predictions[offset:]
    elif limit:
        draug_predictions = draug_predictions[:limit]

    #
    # Add information about predicted node
    #

    predictions: list[Prediction] = []
    for draug_prediction in draug_predictions:
        pred_node_id = draug_prediction.predicted_nid

        pred_node_entity_ids = graph.node_eids(pred_node_id)
        pred_node_entities = [Entity(id=pred_entity_id,
                                     node_id=node_id,
                                     name=graph.entity_name(pred_entity_id),
                                     matches_count=len(matches_store.by_eid(pred_entity_id)))
                              for pred_entity_id in pred_node_entity_ids]

        pred_node = Node(id=node_id,
                         parent_id=graph.get_parent(node_id),
                         entities=pred_node_entities)

        predictions.append(Prediction(node=pred_node,
                                      score=draug_prediction.score,
                                      relation=draug_prediction.relation,
                                      candidate=draug_prediction.candidate))

    return jsonify(PredictionSchema(many=True).dump(predictions))


#
# Run server
#

if __name__ == '__main__':
    app.run()
