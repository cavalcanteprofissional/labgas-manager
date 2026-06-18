import requests
import pytest

pytestmark = pytest.mark.export

BASE = "http://localhost:5000"


def _get_session_token(page):
    """Extract session cookie/token from logged-in Playwright page."""
    cookies = page.context.cookies()
    for c in cookies:
        if c["name"] == "session":
            return c["value"]
    return None


def test_export_json_downloads(login, page):
    token = _get_session_token(page)
    cookies = {"session": token} if token else {}
    resp = requests.get(f"{BASE}/admin/export?formato=json", cookies=cookies)
    assert resp.ok
    cd = resp.headers.get("Content-Disposition", "")
    assert cd.endswith(".json")
    assert "labgas_export" in cd
    data = resp.json()
    assert "kpis" in data
    assert "exportado_por" in data
    assert len(data.get("cilindros", [])) >= 0


def test_export_csv_downloads(login, page):
    token = _get_session_token(page)
    cookies = {"session": token} if token else {}
    resp = requests.get(f"{BASE}/admin/export?formato=csv", cookies=cookies)
    assert resp.ok
    cd = resp.headers.get("Content-Disposition", "")
    assert cd.endswith(".csv")
    assert "labgas_export" in cd
    assert "CILINDROS" in resp.text


def test_export_md_downloads(login, page):
    token = _get_session_token(page)
    cookies = {"session": token} if token else {}
    resp = requests.get(f"{BASE}/admin/export?formato=md", cookies=cookies)
    assert resp.ok
    cd = resp.headers.get("Content-Disposition", "")
    assert cd.endswith(".md")
    assert "labgas_export" in cd
    assert "Cilindros" in resp.text
    assert "KPIs" in resp.text


def test_export_excel_downloads(login, page):
    token = _get_session_token(page)
    cookies = {"session": token} if token else {}
    resp = requests.get(f"{BASE}/admin/export?formato=excel", cookies=cookies)
    assert resp.ok
    cd = resp.headers.get("Content-Disposition", "")
    assert cd.endswith(".xlsx")
    assert "labgas_export" in cd


def test_export_redirects_if_not_admin(page):
    page.goto(f"{BASE}/logout")
    page.wait_for_timeout(1000)
    page.goto(f"{BASE}/admin/export?formato=json")
    page.wait_for_timeout(2000)
    assert "/dashboard" in page.url or "/login" in page.url
