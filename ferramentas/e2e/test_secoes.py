"""Seções na barra lateral e abas do cabeçalho (só no desktop: o menu da TV é o módulo T03)."""
import pytest

TABS = '.MuiTabs-root [role="tab"]'


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV ainda usa o menu de bibliotecas do Jellyfin (módulo T03)')


def test_barra_lateral_lista_as_quatro_secoes(pagina, ir):
    ir('home')
    gaveta = pagina.locator('.MuiDrawer-root')
    textos = gaveta.inner_text()
    for secao in ('Audiovisual', 'Áudios', 'Leitura', 'Fotos'):
        assert secao in textos, secao


def test_secao_ativa_abre_os_subtipos(pagina, ir, biblioteca):
    filmes = biblioteca('Filmes')
    ir(f'movies?topParentId={filmes["id"]}&collectionType=movies&tab=1')
    gaveta = pagina.locator('.MuiDrawer-root').inner_text()

    for nome in ('Filmes', 'Séries', 'Documentários (filmes)', 'Documentários (séries)'):
        assert nome in gaveta, nome
    assert 'Músicas' not in gaveta      # os subtipos de Áudios só abrem na seção Áudios


def test_abas_do_cabecalho(pagina, ir, biblioteca):
    filmes = biblioteca('Filmes')
    ir(f'movies?topParentId={filmes["id"]}&collectionType=movies&tab=1')

    abas = [t.strip() for t in pagina.locator(TABS).all_inner_texts()]
    assert abas[0] == 'Resumo'
    assert abas[-2:] == ['Coleções', 'Gêneros']
    assert 'Filmes' in abas and 'Séries' in abas
    assert pagina.locator(TABS + '[aria-selected="true"]').inner_text().strip() == 'Resumo'


def test_aba_de_series_abre_a_grade_de_series(pagina, ir, biblioteca):
    filmes = biblioteca('Filmes')
    ir(f'movies?topParentId={filmes["id"]}&collectionType=movies&tab=1')

    pagina.locator(TABS, has_text='Séries').first.click()
    pagina.wait_for_url('**/tv?**')
    assert f'topParentId={biblioteca("Séries")["id"]}' in pagina.url


def test_clicar_na_secao_abre_a_primeira_biblioteca(pagina, ir):
    ir('home')
    pagina.locator('.MuiDrawer-root a', has_text='Audiovisual').first.click()
    pagina.wait_for_url('**/movies?**')


def test_visual_da_grade_de_filmes(pagina, ir, biblioteca, conferir):
    ir(f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=0')
    conferir('grade-filmes')
