"""Abertura (módulo D16, prancha 30): moldura, barras e nome em 1,9 s."""
import pytest


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV entra no módulo T07')


def _abrir_parado(pagina, base):
    """Segura as chamadas do servidor para a abertura ficar na tela e a captura não depender da rede."""
    pagina.route('**/System/Info/Public*', lambda rota: None)
    pagina.goto(base, wait_until='commit')
    pagina.locator('[data-testid="splash"]').wait_for()


def test_abertura_tem_moldura_sete_barras_nome_e_status(pagina, base):
    _abrir_parado(pagina, base)
    assert pagina.locator('.cromaSplashBars i').count() == 7
    assert pagina.locator('.cromaSplashName').inner_text() == 'CROMA'
    assert pagina.locator('.cromaSplashStatus').inner_text().startswith('CONECTANDO')


def test_a_sequencia_dura_1_9_s(pagina, base):
    _abrir_parado(pagina, base)
    fim = pagina.evaluate('''() => [...document.querySelectorAll('.splashLogo *')].map(e => {
        const a = getComputedStyle(e); const d = parseFloat(a.animationDelay) + parseFloat(a.animationDuration);
        return isNaN(d) ? 0 : d; }).reduce((m, v) => Math.max(m, v), 0)''')
    assert abs(fim - 1.9) < 0.01, fim


def test_com_movimento_reduzido_o_estado_final_aparece_direto(pagina, base):
    pagina.emulate_media(reduced_motion='reduce')
    _abrir_parado(pagina, base)
    assert pagina.locator('.cromaSplashName').evaluate('e => getComputedStyle(e).animationName') == 'none'
    assert pagina.locator('.cromaSplashName').evaluate('e => getComputedStyle(e).opacity') == '1'
