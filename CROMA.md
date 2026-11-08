# Croma — documentação

Versão pessoal do Jellyfin com identidade visual própria. Foco inicial: **Desktop** e **TV Samsung QN90B (Tizen 6.5)**.

## Repositórios

O projeto é dividido em repositórios próprios, todos na organização [`Croma-plataform`](https://github.com/Croma-plataform) do GitHub. Este (`Croma-plataform/croma-doc`, público) é a **documentação**, o hub: visão geral, arquitetura e especificações. A pasta local do hub se chama `Croma-plataform`. Os demais são clonados **dentro da pasta do hub**, cada um com git próprio (ficam no `.gitignore` do hub).

| Pasta | Repositório (privado) | O que é | Branch |
|---|---|---|---|
| `croma-identidade/` | https://github.com/Croma-plataform/croma-identidade | Identidade visual (v0.1 "Barras" oficial), logos e scripts geradores | `main` |
| `croma-servidor/` | https://github.com/Croma-plataform/croma-servidor | Servidor (fork do servidor do Jellyfin), com scripts do Croma em `croma/` | `croma` |
| `croma-web/` | https://github.com/Croma-plataform/croma-web | Interface web compartilhada (fork do jellyfin-web) | `croma` |
| `croma-desktop/` | https://github.com/Croma-plataform/croma-desktop | App desktop (fork do jellyfin-desktop) | `croma` |
| `croma-tizen/` | https://github.com/Croma-plataform/croma-tizen | App da TV Samsung (fork do jellyfin-tizen) | `croma` |
| `croma-android/` | https://github.com/Croma-plataform/croma-android | App Android (fork do jellyfin-android); criado, ainda não implementado | `croma` |
| `croma-v1/` | https://github.com/Croma-plataform/croma-v1 | Croma v1, arquivado (referência para as tags) | `main` |
| `croma-org/` | https://github.com/Croma-plataform/.github (público) | Página de perfil da organização (`profile/README.md`) | `main` |

## Base de versões dos forks

| Fork | Origem (remote `upstream`) | Base | Commit da base |
|---|---|---|---|
| `croma-servidor` | https://github.com/jellyfin/jellyfin | tag `v12.4` | `83d0d0e7f7` |
| `croma-web` | https://github.com/jellyfin/jellyfin-web | `release-12.z` (v12.4) | `0a580ce8d` |
| `croma-tizen` | https://github.com/jellyfin/jellyfin-tizen | `master` | `31408c1` |
| `croma-desktop` | https://github.com/jellyfin/jellyfin-desktop | `master` | `51807f8` |
| `croma-android` | https://github.com/jellyfin/jellyfin-android | `master` (v2.7.1) | `6c5ab875` |

O GitHub Actions está desativado nos forks, para os workflows herdados do Jellyfin não rodarem.

Regra: a versão do web **sempre** casa com a do servidor (v12.4). Para atualizar: `git fetch upstream` + rebase da `croma`.

### Clonar os repositórios

Em uma máquina nova, clone o hub e, dentro dele, os demais:

```
git clone https://github.com/Croma-plataform/croma-doc.git Croma-plataform
cd Croma-plataform
git clone https://github.com/Croma-plataform/croma-identidade.git
git -c core.longpaths=true clone https://github.com/Croma-plataform/croma-servidor.git
git clone https://github.com/Croma-plataform/croma-v1.git
git clone https://github.com/Croma-plataform/croma-web.git
git clone https://github.com/Croma-plataform/croma-desktop.git
git clone https://github.com/Croma-plataform/croma-tizen.git
git clone https://github.com/Croma-plataform/croma-android.git
git clone https://github.com/Croma-plataform/.github.git croma-org

git -C croma-servidor remote add upstream https://github.com/jellyfin/jellyfin.git
git -C croma-web     remote add upstream https://github.com/jellyfin/jellyfin-web.git
git -C croma-desktop remote add upstream https://github.com/jellyfin/jellyfin-desktop.git
git -C croma-tizen   remote add upstream https://github.com/jellyfin/jellyfin-tizen.git
git -C croma-android remote add upstream https://github.com/jellyfin/jellyfin-android.git
```

- No Windows, rode também `git -C croma-servidor config core.longpaths true`: o código do servidor tem caminhos longos.
- O antigo clone de referência `jellyfin-server/` não é mais necessário: o código do servidor está no `croma-servidor`.
- Quase todos os repositórios são privados (só o `croma-doc` e o `.github` são públicos): o `git clone` pede login no GitHub (`gh auth login` resolve).

### Servidor local

O passo a passo (compilar o servidor com o .NET SDK 10, ou usar o binário oficial na transição, build do `croma-web` e script de inicialização) fica no [`croma/README.md` do `croma-servidor`](https://github.com/Croma-plataform/croma-servidor/blob/croma/croma/README.md).

### Outros repositórios de referência

| Repositório | Para quê |
|---|---|
| https://github.com/jellyfin/jellyfin-androidtv | App de Android TV (fase futura) |
| https://github.com/jellyfin/jellyfin-vue | Cliente web alternativo (não usado: não tem layout de TV) |
| https://github.com/jellyfin/jellyfin-ffmpeg | FFmpeg usado pelo servidor |
| https://github.com/jellyfin/jellyfin-kodi | Integração com o Kodi |
| https://github.com/jellyfin/jellyfin.org | Site e documentação oficial |
| https://github.com/awesome-jellyfin/awesome-jellyfin | Lista de plugins, temas e clientes da comunidade |

## Arquitetura

```
croma-identidade  ← fonte da verdade da marca (manual, logos, ícones)
   │  arquivos copiados para:
   ▼
croma-web (fork do jellyfin-web)  ← a identidade aplicada na interface mora aqui
   ├─ build → croma-servidor serve via --webdir → croma-desktop (carrega a UI do servidor) + navegador
   ├─ build → croma-tizen empacota o dist/ → .wgt na TV
   └─ (futuro) croma-android carrega a UI do servidor numa WebView
```

## Mapa do croma-web (onde mexer)

- **Tema Croma (padrão):** `src/themes/croma/index.ts` (MUI) e `src/themes/croma/theme.scss` (paleta, cores das bibliotecas, cantos vivos, foco); registrado em `src/themes/index.ts` e marcado como padrão em `src/config.json` → `themes[]`
- **Paleta base do Jellyfin:** `src/themes/_base/_palette.scss` (ainda `#00a4dc`; o tema Croma sobrescreve) e `src/themes/_base/theme.ts`
- **Fontes:** `src/styles/fonts.croma.scss` (Archivo Variable e IBM Plex Mono, empacotadas pelo npm)
- **Logos e ícones:** `src/assets/img/croma/` (cópias do `croma-identidade`); usados em `src/styles/site.scss`, `src/themes/_base/_theme.scss`,
  `src/apps/modern/components/drawers/DrawerHeaderLink.tsx`, `src/components/toolbar/ServerButton.tsx`,
  `src/plugins/logoScreensaver/plugin.js`
- **Nome do app:** `src/index.html` (`<title>`, `application-name`), `src/manifest.json`, strings em `src/strings/` (pt-br, pt-pt, pt e en-us já dizem "Croma")
- **Seções (08/11/2026):**
  - `src/apps/modern/features/sections/sections.ts`: seções, cores, ícones e agrupamento das bibliotecas;
  - `src/apps/modern/components/drawers/SectionLinks.tsx`: seções na barra lateral;
  - `src/apps/modern/features/sections/components/SectionTabs.tsx`: cabeçalho e abas, usado pelo `LibraryViewMenu.tsx` quando a biblioteca tem seção;
  - `src/apps/modern/features/libraries/constants/libraryRoutes.ts`: o Resumo (Sugestões) é a aba padrão dos filmes.
- **Edição do filme:** `src/utils/editions.ts` (lista e `getEdition`); etiqueta nos cartões em `components/cardbuilder/Card/` (`badge` na linha do ano) e em `cardBuilder.js`; no detalhe, `renderName` em `apps/legacy/controllers/itemDetails/index.js`; estilos `.cardEdition` (`card.scss`) e `.detailEdition` (`themes/croma/theme.scss`). A tag precisa vir na lista: o campo `Tags` foi pedido em `utils/items.ts`, `SuggestionsSectionView.tsx` e nas seções `resume`/`recentlyAdded`
- **Detalhe do item:** ainda é o controller legado `apps/legacy/controllers/itemDetails/` (index.html e index.js, 2.200 linhas); mudanças pequenas e isoladas
- **Layouts:** `src/apps/modern` (React, desktop) e `src/apps/legacy` (controllers antigos, inclusive vários usados no modo TV)
- **Modo TV:** classe `.layout-tv` (CSS) + `layoutManager.tv` (JS). Testar toda mudança visual nesse modo

## Ferramentas

- [`ferramentas/web_capturas.py`](ferramentas/web_capturas.py): entra no Croma web com a conta de teste e salva capturas de tela (Playwright). Uso: `python3 ferramentas/web_capturas.py <pasta> "<rota>|<nome>" ...`. Para capturar é preciso o servidor no ar e o build do `croma-web`.
- **Build do `croma-web` no Linux:** o `node` do sistema ainda é o 22. Sem trocar o pacote, crie links temporários (`ln -sf /usr/bin/node-24 <pasta>/node` e o mesmo para `npm-24`), ponha a pasta no começo do `PATH` e rode `npm run build:production` (leva de 1 a 2 minutos). Lint e tipos: `npx eslint <caminhos>` e `npx tsc --noEmit`.

## Mapa das cascas

- **Tizen:** `config.xml` (nome, ids `AprZAARz4r.Jellyfin`, `widget id`), `icon.png`
- **Desktop:** `CMakeModules/NameConfiguration.cmake`, `resources/images`, `native/find-webclient.*` (tela de conexão),
  `bundle/win/JellyfinDesktop.iss.in` (instalador Windows)
- **Android:** `app/build.gradle.kts` (`namespace = "org.jellyfin.mobile"`), `app/src/main/res/values/strings_donottranslate.xml` (`app_name`), ícones em `app/src/main/res/mipmap-*`

Nenhuma casca foi alterada ainda: as três seguem com nome, ids e ícones do Jellyfin.

## Plano de desenvolvimento

O roteiro (onde estamos, fases e decisões pendentes) fica em [`PLANO.md`](PLANO.md).

## Especificações

| Arquivo | Assunto | Situação |
|---|---|---|
| [`specs/colecoes.md`](specs/colecoes.md) | Coleções por biblioteca e modo de exibição | Especificado, não implementado |
| [`specs/tags.md`](specs/tags.md) | Tags e editor de tags vindos do v1 | Avaliado, com decisões em aberto |
| [`specs/secoes.md`](specs/secoes.md) | Seções Audiovisual, Áudios e Leitura; TV ao vivo fora do escopo | Estrutura decidida (07/11/2026); cores e detalhes em aberto |
| [`specs/varredura-bau.md`](specs/varredura-bau.md) | Leitura do padrão Baú (acervo do usuário, DL_HERMES): metadados, imagens, legendas e coleções | Filmes implementado (08/11/2026) |
| [`specs/bibliotecas-caseiras.md`](specs/bibliotecas-caseiras.md) | Varredura estruturada (níveis) de Vídeos e Fotos | Formato em desenvolvimento pelo usuário |

## Identidade visual

A identidade oficial é a **v0.1 "Barras"**, decidida em 05/11/2026, e mora no [`croma-identidade`](https://github.com/Croma-plataform/croma-identidade). O manual é `croma-identidade/v0.1-barras/MANUAL.md`, e os arquivos prontos para uso ficam em `croma-identidade/v0.1-barras/logos/` (logotipo, símbolo, ícones das bibliotecas e `app/` com os ícones de cada plataforma). A v0.2 "CAPRA" fica arquivada no mesmo repositório.

Canvas com todas as pranchas: https://claude.ai/artifact/AUKTY2yvnHh4ZYk1c7qpLi (páginas "v0.1 Barras" e "v0.2 Direções CAPRA").
