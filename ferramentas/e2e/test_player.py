"""Player de vídeo (pranchas 11 e 12): cabeçalho, linha do tempo, capítulos, chips e controles."""
import re

import pytest

pytestmark = pytest.mark.usuario('tocador')


def test_osd_mostra_kicker_titulo_e_chips(pagina, tocar, osd):
    tocar('Movie', 'Barras Capitulos (2004)')
    osd()

    assert 'FILME' in pagina.locator('.cromaOsdKicker').inner_text().upper()
    assert 'Barras Capitulos' in pagina.locator('.cromaOsdTitle').inner_text()
    chips = pagina.locator('.cromaOsdChips').inner_text()
    assert re.search(r'Reprodução direta|Convertendo no servidor', chips)


def test_capitulo_e_tempo_restante(pagina, tocar, osd):
    tocar('Movie', 'Barras Capitulos (2004)')
    osd()

    assert re.fullmatch(r'Capítulo \d de 4', pagina.locator('.cromaOsdChapter').inner_text().strip())
    assert re.search(r'−\d+:\d\d', pagina.locator('.videoOsdBottom').inner_text())    # "−0:35 · 0:40"


def test_pausar_e_continuar(pagina, tocar, osd):
    tocar('Movie', 'Barras Capitulos (2004)')
    osd()

    pagina.locator('.videoOsdBottom .btnPause').click()
    pagina.wait_for_function('document.querySelector("video").paused === true')
    pagina.locator('.videoOsdBottom .btnPause').click()
    pagina.wait_for_function('document.querySelector("video").paused === false')


def test_avancar_30_segundos(pagina, tocar, osd):
    tocar('Movie', 'Barras Capitulos (2004)')
    osd()
    antes = pagina.evaluate('document.querySelector("video").currentTime')

    pagina.locator('.videoOsdBottom .btnFastForward').click()
    pagina.wait_for_function(f'document.querySelector("video").currentTime > {antes + 20}', timeout=20000)


def test_buscar_na_linha_do_tempo(pagina, tocar, osd):
    tocar('Movie', 'Barras Capitulos (2004)')
    osd()
    barra = pagina.locator('.cromaOsdTimeline .sliderContainer').first.bounding_box()

    pagina.mouse.click(barra['x'] + barra['width'] * 0.75, barra['y'] + barra['height'] / 2)
    pagina.wait_for_function('document.querySelector("video").currentTime > 25', timeout=20000)
    # O capítulo acompanha o vídeo, que no servidor demora um pouco mais que o salto
    pagina.wait_for_function("/Capítulo [34] de 4/.test(document.querySelector('.cromaOsdChapter').innerText)",
                             timeout=15000)


def test_titulo_sai_do_cabecalho_antigo(pagina, tocar, osd):
    """O título vive no bloco do OSD do Croma; o cabeçalho do Jellyfin fica sem ele."""
    tocar('Movie', 'Barras Capitulos (2004)')
    osd()

    assert pagina.locator('.skinHeader .pageTitle').first.inner_text().strip() == ''
    assert not pagina.locator('.cromaOsdHeader .currentTimeText').first.is_visible()
