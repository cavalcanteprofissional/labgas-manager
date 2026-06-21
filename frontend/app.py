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
app.secret_key = os.getenv("FLASK_SECRET_KEY") or os.getenv("SECRET_KEY") or os.getenv("SUPABASE_SECRET_KEY")
if not app.secret_key:
    raise ValueError("FLASK_SECRET_KEY é obrigatória. Defina a variável de ambiente.")

# Configuração de segurança baseada no ambiente
is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('VERCEL_ENV') == 'production'
if is_production:
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

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


@app.before_request
def populate_user_cache():
    if request.endpoint is None:
        return
    if request.endpoint in PUBLIC_ENDPOINTS:
        return
    user_id = session.get('user_id')
    if user_id and 'cached_user_info' not in session:
        from utils.supabase_utils import get_admin_client
        from blueprints.helpers import ABAS_DEFAULT
        client = get_admin_client()
        try:
            perfil_response = client.table("perfil").select("role,nome,habilitar_abas").eq("id", user_id).execute()
            if perfil_response.data:
                perfil = perfil_response.data[0]
                user_role = perfil.get('role', 'usuario')
                session['cached_user_info'] = {
                    'user_role': user_role,
                    'user_name': perfil.get('nome', ''),
                    'is_admin': user_role in ('admin', 'dev'),
                    'is_dev': user_role == 'dev',
                    'habilitar_abas': perfil.get('habilitar_abas') or ABAS_DEFAULT
                }
            else:
                session['cached_user_info'] = {
                    'user_role': 'usuario',
                    'user_name': '',
                    'is_admin': False,
                    'is_dev': False,
                    'habilitar_abas': ABAS_DEFAULT
                }
        except Exception:
            session['cached_user_info'] = {
                'user_role': 'usuario',
                'user_name': '',
                'is_admin': False,
                'is_dev': False,
                'habilitar_abas': ABAS_DEFAULT
            }


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
    from datetime import datetime, timezone
    from utils.constants import ICON_TIPO, COR_TIPO

    last_activity = session.get('last_activity')
    remaining = 0
    if last_activity:
        try:
            last_dt = datetime.fromisoformat(last_activity)
            if last_dt.tzinfo is None:
                last_dt = last_dt.replace(tzinfo=timezone.utc)
            elapsed = (datetime.now(timezone.utc) - last_dt).total_seconds()
            remaining = max(0, int(INACTIVITY_TIMEOUT.total_seconds() - elapsed))
        except (ValueError, TypeError):
            pass

    cached = session.get('cached_user_info', {})

    return dict(
        is_admin=cached.get('is_admin', False),
        is_dev=cached.get('is_dev', False),
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


def _parse_tempo_chama(tempo_str):
    if not tempo_str:
        return 0
    partes = tempo_str.split(":")
    try:
        if len(partes) == 3:
            return int(partes[0]) * 60 + int(partes[1]) + int(partes[2]) / 60
        if len(partes) == 2:
            return int(partes[0]) * 60 + int(partes[1])
    except (ValueError, IndexError):
        pass
    return 0


MESES_PT = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}


def _formatar_mes_ano(data_str):
    """'2024-03-15' ou '2024-03' → 'Mar 2024'"""
    if not data_str or not isinstance(data_str, str):
        return data_str or ""
    partes = data_str.split("-")
    try:
        mes = int(partes[1])
        ano = partes[0]
        return f"{MESES_PT[mes]} {ano}"
    except (IndexError, ValueError, KeyError):
        return data_str


def _compute_kpis(leituras, cilindro, elementos, amostras_data, ae_data, pressoes):
    from collections import defaultdict
    cilindro_dict = {c["id"]: c for c in cilindro}
    elemento_dict = {e["id"]: e for e in elementos}

    cilindros_ativos = sum(1 for c in cilindro if c.get("status") == "ativo")

    # Single-pass sobre leituras: gas, total, cilindro, mes, top elementos
    gas_por_cilindro = defaultdict(float)
    total_gas_consumido = 0.0
    total_quantidade = 0
    leituras_por_cilindro = defaultdict(int)
    leituras_por_mes = defaultdict(int)
    elem_leituras = defaultdict(int)

    for a in leituras:
        qtd = a.get("quantidade", 1)
        total_quantidade += qtd
        cil_id = a.get("cilindro_id")
        elem_id = a.get("elemento_id")

        if cil_id and elem_id:
            minutos = _parse_tempo_chama(a.get("tempo_chama"))
            elem = elemento_dict.get(elem_id, {})
            consumo = float(elem.get("consumo_lpm", 0))
            gas = minutos / 60 * consumo
            gas_por_cilindro[cil_id] += gas
            total_gas_consumido += gas

        if cil_id:
            leituras_por_cilindro[cil_id] += qtd

        d = a.get("data")
        if d:
            leituras_por_mes[str(d)[:7]] += qtd

        if elem_id:
            elem_leituras[elem_id] += qtd

    # Gás Restante
    gas_restante = 0.0
    for c in cilindro:
        if c.get("status") == "ativo":
            litros = float(c.get("litros_equivalentes", 0))
            usado = gas_por_cilindro.get(c["id"], 0)
            restante = litros - usado
            if restante > 0:
                gas_restante += restante

    # Custo Médio por Leitura
    custo_total = sum(float(c.get("custo", 0)) for c in cilindro if c.get("custo"))
    custo_por_leitura = round(custo_total / total_quantidade, 2) if total_quantidade > 0 else 0

    # Leituras por Cilindro (doughnut)
    cilindro_leituras_labels = []
    cilindro_leituras_values = []
    for cid, qtd in sorted(leituras_por_cilindro.items(), key=lambda x: cilindro_dict.get(x[0], {}).get("codigo", "")):
        cilindro_leituras_labels.append(cilindro_dict.get(cid, {}).get("codigo", str(cid)))
        cilindro_leituras_values.append(qtd)

    # Curva de Pressão (últimas 10 por cilindro)
    pressao_series = defaultdict(list)
    for p in sorted(pressoes, key=lambda x: x.get("data", "")):
        cid = p.get("cilindro_id")
        if cid and len(pressao_series[cid]) < 10:
            pressao_series[cid].append({"data": str(p.get("data", "")), "pressao": float(p.get("pressao", 0))})

    pressao_chart = {}
    for cid, readings in pressao_series.items():
        cod = cilindro_dict.get(cid, {}).get("codigo", str(cid))
        pressao_chart[cod] = {"labels": [r["data"] for r in readings], "values": [r["pressao"] for r in readings]}
    pressao_chart = {
        cod: {"labels": v.get("labels", []), "values": v.get("values", [])}
        for cod, v in pressao_chart.items()
    }

    # Leituras por Mês (últimos 12)
    meses = sorted(leituras_por_mes.keys(), reverse=True)[:12]
    leituras_mes_labels = [_formatar_mes_ano(m) for m in reversed(meses)]
    leituras_mes_values = [leituras_por_mes[m] for m in meses]

    # Elementos por Amostra (distribuição)
    ae_count = defaultdict(int)
    for ae in ae_data:
        ae_count[ae.get("amostra_id")] += 1

    elem_por_amostra_dist = defaultdict(int)
    for count in ae_count.values():
        key = "4+" if count >= 4 else str(count)
        elem_por_amostra_dist[key] += 1

    dist_labels = ["1", "2", "3", "4+"]
    dist_values = [elem_por_amostra_dist.get(l, 0) for l in dist_labels]

    # Elementos mais analisados (top 5)
    elementos_mais_analisados = []
    for eid, qtd in sorted(elem_leituras.items(), key=lambda x: x[1], reverse=True)[:5]:
        elementos_mais_analisados.append({
            "nome": elemento_dict.get(eid, {}).get("nome", str(eid)),
            "quantidade": qtd
        })

    pressao_chart_labels = [formatar_data(l) for l in next(iter(pressao_chart.values()), {}).get("labels", [])]

    return dict(
        cilindros_ativos=cilindros_ativos,
        gas_restante=round(gas_restante, 1),
        total_quantidade=total_quantidade,
        amostras_total=len(amostras_data),
        custo_por_leitura=custo_por_leitura,
        total_gas_consumido=round(total_gas_consumido, 1),
        cilindro_leituras_labels=cilindro_leituras_labels,
        cilindro_leituras_values=cilindro_leituras_values,
        pressao_chart=pressao_chart,
        pressao_chart_labels=pressao_chart_labels,
        leituras_mes_labels=leituras_mes_labels,
        leituras_mes_values=leituras_mes_values,
        elementos_mais_analisados=elementos_mais_analisados,
        dist_labels=dist_labels,
        dist_values=dist_values,
        cilindro_dict={k: v.get("codigo") for k, v in cilindro_dict.items()},
        elemento_dict={k: v.get("nome") for k, v in elemento_dict.items()},
    )


@app.route("/dashboard")
@login_required
def dashboard():
    from utils.supabase_utils import get_supabase_client, get_admin_client
    from blueprints.helpers import get_user_id, is_dev, get_all_users

    current_user_id = get_user_id()
    selected_user_id = request.args.get("selected_user_id", "").strip()
    filter_user_id = current_user_id

    if is_dev() and selected_user_id and selected_user_id != "all":
        filter_user_id = selected_user_id

    if is_dev() and (not selected_user_id or selected_user_id == "all"):
        supabase = get_admin_client()
        cilindro = supabase.table("cilindro").select("id,codigo,status,litros_equivalentes,custo").execute().data or []
        elementos = supabase.table("elemento").select("id,nome,consumo_lpm").order("nome").execute().data or []
        leituras = supabase.table("leitura").select("id,cilindro_id,elemento_id,data,quantidade,tempo_chama").order("data", desc=True).execute().data or []
        try:
            pressoes = supabase.table("pressao").select("id,cilindro_id,data,pressao").order("data").execute().data or []
        except Exception:
            pressoes = []
        try:
            amostras_resp = supabase.table("amostra").select("id,numero_amostra,lote,created_at", count="exact").order("created_at", desc=True).execute()
            amostras_data = amostras_resp.data or []
        except Exception:
            amostras_data = []
    else:
        supabase = get_supabase_client()
        cilindro = supabase.table("cilindro").select("id,codigo,status,litros_equivalentes,custo").eq("user_id", filter_user_id).execute().data or []
        elementos = supabase.table("elemento").select("id,nome,consumo_lpm").eq("user_id", filter_user_id).order("nome").execute().data or []
        leituras = supabase.table("leitura").select("id,cilindro_id,elemento_id,data,quantidade,tempo_chama").eq("user_id", filter_user_id).order("data", desc=True).execute().data or []
        try:
            pressoes = supabase.table("pressao").select("id,cilindro_id,data,pressao").eq("user_id", filter_user_id).order("data").execute().data or []
        except Exception:
            pressoes = []
        try:
            amostras_resp = supabase.table("amostra").select("id,numero_amostra,lote,created_at", count="exact").eq("user_id", filter_user_id).order("created_at", desc=True).execute()
            amostras_data = amostras_resp.data or []
        except Exception:
            amostras_data = []

    user_amostra_ids = {a["id"] for a in amostras_data if a.get("id")}
    try:
        if user_amostra_ids:
            ae_data = supabase.table("amostra_elemento").select("id,amostra_id").in_("amostra_id", list(user_amostra_ids)).execute().data or []
        else:
            ae_data = []
    except Exception:
        ae_data = []

    from utils.cache_utils import get_cached_or_fetch, dashboard_cache_key

    lista_usuarios = get_all_users() if is_dev() else []

    kpi_cache_key = dashboard_cache_key("all") if is_dev() and (not selected_user_id or selected_user_id == "all") else dashboard_cache_key(filter_user_id)
    kpis = get_cached_or_fetch(kpi_cache_key, lambda: _compute_kpis(leituras, cilindro, elementos, amostras_data, ae_data, pressoes), timeout=30)
    leituras_recentes = leituras[:5]
    pressoes_recentes = pressoes[-5:] if pressoes else []
    amostras_recentes = amostras_data[:5]

    return render_template(
        "dashboard.html",
        cilindro=cilindro,
        elementos=elementos,
        leituras=leituras_recentes,
        pressoes=pressoes_recentes,
        amostras=amostras_recentes,
        paleta_cilindro=PALETA_CILINDRO,
        paleta_elemento=PALETA_ELEMENTO,
        lista_usuarios=lista_usuarios,
        selected_user_id=selected_user_id or "all",
        **kpis,
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
                logger.error(f"Erro ao atualizar perfil do usuário {user_id}: {str(e)}")
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
