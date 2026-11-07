# Plano de desenvolvimento

Atualizado em 07/11/2026. Este é o roteiro do Croma: o que já foi feito, onde estamos e a ordem das próximas etapas. As especificações de cada funcionalidade ficam em `specs/`.

## Onde estamos

| Área | Situação |
|---|---|
| Repositórios | Feito: 9 repositórios na organização `Croma-plataform`, documentação em `croma-doc`, perfil em `.github` |
| Identidade visual | Feito: v0.1 "Barras" oficial (manual, logotipo, ícones, pranchas). Vai precisar de uma revisão por causa das seções (fase 2) |
| Servidor | `croma-servidor` é fork do Jellyfin (branch `croma` na tag `v12.4`), ainda sem mudanças. Na máquina CintraMan roda o binário oficial v12.4, **assistente inicial não concluído**. No Linux, nada instalado |
| Interface (`croma-web`) | Tema Croma aplicado: paleta, fontes, cantos vivos, foco, logos, nome e textos (commit `e5f1c1a4c`). Nenhuma tela própria ainda |
| TV (`croma-tizen`) | Fork sem mudanças. Tizen Studio, certificado e modo desenvolvedor da TV ainda não configurados |
| Desktop (`croma-desktop`) | Fork sem mudanças |
| Android (`croma-android`) | Fork sem mudanças, implementação adiada |
| Especificações | Seções Audiovisual, Áudios e Leitura (estrutura decidida, cores e detalhes em aberto), coleções (pronta), tags (decisões em aberto), bibliotecas caseiras (formato em desenvolvimento) |

**Em resumo:** a base está montada (repositórios, marca e tema). Ainda não rodamos o Croma de ponta a ponta com mídia de verdade, nem na TV.

## Fases

### Fase 1 — Servidor de pé com mídia de teste

Objetivo: ter o Croma funcionando com um pouco de cada tipo de mídia, para testar todas as telas.

- [ ] Concluir o assistente em http://localhost:8096 (conta de administrador; a senha é do usuário)
- [ ] Montar uma pasta de mídia de teste com um pouco de cada subtipo: filmes, uma série, um documentário, álbuns, um podcast, um audiolivro (M4B com capítulos), livros EPUB e PDF, uma HQ e um mangá (CBZ), fotos
- [ ] Criar uma biblioteca por subtipo (veja `specs/secoes.md`)
- [ ] Build do `croma-web` servido pelo servidor (`--webdir`, passo a passo em `croma-servidor/croma/README.md`). O `croma-web` v12.4 exige **Node 24 e npm 11**; no Linux há só o Node 22 (`sudo dnf install nodejs24 nodejs24-npm`)
- [ ] Servidor no Linux: script de inicialização equivalente ao `.ps1`, para desenvolver nas duas máquinas

### Fase 2 — Seções e revisão da identidade

Objetivo: fechar a nova organização e atualizar o manual antes de desenhar telas em código.

- [x] Definir as seções e os subtipos: Audiovisual (filmes, séries, documentários), Áudios (músicas, podcasts, audiolivros), Leitura (livros, HQs, mangás); TV ao vivo fora do escopo (07/11/2026)
- [x] Decisões D1 (uma barra por seção), D2 (podcasts por pasta local), D3 (documentários em biblioteca própria); D5 (vídeos caseiros) adiada (07/11/2026)
- [x] D4: o subtipo é um campo da biblioteca no próprio servidor, com mudança no núcleo (07/11/2026)
- [x] O fork do servidor fica no próprio `croma-servidor` (07/11/2026)
- [ ] Revisão do manual: cores por seção, ícones novos (seções e subtipos), navegação nas três plataformas, TV ao vivo marcada como fora do escopo
- [ ] Pranchas novas: páginas das três seções (inclusive Documentários e a página de programa de podcast), player falado, leitor de HQ e mangá
- [ ] Copiar os ícones novos para o `croma-web`

### Fase 3 — Croma na TV

Objetivo: ver o Croma rodando na QN90B o quanto antes, porque tudo precisa ser testado no modo TV. Pode correr em paralelo com a fase 2.

- [ ] Tizen Studio, certificado Samsung e modo desenvolvedor na TV
- [ ] Marca no `croma-tizen`: nome, ids, ícone e tile
- [ ] Empacotar o `dist/` do `croma-web` no `.wgt` e instalar na TV
- [ ] Conferir o tema atual na TV: escala 2×, margens seguras, foco de 8 px, fontes

### Fase 4 — Servidor próprio (fork do Jellyfin)

Objetivo: compilar o servidor a partir do código, para poder mudar o núcleo. Desenho em `specs/secoes.md`, "Modelo no servidor".

- [x] Instalar o .NET SDK 10 no Linux (10.0.403 em `~/.dotnet`, 07/11/2026)
- [ ] Instalar o .NET SDK 10 mais recente no Windows (máquina CintraMan)
- [x] Criar o fork do Jellyfin a partir da tag `v12.4`, branch `croma`, no `croma-servidor` (07/11/2026)
- [x] Build, testes e execução do servidor compilado no Linux (07/11/2026)
- [ ] Build e execução na máquina CintraMan, no lugar do binário oficial (com o `jellyfin-ffmpeg`)
- [ ] Script de inicialização no Linux (com o `jellyfin-ffmpeg`)
- [x] Catálogo de seções e subtipos, campo do subtipo nas opções da biblioteca, validação e padrão por tipo (07/11/2026)
- [x] Subtipo e seção nas visões do usuário, regra de agrupamento e endpoint do catálogo (07/11/2026)
- [x] Testes do servidor para o catálogo, a gravação, a validação e a API (07/11/2026)

### Fase 5 — Seções no `croma-web`

- [ ] Tirar a TV ao vivo da interface: menu, fileiras da tela inicial, busca e painel de administração (`specs/secoes.md`, seção "TV ao vivo")
- [ ] Mapa "biblioteca → seção e subtipo", gravado no servidor, e a tela de ajuste
- [ ] Menu da TV, barra lateral do desktop e abas do celular com as seções
- [ ] Página de seção: resumo ("Continuar" e novidades) e abas por subtipo
- [ ] **Audiovisual:** abas Filmes, Séries e Documentários (filmes e séries documentais juntos), detalhe do filme, detalhe da série com a fita de episódios
- [ ] **Áudios:** músicas (tocando agora com analisador), página de programa de podcast, audiolivros, player falado (pulos de 15/30 s, velocidade, capítulos, temporizador para dormir)
- [ ] **Leitura:** leitores com o visual do manual; mangá da direita para a esquerda por padrão
- [ ] Campo "Subtipo" no diálogo de biblioteca do painel; tipos do SDK estendidos
- [ ] Busca agrupada por seção

### Fase 6 — Coleções e tags

- [ ] Coleções por biblioteca e modo de exibição (`specs/colecoes.md`). Ajustar a spec para falar de seções quando a fase 2 terminar
- [ ] Usuário responde às decisões de `specs/tags.md`
- [ ] Tags e editor de tags

### Fase 7 — Telas e componentes especiais da v0.1

- [ ] Capa gerada para itens sem arte
- [ ] Linha do tempo em espectro no player e no mini player
- [ ] Analisador de espectro (música)
- [ ] Abertura, tela de calibração, descanso de tela e "Sem sinal"
- [ ] Avisos, carregamento e estados com o texto do manual

### Fase 8 — Desktop

- [ ] Marca no `croma-desktop`: nome, ícone `.ico`, instalador do Windows
- [ ] Barra de título própria e tela de conexão ao servidor
- [ ] Build e instalação na máquina CintraMan

### Fase 9 — Depois

- [ ] Bibliotecas caseiras com varredura estruturada: plugin C# no `croma-servidor` (`specs/bibliotecas-caseiras.md`, quando o formato estiver definido). Usa o .NET SDK da fase 4
- [ ] Podcasts por assinatura de feed (plugin próprio; `specs/secoes.md`, decisão D2)
- [ ] App Android (`croma-android`)

## Fora do escopo

- **TV ao vivo** (decisão do usuário, 07/11/2026): continua documentada no manual e em `specs/secoes.md`, mas não será feita por enquanto e sai da interface. A barra vermelha fica reservada para ela.
- **Android TV e iOS:** sem data.
- **Rolagem vertical (webtoon)** no leitor de quadrinhos.

## Decisões pendentes do usuário

| Onde | O quê |
|---|---|
| `specs/secoes.md` | D5 vídeos caseiros e clipes (adiada) |
| `specs/tags.md` | decisões listadas na spec |
| `specs/bibliotecas-caseiras.md` | formato da estrutura de pastas |
