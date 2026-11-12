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


def test_seletor_de_passo_muda_o_tempo_do_descanso_e_vale_depois_de_recarregar(pagina, ir, api_admin, conferir):
    """Prancha 34: o tempo do descanso de tela é um seletor de passo (◂ valor ▸), de 1 em 1 minuto."""
    uid = next(u['Id'] for u in api_admin('Users') if u['Name'] == 'leitor')
    url = f'mypreferencesdisplay?userId={uid}'
    ir(url, espera=2500)
    passo = pagina.locator('[data-testid="stepper-screensaverTime"]')
    passo.wait_for()
    assert passo.locator('output').inner_text() == '5 min'
    passo.scroll_into_view_if_needed()
    conferir('ajustes-exibicao')
    try:
        passo.get_by_role('button', name='+').click()
        assert passo.locator('output').inner_text() == '6 min'
        pagina.get_by_role('button', name='Salvar').click()
        pagina.wait_for_timeout(1500)
        ir(url, espera=2500)
        assert pagina.locator('[data-testid="stepper-screensaverTime"] output').inner_text() == '6 min'
    finally:
        ir(url, espera=2500)
        passo = pagina.locator('[data-testid="stepper-screensaverTime"]')
        if passo.locator('output').inner_text() != '5 min':
            passo.get_by_role('button', name='−').click()
            pagina.get_by_role('button', name='Salvar').click()
            pagina.wait_for_timeout(1000)


def test_linha_de_calibrar_tem_as_barras_e_abre_a_calibracao(pagina, ir, api_admin):
    uid = next(u['Id'] for u in api_admin('Users') if u['Name'] == 'leitor')
    ir(f'mypreferencesdisplay?userId={uid}', espera=2500)
    linha = pagina.locator('[data-testid="open-calibration"]')
    assert linha.locator('.cromaCalibrationRow-bars > span').count() == 7
    assert 'Abrir' in linha.inner_text()
