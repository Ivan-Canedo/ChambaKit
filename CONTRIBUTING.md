# Contribuir a ChambaKit

Guía para quien mantiene la plantilla o le propone cambios. El titular de una copia no la necesita: sus instrucciones están en `AGENTS.md`.

## Plantilla o copia

Un clon de la plantilla se ve igual para el mantenedor que para un titular que la clonó en lugar de crear su copia. Los distingue una marca que vive solo en la configuración local de git (`.git/config`), que no se publica ni viaja en un clon. Ponla en cada clon donde trabajes la plantilla:

```sh
git config --local chambakit.mantenedor true
```

Con la marca, el agente trabaja como mantenedor (`AGENTS.md`, «Al iniciar»); sin ella, como en la copia de un titular.

## Reglas para el agente del mantenedor

Valen las reglas de `AGENTS.md`, con estos cambios:

- **Los módulos son plantilla:** estructura, instrucciones breves y marcadores «pendiente», sin datos de ninguna persona ni nombres de empresas, ni siquiera de ejemplo. Sus filas de ESTADO siguen en «Sin llenar».
- **Remoto público a propósito:** la revisión de «Copia privada» de `AGENTS.md` no aplica a la plantilla.
- **Sin registros ni búsquedas reales:** la plantilla no tiene hoja de registros ni proyecto web. Los scripts se prueban con datos ficticios, en un clon de prueba (ver «Probar como titular»).
- **Versión de la plantilla:** vive en la tabla ESTADO de 01. Súbela con cada cambio que se publique; es la que anota cada copia nueva.

## Agent skills

El mantenedor trabaja con las skills de ingeniería de `mattpocock-skills`: planifica con `grill-with-docs`, resume el plan en un spec con `to-spec`, lo divide con `to-tickets` e implementa un ticket por conversación con `implement`.

### Issue tracker

Los tickets son archivos Markdown en `.scratch/`, fuera de git porque el repo es público. Ver `docs/agents/issue-tracker.md`.

### Triage labels

Los cinco roles canónicos con sus nombres por defecto. Ver `docs/agents/triage-labels.md`.

### Domain docs

Un solo contexto: `CONTEXT.md` (glosario) y `docs/adr/` (decisiones) en la raíz. Ver `docs/agents/domain.md`.

## Privacidad

La plantilla es pública: ningún archivo puede llevar datos de una persona real. Antes de cada commit:

1. **Auditoría de términos:** la lista de términos que identifican al mantenedor vive en `.scratch/convertir-en-plantilla/terminos.txt`, fuera de git. Toda la carpeta debe dar cero coincidencias (agrega `--excluir .venv` si existe):

   ```sh
   python3 -I herramientas/auditar_terminos.py .scratch/convertir-en-plantilla/terminos.txt . --excluir .scratch
   ```

   El formato de la lista, las excepciones (`!frase`), cómo busca y sus códigos de salida están en el docstring del script. Quien contribuya sin esa lista puede auditar con una propia.
2. **Binarios:** la auditoría no los lee; los avisa en stderr. Revisa aparte sus metadatos (autor, rutas de la máquina) antes de publicarlos.
3. **Formato:** `markdownlint-cli2` sin argumentos revisa todo el repo según `.markdownlint-cli2.jsonc` y debe dar cero advertencias.
4. **Correo:** los commits usan el correo noreply de GitHub, configurado en `user.email` local. Revísalo antes de un push con `git log --format='%an <%ae> | %cn <%ce>'`.

## Pruebas

Las pruebas automáticas usan `unittest`, sin red, y llaman a cada script por su línea de comandos con entradas ficticias. La excepción es la búsqueda en un portal: la prueba importa `buscar.py` desde una copia ficticia, cambia `pedir()`, su única función de red, por un portal falso y corre `main()`. Con `-B` no quedan cachés:

```sh
python3 -I -B -m unittest discover -s herramientas/pruebas
```

Las que generan un CV se saltan si faltan LibreOffice o poppler, y las de la herramienta de registros locales, si falta `openpyxl`. Para correrlas, usa el Python de un entorno virtual con `openpyxl`, el mismo que crea `/configurar` en modo local:

```sh
python3 -m venv .venv && .venv/bin/python -m pip install openpyxl
.venv/bin/python -I -B -m unittest discover -s herramientas/pruebas
```

### Probar como titular

Para ver la plantilla como la ve un titular nuevo, trabaja en un clon de prueba temporal, que nace sin la marca:

```sh
git clone . "$(mktemp -d)/clon"
```

El clon de prueba solo lleva lo que ya tiene commit. Para probar cambios sin commit, duplica la carpeta y quítale la marca al duplicado con `git -C <clon> config --local --unset chambakit.mantenedor`.

Al abrir el clon de prueba en VS Code con Claude Code, el agente debe ofrecer `/configurar`. Marca como sintéticos los datos de prueba y bórralos al terminar, incluida cualquier hoja de prueba en Drive.

## Pendientes

- **Skill `/actualizar`:** llevará a una copia las mejoras de una versión nueva de la plantilla, a partir de la «Versión de la plantilla» que anota 01.
