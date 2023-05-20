from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config")

    register_blueprints(app)

    return app

def register_blueprints(app):
    from app.apis import api_blp
    from app.views import main_blp
    app.register_blueprint(api_blp)
    app.register_blueprint(main_blp)