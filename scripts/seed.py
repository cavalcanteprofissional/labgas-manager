"""Seed script — cria/reseta o usuário de teste no Supabase.

Lê TEST_EMAIL e TEST_PASSWORD do frontend/.env.local.
Uso:
    python scripts/seed.py
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / "frontend" / ".env.local")

TEST_EMAIL = os.getenv("TEST_EMAIL", "teste@labgas.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "123456")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERRO: SUPABASE_URL e SUPABASE_SERVICE_KEY são obrigatórios no .env.local")
    sys.exit(1)

admin = create_client(SUPABASE_URL, SUPABASE_KEY)


def seed():
    # 1. Verifica se o auth user já existe pelo perfil
    result = admin.table("perfil").select("id").eq("email", TEST_EMAIL).execute()
    existing = result.data[0] if result.data else None

    if existing:
        user_id = existing["id"]
        print(f"Usuário {TEST_EMAIL} já existe (id={user_id}). Resetando senha...")
        admin.auth.admin.update_user_by_id(user_id, {"password": TEST_PASSWORD})
        print("Senha resetada.")
    else:
        print(f"Criando usuário {TEST_EMAIL}...")
        resp = admin.auth.admin.create_user({
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "email_confirm": True,
        })
        user_id = resp.user.id
        print(f"Usuário criado (id={user_id}).")

    # 2. Upsert do perfil (admin + todas as abas)
    perfil_data = {
        "id": user_id,
        "email": TEST_EMAIL,
        "role": "admin",
        "ativo": True,
        "nome": "Usuário Teste",
        "habilitar_abas": {
            "cilindro": True,
            "pressao": True,
            "elemento": True,
            "leitura": True,
            "amostra": True,
            "historico": True,
        },
    }

    if existing:
        admin.table("perfil").update(perfil_data).eq("id", user_id).execute()
        print("Perfil atualizado.")
    else:
        admin.table("perfil").insert(perfil_data).execute()
        print("Perfil inserido.")

    print(f"\nSeed concluído. Login: {TEST_EMAIL} / {TEST_PASSWORD}")


if __name__ == "__main__":
    seed()
