from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash

from utils.supabase_utils import get_supabase_client, get_admin_client
from utils.validators import safe_int, safe_float, formatar_tempo_chama
from utils.constants import ITEMS_PER_PAGE
from utils.erros_utils import formatar_erro_supabase
from blueprints.helpers import get_user_id, is_dev, registrar_historico, pode_acessar_aba, get_authenticated_client
from utils.cache_utils import invalidate_user_caches

leitura_bp = Blueprint('leitura', __name__)


@leitura_bp.route("/leituras", methods=["GET", "POST"])
def leitura_list():
    if not pode_acessar_aba("leitura"):
        flash("Você não tem permissão para acessar esta aba.", "warning")
        return redirect(url_for("dashboard"))
    
    user_id = get_user_id()
    dev = is_dev()
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", ITEMS_PER_PAGE, type=int)
    
    cilindro = get_authenticated_client().table("cilindro").select("id,codigo,status").eq("user_id", user_id).order("codigo").execute().data or []
    
    elementos = get_authenticated_client().table("elemento").select("id,nome").eq("user_id", user_id).order("nome").execute().data or []
    
    cilindro_dict = {c["id"]: c["codigo"] for c in cilindro}
    elemento_dict = {e["id"]: e["nome"] for e in elementos}
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "create":
            data_leitura = request.form.get("data")
            tempo_chama = request.form.get("tempo_chama")
            cilindro_id = request.form.get("cilindro_id", "").strip()
            elemento_id = request.form.get("elemento_id", "").strip()
            quantidade = request.form.get("quantidade", 1)

            if not data_leitura or not cilindro_id or not elemento_id:
                flash("Data, cilindro e elemento são obrigatórios", "danger")
                return redirect(url_for("leitura.leitura_list"))
            
            try:
                datetime.strptime(data_leitura, "%Y-%m-%d")
            except ValueError:
                flash("Data inválida", "danger")
                return redirect(url_for("leitura.leitura_list"))

            try:
                tempo_val = formatar_tempo_chama(tempo_chama or "00:00:00")
            except ValueError as e:
                flash(str(e), "danger")
                return redirect(url_for("leitura.leitura_list"))

            try:
                quantidade_val = safe_int(quantidade, 1)
                if quantidade_val < 0:
                    flash("Quantidade deve ser um número positivo", "danger")
                    return redirect(url_for("leitura.leitura_list"))
            except ValueError as e:
                flash("Quantidade inválida.", "danger")
                return redirect(url_for("leitura.leitura_list"))

            cilindro_id_int = int(cilindro_id)
            elemento_id_int = int(elemento_id)

            if not dev:
                if cilindro_id_int not in cilindro_dict:
                    flash("Cilindro não encontrado", "danger")
                    return redirect(url_for("leitura.leitura_list"))
                if elemento_id_int not in elemento_dict:
                    flash("Elemento não encontrado", "danger")
                    return redirect(url_for("leitura.leitura_list"))

            try:
                data_insert = {
                    "data": data_leitura,
                    "tempo_chama": tempo_val,
                    "cilindro_id": cilindro_id_int,
                    "elemento_id": elemento_id_int,
                    "quantidade": quantidade_val,
                    "user_id": user_id
                }
                
                if dev:
                    client = get_admin_client()
                else:
                    client = get_authenticated_client()
                
                client.table("leitura").insert(data_insert).execute()
                nome_leitura = f"{cilindro_dict.get(cilindro_id_int, 'N/A')} - {elemento_dict.get(elemento_id_int, 'N/A')}"
                registrar_historico("leitura", "criado", nome_leitura, user_id)
                invalidate_user_caches(user_id)
                flash("Leitura registrada com sucesso!", "success")
            except Exception as e:
                error_str = str(e)
                flash(formatar_erro_supabase(error_str, "criar leitura"), "danger")
            
        elif action == "update":
            leitura_id = request.form.get("leitura_id")
            data_leitura = request.form.get("data")
            tempo_chama = request.form.get("tempo_chama")
            cilindro_id = request.form.get("cilindro_id", "").strip()
            elemento_id = request.form.get("elemento_id", "").strip()
            quantidade = request.form.get("quantidade", 1)

            if not leitura_id or not data_leitura or not cilindro_id or not elemento_id:
                flash("ID da leitura, data, cilindro e elemento são obrigatórios", "danger")
                return redirect(url_for("leitura.leitura_list"))

            try:
                quantidade_val = safe_int(quantidade, 1)
                if quantidade_val < 0:
                    flash("Quantidade deve ser um número positivo", "danger")
                    return redirect(url_for("leitura.leitura_list"))
            except ValueError as e:
                flash("Quantidade inválida.", "danger")
                return redirect(url_for("leitura.leitura_list"))

            cilindro_id_int = int(cilindro_id)
            elemento_id_int = int(elemento_id)

            data_update = {
                "data": data_leitura,
                "tempo_chama": tempo_chama,
                "cilindro_id": cilindro_id_int,
                "elemento_id": elemento_id_int,
                "quantidade": quantidade_val
            }
            
            if not dev:
                if cilindro_id_int not in cilindro_dict:
                    flash("Cilindro não encontrado", "danger")
                    return redirect(url_for("leitura.leitura_list"))
                if elemento_id_int not in elemento_dict:
                    flash("Elemento não encontrado", "danger")
                    return redirect(url_for("leitura.leitura_list"))

            nome_leitura = f"{cilindro_dict.get(cilindro_id_int, 'N/A')} - {elemento_dict.get(elemento_id_int, 'N/A')}"

            try:
                if not dev:
                    get_supabase_client().table("leitura").update(data_update).eq("id", leitura_id).eq("user_id", user_id).execute()
                else:
                    get_admin_client().table("leitura").update(data_update).eq("id", leitura_id).execute()

                registrar_historico("leitura", "atualizado", nome_leitura, user_id)
                invalidate_user_caches(user_id)
                flash("Leitura atualizada com sucesso!", "success")
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "atualizar leitura"), "danger")
            
        elif action == "delete":
            leitura_id = request.form.get("leitura_id")

            if not leitura_id:
                flash("ID da leitura é obrigatório", "danger")
                return redirect(url_for("leitura.leitura_list"))
            
            try:
                leitura_info = get_supabase_client().table("leitura").select("cilindro_id,elemento_id,user_id").eq("id", leitura_id).execute().data
                if not leitura_info:
                    flash("Registro de leitura não encontrado", "danger")
                    return redirect(url_for("leitura.leitura_list"))
                
                if not dev and leitura_info[0].get("user_id") != user_id:
                    flash("Você não tem permissão para excluir esta leitura.", "danger")
                    return redirect(url_for("leitura.leitura_list"))
                
                nome_leitura = "N/A"
                cilindro_nome = get_supabase_client().table("cilindro").select("codigo").eq("id", leitura_info[0]["cilindro_id"]).execute().data
                elemento_nome = get_supabase_client().table("elemento").select("nome").eq("id", leitura_info[0]["elemento_id"]).execute().data
                nome_leitura = f"{cilindro_nome[0]['codigo'] if cilindro_nome else 'N/A'} - {elemento_nome[0]['nome'] if elemento_nome else 'N/A'}"

                (get_admin_client() if dev else get_authenticated_client()).table("leitura").delete().eq("id", leitura_id).execute()
                registrar_historico("leitura", "excluido", nome_leitura, user_id)
                invalidate_user_caches(user_id)
                flash("Leitura excluída com sucesso!", "success")
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "excluir leitura"), "danger")
            
            return redirect(url_for("leitura.leitura_list"))
        
        elif action == "delete_multiple":
            raw_ids = request.form.getlist("leitura_ids")
            if not raw_ids:
                flash("Nenhuma leitura selecionada", "danger")
                return redirect(url_for("leitura.leitura_list"))

            ids = []
            for v in raw_ids:
                try:
                    ids.append(int(v))
                except (ValueError, TypeError):
                    pass
            if not ids:
                flash("IDs inválidos", "danger")
                return redirect(url_for("leitura.leitura_list"))

            try:
                supabase = get_supabase_client()
                leituras = supabase.table("leitura").select("id,cilindro_id,elemento_id,user_id").in_("id", ids).execute().data or []

                permitted = [l for l in leituras if dev or l.get("user_id") == user_id]
                not_owned_count = len(ids) - len(permitted)

                if not permitted:
                    flash("Nenhuma leitura foi excluída", "warning")
                    return redirect(url_for("leitura.leitura_list"))

                cilindro_ids = sorted(set(l["cilindro_id"] for l in permitted))
                elemento_ids = sorted(set(l["elemento_id"] for l in permitted))

                cilindros = supabase.table("cilindro").select("id,codigo").in_("id", cilindro_ids).execute().data or []
                cil_map = {c["id"]: c.get("codigo", "N/A") for c in cilindros}
                elementos = supabase.table("elemento").select("id,nome").in_("id", elemento_ids).execute().data or []
                elem_map = {e["id"]: e.get("nome", "N/A") for e in elementos}

                (get_admin_client() if dev else get_authenticated_client()).table("leitura").delete().in_("id", [l["id"] for l in permitted]).execute()

                for l in permitted:
                    nome = f"{cil_map.get(l['cilindro_id'], 'N/A')} - {elem_map.get(l['elemento_id'], 'N/A')}"
                    registrar_historico("leitura", "excluido", nome, user_id)
                invalidate_user_caches(user_id)

                flash(f"{len(permitted)} leitura(s) excluída(s) com sucesso!", "success")
                if not_owned_count:
                    flash(f"{not_owned_count} leitura(s) não foram excluídas (não pertencem a você)", "warning")
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "excluir leituras"), "danger")

            return redirect(url_for("leitura.leitura_list"))
    
    response = get_supabase_client().table("leitura").select("*").order("data", desc=True).execute()
    leituras = response.data or []
    
    total = len(leituras)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = leituras[start:end]
    
    leituras = paginated_data
    
    pages = (total + per_page - 1) // per_page
    end = min(page * per_page, total)
    max_pages = min(pages, 10)
    
    for leitura in leituras:
        for c in cilindro:
            if c.get("id") == leitura.get("cilindro_id"):
                leitura["cilindro_nome"] = c.get("codigo")
                break
        for e in elementos:
            if e.get("id") == leitura.get("elemento_id"):
                leitura["elemento_nome"] = e.get("nome")
                break
    
    return render_template(
        "leitura.html", 
        leituras=leituras, 
        cilindro=cilindro, 
        elementos=elementos,
        page=page,
        per_page=per_page,
        total=total,
        pages=pages,
        end=end,
        max_pages=max_pages
    )
