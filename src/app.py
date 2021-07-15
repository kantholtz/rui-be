from flask import Flask

from src.taxonomy import root_symptoms
from src.json_encoder import JsonEncoder

app = Flask(__name__)

app.json_encoder = JsonEncoder


@app.route('/')
def hello_world():
    return {'taxonomy': root_symptoms}


if __name__ == '__main__':
    app.run()
