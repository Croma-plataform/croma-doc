"""Músicas (módulo D11)."""
import pytest


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV entra no módulo T06')


def test_visual_da_galeria_de_albuns(pagina, ir, biblioteca, conferir):
    ir(f'music?topParentId={biblioteca("Músicas")["id"]}&collectionType=music&tab=0')
    pagina.locator('.card').first.wait_for()
    conferir('galeria-albuns')


def _tocar_album(pagina, ir, item):
    ir(f'details?id={item("MusicAlbum", "Album Um")}')
    pagina.locator('#itemDetailPage:not(.hide) .btnPlay').first.click()
    pagina.wait_for_selector('.nowPlayingBar:not(.hide)', timeout=20000)
    pagina.wait_for_function('() => { const a = document.querySelector("audio.mediaPlayerAudio"); return a && a.currentTime > 0.5; }',
                             timeout=20000)


@pytest.mark.usuario('tocador')
def test_linha_do_tempo_do_player_e_em_espectro_sem_azul(pagina, ir, item):
    _tocar_album(pagina, ir, item)
    fundo = pagina.locator('.nowPlayingBar .mdl-slider-background-flex').first.evaluate('e => getComputedStyle(e).backgroundImage')
    assert 'linear-gradient' in fundo
    volume = pagina.locator('.nowPlayingBarVolumeSliderContainer .mdl-slider-background-lower').first.evaluate(
        'e => getComputedStyle(e).backgroundColor')
    assert volume == 'rgb(242, 242, 240)'          # Fósforo, não o azul do Jellyfin


@pytest.mark.usuario('tocador')
def test_analisador_desenha_enquanto_toca(pagina, ir, item):
    _tocar_album(pagina, ir, item)
    ir('queue')
    tela = pagina.locator('.nowPlayingPage:not(.hide) .cromaAnalyzer')
    tela.wait_for(state='visible', timeout=10000)
    pagina.wait_for_timeout(1500)
    pintado = tela.evaluate('''c => {
        const d = c.getContext("2d").getImageData(0, 0, c.width, c.height).data;
        let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 0) n++; return n; }''')
    assert pintado > 200
