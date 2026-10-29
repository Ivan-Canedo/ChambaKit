---
name: conectar-nube
description: Prepara la copia de ChambaKit para Claude Code en la nube (claude.ai/code y la pestaña Code de la app), con su repositorio privado de GitHub y un entorno de la nube con la lista de dominios de sus empresas, y termina con una búsqueda de prueba. Úsala cuando el titular pida conectar o usar Code en la nube.
---

# Conectar Code en la nube

Deja la copia del titular lista para Code en la nube (ADR 0007): sesiones de Claude Code que corren en una máquina de Anthropic, abiertas desde claude.ai/code o desde la pestaña Code de la app de Claude, sobre un clon de su repositorio privado de GitHub. Ahí el agente busca, registra y genera el CV como en Code local, también desde el teléfono.

Escribe para alguien que nunca usó git: nada de jerga sin explicar, y los comandos los corres tú, con su permiso. Ninguna de tus herramientas llega a claude.ai ni a la configuración de GitHub: ahí el titular hace cada clic y tú lo acompañas, un punto a la vez. Esta skill no edita módulos ni tiene fila en ESTADO; revisa por sí misma cómo está la copia cada vez que se invoca.

Si `git config --local --get chambakit.mantenedor` da `true`, esta carpeta es la plantilla: detente y dile al mantenedor que pruebe en un clon temporal con un repositorio privado de prueba aparte y datos sintéticos (`CONTRIBUTING.md`).

Si un comando que sale a la red falla porque no se resuelve el nombre o se niega la conexión, sigue «Comandos sin red» de `.claude/skills/configurar/SKILL.md`.

## En palabras simples

Explícaselo al titular al empezar, en tus palabras y sin alargarlo:

- **Una sesión en la nube** es una conversación con el mismo agente, pero en una computadora de Anthropic y no en su equipo. Cada sesión empieza con una copia nueva de su repositorio de GitHub: solo ve lo que ya subió con un **push**, y lo que haga ahí llega a su equipo cuando el agente lo sube a GitHub al cerrar, con su permiso.
- **El entorno de la nube** es la configuración con que arranca cada sesión. La parte que importa es la **lista de dominios**: los únicos sitios de internet a los que la sesión puede llegar. Ahí van los portales de empleo de sus empresas; así sus datos no pueden salir a ningún otro sitio. El entorno de la nube vive en su cuenta de claude.ai, no en su copia, y ningún agente puede cambiarlo por él.
- **La preparación es sola:** al abrir cada sesión, su copia instala lo que hace falta para el CV y los registros. Tarda menos de un minuto y no le pide nada.

## Paso 1: Revisar la copia

1. **Ya en la nube:** si `CLAUDE_CODE_REMOTE` vale `true`, esta sesión ya corre en la nube, así que el repositorio y un entorno de la nube ya existen. Salta al paso 3 para armar la lista de dominios, y en lugar de crear un entorno de la nube, que edite el de esta sesión: en la parte de arriba, el control junto al título de la sesión → «Edit cloud environment». Después, la prueba del paso 4 en una sesión nueva.
2. **Versión:** si `herramientas/preparar_nube.sh` no existe, la copia es de una versión que no se prepara sola en la nube: dile que primero escriba `/actualizar`, en Code local, y detente.
3. **Repositorio, cambios y remoto:** sigue los puntos 3, 5, 6 y 7 del paso 1 de `/conectar-web` (`.claude/skills/conectar-web/SKILL.md`), con estos cambios:
   - **Remoto público:** no ofrezcas la nube. Dile que su copia lleva sus datos personales (su perfil, su CV y sus registros), cómo volver privado el repositorio («Settings» → «General» → «Danger Zone» → «Change visibility») y que vuelva a invocar `/conectar-nube` cuando lo esté. Detente.
   - **Otro servicio** (GitLab, Bitbucket…): dile en dos líneas que Code en la nube solo trabaja con repositorios de GitHub, así que puede mover su copia a un repositorio privado de GitHub o seguir con Code local. Detente.
   - **Sin remoto:** sigue el paso 2 de `/conectar-web`, que crea el repositorio privado y sube su copia.
   - **Salidas:** donde esos puntos o el paso 2 te manden al paso 3 o al paso 4 de `/conectar-web`, sigue aquí con el punto 4.
4. **Rama:** `git branch --show-current`. Las sesiones en la nube integran sus cambios en `main` (11/REG-LOCAL, «Historial y respaldo»). Si su rama tiene otro nombre, díselo en una línea y pregúntale si la renombras a `main`, local y en GitHub, antes de seguir.
5. **Empresas:** lee CAT-EMPRESAS de `06_EMPRESAS_OBJETIVO.md`. Si no tiene ninguna, dile que la lista de dominios queda vacía por ahora y que la prueba del paso 4 solo comprobará la preparación de la sesión; cuando agregue empresas (paso 7 de `/configurar`), el agente le da el dominio de cada una (07/BUS-CANALES, «Empresa nueva»).

## Paso 2: GitHub en claude.ai/code

Dale los puntos uno a la vez y espera a que te diga que terminó cada uno o en cuál tuvo un problema.

1. **Entrar:** que abra <https://claude.ai/code> con su cuenta de claude.ai. Code en la nube viene con los planes Pro, Max, Team y Enterprise (en estos dos, con un asiento que incluya Claude Code). Si ve «Claude Code isn't available on your account», su plan no lo incluye: díselo y detente.
2. **Conectar GitHub:** la página le pide conectar GitHub y lo manda a GitHub para autorizarlo. Que apruebe y vuelva a claude.ai/code. Si ya lo había conectado, la página no se lo pide.
3. **Permiso sobre su repositorio:** la sesión solo puede abrir un repositorio privado si la app de Claude de GitHub está instalada en él.
   - Si conectó el canal Web con `/conectar-web`, la app ya está instalada; que revise que incluye este repositorio en <https://github.com/settings/installations>, «Configure» junto a la app de Claude, «Repository access».
   - Si no, que abra <https://github.com/apps/claude/installations/new>, elija su cuenta, marque «Only select repositories», elija el repositorio de su copia y confirme con «Install». Así la app solo ve ese repositorio.
4. **Comprobación:** en la pantalla de sesión nueva de claude.ai/code, el selector de repositorio, debajo del cuadro de mensaje, debe mostrar su repositorio. Si no aparece, el permiso del punto 3 no lo incluye.

Al conectar GitHub, claude.ai puede crear un entorno de la nube «Default». No sirve para buscar: su red (Trusted) no llega a los portales. Se queda ahí sin estorbar; el paso 3 crea el de ChambaKit.

## Paso 3: Entorno de la nube

1. **Lista de dominios:** ármala tú desde 06 y muéstrasela en un bloque de texto, un dominio por línea, lista para copiar:
   1. Sigue la regla de CAT-PLATAFORMAS («Hosts»), con la `plataforma` y el `portal` del bloque de «### Configuración» de cada ficha del catálogo.
   2. Si deja fuera Workable, nombra en una línea esas empresas y dile que se buscan en Code local.
   3. Un adaptador construido en la copia sin hosts en CAT-PLATAFORMAS pone el host de su `portal` y los que pida su código en `herramientas/buscar.py`.
2. **Entorno de la nube nuevo:** en la pantalla de sesión nueva de claude.ai/code, que abra el selector de entorno, el primer control de la fila bajo el cuadro de mensaje, y elija «New environment». En el diálogo:
   1. **Nombre:** «ChambaKit».
   2. **«Network access»:** **Custom**. En «Allowed domains», que pegue la lista. Que marque «Also include default list of common package managers»: sin ella, la sesión no puede instalar lo que necesita. Si pregunta por **Full**: deja pasar cualquier dominio y no pide lista, pero entonces los datos de la sesión podrían salir a cualquier sitio; Custom solo los deja ir a sus portales.
   3. **«Setup script»:** vacío. La preparación de cada sesión ya viene en su copia y se actualiza con ella.
   4. **«Environment variables»:** ninguna.
   5. Que guarde con «Add environment».
3. **Comprobación:** al volver a la pantalla de sesión nueva, el selector de entorno muestra «ChambaKit». Si tiene más de un entorno, que lo elija ahí cada vez que abra una sesión de ChambaKit, también en el teléfono. GitHub no pasa por la lista, así que el agente sube y baja su copia sin agregar nada.

## Paso 4: Búsqueda de prueba

1. **Empresa:** elige una del catálogo que no esté en Workable. Si el catálogo está vacío o solo tiene empresas de Workable, la prueba solo revisa la preparación (punto 2).
2. **Sesión:** pídele que abra una sesión nueva en claude.ai/code o en la pestaña Code de la app, con su repositorio y el entorno «ChambaKit», y que escriba, según el caso:
   - con empresa: «Haz una búsqueda de prueba solo en EMP-\<ID\>, sin registrarla, y dime cómo salió»;
   - sin empresa: «Comprueba que la sesión quedó preparada: markdownlint-cli2, LibreOffice y el `.venv` con openpyxl».
3. **Resultado:** que te pegue aquí la respuesta. La búsqueda sale bien con `[OK]`, o `[SIN TOTAL]` con la comprobación de su ficha; la revisión, con una versión de cada herramienta. Si es así, Code en la nube quedó conectado.
4. **Si algo falla,** ayúdale según lo que vea y repite la prueba en la misma sesión:
   - **`[FALLO]` que dice que el host no está en la lista de dominios del entorno de la nube:** falta en la lista el host con que termina el mensaje. Que lo agregue: en esa sesión, el control junto al título → «Edit cloud environment» (o, en la pantalla de sesión nueva, el selector de entorno → el ícono de ajustes junto a «ChambaKit»), «Network access», una línea más en «Allowed domains» y «Save changes». La sesión toma el cambio en un minuto.
   - **`[FALLO]` que dice que el sitio bloquea las IP de Code en la nube:** esa empresa se busca en Code local, como las de Workable; repite con otra.
   - **Un aviso que empieza con «Hook de la nube de ChambaKit», o falta una herramienta:** la preparación no pudo instalar algo. Si nombra `apt`, `npm` o `pip`, casi siempre falta marcar «Also include default list of common package managers» en el entorno de la nube (paso 3, punto 2). Con el entorno de la nube corregido, que abra una sesión nueva.
   - **El agente de la sesión pregunta cómo crear `.venv`:** la preparación no corrió. Revisa aquí con `git ls-files .claude/settings.json herramientas/preparar_nube.sh` que los dos archivos tengan commit, y con `git status -sb`, que no falte un push.
   - **Otro `[FALLO]`,** con un código HTTP, un `robots.txt` o un error de la ficha: no es de la nube; se atiende como en Code local (07/BUS-ACCESO-CODE).
   - **No encuentra su repositorio al abrir la sesión:** el permiso del paso 2, punto 3.

## Mantenerlo al día

Antes de terminar, explícale cómo sigue, en pocas líneas:

- **Empresa nueva:** al dar de alta una empresa, el agente le da en una línea el dominio que va en la lista (07/BUS-CANALES, «Empresa nueva»). Que lo agregue en el entorno de la nube como en el paso 4 antes de buscarla en la nube.
- **Al cerrar una sesión en la nube** que cambió algo, el agente le ofrece subir los cambios a `main` en GitHub, con su permiso (11/REG-LOCAL, «Historial y respaldo»). Así los recibe su equipo y, si lo tiene, el proyecto web, donde pulsa «Sync» como siempre.
- **De vuelta en su equipo,** después de trabajar en la nube, que le pida al agente traer los cambios de GitHub antes de empezar (`git pull`).

Si llegó desde `/configurar`, dile que vuelva a esa conversación para cerrar la configuración.
