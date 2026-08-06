# Supabase utility functions
import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")


def get_supabase_client():
    """Retorna cliente Supabase usando Flask g para thread safety.

    Se o usuário da sessão possuir token JWT (supabase_token), o cliente é
    autenticado com ele — exigência do RLS (as políticas de SELECT passam a
    filtrar por auth.uid() = user_id). Sem token, retorna cliente anon.
    """
    from flask import has_request_context, g, session
    
    if not has_request_context():
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    
    if not hasattr(g, '_supabase_client'):
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        token = session.get("supabase_token")
        if token:
            try:
                client.auth.set_session(token, "")
            except Exception:
                pass
        g._supabase_client = client
    return g._supabase_client


def get_admin_client():
    """Retorna cliente Supabase com service_role (bypass RLS) usando Flask g."""
    from flask import has_request_context, g, current_app
    
    if not has_request_context():
        return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    if not hasattr(g, '_admin_client'):
        g._admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return g._admin_client


def buscar_perfis_usuarios(user_ids):
    """Busca perfis de múltiplos usuários em uma única consulta (otimização N+1)."""
    from flask import current_app
    
    supabase = get_admin_client()
    if not user_ids:
        return {}
    try:
        perfis = supabase.table("perfil").select("id,nome").in_("id", list(user_ids)).execute().data
        return {p["id"]: (p.get("nome") or str(p["id"])) for p in (perfis or [])}
    except Exception:
        return {uid: str(uid) for uid in user_ids}


# Aliases for backwards compatibility
supabase_client = get_supabase_client
