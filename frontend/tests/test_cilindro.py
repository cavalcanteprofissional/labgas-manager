import pytest


def test_cilindro_list_page_loads(login, page):
    page.goto("http://localhost:5000/cilindros")
    page.wait_for_selector("body")
    text = page.text_content("body")
    assert "Cilindro" in text


def test_create_cilindro(login, page, cleanup_cilindros, cleanup_historico):
    page.goto("http://localhost:5000/cilindros")
    page.wait_for_selector("body")

    page.locator("button:has-text('Novo Cilindro')").first.click()
    page.wait_for_timeout(500)

    page.locator("input[name='numero']").first.fill("999")
    page.locator("input[name='data_compra']").first.fill("2025-01-15")
    page.locator("input[name='gas_kg']").first.fill("1.0")
    page.locator("input[name='custo']").first.fill("290.00")

    page.locator("button:has-text('Cadastrar')").click()
    page.wait_for_timeout(3000)
    assert "/cilindros" in page.url


def test_cilindro_table_visible(login, page):
    page.goto("http://localhost:5000/cilindros")
    page.wait_for_selector("body")
    table = page.locator("table").first
    assert table.is_visible()


@pytest.mark.modais
def test_cilindro_edit_modal_preenche_campos(login, page, supabase_admin, test_user_id,
                                              cleanup_cilindros, cleanup_historico):
    cil = supabase_admin.table("cilindro").insert({
        "numero": 820, "data_compra": "2025-01-01",
        "gas_kg": 42.0, "custo": 290, "status": "ativo",
        "user_id": test_user_id,
    }).execute()
    cil_id = cil.data[0]["id"]

    page.goto("http://localhost:5000/cilindros?per_page=1000")
    page.wait_for_selector("body")
    page.locator(f"button[data-bs-target='#editModal{cil_id}']").click()
    page.wait_for_timeout(1000)

    modal = page.locator(f"#editModal{cil_id}")
    assert modal.is_visible()

    assert modal.locator("input[name='numero']").input_value() == "820"
    assert modal.locator("input[name='gas_kg']").input_value() == "42.0"
    assert modal.locator("select[name='status']").input_value() == "ativo"


@pytest.mark.modais
def test_cilindro_delete_modal_exclui(login, page, supabase_admin, test_user_id,
                                       cleanup_cilindros, cleanup_historico):
    cil = supabase_admin.table("cilindro").insert({
        "numero": 821, "data_compra": "2025-01-01",
        "gas_kg": 10, "custo": 290, "status": "ativo",
        "user_id": test_user_id,
    }).execute()
    cil_id = cil.data[0]["id"]

    page.goto("http://localhost:5000/cilindros?per_page=1000")
    page.wait_for_selector("body")
    page.locator(f"button[data-bs-target='#deleteModal{cil_id}']").click()
    page.wait_for_timeout(1000)

    delete_modal = page.locator(f"#deleteModal{cil_id}")
    assert delete_modal.is_visible()

    delete_modal.locator(f"button[form='deleteForm{cil_id}']").click()
    page.wait_for_timeout(3000)
    assert "/cilindros" in page.url

    result = supabase_admin.table("cilindro").select("id").eq("id", cil_id).execute()
    assert not result.data


@pytest.mark.modais
def test_cilindro_exibe_numero_sem_rotulos(login, page, supabase_admin, test_user_id,
                                           cleanup_cilindros, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    supabase_admin.table("cilindro").insert({
        "numero": 822, "data_compra": "2025-01-01",
        "gas_kg": 10, "custo": 290, "status": "ativo",
        "user_id": test_user_id,
    }).execute()

    page.goto("http://localhost:5000/cilindros?per_page=1000")
    page.wait_for_selector("body")

    badge = page.locator("table tbody tr td:nth-child(2) .badge").first
    assert badge.text_content().strip() == "1"

    status_badge = page.locator("table tbody tr td:nth-child(9) .badge").first
    assert status_badge.text_content().strip() == "Ativo"

    table_text = page.locator("table tbody").first.text_content()
    assert "50%" not in table_text
    assert "EM USO" not in table_text
    assert "ESGOTADO" not in table_text
    assert "CIL-001" not in table_text


@pytest.mark.modais
def test_cilindro_bulk_delete(login, page, supabase_admin, test_user_id,
                               cleanup_cilindros, cleanup_historico):
    ids = []
    for i in range(2):
        c = supabase_admin.table("cilindro").insert({
            "numero": 823 + i, "data_compra": "2025-01-01",
            "gas_kg": 10, "custo": 290, "status": "ativo",
            "user_id": test_user_id,
        }).execute()
        ids.append(c.data[0]["id"])

    page.goto("http://localhost:5000/cilindros?per_page=1000")
    page.wait_for_selector("body")

    for cid in ids:
        page.locator(f"input.item-checkbox[value='{cid}']").check()
    page.wait_for_timeout(500)

    floating = page.locator("#selectedActions")
    assert floating.is_visible()

    floating.locator("button:has-text('Excluir')").click()
    page.wait_for_timeout(1000)

    bulk = page.locator("#bulkDeleteModal")
    assert bulk.is_visible()

    bulk.locator("button[type='submit']").click()
    page.wait_for_timeout(3000)
    assert "/cilindros" in page.url


def _badges_visiveis(page):
    badges = set()
    for row in page.locator("table tbody tr").all():
        if row.is_visible():
            badges.add(row.locator("td:nth-child(2) .badge").first.text_content().strip())
    return badges


def _badges_ordem(page):
    badges = []
    for row in page.locator("table tbody tr").all():
        if row.is_visible():
            badges.append(row.locator("td:nth-child(2) .badge").first.text_content().strip())
    return badges


def _inserir_cilindro(supabase_admin, test_user_id, numero, status="ativo", gas_kg=42.0, custo=290.0,
                      data_compra="2025-01-01"):
    supabase_admin.table("cilindro").insert({
        "numero": numero, "data_compra": data_compra,
        "gas_kg": gas_kg, "custo": custo, "status": status,
        "user_id": test_user_id,
    }).execute()


def test_cilindro_filtro_acha_numero_em_outra_pagina(login, page, supabase_admin, test_user_id,
                                                     cleanup_cilindros, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    for i in range(1, 13):
        _inserir_cilindro(supabase_admin, test_user_id, i)

    page.goto("http://localhost:5000/cilindros?q=1")
    page.wait_for_selector("body")

    badges = _badges_visiveis(page)
    assert {"1", "10", "11", "12"} <= badges
    assert badges & {"2", "3", "4", "5", "6", "7", "8", "9"} == set()


def test_cilindro_filtro_nao_vaza_digitos_do_custo(login, page, supabase_admin, test_user_id,
                                                   cleanup_cilindros, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    for numero in (1, 2, 3):
        _inserir_cilindro(supabase_admin, test_user_id, numero, gas_kg=42.0, custo=290.0)

    page.goto("http://localhost:5000/cilindros?q=2")
    page.wait_for_selector("body")
    badges = _badges_visiveis(page)
    assert "2" in badges
    assert badges & {"1", "3"} == set()

    page.goto("http://localhost:5000/cilindros?q=9")
    page.wait_for_selector("body")
    assert _badges_visiveis(page) & {"1", "2", "3"} == set()


def test_cilindro_filtro_por_numero_substring(login, page, supabase_admin, test_user_id,
                                              cleanup_cilindros, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    for numero in (5, 15):
        _inserir_cilindro(supabase_admin, test_user_id, numero)

    page.goto("http://localhost:5000/cilindros?q=5")
    page.wait_for_selector("body")
    assert {"5", "15"} <= _badges_visiveis(page)

    page.goto("http://localhost:5000/cilindros?q=CIL-015")
    page.wait_for_selector("body")
    badges = _badges_visiveis(page)
    assert "15" in badges
    assert "5" not in badges


def test_cilindro_filtro_status(login, page, supabase_admin, test_user_id,
                                cleanup_cilindros, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    _inserir_cilindro(supabase_admin, test_user_id, 900, status="ativo")
    _inserir_cilindro(supabase_admin, test_user_id, 901, status="esgotado")

    page.goto("http://localhost:5000/cilindros?status=esgotado&per_page=1000")
    page.wait_for_selector("body")
    badges = _badges_visiveis(page)
    assert "901" in badges
    assert "900" not in badges


def test_cilindro_ordem_por_numero(login, page, supabase_admin, test_user_id,
                                   cleanup_cilindros, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    _inserir_cilindro(supabase_admin, test_user_id, 810, status="esgotado")
    _inserir_cilindro(supabase_admin, test_user_id, 801, status="ativo")
    _inserir_cilindro(supabase_admin, test_user_id, 800, status="esgotado")
    _inserir_cilindro(supabase_admin, test_user_id, 802, status="ativo")

    page.goto("http://localhost:5000/cilindros?per_page=1000")
    page.wait_for_selector("body")

    ordem = _badges_ordem(page)
    idx = {b: i for i, b in enumerate(ordem)}
    assert idx["800"] < idx["801"] < idx["802"] < idx["810"]


def test_cilindro_filtro_data_compra_range(login, page, supabase_admin, test_user_id,
                                           cleanup_cilindros, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    _inserir_cilindro(supabase_admin, test_user_id, 901, data_compra="2026-01-15")
    _inserir_cilindro(supabase_admin, test_user_id, 902, data_compra="2026-02-10")
    _inserir_cilindro(supabase_admin, test_user_id, 903, data_compra="2026-03-05")

    page.goto("http://localhost:5000/cilindros?data_inicio=2026-01-01&data_fim=2026-01-31")
    page.wait_for_selector("body")
    badges = _badges_visiveis(page)
    assert "901" in badges
    assert "902" not in badges
    assert "903" not in badges

    page.goto("http://localhost:5000/cilindros?data_inicio=2026-03-01")
    page.wait_for_selector("body")
    badges = _badges_visiveis(page)
    assert "903" in badges
    assert "901" not in badges


def test_cilindro_filtro_dinamico_ao_digitar(login, page, supabase_admin, test_user_id,
                                             cleanup_cilindros, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    _inserir_cilindro(supabase_admin, test_user_id, 5)
    _inserir_cilindro(supabase_admin, test_user_id, 6)
    _inserir_cilindro(supabase_admin, test_user_id, 15)

    page.goto("http://localhost:5000/cilindros")
    page.wait_for_selector("body")

    page.locator("#searchCilindro").fill("5")
    page.wait_for_function("location.search.includes('q=5')", timeout=10000)
    page.wait_for_selector("tbody tr")

    badges = _badges_visiveis(page)
    assert {"5", "15"} <= badges
    assert "6" not in badges
