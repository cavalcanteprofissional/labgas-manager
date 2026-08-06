import pytest


def test_pressao_list_page_loads(login, page):
    page.goto("http://localhost:5000/pressoes")
    page.wait_for_selector("body")
    text = page.text_content("body")
    assert "Pressão" in text or "pressao" in text


def test_create_pressao(login, page, supabase_admin, test_user_id, cleanup_pressoes, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")

    cil = supabase_admin.table("cilindro").select("id").eq("user_id", test_user_id).limit(1).execute()
    if not cil.data:
        pytest.skip("No cilindro available")

    page.goto("http://localhost:5000/pressoes")
    page.wait_for_selector("body")

    page.locator("button:has-text('Nova'), a:has-text('Nova')").first.click()
    page.wait_for_timeout(1000)

    page.locator("select[name='cilindro_id']").first.select_option(str(cil.data[0]["id"]))
    page.locator("input[name='pressao']").first.fill("150")
    page.locator("input[name='temperatura']").first.fill("25")
    page.locator("input[name='data']").first.fill("2025-06-16")
    page.locator("input[name='hora']").first.fill("14:30")

    page.locator("button[type='submit']").first.click()
    page.wait_for_timeout(3000)
    assert "/pressoes" in page.url


def test_pressao_table_visible(login, page):
    page.goto("http://localhost:5000/pressoes")
    page.wait_for_selector("body")
    table = page.locator("table").first
    assert table.is_visible()


@pytest.mark.modais
def test_pressao_edit_modal_preenche_campos(login, page, supabase_admin, test_user_id,
                                             cleanup_pressoes, cleanup_cilindros, cleanup_historico):
    cil = supabase_admin.table("cilindro").insert({
        "numero": 801, "data_compra": "2025-01-01",
        "gas_kg": 10, "custo": 290, "status": "ativo",
        "user_id": test_user_id,
    }).execute()
    cil_id = cil.data[0]["id"]
    pr = supabase_admin.table("pressao").insert({
        "cilindro_id": cil_id, "pressao": 150.0,
        "temperatura": 25.0, "data": "2025-06-01",
        "hora": "14:30", "user_id": test_user_id,
    }).execute()
    pr_id = pr.data[0]["id"]

    page.goto("http://localhost:5000/pressoes?per_page=1000")
    page.wait_for_selector("body")
    page.locator(f"button[data-bs-target='#editModal{pr_id}']").click()
    page.wait_for_timeout(1000)

    modal = page.locator(f"#editModal{pr_id}")
    assert modal.is_visible()
    assert modal.locator("input[name='pressao']").input_value() == "150.0"
    assert modal.locator("input[name='temperatura']").input_value() == "25.0"
    assert modal.locator("select[name='cilindro_id']").input_value() == str(cil_id)


@pytest.mark.modais
def test_pressao_delete_modal_exclui(login, page, supabase_admin, test_user_id,
                                      cleanup_pressoes, cleanup_cilindros, cleanup_historico):
    cil = supabase_admin.table("cilindro").insert({
        "numero": 802, "data_compra": "2025-01-01",
        "gas_kg": 10, "custo": 290, "status": "ativo",
        "user_id": test_user_id,
    }).execute()
    cil_id = cil.data[0]["id"]
    pr = supabase_admin.table("pressao").insert({
        "cilindro_id": cil_id, "pressao": 200.0, "data": "2025-06-01",
        "hora": "10:00", "user_id": test_user_id,
    }).execute()
    pr_id = pr.data[0]["id"]

    page.goto("http://localhost:5000/pressoes?per_page=1000")
    page.wait_for_selector("body")
    page.locator(f"button[data-bs-target='#deleteModal{pr_id}']").click()
    page.wait_for_timeout(1000)

    delete_modal = page.locator(f"#deleteModal{pr_id}")
    assert delete_modal.is_visible()

    delete_modal.locator(f"button[form='deleteForm{pr_id}']").click()
    page.wait_for_timeout(3000)
    assert "/pressoes" in page.url

    result = supabase_admin.table("pressao").select("id").eq("id", pr_id).execute()
    assert not result.data


@pytest.mark.modais
def test_pressao_bulk_delete(login, page, supabase_admin, test_user_id,
                              cleanup_pressoes, cleanup_cilindros, cleanup_historico):
    cil = supabase_admin.table("cilindro").insert({
        "numero": 803, "data_compra": "2025-01-01",
        "gas_kg": 10, "custo": 290, "status": "ativo",
        "user_id": test_user_id,
    }).execute()
    cil_id = cil.data[0]["id"]
    ids = []
    for i in range(2):
        pr = supabase_admin.table("pressao").insert({
            "cilindro_id": cil_id, "pressao": 100 + i * 10,
            "data": "2025-06-01", "hora": "11:00",
            "user_id": test_user_id,
        }).execute()
        ids.append(pr.data[0]["id"])

    page.goto("http://localhost:5000/pressoes?per_page=1000")
    page.wait_for_selector("body")

    for pid in ids:
        page.locator(f"input.item-checkbox[value='{pid}']").check()
    page.wait_for_timeout(500)

    floating = page.locator("#selectedActions")
    assert floating.is_visible()

    floating.locator("button:has-text('Excluir')").click()
    page.wait_for_timeout(1000)

    bulk = page.locator("#bulkDeleteModal")
    assert bulk.is_visible()

    bulk.locator("button[type='submit']").click()
    page.wait_for_timeout(3000)
    assert "/pressoes" in page.url


def _criar_pressao_teste(supabase_admin, test_user_id, numero=801, pressao=150.0, data="2025-06-01"):
    cil = supabase_admin.table("cilindro").insert({
        "numero": numero, "data_compra": "2025-01-01",
        "gas_kg": 10, "custo": 290, "status": "ativo",
        "user_id": test_user_id,
    }).execute()
    cil_id = cil.data[0]["id"]
    pr = supabase_admin.table("pressao").insert({
        "cilindro_id": cil_id, "pressao": pressao,
        "temperatura": 25.0, "data": data,
        "hora": "14:30", "user_id": test_user_id,
    }).execute()
    return pr.data[0]["id"]


def test_pressao_filter_q_por_pressao(login, page, supabase_admin, test_user_id,
                                      cleanup_pressoes, cleanup_cilindros, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    pr_id = _criar_pressao_teste(supabase_admin, test_user_id, pressao=150.0)

    page.goto("http://localhost:5000/pressoes?q_pressao=150&per_page=1000")
    page.wait_for_selector("body")
    assert page.locator(f"button[data-bs-target='#editModal{pr_id}']").count() == 1


def test_pressao_filter_q_numero_normalizado(login, page, supabase_admin, test_user_id,
                                             cleanup_pressoes, cleanup_cilindros, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    pr_id = _criar_pressao_teste(supabase_admin, test_user_id, numero=801)

    page.goto("http://localhost:5000/pressoes?q_numero=801&per_page=1000")
    page.wait_for_selector("body")
    assert page.locator(f"button[data-bs-target='#editModal{pr_id}']").count() == 1


def test_pressao_filter_q_temperatura(login, page, supabase_admin, test_user_id,
                                      cleanup_pressoes, cleanup_cilindros, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    cil = supabase_admin.table("cilindro").insert({
        "numero": 801, "data_compra": "2025-01-01",
        "gas_kg": 10, "custo": 290, "status": "ativo",
        "user_id": test_user_id,
    }).execute()
    cil_id = cil.data[0]["id"]
    rows = {}
    for i, (pres, temp) in enumerate([(150.0, 25.0), (200.0, 30.0)]):
        pr = supabase_admin.table("pressao").insert({
            "cilindro_id": cil_id, "pressao": pres, "temperatura": temp,
            "data": "2025-06-01", "hora": f"15:0{i}", "user_id": test_user_id,
        }).execute()
        rows[temp] = pr.data[0]["id"]

    page.goto("http://localhost:5000/pressoes?q_temperatura=25&per_page=1000")
    page.wait_for_selector("body")
    assert page.locator(f"button[data-bs-target='#editModal{rows[25.0]}']").count() == 1
    assert page.locator(f"button[data-bs-target='#editModal{rows[30.0]}']").count() == 0


def test_pressao_filter_por_data(login, page, supabase_admin, test_user_id,
                                 cleanup_pressoes, cleanup_cilindros, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    pr_id = _criar_pressao_teste(supabase_admin, test_user_id, data="2025-06-01")

    page.goto("http://localhost:5000/pressoes?data_inicio=2025-06-01&data_fim=2025-06-01&per_page=1000")
    page.wait_for_selector("body")
    assert page.locator(f"button[data-bs-target='#editModal{pr_id}']").count() == 1


def test_pressao_temperatura_cor(login, page, supabase_admin, test_user_id,
                                 cleanup_pressoes, cleanup_cilindros, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    cil = supabase_admin.table("cilindro").insert({
        "numero": 801, "data_compra": "2025-01-01",
        "gas_kg": 10, "custo": 290, "status": "ativo",
        "user_id": test_user_id,
    }).execute()
    cil_id = cil.data[0]["id"]
    for i, temp in enumerate([25.0, 25.0, 50.0]):
        supabase_admin.table("pressao").insert({
            "cilindro_id": cil_id, "pressao": 150.0 + i, "temperatura": temp,
            "data": "2025-06-01", "hora": f"16:0{i}", "user_id": test_user_id,
        }).execute()

    page.goto("http://localhost:5000/pressoes?per_page=1000")
    page.wait_for_selector("body")
    fria = page.locator("td:has-text('25.0°C') span.badge")
    quente = page.locator("td:has-text('50.0°C') span.badge")
    assert fria.count() >= 1
    assert quente.count() >= 1
    assert "background" in (fria.first.get_attribute("style") or "")
    assert fria.first.get_attribute("style") != quente.first.get_attribute("style")


def test_pressao_pressao_cor(login, page, supabase_admin, test_user_id,
                             cleanup_pressoes, cleanup_cilindros, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")
    cil = supabase_admin.table("cilindro").insert({
        "numero": 801, "data_compra": "2025-01-01",
        "gas_kg": 10, "custo": 290, "status": "ativo",
        "user_id": test_user_id,
    }).execute()
    cil_id = cil.data[0]["id"]
    for i, pres in enumerate([100.0, 250.0, 250.0]):
        supabase_admin.table("pressao").insert({
            "cilindro_id": cil_id, "pressao": pres, "temperatura": 25.0,
            "data": "2025-06-01", "hora": f"17:0{i}", "user_id": test_user_id,
        }).execute()

    page.goto("http://localhost:5000/pressoes?per_page=1000")
    page.wait_for_selector("body")
    baixa = page.locator("td:has-text('100.0 bar') span.badge")
    alta = page.locator("td:has-text('250.0 bar') span.badge")
    assert baixa.count() >= 1
    assert alta.count() >= 1
    assert "background" in (baixa.first.get_attribute("style") or "")
    assert baixa.first.get_attribute("style") != alta.first.get_attribute("style")
