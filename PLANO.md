# Plano de desenvolvimento

Atualizado em 08/11/2026. Este é o roteiro do Croma: o que já foi feito, onde estamos e a ordem das próximas etapas. As especificações de cada funcionalidade ficam em `specs/`.

## Onde estamos

| Área | Situação |
|---|---|
| Repositórios | Feito: 9 repositórios na organização `Croma-plataform`, documentação em `croma-doc`, perfil em `.github` |
| Identidade visual | Feito: v0.1 "Barras" oficial (manual, logotipo, ícones, pranchas). Vai precisar de uma revisão por causa das seções (fase 2) |
| Servidor | `croma-servidor` é fork do Jellyfin (branch `croma` na tag `v12.4`), compilado e rodando no Linux com o acervo de Filmes do usuário. Já tem o subtipo da biblioteca e a leitura do padrão Baú (filmes). Na máquina CintraMan ainda roda o binário oficial |
| Interface (`croma-web`) | Tema Croma aplicado (paleta, fontes, cantos vivos, foco, logos, nome e textos), campo "Conteúdo" no diálogo de biblioteca e TV ao vivo fora da interface. A navegação e as telas ainda são as do Jellyfin |
| TV (`croma-tizen`) | Fork sem mudanças. Tizen Studio, certificado e modo desenvolvedor da TV ainda não configurados |
| Desktop (`croma-desktop`) | Fork sem mudanças |
| Android (`croma-android`) | Fork sem mudanças, implementação adiada |
| Especificações | Seções Audiovisual, Áudios e Leitura (decididas), varredura do padrão Baú (filmes implementado), coleções (pronta), tags (decisões em aberto) |

**Em resumo:** a base está montada (repositórios, marca, tema e servidor próprio) e o Croma já roda no Linux com os 160 filmes do acervo, lidos do padrão Baú. Falta a identidade das seções, as telas próprias e a TV.

## Fases

### Fase 1 — Servidor de pé com mídia de teste

Objetivo: ter o Croma funcionando com um pouco de cada tipo de mídia, para testar todas as telas.

- [x] Concluir o assistente em http://localhost:8096 no Linux (08/11/2026)
- [x] Biblioteca de Filmes com o acervo real (`Black_hole/Filmes/movies`, 160 filmes), lida do padrão Baú (08/11/2026)
- [ ] Montar uma pasta de mídia de teste com um pouco de cada subtipo: filmes, uma série, um documentário, álbuns, um podcast, um audiolivro (M4B com capítulos), livros EPUB e PDF, uma HQ e um mangá (CBZ), fotos
- [ ] Criar uma biblioteca por subtipo (veja `specs/secoes.md`)
- [ ] Build do `croma-web` servido pelo servidor (`--webdir`, passo a passo em `croma-servidor/croma/README.md`). O `croma-web` v12.4 exige **Node 24 e npm 11**. No Linux o Node 24 está instalado (`node-24`), mas o comando `node` ainda aponta para o 22: `sudo dnf swap nodejs22-bin nodejs24-bin` resolve. Build e servidor juntos já funcionam no Linux (07/11/2026)
- [x] Servidor no Linux: script de inicialização equivalente ao `.ps1` (07/11/2026)

### Fase 2 — Seções e revisão da identidade

Objetivo: fechar a nova organização e atualizar o manual antes de desenhar telas em código.

- [x] Definir as seções e os subtipos: Audiovisual (filmes, séries, documentários), Áudios (músicas, podcasts, audiolivros), Leitura (livros, HQs, mangás); TV ao vivo fora do escopo (07/11/2026)
- [x] Decisões D1 (uma barra por seção), D2 (podcasts por pasta local), D3 (documentários em biblioteca própria); D5 (vídeos caseiros) adiada (07/11/2026)
- [x] D4: o subtipo é um campo da biblioteca no próprio servidor, com mudança no núcleo (07/11/2026)
- [x] O fork do servidor fica no próprio `croma-servidor` (07/11/2026)
- [x] Revisão do manual: cores por seção, ícones novos (seções e subtipos), navegação nas três plataformas, TV ao vivo marcada como fora do escopo; pranchas de ícones, desktop, mobile, música no mobile, início na TV e estados refeitas (08/11/2026)
- [ ] Pranchas novas: páginas das três seções (inclusive Documentários e a página de programa de podcast), player falado, leitor de HQ e mangá
- [x] Copiar os ícones novos para o `croma-web` (`src/assets/img/croma/icones/`, 08/11/2026)

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
- [x] Script de inicialização no Linux (`croma/scripts/iniciar-servidor.sh`, 07/11/2026). Falta baixar o `jellyfin-ffmpeg`; por enquanto roda com o ffmpeg do sistema
- [x] Catálogo de seções e subtipos, campo do subtipo nas opções da biblioteca, validação e padrão por tipo (07/11/2026)
- [x] Subtipo e seção nas visões do usuário, regra de agrupamento e endpoint do catálogo (07/11/2026)
- [x] Testes do servidor para o catálogo, a gravação, a validação e a API (07/11/2026)
- [x] Leitura do padrão Baú para Filmes: `metadata.json`, pôster e fundos, legendas em `metadata/subs/`, coleções de `collections/`; listas do JSON completas, sem somar as do TMDB (`specs/varredura-bau.md`, 08/11/2026)
- [x] Leitura do padrão Baú para Séries: série, episódios (pela lista `episodes`), pôster das temporadas, legendas `SNNENN_subtitle_*`, coleções (`specs/varredura-bau.md`, 08/11/2026)
- [ ] Padrão Baú para Músicas (documento aprovado em 08/11/2026)

### Fase 5 — Seções no `croma-web`

- [x] Tirar a TV ao vivo da interface, com o interruptor `cromaFeatures.liveTv` (`specs/secoes.md`, seção "TV ao vivo", 07/11/2026)
- [ ] Mapa "biblioteca → seção e subtipo", gravado no servidor, e a tela de ajuste
- [ ] Menu da TV, barra lateral do desktop e abas do celular com as seções. **Barra lateral do desktop feita** (08/11/2026, `SectionLinks.tsx`); faltam TV e celular
- [ ] Página de seção: resumo ("Continuar" e novidades) e abas por subtipo. **Audiovisual em andamento** (08/11/2026, `SectionTabs.tsx`): cabeçalho com a barra da seção e as abas Resumo, uma por biblioteca da seção (Filmes, Séries; cada uma abre a grade da sua biblioteca), Coleções e Gêneros. O **Resumo junta a seção** (08/11/2026, `SectionSummaryView.tsx`): "Continuar assistindo" de filmes e episódios numa fileira só, "A seguir", as novidades de cada biblioteca e as recomendações de filmes. Coleções e Gêneros ainda são os da biblioteca aberta
- [ ] **Audiovisual:** abas Filmes, Séries e Documentários (filmes e séries documentais juntos), detalhe do filme, detalhe da série com a fita de episódios. **Fita de episódios feita** (08/11/2026, `components/croma/episodeStrip/`): no detalhe da série, um segmento por episódio agrupado por temporada (visto, em andamento, novo, não visto), "Próximo: T1 E02", "1 de 26 vistos · 25 min restantes" e o kicker `SÉRIE · 3 TEMPORADAS`. Falta o resto do detalhe da série no visual do manual e o detalhe do episódio (prancha 29)
  - [x] Filmes: aba com grade e filtros (a do Jellyfin, sob o cabeçalho da seção)
  - [x] Detalhe do filme no visual do manual (prancha 28). **Feito:** moldura Fósforo no pôster e edição ao lado do título; (09/11/2026) *kicker* `■ FILME · DRAMA · THRILLER`, título em Archivo Expandida, progresso "parou em 30:00 · faltam 1h 49" na cor da seção, "Assistir" (Fósforo), "Do início" e "Trailer" (Grafite) e as ações em quadrados Grafite, embaixo das informações (vale também para série e episódio). Também (09/11/2026): sinopse acima do progresso e dos botões, sem o logo grande sobre o fundo, ★ para favoritar e os estados marcados (favorito, visto) na cor da seção. Também (09/11/2026) a faixa de baixo: Ficha técnica (direção, roteiro, elenco, estúdio, título original), Arquivo (vídeo, faixas de áudio, idiomas das legendas, tamanho e contêiner, e "● Reprodução direta neste aparelho" calculado pelo servidor com o perfil do aparelho) e Parecidos na biblioteca (4 pôsteres com o ano; na TV, o ↓ dos botões vai direto para eles). Saíram os campos de Vídeo, Áudio e Legendas embaixo dos botões (decisão do usuário, 09/11/2026): os dados ficam no bloco Arquivo e a troca de faixas, no player; a escolha de versão continua quando o filme tem mais de um arquivo. Também (09/11/2026): a seção fica destacada na barra lateral no detalhe (a biblioteca vem dos ancestrais do item). **Detalhe do filme concluído**
- [ ] **Áudios:** músicas (tocando agora com analisador), página de programa de podcast, audiolivros, player falado (pulos de 15/30 s, velocidade, capítulos, temporizador para dormir)
- [ ] **Leitura:** leitores com o visual do manual; mangá da direita para a esquerda por padrão
- [x] Campo "Conteúdo" (o subtipo) no diálogo de biblioteca do painel; tipos do SDK estendidos em `src/types/librarySubtype.ts` e `src/utils/librarySubtypes.ts` (07/11/2026)
- [x] Edição do filme (tag do Baú, por exemplo `Estendida`) como etiqueta ao lado do título, nos cartões (na linha do ano) e no detalhe (`specs/varredura-bau.md`, 08/11/2026). Lista de edições reconhecidas em `src/utils/editions.ts` (hoje só `Estendida`)
- [ ] Busca agrupada por seção

### Fase 6 — Coleções e tags

- [ ] Coleções por biblioteca e modo de exibição (`specs/colecoes.md`). Ajustar a spec para falar de seções quando a fase 2 terminar
- [ ] Usuário responde às decisões de `specs/tags.md`
- [ ] Tags e editor de tags

### Fase 7 — Telas e componentes especiais da v0.1

- [ ] Capa gerada para itens sem arte
- [ ] Linha do tempo em espectro no player e no mini player. **Player de vídeo feito** (09/11/2026, pranchas 11 e 12): kicker e título em cima, hora e "termina às", linha do tempo em espectro com os capítulos como linhas escuras e a cabeça de leitura Fósforo, "Capítulo 5 de 9" e "−1:28:00 · 2:43:52", botões ⏮ −10 ⏸ +30 ⏭ em quadrados Grafite, chips (resolução, HDR, áudio, "Reprodução direta" ou "Convertendo no servidor") e o balão da busca com tempo e capítulo. **Painel de legendas e áudio feito** (09/11/2026, prancha 36): listas de legendas e áudio lado a lado com as etiquetas (forçadas, SDH, BR, Atmos 7.1, comentários), estilo da legenda (tamanho P/M/G/GG, fundo Nenhum/Contorno/Caixa, atraso), vídeo pausado e escurecido. Falta a aba Imagem do painel. **Falta também:** próximo episódio e pular abertura, estado carregando (prancha 38, com o trecho já carregado na linha do tempo), miniatura na busca (depende de trickplay, que não pode ser gerado no acervo) e o mini player de música
- [ ] Analisador de espectro (música)
- [ ] Abertura, tela de calibração, descanso de tela e "Sem sinal"
- [ ] Avisos, carregamento e estados com o texto do manual

### Fase 8 — Desktop

- [ ] Marca no `croma-desktop`: nome, ícone `.ico`, instalador do Windows
- [ ] Barra de título própria e tela de conexão ao servidor
- [ ] Build e instalação na máquina CintraMan

### Fase 9 — Depois

- [ ] Podcasts por assinatura de feed (plugin próprio; `specs/secoes.md`, decisão D2)
- [ ] App Android (`croma-android`)
- [ ] **Verificação da qualidade dos arquivos** (pedido do usuário, 09/11/2026; só depois de terminar o core da plataforma): funcionalidades que conferem a qualidade dos arquivos do acervo. O escopo ainda vai ser definido com o usuário, e a spec vai para `specs/` quando a frente começar. O bloco Arquivo do detalhe do filme (codec, resolução, HDR, faixas, tamanho e modo de reprodução) já mostra parte desses dados

## Fora do escopo

- **TV ao vivo** (decisão do usuário, 07/11/2026): continua documentada no manual e em `specs/secoes.md`, mas não será feita por enquanto e sai da interface. A barra vermelha fica reservada para ela.
- **Android TV e iOS:** sem data.
- **Rolagem vertical (webtoon)** no leitor de quadrinhos.
- **Bibliotecas Vídeos e Galeria do acervo do usuário** (decisão do usuário, 09/11/2026): por privacidade, terão uma aplicação dedicada, fora do Croma. O Croma continua servindo fotos e vídeos com a varredura padrão do Jellyfin; só essas bibliotecas não entram nele.

## Decisões pendentes do usuário

| Onde | O quê |
|---|---|
| `specs/secoes.md` | D5 vídeos caseiros e clipes (adiada) |
| `specs/tags.md` | decisões listadas na spec |
