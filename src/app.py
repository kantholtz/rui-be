from dataclasses import dataclass
from typing import Dict, Tuple, List

import yaml
from draug.homag.tax import Tax, RELATIONS
from flask import Flask, request
from flask_cors import CORS
from werkzeug.datastructures import FileStorage

#
# Set up app object
#

app = Flask(__name__)

CORS(app)

app.config['JSON_SORT_KEYS'] = False  # Simplify debugging in frontend

#
# Create initial taxonomy
#

meta = {
    'name': 'symptax.v4',
    'reflexive': (RELATIONS['synonym'],),
    'inverse': {RELATIONS['parent']: RELATIONS['child']},
    'relmap': {rid: name for name, rid in RELATIONS.items()}
}

tax = Tax(meta)


#
# Set up routes
#

@app.route('/')
def get_root():
    return 'Server is up'


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
    children: List


@app.route('/api/1.1.0/taxonomy', methods=['GET'])
def get_taxonomy() -> Dict[str, List[DeepSymptom]]:
    root_symptom_ids = tax.find_root_symptoms()

    #
    # Build and return list of recusively populated symptoms
    #

    def id_to_symptom(symptom_id: int) -> DeepSymptom:
        return DeepSymptom(id=symptom_id,
                           parent=tax.get_parent(symptom_id),
                           names=tax.nxg.nodes[symptom_id]['names'],
                           children=tax.get_children(symptom_id))

    return {'taxonomy': [id_to_symptom(root_node) for root_node in root_symptom_ids]}


@app.route('/api/1.1.0/taxonomy', methods=['PUT'])
def put_taxonomy() -> str:
    global tax

    meta_yml: FileStorage = request.files['metaYml']
    nodes_txt: FileStorage = request.files['nodesTxt']
    edges_txt: FileStorage = request.files['edgesTxt']

    meta_dict = yaml.load(meta_yml.stream, Loader=yaml.FullLoader)

    str_nodes = (line.split(b' ', maxsplit=1) for line in nodes_txt.stream)
    nodes = ((int(node_id), eval(data)) for node_id, data in str_nodes)

    triples = (tuple(map(int, line.split())) for line in edges_txt.stream)

    tax = Tax.load_from_memory(meta_dict, nodes, triples)

    return ''


@app.route('/api/1.1.0/symptom', methods=['POST'])
def post_symptom() -> Tuple[str, int]:
    request_data: Dict = request.get_json()

    symptom = Symptom(id=request_data['id'],
                      parent=request_data['parent'],
                      names=request_data['names'])

    tax.add_symptom(symptom.parent, symptom.names)

    return '', 201


@app.route('/api/1.1.0/symptom', methods=['PUT'])
def put_symptom() -> str:
    request_data: Dict = request.get_json()

    symptom = Symptom(id=request_data['id'],
                      parent=request_data['parent'],
                      names=request_data['names'])

    tax.update_symptom(symptom.id, symptom.parent, symptom.names)

    return ''


@app.route('/api/1.1.0/symptom/<int:symptom_id>', methods=['DELETE'])
def delete_symptom(symptom_id: int) -> str:
    tax.delete_symptom(symptom_id)

    return ''


#
# Run server
#

if __name__ == '__main__':
    app.run()
