"""Base dos testes de ponta a ponta do Croma (Playwright + pytest) contra o servidor de teste.

Antes de rodar: `python3 ferramentas/midia_teste.py` e `python3 ferramentas/servidor_teste.py subir` (o `verificar.sh`
faz isso). Cada teste roda nos dois layouts: `desktop` (1600×900) e `tv` (1920×1080, modo TV da interface).

Opções: --atualizar-referencias (regrava as capturas de referência), --headed (mostra o navegador).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from visual import conferir as _conferir

ESTADO = Path(os.environ.get('CROMA_TESTE_DIR', Path.home() / '.cache' / 'croma-teste')) / 'estado.json'

LAYOUTS = {
    'desktop': {'width': 1600, 'height': 900},
    'tv': {'width': 1920, 'height': 1080},
}


def pytest_addoption(parser):
    parser.addoption('--atualizar-referencias', action='store_true', help='regrava as capturas de referência')
    parser.addoption('--headed', action='store_true', help='mostra o navegador')


def pytest_generate_tests(metafunc):
    if 'layout' in metafunc.fixturenames:
        metafunc.parametrize('layout', list(LAYOUTS))


@pytest.fixture(scope='session')
def estado():
    if not ESTADO.exists():
        pytest.exit('Servidor de teste não preparado: rode `python3 ferramentas/servidor_teste.py subir`.', returncode=3)
    return json.loads(ESTADO.read_text(encoding='utf-8'))


@pytest.fixture(scope='session')
def base(estado):
    return estado['url'] + '/web/'


@pytest.fixture(scope='session')
def navegador(request):
    with sync_playwright() as p:
        # O Chromium do Playwright não tem H.264: o servidor converte, e os chips mostram "Convertendo"
        b = p.chromium.launch(headless=not request.config.getoption('--headed'),
                              args=['--autoplay-policy=no-user-gesture-required'])
        yield b
        b.close()


@pytest.fixture(scope='session')
def sessoes(navegador, estado, base, tmp_path_factory):
    """Entra uma vez por conta e guarda o estado do navegador (credenciais) para os testes."""
    pasta = tmp_path_factory.mktemp('sessoes')
    caminhos = {}
    for usuario, senha in estado['usuarios'].items():
        ctx = navegador.new_context(viewport=LAYOUTS['desktop'], locale='pt-BR')
        pg = ctx.new_page()
        pg.goto(base + '#/login')
        pg.wait_for_selector('#txtManualName, .btnManual', timeout=30000)
        if not pg.locator('#txtManualName').is_visible():
            pg.locator('.btnManual').first.click()
        pg.fill('#txtManualName', usuario)
        pg.fill('#txtManualPassword', senha)
        pg.locator('#txtManualPassword').press('Enter')
        pg.wait_for_url('**/home**', timeout=30000)
        caminhos[usuario] = pasta / f'{usuario}.json'
        ctx.storage_state(path=str(caminhos[usuario]))
        ctx.close()
    return caminhos


@pytest.fixture
def pagina(navegador, sessoes, layout, base, request):
    """Uma página já logada no layout do teste (conta `leitor`; `@pytest.mark.usuario('tocador')` troca a conta).
    Falha se a página lançar um erro de JavaScript."""
    marca = request.node.get_closest_marker('usuario')
    usuario = marca.args[0] if marca else 'leitor'
    ctx = navegador.new_context(viewport=LAYOUTS[layout], storage_state=str(sessoes[usuario]), locale='pt-BR')
    ctx.add_init_script(f"try {{ localStorage.setItem('layout', '{layout}'); }} catch (e) {{}}")
    pg = ctx.new_page()
    pg.croma_base = base
    erros: list[str] = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    yield pg
    ctx.close()
    assert not erros, f'Erros de JavaScript na página: {erros[:3]}'


@pytest.fixture
def ir(pagina, base):
    """`ir('home')` abre uma rota da interface (`#/rota`) e espera a tela assentar."""
    def _ir(rota: str, espera=1500, rede_ociosa=True):
        # rede_ociosa=False: telas que consultam a internet (o catálogo de plugins) não podem esperar a rede calar
        pagina.goto(base + '#/' + rota)
        pagina.wait_for_load_state('networkidle' if rede_ociosa else 'domcontentloaded')
        pagina.wait_for_timeout(espera)
    return _ir


@pytest.fixture
def conferir(pagina, layout, request):
    """`conferir('nome')` compara a tela com a referência `referencias/<layout>/nome.png`."""
    return lambda nome, **kw: _conferir(pagina, layout, nome,
                                         atualizar=request.config.getoption('--atualizar-referencias'), **kw)


@pytest.fixture(scope='session')
def item(estado):
    """`item('Movie', 'Barras Direto (2001)')` devolve o id de um item da mídia de teste."""
    def _item(tipo: str, nome: str) -> str:
        chave = f'{tipo}:{nome}'
        assert chave in estado['itens'], f'{chave} não está na mídia de teste: {sorted(estado["itens"])[:8]}...'
        return estado['itens'][chave]
    return _item


@pytest.fixture(scope='session')
def biblioteca(estado):
    def _biblioteca(nome: str) -> dict:
        return estado['bibliotecas'][nome]
    return _biblioteca


@pytest.fixture
def tocar(pagina, ir, item):
    """`tocar('Movie', 'Barras Direto (2001)')` abre o item, aperta Assistir e espera o vídeo andar."""
    def _tocar(tipo: str, nome: str, depois_de_s: float = 1.5):
        ir(f'details?id={item(tipo, nome)}')
        pagina.locator('#itemDetailPage:not(.hide) .btnPlay').first.click()
        pagina.wait_for_selector('video', timeout=20000)
        pagina.wait_for_function(f'() => {{ const v = document.querySelector("video"); return v && v.currentTime > {depois_de_s}; }}',
                                 timeout=45000)
    return _tocar


@pytest.fixture
def osd(pagina):
    """`osd()` faz o controle de reprodução aparecer (o mouse mexe) e espera o título."""
    def _osd():
        pagina.mouse.move(700, 400)
        pagina.wait_for_timeout(200)
        pagina.mouse.move(740, 440)
        pagina.wait_for_selector('.cromaOsdTitle', state='visible', timeout=5000)
    return _osd


@pytest.fixture(scope='session')
def api_admin(base):
    """`api_admin('Items/ID', corpo, 'POST')` chama a API do servidor de teste como administrador."""
    import json
    import urllib.request
    raiz = base.removesuffix('web/')
    auth = 'MediaBrowser Client="croma-teste", Device="teste", DeviceId="croma-api", Version="1"'

    def chamar(caminho, corpo=None, metodo=None, token=None):
        pedido = urllib.request.Request(
            raiz + caminho, data=json.dumps(corpo).encode() if corpo is not None else None, method=metodo,
            headers={'Content-Type': 'application/json',
                     'Authorization': auth + (f', Token="{token}"' if token else '')})
        with urllib.request.urlopen(pedido) as r:
            texto = r.read()
            return json.loads(texto) if texto else None

    sessao = chamar('Users/AuthenticateByName', {'Username': 'admin', 'Pw': 'teste'})
    token, uid = sessao['AccessToken'], sessao['User']['Id']

    def api(caminho, corpo=None, metodo=None):
        return chamar(caminho, corpo, metodo, token)
    api.uid = uid
    return api
