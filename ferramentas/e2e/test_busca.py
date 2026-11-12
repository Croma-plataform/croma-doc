"""Busca (módulo D09)."""
import pytest


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV entra no módulo T05')


def test_resultados_agrupados_por_secao(pagina, ir):
    ir('search?query=Barras', espera=2500)
    grupos = pagina.locator('[data-testid="search-group"]')
    grupos.first.wait_for()
    chaves = [g.get_attribute('data-group') for g in grupos.all()]
    assert chaves[0] == 'Audiovisual'
    assert 'Audiovisual' in chaves
    cabecalho = pagina.locator('[data-testid="search-group-header"]').first.inner_text().strip().upper()
    assert cabecalho == 'AUDIOVISUAL'


def test_busca_sem_resultado(pagina, ir, conferir):
    ir('search?query=zzzxyz', espera=2500)
    vazio = pagina.locator('[data-testid="search-empty"]')
    vazio.wait_for()
    assert 'Nada com “zzzxyz”' in vazio.inner_text()
    assert vazio.locator('.cromaChip').count() >= 4
    conferir('busca-vazia')


def test_ctrl_k_abre_a_busca_de_qualquer_tela(pagina, ir):
    ir('home')
    pagina.keyboard.press('Control+k')
    pagina.wait_for_url('**/search**')
    pagina.wait_for_selector('#searchTextInput')
    assert pagina.evaluate('document.activeElement.id') == 'searchTextInput'


def test_abrir_um_resultado_e_voltar(pagina, ir):
    ir('search?query=Barras', espera=2500)
    pagina.locator('.searchResults .card .cardText-first a').first.click()
    pagina.wait_for_url('**/details**')
    pagina.go_back()
    pagina.wait_for_url('**/search?query=Barras**')
    pagina.locator('[data-testid="search-group"]').first.wait_for()


def test_visual_da_busca_com_resultados(pagina, ir, conferir):
    ir('search?query=Barras', espera=3000)
    pagina.locator('[data-testid="search-group"]').first.wait_for()
    pagina.wait_for_timeout(500)
    conferir('busca-resultados')
