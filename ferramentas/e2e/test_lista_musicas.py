"""Lista de músicas, página da música e celular (pedido do usuário, 21/11/2026).

- Numa coleção, as músicas são uma lista (capa pequena, título, duração) e tocar uma continua nas seguintes.
- A página da música mostra só a capa quadrada, sem imagem de fundo.
- No celular (390 px, layout móvel) o detalhe empilha pôster, título e botões; as abas rolam; sem índice alfabético.
"""
import re
from urllib.parse import quote

import pytest

FAIXAS = ['Faixa 1', 'Outra 1', 'Faixa 2', 'Outra 2', 'Faixa 3']
CELULAR = {'width': 390, 'height': 844}
UA_CELULAR = ('Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/130.0 Mobile Safari/537.36')


@pytest.fixture(scope='module')
def mixtape(api_admin, estado):
    """Uma coleção da biblioteca Músicas com as cinco faixas, na ordem de `FAIXAS`."""
    ids = ','.join(estado['itens'][f'Audio:{nome}'] for nome in FAIXAS)
    id_ = api_admin(f'Collections?name=Mixtape%20E2E&ownerLibraryId={estado["bibliotecas"]["Músicas"]["id"]}&ids={ids}',
                    metodo='POST')['Id']
    yield id_
    api_admin(f'Items/{id_}', metodo='DELETE')
    # criar a coleção cria a biblioteca "Coleções" do servidor; sem apagá-la o painel das outras telas muda
    for pasta in api_admin('Library/VirtualFolders'):
        if pasta.get('CollectionType') == 'boxsets':
            api_admin(f'Library/VirtualFolders?name={quote(pasta["Name"])}&refreshLibrary=false', metodo='DELETE')


def _so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV entra no módulo T06')


def test_colecao_de_musicas_e_uma_lista_com_capa_titulo_e_duracao(pagina, layout, ir, mixtape):
    _so_desktop(layout)
    ir(f'details?id={mixtape}')
    linhas = pagina.locator('.collectionItems .cromaSongList .listItem')
    linhas.first.wait_for()
    assert linhas.count() == len(FAIXAS)
    assert [linhas.nth(i).locator('.listItemBodyText').first.inner_text() for i in range(len(FAIXAS))] == FAIXAS
    for i in range(len(FAIXAS)):
        assert linhas.nth(i).locator('.listItemImage').count() == 1
        assert re.fullmatch(r'\d+:\d\d', linhas.nth(i).locator('.listItemMediaInfo').inner_text().strip())
    # todas do mesmo artista: a linha do artista não aparece
    assert pagina.locator('.collectionItems .cromaSongList .listItemBodyText.secondary').count() == 0
    # nenhum cartão sobrando para as músicas
    assert pagina.locator('.collectionItems .card[data-type="Audio"]').count() == 0


@pytest.mark.usuario('tocador')
def test_tocar_uma_musica_da_colecao_continua_na_seguinte(pagina, layout, ir, mixtape, item):
    _so_desktop(layout)
    ir(f'details?id={mixtape}')
    linhas = pagina.locator('.collectionItems .cromaSongList .listItem')
    linhas.first.wait_for()
    linhas.nth(1).locator('.listItemBody').click()

    atual = '.collectionItems .cromaSongList .cromaTrackCurrent'
    pagina.wait_for_function(f'() => document.querySelector("{atual}")?.dataset.id === "{item("Audio", "Outra 1")}"',
                             timeout=20000)
    # as faixas de teste têm 8 s: a seguinte da coleção entra sozinha
    pagina.wait_for_function(f'() => document.querySelector("{atual}")?.dataset.id === "{item("Audio", "Faixa 2")}"',
                             timeout=30000)


def test_pagina_da_musica_nao_tem_fundo(pagina, layout, ir, item):
    _so_desktop(layout)
    ir(f'details?id={item("Audio", "Faixa 1")}')
    pagina.locator('#itemDetailPage:not(.hide) .detailImageContainer .card').first.wait_for()
    assert pagina.locator('#itemDetailPage:not(.hide)').evaluate('e => e.classList.contains("cromaNoBackdrop")')
    # os elementos do fundo ficam na página, vazios
    assert pagina.locator('.backdropImage.displayingBackdropImage').count() == 0
    imagens = pagina.locator('.backdropImage').evaluate_all('es => es.map(e => getComputedStyle(e).backgroundImage)')
    assert all(img == 'none' for img in imagens)
    assert pagina.locator('#itemBackdrop').evaluate('e => getComputedStyle(e).backgroundImage') == 'none'


@pytest.fixture
def celular(navegador, sessoes, base, request):
    """Uma página logada no tamanho de um celular, com o layout móvel da interface (conta `leitor`;
    `@pytest.mark.usuario('tocador')` troca a conta)."""
    marca = request.node.get_closest_marker('usuario')
    ctx = navegador.new_context(viewport=CELULAR, device_scale_factor=2, is_mobile=True, has_touch=True, user_agent=UA_CELULAR,
                                storage_state=str(sessoes[marca.args[0] if marca else 'leitor']), locale='pt-BR')
    ctx.add_init_script("try { localStorage.setItem('layout', 'mobile'); } catch (e) {}")
    pg = ctx.new_page()
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))

    def ir(rota, espera=1500):
        pg.goto(base + '#/' + rota)
        pg.wait_for_load_state('networkidle')
        pg.wait_for_timeout(espera)
    pg.ir = ir
    yield pg
    ctx.close()
    assert not erros, f'Erros de JavaScript na página: {erros[:3]}'


def _sem_rolagem_lateral(pg):
    assert pg.evaluate('document.documentElement.scrollWidth') <= CELULAR['width']


def test_celular_detalhe_empilha_poster_titulo_e_botoes(celular, item):
    celular.ir(f'details?id={item("Series", "Serie de Teste")}')
    pagina = celular.locator('#itemDetailPage:not(.hide)')
    poster = pagina.locator('.infoWrapper .detailImageContainer .card').bounding_box()
    titulo = pagina.locator('.nameContainer .itemName').first.bounding_box()
    botoes = pagina.locator('.mainDetailButtons').bounding_box()
    assert abs(poster['x'] + poster['width'] / 2 - CELULAR['width'] / 2) < 12      # pôster centralizado
    assert poster['y'] + poster['height'] <= titulo['y'] + 1                         # e acima do título
    assert titulo['y'] < botoes['y']
    # sem imagem de fundo, a faixa vazia do topo some: o pôster começa logo abaixo do cabeçalho
    # (a página começa abaixo do cabeçalho fixo)
    assert pagina.bounding_box()['y'] <= poster['y'] < 160
    # nenhum botão invade o vizinho (o Aleatório vazava o rótulo)
    visiveis = pagina.locator('.mainDetailButtons .detailButton:visible')
    caixas = sorted((visiveis.nth(i).bounding_box() for i in range(visiveis.count())), key=lambda b: (round(b['y']), b['x']))
    for a, b in zip(caixas, caixas[1:]):
        if round(a['y']) == round(b['y']):
            assert a['x'] + a['width'] <= b['x'] + 0.5
    _sem_rolagem_lateral(celular)


def test_celular_abas_rolam_e_sem_indice_alfabetico(celular, biblioteca):
    celular.ir(f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=1')
    celular.locator('.card').first.wait_for()
    rolagem = celular.locator('.MuiTabs-scroller').first
    assert rolagem.evaluate('e => getComputedStyle(e).overflowX') in ('auto', 'scroll')
    assert celular.locator('.alphaPicker-fixed-right').count() == 0
    _sem_rolagem_lateral(celular)


def test_celular_lista_de_musicas_mostra_titulo_e_duracao(celular, mixtape):
    celular.ir(f'details?id={mixtape}')
    linha = celular.locator('.collectionItems .cromaSongList .listItem').first
    linha.wait_for()
    assert linha.locator('.listItemBodyText').first.is_visible()
    assert linha.locator('.listItemMediaInfo').is_visible()
    # no celular só o menu fica na linha
    botoes = linha.locator('.listViewUserDataButtons .listItemButton:visible')
    assert botoes.count() == 1
    caixa = linha.bounding_box()
    assert caixa['x'] >= 0 and caixa['x'] + caixa['width'] <= CELULAR['width'] + 0.5
    _sem_rolagem_lateral(celular)


@pytest.mark.usuario('tocador')
def test_celular_tocando_agora_cabe_na_tela(celular, item):
    """O player da música no celular: uma coluna (capa, título, analisador, linha do tempo e botões), nada para fora."""
    pg = celular
    pg.ir(f'details?id={item("MusicAlbum", "Album Um")}')
    pg.locator('#itemDetailPage:not(.hide) .btnPlay').first.click()
    pg.wait_for_selector('.nowPlayingBar:not(.hide)', timeout=20000)
    pg.ir('queue', 2500)
    tela = pg.locator('.nowPlayingPage:not(.hide)')
    capa = tela.locator('.nowPlayingPageImageContainer').bounding_box()
    titulo = tela.locator('.nowPlayingSongName').bounding_box()
    analisador = tela.locator('.cromaAnalyzer').bounding_box()
    linha = tela.locator('.nowPlayingPositionSliderContainer').bounding_box()
    tocar = tela.locator('.nowPlayingInfoButtons .btnPlayPause').bounding_box()
    assert capa['y'] + capa['height'] <= titulo['y']
    assert titulo['y'] < analisador['y'] < linha['y'] < tocar['y']
    assert analisador['width'] > 250 and linha['width'] > 100
    for caixa in (capa, titulo, analisador, linha, tocar):
        assert caixa['x'] >= 0 and caixa['x'] + caixa['width'] <= CELULAR['width'] + 0.5
    _sem_rolagem_lateral(pg)


def test_celular_cabecalho_curto_com_opcoes_e_recolhe_ao_rolar(celular, biblioteca):
    celular.ir(f'music?topParentId={biblioteca("Músicas")["id"]}&collectionType=music&tab=0')
    celular.locator('.card').first.wait_for()
    barra = celular.locator('.MuiAppBar-root').first
    assert barra.bounding_box()['height'] < 200
    # sem a contagem da seção; grade/lista, filtro e ordem ficam atrás do botão de opções
    assert celular.locator('[data-testid="section-label"]').count() == 0
    assert celular.get_by_role('button', name='Lista').count() == 0
    celular.locator('.cromaLibraryOptionsButton').click()
    celular.get_by_role('button', name='Lista').wait_for()
    _sem_rolagem_lateral(celular)
    celular.locator('.cromaLibraryOptionsButton').click()
    celular.locator('.cromaLibraryOptions').wait_for(state='detached')

    # ao rolar para baixo, o título e a linha de botões recolhem; as abas ficam
    aberta = barra.bounding_box()['height']
    celular.evaluate('document.body.style.minHeight = "4000px"')
    celular.mouse.wheel(0, 600)
    celular.wait_for_timeout(800)
    assert barra.bounding_box()['height'] < aberta - 50
    assert celular.locator('.MuiTabs-root').first.is_visible()
    celular.mouse.wheel(0, -300)
    celular.wait_for_timeout(800)
    assert barra.bounding_box()['height'] >= aberta - 1
