"""Componentes comuns da interface (módulo D02): capa gerada, cartões, avisos, vazio."""
import pytest


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('estes componentes são conferidos no desktop; a TV entra no módulo T02')


def test_item_sem_arte_mostra_a_capa_gerada_e_item_com_arte_nao(pagina, ir, biblioteca):
    ir(f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=0')
    pagina.locator('.card').first.wait_for()
    cartoes = {c.locator('.cardText-first').first.inner_text().strip(): c for c in pagina.locator('.card').all()}

    sem_arte = cartoes['Barras Direto (2001)']
    capa = sem_arte.locator('[data-testid="generated-cover"]')
    assert capa.count() == 1
    assert 'Barras' in capa.get_attribute('aria-label')
    # o quadrado da seção e as 7 barras
    assert capa.locator('rect').count() == 2 + 7

    com_arte = [c for n, c in cartoes.items() if n.startswith('Barras Com Arte')][0]
    assert com_arte.locator('[data-testid="generated-cover"]').count() == 0


def test_alternar_grade_e_lista(pagina, ir, biblioteca):
    ir(f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=0')
    alternador = pagina.locator('[data-testid="view-mode-toggle"]')
    alternador.wait_for()
    grade, lista = alternador.locator('button').nth(0), alternador.locator('button').nth(1)
    assert grade.get_attribute('aria-pressed') == 'true'
    lista.click()
    pagina.wait_for_selector('.listItem')
    assert lista.get_attribute('aria-pressed') == 'true'
    assert pagina.locator('.card').count() == 0
    grade.click()
    pagina.locator('.card').first.wait_for()
    assert grade.get_attribute('aria-pressed') == 'true'
