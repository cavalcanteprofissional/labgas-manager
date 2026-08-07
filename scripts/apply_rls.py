"""apply_rls.py — Aplica migration de login history + policies RLS no banco vivo.

Fonte única de segurança: usa os arquivos versionados
`database/migrations/20260620_add_login_history.sql` e `database/rls.sql`
(SECURITY DEFINER, ENABLE RLS e policies dev-aware).

Requisitos:
- `DATABASE_URL_POSTGRES` (superuser) no frontend/.env.local — necessário para
  criar a tabela e as policies (backup_user é somente-leitura).

Uso:
    python scripts/apply_rls.py
    python scripts/apply_rls.py --dry-run     # mostra o SQL sem executar
"""

import argparse
import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / "frontend" / ".env.local")

SUPER_DB_URL = os.getenv("DATABASE_URL_POSTGRES") or os.getenv("DATABASE_URL")
MIGRATION_LOGIN = BASE_DIR / "database" / "migrations" / "20260620_add_login_history.sql"
RLS_SQL = BASE_DIR / "database" / "rls.sql"


def _check_table_exists(conn, tabela):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = %s",
            (tabela,),
        )
        return cur.fetchone() is not None


def main():
    parser = argparse.ArgumentParser(description="Aplica migration de login + rls.sql no banco vivo.")
    parser.add_argument("--dry-run", action="store_true", help="mostra o SQL sem executar")
    args = parser.parse_args()

    if not SUPER_DB_URL:
        print("ERRO: DATABASE_URL_POSTGRES (superuser) é obrigatória para aplicar RLS.")
        sys.exit(1)
    for arquivo, desc in ((MIGRATION_LOGIN, "migration historico_login"), (RLS_SQL, "rls.sql")):
        if not arquivo.exists():
            print(f"ERRO: {desc} não encontrado em {arquivo}")
            sys.exit(1)

    if args.dry_run:
        print("=== MIGRATION historico_login (20260620) ===")
        print(MIGRATION_LOGIN.read_text(encoding="utf-8"))
        print("\n=== RLS (database/rls.sql) ===")
        print(RLS_SQL.read_text(encoding="utf-8"))
        return

    conn = psycopg2.connect(SUPER_DB_URL, sslmode="require")
    conn.set_session(autocommit=True)
    try:
        if _check_table_exists(conn, "historico_login"):
            print("[SKIP] historico_login já existe — migration 20260620 ignorada.")
        else:
            print("[OK] Aplicando migration 20260620_add_login_history.sql...")
            conn.cursor().execute(MIGRATION_LOGIN.read_text(encoding="utf-8"))
            print("     historico_login criado (tabela + índices + policy).")

        print("[OK] Aplicando database/rls.sql (idempotente)...")
        conn.cursor().execute(RLS_SQL.read_text(encoding="utf-8"))
        print("     is_dev(), ENABLE RLS e policies recriadas.")

        print("[OK] Removendo policies legadas da tabela leitura...")
        for legada in (
            '"Users can insert amostra"',
            '"Users can update amostra"',
            '"Users can delete amostra"',
        ):
            conn.cursor().execute(
                f"DROP POLICY IF EXISTS {legada} ON leitura"
            )

        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM pg_policy p "
                "JOIN pg_class c ON c.oid = p.polrelid "
                "JOIN pg_namespace n ON n.oid = c.relnamespace "
                "WHERE n.nspname = 'public'"
            )
            print(f"[OK] Policies no schema public agora: {cur.fetchone()[0]}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
