"""S05: as miniaturas da linha do tempo (trickplay) ficam na pasta de dados do servidor, nunca na pasta da mídia.

Mesmo pedindo `SaveTrickplayWithMedia` na biblioteca, o servidor do Croma ignora (a opção é travada em falso)."""
import os
import shutil
import time
import subprocess
import sys
from pathlib import Path

import pytest

BASE = Path.home() / '.cache' / 'croma-teste-trickplay'
os.environ['CROMA_TESTE_DIR'] = str(BASE)
os.environ['CROMA_TESTE_PORTA'] = '8099'
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import servidor_teste as st  # noqa: E402


def arvore(raiz: Path) -> dict:
    return {str(p.relative_to(raiz)): (p.stat().st_size, p.stat().st_mtime_ns) for p in sorted(raiz.rglob('*'))}


@pytest.fixture(scope='module')
def acervo():
    shutil.rmtree(BASE, ignore_errors=True)
    raiz = BASE / 'acervo' / 'movies'
    pasta = raiz / 'Filme T (2001)'
    pasta.mkdir(parents=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc=size=640x360:rate=10', '-t', '40',
                    '-pix_fmt', 'yuv420p', '-c:v', 'libx264', str(pasta / 'Filme T (2001).mp4')], check=True)
    return raiz


@pytest.fixture(scope='module')
def servidor(acervo):
    st.iniciar()
    st.assistente()
    token = st.login('admin')['AccessToken']
    opcoes = st.opcoes_biblioteca(acervo, 'Movies')
    opcoes.update({'EnableTrickplayImageExtraction': True, 'ExtractTrickplayImagesDuringLibraryScan': True,
                   'SaveTrickplayWithMedia': True})     # o servidor do Croma ignora este último
    st.api('POST', '/Library/VirtualFolders?name=Filmes%20T&collectionType=movies&refreshLibrary=false',
           {'LibraryOptions': opcoes}, token)
    yield token
    st.parar()


def test_miniaturas_ficam_nos_dados_e_nao_na_pasta_da_midia(servidor, acervo):
    antes = arvore(acervo)
    st.api('POST', '/Library/Refresh', token=servidor)
    st.esperar_varredura(servidor)
    filme = st.api('GET', '/Items?Recursive=true&IncludeItemTypes=Movie', token=servidor)['Items'][0]
    tarefa = next(t for t in st.api('GET', '/ScheduledTasks', token=servidor) if t['Key'] == 'RefreshTrickplayImages')
    st.api('POST', f'/ScheduledTasks/Running/{tarefa["Id"]}', token=servidor)
    for _ in range(60):
        filme = st.api('GET', f'/Items?Ids={filme["Id"]}&Fields=Trickplay', token=servidor)['Items'][0]
        if filme.get('Trickplay'):
            break
        time.sleep(2)
    assert filme.get('Trickplay'), 'o servidor não gerou as miniaturas'
    assert arvore(acervo) == antes, 'o trickplay gravou na pasta da mídia'
    achadas = [p for p in (BASE).rglob('*') if 'trickplay' in str(p).lower() and acervo not in p.parents]
    assert achadas, 'as miniaturas não estão na pasta de dados'
