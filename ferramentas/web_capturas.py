"""Entra no Croma web com a conta de teste e captura telas.

Uso: python3 web_capturas.py <saida_dir> <rota>[|nome] ...
Rotas relativas a /web/#/ (ex.: home, "movies?topParentId=...").
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = 'http://localhost:8096/web/'
saida = Path(sys.argv[1])
saida.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1600, 'height': 1000})
    pg.goto(BASE + '#/login')
    pg.wait_for_timeout(3000)
    if pg.locator('#txtManualName').count() == 0 or not pg.locator('#txtManualName').is_visible():
        botao = pg.locator('.btnManual')
        if botao.count():
            botao.first.click()
            pg.wait_for_timeout(800)
    pg.fill('#txtManualName', 'teste')
    pg.fill('#txtManualPassword', '123')
    pg.locator('#txtManualPassword').press('Enter')
    pg.wait_for_timeout(4000)
    for arg in sys.argv[2:]:
        rota, _, nome = arg.partition('|')
        pg.goto(BASE + '#/' + rota)
        pg.wait_for_timeout(4000)
        destino = saida / ((nome or rota.split('?')[0].replace('/', '_')) + '.png')
        pg.screenshot(path=str(destino))
        print(destino)
    b.close()
