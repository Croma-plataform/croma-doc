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


def test_criar_editar_e_varrer_uma_biblioteca(pagina, ir, api_admin, tmp_path):
    nome = 'BibliotecaTemporaria'
    pasta = tmp_path / 'vazia'
    pasta.mkdir()
    api_admin(f'Library/VirtualFolders?name={nome}&collectionType=books&refreshLibrary=false',
              {'LibraryOptions': {'Subtype': 'Podcasts', 'PathInfos': [{'Path': str(pasta)}]}}, 'POST')
    try:
        ir('dashboard/libraries')
        cartao = pagina.locator('.MuiCard-root', has_text=nome)
        expect(cartao).to_be_visible()
        cartao.locator('[data-testid="MoreVertIcon"]').click()
        pagina.get_by_role('menuitem', name='Gerenciar biblioteca').click()
        expect(pagina.locator('#selectLibrarySubtype')).to_have_value('Podcasts')
        pagina.locator('#selectLibrarySubtype').select_option(value='Audiobooks')
        pagina.get_by_role('button', name='OK').click()
        pagina.locator('#selectLibrarySubtype').wait_for(state='detached')
        atual = [p for p in api_admin('Library/VirtualFolders') if p['Name'] == nome][0]
        assert atual['LibraryOptions']['Subtype'] == 'Audiobooks'
        # varrer a biblioteca vazia termina sem erro
        api_admin('Library/Refresh', None, 'POST')
    finally:
        api_admin(f'Library/VirtualFolders?name={nome}&refreshLibrary=false', None, 'DELETE')


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
