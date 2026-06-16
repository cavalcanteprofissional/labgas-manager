import pytest


def test_cilindro_list_page_loads(login, page):
    page.goto("http://localhost:5000/cilindros")
    page.wait_for_selector("body")
    text = page.text_content("body")
    assert "Cilindro" in text


def test_create_cilindro(login, page, cleanup_cilindros):
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
