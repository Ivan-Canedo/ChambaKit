#!/usr/bin/env bash
# Prepara una sesión de Code en la nube (ADR 0007). Lo corre el hook SessionStart de
# .claude/settings.json al abrir o retomar la sesión.
#
# Instala con apt poppler, Carlito y LibreOffice Writer sin interfaz; con npm, markdownlint-cli2;
# y crea .venv con openpyxl. Se salta lo que ya está. Solo actúa con CLAUDE_CODE_REMOTE=true: en
# Code local sale con 0 sin hacer nada ni imprimir nada.
#
# Nunca tumba la sesión: si una parte falla, imprime un aviso con qué falló y sigue; siempre sale
# con 0. Lo que imprime llega al agente como contexto de la sesión, y /configurar lo usa en los
# pasos 2 y 8.

[ "${CLAUDE_CODE_REMOTE:-}" = true ] || exit 0

PAQUETES_APT=(poppler-utils fonts-crosextra-carlito libreoffice-writer-nogui)
avisos=()
salida=$(mktemp) || salida=/dev/null

# Agrega un aviso con las últimas líneas de la salida del comando que falló.
avisar() {
    avisos+=("$1: $(tail -n 3 "$salida" 2>/dev/null | tr '\n' ' ')")
}

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/..}" || {
    echo "Hook de la nube de ChambaKit: no se encontró la carpeta de la copia; no se instaló nada."
    exit 0
}

sudo=()
[ "$(id -u)" = 0 ] || sudo=(sudo -n)

faltan=()
for paquete in "${PAQUETES_APT[@]}"; do
    dpkg -s "$paquete" >/dev/null 2>&1 || faltan+=("$paquete")
done
if [ ${#faltan[@]} -gt 0 ]; then
    if ! { "${sudo[@]}" apt-get update -q &&
           "${sudo[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y -q "${faltan[@]}"; } >"$salida" 2>&1; then
        avisar "apt no instaló ${faltan[*]}"
    fi
fi

# Instalado, la primera línea de --help da la versión, aunque salga con código 2.
if ! markdownlint-cli2 --help 2>/dev/null | head -n 1 | grep -q markdownlint-cli2; then
    if ! "${sudo[@]}" npm install -g markdownlint-cli2 >"$salida" 2>&1; then
        avisar "npm no instaló markdownlint-cli2"
    fi
fi

if ! .venv/bin/python -I -c "import openpyxl" >/dev/null 2>&1; then
    if ! { python3 -m venv .venv && .venv/bin/python -m pip install -q openpyxl; } >"$salida" 2>&1; then
        avisar "no se creó .venv con openpyxl"
    fi
fi

[ "$salida" = /dev/null ] || rm -f "$salida"

if [ ${#avisos[@]} -eq 0 ]; then
    echo "Hook de la nube de ChambaKit: herramientas y .venv listos."
else
    echo "Hook de la nube de ChambaKit: falló una parte de la preparación."
    for aviso in "${avisos[@]}"; do
        echo "- $aviso"
    done
    echo "Para repetirla y ver el aviso de nuevo: CLAUDE_CODE_REMOTE=true bash herramientas/preparar_nube.sh"
fi
exit 0
