"""S02: varredura de uma pasta no padrão Baú de mentira, de ponta a ponta, num servidor descartável (porta 8098).

Confere os metadados lidos do `metadata.json`, as coleções (`collection.json`) e que a varredura não grava nada na
pasta da mídia (a regra do acervo intocável)."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

BASE = Path.home() / '.cache' / 'croma-teste-bau'
os.environ['CROMA_TESTE_DIR'] = str(BASE)
os.environ['CROMA_TESTE_PORTA'] = '8098'
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import servidor_teste as st  # noqa: E402

UUID_A = '019a5f3c-0000-7000-8000-00000000000a'
UUID_B = '019a5f3c-0000-7000-8000-00000000000b'
UUID_C = '019a5f3c-0000-7000-8000-00000000000c'
UUID_COLECAO = '019a5f3c-0000-7000-8000-0000000000c0'


def fotografar(raiz: Path) -> dict:
    """Todos os arquivos e pastas da árvore, com tamanho, data e hash."""
    saida = {}
    for p in sorted(raiz.rglob('*')):
        rel = str(p.relative_to(raiz))
        if p.is_dir():
            saida[rel] = 'pasta'
        else:
            saida[rel] = (p.stat().st_size, p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest())
    return saida


def criar_filme(movies: Path, uuid: str, titulo: str, ano: int, tags: list[str]) -> None:
    pasta = movies / f'{titulo} ({ano})'
    (pasta / 'metadata' / 'images').mkdir(parents=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc=size=320x180:rate=10', '-t', '2',
                    '-pix_fmt', 'yuv420p', '-c:v', 'libx264', str(pasta / f'{titulo} ({ano}).mp4')], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=red:s=200x300', '-frames:v', '1',
                    str(pasta / 'metadata' / 'images' / 'poster.jpg')], check=True)
    (pasta / 'metadata' / 'metadata.json').write_text(json.dumps({
        'schema_version': 2, 'uuid': uuid, 'title': titulo, 'year': ano, 'tags': tags,
        'directors': ['Diretora de Teste'], 'content_rating': '14', 'description': f'Sobre {titulo}.',
        'release_date': f'{ano}-05-01', 'cast': [{'name': 'Atriz de Teste', 'character': 'Ela'}],
        'files': [{'file': f'{titulo} ({ano}).mp4', 'uuid': uuid[:-1] + '1'}]}), encoding='utf-8')


def escrever_colecao(colecoes: Path, nome: str, itens: list[str]) -> Path:
    pasta = colecoes / 'Saga'
    (pasta / 'images').mkdir(parents=True, exist_ok=True)
    if not (pasta / 'images' / 'poster.jpg').exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=blue:s=200x300', '-frames:v', '1',
                        str(pasta / 'images' / 'poster.jpg')], check=True)
    arquivo = pasta / 'collection.json'
    arquivo.write_text(json.dumps({'schema_version': 2, 'uuid': UUID_COLECAO, 'name': nome,
                                   'description': 'Uma saga.', 'tags': ['Saga'], 'items': itens}), encoding='utf-8')
    return arquivo


@pytest.fixture(scope='module')
def acervo():
    shutil.rmtree(BASE, ignore_errors=True)
    raiz = BASE / 'acervo' / 'Filmes'
    movies = raiz / 'movies'
    criar_filme(movies, UUID_A, 'Filme A', 2001, ['Ação', 'Marca Minha'])
    criar_filme(movies, UUID_B, 'Filme B', 2002, ['Drama'])
    criar_filme(movies, UUID_C, 'Filme C', 2003, [])
    escrever_colecao(raiz / 'collections', 'Saga Teste', [UUID_A, UUID_B])
    return raiz


@pytest.fixture(scope='module')
def servidor(acervo):
    st.iniciar()
    st.assistente()
    token = st.login('admin')['AccessToken']
    nome = 'Filmes%20Bau'
    st.api('POST', f'/Library/VirtualFolders?name={nome}&collectionType=movies&refreshLibrary=false',
           {'LibraryOptions': st.opcoes_biblioteca(acervo / 'movies', 'Movies')}, token)
    yield token
    st.parar()


def escanear(token):
    st.esperar_varredura(token)


def itens(token, tipo):
    return st.api('GET', f'/Items?Recursive=true&IncludeItemTypes={tipo}&Fields=ProviderIds,Overview,Tags,People,Genres'
                         '&CollapseBoxSetItems=false', token=token)['Items']


def colecao(token):
    achadas = itens(token, 'BoxSet')
    return achadas[0] if len(achadas) == 1 else achadas


def filhos(token, id_):
    return {i['Name'] for i in st.api('GET', f'/Items?ParentId={id_}', token=token)['Items']}


def test_varrer_le_os_metadados_sem_gravar_na_pasta(servidor, acervo):
    antes = fotografar(acervo)
    escanear(servidor)
    filmes = {f['Name']: f for f in itens(servidor, 'Movie')}
    assert set(filmes) == {'Filme A', 'Filme B', 'Filme C'}
    a = filmes['Filme A']
    assert a['ProductionYear'] == 2001
    assert a['Overview'] == 'Sobre Filme A.'
    assert a['ProviderIds'].get('Bau') == UUID_A
    # a lista do Baú mistura gêneros e tags: os gêneros do TMDB viram gêneros, o resto vira tag
    assert a['Genres'] == ['Ação'] and a['Tags'] == ['Marca Minha']
    assert any(p['Name'] == 'Atriz de Teste' for p in a['People'])
    assert a['ImageTags'].get('Primary'), 'o poster do metadata/images não foi lido'
    assert fotografar(acervo) == antes, 'a varredura mexeu na pasta da mídia'


def test_colecao_criada_pelo_uuid_com_os_itens_do_arquivo(servidor):
    c = colecao(servidor)
    assert isinstance(c, dict), f'esperava uma coleção, veio {c}'
    assert c['Name'] == 'Saga Teste'
    assert c['ProviderIds']['Bau'] == UUID_COLECAO
    assert filhos(servidor, c['Id']) == {'Filme A', 'Filme B'}


def test_nova_varredura_nao_duplica_e_renomear_mantem_a_colecao(servidor, acervo):
    id_antes = colecao(servidor)['Id']
    escanear(servidor)
    assert len(itens(servidor, 'BoxSet')) == 1
    escrever_colecao(acervo / 'collections', 'Saga Renomeada', [UUID_A, UUID_B])
    escanear(servidor)
    c = colecao(servidor)
    assert isinstance(c, dict) and c['Id'] == id_antes and c['Name'] == 'Saga Renomeada'


def test_item_posto_a_mao_sai_na_proxima_varredura(servidor):
    c = colecao(servidor)
    c_filme = next(f for f in itens(servidor, 'Movie') if f['Name'] == 'Filme C')
    st.api('POST', f'/Collections/{c["Id"]}/Items?ids={c_filme["Id"]}', token=servidor)
    assert 'Filme C' in filhos(servidor, c['Id'])
    escanear(servidor)
    assert filhos(servidor, c['Id']) == {'Filme A', 'Filme B'}


def test_arquivo_da_colecao_some_e_a_colecao_fica(servidor, acervo):
    (acervo / 'collections' / 'Saga' / 'collection.json').unlink()
    escanear(servidor)
    c = colecao(servidor)
    assert isinstance(c, dict) and c['Name'] == 'Saga Renomeada'
    assert filhos(servidor, c['Id']) == {'Filme A', 'Filme B'}


def test_biblioteca_sem_o_campo_usa_o_subtipo_padrao_e_editar_recusa_incompativel(servidor, acervo):
    """S01: biblioteca de antes do subtipo (sem o campo) e edição com subtipo que não combina com o tipo."""
    opcoes = st.opcoes_biblioteca(acervo / 'movies', 'Movies')
    del opcoes['Subtype']
    st.api('POST', '/Library/VirtualFolders?name=Antiga&collectionType=tvshows&refreshLibrary=false',
           {'LibraryOptions': opcoes}, servidor)
    antiga = next(b for b in st.api('GET', '/Library/VirtualFolders', token=servidor) if b['Name'] == 'Antiga')
    assert antiga['LibraryOptions'].get('Subtype') in (None, 'Series')
    catalogo = {i['Subtype']: i for i in st.api('GET', '/Library/Subtypes', token=servidor)}
    assert 'tvshows' in catalogo['Series']['DefaultForCollectionTypes']
    corpo = {'Id': antiga['ItemId'], 'LibraryOptions': {**opcoes, 'Subtype': 'Music'}}
    with pytest.raises(SystemExit, match='400'):
        st.api('POST', '/Library/VirtualFolders/LibraryOptions', corpo, servidor)
    corpo['LibraryOptions']['Subtype'] = 'Documentaries'
    st.api('POST', '/Library/VirtualFolders/LibraryOptions', corpo, servidor)
