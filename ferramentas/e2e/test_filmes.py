"""Filmes (módulo D03): grade com filtros."""
import pytest


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV usa a grade própria (módulo T04)')


def _abrir_grade(pagina, ir, biblioteca):
    ir(f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=0')
    pagina.locator('.card').first.wait_for()


def _filtro_resolucao(pagina, rotulo):
    pagina.locator('button[title="Filtro"]').first.click()
    pagina.locator('#filtersVideoTypes-header').click()
    pagina.get_by_label(rotulo, exact=True).click()
    pagina.keyboard.press('Escape')
    pagina.wait_for_timeout(1500)


def test_filtro_de_resolucao_tem_o_nome_certo(pagina, ir, biblioteca):
    _abrir_grade(pagina, ir, biblioteca)
    pagina.locator('button[title="Filtro"]').first.click()
    assert 'Resolução' in pagina.locator('#filtersVideoTypes-header').inner_text()


def test_filtro_sd_mostra_os_filmes_de_640x360(pagina, ir, biblioteca):
    _abrir_grade(pagina, ir, biblioteca)
    total = pagina.locator('.card').count()
    _filtro_resolucao(pagina, 'SD')
    assert pagina.locator('.card').count() == total


def test_filtro_4k_nao_mostra_nada_na_midia_de_teste(pagina, ir, biblioteca):
    _abrir_grade(pagina, ir, biblioteca)
    _filtro_resolucao(pagina, '4K')
    assert pagina.locator('.card').count() == 0
    assert pagina.locator('[data-testid="empty-state"]').count() == 1


def test_galeria_tem_colunas_de_160_px(pagina, ir, biblioteca):
    _abrir_grade(pagina, ir, biblioteca)
    largura = pagina.locator('.card .cardScalable').first.evaluate('e => e.getBoundingClientRect().width')
    assert abs(largura - 160) <= 2, largura
