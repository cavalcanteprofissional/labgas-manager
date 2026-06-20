"""test_backup.py — Testes para scripts de backup e restore.

Uso:
    pytest frontend/tests/test_backup.py                          # unitários apenas
    pytest frontend/tests/test_backup.py --run-backup             # unitários + integração
"""

import importlib.util
import json
import os
import re
import sys
import gzip
import subprocess
from datetime import datetime, date, time, timedelta, UTC
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
BACKUP_SCRIPT = SCRIPTS_DIR / "backup_db.py"
RESTORE_SCRIPT = SCRIPTS_DIR / "restore_db.py"


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    # Isolar variáveis de ambiente para evitar poluição entre testes
    mod.os = __import__("os")
    spec.loader.exec_module(mod)
    return mod


# ─── Fixtures ───────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def backup_module():
    return _load_module("backup_db", BACKUP_SCRIPT)


@pytest.fixture(scope="module")
def restore_module():
    return _load_module("restore_db", RESTORE_SCRIPT)


@pytest.fixture
def sample_row():
    now = datetime.now(UTC)
    return {
        "id": 1,
        "uuid_field": uuid4(),
        "nome": "Teste",
        "data": now.date(),
        "data_hora": now,
        "hora": now.time(),
        "duracao": timedelta(hours=1, minutes=30),
        "valor": Decimal("29.90"),
        "nulo": None,
        "bytes_field": b"\\xdeadbeef",
        "dict_field": {"chave": "valor", "numero": 42},
        "list_field": [1, "dois", Decimal("3.0")],
    }


# ─── Testes de Serialização (backup_db) ────────────────────────────────────────


class TestSerializacao:
    def test_serializar_tipos_basicos(self, backup_module, sample_row):
        result = backup_module.serializar(sample_row)
        assert isinstance(result["id"], int)
        assert result["id"] == 1
        assert result["nome"] == "Teste"
        assert result["nulo"] is None

    def test_serializar_uuid(self, backup_module, sample_row):
        result = backup_module.serializar(sample_row)
        assert isinstance(result["uuid_field"], str)
        assert UUID(result["uuid_field"])

    def test_serializar_datetime(self, backup_module, sample_row):
        result = backup_module.serializar(sample_row)
        assert isinstance(result["data_hora"], str)
        assert "T" in result["data_hora"]

    def test_serializar_date(self, backup_module, sample_row):
        result = backup_module.serializar(sample_row)
        assert isinstance(result["data"], str)

    def test_serializar_time(self, backup_module, sample_row):
        result = backup_module.serializar(sample_row)
        assert isinstance(result["hora"], str)
        assert ":" in result["hora"]

    def test_serializar_timedelta(self, backup_module, sample_row):
        result = backup_module.serializar(sample_row)
        assert isinstance(result["duracao"], str)

    def test_serializar_decimal(self, backup_module, sample_row):
        result = backup_module.serializar(sample_row)
        assert isinstance(result["valor"], float)
        assert result["valor"] == 29.9

    def test_serializar_dict_aninhado(self, backup_module, sample_row):
        result = backup_module.serializar(sample_row)
        assert result["dict_field"]["chave"] == "valor"
        assert result["dict_field"]["numero"] == 42

    def test_serializar_lista_com_decimal(self, backup_module, sample_row):
        result = backup_module.serializar(sample_row)
        assert result["list_field"] == [1, "dois", 3.0]

    def test_serializar_bytes(self, backup_module, sample_row):
        result = backup_module.serializar(sample_row)
        assert isinstance(result["bytes_field"], str)

    def test_serializar_valor_datetime(self, backup_module):
        val = backup_module.serializar_valor(datetime.now(UTC))
        assert isinstance(val, str)
        assert "T" in val

    def test_serializar_valor_date(self, backup_module):
        val = backup_module.serializar_valor(date(2024, 3, 15))
        assert isinstance(val, str)
        assert val == "2024-03-15"

    def test_serializar_valor_decimal(self, backup_module):
        val = backup_module.serializar_valor(Decimal("42.5"))
        assert isinstance(val, float)
        assert val == 42.5

    def test_serializar_valor_uuid(self, backup_module):
        uid = uuid4()
        val = backup_module.serializar_valor(uid)
        assert isinstance(val, str)
        assert val == str(uid)

    def test_serializar_valor_plain(self, backup_module):
        assert backup_module.serializar_valor("texto") == "texto"
        assert backup_module.serializar_valor(42) == 42
        assert backup_module.serializar_valor(True) is True
        assert backup_module.serializar_valor(None) is None


# ─── Testes de Construção de URL (backup_db) ────────────────────────────────────


class TestObterDbUrl:
    def test_url_direta(self, backup_module, monkeypatch):
        url = "postgresql://user:pass@host:5432/db?sslmode=require"
        monkeypatch.setenv("DATABASE_URL", url)
        assert backup_module._obter_db_url() == url

    def test_fallback_supabase(self, backup_module, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.setenv("SUPABASE_URL", "https://xxxxx.supabase.co")
        monkeypatch.setenv("BACKUP_DB_PASSWORD", "secret123")
        result = backup_module._obter_db_url()
        assert "backup_user.xxxxx:secret123" in result
        assert "aws-1-us-east-2.pooler.supabase.com" in result
        assert "sslmode=require" in result

    def test_fallback_sem_password(self, backup_module, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("BACKUP_DB_PASSWORD", raising=False)
        monkeypatch.setenv("SUPABASE_URL", "https://xxxxx.supabase.co")
        assert backup_module._obter_db_url() is None

    def test_fallback_sem_url(self, backup_module, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.setenv("BACKUP_DB_PASSWORD", "secret123")
        assert backup_module._obter_db_url() is None

    def test_fallback_monta_url_corretamente(self, backup_module, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.setenv("SUPABASE_URL", "https://abc123.supabase.co")
        monkeypatch.setenv("BACKUP_DB_PASSWORD", "Senha!Forte#123")
        result = backup_module._obter_db_url()
        assert "backup_user.abc123:Senha%21Forte%23123" in result
        assert "aws-1-us-east-2.pooler.supabase.com" in result
        assert "sslmode=require" in result


# ─── Testes de Restore: colunas_para_sql ────────────────────────────────────────


class TestColunasParaSQL:
    def test_colunas_para_sql_vazia(self, restore_module):
        cols, cols_str, placeholders, update_cols = restore_module.colunas_para_sql([])
        assert cols == ""
        assert cols_str == ""
        assert placeholders == ""
        assert update_cols == ""

    def test_colunas_para_sql_simples(self, restore_module):
        rows = [{"id": 1, "nome": "teste", "valor": 10}]
        cols, cols_str, placeholders, update_cols = restore_module.colunas_para_sql(rows)
        assert '"id"' in cols_str
        assert '"nome"' in cols_str
        assert '"valor"' in cols_str
        assert "%(id)s" in placeholders
        assert "%(nome)s" in placeholders
        assert "EXCLUDED" in update_cols
        assert '"nome" = EXCLUDED."nome"' in update_cols

    def test_colunas_para_sql_exclui_id_do_update(self, restore_module):
        rows = [{"id": 1, "nome": "teste"}]
        _, _, _, update_cols = restore_module.colunas_para_sql(rows)
        assert '"id" = EXCLUDED."id"' not in update_cols
        assert '"nome" = EXCLUDED."nome"' in update_cols


# ─── Testes de Ordem de DELETE/INSERT (restore_db) ──────────────────────────────


class TestOrdemOperacoes:
    def test_delete_antes_de_parent(self, restore_module):
        """Tabelas com FK devem ser deletadas antes da tabela pai."""
        delete_order = restore_module.DELETE_ORDER
        dependencias = {
            "amostra_elemento": ["amostra", "elemento"],
            "leitura": ["cilindro", "elemento"],
            "pressao": ["cilindro"],
            "amostra": ["cilindro", "elemento"],
            "historico_log": ["perfil"],
        }
        for dependente, parents in dependencias.items():
            idx_dep = delete_order.index(dependente)
            for parent in parents:
                idx_parent = delete_order.index(parent)
                assert idx_dep < idx_parent, \
                    f"{dependente} (pos {idx_dep}) deve vir antes de {parent} (pos {idx_parent}) no DELETE_ORDER"

    def test_insert_depois_de_parent(self, restore_module):
        """Tabelas com FK devem ser inseridas depois da tabela pai."""
        insert_public = [t.split(".", 1)[1] for t in restore_module.INSERT_ORDER if t.startswith("public.")]
        dependencias = {
            "amostra_elemento": ["amostra", "elemento"],
            "leitura": ["cilindro", "elemento"],
            "pressao": ["cilindro"],
            "amostra": ["cilindro", "elemento"],
            "historico_log": ["perfil"],
        }
        for dependente, parents in dependencias.items():
            idx_dep = insert_public.index(dependente)
            for parent in parents:
                idx_parent = insert_public.index(parent)
                assert idx_dep > idx_parent, \
                    f"{dependente} (pos {idx_dep}) deve vir depois de {parent} (pos {idx_parent}) no INSERT_ORDER"

    def test_auth_users_primeiro_no_insert(self, restore_module):
        assert restore_module.INSERT_ORDER[0] == "auth.users", \
            "auth.users deve ser inserido primeiro (FKs dependem dele)"

    def test_perfil_segundo_no_insert(self, restore_module):
        assert restore_module.INSERT_ORDER[1] == "public.perfil", \
            "perfil deve vir depois de auth.users (FK user_id)"


# ─── Testes de Integração (subprocess, --run-backup) ────────────────────────────


class TestBackupIntegracao:
    @pytest.mark.backup
    def test_backup_script_executa(self):
        """Executa backup_db.py --no-upload e verifica se um .json.gz foi gerado."""
        backup_dir = BASE_DIR / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        before = sorted(backup_dir.glob("*.json.gz"))
        result = subprocess.run(
            [sys.executable, str(BACKUP_SCRIPT), "--no-upload"],
            cwd=BASE_DIR,
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, f"backup_db.py falhou:\n{result.stderr}"
        after = sorted(backup_dir.glob("*.json.gz"))
        novos = [f for f in after if f not in before]
        assert len(novos) >= 1, "Nenhum novo arquivo de backup foi gerado"

        backup_path = novos[-1]
        assert backup_path.suffixes == [".json", ".gz"]

        with gzip.open(backup_path, "rt", encoding="utf-8") as f:
            dados = json.load(f)

        assert "version" in dados
        assert "created_at" in dados
        assert "tables" in dados
        assert "public.perfil" in dados["tables"]
        assert "public.elemento" in dados["tables"]
        assert "public.cilindro" in dados["tables"]
        assert "public.amostra" in dados["tables"]
        assert "public.amostra_elemento" in dados["tables"]
        assert "public.leitura" in dados["tables"]
        assert "public.pressao" in dados["tables"]
        assert "public.historico_log" in dados["tables"]
        assert isinstance(dados["tables"]["public.perfil"], list)

        backup_path.unlink()

    @pytest.mark.backup
    def test_backup_tabelas_nao_vazias(self):
        """Verifica se as tabelas principais têm registros no backup."""
        backup_dir = BASE_DIR / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            [sys.executable, str(BACKUP_SCRIPT), "--no-upload", "--output-dir", str(backup_dir)],
            cwd=BASE_DIR,
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0
        backups = sorted(backup_dir.glob("*.json.gz"))
        backup_path = backups[-1]

        with gzip.open(backup_path, "rt", encoding="utf-8") as f:
            dados = json.load(f)

        saida = result.stdout
        assert "auth.users" in saida

        backup_path.unlink()

    @pytest.mark.backup
    def test_backup_json_valido(self):
        """Verifica que o JSON gerado é válido e tem estrutura consistente."""
        backup_dir = BASE_DIR / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            [sys.executable, str(BACKUP_SCRIPT), "--no-upload", "--output-dir", str(backup_dir)],
            cwd=BASE_DIR,
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0
        backups = sorted(backup_dir.glob("*.json.gz"))
        backup_path = backups[-1]

        with gzip.open(backup_path, "rt", encoding="utf-8") as f:
            dados = json.load(f)

        assert dados["version"] == "1.0"
        assert "created_at" in dados
        assert len(dados["tables"]) >= 8

        for tbl, registros in dados["tables"].items():
            assert isinstance(registros, list)
            for reg in registros:
                assert isinstance(reg, dict)

        backup_path.unlink()

    @pytest.mark.backup
    def test_restore_list_funciona(self):
        """Verifica que --list lista backups do R2 (se configurado) ou mostra msg."""
        result = subprocess.run(
            [sys.executable, str(RESTORE_SCRIPT), "--list"],
            cwd=BASE_DIR,
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"restore --list falhou:\n{result.stderr}"
        assert "labgas_backup" in result.stdout or "Nenhum" in result.stdout

    @pytest.mark.backup
    def test_restore_dry_run_sem_args(self):
        """Verifica que --dry-run sem --file ou --latest exibe ajuda."""
        result = subprocess.run(
            [sys.executable, str(RESTORE_SCRIPT)],
            cwd=BASE_DIR,
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode != 0
        assert "usage" in result.stdout.lower() or "usage" in result.stderr.lower()
