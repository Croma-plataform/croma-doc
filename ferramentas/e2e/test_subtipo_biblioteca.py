"""Editar o subtipo de uma biblioteca que já existe, pela tela do painel (conta admin)."""
import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.usuario('admin')


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('o painel de administração não é usado na TV')


def abrir_editor(pagina, ir, nome, subtipo_atual):
    """Abre o editor da biblioteca e espera o campo mostrar o subtipo dela: ele só é preenchido depois de buscar o
    catálogo, e uma escolha feita antes disso seria desfeita."""
    ir('dashboard/libraries')
    pagina.locator('.MuiCard-root', has_text=nome).locator('[data-testid="MoreVertIcon"]').click()
    pagina.get_by_role('menuitem', name='Gerenciar biblioteca').click()
    expect(pagina.locator('#selectLibrarySubtype')).to_have_value(subtipo_atual)


def salvar(pagina):
    pagina.get_by_role('button', name='OK').click()
    pagina.locator('#selectLibrarySubtype').wait_for(state='detached')
    pagina.wait_for_timeout(1000)


def test_editor_mostra_o_subtipo_e_so_oferece_os_compativeis(pagina, ir):
    abrir_editor(pagina, ir, 'Mangás', 'Manga')
    opcoes = [o.strip() for o in pagina.locator('#selectLibrarySubtype option').all_inner_texts()]
    # biblioteca de livros: livros, HQs, mangás, podcasts e audiolivros; nada de filmes ou músicas
    assert set(opcoes) == {'Livros', 'HQs', 'Mangás', 'Podcasts', 'Audiolivros'}


def test_trocar_o_subtipo_muda_a_secao_e_a_aba_na_interface(pagina, ir):
    """Mangás vira HQs e volta: o editor mostra o novo valor e as abas de Leitura acompanham."""
    abrir_editor(pagina, ir, 'Mangás', 'Manga')
    pagina.locator('#selectLibrarySubtype').select_option(value='Comics')
    salvar(pagina)
    try:
        abrir_editor(pagina, ir, 'Mangás', 'Comics')
        pagina.keyboard.press('Escape')

        ir('home')
        pagina.locator('.MuiDrawer-root a', has_text='Leitura').first.click()
        pagina.wait_for_timeout(1500)
        # duas bibliotecas de HQs: as abas se distinguem pelo nome da biblioteca
        abas = [t.strip() for t in pagina.locator('.MuiTabs-root [role="tab"]').all_inner_texts()]
        assert 'Mangás' in abas and 'HQs' in abas
    finally:
        abrir_editor(pagina, ir, 'Mangás', 'Comics')
        pagina.locator('#selectLibrarySubtype').select_option(value='Manga')
        salvar(pagina)


def test_criar_biblioteca_escolhe_a_secao_e_depois_o_tipo(pagina, ir):
    """O diálogo de criar pergunta a seção e depois o tipo dela; o tipo do Jellyfin e o subtipo saem dessa escolha."""
    ir('dashboard/libraries')
    pagina.get_by_role('button', name='Adicionar Biblioteca de Mídia').click()
    secao = pagina.locator('#selectLibrarySection')
    tipo = pagina.locator('#selectLibraryKind')
    expect(secao.locator('option', has_text='Leitura')).to_have_count(1)
    opcoes = [o.strip() for o in secao.locator('option').all_inner_texts() if o.strip()]
    assert opcoes == ['Audiovisual', 'Áudios', 'Leitura', 'Fotos']
    expect(tipo).to_be_disabled()
    # o campo de subtipo do editor de opções não aparece: a escolha é a de cima
    expect(pagina.locator('.dlg-librarycreator .fldLibrarySubtype')).to_be_hidden()

    secao.select_option(label='Áudios')
    opcoes = [o.strip() for o in tipo.locator('option').all_inner_texts() if o.strip()]
    assert opcoes == ['Músicas', 'Podcasts', 'Audiolivros']
    expect(pagina.locator('.dlg-librarycreator .libraryOptions')).to_be_hidden()

    tipo.select_option(label='Podcasts')
    expect(pagina.locator('#txtValue')).to_have_value('Podcasts')
    expect(pagina.locator('.dlg-librarycreator .libraryOptions')).to_be_visible()
    # podcasts são uma biblioteca de livros no Jellyfin: sem as opções de vídeo
    expect(pagina.locator('.dlg-librarycreator .trickplaySettingsSection')).to_be_hidden()

    secao.select_option(label='Fotos')
    expect(tipo).to_have_value('Photos')
    expect(pagina.locator('#txtValue')).to_have_value('Fotos')
    pagina.keyboard.press('Escape')
