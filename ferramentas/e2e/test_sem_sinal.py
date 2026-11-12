"""Sem sinal (módulo D18): o servidor não responde."""
import pytest


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV entra no módulo T07')


PADROES = ('**/System/Info/Public*', '**/System/Info*', '**/Users/Me*')


def test_servidor_fora_do_ar_mostra_sem_sinal_e_volta(pagina, base):
    for padrao in PADROES:
        pagina.route(padrao, lambda rota: rota.abort())
    pagina.goto(base + '#/home')
    painel = pagina.locator('[data-testid="no-signal"]')
    painel.wait_for(timeout=20000)
    assert 'SEM SINAL' in painel.inner_text().upper()
    assert 'NOVA TENTATIVA EM' in pagina.locator('[data-testid="no-signal-retry"]').inner_text().upper()

    for padrao in PADROES:
        pagina.unroute(padrao)
    pagina.get_by_role('button', name='Tentar agora').click()
    pagina.wait_for_selector('[data-testid="no-signal"]', state='detached', timeout=30000)
