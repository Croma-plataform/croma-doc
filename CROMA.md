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
  - `src/apps/modern/features/sections/components/SectionTabs.tsx`: cabeçalho e abas (Resumo, uma aba por biblioteca da seção, Coleções, Gêneros), usado pelo `LibraryViewMenu.tsx` quando a biblioteca tem seção; a grade aberta por cada tipo de biblioteca está em `getSubtypeTabs` (`sections.ts`);
  - `src/apps/modern/features/libraries/constants/libraryRoutes.ts`: o Resumo (Sugestões) é a aba padrão dos filmes.
  - `src/apps/modern/features/sections/summary.ts`, `hooks/useSectionSummary.ts` e `components/SectionSummaryView.tsx`: o Resumo da seção, que junta as bibliotecas; o `PageTabContent.tsx` usa ele no lugar das sugestões quando a biblioteca tem seção.
- **Edição do filme:** `src/utils/editions.ts` (lista e `getEdition`); etiqueta nos cartões em `components/cardbuilder/Card/` (`badge` na linha do ano) e em `cardBuilder.js`; no detalhe, `renderName` em `apps/legacy/controllers/itemDetails/index.js`; estilos `.cardEdition` (`card.scss`) e `.detailEdition` (`themes/croma/theme.scss`). A tag precisa vir na lista: o campo `Tags` foi pedido em `utils/items.ts`, `SuggestionsSectionView.tsx` e nas seções `resume`/`recentlyAdded`
- **Fita de episódios (série):** `src/components/croma/episodeStrip/` (modelo, HTML e estilo, com testes); chamada por `renderEpisodeStrip` no detalhe (`apps/legacy/controllers/itemDetails/index.js`), que também põe o kicker (`.detailKicker`, em `themes/croma/theme.scss`). "Novo" é o episódio adicionado depois da última vez que o usuário assistiu à série. Cores das seções em variáveis `--croma-audiovisual` etc. (`theme.scss`)
- **Cabeçalho do detalhe (prancha 28):** `src/components/croma/itemDetail/` (`detailHeader.ts` com o kicker do filme e o progresso "parou em · faltam", com testes; `itemDetail.scss`). O controller põe a classe `cromaDetail` na página dos itens do Audiovisual (filme, série, temporada, episódio, vídeo) e o estilo vale só nela: informações em cima e botões embaixo, "Assistir" em Fósforo, "Do início" e "Trailer" em Grafite (rótulos `.detailButton-label` no `index.html`), as outras ações em quadrados Grafite e o pôster flutuando com `margin-right: -25vw` (como o Jellyfin já faz na TV), senão o bloco de informações encolhe. A sinopse tem uma segunda cópia (`.detailOverview`) no bloco de informações, preenchida pelo mesmo `renderOverview`; o CSS mostra uma ou outra. O progresso é desenhado em `renderResumeProgress`, chamado por `reloadPlayButtons` (atualiza quando os dados do usuário mudam)
- **Faixa de baixo do filme (prancha 28):** `src/components/croma/itemDetail/detailFooter.ts` (ficha técnica, arquivo e modo de reprodução, com testes) e o bloco `.detailFooter` no topo do `detailPageSecondaryContainer` (`index.html`). No controller, `renderDetailFooter` (chamado em `reloadFromItem`; põe a classe `cromaFooter`, que esconde a lista de diretor e estúdios do Jellyfin), `renderFileSheet` (versão selecionada; o "● Reprodução direta neste aparelho" vem do `playbackManager.getPlaybackMediaSources`, o PlaybackInfo com o perfil do aparelho, que não toca nem converte nada) e `renderSimilarInLibrary` (4 pôsteres pelo `cardBuilder`, no lugar do "Mais como este"). Só filmes, por enquanto (`hasDetailFooter`). A classe `cromaFooter` também esconde os campos de Vídeo, Áudio e Legendas (eles continuam na página, porque o Assistir lê os valores; a versão continua visível). Na TV, `onMainButtonsCommand` (via `inputManager.on`) leva o ↓ dos botões aos Parecidos; sem isso a navegação espacial pula para o Elenco. O Chromium do Playwright não tem H.264, então nas capturas aparece "Vídeo convertido pelo servidor"
- **Player (pranchas 11 e 12):** `src/components/croma/videoOsd/` (`videoOsd.ts` com o kicker, os tempos, o capítulo e os chips, com testes; `videoOsd.scss`). No controller `apps/legacy/controllers/playback/video/index.js`: `renderCromaOsdHeading` (põe a classe `cromaOsd` na página para filme, episódio e vídeo, e `cromaOsdHeader` no cabeçalho, que esconde o relógio da TV), `renderCromaOsdChips` (chamado em `updatePlayerStateInternal`) e `renderCromaOsdTimes` (no fim de `updateTimeDisplay`); o título sai do cabeçalho (evento `VIDEO_TITLE_CHANGE` vazio). O bloco de cima (`.cromaOsdTop`) fica dentro do `.videoOsdBottom` com `position: fixed`, para aparecer e sumir junto. A linha do tempo em espectro é só CSS: o gradiente no trilho e a sombra de 100vw do trecho assistido (`.mdl-slider-background-lower`), recortada pelo trilho, cobre o resto com Sinal a 78%. O balão da busca mostra "tempo · Capítulo N", sem miniatura (trickplay não é gerado: pode gravar no acervo). Para testar: `ferramentas` não tem script do player; o Chromium do Playwright toca convertendo (sem H.264). **Carregando (prancha 38):** os eventos `waiting` e `playing` do player (`onCromaWaiting`, que mostra a tela depois de 300 ms, e `onCromaPlaying`); `fetchCromaTranscoding` pede ao servidor a sessão deste aparelho (`TranscodingInfo`, no máximo a cada 10 s) para os chips "2160p → 1080p" e "DTS-HD MA → AAC 5.1" e para o motivo da conversão (`getTranscodeReasonText`). Sem porcentagem: o `CompletionPercentage` do servidor é até onde ele converteu no arquivo, não o progresso da espera. O trecho já carregado é o `.cromaOsdLoaded` (o espectro inteiro recortado com `clip-path` entre a posição e o fim do trecho carregado, com `brightness(0.5)`), com as variáveis `--cromaOsd-loaded-start` e `--cromaOsd-loaded-end` postas em `renderCromaOsdTimes`. A varredura usa `mask-image`, que o build prefixa (`-webkit-`) para o Chromium 85
- **Painel de legendas e áudio (prancha 36):** `src/components/croma/trackPanel/` (`trackPanel.ts` com as listas, as etiquetas e o estilo da legenda, com testes; `trackPanelDialog.js` abre o painel; `trackPanel.scss`). É um diálogo do `dialogHelper` em tela cheia com fundo transparente: o player ignora as teclas enquanto ele está aberto, o foco fica dentro e Voltar fecha (no desktop, o Esc é tratado no próprio painel). Os botões de legenda e de áudio do OSD abrem o painel quando a página tem `cromaOsd` (`showCromaTrackPanel` no controller do player). O vídeo pausa e volta a tocar ao fechar; a classe `cromaTrackPanelOpen` no `body` esconde o OSD e o cabeçalho e leva a legenda para a parte visível. Tamanho e fundo gravam nas configurações de aparência de legenda do Jellyfin (`textSize`, `dropShadow`, `textBackground`; ficam no aparelho) e a legenda externa é reaplicada para mudar na hora. O atraso só aparece quando o Jellyfin consegue deslocar a legenda atual (legenda externa)
- **Componentes comuns do Croma (D02 em diante, `src/components/croma/`):** cada pasta tem o modelo em `.ts` (testado ao lado, `.test.ts`) e o estilo:
  - `states/`: carregando em esqueleto (`CardSkeletons`), vazio (`EmptyState`), erro com tentar de novo (`retry.ts`) e "sem sinal" (`NoSignal`, prancha 38);
  - `generatedCover/`: a capa gerada para itens sem arte;
  - `typeLabel/`: a etiqueta de tipo nos cartões; `avatar/`: o avatar do usuário; `toast/`: a fila de avisos;
  - `analyzer/` (analisador de espectro do player de áudio), `upNext/` (próximo episódio), `skip/` (pular abertura), `screensaver/` (descanso de tela), `quickConnect/` (código e validade do Quick Connect);
  - `collectionDisplay/` (D10): formato do cartão da coleção (pôster ou miniatura), a ordem da arte de reserva e o seletor "Exibir como" (`displaySwitch.ts`).
- **Funcionalidades (`src/apps/modern/features/`):** `calibration/` (calibração de tela, D17), `search/` (agrupamento dos resultados e atalho `Ctrl K`, D09), `photos/` (grade justificada e meses, D14), `preferences/` (ajustes: `SegmentedField`, `StepperField`, `CalibrationRow`, D17), `sections/` (seções, Resumo, Documentários e gêneros agrupados), `libraries/` (grade e abas), `details/` (detalhe).
- **Coleções por biblioteca (D10, 13/11/2026):**
  - a lista da aba Coleções vem de `GET /Collections?ownerLibraryId=` (`hooks/useFetchItems.ts`, caso `LibraryTab.Collections`);
  - "Nova coleção" (`NewCollectionButton.tsx`) e "Adicionar à coleção" (`components/collectionEditor/collectionEditor.js`) usam o dono; este lista só as coleções da biblioteca do item (`GET /Collections?itemId=`);
  - a biblioteca "Coleções" global some das visões do usuário em `hooks/api/userViewsFilter.ts`;
  - o formato da aba vem da biblioteca (`CollectionsUseThumbnails`, caixa no editor de bibliotecas, `libraryoptionseditor`) e o da coleção, do seletor na página dela (`itemDetails/index.js`, `renderCollectionDisplaySwitch`).
- **Entrada e conta (D16):** o Quick Connect em `apps/legacy/controllers/session/login/index.js` (`showQuickConnectCode`).
- **Chromium 85 (TV):** nada de `inset` (Chrome 87), `:not(a, b)` com lista nem `aspect-ratio` (Chrome 88); o `gap` em flex funciona (Chrome 84)
- **Detalhe do item:** ainda é o controller legado `apps/legacy/controllers/itemDetails/` (index.html e index.js, 2.200 linhas); mudanças pequenas e isoladas
- **Layouts:** `src/apps/modern` (React, desktop) e `src/apps/legacy` (controllers antigos, inclusive vários usados no modo TV)
- **Modo TV:** classe `.layout-tv` (CSS) + `layoutManager.tv` (JS). Testar toda mudança visual nesse modo

## Ferramentas

Tudo em [`ferramentas/`](ferramentas/). O módulo D00 do plano explica a ideia; aqui está como usar.

| Arquivo | Para quê |
|---|---|
| [`verificar.sh`](ferramentas/verificar.sh) | **Um comando verifica tudo:** lint, estilo, tipos, testes e build do `croma-web`; testes e formatação do `croma-servidor`; testes de ponta a ponta. `--rapido` roda só o que mudou e sem o build; `--so web\|servidor\|e2e` escolhe a parte; `--ate-o-fim` não para no primeiro erro. Acha o Node 24 sozinho. |
| [`midia_teste.py`](ferramentas/midia_teste.py) | Gera a **mídia de teste**: um pouco de cada subtipo, toda sintética (barras e tons feitos com o ffmpeg, páginas desenhadas). Vai para `~/.cache/croma-teste/midia` (28 MB, 4 s). Os arquivos não entram em nenhum repositório. |
| [`servidor_teste.py`](ferramentas/servidor_teste.py) | **Servidor de teste**: dados em `~/.cache/croma-teste/servidor`, porta **8097**, só a mídia sintética, **sem provedores da internet**, com uma biblioteca por subtipo e as contas `admin`, `leitor` e `tocador` (senha `teste`, só deste servidor descartável). Comandos: `subir`, `parar`, `estado`, `limpar`. Nunca toca o acervo nem o servidor de trabalho (8096). |
| [`e2e_servidor/`](ferramentas/e2e_servidor/) | Testes do servidor num servidor descartável (porta 8098), sem navegador: Baú, subtipo e coleções com dono. `python3 -m pytest e2e_servidor` dentro de `ferramentas/`; o `verificar.sh --so servidor` já roda. |
| [`e2e/`](ferramentas/e2e/) | **Ponta a ponta** com Playwright e pytest, contra o servidor de teste. Cada teste roda no `desktop` (1600×900) e na `tv` (1920×1080, modo TV). `python3 -m pytest` dentro da pasta; `-k nome` filtra; `--headed` mostra o navegador; `--atualizar-referencias` regrava as capturas. `conftest.py` tem os auxiliares (`pagina`, `ir`, `item`, `tocar`, `osd`, `conferir`). Marca `@pytest.mark.usuario('tocador')` nos testes que assistem (eles mudam o estado dos itens; o `leitor` fica intacto para as capturas). Falha também se a página lançar erro de JavaScript. |
| [`e2e/referencias/`](ferramentas/e2e/referencias/) | Capturas de referência (regressão visual), comparadas por `visual.py` (tolerância de 0,3% dos pixels). O que falhar vai para `e2e/falhas/` com o mapa de diferenças. |
| [`web_capturas.py`](ferramentas/web_capturas.py) | Captura avulsa de telas do servidor de trabalho (conta `teste`), para olhar uma tela sem escrever teste. Uso: `python3 ferramentas/web_capturas.py <pasta> "<rota>\|<nome>" ...`. |

- **Dependências:** `pip install --user pytest playwright pillow`, o Chromium do Playwright (`playwright install chromium`) e o ffmpeg do sistema. O Chromium do Playwright não tem H.264: o servidor converte, e os chips mostram "Convertendo no servidor". Reprodução direta só num navegador com H.264 (pendência do D00).
- **Testes de componente** (`croma-web`): Vitest com Testing Library, ao lado do componente (`SectionTabs.test.tsx`, `SectionLinks.test.tsx`). O `vite.config.ts` define as globais do build do webpack (`__WEBPACK_SERVE__` etc.); como as globais do Vitest estão desligadas, o teste chama `afterEach(cleanup)`. Módulos que puxam metade do app (como `useCurrentTab`, que lê as configurações do usuário) são trocados por `vi.mock`.
- **Chromium 85 (TV):** o `.stylelintrc.json` do `croma-web` recusa `inset`, `aspect-ratio` e `:not(a, b)` em `src/components/croma/` e `src/themes/croma/`.
- **Build do `croma-web` no Linux:** o `node` do sistema ainda é o 22; o `verificar.sh` já resolve. À mão: links temporários (`ln -sf /usr/bin/node-24 <pasta>/node`, o mesmo para `npm-24`), a pasta no começo do `PATH`, e `npm run build:production` (1 a 2 minutos). O servidor lê o `dist/` do disco.

## Mapa do croma-servidor (onde mexer)

- **Subtipo da biblioteca (S01):** `Jellyfin.Data/Enums/LibrarySubtype.cs`, `MediaBrowser.Model/Library/LibrarySubtypeCatalog.cs`, `LibraryOptions.Subtype`, `Jellyfin.Api/Controllers/LibrarySubtypesController.cs` (`GET /Library/Subtypes`) e a validação no `LibraryStructureController`.
- **Padrão Baú (S02 e S03):** `MediaBrowser.Providers/Bau/` (`BauLayout` acha as pastas, `BauJson` lê os JSON; um provedor por tipo: filme, série, episódio, faixa; `BauImageProvider` lê as imagens; `BauCollectionsPostScanTask` cria e sincroniza as coleções depois de cada varredura, para filmes, séries e músicas). Especificação em `specs/varredura-bau.md`.
- **Coleções com dono (S04):** `BoxSet.OwnerLibraryId` (no JSON do item, sem migração), `BoxSet.UseThumbnails`, `LibraryOptions.CollectionsUseThumbnails`; `CollectionManager` (dono na criação, recusa de item de outra biblioteca, `GetCollectionsOwnedBy`, `GetCollectionsAcceptingItem`, `SetDisplayModeAsync`); `CollectionController` (`GET /Collections`, `POST /Collections/{id}/DisplayMode`); `MediaBrowser.Providers/BoxSets/BoxSetOwnerPostScanTask.cs` dá dono às coleções antigas. Campos novos no DTO: `OwnerLibraryId`, `CollectionUseThumbnails`, `CollectionsUseThumbnails`.
- **Testes do servidor:** xUnit em `tests/` (`Jellyfin.Providers.Tests/Bau`, `Jellyfin.Model.Tests/Library`) e, de ponta a ponta, `ferramentas/e2e_servidor/` (servidor descartável na porta 8098, sem navegador; usa o binário publicado em `croma-servidor/compilado/`: depois de mudar o C#, `dotnet publish Jellyfin.Server --configuration Release --output compilado`).

## Mapa das cascas

- **Tizen:** `config.xml` (nome, ids `AprZAARz4r.Jellyfin`, `widget id`), `icon.png`
- **Desktop:** `CMakeModules/NameConfiguration.cmake`, `resources/images`, `native/find-webclient.*` (tela de conexão),
  `bundle/win/JellyfinDesktop.iss.in` (instalador Windows)
- **Android:** `app/build.gradle.kts` (`namespace = "org.jellyfin.mobile"`), `app/src/main/res/values/strings_donottranslate.xml` (`app_name`), ícones em `app/src/main/res/mipmap-*`

Nenhuma casca foi alterada ainda: as três seguem com nome, ids e ícones do Jellyfin.

## Plano de desenvolvimento

O roteiro fica em [`PLANO.md`](PLANO.md): etapas por plataforma (desktop agora, depois TV e celular) e módulos, cada um com as entregas e os testes que o fecham.

## Especificações

| Arquivo | Assunto | Situação |
|---|---|---|
| [`specs/colecoes.md`](specs/colecoes.md) | Coleções por biblioteca e modo de exibição | Especificado, não implementado |
| [`specs/tags.md`](specs/tags.md) | Tags e editor de tags vindos do v1 | Avaliado, com decisões em aberto |
| [`specs/secoes.md`](specs/secoes.md) | Seções Audiovisual, Áudios e Leitura; TV ao vivo fora do escopo | Estrutura e cores decididas (07/11/2026); só a D5 adiada |
| [`specs/varredura-bau.md`](specs/varredura-bau.md) | Leitura do padrão Baú (acervo do usuário, DL_HERMES): metadados, imagens, legendas e coleções | Filmes e séries implementados (08/11/2026); músicas a fazer |

## Identidade visual

A identidade oficial é a **v0.1 "Barras"**, decidida em 05/11/2026, e mora no [`croma-identidade`](https://github.com/Croma-plataform/croma-identidade). O manual é `croma-identidade/v0.1-barras/MANUAL.md`, e os arquivos prontos para uso ficam em `croma-identidade/v0.1-barras/logos/` (logotipo, símbolo, ícones das bibliotecas e `app/` com os ícones de cada plataforma). A v0.2 "CAPRA" fica arquivada no mesmo repositório.

Canvas com todas as pranchas: https://claude.ai/artifact/AUKTY2yvnHh4ZYk1c7qpLi (páginas "v0.1 Barras" e "v0.2 Direções CAPRA").
