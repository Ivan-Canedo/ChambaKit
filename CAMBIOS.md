# Cambios de la plantilla

Qué trae cada versión de la plantilla y qué hace `/actualizar` en la copia al llegar a ella. Lo escribe el mantenedor (`CONTRIBUTING.md`, «Versión de la plantilla»); en la copia no se edita.

## v2.1 — 2026-10-29

### Qué cambió

- Tu copia funciona en Code en la nube: el mismo agente, en claude.ai/code o en la pestaña Code de la app de Claude, también desde el teléfono, sobre tu repositorio privado de GitHub. Busca, registra y genera tu CV como en tu equipo. `/conectar-nube`, nueva, te guía para prepararla.
- Cada sesión en la nube se prepara sola al abrirse: instala lo del CV y markdownlint-cli2, y crea `.venv`. En tu equipo, ese paso no hace nada.
- Al cerrar una sesión en la nube, el agente sube tus cambios a `main` con tu permiso, para que lleguen a tu equipo y al canal Web.
- Si un portal no está en la lista de dominios de tu entorno de la nube, la búsqueda te dice cuál falta y dónde agregarlo. Workable no funciona en la nube: la búsqueda te dice que sus empresas se buscan en tu equipo.
- Al dar de alta una empresa, el agente te da en una línea el dominio que va en la lista, por si usas la nube.
- `/actualizar` ya se puede correr también en la nube.
- La búsqueda reconoce el país en las ubicaciones de Workday escritas «MEX.Ciudad». Para eso, 04 lleva también el código de tres letras de cada país.

### En la copia

1. **Code en la nube (con el titular):** si `CLAUDE_CODE_REMOTE` vale `true`, la actualización ya corre en la nube: salta esta acción. Si no, dile en dos frases qué gana: buscar, registrar y generar su CV desde el navegador o el teléfono, sin su equipo. Pregúntale si lo quiere. Si lo quiere, dile que, al terminar la actualización, abra una conversación nueva de su agente en esta carpeta, en Code local, y escriba `/conectar-nube`. Esta acción no edita módulos.
2. **Código alfa-3 en 04 (automática):** si 04 está «Configurado», agrega a la lista de nombres de cada clave de `paises`, en su bloque de PREF-UBICACION, el código ISO 3166-1 alfa-3 de ese país en mayúsculas (`MX` → `MEX`), si no lo tiene. Sale de la clave, así que no hay que preguntarle al titular; muéstraselo en el resumen. La fila de 04 conserva su siguiente paso.

## v2.0 — 2026-10-27

### Qué cambió

- Tus registros viven en un solo lugar: el archivo `ChambaKit_Registros.xlsx` de tu copia, que escribe el canal Code con `herramientas/registros.py`. La hoja de Google sale, y con ella el modo local: ya no hay dos formas de guardar los registros.
- Una búsqueda se registra con `importar`, desde la salida de `buscar.py`, sin que el agente escriba las filas una por una: gasta mucho menos.
- El canal Web ya no busca ni escribe. Lee tus módulos y una instantánea de tus registros (la carpeta `instantanea/`) desde el repositorio privado de GitHub de tu copia, y evalúa o adapta tu CV para una vacante que le pegues. Lo que quieras conservar lo deja en una nota para Code.
- Cualquier agente con terminal trabaja tu copia completa, no solo Claude Code.
- `/conectar-web`, nueva, conecta tu proyecto de claude.ai con tu repositorio, o reconecta el que leía la hoja.

### En la copia

Las acciones dependen de dónde tenía la copia sus registros antes de la fusión: la línea **Registros:** de 00 en el último commit (`git show HEAD:00_INSTRUCCIONES_PROYECTO.md`). Con la URL de una hoja, sigue «Con hoja»; con `modo local`, «En modo local». Si todavía dice «pendiente…», la copia no tiene registros: haz solo la acción 2 de «Con hoja», y `/configurar` crea el archivo en su paso 8.

En los comandos, el Python es `.venv/bin/python` (en Windows, `.venv\Scripts\python.exe`) y `<directorio temporal>` es el de `/actualizar`.

#### Con hoja

1. **Migración (con el titular):** pasa la hoja al archivo de registros sin tocarla (11/REG-LOCAL, «Migración»). Mientras dure, no se registra nada nuevo, ni en la hoja ni en Code.
   1. **Entorno virtual:** si la copia no tiene `.venv/` con `openpyxl`, créalo con su permiso, como dice el punto 2 del paso 8 de `/configurar`.
   2. **Descarga:** dale la URL de la hoja y pídele que la abra y la descargue con Archivo → Descargar → Microsoft Excel (.xlsx), y que te diga dónde quedó el archivo. No lo muevas a la copia.
   3. **Migrar:** `.venv/bin/python -I herramientas/registros.py migrar <archivo descargado>`. Si dice que ya hay un archivo de registros con filas, detente y pregúntale de dónde salió.
   4. **Errores:** si la salida lista errores, no escribió nada. Propónle una corrección por cada uno, sin inventar valores; con las que acepte, arma el JSON de `--correcciones` en `<directorio temporal>` y repite la orden con él. Sigue hasta que no queden errores.
   5. **Conteos:** muéstrale, por pestaña, cuántas filas tenía la hoja y cuántas tiene el archivo, y las columnas quitadas. Si algún conteo no coincide, detente y díselo antes de seguir.
   6. **La hoja:** queda intacta en su Drive. Dile que ya no se usa y que él decide si la borra, de preferencia después del commit de la acción 4.

   Si no puede descargarla ahora, ofrécele deshacer la actualización (paso 6 de `/actualizar`) y repetirla cuando pueda: sin el archivo, la copia 2.0 no tiene dónde registrar.
2. **Módulos que la fusión no ajusta (automática):** en cada uno, sobre el resultado de la fusión.
   - **00:** la línea **Registros:** y su lista toman el texto de la nueva (`git show v2.0:00_INSTRUCCIONES_PROYECTO.md`), sin la URL de la hoja ni `modo local`. Las filas de 00, 10 y 11 de ESTADO, si están «Configurado», retoman los siguientes pasos del cierre del paso 8 de `/configurar`.
   - **06:** quita la columna `Canal` de CAT-EMPRESAS (encabezado, separador y cada fila). En la primera línea de cada ficha, quita `desde <canal>` y `Canal: **<canal>**.`, y renombra su `### Campos y mapeo a la hoja` a `### Campos y mapeo a los registros`. El resto de cada ficha, que escribió el titular, no cambia. Cada ficha editada sube de versión, en su primera línea y en el catálogo, y conserva su fecha de comprobación: no se volvió a comprobar (CAT-REGLAS). La fila de 06 conserva su siguiente paso.
   - **08:** el umbral de «antigua» pasa de 11 a 08. Si la fórmula de `antiguedad` del bloque de 11 en el último commit compara con un número distinto de 20 (`n>=20`), escríbelo en la línea **Marca «antigua»** de 08/EVAL-ACUERDOS. La fila de 08 conserva su siguiente paso.
3. **Primera instantánea (automática):** `.venv/bin/python -I herramientas/registros.py instantanea`, después de la acción 2, para que use el umbral de 08. Debe crear `instantanea/informes.md` e `instantanea/vacantes.md`; si avisa que pasa de 300 KB, díselo al titular.
4. **Un solo commit (automática):** el del paso 6 de `/actualizar` lleva también la migración: `ChambaKit_Registros.xlsx` y `instantanea/` van con `git add`. Después del commit, si la copia tiene remoto privado, ofrécele el push.
5. **Canal Web (con el titular):** pregúntale si tenía un proyecto de claude.ai. Si lo tenía, no le des el recordatorio de «Sync» del paso 6 de `/actualizar`: después del commit y del push, dile que su proyecto sigue leyendo los módulos viejos y la hoja, que ya no recibe registros, y que abra una conversación nueva de su agente en esta carpeta y escriba `/conectar-web`. Esa skill reconecta el mismo proyecto: quita los módulos subidos a mano y el vínculo de Drive, y conecta GitHub, sin perder sus instrucciones ni sus chats. Esta acción no edita módulos.

#### En modo local

1. **Poner al día el archivo (automática):** `.venv/bin/python -I herramientas/registros.py migrar ChambaKit_Registros.xlsx` le quita la columna `canal` a `busquedas` y comprueba cada fila. Muéstrale los conteos al titular. La herramienta 1.x ya comprobaba las filas, así que no espera errores; si lista alguno, no escribió nada, y la acción pasa a ser con el titular: corrígelos con él como en el punto 4 de la acción 1 de «Con hoja».
2. **Módulos (automática):** los de la acción 2 de «Con hoja»: 00, 06 y 08.
3. **Primera instantánea (automática):** la acción 3 de «Con hoja».
4. **Un solo commit (automática):** la acción 4 de «Con hoja».
5. **Canal Web (con el titular):** la acción 5 de «Con hoja». En modo local, su proyecto web, si lo tenía, solo leía los módulos subidos a mano: `/conectar-web` lo reconecta igual.

## v1.1 — 2026-10-18

### Qué cambió

- Tu copia también funciona sin suscripción de Claude, con otro agente con terminal en modo local, como Antigravity con Gemini gratis. Es experimental; ver «Sin suscripción de Claude» en el README.
- Los módulos y las skills hablan de «el agente» en lugar de «Claude», salvo en lo que solo funciona con Claude: el canal Web, la hoja de Google y el proyecto de claude.ai.
- Si tu agente corre los comandos sin internet, `/configurar` y `/actualizar` te lo explican y te dicen cómo darle red.
- `/configurar` ya no te pide instalar markdownlint-cli2 cuando ya lo tienes, y al terminar te lleva a tu primera búsqueda, en una conversación nueva.

### En la copia

Sin acciones.

## v1.0 — 2026-10-17

### Qué cambió

Versión inicial.

### En la copia

Versión inicial, sin acciones.
