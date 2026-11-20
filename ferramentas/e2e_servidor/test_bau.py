"""S02: varredura de uma pasta no padrão Baú de mentira, de ponta a ponta, num servidor descartável (porta 8098).

Confere os metadados lidos do `metadata.json`, as coleções (`collection.json`) e que a varredura não grava nada na
pasta da mídia (a regra do acervo intocável)."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
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


def test_filtro_de_tags_qualquer_ou_todas(servidor, acervo):
    """Croma: `tagsMatchAll=true` exige todas as tags; sem ele o filtro segue o padrão do Jellyfin (qualquer uma)."""
    from urllib.parse import quote
    escanear(servidor)
    filmes = {f"Filme {chr(64 + i['ProductionYear'] - 2000)}": i['Id'] for i in itens(servidor, 'Movie')}
    for nome, tags in (('Filme A', ['praia', 'família']), ('Filme B', ['praia']), ('Filme C', [])):
        completo = st.api('GET', f'/Items/{filmes[nome]}', token=servidor)
        completo['Tags'] = tags
        st.api('POST', f'/Items/{filmes[nome]}', completo, servidor)

    def nomes(consulta):
        consulta = quote(consulta, safe='=&|')
        achados = st.api('GET', f'/Items?Recursive=true&IncludeItemTypes=Movie&{consulta}', token=servidor)['Items']
        return {f"Filme {chr(64 + i['ProductionYear'] - 2000)}" for i in achados}

    assert nomes('tags=praia|família') == {'Filme A', 'Filme B'}
    assert nomes('tags=praia|família&tagsMatchAll=true') == {'Filme A'}
    assert nomes('tags=família|viagem&tagsMatchAll=true') == set()
    assert nomes('tags=FAMILIA|praia&tagsMatchAll=true') in ({'Filme A'}, set())   # o filtro do Jellyfin não ignora acento
    assert nomes('tags=praia&tagsMatchAll=true') == {'Filme A', 'Filme B'}


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


def id_da_biblioteca(token, nome):
    return next(v['ItemId'] for v in st.api('GET', '/Library/VirtualFolders', token=token) if v['Name'] == nome)


def test_tags_editadas_sobrevivem_a_atualizar_os_metadados(servidor, acervo):
    """D15: a trava do campo Tags (`LockedFields`) impede que "Substituir metadados existentes" apague as tags editadas."""
    import time
    filmes = {f"Filme {chr(64 + i['ProductionYear'] - 2000)}": i['Id'] for i in itens(servidor, 'Movie')}
    id_ = filmes['Filme B']
    completo = st.api('GET', f'/Items/{id_}', token=servidor)
    completo['Tags'] = ['minha-tag', 'outra-tag']
    completo['LockedFields'] = sorted(set(completo.get('LockedFields') or []) | {'Tags'})
    st.api('POST', f'/Items/{id_}', completo, servidor)

    st.api('POST', f'/Items/{id_}/Refresh?Recursive=false&MetadataRefreshMode=FullRefresh&ImageRefreshMode=None'
                   '&ReplaceAllMetadata=true', token=servidor)
    for _ in range(30):
        time.sleep(1)
        tags = st.api('GET', f'/Items/{id_}', token=servidor)['Tags']
        if sorted(tags) != ['minha-tag', 'outra-tag']:
            break
    assert sorted(st.api('GET', f'/Items/{id_}', token=servidor)['Tags']) == ['minha-tag', 'outra-tag']


def filme_da_saga(token):
    saga = next(c for c in itens(token, 'BoxSet') if c['ProviderIds'].get('Bau') == UUID_COLECAO)
    return st.api('GET', f'/Items?ParentId={saga["Id"]}', token=token)['Items'][0]


def test_colecao_do_bau_tem_a_biblioteca_como_dona(servidor, musica):
    """S04: o dono é um campo do BoxSet; cada coleção guarda a biblioteca de onde veio."""
    filmes = id_da_biblioteca(servidor, 'Filmes Bau')
    saga = next(c for c in itens(servidor, 'BoxSet') if c['ProviderIds'].get('Bau') == UUID_COLECAO)
    detalhe = st.api('GET', f'/Items?Ids={saga["Id"]}', token=servidor)['Items'][0]
    assert detalhe['OwnerLibraryId'].replace('-', '') == filmes.replace('-', '')
    discos = next(c for c in itens(servidor, 'BoxSet') if c['ProviderIds'].get('Bau') == UUID_MUSICA)
    assert discos['OwnerLibraryId'].replace('-', '') != filmes.replace('-', '')


def test_colecao_com_dono_recusa_item_de_outra_biblioteca(servidor, musica):
    saga = next(c for c in itens(servidor, 'BoxSet') if c['ProviderIds'].get('Bau') == UUID_COLECAO)
    faixa = itens(servidor, 'Audio')[0]
    antes = filhos(servidor, saga['Id'])
    with pytest.raises(st.Erro, match='400'):
        st.api('POST', f'/Collections/{saga["Id"]}/Items?ids={faixa["Id"]}', token=servidor)
    assert filhos(servidor, saga['Id']) == antes


def test_colecao_criada_pela_api_com_dono_aceita_so_a_biblioteca_dela(servidor, musica):
    filmes = id_da_biblioteca(servidor, 'Filmes Bau')
    filme = filme_da_saga(servidor)
    faixa = itens(servidor, 'Audio')[0]
    nova = st.api('POST', f'/Collections?name=Dona%20Api&ownerLibraryId={filmes}&ids={filme["Id"]}', token=servidor)
    detalhe = st.api('GET', f'/Items?Ids={nova["Id"]}', token=servidor)['Items'][0]
    assert detalhe['OwnerLibraryId'].replace('-', '') == filmes.replace('-', '')
    with pytest.raises(st.Erro, match='400'):
        st.api('POST', f'/Collections/{nova["Id"]}/Items?ids={faixa["Id"]}', token=servidor)


def test_colecao_sem_dono_continua_aceitando_qualquer_item(servidor, musica):
    faixa = itens(servidor, 'Audio')[0]
    filme = filme_da_saga(servidor)
    # sem itens na criação, a coleção fica sem dono (com itens ela toma a biblioteca do primeiro)
    nova = st.api('POST', '/Collections?name=Sem%20Dono', token=servidor)
    st.api('POST', f'/Collections/{nova["Id"]}/Items?ids={filme["Id"]}', token=servidor)
    st.api('POST', f'/Collections/{nova["Id"]}/Items?ids={faixa["Id"]}', token=servidor)
    detalhe = st.api('GET', f'/Items?Ids={nova["Id"]}', token=servidor)['Items'][0]
    assert not detalhe.get('OwnerLibraryId')


def test_listar_colecoes_por_dono(servidor, musica):
    filmes = id_da_biblioteca(servidor, 'Filmes Bau')
    nomes = {c['Name'] for c in st.api('GET', f'/Collections?ownerLibraryId={filmes}', token=servidor)['Items']}
    assert {'Saga Renomeada', 'Dona Api'} <= nomes
    assert 'Artista de Teste' not in nomes


def test_listar_as_colecoes_que_aceitam_um_item(servidor, musica):
    filme = filme_da_saga(servidor)
    nomes = {c['Name'] for c in st.api('GET', f'/Collections?itemId={filme["Id"]}', token=servidor)['Items']}
    assert 'Saga Renomeada' in nomes and 'Artista de Teste' not in nomes
    faixa = itens(servidor, 'Audio')[0]
    nomes = {c['Name'] for c in st.api('GET', f'/Collections?itemId={faixa["Id"]}', token=servidor)['Items']}
    assert 'Artista de Teste' in nomes and 'Saga Renomeada' not in nomes
    with pytest.raises(st.Erro, match='400'):
        st.api('GET', '/Collections', token=servidor)


def test_colecao_criada_com_itens_toma_a_biblioteca_do_primeiro(servidor, musica):
    faixa = itens(servidor, 'Audio')[0]
    nova = st.api('POST', f'/Collections?name=So%20Musica&ids={faixa["Id"]}', token=servidor)
    detalhe = st.api('GET', f'/Items?Ids={nova["Id"]}', token=servidor)['Items'][0]
    filmes = id_da_biblioteca(servidor, 'Filmes Bau')
    assert detalhe['OwnerLibraryId'].replace('-', '') != filmes.replace('-', '')


def test_modo_de_exibicao_da_colecao(servidor, musica):
    saga = next(c for c in itens(servidor, 'BoxSet') if c['ProviderIds'].get('Bau') == UUID_COLECAO)

    def modo():
        return st.api('GET', f'/Items?Ids={saga["Id"]}', token=servidor)['Items'][0]['CollectionDisplayShape']

    assert modo() == 'Poster'
    for escolhido in ('Thumbnail', 'Square', 'Poster'):
        st.api('POST', f'/Collections/{saga["Id"]}/DisplayMode?shape={escolhido}', token=servidor)
        assert modo() == escolhido


def test_colecao_de_musica_vem_quadrada_e_aceita_trocar(servidor, musica):
    faixa = itens(servidor, 'Audio')[0]
    nova = st.api('POST', f'/Collections?name=Quadrada&ids={faixa["Id"]}', token=servidor)

    def modo():
        return st.api('GET', f'/Items?Ids={nova["Id"]}', token=servidor)['Items'][0]['CollectionDisplayShape']

    assert modo() == 'Square'
    st.api('POST', f'/Collections/{nova["Id"]}/DisplayMode?shape=Poster', token=servidor)
    assert modo() == 'Poster'


def test_varredura_da_dono_a_colecao_feita_a_mao(servidor, musica):
    filme = filme_da_saga(servidor)
    nova = st.api('POST', '/Collections?name=Feita%20a%20Mao', token=servidor)
    st.api('POST', f'/Collections/{nova["Id"]}/Items?ids={filme["Id"]}', token=servidor)
    antes = st.api('GET', f'/Items?Ids={nova["Id"]}', token=servidor)['Items'][0]
    assert not antes.get('OwnerLibraryId')
    escanear(servidor)
    filmes = id_da_biblioteca(servidor, 'Filmes Bau')
    for _ in range(15):
        depois = st.api('GET', f'/Items?Ids={nova["Id"]}', token=servidor)['Items'][0]
        if depois.get('OwnerLibraryId'):
            break
        time.sleep(2)
    assert depois['OwnerLibraryId'].replace('-', '') == filmes.replace('-', '')


def test_modo_de_exibicao_das_colecoes_da_biblioteca(servidor, acervo):
    """O modo (pôster ou miniatura) da aba Coleções é uma opção da biblioteca e chega na visão do usuário."""
    uid = st.api('GET', '/Users/Me', token=servidor)['Id']

    def modo():
        visoes = st.api('GET', f'/UserViews?userId={uid}', token=servidor)['Items']
        return next(v for v in visoes if v['Name'] == 'Filmes Bau')['CollectionsUseThumbnails']

    assert modo() is False
    pasta = next(b for b in st.api('GET', '/Library/VirtualFolders', token=servidor) if b['Name'] == 'Filmes Bau')
    opcoes = pasta['LibraryOptions']
    opcoes['CollectionsUseThumbnails'] = True
    st.api('POST', '/Library/VirtualFolders/LibraryOptions', {'Id': pasta['ItemId'], 'LibraryOptions': opcoes}, servidor)
    assert modo() is True
    opcoes['CollectionsUseThumbnails'] = False
    st.api('POST', '/Library/VirtualFolders/LibraryOptions', {'Id': pasta['ItemId'], 'LibraryOptions': opcoes}, servidor)
    assert modo() is False


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



# S08: podcasts e livros. As duas bibliotecas são a pasta inteira (Podcasts/, Livros/), com as coleções dentro.
UUID_PROGRAMA = '019a5f3c-0000-7000-8000-0000000000f0'
UUID_EP_LOST = '019a5f3c-0000-7000-8000-0000000000f1'
UUID_EP_GRINCH = '019a5f3c-0000-7000-8000-0000000000f2'
UUID_COLECAO_PODCAST = '019a5f3c-0000-7000-8000-0000000000f9'


def ignorar(pasta: Path) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / '.ignore').write_text('*\n*/*\n')


def capa(caminho: Path, cor: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', f'color=c={cor}:s=300x300', '-frames:v', '1',
                    str(caminho)], check=True)


@pytest.fixture(scope='module')
def podcasts(servidor, acervo):
    """Podcasts/ no padrão Baú: programa/episodes/<id>.mp3, programa/metadata/program.json e collections/."""
    raiz = acervo.parent / 'Podcasts'
    programa = raiz / 'nerdcast'
    # nomes como os do acervo real: número com a letra da parte e sem número
    mp3(programa / 'episodes' / '028a-lost.mp3', 'tag 28a', 'Jovem Nerd', 'NerdCast')
    mp3(programa / 'episodes' / '241-como-o-grinch.mp3', 'tag 241', 'Jovem Nerd', 'NerdCast')
    mp3(programa / 'episodes' / '251-rpg.mp3', 'tag 251', 'Jovem Nerd', 'NerdCast')
    ignorar(programa / 'metadata')
    capa(programa / 'metadata' / 'cover.jpg', 'yellow')
    capa(programa / 'metadata' / 'covers' / '028a-lost.jpg', 'red')
    episodio = {'description': None, 'season': None, 'duration_s': 2.0, 'chapters': [], 'guid': None, 'cover': None}
    (programa / 'metadata' / 'program.json').write_text(json.dumps({
        'schema_version': 2, 'uuid': UUID_PROGRAMA, 'id': 'nerdcast', 'title': 'NerdCast do Bau',
        'description': 'Um programa de teste.', 'author': 'Jovem Nerd', 'language': 'pt', 'tags': [],
        'feed_url': None, 'source': 'manual', 'cover': 'metadata/cover.jpg', 'status': 'active',
        'episodes': [
            {**episodio, 'uuid': UUID_EP_LOST, 'id': '028a-lost', 'file': '028a-lost.mp3', 'title': 'Lost, parte 1',
             'description': 'Notas do episódio.', 'number': '028a', 'participants': ['Alottoni', 'Azaghâl'],
             'published_at': '2006-11-24', 'cover': 'metadata/covers/028a-lost.jpg'},
            {**episodio, 'uuid': UUID_EP_GRINCH, 'id': '241-como-o-grinch', 'file': '241-como-o-grinch.mp3',
             'title': 'Como o Grinch roubou o NerdCast', 'number': '241', 'participants': ['Alottoni'],
             'published_at': '2010-12-24'},
            # data que o usuário ainda vai digitar (como os episódios de RPG do acervo)
            {**episodio, 'uuid': UUID_EP_LOST[:-1] + '3', 'id': '251-rpg', 'file': '251-rpg.mp3', 'title': 'RPG',
             'number': '251', 'participants': [], 'published_at': None}],
        'files': []}), encoding='utf-8')
    colecao = raiz / 'collections' / 'lost'
    colecao.mkdir(parents=True)
    (colecao / 'collection.json').write_text(json.dumps({
        'schema_version': 2, 'uuid': UUID_COLECAO_PODCAST, 'id': 'lost', 'name': 'Lost', 'description': None,
        'tags': [], 'items': [UUID_EP_LOST], 'files': []}), encoding='utf-8')
    ignorar(raiz / '_management')
    (raiz / '_management' / 'lixo.mp3').write_bytes(b'x')
    st.api('POST', '/Library/VirtualFolders?name=Podcasts%20Bau&collectionType=books&refreshLibrary=false',
           {'LibraryOptions': st.opcoes_biblioteca(raiz, 'Podcasts')}, servidor)
    antes = fotografar(raiz)
    escanear(servidor)
    return raiz, antes


def test_podcast_le_os_episodios_pelo_program_json(servidor, podcasts):
    episodios = {e['Name']: e for e in st.api(
        'GET', '/Items?Recursive=true&IncludeItemTypes=AudioBook&Fields=ProviderIds,Overview,Studios,PremiereDate',
        token=servidor)['Items']}
    assert set(episodios) == {'Lost, parte 1', 'Como o Grinch roubou o NerdCast', 'RPG'}, episodios.keys()
    lost = episodios['Lost, parte 1']
    assert lost['ProviderIds']['Bau'] == UUID_EP_LOST
    assert lost['Overview'] == 'Notas do episódio.' and lost['Album'] == 'NerdCast do Bau'
    assert lost['PremiereDate'].startswith('2006-11-24') and lost['ProductionYear'] == 2006
    assert lost['IndexNumber'] == 28
    assert {'Alottoni', 'Azaghâl'} <= set(lost['Artists'])
    assert [s['Name'] for s in lost['Studios']] == ['Jovem Nerd']
    assert lost['ImageTags'].get('Primary'), 'a capa do episódio (metadata/covers) não foi lida'
    assert not episodios['RPG'].get('PremiereDate', '').startswith('2'), 'episódio sem data ganhou uma'


def test_podcast_programa_e_a_pasta_com_titulo_capa_e_autor(servidor, podcasts):
    biblioteca = id_da_biblioteca(servidor, 'Podcasts Bau')
    raiz = st.api('GET', f'/Items?ParentId={biblioteca}&Fields=ProviderIds,Overview,Studios', token=servidor)['Items']
    # só o programa: a pasta collections/ e a _management ficam de fora
    assert [i['Name'] for i in raiz] == ['NerdCast do Bau'], [i['Name'] for i in raiz]
    programa = raiz[0]
    assert programa['Type'] == 'Folder' and programa['ProviderIds']['Bau'] == UUID_PROGRAMA
    assert programa['Overview'] == 'Um programa de teste.'
    assert [s['Name'] for s in programa['Studios']] == ['Jovem Nerd']
    assert programa['ImageTags'].get('Primary'), 'a capa do programa (metadata/cover) não foi lida'


def test_podcast_colecao_do_bau_com_os_episodios(servidor, podcasts):
    colecoes = [c for c in itens(servidor, 'BoxSet') if c['ProviderIds'].get('Bau') == UUID_COLECAO_PODCAST]
    assert len(colecoes) == 1
    assert filhos(servidor, colecoes[0]['Id']) == {'Lost, parte 1'}


def test_varrer_podcasts_nao_grava_na_pasta(servidor, podcasts):
    raiz, antes = podcasts
    escanear(servidor)
    assert fotografar(raiz) == antes, 'a varredura mexeu na pasta dos podcasts'


UUID_LIVRO = '019a5f3c-0000-7000-8000-0000000000d0'
UUID_COLECAO_LIVROS = '019a5f3c-0000-7000-8000-0000000000d9'


def epub(caminho: Path, titulo: str) -> None:
    """Um EPUB mínimo, com o OPF que o Jellyfin lê (título diferente do book.json, para ver quem vence)."""
    import zipfile
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(caminho, 'w') as z:
        z.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
        z.writestr('META-INF/container.xml', '<?xml version="1.0"?><container version="1.0" '
                   'xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile '
                   'full-path="content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
        z.writestr('content.opf', '<?xml version="1.0"?><package xmlns="http://www.idpf.org/2007/opf" version="2.0" '
                   'unique-identifier="id"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
                   f'<dc:title>{titulo}</dc:title><dc:identifier id="id">x</dc:identifier><dc:language>pt-BR'
                   '</dc:language></metadata><manifest><item id="c" href="c.xhtml" media-type="application/xhtml+xml"/>'
                   '</manifest><spine><itemref idref="c"/></spine></package>')
        z.writestr('c.xhtml', '<html xmlns="http://www.w3.org/1999/xhtml"><body><p>Oi.</p></body></html>')


@pytest.fixture(scope='module')
def livros(servidor, acervo):
    """Livros/ no padrão Baú: autor/titulo/titulo.epub, autor/titulo/metadata/book.json e collections/."""
    raiz = acervo.parent / 'Livros'
    pasta = raiz / 'j-r-r-tolkien' / 'a-sociedade-do-anel'
    epub(pasta / 'a-sociedade-do-anel.epub', 'Titulo do OPF')
    ignorar(pasta / 'metadata')
    capa(pasta / 'metadata' / 'cover.jpg', 'purple')
    (pasta / 'metadata' / 'book.json').write_text(json.dumps({
        'schema_version': 2, 'uuid': UUID_LIVRO, 'id': 'a-sociedade-do-anel', 'title': 'A Sociedade do Anel',
        'subtitle': None, 'original_title': 'The Fellowship of the Ring', 'authors': ['J. R. R. Tolkien'],
        'translators': ['Lenita Esteves'], 'series': 'O Senhor dos Anéis', 'series_index': 1, 'year': 2019,
        'language': 'pt-BR', 'publisher': 'HarperCollins Brasil', 'isbn': '9788595084759', 'page_count': None,
        'description': 'Primeira parte.', 'tags': ['fantasia'], 'google_books_id': None, 'audiobook_uuid': None,
        'cover': 'metadata/cover.jpg',
        'files': [{'file': 'a-sociedade-do-anel.epub', 'uuid': UUID_LIVRO[:-1] + '1'}]}), encoding='utf-8')
    colecao = raiz / 'collections' / 'terra-media'
    colecao.mkdir(parents=True)
    (colecao / 'collection.json').write_text(json.dumps({
        'schema_version': 2, 'uuid': UUID_COLECAO_LIVROS, 'id': 'terra-media', 'name': 'Terra-média',
        'description': None, 'tags': [], 'items': [UUID_LIVRO], 'files': []}), encoding='utf-8')
    st.api('POST', '/Library/VirtualFolders?name=Livros%20Bau&collectionType=books&refreshLibrary=false',
           {'LibraryOptions': st.opcoes_biblioteca(raiz, 'Books')}, servidor)
    antes = fotografar(raiz)
    escanear(servidor)
    return raiz, antes


def test_livro_le_o_book_json(servidor, livros):
    achados = st.api('GET', '/Items?Recursive=true&IncludeItemTypes=Book&Fields=ProviderIds,Overview,Tags,People,'
                            'Studios,OriginalTitle', token=servidor)['Items']
    livro = next(b for b in achados if b['ProviderIds'].get('Bau') == UUID_LIVRO)
    assert livro['Name'] == 'A Sociedade do Anel' and livro['OriginalTitle'] == 'The Fellowship of the Ring'
    assert livro['SeriesName'] == 'O Senhor dos Anéis' and livro['IndexNumber'] == 1
    assert livro['ProductionYear'] == 2019 and livro['Overview'] == 'Primeira parte.' and livro['Tags'] == ['fantasia']
    assert livro['ProviderIds'].get('ISBN') == '9788595084759'
    assert [s['Name'] for s in livro['Studios']] == ['HarperCollins Brasil']
    pessoas = {(p['Name'], p['Type']) for p in livro['People']}
    assert ('J. R. R. Tolkien', 'Author') in pessoas and ('Lenita Esteves', 'Translator') in pessoas
    assert livro['ImageTags'].get('Primary'), 'a capa (metadata/cover) não foi lida'


def test_livros_colecao_do_bau_e_pasta_collections_fora_da_estante(servidor, livros):
    colecoes = [c for c in itens(servidor, 'BoxSet') if c['ProviderIds'].get('Bau') == UUID_COLECAO_LIVROS]
    assert len(colecoes) == 1 and filhos(servidor, colecoes[0]['Id']) == {'A Sociedade do Anel'}
    biblioteca = id_da_biblioteca(servidor, 'Livros Bau')
    assert filhos(servidor, biblioteca) == {'j-r-r-tolkien'}


def test_varrer_livros_nao_grava_na_pasta(servidor, livros):
    raiz, antes = livros
    escanear(servidor)
    assert fotografar(raiz) == antes, 'a varredura mexeu na pasta dos livros'
