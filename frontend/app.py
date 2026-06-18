import os
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_login import LoginManager, login_required, current_user
from flask_wtf import CSRFProtect
from flask_caching import Cache
from dotenv import load_dotenv
from supabase import create_client, Client

from blueprints.helpers import get_authenticated_client
from utils.limiter import limiter
from utils.constants import ELEMENTO_CORES, ELEMENTO_CORES_LEITURAS, PALETA_CILINDRO, PALETA_ELEMENTO, PALETA_LEITURA
from utils.erros_utils import formatar_erro_supabase

# Carrega .env.local para desenvolvimento local (se existir)
# Na Vercel, as variáveis são injetadas automaticamente via Environment Variables
try:
    load_dotenv('.env.local')
except Exception:
    pass  # Se não existir, continua sem erro

app = Flask(__name__)
app.secret_key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("FLASK_SECRET_KEY") or os.getenv("SECRET_KEY")
if not app.secret_key:
    raise ValueError("SUPABASE_SECRET_KEY é obrigatória. Defina a variável de ambiente.")

# Configuração de segurança baseada no ambiente
is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('VERCEL_ENV') == 'production'
if is_production:
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

csrf = CSRFProtect(app)

app.config["RATELIMIT_DEFAULT"] = os.getenv("RATE_LIMIT", "500 per day;200 per hour")
app.config["RATELIMIT_STORAGE_URI"] = os.getenv("REDIS_URL", "memory://")
limiter.init_app(app)

cache = Cache(app, config={
    "CACHE_TYPE": os.getenv("CACHE_TYPE", "SimpleCache"),
    "CACHE_DEFAULT_TIMEOUT": int(os.getenv("CACHE_TIMEOUT", "300")),
    "CACHE_THRESHOLD": 100
})

# URLs do Supabase (injetadas pela Vercel ou via .env.local)
SUPABASE_URL = os.getenv("SUPABASE_URL")
# Vercel injeta como SUPABASE_ANON_KEY, desenvolvimento local usa SUPABASE_KEY
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")
# Vercel injeta como SUPABASE_SERVICE_ROLE_KEY, desenvolvimento local usa SUPABASE_SERVICE_KEY
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL e SUPABASE_KEY são obrigatórios")

import logging
logging.basicConfig(level=logging.WARNING if is_production else logging.INFO)
logger = logging.getLogger(__name__)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "warning"

from blueprints.auth import User

@login_manager.user_loader
def load_user(user_id):
    user_data = session.get("user_data")
    if user_data:
        return User(user_id, user_data.get("email"), user_data)
    return None


INACTIVITY_TIMEOUT_MINUTES = int(os.getenv("INACTIVITY_TIMEOUT_MINUTES", "10"))
INACTIVITY_TIMEOUT = timedelta(minutes=INACTIVITY_TIMEOUT_MINUTES)

PUBLIC_ENDPOINTS = [
    'auth.login',
    'auth.register', 
    'auth.logout',
    'static',
    '_debug_toolbar.static'
]

@app.before_request
def check_inactivity():
    if request.endpoint is None:
        return
    
    if request.endpoint in PUBLIC_ENDPOINTS:
        return
    
    if 'user_id' not in session:
        return
    
    last_activity = session.get('last_activity')
    now = datetime.now(timezone.utc)
    
    if last_activity:
        try:
            last_activity_dt = datetime.fromisoformat(str(last_activity))
            if now - last_activity_dt > INACTIVITY_TIMEOUT:
                session.clear()
                flash('Sessão expirada por inatividade. Faça login novamente.', 'warning')
                logger.info(f"Sessão expirada por inatividade para user_id: {session.get('user_id', 'desconhecido')}")
                return redirect(url_for('auth.login'))
        except (ValueError, TypeError):
            session['last_activity'] = now.isoformat()
    
    session['last_activity'] = now.isoformat()


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin:
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else ["http://localhost:5000", "http://127.0.0.1:5000"]
        if origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
    
    if request.method == "OPTIONS":
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
    
    if is_production:
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' https://cdn.jsdelivr.net; img-src 'self' data:;"
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response


@app.context_processor
def inject_user_info():
    from blueprints.helpers import get_habilitar_abas
    from datetime import datetime
    from utils.constants import ICON_TIPO, COR_TIPO
    
    user_id = session.get('user_id')
    
    if user_id and 'cached_user_info' not in session:
        from utils.supabase_utils import get_admin_client
        client = get_admin_client()
        
        perfil_response = client.table("perfil").select("role,nome,habilitar_abas").eq("id", user_id).execute()
        
        if perfil_response.data:
            perfil = perfil_response.data[0]
            from blueprints.helpers import ABAS_DEFAULT
            user_role = perfil.get('role', 'usuario')
            session['cached_user_info'] = {
                'user_role': user_role,
                'user_name': perfil.get('nome', ''),
                'is_admin': user_role in ('admin', 'dev'),
                'is_dev': user_role == 'dev',
                'habilitar_abas': perfil.get('habilitar_abas') or ABAS_DEFAULT
            }
        else:
            from blueprints.helpers import ABAS_DEFAULT
            session['cached_user_info'] = {
                'user_role': 'usuario',
                'user_name': '',
                'is_admin': False,
                'habilitar_abas': ABAS_DEFAULT
            }
    
    from datetime import timezone
    last_activity = session.get('last_activity')
    remaining = 0
    if last_activity:
        try:
            last_dt = datetime.fromisoformat(last_activity)
            elapsed = (datetime.now(timezone.utc) - last_dt).total_seconds()
            remaining = max(0, int(INACTIVITY_TIMEOUT.total_seconds() - elapsed))
        except (ValueError, TypeError):
            pass

    cached = session.get('cached_user_info', {})
    
    return dict(
        is_admin=cached.get('is_admin', False), 
        user_role=cached.get('user_role', 'usuario'), 
        user_name=cached.get('user_name', ''), 
        pode_acessar_aba=get_habilitar_abas,
        today=datetime.now().strftime("%Y-%m-%d"),
        ICON_TIPO=ICON_TIPO,
        COR_TIPO=COR_TIPO,
        session_remaining_seconds=remaining,
    )


@app.template_filter("formatar_data")
def formatar_data(data):
    if not data:
        return "-"
    if isinstance(data, str):
        if "T" in data:
            data = data.split("T")[0]
        try:
            dt = datetime.strptime(data, "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            return data
    return data


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("auth.login"))


@app.route("/dashboard")
@login_required
def dashboard():
    from utils.supabase_utils import get_supabase_client
    from blueprints.helpers import get_user_id
    
    user_id = get_user_id()
    supabase = get_supabase_client()
    
    cilindro_response = supabase.table("cilindro").select("*").eq("user_id", user_id).execute()
    elementos_response = supabase.table("elemento").select("*").eq("user_id", user_id).order("nome").execute()
    leituras_response = supabase.table("leitura").select("*").eq("user_id", user_id).execute()
    try:
        pressoes_response = supabase.table("pressao").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        pressoes = pressoes_response.data or []
    except Exception:
        pressoes = []

    try:
        amostras_response = supabase.table("amostra").select("*", count="exact").eq("user_id", user_id).order("numero_amostra", desc=True).execute()
        amostras_data = amostras_response.data or []
        amostras_total = amostras_response.count or 0
    except Exception:
        amostras_data = []
        amostras_total = 0

    cilindro = cilindro_response.data or []
    elementos = elementos_response.data or []
    leituras = leituras_response.data or []

    ativos = len([c for c in cilindro if c.get("status") == "ativo"])

    status_counts = {}
    for c in cilindro:
        status = c.get("status", "desconhecido")
        status_counts[status] = status_counts.get(status, 0) + 1

    status_labels = list(status_counts.keys())
    status_values = list(status_counts.values())

    cilindro_leituras = {}
    for a in leituras:
        cil_id = a.get("cilindro_id")
        if cil_id:
            cilindro_leituras[cil_id] = cilindro_leituras.get(cil_id, 0) + a.get("quantidade", 1)

    cilindro_leituras_labels = []
    cilindro_leituras_values = []
    cilindro_dict = {c.get("id"): c.get("codigo") for c in cilindro}
    for cil_id, count in sorted(cilindro_leituras.items(), key=lambda x: cilindro_dict.get(x[0], str(x[0]))):
        cilindro_leituras_labels.append(cilindro_dict.get(cil_id, str(cil_id)))
        cilindro_leituras_values.append(count)

    elemento_leituras_count = {}
    for a in leituras:
        elem_id = a.get("elemento_id")
        if elem_id:
            elemento_leituras_count[elem_id] = elemento_leituras_count.get(elem_id, 0) + a.get("quantidade", 1)

    elemento_dict = {e.get("id"): e.get("nome") for e in elementos}
    elementos_mais_analisados = []
    for elem_id, count in sorted(elemento_leituras_count.items(), key=lambda x: x[1], reverse=True)[:5]:
        elementos_mais_analisados.append({
            "nome": elemento_dict.get(elem_id, str(elem_id)),
            "quantidade": count
        })

    tempo_chama_elementos = {}
    for a in leituras:
        elem_id = a.get("elemento_id")
        tempo = a.get("tempo_chama", "00:00:00")
        if elem_id and tempo:
            try:
                partes = tempo.split(":")
                minutos = int(partes[0]) * 60 + int(partes[1]) + int(partes[2])/60
                tempo_chama_elementos[elem_id] = tempo_chama_elementos.get(elem_id, 0) + minutos
            except:
                pass

    elementos_labels = []
    elementos_consumo_tempo = []
    for e in elementos:
        eid = e.get("id")
        consumo = float(e.get("consumo_lpm", 0))
        tempo = tempo_chama_elementos.get(eid, 0)
        elementos_labels.append(e.get("nome"))
        elementos_consumo_tempo.append(round(consumo * tempo, 2))

    eficiencia = {}
    for a in leituras:
        cil_id = a.get("cilindro_id")
        elem_id = a.get("elemento_id")
        if cil_id and elem_id:
            key = f"{cil_id}-{elem_id}"
            eficiencia[key] = eficiencia.get(key, 0) + a.get("quantidade", 1)

    eficiencia_labels = []
    eficiencia_values = []
    for key, count in sorted(eficiencia.items(), key=lambda x: x[1], reverse=True)[:10]:
        cil_id, elem_id = key.split("-")
        nome_cil = cilindro_dict.get(cil_id, str(cil_id))
        nome_elem = elemento_dict.get(elem_id, str(elem_id))
        eficiencia_labels.append(f"{nome_cil} × {nome_elem}")
        eficiencia_values.append(count)

    total_quantidade = sum(a.get("quantidade", 1) for a in leituras)

    return render_template(
        "dashboard.html",
        cilindro=cilindro,
        elementos=elementos,
        leituras=leituras,
        pressoes=pressoes,
        amostras=amostras_data,
        ativos=ativos,
        status_counts=status_counts,
        status_labels=status_labels,
        status_values=status_values,
        cilindro_leituras_labels=cilindro_leituras_labels,
        cilindro_leituras_values=cilindro_leituras_values,
        elementos_mais_analisados=elementos_mais_analisados,
        elementos_labels=elementos_labels,
        elementos_consumo_tempo=elementos_consumo_tempo,
        eficiencia_labels=eficiencia_labels,
        eficiencia_values=eficiencia_values,
        eficiencia_data=eficiencia,
        cilindro_dict=cilindro_dict,
        elemento_dict=elemento_dict,
        elemento_cores=ELEMENTO_CORES,
        elemento_cores_leituras=ELEMENTO_CORES_LEITURAS,
        paleta_cilindro=PALETA_CILINDRO,
        paleta_elemento=PALETA_ELEMENTO,
        paleta_leitura=PALETA_LEITURA,
        total_quantidade=total_quantidade,
        amostras_total=amostras_total,
    )


@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    from blueprints.helpers import get_user_id, get_authenticated_client, get_habilitar_abas, is_admin
    
    user_id = get_user_id()
    supabase = get_authenticated_client()

    perfil_response = supabase.table("perfil").select("*").eq("id", user_id).execute()
    perfil_data = perfil_response.data[0] if perfil_response.data else {}
    user_role = perfil_data.get("role", "usuario")
    user_nome = perfil_data.get("nome", "")
    
    if is_admin():
        habilitar_abas = {"cilindro": True, "pressao": True, "elemento": True, "leitura": True, "amostra": True, "historico": True}
    else:
        habilitar_abas = get_habilitar_abas(user_id)

    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "update_profile":
            nome = request.form.get("nome", "").strip()
            
            try:
                perfil_check = supabase.table("perfil").select("id").eq("id", user_id).execute()
                
                if not perfil_check.data:
                    supabase.table("perfil").insert({
                        "id": user_id,
                        "role": "usuario",
                        "ativo": True,
                        "nome": nome,
                        "email": current_user.email
                    }).execute()
                    flash("Perfil criado com sucesso!", "success")
                else:
                    supabase.table("perfil").update({"nome": nome}).eq("id", user_id).execute()
                    flash("Perfil atualizado com sucesso!", "success")
            except Exception as e:
                flash("Erro ao atualizar perfil.", "danger")
            
            return redirect(url_for("perfil"))

    cilindro_response = supabase.table("cilindro").select("id").eq("user_id", user_id).execute()
    elementos_response = supabase.table("elemento").select("id").eq("user_id", user_id).execute()
    leituras_response = supabase.table("leitura").select("id").eq("user_id", user_id).execute()
    pressoes_response = supabase.table("pressao").select("id").eq("user_id", user_id).execute()
    amostras_response = supabase.table("amostra").select("id").eq("user_id", user_id).execute()

    stats = {
        "cilindros": len(cilindro_response.data or []),
        "elementos": len(elementos_response.data or []),
        "leituras": len(leituras_response.data or []),
        "pressoes": len(pressoes_response.data or []),
        "amostras": len(amostras_response.data or []),
    }

    return render_template("perfil.html", stats=stats, user_role=user_role, user_nome=user_nome, habilitar_abas=habilitar_abas)


@app.route("/api/buscar-codigo", methods=["POST"])
@login_required
def api_buscar_codigo():
    """Retorna ID do cilindro pelo código"""
    data = request.get_json()
    codigo = data.get("codigo", "").strip()
    
    if not codigo:
        return {"error": "Código é obrigatório"}, 400
    
    try:
        from blueprints.helpers import get_user_id, is_dev
        user_id = get_user_id()
        dev = is_dev()
        
        # Buscar cilindro pelo código
        if dev:
            response = supabase.table("cilindro").select("id,codigo").eq("codigo", codigo).execute()
        else:
            response = supabase.table("cilindro").select("id,codigo").eq("codigo", codigo).eq("user_id", user_id).execute()
        
        if response.data:
            return {"id": response.data[0]["id"], "codigo": response.data[0]["codigo"]}
        else:
            return {"error": "Cilindro não encontrado"}, 404
    except Exception as e:
        return {"error": formatar_erro_supabase(str(e), "buscar código")}, 500


@app.route("/api/buscar-elemento", methods=["POST"])
@login_required
def api_buscar_elemento():
    """Retorna ID do elemento pelo nome"""
    data = request.get_json()
    nome = data.get("nome", "").strip()
    
    if not nome:
        return {"error": "Nome é obrigatório"}, 400
    
    try:
        from blueprints.helpers import get_user_id, is_dev
        user_id = get_user_id()
        dev = is_dev()
        
        # Normalizar nome para busca (primeira maiúscula)
        nome_normalizado = nome.title()
        
        # Buscar elemento pelo nome
        if dev:
            response = supabase.table("elemento").select("id,nome").eq("nome", nome_normalizado).execute()
        else:
            response = supabase.table("elemento").select("id,nome").eq("nome", nome_normalizado).eq("user_id", user_id).execute()
        
        if response.data:
            return {"id": response.data[0]["id"], "nome": response.data[0]["nome"]}
        else:
            return {"error": "Elemento não encontrado"}, 404
    except Exception as e:
        return {"error": formatar_erro_supabase(str(e), "buscar elemento")}, 500


@app.route("/api/dados-usuario", methods=["GET"])
@login_required
def api_dados_usuario():
    """Retorna cilindro e elementos do usuário para quick-select"""
    try:
        from blueprints.helpers import get_user_id
        user_id = get_user_id()
        
        # Buscar cilindos
        cilindro_response = supabase.table("cilindro").select("id,codigo").eq("user_id", user_id).order("codigo").execute()
        cilindros = [{"id": c["id"], "codigo": c["codigo"]} for c in (cilindro_response.data or [])]
        
        # Buscar elementos
        elemento_response = supabase.table("elemento").select("id,nome").eq("user_id", user_id).order("nome").execute()
        elementos = [{"id": e["id"], "nome": e["nome"]} for e in (elemento_response.data or [])]
        
        return {"cilindros": cilindros, "elementos": elementos}
    except Exception as e:
        return {"error": formatar_erro_supabase(str(e), "buscar dados do usuário")}, 500


from blueprints.auth import auth_bp
from blueprints.cilindro import cilindro_bp
from blueprints.elemento import elemento_bp
from blueprints.leitura import leitura_bp
from blueprints.admin import admin_bp
from blueprints.historico import historico_bp
from blueprints.pressao import pressao_bp
from blueprints.amostra import amostra_bp

app.register_blueprint(auth_bp)
app.register_blueprint(cilindro_bp)
app.register_blueprint(elemento_bp)
app.register_blueprint(leitura_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(historico_bp)
app.register_blueprint(pressao_bp)
app.register_blueprint(amostra_bp)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    if is_production:
        debug = False
    app.run(host="0.0.0.0", port=port, debug=debug)
