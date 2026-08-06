# Cilindro blueprint - CRUD operations
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from utils.supabase_utils import get_supabase_client, get_admin_client
from utils.validators import safe_float, validar_numero_cilindro
from utils.constants import ITEMS_PER_PAGE, LITROS_EQUIVALENTES_KG, GAS_KG_DEFAULT, CUSTO_DEFAULT, CILINDRO_STATUS
from utils.cilindro_utils import enriquecer_cilindros, normalizar_numero_cilindro, numero_corresponde
from utils.erros_utils import formatar_erro_supabase
from blueprints.helpers import get_user_id, is_dev, registrar_historico, pode_acessar_aba, get_authenticated_client
from utils.cache_utils import invalidate_user_caches

cilindro_bp = Blueprint('cilindro', __name__)


def _chave_ordenacao_cilindros(c):
    """Ordena pelo numero do cilindro (registros sem numero vao para o fim)."""
    numero = normalizar_numero_cilindro(c.get("numero"))
    return numero if numero is not None else float("inf")


def _ler_numero(form, campo="numero"):
    """Le e valida o numero do cilindro do form. Retorna int ou None."""
    raw = form.get(campo, "").strip()
    if not validar_numero_cilindro(raw):
        return None
    return int(raw)


@cilindro_bp.route("/cilindros", methods=["GET", "POST"])
def list():
    if not pode_acessar_aba("cilindro"):
        flash("Você não tem permissão para acessar esta aba.", "warning")
        from flask import current_app
        return redirect(current_app.config.get("LOGIN_VIEW", "/dashboard"))
    
    user_id = get_user_id()
    dev = is_dev()
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", ITEMS_PER_PAGE, type=int)
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "create":
            numero = _ler_numero(request.form)
            data_compra = request.form.get("data_compra", "").strip()
            data_inicio_consumo = request.form.get("data_inicio_consumo", "").strip()
            data_fim = request.form.get("data_fim", "").strip()
            gas_kg = request.form.get("gas_kg", "")
            custo = request.form.get("custo", "")
            status = request.form.get("status", "ativo")
            
            if status not in CILINDRO_STATUS:
                status = "ativo"
            
            if numero is None or not data_compra:
                flash("Número e data de compra são obrigatórios", "danger")
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
            
            if not dev:
                try:
                    existing = get_supabase_client().table("cilindro").select("id").eq("user_id", user_id).eq("numero", numero).execute()
                    if existing.data:
                        flash("Número já existe para este usuário", "danger")
                        return redirect(url_for("cilindro.list"))
                except Exception as e:
                    flash(formatar_erro_supabase(str(e), "verificar número"), "danger")
                    return redirect(url_for("cilindro.list"))
            
            try:
                data = {
                    "numero": numero,
                    "data_compra": data_compra,
                    "data_inicio_consumo": data_inicio_consumo,
                    "data_fim": data_fim or None,
                    "gas_kg": gas_kg_val,
                    "litros_equivalentes": gas_kg_val * LITROS_EQUIVALENTES_KG,
                    "custo": custo_val,
                    "status": status,
                    "user_id": user_id
                }
                
                if dev:
                    client = get_admin_client()
                else:
                    client = get_authenticated_client()
                
                resp = client.table("cilindro").insert(data).execute()
                novo_id = resp.data[0]["id"] if resp.data else None
                registrar_historico("cilindro", "criado", str(numero), user_id, ref_id=novo_id)
                invalidate_user_caches(user_id)
                flash("Cilindro criado com sucesso!", "success")
            except Exception as e:
                error_str = str(e)
                flash(formatar_erro_supabase(error_str, "criar cilindro"), "danger")
            
        elif action == "update":
            cilindro_id = request.form.get("cilindro_id", "").strip()
            numero = _ler_numero(request.form)
            data_compra = request.form.get("data_compra", "").strip()
            data_inicio_consumo = request.form.get("data_inicio_consumo", "").strip()
            data_fim = request.form.get("data_fim", "").strip()
            gas_kg = request.form.get("gas_kg", "")
            custo = request.form.get("custo", "")
            status = request.form.get("status", "ativo")
            
            if status not in CILINDRO_STATUS:
                status = "ativo"
            
            if not cilindro_id or numero is None or not data_compra:
                flash("ID do cilindro, número e data de compra são obrigatórios", "danger")
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
                if not dev:
                    existing = get_supabase_client().table("cilindro").select("id").eq("user_id", user_id).eq("numero", numero).neq("id", cilindro_id).execute()
                    if existing.data:
                        flash("Número já existe para este usuário", "danger")
                        return redirect(url_for("cilindro.list"))
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "verificar número"), "danger")
                return redirect(url_for("cilindro.list"))
            
            try:
                data = {
                    "numero": numero,
                    "data_compra": data_compra,
                    "data_inicio_consumo": data_inicio_consumo or None,
                    "data_fim": data_fim or None,
                    "gas_kg": gas_kg_val,
                    "litros_equivalentes": gas_kg_val * LITROS_EQUIVALENTES_KG,
                    "custo": custo_val,
                    "status": status
                }
                
                if not dev:
                    get_authenticated_client().table("cilindro").update(data).eq("id", cilindro_id).eq("user_id", user_id).execute()
                else:
                    get_admin_client().table("cilindro").update(data).eq("id", cilindro_id).execute()
                
                registrar_historico("cilindro", "atualizado", str(numero), user_id, ref_id=int(cilindro_id))
                invalidate_user_caches(user_id)
                flash("Cilindro atualizado com sucesso!", "success")
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "atualizar cilindro"), "danger")
            
        elif action == "delete":
            cilindro_id = request.form.get("cilindro_id", "").strip()
            
            if not cilindro_id:
                flash("ID do cilindro é obrigatório", "danger")
                return redirect(url_for("cilindro.list"))
            
            try:
                cilindro_info = get_supabase_client().table("cilindro").select("numero,user_id").eq("id", cilindro_id).execute().data
                if not cilindro_info:
                    flash("Cilindro não encontrado", "danger")
                    return redirect(url_for("cilindro.list"))
                
                if not dev and cilindro_info[0].get("user_id") != user_id:
                    flash("Você não tem permissão para excluir este cilindro.", "danger")
                    return redirect(url_for("cilindro.list"))
                
                cilindro_numero = str(cilindro_info[0].get("numero", cilindro_id))
                
                amostra_count = get_supabase_client().table("leitura").select("id", count="exact").eq("cilindro_id", cilindro_id).execute()
                if amostra_count.count and amostra_count.count > 0:
                    flash("Não é possível excluir este cilindro pois existem leituras vinculadas a ele. Exclua primeiro as leituras.", "warning")
                    return redirect(url_for("cilindro.list"))
                
                (get_admin_client() if dev else get_authenticated_client()).table("cilindro").delete().eq("id", cilindro_id).execute()
                
                registrar_historico("cilindro", "excluido", cilindro_numero, user_id, ref_id=int(cilindro_id))
                invalidate_user_caches(user_id)
                flash("Cilindro excluído com sucesso!", "success")
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "excluir cilindro"), "danger")
            
            return redirect(url_for("cilindro.list"))
        
        elif action == "delete_multiple":
            raw_ids = request.form.getlist("cilindro_ids")
            if not raw_ids:
                flash("Nenhum cilindro selecionado", "danger")
                return redirect(url_for("cilindro.list"))

            ids = []
            for v in raw_ids:
                try:
                    ids.append(int(v))
                except (ValueError, TypeError):
                    pass
            if not ids:
                flash("IDs inválidos", "danger")
                return redirect(url_for("cilindro.list"))

            try:
                supabase = get_supabase_client()
                cilindros = supabase.table("cilindro").select("id,numero,user_id").in_("id", ids).execute().data or []

                tem_leitura = set()
                leituras = supabase.table("leitura").select("cilindro_id").in_("cilindro_id", ids).execute().data or []
                for lr in leituras:
                    tem_leitura.add(lr["cilindro_id"])

                permitidos = []
                skipped = []
                not_owned = []
                for c in cilindros:
                    rotulo = str(c.get("numero", c["id"]))
                    if not dev and c.get("user_id") != user_id:
                        not_owned.append(rotulo)
                    elif c["id"] in tem_leitura:
                        skipped.append(rotulo)
                    else:
                        permitidos.append(c)

                if permitidos:
                    (get_admin_client() if dev else get_authenticated_client()).table("cilindro").delete().in_("id", [c["id"] for c in permitidos]).execute()
                    for c in permitidos:
                        registrar_historico("cilindro", "excluido", str(c.get("numero", c["id"])), user_id, ref_id=c["id"])
                    invalidate_user_caches(user_id)

                if permitidos:
                    flash(f"{len(permitidos)} cilindro(s) excluído(s) com sucesso!", "success")
                if skipped:
                    flash(f"Alguns cilindros não puderam ser excluídos (leituras vinculadas): {', '.join(skipped)}", "warning")
                if not_owned:
                    flash(f"Alguns cilindros não foram excluídos (não pertencem a você): {', '.join(not_owned)}", "warning")
                if not permitidos and not skipped and not not_owned:
                    flash("Nenhum cilindro foi excluído", "warning")
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "excluir cilindros"), "danger")

            return redirect(url_for("cilindro.list"))
    
    offset = (page - 1) * per_page
    query = get_supabase_client().table("cilindro").select("*", count="exact")
    if not dev:
        query = query.eq("user_id", user_id)

    q = request.args.get("q", "").strip()
    status_filtro = request.args.get("status", "").strip()
    data_inicio = request.args.get("data_inicio", "").strip()
    data_fim = request.args.get("data_fim", "").strip()
    if q:
        codes = get_supabase_client().table("cilindro").select("id,numero")
        if not dev:
            codes = codes.eq("user_id", user_id)
        todos = (codes.execute().data or [])
        ids = [c["id"] for c in todos if numero_corresponde(c.get("numero"), q)]
        query = query.in_("id", ids) if ids else query.eq("id", 0)
    if status_filtro in CILINDRO_STATUS:
        query = query.eq("status", status_filtro)
    if data_inicio:
        try:
            datetime.strptime(data_inicio, "%Y-%m-%d")
            query = query.gte("data_compra", data_inicio)
        except ValueError:
            pass
    if data_fim:
        try:
            datetime.strptime(data_fim, "%Y-%m-%d")
            query = query.lte("data_compra", data_fim)
        except ValueError:
            pass

    response = query.order("numero").range(offset, offset + per_page - 1).execute()
    cilindro = response.data or []
    total = response.count or 0
    
    cilindro = enriquecer_cilindros(cilindro)
    cilindro.sort(key=_chave_ordenacao_cilindros)
    
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
