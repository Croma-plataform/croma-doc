# Bibliotecas caseiras (Vídeos e Fotos)

As bibliotecas de arquivos caseiros, de vídeos ou de fotos, têm dois tipos de varredura:

1. **Genérica:** a varredura padrão do Jellyfin, sem estrutura obrigatória.
2. **Estruturada (Croma):** segue uma estrutura de pastas com níveis, como as pastas `Nivel_1..3` do v1 (`croma-v1`). **O formato está em desenvolvimento pelo usuário** e será adicionado depois.

A varredura roda no servidor (C#). Desde 08/11/2026 o acervo do usuário segue o **padrão Baú** (repositório DL_HERMES), e o servidor já lê esse padrão para Filmes (`specs/varredura-bau.md`). O modo estruturado de Vídeos e Fotos vai entrar no mesmo leitor (`croma-servidor`, `MediaBrowser.Providers/Bau/`) quando os documentos dessas bibliotecas forem aprovados. Até lá, essas bibliotecas usam o modo genérico.

