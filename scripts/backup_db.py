"""backup_db.py — Backup lógico completo do banco LabGas Manager.

Exporta todas as tabelas `public` via PostgreSQL (`backup_user`) e
`auth.users` via Supabase Admin API (`SUPABASE_SERVICE_KEY`),
compacta em .json.gz e envia ao Cloudflare R2.

Uso:
    python scripts/backup_db.py                       # backup + upload R2
    python scripts/backup_db.py --no-upload            # só backup local
    python scripts/backup_db.py --output-dir ./tmp     # diretório customizado
    python scripts/backup_db.py --max-backups 15       # mantém só 15 backups
"""

import argparse
import gzip
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time as time_mod
import urllib.parse
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

SCHEMA_VERSION = "1.1"
MIN_DISK_MB = 50


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
            encoded = urllib.parse.quote(password, safe="")
            return f"postgresql://backup_user.{ref}:{encoded}@aws-1-us-east-2.pooler.supabase.com:5432/postgres?sslmode=require"
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
    """Remove parametros invalidos e retorna (url_limpa, hostaddr)."""
    from urllib.parse import urlparse, urlunparse, parse_qs
    import socket
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    params.pop("pgbouncer", None)
    cleaned = "&".join(f"{k}={v[0]}" for k, v in params.items()) if params else ""
    url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, cleaned, parsed.fragment))
    if not url.startswith("postgresql://"):
        return url, None
    try:
        ips = [addr[4][0] for addr in socket.getaddrinfo(parsed.hostname, parsed.port, socket.AF_INET)]
        if ips:
            return url, ips[0]
    except Exception:
        pass
    return url, None


def conectar():
    if not DB_URL:
        raise ValueError("DATABASE_URL não definida no .env.local")
    url, hostaddr = _resolver_ipv4(DB_URL)
    if hostaddr:
        conn_str = f"{url}&hostaddr={hostaddr}" if "?" in url else f"{url}?hostaddr={hostaddr}"
    else:
        conn_str = url
    return psycopg2.connect(conn_str, sslmode="require")


def _get_table_schema_hash(conn, schema, tabela):
    """Retorna SHA256 das definições de coluna (nome, tipo, nullable, default)."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """, (schema, tabela))
        cols = cur.fetchall()
    raw = json.dumps([dict(c) for c in cols], sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def pre_flight(output_dir):
    """Valida conexões e recursos antes de iniciar o backup."""
    print("--- Pre-flight checks ---")
    ok = True

    try:
        conn = conectar()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
        print("  [OK] Conexão com o banco")
    except Exception as e:
        print(f"  [FALHA] Banco de dados: {e}")
        ok = False

    if all([R2_ENDPOINT, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
        try:
            client = _init_r2_client()
            client.head_bucket(Bucket=R2_BUCKET)
            print(f"  [OK] Bucket R2: {R2_BUCKET}")
        except Exception as e:
            print(f"  [AVISO] R2: {e} — backup local apenas")
    else:
        print("  [AVISO] R2 não configurado — backup local apenas")

    free_mb = shutil.disk_usage(output_dir).free / 1024 / 1024
    if free_mb < MIN_DISK_MB:
        print(f"  [FALHA] Disco insuficiente: {free_mb:.0f} MB livres (mín {MIN_DISK_MB} MB)")
        ok = False
    else:
        print(f"  [OK] Espaço em disco: {free_mb:.0f} MB livres")

    if not ok:
        sys.exit("ERRO: Pre-flight checks falharam. Corrija os problemas acima e tente novamente.")
    print()


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


def _parse_user(u):
    ud = u.__dict__ if hasattr(u, "__dict__") else u
    return {
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
    }


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
        users.extend(_parse_user(u) for u in batch)
        page += 1
        if len(batch) < 1000:
            break
    return users


def _init_r2_client():
    if not all([R2_ENDPOINT, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
        return None
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    )


def upload_r2(local_path, remote_key):
    client = _init_r2_client()
    if not client:
        print("AVISO: R2 nao configurado — backup salvo apenas localmente.")
        return False
    client.upload_file(str(local_path), R2_BUCKET, remote_key)
    print(f"  -> Upload R2: s3://{R2_BUCKET}/{remote_key}")
    return True


def verify_upload(local_path, remote_key):
    """Verifica integridade do upload. Baixa o objeto do R2 e compara SHA256."""
    client = _init_r2_client()
    if not client:
        return False
    local_hash = compute_sha256(local_path)
    try:
        resp = client.get_object(Bucket=R2_BUCKET, Key=remote_key)
        remote_hash = hashlib.sha256(resp["Body"].read()).hexdigest()
        if local_hash != remote_hash:
            print(f"  ERRO: Hash do upload diverge!")
            print(f"    Local:  {local_hash}")
            print(f"    Remoto: {remote_hash}")
            return False
        print("  [OK] Integridade verificada pós-upload")
        return True
    except Exception as e:
        print(f"  AVISO: Não foi possível verificar integridade: {e}")
        return False


def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def download_hash_from_r2(bucket):
    client = _init_r2_client()
    if not client:
        return None
    try:
        resp = client.get_object(Bucket=bucket, Key="last_backup_hash.txt")
        return resp["Body"].read().decode("utf-8").strip()
    except Exception:
        return None


def upload_hash_to_r2(bucket, hash_value):
    client = _init_r2_client()
    if not client:
        return False
    try:
        client.put_object(Bucket=bucket, Key="last_backup_hash.txt", Body=hash_value.encode("utf-8"))
        return True
    except Exception:
        return False


def _download_table_hashes_from_r2(bucket):
    """Baixa hashes individuais por tabela do R2."""
    client = _init_r2_client()
    if not client:
        return None
    try:
        resp = client.get_object(Bucket=bucket, Key="last_backup_hashes.json")
        return json.loads(resp["Body"].read().decode("utf-8"))
    except Exception:
        return None


def _upload_table_hashes_to_r2(bucket, hashes):
    """Sobe hashes individuais por tabela para o R2."""
    client = _init_r2_client()
    if not client:
        return False
    try:
        client.put_object(
            Bucket=bucket,
            Key="last_backup_hashes.json",
            Body=json.dumps(hashes, ensure_ascii=False).encode("utf-8"),
        )
        return True
    except Exception:
        return False


def _prune_old_backups(bucket, prefix, max_keep=30):
    """Remove backups antigos do R2, mantendo apenas os max_keep mais recentes."""
    client = _init_r2_client()
    if not client:
        return
    try:
        resp = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        objs = sorted(resp.get("Contents", []), key=lambda o: o["LastModified"])
        if len(objs) <= max_keep:
            return
        to_delete = objs[:-max_keep]
        for obj in to_delete:
            client.delete_object(Bucket=bucket, Key=obj["Key"])
            print(f"  Removido backup antigo: {obj['Key']}")
        print(f"  Limpeza: {len(to_delete)} backup(s) removido(s) do R2")
    except Exception as e:
        print(f"  AVISO: Falha ao limpar backups antigos do R2: {e}")


def _run_backup():
    """Exporta todas as tabelas e retorna (backup_dict, total_rows, table_hashes, table_row_counts)."""
    conn = conectar()
    backup = {
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(UTC).isoformat(),
        "_schema": {},
        "tables": {},
    }
    total = 0
    table_hashes = {}
    table_row_counts = {}

    for tabela in PUBLIC_TABLES:
        key = f"public.{tabela}"
        print(f"  {key}...", end=" ")
        backup["_schema"][key] = _get_table_schema_hash(conn, "public", tabela)
        rows = exportar_tabela(conn, "public", tabela)
        backup["tables"][key] = rows
        table_row_counts[key] = len(rows)
        table_hashes[key] = hashlib.sha256(json.dumps(rows, sort_keys=True, default=str).encode()).hexdigest()
        print(f"{len(rows)} registros")
        total += len(rows)

    conn.close()

    print(f"  auth.users...", end=" ")
    try:
        users = exportar_auth_users()
        backup["tables"]["auth.users"] = users
        table_row_counts["auth.users"] = len(users)
        backup["_schema"]["auth.users"] = "n/a"
        table_hashes["auth.users"] = hashlib.sha256(json.dumps(users, sort_keys=True, default=str).encode()).hexdigest()
        print(f"{len(users)} registros")
        total += len(users)
    except Exception as e:
        print(f"erro: {e}")
        backup["tables"]["auth.users"] = []
        table_row_counts["auth.users"] = 0

    return backup, total, table_hashes, table_row_counts


def main():
    parser = argparse.ArgumentParser(description="Backup do LabGas Manager")
    parser.add_argument("--no-upload", action="store_true", help="Apenas backup local")
    parser.add_argument("--output-dir", default="backups", help="Diretorio local de saida")
    parser.add_argument("--check-hash", action="store_true", help="Pular backup se hash nao mudou")
    parser.add_argument("--result-file", default=".backup_result.json", help="Path do JSON de resultado")
    parser.add_argument("--max-backups", type=int, default=30, help="Maximo de backups para manter no R2 (0 = manter todos)")
    parser.add_argument("--no-pre-flight", action="store_true", help="Pular verificacoes pre-flight")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.check_hash:
        _run_backup_with_hash_check(args, output_dir)
    else:
        _run_backup_simple(args, output_dir)


def _run_backup_simple(args, output_dir):
    """Fluxo original (sem --check-hash)."""
    if not args.no_pre_flight:
        pre_flight(output_dir)

    start = time_mod.monotonic()
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"labgas_backup_{timestamp}.json.gz"
    local_path = output_dir / filename

    print("Conectando ao banco...")
    backup, total, table_hashes, table_row_counts = _run_backup()

    print(f"\nComprimindo -> {local_path}")
    with gzip.open(local_path, "wt", encoding="utf-8") as f:
        json.dump(backup, f, ensure_ascii=False, default=str)

    size_mb = local_path.stat().st_size / 1024 / 1024
    duration = time_mod.monotonic() - start
    print(f"  Tamanho: {size_mb:.2f} MB ({total} registros)")
    print(f"  Duracao: {duration:.1f}s")

    if not args.no_upload:
        remote_key = f"labgas_backup_{timestamp}.json.gz"
        upload_r2(local_path, remote_key)

    print("\nBackup concluido com sucesso!")


def _run_backup_with_hash_check(args, output_dir):
    """Fluxo com --check-hash: compara SHA256, pula se inalterado."""
    result = {"status": "error", "reason": "unknown"}

    if not args.no_pre_flight:
        pre_flight(output_dir)

    try:
        start = time_mod.monotonic()
        print("Conectando ao banco...")
        backup, total, table_hashes, table_row_counts = _run_backup()

        with tempfile.NamedTemporaryFile(suffix=".json.gz", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            with gzip.open(tmp_path, "wt", encoding="utf-8") as f:
                json.dump(backup, f, ensure_ascii=False, default=str)

        current_hash = compute_sha256(tmp_path)
        size_mb = tmp_path.stat().st_size / 1024 / 1024
        duration = time_mod.monotonic() - start
        print(f"  SHA256: {current_hash}")
        print(f"  Tamanho: {size_mb:.2f} MB ({total} registros)")
        print(f"  Duracao: {duration:.1f}s")

        previous_table_hashes = _download_table_hashes_from_r2(R2_BUCKET)
        previous_full_hash = download_hash_from_r2(R2_BUCKET)

        if previous_full_hash == current_hash:
            print("\nNenhuma alteracao detectada — backup pulado.")
            tmp_path.unlink()
            result = {
                "status": "skipped",
                "reason": "no changes",
                "hash": current_hash,
                "duration_sec": round(duration, 2),
            }
            _write_result(args.result_file, result)
            return

        changed_tables = []
        if previous_table_hashes:
            for key, h in table_hashes.items():
                if previous_table_hashes.get(key) != h:
                    changed_tables.append(key)
            if not changed_tables and total > 0:
                print("\n  Tabelas individualmente inalteradas — pulando.")
                tmp_path.unlink()
                result = {
                    "status": "skipped",
                    "reason": "no table-level changes",
                    "hash": current_hash,
                    "table_hashes": table_hashes,
                    "duration_sec": round(duration, 2),
                }
                _write_result(args.result_file, result)
                return

        timestamp = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"labgas_backup_{timestamp}.json.gz"
        local_path = output_dir / filename
        tmp_path.rename(local_path)
        print(f"\nSalvo -> {local_path}")
        if changed_tables:
            print(f"  Tabelas alteradas: {', '.join(changed_tables)}")

        if not args.no_upload:
            remote_key = f"labgas_backup_{timestamp}.json.gz"
            upload_r2(local_path, remote_key)
            verify_upload(local_path, remote_key)
            upload_hash_to_r2(R2_BUCKET, current_hash)
            _upload_table_hashes_to_r2(R2_BUCKET, table_hashes)
            print("  Hash atualizado no R2.")
            if args.max_backups > 0:
                _prune_old_backups(R2_BUCKET, "labgas_backup_", args.max_backups)

        compression_ratio = round(size_mb / (local_path.stat().st_size / 1024 / 1024) if size_mb > 0 else 0, 2)

        result = {
            "status": "uploaded",
            "filename": str(local_path),
            "timestamp": timestamp,
            "hash": current_hash,
            "size_mb": round(size_mb, 2),
            "duration_sec": round(duration, 2),
            "total_rows": total,
            "tables": table_row_counts,
            "changed_tables": changed_tables,
        }
        _write_result(args.result_file, result)
        print("\nBackup concluido com sucesso!")
    except Exception as e:
        result = {"status": "error", "reason": str(e)}
        _write_result(args.result_file, result)
        print(f"\nERRO: {e}", file=sys.stderr)
        sys.exit(1)


def _write_result(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
