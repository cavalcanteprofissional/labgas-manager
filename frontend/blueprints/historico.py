# Historico blueprint - Activity history
from flask import Blueprint, render_template, flash, redirect, request, url_for

from utils.supabase_utils import get_supabase_client
from utils.supabase_utils import buscar_perfis_usuarios
from blueprints.helpers import get_user_id, is_admin, pode_acessar_aba

historico_bp = Blueprint('historico', __name__)


@historico_bp.route("/historico")
def list():
    if not pode_acessar_aba("historico"):
        flash("Você não tem permissão para acessar esta aba.", "warning")
        return redirect(url_for("dashboard"))
    
    user_id = get_user_id()
    admin = is_admin()
    
    page = int(request.args.get("page", 1))
    per_page = 20
    offset = (page - 1) * per_page
    
    response = get_supabase_client().table("historico_log").select("*", count="exact").order("created_at", desc=True).range(offset, offset + per_page - 1).execute()
    historico_log = response.data or []
    total = response.count or 0
    
    all_user_ids = {h.get("user_id") for h in historico_log if h.get("user_id")}
    user_map = buscar_perfis_usuarios(all_user_ids)
    if not user_map:
        user_map = {uid: str(uid) for uid in all_user_ids}
    
    history = []
    
    for h in historico_log:
        history.append({
            "tipo": h.get("tipo"),
            "acao": h.get("acao"),
            "nome": h.get("nome"),
            "data": h.get("created_at"),
            "user_id": h.get("user_id"),
            "usuario_nome": user_map.get(h.get("user_id"), '-')
        })
    
    return render_template("historico.html", history=history, page=page, per_page=per_page, total=total)
