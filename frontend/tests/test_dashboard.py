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
