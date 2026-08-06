# Historico blueprint - Activity history
from datetime import datetime
from flask import Blueprint, render_template, flash, redirect, request, url_for

from utils.supabase_utils import get_supabase_client, get_admin_client
from utils.supabase_utils import buscar_perfis_usuarios
from blueprints.helpers import get_user_id, is_dev, is_admin, pode_acessar_aba

historico_bp = Blueprint('historico', __name__)

TIPOS_VALIDOS = {"cilindro", "pressao", "elemento", "leitura", "amostra", "perfil"}
ACOES_VALIDAS = {"criado", "atualizado", "excluido"}
PER_PAGE_VALIDOS = {10, 20, 50, 100}


@historico_bp.route("/historico")
def list():
    if not pode_acessar_aba("historico"):
        flash("Você não tem permissão para acessar esta aba.", "warning")
        return redirect(url_for("dashboard"))
    
    user_id = get_user_id()
    admin = is_admin()
    dev = is_dev()
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    if per_page not in PER_PAGE_VALIDOS:
        per_page = 20

    q = request.args.get("q", "").strip()
    tipo_filtro = request.args.get("tipo", "").strip()
    acao_filtro = request.args.get("acao", "").strip()
    data_inicio = request.args.get("data_inicio", "").strip()
    data_fim = request.args.get("data_fim", "").strip()

    if tipo_filtro not in TIPOS_VALIDOS:
        tipo_filtro = ""
    if acao_filtro not in ACOES_VALIDAS:
        acao_filtro = ""

    user_ids_por_nome = []
    if q and dev:
        q_safe = q.replace(",", "").replace("(", "").replace(")", "")
        if q_safe:
            resp = get_admin_client().table("perfil").select("id").ilike("nome", f"%{q_safe}%").execute()
            user_ids_por_nome = [r["id"] for r in (resp.data or [])]

    def montar(query):
        if q:
            clauses = [f"label.ilike.%{q.replace(',', '').replace('(', '').replace(')', '')}%"]
            if user_ids_por_nome:
                clauses.append(f"user_id.in.({','.join(str(i) for i in user_ids_por_nome)})")
            if len(clauses) > 1:
                query = query.or_(",".join(clauses))
            else:
                query = query.ilike("label", f"%{q}%")

        if tipo_filtro:
            query = query.eq("tipo", tipo_filtro)

        if acao_filtro:
            query = query.eq("acao", acao_filtro)

        if data_inicio:
            try:
                datetime.strptime(data_inicio, "%Y-%m-%d")
                query = query.gte("created_at", data_inicio)
            except ValueError:
                pass

        if data_fim:
            try:
                datetime.strptime(data_fim, "%Y-%m-%d")
                query = query.lte("created_at", data_fim)
            except ValueError:
                pass

        return query

    def construir():
        return montar(get_supabase_client().table("historico_auditoria").select("*", count="exact"))

    total = (construir().execute().count) or 0
    pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, pages))
    offset = (page - 1) * per_page
    
    response = construir().order("created_at", desc=True).range(offset, offset + per_page - 1).execute()
    historico_aud = response.data or []
    
    all_user_ids = {h.get("user_id") for h in historico_aud if h.get("user_id")}
    user_map = buscar_perfis_usuarios(all_user_ids)
    if not user_map:
        user_map = {uid: str(uid) for uid in all_user_ids}
    
    history = []
    
    for h in historico_aud:
        history.append({
            "tipo": h.get("tipo"),
            "acao": h.get("acao"),
            "label": h.get("label"),
            "ref_id": h.get("ref_id"),
            "detalhe": h.get("detalhe"),
            "data": h.get("created_at"),
            "user_id": h.get("user_id"),
            "usuario_nome": user_map.get(h.get("user_id"), '-')
        })
    
    end = min(page * per_page, total)
    max_pages = min(pages, 10)

    return render_template(
        "historico.html",
        history=history,
        page=page,
        per_page=per_page,
        total=total,
        pages=pages,
        end=end,
        max_pages=max_pages,
        is_admin=admin,
    )
