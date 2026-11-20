"""Leitura: HQs e mangás (módulo D13)."""
import pytest


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV entra no módulo T07')


def _abrir(pagina, ir, item, nome):
    ir(f'details?id={item("Book", nome)}')
    pagina.locator('#itemDetailPage:not(.hide) .btnPlay').first.click()
    pagina.locator('#comicsPlayer .bookOsdPage').wait_for(timeout=30000)
    return pagina.locator('#comicsPlayer')


def test_hq_le_da_esquerda_e_mostra_pagina_e_volume(pagina, ir, item):
    leitor = _abrir(pagina, ir, item, 'HQ de Teste 1')
    assert ' '.join(leitor.locator('.bookOsdPage').inner_text().split()) == 'VOL. 1 · P. 1 DE 6'
    assert leitor.locator('.bookOsdDirection').inner_text() == 'LER → DA ESQUERDA'
    pagina.screenshot(path='/tmp/claude-1000/hq.png')


def test_manga_le_da_direita_por_padrao(pagina, ir, item):
    leitor = _abrir(pagina, ir, item, 'Manga de Teste 1')
    assert leitor.locator('.bookOsdDirection').inner_text() == 'LER ← DA DIREITA'
    assert leitor.locator('.slideshowSwiperContainer').get_attribute('dir') == 'rtl'
    pagina.screenshot(path='/tmp/claude-1000/manga.png')


def test_resumo_de_leitura_tem_continuar_lendo_e_os_recentes(pagina, ir, biblioteca, item):
    ir('home')
    pagina.evaluate('''async (id) => {
        const c = window.ApiClient;
        await c.ajax({type: 'POST', url: c.getUrl('UserItems/' + id + '/UserData', {userId: c.getCurrentUserId()}),
                      data: JSON.stringify({PlaybackPositionTicks: 20000000}), contentType: 'application/json'});
    }''', item('Book', 'HQ de Teste 2'))
    ir(f'books?topParentId={biblioteca("Livros")["id"]}&collectionType=books&tab=0')
    pagina.locator('.MuiTabs-root [role="tab"]', has_text='Resumo').click()
    titulos = pagina.locator('.sectionTitle')
    titulos.filter(has_text='Continuar lendo').wait_for(timeout=15000)
    textos = [t.strip() for t in titulos.all_inner_texts()]
    assert 'Continuar lendo' in textos
    assert any(t.startswith('Adicionados recentemente') for t in textos)
    # devolve o item ao estado de antes, para não mudar o Início dos outros testes
    pagina.evaluate('''async (id) => {
        const c = window.ApiClient;
        await c.ajax({type: 'POST', url: c.getUrl('UserItems/' + id + '/UserData', {userId: c.getCurrentUserId()}),
                      data: JSON.stringify({PlaybackPositionTicks: 0}), contentType: 'application/json'});
    }''', item('Book', 'HQ de Teste 2'))
