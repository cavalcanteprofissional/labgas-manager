# Auth blueprint - Login, register, logout
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from datetime import datetime, timedelta, timezone
import jwt
import logging

from utils.supabase_utils import get_supabase_client, get_admin_client
from blueprints.helpers import registrar_historico, is_user_active
from utils.limiter import limiter

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)


class User:
    def __init__(self, id, email, user_data=None):
        self.id = id
        self.email = email
        self.user_data = user_data or {}

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


def generate_jwt_token(user_id, secret_key):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    login_blocked_until = session.get("login_blocked_until")
    if login_blocked_until:
        if datetime.utcnow().isoformat() < login_blocked_until:
            remaining = 60  # segundos大致
            flash(f"Login bloqueado. Tente novamente em {remaining} segundos.", "danger")
            return redirect(url_for("auth.login"))
        else:
            session.pop("login_blocked_until", None)

    if request.method == "POST":
        login_attempts = session.get("login_attempts", 0)
        
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email e senha são obrigatórios", "danger")
            return redirect(url_for("auth.login"))

        supabase = get_supabase_client()

        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if response.user:
                from flask import current_app
                secret_key = current_app.secret_key
                
                session.clear()
                session["last_activity"] = datetime.now(timezone.utc).isoformat()
                
                session["user_id"] = response.user.id
                session["supabase_token"] = response.session.access_token
                session["jwt_token"] = generate_jwt_token(response.user.id, secret_key)
                session.permanent = True
                
                if not is_user_active(response.user.id):
                    session.clear()
                    flash("Usuário desativado. Contacte o administrador.", "danger")
                    return redirect(url_for("auth.login"))
                
                session["user_data"] = {
                    "id": response.user.id,
                    "email": response.user.email,
                    "email_confirmed_at": response.user.email_confirmed_at,
                }

                try:
                    from blueprints.helpers import get_authenticated_client
                    perfil_client = get_authenticated_client()
                    perfil = perfil_client.table("perfil").select("*").eq("id", response.user.id).execute()
                    nome = response.user.user_metadata.get("nome", "") if response.user.user_metadata else ""
                    
                    if not perfil.data:
                        get_admin_client().table("perfil").insert({
                            "id": response.user.id,
                            "role": "usuario",
                            "ativo": True,
                            "nome": nome,
                            "email": email,
                            "habilitar_abas": {"cilindro": True, "pressao": True, "elemento": True, "leitura": True, "historico": True}
                        }).execute()
                        flash("Perfil criado com sucesso!", "success")

                except Exception as e:
                    flash("Erro ao criar/atualizar perfil.", "warning")

                user = User(response.user.id, response.user.email, session["user_data"])
                login_user(user, remember=True, duration=timedelta(days=7))

                flash("Login realizado com sucesso!", "success")
                return redirect(url_for("dashboard"))

        except Exception as e:
            error_str = str(e)
            if "Invalid login credentials" in error_str:
                flash("Email ou senha inválidos.", "danger")
                login_attempts = session.get("login_attempts", 0) + 1
                session["login_attempts"] = login_attempts
                if login_attempts >= 5:
                    session["login_blocked_until"] = (datetime.utcnow() + timedelta(minutes=1)).isoformat()
                    session.pop("login_attempts", None)
            elif "rate limit" in error_str.lower():
                flash("Muitas tentativas de login. Tente novamente em 1 minuto.", "danger")
            else:
                flash(f"Erro no login: {error_str}", "danger")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        register_blocked_until = session.get("register_blocked_until")
        if register_blocked_until:
            if datetime.utcnow().isoformat() < register_blocked_until:
                flash("Registro bloqueado. Tente novamente em 1 minuto.", "danger")
                return redirect(url_for("auth.register"))
            else:
                session.pop("register_blocked_until", None)
        
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        nome = request.form.get("nome", "")

        if not email or not password:
            flash("Email e senha são obrigatórios", "danger")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Senhas não conferem.", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("A senha deve ter pelo menos 6 caracteres", "danger")
            return redirect(url_for("auth.register"))

        supabase = get_supabase_client()

        try:
            try:
                existing = supabase.auth.get_user(email)
                if existing.user:
                    flash("Este email já está cadastrado.", "danger")
                    return redirect(url_for("auth.register"))
            except Exception:
                pass

            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": {"nome": nome}},
            })

            if response.user:
                try:
                    get_admin_client().table("perfil").insert({
                        "id": response.user.id,
                        "role": "usuario",
                        "ativo": True,
                        "nome": nome,
                        "email": email,
                        "habilitar_abas": {"cilindro": True, "pressao": True, "elemento": True, "leitura": True, "historico": True}
                    }).execute()
                    
                    # Registrar cadastro no histórico
                    registrar_historico("perfil", "criado", email, response.user.id)
                except Exception as perfil_error:
                    error_str = str(perfil_error)
                    if "23503" in error_str or "foreign key" in error_str.lower():
                        flash("Este email já está cadastrado.", "danger")
                    else:
                        flash("Conta criada! Você pode fazer login.", "success")
                    return redirect(url_for("auth.login"))

                flash("Conta criada! Verifique seu email para confirmação.", "success")
                return redirect(url_for("auth.login"))

        except Exception as e:
            error_str = str(e)
            if "email rate limit exceeded" in error_str.lower():
                flash("Muitas tentativas de registro. Tente novamente em 1 minuto.", "danger")
            elif "User already registered" in error_str:
                flash("Este email já está cadastrado.", "danger")
            elif "User already registered" in error_str:
                flash("Este email já está cadastrado.", "danger")
            else:
                flash(f"Erro no registro: {error_str}", "danger")
                
            register_attempts = session.get("register_attempts", 0) + 1
            session["register_attempts"] = register_attempts
            if register_attempts >= 3:
                session["register_blocked_until"] = (datetime.utcnow() + timedelta(minutes=1)).isoformat()
                session.pop("register_attempts", None)

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    supabase = get_supabase_client()
    try:
        supabase.auth.sign_out()
    except:
        pass
    
    session.clear()
    logout_user()
    flash("Logout realizado com sucesso!", "success")
    return redirect(url_for("auth.login"))
