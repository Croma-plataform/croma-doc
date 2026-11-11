"""O catálogo do servidor (`GET /Library/Subtypes`) e as seções do web têm de dizer a mesma coisa."""
import json
import re
import urllib.request
from pathlib import Path

import pytest

WEB = Path(__file__).resolve().parents[2] / 'croma-web' / 'src'
AUTH = 'MediaBrowser Client="croma-teste", Device="teste", DeviceId="croma-catalogo", Version="1"'


@pytest.fixture(scope='module')
def catalogo(base):
    def chamar(caminho, corpo=None, token=None):
        pedido = urllib.request.Request(
            f'{base.removesuffix("web/")}{caminho}', data=json.dumps(corpo).encode() if corpo else None,
            headers={'Content-Type': 'application/json',
                     'Authorization': AUTH + (f', Token="{token}"' if token else '')})
        with urllib.request.urlopen(pedido) as r:
            return json.load(r)

    token = chamar('Users/AuthenticateByName', {'Username': 'leitor', 'Pw': 'teste'})['AccessToken']
    return chamar('Library/Subtypes', token=token)


def valores_do_enum(nome):
    """Os valores de um `enum` de `types/librarySubtype.ts`."""
    texto = (WEB / 'types' / 'librarySubtype.ts').read_text()
    corpo = re.search(rf'enum {nome} \{{(.*?)\}}', texto, re.S).group(1)
    return re.findall(r"=\s*'(\w+)'", corpo)


def test_os_subtipos_do_web_sao_os_do_servidor(catalogo):
    assert valores_do_enum('LibrarySubtype') == [i['Subtype'] for i in catalogo]


def test_as_secoes_do_web_sao_as_do_servidor(catalogo):
    do_servidor = []
    for info in catalogo:
        if info['Section'] not in do_servidor:
            do_servidor.append(info['Section'])
    assert valores_do_enum('LibrarySection') == do_servidor


def test_as_barras_seguem_a_ordem_das_secoes(catalogo):
    texto = (WEB / 'apps/modern/features/sections/sections.ts').read_text()
    ordem = re.findall(r'section: LibrarySection\.(\w+), labelKey', texto)
    assert [s.lower() for s in ordem] == [s.lower() for s in dict.fromkeys(i['Section'] for i in catalogo)]


def test_todo_subtipo_tem_icone_e_nome_em_portugues(catalogo):
    sections = (WEB / 'apps/modern/features/sections/sections.ts').read_text()
    nomes = json.loads((WEB / 'strings/pt-br.json').read_text())
    for info in catalogo:
        sub = info['Subtype']
        assert f'[LibrarySubtype.{sub}]' in sections or sub == 'Photos', f'{sub} sem ícone na barra lateral'
        assert f'LibrarySubtype{sub}' in nomes, f'{sub} sem nome em pt-br'
