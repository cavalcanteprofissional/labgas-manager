import pytest


def test_elemento_list_page_loads(login, page):
    page.goto("http://localhost:5000/elementos")
    page.wait_for_selector("body")
    text = page.text_content("body")
    assert "Elemento" in text


def test_create_elemento(login, page, cleanup_elementos):
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
