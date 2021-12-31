# -*- coding: utf-8 -*-

# initializes logging
import rui_be  # noqa: F401

from flask import Flask
from flask_cors import CORS

from rui_be.routes.entities import entities
from rui_be.routes.matches import matches
from rui_be.routes.nodes import nodes
from rui_be.routes.predictions import predictions
from rui_be.routes.upload import upload


def main():
    app = create_app()
    app.run(host="0.0.0.0")


def create_app(config=None) -> Flask:
    app = Flask(__name__)

    if config:
        app.config.update(config)

    CORS(app)

    app.config["JSON_SORT_KEYS"] = False  # Simplify debugging in frontend

    @app.route("/")
    def get_root():
        return "Server is up"

    app.register_blueprint(entities)
    app.register_blueprint(matches)
    app.register_blueprint(nodes)
    app.register_blueprint(predictions)
    app.register_blueprint(upload)

    return app
