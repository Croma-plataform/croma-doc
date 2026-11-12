"""Painel de administração (conta admin): bibliotecas de cada subtipo e nada de TV ao vivo nem de marca Jellyfin."""
import re

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.usuario('admin')

# nome da biblioteca de teste -> subtipo que o editor deve mostrar
SUBTIPOS = {
    'Mangás': 'Manga',
    'HQs': 'Comics',
}


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('o painel de administração não é usado na TV')


def test_cada_biblioteca_mostra_o_seu_subtipo(pagina, ir, api_admin):
    pastas = api_admin('Library/VirtualFolders')
    assert pastas, 'o servidor de teste deveria ter bibliotecas'
    catalogo = {i['Subtype'] for i in api_admin('Library/Subtypes')}
    vistos = set()
    for pasta in pastas:
        subtipo = pasta['LibraryOptions'].get('Subtype')
        assert subtipo in catalogo, f"{pasta['Name']}: subtipo {subtipo!r} fora do catálogo"
        vistos.add(subtipo)
    # a mídia de teste cobre vários subtipos, de seções diferentes
    assert len(vistos) >= 6


def test_criar_biblioteca_com_subtipo_incompativel_e_recusado(api_admin, tmp_path):
    """Criar de verdade deixaria a biblioteca nas telas dos outros usuários até limpar o servidor de teste (o
    servidor mantém o item da raiz depois de apagar a pasta virtual), então aqui só se confere a validação."""
    import urllib.error
    with pytest.raises(urllib.error.HTTPError) as erro:
        api_admin('Library/VirtualFolders?name=Recusada&collectionType=movies&refreshLibrary=false',
                  {'LibraryOptions': {'Subtype': 'Music', 'PathInfos': [{'Path': str(tmp_path)}]}}, 'POST')
    assert erro.value.code == 400
    assert 'Recusada' not in [p['Name'] for p in api_admin('Library/VirtualFolders')]


def test_nenhuma_entrada_de_tv_ao_vivo(pagina, ir):
    ir('dashboard')
    gaveta = pagina.locator('.MuiDrawer-root').filter(has=pagina.get_by_role('link', name='Painel'))
    expect(gaveta.first).to_be_attached()
    gaveta = gaveta.first
    assert not re.search(r'tv ao vivo|live tv', gaveta.text_content(), re.I)
    assert gaveta.locator('a[href*="livetv"]').count() == 0
    ir('dashboard/libraries')
    pagina.get_by_role('button', name='Adicionar biblioteca de mídia').click()
    tipos = pagina.locator('#selectCollectionType option, select option').all_inner_texts()
    assert not any(re.search(r'tv ao vivo|live tv', t, re.I) for t in tipos)


def test_painel_sem_a_marca_jellyfin(pagina, ir):
    for rota in ('dashboard', 'dashboard/libraries', 'dashboard/settings'):
        ir(rota)
        assert 'jellyfin' not in pagina.title().lower(), rota
        texto = pagina.locator('body').inner_text().lower()
        # o nome pode aparecer em textos de licença, mas não no cabeçalho nem na gaveta
        assert 'jellyfin' not in pagina.locator('header, .MuiDrawer-root').first.text_content().lower(), rota
        assert pagina.locator('img[src*="jellyfin" i], img[src*="banner-light" i]').count() == 0, rota
        _ = texto


def test_painel_visual(pagina, ir, conferir):
    ir('dashboard/libraries')
    conferir('painel-bibliotecas')
