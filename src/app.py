from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional

import yaml
from draug.homag.tax import Tax, RELATIONS
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from werkzeug.datastructures import FileStorage

from src import taxonomy
from src.json_encoder import JsonEncoder

#
# Set up app object
#

app = Flask(__name__)

CORS(app)

app.config['JSON_SORT_KEYS'] = False  # Simplify debugging in frontend
app.json_encoder = JsonEncoder

#
# Create taxonomy
#

meta = {
    'name': 'symptax.v4',
    'reflexive': (RELATIONS['synonym'],),
    'inverse': {RELATIONS['parent']: RELATIONS['child']},
    'relmap': {rid: name for name, rid in RELATIONS.items()}
}

tax = Tax(meta)


#
# Seed taxonomy
#

# cat_a = add_symptom(None, 'Cat A')
# cat_a_1 = add_symptom(cat_a, 'Cat A.1')
# cat_a_2 = add_symptom(cat_a, 'Cat A.2')
# cat_a_2_1 = add_symptom(cat_a_2, 'Cat A.2.1')
# cat_b = add_symptom(None, 'Cat B')


#
# Set up routes
#

@app.route('/')
def get_root():
    return 'Server is up'


@app.route('/api/1.0.0/symptom/<int:symptom_id>', methods=['DELETE'])
def delete_symptom(symptom_id: int) -> Response:
    symptom = taxonomy.delete_symptom(symptom_id)

    return jsonify(symptom)


@dataclass
class Symptom:
    id: int
    parent: int
    names: List[str]


@dataclass
class DeepSymptom:
    id: int
    parent: int
    names: List[str]
    child_symptoms: List


def get_parent(node: int) -> Optional[int]:
    parents = [neighbor for neighbor, edge_props in tax.nxg[node].items()
               if RELATIONS['parent'] in edge_props]

    assert len(parents) <= 1

    return parents[0] if len(parents) == 1 else None


@app.route('/api/1.0.0/taxonomy', methods=['GET'])
def get_taxonomy() -> Dict[str, List[DeepSymptom]]:
    #
    # Determine root nodes
    #

    def find_root(node: int) -> int:
        parent = get_parent(node)

        if parent:
            return find_root(parent)
        else:
            return node

    root_nodes = {find_root(node) for node in tax.nxg.nodes}

    #
    # Build and return list of recusively populated symptoms
    #

    def get_children(node: int) -> List[int]:
        return [neighbor for neighbor, edge_props in tax.nxg[node].items()
                if RELATIONS['child'] in edge_props]

    def node_to_symptom(node: int) -> DeepSymptom:
        return DeepSymptom(id=node,
                           parent=get_parent(node),
                           names=tax.nxg.nodes[node]['names'],
                           child_symptoms=get_children(node))

    return {'root_symptoms': [node_to_symptom(root_node) for root_node in root_nodes]}


@app.route('/api/1.0.0/taxonomy', methods=['PUT'])
def put_taxonomy() -> Tuple[str, int]:
    global tax

    meta_yml: FileStorage = request.files['metaYml']
    nodes_txt: FileStorage = request.files['nodesTxt']
    edges_txt: FileStorage = request.files['edgesTxt']

    meta_dict = yaml.load(meta_yml.stream, Loader=yaml.FullLoader)

    str_nodes = (line.split(b' ', maxsplit=1) for line in nodes_txt.stream)
    nodes = ((int(node_id), eval(data)) for node_id, data in str_nodes)

    triples = (tuple(map(int, line.split())) for line in edges_txt.stream)

    tax = Tax.load_from_memory(meta_dict, nodes, triples)

    return '', 201


@app.route('/api/1.0.0/symptom', methods=['POST'])
def post_symptom() -> Tuple[str, int]:
    request_data: Dict = request.get_json()

    symptom = Symptom(id=request_data['id'],
                      parent=request_data['parent'],
                      names=request_data['names'])

    next_id = max(tax.nxg.nodes) + 1
    tax.nxg.add_nodes_from([(next_id, {'tid': '', 'names': symptom.names})])

    parent = symptom.parent

    if parent:
        tax.nxg.add_edges_from([
            (parent, next_id, RELATIONS['child']),
            (next_id, parent, RELATIONS['parent'])
        ])

    tax.nxg.add_edges_from([
        (next_id, next_id, RELATIONS['synonym'])
    ])

    return '', 201


@app.route('/api/1.0.0/symptom', methods=['PUT'])
def put_symptom() -> str:
    request_data: Dict = request.get_json()

    symptom = Symptom(id=request_data['id'],
                      parent=request_data['parent'],
                      names=request_data['names'])

    node = symptom.id

    #
    # Disconnect from old parent
    #

    old_parent = get_parent(node)

    if old_parent:
        tax.nxg.remove_edge(old_parent, node)
        tax.nxg.remove_edge(node, old_parent)

    #
    # Connect to new parent
    #

    new_parent = symptom.parent

    if new_parent:
        tax.nxg.add_edges_from([
            (new_parent, node, RELATIONS['child']),
            (node, new_parent, RELATIONS['parent']),
        ])

    #
    # Set new names
    #

    tax.nxg.nodes[node]['names'] = symptom.names

    return ''


#
# Run server
#

if __name__ == '__main__':
    app.run()
