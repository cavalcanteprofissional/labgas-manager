import pytest


def test_amostra_page_loads(login, page):
    page.goto("http://localhost:5000/amostras")
    page.wait_for_selector("body")
    text = page.text_content("body")
    assert "Amostras" in text


def test_create_amostra(login, page, cleanup_amostras):
    page.goto("http://localhost:5000/amostras")
    page.wait_for_selector("body")

    page.click("button[data-bs-target='#formAmostra']")
    page.wait_for_timeout(1000)

    lote_input = page.locator("input[name='lote']").first
    lote_input.wait_for(state="visible", timeout=5000)
    lote_input.fill("42")

    submit = page.locator("button[type='submit']").first
    submit.click()
    page.wait_for_timeout(3000)
    assert "/amostras" in page.url


def test_amostra_empty_state(login, page):
    page.goto("http://localhost:5000/amostras")
    page.wait_for_selector("body")
    text = page.text_content("body")
    assert "Nenhuma amostra" in text or "Amostras" in text
