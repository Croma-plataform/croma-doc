"""Componentes comuns da interface (módulo D02): capa gerada, cartões, avisos, vazio."""
import pytest


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('estes componentes são conferidos no desktop; a TV entra no módulo T02')


def test_item_sem_arte_mostra_a_capa_gerada_e_item_com_arte_nao(pagina, ir, biblioteca):
    ir(f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=0')
    pagina.locator('.card').first.wait_for()
    cartoes = {c.locator('.cardText-first').first.inner_text().strip(): c for c in pagina.locator('.card').all()}

    sem_arte = cartoes['Barras Direto (2001)']
    capa = sem_arte.locator('[data-testid="generated-cover"]')
    assert capa.count() == 1
    assert 'Barras' in capa.get_attribute('aria-label')
    # o quadrado da seção e as 7 barras
    assert capa.locator('rect').count() == 2 + 7

    com_arte = [c for n, c in cartoes.items() if n.startswith('Barras Com Arte')][0]
    assert com_arte.locator('[data-testid="generated-cover"]').count() == 0


def test_alternar_grade_e_lista(pagina, ir, biblioteca):
    ir(f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=0')
    alternador = pagina.locator('[data-testid="view-mode-toggle"]')
    alternador.wait_for()
    grade, lista = alternador.locator('button').nth(0), alternador.locator('button').nth(1)
    assert grade.get_attribute('aria-pressed') == 'true'
    lista.click()
    pagina.wait_for_selector('.listItem')
    assert lista.get_attribute('aria-pressed') == 'true'
    assert pagina.locator('.card').count() == 0
    grade.click()
    pagina.locator('.card').first.wait_for()
    assert grade.get_attribute('aria-pressed') == 'true'


def test_aviso_aparece_e_some_e_so_tres_ficam_empilhados(pagina, ir):
    ir('mostruario')
    pagina.click('#avisoSucesso')
    aviso = pagina.locator('.toast.toast-success')
    aviso.wait_for()
    assert 'Salvo' in aviso.inner_text()
    aviso.wait_for(state='detached', timeout=8000)  # sucesso some em 4 s

    for _ in range(4):
        pagina.click('#avisoErro')
    pagina.wait_for_timeout(500)
    assert pagina.locator('.toast').count() <= 3
    # o erro fica até a pessoa agir: clicar dispensa
    pagina.wait_for_timeout(4500)
    assert pagina.locator('.toast-error').count() >= 1
    pagina.locator('.toast-error').first.click()


def test_movimento_reduzido_deixa_o_carregando_parado(pagina, ir):
    pagina.emulate_media(reduced_motion='reduce')
    ir('mostruario')
    duracao = pagina.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--croma-dur-padrao')")
    assert duracao.strip() == '0ms'


def test_mostruario_tem_todos_os_componentes(pagina, ir, conferir):
    ir('mostruario')
    assert pagina.locator('[data-testid="generated-cover"]').count() == 3
    assert pagina.locator('[data-testid="card-skeletons"]').count() == 1
    assert pagina.locator('[data-testid="empty-state"]').count() == 1
    pagina.wait_for_timeout(500)
    conferir('mostruario')
