"""Ajustes (módulo D17): o menu lateral das telas de ajustes (prancha 34)."""
import pytest

MENU = '[data-testid="settings-menu"]'


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV usa o menu de ajustes próprio (módulo T10)')


@pytest.mark.parametrize('rota,ativo', [
    ('mypreferencesdisplay', 'Exibição'),
    ('mypreferencesplayback', 'Reprodução'),
    ('mypreferencessubtitles', 'Legendas'),
    ('mypreferenceshome', 'Tela inicial'),
])
def test_menu_mostra_a_tela_ativa(pagina, ir, rota, ativo):
    ir(rota)
    pagina.locator(MENU).wait_for()
    atual = pagina.locator(f'{MENU} [aria-current="page"]')
    assert atual.count() == 1 and atual.inner_text().strip() == ativo


def test_menu_leva_de_uma_tela_a_outra(pagina, ir):
    ir('mypreferencesdisplay')  # o menu leva o id do usuário na rota de cada tela
    pagina.locator(f'{MENU} a', has_text='Legendas').click()
    pagina.wait_for_url('**#/mypreferencessubtitles?userId=*')
    assert pagina.locator(f'{MENU} [aria-current="page"]').inner_text().strip() == 'Legendas'


def test_menu_tem_o_perfil_do_usuario(pagina, ir):
    ir('mypreferencesdisplay')
    pagina.locator(f'{MENU} a', has_text='Perfil').click()
    pagina.wait_for_url('**#/userprofile?userId=*')


def test_menu_nao_aparece_fora_dos_ajustes(pagina, ir):
    ir('home')
    assert pagina.locator(MENU).count() == 0


def test_visual_do_menu_dos_ajustes(pagina, ir, api_admin, conferir):
    uid = next(u['Id'] for u in api_admin('Users') if u['Name'] == 'leitor')
    ir(f'mypreferencesdisplay?userId={uid}', espera=2500)
    pagina.locator(MENU).wait_for()
    pagina.locator('.cromaSegmented').first.wait_for()  # o conteúdo da tela ao lado do menu
    pagina.wait_for_timeout(500)
    conferir('ajustes-menu')
