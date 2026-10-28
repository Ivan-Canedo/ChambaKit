# 06 — Empresas objetivo y fichas

**Versión:** 1.2 — 2026-10-27 — Sale el canal del catálogo y de las fichas; una ficha puede decir cómo leer el detalle de una vacante desde Web.
**Estado:** plantilla sin empresas. Las agrega el paso 7 de `/configurar` (Empresas), cada una con su ficha y la configuración de su plataforma de reclutamiento.

## CAT-EMPRESAS — Catálogo

| ID | Empresa | Estado | Versión de ficha | Fecha de comprobación |
| --- | --- | --- | --- | --- |

El ID es una referencia interna, no una razón social. Los nombres alternativos y la entidad contratante van en cada ficha. No fusionar empresas por similitud de nombre.

El script de búsqueda (07/BUS-ACCESO-CODE) toma los IDs de esta tabla: sin argumentos, busca en todas sus filas.

## CAT-REGLAS — Mantenimiento

- **Una empresa = una fila + una ficha** `## EMP-<ID> — <Nombre>` en este archivo. Al agregar una: asignar un ID nuevo, sin reutilizar (`EMP-` más un nombre corto en mayúsculas, con letras sin acentos, dígitos y guiones); añadir la fila y escribir la ficha según FICHA-PLANTILLA, dejando como pendiente lo no comprobado. La herramienta de registros lee el catálogo, así que el ID vale para `empresa_id` desde que está aquí (11/REG-CAMPOS).
- **Estado:** «Objetivo» para las que el titular quiere seguir; «Explorada» para una que se conserva solo porque tiene vacantes registradas. Las dos se buscan por defecto, así que una explorada también lleva su configuración.
- **Plataforma:** identificar la plataforma de reclutamiento del portal oficial (CAT-PLATAFORMAS dice cómo se reconoce cada una). Si el script tiene su adaptador, basta el bloque de configuración de la ficha. Si no lo tiene, o el portal es un sitio propio, buscar la API que usa el portal y revisar su `robots.txt` antes de construir un adaptador en `herramientas/buscar.py` de esta copia; después, describir su configuración en CAT-PLATAFORMAS. Sin una ruta que el `robots.txt` permita, la empresa no entra al catálogo.
- **Comprobación:** al dar de alta una empresa o cambiar su configuración, correr el script solo con su ID; debe pasar sus comprobaciones (`[OK]`, o `[SIN TOTAL]` con la comprobación de su ficha). Esa búsqueda de prueba no se registra.
- **Al editar una ficha:** actualizar su versión y su fecha de comprobación. La fecha de edición no es fecha de verificación.
- **Empresas nuevas:** se buscan según 07/BUS-REGLAS; una explorada entra al catálogo solo si el titular la acepta.
- **Inventario:** las fichas no lo guardan. Las vacantes de todas las empresas viven en los registros (11).

## CAT-PLATAFORMAS — Configuración por plataforma

Lo que pone cada plataforma en el bloque de configuración de una ficha y cómo la lee el script. Las plataformas con adaptador en esta copia son las que lista `python3 -I herramientas/buscar.py --help`. Un adaptador construido en la copia se describe aquí con las mismas partes.

### Workday

- **`plataforma`:** `workday`.
- **Cómo se reconoce:** el buscador de empleos vive en `https://<empresa>.wd<N>.myworkdayjobs.com/<sitio>`. Suele enlazarse desde la página de empleo de la empresa o desde su botón de postulación.
- **`portal`:** esa URL, sin la ruta de una vacante. Puede llevar el idioma (`/<idioma>/<sitio>`).
- **Listado:** con la faceta de país del portal, por los nombres de `paises` de 04 de cada país de `localidades`. Si el portal no tiene faceta de país, con los valores de su faceta de ubicación que nombran uno de esos países como una de sus partes («País - Ciudad», «Ciudad, País») o una localidad aceptada.
- **Remoto:** con la faceta de remoto del portal, acotada a los países del remoto si el alcance es `"paises"`. Si no la tiene, con sus ubicaciones «Remote …». Si no hay ninguna de las dos, el script lo avisa con una línea «revisar».
- **`consulta`:** `{"facetas": {"<parámetro>": ["<nombre visible>"]}, "texto": "<búsqueda>"}`, con al menos uno de los dos. Reemplaza el listado por países; sirve para una empresa con miles de vacantes en un país grande. Los parámetros y los nombres son los del portal, que aparecen en `facets` de la respuesta del listado; el script busca sus IDs por nombre en cada ejecución y avisa con «revisar» si un nombre ya no aparece.
- **Vigencia:** `canApply`. `true` = postulación activa; cualquier otro valor sale como «Revisar».
- **Comprobación de ID:** la ruta del detalle termina en `_<jobReqId>`, a veces con un sufijo `-1` (republicación).

| Columna | Campo del detalle |
| --- | --- |
| `job_id` | `jobReqId` |
| `titulo` | `title`, literal |
| `url_oficial` | `externalUrl` |
| `ubicacion_literal` | `location` y `additionalLocations`, unidas con ` \| ` |
| `modalidad_literal` | `remoteType`, literal; si no viene, lo que diga la descripción; si no lo dice, `No publicado` |
| `fecha_publicacion` | `startDate`, fecha sin hora (07/BUS-FECHAS). El listado solo da `postedOn` relativo («Posted 30+ Days Ago»), que no llena la fecha |
| `observaciones.url_fuente` | URL del detalle consultado |

### Eightfold

- **`plataforma`:** `eightfold`.
- **Cómo se reconoce:** el buscador vive en `https://<empresa>.eightfold.ai/careers` o en un dominio de la empresa con la misma ruta `/careers`, y carga las vacantes desde `/api/pcsx`. Su `robots.txt` prohíbe todo salvo `/careers`, `/api/pcsx` y otras rutas para postularse.
- **`portal`:** `https://<sitio>/careers?domain=<dominio>`. El dominio de la empresa aparece en la línea `Sitemap` del `robots.txt` del sitio (`domain=<dominio>`).
- **Solo el buscador con pcsx:** un sitio con el buscador anterior de Eightfold responde HTTP 403 a `/api/pcsx` y sale como `[FALLO]`. Para él se construye un adaptador en la copia (CAT-REGLAS).
- **Listado:** `GET /api/pcsx/search?domain=<dominio>&location=<país>&sort_by=timestamp&start=<n>`, uno por cada país de `localidades`. Usa el primero de sus nombres en `paises` de 04 que el buscador reconoce como país. A una ciudad, o a un nombre que no reconoce, el buscador le aplica un radio (`distance` en `appliedFilters`): ese nombre se salta, y si ninguno sirve, el script lo avisa con «revisar». Trae 10 vacantes por página y el total en `data.count`. `sort_by=timestamp` es el único orden estable; con el de por defecto, las páginas se traslapan.
- **Remoto:** con el filtro de modalidad del buscador (`filter_work_location_option`, con sus valores remotos, como `remote_local`), un listado por cada país del remoto si el alcance es `"paises"`. Si el buscador no tiene ese filtro, con su búsqueda `location=Remote`, que trae las remotas de todos los países. Con el alcance `"paises"`, lo decide el código de país con que termina cada `standardizedLocations`, porque la búsqueda por país también puede traer remotas abiertas a otros países. Si no hay filtro ni búsqueda de remotas, el script lo avisa con una línea «revisar».
- **`consulta`:** `{"ubicaciones": ["<lugar>"], "filtros": {"<filtro>": ["<nombre visible>"]}, "texto": "<búsqueda>"}`, con al menos uno de los tres. Reemplaza el listado por países:
  - **`ubicaciones`:** cada una es un listado aparte, con lo que se escribiría en el buscador de lugar; a una ciudad, el buscador le aplica su radio.
  - **`filtros`:** los `filterName` de `filterDef.allFilters` en la respuesta del listado, con sus opciones por valor o por nombre visible. El script avisa con «revisar» si una opción ya no aparece.
  - **`texto`:** la búsqueda libre del portal (`query`), que también trae vacantes parecidas.
- **Detalle:** `GET /api/pcsx/position_details?position_id=<id>&domain=<dominio>&hl=en`, con el `id` numérico del listado, no `displayJobId`.
- **Vigencia:** `positionUserActions.applyAction.status`. `allowed` (postulación directa) o `log_in` (postulación tras iniciar sesión) = postulación activa; cualquier otro valor sale como «Revisar».
- **Comprobación de ID:** el `id` del detalle es el pedido.

| Columna | Campo del listado |
| --- | --- |
| `job_id` | `displayJobId` |
| `titulo` | `name`, literal |
| `url_oficial` | `https://<sitio>` + `positionUrl` |
| `ubicacion_literal` | `locations`, unidas con ` \| ` |
| `modalidad_literal` | `workLocationOption`, literal; si `locationFlexibility` no es nulo, se agrega ` \| ` y su valor |
| `fecha_publicacion` | `postedTs`, según 07/BUS-FECHAS: a las 00:00 UTC, fecha UTC; con hora real, la fecha en la zona horaria de 04. `creationTs` no se usa |
| `observaciones.url_fuente` | URL del detalle consultado |

### Workable

- **`plataforma`:** `workable`.
- **Cómo se reconoce:** la página de la cuenta de la empresa vive en `https://apply.workable.com/<cuenta>/`. Si la página de empleo de la empresa embebe el widget de Workable, sus enlaces a las vacantes llevan a esa cuenta.
- **`portal`:** esa URL, sin la ruta de una vacante (`/j/<shortcode>`).
- **Listado:** `POST https://apply.workable.com/api/v3/accounts/<cuenta>/jobs`, uno solo, con los códigos de los países de `localidades` en `location` (`[{"countryCode": "<código>"}]`). Trae 10 vacantes por página, el total en `total` y, mientras haya más, `nextPage`, que se manda como `token` para pedir la siguiente. Ese filtro también trae las remotas abiertas a cualquier país; las de fuera de la región se reparten como las demás.
- **Remoto:** `remote: [true]`, con los códigos de los países del remoto en `location` si el alcance es `"paises"`. Como ese filtro también trae las remotas abiertas a otros países, el alcance se decide por el `countryCode` de cada ubicación. Una vacante con `remote: true` cuenta como remota aunque `workplace` diga otra cosa.
- **`consulta`:** `{"ubicaciones": [{"countryCode": "<código>", "region": "<región>", "city": "<ciudad>"}], "texto": "<búsqueda>"}`, con al menos uno de los dos. Reemplaza el listado por países:
  - **`ubicaciones`:** cada una lleva uno o más de esos campos, con los valores que trae `locations` en el listado.
  - **`texto`:** la búsqueda del portal (`query`).

  El filtro por departamento de la API no acepta nombres, así que la consulta no lo usa.
- **Detalle:** `GET https://apply.workable.com/api/v2/accounts/<cuenta>/jobs/<shortcode>`.
- **Vigencia:** `state`. `published` = publicada; cualquier otro valor sale como «Revisar».
- **Comprobación de ID:** el `shortcode` del detalle es el pedido.

| Columna | Campo del listado |
| --- | --- |
| `job_id` | `shortcode` |
| `titulo` | `title`, literal |
| `url_oficial` | `https://apply.workable.com/<cuenta>/j/<shortcode>/` |
| `ubicacion_literal` | Cada elemento de `locations` como «Ciudad, Región, País», sin las partes vacías, unidos con ` \| ` |
| `modalidad_literal` | `workplace`, literal (`on_site`, `hybrid` o `remote`) |
| `fecha_publicacion` | `published`, según 07/BUS-FECHAS: a las 00:00 UTC, fecha UTC; con hora real, la fecha en la zona horaria de 04 |
| `observaciones.url_fuente` | URL del detalle consultado |

### SmartRecruiters

- **`plataforma`:** `smartrecruiters`.
- **Cómo se reconoce:** cada vacante vive en `https://jobs.smartrecruiters.com/<empresa>/<id>-<título>`, y el sitio de carreras de la empresa en `https://careers.smartrecruiters.com/<empresa>`. El botón de postulación de la página de empleo de la empresa suele llevar ahí.
- **`portal`:** `https://careers.smartrecruiters.com/<empresa>`, con el identificador de la empresa como aparece en esas URL.
- **`robots.txt`:** el de `api.smartrecruiters.com` prohíbe su API, así que no se usa, aunque el buscador de la empresa la lea. El script revisa también el de `www.smartrecruiters.com`, que prohíbe las páginas de algunas empresas (`Disallow: /<empresa>/*`): esas salen como `[FALLO]` y se busca otra ruta en el sitio oficial de la empresa.
- **Listado:** el del sitio de carreras, en HTML y por grupos: `GET https://careers.smartrecruiters.com/<empresa>/api/groups?page=<n>`. Cada grupo trae su nombre y su conteo, y muestra hasta 10 publicaciones, o 9 y su «Show more», que se recorre con `GET …/api/more?type=<tipo>&value=<valor>&page=<n>`. Los IDs únicos de los grupos que se completan deben igualar la suma de sus conteos. El sitio agrupa por ubicación o por otro campo, como el departamento, y el «Show more» de un grupo dice cuál:
  - **Por ubicación:** el lugar de cada publicación es el nombre de su grupo («Ciudad, País», «Ciudad, Estado»). Solo se completan los grupos que pueden estar en la región o que nombran uno de sus países.
  - **Por otro campo:** el lugar es el texto bajo el título de cada publicación, y se completan todos los grupos.
  - **Sin ningún «Show more»:** se prueban los dos.

  Se lee la página de cada publicación que puede estar en la región o nombra uno de sus países, y el lugar de la página decide la región. Un lugar del listado que no nombra ningún país de 04, como «Ciudad, Estado», lo decide la página de la primera publicación con ese lugar.
- **Remoto:** con el filtro `locationType=REMOTE` del sitio, que trae las remotas de todos los países; se lista antes que la región, porque el listado no dice la modalidad. Con el alcance `"paises"`, lo decide el nombre del país en el lugar de cada remota, porque el sitio no publica su código ISO: una remota de un país que 04 no nombra puede estar en el alcance y se entrega.
- **`consulta`:** `{"grupos": ["<nombre visible del grupo>"], "texto": "<búsqueda>"}`, con al menos uno de los dos. Reemplaza el listado de la región:
  - **`grupos`:** nombres de grupo del sitio de carreras (ubicaciones o departamentos), como aparecen en él. El script avisa con «revisar» si uno ya no aparece.
  - **`texto`:** la búsqueda del sitio (`search`), que es aproximada: también trae publicaciones que no corresponden.
- **Detalle desde Web:** el texto visible de la página no trae el Job ID, la fecha ni el lugar, que van en atributos y etiquetas `meta`; esos campos quedan sin leer (07/BUS-ACCESO-WEB).
- **Página de cada publicación:** `GET https://jobs.smartrecruiters.com/<empresa>/<id>`, en HTML.
- **Vigencia:** el botón de postulación (`data-sr-track="apply"`). Presente = postulación activa; si falta, sale como «Revisar».
- **Comprobación de ID:** el `link rel="canonical"` de la página termina en el ID pedido.
- **Varias publicaciones de una requisición:** una requisición puede publicarse una vez por sede, con el mismo `job_id`. El script señala con «revisar» las que entrega juntas: se registran como una sola vacante, con todas sus ubicaciones (11/REG-IDENTIDAD).

| Columna | Campo |
| --- | --- |
| `job_id` | `jobRefCode` de la página; si no viene, la referencia del listado (`aria-label="<título> - <ref>"`), salvo `undefined`. Si no hay ninguna, la vacante no tiene Job ID y su identidad es `url_oficial` (11/REG-IDENTIDAD) |
| `titulo` | Título del listado, literal |
| `url_oficial` | URL de la publicación, sin la parte `?…` |
| `ubicacion_literal` | Microdatos de la página (`addressLocality`, `addressRegion`, `addressCountry`), unidos con «, » y sin partes repetidas; si la página falla, el lugar del listado |
| `modalidad_literal` | `workplaceType` de `spl-job-location`, literal (`on_site`, `hybrid`, `remote`); si `workplaceDescription` no viene vacío, se agrega ` \| ` y su valor |
| `fecha_publicacion` | `datePosted` de la página, según 07/BUS-FECHAS |
| `observaciones.url_fuente` | URL de la publicación consultada |

### Oracle Recruiting Cloud

- **`plataforma`:** `oraclerecruitingcloud`.
- **Cómo se reconoce:** el buscador vive en `https://<host>/hcmUI/CandidateExperience/<idioma>/sites/<sitio>`, casi siempre en un host de `oraclecloud.com`. La página de empleo de la empresa enlaza ahí, o carga sus vacantes desde `/hcmRestApi/` de ese host.
- **`portal`:** esa URL, sin la ruta de una vacante (`/job/<id>`). `<sitio>` es el número del sitio, como `CX_1`.
- **Listado:** `GET https://<host>/hcmRestApi/resources/latest/recruitingCEJobRequisitions` con el finder `findReqs` (`siteNumber`, `limit=25`, `offset`, `sortBy=POSTING_DATES_DESC`), uno por cada país de `localidades`, con `location=<país>`. Trae el total en `TotalJobsCount` y también las requisiciones que tienen el país como ubicación secundaria.
  - **Nombre del país:** el primero de sus nombres en `paises` de 04 que la API reconoce, que suele ser el de su faceta de ubicaciones, en inglés. Con un nombre que no reconoce, `location` no filtra y trae todo el sitio; por eso el script solo acepta el nombre si esa faceta lo trae con el total del resultado. Si ninguno sirve, lo avisa con «revisar».
- **Remoto:** con el valor remoto de la faceta de modalidad (`selectedWorkplaceTypesFacet`, como `ORA_REMOTE`), un listado por cada país del remoto si el alcance es `"paises"`. Con ese alcance, lo deciden los códigos de país de la ubicación principal y de las secundarias (`PrimaryLocationCountry` y `CountryCode`). La faceta solo trae los valores que tiene alguna vacante: si no trae uno remoto, el script lo avisa con una línea «revisar».
- **`consulta`:** `{"facetas": {"<faceta>": ["<nombre visible>"]}, "texto": "<búsqueda>"}`, con al menos uno de los dos. Reemplaza el listado por países:
  - **`facetas`:** `LOCATIONS`, `WORKPLACE_TYPES`, `CATEGORIES`, `ORGANIZATIONS` o `TITLES`, con los nombres de sus valores en la respuesta del listado (`locationsFacet`, `categoriesFacet`…). La API solo trae los valores más frecuentes de cada faceta. El script busca sus IDs por nombre en cada ejecución y avisa con «revisar» si un nombre ya no aparece.
  - **`texto`:** la búsqueda del sitio (`keyword`).
- **Detalle desde Web:** la URL del detalle lleva `;`, `,` y comillas (`%22`), que la herramienta web debe conservar.
- **Detalle:** `GET https://<host>/hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails?expand=all&onlyData=true&finder=ById;Id="<Id>",siteNumber=<sitio>`.
- **Vigencia:** la API no trae un indicador de postulación. Sale `Confirmada abierta` por la presencia en el listado si `ExternalPostedEndDate` es nulo o futuro; con una fecha de cierre pasada, «Revisar».
- **Comprobación de ID:** el `Id` del detalle es el pedido.

| Columna | Campo |
| --- | --- |
| `job_id` | `Id` |
| `titulo` | `Title`, literal |
| `url_oficial` | `<portal>/job/<Id>` |
| `ubicacion_literal` | `PrimaryLocation` y el `Name` de cada elemento de `secondaryLocations`, unidos con ` \| ` |
| `modalidad_literal` | `WorkplaceType`, literal; si viene vacío, lo que diga la descripción; si no lo dice, `No publicado` |
| `fecha_publicacion` | `ExternalPostedStartDate` del detalle, según 07/BUS-FECHAS; si el detalle falla, `PostedDate` del listado, fecha sin hora |
| `observaciones.url_fuente` | URL del detalle consultado |

### Plataformas sin adaptador

- **Avature:** la plantilla no trae adaptador, porque cada portal define los suyos: el filtro de país es un campo propio del sitio cuyas opciones se cargan aparte, el listado no siempre muestra la ubicación ni un total exacto, y las etiquetas del detalle cambian de un sitio a otro. Para una empresa en Avature se construye el adaptador en esta copia (CAT-REGLAS).

## FICHA-PLANTILLA — Contenido de cada ficha

Cada ficha es una sección `## EMP-<ID> — <Nombre>`. Su primera línea dice `**Ficha <versión>** — comprobada el <fecha>, con una búsqueda de prueba (<únicos> de <total>).` Después van estas subsecciones, en este orden:

1. **`### Configuración`:** el bloque que lee el script, el primer bloque ```` ```json ```` de la subsección:

   ```json
   {
     "plataforma": "workday",
     "portal": "https://<empresa>.wd<N>.myworkdayjobs.com/<sitio>",
     "consulta": null
   }
   ```

   | Campo | Qué lleva |
   | --- | --- |
   | `plataforma` | El nombre de su adaptador, en minúsculas (CAT-PLATAFORMAS) |
   | `portal` | La URL del buscador de la empresa en esa plataforma, con la forma que da CAT-PLATAFORMAS |
   | `consulta` | `null`, o una consulta más estrecha que reemplaza el listado por los países de la región, con la forma de su plataforma |

   Si el bloque falta o no sirve, el script reporta la empresa como `[FALLO]` y sigue con las demás.
2. **`### Identidad`:** razón social, nombres alternativos y entidad contratante.
3. **`### Portal`:** portal oficial y plataforma de reclutamiento, con las rutas comprobadas desde el sitio de la empresa y lo que permite su `robots.txt`, con fecha. La raíz de una plataforma no siempre es el buscador público.
4. **`### Acceso`:** solo lo que esta empresa cambie respecto de CAT-PLATAFORMAS: paginación, total, filtros, comprobación de ID o indicador de vigencia. Si el portal complica leer el anuncio de una vacante con la herramienta de lectura web, una línea opcional **Detalle desde Web:** dice cómo llegar a sus campos (07/BUS-ACCESO-WEB), por ejemplo, con una API de detalle en lugar de la página pública.
5. **`### Sedes y región`:** ubicación literal y su relación con la región de 04, por separado. No trasladar equivalencias de otra empresa. Límites de cobertura observados, como remotas que el filtro no trae.
6. **`### Campos y mapeo a los registros`:** los de su plataforma (CAT-PLATAFORMAS); anotar solo lo que cambie en esta empresa y cuál es la fecha de publicación confiable.
7. **`### Vocabulario observado`:** familias de puestos y vocabulario propio, a partir de 02, 04 y 05; no inferir experiencia por la empresa.
8. **`### Fuentes y limitaciones`:** fuentes, fecha de comprobación, cobertura de la búsqueda de prueba y pendientes.

Para trabajar una ficha: leer `07_METODO_DE_BUSQUEDA.md` y 04, trabajar solo esa ficha y comprobar rutas, ubicaciones, filtros, paginación y limitaciones. No declarar vacantes abiertas sin comprobarlas una por una.
