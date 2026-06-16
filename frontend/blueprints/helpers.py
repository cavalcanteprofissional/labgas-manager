# Helper functions for the application
import logging
from flask import session

logger = logging.getLogger(__name__)


def get_user_id():
    """Retorna o ID do usuário atual"""
    return session.get("user_id")


def is_admin():
    """Verifica se o usuário atual é admin - usa cache da sessão"""
    cached = session.get('cached_user_info', {})
    return cached.get('is_admin', False)


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


def registrar_historico(tipo, acao, nome, user_id):
    """Registra uma ação no histórico"""
    from utils.supabase_utils import get_admin_client
    try:
        client = get_admin_client()
        client.table("historico_log").insert({
            "tipo": tipo,
            "acao": acao,
            "nome": nome,
            "user_id": user_id
        }).execute()
        logger.info(f"Histórico registrado: {tipo} | {acao} | {nome} | User: {user_id}")
    except Exception as e:
        logger.error(f"Erro ao registrar histórico: {str(e)}")


ABAS_DISPONIVEIS = ["cilindro", "pressao", "elemento", "leitura", "amostra", "historico"]
ABAS_DEFAULT = {aba: True for aba in ABAS_DISPONIVEIS}


def pode_acessar_aba(aba):
    """Verifica se o usuário atual pode acessar a aba especificada"""
    if is_admin():
        return True
    
    user_id = get_user_id()
    if not user_id:
        return False
    
    habilitar_abas = get_habilitar_abas(user_id)
    return habilitar_abas.get(aba, True)


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
