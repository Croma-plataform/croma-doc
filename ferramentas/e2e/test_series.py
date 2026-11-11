"""Séries e episódios (módulo D04)."""
import pytest

PAGINA = '#itemDetailPage:not(.hide) '


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV entra no módulo T04')


def test_visual_da_galeria_de_series(pagina, ir, biblioteca, conferir):
    ir(f'tv?topParentId={biblioteca("Séries")["id"]}&collectionType=tvshows&tab=0')
    pagina.locator('.card').first.wait_for()
    conferir('grade-series')


def test_visual_do_detalhe_da_serie(pagina, ir, item, conferir):
    ir(f'details?id={item("Series", "Serie de Teste")}')
    conferir('detalhe-serie')


def test_visual_do_detalhe_do_episodio(pagina, ir, item, conferir):
    ir(f'details?id={item("Episode", "Serie de Teste - S01E02 - Episodio 2")}')
    conferir('detalhe-episodio')


EPISODIOS = [f'Serie de Teste - S{t:02d}E{e:02d} - Episodio {e}' for t, e in ((1, 1), (1, 2), (1, 3), (2, 1), (2, 2))]


@pytest.fixture
def marcar_vistos(item, api_admin):
    """Marca os `n` primeiros episódios como vistos para o administrador e desfaz no fim."""
    marcados = []

    def _marcar(n):
        for nome in EPISODIOS[:n]:
            ident = item('Episode', nome)
            api_admin(f'Users/{api_admin.uid}/PlayedItems/{ident}', None, 'POST')
            marcados.append(ident)
    yield _marcar
    for ident in marcados:
        api_admin(f'Users/{api_admin.uid}/PlayedItems/{ident}', None, 'DELETE')


@pytest.mark.usuario('admin')
def test_serie_sem_nada_visto(pagina, ir, item):
    ir(f'details?id={item("Series", "Serie de Teste")}')
    assert 'T1 E01' in pagina.locator('.episodeStrip-next').inner_text()
    assert '0 de 5' in pagina.locator('.episodeStrip-status').inner_text()
    assert pagina.locator('.episodeStrip-segment').count() == 5


@pytest.mark.usuario('admin')
def test_serie_pela_metade_e_proximo_abre_o_episodio_certo(pagina, ir, item, marcar_vistos):
    marcar_vistos(1)
    ir(f'details?id={item("Series", "Serie de Teste")}')
    assert 'T1 E02' in pagina.locator('.episodeStrip-next').inner_text()
    assert '1 de 5' in pagina.locator('.episodeStrip-status').inner_text()
    pagina.locator('.episodeStrip-segment.episodeStrip-next, .episodeStrip-segment').nth(1).click()
    pagina.wait_for_url(f'**id={item("Episode", EPISODIOS[1])}**')


@pytest.mark.usuario('admin')
def test_serie_toda_vista(pagina, ir, item, marcar_vistos):
    marcar_vistos(5)
    ir(f'details?id={item("Series", "Serie de Teste")}')
    assert '5 de 5' in pagina.locator('.episodeStrip-status').inner_text()
    assert pagina.locator('.episodeStrip-next').count() == 0


def test_episodio_tem_kicker_e_ficha_do_arquivo(pagina, ir, item):
    ir(f'details?id={item("Episode", EPISODIOS[1])}')
    assert 'EPISÓDIO · T1 E02' in pagina.locator(PAGINA + '.detailKicker').inner_text().upper()
    assert pagina.locator(PAGINA + '.detailFooter-file').inner_text().startswith('Arquivo')
