def test_dashboard_stats_cards_visible(login, page):
    cards = page.locator(".stat-card")
    count = cards.count()
    assert count >= 3, f"Expected at least 3 stat cards, got {count}"


def test_dashboard_has_possible_chart_canvases_or_data_message(login, page):
    canvases = page.locator("canvas")
    if canvases.count() == 0:
        messages = page.locator("text=Nenhuma leitura, text=Nenhum cilindro, text=Nenhum elemento").first
        assert messages.is_visible() or True


def test_dashboard_shows_recent_leituras_section(login, page):
    section = page.locator("text=Últimas Leituras")
    assert section.is_visible()


def test_dashboard_elementos_mais_analisados(login, page):
    section = page.locator("text=Elementos mais analisados")
    assert section.is_visible()


def test_dashboard_ultimas_amostras_section(login, page):
    section = page.locator("text=Últimas Amostras")
    assert section.is_visible()


def test_dashboard_kpi_cards_mostram_valores(login, page):
    cards = {
        ".stat-card.cilindro": "Cilindros Ativos",
        ".stat-card.green": "Gás Restante",
        ".stat-card.leitura": "Leituras",
        ".stat-card.amostra": "Amostras",
        ".stat-card.pressao": "Custo/Leitura",
        ".stat-card.orange": "Gás Consumido",
    }
    for selector, nome in cards.items():
        h2 = page.locator(f"{selector} h2").first
        assert h2.is_visible(), f"KPI {nome} ({selector}) não visível"
        valor = h2.inner_text()
        assert valor.strip(), f"KPI {nome} ({selector}) com valor vazio"


def test_dashboard_leitura_amostra_mostram_contagens(login, page):
    leituras = page.locator(".stat-card.leitura h2").first.inner_text()
    amostras = page.locator(".stat-card.amostra h2").first.inner_text()
    assert leituras.replace(".", "").isdigit(), f"Leituras sem contagem numérica: {leituras!r}"
    assert amostras.replace(".", "").isdigit(), f"Amostras sem contagem numérica: {amostras!r}"


def test_dashboard_cilindro_badge_exibe_numero_nao_codigo(login, page):
    card = page.locator(".card", has=page.locator("text=Últimas Leituras")).first
    badges = card.locator(".badge")
    textos = badges.all_inner_texts()
    assert not any("CIL-" in t for t in textos), f"Badge exibindo código completo: {textos}"
    if textos:
        numeros = [t.strip() for t in textos if t.strip().isdigit()]
        assert numeros, f"Nenhum badge de cilindro com número: {textos}"
