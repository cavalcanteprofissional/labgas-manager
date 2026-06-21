from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import jwt
from config import SECRET_KEY


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token é necessário'}), 401
        
        if not token:
            return jsonify({'message': 'Token não fornecido'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user_id = data['user_id']
            request.user_email = data.get('email')
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def generate_token(user_id: str, email: str) -> str:
    now = datetime.utcnow()
    payload = {
        'user_id': user_id,
        'email': email,
        'iat': now,
        'exp': now + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
