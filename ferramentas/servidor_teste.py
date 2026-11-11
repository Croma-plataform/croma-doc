#!/usr/bin/env python3
"""Servidor de teste do Croma: outra pasta de dados, outra porta e só a mídia sintética de `midia_teste.py`.

Nunca toca o acervo do usuário nem o servidor de trabalho (porta 8096). Os testes de ponta a ponta usam este servidor.

  python3 servidor_teste.py subir      cria (se preciso) e sobe o servidor, e espera as bibliotecas ficarem prontas
  python3 servidor_teste.py parar      encerra o servidor
  python3 servidor_teste.py estado     mostra se está no ar e onde ficam os arquivos
  python3 servidor_teste.py limpar     encerra e apaga os dados do servidor de teste (a mídia fica)

Variáveis: CROMA_TESTE_DIR (padrão ~/.cache/croma-teste), CROMA_TESTE_PORTA (padrão 8097), FFMPEG (padrão ffmpeg do
sistema) e DOTNET_ROOT (padrão ~/.dotnet). O servidor compilado vem de ../croma-servidor/compilado e a interface de
../croma-web/dist (veja croma/README.md do croma-servidor).

As contas são só deste servidor descartável: `admin`, `leitor` e `tocador`, todas com a senha `teste`.
"""
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HUB = Path(__file__).resolve().parent.parent
BASE = Path(os.environ.get('CROMA_TESTE_DIR', Path.home() / '.cache' / 'croma-teste'))
PORTA = int(os.environ.get('CROMA_TESTE_PORTA', '8097'))
URL = f'http://localhost:{PORTA}'
SERVIDOR = BASE / 'servidor'
MIDIA = BASE / 'midia'
ESTADO = BASE / 'estado.json'
PIDFILE = BASE / 'servidor.pid'
SENHA = 'teste'
# `leitor` só lê (telas e capturas de referência); `tocador` é o que assiste, ouve e muda o estado dos itens
USUARIOS = ('admin', 'leitor', 'tocador')

CABECALHO = 'MediaBrowser Client="CromaTeste", Device="teste", DeviceId="croma-teste", Version="1.0"'


class Erro(SystemExit):
    pass


def api(metodo: str, caminho: str, corpo=None, token: str | None = None, espera=60):
    dados = None if corpo is None else json.dumps(corpo).encode()
    req = urllib.request.Request(URL + caminho, data=dados, method=metodo)
    req.add_header('Authorization', CABECALHO + (f', Token="{token}"' if token else ''))
    if dados is not None:
        req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, timeout=espera) as r:
            texto = r.read().decode() or 'null'
            return json.loads(texto)
    except urllib.error.HTTPError as e:
        raise Erro(f'{metodo} {caminho} → {e.code}: {e.read().decode()[:300]}') from e


def no_ar() -> bool:
    try:
        with urllib.request.urlopen(URL + '/System/Info/Public', timeout=2) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError):
        return False


def pid_vivo() -> int | None:
    try:
        pid = int(PIDFILE.read_text())
        os.kill(pid, 0)
        return pid
    except (OSError, ValueError):
        return None


def escrever_rede() -> None:
    config = SERVIDOR / 'config'
    config.mkdir(parents=True, exist_ok=True)
    (config / 'network.xml').write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<NetworkConfiguration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <InternalHttpPort>{PORTA}</InternalHttpPort>
  <PublicHttpPort>{PORTA}</PublicHttpPort>
  <AutoDiscovery>false</AutoDiscovery>
  <EnableUPnP>false</EnableUPnP>
  <EnableIPv6>false</EnableIPv6>
</NetworkConfiguration>
''', encoding='utf-8')


def iniciar() -> None:
    compilado = HUB / 'croma-servidor' / 'compilado' / 'jellyfin'
    web = HUB / 'croma-web' / 'dist'
    if not compilado.exists():
        raise Erro(f'Servidor não compilado em {compilado} (veja croma-servidor/croma/README.md).')
    if not (web / 'index.html').exists():
        raise Erro(f'Build do croma-web não encontrado em {web} (npm run build:production).')
    if PORTA == 8096:
        raise Erro('A porta 8096 é do servidor de trabalho; o de teste usa outra.')

    escrever_rede()
    env = dict(os.environ)
    env.setdefault('DOTNET_ROOT', str(Path.home() / '.dotnet'))
    (SERVIDOR / 'log').mkdir(parents=True, exist_ok=True)
    log = SERVIDOR / 'saida.log'
    inicio_log = log.stat().st_size if log.exists() else 0
    saida = open(log, 'ab')
    proc = subprocess.Popen(
        [str(compilado), '--datadir', str(SERVIDOR / 'data'), '--configdir', str(SERVIDOR / 'config'),
         '--cachedir', str(SERVIDOR / 'cache'), '--logdir', str(SERVIDOR / 'log'),
         '--ffmpeg', os.environ.get('FFMPEG', shutil.which('ffmpeg') or 'ffmpeg'), '--webdir', str(web)],
        env=env, stdout=saida, stderr=subprocess.STDOUT, start_new_session=True)
    PIDFILE.write_text(str(proc.pid))

    # Durante a inicialização um servidor provisório já responde na porta (com 503): só vale depois do
    # "Startup complete" no log (veja croma-servidor/croma/README.md).
    for _ in range(180):
        with open(log, 'rb') as f:
            f.seek(inicio_log)
            if b'Startup complete' in f.read():
                return
        if proc.poll() is not None:
            raise Erro(f'O servidor de teste encerrou ao iniciar (veja {SERVIDOR / "saida.log"}).')
        time.sleep(1)
    raise Erro('O servidor de teste não terminou de iniciar em 3 minutos.')


def login(usuario: str) -> dict:
    return api('POST', '/Users/AuthenticateByName', {'Username': usuario, 'Pw': SENHA})


def assistente() -> None:
    api('POST', '/Startup/Configuration', {'UICulture': 'pt-BR', 'MetadataCountryCode': 'BR',
                                           'PreferredMetadataLanguage': 'pt'})
    api('GET', '/Startup/User')
    api('POST', '/Startup/User', {'Name': 'admin', 'Password': SENHA})
    api('POST', '/Startup/RemoteAccess', {'EnableRemoteAccess': False, 'EnableAutomaticPortMapping': False})
    api('POST', '/Startup/Complete')


# Tipos de item que têm provedores de metadados e de imagens da internet
TIPOS = ('Movie', 'Series', 'Season', 'Episode', 'MusicAlbum', 'MusicArtist', 'Audio', 'AudioBook', 'Book',
         'Photo', 'BoxSet', 'Video')


def opcoes_biblioteca(caminho: Path, subtipo: str) -> dict:
    """Só leitura e sem internet: nada grava na pasta da mídia e nada sai da máquina.

    `EnableInternetProviders` sozinho não basta: quando um tipo tem opções, a lista de provedores dele é uma lista de
    permissão, então uma lista vazia desliga todos (a mídia de teste chegou a ser "identificada" pelo TMDB)."""
    return {
        'PathInfos': [{'Path': str(caminho)}],
        'Subtype': subtipo,
        'EnableInternetProviders': False,
        'SaveLocalMetadata': False,
        'MetadataSavers': [],
        'EnableRealtimeMonitor': False,
        'EnableTrickplayImageExtraction': False,
        'ExtractTrickplayImagesDuringLibraryScan': False,
        'SaveTrickplayWithMedia': False,
        'EnableChapterImageExtraction': False,
        'ExtractChapterImagesDuringLibraryScan': False,
        'DownloadImagesInAdvance': False,
        'AutomaticallyAddToCollection': False,
        'TypeOptions': [{'Type': t, 'MetadataFetchers': [], 'ImageFetchers': []} for t in TIPOS],
    }


NOMES = {
    'filmes': 'Filmes', 'series': 'Séries', 'documentarios-filmes': 'Documentários (filmes)',
    'documentarios-series': 'Documentários (séries)', 'musicas': 'Músicas', 'podcasts': 'Podcasts',
    'audiolivros': 'Audiolivros', 'livros': 'Livros', 'hqs': 'HQs', 'mangas': 'Mangás', 'fotos': 'Fotos',
}


def criar_bibliotecas(token: str) -> None:
    catalogo = json.loads((MIDIA / 'catalogo.json').read_text(encoding='utf-8'))
    for chave, info in catalogo.items():
        caminho = (MIDIA / info['pasta']).resolve()
        if MIDIA.resolve() not in caminho.parents:
            raise Erro(f'Recusado: {caminho} está fora da mídia de teste.')
        nome = urllib.parse.quote(NOMES.get(chave, chave))
        api('POST', f'/Library/VirtualFolders?name={nome}&collectionType={info["tipo"]}&refreshLibrary=false',
            {'LibraryOptions': opcoes_biblioteca(caminho, info['subtipo'])}, token)


def esperar_varredura(token: str, limite=300) -> None:
    api('POST', '/Library/Refresh', token=token)
    inicio = time.time()
    time.sleep(3)
    while time.time() - inicio < limite:
        tarefas = api('GET', '/ScheduledTasks', token=token)
        varredura = next((t for t in tarefas if t.get('Key') == 'RefreshLibrary'), None)
        if varredura and varredura.get('State') == 'Idle':
            return
        time.sleep(2)
    raise Erro('A varredura da mídia de teste passou do limite.')


def guardar_estado(token_admin: str) -> None:
    itens = api('GET', '/Items?Recursive=true&IncludeItemTypes=Movie,Series,Season,Episode,MusicAlbum,MusicArtist,'
                       'Audio,AudioBook,Book,Photo,PhotoAlbum,Folder&Fields=Path&Limit=500', token=token_admin)
    bibliotecas = api('GET', '/Library/VirtualFolders', token=token_admin)
    estado = {
        'url': URL,
        'usuarios': {u: SENHA for u in USUARIOS},
        'bibliotecas': {b['Name']: {'id': b['ItemId'], 'tipo': b.get('CollectionType'),
                                    'subtipo': b['LibraryOptions'].get('Subtype')} for b in bibliotecas},
        'itens': {f'{i["Type"]}:{i["Name"]}': i['Id'] for i in itens['Items']},
    }
    ESTADO.write_text(json.dumps(estado, indent=2, ensure_ascii=False), encoding='utf-8')


def garantir_usuarios(token: str) -> None:
    existentes = {u['Name'] for u in api('GET', '/Users', token=token)}
    for nome in USUARIOS:
        if nome not in existentes:
            api('POST', '/Users/New', {'Name': nome, 'Password': SENHA}, token)


def subir() -> None:
    if not (MIDIA / 'catalogo.json').exists():
        raise Erro('Gere a mídia antes: python3 ferramentas/midia_teste.py')
    if no_ar():
        token = login('admin')['AccessToken']
        garantir_usuarios(token)
        guardar_estado(token)
        print(f'Servidor de teste já está no ar em {URL}.')
        return
    novo = not (SERVIDOR / 'data').exists()
    iniciar()
    if novo:
        print('Primeira vez: assistente, contas e bibliotecas...')
        assistente()
        token = login('admin')['AccessToken']
        criar_bibliotecas(token)
        esperar_varredura(token)
        guardar_estado(token)
    elif not ESTADO.exists():
        guardar_estado(login('admin')['AccessToken'])
    garantir_usuarios(login('admin')['AccessToken'])
    print(f'Servidor de teste no ar em {URL} (contas: {", ".join(USUARIOS)}; senha "{SENHA}").')


def parar() -> None:
    pid = pid_vivo()
    if pid:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
        for _ in range(30):
            if pid_vivo() is None:
                break
            time.sleep(0.5)
        else:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        print('Servidor de teste encerrado.')
    else:
        print('Servidor de teste não estava rodando.')
    PIDFILE.unlink(missing_ok=True)


def main() -> None:
    comando = sys.argv[1] if len(sys.argv) > 1 else ''
    if comando == 'subir':
        subir()
    elif comando == 'parar':
        parar()
    elif comando == 'estado':
        print(f'{URL}: {"no ar" if no_ar() else "fora do ar"}; dados em {SERVIDOR}; mídia em {MIDIA}')
    elif comando == 'limpar':
        parar()
        shutil.rmtree(SERVIDOR, ignore_errors=True)
        ESTADO.unlink(missing_ok=True)
        print('Dados do servidor de teste apagados.')
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == '__main__':
    main()
