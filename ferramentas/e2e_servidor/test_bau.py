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


UUID_SERIE = '019a5f3c-0000-7000-8000-0000000000d0'


def video(caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc=size=320x180:rate=10', '-t', '2',
                    '-pix_fmt', 'yuv420p', '-c:v', 'libx264', str(caminho)], check=True)


@pytest.fixture(scope='module')
def serie(servidor, acervo):
    """Uma série no padrão Baú: o título do episódio vem do arquivo de metadados, achado pelo caminho do vídeo."""
    raiz = acervo.parent / 'Series'
    pasta = raiz / 'shows' / 'Serie Bau (2010)'
    video(pasta / 'Season 01' / 'Serie Bau (2010) - S01E01 - nome do arquivo.mp4')
    video(pasta / 'Season 01' / 'Serie Bau (2010) - S01E02 - nome do arquivo.mp4')
    video(pasta / 'Season 01' / 'Serie Bau (2010) - S01E03 - fora da lista.mp4')
    video(pasta / 'Specials' / 'Serie Bau (2010) - S00E01 - especial.mp4')
    (pasta / 'metadata' / 'images').mkdir(parents=True)
    (pasta / 'metadata' / 'metadata.json').write_text(json.dumps({
        'schema_version': 2, 'uuid': UUID_SERIE, 'title': 'Serie do Bau', 'year': 2010, 'status': 'ended',
        'description': 'Uma série de teste.', 'tags': ['Drama'], 'first_air_date': '2010-01-01',
        'seasons': [{'number': 0, 'episodes_in_files': 1}, {'number': 1, 'episodes_in_files': 3}],
        'episodes': [
            {'uuid': UUID_SERIE[:-1] + '1', 'season': 1, 'episode': 1, 'title': 'Piloto do Bau',
             'file': 'Season 01/Serie Bau (2010) - S01E01 - nome do arquivo.mp4'},
            {'uuid': UUID_SERIE[:-1] + '2', 'season': 1, 'episode': 2, 'title': 'Segundo do Bau',
             'file': 'Season 01/Serie Bau (2010) - S01E02 - nome do arquivo.mp4'},
            {'uuid': UUID_SERIE[:-1] + '3', 'season': 0, 'episode': 1, 'title': 'Especial do Bau',
             'file': 'Specials/Serie Bau (2010) - S00E01 - especial.mp4'}],
        'files': []}), encoding='utf-8')
    st.api('POST', '/Library/VirtualFolders?name=Series%20Bau&collectionType=tvshows&refreshLibrary=false',
           {'LibraryOptions': st.opcoes_biblioteca(raiz / 'shows', 'Series')}, servidor)
    antes = fotografar(raiz)
    escanear(servidor)
    return raiz, antes


def test_serie_le_titulo_e_episodios_pelo_arquivo(servidor, serie):
    raiz, antes = serie
    series = [s for s in itens(servidor, 'Series') if s['ProviderIds'].get('Bau') == UUID_SERIE]
    assert len(series) == 1 and series[0]['Name'] == 'Serie do Bau'
    assert series[0]['ProductionYear'] == 2010 and series[0]['Overview'] == 'Uma série de teste.'
    episodios = {(e['ParentIndexNumber'], e['IndexNumber']): e['Name']
                 for e in itens(servidor, 'Episode') if e.get('SeriesName') == 'Serie do Bau'}
    assert episodios[(1, 1)] == 'Piloto do Bau'
    assert episodios[(1, 2)] == 'Segundo do Bau'
    assert episodios[(0, 1)] == 'Especial do Bau', 'o especial (temporada 0) não foi lido'


def test_video_fora_da_lista_fica_com_o_nome_do_arquivo(servidor, serie):
    episodio = next(e for e in itens(servidor, 'Episode') if e.get('IndexNumber') == 3 and e.get('ParentIndexNumber') == 1)
    # sem entrada no metadata.json o episódio segue a leitura padrão do nome do arquivo, sem título do Baú
    assert episodio['Name'] not in ('Piloto do Bau', 'Segundo do Bau', 'Especial do Bau')


def test_varrer_serie_nao_grava_na_pasta(servidor, serie):
    raiz, antes = serie
    escanear(servidor)
    assert fotografar(raiz) == antes, 'a varredura mexeu na pasta da série'


UUID_MUSICA = '019a5f3c-0000-7000-8000-0000000000e0'


def mp3(caminho: Path, titulo: str, artista: str, album: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=2', '-c:a', 'libmp3lame',
                    '-metadata', f'title={titulo}', '-metadata', f'artist={artista}', '-metadata', f'album={album}',
                    str(caminho)], check=True)


@pytest.fixture(scope='module')
def musica(servidor, acervo):
    """Uma biblioteca de Músicas no padrão Baú: coleção/tracks/id.mp3 e coleção/metadata/playlist.json."""
    raiz = acervo.parent / 'Musicas'
    colecao = raiz / 'artista-teste'
    # o artista da tag é o do JSON (como no acervo real): o Jellyfin une os artistas da tag e do provedor
    mp3(colecao / 'tracks' / 'faixa-um.mp3', 'titulo da tag um', 'Artista de Teste', 'Tag Album')
    mp3(colecao / 'tracks' / 'faixa-dois.mp3', 'titulo da tag dois', 'Artista de Teste', 'Tag Album')
    mp3(colecao / 'tracks' / 'fora.mp3', 'Fora da Lista', 'Tag Artista', 'Tag Album')
    (colecao / 'metadata' / 'covers').mkdir(parents=True)
    for nome in ('cover', 'covers/faixa-um'):
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=green:s=300x300', '-frames:v', '1',
                        str(colecao / 'metadata' / f'{nome}.jpg')], check=True)
    # os marcadores do padrão: a Jellyfin não deve entrar em metadata/
    (colecao / 'metadata' / '.ignore').write_text('*\n*/*\n')
    (colecao / 'metadata' / 'playlist.json').write_text(json.dumps({
        'schema_version': 2, 'uuid': UUID_MUSICA, 'id': 'artista-teste', 'type': 'artist', 'title': 'Artista de Teste',
        'description': 'Uma coleção de música.', 'cover': 'metadata/cover.jpg', 'tracks_base': '../tracks',
        'tracks': [
            {'uuid': UUID_MUSICA[:-1] + '1', 'id': 'faixa-um', 'file': 'faixa-um.mp3', 'title': 'Faixa Um do Bau',
             'artist': 'Artista de Teste', 'album': 'Album do Bau', 'year': '2015'},
            {'uuid': UUID_MUSICA[:-1] + '2', 'id': 'faixa-dois', 'file': 'faixa-dois.mp3', 'title': 'Faixa Dois do Bau',
             'artist': 'Artista de Teste', 'album': 'Album do Bau', 'year': 2016}],
        'files': []}), encoding='utf-8')
    (raiz / '_management').mkdir()
    (raiz / '_management' / 'lixo.mp3').write_bytes(b'x')
    (raiz / '_management' / '.ignore').write_text('*\n*/*\n')
    st.api('POST', '/Library/VirtualFolders?name=Musicas%20Bau&collectionType=music&refreshLibrary=false',
           {'LibraryOptions': st.opcoes_biblioteca(raiz, 'Music')}, servidor)
    antes = fotografar(raiz)
    escanear(servidor)
    return raiz, antes


def test_musica_le_a_faixa_pelo_playlist_json(servidor, musica):
    faixas = {f['Name']: f for f in itens(servidor, 'Audio')}
    um = faixas['Faixa Um do Bau']
    assert um['Artists'] == ['Artista de Teste'] and um['Album'] == 'Album do Bau'
    assert um['ProductionYear'] == 2015 and faixas['Faixa Dois do Bau']['ProductionYear'] == 2016
    assert um['ProviderIds']['Bau'] == UUID_MUSICA[:-1] + '1'
    assert um['ImageTags'].get('Primary'), 'a capa da faixa (metadata/covers) não foi lida'
    # fora da lista: segue as tags do próprio MP3
    assert faixas['Fora da Lista']['Artists'] == ['Tag Artista']
    assert 'lixo' not in ' '.join(faixas), 'a pasta _management deveria ser ignorada'


def test_musica_cria_a_colecao_com_as_faixas_na_ordem_e_a_capa(servidor, musica):
    colecoes = [c for c in itens(servidor, 'BoxSet') if c['ProviderIds'].get('Bau') == UUID_MUSICA]
    assert len(colecoes) == 1
    c = colecoes[0]
    assert c['Name'] == 'Artista de Teste' and 'artist' in c['Tags'] and c['Overview'] == 'Uma coleção de música.'
    assert c['ImageTags'].get('Primary')
    assert filhos(servidor, c['Id']) == {'Faixa Um do Bau', 'Faixa Dois do Bau'}


def test_varrer_musica_nao_grava_na_pasta(servidor, musica):
    raiz, antes = musica
    escanear(servidor)
    assert fotografar(raiz) == antes, 'a varredura mexeu na pasta da música'
