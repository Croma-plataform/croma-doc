"""Detalhe do filme (prancha 28): kicker, botões, faixa de baixo e o que ficou de fora."""
import re

import pytest

PAGINA = '#itemDetailPage:not(.hide) '


def test_cabecalho_do_filme(pagina, ir, item):
    ir(f'details?id={item("Movie", "Barras Faixas (2003)")}')

    assert 'FILME' in pagina.locator(PAGINA + '.detailKicker').inner_text().upper()
    assert 'Barras Faixas' in pagina.locator(PAGINA + '.nameContainer').inner_text()
    assert pagina.locator(PAGINA + '.btnPlay').first.inner_text().strip() == 'Assistir'


def test_campos_de_faixas_ficam_so_no_arquivo(pagina, ir, item):
    """Decisão de 09/11/2026: Vídeo, Áudio e Legendas saem de baixo dos botões e ficam no bloco Arquivo."""
    ir(f'details?id={item("Movie", "Barras Faixas (2003)")}')

    for seletor in ('.selectVideoContainer', '.selectAudioContainer', '.selectSubtitlesContainer'):
        assert not pagina.locator(PAGINA + seletor).first.is_visible(), seletor

    arquivo = pagina.locator(PAGINA + '.detailFooter-file').inner_text()
    assert arquivo.startswith('Arquivo')
    assert 'H.264' in arquivo
    assert 'português' in arquivo and 'inglês' in arquivo       # as duas faixas de áudio
    assert re.search(r'\d,\d\d MB · MKV', arquivo)               # tamanho e contêiner
    assert re.search(r'Reprodução direta|convertid[oa] pelo servidor', arquivo)


def test_filme_sem_dados_nao_desenha_ficha_tecnica(pagina, ir, item):
    """A mídia de teste não tem elenco nem direção: o bloco Ficha técnica não aparece vazio."""
    ir(f'details?id={item("Movie", "Barras Direto (2001)")}')

    assert not pagina.locator(PAGINA + '.detailFooter-sheet').first.is_visible()
    assert pagina.locator(PAGINA + '.detailFooter-file').first.is_visible()


def test_secao_fica_destacada_no_detalhe(pagina, ir, item, layout):
    if layout == 'tv':
        return  # a TV usa o menu legado; o menu de seções dela é o módulo T03
    ir(f'details?id={item("Movie", "Barras Direto (2001)")}')

    atual = pagina.locator('.MuiDrawer-root .Mui-selected')
    assert 'Audiovisual' in atual.first.inner_text()


def test_visual_do_detalhe(pagina, ir, item, conferir):
    ir(f'details?id={item("Movie", "Barras Faixas (2003)")}')
    conferir('detalhe-filme-faixas')


def _editar(api_admin, id_item, **campos):
    """Muda campos do item e devolve os valores antigos (para restaurar)."""
    dto = api_admin(f'Items/{id_item}')
    antigos = {k: dto.get(k) for k in campos}
    dto.update(campos)
    api_admin(f'Items/{id_item}', dto, 'POST')
    return antigos


def test_edicao_e_classificacao_aparecem_no_detalhe(pagina, ir, item, api_admin):
    id_item = item('Movie', 'Barras Capitulos (2004)')
    antigos = _editar(api_admin, id_item, Tags=['Diretor'], OfficialRating='14')
    try:
        ir(f'details?id={id_item}')
        assert pagina.locator(PAGINA + '.detailEdition').inner_text().strip().lower() == 'diretor'
        classificacao = pagina.locator(PAGINA + '.mediaInfoOfficialRating').first
        assert classificacao.inner_text().strip() == '14'
        cor = classificacao.evaluate('e => getComputedStyle(e).backgroundColor')
        assert cor == 'rgb(242, 242, 240)'     # Fósforo
    finally:
        _editar(api_admin, id_item, **antigos)


@pytest.mark.usuario('admin')
def test_favoritar_e_marcar_como_visto(pagina, ir, item, api_admin):
    id_item = item('Movie', 'Barras Direto (2001)')
    uid = api_admin.uid
    try:
        ir(f'details?id={id_item}')
        pagina.locator(PAGINA + '.btnPlaystate').first.click()
        pagina.locator(PAGINA + '.btnUserRating').first.click()
        pagina.wait_for_timeout(1500)
        dados = api_admin(f'Users/{uid}/Items/{id_item}')['UserData']
        assert dados['Played'] is True
        assert dados['IsFavorite'] is True
    finally:
        api_admin(f'Users/{uid}/PlayedItems/{id_item}', None, 'DELETE')
        api_admin(f'Users/{uid}/FavoriteItems/{id_item}', None, 'DELETE')
