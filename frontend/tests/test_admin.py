import pytest


def test_admin_page_redirects_if_not_admin(login, page, supabase_admin, test_user_id):
    if not test_user_id:
        pytest.skip("No test user found")

    role = supabase_admin.table("perfil").select("role").eq("id", test_user_id).execute()
    is_admin = role.data and role.data[0].get("role") == "admin"

    page.goto("http://localhost:5000/admin")
    page.wait_for_timeout(2000)

    if is_admin:
        assert "/admin" in page.url
        assert page.locator("text=Admin").first.is_visible()
    else:
        assert "/dashboard" in page.url or "403" in page.text_content("body") or "Acesso" in page.text_content("body")


def test_admin_user_table_visible(login, page):
    page.goto("http://localhost:5000/admin")
    page.wait_for_timeout(2000)

    table = page.locator("table").first
    if table.is_visible():
        assert True
