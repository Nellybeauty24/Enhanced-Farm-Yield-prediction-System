from flask import request, jsonify, Blueprint, current_app
from datetime import datetime, timedelta
import jwt
import logging

from .. import db
from ..models.user import User

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        if not request.is_json:
            return jsonify({"status": "error", "message": "Request must be JSON"}), 400
            
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')
        
        if not email or not name or not password:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
            
        if User.query.filter_by(email=email).first():
            return jsonify({"status": "error", "message": "Email already registered"}), 400
            
        user = User(email=email, name=name)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "status": "success",
            "message": "User registered successfully",
            "token": token,
            "user": user.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error in register: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({"status": "error", "message": "Failed to register user"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        if not request.is_json:
            return jsonify({"status": "error", "message": "Request must be JSON"}), 400
            
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"status": "error", "message": "Missing email or password"}), 400
            
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({"status": "error", "message": "Invalid email or password"}), 401
            
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "status": "success",
            "token": token,
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in login: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": "Failed to login"}), 500

from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({"status": "error", "message": "Token is missing"}), 401
            
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({"status": "error", "message": "User not found"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"status": "error", "message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"status": "error", "message": "Invalid token"}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated
