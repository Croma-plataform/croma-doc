"""Áudio falado: podcasts e audiolivros (módulo D12)."""
import pytest


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV entra no módulo T06')


def _tocar_episodio(pagina, ir, item, nome='Episodio 1'):
    ir(f'details?id={item("AudioBook", nome)}')
    pagina.locator('#itemDetailPage:not(.hide) .btnPlay').first.click()
    pagina.wait_for_selector('.nowPlayingBar:not(.hide)', timeout=20000)
    pagina.wait_for_function('() => { const a = document.querySelector("audio.mediaPlayerAudio"); return a && a.currentTime > 0.3; }',
                             timeout=20000)
    ir('queue')
    return pagina.locator('.nowPlayingPage:not(.hide)')


@pytest.mark.usuario('tocador')
def test_player_falado_nao_tem_analisador_e_tem_os_controles(pagina, ir, item):
    tela = _tocar_episodio(pagina, ir, item)
    tela.locator('.cromaSpoken').wait_for()
    assert tela.locator('.cromaSpoken-skip').all_inner_texts() == ['−30 s', '−15 s', '+15 s', '+30 s']
    assert tela.locator('.cromaAnalyzer').is_hidden()
    assert tela.locator('.cromaSpoken-speed').inner_text() == '1,0×'


@pytest.mark.usuario('tocador')
def test_menu_de_velocidade_vai_de_0_8_a_2_e_muda_a_velocidade(pagina, ir, item):
    tela = _tocar_episodio(pagina, ir, item)
    tela.locator('.cromaSpoken-speed').click()
    opcoes = pagina.locator('.actionSheetMenuItem')
    opcoes.first.wait_for()
    textos = [t.strip() for t in opcoes.all_inner_texts()]
    assert textos[0] == '0,8×' and textos[-1] == '2,0×' and len(textos) == 13
    opcoes.filter(has_text='1,5×').click()
    pagina.wait_for_function('() => document.querySelector("audio.mediaPlayerAudio").playbackRate === 1.5')
    assert tela.locator('.cromaSpoken-speed').inner_text() == '1,5×'


@pytest.mark.usuario('tocador')
def test_temporizador_tem_as_cinco_opcoes_e_mostra_a_contagem(pagina, ir, item):
    tela = _tocar_episodio(pagina, ir, item)
    tela.locator('.cromaSpoken-sleep').click()
    opcoes = pagina.locator('.actionSheetMenuItem')
    opcoes.first.wait_for()
    assert [t.strip() for t in opcoes.all_inner_texts()] == ['Fim do capítulo', '15 min', '30 min', '60 min', 'Desligado']
    opcoes.filter(has_text='15 min').click()
    chip = tela.locator('.cromaSpoken-chip')
    chip.wait_for(state='visible')
    assert ' '.join(chip.inner_text().split()).startswith('DORMIR EM 14:5') or ' '.join(chip.inner_text().split()).startswith('DORMIR EM 15:00')


@pytest.mark.usuario('tocador')
def test_pulo_de_15_segundos_anda_o_episodio(pagina, ir, item):
    tela = _tocar_episodio(pagina, ir, item)
    antes = pagina.evaluate('() => document.querySelector("audio.mediaPlayerAudio").currentTime')
    tela.locator('.cromaSpoken-skip', has_text='+15 s').click()
    pagina.wait_for_function(f'() => document.querySelector("audio.mediaPlayerAudio").currentTime > {antes} + 0.4 || document.querySelector("audio.mediaPlayerAudio").ended')


def test_galeria_de_podcasts_diz_quantos_episodios_e_novos(pagina, ir, biblioteca):
    ir(f'books?topParentId={biblioteca("Podcasts")["id"]}&collectionType=books&tab=0')
    cartao = pagina.locator('.card', has_text='Podcast de Teste')
    cartao.wait_for()
    pagina.wait_for_function("document.querySelector('.card').innerText.includes('episódios')")
    texto = ' '.join(cartao.inner_text().split())
    assert '3 episódios · 3 novos' in texto
    assert cartao.get_attribute('class').count('squareCard') == 1


def test_pagina_do_programa_lista_episodios_do_mais_novo_ao_mais_antigo(pagina, ir, biblioteca):
    ir(f'books?topParentId={biblioteca("Podcasts")["id"]}&collectionType=books&tab=0')
    pagina.locator('.card .cardImageContainer').first.click(force=True)
    pagina.locator('.cromaProgram').wait_for()
    assert ' '.join(pagina.locator('.cromaProgram-kicker').inner_text().split()) == 'PODCAST · ÁUDIOS'
    assert pagina.locator('.cromaProgram-title').inner_text() == 'Podcast de Teste'
    assert pagina.locator('.cromaProgram-play').inner_text() == 'Ouvir o mais novo'
    linhas = pagina.locator('.cromaEpisode')
    linhas.first.wait_for()
    assert linhas.count() == 3
    assert linhas.first.get_attribute('data-state') == 'new'
    pagina.screenshot(path='/tmp/claude-1000/programa.png')


@pytest.mark.usuario('tocador')
def test_continuar_ouvindo_mostra_o_que_falta(pagina, ir, biblioteca, item):
    episodio = item('AudioBook', 'Episodio 2')
    ir('home')
    pagina.evaluate('''async (id) => {
        const c = window.ApiClient;
        await c.ajax({type: 'POST', url: c.getUrl('UserItems/' + id + '/UserData', {userId: c.getCurrentUserId()}),
                      data: JSON.stringify({PlaybackPositionTicks: 30000000}), contentType: 'application/json'});
    }''', episodio)
    ir(f'music?topParentId={biblioteca("Músicas")["id"]}&collectionType=music&tab=0')
    pagina.locator('.MuiTabs-root [role="tab"]', has_text='Resumo').click()
    titulo = pagina.locator('.sectionTitle', has_text='Continuar ouvindo')
    titulo.wait_for(timeout=15000)
    secao = titulo.locator('xpath=ancestor::*[contains(@class,"verticalSection")][1]')
    secao.locator('.card').first.wait_for()
    assert 'faltam' in secao.inner_text().lower()
    # devolve o item ao estado de antes, para não mudar o Início dos outros testes
    pagina.evaluate('''async (id) => {
        const c = window.ApiClient;
        await c.ajax({type: 'POST', url: c.getUrl('UserItems/' + id + '/UserData', {userId: c.getCurrentUserId()}),
                      data: JSON.stringify({PlaybackPositionTicks: 0}), contentType: 'application/json'});
    }''', item('AudioBook', 'Episodio 2'))
