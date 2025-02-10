from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, decode_token, get_jwt
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError, WrongTokenError, RevokedTokenError, FreshTokenRequired, CSRFError
import jwt
from models.user import user_schema
from db.mongo_client import get_db
from werkzeug.security import generate_password_hash, check_password_hash

users_bp = Blueprint('users', __name__)
db = get_db()
users_collection = db.get_collection('users')

@users_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    data['password'] = generate_password_hash(data['password'])
    if users_collection.find_one({"username": data['username']}):
        return jsonify({"error": "User already exists"}), 400
    users_collection.insert_one(data)
    return jsonify({"message": "User registered successfully"}), 201

@users_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = users_collection.find_one({"username": data['username']})
    if user and check_password_hash(user['password'], data['password']):
        access_token = create_access_token(identity=user['username'])
        refresh_token = create_refresh_token(identity=user['username'])
        user_data = {
            "username": user['username'],
            "role": user['role'],
            "access_token": access_token,
            "refresh_token": refresh_token  
        }
        
        # Create a response object
        response = make_response(jsonify(user_data))
        
        # Set the token as an HttpOnly cookie
        response.set_cookie('authToken', access_token, httponly=True, secure=False, samesite='Strict')
        return response, 200
    return jsonify({"message": "Invalid credentials"}), 401

@users_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200 

@users_bp.route("/refresh", methods=["GET"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify(access_token=access_token), 200

@users_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = make_response(jsonify({"message": "Logged out successfully"}))
    response.set_cookie('authToken', '', httponly=True, secure=False, samesite='Strict', expires=0)
    return response, 200

@users_bp.route("/isTokenExpired", methods=["GET"]) 
@jwt_required()
def isTokenExpired():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"message": "Authorization header is missing"}), 400

    try:
        token = auth_header.split()[1]
    except IndexError:
        return jsonify({"message": "Bearer token is malformed"}), 400

    try:
        decoded_token = decode_token(token)
        exp_timestamp = decoded_token['exp']
        current_timestamp = datetime.now(timezone.utc).timestamp()
        if exp_timestamp < current_timestamp:
            return jsonify({"message": "Token is expired"}), 401
    except (NoAuthorizationError, InvalidHeaderError, WrongTokenError, RevokedTokenError, FreshTokenRequired, CSRFError) as e:
        return jsonify({"message": "Token verification failed", "error": str(e)}), 422
    except Exception as e:
        return jsonify({"message": "Error decoding token", "error": str(e)}), 400

    return jsonify({"message": "Token is not expired"}), 200

