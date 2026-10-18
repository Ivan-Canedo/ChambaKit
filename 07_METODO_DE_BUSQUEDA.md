# 07 — Método de búsqueda

**Versión:** 1.1 — 2026-10-18 — El canal Code es cualquier agente con terminal sobre la copia; el canal Web y la hoja necesitan Claude.
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

## BUS-CANALES — Dónde se ejecuta cada búsqueda

La diferencia entre canales no es renderizar JavaScript, sino qué peticiones llegan al portal.

| | Code | Web |
| --- | --- | --- |
| Dónde | Un agente con terminal sobre esta carpeta: Claude Code, Antigravity u otro | Chat del proyecto en claude.ai, desde cualquier dispositivo; necesita Claude |
| Acceso a los portales | La terminal llega directo: peticiones GET y POST | Solo la herramienta de lectura web: GET, respuesta mediada por un modelo y con caché (BUS-ACCESO-WEB) |
| Lectura | `herramientas/buscar.py`: conteos, IDs y campos exactos (BUS-ACCESO-CODE) | Manual, página por página, con comprobación de ID |
| Registros (00, «Registros») | La hoja, con el conector de Google Sheets, solo si el agente es Claude Code; en modo local, el archivo, con `herramientas/registros.py` | La hoja, con el conector de Google Sheets; en modo local no hay canal Web |
| Empresas | Todas las del catálogo de 06 | Solo las fichas con canal «Web y Code» |

- **`robots.txt`:** solo se usan rutas que el sitio permite, en ambos canales. La herramienta web lo respeta por sí sola. En Code, cada adaptador lo comprueba en cada búsqueda, y la ficha anota lo que se revisó al darla de alta. Si una API lo prohíbe, se busca otra ruta del sitio oficial; no se rodea.
- **Canal de cada empresa:** lo declara su ficha en 06. «Solo Code» cuando el listado exige POST o navegador, o cuando el texto visible no trae los campos del mapeo (BUS-ACCESO-WEB).
- **Búsqueda completa:** se hace desde Code; desde Web se continúa con lo registrado.
- **Búsqueda desde Web:** solo cubre las empresas con canal «Web y Code». Las «Solo Code» no se buscan ni se sustituyen con agregadores: se anotan en `no_revisado_pendientes` con la fecha de su última búsqueda en Code, tomada de `busquedas`.
- **Continuidad:** lo que registra una búsqueda en Code (vacantes, observaciones, requisitos, evaluaciones y la tabla resumen en `informes`) se usa desde Web para ver la tabla, pedir el detalle de una vacante o adaptar el CV, sin repetir la búsqueda (08/EVAL-INFORME).
- **Empresa sin API:** antes de declararla «Solo Code», buscar la API que usa su portal; a veces está en el dominio de la empresa y no en el de la plataforma. Si no hay, un navegador sin interfaz (Chromium headless) en Code.

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
- **Fallos:** si una API cambia de forma o no responde, o su `robots.txt` prohíbe la ruta, la empresa sale como `[FALLO]` con el motivo y la búsqueda de esa empresa queda sin hacer; no se completa a mano con otro canal sin declararlo.
- **Qué no hace:** filtrar por familia ROL, evaluar ni escribir en los registros. Eso sigue en los pasos 4–9.
- **Resumen en pantalla:** una línea por empresa (`[OK]`, `[INCOMPLETA]`, `[SIN TOTAL]` o `[FALLO]`; únicos/total, en la región y remotas), una línea `cobertura:` si la fuente no publica total, y las líneas «revisar» que hay que atender antes de registrar, también las de las remotas fuera de la región. Una vacante sin Job ID publicado se nombra por su URL.

## BUS-ACCESO-WEB — Lectura web desde el chat

Aplica solo al canal Web:

- **Terminal:** no llega a los portales de empleo (el proxy rechaza la conexión). Toda la lectura se hace con la herramienta de lectura web (WebFetch). La terminal solo sirve para cálculos locales, como convertir fechas Unix.
- **Reutilización de respuestas:** la herramienta puede devolver la respuesta de otra URL parecida del mismo sitio, guardada unos 15 minutos. Por eso:
  - Cada consulta usa una forma de URL distinta: otro dominio equivalente, `/` final o no, otro orden de parámetros. Las formas de cada empresa están en su ficha.
  - **Después de cada lectura se comprueba que lo devuelto corresponda a lo pedido** (ID, página o filtro). Si no corresponde, se cambia la forma y se repite. Si sigue sin corresponder, ese dato queda como no revisado.
- **Lectura mediada:** la respuesta pasa por un modelo intermedio. Se piden los campos literales que se necesitan y se validan conteos e IDs.
- **Solo texto visible:** la herramienta convierte la página a texto y descarta los `<script>`; el JSON-LD y los datos embebidos no llegan. En Web, cada ficha indica qué se lee del texto visible.
- **Sin terminal ni rodeos:** si la herramienta no puede leer algo (por `robots.txt` o por la red), el dato queda como no revisado o se deja para Code. La búsqueda no depende de pasos manuales del titular: no se le pide que pegue URL ni que descargue páginas.

## BUS-PASOS — Ejecución

1. **Encargo.** Empresas y región. Por defecto, todas las de 06 con la región de 04: sus localidades, más el remoto según su alcance. Desde Web, solo las de canal «Web y Code» (BUS-CANALES).
2. **Preparar.** Leer la ficha de cada empresa en 06 (acceso, ubicaciones, campos) y, de los registros, las pestañas `vacantes`, `evaluaciones` y `busquedas`. Anotar las versiones de 02, 04, 05, 06/EMP-ID, 07 y 08.
3. **Listar.** En Code, ejecutar `herramientas/buscar.py` y atender sus líneas «revisar» y `[FALLO]`. En Web, recorrer todas las páginas del acceso de la ficha. En ambos, BUS-COBERTURA.
4. **Identificar.** Cruzar cada Job ID con `vacantes` (11/REG-IDENTIDAD): nueva, ya registrada o registrada y no observada esta vez.
5. **Filtrar por familia ROL (05)** con título y departamento. Si la relación es dudosa, se incluye. Las de un tipo de puesto que 04 excluye siguen BUS-REGLAS.
6. **Detalle de las relacionadas.** Leer el anuncio oficial y comprobar el ID; en Code ya viene en la salida del script. De ahí salen la vigencia (BUS-VIGENCIA), la ubicación y modalidad literales y los requisitos.
7. **Registradas no observadas.** Solo las que tienen fila en `evaluaciones`: leer su detalle oficial para ver si siguen abiertas. Las demás solo se mencionan en la comparación.
8. **Evaluar (08)** las relacionadas, reutilizando evaluaciones guardadas según 08/EVAL-REGISTRO.
9. **Registrar** (BUS-REGISTRO).
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

- Se compara con la última búsqueda comparable: misma empresa, mismo acceso y misma región. El mismo acceso leído desde otro canal es comparable (la misma API desde Code o Web).
- Se reportan IDs nuevos, IDs ya conocidos, IDs no observados esta vez (sin declararlos cerrados) y cambios de título, ubicación o modalidad.
- La primera vez se registra «Sin búsqueda comparable».

## BUS-REGISTRO — Escritura en los registros

**En la hoja,** se escribe con el conector de Google Sheets, leyendo cada pestaña antes y después (00 y 11). Orden: `busquedas` → `vacantes` → `observaciones` → actualización de `vacantes` → `habilidades_vacante` → `evaluaciones` → `informes`. Cada pestaña se escribe en un solo bloque. Si el bloque es demasiado grande para una llamada del conector, se escribe en tramos consecutivos del mismo rango, sin escribir otra pestaña entre ellos, y después se lee el bloque completo para compararlo. Si la pestaña no tiene filas suficientes, se insertan antes dentro del rango validado (11/REG-VALIDACION). Si el conector falla, las filas se entregan separadas por tabulador, después de la tabla resumen.

**En modo local,** con `herramientas/registros.py` (11/REG-LOCAL), en dos llamadas: `agregar` con todas las filas nuevas de la búsqueda, de todas las pestañas, y después `actualizar` con los cambios a las vacantes ya registradas. Si la herramienta rechaza una fila, no escribe ninguna: se corrigen las filas y se repite la llamada. Al final, `informe` con el `busqueda_id` da la tabla resumen, que no debe tener `#N/A` y es la que se entrega.

| Pestaña | Qué se escribe |
| --- | --- |
| `busquedas` | Una fila por ejecución. `fecha_hora` con la hora si se conoce. `recursos_versiones`: versiones del paso 2. `fuentes_consultas_filtros`: las URL o formas usadas, con orden y filtros. `cobertura_limitaciones`: «N únicos de T, completa/incompleta; detalle M de K relacionadas»; si la fuente no publica total, «N únicos, sin total publicado; <comprobación>; detalle M de K». `no_revisado_pendientes` y `comparacion_anterior` según BUS-COBERTURA; desde Web, las empresas «Solo Code» van en `no_revisado_pendientes`. `canal`: `Code` o `Web`. En Code, `fuentes_consultas_filtros` empieza con la versión del script |
| `vacantes` | Una fila por cada vacante listada que no exista: campos según el mapeo de la ficha (06), `primera_deteccion` = fecha de la búsqueda. En las ya registradas, actualizar los campos que cambiaron y `ultima_observacion_id` |
| `observaciones` | Una fila por vacante listada y por cada registrada no observada que se comprobó (paso 7). Si se leyó el detalle, la observación usa esa evidencia y su URL; si no, la del listado. `tipo_fuente`: `Oficial`. En Code, `fecha_verificacion` va sin hora: la del script es la de inicio, no la de cada lectura |
| `habilidades_vacante` | Solo vacantes relacionadas con detalle leído y no excluidas por «Tipo de puesto» (BUS-REGLAS), una fila por requisito con su tipo (08/EVAL-REQUISITOS). Si el conjunto no cambió respecto de lo registrado, no se agregan filas (11/REG-IDENTIDAD) |
| `evaluaciones` | Una fila por evaluación nueva o rehecha (08/EVAL-REGISTRO) |
| `informes` | Una fila por vacante de la tabla resumen (08/EVAL-INFORME), en su orden: `busqueda_id`, `vacante_id` y la `evaluacion_id` que muestra la tabla. Solo esas tres columnas (A:C); las demás se calculan. Se lee el bloque después para comprobar que no hay `#N/A` y que coincide con la tabla que se entrega |

Las vacantes no relacionadas quedan en `vacantes` y `observaciones`, sin requisitos ni evaluación.

**Los módulos no se editan por una búsqueda.** Resultados, cobertura, comparación, evaluaciones y la tabla resumen viven solo en los registros (00, «Registros»). Un módulo se edita solo si cambia el método, una ficha (p. ej., un `[FALLO]` porque la API cambió de forma), el perfil o las preferencias.
