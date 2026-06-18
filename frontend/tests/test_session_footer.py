import os
import re
import pytest

TEST_EMAIL = os.getenv("TEST_EMAIL", "teste@labgas.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "123456")

pytestmark = pytest.mark.footer


def login(page, base_url):
    page.goto(f"{base_url}/login")
    page.fill("input[name='email']", TEST_EMAIL)
    page.fill("input[name='password']", TEST_PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_url(f"{base_url}/dashboard")


def test_footer_visible_after_login(page, base_url):
    login(page, base_url)
    footer = page.locator("footer.session-footer")
    assert footer.is_visible()
    assert footer.locator(".bi-person-circle").is_visible()
    assert footer.locator(".bi-clock-history").is_visible()


def test_footer_shows_user_name(page, base_url):
    login(page, base_url)
    name_el = page.locator("footer.session-footer span.small").first
    text = name_el.text_content()
    assert text and text.strip(), "User name should not be empty"


def test_footer_has_countdown_timer(page, base_url):
    login(page, base_url)
    timer = page.locator("#session-timer")
    assert timer.is_visible()
    text = timer.text_content()
    assert re.match(r"^\d+:\d{2}$", text.strip()), (
        f"Timer should show MM:SS format, got '{text}'"
    )


def test_footer_not_visible_on_login_page(page, base_url):
    page.goto(f"{base_url}/login")
    footer = page.locator("footer.session-footer")
    assert footer.is_hidden()
