"""Comparação de capturas de tela com as referências (regressão visual)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops

PASTA = Path(__file__).resolve().parent
REFERENCIAS = PASTA / 'referencias'
FALHAS = PASTA / 'falhas'

# Uma cor muda "de verdade" quando passa disso em algum canal; abaixo é ruído de renderização
LIMIAR_CANAL = 24
# Fração de pixels diferentes tolerada
LIMITE = 0.003

CSS_ESTAVEL = '''
*, *::before, *::after { animation: none !important; transition: none !important; caret-color: transparent !important; }
.clock, .headerClock, .cromaOsdClock, .endsAt { visibility: hidden !important; }
'''


def conferir(pagina, layout: str, nome: str, *, atualizar=False, esconder: list[str] | None = None) -> None:
    """Captura a página e compara com `referencias/<layout>/<nome>.png`.

    Sem referência (ou com --atualizar-referencias) grava a captura como referência. Se a diferença passar do limite,
    salva a captura e o mapa de diferenças em `falhas/` e reprova."""
    pagina.add_style_tag(content=CSS_ESTAVEL + ''.join(f'{s} {{ visibility: hidden !important; }}' for s in esconder or []))
    pagina.wait_for_timeout(300)
    destino = REFERENCIAS / layout / f'{nome}.png'
    atual_png = FALHAS / layout / f'{nome}-atual.png'
    atual_png.parent.mkdir(parents=True, exist_ok=True)
    pagina.screenshot(path=str(atual_png))

    if atualizar or not destino.exists():
        destino.parent.mkdir(parents=True, exist_ok=True)
        atual_png.replace(destino)
        return

    ref = Image.open(destino).convert('RGB')
    atual = Image.open(atual_png).convert('RGB')
    assert ref.size == atual.size, f'{layout}/{nome}: tamanho {atual.size} ≠ referência {ref.size}'
    diff = ImageChops.difference(ref, atual)
    mascara = diff.point(lambda v: 255 if v > LIMIAR_CANAL else 0).convert('L').point(lambda v: 255 if v else 0)
    mudou = sum(1 for v in mascara.get_flattened_data() if v) / (ref.size[0] * ref.size[1])
    if mudou > LIMITE:
        diff_png = FALHAS / layout / f'{nome}-diff.png'
        mascara.save(diff_png)
        raise AssertionError(f'{layout}/{nome}: {mudou:.2%} dos pixels mudaram (limite {LIMITE:.2%}); veja {atual_png} e {diff_png}')
    atual_png.unlink()
