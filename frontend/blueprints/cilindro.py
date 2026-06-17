# Cilindro blueprint - CRUD operations
import re
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from utils.supabase_utils import get_supabase_client, get_admin_client
from utils.validators import safe_float
from utils.constants import ITEMS_PER_PAGE, LITROS_EQUIVALENTES_KG, GAS_KG_DEFAULT, CUSTO_DEFAULT, CILINDRO_STATUS
from utils.erros_utils import formatar_erro_supabase
from blueprints.helpers import get_user_id, is_admin, registrar_historico, pode_acessar_aba

cilindro_bp = Blueprint('cilindro', __name__)


@cilindro_bp.route("/cilindros", methods=["GET", "POST"])
def list():
    if not pode_acessar_aba("cilindro"):
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
            codigo = request.form.get("codigo", "").strip()
            data_compra = request.form.get("data_compra", "").strip()
            data_inicio_consumo = request.form.get("data_inicio_consumo", "").strip()
            data_fim = request.form.get("data_fim", "").strip()
            gas_kg = request.form.get("gas_kg", "")
            custo = request.form.get("custo", "")
            status = request.form.get("status", "ativo")
            
            if status not in CILINDRO_STATUS:
                status = "ativo"
            
            if not codigo or not data_compra:
                flash("Código e data de compra são obrigatórios", "danger")
                return redirect(url_for("cilindro.list"))
            
            if not re.match(r'^CIL-\d{3}$', codigo):
                flash("Código deve seguir o formato CIL-XXX (ex: CIL-001, CIL-002)", "danger")
                return redirect(url_for("cilindro.list"))
            
            try:
                datetime.strptime(data_compra, "%Y-%m-%d")
            except ValueError:
                flash("Data de compra inválida", "danger")
                return redirect(url_for("cilindro.list"))
            
            try:
                gas_kg_val = safe_float(gas_kg, GAS_KG_DEFAULT)
                custo_val = safe_float(custo, CUSTO_DEFAULT)
                if gas_kg_val < 0 or custo_val < 0:
                    raise ValueError("Valores não podem ser negativos")
            except ValueError as e:
                flash(f"Valores inválidos.", "danger")
                return redirect(url_for("cilindro.list"))
            
            if not admin:
                try:
                    existing = get_admin_client().table("cilindro").select("id").eq("user_id", user_id).eq("codigo", codigo).execute()
                    if existing.data:
                        flash("Código já existe para este usuário", "danger")
                        return redirect(url_for("cilindro.list"))
                except Exception as e:
                    flash(formatar_erro_supabase(str(e), "verificar código"), "danger")
                    return redirect(url_for("cilindro.list"))
            
            try:
                data = {
                    "codigo": codigo,
                    "data_compra": data_compra,
                    "data_inicio_consumo": data_inicio_consumo,
                    "data_fim": data_fim or None,
                    "gas_kg": gas_kg_val,
                    "litros_equivalentes": gas_kg_val * LITROS_EQUIVALENTES_KG,
                    "custo": custo_val,
                    "status": status,
                    "user_id": user_id
                }
                
                from blueprints.helpers import get_authenticated_client
                if admin:
                    client = get_admin_client()
                else:
                    client = get_authenticated_client()
                
                client.table("cilindro").insert(data).execute()
                registrar_historico("cilindro", "criado", codigo, user_id)
                flash("Cilindro criado com sucesso!", "success")
            except Exception as e:
                error_str = str(e)
                flash(formatar_erro_supabase(error_str, "criar cilindro"), "danger")
            
        elif action == "update":
            cilindro_id = request.form.get("cilindro_id", "").strip()
            codigo = request.form.get("codigo", "").strip()
            data_compra = request.form.get("data_compra", "").strip()
            data_inicio_consumo = request.form.get("data_inicio_consumo", "").strip()
            data_fim = request.form.get("data_fim", "").strip()
            gas_kg = request.form.get("gas_kg", "")
            custo = request.form.get("custo", "")
            status = request.form.get("status", "ativo")
            
            if status not in CILINDRO_STATUS:
                status = "ativo"
            
            if not cilindro_id or not codigo or not data_compra:
                flash("ID do cilindro, código e data de compra são obrigatórios", "danger")
                return redirect(url_for("cilindro.list"))
            
            if not re.match(r'^CIL-\d{3}$', codigo):
                flash("Código deve seguir o formato CIL-XXX (ex: CIL-001, CIL-002)", "danger")
                return redirect(url_for("cilindro.list"))
            
            try:
                gas_kg_val = safe_float(gas_kg, GAS_KG_DEFAULT)
                custo_val = safe_float(custo, CUSTO_DEFAULT)
                if gas_kg_val < 0 or custo_val < 0:
                    raise ValueError("Valores não podem ser negativos")
            except ValueError as e:
                flash(f"Valores inválidos.", "danger")
                return redirect(url_for("cilindro.list"))
            
            try:
                if not admin:
                    existing = get_admin_client().table("cilindro").select("id").eq("user_id", user_id).eq("codigo", codigo).neq("id", cilindro_id).execute()
                    if existing.data:
                        flash("Código já existe para este usuário", "danger")
                        return redirect(url_for("cilindro.list"))
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "verificar código"), "danger")
                return redirect(url_for("cilindro.list"))
            
            try:
                data = {
                    "codigo": codigo,
                    "data_compra": data_compra,
                    "data_inicio_consumo": data_inicio_consumo or None,
                    "data_fim": data_fim or None,
                    "gas_kg": gas_kg_val,
                    "litros_equivalentes": gas_kg_val * LITROS_EQUIVALENTES_KG,
                    "custo": custo_val,
                    "status": status
                }
                
                if not admin:
                    get_supabase_client().table("cilindro").update(data).eq("id", cilindro_id).eq("user_id", user_id).execute()
                else:
                    get_admin_client().table("cilindro").update(data).eq("id", cilindro_id).execute()
                
                registrar_historico("cilindro", "atualizado", codigo, user_id)
                flash("Cilindro atualizado com sucesso!", "success")
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "atualizar cilindro"), "danger")
            
        elif action == "delete":
            cilindro_id = request.form.get("cilindro_id", "").strip()
            
            if not cilindro_id:
                flash("ID do cilindro é obrigatório", "danger")
                return redirect(url_for("cilindro.list"))
            
            try:
                cilindro_info = get_supabase_client().table("cilindro").select("codigo,user_id").eq("id", cilindro_id).execute().data
                if not cilindro_info:
                    flash("Cilindro não encontrado", "danger")
                    return redirect(url_for("cilindro.list"))
                
                if cilindro_info[0].get("user_id") != user_id:
                    flash("Você não tem permissão para excluir este cilindro.", "danger")
                    return redirect(url_for("cilindro.list"))
                
                cilindro_codigo = cilindro_info[0].get("codigo")
                
                amostra_count = get_supabase_client().table("leitura").select("id", count="exact").eq("cilindro_id", cilindro_id).execute()
                if amostra_count.count and amostra_count.count > 0:
                    flash("Não é possível excluir este cilindro pois existem leituras vinculadas a ele. Exclua primeiro as leituras.", "warning")
                    return redirect(url_for("cilindro.list"))
                
                get_admin_client().table("cilindro").delete().eq("id", cilindro_id).execute()
                
                registrar_historico("cilindro", "excluido", cilindro_codigo, user_id)
                flash("Cilindro excluído com sucesso!", "success")
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "excluir cilindro"), "danger")
            
            return redirect(url_for("cilindro.list"))
        
        elif action == "delete_multiple":
            cilindro_ids = request.form.getlist("cilindro_ids")
            
            if not cilindro_ids:
                flash("Nenhum cilindro selecionado", "danger")
                return redirect(url_for("cilindro.list"))
            
            try:
                deleted_count = 0
                skipped = []
                not_owned = []
                
                for cilindro_id in cilindro_ids:
                    try:
                        cilindro_info = get_supabase_client().table("cilindro").select("codigo,user_id").eq("id", cilindro_id).execute().data
                        if not cilindro_info:
                            continue
                        
                        if cilindro_info[0].get("user_id") != user_id:
                            not_owned.append(cilindro_info[0].get("codigo", cilindro_id))
                            continue
                        
                        cilindro_codigo = cilindro_info[0].get("codigo")
                        
                        amostra_count = get_supabase_client().table("leitura").select("id", count="exact").eq("cilindro_id", cilindro_id).execute()
                        if amostra_count.count and amostra_count.count > 0:
                            skipped.append(cilindro_codigo)
                            continue
                        
                        get_admin_client().table("cilindro").delete().eq("id", cilindro_id).execute()
                        
                        registrar_historico("cilindro", "excluido", cilindro_codigo, user_id)
                        deleted_count += 1
                    except Exception:
                        continue
                
                if deleted_count > 0:
                    flash(f"{deleted_count} cilindro(s) excluído(s) com sucesso!", "success")
                if skipped:
                    flash(f"Alguns cilindos não puderam ser excluídos (leituras vinculadas): {', '.join(skipped)}", "warning")
                if not_owned:
                    flash(f"Alguns cilindos não foram excluídos (não pertencem a você): {', '.join(not_owned)}", "warning")
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "excluir cilindros"), "danger")
            
            return redirect(url_for("cilindro.list"))
    
    response = get_supabase_client().table("cilindro").select("*").order("created_at", desc=True).execute()
    cilindro = response.data or []
    
    total = len(cilindro)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = cilindro[start:end]
    
    cilindro = paginated_data
    
    pages = (total + per_page - 1) // per_page
    end = min(page * per_page, total)
    max_pages = min(pages, 10)
        
    return render_template(
        "cilindro.html", 
        cilindro=cilindro, 
        status_options=CILINDRO_STATUS,
        page=page,
        per_page=per_page,
        total=total,
        pages=pages,
        end=end,
        max_pages=max_pages
    )
