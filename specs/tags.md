# Tags (avaliação de 05/11/2026)

Avaliação de como levar as tags e o editor de tags do Croma v1 (`croma-v1`, marcos M3, M12 e M13) para o Croma v2.

## O que o Jellyfin já tem

- O campo `Tags` em todo item e o filtro `?tags=`, que funciona no modo "qualquer".
- A lista de tags vem de `/Items/Filters`.
- O `PhotoProvider` lê as palavras-chave (Keywords) do arquivo para o campo `Tags`.

## Plano

Levar para TypeScript, no `croma-web`, a lógica pura do v1, trocando só a camada de API:

- `web/src/logica/tagPicker.ts`, `edicaoMassa.ts` e `pesquisa.ts`;
- `server/src/busca/tags.ts`.

(Caminhos relativos ao repositório `croma-v1`.)

## O que fazer no cliente

- modo "todas" da pesquisa;
- tags herdadas do álbum;
- edição em massa: uma chamada `POST /Items/{id}` por item;
- níveis: lidos do nome da pasta pai `Nivel_N`;
- álbum oculto: tag reservada mais `excludeTags`.

## Riscos

- Uma atualização de metadados pode sobrescrever as tags com as Keywords do arquivo. Por isso, trave o campo Tags (`LockedFields`) ao editar.
- A pasta `metadados/` do v1 precisa de um arquivo `.ignore`.

## Decisões em aberto (ainda sem resposta do usuário)

1. **Onde as tags ficam salvas:** só no Jellyfin, com um script de backup e importação dos JSONs do v1 (recomendado), ou num plugin C# com os arquivos como fonte da verdade.
2. **Níveis:** achatar as pastas no cliente ou convertê-los em tags.
3. **Escopo:** tags só em Fotos ou em todas as bibliotecas.

A varredura estruturada que resolveria os níveis e as tags de uma vez era a das bibliotecas Vídeos e Galeria do acervo, que saíram do Croma (09/11/2026, aplicação dedicada por privacidade). Os níveis precisam de outra solução, se ainda fizerem sentido.
