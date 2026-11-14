# Pranchas a desenhar (módulo I01 e I02)

Descrição visual das telas que ainda não têm prancha. Cada uma diz onde a tela aparece, o que ela mostra, as medidas e os textos de exemplo. Depois de aprovadas, viram imagens em `croma-identidade/v0.1-barras/imagens/` e destravam o D12, o D13 e os acabamentos do D06 e do D01.

Regras que valem para todas (manual v0.1): cantos vivos; fundo Sinal `#0B0B0C` com cartões Grafite `#17181A`; títulos em Archivo Expandida 800; interface em Archivo; dados, tempos e rótulos em IBM Plex Mono em caixa alta; foco sempre Fósforo (moldura de 4 px no desktop, 8 px na TV); quadrado de 16 px na cor da seção ao lado de cada título de seção; textos em português do Brasil, caixa de frase, sem ponto final em botões e rótulos, números exatos ("faltam 3 h 12 min"). Tamanho de prancha: 1920 × 1080 (TV e player) e 1600 × 1000 (desktop), como as existentes.

Cores das seções (75%): Audiovisual amarelo `#C0C000`, Áudios verde `#00C000`, Leitura azul `#0000C0` (em elemento pequeno, `#3B3BFF`), Fotos magenta `#C000C0`.

---

## 1. Podcasts: aba e página do programa (Áudios, verde)

**Onde:** seção Áudios, aba "Podcasts" (ao lado de Músicas e Audiolivros), e a página de cada programa. Partem das pranchas 17 (galeria de música) e 21 (artista).

**1a. Aba Podcasts (galeria).** Grade de capas quadradas na moldura com a faixa de barras, como a galeria de álbuns. Embaixo de cada capa: nome do programa em Archivo 700 e, em mono, `12 EPISÓDIOS · 3 NOVOS`. O canto superior direito leva a etiqueta de episódios novos no padrão dos cartões (quadrado Fósforo com texto Sinal). Programas com episódio em andamento mostram uma linha de progresso de 4 px verde no pé da capa. Cabeçalho da seção: quadrado verde, "Áudios" em Archivo Expandida 800 e o rótulo mono `PODCASTS · 14 PROGRAMAS`.

**1b. Página do programa.** À esquerda, a capa grande (cerca de 360 px) na moldura grossa. À direita: rótulo mono `PODCAST · ÁUDIOS`, nome do programa em Archivo Expandida 800, autor em mono, descrição em até 4 linhas e dois botões: principal Fósforo "Ouvir o mais novo" e secundário Grafite "Seguir". Embaixo, a lista de episódios, **do mais novo ao mais antigo**, cada linha com:
- à esquerda a data em mono (`12 NOV 2026`);
- título em Archivo 700 e descrição curta em Névoa, uma linha;
- à direita a duração em mono (`48 MIN`) e o estado: não ouvido (nada), em andamento (barra de 4 px verde com "faltam 12 min"), ouvido (visto: quadrado verde com ✓ em Sinal e título em Cinza médio);
- linha em foco: fundo Grafite com moldura Fósforo e botão de ouvir.

**Estados a mostrar:** programa novo sem nenhum episódio ouvido; programa com um episódio pela metade; lista longa com "Mostrar episódios antigos"; programa sem capa (capa gerada).

---

## 2. Player falado: podcast e audiolivro (verde)

**Onde:** tela de reprodução de podcasts e audiolivros. Parte da prancha 18 (Tocando agora), **sem o analisador de espectro** (voz não tem equalizador) e com os controles do player de vídeo (prancha 11).

**Layout (1920 × 1080).** Capa quadrada grande à esquerda (cerca de 560 px) na moldura grossa. À direita:
- rótulo mono `EPISÓDIO 112 · NOME DO PROGRAMA` (podcast) ou `CAPÍTULO 4 DE 18 · AUTOR` (audiolivro);
- título em Archivo Expandida 800, até 2 linhas;
- **linha do tempo em espectro**, larga, com o que já foi ouvido em cores cheias e o resto a 22%; os capítulos são linhas escuras de 4 px; a cabeça é um traço Fósforo de 8 px; embaixo, à esquerda o tempo atual (`1:02:15`) e à direita o que falta (`−48:40`), em mono;
- linha de comandos: `−30 s`, `−15 s`, play/pausa grande, `+15 s`, `+30 s`;
- segunda linha de controles, em botões secundários: **velocidade** (`1,0×`; abre uma lista de 0,8× a 2× em passos de 0,1), **temporizador** (ícone de lua; opções "Fim do capítulo", "15 min", "30 min", "60 min", "Desligado"), **capítulos** e **fila**.
- Abaixo, a lista de capítulos (ou as notas do episódio), com o atual em Fósforo e o número do capítulo em verde.

**Estados a mostrar:** tocando; velocidade escolhida (`1,5×` com o tempo restante já corrigido: "faltam 32 min"); temporizador ativo (chip mono `DORMIR EM 14:20` verde); menu de velocidade aberto; audiolivro com capítulo longo; sem capítulos (só a linha do tempo, sem marcas). **Mini player** da tela inteira: igual ao da música, com o progresso em espectro de 3 a 4 px, mas com a velocidade ao lado do botão de pausa quando for diferente de 1×.

---

## 3. "Continuar ouvindo" (Início e resumo de Áudios)

**Onde:** fileira no Início (prancha 15, desktop) e no Resumo da seção Áudios.

Fileira horizontal de cartões largos (cerca de 360 × 120 px), cada um com capa quadrada pequena à esquerda, título em Archivo 700, autor em mono e uma barra de progresso de 4 px verde. Texto de tempo em mono, sempre exato: `FALTAM 3 H 12 MIN`. Cabeçalho da fileira com o quadrado verde e "Continuar ouvindo". Mostrar também o cartão em foco (moldura Fósforo) e a fileira com um só item.

---

## 4. Leitor de HQ e mangá (Leitura, azul)

**Onde:** abrir uma HQ ou um mangá na seção Leitura. Parte da prancha 27 (leitor de livros) e do tema Escuro.

**Layout (1920 × 1080).** A página ocupa o centro, sobre Sinal, **sem moldura nem margens decorativas**. Dois modos:
- **página dupla** (padrão no desktop): duas páginas lado a lado, com uma linha de 2 px Linha entre elas; a capa aparece sozinha, à direita no caso do mangá;
- **página única**: uma página, ajustada à altura ou à largura.

**Direção de leitura:** HQ da esquerda para a direita; **mangá da direita para a esquerda por padrão**, pelo subtipo da biblioteca. A direção aparece na barra de baixo com uma seta e o texto `LER ← DA DIREITA` ou `LER → DA ESQUERDA`.

**Barra de cima (some com o mouse parado):** título da obra e volume em Archivo 700, rótulo mono `VOL. 3 · P. 45 DE 180`, botão fechar. **Barra de baixo:** linha de progresso azul `#3B3BFF` de 4 px com a página atual marcada por um traço Fósforo de 8 px (invertida no mangá, acompanhando a direção); botões "Página dupla/única", "Ajustar", "Direção" e "Miniaturas". Passar o mouse na linha de progresso mostra a miniatura da página na moldura com o número em mono.

**Estados a mostrar:** página dupla de HQ; página dupla de mangá com a direção invertida; página única; miniaturas abertas (fita de páginas, a atual com borda Fósforo de 4 px); fim do volume com o botão "Próximo volume".

---

## 5. Resumo de cada seção (Áudios, Leitura, Fotos)

**Onde:** primeira aba de cada seção (hoje só o Audiovisual tem prancha, a 09 e a 15 mostram o desktop). Cada Resumo repete a estrutura do Audiovisual com a cor da seção.

Cabeçalho: quadrado da cor, nome da seção em Archivo Expandida 800 e rótulo mono com a contagem (`λ 540 nm · 1.336 FAIXAS · 54 PLAYLISTS`). Abas dos subtipos embaixo, a ativa com barra de 4 px da cor. Fileiras:
- **Áudios:** Continuar ouvindo, Álbuns recentes, Playlists, Podcasts com episódios novos.
- **Leitura:** Continuar lendo (`VOL. 3 · P. 45 DE 180`, progresso azul), Livros recentes, HQs, Mangás.
- **Fotos:** Álbuns recentes, "Neste dia" (fotos da mesma data em anos anteriores) e favoritas, com o quadrado magenta.

Mostrar também a seção **vazia** (biblioteca sem itens): moldura Linha tracejada de 2 px, texto "Nada aqui ainda" em Archivo 700 e a dica de adicionar uma pasta no painel.

---

## 6. Documentários (Audiovisual, amarelo)

**Onde:** subtipo "Documentários" da seção Audiovisual. Mesma galeria dos filmes (prancha 09), com três diferenças a desenhar:
- a etiqueta de tema no pôster (`NATUREZA`, `HISTÓRIA`, `CIÊNCIA`) em mono, no canto inferior, no lugar da edição;
- a aba "Temas" (no lugar de "Gêneros"), com a contagem por tema;
- documentários em série (várias partes) aparecem agrupados como séries, com `+6` de episódios.

---

## 7. Aba Imagem do painel de legendas e áudio (I02)

**Onde:** painel do player (prancha 36), ao lado de "Legendas" e "Áudio".

Lista curta de ajustes de imagem, sem jargão, cada um em linha com rótulo à esquerda e controle à direita, no padrão dos ajustes (prancha 34):
- **Proporção:** seleção segmentada `Original · Preencher · Esticar`;
- **Brilho:** controle deslizante com o valor em mono (`+10`);
- **Contraste:** igual;
- **Saturação:** igual;
- botão terciário (só contorno de 2 px) "Restaurar".

Decisão a registrar: no desktop, no mpv, esses ajustes mudam a imagem de verdade; no navegador, só a proporção funciona. Desenhar a aba com os quatro controles e uma variante só com a proporção.

---

## Ordem sugerida para gerar as imagens

1. Player falado e página do programa (destravam o D12).
2. Leitor de HQ e mangá (destrava o D13).
3. "Continuar ouvindo" e os Resumos das seções.
4. Documentários e a aba Imagem (acabamentos).
