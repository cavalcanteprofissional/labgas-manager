import pytest


def test_leitura_list_page_loads(login, page):
    page.goto("http://localhost:5000/leituras")
    page.wait_for_selector("body")
    assert "Leitura" in page.text_content("body")


def test_create_leitura(login, page, cleanup_leituras):
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


def test_create_leitura_with_existing_cilindro_elemento(login, page, supabase_admin, test_user_id, cleanup_leituras):
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
