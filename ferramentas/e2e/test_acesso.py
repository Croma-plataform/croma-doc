"""Uma conta que só vê uma biblioteca: a barra lateral só mostra a seção dela (conta criada e apagada pelo teste)."""
import json
import urllib.request

import pytest

AUTH = 'MediaBrowser Client="croma-teste", Device="teste", DeviceId="croma-acesso", Version="1"'


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV ainda usa o menu de bibliotecas do Jellyfin (módulo T03)')


@pytest.fixture
def conta_restrita(base, biblioteca):
    """Cria uma conta que só enxerga `Filmes` e a apaga no fim; devolve o nome e a senha."""
    raiz = base.removesuffix('web/')

    def chamar(caminho, corpo=None, token=None, metodo=None):
        pedido = urllib.request.Request(
            raiz + caminho, data=json.dumps(corpo).encode() if corpo is not None else None, method=metodo,
            headers={'Content-Type': 'application/json',
                     'Authorization': AUTH + (f', Token="{token}"' if token else '')})
        with urllib.request.urlopen(pedido) as r:
            texto = r.read()
            return json.loads(texto) if texto else None

    token = chamar('Users/AuthenticateByName', {'Username': 'admin', 'Pw': 'teste'})['AccessToken']
    nome = 'so-filmes'
    for u in chamar('Users', token=token):
        if u['Name'] == nome:
            chamar(f'Users/{u["Id"]}', token=token, metodo='DELETE')
    usuario = chamar('Users/New', {'Name': nome, 'Password': 'teste'}, token)
    politica = chamar(f'Users/{usuario["Id"]}', token=token)['Policy']
    politica.update({'EnableAllFolders': False, 'EnabledFolders': [biblioteca('Filmes')['id']]})
    chamar(f'Users/{usuario["Id"]}/Policy', politica, token)
    yield nome, 'teste'
    chamar(f'Users/{usuario["Id"]}', token=token, metodo='DELETE')


def test_conta_com_uma_biblioteca_so_ve_a_secao_dela(navegador, base, conta_restrita, biblioteca):
    nome, senha = conta_restrita
    ctx = navegador.new_context(viewport={'width': 1600, 'height': 900}, locale='pt-BR')
    pg = ctx.new_page()
    try:
        pg.goto(base + '#/login')
        pg.wait_for_selector('#txtManualName, .btnManual', timeout=30000)
        if not pg.locator('#txtManualName').is_visible():
            pg.locator('.btnManual').first.click()
        pg.fill('#txtManualName', nome)
        pg.fill('#txtManualPassword', senha)
        pg.locator('#txtManualPassword').press('Enter')
        pg.wait_for_url('**/home**', timeout=30000)
        pg.wait_for_timeout(2000)

        gaveta = pg.locator('.MuiDrawer-root').inner_text()
        assert 'Audiovisual' in gaveta
        for secao in ('Áudios', 'Leitura', 'Fotos'):
            assert secao not in gaveta, f'{secao} apareceu para uma conta sem acesso'

        # Dentro da seção, só a biblioteca liberada vira aba
        pg.goto(base + f'#/movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=1')
        pg.wait_for_timeout(2000)
        abas = [t.strip() for t in pg.locator('.MuiTabs-root [role="tab"]').all_inner_texts()]
        assert 'Filmes' in abas
        assert 'Séries' not in abas and 'Documentários (filmes)' not in abas
    finally:
        ctx.close()
