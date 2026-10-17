# Trabajo en esta copia de ChambaKit

Esta carpeta es la copia de ChambaKit de un titular: los módulos 00–11 con su perfil, su CV y su método de búsqueda laboral, más las herramientas del canal Code. No es una aplicación. Conversa en español.

## Al iniciar

1. Corre `git config --local --get chambakit.mantenedor`. Si da `true`, hablas con el mantenedor de la plantilla: lee `CONTRIBUTING.md` y salta al paso 4.
2. Lee `00_INSTRUCCIONES_PROYECTO.md` (las mismas reglas que el proyecto web) y la tabla ESTADO de `01_MAPA_DEL_PROYECTO.md`.
3. Si alguna fila de ESTADO dice «Sin llenar», ofrece `/configurar` en tu primera respuesta.
4. Lee el módulo pedido.

## Reglas de trabajo

- **Arquitectura:**
  - Los módulos 00–11 son `.md`. Si el titular usa el canal Web, se suben como conocimiento de un proyecto de claude.ai y 00 se pega en «Instrucciones».
  - Los registros viven donde indica 00 («Registros»), con el esquema de 11, no en CSV sueltos.
  - Los módulos solo se editan aquí; el proyecto web es una réplica de solo lectura. Las notas para Code que deja un chat web se aplican aquí (00, «Cambios a los módulos»).
- **Copia privada:** antes de editar el primer módulo de la sesión, haz la revisión del paso 1 de `/configurar` (`.claude/skills/configurar/SKILL.md`), salvo que la skill ya la haya hecho.
- **Alcance de cada sesión:** un módulo o sección a la vez, salvo que el titular pida otra cosa. Un módulo ya lleno conserva su contenido, sus fuentes y sus IDs: amplíalo con hechos nuevos en lugar de repetir su entrevista.
- **Datos y búsquedas:** no inventes datos, métricas, preferencias ni verificaciones; lo que falte se le pregunta al titular. No inicies búsquedas laborales por abrir la copia.
- **Empresas:** cada una tiene su ficha con ID dentro de 06; no crees `EMPRESA_<NOMBRE>.md`.
- **Canal Code (07/BUS-CANALES):** aquí la terminal sí llega a los portales. Las búsquedas usan `python3 -I herramientas/buscar.py` y se registran donde indica 00, con `canal` = `Code`. Atiende las líneas «revisar» y `[FALLO]` antes de registrar. Guarda la salida JSON en el directorio temporal de la sesión, no en esta carpeta.
- **Empresa nueva:** identifica la plataforma de reclutamiento de su portal. Si el script ya tiene su adaptador, basta la ficha en 06 con su configuración. Si no, busca la API que usa el portal y revisa su `robots.txt` antes de construir un adaptador en esta copia: no uses rutas que prohíba.
- **Formato Markdown:** tras editar un `.md`, corre `markdownlint-cli2` sobre él y deja cero advertencias (reglas en `.markdownlint-cli2.jsonc`; lo instala `/configurar`). En CV-ES y CV-EN de 03, conserva las negritas y los niveles de `###` al corregir el lint: `herramientas/generar_cv.py` lee ese formato literal (09/CV-HERRAMIENTAS).
- **Al cerrar una sesión que modificó un módulo:**
  - Actualiza la versión, la fecha y la línea de cambio del módulo, y su fila en la tabla ESTADO de 01. En 06, también la versión y la fecha de comprobación de la ficha.
  - Si 00 («Registros») tiene la URL de la hoja, recuérdale reemplazar en su proyecto web, si lo tiene, cada módulo editado (00 se vuelve a pegar en «Instrucciones»).
  - Una búsqueda no modifica módulos: sus resultados quedan solo en los registros (07/BUS-REGISTRO).
- **Al cerrar una sesión que escribió en el archivo del modo local:** ofrece el commit de 11/REG-LOCAL («Historial y respaldo»).
