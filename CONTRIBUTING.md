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
- **Sin registros ni búsquedas reales:** la plantilla no tiene archivo de registros, instantánea ni proyecto web. Los scripts se prueban con datos ficticios, en un clon de prueba (ver «Probar como titular»).
- **Versión de la plantilla:** vive en la tabla ESTADO de 01, junto a la URL de la plantilla; es la que anota cada copia nueva y de la que parte `/actualizar` (ADR 0004). Ver «Versión de la plantilla».

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

Las pruebas automáticas usan `unittest`, sin red, y llaman a cada script por su línea de comandos con entradas ficticias. La excepción es la búsqueda en un portal: la prueba importa `buscar.py` desde una copia ficticia, cambia `pedir()`, su única función de red, por un portal falso y corre `main()`. Para probar lo que detecta el propio `pedir()`, como un host bloqueado por el proxy o el 429 de Workable en la nube, cambia en su lugar `urllib.request.urlopen` por una red falsa. La otra es `test_punteros_skills.py`, que no llama a ningún script: lee las skills del repo y comprueba que cada una de `.claude/skills/` tenga en `.agents/skills/` su puntero, con el mismo `name` y la misma `description`. Y `test_preparar_nube.py` lee el comando del hook de `.claude/settings.json` y lo corre con `bash` en una copia ficticia: sin `CLAUDE_CODE_REMOTE` debe salir con 0, sin imprimir ni crear nada; con la variable, cambia `dpkg`, `apt-get`, `npm`, `markdownlint-cli2`, `python3` e `id` por comandos falsos al inicio del `PATH`, porque la instalación real necesita root y red. Con `-B` no quedan cachés:

```sh
python3 -I -B -m unittest discover -s herramientas/pruebas
```

Las que generan un CV se saltan si faltan LibreOffice o poppler; las de la herramienta de registros, si falta `openpyxl`, y la que revisa el formato de la instantánea, si falta `markdownlint-cli2`. Para correrlas, usa el Python de un entorno virtual con `openpyxl`, el mismo que crea `/configurar` en el paso 8 (Registros):

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

Al abrir el clon de prueba en VS Code con Claude Code, el agente debe ofrecer `/configurar`. Marca como sintéticos los datos de prueba y bórralos al terminar, incluidos el archivo de registros, la instantánea y cualquier proyecto web o repositorio de prueba.

## Versión de la plantilla

Cada versión publicada es una etiqueta `vX.Y` sobre su commit. `/actualizar` fusiona cada archivo de la copia en tres vías, con la etiqueta que anota su 01 como base, así que una etiqueta publicada no se mueve ni se borra. Para publicar una versión:

1. Sube la versión en la línea **Versión de la plantilla** de 01. Los módulos de la plantilla no cambian de versión por esto: la copia lleva la suya.
2. Agrega a `CAMBIOS.md` la sección `## vX.Y — fecha`, arriba de las anteriores, con dos subsecciones:
   - `### Qué cambió`: en pocas líneas, para el titular.
   - `### En la copia`: una lista numerada de lo que la fusión no ve, como columnas nuevas en los registros o datos que hay que preguntarle al titular. Cada acción va marcada **automática** o **con el titular** y, si toca un módulo que en la copia puede estar «Configurado», dice qué paso retomar en su fila de ESTADO. Si no hay acciones, «Sin acciones».
3. Commit, etiqueta y push de los dos:

   ```sh
   git tag vX.Y
   git push origin main vX.Y
   ```

`v1.0` es el commit que trae `/actualizar` y `CAMBIOS.md`.
