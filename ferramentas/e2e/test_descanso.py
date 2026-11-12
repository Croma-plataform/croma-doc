"""Descanso de tela (módulo D18): entra depois de 5 min parado, com o símbolo se movendo."""
import pytest


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV entra no módulo T07')


def test_entra_depois_de_5_minutos_parado_e_o_simbolo_anda(pagina, ir):
    ir('home')
    pagina.clock.install()
    pagina.clock.run_for(4 * 60 * 1000)
    assert pagina.locator('.logoScreenSaver').count() == 0          # antes dos 5 min, nada
    pagina.clock.run_for(70 * 1000)
    pagina.locator('.logoScreenSaver').wait_for(timeout=5000)
    simbolo = pagina.locator('.logoScreenSaverImage')
    antes = simbolo.evaluate('e => e.style.transform')
    pagina.clock.run_for(1500)
    depois = simbolo.evaluate('e => e.style.transform')
    assert antes != depois


def test_qualquer_tecla_tira_o_descanso(pagina, ir):
    ir('home')
    pagina.clock.install()
    pagina.clock.run_for(5 * 60 * 1000 + 10 * 1000)
    pagina.locator('.logoScreenSaver').wait_for(timeout=5000)
    pagina.keyboard.press('Space')
    pagina.wait_for_selector('.logoScreenSaver', state='detached', timeout=5000)


def test_o_descanso_cobre_a_tela_inteira(pagina, ir):
    ir('home')
    pagina.clock.install()
    pagina.clock.run_for(5 * 60 * 1000 + 10 * 1000)
    pagina.locator('.logoScreenSaver').wait_for(timeout=5000)
    # o elemento no meio da barra lateral é o descanso, não a barra
    topo = pagina.evaluate('document.elementFromPoint(100, 200).closest(".logoScreenSaver") !== null')
    assert topo
