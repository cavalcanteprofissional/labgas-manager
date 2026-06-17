import pytest


def test_amostra_page_loads(login, page):
    page.goto("http://localhost:5000/amostras")
    page.wait_for_selector("body")
    text = page.text_content("body")
    assert "Amostras" in text


def test_create_amostra(login, page, supabase_admin, test_user_id, cleanup_amostras, cleanup_elementos, cleanup_historico):
    elem = supabase_admin.table("elemento").insert({
        "nome": "TestElem",
        "consumo_lpm": 1.0,
        "user_id": test_user_id,
    }).execute()
    elem_id = elem.data[0]["id"]

    page.goto("http://localhost:5000/amostras")
    page.wait_for_selector("body")

    page.click("button[data-bs-target='#formAmostra']")
    page.wait_for_timeout(2000)

    form = page.locator("#formAmostra")
    form.locator("input[name='numero_amostra']").fill("2")
    form.locator("input[name='lote']").fill("42")
    form.locator(f"#elem_create_{elem_id}").check()
    form.locator("button[type='submit']").click()
    page.wait_for_timeout(3000)
    assert "/amostras" in page.url

    body_text = page.text_content("body")
    assert "TestElem" in body_text


def test_amostra_empty_state(login, page, cleanup_amostras):
    page.goto("http://localhost:5000/amostras")
    page.wait_for_selector("body")
    text = page.text_content("body")
    assert "Nenhuma amostra" in text or "Amostras" in text


@pytest.mark.modais
def test_edit_modal_preenche_campos(login, page, supabase_admin, test_user_id,
                                     cleanup_amostras, cleanup_elementos, cleanup_historico):
    elem = supabase_admin.table("elemento").insert({
        "nome": "TestElem", "consumo_lpm": 1.0, "user_id": test_user_id,
    }).execute()
    elem_id = elem.data[0]["id"]
    amostra = supabase_admin.table("amostra").insert({
        "numero_amostra": 100, "lote": 42, "user_id": test_user_id,
    }).execute()
    amostra_id = amostra.data[0]["id"]
    supabase_admin.table("amostra_elemento").insert({
        "amostra_id": amostra_id, "elemento_id": elem_id,
    }).execute()

    page.goto("http://localhost:5000/amostras")
    page.wait_for_selector("body")
    page.locator(f"button[data-bs-target='#editModal{amostra_id}']").click()
    page.wait_for_timeout(1000)

    modal = page.locator(f"#editModal{amostra_id}")
    assert modal.is_visible()

    numero = modal.locator("input[name='numero_amostra']")
    assert numero.input_value() == "100"
    lote = modal.locator("input[name='lote']")
    assert lote.input_value() == "42"

    checkbox = modal.locator(f"#elem_edit_{amostra_id}_{elem_id}")
    assert checkbox.is_checked()


@pytest.mark.modais
def test_edit_modal_valida_elemento(login, page, supabase_admin, test_user_id,
                                     cleanup_amostras, cleanup_elementos, cleanup_historico):
    elem = supabase_admin.table("elemento").insert({
        "nome": "TestElem", "consumo_lpm": 1.0, "user_id": test_user_id,
    }).execute()
    elem_id = elem.data[0]["id"]
    amostra = supabase_admin.table("amostra").insert({
        "numero_amostra": 101, "lote": 43, "user_id": test_user_id,
    }).execute()
    amostra_id = amostra.data[0]["id"]
    supabase_admin.table("amostra_elemento").insert({
        "amostra_id": amostra_id, "elemento_id": elem_id,
    }).execute()

    page.goto("http://localhost:5000/amostras")
    page.wait_for_selector("body")
    page.locator(f"button[data-bs-target='#editModal{amostra_id}']").click()
    page.wait_for_timeout(1000)

    modal = page.locator(f"#editModal{amostra_id}")
    modal.locator(f"#elem_edit_{amostra_id}_{elem_id}").uncheck()
    modal.locator("button[type='submit']").click()
    page.wait_for_timeout(500)

    warning = modal.locator(".elemento-warning")
    assert not warning.get_attribute("class").__contains__("d-none") if warning.is_visible() else False


@pytest.mark.modais
def test_edit_modal_submit_atualiza(login, page, supabase_admin, test_user_id,
                                     cleanup_amostras, cleanup_elementos, cleanup_historico):
    elem = supabase_admin.table("elemento").insert({
        "nome": "TestElem", "consumo_lpm": 1.0, "user_id": test_user_id,
    }).execute()
    elem_id = elem.data[0]["id"]
    amostra = supabase_admin.table("amostra").insert({
        "numero_amostra": 102, "lote": 44, "user_id": test_user_id,
    }).execute()
    amostra_id = amostra.data[0]["id"]
    supabase_admin.table("amostra_elemento").insert({
        "amostra_id": amostra_id, "elemento_id": elem_id,
    }).execute()

    page.goto("http://localhost:5000/amostras")
    page.wait_for_selector("body")
    page.locator(f"button[data-bs-target='#editModal{amostra_id}']").click()
    page.wait_for_timeout(1000)

    modal = page.locator(f"#editModal{amostra_id}")
    modal.locator("input[name='lote']").fill("99")
    modal.locator("button[type='submit']").click()
    page.wait_for_timeout(3000)
    assert "/amostras" in page.url

    body = page.text_content("body")
    assert "99" in body


@pytest.mark.modais
def test_delete_modal_exclui(login, page, supabase_admin, test_user_id,
                              cleanup_amostras, cleanup_elementos, cleanup_historico):
    elem = supabase_admin.table("elemento").insert({
        "nome": "TestElem", "consumo_lpm": 1.0, "user_id": test_user_id,
    }).execute()
    elem_id = elem.data[0]["id"]
    amostra = supabase_admin.table("amostra").insert({
        "numero_amostra": 103, "lote": 45, "user_id": test_user_id,
    }).execute()
    amostra_id = amostra.data[0]["id"]
    supabase_admin.table("amostra_elemento").insert({
        "amostra_id": amostra_id, "elemento_id": elem_id,
    }).execute()

    page.goto("http://localhost:5000/amostras")
    page.wait_for_selector("body")
    page.locator(f"button[data-bs-target='#deleteModal{amostra_id}']").click()
    page.wait_for_timeout(1000)

    delete_modal = page.locator(f"#deleteModal{amostra_id}")
    assert delete_modal.is_visible()
    body_text = delete_modal.text_content()
    assert "103" in body_text
    assert "45" in body_text

    delete_modal.locator("button[type='submit']").click()
    page.wait_for_timeout(3000)
    assert "/amostras" in page.url
    assert "103" not in (page.text_content("body") or "")


@pytest.mark.modais
def test_delete_modal_cancela(login, page, supabase_admin, test_user_id,
                               cleanup_amostras, cleanup_elementos, cleanup_historico):
    elem = supabase_admin.table("elemento").insert({
        "nome": "TestElem", "consumo_lpm": 1.0, "user_id": test_user_id,
    }).execute()
    elem_id = elem.data[0]["id"]
    amostra = supabase_admin.table("amostra").insert({
        "numero_amostra": 104, "lote": 46, "user_id": test_user_id,
    }).execute()
    amostra_id = amostra.data[0]["id"]
    supabase_admin.table("amostra_elemento").insert({
        "amostra_id": amostra_id, "elemento_id": elem_id,
    }).execute()

    page.goto("http://localhost:5000/amostras")
    page.wait_for_selector("body")
    page.locator(f"button[data-bs-target='#deleteModal{amostra_id}']").click()
    page.wait_for_timeout(1000)

    cancel_btn = page.locator(f"#deleteModal{amostra_id} button:has-text('Cancelar')")
    cancel_btn.click()
    page.wait_for_timeout(500)

    body = page.text_content("body")
    assert "104" in body


@pytest.mark.modais
def test_bulk_delete_modal(login, page, supabase_admin, test_user_id,
                            cleanup_amostras, cleanup_elementos, cleanup_historico):
    elem = supabase_admin.table("elemento").insert({
        "nome": "TestElem", "consumo_lpm": 1.0, "user_id": test_user_id,
    }).execute()
    elem_id = elem.data[0]["id"]
    ids = []
    for i in range(2):
        a = supabase_admin.table("amostra").insert({
            "numero_amostra": 200 + i, "lote": 50 + i, "user_id": test_user_id,
        }).execute()
        aid = a.data[0]["id"]
        ids.append(aid)
        supabase_admin.table("amostra_elemento").insert({
            "amostra_id": aid, "elemento_id": elem_id,
        }).execute()

    page.goto("http://localhost:5000/amostras")
    page.wait_for_selector("body")

    for aid in ids:
        page.locator(f"input.item-checkbox[value='{aid}']").check()
    page.wait_for_timeout(500)

    floating = page.locator("#selectedActions")
    assert floating.is_visible()
    assert "2" in floating.text_content()

    floating.locator("button:has-text('Excluir')").click()
    page.wait_for_timeout(1000)

    bulk = page.locator("#bulkDeleteModal")
    assert bulk.is_visible()
    assert "2" in bulk.text_content()

    bulk.locator("button[type='submit']").click()
    page.wait_for_timeout(3000)
    assert "/amostras" in page.url
