"""Coleções (módulo D10): cada coleção pertence a uma biblioteca (`specs/colecoes.md`, servidor S04)."""
import urllib.error
from urllib.parse import quote

import pytest

TABS = '.MuiTabs-root [role="tab"]'


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV entra no módulo T04')


@pytest.fixture
def colecoes(api_admin, biblioteca, estado):
    """Uma coleção de Filmes e outra de Músicas, cada uma já com um item da própria biblioteca."""
    filme = next(v for k, v in estado['itens'].items() if k.startswith('Movie:'))
    faixa = next(v for k, v in estado['itens'].items() if k.startswith('Audio:'))
    criadas = {}
    for nome, biblioteca_dona, item in (('Saga E2E', 'Filmes', filme), ('Discos E2E', 'Músicas', faixa)):
        criadas[nome] = api_admin(
            f'Collections?name={nome.replace(" ", "%20")}&ownerLibraryId={biblioteca(biblioteca_dona)["id"]}&ids={item}',
            metodo='POST')['Id']
    yield criadas
    for id_ in criadas.values():
        api_admin(f'Items/{id_}', metodo='DELETE')
    # criar a primeira coleção cria a biblioteca "Coleções" do servidor; sem ela o painel das outras telas muda
    for pasta in api_admin('Library/VirtualFolders'):
        if pasta.get('CollectionType') == 'boxsets':
            api_admin(f'Library/VirtualFolders?name={quote(pasta["Name"])}&refreshLibrary=false', metodo='DELETE')


def test_aba_colecoes_lista_so_as_da_biblioteca(pagina, ir, biblioteca, colecoes):
    ir(f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=0')
    pagina.locator(TABS, has_text='Coleções').click()
    pagina.locator('.card', has_text='Saga E2E').wait_for()
    nomes = pagina.locator('.card .cardText-first').all_inner_texts()
    assert 'Saga E2E' in nomes and 'Discos E2E' not in nomes


def test_adicionar_a_colecao_lista_so_as_do_dono_do_item(api_admin, estado, colecoes):
    filme = next(v for k, v in estado['itens'].items() if k.startswith('Movie:'))
    nomes = {c['Name'] for c in api_admin(f'Collections?itemId={filme}')['Items']}
    assert 'Saga E2E' in nomes and 'Discos E2E' not in nomes


def test_servidor_recusa_item_de_outra_biblioteca_na_coleção(api_admin, estado, colecoes):
    faixa = next(v for k, v in estado['itens'].items() if k.startswith('Audio:'))
    with pytest.raises(urllib.error.HTTPError) as erro:
        api_admin(f'Collections/{colecoes["Saga E2E"]}/Items?ids={faixa}', metodo='POST')
    assert erro.value.code == 400


def _abrir_colecao(pagina, ir, id_):
    ir(f'details?id={id_}')
    pagina.locator('#itemDetailPage:not(.hide) .collectionItemsContainer .card').first.wait_for()


@pytest.mark.usuario('admin')
def test_mudar_o_modo_de_exibicao_da_colecao_e_ele_fica_gravado(pagina, ir, api_admin, colecoes):
    id_ = colecoes['Saga E2E']
    _abrir_colecao(pagina, ir, id_)
    cartao = pagina.locator('#itemDetailPage:not(.hide) .collectionItemsContainer .card').first
    assert 'portraitCard' in cartao.get_attribute('class')
    pagina.get_by_test_id('collection-display-switch').get_by_role('radio', name='Miniatura').click()
    pagina.locator('#itemDetailPage:not(.hide) .collectionItemsContainer .backdropCard').first.wait_for()
    assert pagina.locator('#itemDetailPage:not(.hide) .collectionItemsContainer .portraitCard').count() == 0
    assert api_admin(f'Items?Ids={id_}')['Items'][0]['CollectionUseThumbnails'] is True
    pagina.reload()
    pagina.locator('#itemDetailPage:not(.hide) .collectionItemsContainer .backdropCard').first.wait_for()
    marcado = pagina.get_by_test_id('collection-display-switch').get_by_role('radio', name='Miniatura')
    assert marcado.get_attribute('aria-checked') == 'true'


def test_quem_nao_gerencia_colecoes_ve_o_modo_mas_nao_muda(pagina, ir, api_admin, colecoes):
    id_ = colecoes['Saga E2E']
    api_admin(f'Collections/{id_}/DisplayMode?useThumbnails=true', metodo='POST')
    _abrir_colecao(pagina, ir, id_)
    pagina.locator('#itemDetailPage:not(.hide) .collectionItemsContainer .backdropCard').first.wait_for()
    assert pagina.get_by_test_id('collection-display-switch').count() == 0


def _opcao_da_biblioteca(api_admin, nome, miniaturas):
    pasta = next(b for b in api_admin('Library/VirtualFolders') if b['Name'] == nome)
    opcoes = {**pasta['LibraryOptions'], 'CollectionsUseThumbnails': miniaturas}
    api_admin('Library/VirtualFolders/LibraryOptions', {'Id': pasta['ItemId'], 'LibraryOptions': opcoes}, 'POST')


def _abrir_aba_colecoes(pagina, ir, biblioteca):
    ir(f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=0')
    pagina.locator('.MuiTabs-root [role="tab"]', has_text='Coleções').click()


def test_aba_colecoes_usa_posteres_por_padrao(pagina, ir, biblioteca, colecoes):
    _abrir_aba_colecoes(pagina, ir, biblioteca)
    pagina.locator('.card.portraitCard', has_text='Saga E2E').wait_for()
    assert pagina.locator('.card.backdropCard').count() == 0


def test_aba_colecoes_segue_o_modo_da_biblioteca(pagina, ir, api_admin, biblioteca, colecoes):
    # a visão da biblioteca fica em cache na sessão da página: o modo é gravado antes de abrir a tela
    _opcao_da_biblioteca(api_admin, 'Filmes', True)
    try:
        _abrir_aba_colecoes(pagina, ir, biblioteca)
        pagina.locator('.card.backdropCard', has_text='Saga E2E').wait_for()
        assert pagina.locator('.card.portraitCard').count() == 0
    finally:
        _opcao_da_biblioteca(api_admin, 'Filmes', False)


def test_nao_ha_tela_global_de_colecoes(pagina, ir, colecoes):
    ir('home')
    assert pagina.locator('a[href*="boxsets"]').count() == 0
    assert 'collectionType=boxsets' not in pagina.content()
