# Varredura do padrão Baú (especificação, 08/11/2026)

O acervo do usuário já é organizado num padrão próprio, o **Baú**, documentado no repositório **DL_HERMES** (`~/Documentos/Projetos/Codes/DL_HERMES`). Cada item guarda os seus dados ao lado do arquivo de mídia: `metadata/metadata.json`, `metadata/images/` e `metadata/subs/`. O Croma lê esse padrão direto, sem depender da identificação pela internet.

- **Fonte da verdade:** o padrão é definido no DL_HERMES. Este documento só diz como o servidor lê o padrão. Se os dois divergirem, vale o DL_HERMES, e o leitor precisa ser corrigido.
- **Situação:** só **Filmes** está aprovado e testado (`docs/bibliotecas/filmes.md`, `schema_version` 2). Séries, Músicas, Vídeos e Galeria entram quando os documentos deles estiverem prontos.
- **O servidor só lê:** nada é gravado nas pastas do acervo. Quem escreve nelas são os scripts e pipelines do Baú.

## Filmes

Biblioteca do tipo `movies` apontando para `Filmes/movies/` (como no Plex). Cada `movies/Título (Ano)/` tem o vídeo e `metadata/`.

| O que | De onde | Para onde (servidor) |
|---|---|---|
| Título, título original, ano, sinopse | `title`, `original_title`, `year`, `description` | nome, título original, ano, sinopse |
| Lançamento | `release_date` | data de estreia |
| Classificação | `content_rating` (`L`, `10`…`18`) | `BR-14` etc. (mesma forma do provedor TMDB; o servidor já tem a tabela do Brasil) |
| Idioma original | `original_language` | idioma original |
| Gêneros e tags | `tags` (uma lista só, D29) | os gêneros de filme do TMDB em pt-BR viram **gêneros**; o resto (`Super Herói`, `Marvel`, `De época`…) vira **tags** |
| Direção, roteiro, elenco | `directors`, `writers`, `cast` | pessoas (elenco na ordem do arquivo, com o personagem) |
| Produtoras, países | `studios`, `countries` | estúdios, locais de produção (nome do país) |
| IDs | `uuid`, `imdb_id`, `tmdb_id`, `tmdb_collection.id` | IDs externos `Bau`, `Imdb`, `Tmdb`, `TmdbCollection` |
| Saga do TMDB | `tmdb_collection.name` | nome da coleção do TMDB (usada pela opção "agrupar filmes em coleções automaticamente", se ligada) |
| Pôster, fundos | `metadata/images/poster.*`, `background.*`, `extra.*` (`.jpg`, `.png`, `.webp`) | imagem principal; fundo e, se houver, um segundo fundo |
| Legendas | `metadata/subs/<Título (Ano)>_subtitle_<idioma>.srt` | legenda externa com o idioma (`pt-br` vira Português (Brasil)); `_forced` no fim marca forçada |

- **Prioridade:** o leitor "Baú" roda antes dos provedores da internet. O que o JSON tem prevalece; o TMDB só completa campos vazios (nota da crítica, slogan) e acrescenta IDs e fotos às pessoas que o JSON já lista. Com os IDs do JSON, o TMDB nunca identifica o filme errado. Quem quiser o acervo 100% local desliga os provedores da internet nas opções da biblioteca.
- **Listas completas:** gêneros, tags, produtoras e países do JSON são a lista inteira. Por padrão o servidor **soma** as listas de todos os provedores (o TMDB acrescentaria as palavras-chave dele, em inglês, às tags). Para isso foi criada a interface `IAuthoritativeMetadataProvider` no núcleo: um leitor local declara quais listas estão completas, e nem a internet nem os dados antigos do item acrescentam nada a elas.
- **Conferência:** se o JSON tiver `files`, ele precisa listar o vídeo; senão é ignorado (proteção contra uma pasta com o JSON de outro filme). JSON inválido ou de outra `schema_version` é ignorado e registrado no log.
- **Atualização:** quando o `metadata.json` muda, a próxima varredura relê o filme sozinha.

## Coleções

`Filmes/collections/<Nome>/collection.json` (pasta irmã de `movies/`) vira uma coleção do servidor a cada **varredura da biblioteca** (não na "atualização de metadados", que não roda as tarefas pós-varredura):

- encontrada de novo pelo `uuid`, então renomear a pasta ou o nome não duplica a coleção;
- nome, descrição, tags, pôster e fundo vêm do arquivo;
- os itens são os filmes com os `uuid` de `items`. **O arquivo manda:** um filme posto na coleção à mão sai na próxima varredura;
- a coleção fica **travada**, para o TMDB não trocar nome nem imagens;
- apagar o `collection.json` não apaga a coleção do servidor (apague pela interface).

## Campos com decisão do usuário (08/11/2026)

| Campo | Decisão | Como está |
|---|---|---|
| `favorite` (13 filmes) | **Não importar.** No Croma, favorito é de cada usuário e se marca na tela | O leitor ignora o campo |
| `edition` (`Estendida`, 4 filmes) | **Tag e etiqueta no título** | Servidor: vira a tag `Estendida` (feito). Interface: etiqueta ao lado do título nos cartões e no detalhe (fase 5; a interface reconhece a edição pela tag) |
| `metadata/images/extra.*` | É uma foto sem papel definido; imagens a mais podem ser vários pôsteres ou fundos | Entra como **segundo fundo**, depois do `background`. Quando o DL_HERMES definir nomes para vários pôsteres e fundos, o `BauLayout.ImageFiles` ganha esses nomes |
| Dados técnicos de `files` (`sha256`, faixas…) | Não lidos | O servidor já lê o próprio arquivo com o ffprobe. Os hashes servem ao Baú, não à interface |

## Implementação (08/11/2026)

No `croma-servidor`, em `MediaBrowser.Providers/Bau/` (arquivos novos), mais uma mudança no núcleo:

| Arquivo | O quê |
|---|---|
| `BauLayout.cs` | Nomes de pastas e arquivos do padrão; nome das legendas |
| `BauJson.cs`, `BauMovieMetadata.cs`, `BauCollectionMetadata.cs`… | Leitura do JSON (`snake_case`, só `schema_version` 2) |
| `BauMovieProvider.cs` | Leitor de metadados local "Baú" para filmes (aparece nas opções da biblioteca) |
| `BauImageProvider.cs` | Pôster e fundos de `metadata/images/` |
| `BauExternalId.cs` | O `uuid` como ID externo `Bau` |
| `BauCollectionsPostScanTask.cs` | Sincroniza as coleções depois de cada varredura |
| `MediaBrowser.Providers/MediaInfo/MediaInfoResolver.cs` | **Núcleo:** procura legendas também em `metadata/subs/` com o nome do Baú |
| `MediaBrowser.Controller/Providers/IAuthoritativeMetadataProvider.cs`, `MediaBrowser.Providers/Manager/MetadataService.cs` | **Núcleo:** listas completas de um leitor local (acima) |

Testes em `tests/Jellyfin.Providers.Tests/Bau/` e `tests/Jellyfin.Providers.Tests/Manager/AuthoritativeMetadataProviderTests.cs`.

## Incidente: fundos apagados (08/11/2026)

A instrução de atualizar os metadados com "Substituir as imagens existentes" fez o Jellyfin apagar do acervo os 160 `metadata/images/background.jpg`. No original, ao substituir os fundos, ele apaga os arquivos antigos, mesmo os que estão na pasta da mídia. O PhotoRec recuperou 7, idênticos pelo `sha256` de `files[]` (*Chumbo Grosso*, *Clube da Luta*, *Gangues de Nova York*, *Herói*, *John Wick – De Volta ao Jogo*, *O Grande Truque*, *Sim Senhor*). Os outros 153 foram sobrescritos. O usuário decidiu deixar como está; os 7 não foram copiados de volta (o disco ficou montado só leitura). Pôsteres, `extra`, legendas, vídeos e JSON ficaram intactos.

Correção no `croma-servidor` (`ItemImageProvider.cs`, veja o README dele). Regras daqui em diante:

- O servidor nunca grava nem apaga nada no acervo. Toda opção do Jellyfin que mexe em arquivos é verificada no código antes de ser indicada ao usuário.
- Opções destrutivas são testadas antes numa cópia pequena do acervo, nunca no acervo real.
- Enquanto o Croma estiver em desenvolvimento, o disco do acervo fica montado só leitura; o usuário remonta para gravação quando for usar o DL_HERMES.
