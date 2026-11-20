#!/usr/bin/env python3
"""Backup e importação das tags do Croma v1 para o Jellyfin (módulo D15, decisão de 13/11/2026: tags só no Jellyfin).

  python3 tags_v1.py exportar --saida backup-tags.json
      Guarda as tags de todos os itens do Jellyfin (caminho e tags) num JSON, para ter cópia.
  python3 tags_v1.py importar --v1 /pasta/dos/albuns/do/v1
      Mostra o que seria importado dos `metadados/colecao.json` e `metadados/fotos.json` do v1 (nada é gravado).
  python3 tags_v1.py importar --v1 /pasta/dos/albuns/do/v1 --aplicar
      Grava: junta as tags do v1 às que o item já tem e trava o campo Tags (`LockedFields`), para uma atualização de
      metadados não apagar o que foi importado.

O servidor, o usuário e a senha vêm de --url, --usuario e --senha (ou CROMA_URL, CROMA_USUARIO e CROMA_SENHA). O
script só lê a pasta do v1: nunca grava nos arquivos de mídia nem nos JSON do v1. Usa só a biblioteca padrão.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

PASTA_METADADOS = 'metadados'
CABECALHO = 'MediaBrowser Client="tags_v1", Device="script", DeviceId="croma-tags-v1", Version="1"'


def normalizar_tags(tags) -> list[str]:
    """Tira os espaços, descarta o que ficar vazio e as repetidas (sem diferenciar maiúsculas), mantendo a ordem."""
    vistas: set[str] = set()
    saida: list[str] = []
    for tag in tags or []:
        texto = str(tag).strip()
        if texto and texto.casefold() not in vistas:
            vistas.add(texto.casefold())
            saida.append(texto)
    return saida


def _ler_json(arquivo: Path):
    try:
        return json.loads(arquivo.read_text(encoding='utf-8-sig'))
    except (OSError, ValueError):
        return None


def ler_tags_do_v1(raiz: Path) -> dict[str, list[str]]:
    """Lê os `colecao.json` (tags do álbum) e `fotos.json` (tags de cada foto) e devolve {caminho absoluto: tags}."""
    resultado: dict[str, list[str]] = {}
    for pasta in sorted(raiz.rglob(PASTA_METADADOS)):
        if not pasta.is_dir():
            continue
        album = pasta.parent
        colecao = _ler_json(pasta / 'colecao.json')
        if isinstance(colecao, dict) and normalizar_tags(colecao.get('tags')):
            resultado[str(album)] = normalizar_tags(colecao.get('tags'))
        fotos = _ler_json(pasta / 'fotos.json')
        if isinstance(fotos, dict) and isinstance(fotos.get('fotos'), dict):
            for chave, entrada in fotos['fotos'].items():
                tags = normalizar_tags(entrada.get('tags') if isinstance(entrada, dict) else None)
                if tags:
                    resultado[str(album / chave.replace('\\', '/'))] = tags
    return resultado


def juntar_tags(atuais, novas) -> list[str]:
    """As tags que o item já tem mais as importadas, sem repetir."""
    return normalizar_tags(list(atuais or []) + list(novas or []))


class Servidor:
    def __init__(self, url: str, usuario: str, senha: str):
        self.url = url.rstrip('/')
        resposta = self._pedir('POST', '/Users/AuthenticateByName', {'Username': usuario, 'Pw': senha})
        self.token = resposta['AccessToken']

    def _pedir(self, metodo: str, caminho: str, corpo=None):
        dados = None if corpo is None else json.dumps(corpo).encode()
        req = urllib.request.Request(self.url + caminho, data=dados, method=metodo)
        req.add_header('Authorization', CABECALHO + (f', Token="{self.token}"' if getattr(self, 'token', None) else ''))
        if dados is not None:
            req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=60) as r:
            texto = r.read().decode() or 'null'
            return json.loads(texto)

    def itens(self) -> list[dict]:
        consulta = urllib.parse.urlencode({'Recursive': 'true', 'Fields': 'Path,Tags'})
        return self._pedir('GET', f'/Items?{consulta}')['Items']

    def gravar_tags(self, item_id: str, tags: list[str]) -> None:
        completo = self._pedir('GET', f'/Items/{item_id}')
        completo['Tags'] = tags
        completo['LockedFields'] = sorted(set(completo.get('LockedFields') or []) | {'Tags'})
        # o servidor não lê de volta o Trickplay (o DTO dele não tem setters): mandá-lo dá HTTP 500
        completo.pop('Trickplay', None)
        self._pedir('POST', f'/Items/{item_id}', completo)


def _normalizar_caminho(caminho: str) -> str:
    return caminho.replace('\\', '/').rstrip('/')


def planejar(itens: list[dict], tags_v1: dict[str, list[str]]) -> tuple[list[tuple[dict, list[str]]], list[str]]:
    """Casa cada caminho do v1 com um item do Jellyfin pelo caminho; devolve (o que gravar, o que não achou)."""
    por_caminho = {_normalizar_caminho(i.get('Path') or ''): i for i in itens if i.get('Path')}
    gravar: list[tuple[dict, list[str]]] = []
    sem_item: list[str] = []
    for caminho, tags in sorted(tags_v1.items()):
        item = por_caminho.get(_normalizar_caminho(caminho))
        if item is None:
            sem_item.append(caminho)
            continue
        final = juntar_tags(item.get('Tags'), tags)
        if final != list(item.get('Tags') or []):
            gravar.append((item, final))
    return gravar, sem_item


def _servidor(args) -> Servidor:
    return Servidor(args.url, args.usuario, args.senha)


def exportar(args) -> int:
    itens = [{'Path': i.get('Path'), 'Id': i['Id'], 'Tags': i['Tags']} for i in _servidor(args).itens() if i.get('Tags')]
    Path(args.saida).write_text(json.dumps(itens, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{len(itens)} itens com tags guardados em {args.saida}')
    return 0


def importar(args) -> int:
    tags_v1 = ler_tags_do_v1(Path(args.v1))
    print(f'{len(tags_v1)} álbuns e fotos com tags no v1.')
    servidor = _servidor(args)
    gravar, sem_item = planejar(servidor.itens(), tags_v1)
    for item, tags in gravar:
        print(f'  {item.get("Path")}: {", ".join(tags)}')
    for caminho in sem_item:
        print(f'  sem item no Jellyfin: {caminho}')
    print(f'{len(gravar)} itens a atualizar, {len(sem_item)} do v1 sem item correspondente.')
    if not args.aplicar:
        print('Nada foi gravado (use --aplicar).')
        return 0
    for item, tags in gravar:
        servidor.gravar_tags(item['Id'], tags)
    print('Tags gravadas, com o campo Tags travado.')
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--url', default=os.environ.get('CROMA_URL', 'http://localhost:8096'))
    ap.add_argument('--usuario', default=os.environ.get('CROMA_USUARIO'))
    ap.add_argument('--senha', default=os.environ.get('CROMA_SENHA'))
    sub = ap.add_subparsers(dest='comando', required=True)
    exp = sub.add_parser('exportar')
    exp.add_argument('--saida', default='backup-tags.json')
    exp.set_defaults(funcao=exportar)
    imp = sub.add_parser('importar')
    imp.add_argument('--v1', required=True, help='pasta com os álbuns do v1 (cada um com metadados/colecao.json e fotos.json)')
    imp.add_argument('--aplicar', action='store_true', help='grava; sem isso só mostra o que faria')
    imp.set_defaults(funcao=importar)
    args = ap.parse_args()
    if not args.usuario or not args.senha:
        ap.error('informe --usuario e --senha (ou CROMA_USUARIO e CROMA_SENHA)')
    return args.funcao(args)


if __name__ == '__main__':
    sys.exit(main())
