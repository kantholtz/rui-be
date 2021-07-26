from flask import Flask, request, make_response, jsonify
from flask_cors import CORS

from src import taxonomy
from src.taxonomy import root_symptoms, add_symptom, Symptom
from src.json_encoder import JsonEncoder

#
# Set up app object
#

app = Flask(__name__)

CORS(app)

app.config['JSON_SORT_KEYS'] = False  # Simplify debugging in frontend
app.json_encoder = JsonEncoder

#
# Seed taxonomy
#

cat_a = add_symptom(None, 'Cat A')
cat_a_1 = add_symptom(cat_a, 'Cat A.1')
cat_a_2 = add_symptom(cat_a, 'Cat A.2')
cat_b = add_symptom(None, 'Cat B')


#
# Set up routes
#

@app.route('/')
def get_root():
    return 'Server is up'


@app.route('/api/1.0.0/symptoms', methods=['GET'])
def get_symptoms():
    return {'taxonomy': root_symptoms}


@app.route('/api/1.0.0/symptom', methods=['POST'])
def post_symptoms():
    symptom = request.get_json()

    created_symptom = taxonomy.add_symptom(None, symptom['name'])

    return jsonify(created_symptom), 201


#
# Run server
#

if __name__ == '__main__':
    app.run()
