# Guia de instalação e uso do Croma

Para uso pessoal. Versão 12.4 (servidor e interface andam juntos). Escrito em 12/11/2026 para o desktop; TV e celular entram quando existirem.

## 1. O que você precisa

| Peça | Repositório | Para quê |
|---|---|---|
| Servidor | `croma-servidor` (branch `croma`) | guarda e serve o acervo |
| Interface | `croma-web` (branch `croma`) | a tela; o servidor a serve pelo `--webdir` |
| App desktop | `croma-desktop` (branch `croma`) | janela própria com o player mpv (opcional: o navegador também serve) |

Clonar tudo: `CROMA.md`, seção "Clonar os repositórios".

## 2. Servidor

1. Instale o .NET SDK 10 (no Fedora, em `~/.dotnet`) e o Node 24 com npm 11.
2. Compile o servidor: `dotnet publish` do `croma-servidor` para a pasta `compilado/` (detalhes em `croma-servidor/croma/README.md`).
3. Gere a interface: `cd croma-web && npm ci && npm run build:production`.
4. Coloque o `jellyfin-ffmpeg` em `croma-servidor/ffmpeg/` (ou passe `--ffmpeg /usr/bin/ffmpeg`).
5. Suba: `croma-servidor/croma/scripts/iniciar-servidor.sh` (Linux) ou `iniciar-servidor.ps1` (Windows). Os dados ficam em `croma-servidor/dados/`.
6. Abra `http://localhost:8096`, faça o assistente inicial e crie as bibliotecas (cada uma tem um **tipo** e um **Conteúdo**: Filmes, Séries, Documentários, Músicas, Podcasts, Audiolivros, Livros, HQs, Mangás, Fotos).

**Acervo:** monte o disco só leitura durante o desenvolvimento e não use "Substituir as imagens existentes" (`specs/varredura-bau.md`).

## 3. App desktop (Linux/Fedora)

```
croma-desktop/dev/linux/setup-fedora.sh   # instala cmake, g++, mpv e Qt (usa sudo dnf)
croma-desktop/dev/linux/build.sh          # compila; o binário fica em build/src
```

Na primeira abertura informe o endereço do servidor. No Windows o instalador sai do D20 do `PLANO.md`.

## 4. Uso

- **Barra lateral:** Início, Favoritos e as seções (Audiovisual, Áudios, Leitura, Fotos). Cada seção tem as suas abas.
- **Busca:** `Ctrl K`; os resultados vêm agrupados por seção.
- **Player:** espaço pausa; `←/→` pulam; `M` muda o som; `F` tela cheia. Legendas e áudio no painel do player.
- **Descanso de tela:** o logotipo anda pela tela depois de 5 minutos parado, e não entra com vídeo tocando.
- **Calibrar a tela:** Ajustes de exibição → "Calibrar a tela".
- **Teste de componentes:** `#/mostruario`.

## 5. Para quem desenvolve

- `ferramentas/verificar.sh` roda lint, tipos, testes unitários, testes do servidor e ponta a ponta.
- `PLANO.md` lista os módulos e o que falta; `CROMA.md` mapeia o código.

## 6. Licença

O Croma é derivado do Jellyfin (GPL-2.0, servidor e interface web). Os arquivos `LICENSE` de cada repositório seguem como no original, e o código modificado é publicado nos repositórios da organização `Croma-plataform`. O nome e o logotipo "Jellyfin" não aparecem no produto; as menções que sobram são de licença e de crédito no código.
