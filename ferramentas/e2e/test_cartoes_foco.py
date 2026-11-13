"""Cartões: a moldura de foco aparece inteira nos quatro lados e a etiqueta de quantidade é Fósforo (módulo D02)."""
import io

import pytest
from PIL import Image


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV tem foco de 8 px e é testada no módulo T04')


def _lados_claros(imagem, caixa, espessura=3):
    """Fração de pixels claros (Fósforo) em cada faixa, por dentro das bordas da caixa. A moldura tem 4 px e a caixa pode
    cair em meio pixel: a faixa medida começa 1 px para dentro e tem 2 px."""
    im = imagem.convert('L')
    x0, y0, x1, y1 = (round(caixa['x']), round(caixa['y']), round(caixa['x'] + caixa['width']), round(caixa['y'] + caixa['height']))
    faixas = {
        'esquerda': (x0 + 1, y0 + 8, x0 + espessura, y1 - 8),
        'direita': (x1 - espessura, y0 + 8, x1 - 1, y1 - 8),
        'topo': (x0 + 8, y0 + 1, x1 - 8, y0 + espessura),
        'base': (x0 + 8, y1 - espessura, x1 - 8, y1 - 1),
    }
    resultado = {}
    for lado, area in faixas.items():
        pixels = list(im.crop(area).getdata())
        resultado[lado] = sum(1 for p in pixels if p > 200) / len(pixels)
    return resultado


def test_moldura_de_foco_inteira_nos_quatro_lados(pagina, ir, biblioteca):
    ir(f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=1')
    cartao = pagina.locator('.card').first
    cartao.wait_for()
    cartao.hover()
    pagina.wait_for_timeout(400)
    caixa = cartao.locator('.cardScalable').bounding_box()
    imagem = Image.open(io.BytesIO(pagina.screenshot()))
    for lado, fracao in _lados_claros(imagem, caixa).items():
        assert fracao > 0.9, f'a moldura está cortada do lado {lado} ({fracao:.0%} clara)'


def test_moldura_de_foco_inteira_numa_fileira_rolavel(pagina, ir):
    ir('home')
    cartao = pagina.locator('.itemsContainer.scrollSlider .card').first
    cartao.wait_for()
    cartao.hover()
    pagina.wait_for_timeout(400)
    caixa = cartao.locator('.cardScalable').bounding_box()
    imagem = Image.open(io.BytesIO(pagina.screenshot()))
    for lado, fracao in _lados_claros(imagem, caixa).items():
        assert fracao > 0.9, f'a moldura está cortada do lado {lado} ({fracao:.0%} clara)'


def test_etiqueta_de_quantidade_e_fosforo(pagina, ir, biblioteca):
    ir(f'tv?topParentId={biblioteca("Séries")["id"]}&collectionType=tvshows&tab=0')
    etiqueta = pagina.locator('.card .unplayedItemCount').first
    etiqueta.wait_for()
    fundo = etiqueta.evaluate('e => getComputedStyle(e).backgroundColor')
    assert fundo == 'rgb(242, 242, 240)', f'o fundo da etiqueta devia ser Fósforo, é {fundo}'
