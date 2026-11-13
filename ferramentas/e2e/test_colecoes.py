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
