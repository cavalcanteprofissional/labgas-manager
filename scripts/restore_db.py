"""restore_db.py — Restaura backup do LabGas Manager.

Restaura `auth.users` via Supabase Admin API e tabelas `public`
via PostgreSQL direto (backup_user).

Uso:
    python scripts/restore_db.py --list                # lista backups no R2
    python scripts/restore_db.py --latest --dry-run    # preview do restore
    python scripts/restore_db.py --latest              # restaura backup mais recente
    python scripts/restore_db.py --file backup.json.gz # arquivo local
"""

import argparse
import gzip
import json
import os
import re
import sys
from pathlib import Path

import boto3
import psycopg2
from dotenv import load_dotenv
from supabase import create_client

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / "frontend" / ".env.local")


def _obter_db_url():
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    supabase_url = os.getenv("SUPABASE_URL")
    password = os.getenv("BACKUP_DB_PASSWORD")
    if supabase_url and password:
        match = re.search(r"https?://([^.]+)\.supabase\.co", supabase_url)
        if match:
            ref = match.group(1)
            return f"postgresql://backup_user:{password}@db.{ref}.supabase.co:5432/postgres?sslmode=require"
    return None


DB_URL = _obter_db_url()
R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET = os.getenv("R2_BUCKET_NAME", "labgas-backups")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

DELETE_ORDER = [
    "amostra_elemento",
    "leitura",
    "pressao",
    "amostra",
    "cilindro",
    "elemento",
    "historico_log",
    "perfil",
]

INSERT_ORDER = [
    "auth.users",
    "public.perfil",
    "public.elemento",
    "public.cilindro",
    "public.amostra",
    "public.amostra_elemento",
    "public.leitura",
    "public.pressao",
    "public.historico_log",
]


def _resolver_ipv4(url):
    """Resolve hostname para IPv4, contornando problemas de IPv6 no runner."""
    from urllib.parse import urlparse
    import socket
    parsed = urlparse(url)
    try:
        ips = [addr[4][0] for addr in socket.getaddrinfo(parsed.hostname, parsed.port, socket.AF_INET)]
        if ips:
            return url.replace(parsed.hostname, ips[0])
    except Exception:
        pass
    return url


def conectar():
    if not DB_URL:
        sys.exit("ERRO: DATABASE_URL nao definida no .env.local")
    ipv4_url = _resolver_ipv4(DB_URL)
    return psycopg2.connect(ipv4_url, sslmode="require")


def listar_backups():
    if not all([R2_ENDPOINT, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
        sys.exit("ERRO: R2 nao configurado (variaveis de ambiente)")
    client = boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    )
    resp = client.list_objects_v2(Bucket=R2_BUCKET, Prefix="labgas_backup_")
    objs = resp.get("Contents", [])
    if not objs:
        print("Nenhum backup encontrado no R2.")
        return
    for obj in sorted(objs, key=lambda o: o["LastModified"], reverse=True):
        size_mb = obj["Size"] / 1024 / 1024
        print(f"  {obj['Key']:50s} {size_mb:.2f} MB  {obj['LastModified']}")


def baixar_backup(remote_key, dest_dir="backups"):
    dest = Path(dest_dir) / remote_key
    dest.parent.mkdir(parents=True, exist_ok=True)
    client = boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    )
    print(f"Baixando {remote_key}...")
    client.download_file(R2_BUCKET, remote_key, str(dest))
    return dest


def carregar_backup(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def confirmar():
    print("\nATENCAO: Isso ira SOBRESCREVER todos os dados atuais!")
    print("  - Dados existentes serao DELETADOS")
    resp = input("\nDigite 'RESTAURAR' para confirmar: ")
    if resp.strip() != "RESTAURAR":
        print("Restauracao cancelada.")
        sys.exit(0)


def deletar_dados(conn):
    print("\nLimpando dados atuais...")
    with conn.cursor() as cur:
        for tabela in DELETE_ORDER:
            cur.execute(f'DELETE FROM public."{tabela}"')
            print(f"  public.{tabela}: {cur.rowcount} registros deletados")
    conn.commit()


def colunas_para_sql(rows):
    if not rows:
        return "", "", "", ""
    colunas = list(rows[0].keys())
    cols_str = ", ".join(f'"{c}"' for c in colunas)
    placeholders = ", ".join(f"%({c})s" for c in colunas)
    update_cols = ", ".join(
        f'"{c}" = EXCLUDED."{c}"' for c in colunas if c not in ("id", "id",)
    )
    return colunas, cols_str, placeholders, update_cols


def restaurar_tabela(conn, schema, tabela, rows):
    if not rows:
        print(f"  {schema}.{tabela}: 0 registros — pulando")
        return

    colunas, cols_str, placeholders, update_cols = colunas_para_sql(rows)

    sql = f"""
        INSERT INTO {schema}."{tabela}" ({cols_str})
        VALUES ({placeholders})
        ON CONFLICT ("id") DO UPDATE SET {update_cols}
    """

    with conn.cursor() as cur:
        cur.executemany(sql, rows)
    conn.commit()
    print(f"  {schema}.{tabela}: {len(rows)} registros restaurados")


def restaurar_auth_users(rows):
    if not rows:
        print("  auth.users: 0 registros — pulando")
        return

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("  auth.users: SUPABASE_SERVICE_KEY nao configurada — pulando")
        return

    client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    criados = 0
    atualizados = 0
    sem_senha = 0

    for row in rows:
        user_id = row.get("id")
        email = row.get("email", "")
        meta = row.get("raw_user_meta_data") or {}
        app_meta = row.get("raw_app_meta_data") or {}

        try:
            info = client.auth.admin.get_user_by_id(user_id)
            if info and getattr(info, "user", None):
                client.auth.admin.update_user_by_id(user_id, {
                    "email": email,
                    "user_metadata": meta,
                    "app_metadata": app_meta,
                })
                atualizados += 1
                continue
        except Exception:
            pass

        try:
            import secrets
            temp_pass = secrets.token_urlsafe(12)
            client.auth.admin.create_user({
                "email": email,
                "password": temp_pass,
                "email_confirm": True,
                "user_metadata": meta,
                "app_metadata": app_meta,
            })
            criados += 1
            sem_senha += 1
            print(f"    Usuario {email} criado com senha temporaria — redefina pelo login")
        except Exception as e:
            print(f"    Erro ao restaurar {email}: {e}")

    print(f"  auth.users: {len(rows)} processados ({atualizados} atualizados, {criados} criados)")


def main():
    parser = argparse.ArgumentParser(description="Restaura backup do LabGas Manager")
    parser.add_argument("--list", action="store_true", help="Listar backups no R2")
    parser.add_argument("--file", help="Arquivo de backup local (.json.gz)")
    parser.add_argument("--latest", action="store_true", help="Usar backup mais recente do R2")
    parser.add_argument("--dry-run", action="store_true", help="Apenas mostrar preview sem alterar dados")
    args = parser.parse_args()

    if args.list:
        listar_backups()
        return

    if not args.file and not args.latest:
        parser.print_help()
        sys.exit("Use --file, --latest ou --list")

    if args.latest:
        if not all([R2_ENDPOINT, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
            sys.exit("ERRO: R2 nao configurado (variaveis de ambiente)")
        client = boto3.client(
            "s3",
            endpoint_url=R2_ENDPOINT,
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        )
        resp = client.list_objects_v2(Bucket=R2_BUCKET, Prefix="labgas_backup_")
        objs = sorted(resp.get("Contents", []), key=lambda o: o["LastModified"], reverse=True)
        if not objs:
            sys.exit("Nenhum backup disponivel no R2.")
        remote_key = objs[0]["Key"]
        local_path = baixar_backup(remote_key)
    else:
        local_path = Path(args.file)
        if not local_path.exists():
            sys.exit(f"Arquivo nao encontrado: {local_path}")

    backup = carregar_backup(local_path)
    print(f"\nBackup criado em: {backup['created_at']}")
    print(f"Tabelas no backup: {len(backup['tables'])}\n")

    for tbl_key, rows in backup["tables"].items():
        print(f"  {tbl_key}: {len(rows)} registros")

    if args.dry_run:
        print("\nDry-run — nenhuma alteracao foi feita.")
        return

    confirmar()

    conn = conectar()
    try:
        deletar_dados(conn)
        print("\nRestaurando dados...")
        for tbl_key in INSERT_ORDER:
            rows = backup["tables"].get(tbl_key, [])
            if tbl_key == "auth.users":
                restaurar_auth_users(rows)
            else:
                schema, tabela = tbl_key.split(".", 1)
                restaurar_tabela(conn, schema, tabela, rows)
    finally:
        conn.close()

    print("\nRestauracao concluida com sucesso!")


if __name__ == "__main__":
    main()
