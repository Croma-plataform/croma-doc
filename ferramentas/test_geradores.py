"""I03: os geradores da identidade, rodados do zero numa cópia, precisam dar o que está versionado.

Roda `gerar_icones.py`, `gerar_icones_app.py` e `gerar_png.py` (o `gerar_logotipo.py` precisa da fonte Archivo
variável em TTF e do `fontTools`, que não vêm no ambiente de teste). Nada é escrito no repositório da identidade:
tudo acontece numa cópia temporária. Uso: `python3 -m pytest ferramentas/test_geradores.py`."""
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HUB = Path(__file__).resolve().parent.parent
IDENTIDADE = HUB / 'croma-identidade'
FONTES = Path('v0.1-barras') / 'fontes'

pytestmark = pytest.mark.skipif(not IDENTIDADE.exists(), reason='o croma-identidade não está clonado')


@pytest.fixture(scope='module')
def copia(tmp_path_factory):
    destino = tmp_path_factory.mktemp('identidade') / 'croma-identidade'
    shutil.copytree(IDENTIDADE, destino, ignore=shutil.ignore_patterns('.git', 'midia'))
    return destino


@pytest.fixture
def copia_nova(tmp_path):
    """Uma cópia só deste teste: a do módulo já foi regerada pelos testes anteriores."""
    destino = tmp_path / 'croma-identidade'
    shutil.copytree(IDENTIDADE, destino, ignore=shutil.ignore_patterns('.git', 'midia'))
    return destino


def rodar(copia, script):
    resultado = subprocess.run([sys.executable, str(copia / FONTES / script)], cwd=copia / FONTES,
                               capture_output=True, text=True, timeout=600)
    assert resultado.returncode == 0, f'{script}: {resultado.stderr[-500:]}'


def arvore(raiz: Path, subpasta: str, sufixos) -> dict:
    """Caminho relativo → hash do conteúdo, dos arquivos da subpasta com os sufixos."""
    return {str(p.relative_to(raiz)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((raiz / subpasta).rglob('*')) if p.is_file() and p.suffix in sufixos}


def pixels(caminho: Path):
    from PIL import Image
    with Image.open(caminho) as imagem:
        return imagem.convert('RGBA').size, imagem.convert('RGBA').tobytes()


def test_icones_svg_saem_iguais(copia):
    antes = arvore(copia, 'v0.1-barras/logos/icones', {'.svg'})
    assert antes, 'não há ícones versionados'
    rodar(copia, 'gerar_icones.py')
    depois = arvore(copia, 'v0.1-barras/logos/icones', {'.svg'})
    assert depois == antes, sorted(set(depois.items()) ^ set(antes.items()))[:6]


TILES_DA_TV = {Path('tv/tile-960x540.png'), Path('tv/tile-1920x1080.png')}


def _icones_do_app(copia):
    pasta = copia / 'v0.1-barras' / 'logos' / 'app'
    return {p.relative_to(pasta): pixels(p) for p in pasta.rglob('*.png')}


def test_icones_do_app_saem_com_os_mesmos_pixels(copia):
    antes = _icones_do_app(copia)
    assert antes, 'não há ícones do app versionados'
    rodar(copia, 'gerar_icones_app.py')
    depois = _icones_do_app(copia)
    assert depois.keys() == antes.keys()
    diferentes = [str(k) for k in antes if depois[k] != antes[k] and k not in TILES_DA_TV]
    assert not diferentes, diferentes[:6]


@pytest.mark.xfail(strict=True, reason=(
    'ACHADO (13/11/2026): o tile da TV versionado (símbolo com a faixa de barras embaixo e a palavra CROMA) não é '
    'o que o gerar_icones_app.py desenha (moldura toda preenchida pelas 7 barras). Decidir qual vale e regerar ou '
    'corrigir o script; quando os dois baterem, este teste passa e o strict=True avisa para tirar a marca.'))
def test_tiles_da_tv_saem_iguais(copia_nova):
    antes = _icones_do_app(copia_nova)
    rodar(copia_nova, 'gerar_icones_app.py')
    depois = _icones_do_app(copia_nova)
    assert all(depois[k] == antes[k] for k in TILES_DA_TV)


def test_png_dos_svg_saem_com_os_mesmos_pixels(copia):
    pasta = copia / 'v0.1-barras'
    antes = {p.relative_to(copia): pixels(p) for p in pasta.rglob('png/*.png')}
    assert antes, 'não há PNG versionados'
    rodar(copia, 'gerar_png.py')
    depois = {p.relative_to(copia): pixels(p) for p in pasta.rglob('png/*.png')}
    assert depois.keys() == antes.keys(), sorted(set(depois) ^ set(antes))[:6]
    diferentes = [str(k) for k in antes if depois[k] != antes[k]]
    assert not diferentes, diferentes[:6]
