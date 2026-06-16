import os
import pytest

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:5000")
TEST_EMAIL = os.getenv("TEST_EMAIL", "teste@labgas.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "123456")


def test_redirect_to_login_when_unauthenticated(page):
    page.goto(f"{BASE_URL}/dashboard", wait_until="networkidle")
    page.wait_for_timeout(2000)
    assert "/login" in page.url


def test_login_page_has_required_elements(page, flask_app):
    page.goto(f"{BASE_URL}/login", wait_until="networkidle")
    page.wait_for_timeout(2000)
    body = page.text_content("body")
    assert "Email" in body or "email" in body, f"Login page content: {body[:200]}"
    email = page.locator("input[name='email']")
    assert email.is_visible(), f"Email input not visible. URL: {page.url}"
    assert page.locator("input[name='password']").is_visible()
    assert page.locator("button[type='submit']").is_visible()


def test_login_success(page):
    page.goto(f"{BASE_URL}/login")
    page.fill("input[name='email']", TEST_EMAIL)
    page.fill("input[name='password']", TEST_PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_timeout(5000)
    assert "/dashboard" in page.url


def test_login_invalid_credentials(page):
    page.goto(f"{BASE_URL}/login")
    page.fill("input[name='email']", "invalido@email.com")
    page.fill("input[name='password']", "senha_errada")
    page.click("button[type='submit']")
    page.wait_for_timeout(2000)
    assert "/login" in page.url


def test_login_empty_fields(page):
    page.goto(f"{BASE_URL}/login")
    page.click("button[type='submit']")
    page.wait_for_timeout(1000)
    assert "/login" in page.url


def test_logout(login, page):
    page.goto(f"{BASE_URL}/dashboard")
    page.wait_for_selector("a[href*='logout'], button:has-text('Sair')", timeout=5000)
    page.click("a[href*='logout'], button:has-text('Sair')")
    page.wait_for_timeout(3000)
    assert "/login" in page.url


def test_dashboard_accessible_after_login(login, page):
    assert "/dashboard" in page.url
    assert page.locator(".stat-card").count() >= 3
