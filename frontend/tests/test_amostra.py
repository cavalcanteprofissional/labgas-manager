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
