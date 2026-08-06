from flask import Blueprint, request, jsonify
from utils.supabase import get_supabase
from utils.decorators import token_required
from config import LITROS_EQUIVALENTES_KG, CUSTO_DEFAULT, GAS_KG_DEFAULT

cilindro_bp = Blueprint("cilindro", __name__, url_prefix="/api/cilindros")


def _numero_valido(numero):
    try:
        return int(numero) >= 1
    except (ValueError, TypeError):
        return False


@cilindro_bp.route("", methods=["GET"])
@token_required
def get_cilindros():
    supabase = get_supabase()
    user_id = request.user_id

    response = supabase.table("cilindro").select("*").eq("user_id", user_id).execute()

    return jsonify(response.data), 200


@cilindro_bp.route("", methods=["POST"])
@token_required
def create_cilindro():
    supabase = get_supabase()
    user_id = request.user_id
    data = request.get_json()

    if not data.get("numero") or not _numero_valido(data["numero"]):
        return jsonify({"message": "Número é obrigatório"}), 400

    if not data.get("data_compra"):
        return jsonify({"message": "Data de compra é obrigatória"}), 400

    numero = int(data["numero"])

    existing = (
        supabase.table("cilindro")
        .select("id")
        .eq("numero", numero)
        .eq("user_id", user_id)
        .execute()
    )
    if existing.data:
        return jsonify({"message": "Número já existe"}), 400

    gas_kg = data.get("gas_kg", GAS_KG_DEFAULT)
    litros = gas_kg * LITROS_EQUIVALENTES_KG
    custo = data.get("custo", CUSTO_DEFAULT)

    new_data = {
        "numero": numero,
        "data_compra": data["data_compra"],
        "data_inicio_consumo": data.get("data_inicio_consumo"),
        "data_fim": data.get("data_fim"),
        "gas_kg": gas_kg,
        "litros_equivalentes": litros,
        "custo": custo,
        "status": data.get("status", "ativo"),
        "user_id": user_id,
    }

    response = supabase.table("cilindro").insert(new_data).execute()

    return jsonify(
        {"message": "Cilindro criado com sucesso", "data": response.data[0]}
    ), 201


@cilindro_bp.route("/<int:cilindro_id>", methods=["GET"])
@token_required
def get_cilindro(cilindro_id):
    supabase = get_supabase()
    user_id = request.user_id

    response = (
        supabase.table("cilindro")
        .select("*")
        .eq("id", cilindro_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not response.data:
        return jsonify({"message": "Cilindro não encontrado"}), 404

    return jsonify(response.data[0]), 200


@cilindro_bp.route("/<int:cilindro_id>", methods=["PUT"])
@token_required
def update_cilindro(cilindro_id):
    supabase = get_supabase()
    user_id = request.user_id
    data = request.get_json()

    existing = (
        supabase.table("cilindro")
        .select("id,numero,gas_kg,data_compra,data_inicio_consumo,data_fim,custo,status")
        .eq("id", cilindro_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not existing.data:
        return jsonify({"message": "Cilindro não encontrado"}), 404

    if data.get("numero") is not None:
        if not _numero_valido(data["numero"]):
            return jsonify({"message": "Número inválido"}), 400
        numero = int(data["numero"])
        duplicate = (
            supabase.table("cilindro")
            .select("id")
            .eq("numero", numero)
            .eq("user_id", user_id)
            .neq("id", cilindro_id)
            .execute()
        )
        if duplicate.data:
            return jsonify({"message": "Número já existe"}), 400

    gas_kg = data.get("gas_kg", existing.data[0].get("gas_kg", GAS_KG_DEFAULT))
    litros = gas_kg * LITROS_EQUIVALENTES_KG

    update_data = {
        "numero": int(data["numero"]) if data.get("numero") is not None else existing.data[0]["numero"],        "data_compra": data.get("data_compra", existing.data[0]["data_compra"]),
        "data_inicio_consumo": data.get("data_inicio_consumo", existing.data[0].get("data_inicio_consumo")),
        "data_fim": data.get("data_fim", existing.data[0].get("data_fim")),
        "gas_kg": gas_kg,
        "litros_equivalentes": litros,
        "custo": data.get("custo", existing.data[0]["custo"]),
        "status": data.get("status", existing.data[0]["status"]),
    }

    response = (
        supabase.table("cilindro").update(update_data).eq("id", cilindro_id).execute()
    )

    return jsonify(
        {"message": "Cilindro atualizado com sucesso", "data": response.data[0]}
    ), 200


@cilindro_bp.route("/<int:cilindro_id>", methods=["DELETE"])
@token_required
def delete_cilindro(cilindro_id):
    supabase = get_supabase()
    user_id = request.user_id

    existing = (
        supabase.table("cilindro")
        .select("id")
        .eq("id", cilindro_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not existing.data:
        return jsonify({"message": "Cilindro não encontrado"}), 404

    supabase.table("cilindro").delete().eq("id", cilindro_id).execute()

    return jsonify({"message": "Cilindro excluído com sucesso"}), 200
