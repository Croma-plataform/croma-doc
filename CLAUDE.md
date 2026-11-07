# CLAUDE.md — Croma

Responda sempre em português do Brasil.

## O que é

O **Croma** é a versão pessoal do Jellyfin do usuário: um servidor de mídia que reúne filmes, séries, música, fotos, TV ao vivo e livros. É para uso pessoal, com identidade visual própria.

- **Plataformas iniciais:** desktop e TV Samsung **QN90B** (2022, Tizen 6.5, Chromium 85). Android, Android TV e outras ficam para depois.
- **Visão geral, repositórios, versões e mapa do código:** `CROMA.md`. Leia esse arquivo antes de mexer nos repositórios.

## Repositórios

Esta pasta é o **hub**, a documentação do projeto (repositório `Croma-plataform/croma-doc`; a pasta local se chama `Croma-plataform`): só documentação geral (`CLAUDE.md`, `CROMA.md`, `README.md`) e especificações (`specs/`). Todos os repositórios ficam na organização **`Croma-plataform`** do GitHub (o usuário é admin). Cada subpasta abaixo é um repositório git próprio, fica no `.gitignore` do hub e é privado (só o `croma-doc` e o `.github` são públicos):

| Pasta | Repositório | O que é | Branch |
|---|---|---|---|
| `croma-identidade/` | `Croma-plataform/croma-identidade` | Identidade visual, logos e scripts geradores | `main` |
| `croma-servidor/` | `Croma-plataform/croma-servidor` | Scripts e configuração do servidor; futuros plugins C# | `main` |
| `croma-web/` | `Croma-plataform/croma-web` | Fork do jellyfin-web `release-12.z` (v12.4): a interface | `croma` |
| `croma-desktop/` | `Croma-plataform/croma-desktop` | Fork do jellyfin-desktop `master` (Qt WebEngine + mpv) | `croma` |
| `croma-tizen/` | `Croma-plataform/croma-tizen` | Fork do jellyfin-tizen `master` | `croma` |
| `croma-android/` | `Croma-plataform/croma-android` | Fork do jellyfin-android `master` (v2.7.1); criado, ainda não implementado | `croma` |
| `croma-v1/` | `Croma-plataform/croma-v1` | Croma v1, **arquivado** no GitHub (só leitura) | `main` |
| `croma-org/` | `Croma-plataform/.github` | Página de perfil da organização (`profile/README.md`), com logo copiado do `croma-identidade` | `main` |
| `jellyfin-server/` | jellyfin/jellyfin, tag `v12.4` | Só referência; o servidor roda com o binário oficial | — |

- Os forks são repositórios comuns (não forks do GitHub), com o Jellyfin como remote `upstream` e a organização como `origin`. O GitHub Actions está desativado nos forks.
- O `croma-identidade` e o `croma-servidor` têm `CLAUDE.md` próprios.
- **Clonar tudo numa máquina nova:** `CROMA.md`, seção "Clonar os repositórios".
- **Git:** só faça commit ou push quando o usuário pedir. Cada commit vai para o repositório da pasta em que foi feito; confira com `git -C <pasta> status` antes.

## Arquitetura

O desktop e o Tizen rodam a **mesma interface web**. A marca nasce no `croma-identidade` e é aplicada no `croma-web`:

```
croma-identidade (manual, logos, ícones)
   └─ copiado para → croma-web (fork jellyfin-web, release-12.z / v12.4)
                       ├─ build → croma-servidor serve via --webdir → croma-desktop (carrega a UI do servidor)
                       ├─ build → croma-tizen empacota o dist/ no .wgt
                       └─ (futuro) croma-android carrega a UI do servidor
```

- **Versões casadas:** a versão do web precisa bater com a do servidor (v12.4).
- **Base do web:** use o `jellyfin-web`, não o `jellyfin-vue`. Só o `jellyfin-web` tem layout de TV (`.layout-tv`, `layoutManager.tv`) e a integração com o Tizen.
- **Licença:** o código é GPL, e o nome e o logo "Jellyfin" não podem ser usados no produto.
- **Máquinas:** o projeto roda em mais de uma máquina.
  - **CintraMan (Windows):** servidor portátil instalado. A conexão é lenta: downloads grandes levam dezenas de minutos, então prefira espelhos rápidos e `curl -C -` para retomar. O .NET SDK não está instalado.
  - **Linux (Fedora, usuário `cintra_man`, pasta `~/Documentos/Projetos/Codes/Croma-plataform`):** tem `gh` (logado como Cintriano), Node, git, Chrome, o runtime do .NET (mas não o SDK) e o `git-filter-repo` (em `~/.local/bin`, instalado com `pip --user`). O git global está como "Your Name": cada repositório do projeto tem `user.name Cintriano` e o e-mail do usuário configurados localmente; faça o mesmo num clone novo. O servidor ainda não foi instalado aqui. A conexão é razoável (os clones completos levaram poucos minutos).

## Identidade visual oficial: v0.1 "Barras"

**Decisão do usuário (05/11/2026):** a identidade oficial do Croma é a **v0.1 "Barras", como está**. O manual é a fonte da verdade: `croma-identidade/v0.1-barras/MANUAL.md`. Confira toda proposta visual contra ele.

Resumo das regras:
- **Logotipo:** "CR▭MA", em que o "O" é a moldura 16:9 com a faixa de 7 barras. Arquivos em curvas em `croma-identidade/v0.1-barras/logos/`.
- **Formas:** cantos vivos em tudo, e a moldura grossa emoldura imagens. A única curva é a máscara de ícone do sistema.
- **Cores:**
  - **neutros:** Sinal `#0B0B0C` (fundo), Grafite `#17181A`, Linha `#2A2B2E`, Cinza médio `#8A8B8E`, Névoa `#A3A3A0`, Fósforo `#F2F2F0`;
  - **barras de 75%, uma por biblioteca:** Início `#C0C0C0`, Filmes `#C0C000`, Séries `#00C0C0`, Música `#00C000`, Fotos `#C000C0`, TV ao vivo `#C00000`, Livros `#0000C0` (use `#3B3BFF` em elementos pequenos).
  - A cor da biblioteca só aparece em sinais pequenos. O foco é sempre Fósforo.
- **Tipografia:** Archivo Expandida 800 em títulos, Archivo na interface, IBM Plex Mono em dados, tempos e rótulos (estes em caixa alta).
- **TV:** escala 2×, margem segura de 96 px nas laterais e 54 px em cima e embaixo, foco com borda Fósforo de 8 px.
- **Itens sem arte** usam a "capa gerada", descrita no manual.

**Relação com a CAPRA:** o Croma deixou de seguir as regras de marca expressiva da CAPRA (maluma, paleta pastel, Inter e endosso). A v0.2 (`croma-identidade/v0.2-capra/`) fica arquivada como referência. O repositório da CAPRA (https://github.com/Cintriano/Capra) continua sendo do usuário. Não o altere sem pedido.

**Conceitos do usuário:**
- barras de cor das TVs antigas;
- moldura da National Geographic, mas horizontal, como uma tela de TV;
- "croma" como luz e espectro (espectrometria, comprimentos de onda).

**Canvas de design:** https://claude.ai/artifact/AUKTY2yvnHh4ZYk1c7qpLi (tipo Design; páginas "v0.1 Barras" e "v0.2 Direções CAPRA"; arquivos em `project/` e `project/v02/`).
- Antes de publicar nele, leia o `croma-identidade/v0.1-barras/fontes/canvas.json`.
- No Windows, use caminhos longos (`C:\Users\<usuário>\...`), porque o caminho curto (como `DANILO~1.GAM` ou `CINTRA~1`) é bloqueado.

## Estado atual

| Item | Situação | Onde |
|---|---|---|
| Projeto dividido em repositórios próprios e publicados (privados) | Feito (05/11/2026) | veja "Repositórios" |
| Identidade v0.1 "Barras" | **Oficial** (05/11/2026): manual, logotipo em curvas, ícones do app e pranchas | `croma-identidade/v0.1-barras/` |
| Identidade v0.2 (CAPRA, direções A, B e C) | Arquivada | `croma-identidade/v0.2-capra/` |
| Servidor Jellyfin v12.4 portátil | Instalado e rodando na máquina CintraMan (Windows); o assistente inicial ainda não foi concluído. No Linux, não instalado | `croma-servidor/` |
| Tema "Croma" e marca no `croma-web` | Feito: paleta, fontes Archivo e IBM Plex Mono, cantos vivos, foco, logos, ícones, nome e textos | commit `e5f1c1a4c` na branch `croma`, publicado |
| Componentes e telas especiais da v0.1 (capa gerada, calibração, sem sinal, espectro no player) | Não iniciado | `croma-web` |
| Coleções por biblioteca e modo de exibição | Especificado, não implementado | `specs/colecoes.md` |
| Tags e editor de tags (vindos do v1) | Avaliado, com decisões em aberto | `specs/tags.md` |
| Varredura estruturada (com níveis) das bibliotecas caseiras | Formato em desenvolvimento pelo usuário | `specs/bibliotecas-caseiras.md` |
| `croma-tizen` e `croma-desktop` | Não iniciados (ícones, nomes, empacotamento) | `croma-tizen/`, `croma-desktop/` |
| `croma-android` | Criado (fork sem mudanças), implementação adiada | `croma-android/` |
| Repositórios na organização `Croma-plataform`, perfil `.github` e hub renomeado para `croma-doc` | Feito (07/11/2026) | veja "Repositórios" |

**Última sessão (07/11/2026, máquina Linux):** os repositórios foram transferidos da conta `Cintriano` para a organização `Croma-plataform`, a pasta do projeto passou a se chamar `Croma-plataform` foi criado o `croma-android`, o perfil da organização (`.github`, pasta `croma-org/`) foi publicado e o hub foi renomeado para `croma-doc`. Falta o usuário trocar o avatar da organização pelo site (ícone `croma-identidade/v0.1-barras/logos/app/mobile/icone-1024.png`). Antes (05–06/11) o projeto foi dividido em repositórios próprios (v1 arquivado, forks como repositórios comuns e privados).

**Próximos passos:**
1. O usuário conclui o assistente em http://localhost:8096: cria a conta de administrador (a senha é dele) e adiciona uma biblioteca de teste.
2. Implementar as coleções por biblioteca (`specs/colecoes.md`).
3. Implementar as tags (`specs/tags.md`), depois que o usuário responder às decisões em aberto.

**Na máquina CintraMan:** a pasta antiga ainda tem o layout anterior (`repos/`, `servidor/`, `identidade/`). Para migrar: dê `git pull` no hub, mova `repos/croma-*` para a raiz do hub (ajustando o `origin` para `https://github.com/Croma-plataform/<repo>.git`; o hub também muda de `origin`), renomeie a pasta para `Croma-plataform`, mova `servidor/jellyfin` e `servidor/dados` para dentro do `croma-servidor` e apague `repos/`, `servidor/` e `patches/`.

## Convenções

- **Especificações** de funcionalidades ficam em `specs/`, no hub, uma por arquivo. Detalhes de implementação ficam no README do repositório onde o código mora.
- **Identidade:** convenções de pastas, scripts geradores e renderização de pranchas estão no `croma-identidade/README.md`. Arquivos gerados por script não são editados à mão.
- **Croma v1 (`croma-v1`):** é só referência. Não o evolua; leve as funções para o v2. Para rodá-lo, entre na pasta, depois `npm install` e `npm run dev`. Os caminhos dele são relativos à raiz dele, inclusive `dados/`.
- **Não altere o repositório CAPRA** sem pedido explícito.
