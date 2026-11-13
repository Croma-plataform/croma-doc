# Coleções por biblioteca (especificação, 05/11/2026)

No Jellyfin, as coleções são globais: moram na biblioteca virtual "Coleções". No Croma, cada coleção pertence a uma biblioteca.

- **Posse (decidido em 12/11/2026, S04):** cada coleção tem uma biblioteca dona, gravada num **campo do próprio `BoxSet`** no servidor (`OwnerLibraryId`, no JSON do item, sem migração do banco), e não numa tag reservada. O campo aparece no DTO (`OwnerLibraryId`) e em `POST /Collections?ownerLibraryId=`. A coleção é criada dentro da biblioteca e só aparece nela. O servidor recusa (400) item de outra biblioteca em coleção com dono; coleção sem dono (de antes) aceita qualquer item. As coleções do Baú (filmes, séries e músicas) recebem o dono na varredura, inclusive as já existentes.
- **Só itens da própria biblioteca:** uma coleção de Filmes não aceita séries. "Adicionar à coleção" lista só as coleções da biblioteca do item.
- **Listar:** `GET /Collections?ownerLibraryId=<biblioteca>` devolve as coleções da biblioteca que o usuário enxerga.
- **Sem tela global:** a biblioteca "Coleções" (`/boxsets`) sai do Início e do menu. Toda biblioteca tem a aba "Coleções", inclusive Vídeos e Clipes.
- **Dois controles de exibição, pôster (vertical) ou miniatura (horizontal):**
  1. **Por biblioteca:** vale para a aba "Coleções" daquela biblioteca. Todos os cartões de coleção têm o mesmo formato.
  2. **Por coleção:** vale para os itens dentro dela. Todos os itens têm o mesmo formato. Fica gravado no `BoxSet` (`UseThumbnails`, `CollectionUseThumbnails` no DTO; `POST /Collections/{id}/DisplayMode`; por padrão é pôster).
  - Nunca há formatos misturados na mesma tela. O padrão é pôster.
  - A configuração fica no servidor, não no `localStorage`, para valer igual no desktop e na TV.
  - Miniatura sem arte horizontal (Thumb) usa o fundo (Backdrop) e, sem nenhum dos dois, a capa gerada.
- **Tags reservadas:** as que começam com `croma-` não aparecem nas telas de tags.
- **Migração:** a varredura do Baú atribui o dono às coleções dela e a tarefa `BoxSetOwnerPostScanTask` atribui às feitas à mão, pela biblioteca com a maioria dos itens (roda a cada varredura, só nas coleções sem dono); falta só consertar coleções órfãs quando uma biblioteca é recriada.
- **Onde mexer no `croma-web`:**
  - `libraryRoutes.ts`: abas e rota `/boxsets`;
  - `useFetchItems.ts`: consulta da aba Coleções;
  - `components/collectionEditor`: criar coleção e adicionar itens;
  - `itemDetails/index.js`, em `renderCollectionItemType`: formato dos itens.

