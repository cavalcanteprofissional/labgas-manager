import os
import sys
import subprocess
import time
import logging
import signal

import pytest
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env.local"))

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:5000")
TEST_EMAIL = os.getenv("TEST_EMAIL", "teste@labgas.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "123456")


def ensure_test_user():
    from supabase import create_client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        logger.warning("SUPABASE_URL or SUPABASE_SERVICE_KEY not set, skipping user creation")
        return

    admin = create_client(url, key)
    result = admin.table("perfil").select("id").eq("email", TEST_EMAIL).execute()
    if result.data:
        logger.info(f"Test user {TEST_EMAIL} already exists")
        return

    try:
        auth_admin = create_client(url, key)
        auth_admin.auth.admin.create_user({
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "email_confirm": True,
        })
        user_resp = auth_admin.auth.admin.get_user_by_email(TEST_EMAIL)
        user_id = user_resp.user.id if user_resp.user else None
        if user_id:
            admin.table("perfil").insert({
                "id": user_id,
                "email": TEST_EMAIL,
                "role": "admin",
                "ativo": True,
                "nome": "Usuario Teste",
                "habilitar_abas": {"cilindro": True, "pressao": True, "elemento": True, "leitura": True, "amostra": True, "historico": True},
            }).execute()
            logger.info(f"Test user {TEST_EMAIL} created with id {user_id}")
    except Exception as e:
        logger.warning(f"Could not create test user: {e}")


ensure_test_user()


def is_port_open(port, host="127.0.0.1"):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


@pytest.fixture(scope="session")
def flask_app():
    if is_port_open(5000):
        logger.info("Flask already running on port 5000, reusing")
        yield None
        return

    env = os.environ.copy()
    env["FLASK_DEBUG"] = "0"
    env["PYTHONUNBUFFERED"] = "1"
    env["RATE_LIMIT"] = "10000 per hour"

    proc = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=os.path.join(os.path.dirname(__file__), ".."),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    logger.info("Starting Flask server...")
    for i in range(60):
        if is_port_open(5000):
            logger.info(f"Flask ready after {i*0.5:.1f}s")
            break
        if i % 10 == 0 and i > 0:
            logger.info(f"Waiting for Flask... ({i*0.5:.0f}s)")
        time.sleep(0.5)
    else:
        proc.kill()
        raise RuntimeError("Flask app did not start within 30s")

    yield

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture(scope="session")
def browser_context_args():
    return {
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture
def page(page, flask_app):
    page.set_default_timeout(20000)
    return page


@pytest.fixture
def login(page):
    logger.info(f"Logging in as {TEST_EMAIL}")
    page.context.clear_cookies()
    page.goto(f"{BASE_URL}/login", wait_until="networkidle")
    page.wait_for_selector("input[name='email']", timeout=10000)
    page.fill("input[name='email']", TEST_EMAIL)
    page.fill("input[name='password']", TEST_PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_timeout(5000)
    if "/dashboard" not in page.url:
        page.goto(f"{BASE_URL}/dashboard")
        page.wait_for_timeout(2000)
    return page


@pytest.fixture
def supabase_admin():
    from utils.supabase_utils import get_admin_client
    return get_admin_client()


@pytest.fixture
def test_user_id(supabase_admin):
    result = supabase_admin.table("perfil").select("id").eq("email", TEST_EMAIL).execute()
    if result.data:
        return result.data[0]["id"]
    return None


@pytest.fixture
def cleanup_leituras(supabase_admin, test_user_id):
    yield
    if test_user_id:
        supabase_admin.table("leitura").delete().eq("user_id", test_user_id).neq("id", 0).execute()


@pytest.fixture
def cleanup_cilindros(supabase_admin, test_user_id):
    yield
    if test_user_id:
        supabase_admin.table("cilindro").delete().eq("user_id", test_user_id).neq("id", 0).execute()


@pytest.fixture
def cleanup_elementos(supabase_admin, test_user_id):
    yield
    if test_user_id:
        supabase_admin.table("elemento").delete().eq("user_id", test_user_id).neq("id", 0).execute()


@pytest.fixture
def cleanup_pressoes(supabase_admin, test_user_id):
    yield
    if test_user_id:
        supabase_admin.table("pressao").delete().eq("user_id", test_user_id).neq("id", 0).execute()


@pytest.fixture
def cleanup_amostras(supabase_admin, test_user_id):
    yield
    if test_user_id:
        supabase_admin.table("amostra_elemento").delete().neq("id", 0).execute()
        supabase_admin.table("amostra").delete().eq("user_id", test_user_id).neq("id", 0).execute()


@pytest.fixture
def cleanup_historico(supabase_admin, test_user_id):
    yield
    if test_user_id:
        supabase_admin.table("historico_log").delete().eq("user_id", test_user_id).neq("id", 0).execute()
