"""Tela de carregando do player (prancha 38): aparece quando a rede segura o vídeo e some quando ele volta."""
import pytest

pytestmark = [pytest.mark.usuario('tocador'), pytest.mark.lento]


def test_carregando_aparece_com_rede_lenta_e_some_ao_tocar(pagina, tocar, osd):
    tocar('Movie', 'Barras Capitulos (2004)')
    osd()
    barra = pagina.locator('.cromaOsdTimeline .sliderContainer').first.bounding_box()
    cdp = pagina.context.new_cdp_session(pagina)
    cdp.send('Network.enable')
    cdp.send('Network.emulateNetworkConditions',
             {'offline': False, 'latency': 400, 'downloadThroughput': 40000, 'uploadThroughput': 40000})

    pagina.mouse.click(barra['x'] + barra['width'] * 0.8, barra['y'] + barra['height'] / 2)
    pagina.wait_for_selector('.cromaOsdLoading:not(.hide)', timeout=15000)

    centro = pagina.locator('.cromaOsdLoadingCenter').inner_text()
    assert 'Preparando a imagem' in centro or 'Carregando' in centro
    animacoes = pagina.evaluate("document.querySelector('.cromaOsdLoadingBar b').getAnimations().map(a => a.animationName)")
    assert 'cromaOsdSweep' in animacoes       # o espectro varre a barra

    cdp.send('Network.emulateNetworkConditions',
             {'offline': False, 'latency': 0, 'downloadThroughput': -1, 'uploadThroughput': -1})
    pagina.wait_for_selector('.cromaOsdLoading', state='hidden', timeout=60000)
    pagina.wait_for_function('document.querySelector("video").paused === false')
