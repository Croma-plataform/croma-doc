"""Testes do script de tags do v1 (a parte pura: ler os JSON e casar com os itens)."""
import json

import tags_v1 as t


def _v1(tmp_path):
    album = tmp_path / 'Viagem'
    (album / 'metadados').mkdir(parents=True)
    (album / 'metadados' / 'colecao.json').write_text(
        json.dumps({'titulo': 'Viagem', 'tags': [' praia ', 'Praia', 'família', '']}), encoding='utf-8-sig')
    (album / 'metadados' / 'fotos.json').write_text(
        json.dumps({'versao': 1, 'fotos': {'Dia1\\IMG_1.jpg': {'tags': ['pôr do sol'], 'tamanho': 10},
                                           'IMG_2.jpg': {'tags': [], 'tamanho': 5}}}), encoding='utf-8')
    return album


def test_normaliza_sem_repetir_nem_vazias():
    assert t.normalizar_tags([' praia ', 'Praia', '', 'família']) == ['praia', 'família']
    assert t.normalizar_tags(None) == []


def test_le_as_tags_do_album_e_das_fotos(tmp_path):
    album = _v1(tmp_path)
    lido = t.ler_tags_do_v1(tmp_path)
    assert lido[str(album)] == ['praia', 'família']
    assert lido[str(album / 'Dia1/IMG_1.jpg')] == ['pôr do sol']
    assert str(album / 'IMG_2.jpg') not in lido          # foto sem tags não entra


def test_ignora_json_quebrado(tmp_path):
    pasta = tmp_path / 'A' / 'metadados'
    pasta.mkdir(parents=True)
    (pasta / 'colecao.json').write_text('{lixo', encoding='utf-8')
    assert t.ler_tags_do_v1(tmp_path) == {}


def test_junta_sem_perder_as_que_o_item_ja_tem():
    assert t.juntar_tags(['minha'], ['praia', 'Minha']) == ['minha', 'praia']


def test_planeja_pelo_caminho_e_conta_o_que_nao_achou():
    itens = [{'Id': '1', 'Path': '/fotos/A/f.jpg', 'Tags': ['x']}, {'Id': '2', 'Path': '/fotos/A/g.jpg', 'Tags': ['y']}]
    v1 = {'/fotos/A/f.jpg': ['y'], '/fotos/A/g.jpg': ['y'], '/fotos/B/h.jpg': ['z']}
    gravar, sem_item = t.planejar(itens, v1)
    assert [(i['Id'], tags) for i, tags in gravar] == [('1', ['x', 'y'])]      # o 2 já tinha 'y': nada a fazer
    assert sem_item == ['/fotos/B/h.jpg']
