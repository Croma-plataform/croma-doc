"""Seções na barra lateral e abas do cabeçalho (só no desktop: o menu da TV é o módulo T03)."""
import pytest

TABS = '.MuiTabs-root [role="tab"]'


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV ainda usa o menu de bibliotecas do Jellyfin (módulo T03)')


def test_barra_lateral_lista_as_quatro_secoes(pagina, ir):
    ir('home')
    gaveta = pagina.locator('.MuiDrawer-root')
    textos = gaveta.inner_text()
    for secao in ('Audiovisual', 'Áudios', 'Leitura', 'Fotos'):
        assert secao in textos, secao


def test_secao_ativa_abre_os_subtipos(pagina, ir, biblioteca):
    filmes = biblioteca('Filmes')
    ir(f'movies?topParentId={filmes["id"]}&collectionType=movies&tab=1')
    gaveta = pagina.locator('.MuiDrawer-root').inner_text()

    for nome in ('Filmes', 'Séries', 'Documentários (filmes)', 'Documentários (séries)'):
        assert nome in gaveta, nome
    assert 'Músicas' not in gaveta      # os subtipos de Áudios só abrem na seção Áudios


def test_abas_do_cabecalho(pagina, ir, biblioteca):
    filmes = biblioteca('Filmes')
    ir(f'movies?topParentId={filmes["id"]}&collectionType=movies&tab=1')

    abas = [t.strip() for t in pagina.locator(TABS).all_inner_texts()]
    assert abas[0] == 'Resumo'
    assert abas[-2:] == ['Coleções', 'Gêneros']
    assert 'Filmes' in abas and 'Séries' in abas
    assert pagina.locator(TABS + '[aria-selected="true"]').inner_text().strip() == 'Resumo'


def test_aba_de_series_abre_a_grade_de_series(pagina, ir, biblioteca):
    filmes = biblioteca('Filmes')
    ir(f'movies?topParentId={filmes["id"]}&collectionType=movies&tab=1')

    pagina.locator(TABS, has_text='Séries').first.click()
    pagina.wait_for_url('**/tv?**')
    assert f'topParentId={biblioteca("Séries")["id"]}' in pagina.url


def test_clicar_na_secao_abre_a_primeira_biblioteca(pagina, ir):
    ir('home')
    pagina.locator('.MuiDrawer-root a', has_text='Audiovisual').first.click()
    pagina.wait_for_url('**/movies?**')


def test_visual_da_grade_de_filmes(pagina, ir, biblioteca, conferir):
    ir(f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=0')
    conferir('grade-filmes')


def test_cabecalho_mostra_o_comprimento_de_onda_e_as_contagens(pagina, ir, biblioteca):
    ir(f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=1')
    rotulo = pagina.locator('[data-testid="section-label"]')
    rotulo.wait_for()
    # as contagens chegam depois do primeiro desenho
    pagina.wait_for_function(
        "document.querySelector('[data-testid=section-label]').textContent.includes('·')")
    texto = rotulo.inner_text()
    assert texto.startswith('λ 580 nm'), texto
    assert 'FILMES' in texto.upper() and 'SÉRIES' in texto.upper()


@pytest.mark.parametrize('secao,biblio,rota,cor', [
    ('Audiovisual', 'Filmes', 'movies', 'rgb(192, 192, 0)'),
    ('Áudios', 'Músicas', 'music', 'rgb(0, 192, 0)'),
    ('Leitura', 'Livros', 'books', 'rgb(59, 59, 255)'),
    ('Fotos', 'Fotos', 'homevideos', 'rgb(192, 0, 192)'),
])
def test_cada_secao_tem_cabecalho_com_a_sua_cor(pagina, ir, biblioteca, secao, biblio, rota, cor):
    b = biblioteca(biblio)
    ir(f'{rota}?topParentId={b["id"]}&collectionType={rota}&tab=0')
    pagina.locator('[data-testid="section-label"]').wait_for()
    cabecalho = pagina.locator('[data-testid="section-label"]').locator('xpath=..')
    assert secao in cabecalho.inner_text()
    quadrado = cabecalho.locator('xpath=./div[2]/div[1]')
    assert quadrado.evaluate('e => getComputedStyle(e).backgroundColor') == cor


@pytest.mark.parametrize('secao,biblio,rota', [
    ('audiovisual', 'Filmes', 'movies'),
    ('audios', 'Músicas', 'music'),
    ('leitura', 'Livros', 'books'),
    ('fotos', 'Fotos', 'homevideos'),
])
def test_visual_do_cabecalho_de_cada_secao(pagina, ir, biblioteca, conferir, secao, biblio, rota):
    ir(f'{rota}?topParentId={biblioteca(biblio)["id"]}&collectionType={rota}&tab=0')
    pagina.wait_for_function(
        "(document.querySelector('[data-testid=section-label]')||{textContent:''}).textContent.includes('·')"
        " || document.querySelector('[data-testid=section-label]')")
    pagina.wait_for_timeout(600)
    # só o cabeçalho e a barra lateral: a grade abaixo carrega em ritmo variável
    conferir(f'cabecalho-{secao}', esconder=['.itemsContainer', '.listItem', '.alphaPicker', '.paging'])


def test_generos_sao_os_da_secao_inteira_com_contagem_por_subtipo(pagina, ir, biblioteca):
    ir(f'movies?topParentId={biblioteca("Filmes")["id"]}&collectionType=movies&tab=1')
    pagina.locator(TABS, has_text='Gêneros').click()
    pagina.locator('[data-testid="section-genre"]').first.wait_for()
    pagina.wait_for_function("document.querySelectorAll('[data-testid=section-genre]').length >= 3")

    linhas = {}
    for linha in pagina.locator('[data-testid="section-genre"]').all():
        nome = linha.locator('h2').inner_text().strip()
        linhas[nome] = linha.locator('.MuiTypography-caption').inner_text().strip().upper()

    assert set(linhas) == {'Ação', 'Documentário', 'Drama'}
    # Drama existe em Filmes (2) e em Documentários (filmes) (1): a contagem separa os subtipos
    assert linhas['Drama'] == '2 FILMES · 1 DOCUMENTÁRIOS'
    assert linhas['Ação'] == '2 FILMES'
