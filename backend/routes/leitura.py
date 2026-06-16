from flask import Blueprint, request, jsonify
from utils.supabase import get_supabase
from utils.decorators import token_required

leitura_bp = Blueprint("leitura", __name__, url_prefix="/api/leituras")


@leitura_bp.route("", methods=["GET"])
@token_required
def get_leituras():
    supabase = get_supabase()
    user_id = request.user_id

    response = supabase.table("leitura").select("*").eq("user_id", user_id).execute()

    return jsonify(response.data), 200


@leitura_bp.route("", methods=["POST"])
@token_required
def create_leitura():
    supabase = get_supabase()
    user_id = request.user_id
    data = request.get_json()

    if not data.get("data") or not data.get("tempo_chama"):
        return jsonify({"message": "Data e tempo de chama são obrigatórios"}), 400

    new_data = {
        "data": data["data"],
        "tempo_chama": data["tempo_chama"],
        "cilindro_id": data.get("cilindro_id"),
        "elemento_id": data.get("elemento_id"),
        "quantidade": data.get("quantidade", 1),
        "user_id": user_id,
    }

    response = supabase.table("leitura").insert(new_data).execute()

    return jsonify(
        {"message": "Leitura criada com sucesso", "data": response.data[0]}
    ), 201


@leitura_bp.route("/<int:leitura_id>", methods=["GET"])
@token_required
def get_leitura(leitura_id):
    supabase = get_supabase()
    user_id = request.user_id

    response = (
        supabase.table("leitura")
        .select("*")
        .eq("id", leitura_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not response.data:
        return jsonify({"message": "Leitura não encontrada"}), 404

    return jsonify(response.data[0]), 200


@leitura_bp.route("/<int:leitura_id>", methods=["PUT"])
@token_required
def update_leitura(leitura_id):
    supabase = get_supabase()
    user_id = request.user_id
    data = request.get_json()

    existing = (
        supabase.table("leitura")
        .select("id")
        .eq("id", leitura_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not existing.data:
        return jsonify({"message": "Leitura não encontrada"}), 404

    update_data = {
        "data": data.get("data", existing.data[0]["data"]),
        "tempo_chama": data.get("tempo_chama", existing.data[0]["tempo_chama"]),
        "cilindro_id": data.get("cilindro_id", existing.data[0].get("cilindro_id")),
        "elemento_id": data.get("elemento_id", existing.data[0].get("elemento_id")),
        "quantidade": data.get(
            "quantidade", existing.data[0].get("quantidade", 1)
        ),
    }

    response = (
        supabase.table("leitura").update(update_data).eq("id", leitura_id).execute()
    )

    return jsonify(
        {"message": "Leitura atualizada com sucesso", "data": response.data[0]}
    ), 200


@leitura_bp.route("/<int:leitura_id>", methods=["DELETE"])
@token_required
def delete_leitura(leitura_id):
    supabase = get_supabase()
    user_id = request.user_id

    existing = (
        supabase.table("leitura")
        .select("id")
        .eq("id", leitura_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not existing.data:
        return jsonify({"message": "Leitura não encontrada"}), 404

    supabase.table("leitura").delete().eq("id", leitura_id).execute()

    return jsonify({"message": "Leitura excluída com sucesso"}), 200
