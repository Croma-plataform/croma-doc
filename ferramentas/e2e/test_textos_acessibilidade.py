"""D21: nenhum "Jellyfin" na interface e navegação pelo teclado com foco sempre visível."""
import re

import pytest

ROTAS_COMUNS = ['home', 'movies', 'search', 'mypreferencesmenu', 'mypreferencesdisplay', 'mypreferencesplayback',
                'mypreferencessubtitles', 'mypreferenceshome', 'quickconnect', 'mostruario', 'calibration']


def sem_jellyfin(pagina, rota):
    pagina.wait_for_timeout(300)
    texto = pagina.locator('body').inner_text() + ' ' + pagina.title()
    atributos = pagina.evaluate("""() => [...document.querySelectorAll('[alt],[title],[aria-label],[placeholder]')]
        .map(e => [e.alt, e.title, e.getAttribute('aria-label'), e.placeholder].join(' ')).join(' ')""")
    assert not re.search('jellyfin', texto + ' ' + atributos, re.I), f'"Jellyfin" visível em {rota}'


@pytest.mark.parametrize('rota', ROTAS_COMUNS)
def test_tela_sem_jellyfin(pagina, ir, layout, rota):
    if rota == 'mypreferencesmenu' or rota.startswith('mypreferences'):
        rota = f'{rota}?userId=x' if False else rota
    # o catálogo de plugins consulta o repositório na internet: não esperar a rede ficar ociosa
    ir(rota, espera=4000 if rota == 'dashboard/plugins' else 1500, rede_ociosa=rota != 'dashboard/plugins')
    sem_jellyfin(pagina, rota)


@pytest.mark.usuario('admin')
@pytest.mark.parametrize('rota', ['dashboard', 'dashboard/libraries', 'dashboard/users', 'dashboard/settings',
                                  'dashboard/branding', 'dashboard/playback/transcoding', 'dashboard/plugins',
                                  'dashboard/logs', 'dashboard/tasks', 'dashboard/keys'])
def test_painel_sem_jellyfin(pagina, ir, layout, rota):
    if layout == 'tv':
        pytest.skip('painel só no desktop')
    # o catálogo de plugins consulta o repositório na internet: não esperar a rede ficar ociosa
    ir(rota, espera=4000 if rota == 'dashboard/plugins' else 1500, rede_ociosa=rota != 'dashboard/plugins')
    sem_jellyfin(pagina, rota)


def test_foco_visivel_em_todo_o_tab(pagina, ir, layout):
    """Percorre 20 paradas com Tab: o elemento focado precisa ficar diferente na tela do que sem foco."""
    ir('home')
    sem_foco = []
    for _ in range(20):
        pagina.keyboard.press('Tab')
        caixa = pagina.evaluate("""() => {
            const e = document.activeElement;
            if (!e || e === document.body) return null;
            e.scrollIntoView({block: 'center', inline: 'center'});
            const r = e.getBoundingClientRect();
            const nome = (e.getAttribute('aria-label') || e.textContent || e.className).trim().slice(0, 40);
            return {x: Math.max(0, r.x - 16), y: Math.max(0, r.y - 16), width: r.width + 32, height: r.height + 32, nome};
        }""")
        if not caixa or caixa['width'] < 36 or caixa['height'] < 36:
            continue
        nome = caixa.pop('nome')
        com_foco = pagina.screenshot(clip=caixa)
        pagina.evaluate("document.activeElement.blur()")
        pagina.wait_for_timeout(150)
        sem = pagina.screenshot(clip=caixa)
        if com_foco == sem:
            sem_foco.append(nome)
        pagina.keyboard.press('Shift+Tab')
        pagina.wait_for_timeout(100)
    assert not sem_foco, f'sem foco visível: {sem_foco}'
