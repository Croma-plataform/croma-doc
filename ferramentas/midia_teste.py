#!/usr/bin/env python3
"""Gera a mídia de teste do Croma: um pouco de cada subtipo, toda sintética (barras, tons e páginas desenhadas).

Nada aqui vem do acervo do usuário nem tem direitos de terceiros. O script cria a mídia numa pasta que o chamador
escolhe (por padrão fora dos repositórios) e escreve nela um `catalogo.json` com os nomes e o subtipo de cada pasta,
que o `servidor_teste.py` usa para criar as bibliotecas.

Uso: python3 midia_teste.py [--saida PASTA] [--refazer]
Precisa de: ffmpeg (com libx264, libx265, libmp3lame e aac) e Pillow.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

PADRAO = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache')) / 'croma-teste' / 'midia'
FFMPEG = os.environ.get('FFMPEG', 'ffmpeg')

# Cores das barras de 75% do manual (Início, Audiovisual, Áudios, Fotos, Leitura)
BARRAS = ['#C0C0C0', '#C0C000', '#00C0C0', '#00C000', '#C000C0', '#C00000', '#0000C0']


def rodar(*args: str) -> None:
    r = subprocess.run([FFMPEG, '-hide_banner', '-loglevel', 'error', '-y', *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f'ffmpeg falhou: {" ".join(args[:6])}...\n{r.stderr}')


def srt(caminho: Path, linhas: list[str]) -> Path:
    blocos = []
    for i, texto in enumerate(linhas):
        blocos.append(f'{i + 1}\n00:00:{i * 2:02d},000 --> 00:00:{i * 2 + 1:02d},500\n{texto}\n')
    caminho.write_text('\n'.join(blocos), encoding='utf-8')
    return caminho


def capitulos(caminho: Path, titulos: list[str], duracao_s: int) -> Path:
    """Arquivo ffmetadata com os capítulos, divididos por igual."""
    passo = duracao_s * 1000 // len(titulos)
    partes = [';FFMETADATA1']
    for i, titulo in enumerate(titulos):
        partes += ['[CHAPTER]', 'TIMEBASE=1/1000', f'START={i * passo}', f'END={(i + 1) * passo - 1}', f'title={titulo}']
    caminho.write_text('\n'.join(partes) + '\n', encoding='utf-8')
    return caminho


def video(destino: Path, *, codec='libx264', segundos=12, audios=(('por', 440),), legendas=(), cap=(), titulo='',
          extra=()) -> None:
    """Vídeo de barras com um tom por faixa de áudio; legendas e capítulos opcionais (contêiner MKV ou MP4)."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    entradas: list[str] = ['-f', 'lavfi', '-i', f'testsrc2=size=640x360:rate=15:duration={segundos}']
    for _, freq in audios:
        entradas += ['-f', 'lavfi', '-i', f'sine=frequency={freq}:duration={segundos}']
    base = 1 + len(audios)
    for arquivo in legendas:
        entradas += ['-i', str(arquivo[1])]
    if cap:
        entradas += ['-i', str(cap)]

    mapa = ['-map', '0:v']
    for i in range(len(audios)):
        mapa += ['-map', f'{i + 1}:a']
    for i in range(len(legendas)):
        mapa += ['-map', f'{base + i}:s']

    saida = ['-c:v', codec, '-pix_fmt', 'yuv420p', '-preset', 'ultrafast', '-g', '15', '-c:a', 'aac', '-b:a', '96k']
    if codec == 'libx265':
        saida += ['-tag:v', 'hvc1', '-x265-params', 'log-level=error']
    if legendas:
        saida += ['-c:s', 'mov_text' if destino.suffix == '.mp4' else 'srt']
    meta = []
    for i, (idioma, _) in enumerate(audios):
        meta += [f'-metadata:s:a:{i}', f'language={idioma}']
    for i, (idioma, _) in enumerate(legendas):
        meta += [f'-metadata:s:s:{i}', f'language={idioma}']
    if titulo:
        meta += ['-metadata', f'title={titulo}']
    if cap:
        meta += ['-map_metadata', str(base + len(legendas))]
    rodar(*entradas, *mapa, *saida, *meta, *extra, str(destino))


def tom(destino: Path, *, freq=440, segundos=8, codec='libmp3lame', titulo='', artista='', album='', faixa=1,
        capa: Path | None = None, cap=()) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    args = ['-f', 'lavfi', '-i', f'sine=frequency={freq}:duration={segundos}']
    if capa:
        args += ['-i', str(capa)]
    if cap:
        args += ['-i', str(cap)]
    args += ['-map', '0:a']
    if capa:
        args += ['-map', '1:v', '-c:v', 'mjpeg', '-disposition:v', 'attached_pic']
    args += ['-c:a', codec]
    if codec == 'aac':
        args += ['-b:a', '64k']
    for k, v in (('title', titulo), ('artist', artista), ('album', album), ('track', str(faixa))):
        if v:
            args += ['-metadata', f'{k}={v}']
    if cap:
        args += ['-map_metadata', str(2 if capa else 1)]
    rodar(*args, str(destino))


def imagem(destino: Path, *, tamanho=(600, 900), titulo='', cor=BARRAS[1]) -> Path:
    """Imagem com as 7 barras na base e o título; serve de pôster, capa ou foto."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new('RGB', tamanho, '#17181A')
    d = ImageDraw.Draw(img)
    larg, alt = tamanho
    d.rectangle([24, 24, 24 + larg // 14, 24 + larg // 14], fill=cor)
    faixa = alt // 16
    for i, c in enumerate(BARRAS):
        d.rectangle([i * larg // 7, alt - faixa, (i + 1) * larg // 7, alt], fill=c)
    if titulo:
        d.text((24, alt - faixa - 48), titulo, fill='#F2F2F0')
    img.save(destino, quality=88)
    return destino


def pagina(texto: str, cor: str, tamanho=(600, 900)) -> Image.Image:
    img = Image.new('RGB', tamanho, '#F2F2F0')
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, tamanho[0], 60], fill=cor)
    d.text((24, 90), texto, fill='#0B0B0C')
    return img


def epub(destino: Path, titulo: str, autor: str, capitulos_: int = 3) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    itens = ''.join(f'<item id="c{i}" href="c{i}.xhtml" media-type="application/xhtml+xml"/>' for i in range(capitulos_))
    ordem = ''.join(f'<itemref idref="c{i}"/>' for i in range(capitulos_))
    with zipfile.ZipFile(destino, 'w') as z:
        z.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
        z.writestr('META-INF/container.xml',
                   '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                   '<rootfiles><rootfile full-path="content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
        z.writestr('content.opf',
                   '<?xml version="1.0"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="id">'
                   f'<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="id">croma-teste-{titulo}</dc:identifier>'
                   f'<dc:title>{titulo}</dc:title><dc:creator>{autor}</dc:creator><dc:language>pt-BR</dc:language></metadata>'
                   f'<manifest>{itens}</manifest><spine>{ordem}</spine></package>')
        for i in range(capitulos_):
            texto = ' '.join(f'Parágrafo {n} do capítulo {i + 1}.' for n in range(1, 40))
            z.writestr(f'c{i}.xhtml',
                       '<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml"><head>'
                       f'<title>Capítulo {i + 1}</title></head><body><h1>Capítulo {i + 1}</h1><p>{texto}</p></body></html>')


def pdf(destino: Path, paginas: int = 3) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    imgs = [pagina(f'Página {i + 1} de {paginas}', BARRAS[6]) for i in range(paginas)]
    imgs[0].save(destino, save_all=True, append_images=imgs[1:])


def cbz(destino: Path, serie: str, volume: int, manga: bool, paginas: int = 6) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    info = (f'<?xml version="1.0"?><ComicInfo><Series>{serie}</Series><Number>{volume}</Number>'
            f'<Title>{serie} {volume}</Title><PageCount>{paginas}</PageCount>'
            f'<Manga>{"YesAndRightToLeft" if manga else "No"}</Manga></ComicInfo>')
    with zipfile.ZipFile(destino, 'w') as z:
        z.writestr('ComicInfo.xml', info)
        for i in range(paginas):
            tmp = destino.parent / f'.p{i}.png'
            pagina(f'{serie} {volume} · página {i + 1}', BARRAS[6]).save(tmp)
            z.write(tmp, f'{i + 1:03d}.png')
            tmp.unlink()


def gerar(raiz: Path) -> dict:
    cat: dict = {}
    tmp = raiz / '.tmp'
    tmp.mkdir(parents=True, exist_ok=True)
    legendas = (('por', srt(tmp / 'por.srt', ['Olá, Croma.', 'Segunda fala.', 'Terceira fala.'])),
                ('eng', srt(tmp / 'eng.srt', ['Hello, Croma.', 'Second line.', 'Third line.'])))

    # Filmes
    f = raiz / 'filmes'
    video(f / 'Barras Direto (2001)' / 'Barras Direto (2001).mp4', titulo='Barras Direto')
    video(f / 'Barras HEVC (2002)' / 'Barras HEVC (2002).mkv', codec='libx265', titulo='Barras HEVC')
    video(f / 'Barras Faixas (2003)' / 'Barras Faixas (2003).mkv', audios=(('por', 440), ('eng', 660)),
          legendas=legendas, titulo='Barras Faixas')
    video(f / 'Barras Capitulos (2004)' / 'Barras Capitulos (2004).mkv', segundos=40,
          cap=capitulos(tmp / 'cap.ffmeta', ['Abertura', 'Meio', 'Virada', 'Final'], 40), titulo='Barras Capítulos')
    video(f / 'Barras Com Arte (2005)' / 'Barras Com Arte (2005).mp4', titulo='Barras Com Arte')
    imagem(f / 'Barras Com Arte (2005)' / 'poster.jpg', titulo='Barras Com Arte')
    cat['filmes'] = {'tipo': 'movies', 'subtipo': 'Movies', 'pasta': 'filmes'}

    # Séries: 2 temporadas
    s = raiz / 'series' / 'Serie de Teste (2010)'
    for temporada, eps in ((1, 3), (2, 2)):
        for e in range(1, eps + 1):
            nome = f'Serie de Teste - S{temporada:02d}E{e:02d} - Episodio {e}'
            video(s / f'Season {temporada:02d}' / f'{nome}.mp4', segundos=10, audios=(('por', 300 + 40 * e),),
                  legendas=legendas[:1])
    cat['series'] = {'tipo': 'tvshows', 'subtipo': 'Series', 'pasta': 'series'}

    # Documentários: um filme e uma série
    d = raiz / 'documentarios-filmes'
    video(d / 'Documental Um (2015)' / 'Documental Um (2015).mp4', titulo='Documental Um')
    cat['documentarios-filmes'] = {'tipo': 'movies', 'subtipo': 'Documentaries', 'pasta': 'documentarios-filmes'}
    ds = raiz / 'documentarios-series' / 'Serie Documental (2016)'
    for e in (1, 2):
        video(ds / 'Season 01' / f'Serie Documental - S01E{e:02d} - Parte {e}.mp4', segundos=10)
    cat['documentarios-series'] = {'tipo': 'tvshows', 'subtipo': 'Documentaries', 'pasta': 'documentarios-series'}

    # Músicas: 2 álbuns de um artista, com e sem capa
    m = raiz / 'musicas' / 'Artista de Teste'
    capa = imagem(tmp / 'capa.jpg', tamanho=(600, 600), titulo='Album Um', cor=BARRAS[3])
    for i in range(1, 4):
        tom(m / 'Album Um (2020)' / f'{i:02d} - Faixa {i}.mp3', freq=220 * i, titulo=f'Faixa {i}',
            artista='Artista de Teste', album='Album Um', faixa=i, capa=capa)
    for i in range(1, 3):
        tom(m / 'Album Dois (2021)' / f'{i:02d} - Outra {i}.mp3', freq=330 * i, titulo=f'Outra {i}',
            artista='Artista de Teste', album='Album Dois', faixa=i)
    cat['musicas'] = {'tipo': 'music', 'subtipo': 'Music', 'pasta': 'musicas'}

    # Podcast: uma pasta com 3 episódios (biblioteca de livros)
    p = raiz / 'podcasts' / 'Podcast de Teste'
    for i in range(1, 4):
        tom(p / f'Episodio {i}.mp3', freq=250 + 50 * i, segundos=10, titulo=f'Episodio {i}',
            artista='Podcast de Teste', album='Podcast de Teste', faixa=i)
    cat['podcasts'] = {'tipo': 'books', 'subtipo': 'Podcasts', 'pasta': 'podcasts'}

    # Audiolivro com capítulos
    a = raiz / 'audiolivros' / 'Autor de Teste' / 'Audiolivro de Teste'
    tom(a / 'Audiolivro de Teste.m4b', codec='aac', segundos=60, titulo='Audiolivro de Teste', artista='Autor de Teste',
        album='Audiolivro de Teste', cap=capitulos(tmp / 'audio.ffmeta', ['Capitulo 1', 'Capitulo 2', 'Capitulo 3'], 60))
    cat['audiolivros'] = {'tipo': 'books', 'subtipo': 'Audiobooks', 'pasta': 'audiolivros'}

    # Livros: EPUB e PDF
    epub(raiz / 'livros' / 'Livro de Teste.epub', 'Livro de Teste', 'Autor de Teste')
    pdf(raiz / 'livros' / 'Documento de Teste.pdf')
    cat['livros'] = {'tipo': 'books', 'subtipo': 'Books', 'pasta': 'livros'}

    # HQs e mangás
    for vol in (1, 2):
        cbz(raiz / 'hqs' / 'HQ de Teste' / f'HQ de Teste {vol:02d}.cbz', 'HQ de Teste', vol, manga=False)
        cbz(raiz / 'mangas' / 'Manga de Teste' / f'Manga de Teste {vol:02d}.cbz', 'Manga de Teste', vol, manga=True)
    cat['hqs'] = {'tipo': 'books', 'subtipo': 'Comics', 'pasta': 'hqs'}
    cat['mangas'] = {'tipo': 'books', 'subtipo': 'Manga', 'pasta': 'mangas'}

    # Fotos: duas pastas
    for album, n in (('Album A', 4), ('Album B', 3)):
        for i in range(1, n + 1):
            imagem(raiz / 'fotos' / album / f'foto-{i}.jpg', tamanho=(1200 if i % 2 else 900, 800), titulo=f'{album} {i}',
                   cor=BARRAS[4])
    cat['fotos'] = {'tipo': 'homevideos', 'subtipo': 'Photos', 'pasta': 'fotos'}

    shutil.rmtree(tmp, ignore_errors=True)
    return cat


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--saida', type=Path, default=PADRAO, help=f'pasta de destino (padrão: {PADRAO})')
    ap.add_argument('--refazer', action='store_true', help='apaga a pasta e gera tudo de novo')
    args = ap.parse_args()

    destino: Path = args.saida
    if (destino / 'catalogo.json').exists() and not args.refazer:
        print(f'Mídia de teste já existe em {destino} (use --refazer para gerar de novo).')
        return
    if args.refazer and destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True, exist_ok=True)

    catalogo = gerar(destino)
    (destino / 'catalogo.json').write_text(json.dumps(catalogo, indent=2, ensure_ascii=False), encoding='utf-8')
    total = sum(1 for p in destino.rglob('*') if p.is_file())
    print(f'Mídia de teste gerada em {destino}: {len(catalogo)} bibliotecas, {total} arquivos.')


if __name__ == '__main__':
    main()
