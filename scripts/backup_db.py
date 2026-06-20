"""backup_db.py — Backup lógico completo do banco LabGas Manager.

Exporta todas as tabelas `public` via PostgreSQL (`backup_user`) e
`auth.users` via Supabase Admin API (`SUPABASE_SERVICE_KEY`),
compacta em .json.gz e envia ao Cloudflare R2.

Uso:
    python scripts/backup_db.py                       # backup + upload R2
    python scripts/backup_db.py --no-upload            # só backup local
    python scripts/backup_db.py --output-dir ./tmp     # diretório customizado
"""

import argparse
import gzip
import json
import os
import re
import sys
from datetime import datetime, date, time, timedelta, UTC
from decimal import Decimal
from pathlib import Path
from uuid import UUID

import boto3
import psycopg2
import psycopg2.extras
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

PUBLIC_TABLES = [
    "perfil",
    "elemento",
    "cilindro",
    "amostra",
    "amostra_elemento",
    "leitura",
    "pressao",
    "historico_log",
]


def _resolver_ipv4(url):
    """Remove parametros invalidos e resolve hostname para IPv4."""
    from urllib.parse import urlparse, urlunparse, parse_qs
    import socket
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    params.pop("pgbouncer", None)
    cleaned = "&".join(f"{k}={v[0]}" for k, v in params.items()) if params else ""
    url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, cleaned, parsed.fragment))
    if not url.startswith("postgresql://"):
        return url
    try:
        ips = [addr[4][0] for addr in socket.getaddrinfo(parsed.hostname, parsed.port, socket.AF_INET)]
        if ips:
            url = url.replace(parsed.hostname, ips[0])
    except Exception:
        pass
    return url


def conectar():
    if not DB_URL:
        sys.exit("ERRO: DATABASE_URL não definida no .env.local")
    ipv4_url = _resolver_ipv4(DB_URL)
    return psycopg2.connect(ipv4_url, sslmode="require")


def exportar_tabela(conn, schema, tabela):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f'SELECT * FROM {schema}."{tabela}"')
        rows = cur.fetchall()
        return [serializar(dict(r)) for r in rows]


def serializar(row):
    out = {}
    for k, v in row.items():
        if v is None:
            out[k] = None
        elif isinstance(v, (datetime, date)):
            out[k] = v.isoformat()
        elif isinstance(v, time):
            out[k] = v.isoformat()
        elif isinstance(v, timedelta):
            out[k] = str(v)
        elif isinstance(v, Decimal):
            out[k] = float(v)
        elif isinstance(v, UUID):
            out[k] = str(v)
        elif isinstance(v, (bytes, memoryview)):
            out[k] = v.hex() if isinstance(v, bytes) else bytes(v).hex()
        elif isinstance(v, dict):
            out[k] = {sk: serializar_valor(sv) for sk, sv in v.items()}
        elif isinstance(v, list):
            out[k] = [serializar_valor(i) for i in v]
        else:
            out[k] = v
    return out


def serializar_valor(v):
    if isinstance(v, (datetime, date, time, timedelta)):
        return v.isoformat()
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, UUID):
        return str(v)
    if isinstance(v, (bytes, memoryview)):
        return v.hex() if isinstance(v, bytes) else bytes(v).hex()
    return v


def exportar_auth_users():
    """Exporta auth.users via Supabase Admin API (fallback quando
    o backup_user nao tem SELECT no schema auth)."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("sem credenciais — pulando")
        return []
    client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    page = 0
    users = []
    while True:
        resp = client.auth.admin.list_users(page=page, per_page=1000)
        batch = getattr(resp, "users", resp) if not isinstance(resp, dict) else resp.get("users", [])
        if not batch:
            break
        for u in batch:
            ud = u.__dict__ if hasattr(u, "__dict__") else u
            users.append({
                "id": str(ud.get("id", "")),
                "email": ud.get("email"),
                "phone": ud.get("phone"),
                "created_at": ud.get("created_at"),
                "last_sign_in_at": ud.get("last_sign_in_at"),
                "confirmed_at": ud.get("confirmed_at"),
                "email_confirmed_at": ud.get("email_confirmed_at"),
                "is_sso_user": ud.get("is_sso_user", False),
                "banned_until": ud.get("banned_until"),
                "raw_app_meta_data": ud.get("raw_app_meta_data"),
                "raw_user_meta_data": ud.get("raw_user_meta_data"),
            })
        page += 1
        if len(batch) < 1000:
            break
    return users


def upload_r2(local_path, remote_key):
    if not all([R2_ENDPOINT, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
        print("AVISO: R2 nao configurado — backup salvo apenas localmente.")
        return False
    client = boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    )
    client.upload_file(str(local_path), R2_BUCKET, remote_key)
    print(f"  -> Upload R2: s3://{R2_BUCKET}/{remote_key}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Backup do LabGas Manager")
    parser.add_argument("--no-upload", action="store_true", help="Apenas backup local")
    parser.add_argument("--output-dir", default="backups", help="Diretorio local de saida")
    args = parser.parse_args()

    timestamp = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"labgas_backup_{timestamp}.json.gz"
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    local_path = output_dir / filename

    print("Conectando ao banco...")
    conn = conectar()

    backup = {
        "version": "1.0",
        "created_at": datetime.now(UTC).isoformat(),
        "tables": {},
    }

    total = 0
    for tabela in PUBLIC_TABLES:
        print(f"  public.{tabela}...", end=" ")
        rows = exportar_tabela(conn, "public", tabela)
        backup["tables"][f"public.{tabela}"] = rows
        print(f"{len(rows)} registros")
        total += len(rows)

    conn.close()

    print(f"  auth.users...", end=" ")
    try:
        users = exportar_auth_users()
        backup["tables"]["auth.users"] = users
        print(f"{len(users)} registros")
        total += len(users)
    except Exception as e:
        print(f"erro: {e}")
        backup["tables"]["auth.users"] = []

    print(f"\nComprimindo -> {local_path}")
    with gzip.open(local_path, "wt", encoding="utf-8") as f:
        json.dump(backup, f, ensure_ascii=False, default=str)

    size_mb = local_path.stat().st_size / 1024 / 1024
    print(f"  Tamanho: {size_mb:.2f} MB ({total} registros)")

    if not args.no_upload:
        remote_key = f"labgas_backup_{timestamp}.json.gz"
        upload_r2(local_path, remote_key)

    print("\nBackup concluido com sucesso!")


if __name__ == "__main__":
    main()
