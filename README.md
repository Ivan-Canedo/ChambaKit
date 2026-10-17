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
- **Registros** de búsquedas, vacantes, evaluaciones y documentos, en una hoja de Google o, sin Google, en un archivo de tu copia.
- **Tendencias:** qué habilidades piden las vacantes que registraste.

Claude nunca postula ni contacta a nadie por ti.

## Qué necesitas

- **VS Code** con la extensión **Claude Code**.
- **Una cuenta de claude.ai** con plan Pro, Max, Team o Enterprise, con la que inicias sesión en Claude Code. El plan gratuito no incluye Claude Code.
- **Tu CV actual**, en PDF o DOCX, y, si lo tienes, el PDF de tu perfil de LinkedIn. Sin CV también se puede: Claude te entrevista sección por sección.
- **Opcional, una cuenta de Google:** para tener la hoja de registros en tu Drive y usar ChambaKit desde claude.ai. Sin ella, tu copia trabaja en modo local.
- **Opcional, una cuenta de GitHub:** para crear tu copia con «Use this template». Sin ella, usa el ZIP.

Lo demás lo instala `/configurar` cuando hace falta, siempre con tu permiso: Python, Node y markdownlint-cli2 al empezar; LibreOffice, poppler y la fuente Carlito al generar tu primer CV; y, solo en modo local, la biblioteca `openpyxl`, en un entorno virtual dentro de tu copia.

**Sistemas:** solo Linux está probado. En macOS y Windows, `/configurar` instala con Homebrew o winget, pero un fallo puede venir de ahí.

### Conectores de Google en Claude Code

La hoja de registros se crea y se usa con los conectores «Google Drive» y «Google Sheets», que conectas en claude.ai. Según la documentación de Claude Code ([«Use MCP servers from claude.ai»](https://code.claude.com/docs/en/mcp#use-mcp-servers-from-claude-ai), consultada el 2026-10-17):

- Los conectores de claude.ai aparecen en Claude Code solo cuando la autenticación activa es el inicio de sesión con una suscripción de claude.ai.
- No se cargan, aunque antes hayas corrido `/login`, si la credencial viene de otro lado: una clave de API (`ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` o `apiKeyHelper`), un proveedor externo como Amazon Bedrock o Google Cloud, un perfil de Anthropic (`ANTHROPIC_PROFILE`) o un token de `claude setup-token`.
- `/status` muestra qué autenticación está activa, y `/mcp` lista los conectores.
- En un plan Team o Enterprise, un Owner de la organización tiene que agregar los conectores primero.

Si te faltan, `/configurar` te guía para conectarlos. Si no los conectas, tu copia trabaja en modo local.

## Crea tu copia privada

Tu copia va a guardar tus datos personales: contacto, trayectoria, sueldo deseado, empresas y búsquedas. En un repositorio público, cualquiera podría leerlos. Por eso tu copia debe ser un repositorio privado o una carpeta sin remoto.

No uses «Fork»: el fork de un repositorio público también es público. Si clonas esta plantilla en lugar de crear tu copia, Claude te lo dice y no la configura hasta que trabajes en tu copia o le quites el remoto al clon para seguir sin GitHub. Antes de llenar nada, Claude revisa la visibilidad de tu copia y te avisa si es pública.

### Con «Use this template»

1. En esta página, arriba de la lista de archivos, selecciona «Use this template» → «Create a new repository».
2. Elige tu cuenta como dueña, ponle un nombre y marca la visibilidad **Private**. Termina con «Create repository from template». Tu copia empieza con un solo commit, sin el historial de la plantilla.
3. Clona tu repositorio nuevo en tu equipo. En VS Code, con git instalado, abre la paleta de comandos, elige «Git: Clone», inicia sesión en GitHub y elige tu repositorio.

Así tienes el historial de tus cambios y un respaldo privado en GitHub.

### Con el ZIP

1. En esta página, selecciona «Code» → «Download ZIP».
2. Descomprime el archivo donde quieras guardar tu copia.

La carpeta no es un repositorio de git: no tiene remoto, así que nada se publica, pero tampoco guarda historial. Si quieres historial, conviértela en repositorio con `git init` y un primer commit; si algún día le agregas un remoto, que sea privado. En modo local conviene hacerlo, porque git es el único respaldo de tus registros.

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
8. Crea tus registros: la hoja de Google o, si no conectas Google, el archivo del modo local.
9. Opcional, solo con la hoja: te da la lista de pasos para crear tu proyecto en claude.ai.

Puedes repartirlo en varias sesiones. El avance queda en la tabla ESTADO de `01_MAPA_DEL_PROYECTO.md`, y `/configurar` retoma donde quedó.

Con la copia configurada, pídele a Claude lo que necesites con tus palabras: buscar vacantes, evaluar una, adaptar tu CV a ella o revisar tendencias.

## Dónde se usa

ChambaKit tiene dos canales:

| | Code | Web |
| --- | --- | --- |
| Dónde | Claude Code en VS Code, sobre tu copia | Un proyecto de claude.ai, desde cualquier dispositivo |
| Módulos | Los edita: es el único lugar donde se editan | Los lee; un cambio queda como nota para aplicarlo en Code |
| Búsqueda | En todas tus empresas, con el script de búsqueda | Solo en las empresas que se pueden leer desde la web |
| Archivo del CV | Lo genera, en PDF y DOCX | Se genera en Code; aquí se puede adaptar el texto |
| Registros | La hoja de Google o el archivo del modo local | Solo la hoja de Google |

**Proyecto web:** si usas la hoja de Google, al final de `/configurar` Claude te da la lista para crearlo: crear el proyecto, pegar `00_INSTRUCCIONES_PROYECTO.md` en sus instrucciones, subir los módulos 01 a 11 y vincular la hoja desde Drive. El proyecto es una réplica: cada vez que edites un módulo en Code, reemplázalo ahí. Claude te lo recuerda.

### Modo local

Si no puedes o no quieres conectar Google, tus registros van al archivo `ChambaKit_Registros.xlsx` de tu copia, que Claude escribe y lee con un script. Todo funciona desde Code, pero no hay canal Web: un proyecto de claude.ai no puede leer ese archivo. El respaldo y el historial del archivo son los commits de tu copia.

Si conectas Google después, `/configurar` pasa tus registros a una hoja nueva y retira el archivo. Al revés no se puede.

## Contribuir

Para mantener la plantilla o proponerle cambios, lee [CONTRIBUTING.md](CONTRIBUTING.md). Tu copia no lo necesita.

## Licencia

[MIT](LICENSE).
