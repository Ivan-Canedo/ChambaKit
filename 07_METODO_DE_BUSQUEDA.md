# 07 — Método de búsqueda

**Versión:** 1.8 — 2026-10-29 — BUS-ACCESO-CODE reconoce también por su `Retry-After` el bloqueo de las IP de la nube.
**Estado:** método de la plantilla. Queda listo con la región de 04 y las fichas de 06, en el paso 7 de `/configurar` (Empresas).

## BUS-ALCANCE — Responsabilidad

Descubrir vacantes en las empresas de 06, comprobar su vigencia, deduplicarlas, declarar la cobertura, comparar con búsquedas anteriores y registrar cada ejecución. La evaluación es de 08; el acceso propio de cada empresa, de su ficha en 06. Este método es común a todas las empresas.

## BUS-ACUERDOS — Decisiones del titular

Las reglas de este método valen para cualquier titular. Si el titular cambia una, el cambio se anota aquí, con ID `BUS-U##` y fecha, y se aplica en la sección que la usa. Sus condiciones y exclusiones no se anotan aquí: su autoridad es 04.

| ID | Fecha | Decisión |
| --- | --- | --- |

## BUS-REGLAS — Reglas

- Descubrir primero todo el alcance pedido y evaluar después. No excluir anuncios porque una habilidad no aparezca en el CV.
- Confirmar la vigencia en la fuente oficial. Un fragmento antiguo con «Apply Now» no confirma que siga abierta.
- Una ausencia, redirección o error no demuestra cierre. Al comparar, «no observada esta vez» no significa «cerrada».
- Un mensaje oficial explícito de cierre en la página de la vacante prevalece sobre su presencia en el listado: se registra `Cerrada`, con el mensaje literal.
- Identidad por Job ID (11/REG-IDENTIDAD); el mismo título no basta para fusionar.
- Separar fecha de publicación, primera detección y última verificación.
- **Qué se registra:** las vacantes de la región y las remotas que trae el acceso de la ficha van todas a `vacantes` y `observaciones`, también las remotas con sede fuera de la región (`region_relacionada` = `Fuera`), porque basta con guardar lo que da el listado. Requisitos y evaluación, solo de las relacionadas con alguna familia ROL (05).
- **Requisitos de una excluida:** los de una vacante relacionada se registran en `habilidades_vacante` aunque su evaluación resulte excluida por condiciones, salvo por «Tipo de puesto».
- **Tipos de puesto excluidos:** si 04/PREF-TIPOS excluye alguno, las vacantes de esos tipos no gastan trabajo: se registran en `vacantes` y `observaciones`, con su fila `Excluida` en `evaluaciones` (08, condición «Tipo de puesto»), sin extraer requisitos. Si 04 no excluye ninguno, esta regla no aplica.
- **Agregadores y buscadores:** solo si la fuente oficial no da cobertura completa (BUS-COBERTURA) o al descubrir empresas nuevas.
- **Empresas nuevas:** solo cuando se pida; buscarlas por funciones, habilidades, roles, ubicación y condiciones (02, 04 y 05), no solo por sector. Una empresa explorada entra al catálogo de 06 solo si el titular la acepta.

## BUS-CANALES — Qué se hace en cada canal

- **Code local y Code en la nube:** son el mismo canal Code, con las mismas reglas. Cambia el Entorno de la nube: cada sesión de Code en la nube trabaja sobre un clon nuevo del repositorio privado de la copia y solo llega a los hosts de la lista de dominios del entorno de la nube (06/CAT-PLATAFORMAS, «Hosts»). Lo que esa lista cambia va marcado «Code en la nube»: los fallos de la búsqueda (BUS-ACCESO-CODE), el alta de una empresa (abajo) y la comprobación puntual (BUS-PUNTUAL).
- **Búsquedas:** solo en Code, porque la terminal llega directo a los portales, con GET y POST, y `herramientas/buscar.py` da conteos, IDs y campos exactos (BUS-ACCESO-CODE). Si el titular pide una búsqueda desde Web, el agente le dice que se hace en Code.
- **Comprobaciones puntuales:** en los dos canales (BUS-PUNTUAL). Desde Web, con la herramienta de lectura web del chat (BUS-ACCESO-WEB).
- **Registros:** solo los escribe Code, con `herramientas/registros.py` (00, «Escritura de registros»). Web lee la instantánea (11/REG-INSTANTANEA) y deja en una nota para Code lo que haya que conservar (00, «Cambios a los registros»).
- **Continuidad:** lo que registra una búsqueda en Code (vacantes, observaciones, requisitos, evaluaciones y la tabla resumen en `informes`) se usa desde Web para ver la tabla, pedir el detalle de una vacante o adaptar el CV, sin repetir la búsqueda (08/EVAL-INFORME).
- **`robots.txt`:** solo se usan rutas que el sitio permite, en ambos canales. La herramienta web lo respeta por sí sola. En Code, cada adaptador lo comprueba en cada búsqueda, y la ficha anota lo que se revisó al darla de alta. Si una API lo prohíbe, se busca otra ruta del sitio oficial; no se rodea.
- **Empresa sin API:** buscar la API que usa su portal; a veces está en el dominio de la empresa y no en el de la plataforma. Si no hay, un navegador sin interfaz (Chromium headless) en Code.
- **Empresa nueva:** si su plataforma tiene adaptador, basta la ficha (06/CAT-REGLAS). Al darla de alta, el agente le da al titular, en una línea de su respuesta, el host que va en la lista de dominios del entorno de la nube (06/CAT-PLATAFORMAS, «Hosts»), para si usa Code en la nube; la copia no anota si la usa, así que la línea va siempre. En Workable, la línea dice en cambio que esa empresa se busca en Code local. Sin adaptador, la investigación de su API (arriba) pide hosts que la lista no deja pasar: se hace en Code local o, en Code en la nube, con los dominios que el titular agrega a mano en el Entorno de la nube mientras se investiga.

## BUS-ACCESO-CODE — Script de búsqueda

```text
python3 -I herramientas/buscar.py [EMP-ID ...] [--salida archivo.json] [--sin-remotas]
```

- **Empresas:** por su ID de 06; sin IDs, todas las del catálogo. `--help` lista las plataformas con adaptador.
- **Configuración:** lee la región, el alcance del remoto y la zona horaria del bloque de 04/PREF-UBICACION, y la plataforma, el portal y la consulta del bloque de cada ficha (06/FICHA-PLANTILLA). Si el bloque de 04 falta o no cumple sus reglas, o el catálogo está vacío, se detiene sin buscar (código 2) y dice qué falta. Una ficha sin configuración usable, o con una plataforma sin adaptador, sale como `[FALLO]`.
- **Qué hace:** por cada empresa, el adaptador de su plataforma (06/CAT-PLATAFORMAS):
  1. Comprueba que el `robots.txt` del portal permita las rutas que usa.
  2. Lista las vacantes de los países de `localidades`, o las de la consulta de la ficha si la trae.
  3. Lista las remotas con el filtro de remoto de la plataforma, según el alcance del remoto de 04, salvo con `--sin-remotas` o si 04 no acepta remoto.
  4. Comprueba que los IDs únicos de cada listado igualen el total que reporta, o, si la fuente no lo publica, hace la comprobación de su ficha.
  5. Lee con comprobación de ID el detalle de cada vacante que entrega, y da sus campos de `vacantes` y `observaciones` según el mapeo de su plataforma, más la descripción en texto.
- **Región:** clasifica cada ubicación literal con los grupos de 04 («Cómo se lee un grupo»). `region_relacionada` es `Dentro` si todas las ubicaciones están en la región; `Incluye` si alguna lo está; `Indeterminada` si ninguna lo está pero alguna puede estarlo, porque nombra una división de 04 sin una localidad aceptada, solo el país o nada más concreto que «Remote»; y `Fuera` en los demás casos. Una ubicación que nombra otro país de 04 no cuenta para los grupos de un país distinto, porque hay ciudades y divisiones homónimas entre países. Las que pueden estar dentro van en `ubicaciones_por_revisar` y salen como «revisar ubicación»; no se descartan.
- **Salida:**
  - `vacantes`: las de la región, también las indeterminadas.
  - `remotas_fuera_de_region`: las remotas con sede fuera de la región que trajo el filtro de remoto o que están en el alcance del remoto de 04.
  - `fuera_de_region`: solo las ubicaciones de las demás vacantes de fuera, que no se registran.
  - `consultas` y `remotas_revision`: qué se listó, con qué filtros y cuántas, para `fuentes_consultas_filtros` y `cobertura_limitaciones`.
  - `unicos` y `total_reportado`: la suma de los listados, con cada vacante contada una vez aunque la traigan dos (el de la región y el de remotas).
  - `fecha_hora`: la de inicio, en la zona horaria de 04.
- **Vigencia:** sugiere `Confirmada abierta` solo con el indicador positivo de su plataforma, o, si la plataforma no publica uno (06/CAT-PLATAFORMAS), con la presencia en el listado, como admite BUS-VIGENCIA. Cualquier otro valor sale como «Revisar» y se decide con BUS-VIGENCIA. El motivo de un indicador del detalle ya trae el prefijo «Detalle oficial: » con el que se registra.
- **Fallos:** si una API cambia de forma o no responde, o su `robots.txt` prohíbe la ruta, la empresa sale como `[FALLO]` con el motivo y la búsqueda de esa empresa queda sin hacer; no se completa a mano por otra vía sin declararlo.
- **Host fuera de la lista (Code en la nube):** si el `[FALLO]` dice que el host no está en la lista de dominios del entorno de la nube, el agente le da al titular el host con que termina el mensaje, para que lo agregue en claude.ai/code (entorno → red → Custom). Con el host agregado, se vuelve a buscar esa empresa; hasta entonces queda sin hacer, como cualquier `[FALLO]`. El mensaje de `robots.txt` que no se pudo leer es otro caso: ahí falló la petición al portal.
- **IP bloqueada (Code en la nube):** si el `[FALLO]` dice que el sitio bloquea las IP de Code en la nube y que la empresa se busca en Code local, el sitio respondió HTTP 429 con el `error code: 1015` de Cloudflare o con un `Retry-After` de más de un minuto, como hace Workable con todas sus cuentas (06/CAT-PLATAFORMAS). El script no lo reintenta, porque esperar no lo resuelve. Esa empresa queda como no revisada en la cobertura (BUS-COBERTURA) y el agente le dice al titular que la busque en Code local. En Code local, el mismo 429 se reintenta como cualquier límite pasajero, con la espera de `Retry-After`.
- **Qué no hace:** filtrar por familia ROL, evaluar ni escribir en los registros. Eso sigue en los pasos 4–9.
- **Resumen en pantalla:** una línea por empresa (`[OK]`, `[INCOMPLETA]`, `[SIN TOTAL]` o `[FALLO]`; únicos/total, en la región y remotas), una línea `cobertura:` si la fuente no publica total, y las líneas «revisar» que hay que atender antes de registrar, también las de las remotas fuera de la región. Una vacante sin Job ID publicado se nombra por su URL.

## BUS-ACCESO-WEB — Lectura de una vacante desde Web

Aplica a una comprobación puntual desde el canal Web (BUS-PUNTUAL). La terminal del chat no llega a los portales de empleo (el proxy rechaza la conexión): se lee con la herramienta de lectura web, que solo hace GET y devuelve la respuesta mediada por un modelo y con caché.

- **Solo lo nombrado:** el anuncio de cada vacante que el titular nombra o pega, nunca un listado ni páginas de resultados.
- **Comprobación de ID:** la herramienta puede devolver la respuesta de otra URL parecida del mismo sitio, guardada unos 15 minutos. **Después de cada lectura se comprueba que lo devuelto sea la vacante pedida,** por su Job ID. Si no lo es, se cambia la forma de la URL (otro dominio equivalente, `/` final o no, otro orden de parámetros) y se repite. Si sigue sin serlo, la vacante queda `No verificable`, con el motivo «devolvió otro ID».
- **Lectura mediada:** la respuesta pasa por un modelo intermedio, así que se piden los campos literales que se necesitan: Job ID, título, ubicación, modalidad, fecha de publicación, requisitos y el indicador de postulación.
- **Solo texto visible:** la herramienta convierte la página a texto y descarta los `<script>`; el JSON-LD y los datos embebidos no llegan. Si la ficha de la empresa en 06 dice cómo leer el detalle desde Web (06/FICHA-PLANTILLA, «Acceso»), se lee así. Un campo que no aparece queda sin leer; no se completa por inferencia.
- **Vigencia:** BUS-VIGENCIA, con lo que muestre el texto visible. Sin listado, la presencia en él no cuenta.
- **Sin rodeos:** no se le pide al titular que descargue páginas. Si la herramienta no puede leer el anuncio (por `robots.txt` o por la red), la vacante queda `No verificable` o la comprobación se deja para Code. Si el titular pega el texto de un anuncio que no está en el portal, se usa como aportado por él (BUS-PUNTUAL).

## BUS-PASOS — Ejecución

1. **Encargo.** Empresas y región. Por defecto, todas las de 06 con la región de 04: sus localidades, más el remoto según su alcance.
2. **Preparar.** Leer la ficha de cada empresa en 06 (acceso, ubicaciones, campos). Anotar las versiones de 02, 04, 05, 06/EMP-ID, 07 y 08.
3. **Listar.** Ejecutar `herramientas/buscar.py` con `--salida` en el directorio temporal de la sesión y atender sus líneas «revisar» y `[FALLO]` (BUS-COBERTURA) en el archivo de decisiones (BUS-REGISTRO).
4. **Registrar el listado** con `importar` (BUS-REGISTRO). La herramienta cruza cada vacante con `vacantes` (11/REG-IDENTIDAD), la registra con su observación y compara con la última búsqueda comparable. Devuelve la lista compacta de las vacantes de la búsqueda.
5. **Filtrar por familia ROL (05)** con el título y el departamento de la lista compacta. Si la relación es dudosa, se incluye. Las de un tipo de puesto que 04 excluye siguen BUS-REGLAS.
6. **Detalle de las relacionadas.** El anuncio oficial, con el ID comprobado, ya viene en la `descripcion` de la salida del script, junto al Job ID o la URL de la vacante. De ahí salen la vigencia (BUS-VIGENCIA), la ubicación y modalidad literales y los requisitos.
7. **Registradas no observadas.** Las que `comparacion_anterior` da como no observadas esta vez. Solo las que tienen fila en `evaluaciones`: leer su detalle oficial para ver si siguen abiertas. Las demás solo se mencionan en la comparación.
8. **Evaluar (08)** las relacionadas, reutilizando evaluaciones guardadas según 08/EVAL-REGISTRO.
9. **Registrar el juicio** con `agregar` y `actualizar` (BUS-REGISTRO): requisitos, evaluaciones, `informes` y las observaciones del paso 7.
10. **Entregar** la tabla resumen de 08/EVAL-INFORME, más dos líneas: cobertura y comparación.

## BUS-VIGENCIA — Evidencia mínima por estado

| Estado | Evidencia mínima | `motivo` |
| --- | --- | --- |
| Confirmada abierta | Detalle oficial con indicador de postulación activa (el de su plataforma, 06/CAT-PLATAFORMAS), **o** presencia en el listado oficial de esta búsqueda | Lo que se vio; si solo fue el listado: «En listado oficial; detalle no consultado» |
| Cerrada | Mensaje oficial explícito de cierre o indicador oficial de postulación desactivada, en la página o API de esa vacante | Texto breve literal |
| No verificable | Todo lo demás: error, redirección, ausencia del listado, ID que no coincide tras reintentar, o solo visto en agregador o buscador | Lo que pasó, p. ej. «error 404», «devolvió otro ID» |

Un agregador nunca basta para «Confirmada abierta». Una vacante vista solo en agregador se reporta aparte como no confirmada y no se registra.

## BUS-FECHAS — Publicación y antigüedad

- `fecha_publicacion` es la fecha que publica la fuente oficial, aunque sea republicación. Si la fuente también da una fecha de creación, no se usa.
- Las fechas Unix a las 00:00 UTC se registran como fecha UTC, sin pasarlas a la zona horaria de 04, porque eso podría moverlas de día.
- Las marcas de tiempo con hora real se registran con la fecha en la zona horaria de 04. Las fechas sin hora (Workday: `startDate`) se copian tal cual.
- Para una vacante ya registrada, 08/EVAL-ANTIGUEDAD toma la más antigua entre `fecha_publicacion` y `primera_deteccion`. Una republicación cuenta como nueva solo la primera vez que se detecta.

## BUS-COBERTURA — Cobertura y comparación

**Cobertura del listado:**

- Es **completa** solo si el número de Job IDs únicos iguala el total que reporta la fuente.
- Si no lo iguala, se intenta otro orden de resultados. Si sigue sin igualar, la búsqueda queda **incompleta**: se declara cuántas faltan y se usan agregadores y buscadores para buscar lo faltante.
- **Fuente sin total publicado:** la cobertura se declara «sin total publicado», con la comprobación que indique la ficha (por ejemplo, que los filtros de modalidad repartan exactamente el listado). Si la comprobación cuadra, no se buscan faltantes en agregadores. Si no cuadra, la búsqueda queda incompleta y se sigue la regla anterior.
- Lo que no se pudo revisar (detalles fallidos, modalidades no cubiertas por el acceso, posibles duplicados) va en `no_revisado_pendientes`.

**Comparación:**

- Se compara con la última búsqueda comparable: misma empresa, mismo acceso y misma región, es decir, los mismos listados con los mismos filtros, aunque cambien sus conteos. Una comprobación puntual no es comparable, porque no lista.
- Se reportan IDs nuevos, IDs ya conocidos, IDs no observados esta vez (sin declararlos cerrados) y cambios de título, ubicación o modalidad.
- La primera vez se registra «Sin búsqueda comparable».
- `importar` la calcula al registrar la búsqueda (BUS-REGISTRO).

## BUS-REGISTRO — Escritura en los registros

Con `herramientas/registros.py` (11/REG-LOCAL), en tres pasos. Las filas del listado no pasan por el agente: él solo aporta lo que pide juicio.

1. **`importar`** con la salida JSON de `buscar.py` y un archivo de decisiones, los dos en el directorio temporal de la sesión (paso 4 de BUS-PASOS):

   ```sh
   .venv/bin/python -I herramientas/registros.py importar <salida>.json <decisiones>.json
   ```

   Escribe la fila de `busquedas`, las vacantes nuevas, una observación por vacante listada y los cambios a las ya registradas. Devuelve el `busqueda_id` y una línea `VAC-ID · título · departamento` por vacante de la búsqueda, para el paso 5.
2. **`agregar`** con las filas que piden juicio, de todas las pestañas en una sola llamada: `habilidades_vacante`, `evaluaciones`, `informes` y las observaciones del paso 7, con el `busqueda_id` de esta búsqueda. Después, `actualizar` con el `ultima_observacion_id` y los campos que cambiaron en las vacantes del paso 7.
3. **`informe`** con el `busqueda_id`: da la tabla resumen, que no debe tener `#N/A` y es la que se entrega.

Si la herramienta rechaza la entrada, no escribe nada y dice todos los errores: se corrigen y se repite la llamada. `importar` rechaza también una salida que ya importó.

**Archivo de decisiones:** lo que el script no sabe.

```json
{
  "solicitud_alcance": "Todas las empresas de 06 con la región de 04",
  "recursos_versiones": "07 v1.4 | 06/EMP-<ID> v1.0 | 04 v1.1",
  "no_revisado_pendientes": "Ninguno",
  "revisar": {
    "EMP-<ID>": {
      "<Job ID>": {"region_relacionada": "Dentro", "motivo_region": "<por qué>"},
      "<URL de una sin Job ID>": {"estado_vigencia": "No verificable", "motivo": "<lo que pasó>"}
    }
  }
}
```

- **`revisar`:** una decisión por cada línea «revisar ubicación» (`region_relacionada` con `motivo_region`) y por cada «revisar vigencia» (`estado_vigencia` con `motivo`, según BUS-VIGENCIA). Cada vacante se nombra como en su línea: por su Job ID o, sin él, por su URL. Una requisición con varias publicaciones (su línea «revisar» lo dice) se registra como una sola vacante, con todas sus ubicaciones, y pide su región. Una decisión también corrige una vacante sin línea «revisar», por ejemplo con la vigencia que se vio en su detalle.
- **Líneas «revisar» de una empresa,** como un filtro que el portal no ofrece: `importar` las copia a la cobertura. Lo que dejan sin revisar va en `no_revisado_pendientes`.
- **`[FALLO]`:** cada empresa que falló se nombra, por su EMP-ID, en `no_revisado_pendientes`. Una que falló por un bloqueo de Code en la nube (BUS-ACCESO-CODE) se nombra con el motivo, por ejemplo «EMP-ID: apply.workable.com bloquea las IP de Code en la nube; buscar en Code local».
- **Sin decisión:** si queda una línea «revisar» sin decidir o un `[FALLO]` sin declarar, `importar` no escribe nada.

| Pestaña | Qué se escribe |
| --- | --- |
| `busquedas` | `importar`, una fila por ejecución. `fecha_hora`: la de inicio del script. `solicitud_alcance`, `recursos_versiones` (las versiones del paso 2) y `no_revisado_pendientes` (BUS-COBERTURA): de las decisiones. `fuentes_consultas_filtros`: la versión del script y, por empresa, el acceso, cada listado con sus filtros y conteos, y cómo se revisaron las remotas. `cobertura_limitaciones`, por empresa: «EMP-ID: N únicos de T, completa» o «incompleta»; si la fuente no publica total, «N únicos, sin total publicado; <comprobación de la ficha>»; después, «detalle leído en M de K» y sus líneas «revisar». `comparacion_anterior`: según BUS-COBERTURA, por empresa: «EMP-ID, contra BUS-…: nuevos …; ya conocidos …; no observados esta vez, sin declararlos cerrados: …; cambios: VAC-… (columnas)» |
| `vacantes` | `importar`: una fila por cada vacante listada que no exista, con los campos de la salida, la región decidida y `primera_deteccion` = fecha de la búsqueda; en las ya registradas, los campos que cambiaron y `ultima_observacion_id`. Las del paso 7, con `actualizar` |
| `observaciones` | `importar`: una fila por vacante listada, con `tipo_fuente` `Oficial`, la vigencia del script o la decidida y su URL. `fecha_verificacion` va sin hora: la del script es la de inicio, no la de cada lectura. El `motivo` agrega la región decidida con su motivo y cada cambio como «antes → ahora» (11/REG-IDENTIDAD). Las del paso 7, con `agregar`: la evidencia de su detalle y su URL |
| `habilidades_vacante` | `agregar`. Solo vacantes relacionadas con detalle leído y no excluidas por «Tipo de puesto» (BUS-REGLAS), una fila por requisito con su tipo (08/EVAL-REQUISITOS). Si el conjunto no cambió respecto de lo registrado, no se agregan filas (11/REG-IDENTIDAD) |
| `evaluaciones` | `agregar`. Una fila por evaluación nueva o rehecha (08/EVAL-REGISTRO) |
| `informes` | `agregar`. Una fila por vacante de la tabla resumen (08/EVAL-INFORME), en su orden: `busqueda_id`, `vacante_id` y la `evaluacion_id` que muestra la tabla. Las demás columnas las calcula `informe` |

Las vacantes no relacionadas quedan en `vacantes` y `observaciones`, sin requisitos ni evaluación.

**Los módulos no se editan por una búsqueda.** Resultados, cobertura, comparación, evaluaciones y la tabla resumen viven solo en los registros (00, «Registros»). Un módulo se edita solo si cambia el método, una ficha (p. ej., un `[FALLO]` porque la API cambió de forma), el perfil o las preferencias.

## BUS-PUNTUAL — Comprobación puntual

Leer el anuncio oficial de una vacante, o de unas pocas que el titular nombra, sin recorrer ningún listado. Se hace en los dos canales (BUS-CANALES) y no sigue BUS-PASOS: no hay listado, cobertura ni comparación.

- **Lectura:** en Code, la terminal pide el detalle oficial de cada vacante por la misma ruta que usa el adaptador de su plataforma (06/CAT-PLATAFORMAS), que su `robots.txt` permite, y comprueba su ID; `buscar.py` no lee una vacante suelta; en Web, según BUS-ACCESO-WEB. La vigencia sigue BUS-VIGENCIA.
- **Eightfold:** la vacante se lee por su API de detalle, no en `url_oficial` (06/CAT-PLATAFORMAS, «Eightfold»).
- **URL fuera de la lista (Code en la nube):** si la lectura falla con `getaddrinfo ENOTFOUND` en la herramienta de lectura web o con el error de túnel del proxy (`Tunnel connection failed: 403`) en Python, el host no está en la lista de dominios del entorno de la nube. El agente lo dice y ofrece dos salidas: que el titular pegue el texto del anuncio, que se usa como aportado por él, o que agregue el host en claude.ai/code (entorno → red → Custom) para volver a leerlo.
- **Desde Web:** lo que el titular quiera conservar (observación, requisitos o evaluación) queda en una nota para Code (00, «Cambios a los registros»).
- **Registro, solo en Code:** sin `importar`, que es para la salida de `buscar.py`: `agregar` con las filas nuevas y después `actualizar` con `ultima_observacion_id` y los campos que cambiaron en las vacantes ya registradas. La herramienta comprueba cada fila de la nota contra el esquema; si rechaza una, se corrige con el titular.

| Pestaña | Qué se escribe |
| --- | --- |
| `busquedas` | Una fila por comprobación. `fecha_hora`: la de la lectura. `solicitud_alcance`: «Comprobación puntual» y las vacantes pedidas. `recursos_versiones`: las de los módulos usados, que la nota de Web trae. `fuentes_consultas_filtros`: las URL leídas y cómo se leyeron; desde Web, «Herramienta de lectura web del chat». `cobertura_limitaciones`: «Comprobación puntual, sin listado» y lo que no se pudo leer. `no_revisado_pendientes`: lo que quedó sin leer, o `Ninguno`. `comparacion_anterior`: «No comparable: comprobación puntual» |
| `vacantes` | Solo si la vacante no está registrada: los campos leídos, `primera_deteccion` = fecha de la lectura. Su empresa necesita un EMP-ID en 06 (11/REG-CAMPOS) |
| `observaciones` | Una fila por vacante leída. `fecha_verificacion`: la de la lectura, con hora si se conoce. `tipo_fuente`: `Oficial` si se leyó en su anuncio oficial; `Aportada por el titular` si el titular pegó el anuncio porque no se encontró en el portal o no se pudo leer, sin `url_fuente`, con vigencia `No verificable` y el motivo «Anuncio pegado por el titular» |
| `habilidades_vacante` y `evaluaciones` | Si la vacante se evaluó, según 08/EVAL-REGISTRO |
