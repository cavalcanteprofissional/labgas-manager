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
