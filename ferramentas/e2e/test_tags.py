"""Tags (módulo D15): filtrar por duas tags (todas ou qualquer) e editar as tags de vários itens de uma vez."""
import pytest

pytestmark = pytest.mark.usuario('admin')

A = 'Barras Direto (2001)'
B = 'Barras Faixas (2003)'


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV usa a grade própria (módulo T04)')


def _definir_tags(api_admin, item_id, tags):
    completo = api_admin(f'Items/{item_id}')
    completo['Tags'] = tags
    api_admin(f'Items/{item_id}', completo, 'POST')


def _tags_de(api_admin, item_id):
    return api_admin(f'Items/{item_id}')


@pytest.fixture
def com_tags(api_admin, item):
    a, b = item('Movie', A), item('Movie', B)
    _definir_tags(api_admin, a, ['praia', 'família'])
    _definir_tags(api_admin, b, ['praia'])
    yield a, b
    for i in (a, b):
        _definir_tags(api_admin, i, [])


def _abrir_grade(pagina, ir, biblioteca):
    ir(f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=0')
    pagina.locator('.card').first.wait_for()


def _nomes(pagina):
    pagina.wait_for_timeout(1500)
    return {t.strip() for t in pagina.locator('.card .cardText-first').all_inner_texts()}


def test_filtrar_por_duas_tags_em_qualquer_ou_todas(pagina, ir, biblioteca, com_tags):
    _abrir_grade(pagina, ir, biblioteca)
    pagina.locator('button[title="Filtro"]').first.click()
    pagina.locator('#filtersTags-header').click()
    pagina.get_by_label('praia', exact=True).click()
    pagina.get_by_label('família', exact=True).click()
    pagina.wait_for_timeout(500)
    qualquer = _nomes(pagina)
    assert {'Barras Direto', 'Barras Faixas'} <= {n.split(' (')[0] for n in qualquer} or len(qualquer) == 2

    pagina.get_by_label('Ter todas as tags escolhidas').click()
    todas = _nomes(pagina)
    assert len(todas) == 1, f'com "todas" deveria sobrar só o filme com as duas tags: {todas}'


def test_editar_as_tags_de_dois_filmes_de_uma_vez(pagina, ir, biblioteca, api_admin, com_tags):
    a, b = com_tags
    _abrir_grade(pagina, ir, biblioteca)
    cartoes = pagina.locator('.card')
    # segurar o botão do mouse sobre um cartão liga a seleção; depois, cada clique escolhe um cartão
    caixa = cartoes.filter(has_text=A.split(' (')[0]).first.bounding_box()
    pagina.mouse.move(caixa['x'] + caixa['width'] / 2, caixa['y'] + caixa['height'] / 2)
    pagina.mouse.down()
    pagina.wait_for_timeout(800)
    pagina.mouse.up()
    pagina.locator('.btnSelectionPanelOptions').wait_for()
    cartoes.filter(has_text=B.split(' (')[0]).first.click()
    pagina.locator('.btnSelectionPanelOptions').click()
    pagina.get_by_text('Editar tags', exact=True).click()
    painel = pagina.locator('.cromaTagsEditor')
    painel.wait_for()
    # em comum aparece só "praia"
    assert [t.strip().rstrip('×').strip().lower() for t in painel.locator('.cromaTagChip').all_inner_texts()] == ['praia']
    painel.locator('.txtNewTag').fill('Viagem')
    painel.locator('.txtNewTag').press('Enter')
    painel.locator('.btnSaveTags').click()
    pagina.wait_for_selector('.cromaTagsEditor', state='detached', timeout=10000)

    for i, esperado in ((a, {'praia', 'família', 'viagem'}), (b, {'praia', 'viagem'})):
        completo = _tags_de(api_admin, i)
        assert set(completo['Tags']) == esperado
        assert 'Tags' in completo['LockedFields']
