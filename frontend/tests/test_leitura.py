import pytest


def test_leitura_list_page_loads(login, page):
    page.goto("http://localhost:5000/leituras")
    page.wait_for_selector("body")
    assert "Leitura" in page.text_content("body")


def test_create_leitura(login, page, cleanup_leituras, cleanup_historico):
    page.goto("http://localhost:5000/leituras")
    page.wait_for_selector("body")

    add_btn = page.locator("button:has-text('Nova'), a:has-text('Nova'), button:has-text('Adicionar')").first
    if add_btn.is_visible():
        add_btn.click()
        page.wait_for_timeout(1000)

    page.locator("input[name='data']").first.fill("2025-06-16")
    page.locator("input[name='tempo_chama']").first.fill("00:30:00")

    submit = page.locator("button[type='submit']").first
    submit.click()
    page.wait_for_timeout(3000)
    assert "/leituras" in page.url


def test_create_leitura_with_existing_cilindro_elemento(login, page, supabase_admin, test_user_id, cleanup_leituras, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")

    cil = supabase_admin.table("cilindro").select("id,codigo").eq("user_id", test_user_id).limit(1).execute()
    elem = supabase_admin.table("elemento").select("id,nome").eq("user_id", test_user_id).limit(1).execute()

    if not cil.data or not elem.data:
        pytest.skip("No cilindro/elemento available for test user")

    page.goto("http://localhost:5000/leituras")
    page.wait_for_selector("body")

    add_btn = page.locator("button:has-text('Nova'), a:has-text('Nova'), button:has-text('Adicionar')").first
    if add_btn.is_visible():
        add_btn.click()
        page.wait_for_timeout(1000)

    page.locator("input[name='data']").first.fill("2025-06-16")
    page.locator("input[name='tempo_chama']").first.fill("00:30:00")
    page.locator("select[name='cilindro_id']").first.select_option(str(cil.data[0]["id"]))
    page.locator("select[name='elemento_id']").first.select_option(str(elem.data[0]["id"]))
    page.locator("input[name='quantidade']").first.fill("2")

    submit = page.locator("button[type='submit']").first
    submit.click()
    page.wait_for_timeout(3000)
    assert "/leituras" in page.url


def test_leituras_page_structure(login, page):
    page.goto("http://localhost:5000/leituras")
    page.wait_for_selector("body")
    assert "Leitura" in page.text_content("body")


def test_bulk_delete_button_not_required(login, page):
    page.goto("http://localhost:5000/leituras")
    page.wait_for_selector("body")


@pytest.mark.modais
def test_leitura_edit_modal_preenche_campos(login, page, supabase_admin, test_user_id,
                                             cleanup_leituras, cleanup_cilindros, cleanup_elementos, cleanup_historico):
    cil = supabase_admin.table("cilindro").insert({
        "codigo": "CIL-LT", "data_compra": "2025-01-01",
        "gas_kg": 10, "custo": 290, "status": "ativo",
        "user_id": test_user_id,
    }).execute()
    cil_id = cil.data[0]["id"]
    el = supabase_admin.table("elemento").insert({
        "nome": "LeituraElem", "consumo_lpm": 2.0, "user_id": test_user_id,
    }).execute()
    el_id = el.data[0]["id"]
    lei = supabase_admin.table("leitura").insert({
        "data": "2025-06-01", "tempo_chama": "01:30:00",
        "cilindro_id": cil_id, "elemento_id": el_id,
        "quantidade": 5, "user_id": test_user_id,
    }).execute()
    lei_id = lei.data[0]["id"]

    page.goto("http://localhost:5000/leituras?per_page=1000")
    page.wait_for_selector("body")
    page.locator(f"button[data-bs-target='#editModal{lei_id}']").click()
    page.wait_for_timeout(1000)

    modal = page.locator(f"#editModal{lei_id}")
    assert modal.is_visible()
    assert modal.locator("input[name='quantidade']").input_value() == "5"
    assert modal.locator("select[name='cilindro_id']").input_value() == str(cil_id)
    assert modal.locator("select[name='elemento_id']").input_value() == str(el_id)


@pytest.mark.modais
def test_leitura_delete_modal_exclui(login, page, supabase_admin, test_user_id,
                                      cleanup_leituras, cleanup_cilindros, cleanup_elementos, cleanup_historico):
    cil = supabase_admin.table("cilindro").insert({
        "codigo": "CIL-LD", "data_compra": "2025-01-01",
        "gas_kg": 10, "custo": 290, "status": "ativo",
        "user_id": test_user_id,
    }).execute()
    cil_id = cil.data[0]["id"]
    el = supabase_admin.table("elemento").insert({
        "nome": "DelLeitura", "consumo_lpm": 1.0, "user_id": test_user_id,
    }).execute()
    el_id = el.data[0]["id"]
    lei = supabase_admin.table("leitura").insert({
        "data": "2025-06-01", "tempo_chama": "00:15:00",
        "cilindro_id": cil_id, "elemento_id": el_id,
        "quantidade": 1, "user_id": test_user_id,
    }).execute()
    lei_id = lei.data[0]["id"]

    page.goto("http://localhost:5000/leituras?per_page=1000")
    page.wait_for_selector("body")
    page.locator(f"button[data-bs-target='#deleteModal{lei_id}']").click()
    page.wait_for_timeout(1000)

    delete_modal = page.locator(f"#deleteModal{lei_id}")
    assert delete_modal.is_visible()

    delete_modal.locator(f"button[form='deleteForm{lei_id}']").click()
    page.wait_for_timeout(3000)
    assert "/leituras" in page.url

    result = supabase_admin.table("leitura").select("id").eq("id", lei_id).execute()
    assert not result.data


@pytest.mark.modais
def test_leitura_bulk_delete(login, page, supabase_admin, test_user_id,
                              cleanup_leituras, cleanup_cilindros, cleanup_elementos, cleanup_historico):
    cil = supabase_admin.table("cilindro").insert({
        "codigo": "CIL-LB", "data_compra": "2025-01-01",
        "gas_kg": 10, "custo": 290, "status": "ativo",
        "user_id": test_user_id,
    }).execute()
    cil_id = cil.data[0]["id"]
    el = supabase_admin.table("elemento").insert({
        "nome": "BulkLeitura", "consumo_lpm": 1.0, "user_id": test_user_id,
    }).execute()
    el_id = el.data[0]["id"]
    ids = []
    for i in range(2):
        lei = supabase_admin.table("leitura").insert({
            "data": "2025-06-01", "tempo_chama": "00:10:00",
            "cilindro_id": cil_id, "elemento_id": el_id,
            "quantidade": i + 1, "user_id": test_user_id,
        }).execute()
        ids.append(lei.data[0]["id"])

    page.goto("http://localhost:5000/leituras?per_page=1000")
    page.wait_for_selector("body")

    for lid in ids:
        page.locator(f"input.item-checkbox[value='{lid}']").check()
    page.wait_for_timeout(500)

    floating = page.locator("#selectedActions")
    assert floating.is_visible()

    floating.locator("button:has-text('Excluir')").click()
    page.wait_for_timeout(1000)

    bulk = page.locator("#bulkDeleteModal")
    assert bulk.is_visible()

    bulk.locator("button[type='submit']").click()
    page.wait_for_timeout(3000)
    assert "/leituras" in page.url
