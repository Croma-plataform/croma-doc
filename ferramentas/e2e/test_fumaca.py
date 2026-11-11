"""Fumaça: entrar, ver o Início, abrir um filme e tocar alguns segundos, nos dois layouts."""


def test_inicio_abre(pagina, ir, layout):
    ir('home')
    assert pagina.evaluate(f"document.documentElement.classList.contains('layout-{layout}')"), 'o layout pedido não valeu'
    assert '#/home' in pagina.url
    assert pagina.locator('.homePage:not(.hide), #indexPage:not(.hide)').count() > 0


def test_filme_abre_e_toca(pagina, ir, item):
    ir(f'details?id={item("Movie", "Barras Direto (2001)")}')
    pagina.locator('#itemDetailPage:not(.hide) .btnPlay').first.click()
    pagina.wait_for_selector('video', timeout=20000)
    pagina.wait_for_function('() => { const v = document.querySelector("video"); return v && v.currentTime > 2; }',
                             timeout=30000)
    assert pagina.evaluate('document.querySelector("video").paused') is False
