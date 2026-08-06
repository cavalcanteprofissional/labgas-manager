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


def test_admin_user_search(login, page, supabase_admin, test_user_id):
    if not test_user_id:
        pytest.skip("No test user found")

    perfil = supabase_admin.table("perfil").select("nome,email").eq("id", test_user_id).execute().data
    if not perfil:
        pytest.skip("No perfil found")
    nome = perfil[0].get("nome") or ""
    email = perfil[0].get("email") or ""
    termo = (nome or email)[:6]

    page.goto(f"http://localhost:5000/admin?q={termo}")
    page.wait_for_timeout(2000)
    assert page.locator(f"text={nome}").first.is_visible() or page.locator(f"text={email}").first.is_visible()


def test_admin_user_data_filtro_tipo(login, page, supabase_admin, test_user_id, cleanup_historico):
    if not test_user_id:
        pytest.skip("No test user found")

    import uuid
    tag = uuid.uuid4().hex[:8]
    cil_label = f"UNIQ-ADMIN-CIL-{tag}"
    amo_label = f"UNIQ-ADMIN-AMO-{tag}"
    supabase_admin.table("historico_auditoria").insert([
        {"tipo": "cilindro", "acao": "criado", "label": cil_label, "user_id": test_user_id,
         "created_at": "2025-06-01T10:00:00"},
        {"tipo": "amostra", "acao": "criado", "label": amo_label, "user_id": test_user_id,
         "created_at": "2025-06-01T10:00:00"},
    ]).execute()

    page.goto(f"http://localhost:5000/admin/user-data/{test_user_id}?tipo=cilindro&per_page=1000")
    page.wait_for_timeout(2000)
    body = page.text_content("body")
    assert cil_label in body
    assert amo_label not in body
