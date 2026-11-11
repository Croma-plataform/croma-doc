#!/usr/bin/env bash
# Verifica o Croma inteiro com um comando: lint, tipos, testes e build do croma-web; testes e formatação do
# croma-servidor; e os testes de ponta a ponta contra o servidor de teste.
#
# Uso: ferramentas/verificar.sh [--rapido] [--so web|servidor|e2e] [--ate-o-fim]
#
#   --rapido    só o que o dia a dia pede: lint e estilo dos arquivos que mudaram, tipos, testes do Croma, sem o
#               build (usa o dist atual) e sem os testes lentos de ponta a ponta
#   --so X      roda só uma parte (web, servidor ou e2e)
#   --ate-o-fim não para no primeiro erro de uma parte (o resumo no fim mostra tudo de qualquer jeito)
#
# Ambiente: Node 24 (se o `node` do sistema for outro, usa o `node-24` por links temporários), .NET em ~/.dotnet,
# ffmpeg no PATH e Playwright + pytest do Python. O servidor de teste e a mídia sintética são criados sozinhos.
set -uo pipefail

hub="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
web="$hub/croma-web"
servidor="$hub/croma-servidor"
rapido=0
so=""
ate_o_fim=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --rapido) rapido=1; shift ;;
        --so) so="${2:-}"; shift 2 ;;
        --ate-o-fim) ate_o_fim=1; shift ;;
        -h|--help) sed -n '2,15p' "${BASH_SOURCE[0]}"; exit 0 ;;
        *) echo "Opção desconhecida: $1" >&2; exit 2 ;;
    esac
done
[[ -z "$so" || "$so" =~ ^(web|servidor|e2e)$ ]] || { echo "--so aceita web, servidor ou e2e" >&2; exit 2; }

resumo=()
falhou=0
passo() {  # passo "nome" comando...
    local nome="$1"; shift
    local inicio=$SECONDS
    echo; echo "━━ $nome"
    if "$@"; then
        resumo+=("✔ $nome ($((SECONDS - inicio)) s)")
    else
        resumo+=("✘ $nome ($((SECONDS - inicio)) s)")
        falhou=1
        [[ $ate_o_fim -eq 1 ]] || return 1
    fi
    return 0
}
quer() { [[ -z "$so" || "$so" == "$1" ]]; }

# Node 24 (o croma-web exige) mesmo que o `node` do sistema seja outro
if [[ "$(node --version 2>/dev/null)" != v24.* ]]; then
    if command -v node-24 >/dev/null && command -v npm-24 >/dev/null; then
        links="${TMPDIR:-/tmp}/croma-node24"
        mkdir -p "$links"
        ln -sf "$(command -v node-24)" "$links/node"
        ln -sf "$(command -v npm-24)" "$links/npm"
        ln -sf "$(command -v npx-24 2>/dev/null || command -v npx)" "$links/npx"
        export PATH="$links:$PATH"
    else
        echo "Node 24 não encontrado (o croma-web exige Node 24 e npm 11)." >&2
        exit 1
    fi
fi
export DOTNET_ROOT="${DOTNET_ROOT:-$HOME/.dotnet}"
export PATH="$DOTNET_ROOT:$PATH"

# Arquivos que mudaram no croma-web (para o modo rápido)
mudados() {  # mudados 'padrao-egrep'
    { git -C "$web" diff --name-only HEAD; git -C "$web" ls-files --others --exclude-standard; } |
        grep -E "$1" | sort -u | while read -r f; do [[ -f "$web/$f" ]] && echo "$f"; done
}

web_lint() {
    cd "$web" || return 1
    if [[ $rapido -eq 1 ]]; then
        mapfile -t js < <(mudados '\.(js|jsx|ts|tsx)$')
        [[ ${#js[@]} -eq 0 ]] || npx eslint "${js[@]}"
    else
        npx eslint
    fi
}
web_estilo() {
    cd "$web" || return 1
    if [[ $rapido -eq 1 ]]; then
        mapfile -t css < <(mudados '\.(css|scss)$')
        [[ ${#css[@]} -eq 0 ]] || npx stylelint "${css[@]}"
    else
        npx stylelint "src/**/*.{css,scss}"
    fi
}
web_tipos() { cd "$web" && npx tsc --noEmit; }
web_testes() {
    cd "$web" || return 1
    if [[ $rapido -eq 1 ]]; then
        npx vitest run --config vite.config.ts src/components/croma src/apps/modern src/utils src/constants
    else
        npm test
    fi
}
web_build() { cd "$web" && npm run build:production >/dev/null && npm run escheck; }

servidor_testes() {
    cd "$servidor" || return 1
    export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
    if [[ $rapido -eq 1 ]]; then
        dotnet test tests/Jellyfin.Providers.Tests --nologo -v q --filter "FullyQualifiedName~Bau|FullyQualifiedName~Authoritative|FullyQualifiedName~ItemImageProviderMediaFiles" &&
        dotnet test tests/Jellyfin.Model.Tests --nologo -v q --filter "FullyQualifiedName~Library" &&
        dotnet test tests/Jellyfin.Server.Integration.Tests --nologo -v q --filter "FullyQualifiedName~LibrarySubtypes"
    else
        dotnet test --nologo -v q
    fi
}
servidor_formato() { cd "$servidor" && dotnet format --verify-no-changes; }

e2e() {
    python3 "$hub/ferramentas/midia_teste.py" || return 1
    python3 "$hub/ferramentas/servidor_teste.py" subir || return 1
    # O servidor lê o dist/ do disco: um dist antigo testaria o código errado
    if [[ -n "$(find "$web/src" -newer "$web/dist/index.html" -type f -print -quit 2>/dev/null)" ]]; then
        echo "AVISO: o croma-web/dist está mais velho que o código em src/. Rode sem --rapido ou faça o build."
    fi
    cd "$hub/ferramentas/e2e" || return 1
    if [[ $rapido -eq 1 ]]; then python3 -m pytest -q -m "not lento"; else python3 -m pytest -q; fi
}

if quer web; then
    passo "croma-web: eslint" web_lint
    passo "croma-web: stylelint (inclui o Chromium 85 da TV)" web_estilo
    passo "croma-web: tipos (tsc)" web_tipos
    passo "croma-web: testes (Vitest)" web_testes
    [[ $rapido -eq 1 ]] || passo "croma-web: build e es-check" web_build
fi
if quer servidor; then
    passo "croma-servidor: testes (dotnet test)" servidor_testes
    [[ $rapido -eq 1 ]] || passo "croma-servidor: formatação (dotnet format)" servidor_formato
fi
if quer e2e; then
    passo "ponta a ponta (Playwright)" e2e
fi

echo; echo "━━ Resumo"
printf '%s\n' "${resumo[@]}"
if [[ $falhou -eq 0 ]]; then echo "Tudo certo."; else echo "Há falhas."; fi
exit $falhou
