from flask import Flask
from flask_cors import CORS

from src.rui_be.routes.entities import entities
from src.rui_be.routes.matches import matches
from src.rui_be.routes.nodes import nodes
from src.rui_be.routes.predictions import predictions
from src.rui_be.routes.upload import upload


def create_app(config=None) -> Flask:
    app = Flask(__name__)

    if config:
        app.config.update(config)

    CORS(app)

    app.config['JSON_SORT_KEYS'] = False  # Simplify debugging in frontend

    @app.route('/')
    def get_root():
        return 'Server is up'

    app.register_blueprint(entities)
    app.register_blueprint(matches)
    app.register_blueprint(nodes)
    app.register_blueprint(predictions)
    app.register_blueprint(upload)

    return app
