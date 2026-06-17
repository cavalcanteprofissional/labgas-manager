import pytest


def test_elemento_list_page_loads(login, page):
    page.goto("http://localhost:5000/elementos")
    page.wait_for_selector("body")
    text = page.text_content("body")
    assert "Elemento" in text


def test_create_elemento(login, page, cleanup_elementos, cleanup_historico):
    page.goto("http://localhost:5000/elementos")
    page.wait_for_selector("body")

    add_btn = page.locator("button:has-text('Novo'), a:has-text('Novo')").first
    if add_btn.is_visible():
        add_btn.click()
        page.wait_for_timeout(1000)

    page.locator("input[name='nome']").first.fill("Elemento Teste")
    page.locator("input[name='consumo_lpm']").first.fill("0.5")

    submit = page.locator("button[type='submit']").first
    submit.click()
    page.wait_for_timeout(3000)

    page.goto("http://localhost:5000/elementos")
    page.wait_for_timeout(2000)
    html = page.content()
    assert "Elemento Teste" in html


def test_elemento_table_visible(login, page):
    page.goto("http://localhost:5000/elementos")
    page.wait_for_selector("body")
    table = page.locator("table").first
    assert table.is_visible()


@pytest.mark.modais
def test_elemento_edit_modal_preenche_campos(login, page, supabase_admin, test_user_id,
                                              cleanup_elementos, cleanup_historico):
    el = supabase_admin.table("elemento").insert({
        "nome": "ModalElem", "consumo_lpm": 3.5, "user_id": test_user_id,
    }).execute()
    el_id = el.data[0]["id"]

    page.goto("http://localhost:5000/elementos?per_page=1000")
    page.wait_for_selector("body")
    page.locator(f"button[data-bs-target='#editModal{el_id}']").click()
    page.wait_for_timeout(1000)

    modal = page.locator(f"#editModal{el_id}")
    assert modal.is_visible()
    assert modal.locator("input[name='nome']").input_value() == "ModalElem"
    assert modal.locator("input[name='consumo_lpm']").input_value() == "3.5"


@pytest.mark.modais
def test_elemento_delete_modal_exclui(login, page, supabase_admin, test_user_id,
                                       cleanup_elementos, cleanup_historico):
    el = supabase_admin.table("elemento").insert({
        "nome": "DelElem", "consumo_lpm": 1.0, "user_id": test_user_id,
    }).execute()
    el_id = el.data[0]["id"]

    page.goto("http://localhost:5000/elementos?per_page=1000")
    page.wait_for_selector("body")
    page.locator(f"button[data-bs-target='#deleteModal{el_id}']").click()
    page.wait_for_timeout(1000)

    delete_modal = page.locator(f"#deleteModal{el_id}")
    assert delete_modal.is_visible()

    delete_modal.locator(f"button[form='deleteForm{el_id}']").click()
    page.wait_for_timeout(3000)
    assert "/elementos" in page.url

    result = supabase_admin.table("elemento").select("id").eq("id", el_id).execute()
    assert not result.data


@pytest.mark.modais
def test_elemento_bulk_delete(login, page, supabase_admin, test_user_id,
                               cleanup_elementos, cleanup_historico):
    ids = []
    for i in range(2):
        el = supabase_admin.table("elemento").insert({
            "nome": f"BulkElem{i}", "consumo_lpm": 1.0, "user_id": test_user_id,
        }).execute()
        ids.append(el.data[0]["id"])

    page.goto("http://localhost:5000/elementos?per_page=1000")
    page.wait_for_selector("body")

    for eid in ids:
        page.locator(f"input.item-checkbox[value='{eid}']").check()
    page.wait_for_timeout(500)

    floating = page.locator("#selectedActions")
    assert floating.is_visible()

    floating.locator("button:has-text('Excluir')").click()
    page.wait_for_timeout(1000)

    bulk = page.locator("#bulkDeleteModal")
    assert bulk.is_visible()

    bulk.locator("button[type='submit']").click()
    page.wait_for_timeout(3000)
    assert "/elementos" in page.url
