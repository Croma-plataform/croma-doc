"""Entrada e perfis (módulo D16, prancha 31): avatar de barras, senha errada, entrar e sair."""
import pytest

from conftest import LAYOUTS


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV entra no módulo T07')


@pytest.fixture
def perfis_visiveis(api_admin):
    """Mostra a conta `leitor` na tela de entrada e desfaz no fim."""
    usuario = next(u for u in api_admin('Users') if u['Name'] == 'leitor')
    politica = usuario['Policy']
    antes = politica.get('IsHidden')
    api_admin(f"Users/{usuario['Id']}/Policy", {**politica, 'IsHidden': False}, 'POST')
    yield
    api_admin(f"Users/{usuario['Id']}/Policy", {**politica, 'IsHidden': antes}, 'POST')


@pytest.fixture
def visitante(navegador, base):
    """Uma página sem sessão."""
    ctx = navegador.new_context(viewport=LAYOUTS['desktop'], locale='pt-BR')
    pg = ctx.new_page()
    pg.goto(base + '#/login')
    pg.wait_for_selector('#txtManualName, .btnManual, [data-testid="profile-avatar"]', timeout=30000)
    yield pg
    ctx.close()


def _entrar(pg, usuario, senha):
    if not pg.locator('#txtManualName').is_visible():
        manual = pg.locator('.btnManual').first
        if manual.count():
            manual.click()
    pg.fill('#txtManualName', usuario)
    pg.fill('#txtManualPassword', senha)
    pg.locator('#txtManualPassword').press('Enter')


def test_perfis_tem_avatar_de_barras_com_a_inicial(perfis_visiveis, navegador, base):
    ctx = navegador.new_context(viewport=LAYOUTS['desktop'], locale='pt-BR')
    visitante = ctx.new_page()
    visitante.goto(base + '#/login')
    visitante.wait_for_selector('[data-testid="profile-avatar"]', timeout=30000)
    avatares = visitante.locator('[data-testid="profile-avatar"]')
    assert avatares.count() == 1
    for i in range(avatares.count()):
        avatar = avatares.nth(i)
        assert avatar.locator('.cromaAvatarBars span').count() == 7
        assert avatar.locator('.cromaAvatarPlate').inner_text().strip() == 'L'
    ctx.close()


def test_senha_errada_nao_entra(visitante):
    _entrar(visitante, 'leitor', 'errada')
    visitante.wait_for_timeout(2500)
    assert '/login' in visitante.url
    assert visitante.locator('.toast-error, .toast').count() >= 1


def test_entrar_e_sair(visitante):
    _entrar(visitante, 'leitor', 'teste')
    visitante.wait_for_url('**/home**', timeout=30000)
    visitante.locator('button[aria-controls="app-user-menu"]').first.click()
    visitante.locator('li:visible, [role="menuitem"]:visible', has_text='Sair').first.click()
    visitante.wait_for_url('**/login**', timeout=30000)
