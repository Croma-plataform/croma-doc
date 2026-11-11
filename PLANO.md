# Plano de desenvolvimento

Atualizado em 10/11/2026. Este é o roteiro do Croma, organizado em **etapas por plataforma** e, dentro delas, em **módulos**. Cada módulo diz o que entrega, de que depende e **quais testes o fecham**. As especificações de cada funcionalidade ficam em `specs/`; o mapa do código, em `CROMA.md`.

- **Etapa atual: 1 — Desktop** (decisão do usuário, 10/11/2026). As outras plataformas já estão planejadas abaixo e começam quando o desktop fechar.
- **"Desktop"** aqui é a interface web no layout de desktop (no navegador e no app) mais a casca `croma-desktop` (Qt WebEngine com mpv), para Windows.
- Marque as tarefas feitas neste arquivo. Marcas: `[x]` feito, `[ ]` a fazer, `[?]` a conferir contra o manual.

## Onde estamos

| Área | Situação |
|---|---|
| Repositórios, identidade v0.1 "Barras" | Feitos. Faltam pranchas das telas novas (módulo I01) |
| Servidor (`croma-servidor`) | Fork do Jellyfin v12.4 rodando no Linux com os 160 filmes do acervo. Subtipo da biblioteca e padrão Baú (filmes e séries) feitos, com 107 testes |
| Interface (`croma-web`) | Tema e marca; **filmes no desktop**: seções na barra lateral, abas e Resumo, detalhe do filme, player, painel de legendas e áudio, tela de carregando. 60 testes, só de lógica pura. O resto ainda é do Jellyfin |
| App desktop, TV, Android | Forks sem nenhuma mudança. Nada foi visto na TV de verdade |
| Testes | Só de unidade. Sem testes de componente nem de ponta a ponta; nada roda sozinho (GitHub Actions desligado) |

## Como o plano funciona

### Etapas

| Etapa | Plataforma | Situação |
|---|---|---|
| 1 | **Desktop:** web no layout de desktop e app `croma-desktop` | **em andamento** |
| 2 | **TV:** Samsung QN90B (`croma-tizen`, layout de TV) | planejada |
| 3 | **Celular:** web no layout móvel e `croma-android` | planejada |
| 4 | **Depois:** podcasts por feed, qualidade dos arquivos | planejada |

O servidor (módulos **S**) e a identidade (módulos **I**) servem a todas as etapas e entram quando um módulo de plataforma depende deles.

### O que o desktop já deixa pronto para as outras

A interface é a mesma nas três plataformas. Para a TV e o celular não virarem retrabalho:

- a regra de cada módulo fica em funções puras em `src/components/croma/<módulo>/` (como já é hoje), separada do desenho da tela; a TV e o celular reaproveitam a regra e mudam só a apresentação;
- o CSS do Croma já nasce compatível com o **Chromium 85** da TV (sem `inset`, `:not(a, b)` nem `aspect-ratio`), cobrado por verificação automática (D00);
- todo módulo do desktop passa por um **teste de fumaça no modo TV** do navegador (abre, navega com as setas, não quebra). O acabamento da TV é da etapa 2.

### Camadas de teste

| Sigla | Camada | Ferramenta | O que prova |
|---|---|---|---|
| **U** | Unidade | Vitest (`croma-web`), xUnit (`croma-servidor`), CTest (`croma-desktop`) | a regra, sem tela |
| **C** | Componente | Vitest com Testing Library | o componente React desenha e reage certo |
| **E** | Ponta a ponta | Playwright, em `ferramentas/e2e/`, contra um servidor de teste | o fluxo inteiro na tela, com verificação |
| **V** | Visual | captura de referência comparada a cada mudança | a tela continua igual à aprovada e à prancha |
| **S** | Servidor | xUnit de integração | API, gravação e varredura |
| **M** | Manual | lista de conferência versionada | o que só o aparelho de verdade mostra (mpv, TV, instalador) |

### Um módulo está pronto quando

1. as entregas estão feitas e conferidas contra o manual da identidade;
2. os testes listados existem e passam no `ferramentas/verificar.sh`, junto com todos os anteriores;
3. o teste de fumaça no modo TV passa;
4. o mapa do código (`CROMA.md`) e este plano estão atualizados;
5. o usuário viu a tela e aprovou, e o trabalho está em commits por funcionalidade.

Tamanho: **P** (pequeno), **M** (médio), **G** (grande). É só para comparar os módulos entre si.

---

## Etapa 1 — Desktop

| Módulo | O quê | Depende de | Tamanho | Situação |
|---|---|---|---|---|
| D00 | Base de testes e ambiente | — | M | **pronto**, faltam só 3 ações de ambiente |
| D01 | Seções e navegação | D00 | M | em parte |
| D02 | Componentes comuns | D00 | G | a fazer |
| D03 | Filmes: fecho | D01, D02 | P | quase pronto |
| D04 | Séries e episódios | D02, D03 | M | em parte |
| D05 | Documentários | D01, D04 | P | a fazer |
| D06 | Player de vídeo: complementos | D04 | M | em parte |
| D07 | App desktop: primeira versão | D00 | M | a fazer |
| D08 | Início | D01, D02 | M | a fazer |
| D09 | Busca | D01, D02 | M | a fazer |
| D10 | Coleções | D01, S04 | M | a fazer |
| D11 | Músicas | D02, D07 | G | a fazer |
| D12 | Falado: podcasts e audiolivros | D11, I01 | G | a fazer |
| D13 | Leitura | D02, I01 | G | a fazer |
| D14 | Fotos | D02 | M | a fazer |
| D15 | Tags | decisões do usuário | M | bloqueado |
| D16 | Entrada e conta | D02 | M | a fazer |
| D17 | Ajustes e calibração | D02 | M | a fazer |
| D18 | Espera e erro | D02 | M | a fazer |
| D19 | Painel de administração | D02 | P | a conferir |
| D20 | App desktop: versão final | D07 e os demais | M | a fazer |
| D21 | Fechamento do desktop | todos | M | a fazer |

A ordem da tabela é a ordem sugerida. O **D07 entra cedo** de propósito: o app toca com o mpv, não com o player do navegador, e isso muda o comportamento do player, das legendas e do áudio. É melhor descobrir agora do que no fim.

### D00 · Base de testes e ambiente

Tudo o que os outros módulos usam para provar que funcionam. Como usar: `CROMA.md`, seção "Ferramentas".

- [x] `ferramentas/verificar.sh`: eslint, stylelint, tipos, testes e build do `croma-web`; testes e formatação do `croma-servidor`; ponta a ponta. `--rapido` roda só o que mudou (10/11/2026).
- [x] **Mídia de teste gerada por script** (`ferramentas/midia_teste.py`), fora do acervo e sem direitos de terceiros: 5 filmes (H.264, HEVC, 2 áudios e 2 legendas, capítulos, com pôster), uma série de 2 temporadas, um filme e uma série documentais, 2 álbuns, um podcast, um audiolivro com capítulos, um EPUB, um PDF, uma HQ e um mangá em CBZ, 7 fotos. 28 MB em 4 s; o repositório guarda o script, não os arquivos (10/11/2026).
- [x] **Servidor de teste** (`ferramentas/servidor_teste.py`): outra pasta de dados, porta 8097, uma biblioteca por subtipo, contas `admin`, `leitor` e `tocador`, **sem provedores da internet** (só `EnableInternetProviders` não bastava: o TMDB "identificou" um documentário de teste; é preciso deixar vazias as listas de provedores de cada tipo) (10/11/2026).
- [x] **Ponta a ponta** em `ferramentas/e2e/` (Playwright com pytest), nos dois layouts: fumaça, detalhe do filme, seções, player, painel de legendas e áudio, tela de carregando, e navegação por setas no modo TV. Falha também com erro de JavaScript na página. 40 casos (10/11/2026).
- [x] **Capturas de referência** e comparação automática (`ferramentas/e2e/visual.py`), com 3 telas (detalhe do filme nos dois layouts e grade de filmes); as outras entram junto com o módulo de cada tela (10/11/2026).
- [x] **Testes de componente:** Testing Library no `croma-web`, com `SectionTabs` (5 casos) e `SectionLinks` (4 casos) (10/11/2026).
- [x] **Chromium 85:** regra no `stylelint` que recusa `inset`, `aspect-ratio` e `:not(a, b)` em `src/components/croma/` e `src/themes/croma/`; o `escheck` (ES5) está no build do `verificar.sh` (10/11/2026).
- [x] **Fumaça no modo TV:** `test_navegacao_tv.py` abre 5 telas com `layout=tv` e anda só com as setas (10/11/2026).
- [x] **Referência** (10/11/2026): a verificação completa passou inteira, sem nenhuma falha herdada do Jellyfin: eslint do repositório todo (59 s), stylelint, tipos, Vitest, build com `es-check` (57 s), `dotnet test` do servidor inteiro (105 s), `dotnet format` (47 s) e 40 casos de ponta a ponta (189 s). Qualquer falha daqui em diante vem de uma mudança nova.
- [ ] **Navegador com H.264** nos testes (Chrome do sistema no lugar do Chromium do Playwright), para testar a reprodução direta; hoje o servidor converte em quase tudo.
- [ ] **Ambiente (ações do usuário):** remontar o **acervo só leitura** (`sudo mount -o remount,ro /dev/sdb1`; em 10/11/2026 estava em `rw`) e baixar o `jellyfin-ffmpeg` para `croma-servidor/ffmpeg/`.
- [ ] Decidir se o GitHub Actions volta a rodar nos forks só com os testes do Croma.

Testes do próprio módulo:

- [x] **E** fumaça: entrar, ver o Início, abrir um filme e tocar, no desktop e no modo TV (`test_fumaca.py`).
- [x] O `verificar.sh` falha de propósito com um erro plantado em cada camada: lint, tipo, teste, CSS proibido e ponta a ponta reprovaram (10/11/2026).

Pronto quando: um comando só diz se o projeto está inteiro.

### D01 · Seções e navegação

Feito: barra lateral com as seções, cabeçalho com abas, Resumo do Audiovisual, seção destacada no detalhe.

- [x] Cabeçalho da seção como no manual: rótulo mono `λ 580 nm · 5 FILMES · 1 SÉRIES`, nome em Archivo Expandida e o quadrado na cor (11/11/2026). Fotos fica sem λ (o magenta não é espectral). Código em `features/sections/counts.ts` e `useSectionCounts.ts`.
- [x] **Gêneros da seção inteira**, com a contagem por subtipo em cada gênero (`SectionGenresView`, `genres.ts`). Gêneros iguais de bibliotecas diferentes se juntam, sem contar acento ou caixa.
- [ ] **Coleções da seção inteira.** Depende da decisão do usuário sobre o dono das coleções (`specs/colecoes.md`); hoje a aba mostra as da biblioteca aberta.
- [?] Barra lateral: 240 px, barra de 4 px e fundo Grafite na ativa, subtipos com ícone sem cor. Conferido na captura (240 px, barra amarela, subtipos com ícone); falta medir a barra e a cor.
- [x] A lista de seções e subtipos do web confere com o catálogo do servidor (`test_catalogo.py`).
- [x] Editar o subtipo de uma biblioteca que já existe, pela tela: o campo já existia no editor; agora há teste (`test_subtipo_biblioteca.py`).
- [ ] O cartão da biblioteca no painel mostra o tipo do Jellyfin ("Livros") e não o subtipo ("Mangás").

Testes:

- [x] **U** contagens do cabeçalho, gêneros somados e filtrados por letra (`counts.test.ts`, `genres.test.ts`). `getHeaderTabs` está exportada, falta o caso dedicado.
- [x] **U/E** seções do web contra o catálogo do servidor de teste.
- [x] **C** `SectionTabs` (agora com o rótulo), `SectionLinks`. `SectionSummaryView` (fileira vazia some, recomendações dos filmes).
- [x] **E** abas e cabeçalho das quatro seções, gêneros da seção, conta com uma só biblioteca (`test_acesso.py`), troca de subtipo.
- [x] **V** cabeçalho e barra lateral de cada seção (`cabecalho-*`).

### D02 · Componentes comuns

O que todas as seções usam. Fazer antes delas evita refazer.

- [x] **Capa gerada** (11/11/2026, `components/croma/generatedCover/`, ligada em `Media.tsx`; SVG que escala com o cartão; filmes, séries, temporadas, coleções, álbuns e livros; episódios mantêm o ícone). Era: 2:3 e 1:1, quadrado na cor da seção, título, autor em mono, faixa de 7 barras, com visto e progresso por cima.
- [~] **Cartões** (11/11/2026, `themes/croma/theme.scss`, `CardImageContainer.tsx` define `--croma-card-cor` pela seção do item): feitos o visto (quadrado na cor da seção com ✓ em Sinal), o progresso na cor da seção (era azul do Jellyfin), a etiqueta `+2` em mono e a borda Fósforo de 4 px ao passar o mouse. Faltam o título em Névoa nos vistos, a etiqueta de tipo (FILME/SÉRIE, módulo D05) e o botão de assistir ao passar o mouse.
- [x] **Avisos rápidos** (11/11/2026, `components/toast/toast.ts` reescrito sobre `components/croma/toast/toastQueue.ts`; callers antigos seguem como informação de 6 s): sucesso, informação e erro, com as durações do manual, até 3 empilhados.
- [x] **Carregando** geral (`components/loading/`: faixa do espectro com trecho aceso a 1,8 s, só depois de 300 ms, parada a 60% com movimento reduzido) e **cartões-esqueleto** (`components/croma/states/CardSkeletons.tsx`, usados no Resumo e nos Gêneros da seção; as outras telas ainda usam só o carregando geral) (11/11/2026).
- [x] **Vazio** (`components/croma/states/EmptyState.tsx`, aplicado pelo `NoItemsMessage`): moldura apagada, ícone do subtipo, "0 ITENS" e a ação principal. Falta passar o ícone e a ação em cada tela (11/11/2026).
- [x] **Alternar grade e lista** (11/11/2026, `apps/modern/features/libraries/components/ViewModeToggle.tsx`): seleção segmentada visível na barra da biblioteca (o escolhido em Fósforo com texto Sinal); o menu de configurações do Jellyfin continua com as opções de imagem e cartão.
- [~] Tema contra o manual (11/11/2026, `themes/croma/theme.scss`): feitos botões (principal, secundário, terciário com contorno de 2 px), foco em botão (fundo Fósforo e contorno de 4 px afastado 4 px), campos (contorno `#4A4B4F` sobre Sinal, rótulo mono), alternância (trilho Fósforo/Linha), abas (barra de 4 px) e título em Névoa nos vistos (`data-played` no `CardBox`). Falta conferir tudo na página de mostruário (V) e o seletor de passo; alternância sem o texto "Ligado/Desligado" ao lado.
- [x] **Movimento** (variáveis `--croma-dur-*` e `--croma-ease-enter` no tema, zeradas com movimento reduzido; falta aplicar nas telas antigas): durações e curva do manual como variáveis; tudo respeita `prefers-reduced-motion`.

Testes:

- [ ] **U** capa gerada (proporção por tipo, título longo, cor da seção, sem autor); fila de avisos (limite de 3, durações, erro fica até a pessoa agir).
- [ ] **C** cada componente nos seus estados.
- [ ] **E** item sem arte mostra a capa gerada; aviso aparece e some; biblioteca vazia; movimento reduzido para as animações.
- [ ] **V** uma página de mostruário com todos os componentes e estados, comparada à prancha 35.

### D03 · Filmes: fecho

Feito: grade com filtros, detalhe completo (prancha 28), etiqueta da edição.

- [?] Galeria (prancha 09): 7 colunas de 160 px, indicadores do D02.
- [ ] Filtro por **resolução**, além de gênero, ano e visto.
- [?] Detalhe: etiqueta de classificação (número em mono sobre Fósforo).
- [ ] Lista de edições (`editions.ts` só conhece `Estendida`): vir do servidor ou ganhar as demais.

Testes:

- [ ] **E** detalhe com e sem progresso, com edição, com mais de uma versão, sem elenco, sem fundo; favoritar e marcar como visto; filtros da grade.
- [ ] **U** falha do `PlaybackInfo` na ficha do arquivo.
- [ ] **V** grade e detalhe contra as pranchas 09 e 28.

### D04 · Séries e episódios

Feito: fita de episódios e kicker no detalhe da série. O leitor do Baú para séries já existe no servidor.

- [ ] Biblioteca de Séries do acervo criada e varrida.
- [ ] Galeria de séries (prancha 10) com a etiqueta `+2`.
- [ ] Resto do detalhe da série e a página da temporada no visual do manual.
- [ ] **Detalhe do episódio** (prancha 29): imagem na moldura, fita da temporada e a lista com o episódio atual em Grafite.
- [ ] Faixa de baixo (ficha técnica e arquivo) para o episódio.

Testes:

- [ ] **U** fita com especiais e com temporada sem episódios (o modelo já tem 7 testes).
- [ ] **E** série sem nada visto, pela metade e toda vista; episódio novo depois da última vez que a pessoa assistiu; "Próximo: T1 E02" abre o episódio certo.
- [ ] **V** pranchas 10 e 29.

### D05 · Documentários

- [ ] Aba **Documentários** que junta as bibliotecas de filmes e de séries documentais numa grade só, com a etiqueta FILME ou SÉRIE.
- [ ] Novidades de documentários no Resumo.

Testes:

- [ ] **U** junção e ordenação das duas bibliotecas; etiqueta de tipo.
- [ ] **S** já existe: documentários não entram nas visões agrupadas de filmes.
- [ ] **E** um filme documental aparece em Documentários e não em Filmes.

### D06 · Player de vídeo: complementos

Feito: OSD (pranchas 11 e 12), painel de legendas e áudio (36), tela de carregando (38).

- [ ] **Próximo episódio** (prancha 37): o vídeo encolhe para a moldura, cartão do episódio, contagem de 8 s, "Assistir agora" em foco. O Jellyfin já tem o `upnextdialog`.
- [ ] **Pular abertura:** botão já em foco, só durante a abertura. O Jellyfin já tem os segmentos de mídia; falta decidir **de onde vêm as marcações** (S05).
- [ ] **Aba Imagem** do painel: o manual não define o conteúdo (I02).
- [ ] Miniatura na busca: depende do trickplay fora do acervo (S05).

Testes:

- [ ] **U** contagem do próximo episódio; janela em que o botão de pular aparece e some (1 s depois do fim).
- [ ] **E** do que já existe: tocar, pausar, −10 e +30, capítulos, buscar, sair e voltar no ponto; painel (trocar legenda e áudio, tamanho, fundo, atraso, fechar com Esc); carregando com a rede lenta.
- [ ] **E** fim de um episódio leva ao próximo; cancelar a contagem; pular a abertura.
- [ ] **E** reprodução direta (navegador com H.264), conversão só de áudio e conversão de vídeo: os selos e os chips certos em cada caso.

### D07 · App desktop: primeira versão

Objetivo: o Croma abrindo no app, com o player do Croma tocando pelo mpv, o quanto antes.

- [ ] Compilar o `croma-desktop` no Linux. O `dev/linux/setup.sh` é só para Debian e Ubuntu: fazer a lista de pacotes do Fedora ou usar o contêiner do AppImage.
- [ ] Marca mínima: nome (`CMakeModules/NameConfiguration.cmake`, `appName` em `native/nativeshell.js`), ícone e a tela de conexão (`native/find-webclient.*`) sem o nome e o logo do Jellyfin.
- [ ] **Desligar o aviso de atualização** (`native/updatePlugin.js` consulta os lançamentos do Jellyfin).
- [ ] Conferir o player do Croma com o `mpvVideoPlayer.js`:
  - eventos `waiting` e `playing` (tela de carregando) e trechos carregados na linha do tempo;
  - chips e selo: o mpv toca quase tudo direto, então "Reprodução direta" deve ser a regra;
  - **estilo da legenda:** quem desenha a legenda é o mpv, então tamanho e fundo do painel podem não ter efeito; descobrir e decidir (aplicar no mpv ou esconder as opções no app);
  - atraso da legenda e troca de faixas.

Testes:

- [ ] **U** os 4 testes do `croma-desktop` (CTest) continuam passando.
- [ ] **M** lista de conferência no app: conectar, entrar, abrir um filme, tocar um HEVC 4K com HDR e áudio de vários canais, trocar legenda e áudio, buscar, tela cheia, sair e voltar no ponto.
- [ ] O que o mpv fizer diferente do navegador vira item do D06, do D11 ou do D20.

### D08 · Início

- [ ] Tela inicial (pranchas 04 e 15) no visual do manual: "Continuar" primeiro, com o rótulo de tipo na cor da seção (`SÉRIE · DARK · T2 E06`), depois as novidades por seção.
- [ ] Opções da tela inicial sem as fileiras que saíram.

Testes:

- [ ] **U** rótulo de tipo de cada item; ordem das fileiras; nunca pôster e capa quadrada na mesma fileira.
- [ ] **E** conta nova (Início vazio), conta com itens pela metade de três seções.
- [ ] **V** prancha 15.

### D09 · Busca

- [ ] Resultados agrupados por seção e, dentro dela, por subtipo (prancha 33).
- [ ] Atalho `Ctrl K`; campo no visual do manual.
- [ ] Sem resultados: "0" grande, "Nada com “termo”" e sugestões em chips.

Testes:

- [ ] **U** agrupamento e ordem dos resultados; pessoas e estúdios no lugar certo.
- [ ] **E** buscar com e sem resultado; `Ctrl K` de qualquer tela; abrir um resultado e voltar.
- [ ] **V** prancha 33.

### D10 · Coleções

- [ ] **Rever a `specs/colecoes.md` antes** (S04): ela fala em bibliotecas e guarda o dono em tags reservadas.
- [ ] Coleção com dono; "Adicionar à coleção" só lista as do dono do item; sem tela global; modo de exibição por biblioteca e por coleção; coleções do Baú com dono.

Testes:

- [ ] **S** gravação, validação e consulta por dono; migração numa cópia do banco.
- [ ] **U** escolha do formato (pôster ou miniatura) e a ordem de arte de reserva (Thumb, Backdrop, capa gerada).
- [ ] **E** criar, adicionar, mudar o modo de exibição; formatos nunca misturados.

### D11 · Músicas

Nada feito no visual do Croma. O Jellyfin já tem as bibliotecas, a fila e as letras.

- [ ] Abas e Resumo da seção **Áudios**.
- [ ] Galeria, álbum e artista (pranchas 17, 20 e 21): capa na moldura, faixa tocando com o mini equalizador, capa de artista (foto, mosaico ou capa) com a etiqueta de origem.
- [ ] **Tocando agora** (prancha 18) com a fila.
- [ ] **Analisador de espectro.** O web não tem nenhum hoje. No navegador sai do Web Audio; **no app o som passa pelo mpv**, que não entrega as amostras à interface: precisa de uma ponte nativa ou de outra saída (decidir depois do D07).
- [ ] **Mini player** fixo embaixo, com o progresso em espectro.
- [ ] Capas de playlist geradas.

Testes:

- [ ] **U** cor de cada coluna do analisador pela frequência e o pico; escolha da capa do artista; faixa de espectro de cada playlist.
- [ ] **C** mini player e linha de faixa nos estados (tocando, pausado, sem capa).
- [ ] **E** tocar um álbum, trocar de faixa, fila, o mini player continua ao navegar, sair e voltar.
- [ ] **M** no app: som pelo mpv, teclas de mídia, analisador.
- [ ] **V** pranchas 17, 18, 20 e 21.

### D12 · Falado: podcasts e audiolivros

Depende das pranchas novas (I01).

- [ ] Abas Podcasts e Audiolivros; **página do programa** com os episódios do mais novo ao mais antigo, com "ouvido" e progresso.
- [ ] **Player falado:** pulos de 15 s e 30 s, velocidade de 0,8× a 2×, capítulos ou notas, temporizador para dormir, linha do tempo em espectro com os capítulos, sem analisador.
- [ ] "Continuar ouvindo" com "faltam 3 h 12 min".

Testes:

- [ ] **U** tempo restante com a velocidade; temporizador (fim do capítulo, 15, 30 e 60 min); ordem dos episódios.
- [ ] **E** ouvir, sair e voltar no ponto; mudar a velocidade; o temporizador pausa na hora certa.

### D13 · Leitura

A prancha do leitor de HQ e mangá ainda não existe (I01).

- [ ] Abas Livros, HQs e Mangás, com as grades agrupadas por série, e o Resumo ("vol. 3 · p. 45 de 180").
- [ ] Leitor de EPUB e de PDF (prancha 27): temas Escuro e Papel, coluna de 1040 px, progresso azul com página e tempo restante.
- [ ] Leitor de HQ e mangá: página dupla; **mangá da direita para a esquerda por padrão**, pelo subtipo da biblioteca.

Testes:

- [ ] **U** direção pelo subtipo; tecla que avança em cada direção; pares da página dupla (capa sozinha); texto do progresso.
- [ ] **E** abrir, virar páginas, fechar e voltar na mesma página, para EPUB, PDF, HQ e mangá.
- [ ] **V** pranchas 26 e 27.

### D14 · Fotos

O Croma serve fotos e vídeos com a varredura padrão do Jellyfin. As bibliotecas Vídeos e Galeria do acervo ficam fora (veja "Fora do escopo").

- [ ] Grade justificada com agrupamento por mês (prancha 24), favorita com o quadrado magenta, etiqueta de vídeo "▶ 0:42".
- [ ] Visualizador com a fita de miniaturas (prancha 25).

Testes:

- [ ] **U** a conta da grade justificada (cada fileira fecha a largura, proporções mantidas) e o agrupamento por mês.
- [ ] **E** abrir a grade, o visualizador, avançar, favoritar.
- [ ] **V** pranchas 24 e 25.

### D15 · Tags

Bloqueado nas três decisões de `specs/tags.md` (onde ficam salvas, níveis, escopo). A spec precisa de revisão: ela se apoiava nas bibliotecas que saíram do Croma.

- [ ] Depois das decisões: levar a lógica do v1 para TypeScript, modo "todas", edição em massa, trava do campo Tags.

Testes:

- [ ] **U** os testes do v1 vêm com o código (`tagPicker`, `edicaoMassa`, `pesquisa`).
- [ ] **S** atualizar metadados não sobrescreve as tags editadas.
- [ ] **E** marcar vários itens, filtrar por duas tags.

### D16 · Entrada e conta

- [ ] **Abertura** (prancha 30): moldura, barras e nome em 1,9 s.
- [ ] **Servidor** (prancha 32): escolher e adicionar, com a varredura de servidores.
- [ ] Entrar e **perfis** (prancha 31), com o avatar de barras; código de autorização.

Testes:

- [ ] **U** barras do avatar pelo perfil; validade do código.
- [ ] **E** primeiro acesso, senha errada, trocar de perfil, sair; abertura com movimento reduzido.
- [ ] **V** pranchas 30, 31 e 32.

### D17 · Ajustes e calibração

- [ ] **Ajustes** (prancha 34) no visual do manual, com os controles do D02.
- [ ] **Tela de calibração** (prancha 03), em Ajustes › Imagem: Brilho (PLUGE), Contraste e Cor.

Testes:

- [ ] **U** os valores das barras e do PLUGE de cada etapa.
- [ ] **E** mudar uma preferência e conferir que valeu depois de recarregar; percorrer as três etapas da calibração.
- [ ] **V** pranchas 03 e 34.

### D18 · Espera e erro

- [ ] **Descanso de tela** (pranchas 05 e 06): o movimento do manual, depois de 5 min parado no menu, nunca durante a reprodução. Hoje só o logo foi trocado.
- [ ] **Sem sinal** (prancha 07): estática, painel, nova tentativa a cada 15 s e "Trocar servidor".
- [ ] Textos de erro com a voz do manual.

Testes:

- [ ] **U** movimento do descanso (ângulo sempre entre 25° e 65°, troca de cor na borda, canto em cheio); contagem da nova tentativa.
- [ ] **E** derrubar o servidor de teste: aparece "Sem sinal" e a tela volta sozinha quando ele sobe; o descanso não entra com um vídeo tocando.

### D19 · Painel de administração

Só existe no desktop.

- [?] Telas do painel com o tema Croma, sem nome nem logo do Jellyfin.
- [ ] Campo "Conteúdo" do diálogo de biblioteca e a TV ao vivo escondida, cobertos por teste.

Testes:

- [ ] **C** o campo "Conteúdo" lista só os subtipos do tipo escolhido.
- [ ] **E** criar uma biblioteca de cada subtipo, editar, varrer; nenhuma entrada de TV ao vivo.

### D20 · App desktop: versão final

- [ ] Marca completa: `croma.ico`, instalador do Windows (`bundle/win/JellyfinDesktop.iss.in`), nomes das pastas de dados.
- [ ] **Barra de título própria**, escura, com o símbolo e o nome do servidor.
- [ ] Tela de conexão no visual do manual.
- [ ] O que o D07 e o D11 deixaram para o app (legenda no mpv, analisador).
- [ ] Teclas de mídia, integração com a barra de tarefas e tela cheia.
- [ ] Build e instalação no Windows (máquina CintraMan), com o servidor do S06.

Testes:

- [ ] **U** CTest, mais os testes das mudanças em C++.
- [ ] **M** roteiro de aceitação no Windows: instalar do zero, conectar, um fluxo de cada seção, desinstalar; atualizar por cima de uma versão anterior.

### D21 · Fechamento do desktop

- [ ] Roteiro de aceitação completo (todos os **E** e **M**) numa instalação limpa.
- [ ] Desempenho com o acervo real: grade, busca e abertura do detalhe.
- [ ] Acessibilidade: tudo pelo teclado, foco sempre visível, movimento reduzido.
- [ ] Textos: nenhum "Jellyfin" na interface; voz do manual.
- [ ] Licença: código GPL publicado, sem nome nem logo do Jellyfin no produto.
- [ ] Guia de instalação e uso em `croma-doc`.

---

## Servidor (serve a todas as etapas)

| Módulo | O quê | Quem depende | Situação |
|---|---|---|---|
| S01 | Subtipo da biblioteca | todos | feito |
| S02 | Padrão Baú: filmes e séries | D03, D04 | feito, faltam testes |
| S03 | Padrão Baú: músicas | acervo de música no D11 | a fazer |
| S04 | Coleções com dono | D10 | a fazer |
| S05 | Marcações de abertura e trickplay | D06 | decisão |
| S06 | Servidor no Windows (CintraMan) | D20 | a fazer |
| S07 | Atualização para uma versão nova do Jellyfin | todas | ensaio a fazer |

- **S01** — testes que faltam: [ ] editar o subtipo de uma biblioteca existente (`400` quando não combina); [ ] biblioteca antiga, sem o campo, com o servidor no ar.
- **S02** — testes que faltam: [ ] `BauCollectionsPostScanTask` (cria, acha pelo `uuid`, não duplica ao renomear, tira o item posto à mão, trava, não apaga quando o arquivo some); [ ] `BauEpisodeProvider` (achado pelo `file`, vídeo fora da lista, especiais); [ ] varredura de uma pasta Baú de mentira de ponta a ponta; [ ] **somente leitura:** varrer e atualizar uma cópia e conferir que nenhum arquivo dela mudou.
- **S03** — [ ] leitores de artista, álbum e faixa, imagens e coleções (documento do DL_HERMES aprovado em 08/11/2026); atualizar `specs/varredura-bau.md`. Testes: um arquivo por leitor, como nos filmes. As telas do D11 não dependem dele: usam a mídia de teste e a varredura padrão.
- **S04** — [ ] decidir onde mora o dono da coleção. A convenção de 07/11/2026 pede o modelo do servidor, não tags reservadas. Testes **S** no D10.
- **S05** — [ ] abertura: de onde vêm as marcações (capítulos do arquivo, plugin ou marcação à mão); [ ] trickplay: só se as miniaturas ficarem fora da pasta da mídia, confirmado no código e testado numa cópia.
- **S06** — [ ] .NET SDK 10 no Windows, migrar a pasta para o layout novo, compilar, `jellyfin-ffmpeg`, trocar o binário oficial pelo fork. Teste **M**: subir, varrer uma biblioteca de teste, tocar.
- **S07** — [ ] ensaiar o rebase da branch `croma` numa versão nova, com o `croma-web` junto, e rodar o `verificar.sh`.

## Identidade (serve a todas as etapas)

| Módulo | O quê | Quem depende |
|---|---|---|
| I01 | Pranchas novas: páginas das seções com o Resumo, Documentários, página de programa de podcast, player falado, leitor de HQ e mangá | D05, D12, D13 |
| I02 | Decisões de prancha: conteúdo da aba Imagem do painel; prancha 38 sem tempo estimado nem velocidade da rede (o servidor não informa) | D06 |
| I03 | Teste dos geradores: rodar os scripts do zero e conferir que as pranchas saem iguais às versionadas | — |

---

## Etapa 2 — TV (planejada)

A TV usa o **layout legado** do `croma-web` (`.layout-tv`), então o menu e o Início são feitos de novo nele. O resto reaproveita a regra dos módulos do desktop e muda a apresentação: escala 2×, margens seguras de 96 e 54 px, foco de 8 px, um item em foco por vez.

| Módulo | O quê | Reaproveita |
|---|---|---|
| T00 | Ambiente: Tizen Studio, certificado Samsung, modo desenvolvedor da TV | — |
| T01 | Casca `croma-tizen`: nome, ids (`config.xml`), ícone e tile; empacotar o `dist/` no `.wgt` e instalar. As fontes do Croma continuam embutidas mesmo com `USE_SYSTEM_FONTS=1` | — |
| T02 | Base do modo TV: tema, escala, margens, foco, desempenho das animações no Chromium 85 | D02 |
| T03 | Menu no topo com as seções, Início e teclas coloridas | D01, D08 |
| T04 | Audiovisual: grades, detalhes com o menu reduzido, fita de episódios | D03 a D05 |
| T05 | Player na TV de verdade: o que toca direto (HEVC 4K HDR, áudios), OSD, painel, carregando, próximo episódio | D06 |
| T06 | Áudios: tocando agora, analisador, player falado | D11, D12 |
| T07 | Leitura: corpo de 32 px, setas seguindo a direção de leitura | D13 |
| T08 | Fotos: grade e visualizador pelo controle | D14 |
| T09 | Busca com o teclado da TV; formulários com as medidas do manual | D09, D17 |
| T10 | Abertura, perfis, servidor, calibração, descanso de tela e sem sinal | D16 a D18 |
| T11 | Fechamento: roteiro de aceitação na QN90B | todos |

Testes da etapa:

- **E** os roteiros do desktop ganham a versão do modo TV: 1920×1080, `layout=tv`, **só com as setas, OK e Voltar**. Cada tela prova que todo elemento é alcançável e que o foco nunca se perde.
- **E** tentar rodar esses roteiros num **Chromium 85** de verdade, além do navegador atual.
- **V** capturas de referência do modo TV contra as pranchas da TV.
- **M** lista de conferência na QN90B por módulo: escala e margens, foco, fontes, teclas do controle, reprodução direta de cada formato do acervo, fluidez.
- **U** e **C** são os mesmos do desktop: a regra é compartilhada.

## Etapa 3 — Celular (planejada)

| Módulo | O quê |
|---|---|
| M01 | Web no layout móvel: 5 abas embaixo (Início, Audiovisual, Áudios, Leitura, Mais), subtipos em chips, margens de 20 px e áreas seguras, alvos de toque de 48 px |
| M02 | Telas próprias do celular (prancha 16 e 19): série com as abas de temporada, músicas com o mini player acima das abas, player em retrato |
| M03 | Casca `croma-android`: nome, `namespace`, ícones (já prontos em `logos/app/mobile/`), conexão ao servidor |
| M04 | Fechamento: roteiro de aceitação num aparelho |

Testes da etapa:

- **E** os roteiros em 390×844 com toque (emulação do Playwright).
- **U** os testes do `croma-android` (Gradle), `detekt` e o lint do Android.
- **M** lista de conferência num aparelho: gestos, giro da tela, reprodução em segundo plano, notificação de mídia.

## Etapa 4 — Depois

- [ ] Podcasts por assinatura de feed (plugin próprio no servidor; `specs/secoes.md`, decisão D2).
- [ ] **Verificação da qualidade dos arquivos** (pedido do usuário, 09/11/2026; só depois do core): funcionalidades que conferem a qualidade dos arquivos do acervo. O escopo vai ser definido com o usuário e a spec vai para `specs/`. O bloco Arquivo do detalhe do filme já mostra parte desses dados.

---

## Feito até aqui

- **Repositórios** (05–07/11/2026): 9 repositórios na organização `Croma-plataform`, documentação em `croma-doc`, perfil em `.github`.
- **Identidade** (05–08/11/2026): v0.1 "Barras" oficial; manual revisto para as seções (cores, ícones, navegação); ícones copiados para o `croma-web`.
- **Servidor** (07–08/11/2026): fork na tag `v12.4`, build e script de inicialização no Linux; catálogo de seções e subtipos, campo nas opções da biblioteca, validação, visões do usuário e endpoint; padrão Baú para filmes e séries (metadados, imagens, legendas, coleções); correção que impede apagar imagens da pasta da mídia.
- **Web** (07–10/11/2026): tema e marca; TV ao vivo fora da interface (`cromaFeatures.liveTv`); campo "Conteúdo" no diálogo de biblioteca; barra lateral com as seções; cabeçalho com abas; Resumo que junta as bibliotecas; etiqueta da edição; fita de episódios; detalhe do filme completo (prancha 28: kicker, botões, progresso, ficha técnica, arquivo, parecidos); player (pranchas 11 e 12); painel de legendas e áudio (36); tela de carregando (38).
- **Decisões:** seções e subtipos, D1 a D4 (07/11/2026); foco em filmes e web (08/11/2026); campos de Vídeo, Áudio e Legendas fora do detalhe (09/11/2026); desktop primeiro (10/11/2026).

## Fora do escopo

- **TV ao vivo** (07/11/2026): continua documentada no manual e em `specs/secoes.md`, mas sai da interface. A barra vermelha fica reservada.
- **Android TV e iOS:** sem data.
- **Rolagem vertical (webtoon)** no leitor de quadrinhos.
- **Bibliotecas Vídeos e Galeria do acervo do usuário** (09/11/2026): por privacidade, terão uma aplicação dedicada, fora do Croma. O Croma continua servindo fotos e vídeos com a varredura padrão do Jellyfin.

## Decisões e ações do usuário

| O quê | Trava |
|---|---|
| Remontar o acervo só leitura | D00 |
| Aprovar a estrutura das bibliotecas de música no acervo | S03 (as telas não dependem) |
| Onde mora o dono da coleção (modelo do servidor ou tags reservadas) | S04, D10 |
| De onde vêm as marcações de abertura; aceitar trickplay fora do acervo | S05, D06 |
| Conteúdo da aba Imagem do painel; manter ou ajustar a prancha 38 | I02, D06 |
| Legenda no app: aplicar o estilo no mpv ou esconder as opções | D07, D20 |
| Analisador de espectro no app (o mpv não entrega o som à interface) | D11, D20 |
| As três decisões de `specs/tags.md` | D15 |
| D5: vídeos caseiros e clipes (adiada) | D14 |
| Metadados dos filmes "Estendida" e do *Twin Peaks*; pasta Coleções para a conta `teste` | conferência das telas |
| Tizen Studio, certificado e modo desenvolvedor da TV | T00 |
| Escopo da verificação de qualidade dos arquivos | etapa 4 |
