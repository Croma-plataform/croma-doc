# Croma

Versão pessoal do Jellyfin com identidade visual própria. Foco inicial: **Desktop** e **TV Samsung QN90B (Tizen 6.5)**.

## Repositórios

O projeto é dividido em repositórios próprios, todos na organização [`Croma-plataform`](https://github.com/Croma-plataform) do GitHub. Este (`Croma-plataform/Croma`) é o **hub**: visão geral, arquitetura e especificações. Os demais são clonados **dentro da pasta do hub**, cada um com git próprio (ficam no `.gitignore` do hub).

| Pasta | Repositório (privado) | O que é | Branch |
|---|---|---|---|
| `croma-identidade/` | https://github.com/Croma-plataform/croma-identidade | Identidade visual (v0.1 "Barras" oficial), logos e scripts geradores | `main` |
| `croma-servidor/` | https://github.com/Croma-plataform/croma-servidor | Scripts e configuração do servidor; futuros plugins C# | `main` |
| `croma-web/` | https://github.com/Croma-plataform/croma-web | Interface web compartilhada (fork do jellyfin-web) | `croma` |
| `croma-desktop/` | https://github.com/Croma-plataform/croma-desktop | App desktop (fork do jellyfin-desktop) | `croma` |
| `croma-tizen/` | https://github.com/Croma-plataform/croma-tizen | App da TV Samsung (fork do jellyfin-tizen) | `croma` |
| `croma-android/` | https://github.com/Croma-plataform/croma-android | App Android (fork do jellyfin-android); criado, ainda não implementado | `croma` |
| `croma-v1/` | https://github.com/Croma-plataform/croma-v1 | Croma v1, arquivado (referência para as tags) | `main` |
| `jellyfin-server/` | https://github.com/jellyfin/jellyfin | Código do servidor oficial, só para consulta | tag `v12.4` |

## Base de versões dos forks

| Fork | Origem (remote `upstream`) | Base | Commit da base |
|---|---|---|---|
| `croma-web` | https://github.com/jellyfin/jellyfin-web | `release-12.z` (v12.4) | `0a580ce8d` |
| `croma-tizen` | https://github.com/jellyfin/jellyfin-tizen | `master` | `31408c1` |
| `croma-desktop` | https://github.com/jellyfin/jellyfin-desktop | `master` | `51807f8` |
| `croma-android` | https://github.com/jellyfin/jellyfin-android | `master` (v2.7.1) | `6c5ab875` |

O GitHub Actions está desativado nos forks, para os workflows herdados do Jellyfin não rodarem.

Regra: a versão do web **sempre** casa com a do servidor (v12.4). Para atualizar: `git fetch upstream` + rebase da `croma`.

### Clonar os repositórios

Em uma máquina nova, clone o hub e, dentro dele, os demais:

```
git clone https://github.com/Croma-plataform/Croma.git Croma-plataform
cd Croma-plataform
git clone https://github.com/Croma-plataform/croma-identidade.git
git clone https://github.com/Croma-plataform/croma-servidor.git
git clone https://github.com/Croma-plataform/croma-v1.git
git clone https://github.com/Croma-plataform/croma-web.git
git clone https://github.com/Croma-plataform/croma-desktop.git
git clone https://github.com/Croma-plataform/croma-tizen.git
git clone https://github.com/Croma-plataform/croma-android.git
git clone --filter=blob:none -o upstream https://github.com/jellyfin/jellyfin.git jellyfin-server

git -C croma-web     remote add upstream https://github.com/jellyfin/jellyfin-web.git
git -C croma-desktop remote add upstream https://github.com/jellyfin/jellyfin-desktop.git
git -C croma-tizen   remote add upstream https://github.com/jellyfin/jellyfin-tizen.git
git -C croma-android remote add upstream https://github.com/jellyfin/jellyfin-android.git
git -C jellyfin-server checkout v12.4
```

- No Windows, rode também `git -C jellyfin-server config core.longpaths true` antes do checkout.
- O `--filter=blob:none` baixa o conteúdo dos arquivos sob demanda, o que deixa o clone de referência bem mais leve.
- Os repositórios são privados: o `git clone` pede login no GitHub (`gh auth login` resolve).

### Servidor local

O passo a passo (binário oficial portátil, build do `croma-web` e script de inicialização) fica no [README do `croma-servidor`](https://github.com/Croma-plataform/croma-servidor).

### Outros repositórios de referência

| Repositório | Para quê |
|---|---|
| https://github.com/jellyfin/jellyfin-androidtv | App de Android TV (fase futura) |
| https://github.com/jellyfin/jellyfin-android | App de Android (fase futura) |
| https://github.com/jellyfin/jellyfin-vue | Cliente web alternativo (não usado: não tem layout de TV) |
| https://github.com/jellyfin/jellyfin-ffmpeg | FFmpeg usado pelo servidor |
| https://github.com/jellyfin/jellyfin-kodi | Integração com o Kodi |
| https://github.com/jellyfin/jellyfin.org | Site e documentação oficial |
| https://github.com/awesome-jellyfin/awesome-jellyfin | Lista de plugins, temas e clientes da comunidade |

## Arquitetura

```
croma-identidade  ← fonte da verdade da marca (manual, logos, ícones)
   │  arquivos copiados para:
   ▼
croma-web (fork do jellyfin-web)  ← a identidade aplicada na interface mora aqui
   ├─ build → croma-servidor serve via --webdir → croma-desktop (carrega a UI do servidor) + navegador
   └─ build → croma-tizen empacota o dist/ → .wgt na TV
```

## Mapa do croma-web (onde mexer)

- **Paleta base:** `src/themes/_base/_palette.scss` (cor primária hoje `#00a4dc`), `src/themes/_base/theme.ts`
- **Registro de temas (MUI):** `src/themes/index.ts`; tema padrão em `src/config.json` → `themes[].default`
- **Tema Croma:** criar `src/themes/croma/{index.ts,theme.scss}`, registrar em `index.ts` e `config.json`
- **Logos:** vêm do pacote `@jellyfin/ux-web`; referências em `src/styles/site.scss`, `src/themes/_base/_theme.scss`,
  `src/apps/modern/components/drawers/DrawerHeaderLink.tsx`, `src/components/toolbar/ServerButton.tsx`,
  `src/plugins/logoScreensaver/plugin.js`
- **Nome do app:** `src/index.html` (`<title>`, `application-name`), `src/manifest.json`, strings em `src/strings/`
- **Layouts:** `src/apps/modern` (React, desktop) e `src/apps/legacy` (controllers antigos, inclusive vários usados no modo TV)
- **Modo TV:** classe `.layout-tv` (CSS) + `layoutManager.tv` (JS). Testar toda mudança visual nesse modo

## Mapa das cascas

- **Tizen:** `config.xml` (nome, ids `AprZAARz4r.Jellyfin`, `widget id`), `icon.png`
- **Desktop:** `CMakeModules/NameConfiguration.cmake`, `resources/images`, `native/find-webclient.*` (tela de conexão),
  `bundle/win/JellyfinDesktop.iss.in` (instalador Windows)

## Pendências

- [x] Instalar o servidor Jellyfin v12.4 oficial no Windows (máquina CintraMan; veja o `croma-servidor`)
- [ ] Servidor no Linux: script de inicialização equivalente ao `.ps1`
- [x] Tema "Croma" e marca no `croma-web` (paleta, fontes, cantos vivos, foco, logos, nome e ícones): commit `e5f1c1a4c` na branch `croma`
- [x] Dividir o projeto em repositórios próprios e publicá-los no GitHub (05/11/2026)
- [ ] Tizen Studio + certificado Samsung + Developer Mode na TV
- [x] Identidade visual: v0.1 "Barras" definida como oficial (05/11/2026)
- [ ] Implementar a v0.1 no `croma-web` (tema, logos, ícones e telas), no `croma-tizen` (ícone e tile) e no `croma-desktop` (ícone `.ico`)
- [x] Detalhar a dinâmica das coleções (especificada em 05/11/2026; veja `specs/colecoes.md`)
- [ ] Implementar coleções por biblioteca e modo de exibição
- [ ] Definir o formato estruturado das bibliotecas caseiras (o usuário está desenvolvendo)

## Especificações

| Arquivo | Assunto | Situação |
|---|---|---|
| [`specs/colecoes.md`](specs/colecoes.md) | Coleções por biblioteca e modo de exibição | Especificado, não implementado |
| [`specs/tags.md`](specs/tags.md) | Tags e editor de tags vindos do v1 | Avaliado, com decisões em aberto |
| [`specs/bibliotecas-caseiras.md`](specs/bibliotecas-caseiras.md) | Varredura estruturada (níveis) de Vídeos e Fotos | Formato em desenvolvimento pelo usuário |

## Identidade visual

A identidade oficial é a **v0.1 "Barras"**, decidida em 05/11/2026, e mora no [`croma-identidade`](https://github.com/Croma-plataform/croma-identidade). O manual é `croma-identidade/v0.1-barras/MANUAL.md`, e os arquivos prontos para uso ficam em `croma-identidade/v0.1-barras/logos/` (logotipo, símbolo, ícones das bibliotecas e `app/` com os ícones de cada plataforma). A v0.2 "CAPRA" fica arquivada no mesmo repositório.

Canvas com todas as pranchas: https://claude.ai/artifact/AUKTY2yvnHh4ZYk1c7qpLi (páginas "v0.1 Barras" e "v0.2 Direções CAPRA").
