opencode# Plano de Migração: Supabase → PostgreSQL Local + Auth Customizado

**Projeto:** LabGas Manager
**Data:** Julho 2026
**TVBox:** Armbian (ARM64)
**DNS:** DuckDNS
**Tunnel:** Cloudflare Tunnel

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Fase 0: Setup TVBox Armbian](#2-fase-0-setup-tvbox-armbian)
3. [Fase 1: Banco de Dados Local](#3-fase-1-banco-de-dados-local)
4. [Fase 2: Camada de Banco (db_utils.py)](#4-fase-2-camada-de-banco-db_utilspy)
5. [Fase 3: Auth Customizado](#5-fase-3-auth-customizado)
6. [Fase 4: Migrar Blueprints](#6-fase-4-migrar-blueprints)
7. [Fase 5: Backend API](#7-fase-5-backend-api)
8. [Fase 6: Deploy na TVBox](#8-fase-6-deploy-na-tvbox)
9. [Fase 7: Backup Local](#9-fase-7-backup-local)

---

## 1. Visão Geral

### Stack Atual (Supabase)

```
Frontend (Flask) ─── supabase SDK ─── Supabase Cloud
                                        ├── Auth (sign_in_with_password, etc.)
                                        ├── PostgreSQL (auth.users + 8 tables)
                                        └── RLS (auth.uid())
                     ─── psycopg2 ───── Supabase PostgreSQL (backup)
Backend (Flask)  ─── supabase SDK ─── Supabase Cloud (Auth + DB)
```

### Stack Futura (Local)

```
Frontend (Flask) ─── psycopg2 (db_utils.py) ─── PostgreSQL Local (TVBox)
                    └── werkzeug.security ────── users table (password_hash)
Backend (Flask)  ─── psycopg2 ────────────────── PostgreSQL Local
                                          Tunnel Cloudflare ← DuckDNS → Internet
```

### O que muda

| Componente | Antes (Supabase) | Depois (Local) |
|---|---|---|
| Auth login | `supabase.auth.sign_in_with_password()` | `check_password_hash()` + SELECT users |
| Auth register | `supabase.auth.sign_up()` | `generate_password_hash()` + INSERT users |
| Auth logout | `supabase.auth.sign_out()` | `session.clear()` + `logout_user()` |
| Queries | `.table("X").select().eq().execute()` | `db_select("X", where={...})` |
| Inserts | `.table("X").insert({...}).execute()` | `db_insert("X", {...})` |
| Updates | `.table("X").update({...}).eq().execute()` | `db_update("X", {...}, where={...})` |
| Deletes | `.table("X").delete().eq().execute()` | `db_delete("X", where={...})` |
| Schema users | `auth.users` (gerenciado pelo Supabase) | `users` table local |
| RLS | `auth.uid()` policies | Validação via `user_id` na aplicação (já existe) |
| JWT (backend) | `python-jose` + `SUPABASE_JWT_SECRET` | `python-jose` + `SECRET_KEY` (já é custom) |
| Deploy | Vercel | TVBox + Gunicorn + Systemd |
| DNS | — | DuckDNS (cron update) |
| TLS | Vercel automático | Cloudflare Tunnel |
| Dependência | `supabase>=2.0.0` | Removida |

---

## 2. Fase 0: Setup TVBox Armbian

### 2.1 Sistema Base

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências do sistema
sudo apt install -y \
    python3 python3-pip python3-venv \
    postgresql postgresql-contrib \
    git curl wget \
    nginx \
    cron

# Instalar Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

### 2.2 PostgreSQL

```bash
# Verificar versão
psql --version

# Iniciar PostgreSQL
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Criar database e usuário
sudo -u postgres psql
```

```sql
-- No psql:
CREATE USER labgas_user WITH PASSWORD 'senha_forte_aqui';
CREATE DATABASE labgas_db OWNER labgas_user;
GRANT ALL PRIVILEGES ON DATABASE labgas_db TO labgas_user;
\c labgas_db
GRANT ALL ON SCHEMA public TO labgas_user;
```

### 2.3 DuckDNS

```bash
# Criar script de update
sudo mkdir -p /opt/duckdns
sudo tee /opt/duckdns/duck.sh << 'EOF'
#!/bin/bash
echo url="https://www.duckdns.org/update?domains=SEU_DOMINIO&token=SEU_TOKEN&ip=" | curl -k -o /opt/duckdns/duck.log -K -
EOF

sudo chmod 700 /opt/duckdns/duck.sh

# Adicionar ao cron (a cada 5 minutos)
crontab -e
*/5 * * * * /opt/duckdns/duck.sh >/dev/null 2>&1
```

### 2.4 Cloudflare Tunnel

```bash
# Baixar cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Autenticar (abre URL no navegador)
cloudflared tunnel login

# Criar tunnel
cloudflared tunnel create labgas-tunnel

# Configurar DNS
cloudflared tunnel route dns labgas-tunnel seu-dominio.duckdns.org

# Criar config
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: ID_DO_TUNNEL
credentials-file: /root/.cloudflared/ID_DO_TUNNEL.json

ingress:
  - hostname: seu-dominio.duckdns.org
    service: http://localhost:8000
  - service: http_status:404
EOF

# Instalar como serviço
sudo cloudflared service install

# Verificar
sudo systemctl status cloudflared
```

### 2.5 Clonar o Projeto

```bash
git clone https://github.com/SEU_USUARIO/labgas-manager.git /opt/labgas-manager
cd /opt/labgas-manager
poetry install --no-dev
```

---

## 3. Fase 1: Banco de Dados Local

### 3.1 Schema Local (`database/schema_local.sql`)

```sql
-- =====================================================
-- SCHEMA LOCAL - LabGas Manager (sem Supabase)
-- =====================================================

-- Tabela: users (substitui auth.users do Supabase)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nome VARCHAR(100),
    email_confirmed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela: perfil
CREATE TABLE perfil (
    id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'usuario' CHECK (role IN ('dev', 'admin', 'usuario')),
    ativo BOOLEAN DEFAULT true,
    nome VARCHAR(100),
    email VARCHAR(255),
    habilitar_abas JSONB DEFAULT '{"cilindro": true, "elemento": true, "leitura": true, "amostra": true, "historico": true}',
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_perfil_role ON perfil(role);
CREATE INDEX idx_perfil_role_ativo ON perfil(role, ativo);

-- Tabela: cilindro
CREATE TABLE cilindro (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL,
    data_compra DATE NOT NULL,
    data_inicio_consumo DATE,
    data_fim DATE,
    gas_kg NUMERIC(6,2) DEFAULT 1.0,
    litros_equivalentes NUMERIC(10,3) DEFAULT 956.0,
    custo NUMERIC(10,2) DEFAULT 290.00,
    status VARCHAR(20) DEFAULT 'ativo',
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_cilindro_user_id ON cilindro(user_id);
CREATE INDEX idx_cilindro_codigo ON cilindro(codigo);

-- Tabela: elemento
CREATE TABLE elemento (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    consumo_lpm NUMERIC(5,2) NOT NULL,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_elemento_user_id ON elemento(user_id);
CREATE INDEX idx_elemento_nome ON elemento(nome);

-- Tabela: pressao
CREATE TABLE pressao (
    id SERIAL PRIMARY KEY,
    cilindro_id INTEGER REFERENCES cilindro(id) ON DELETE CASCADE,
    pressao NUMERIC(5,2) NOT NULL,
    temperatura NUMERIC(5,2),
    data DATE NOT NULL,
    hora TIME NOT NULL,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pressao_user_id ON pressao(user_id);
CREATE INDEX idx_pressao_cilindro_id ON pressao(cilindro_id);
CREATE INDEX idx_pressao_data ON pressao(data);

-- Tabela: leitura
CREATE TABLE leitura (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    tempo_chama VARCHAR(8) NOT NULL,
    cilindro_id INTEGER REFERENCES cilindro(id) ON DELETE CASCADE,
    elemento_id INTEGER REFERENCES elemento(id) ON DELETE CASCADE,
    quantidade INTEGER DEFAULT 1,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_leitura_user_id ON leitura(user_id);
CREATE INDEX idx_leitura_cilindro_id ON leitura(cilindro_id);
CREATE INDEX idx_leitura_elemento_id ON leitura(elemento_id);
CREATE INDEX idx_leitura_data ON leitura(data);

-- Tabela: historico_auditoria (antiga historico_log)
CREATE TABLE historico_auditoria (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL,
    acao VARCHAR(20) NOT NULL CHECK (acao IN ('criado', 'atualizado', 'excluido')),
    ref_id INTEGER,
    label VARCHAR(150) NOT NULL,
    detalhe JSONB,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_historico_aud_tipo ON historico_auditoria(tipo);
CREATE INDEX idx_historico_aud_user_id ON historico_auditoria(user_id);
CREATE INDEX idx_historico_aud_created_at ON historico_auditoria(created_at);
CREATE INDEX idx_historico_aud_ref ON historico_auditoria(tipo, ref_id);

-- Tabela: amostra
CREATE TABLE amostra (
    id SERIAL PRIMARY KEY,
    numero_amostra INTEGER NOT NULL,
    lote INTEGER NOT NULL,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(numero_amostra, user_id)
);

CREATE INDEX idx_amostra_user_id ON amostra(user_id);
CREATE INDEX idx_amostra_lote ON amostra(lote);
CREATE INDEX idx_amostra_lote_created ON amostra(lote, created_at DESC);

-- Tabela: amostra_elemento (relação N:N)
CREATE TABLE amostra_elemento (
    id SERIAL PRIMARY KEY,
    amostra_id INTEGER REFERENCES amostra(id) ON DELETE CASCADE,
    elemento_id INTEGER REFERENCES elemento(id) ON DELETE CASCADE,
    UNIQUE(amostra_id, elemento_id)
);

CREATE INDEX idx_amostra_elemento_amostra_id ON amostra_elemento(amostra_id);
CREATE INDEX idx_amostra_elemento_elemento_id ON amostra_elemento(elemento_id);

-- Tabela: historico_login
CREATE TABLE historico_login (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    ip VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_historico_login_user_id ON historico_login(user_id);
CREATE INDEX idx_historico_login_created_at ON historico_login(created_at);
```

### 3.2 Migrar Dados do Supabase

Usar `scripts/backup_db.py` para extrair dados atuais do Supabase:

```bash
# No ambiente atual (com acesso ao Supabase)
python scripts/backup_db.py
# Gera: backups/labgas_backup_AAAAMMDD_HHMMSS.json.gz
```

Depois, criar script `scripts/migrate_to_local.py`:

```python
"""
migrate_to_local.py — Migra dados do backup Supabase para PostgreSQL local.

Uso:
    python scripts/migrate_to_local.py --backup backups/labgas_backup_*.json.gz
"""

import gzip
import json
import os
import secrets
from pathlib import Path

import psycopg2
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "labgas_db")
DB_USER = os.getenv("DB_USER", "labgas_user")
DB_PASS = os.getenv("DB_PASSWORD")


def conectar():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )


def migrar(backup_path):
    with gzip.open(backup_path, "rt") as f:
        data = json.load(f)

    conn = conectar()
    cur = conn.cursor()

    # 1. Migrar auth.users → users (com senha temporária)
    users_supabase = data["tables"].get("auth.users", [])
    user_id_map = {}

    for u in users_supabase:
        uid = u["id"]
        email = u["email"]
        nome = (u.get("raw_user_meta_data") or {}).get("nome", "")
        temp_pass = secrets.token_urlsafe(12)
        password_hash = generate_password_hash(temp_pass)

        cur.execute("""
            INSERT INTO users (id, email, password_hash, nome, email_confirmed_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET email=EXCLUDED.email
        """, (uid, email, password_hash, nome, u.get("email_confirmed_at") or "NOW()"))

        user_id_map[uid] = temp_pass
        print(f"  User {email}: senha temporária = {temp_pass}")

    conn.commit()

    # 2. Migrar tabelas public (na ordem correta)
    INSERT_ORDER = [
        "public.perfil", "public.elemento", "public.cilindro",
        "public.amostra", "public.amostra_elemento",
        "public.leitura", "public.pressao", "public.historico_auditoria"
    ]

    for tbl_key in INSERT_ORDER:
        rows = data["tables"].get(tbl_key, [])
        if not rows:
            continue

        schema, tabela = tbl_key.split(".", 1)
        colunas = list(rows[0].keys())
        cols_str = ", ".join(f'"{c}"' for c in colunas)
        placeholders = ", ".join(f"%({c})s" for c in colunas)

        sql = f'INSERT INTO {schema}."{tabela}" ({cols_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING'
        cur.executemany(sql, rows)
        conn.commit()
        print(f"  {tbl_key}: {len(rows)} registros")

    conn.close()
    print("\nMigração concluída!")
    print("AVISO: Anote as senhas temporárias acima. Usuários precisarão redefinir.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", required=True)
    args = parser.parse_args()
    migrar(args.backup)
```

---

## 4. Fase 2: Camada de Banco (db_utils.py)

**Criar:** `frontend/utils/db_utils.py`

```python
"""
db_utils.py — Camada de acesso a PostgreSQL local.
Substitui o Supabase SDK em toda a aplicação.
"""
import os
from contextlib import contextmanager
import psycopg2
import psycopg2.pool
from psycopg2.extras import RealDictCursor
from flask import has_request_context, g

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "labgas_db"),
    "user": os.getenv("DB_USER", "labgas_user"),
    "password": os.getenv("DB_PASSWORD", ""),
}

_pool = None


def get_pool():
    global _pool
    if _pool is None:
        _pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=2, maxconn=10, **DB_CONFIG
        )
    return _pool


@contextmanager
def get_db():
    if has_request_context():
        if not hasattr(g, "_db_conn"):
            g._db_conn = get_pool().getconn()
        yield g._db_conn
    else:
        conn = get_pool().getconn()
        try:
            yield conn
        finally:
            get_pool().putconn(conn)


def db_select(table, columns=None, where=None, order=None, limit=None, offset=None):
    """SELECT genérico.
    
    Exemplo:
        db_select("cilindro", where={"user_id": uid}, order="codigo")
        db_select("leitura", columns=["id", "data"], where={"elemento_id": 5}, limit=10)
    """
    cols = ", ".join(columns) if columns else "*"
    sql = f"SELECT {cols} FROM {table}"
    params = []

    if where:
        clauses = []
        for k, v in where.items():
            if isinstance(v, (list, tuple)):
                placeholders = ", ".join(["%s"] * len(v))
                clauses.append(f'"{k}" IN ({placeholders})')
                params.extend(v)
            else:
                clauses.append(f'"{k}" = %s')
                params.append(v)
        sql += " WHERE " + " AND ".join(clauses)

    if order:
        sql += f" ORDER BY {order}"

    if limit:
        sql += f" LIMIT {limit}"

    if offset:
        sql += f" OFFSET {offset}"

    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def db_get(table, columns=None, where=None, order=None):
    """Retorna um único registro ou None."""
    rows = db_select(table, columns=columns, where=where, order=order, limit=1)
    return rows[0] if rows else None


def db_insert(table, data, returning=None):
    """INSERT genérico.
    
    Exemplo:
        db_insert("perfil", {"id": uid, "role": "usuario", "email": email})
    """
    colunas = list(data.keys())
    valores = [data[c] for c in colunas]
    cols_str = ", ".join(f'"{c}"' for c in colunas)
    placeholders = ", ".join(["%s"] * len(valores))

    sql = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"
    
    if returning:
        sql += f" RETURNING {', '.join(returning)}"

    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, valores)
            conn.commit()
            if returning:
                return cur.fetchone()
    return None


def db_update(table, data, where):
    """UPDATE genérico.
    
    Exemplo:
        db_update("cilindro", {"status": "esgotado"}, where={"id": 5, "user_id": uid})
    """
    set_clauses = [f'"{k}" = %s' for k in data.keys()]
    valores = list(data.values())

    where_clauses = []
    for k, v in where.items():
        where_clauses.append(f'"{k}" = %s')
        valores.append(v)

    sql = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, valores)
            conn.commit()
            return cur.rowcount


def db_delete(table, where):
    """DELETE genérico.
    
    Exemplo:
        db_delete("pressao", where={"id": 10})
    """
    clauses = []
    valores = []
    for k, v in where.items():
        if isinstance(v, (list, tuple)):
            placeholders = ", ".join(["%s"] * len(v))
            clauses.append(f'"{k}" IN ({placeholders})')
            valores.extend(v)
        else:
            clauses.append(f'"{k}" = %s')
            valores.append(v)

    sql = f"DELETE FROM {table} WHERE {' AND '.join(clauses)}"

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, valores)
            conn.commit()
            return cur.rowcount


def db_count(table, where=None):
    """COUNT genérico."""
    sql = f"SELECT COUNT(*) as total FROM {table}"
    params = []

    if where:
        clauses = []
        for k, v in where.items():
            clauses.append(f'"{k}" = %s')
            params.append(v)
        sql += " WHERE " + " AND ".join(clauses)

    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchone()["total"]


def db_raw(sql, params=None, fetch=True):
    """SQL raw para consultas complexas."""
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params or [])
            conn.commit()
            if fetch and cur.description:
                return cur.fetchall()
            return None
```

### Padrão de Substituição

**Antes (Supabase):**
```python
supabase.table("cilindro").select("id,codigo,status").eq("user_id", uid).execute().data
```

**Depois (db_utils):**
```python
db_select("cilindro", columns=["id","codigo","status"], where={"user_id": uid})
```

---

## 5. Fase 3: Auth Customizado

### 5.1 Auth Blueprint (`frontend/blueprints/auth.py`)

```python
# Substituir:

# ANTES (login):
supabase = get_supabase_client()
response = supabase.auth.sign_in_with_password({
    "email": email, "password": password
})

# DEPOIS (login):
user = db_get("users", where={"email": email})
if user and check_password_hash(user["password_hash"], password):
    # login OK
    session["user_id"] = user["id"]
    ...
else:
    flash("Email ou senha inválidos.", "danger")
```

```python
# ANTES (register):
response = supabase.auth.sign_up({
    "email": email, "password": password,
    "options": {"data": {"nome": nome}}
})

# DEPOIS (register):
existing = db_get("users", where={"email": email})
if existing:
    flash("Email já cadastrado.", "danger")
else:
    password_hash = generate_password_hash(password)
    user = db_insert("users", {
        "id": str(uuid.uuid4()),
        "email": email,
        "password_hash": password_hash,
        "nome": nome,
        "email_confirmed_at": datetime.utcnow().isoformat()
    }, returning=["id"])
    
    db_insert("perfil", {
        "id": user["id"], "role": "usuario",
        "ativo": True, "nome": nome, "email": email,
        "habilitar_abas": {...}
    })
```

```python
# ANTES (logout):
supabase.auth.sign_out()

# DEPOIS (logout):
# Só limpar sessão (já faz)
session.clear()
logout_user()
```

### 5.2 Env vars mudam

**Antes (.env.local):**
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx
SUPABASE_JWT_SECRET=xxx
```

**Depois (.env.local):**
```env
# Flask
FLASK_SECRET_KEY=gerar-uma-chave-aleatoria-forte
FLASK_ENV=production

# PostgreSQL Local
DB_HOST=localhost
DB_PORT=5432
DB_NAME=labgas_db
DB_USER=labgas_user
DB_PASSWORD=senha_forte_aqui

# JWT (backend)
SECRET_KEY=mesma-chave-do-flask-ou-outra

# Opcionais
INACTIVITY_TIMEOUT_MINUTES=10
ITEMS_PER_PAGE=10
CACHE_TYPE=SimpleCache
```

---

## 6. Fase 4: Migrar Blueprints

### Arquivos a modificar (49 chamadas Supabase)

| Arquivo | Chamadas | Mudança Principal |
|---|---|---|
| `frontend/app.py` | ~20 | Dashboard, perfil, APIs(`buscar-codigo`, `buscar-elemento`, `dados-usuario`) |
| `frontend/blueprints/amostra.py` | ~7 | Listar/criar/editar amostras |
| `frontend/blueprints/helpers.py` | ~4 | `is_user_active`, `registrar_historico`, `get_all_users`, `get_authenticated_client` |
| `frontend/blueprints/leitura.py` | ~4 | Listar/criar leituras |
| `frontend/blueprints/pressao.py` | ~2 | Deletar pressões |
| `frontend/blueprints/cilindro.py` | ~2 | Deletar cilindros |
| `frontend/blueprints/elemento.py` | ~2 | Deletar elementos |
| `frontend/blueprints/admin.py` | ~1 | Admin (usuários) |
| `frontend/utils/supabase_utils.py` | 1 | `buscar_perfis_usuarios` |

### Remover ao final

- `frontend/utils/supabase_utils.py` (todo)
- Dependência `supabase` do `pyproject.toml`
- `frontend/requirements.txt` → remover `supabase`

---

## 7. Fase 5: Backend API

### `backend/utils/supabase.py` (remover)

Substituir por conexão direta PostgreSQL.

### `backend/config.py`

Mudar variáveis:

```python
# ANTES:
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")

# DEPOIS:
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "labgas_db")
DB_USER = os.getenv("DB_USER", "labgas_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
```

### Rotas do backend

Seguem o mesmo padrão: criar `backend/utils/db.py` (similar ao `db_utils.py` do frontend) e substituir chamadas Supabase.

---

## 8. Fase 6: Deploy na TVBox

### 8.1 Systemd Service

```ini
# /etc/systemd/system/labgas.service
[Unit]
Description=LabGas Manager
After=network.target postgresql.service

[Service]
Type=simple
User=labgas
WorkingDirectory=/opt/labgas-manager/frontend
Environment=PYTHONPATH=/opt/labgas-manager
EnvironmentFile=/opt/labgas-manager/frontend/.env.local
ExecStart=/opt/labgas-manager/.venv/bin/gunicorn app:app --bind 0.0.0.0:8000 --workers 2 --timeout 120
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 8.2 Dockerfile alternativo (se preferir container)

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

RUN groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry && \
    poetry install --no-dev --no-root && \
    pip uninstall --yes poetry

COPY . .

RUN chown -R app:app /app
USER app

EXPOSE 8000
CMD ["gunicorn", "frontend.app:app", "--bind", "0.0.0.0:8000", "--workers", "2"]
```

### 8.3 Pipeline de Deploy

```yaml
# .github/workflows/deploy-tvbox.yml
name: Deploy para TVBox
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.TVBOX_HOST }}
          username: ${{ secrets.TVBOX_USER }}
          key: ${{ secrets.TVBOX_SSH_KEY }}
          script: |
            cd /opt/labgas-manager
            git pull
            poetry install --no-dev
            sudo systemctl restart labgas
```

---

## 9. Fase 7: Backup Local

### 9.1 Script de Backup Local

**Modificar:** `scripts/backup_db.py`

Mudar `_obter_db_url()` para conectar no PostgreSQL local:

```python
def _obter_db_url():
    return f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Remover lógica de Supabase (auth.users via API, etc.)
# users saem da tabela local `users` (não mais `auth.users`)
```

### 9.2 Cron de Backup

```bash
# /etc/cron.d/labgas-backup
0 3 * * * labgas cd /opt/labgas-manager && /opt/labgas-manager/.venv/bin/python scripts/backup_db.py >> /var/log/labgas-backup.log 2>&1
```

### 9.3 Testar Restore

```bash
python scripts/restore_db.py --list           # listar backups
python scripts/restore_db.py --latest --dry-run  # preview
python scripts/restore_db.py --latest         # restaurar
```

---

## Checklist de Migração

### Pré-requisitos (TVBox)

- [ ] Armbian instalado e rodando
- [ ] Python 3.11+ instalado
- [ ] PostgreSQL 15+ instalado e rodando
- [ ] Poetry instalado
- [ ] DuckDNS configurado e apontando para IP da TVBox
- [ ] Cloudflare Tunnel instalado e apontando para `localhost:8000`
- [ ] Projeto clonado e `poetry install` executado
- [ ] `.env.local` configurado com credenciais locais

### Migração de Dados

- [ ] Executar `scripts/backup_db.py` no ambiente atual (extrair dados do Supabase)
- [ ] Aplicar `database/schema_local.sql` no PostgreSQL local
- [ ] Executar `scripts/migrate_to_local.py` para migrar dados
- [ ] Verificar integridade: todas as tabelas populadas
- [ ] Testar login com senha temporária

### Código

- [ ] `frontend/utils/db_utils.py` criado
- [ ] `frontend/blueprints/auth.py` migrado (login/register/logout)
- [ ] `frontend/app.py` migrado (dashboard, perfil, APIs)
- [ ] `frontend/blueprints/helpers.py` migrado
- [ ] `frontend/blueprints/*.py` migrados (amostra, cilindro, elemento, leitura, pressao, admin, historico)
- [ ] `frontend/utils/supabase_utils.py` removido
- [ ] `frontend/utils/supabase_utils.py` import removido de todos os arquivos
- [ ] `backend/config.py` atualizado (sem Supabase)
- [ ] `backend/utils/supabase.py` removido
- [ ] `backend/utils/db.py` criado
- [ ] `backend/routes/*.py` migrados
- [ ] Dependência `supabase` removida do `pyproject.toml`
- [ ] `frontend/requirements.txt` atualizado

### Deploy

- [ ] Systemd service configurado
- [ ] Ambiente rodando com gunicorn
- [ ] Cloudflare Tunnel ativo
- [ ] HTTPS funcionando via DuckDNS
- [ ] Backup automático agendado
- [ ] CI/CD configurado (opcional)

### Testes

- [ ] Login/Register funcionando
- [ ] CRUD cilindros
- [ ] CRUD elementos
- [ ] CRUD leituras
- [ ] CRUD pressões
- [ ] CRUD amostras
- [ ] Dashboard exibindo dados corretamente
- [ ] Admin panel funcional
- [ ] Exportação de dados
- [ ] Histórico sendo registrado
- [ ] Backup manual funcionando

---

## Observações Finais

1. **Senhas temporárias**: Durante a migração, todos os usuários receberão senhas temporárias. Anote-as e distribua para os usuários redefinirem no primeiro login.

2. **DuckDNS + Cloudflare Tunnel**: O DuckDNS resolve o IP dinâmico da TVBox. O Cloudflare Tunnel cria um túnel seguro HTTPS sem precisar abrir portas no firewall.

3. **Performance**: A TVBox Armbian (ARM) tem recursos limitados. Recomendo:
   - Gunicorn com 2 workers (não mais)
   - Connection pool com max 10 conexões
   - Cache SimpleCache (evitar Redis)
   - Monitorar uso de RAM/CPU

4. **Rollback**: Mantenha o Supabase funcionando até a migração ser validada. Se algo der errado, só trocar as env vars de volta.
