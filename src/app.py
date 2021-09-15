from flask import Flask
from flask_cors import CORS

from src.routes.entities import entities
from src.routes.matches import matches
from src.routes.nodes import nodes
from src.routes.predictions import predictions
from src.routes.upload import upload


def main():
    app = create_app()
    app.run()


def create_app() -> Flask:
    app = Flask(__name__)

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


if __name__ == '__main__':
    main()
