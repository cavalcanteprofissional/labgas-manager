from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from utils.supabase_utils import get_supabase_client, get_admin_client
from utils.validators import safe_int
from utils.constants import ITEMS_PER_PAGE
from utils.erros_utils import formatar_erro_supabase
from blueprints.helpers import get_user_id, is_admin, registrar_historico, pode_acessar_aba, get_authenticated_client

amostra_bp = Blueprint("amostra", __name__)


@amostra_bp.route("/amostras", methods=["GET", "POST"])
def list():
    if not pode_acessar_aba("amostra"):
        flash("Você não tem permissão para acessar esta aba.", "warning")
        return redirect(current_app.config.get("LOGIN_VIEW", "/dashboard"))

    user_id = get_user_id()
    admin = is_admin()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", ITEMS_PER_PAGE, type=int)

    supabase = get_supabase_client()
    admin_client = get_admin_client()
    authenticated = get_authenticated_client()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            numero_amostra = request.form.get("numero_amostra", "").strip()
            lote = request.form.get("lote", "").strip()
            elemento_ids = request.form.getlist("elemento_ids")

            if not numero_amostra:
                flash("N° da Amostra é obrigatório", "danger")
                return redirect(url_for("amostra.list"))

            if not lote:
                flash("Lote é obrigatório", "danger")
                return redirect(url_for("amostra.list"))

            numero_val = safe_int(numero_amostra)
            if numero_val is None or numero_val <= 0:
                flash("N° da Amostra deve ser um número inteiro positivo", "danger")
                return redirect(url_for("amostra.list"))

            lote_val = safe_int(lote)
            if lote_val is None or lote_val < 0:
                flash("Lote deve ser um número inteiro não negativo", "danger")
                return redirect(url_for("amostra.list"))

            try:
                client = admin_client if admin else authenticated
                response = client.table("amostra").insert({
                    "numero_amostra": numero_val,
                    "lote": lote_val,
                    "user_id": user_id,
                }).execute()

                amostra_id = response.data[0]["id"]

                for elem_id in elemento_ids:
                    try:
                        eid = int(elem_id)
                        client.table("amostra_elemento").insert({
                            "amostra_id": amostra_id,
                            "elemento_id": eid,
                        }).execute()
                    except (ValueError, Exception):
                        pass

                registrar_historico("amostra", "criado", f"#{numero_val} Lote {lote_val}", user_id)
                flash(f"Amostra #{numero_val} criada com sucesso!", "success")
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "criar amostra"), "danger")

            return redirect(url_for("amostra.list"))

        elif action == "update":
            amostra_id = request.form.get("amostra_id")
            numero_amostra = request.form.get("numero_amostra", "").strip()
            lote = request.form.get("lote", "").strip()
            elemento_ids = request.form.getlist("elemento_ids")

            if not amostra_id:
                flash("ID da amostra não informado", "danger")
                return redirect(url_for("amostra.list"))

            if not numero_amostra:
                flash("N° da Amostra é obrigatório", "danger")
                return redirect(url_for("amostra.list"))

            numero_val = safe_int(numero_amostra)
            if numero_val is None or numero_val <= 0:
                flash("N° da Amostra deve ser um número inteiro positivo", "danger")
                return redirect(url_for("amostra.list"))

            if not lote:
                flash("Lote é obrigatório", "danger")
                return redirect(url_for("amostra.list"))

            try:
                amostra_id = int(amostra_id)
            except (ValueError, TypeError):
                flash("ID inválido", "danger")
                return redirect(url_for("amostra.list"))

            lote_val = safe_int(lote)
            if lote_val is None or lote_val < 0:
                flash("Lote inválido", "danger")
                return redirect(url_for("amostra.list"))

            existing = supabase.table("amostra").select("id,user_id").eq("id", amostra_id).execute()
            if not existing.data:
                flash("Amostra não encontrada", "danger")
                return redirect(url_for("amostra.list"))
            if not admin and existing.data[0].get("user_id") != user_id:
                flash("Você não tem permissão para editar esta amostra", "danger")
                return redirect(url_for("amostra.list"))

            try:
                client = admin_client if admin else authenticated
                client.table("amostra").update({
                    "numero_amostra": numero_val,
                    "lote": lote_val,
                }).eq("id", amostra_id).execute()

                client.table("amostra_elemento").delete().eq("amostra_id", amostra_id).execute()
                for elem_id in elemento_ids:
                    try:
                        eid = int(elem_id)
                        client.table("amostra_elemento").insert({
                            "amostra_id": amostra_id,
                            "elemento_id": eid,
                        }).execute()
                    except (ValueError, Exception):
                        pass

                registro_nome = f"#{numero_val} Lote {lote_val}"
                registrar_historico("amostra", "atualizado", registro_nome, user_id)
                flash("Amostra atualizada com sucesso!", "success")
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "atualizar amostra"), "danger")

            return redirect(url_for("amostra.list"))

        elif action == "delete":
            amostra_id = request.form.get("amostra_id")

            if not amostra_id:
                flash("ID da amostra não informado", "danger")
                return redirect(url_for("amostra.list"))

            try:
                amostra_id = int(amostra_id)
            except (ValueError, TypeError):
                flash("ID inválido", "danger")
                return redirect(url_for("amostra.list"))

            existing = supabase.table("amostra").select("numero_amostra,lote,user_id").eq("id", amostra_id).execute()
            if not existing.data:
                flash("Amostra não encontrada", "danger")
                return redirect(url_for("amostra.list"))
            if not admin and existing.data[0].get("user_id") != user_id:
                flash("Você não tem permissão para excluir esta amostra", "danger")
                return redirect(url_for("amostra.list"))

            try:
                num = existing.data[0].get("numero_amostra", "?")
                lote_val = existing.data[0].get("lote", "?")
                client = admin_client if admin else authenticated
                client.table("amostra_elemento").delete().eq("amostra_id", amostra_id).execute()
                client.table("amostra").delete().eq("id", amostra_id).execute()
                registrar_historico("amostra", "excluido", f"#{num} Lote {lote_val}", user_id)
                flash("Amostra excluída com sucesso!", "success")
            except Exception as e:
                flash(formatar_erro_supabase(str(e), "excluir amostra"), "danger")

            return redirect(url_for("amostra.list"))

        elif action == "delete_multiple":
            amostra_ids = request.form.getlist("amostra_ids")

            if not amostra_ids:
                flash("Nenhuma amostra selecionada", "danger")
                return redirect(url_for("amostra.list"))

            deleted = 0
            for aid in amostra_ids:
                try:
                    aid = int(aid)
                    existing = supabase.table("amostra").select("user_id").eq("id", aid).execute()
                    if not existing.data:
                        continue
                    if not admin and existing.data[0].get("user_id") != user_id:
                        continue

                    client = admin_client if admin else authenticated
                    client.table("amostra_elemento").delete().eq("amostra_id", aid).execute()
                    client.table("amostra").delete().eq("id", aid).execute()
                    deleted += 1
                except (ValueError, Exception):
                    continue

            if deleted:
                registrar_historico("amostra", "excluido", f"{deleted} amostras", user_id)
                flash(f"{deleted} amostra(s) excluída(s) com sucesso!", "success")
            else:
                flash("Nenhuma amostra foi excluída", "warning")

            return redirect(url_for("amostra.list"))

    response = supabase.table("amostra").select("*").order("numero_amostra", desc=True).execute()
    amostras = response.data or []

    amostra_ids = [a["id"] for a in amostras]
    elementos_map = {a["id"]: [] for a in amostras}
    if amostra_ids:
        ae_response = supabase.table("amostra_elemento").select("amostra_id, elemento_id").in_("amostra_id", amostra_ids).execute()
        if ae_response.data:
            elem_ids = sorted(set(ae["elemento_id"] for ae in ae_response.data))
            elem_response = supabase.table("elemento").select("id, nome").in_("id", elem_ids).execute()
            elem_nomes = {e["id"]: e["nome"] for e in (elem_response.data or [])}
            for ae in ae_response.data:
                aid = ae["amostra_id"]
                eid = ae["elemento_id"]
                if aid in elementos_map and eid in elem_nomes:
                    elementos_map[aid].append(elem_nomes[eid])

    for a in amostras:
        a["elementos_nomes"] = elementos_map.get(a["id"], [])

    elementos_disponiveis = supabase.table("elemento").select("id, nome").order("nome").execute()
    elementos = elementos_disponiveis.data or []

    lotes_response = supabase.table("amostra").select("lote, created_at").order("created_at", desc=True).execute()
    lotes_vistos = []
    vistos = set()
    for item in (lotes_response.data or []):
        if item["lote"] not in vistos:
            vistos.add(item["lote"])
            lotes_vistos.append(item["lote"])

    total = len(amostras)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = amostras[start:end]

    return render_template(
        "amostra.html",
        amostras=paginated,
        elementos=elementos,
        lotes=lotes_vistos,
        page=page,
        per_page=per_page,
        total=total,
        user_id=user_id,
        admin=admin,
    )
