from flask import Flask
from flask_cors import CORS

from src.taxonomy import root_symptoms, add_symptom
from src.json_encoder import JsonEncoder

#
# Set up app object
#

app = Flask(__name__)

CORS(app)

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
def hello_world():
    return {'taxonomy': root_symptoms}


#
# Run server
#

if __name__ == '__main__':
    app.run()
