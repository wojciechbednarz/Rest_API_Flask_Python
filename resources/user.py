import jwt.algorithms
from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt, jwt_required

from blocklist import add_token_to_blocklist
from db import db
from models import UserModel
from schemas import UserSchema, MessageSchema
from datetime import timedelta

blp = Blueprint("Users", "users", description="Operations on users.")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel(username=user_data["username"],
                         password=pbkdf2_sha256.hash(user_data["password"]))

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            abort(409, message="User with this username already exists.")
        username = user_data["username"]
        return {"message": f"User {username} created successfully."}, 201


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            expires_in_minutes = 30
            expires_delta = timedelta(minutes=expires_in_minutes)
            access_token = create_access_token(identity=user.id, fresh=True, expires_delta=expires_delta)
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}

        abort(401, message="Invalid credentials.")


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        expires_in_minutes = 30
        expires_delta = timedelta(minutes=expires_in_minutes)
        new_token = create_access_token(identity=current_user, fresh=False, expires_delta=expires_delta)
        jti = get_jwt()["jti"]
        add_token_to_blocklist(jti)
        return {"access_token": new_token}


@blp.route('/logout')
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        # Zabezpieczenie żeby nie używać "non-fresh" tokena - ma byc uzywany typ "fresh"
        add_token_to_blocklist(jti)
        return jsonify({"message:": "Successfully logged out."}), 200


@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    @blp.response(200, MessageSchema)
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)

        if user is None:
            abort(404, message="User with provided username not found")

        db.session.delete(user)
        db.session.commit()
        return {"message": "User successfully deleted."}, 200
