"""Documentários (módulo D05): filmes e séries documentais numa aba só."""
import pytest

TABS = '.MuiTabs-root [role="tab"]'


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV entra no módulo T04')


def _abrir(pagina, ir, biblioteca):
    ir(f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=0')
    pagina.locator(TABS, has_text='Documentários').click()
    pagina.locator('[data-testid="grouped-items"] .card').first.wait_for()


def test_uma_aba_so_para_documentarios(pagina, ir, biblioteca):
    ir(f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=0')
    abas = [t.strip() for t in pagina.locator(TABS).all_inner_texts()]
    assert abas.count('Documentários') == 1
    assert not any('Documentários (' in a for a in abas)


def test_filme_e_serie_documentais_na_mesma_grade_com_etiqueta(pagina, ir, biblioteca):
    _abrir(pagina, ir, biblioteca)
    cartoes = pagina.locator('[data-testid="grouped-items"] .card')
    assert cartoes.count() == 2          # 1 filme documental + 1 série documental
    etiquetas = sorted(c.locator('.cardImageContainer[data-kind-label]').get_attribute('data-kind-label') for c in cartoes.all())
    assert etiquetas == ['Filme', 'Série']
    assert pagina.locator(TABS + '[aria-selected="true"]').inner_text().strip() == 'Documentários'


def test_filme_documental_nao_aparece_em_filmes(pagina, ir, biblioteca):
    ir(f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=0')
    pagina.locator('.card').first.wait_for()
    nomes = ' '.join(pagina.locator('.card .cardText-first').all_inner_texts())
    assert 'Documental' not in nomes


def test_visual_da_aba_documentarios(pagina, ir, biblioteca, conferir):
    _abrir(pagina, ir, biblioteca)
    pagina.wait_for_timeout(500)
    conferir('grade-documentarios')
