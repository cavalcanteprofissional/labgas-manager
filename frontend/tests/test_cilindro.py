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

    page.locator("input[name='codigo']").first.fill("CIL-999")
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
        "codigo": "CIL-TST", "data_compra": "2025-01-01",
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

    assert modal.locator("input[name='codigo']").input_value() == "CIL-TST"
    assert modal.locator("input[name='gas_kg']").input_value() == "42.0"
    assert modal.locator("select[name='status']").input_value() == "ativo"


@pytest.mark.modais
def test_cilindro_delete_modal_exclui(login, page, supabase_admin, test_user_id,
                                       cleanup_cilindros, cleanup_historico):
    cil = supabase_admin.table("cilindro").insert({
        "codigo": "CIL-DEL", "data_compra": "2025-01-01",
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
def test_cilindro_bulk_delete(login, page, supabase_admin, test_user_id,
                               cleanup_cilindros, cleanup_historico):
    ids = []
    for i in range(2):
        c = supabase_admin.table("cilindro").insert({
            "codigo": f"CIL-BULK{i}", "data_compra": "2025-01-01",
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
