"""Ajustes e calibração (módulo D17)."""
import pytest


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV entra no módulo T07')


def test_calibracao_abre_pelos_ajustes_e_percorre_as_tres_etapas(pagina, ir, conferir, api_admin):
    uid = next(u['Id'] for u in api_admin('Users') if u['Name'] == 'leitor')
    ir(f'mypreferencesdisplay?userId={uid}')
    pagina.locator('[data-testid="open-calibration"]').click()
    pagina.wait_for_url('**/calibration**')
    etapa = pagina.locator('[data-testid="calibration-step"]')
    padrao = pagina.locator('[data-testid="calibration-pattern"]')

    assert '1 / 3' in etapa.inner_text() and 'BRILHO' in etapa.inner_text().upper()
    assert padrao.get_attribute('data-step') == 'brightness'
    assert [d.get_attribute('data-level') for d in padrao.locator('> div').all()] == ['0', '16', '32', '16']
    conferir('calibracao-brilho')

    pagina.get_by_role('button', name='Próxima etapa').click()
    assert padrao.get_attribute('data-step') == 'contrast'
    assert padrao.locator('> div').first.get_attribute('data-level') == '255'
    conferir('calibracao-contraste')

    pagina.get_by_role('button', name='Próxima etapa').click()
    assert padrao.get_attribute('data-step') == 'color'
    assert padrao.locator('> div').count() == 7
    conferir('calibracao-cor')

    pagina.get_by_role('button', name='Concluir').click()
    pagina.wait_for_url('**/mypreferencesdisplay**')




def test_uma_preferencia_vale_depois_de_recarregar(pagina, ir, api_admin):
    uid = next(u['Id'] for u in api_admin('Users') if u['Name'] == 'leitor')
    url = f'mypreferencesdisplay?userId={uid}'
    ir(url, espera=2500)
    caixa = pagina.locator('#displayPreferencesPage input[type="checkbox"]').first
    caixa.wait_for(state='attached')
    antes = caixa.is_checked()
    try:
        caixa.evaluate('e => e.click()')
        pagina.get_by_role('button', name='Salvar').click()
        pagina.wait_for_timeout(1500)
        ir(url, espera=2500)
        depois = pagina.locator('#displayPreferencesPage input[type="checkbox"]').first
        depois.wait_for(state='attached')
        assert depois.is_checked() != antes
    finally:
        ir(url, espera=2500)
        c = pagina.locator('#displayPreferencesPage input[type="checkbox"]').first
        if c.is_checked() != antes:
            c.evaluate('e => e.click()')
            pagina.get_by_role('button', name='Salvar').click()
            pagina.wait_for_timeout(1500)
