"""Fotos (módulo D14)."""
import pytest


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV entra no módulo T06')


def _abrir(pagina, ir, biblioteca):
    # A aba Fotos da biblioteca de fotos é a de índice 1 (a 0 são as pastas)
    ir(f'homevideos?topParentId={biblioteca("Fotos")["id"]}&collectionType=homevideos&tab=1')
    pagina.locator('[data-testid="photo"]').first.wait_for()
    pagina.wait_for_timeout(800)


def test_grade_justificada_agrupada_por_mes(pagina, ir, biblioteca):
    _abrir(pagina, ir, biblioteca)
    assert pagina.locator('[data-testid="photo"]').count() == 7
    assert pagina.locator('[data-testid="photos-month"]').count() >= 1
    titulo = pagina.locator('[data-testid="photos-month"] h2').first.inner_text().upper()
    assert '7 ITENS' in titulo


def test_cada_fileira_cheia_fecha_a_largura(pagina, ir, biblioteca):
    _abrir(pagina, ir, biblioteca)
    larguras = pagina.evaluate('''() => {
        const grade = document.querySelector('[data-testid="photos-grid"]');
        const total = grade.clientWidth;
        return { total, linhas: [...document.querySelectorAll('.cromaPhotosRow')].map(r => {
            const fotos = [...r.children]; const w = fotos.reduce((s, f) => s + f.getBoundingClientRect().width, 0) + 8 * (fotos.length - 1);
            return w; }) };
    }''')
    # todas as fileiras menos a última (que mantém a altura) fecham a largura
    for w in larguras['linhas'][:-1]:
        assert abs(w - larguras['total']) < 2, larguras


@pytest.mark.usuario('admin')
def test_favorita_ganha_o_quadrado_magenta(pagina, ir, biblioteca, item, api_admin):
    ident = item('Photo', 'foto-1')
    uid = api_admin.uid
    api_admin(f'Users/{uid}/FavoriteItems/{ident}', None, 'POST')
    try:
        _abrir(pagina, ir, biblioteca)
        marca = pagina.locator('[data-testid="photo-favorite"]')
        marca.first.wait_for()
        assert marca.count() == 1
        assert marca.first.evaluate('e => getComputedStyle(e).backgroundColor') == 'rgb(192, 0, 192)'
    finally:
        api_admin(f'Users/{uid}/FavoriteItems/{ident}', None, 'DELETE')


def test_abrir_uma_foto(pagina, ir, biblioteca):
    _abrir(pagina, ir, biblioteca)
    pagina.locator('[data-testid="photo"]').first.click()
    pagina.wait_for_url('**/details**')


def test_visual_da_galeria_de_fotos(pagina, ir, biblioteca, conferir):
    _abrir(pagina, ir, biblioteca)
    conferir('galeria-fotos')


def _abrir_visualizador(pagina, ir, item, nome='foto-1'):
    ir(f'details?id={item("Photo", nome)}')
    pagina.locator('#itemDetailPage:not(.hide) .btnPlay').first.click()
    pagina.locator('.slideshowDialog.cromaViewer').wait_for()
    pagina.locator('[data-testid="viewer-strip"] .cromaViewerThumb').first.wait_for()


def test_visualizador_diz_onde_esta_e_mostra_a_fita(pagina, ir, item):
    _abrir_visualizador(pagina, ir, item)
    kicker = pagina.locator('[data-testid="viewer-kicker"]')
    assert kicker.inner_text().upper().startswith('FOTOS · 1 DE ')
    miniaturas = pagina.locator('[data-testid="viewer-strip"] .cromaViewerThumb')
    assert 1 <= miniaturas.count() <= 9
    assert pagina.locator('[data-testid="viewer-strip"] [aria-current="true"]').count() == 1
    assert pagina.locator('[data-testid="viewer-info"]').count() == 1


def test_visualizador_avanca_e_a_fita_acompanha(pagina, ir, item):
    _abrir_visualizador(pagina, ir, item)
    total = int(pagina.locator('[data-testid="viewer-kicker"]').text_content().split(' de ')[1].split(' ')[0])
    pagina.keyboard.press('ArrowRight')
    pagina.wait_for_function("document.querySelector('[data-testid=\"viewer-kicker\"]').textContent.includes('2 de')")
    assert pagina.locator('[data-testid="viewer-strip"] [aria-current="true"]').get_attribute('data-index') == '1'
    # clicar numa miniatura leva a ela
    ultima = pagina.locator('[data-testid="viewer-strip"] .cromaViewerThumb').last
    indice = int(ultima.get_attribute('data-index'))
    ultima.click()
    pagina.wait_for_function(f"document.querySelector('[data-testid=\"viewer-kicker\"]').textContent.includes('{indice + 1} de {total}')")
    assert pagina.locator('[data-testid="viewer-strip"] [aria-current="true"]').get_attribute('data-index') == str(indice)


def _mostrar_barra(pagina):
    # o primeiro movimento só anota a posição do ponteiro; o seguinte, longe dele, mostra a barra
    pagina.mouse.move(300, 300)
    pagina.mouse.move(600, 400)
    pagina.locator('.slideshowBottomBar').wait_for(state='visible')


def test_barra_do_visualizador_tem_os_botoes_da_prancha(pagina, ir, item):
    _abrir_visualizador(pagina, ir, item)
    _mostrar_barra(pagina)
    for classe, nome in (('btnSlideshowPause', 'Apresentação'), ('btnRotate', 'Girar'),
                         ('btnPhotoInfo', 'Informações'), ('btnFavorite', 'Favorito')):
        assert pagina.locator(f'.slideshowBottomBar .{classe}').get_attribute('aria-label') == nome


def test_girar_a_foto_e_voltar_ao_fim_de_quatro_giros(pagina, ir, item):
    _abrir_visualizador(pagina, ir, item)
    _mostrar_barra(pagina)
    imagem = pagina.locator('.swiper-slide-active .swiper-slide-img')
    for graus in (90, 180, 270, 0):
        pagina.locator('.slideshowBottomBar .btnRotate').click()
        assert imagem.evaluate('e => e.style.transform') == f'rotate({graus}deg)'


def test_botao_de_informacoes_esconde_e_mostra_a_linha_de_dados(pagina, ir, item):
    _abrir_visualizador(pagina, ir, item)
    _mostrar_barra(pagina)
    info = pagina.locator('[data-testid="viewer-info"]')
    pagina.locator('.slideshowBottomBar .btnPhotoInfo').click()
    assert not info.is_visible()
    pagina.locator('.slideshowBottomBar .btnPhotoInfo').click()
    assert info.evaluate('e => getComputedStyle(e).display') != 'none'


def test_favoritar_a_foto_no_visualizador_grava_no_servidor(pagina, ir, item, api_admin):
    _abrir_visualizador(pagina, ir, item)
    _mostrar_barra(pagina)
    botao = pagina.locator('.slideshowBottomBar .btnFavorite')
    botao.click()
    pagina.wait_for_function("document.querySelector('.btnFavorite .material-icons').classList.contains('favorite')")
    assert botao.get_attribute('aria-pressed') == 'true'
    botao.click()  # deixa o servidor como estava
    pagina.wait_for_function("document.querySelector('.btnFavorite .material-icons').classList.contains('favorite_border')")


def test_visual_do_visualizador_de_fotos(pagina, ir, item, conferir):
    _abrir_visualizador(pagina, ir, item)
    pagina.wait_for_timeout(1200)
    pagina.mouse.move(5, 5)  # o ponteiro parado fora da foto: sem os botões que aparecem ao mexer
    conferir('visualizador-fotos')
