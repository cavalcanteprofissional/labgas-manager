"""setup_backup_user.py — Cria/atualiza o usuário PostgreSQL readonly para backup.

Lê BACKUP_DB_PASSWORD e DATABASE_URL (superuser) do frontend/.env.local.
Cria (ou altera a senha de) `backup_user` com permissão SELECT nos schemas
`public` e `auth`, depois exibe a DATABASE_URL readonly pronta para usar.

No Supabase, o schema `auth` é gerenciado pelo `supabase_admin` e pode não
aceitar GRANT via `postgres`. Se o script falhar no schema `auth`, execute
os comandos manualmente no Supabase SQL Editor.

Uso:
    python scripts/setup_backup_user.py
"""

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / "frontend" / ".env.local")

SUPER_DB_URL = os.getenv("DATABASE_URL_POSTGRES") or os.getenv("DATABASE_URL")
BACKUP_PASSWORD = os.getenv("BACKUP_DB_PASSWORD")

if not SUPER_DB_URL:
    print("ERRO: DATABASE_URL_POSTGRES (superuser) é obrigatória para configurar o backup_user.")
    print("Adicione a connection string do PostgreSQL (usuário postgres) ao .env.local:")
    print("DATABASE_URL_POSTGRES=postgresql://postgres:senha@db.xxxxx.supabase.co:5432/postgres?sslmode=require")
    sys.exit(1)

if not BACKUP_PASSWORD:
    print("ERRO: BACKUP_DB_PASSWORD não definida no .env.local.")
    print("Adicione BACKUP_DB_PASSWORD=sua-senha ao frontend/.env.local")
    sys.exit(1)


def main():
    conn = psycopg2.connect(SUPER_DB_URL, sslmode="require")
    conn.set_session(autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'backup_user'"
            )
            exists = cur.fetchone()
            if exists:
                cur.execute(
                    "ALTER ROLE backup_user WITH PASSWORD %s",
                    (BACKUP_PASSWORD,)
                )
            else:
                cur.execute(
                    "CREATE ROLE backup_user WITH LOGIN PASSWORD %s NOBYPASSRLS",
                    (BACKUP_PASSWORD,)
                )
            cur.execute("GRANT CONNECT ON DATABASE postgres TO backup_user")
            cur.execute("GRANT USAGE ON SCHEMA public TO backup_user")
            cur.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user")
            cur.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO backup_user")

            try:
                cur.execute("GRANT USAGE ON SCHEMA auth TO backup_user")
                cur.execute("GRANT SELECT ON ALL TABLES IN SCHEMA auth TO backup_user")
                cur.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA auth GRANT SELECT ON TABLES TO backup_user")
                auth_ok = True
            except Exception:
                auth_ok = False

        parsed = urlparse(SUPER_DB_URL)
        host = parsed.hostname

        print("backup_user configurado com sucesso!\n")
        print("Adicione AO .env.local e aos GitHub Secrets a linha abaixo:")
        print(f"DATABASE_URL=postgresql://backup_user:{BACKUP_PASSWORD}@{host}:5432/postgres?sslmode=require\n")

        if not auth_ok:
            print("AVISO: nao foi possivel conceder permissoes no schema `auth`.")
            print("Para incluir auth.users no backup, execute no Supabase SQL Editor:\n")
            print("    GRANT USAGE ON SCHEMA auth TO backup_user;")
            print("    GRANT SELECT ON ALL TABLES IN SCHEMA auth TO backup_user;")
            print("    ALTER DEFAULT PRIVILEGES IN SCHEMA auth GRANT SELECT ON TABLES TO backup_user;\n")
            print("Se preferir, o backup funciona apenas com as tabelas public (sem auth.users).\n")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
