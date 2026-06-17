# Elemento blueprint - CRUD operations
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from utils.supabase_utils import get_supabase_client, get_admin_client
from utils.validators import safe_float
from utils.constants import ITEMS_PER_PAGE
from utils.erros_utils import formatar_erro_supabase
from blueprints.helpers import get_user_id, is_admin, registrar_historico, pode_acessar_aba

elemento_bp = Blueprint('elemento', __name__)


@elemento_bp.route("/elementos", methods=["GET", "POST"])
def list():
    if not pode_acessar_aba("elemento"):
        flash("Você não tem permissão para acessar esta aba.", "warning")
        from flask import current_app
        return redirect(current_app.config.get("LOGIN_VIEW", "/dashboard"))
    
    user_id = get_user_id()
    admin = is_admin()
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", ITEMS_PER_PAGE, type=int)
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "create":
            nome = request.form.get("nome").strip().title()
            consumo_lpm = request.form.get("consumo_lpm")
            
            if not nome or not consumo_lpm:
                flash("Nome e consumo são obrigatórios", "danger")
                return redirect(url_for("elemento.list"))
            
            existing = get_admin_client().table("elemento").select("id").eq("nome", nome).execute()
            if existing.data:
                if admin:
                    flash(f"Elemento '{nome}' já existe no sistema", "danger")
                else:
                    flash("Elemento com este nome já existe para este usuário", "danger")
                return redirect(url_for("elemento.list"))
            
            data = {
                "nome": nome,
                "consumo_lpm": safe_float(consumo_lpm, 0),
                "user_id": user_id
            }
            
            try:
                from blueprints.helpers import get_authenticated_client
                if admin:
                    client = get_admin_client()
                else:
                    client = get_authenticated_client()
                
                client.table("elemento").insert(data).execute()
                registrar_historico("elemento", "criado", nome, user_id)
                flash("Elemento criado com sucesso!", "success")
            except Exception as e:
                error_str = str(e)
                flash(formatar_erro_supabase(error_str, "criar elemento"), "danger")
            
        elif action == "update":
            elemento_id = request.form.get("elemento_id")
            nome = request.form.get("nome").strip().title()
            consumo_lpm = request.form.get("consumo_lpm")
            
            if not elemento_id or not nome or not consumo_lpm:
                flash("ID do elemento, nome e consumo são obrigatórios", "danger")
                return redirect(url_for("elemento.list"))
            
            if not admin:
                existing = get_admin_client().table("elemento").select("id").eq("user_id", user_id).eq("nome", nome).neq("id", elemento_id).execute()
                if existing.data:
                    flash("Elemento com este nome já existe para este usuário", "danger")
                    return redirect(url_for("elemento.list"))
            
            data = {
                "nome": nome,
                "consumo_lpm": safe_float(consumo_lpm, 0)
            }
            
            if not admin:
                get_supabase_client().table("elemento").update(data).eq("id", elemento_id).eq("user_id", user_id).execute()
            else:
                get_admin_client().table("elemento").update(data).eq("id", elemento_id).execute()
            
            registrar_historico("elemento", "atualizado", nome, user_id)
            flash("Elemento atualizado com sucesso!", "success")
            
        elif action == "delete":
            elemento_id = request.form.get("elemento_id")
            
            if not elemento_id:
                flash("ID do elemento é obrigatório", "danger")
                return redirect(url_for("elemento.list"))
            
            elemento_info = get_supabase_client().table("elemento").select("nome,user_id").eq("id", elemento_id).execute().data
            if not elemento_info:
                flash("Elemento não encontrado", "danger")
                return redirect(url_for("elemento.list"))
            
            if elemento_info[0].get("user_id") != user_id:
                flash("Você não tem permissão para excluir este elemento.", "danger")
                return redirect(url_for("elemento.list"))
            
            elemento_nome = elemento_info[0].get("nome")
            
            leitura_count = get_supabase_client().table("leitura").select("id", count="exact").eq("elemento_id", elemento_id).execute()
            if leitura_count.count and leitura_count.count > 0:
                flash("Não é possível excluir este elemento pois existem leituras vinculadas a ele. Exclua primeiro as leituras.", "warning")
                return redirect(url_for("elemento.list"))
            
            try:
                get_admin_client().table("elemento").delete().eq("id", elemento_id).execute()
                
                registrar_historico("elemento", "excluido", elemento_nome, user_id)
                flash("Elemento excluído com sucesso!", "success")
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "excluir elemento"), "danger")
            
            return redirect(url_for("elemento.list"))
        
        elif action == "delete_multiple":
            raw_ids = request.form.getlist("elemento_ids")
            if not raw_ids:
                flash("Nenhum elemento selecionado", "danger")
                return redirect(url_for("elemento.list"))

            ids = []
            for v in raw_ids:
                try:
                    ids.append(int(v))
                except (ValueError, TypeError):
                    pass
            if not ids:
                flash("IDs inválidos", "danger")
                return redirect(url_for("elemento.list"))

            try:
                supabase = get_supabase_client()
                elementos = supabase.table("elemento").select("id,nome,user_id").in_("id", ids).execute().data or []

                tem_leitura = set()
                leituras = supabase.table("leitura").select("elemento_id").in_("elemento_id", ids).execute().data or []
                for lr in leituras:
                    tem_leitura.add(lr["elemento_id"])

                permitidos = []
                skipped = []
                not_owned = []
                for e in elementos:
                    if e.get("user_id") != user_id:
                        not_owned.append(e.get("nome", str(e["id"])))
                    elif e["id"] in tem_leitura:
                        skipped.append(e.get("nome", str(e["id"])))
                    else:
                        permitidos.append(e)

                if permitidos:
                    get_admin_client().table("elemento").delete().in_("id", [e["id"] for e in permitidos]).execute()
                    for e in permitidos:
                        registrar_historico("elemento", "excluido", e.get("nome", str(e["id"])), user_id)

                if permitidos:
                    flash(f"{len(permitidos)} elemento(s) excluído(s) com sucesso!", "success")
                if skipped:
                    flash(f"Alguns elementos não puderam ser excluídos (leituras vinculadas): {', '.join(skipped)}", "warning")
                if not_owned:
                    flash(f"Alguns elementos não foram excluídos (não pertencem a você): {', '.join(not_owned)}", "warning")
                if not permitidos and not skipped and not not_owned:
                    flash("Nenhum elemento foi excluído", "warning")
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "excluir elementos"), "danger")

            return redirect(url_for("elemento.list"))
    
    response = get_supabase_client().table("elemento").select("*").order("nome", desc=False).execute()
    elementos = response.data or []
    
    total = len(elementos)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = elementos[start:end]
    
    elementos = paginated_data
    
    pages = (total + per_page - 1) // per_page
    end = min(page * per_page, total)
    max_pages = min(pages, 10)
    
    return render_template("elemento.html", elementos=elementos, page=page, per_page=per_page, total=total, pages=pages, end=end, max_pages=max_pages)
