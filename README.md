# ChambaKit

ChambaKit es una plantilla para buscar trabajo con Claude. Tu copia guarda tu perfil, tu CV y tu método de búsqueda en archivos Markdown, y Claude trabaja sobre ellos desde Claude Code, en VS Code, y, si quieres, desde un proyecto de claude.ai.

No es una aplicación: son instrucciones, módulos y unos scripts de Python. Claude te entrevista para llenar los módulos y después los usa para buscar vacantes, evaluarlas y adaptar tu CV.

## Qué hace

- **Perfil maestro:** reúne tu trayectoria desde tu CV actual y el PDF de tu perfil de LinkedIn, cada dato con su fuente, y te pregunta solo lo que falta. No inventa datos, métricas ni habilidades.
- **CV base** en español e inglés, en PDF y DOCX editable.
- **Preferencias:** dónde quieres trabajar (una ciudad, varias, varios países o solo remoto), modalidad, sueldo en tu moneda y los tipos de puesto que excluyes.
- **Búsqueda de vacantes** en las empresas que elijas, leyendo directo sus portales de empleo. El script trae adaptadores para Workday, Eightfold, SmartRecruiters, Workable y Oracle Recruiting Cloud. Para otra plataforma, Claude construye uno en tu copia, solo con las rutas que permite el `robots.txt` del sitio.
- **Evaluación** de cada vacante contra tu perfil y tus condiciones, con una tabla resumen por búsqueda.
- **CV adaptado** a una vacante, con hechos de tu perfil y sin exagerarlos.
- **Registros** de búsquedas, vacantes, evaluaciones y documentos, en un archivo de tu copia.
- **Tendencias:** qué habilidades piden las vacantes que registraste.

Claude nunca postula ni contacta a nadie por ti.

## Qué necesitas

- **VS Code** con la extensión **Claude Code**.
- **Una cuenta de claude.ai** con plan Pro, Max, Team o Enterprise, con la que inicias sesión en Claude Code. El plan gratuito no incluye Claude Code.
- **Tu CV actual**, en PDF o DOCX, y, si lo tienes, el PDF de tu perfil de LinkedIn. Sin CV también se puede: Claude te entrevista sección por sección.
- **Opcional, una cuenta de GitHub:** para crear tu copia con «Use this template» y usar ChambaKit desde claude.ai. Sin ella, usa el ZIP.

Lo demás lo instala `/configurar` cuando hace falta, siempre con tu permiso: Python, Node y markdownlint-cli2 al empezar; LibreOffice, poppler y la fuente Carlito al generar tu primer CV; y, al crear tus registros, la biblioteca `openpyxl`, en un entorno virtual dentro de tu copia.

**Sistemas:** solo Linux está probado. En macOS y Windows, `/configurar` instala con Homebrew o winget, pero un fallo puede venir de ahí.

## Sin suscripción de Claude

**Experimental.** Tu copia también funciona con Antigravity, el agente de Google, y Gemini en su plan gratuito. Puedes configurarla, buscar vacantes, evaluarlas, generar tu CV y actualizar tu copia, como con Claude Code. Gemini puede seguir peor que Claude las reglas largas de tu copia, como no inventar datos, así que revisa lo que escribe.

Sin Claude no funciona el canal Web, que es un proyecto de claude.ai.

Necesitas:

- **Antigravity** instalado.
- **Una sesión** iniciada en Antigravity con una cuenta de Google.
- **La carpeta de tu copia** abierta en Antigravity.

Para empezar, escribe `/configurar` o, si tu Antigravity no admite comandos con barra, «configura mi copia». Para actualizar, `/actualizar` o «actualiza mi copia».

En Linux y macOS, con el preset de permisos «Default», Antigravity corre los comandos sin internet. La primera vez que un comando lo necesite, como al revisar o instalar herramientas o al buscar vacantes, el agente te va a pedir que cambies el preset a «Request Review», en el que apruebas cada comando antes de que corra, y no «Turbo», que los corre sin preguntarte.

La línea «Sistemas» de arriba vale también aquí: solo Linux está probado.

Otros agentes que lean `AGENTS.md` y las skills de `.agents/skills/` podrían funcionar igual, pero no están probados.

## Crea tu copia privada

Tu copia va a guardar tus datos personales: contacto, trayectoria, sueldo deseado, empresas y búsquedas. En un repositorio público, cualquiera podría leerlos. Por eso tu copia debe ser un repositorio privado o una carpeta sin remoto.

No uses «Fork»: el fork de un repositorio público también es público. Si clonas esta plantilla en lugar de crear tu copia, Claude te lo dice y te ofrece desconectar el clon de GitHub, para que siga solo en tu equipo, o crear tu copia privada con «Use this template». Antes de llenar nada, Claude revisa la visibilidad de tu copia y te avisa si es pública.

### Con «Use this template»

1. En esta página, arriba de la lista de archivos, selecciona «Use this template» → «Create a new repository».
2. Elige tu cuenta como dueña, ponle un nombre y marca la visibilidad **Private**. Termina con «Create repository from template». Tu copia empieza con un solo commit, sin el historial de la plantilla.
3. Clona tu repositorio nuevo en tu equipo. En VS Code, con git instalado, abre la paleta de comandos, elige «Git: Clone», inicia sesión en GitHub y elige tu repositorio.

Así tienes el historial de tus cambios y un respaldo privado en GitHub.

### Con el ZIP

1. En esta página, selecciona «Code» → «Download ZIP».
2. Descomprime el archivo donde quieras guardar tu copia.

La carpeta no es un repositorio de git: no tiene remoto, así que nada se publica, pero tampoco guarda historial. Si quieres historial, conviértela en repositorio con `git init` y un primer commit; si algún día le agregas un remoto, que sea privado. Conviene hacerlo, porque git es el único respaldo de tus registros.

## Empieza

1. En VS Code, abre la carpeta de tu copia («File» → «Open Folder»).
2. Abre Claude Code e inicia sesión con tu cuenta de claude.ai, si todavía no lo has hecho.
3. Escríbele, por ejemplo, «Hola». Claude ve que tu copia está sin llenar y te ofrece `/configurar`: acepta. También puedes escribir `/configurar` cuando quieras.

`/configurar` avanza un paso corto a la vez:

1. Revisa que tu copia sea privada.
2. Instala las herramientas básicas.
3. Llena tu perfil maestro desde tu CV y te pregunta lo que falte.
4. Te pregunta tus preferencias.
5. Relaciona tus habilidades con las familias de roles que buscas.
6. Redacta tu CV base en español e inglés y genera el primero con el color que elijas.
7. Da de alta las empresas donde quieres buscar. Si no sabes cuáles, puede proponerte algunas.
8. Crea tu archivo de registros.
9. Opcional: te ofrece conectar tu copia a un proyecto de claude.ai.

Puedes repartirlo en varias sesiones. El avance queda en la tabla ESTADO de `01_MAPA_DEL_PROYECTO.md`, y `/configurar` retoma donde quedó.

Con la copia configurada, pídele a Claude lo que necesites con tus palabras: buscar vacantes, evaluar una, adaptar tu CV a ella o revisar tendencias.

## Actualiza tu copia

La plantilla publica versiones nuevas, con lo que trae cada una en [CAMBIOS.md](CAMBIOS.md). Tu copia no se entera sola: cuando quieras las mejoras, escribe `/actualizar` en Claude Code. Claude trae la versión más reciente, la fusiona archivo por archivo con tu copia y conserva lo que escribiste; si un cambio choca con tus datos, te pregunta. Al final te propone un solo commit, que puedes revisar antes.

Necesita que tu copia sea un repositorio de git sin cambios pendientes. Si la creaste con el ZIP y todavía no es repositorio, conviértela con `git init` y un primer commit con todo.

## Dónde se usa

ChambaKit tiene dos canales:

| | Code | Web |
| --- | --- | --- |
| Dónde | Claude Code en VS Code, sobre tu copia | Un proyecto de claude.ai, desde cualquier dispositivo |
| Módulos | Los edita: es el único lugar donde se editan | Los lee; un cambio queda como nota para aplicarlo en Code |
| Búsqueda | En todas tus empresas, con el script de búsqueda | No busca; revisa una vacante que nombres o pegues |
| Archivo del CV | Lo genera, en PDF y DOCX | Se genera en Code; aquí se puede adaptar el texto |
| Registros | Los escribe en el archivo de tu copia | Lee su instantánea; lo que quieras conservar queda como nota para Code |

**Registros:** viven en el archivo `ChambaKit_Registros.xlsx` de tu copia, que el agente escribe con un script. Cada escritura regenera la instantánea, una copia en Markdown en la carpeta `instantanea/` que lee el proyecto web. El respaldo y el historial del archivo son los commits de tu copia.

**Proyecto web:** lee tus módulos y la instantánea desde tu repositorio privado de GitHub. Al final, `/configurar` te ofrece conectarlo. Cada vez que el agente sube tus cambios, pulsas «Sync» en el proyecto para que los reciba; el agente te lo recuerda.

## Contribuir

Para mantener la plantilla o proponerle cambios, lee [CONTRIBUTING.md](CONTRIBUTING.md). Tu copia no lo necesita.

## Licencia

[MIT](LICENSE).
