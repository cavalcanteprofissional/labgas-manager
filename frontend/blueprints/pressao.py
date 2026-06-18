# Pressao blueprint - CRUD operations
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash

from utils.supabase_utils import get_supabase_client, get_admin_client
from utils.validators import safe_float
from utils.constants import ITEMS_PER_PAGE
from utils.erros_utils import formatar_erro_supabase
from blueprints.helpers import get_user_id, is_dev, registrar_historico, pode_acessar_aba, get_authenticated_client
from utils.cache_utils import invalidate_user_caches

pressao_bp = Blueprint('pressao', __name__)


@pressao_bp.route("/pressoes", methods=["GET", "POST"])
def pressao_list():
    if not pode_acessar_aba("pressao"):
        flash("Você não tem permissão para acessar esta aba.", "warning")
        return redirect(url_for("dashboard"))
    
    user_id = get_user_id()
    dev = is_dev()
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", ITEMS_PER_PAGE, type=int)
    
    cilindro_list_response = get_authenticated_client().table("cilindro").select("id,codigo").eq("user_id", user_id).order("codigo").execute()
    cilindro_list = cilindro_list_response.data or []
    cilindro_dict_lookup = {c["id"]: c["codigo"] for c in cilindro_list}
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "create":
            cilindro_id = request.form.get("cilindro_id", "").strip()
            pressao = request.form.get("pressao", "").strip()
            temperatura = request.form.get("temperatura", "").strip()
            data = request.form.get("data", "").strip()
            hora = request.form.get("hora", "").strip()
            
            if not cilindro_id or not pressao or not data or not hora:
                flash("Cilindro, pressão, temperatura, data e hora são obrigatórios", "danger")
                return redirect(url_for("pressao.pressao_list"))
            
            try:
                pressao_val = safe_float(pressao, 1.0)
                if pressao_val < 0 or pressao_val > 300:
                    flash("Pressão deve estar entre 0 e 300 bar", "danger")
                    return redirect(url_for("pressao.pressao_list"))
            except ValueError as e:
                flash("Pressão inválida.", "danger")
                return redirect(url_for("pressao.pressao_list"))
            
            temp_val = None
            if temperatura:
                try:
                    temp_val = safe_float(temperatura, 25.0)
                    if temp_val < -50 or temp_val > 100:
                        flash("Temperatura deve estar entre -50°C e 100°C", "danger")
                        return redirect(url_for("pressao.pressao_list"))
                except ValueError as e:
                    flash("Temperatura inválida.", "danger")
                    return redirect(url_for("pressao.pressao_list"))
            
            try:
                datetime.strptime(data, "%Y-%m-%d")
            except ValueError:
                flash("Data inválida", "danger")
                return redirect(url_for("pressao.pressao_list"))
            
            try:
                datetime.strptime(hora, "%H:%M")
            except ValueError:
                flash("Hora inválida", "danger")
                return redirect(url_for("pressao.pressao_list"))
            
            cilindro_id_int = int(cilindro_id)
            if not dev:
                if cilindro_id_int not in cilindro_dict_lookup:
                    flash("Cilindro não encontrado", "danger")
                    return redirect(url_for("pressao.pressao_list"))
            cilindro_codigo = cilindro_dict_lookup.get(cilindro_id_int, str(cilindro_id_int))
            
            try:
                data_insert = {
                    "cilindro_id": cilindro_id_int,
                    "pressao": pressao_val,
                    "temperatura": temp_val,
                    "data": data,
                    "hora": hora,
                    "user_id": user_id
                }
                
                if dev:
                    client = get_admin_client()
                else:
                    client = get_authenticated_client()
                
                client.table("pressao").insert(data_insert).execute()
                temp_str = f", {temp_val}°C" if temp_val is not None else ""
                registrar_historico("pressao", "criado", f"{cilindro_codigo} - {pressao_val} bar{temp_str}", user_id)
                invalidate_user_caches(user_id)
                flash("Pressão registrada com sucesso!", "success")
            except Exception as e:
                error_str = str(e)
                flash(formatar_erro_supabase(error_str, "registrar pressão"), "danger")
            
        elif action == "update":
            pressao_id = request.form.get("pressao_id", "").strip()
            cilindro_id = request.form.get("cilindro_id", "").strip()
            pressao = request.form.get("pressao", "").strip()
            temperatura = request.form.get("temperatura", "").strip()
            data = request.form.get("data", "").strip()
            hora = request.form.get("hora", "").strip()
            
            if not pressao_id or not cilindro_id or not pressao or not data or not hora:
                flash("ID, cilindro, pressão, temperatura, data e hora são obrigatórios", "danger")
                return redirect(url_for("pressao.pressao_list"))
            
            try:
                pressao_val = safe_float(pressao, 1.0)
                if pressao_val < 0 or pressao_val > 300:
                    flash("Pressão deve estar entre 0 e 300 bar", "danger")
                    return redirect(url_for("pressao.pressao_list"))
            except ValueError as e:
                flash("Pressão inválida.", "danger")
                return redirect(url_for("pressao.pressao_list"))
            
            temp_val = None
            if temperatura:
                try:
                    temp_val = safe_float(temperatura, 25.0)
                    if temp_val < -50 or temp_val > 100:
                        flash("Temperatura deve estar entre -50°C e 100°C", "danger")
                        return redirect(url_for("pressao.pressao_list"))
                except ValueError as e:
                    flash("Temperatura inválida.", "danger")
                    return redirect(url_for("pressao.pressao_list"))
            
            cilindro_id_int = int(cilindro_id)
            if not dev:
                if cilindro_id_int not in cilindro_dict_lookup:
                    flash("Cilindro não encontrado", "danger")
                    return redirect(url_for("pressao.pressao_list"))
            cilindro_codigo = cilindro_dict_lookup.get(cilindro_id_int, str(cilindro_id_int))
            
            try:
                data_update = {
                    "cilindro_id": cilindro_id_int,
                    "pressao": pressao_val,
                    "temperatura": temp_val,
                    "data": data,
                    "hora": hora
                }
                
                if not dev:
                    get_supabase_client().table("pressao").update(data_update).eq("id", pressao_id).eq("user_id", user_id).execute()
                else:
                    get_admin_client().table("pressao").update(data_update).eq("id", pressao_id).execute()
                
                temp_str = f", {temp_val}°C" if temp_val is not None else ""
                registrar_historico("pressao", "atualizado", f"{cilindro_codigo} - {pressao_val} bar{temp_str}", user_id)
                invalidate_user_caches(user_id)
                flash("Pressão atualizada com sucesso!", "success")
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "atualizar pressão"), "danger")
            
        elif action == "delete":
            pressao_id = request.form.get("pressao_id", "").strip()
            
            if not pressao_id:
                flash("ID da pressão é obrigatório", "danger")
                return redirect(url_for("pressao.pressao_list"))
            
            try:
                pressao_info = get_supabase_client().table("pressao").select("cilindro_id,pressao,user_id").eq("id", pressao_id).execute().data
                if not pressao_info:
                    flash("Registro de pressão não encontrado", "danger")
                    return redirect(url_for("pressao.pressao_list"))
                
                if not dev and pressao_info[0].get("user_id") != user_id:
                    flash("Você não tem permissão para excluir este registro.", "danger")
                    return redirect(url_for("pressao.pressao_list"))
                
                cilindro_id = pressao_info[0].get("cilindro_id")
                pressao_val = pressao_info[0].get("pressao")
                temp_val = pressao_info[0].get("temperatura")
                
                cilindro_info = get_supabase_client().table("cilindro").select("codigo").eq("id", cilindro_id).execute().data
                cilindro_codigo = cilindro_info[0].get("codigo") if cilindro_info else str(cilindro_id)
                
                (get_admin_client() if dev else get_authenticated_client()).table("pressao").delete().eq("id", pressao_id).execute()
                
                temp_str = f", {temp_val}°C" if temp_val is not None else ""
                registrar_historico("pressao", "excluido", f"{cilindro_codigo} - {pressao_val} bar{temp_str}", user_id)
                invalidate_user_caches(user_id)
                flash("Registro de pressão excluído com sucesso!", "success")
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "excluir pressão"), "danger")
            
            return redirect(url_for("pressao.pressao_list"))
        
        elif action == "delete_multiple":
            raw_ids = request.form.getlist("pressao_ids")
            if not raw_ids:
                flash("Nenhum registro selecionado", "danger")
                return redirect(url_for("pressao.pressao_list"))

            ids = []
            for v in raw_ids:
                try:
                    ids.append(int(v))
                except (ValueError, TypeError):
                    pass
            if not ids:
                flash("IDs inválidos", "danger")
                return redirect(url_for("pressao.pressao_list"))

            try:
                supabase = get_supabase_client()
                rows = supabase.table("pressao").select("id,cilindro_id,pressao,temperatura,user_id").in_("id", ids).execute().data or []

                permitted = [r for r in rows if dev or r.get("user_id") == user_id]
                not_owned_count = len(ids) - len(permitted)

                if not permitted:
                    flash("Nenhum registro foi excluído", "warning")
                    return redirect(url_for("pressao.pressao_list"))

                cil_ids = sorted(set(r["cilindro_id"] for r in permitted))
                cilindros = supabase.table("cilindro").select("id,codigo").in_("id", cil_ids).execute().data or []
                cil_map = {c["id"]: c.get("codigo", str(c["id"])) for c in cilindros}

                (get_admin_client() if dev else get_authenticated_client()).table("pressao").delete().in_("id", [r["id"] for r in permitted]).execute()

                for r in permitted:
                    cod = cil_map.get(r["cilindro_id"], str(r["cilindro_id"]))
                    temp_str = f", {r['temperatura']}°C" if r.get("temperatura") is not None else ""
                    registrar_historico("pressao", "excluido", f"{cod} - {r['pressao']} bar{temp_str}", user_id)
                invalidate_user_caches(user_id)

                flash(f"{len(permitted)} registro(s) excluído(s) com sucesso!", "success")
                if not_owned_count:
                    flash(f"{not_owned_count} registro(s) não foram excluídos (não pertencem a você)", "warning")
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "excluir registros"), "danger")

            return redirect(url_for("pressao.pressao_list"))
    
    response = get_supabase_client().table("pressao").select("*").order("created_at", desc=True).execute()
    pressoes = response.data or []
    
    for p in pressoes:
        p["cilindro_codigo"] = cilindro_dict_lookup.get(p.get("cilindro_id"), "")
    
    total = len(pressoes)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = pressoes[start:end]
    
    pressoes = paginated_data
    
    pages = (total + per_page - 1) // per_page if total > 0 else 1
    end_page = min(page * per_page, total) if total > 0 else 0
    max_pages = min(pages, 10)
        
    return render_template(
        "pressao.html", 
        pressoes=pressoes, 
        cilindro_list=cilindro_list,
        page=page,
        per_page=per_page,
        total=total,
        pages=pages,
        end=end_page,
        max_pages=max_pages
    )