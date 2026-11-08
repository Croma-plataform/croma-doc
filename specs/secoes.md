# Seções: Audiovisual, Áudios e Leitura (especificação, 07/11/2026)

O manual v0.1 tem uma página por tipo de biblioteca: Filmes, Séries, Música, Fotos, TV ao vivo e Livros. O Croma passa a agrupar por **forma de consumo**.

**Decisão do usuário (07/11/2026):**

| Seção | Subtipos |
|---|---|
| **Audiovisual** | Filmes, Séries, Documentários |
| **Áudios** | Músicas, Podcasts, Audiolivros |
| **Leitura** | Livros, HQs, Mangás |

- A lista de subtipos é **aberta**: novos subtipos podem entrar depois, então a implementação não pode fixá-los no código.
- **Fotos** continua como seção própria, como está no manual.
- **TV ao vivo fica fora do escopo** por enquanto: continua documentada, mas sai da interface (veja "TV ao vivo" no fim).

O manual (`croma-identidade/v0.1-barras/MANUAL.md`) precisa de uma revisão para refletir isto (cores, ícones, navegação e as telas novas). Até lá, esta spec vale onde os dois discordarem.

## Conceito: seção, subtipo e biblioteca

- **Biblioteca** é o que existe no servidor Jellyfin: uma pasta com um tipo (`movies`, `tvshows`, `music`, `books`, `photos`...). Pode haver várias do mesmo tipo.
- **Seção** é a página do Croma.
- **Subtipo** é a divisão dentro da seção (uma aba). Cada biblioteca pertence a **uma seção e um subtipo**.

| Seção | Subtipo | Tipo de biblioteca no Jellyfin | Itens |
|---|---|---|---|
| Audiovisual | Filmes | `movies` | `Movie` |
| Audiovisual | Séries | `tvshows` | `Series`, `Season`, `Episode` |
| Audiovisual | Documentários | `movies` ou `tvshows` (veja abaixo) | `Movie` ou `Series` |
| Áudios | Músicas | `music` | `MusicAlbum`, `MusicArtist`, `Audio` |
| Áudios | Podcasts | `music` ou `books` (veja abaixo) | `Audio` ou `AudioBook` |
| Áudios | Audiolivros | `books` com arquivos de áudio | `AudioBook` |
| Leitura | Livros | `books` | `Book` (EPUB, PDF) |
| Leitura | HQs | `books` | `Book` (CBZ, CBR, CBT, CB7) |
| Leitura | Mangás | `books` | `Book` (CBZ, CBR, CBT, CB7) |
| Fotos | — | `photos` | `Photo`, `PhotoAlbum` |

- O Croma deduz o subtipo pelo tipo quando dá (`movies` → Filmes, `music` → Músicas) e pede ao usuário quando não dá: uma biblioteca `books` pode ser Livros, HQs, Mangás, Audiolivros ou Podcasts.
- **Uma biblioteca por subtipo** (por exemplo, "Mangás" separada de "HQs"). O Jellyfin não guarda a diferença entre HQ e mangá: o leitor de metadados lê o campo `Manga` do `ComicInfo.xml`, mas descarta (o código diz "Jellyfin has no manga flag"). Por isso o subtipo vem da biblioteca.
- A configuração "biblioteca → seção e subtipo" fica **no servidor**, para valer igual no desktop, na TV e no celular (mesma regra das coleções em `specs/colecoes.md`). O desenho está em "Modelo no servidor".

## Estrutura comum das seções

O mesmo esqueleto nas três, para a TV ficar previsível no controle remoto:

1. **Cabeçalho:** ícone e nome da seção, com a barra na cor dela.
2. **Abas:** a primeira é o **Resumo**; depois uma aba por subtipo; por fim as abas de apoio (Coleções, Gêneros).
3. **Resumo:** fileiras horizontais. "Continuar" sempre primeiro, depois as novidades de cada subtipo.
4. **Aba de subtipo:** grade com filtros e ordenação.

- Subtipo sem biblioteca não mostra aba. Seção sem biblioteca some do menu.
- Nunca misturar pôster vertical e capa quadrada na mesma fileira (regra das coleções). Cada fileira é de um subtipo, ou de subtipos com a mesma proporção.
- O Jellyfin já separa "Continuar assistindo" (vídeo), "Continuar ouvindo" (áudio) e "Continuar lendo" (livros) na tela inicial. Cada seção usa a fileira correspondente, filtrada pelas bibliotecas dela.

## Audiovisual

| Aba | Conteúdo |
|---|---|
| Resumo | Continuar assistindo (filmes, episódios e documentários) · Próximos episódios · Filmes adicionados · Séries com episódios novos · Documentários adicionados |
| Filmes | grade 2:3; filtros de gênero, ano, visto e resolução |
| Séries | grade 2:3 com a etiqueta `+2` de episódios novos |
| Documentários | grade 2:3, filmes e séries documentais juntos, com a etiqueta de tipo (FILME ou SÉRIE) |
| Coleções | as coleções da seção (`specs/colecoes.md`) |
| Gêneros | gêneros dos três subtipos, com contagem por subtipo |

- **Telas do manual que continuam valendo:** galeria, detalhe do filme, detalhe da série com a fita de episódios, detalhe do episódio e player com a linha do tempo em espectro.
- **Documentários:** o detalhe e o player são os mesmos dos filmes e das séries; só muda onde aparecem.

## Áudios

| Aba | Conteúdo |
|---|---|
| Resumo | Continuar ouvindo (audiolivros e episódios de podcast pela metade) · Tocadas recentemente · Episódios novos · Álbuns adicionados |
| Músicas | álbuns, artistas, playlists, gêneros e faixas (as abas que o Jellyfin já tem) |
| Podcasts | programas (capa 1:1) → página do programa com os episódios, do mais novo ao mais antigo, com "ouvido" e progresso |
| Audiolivros | capas 1:1; autores e séries de livros |

### Dois players

- **Músicas (tocando agora):** o do manual: capa na moldura, analisador de espectro, fila e mini player.
- **Falado (podcasts e audiolivros):** a pessoa volta depois e quer saber onde parou.
  - posição salva sempre; "Continuar" mostra "faltam 3 h 12 min";
  - pular 15 s para trás e 30 s para frente;
  - velocidade de 0,8× a 2×;
  - capítulos (audiolivro) ou notas do episódio (podcast);
  - temporizador para dormir: fim do capítulo, 15, 30 ou 60 min;
  - linha do tempo em espectro com os capítulos marcados, sem analisador.
- O mini player é o mesmo para os dois.

## Leitura

| Aba | Conteúdo |
|---|---|
| Resumo | Continuar lendo ("vol. 3 · p. 45 de 180") · Adicionados recentemente, por subtipo |
| Livros | grade 2:3; autores e séries |
| HQs | grade 2:3, agrupada por série, com os volumes ou edições em ordem |
| Mangás | grade 2:3, agrupada por série, com os volumes em ordem |

| Subtipo | Formatos | Leitor do `croma-web` | O que o Croma define |
|---|---|---|---|
| Livros | EPUB | `bookPlayer` | temas Escuro e Papel, corpo de 32 px na TV, coluna de 1040 px, progresso azul (manual) |
| Livros | PDF | `pdfPlayer` | página inteira com zoom; mesmo cabeçalho e progresso do EPUB |
| HQs | CBZ, CBR, CBT, CB7 | `comicsPlayer` | página a página, da **esquerda para a direita**; página dupla na TV e no desktop |
| Mangás | CBZ, CBR, CBT, CB7 | `comicsPlayer` | igual às HQs, mas da **direita para a esquerda** por padrão |

- Na TV, as setas do controle seguem a direção de leitura: no mangá, a seta da esquerda avança.
- Itens sem arte usam a capa gerada do manual (2:3).
- Fora do escopo agora: rolagem vertical (webtoon).

## Navegação

| Plataforma | Hoje (manual v0.1) | Novo |
|---|---|---|
| TV (menu no topo) | Início, Filmes, Séries, Música, Fotos, TV ao vivo, Livros | Início, Audiovisual, Áudios, Leitura, Fotos |
| Desktop (barra lateral) | as 7 bibliotecas | as 5 seções; a ativa abre os subtipos embaixo dela |
| Mobile (5 abas) | Início, Filmes, Séries, Música, Mais | Início, Audiovisual, Áudios, Leitura, Mais (Fotos dentro de Mais) |

- As teclas coloridas do controle continuam como atalho, na ordem das barras.
- **Busca:** resultados agrupados por seção e, dentro dela, por subtipo.

## Cores (decidido, D1)

A regra "uma barra por biblioteca" vira **uma barra por seção**:

| Barra | HEX | Hoje | Proposta |
|---|---|---|---|
| Branco | `#C0C0C0` | Início | Início |
| Amarelo | `#C0C000` | Filmes | **Audiovisual** |
| Ciano | `#00C0C0` | Séries | livre |
| Verde | `#00C000` | Música | **Áudios** |
| Magenta | `#C000C0` | Fotos | Fotos |
| Vermelho | `#C00000` | TV ao vivo | reservado para a TV ao vivo, quando voltar |
| Azul | `#0000C0` / `#3B3BFF` | Livros | **Leitura** |

- Os subtipos se diferenciam pelo **ícone e pelo rótulo**, sem cor própria. A fita de episódios das séries passa de ciano para amarelo.
- A faixa de 7 barras do logotipo e da capa gerada não muda: ela é o padrão de teste, não a lista de seções.
- **Ícones:** as seções reaproveitam os atuais (claquete para Audiovisual, notas para Áudios, lombadas para Leitura). Os subtipos ganham ícones novos, sem acento de cor: filme, série, documentário, nota, microfone (podcast), fone com livro (audiolivro), livro, balão de fala (HQ) e balão com traços de velocidade (mangá). Gerados pelo `fontes/gerar_icones.py` do `croma-identidade`.

## O que está faltando

Comparação entre o que o Jellyfin v12.4 (servidor e `croma-web`) já faz e o que cada subtipo precisa.

| Subtipo | O Jellyfin já tem | Falta |
|---|---|---|
| Filmes | tudo: biblioteca, metadados, detalhe, player | só o visual do Croma |
| Séries | tudo, inclusive "Próximos episódios" | só o visual (fita de episódios) |
| Documentários | nada específico: não existe tipo "documentário" | o subtipo vindo da biblioteca, a aba que junta filmes e séries documentais, e a regra de não repetir esses itens em Filmes e Séries |
| Músicas | tudo: álbuns, artistas, playlists, letras | só o visual (tocando agora, analisador, capas geradas de playlist) |
| Podcasts | **nada nativo**: não assina feeds RSS nem baixa episódios | a origem dos episódios (decisão D2), a página de programa e o player falado |
| Audiolivros | itens `AudioBook` em bibliotecas de livros, leitura de capítulos do arquivo, "Continuar ouvindo", velocidade no player de áudio, tempo de pulo configurável | o player falado (pulos de 15/30 s como padrão, capítulos visíveis, temporizador para dormir) e a aba em Áudios |
| Livros | leitor EPUB e PDF, metadados lidos do próprio arquivo (OPF do EPUB), "Continuar lendo" | o visual do leitor (temas, medidas, progresso); o servidor não busca metadados de livros na internet, só guarda links (Google Books, ISBN) |
| HQs | leitor de quadrinhos, metadados lidos do arquivo (`ComicInfo.xml` ou ComicBookInfo) | agrupamento por série na grade, página dupla |
| Mangás | o mesmo leitor das HQs, com a chave manual de direção | direção da direita para a esquerda como padrão do subtipo (o Jellyfin descarta a marcação de mangá do arquivo) |
| Todas | bibliotecas por tipo, "Continuar" por tipo de mídia | o mapa biblioteca → seção e subtipo, a tela de ajuste dele, o menu e as páginas das seções |

### Documentários

O Jellyfin não tem tipo "documentário". Um filme documental é um `Movie`; uma série documental é uma `Series`. Decidido (D3): **bibliotecas próprias.**

- **Bibliotecas próprias (escolhido):** uma biblioteca `movies` e/ou uma `tvshows` marcadas como subtipo Documentários. Os itens delas aparecem só em Documentários, não em Filmes nem em Séries.
- **Alternativa descartada:** usar o gênero "Documentário" que vem dos metadados (TMDb). Não exige separar pastas, mas depende da qualidade dos metadados e o item apareceria nos dois lugares.

### Podcasts

Três caminhos. Decidido (D2): **caminho 1 agora, caminho 3 depois.**

1. **Pasta local:** os episódios são baixados por outro programa e ficam numa biblioteca marcada como Podcasts. O Croma só exibe. É o mais simples.
2. **Plugin de canal de terceiros:** expõe feeds como "canais" do Jellyfin. Depende de plugin externo e o progresso funciona mal.
3. **Plugin próprio no `croma-servidor`:** assina os feeds, baixa os episódios para uma pasta e o Jellyfin os indexa. É o mais completo e exige C# (junto com o plugin das bibliotecas caseiras).


## TV ao vivo (fora do escopo)

**Decisão do usuário (07/11/2026):** a TV ao vivo não será feita por enquanto.

- O que o manual define (selo AO VIVO, guia, canal fora do ar, troca de canal) **continua documentado**, para quando ela voltar.
- **Sai da interface do `croma-web`:**
  - o item "TV ao vivo" do menu, da barra lateral e das abas;
  - as fileiras "No ar agora" e "Gravações" da tela inicial e das opções da tela inicial;
  - os grupos de canais e programas na busca;
  - a seção "TV ao vivo" do painel de administração (sintonizadores e guia).
- No servidor, basta não configurar sintonizador nem guia: sem sintonizador, o servidor não devolve a visão "TV ao vivo".

**Implementado (07/11/2026)** no `croma-web` com um interruptor só, `cromaFeatures.liveTv = false` (`src/constants/cromaFeatures.ts`). O código da TV ao vivo continua lá; desligado, o interruptor esconde:

- a seção "TV ao vivo" do painel de administração (sintonizadores, guia e gravações). Sem ela não dá para configurar um sintonizador, e o servidor nunca devolve a visão de TV ao vivo para o menu, a tela inicial e a busca;
- as fileiras "TV ao vivo" e "Gravações ativas" da tela inicial;
- essas duas opções nas preferências da tela inicial.

Para a TV ao vivo voltar: `liveTv: true`.
- A barra vermelha fica reservada para ela.

## Modelo no servidor (D4, decidido)

**Decisão do usuário (07/11/2026):** a solução segue as boas práticas, sem atalhos. Se for preciso mudar o núcleo do servidor, ele é mudado. Por isso o subtipo **é um dado da biblioteca no próprio servidor**, e não uma configuração guardada à parte pelos clientes.

### Por que não usar as preferências de exibição

As preferências de exibição do Jellyfin são para gostos do usuário (ordenação, modo de exibição). O subtipo é um fato sobre a biblioteca, igual para todos os usuários. Guardá-lo ali o deixaria fora do modelo da biblioteca: o painel de administração não o mostraria, e nada no servidor o validaria.

### Por que não criar tipos novos de biblioteca

Outra opção seria acrescentar `documentaries`, `podcasts`, `manga` etc. ao `CollectionType` do Jellyfin. Isso mistura duas coisas diferentes:

- o **tipo** (`movies`, `tvshows`, `music`, `books`) diz **como o servidor lê os arquivos**: quais resolvedores e quais provedores de metadados usa. Um mangá e um livro são lidos do mesmo jeito; um documentário e um filme também;
- o **subtipo** diz **o que é o conteúdo** e onde ele aparece no Croma.

Tipos novos obrigariam a mexer em dezenas de pontos do servidor que decidem pelo tipo (resolvedores, provedores, tarefas) só para repetir o comportamento de um tipo que já existe. Cada subtipo novo repetiria o trabalho.

### Desenho

1. **Catálogo de seções e subtipos no servidor.** Uma lista definida no código do servidor: cada subtipo tem um id (`filmes`, `series`, `documentarios`, `musicas`, `podcasts`, `audiolivros`, `livros`, `hqs`, `mangas`, `fotos`), a seção a que pertence, os tipos de biblioteca compatíveis e se é o padrão de algum tipo. Acrescentar um subtipo é acrescentar uma entrada.
2. **Campo novo nas opções da biblioteca** (`LibraryOptions`): o id do subtipo. Ele é gravado junto com as outras opções da biblioteca (`options.xml`), sem tabela nova nem migração de banco.
3. **Validação:** o servidor recusa um subtipo incompatível com o tipo (por exemplo, Mangás numa biblioteca `movies`).
4. **Padrão:** sem subtipo escolhido, vale o padrão do tipo (`movies` → Filmes, `tvshows` → Séries, `music` → Músicas, `books` → Livros, `photos` → Fotos). Bibliotecas antigas continuam funcionando.
5. **API:**
   - o subtipo vai nas opções da biblioteca, que o painel de administração já lê e grava;
   - o subtipo e a seção também vão no item de cada biblioteca que o usuário enxerga (as "visões" da tela inicial). Isso é necessário porque a lista de bibliotecas com as opções é só para administradores;
   - um endpoint devolve o catálogo de seções e subtipos, para os clientes não repetirem a lista no código deles.
6. **Painel de administração** (`croma-web`): o diálogo de criar e editar biblioteca ganha o campo "Subtipo", filtrado pelo tipo escolhido.

### Onde fica o código e como acompanhar o Jellyfin

- O servidor passa a ser um **fork do Jellyfin** a partir da tag `v12.4`, com a branch `croma`, como os outros forks. O binário oficial deixa de ser usado.
- Regras para o fork continuar fácil de atualizar:
  - mudanças pequenas e localizadas; o que for novo fica em arquivos próprios (nos namespaces do Jellyfin correspondentes);
  - commits separados por funcionalidade, com mensagem clara;
  - a cada versão nova do Jellyfin, a branch `croma` é rebaseada na tag nova e o `croma-web` sobe junto (as versões continuam casadas).
- Os campos novos não existem nos tipos do SDK do Jellyfin usado pelo `croma-web` (`@jellyfin/sdk`). O `croma-web` estende esses tipos num arquivo próprio, em vez de usar `any`.
- **Núcleo ou plugin:** muda-se o núcleo quando muda o modelo de dados ou um comportamento central (como o subtipo). Funcionalidades independentes que o Jellyfin prevê como extensão continuam como plugin, porque esse é o mecanismo certo para elas (por exemplo, a assinatura de podcasts, que é uma tarefa agendada que baixa arquivos).
- **Exige o .NET SDK 10 mais recente** (detalhes em `croma-servidor/croma/README.md`).

### Implementação (07/11/2026)

Feito no `croma-servidor`, com testes. Nomes na API (em inglês, como o resto do Jellyfin):

- subtipos: `Movies`, `Series`, `Documentaries`, `Music`, `Podcasts`, `Audiobooks`, `Books`, `Comics`, `Manga`, `Photos`;
- seções: `Audiovisual`, `Audio`, `Reading`, `Photos`;
- `LibraryOptions.Subtype` (opções da biblioteca), `BaseItemDto.LibrarySubtype` e `BaseItemDto.LibrarySection` (visões do usuário), `GET /Library/Subtypes` (catálogo).

Descobertas da implementação:

- O Jellyfin não tem tipo "fotos" para criar biblioteca: as fotos usam `homevideos` ("vídeos caseiros e fotos"). Por enquanto o padrão de `homevideos` é Fotos; os vídeos caseiros continuam adiados (D5).
- O agrupamento de bibliotecas (a opção do usuário que junta várias bibliotecas de filmes numa visão "Filmes") só considera bibliotecas com o subtipo padrão. Sem isso, uma biblioteca de documentários do tipo `movies` entraria na visão agrupada de filmes.
- Podcasts são aceitos em bibliotecas `books` (recomendado, porque o Jellyfin trata os arquivos como audiolivros, com posição salva) ou `music`.

## Decisões

Decididas pelo usuário em 07/11/2026:

- **D1. Cores:** uma barra por seção, como na tabela de cores, com o ciano livre e o vermelho reservado para a TV ao vivo.
- **D2. Podcasts:** pasta local agora; plugin próprio no `croma-servidor` depois.
- **D3. Documentários:** bibliotecas próprias (`movies` e/ou `tvshows` marcadas como Documentários).
- **D4. Mapa de seções:** o subtipo é um campo da biblioteca no próprio servidor, com mudança no núcleo (veja "Modelo no servidor").
- **D5. Vídeos caseiros e clipes:** adiado. O foco agora são as três seções decididas.

Adiada:

- **D5 (adiado). Vídeos caseiros e clipes** (`homevideos`, `musicvideos`): vídeos caseiros em Fotos (como "memórias") ou numa seção própria com o ciano; clipes em Audiovisual ou em Áudios/Músicas. Volta quando a spec das bibliotecas caseiras avançar.

## Implementação (resumo)

- **Servidor (fork do Jellyfin):** catálogo de seções e subtipos, campo do subtipo nas opções da biblioteca, validação, subtipo e seção nas visões do usuário, endpoint do catálogo.
- **`croma-web`:**
  - tirar a TV ao vivo da interface;
  - campo "Subtipo" no diálogo de biblioteca do painel e os tipos do SDK estendidos;
  - menu da TV, barra lateral e abas do celular com as seções;
  - página de seção (Resumo e abas), inclusive Documentários juntando filmes e séries;
  - página de programa de podcast e player falado;
  - direção de leitura padrão por subtipo no `comicsPlayer`.
- **`croma-identidade`:** revisão do manual (cores, ícones, navegação, TV ao vivo fora do escopo) e pranchas das três seções, do player falado e dos leitores.
