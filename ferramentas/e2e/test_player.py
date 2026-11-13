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


def test_voltar_10_segundos(pagina, tocar, osd):
    tocar('Movie', 'Barras Capitulos (2004)', depois_de_s=1.5)
    osd()
    # vai para perto do fim e volta: o salto de −10 s tem de andar pelo menos uns 8 s para trás
    barra = pagina.locator('.cromaOsdTimeline .sliderContainer').first.bounding_box()
    pagina.mouse.click(barra['x'] + barra['width'] * 0.75, barra['y'] + barra['height'] / 2)
    pagina.wait_for_function('document.querySelector("video").currentTime > 25', timeout=20000)
    pagina.locator('.videoOsdBottom .btnPause').click()
    pagina.wait_for_function('document.querySelector("video").paused === true')
    antes = pagina.evaluate('document.querySelector("video").currentTime')

    pagina.locator('.videoOsdBottom .btnRewind').click()
    pagina.wait_for_function(f'document.querySelector("video").currentTime < {antes - 8}', timeout=20000)


def test_capitulo_seguinte_e_anterior(pagina, tocar, osd):
    tocar('Movie', 'Barras Capitulos (2004)')
    osd()
    capitulo = "document.querySelector('.cromaOsdChapter').innerText.match(/Capítulo (\\d) de 4/)[1]"
    antes = int(pagina.evaluate(capitulo))

    pagina.keyboard.press('PageUp')
    pagina.wait_for_function(f'{capitulo} > {antes}', timeout=20000)
    pagina.keyboard.press('PageDown')
    pagina.wait_for_function(f'{capitulo} <= {antes}', timeout=20000)


@pytest.fixture
def retomada_em_videos_curtos(api_admin, item):
    """O servidor só guarda o ponto de itens com mais de 5 min (`MinResumeDurationSeconds`); a mídia de teste tem 40 s."""
    config = api_admin('System/Configuration')
    anterior = config['MinResumeDurationSeconds']
    api_admin('System/Configuration', {**config, 'MinResumeDurationSeconds': 10}, 'POST')
    yield
    api_admin('System/Configuration', {**api_admin('System/Configuration'), 'MinResumeDurationSeconds': anterior}, 'POST')
    # o ponto salvo faria os outros testes do filme começarem no meio
    for usuario in api_admin('Users'):
        api_admin(f'Users/{usuario["Id"]}/PlayedItems/{item("Movie", "Barras Capitulos (2004)")}', metodo='DELETE')


def test_sair_e_voltar_no_ponto(pagina, ir, tocar, item, retomada_em_videos_curtos):
    tocar('Movie', 'Barras Capitulos (2004)', depois_de_s=7)

    # sair do player (voltar) grava o ponto; a página do filme oferece continuar de lá
    pagina.go_back()
    pagina.wait_for_selector('video', state='detached', timeout=15000)
    ir(f'details?id={item("Movie", "Barras Capitulos (2004)")}')
    # com ponto salvo a página oferece "Do início" além de "Assistir", que continua de onde parou
    pagina.locator('#itemDetailPage:not(.hide) .btnReplay').first.wait_for(state='visible', timeout=15000)
    pagina.locator('#itemDetailPage:not(.hide) .btnPlay').first.click()
    pagina.wait_for_selector('video', timeout=20000)
    # sem retomar, o vídeo começaria em 0: passados 2 s ele estaria perto de 2 s, não de 7
    pagina.wait_for_function('document.querySelector("video") && document.querySelector("video").currentTime > 6.5',
                             timeout=45000)


def _chips(pagina, tocar, osd, nome):
    tocar('Movie', nome)
    osd()
    return pagina.locator('.cromaOsdChips').inner_text()


def test_chip_de_reproducao_direta_no_mp4_de_h264(pagina, tocar, osd):
    chips = _chips(pagina, tocar, osd, 'Barras Direto (2001)')
    assert 'Reprodução direta' in chips
    assert pagina.locator('.cromaOsdChip-direct').count() == 1
    assert pagina.locator('.cromaOsdChip-transcode').count() == 0


def test_chip_de_conversao_quando_o_navegador_nao_toca_o_video(pagina, tocar, osd):
    # o Chromium do teste não decodifica H.265: o servidor converte o vídeo
    chips = _chips(pagina, tocar, osd, 'Barras HEVC (2002)')
    assert 'Convertendo no servidor' in chips
    assert pagina.locator('.cromaOsdChip-transcode').count() == 1
