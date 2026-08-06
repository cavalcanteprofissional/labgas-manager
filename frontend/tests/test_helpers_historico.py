import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env.local"))

from unittest.mock import patch

from blueprints.helpers import registrar_historico


def _fake_client(insert_fn):
    class T:
        def __init__(self, nome):
            self.nome = nome
        def insert(self, registro):
            insert_fn(self.nome, registro)
            class Resp:
                data = [{"id": 1}]
            return Resp()
    class C:
        def __init__(self):
            self._insert_fn = insert_fn
        def table(self, nome):
            return T(nome)
    return C()


def test_registrar_historico_simples_nao_inclui_ref_ou_detalhe():
    chamadas = {}

    def fake_insert(nome, registro):
        chamadas["registro"] = registro

    with patch("utils.supabase_utils.get_admin_client", return_value=_fake_client(fake_insert)):
        registrar_historico("cilindro", "criado", "CIL-001", "user-1")

    registro = chamadas["registro"]
    assert registro["tipo"] == "cilindro"
    assert registro["acao"] == "criado"
    assert registro["label"] == "CIL-001"
    assert registro["user_id"] == "user-1"
    assert "ref_id" not in registro
    assert "detalhe" not in registro


def test_registrar_historico_com_ref_id_e_detalhe():
    chamadas = {}

    def fake_insert(nome, registro):
        chamadas["registro"] = registro

    with patch("utils.supabase_utils.get_admin_client", return_value=_fake_client(fake_insert)):
        registrar_historico(
            "pressao",
            "criado",
            "CIL-001 - 150 bar",
            "user-1",
            ref_id=42,
            detalhe={"pressao": 150.0, "temperatura": 25.0},
        )

    registro = chamadas["registro"]
    assert registro["ref_id"] == 42
    assert registro["detalhe"] == {"pressao": 150.0, "temperatura": 25.0}


def test_registrar_historico_ref_id_zero_e_detalhe_vazio_sao_respeitados():
    chamadas = {}

    def fake_insert(nome, registro):
        chamadas["registro"] = registro

    with patch("utils.supabase_utils.get_admin_client", return_value=_fake_client(fake_insert)):
        registrar_historico("perfil", "atualizado", "Usuário ativado", "user-1",
                            ref_id=0, detalhe={})

    registro = chamadas["registro"]
    assert registro["ref_id"] == 0
    assert registro["detalhe"] == {}


def test_registrar_historico_nao_quebra_se_client_estourar():
    with patch("utils.supabase_utils.get_admin_client", side_effect=Exception("boom")):
        registrar_historico("cilindro", "criado", "CIL-001", "user-1")
