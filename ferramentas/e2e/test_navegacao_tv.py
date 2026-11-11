"""Fumaça do modo TV: cada tela abre e o foco anda só com as setas (o controle remoto não tem mouse).

Roda só no layout `tv`. O acabamento na TV de verdade é a etapa 2 do plano; aqui se pega o que quebra antes dela.
"""
import pytest

ATIVO = "(() => { const a = document.activeElement; return a ? a.tagName + '.' + a.className + '|' + (a.textContent || '').trim().slice(0, 30) : ''; })()"


@pytest.fixture(autouse=True)
def so_tv(layout):
    if layout != 'tv':
        pytest.skip('só no modo TV')


def rotas(item, biblioteca):
    return {
        'inicio': 'home',
        'grade-filmes': f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=0',
        'detalhe-filme': f'details?id={item("Movie", "Barras Faixas (2003)")}',
        'detalhe-serie': f'details?id={item("Series", "Serie de Teste")}',
        'detalhe-episodio': f'details?id={item("Episode", "Serie de Teste - S01E02 - Episodio 2")}',
    }


@pytest.mark.parametrize('tela', ['inicio', 'grade-filmes', 'detalhe-filme', 'detalhe-serie', 'detalhe-episodio'])
def test_o_foco_anda_com_as_setas(tela, pagina, ir, item, biblioteca):
    ir(rotas(item, biblioteca)[tela])

    vistos = {pagina.evaluate(ATIVO)}
    for tecla in ('ArrowDown', 'ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp', 'ArrowRight', 'ArrowDown'):
        pagina.keyboard.press(tecla)
        pagina.wait_for_timeout(250)
        vistos.add(pagina.evaluate(ATIVO))

    assert len(vistos) >= 2, f'o foco não saiu do lugar em {tela}: {vistos}'
    assert pagina.evaluate("document.activeElement !== document.body"), f'o foco se perdeu em {tela}'
