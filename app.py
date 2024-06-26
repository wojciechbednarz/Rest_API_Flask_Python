import os
import time

from blocklist import is_token_in_blocklist
from flask import Flask, jsonify
from flask_smorest import Api
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint

from db import db
from reset_db import reset_db
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate


def create_app(db_url=None):
    app = Flask(__name__)

    @app.route("/reset", methods=['POST'])
    def reset():
        reset_db()
        return {'message': 'Database reset successful'}, 200

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)

    app.config["JWT_SECRET_KEY"] = "63211992552047350090104967246493725410"
    jwt = JWTManager(app)

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        if jwt_payload["exp"] < time.time():
            return (
                jsonify(
                    {"description": "The token is not fresh.", "error": "fresh_token_requried"}), 401)
        else:
            return jsonify({"description": "Token is fresh."}), 200

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return is_token_in_blocklist(jti)

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}), 401)

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        # Tutaj powinno byc raczej cos w stylu: sprawdz w bazie danych czy uzytkownik ma prawa admina.
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}), 401)

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({"message": "Signature verification failed.", "error": "token_invalid"}), 401)

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {"message": "Request does not contain an access token.", "error": "authorization_required"}), 401)

    # No longer need since usage of flask-migrate
    # with app.app_context():
    #     db.create_all()

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
