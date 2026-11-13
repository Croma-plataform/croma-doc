"""Início (módulo D08)."""
import pytest


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV entra no módulo T05')


def test_visual_do_inicio(pagina, ir, conferir):
    ir('home', espera=3000)
    conferir('inicio')


@pytest.mark.usuario('tocador')
def test_inicio_nao_repete_minha_midia(pagina, ir):
    ir('home', espera=3000)
    titulos = ' '.join(pagina.locator('.sectionTitle, .sectionTitle-cards').all_inner_texts())
    assert 'Minha mídia' not in titulos


@pytest.mark.usuario('admin')
def test_cartoes_da_tela_inicial_mostram_o_rotulo_de_tipo_na_cor_da_secao(pagina, ir, item, api_admin):
    """Com o primeiro episódio visto, "A seguir" mostra o próximo com o rótulo SÉRIE · NOME · T1 E02."""
    ident = item('Episode', 'Serie de Teste - S01E01 - Episodio 1')
    uid = api_admin.uid
    api_admin(f'Users/{uid}/PlayedItems/{ident}', None, 'POST')
    try:
        ir('home', espera=3000)
        rotulo = pagina.locator('[data-testid="type-label"]').first
        rotulo.wait_for()
        assert rotulo.inner_text().upper() == 'SÉRIE · SERIE DE TESTE · T1 E02'
        assert rotulo.evaluate('e => getComputedStyle(e).color') == 'rgb(192, 192, 0)'    # Audiovisual
    finally:
        api_admin(f'Users/{uid}/PlayedItems/{ident}', None, 'DELETE')


def test_novidades_seguem_a_ordem_das_secoes(pagina, ir):
    ir('home', espera=3000)
    titulos = [t.strip() for t in pagina.locator('.sectionTitle').all_inner_texts()]
    ordem = [t for t in titulos if t.endswith('recentes') or t.endswith('recentemente')]
    ordem = [t for t in ordem if any(n in t for n in ('Filmes', 'Séries', 'Músicas', 'Livros', 'Fotos'))]
    assert ordem, titulos
    posicao = {nome: i for i, t in enumerate(ordem) for nome in ('Filmes', 'Séries', 'Músicas', 'Livros', 'Fotos') if nome in t}
    sequencia = [posicao[n] for n in ('Filmes', 'Séries', 'Músicas', 'Livros', 'Fotos') if n in posicao]
    assert sequencia == sorted(sequencia), ordem


def test_item_sem_arte_na_tela_inicial_tem_capa_gerada(pagina, ir):
    ir('home', espera=3000)
    assert pagina.locator('.card [data-testid="generated-cover"]').count() >= 1


def test_opcoes_da_tela_inicial_sem_as_fileiras_que_sairam(pagina, ir, layout, api_admin):
    """Ajustes › Tela inicial: sem TV ao vivo, e sem "Minha mídia" no desktop (a TV mantém a fileira)."""
    uid = next(u['Id'] for u in api_admin('Users') if u['Name'] == 'leitor')
    ir(f'mypreferenceshome?userId={uid}', espera=2500)
    valores = set(pagina.locator('select[id^="selectHomeSection"] option').evaluate_all('os => os.map(o => o.value)'))
    assert valores, 'a página de ajustes da tela inicial não carregou'
    assert not valores & {'livetv', 'activerecordings'}
    if layout == 'tv':
        assert {'smalllibrarytiles', 'librarybuttons'} <= valores
    else:
        assert not valores & {'smalllibrarytiles', 'librarybuttons'}
