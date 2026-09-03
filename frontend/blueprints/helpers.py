# Helper functions for the application
import logging
from flask import session

logger = logging.getLogger(__name__)

ROLES_HIERARCHY = {"dev": 3, "admin": 2, "usuario": 1}


def get_user_id():
    """Retorna o ID do usuário atual"""
    return session.get("user_id")


def role_at_least(min_role):
    """Verifica se o usuário atual tem role >= min_role na hierarquia"""
    user_role = get_user_role()
    min_level = ROLES_HIERARCHY.get(min_role, 0)
    user_level = ROLES_HIERARCHY.get(user_role, 0)
    return user_level >= min_level


def is_admin():
    """Verifica se o usuário atual é admin ou dev - usa cache da sessão"""
    cached = session.get('cached_user_info', {})
    return cached.get('is_admin', False)


def is_dev():
    """Verifica se o usuário atual é dev (supremo) - usa cache da sessão"""
    return get_user_role() == 'dev'


def is_user_active(user_id):
    """Verifica se o usuário está ativo"""
    try:
        from utils.supabase_utils import get_supabase_client
        supabase = get_authenticated_client()
        response = supabase.table("perfil").select("ativo").eq("id", user_id).execute()
        if response.data:
            return response.data[0].get("ativo", True)
    except Exception as e:
        logger.error(f"is_user_active: erro: {str(e)}")
    return True


def get_user_role():
    """Retorna o role do usuário atual - usa cache da sessão"""
    cached = session.get('cached_user_info', {})
    return cached.get('user_role', 'usuario')


def get_user_name():
    """Retorna o nome do usuário atual - usa cache da sessão"""
    cached = session.get('cached_user_info', {})
    return cached.get('user_name', '')


def get_authenticated_client():
    """Retorna cliente Supabase autenticado com token JWT do usuário"""
    from utils.supabase_utils import get_supabase_client
    token = session.get("supabase_token")
    if token:
        client = get_supabase_client()
        client.auth.set_session(token, "")
        return client
    return get_supabase_client()


def get_admin_client():
    """Retorna cliente Supabase com service_role (bypass RLS)"""
    from utils.supabase_utils import get_admin_client as supabase_admin
    return supabase_admin()


def registrar_historico(tipo, acao, label, user_id, ref_id=None, detalhe=None):
    """Registra uma ação no histórico de auditoria.

    tipo: tabela de origem (cilindro, pressao, elemento, leitura, amostra, perfil)
    acao: criado | atualizado | excluido
    label: texto legível (antiga coluna nome)
    ref_id: id do registro de origem na tabela de `tipo` (None p/ perfil/auth/lote)
    detalhe: payload estruturado JSONB — obrigatório para 'atualizado'
    """
    from utils.supabase_utils import get_admin_client

    try:
        client = get_admin_client()
        registro = {
            "tipo": tipo,
            "acao": acao,
            "label": label,
            "user_id": user_id,
        }
        if ref_id is not None:
            registro["ref_id"] = ref_id
        
        if acao == "atualizado" and (detalhe is None or (isinstance(detalhe, dict) and len(detalhe) == 0)):
            detalhe = {"_incomplete": True}
        
        if detalhe is not None:
            registro["detalhe"] = detalhe
        
        client.table("historico_auditoria").insert(registro).execute()
        logger.info(f"Histórico registrado: {tipo} | {acao} | {label} | ref={ref_id} | User: {user_id}")
    except Exception as e:
        logger.error(f"Erro ao registrar histórico: {str(e)}")


ABAS_DISPONIVEIS = ["cilindro", "pressao", "elemento", "leitura", "amostra", "historico"]
ABAS_DEFAULT = {aba: True for aba in ABAS_DISPONIVEIS}


def pode_acessar_aba(aba):
    """Verifica se o usuário atual pode acessar a aba especificada.
    
    Admin e dev sempre têm acesso a todas as abas (override).
    Usuários comuns seguem o habilitar_abas do perfil.
    """
    if is_admin():
        return True
    
    user_id = get_user_id()
    if not user_id:
        return False
    
    habilitar_abas = get_habilitar_abas(user_id)
    return habilitar_abas.get(aba, True)


def consultar_paginado(supabase, tabela, cols, page, per_page, dev, user_id, montar, ordem_coluna=None, desc=True):
    """Consulta paginada segura: conta primeiro e limita a página ao intervalo existente.

    Evita o erro 416 (\"JSON could not be generated\") do PostgREST quando
    count=exact é combinado com range além do fim do resultado.
    `montar` é um callable que aplica os filtros adicionais ao builder.
    """
    def construir():
        q = supabase.table(tabela).select(cols, count="exact")
        if not dev:
            q = q.eq("user_id", user_id)
        montar(q)
        return q

    total = (construir().execute().count) or 0
    pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, pages))
    offset = (page - 1) * per_page

    q = construir()
    if ordem_coluna:
        q = q.order(ordem_coluna, desc=desc)
    response = q.range(offset, offset + per_page - 1).execute()
    return (response.data or []), total, page, pages


def get_habilitar_abas(user_id=None):
    """Retorna o dicionário de abas habilitadas para o usuário - usa cache da sessão"""
    if user_id is None:
        user_id = get_user_id()
    
    if not user_id:
        return ABAS_DEFAULT.copy()
    
    cached = session.get('cached_user_info', {})
    
    if cached.get('is_admin'):
        return {aba: True for aba in ABAS_DISPONIVEIS}
    
    habilitar_abas = cached.get('habilitar_abas')
    if habilitar_abas:
        return {aba: habilitar_abas.get(aba, True) for aba in ABAS_DISPONIVEIS}
    
    return ABAS_DEFAULT.copy()


def get_all_users():
    """Retorna lista de todos os usuários (id, nome, email) — cache via SimpleCache"""
    from utils.cache_utils import get_cached_or_fetch
    from utils.supabase_utils import get_admin_client

    def _fetch():
        try:
            client = get_admin_client()
            resp = client.table("perfil").select("id,nome,email").execute()
            return resp.data or []
        except Exception as e:
            logger.error(f"get_all_users: erro: {str(e)}")
            return []

    return get_cached_or_fetch("get_all_users", _fetch, timeout=300)


def verificar_alerta_pressao():
    """MELHORIA-02: Verifica se cilindro ativo está sem medição de pressão há 7+ dias.

    Retorna dict com alerta e detalhes, ou None se não houver alerta.
    """
    from datetime import datetime, timezone
    from utils.supabase_utils import get_supabase_client

    try:
        supabase = get_supabase_client()
        cil_ativo = supabase.table("cilindro").select("id,numero,status").eq("status", "ativo").execute().data or []
        if not cil_ativo:
            return None

        alertas = []
        for cil in cil_ativo:
            cil_id = cil["id"]
            ultima_pressao = supabase.table("pressao").select("data,pressao").eq("cilindro_id", cil_id).order("data", desc=True).limit(1).execute().data

            if ultima_pressao:
                try:
                    ultima_data = datetime.strptime(str(ultima_pressao[0]["data"]), "%Y-%m-%d")
                    dias = (datetime.now(timezone.utc).date() - ultima_data.date()).days
                except (ValueError, TypeError):
                    dias = None
            else:
                dias = None

            if dias is None or dias > 7:
                alertas.append({
                    "cilindro": cil.get("numero"),
                    "dias": dias,
                    "pressao": ultima_pressao[0].get("pressao") if ultima_pressao else None,
                    "tem_pressao": bool(ultima_pressao)
                })

        if alertas:
            return {"alerta": True, "alertas": alertas}
        return {"alerta": False}
    except Exception as e:
        logger.error(f"verificar_alerta_pressao: erro: {str(e)}")
        return None
