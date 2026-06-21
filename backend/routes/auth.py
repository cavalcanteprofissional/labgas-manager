from flask import Blueprint, request, jsonify
from utils.supabase import get_supabase
from utils.decorators import generate_token, token_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email e senha são obrigatórios'}), 400
    
    supabase = get_supabase()
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data['email'],
            "password": data['password']
        })
        
        if not response.user:
            return jsonify({'message': 'Credenciais inválidas'}), 401
        
        token = generate_token(response.user.id, response.user.email)
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'token': token,
            'user': {
                'id': response.user.id,
                'email': response.user.email,
                'role': response.user.user_metadata.get('role', 'viewer') if response.user.user_metadata else 'viewer'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Erro no login. Verifique suas credenciais.'}), 401


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email e senha são obrigatórios'}), 400
    
    supabase = get_supabase()
    
    try:
        user_data = {
            "name": data.get('name', '')
        }
        
        response = supabase.auth.sign_up({
            "email": data['email'],
            "password": data['password'],
            "options": {
                "data": user_data
            }
        })
        
        if response.user:
            return jsonify({
                'message': 'Conta criada com sucesso! Verifique seu email para confirmação.',
                'user_id': response.user.id
            }), 201
        else:
            return jsonify({'message': 'Erro ao criar conta'}), 400
            
    except Exception:
        return jsonify({'message': 'Erro no registro. Tente novamente.'}), 400


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    supabase = get_supabase()
    
    try:
        supabase.auth.sign_out()
        return jsonify({'message': 'Logout realizado com sucesso'}), 200
    except Exception:
        return jsonify({'message': 'Erro no logout. Tente novamente.'}), 400


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    return jsonify({
        'user_id': request.user_id,
        'email': request.user_email
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'message': 'Email é obrigatório'}), 400
    
    supabase = get_supabase()
    
    try:
        supabase.auth.reset_password_for_email(data['email'])
        return jsonify({'message': 'Email de recuperação enviado'}), 200
    except Exception:
        return jsonify({'message': 'Erro ao enviar email de recuperação. Tente novamente.'}), 400
