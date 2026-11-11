"""Painel de legendas e áudio (prancha 36)."""
import pytest

pytestmark = pytest.mark.usuario('tocador')


def abrir_painel(pagina, osd):
    osd()
    # Na TV o botão fica fora do alcance do mouse; o clique por script vale para os dois layouts
    pagina.evaluate("document.querySelector('.btnSubtitles:not(.hide), .btnAudio:not(.hide)').click()")
    pagina.wait_for_selector('.cromaPanel', timeout=5000)
    # O diálogo entra com uma animação de 200 ms e só depois recebe o foco
    pagina.wait_for_function("document.activeElement && document.activeElement.closest('.cromaPanel') !== null",
                             timeout=3000)


def test_painel_abre_pausa_o_video_e_lista_as_faixas(pagina, tocar, osd):
    tocar('Movie', 'Barras Faixas (2003)')
    abrir_painel(pagina, osd)

    assert pagina.evaluate('document.querySelector("video").paused') is True
    assert pagina.locator('.cromaPanelOption[data-kind="subtitle"]').count() == 3     # Desligadas + 2 idiomas
    assert pagina.locator('.cromaPanelOption[data-kind="audio"]').count() == 2
    assert 'PAUSADO' in pagina.locator('.cromaPanelKicker').inner_text().upper()
    assert 'Barras Faixas' in pagina.locator('.cromaPanelTitle').inner_text()


def test_escolher_legenda_e_estilo(pagina, tocar, osd, layout):
    if layout == 'tv':
        pytest.skip('o clique do mouse é do desktop; a TV é testada pelas setas em test_painel_na_tv')
    tocar('Movie', 'Barras Faixas (2003)')
    abrir_painel(pagina, osd)

    opcoes = pagina.locator('.cromaPanelOption[data-kind="subtitle"]')
    opcoes.nth(opcoes.count() - 1).click()
    pagina.locator('.cromaPanelChoice[data-kind="size"][data-value="large"]').click()
    pagina.locator('.cromaPanelChoice[data-kind="background"][data-value="box"]').click()

    escolhidos = pagina.evaluate("[...document.querySelectorAll('.cromaPanelOption-selected, .cromaPanelChoice-selected')]"
                                 ".map(e => e.dataset.kind + '=' + (e.dataset.value ?? e.dataset.index))")
    assert 'subtitle=4' in escolhidos          # a última faixa de legenda (inglês)
    assert 'size=large' in escolhidos
    assert 'background=box' in escolhidos


def test_esc_fecha_e_o_video_volta_a_tocar(pagina, tocar, osd):
    tocar('Movie', 'Barras Faixas (2003)')
    abrir_painel(pagina, osd)

    pagina.keyboard.press('Escape')
    pagina.wait_for_selector('.cromaPanel', state='detached', timeout=5000)
    pagina.wait_for_function('document.querySelector("video").paused === false', timeout=10000)
    assert '#/video' in pagina.url        # fechou o painel, não o player


def test_painel_na_tv(pagina, tocar, osd, layout):
    if layout != 'tv':
        pytest.skip('só na TV')
    tocar('Movie', 'Barras Faixas (2003)')
    abrir_painel(pagina, osd)

    dentro = "document.activeElement && document.activeElement.closest('.cromaPanel') !== null"
    for tecla in ('ArrowDown', 'ArrowRight', 'ArrowDown', 'ArrowDown'):
        pagina.keyboard.press(tecla)
        pagina.wait_for_timeout(250)
        assert pagina.evaluate(dentro), f'o foco saiu do painel em {tecla}'
