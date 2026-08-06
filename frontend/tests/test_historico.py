import pytest
import uuid
from datetime import datetime


def _inserir_historico(supabase_admin, test_user_id, tipo, acao, label, data=None, ref_id=None):
    created_at = data or datetime.now().isoformat()
    return supabase_admin.table("historico_auditoria").insert({
        "tipo": tipo,
        "acao": acao,
        "label": label,
        "user_id": test_user_id,
        "created_at": created_at,
        "ref_id": ref_id,
    }).execute().data[0]["id"]


def test_historico_page_loads(login, page):
    page.goto("http://localhost:5000/historico")
    page.wait_for_selector("body")
    assert "Histórico" in page.text_content("body")


def test_historico_filter_por_tipo(login, page, supabase_admin, test_user_id, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    tag = uuid.uuid4().hex[:8]
    cil_label = f"UNIQ-CIL-{tag}"
    amo_label = f"UNIQ-AMO-{tag}"
    _inserir_historico(supabase_admin, test_user_id, "cilindro", "criado", cil_label)
    _inserir_historico(supabase_admin, test_user_id, "amostra", "criado", amo_label)

    page.goto("http://localhost:5000/historico?tipo=cilindro&per_page=100")
    page.wait_for_selector("body")
    body = page.text_content("body")
    assert cil_label in body
    assert amo_label not in body


def test_historico_filter_por_acao(login, page, supabase_admin, test_user_id, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    tag = uuid.uuid4().hex[:8]
    criado_label = f"UNIQ-CRIADO-{tag}"
    excluido_label = f"UNIQ-EXCL-{tag}"
    _inserir_historico(supabase_admin, test_user_id, "cilindro", "criado", criado_label)
    _inserir_historico(supabase_admin, test_user_id, "elemento", "excluido", excluido_label)

    page.goto("http://localhost:5000/historico?acao=excluido&per_page=100")
    page.wait_for_selector("body")
    body = page.text_content("body")
    assert excluido_label in body
    assert criado_label not in body


def test_historico_filter_por_q_label(login, page, supabase_admin, test_user_id, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    tag = uuid.uuid4().hex[:8]
    alvo = f"UNIQ-LABEL-{tag}"
    outro = f"UNIQ-OUTRO-{tag}"
    _inserir_historico(supabase_admin, test_user_id, "pressao", "criado", alvo)
    _inserir_historico(supabase_admin, test_user_id, "leitura", "criado", outro)

    page.goto(f"http://localhost:5000/historico?q={tag}&per_page=100")
    page.wait_for_selector("body")
    body = page.text_content("body")
    assert alvo in body
    assert outro in body


def test_historico_filter_por_intervalo_data(login, page, supabase_admin, test_user_id, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    tag = uuid.uuid4().hex[:8]
    dentro = f"UNIQ-DENTRO-{tag}"
    fora = f"UNIQ-FORA-{tag}"
    _inserir_historico(supabase_admin, test_user_id, "cilindro", "criado", dentro, data="2025-06-10")
    _inserir_historico(supabase_admin, test_user_id, "cilindro", "criado", fora, data="2025-06-20")

    page.goto("http://localhost:5000/historico?data_inicio=2025-06-01&data_fim=2025-06-15&per_page=100")
    page.wait_for_selector("body")
    body = page.text_content("body")
    assert dentro in body
    assert fora not in body


def test_historico_paginacao_preserva_filtros(login, page, supabase_admin, test_user_id, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    tag = uuid.uuid4().hex[:8]
    for i in range(25):
        _inserir_historico(supabase_admin, test_user_id, "cilindro", "criado", f"UNIQ-PAG-{tag}-{i}")

    page.goto(f"http://localhost:5000/historico?q={tag}&per_page=10")
    page.wait_for_selector("body")
    next_link = page.locator("a:has-text('Próxima')").first
    assert next_link.is_visible()
    href = next_link.get_attribute("href")
    assert f"q={tag}" in href
    assert "per_page=10" in href


def test_historico_per_page_seletor(login, page, supabase_admin, test_user_id, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    tag = uuid.uuid4().hex[:8]
    for i in range(25):
        _inserir_historico(supabase_admin, test_user_id, "elemento", "criado", f"UNIQ-PP-{tag}-{i}")

    page.goto(f"http://localhost:5000/historico?q={tag}")
    page.wait_for_selector("body")
    selector = page.locator("select:has(option[value='20'])")
    assert selector.count() >= 1
    assert selector.locator("option[value='20'][selected]").count() >= 1
