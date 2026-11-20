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


def test_pagina_do_album_tem_kicker_info_e_botoes_com_texto(pagina, ir, item):
    ir(f'details?id={item("MusicAlbum", "Album Um")}')
    pagina.locator('.detailKicker').wait_for()
    assert ' '.join(pagina.locator('.detailKicker').inner_text().split()) == 'ÁLBUM · λ 530 nm'
    assert pagina.locator('.itemMiscInfo-primary').first.inner_text().split() == ['3', 'faixas', '0:24']
    rotulos = pagina.locator('.mainDetailButtons .detailButton:visible .detailButton-label:visible')
    # a ordem na tela (da esquerda para a direita), não a do HTML
    lidos = sorted((rotulos.nth(i).bounding_box()['x'], rotulos.nth(i).inner_text().strip()) for i in range(rotulos.count()))
    assert [r for _, r in lidos] == ['Tocar', 'Aleatório', 'Rádio do álbum']


@pytest.mark.usuario('tocador')
def test_lista_de_faixas_do_album_numera_em_mono_e_marca_a_que_toca(pagina, ir, item):
    ir(f'details?id={item("MusicAlbum", "Album Um")}')
    linhas = pagina.locator('.cromaTrackList .listItem')
    linhas.first.wait_for()
    assert linhas.count() == 3
    assert [linhas.nth(i).locator('.listItem-indexnumberleft').inner_text() for i in range(3)] == ['01', '02', '03']
    assert pagina.locator('.cromaTrackCurrent').count() == 0

    _tocar_album(pagina, ir, item)
    atual = pagina.locator('.cromaTrackCurrent')
    atual.wait_for()
    assert atual.count() == 1
    assert atual.locator('.cromaEqualizer i').count() == 3
    assert atual.locator('.listItem-indexnumberleft').evaluate('e => getComputedStyle(e).color') == 'rgb(0, 192, 0)'
    pagina.screenshot(path='/tmp/claude-1000/album-faixas.png')


def test_resumo_de_audios_tem_albuns_recentes_e_artistas(pagina, ir, biblioteca):
    ir(f'music?topParentId={biblioteca("Músicas")["id"]}&collectionType=music&tab=0')
    pagina.locator('.MuiTabs-root [role="tab"]', has_text='Resumo').click()
    pagina.locator('.sectionTitle', has_text='Adicionados recentemente').wait_for()
    titulos = [t.strip() for t in pagina.locator('.sectionTitle').all_inner_texts()]
    assert 'Adicionados recentemente' in titulos
    assert 'Artistas' in titulos
    artista = pagina.locator('.sectionTitle', has_text='Artistas').locator('xpath=ancestor::*[contains(@class,"verticalSection")][1]')
    artista.locator('.card').first.wait_for()
    assert artista.locator('.card[class*="quareCard"]').count() >= 1
    pagina.screenshot(path='/tmp/claude-1000/resumo-audios.png')


def _png(cor):
    import struct
    import zlib
    linha = b'\x00' + bytes(cor) * 8
    bruto = linha * 8

    def parte(tipo, dados):
        corpo = tipo + dados
        return struct.pack('>I', len(dados)) + corpo + struct.pack('>I', zlib.crc32(corpo))
    return (b'\x89PNG\r\n\x1a\n' + parte(b'IHDR', struct.pack('>IIBBBBB', 8, 8, 8, 2, 0, 0, 0))
            + parte(b'IDAT', zlib.compress(bruto)) + parte(b'IEND', b''))


def test_artista_sem_foto_e_sem_capa_de_album_fica_com_a_capa_gerada(pagina, ir, item):
    ir(f'details?id={item("MusicArtist", "Artista de Teste")}')
    capa = pagina.locator('#itemDetailPage:not(.hide) .detailImageContainer .cromaArtistCover[data-kind]').first
    capa.wait_for(timeout=15000)
    assert capa.get_attribute('data-kind') == 'generated'
    assert capa.locator('svg.generatedCover').count() == 1


def test_artista_sem_foto_ganha_mosaico_dos_albuns(pagina, ir, item):
    import json
    artista = item("MusicArtist", "Artista de Teste")
    albuns = {'Items': [{'Id': 'a1', 'Name': 'A', 'ImageTags': {'Primary': 'x'}},
                        {'Id': 'a2', 'Name': 'B', 'ImageTags': {'Primary': 'y'}}], 'TotalRecordCount': 2}
    pagina.route(lambda url: 'ArtistIds' in url and 'Limit=8' in url and '/Items?' in url, lambda r: r.fulfill(status=200, content_type='application/json', body=json.dumps(albuns)))
    pagina.route('**/Items/a1/Images/Primary*', lambda r: r.fulfill(status=200, content_type='image/png', body=_png((200, 0, 0))))
    pagina.route('**/Items/a2/Images/Primary*', lambda r: r.fulfill(status=200, content_type='image/png', body=_png((0, 0, 200))))
    ir(f'details?id={artista}')
    capa = pagina.locator('#itemDetailPage:not(.hide) .detailImageContainer .cromaArtistCover[data-kind]').first
    capa.wait_for(timeout=15000)
    assert capa.get_attribute('data-kind') == 'mosaic'
    assert capa.locator('.cromaArtistCover-image').count() == 2
    assert capa.locator('.cromaArtistCover-tag').inner_text() == 'MOSAICO'
    pagina.wait_for_timeout(500)
    pagina.screenshot(path='/tmp/claude-1000/artista.png')


def test_pagina_do_artista_tem_kicker_botoes_e_mais_tocadas(pagina, ir, item):
    ir(f'details?id={item("MusicArtist", "Artista de Teste")}')
    kicker = pagina.locator('#itemDetailPage:not(.hide) .detailKicker').first
    kicker.wait_for()
    pagina.wait_for_function("document.querySelector('#itemDetailPage:not(.hide) .detailKicker').innerText.includes('FAIXAS')")
    assert ' '.join(kicker.inner_text().split()).startswith('ARTISTA · 2 ÁLBUNS · ')
    rotulos = pagina.locator('.mainDetailButtons .detailButton:visible .detailButton-label:visible')
    lidos = sorted((rotulos.nth(i).bounding_box()['x'], rotulos.nth(i).inner_text().strip()) for i in range(rotulos.count()))
    assert [r for _, r in lidos] == ['Tocar tudo', 'Aleatório', 'Rádio do artista']
    linhas = pagina.locator('#itemDetailPage:not(.hide) .cromaTopTrack')
    linhas.first.wait_for()
    assert 1 <= linhas.count() <= 5
    assert linhas.first.locator('.cromaTopTrack-number').inner_text() == '01'
    pagina.screenshot(path='/tmp/claude-1000/artista2.png')
    titulos = [t.strip().lower() for t in pagina.locator('#itemDetailPage:not(.hide) .sectionTitle:visible').all_inner_texts()]
    assert 'mais tocadas' in titulos and 'na biblioteca' in titulos, titulos


@pytest.mark.usuario('tocador')
def test_tocando_agora_mostra_faixa_a_seguir_formato_e_tempo_que_falta(pagina, ir, item):
    _tocar_album(pagina, ir, item)
    ir('queue')
    tela = pagina.locator('.nowPlayingPage:not(.hide)')
    tela.locator('.cromaNowKicker').wait_for()
    assert 'MÚSICA · TOCANDO AGORA' in ' '.join(tela.locator('.cromaNowKicker').inner_text().split())
    pagina.wait_for_function("document.querySelector('.nowPlayingPage:not(.hide) .cromaNowLine').innerText.includes('FAIXA')")
    linha = ' '.join(tela.locator('.cromaNowLine').inner_text().split())
    assert linha.startswith('FAIXA 1 DE 3 · ALBUM UM')
    tela.locator('.cromaNowUpNext-row').first.wait_for()
    assert tela.locator('.cromaNowUpNext-row').count() == 2
    assert 'Faixa 2' in tela.locator('.cromaNowUpNext-row').first.inner_text()
    pagina.wait_for_function("/^−\\d+:\\d\\d · \\d+:\\d\\d$/.test(document.querySelector('.nowPlayingPage:not(.hide) .cromaNowRemaining').innerText)")
    pagina.screenshot(path='/tmp/claude-1000/tocando.png')
    assert tela.locator('.cromaNowTech-chip').count() >= 1
