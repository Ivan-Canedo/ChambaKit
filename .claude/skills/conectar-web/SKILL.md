---
name: conectar-web
description: Conecta un proyecto de claude.ai con el repositorio privado de GitHub de la copia de ChambaKit, para que el canal Web lea los módulos y la instantánea, o reconecta un proyecto web que leía la hoja de Google. Úsala cuando el titular pida conectar o reconectar el canal Web.
---

# Conectar el canal Web

Lleva la copia del titular a un proyecto de claude.ai que lee sus módulos 01–11 y su instantánea (11/REG-INSTANTANEA) desde su repositorio privado de GitHub, con la integración de GitHub de claude.ai. Sirve también para reconectar un proyecto web que leía la hoja de Google y tenía los módulos subidos a mano.

Escribe para alguien que nunca usó git: nada de jerga sin explicar, y los comandos los corres tú, con su permiso. Ninguna de tus herramientas llega a claude.ai ni a la configuración de GitHub: ahí el titular hace cada clic y tú lo acompañas, un punto a la vez. Esta skill no edita módulos ni tiene fila en ESTADO; revisa por sí misma cómo está la copia cada vez que se invoca.

Si `git config --local --get chambakit.mantenedor` da `true`, esta carpeta es la plantilla: detente y dile al mantenedor que pruebe en un clon temporal con un repositorio de prueba aparte (`CONTRIBUTING.md`).

Si un comando que sale a la red falla porque no se resuelve el nombre o se niega la conexión, sigue «Comandos sin red» de `.claude/skills/configurar/SKILL.md`.

## En palabras simples

Explícaselo al titular al empezar, en tus palabras y sin alargarlo:

- **Su copia** es la carpeta de su equipo. Cada **commit** guarda en ella una versión de sus archivos, como un punto al que se puede volver.
- **Su repositorio de GitHub** es una copia privada de esa carpeta en internet. El **push** sube a GitHub los commits que todavía no estaban ahí. Sin push, GitHub no se entera de lo nuevo.
- **El proyecto de claude.ai** no lee su equipo: lee GitHub. **«Sync»** le dice al proyecto que traiga de GitHub la versión más reciente de los archivos elegidos. Ningún agente puede pulsarlo por él.

Por eso, cada vez que algo cambia en Code: el agente hace el commit y el push (con su permiso), y después él pulsa «Sync» en el proyecto.

## Paso 1: Revisar la copia

1. **Versión:** si la sección «Registros» de `00_INSTRUCCIONES_PROYECTO.md` no menciona `instantanea/`, la copia es de antes de 2.0: dile que primero escriba `/actualizar` y detente.
2. **Archivo de registros:** si `ChambaKit_Registros.xlsx` no existe, falta el paso 8 de `/configurar`: díselo y detente.
3. **Repositorio:** `git rev-parse --is-inside-work-tree`. Si la carpeta no es un repositorio de git (la descargó como ZIP), explícale que hay que convertirla en uno para subirla, y con su permiso:
   1. Si `git config user.name` o `git config user.email` no dan nada, pregúntale su nombre y el correo para sus commits, y guárdalos en la copia con `git config user.name` y `git config user.email`. Si no quiere publicar su correo, el de GitHub sin respuesta (`<usuario>@users.noreply.github.com`) sirve.
   2. `git init -b main`, `git add -A` y `git commit -m "Copia de ChambaKit"`.
4. **Instantánea:** si la carpeta `instantanea/` no existe, créala con `.venv/bin/python -I herramientas/registros.py instantanea` (en Windows, con `.venv\Scripts\python.exe`). Antes de la primera búsqueda trae las vistas vacías, con su fecha; sirve para la prueba.
5. **Cambios sin guardar:** `git status --porcelain`. Si lista algo, muéstraselo en pocas líneas y ofrécele el commit: el proyecto solo recibe lo que tiene commit y push.
6. **Remoto:** `git remote -v`.
   - **Apunta a la plantilla** (`github.com/Ivan-Canedo/ChambaKit`): su copia es un clon de la plantilla pública. Dile que escriba `/configurar`, cuyo paso 1 lo resuelve, y detente.
   - **Un repositorio de GitHub:** revisa su visibilidad como en el paso 1 de `/configurar` (punto 3). Si es público, no sigas: la instantánea lleva sus datos personales. Dile cómo volverlo privado («Settings» → «General» → «Danger Zone» → «Change visibility») y que vuelva a invocar `/conectar-web` cuando lo esté. Si es privado, sigue en el punto 7.
   - **Otro servicio** (GitLab, Bitbucket…): dile en dos líneas que el proyecto web solo lee repositorios de GitHub, así que puede crear un proyecto y subir a mano los módulos 01–11 y los archivos de `instantanea/`, reemplazándolos cada vez que cambien, o quedarse sin canal Web. Detente.
   - **Sin remoto:** su copia está solo en su equipo. Sigue en el paso 2.
7. **Push pendiente:** `git status -sb`. Si su rama va adelante del remoto (`ahead`), ofrécele el push (`git push`). Si la primera línea no nombra una rama remota (`...origin/<rama>`), la rama nunca se subió: ofrécele `git push -u origin <rama>`. Sigue en el paso 3 o, si ya tiene un proyecto web que no lee su repositorio, en el paso 4.

## Paso 2: Subir la copia a un repositorio privado

Explícale que vas a crear en su cuenta de GitHub un repositorio **privado**, que solo él puede ver, y subir ahí su copia. Si no tiene cuenta de GitHub, que la cree en <https://github.com/signup>. Pídele el nombre del repositorio; si no tiene preferencia, propón `ChambaKit`. La rama es la que da `git branch --show-current`.

**Con `gh`:** si `gh auth status` dice que tiene sesión iniciada, muéstrale este comando y pide su permiso antes de correrlo:

```sh
gh repo create <nombre> --private --source . --remote origin --push
```

**Sin `gh`:** guíalo para crear un repositorio vacío y después súbelo tú:

1. En GitHub, abre <https://github.com/new>.
2. En «Repository name», escribe el nombre.
3. Elige **Private**.
4. Deja apagados «Add README», «.gitignore» y «License»: el repositorio tiene que nacer vacío para recibir su copia.
5. Selecciona «Create repository».
6. Copia la dirección HTTPS que muestra la página, que termina en `.git`, y pégala en esta conversación.

Con su permiso, corre `git remote add origin <URL>` y `git push -u origin <rama>`. Si el push pide usuario y contraseña, o falla por autenticación, GitHub no acepta la contraseña de la cuenta: pídele que corra él el mismo `git push -u origin <rama>` en la terminal de VS Code, que le abre el inicio de sesión de GitHub en el navegador, o que instale `gh` y entre con `gh auth login`.

**Comprobación:** la primera línea de `git status -sb` nombra `origin/<rama>` sin `ahead`, y la visibilidad, revisada como en el paso 1 de `/configurar`, es privada. Sigue en el paso 3 o, si ya tiene un proyecto web, en el paso 4.

## Paso 3: Proyecto nuevo en claude.ai

Dale los puntos uno a la vez y espera a que te diga que terminó cada uno o en cuál tuvo un problema.

1. **Proyecto:** en claude.ai, abre «Projects» en la barra lateral (<https://claude.ai/projects>) y selecciona «+ New Project». Ponle un nombre, como «ChambaKit». En un plan Team o Enterprise, elige «Keep it private»: el proyecto va a tener sus datos.
2. **Instrucciones:** selecciona «Set project instructions», pega el contenido completo de `00_INSTRUCCIONES_PROYECTO.md` de su copia y guárdalo con «Save instructions». 00 va solo en ese campo, no como archivo.
3. **GitHub:** en la sección de conocimiento del proyecto, selecciona «+» → «GitHub».
   1. La primera vez, claude.ai lo manda a GitHub para darle permiso a la app de Claude. En la pantalla de instalación, elige «Only select repositories», elige el repositorio de su copia y confirma con «Install» (puede decir «Install & Authorize»). Así la app solo ve ese repositorio.
   2. De vuelta en claude.ai, busca el repositorio por su nombre o pega su dirección.
4. **Archivos:** en el explorador de archivos que se abre, el mismo de «Configure files», marca solo los once módulos, de `01_MAPA_DEL_PROYECTO.md` a `11_ESQUEMAS_DE_REGISTROS.md`, y la carpeta `instantanea`, y agrégalos al conocimiento del proyecto. Nada más: 00 ya está en «Instrucciones», y el archivo de registros, las herramientas y lo demás de 01 («Fuera del proyecto») se quedan en la copia. Para cambiar la selección después, el ícono «Configure files» vuelve a abrirlo.
5. **Sync:** selecciona el ícono «Sync» («Sync now») del repositorio, para traer la versión más reciente.

Sigue con la prueba (paso 5).

## Paso 4: Reconectar un proyecto existente

Para un proyecto web que ya tiene, sobre todo uno de antes de 2.0, que leía la hoja de Google y tenía los módulos subidos a mano. Se conserva el proyecto con sus instrucciones y sus chats; solo cambia de dónde lee.

1. **Archivos viejos:** en la sección de conocimiento del proyecto, quita los módulos que subió a mano (`01_…` a `11_…`) y el vínculo de la hoja de Drive (`ChambaKit_Registros`), con la opción de quitar de cada archivo. Quitarlos del proyecto no borra nada de su copia ni de su Drive: la hoja sigue en Drive y él decide si la borra.
2. **Instrucciones:** abre las instrucciones del proyecto y reemplaza su texto por el contenido actual de `00_INSTRUCCIONES_PROYECTO.md`, que cambió con 2.0, y guárdalo con «Save instructions».
3. **GitHub, archivos y Sync:** los puntos 3 a 5 del paso 3.
4. **Chats viejos:** siguen ahí, pero hablan de la hoja. Para trabajar con la instantánea, que abra un chat nuevo. El conector de Google Sheets ya no hace falta en los chats del proyecto.

Sigue con la prueba (paso 5).

## Paso 5: Prueba

1. Lee la línea **Exportada:** del encabezado de `instantanea/informes.md` de la copia.
2. Pídele que abra un chat nuevo en el proyecto y escriba: «Muéstrame la tabla ESTADO de 01 y la fecha de exportación de la instantánea».
3. La respuesta debe traer la tabla de 01 y la misma fecha que leíste, sin pedirle archivos. Si es así, el canal Web quedó conectado.
4. **Si algo falla,** ayúdale según lo que vea y repite la prueba en un chat nuevo:
   - **No encuentra su repositorio al buscarlo:** la app de Claude no tiene permiso sobre él. En GitHub, en <https://github.com/settings/installations>, «Configure» junto a la app de Claude, y en «Repository access» agrega el repositorio. En una organización de GitHub, quizá un administrador tenga que aprobarlo.
   - **No trae la tabla de 01, o pide archivos:** los módulos no están elegidos. «Configure files» y marcar los once (paso 3, punto 4); después «Sync».
   - **No trae la fecha de la instantánea:** la carpeta `instantanea` no está elegida («Configure files»), o no llegó a GitHub. Revisa con `git status -sb` que no haya commits sin push y con `git ls-files instantanea` que la carpeta tenga commit.
   - **Trae una fecha más vieja:** falta el push del último commit (`git status -sb`) o faltó pulsar «Sync» después.
   - **Las respuestas siguen hablando de la hoja:** las instrucciones son las de antes de 2.0 (paso 4, punto 2).

## Mantenerlo al día

Antes de terminar, explícale cómo sigue, en pocas líneas:

- Cada vez que una sesión en Code cambie un módulo o los registros, el agente le ofrece el commit y el push, y le recuerda pulsar «Sync» en el proyecto (AGENTS.md, «Al cerrar»). El encabezado de la instantánea dice hasta cuándo están al día los datos que ve en Web.
- Si cambia 00, se vuelve a pegar en «Instrucciones»: no llega por «Sync».
- En Web no se editan módulos ni registros: lo que quiera conservar queda en una nota para Code, que se aplica en la copia (00, «Cambios a los módulos» y «Cambios a los registros»).

Si llegó desde `/configurar`, dile que vuelva a esa conversación para cerrar la configuración.
