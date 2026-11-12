"""Próximo episódio no player (prancha 37)."""
import pytest

pytestmark = pytest.mark.usuario('tocador')

# O único episódio com mais de 10 min (exigência do Jellyfin para mostrar o cartão); o próximo é o T2 E01
PRIMEIRO = 'Serie de Teste - S01E03 - Episodio 3'


@pytest.fixture(autouse=True)
def so_desktop(layout):
    if layout == 'tv':
        pytest.skip('a TV entra no módulo T05')


def _perto_do_fim(pagina):
    pagina.evaluate('() => { const v = document.querySelector("video"); v.currentTime = Math.max(0, v.duration - 35); }')


def test_cartao_do_proximo_episodio_aparece_com_codigo_e_foco(pagina, tocar):
    tocar('Episode', PRIMEIRO)
    _perto_do_fim(pagina)
    cartao = pagina.locator('.upNextContainer:not(.hide):not(.upNextDialog-hidden)')
    cartao.wait_for(timeout=20000)
    assert 'T2 E01' in cartao.locator('.upNextDialog-kicker').inner_text().upper()
    pagina.wait_for_function('document.activeElement && document.activeElement.classList.contains("btnStartNow")')
    assert cartao.locator('.upNextDialog-countdown').get_attribute('aria-valuenow') is not None


def test_assistir_agora_abre_o_proximo_episodio(pagina, tocar):
    tocar('Episode', PRIMEIRO)
    _perto_do_fim(pagina)
    pagina.locator('.upNextContainer .btnStartNow').click(timeout=20000)
    pagina.wait_for_function(
        '() => { const t = document.querySelector(".cromaOsdTitle"); return t && t.textContent.includes("Episodio 1"); }',
        timeout=30000)


def test_ocultar_cancela_a_contagem(pagina, tocar):
    tocar('Episode', PRIMEIRO)
    _perto_do_fim(pagina)
    pagina.locator('.upNextContainer .btnHide').click(timeout=20000)
    pagina.wait_for_selector('.upNextContainer.upNextDialog-hidden', state='attached')
    pagina.wait_for_function("() => getComputedStyle(document.querySelector('.upNextContainer')).opacity === '0'")


def test_pular_abertura_aparece_em_foco_e_some_1_s_depois_do_fim(pagina, ir, item):
    """As marcações vêm do servidor (S05): aqui a resposta é simulada com uma abertura de 2 s a 5 s."""
    id_ep = item('Episode', 'Serie de Teste - S02E01 - Episodio 1')
    segmento = {'Items': [{'Id': 'a' * 32, 'ItemId': id_ep, 'Type': 'Intro',
                           'StartTicks': 2 * 10_000_000, 'EndTicks': 5 * 10_000_000}], 'TotalRecordCount': 1}
    pagina.route('**/MediaSegments/**', lambda rota: rota.fulfill(json=segmento))

    def com_segmentos(rota):
        resposta = rota.fetch()
        corpo = resposta.json()
        for fonte in corpo.get('MediaSources', []):
            fonte['HasSegments'] = True
        rota.fulfill(response=resposta, json=corpo)
    pagina.route('**/PlaybackInfo*', com_segmentos)
    ir(f'details?id={id_ep}')
    pagina.locator('#itemDetailPage:not(.hide) .btnPlay').first.click()
    botao = pagina.locator('.skip-button:not(.hide):not(.skip-button-hidden)')
    botao.wait_for(timeout=30000)
    assert 'Pular' in botao.inner_text()
    pagina.wait_for_function('document.activeElement && document.activeElement.classList.contains("skip-button")')
    # pular leva ao fim da abertura
    botao.click()
    pagina.wait_for_function('document.querySelector("video").currentTime >= 5')
    pagina.wait_for_selector('.skip-button-hidden, .skip-button.hide', state='attached', timeout=8000)
