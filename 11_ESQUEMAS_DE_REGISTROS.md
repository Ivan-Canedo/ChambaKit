# 11 — Esquema de registros

**Versión:** 1.0 — 2026-10-17 — Plantilla inicial.
**Estado:** esquema de la plantilla. El paso 8 de `/configurar` (Registros) crea la hoja o el archivo local desde el bloque de REG-ESQUEMA.

## Responsabilidad

Definir campos, relaciones, autoridades y versionado de los datos de búsquedas, vacantes, observaciones, habilidades, evaluaciones, informes y documentos, y cómo se crean y comprueban la hoja o el archivo local que los guardan.

## REG-HOJA — Dónde viven los registros

**En uno de dos lugares, con el mismo esquema (REG-ESQUEMA):**

- **Hoja de Google `ChambaKit_Registros`**, con una pestaña por tabla. La crea el paso 8 de `/configurar` desde REG-ESQUEMA, según REG-VALIDACION. Sirve a los canales Code y Web.
- **Modo local:** el archivo `ChambaKit_Registros.xlsx` de la copia, cuando el titular no conecta Google (REG-LOCAL). Solo sirve al canal Code.

**Cuál usa la copia:** lo dice 00 («Registros»): una URL es la hoja; `modo local`, el archivo; «pendiente», todavía no hay registros. Claude lee y escribe solo en ese lugar.

**Cambio de lugar:** del modo local a la hoja, nunca al revés. Lo hace `/configurar` (paso 8, «De modo local a la hoja») cuando el titular conecta Google: copia las filas a una hoja nueva, compara los conteos de cada pestaña y, si coinciden, retira el archivo, cuya historia queda en git.

**En la hoja:**

- **Lectura:** en el proyecto web, la hoja está vinculada al conocimiento del proyecto desde Drive. Claude la recibe como CSV con todas las pestañas y Drive la refresca periódicamente al abrir el proyecto. Dentro de un chat, y siempre en Code, el estado actual se lee con el conector.
- **Escritura:** Claude escribe con el conector de Google Sheets, por rango, en las filas que siguen a la última ocupada; el conector, al agregar (`append`), inserta una fila nueva en lugar de ocupar una vacía. Si el conector no está disponible o falla, Claude entrega las filas listas para pegar, separadas por tabulador y con el orden de columnas de la pestaña, e indica a qué pestaña van.
- **La validación no detiene al conector:** escribe sin error un valor inválido, que la hoja solo marca. Por eso Claude comprueba cada valor contra este esquema antes de escribir y lee la pestaña después.
- **Valores que la hoja interpretaría:** el conector escribe como si se tecleara, aun en celdas con formato de texto: un valor que empieza con `=` o `+` se vuelve fórmula, y un apóstrofo inicial desaparece. Esos valores se escriben con un `'` delante, que la hoja no guarda.
- **Historial:** el historial de versiones de Google Sheets reemplaza al control de cambios manual.

## REG-CONVENCIONES — Reglas comunes

**Tipos:**

- **ID:** prefijo y número consecutivo (tabla de abajo).
- **Texto.** Cuando la columna dice «literal», se copia tal cual de la fuente, sin traducir ni normalizar.
- **Fecha:** texto ISO `AAAA-MM-DD`; donde se indica, se admite la hora: `AAAA-MM-DD HH:MM`. Se guarda como texto porque un valor de fecha no puede tener hora opcional: mostraría un 00:00 falso o escondería una hora real. Además, el CSV del conocimiento recibe exactamente lo escrito. Se ordena bien alfabéticamente y la validación comprueba que sea una fecha real.
- **URL.**
- **Lista cerrada:** desplegable que rechaza cualquier otro valor.
- **Multivalor:** elementos separados por ` | `. Se usa la barra porque las ubicaciones ya llevan comas.

**Obligatoriedad:** **Sí** (siempre), **Si existe** (cuando la fuente lo ofrece o el caso lo tiene) y **No** (opcional).

**IDs:**

| Pestaña | Formato |
| --- | --- |
| `vacantes` | `VAC-0001` |
| `observaciones` | `OBS-0001` |
| `habilidades_vacante` | `HV-00001` (no `HAB-`, que usa 05) |
| `documentos` | `DOC-0001` |
| `busquedas` | `BUS-0001` |
| `evaluaciones` | `EVA-0001` (las secciones de 08 usan `EVAL-`) |

- Antes de escribir, leer la pestaña y tomar el número siguiente al mayor. Los IDs no se reutilizan ni se renumeran.
- Los datos sintéticos llevan `PRUEBA-` delante (p. ej. `PRUEBA-VAC-0001`) y se borran al terminar.

**Fechas y zona horaria:** en la zona horaria de 04 (`zona_horaria` del bloque de PREF-UBICACION), que también es la de la hoja. La hora solo se registra si se conoce: en claude.ai no hay garantía de conocerla y no se infiere. Las comprobaciones del mismo día se ordenan por ID.

**Nulos:** una celda vacía significa «no registrado». Hay dos valores explícitos:

- `No publicado`: se comprobó que la fuente no da el dato. Solo en `job_id`, `ubicacion_literal` y `modalidad_literal`.
- `Ninguno`: no hay nada que reportar. Solo en `busquedas` y en `evaluaciones.condiciones_detalle`.

**Formato de texto:** todas las celdas de datos usan el formato de texto de Sheets, y en el archivo local se escriben como texto. Así `1.10` no se convierte en 1.1, un Job ID numérico no pierde ceros y las fechas no cambian de forma. Ninguna columna lleva números ni fórmulas, salvo las calculadas de `informes`, que es una vista y no guarda datos propios.

**Ubicaciones múltiples:** una fila por requisición, no por sede. `ubicacion_literal` las anota en el orden de la fuente y `region_relacionada` resume el conjunto.

## REG-CAMPOS — Pestañas y columnas

| Pestaña | Unidad | Columnas |
| --- | --- | --- |
| `vacantes` | Una requisición identificada | vacante_id, empresa_id, job_id, titulo, url_oficial, ubicacion_literal, modalidad_literal, region_relacionada, fecha_publicacion, primera_deteccion, ultima_observacion_id, duplicado_de |
| `observaciones` | Comprobación fechada de una vacante | observacion_id, vacante_id, busqueda_id, fecha_verificacion, estado_vigencia, motivo, url_fuente, tipo_fuente |
| `habilidades_vacante` | Habilidad o requisito en una descripción observada | habilidad_observacion_id, vacante_id, observacion_id, habilidad_literal, habilidad_normalizada, tipo_requisito |
| `documentos` | Un archivo generado | documento_id, vacante_id, fecha_generacion, version_perfil, version_cv_base, idioma, formato, archivo, revision_visual, texto_extraible, notas |
| `busquedas` | Ejecución de una búsqueda o comprobación | busqueda_id, fecha_hora, solicitud_alcance, recursos_versiones, fuentes_consultas_filtros, cobertura_limitaciones, no_revisado_pendientes, comparacion_anterior, canal |
| `evaluaciones` | Evaluación de una vacante con una descripción observada | evaluacion_id, vacante_id, observacion_id, fecha_evaluacion, version_perfil, version_evaluacion, condiciones, condiciones_detalle, encaje, cobertura, nucleos |
| `informes` | Vacante evaluada en la tabla resumen de una búsqueda | busqueda_id, vacante_id, evaluacion_id, empresa, vacante, encaje, antiguedad, alertas, url_oficial |

Las tablas de cada pestaña explican sus columnas; el bloque de REG-ESQUEMA las da en la forma que lee una herramienta.

### `vacantes`

| Columna | Tipo | Oblig. | Valores y reglas |
| --- | --- | --- | --- |
| vacante_id | ID | Sí | `VAC-0001`, único |
| empresa_id | Lista cerrada | Sí | IDs del catálogo de 06 (CAT-EMPRESAS). Se amplía cuando 06 agregue uno |
| job_id | Texto | Si existe | Literal, sin normalizar; `No publicado` si la fuente no lo muestra |
| titulo | Texto | Sí | Literal, en el idioma del anuncio |
| url_oficial | URL | Si existe | Solo del sitio de la empresa; las URL de agregadores van en `observaciones` |
| ubicacion_literal | Multivalor | Si existe | Literal; `No publicado` si la fuente no la muestra |
| modalidad_literal | Texto | Si existe | Literal («Hybrid», «Remote»); `No publicado` si no aparece. No confirma que se pueda trabajar desde la residencia del titular: eso se evalúa en 08 |
| region_relacionada | Lista cerrada | Sí | `Dentro` / `Incluye` / `Fuera` / `Indeterminada`, respecto de la región de 04 (`localidades` de PREF-UBICACION) |
| fecha_publicacion | Fecha | Si existe | Solo una fecha absoluta mostrada por la fuente; «hace 3 días» no la llena |
| primera_deteccion | Fecha | Sí | Fecha de su primera observación; no cambia |
| ultima_observacion_id | ID | Sí | `OBS-` de esta vacante; se actualiza en la misma operación que agrega la observación. Vacía en una fila absorbida |
| duplicado_de | ID | No | `VAC-` de la fila canónica cuando esta fila resultó duplicada (REG-IDENTIDAD) |

**`region_relacionada`** (07/BUS-ACCESO-CODE, «Región»):

- **Dentro:** todas las ubicaciones literales están en la región.
- **Incluye:** hay varias y al menos una está dentro.
- **Fuera:** ninguna está dentro ni puede estarlo.
- **Indeterminada:** ninguna está dentro, pero alguna puede estarlo, porque nombra una división de 04 sin una localidad aceptada, solo el país o nada más concreto que «Remote» o «Multiple locations»; o la ubicación no está publicada.

**Empresa:** para registrar una vacante, su empresa necesita un EMP-ID en 06, aunque solo esté como «explorada». Al agregar un ID en 06, se agrega también a la lista de `empresa_id` en la hoja (REG-VALIDACION); en modo local no hace falta, porque la herramienta lee el catálogo de 06.

### `observaciones`

| Columna | Tipo | Oblig. | Valores y reglas |
| --- | --- | --- | --- |
| observacion_id | ID | Sí | `OBS-0001` |
| vacante_id | ID | Sí | Debe existir en `vacantes` |
| busqueda_id | ID | Sí | Debe existir en `busquedas`. Una comprobación puntual también abre su fila en `busquedas` |
| fecha_verificacion | Fecha | Sí | Hora opcional, solo si se conoce |
| estado_vigencia | Lista cerrada | Sí | `Confirmada abierta` / `No verificable` / `Cerrada` |
| motivo | Texto | Sí | Lo que se vio: botón de postular activo, mensaje de cierre, error 404… Si la fuente muestra un texto breve pertinente, se cita literal, p. ej. «This job is no longer accepting applications» |
| url_fuente | URL | Si existe | URL exacta que se consultó |
| tipo_fuente | Lista cerrada | Sí | `Oficial` / `Agregador` / `Buscador` / `Aportada por el titular` |

La observación es la evidencia fechada (REG-DECISIONES). La evidencia mínima de cada estado se define en 07.

### `habilidades_vacante`

| Columna | Tipo | Oblig. | Valores y reglas |
| --- | --- | --- | --- |
| habilidad_observacion_id | ID | Sí | `HV-00001` |
| vacante_id | ID | Sí | El mismo de su observación; permite contar por requisición y no por comprobación |
| observacion_id | ID | Sí | La observación cuya descripción se analizó |
| habilidad_literal | Texto | Sí | Frase literal, en el idioma original |
| habilidad_normalizada | Texto | No | Término canónico (Python, SQL, Excel); vacío si normalizar exige interpretar. El vocabulario controlado se define en 10 |
| tipo_requisito | Lista cerrada | Sí | `Obligatorio` / `Deseable` / `En funciones` / `Ambiguo` |

- **Una fila por habilidad.** En «Python or R» van dos filas con la misma frase literal, y así se conserva la alternativa.
- **`tipo_requisito`:**
  - `Obligatorio`: requisitos mínimos (required, must).
  - `Deseable`: preferred, nice to have, plus.
  - `En funciones`: aparece en las responsabilidades, no en los requisitos.
  - `Ambiguo`: la redacción no permite clasificarla.
  - Las reglas detalladas de clasificación (secciones, matices, alternativas y títulos neutros) están en 08/EVAL-REQUISITOS.
- **Sin HAB-##:** la relación con la evidencia personal se hace en la evaluación (08). Así la demanda observada queda separada de lo que posee el titular (10).

### `documentos`

| Columna | Tipo | Oblig. | Valores y reglas |
| --- | --- | --- | --- |
| documento_id | ID | Sí | `DOC-0001`; un archivo por fila, así que cada idioma y cada formato ocupan su propia fila |
| vacante_id | ID | Si existe | Vacío para un documento general |
| fecha_generacion | Fecha | Sí | |
| version_perfil | Texto | Sí | Versión de 02, p. ej. `1.2` |
| version_cv_base | Texto | Sí | Versión de 03, p. ej. `1.0` |
| idioma | Lista cerrada | Sí | `ES` / `EN` |
| formato | Lista cerrada | Sí | `PDF` / `DOCX` / `ODT` / `TXT` / `MD` / `Formulario`; se amplía si 09 usa otro |
| archivo | Texto | Sí | Nombre exacto del archivo entregado |
| revision_visual | Lista cerrada | Sí | `Satisfactoria` / `Con fallas` / `No realizada` / `No aplica` (09/CV-CONTROLES) |
| texto_extraible | Lista cerrada | Sí | Los mismos valores |
| notas | Texto | No | Si es borrador o está listo para envío, versión de 09, limitaciones |

### `evaluaciones`

| Columna | Tipo | Oblig. | Valores y reglas |
| --- | --- | --- | --- |
| evaluacion_id | ID | Sí | `EVA-0001`, único |
| vacante_id | ID | Sí | Debe existir en `vacantes` |
| observacion_id | ID | Sí | La observación cuya descripción se evaluó; debe ser de esa vacante |
| fecha_evaluacion | Fecha | Sí | Sin hora |
| version_perfil | Texto | Sí | Versión de 02, p. ej. `1.2` |
| version_evaluacion | Texto | Sí | Versión de 08, p. ej. `1.0` |
| condiciones | Lista cerrada | Sí | `Sin exclusiones` / `Excluida` (08/EVAL-CONDICIONES) |
| condiciones_detalle | Multivalor | Sí | Si está excluida: la condición y el texto literal, p. ej. `Duración: «6-month contract»`. Si no: los pendientes (`Sueldo \| Duración \| Relación \| Horario`) o `Ninguno` |
| encaje | Lista cerrada | Si existe | `★★★★★` / `★★★★☆` / `★★★☆☆` / `★★☆☆☆` / `★☆☆☆☆` / `☆☆☆☆☆` (08/EVAL-ENCAJE); vacía si está excluida |
| cobertura | Texto | Si existe | `X/Y` o `X/Y, N solo académico(s)`; vacía si está excluida |
| nucleos | Multivalor | Si existe | `Núcleo: Categoría`, p. ej. `Análisis de datos: Directa \| Gestión de proyectos: Transferible`; vacía si está excluida |

- **Una fila por evaluación**, incluidas las excluidas. Las vacantes no evaluadas por no tener relación con las familias de 05 no tienen fila.
- **Reutilización, aclaraciones y núcleos:** ver 08/EVAL-REGISTRO.
- **Orden:** las estrellas se guardan tal cual. En orden A→Z, ★ va antes que ☆, así que las de más estrellas quedan arriba.
- **Qué no se guarda:** las categorías por requisito, la familia ROL y la antigüedad, que se calcula con `vacantes` (08/EVAL-ANTIGUEDAD).

### `busquedas`

| Columna | Tipo | Oblig. | Valores y reglas |
| --- | --- | --- | --- |
| busqueda_id | ID | Sí | `BUS-0001` |
| fecha_hora | Fecha | Sí | Hora opcional, solo si se conoce |
| solicitud_alcance | Texto | Sí | Encargo, empresas y región |
| recursos_versiones | Multivalor | Sí | P. ej. `07 v1.0 \| 06/EMP-<ID> v1.0 \| 04 v1.1` |
| fuentes_consultas_filtros | Multivalor | Sí | Sitio, consulta y filtros |
| cobertura_limitaciones | Texto | Sí | Páginas revisadas, totales mostrados y límites |
| no_revisado_pendientes | Texto | Sí | `Ninguno` si no queda nada |
| comparacion_anterior | Texto | Sí | `Sin búsqueda comparable` la primera vez. «No observada esta vez» no significa «cerrada» |
| canal | Lista cerrada | Sí | `Code` / `Web`: dónde se ejecutó (07/BUS-CANALES). Permite encontrar la última búsqueda en Code de una empresa «Solo Code» |

### `informes`

La tabla resumen de cada búsqueda (08/EVAL-INFORME), para consultarla desde cualquier dispositivo sin rehacerla. Claude escribe solo los IDs; las demás columnas se calculan desde `vacantes` y `evaluaciones`, en la hoja con fórmulas y en modo local con la herramienta (REG-LOCAL), que sigue su misma lógica.

| Columna | Tipo | Oblig. | Valores y reglas |
| --- | --- | --- | --- |
| busqueda_id | ID | Sí | Debe existir en `busquedas` |
| vacante_id | ID | Sí | Debe existir en `vacantes`; una sola vez por búsqueda |
| evaluacion_id | ID | Sí | La evaluación que muestra la tabla; debe ser de esa vacante |
| empresa | Calculada | — | `empresa_id` sin el prefijo `EMP-` |
| vacante | Calculada | — | `Job ID — título`, con liga a `url_oficial`; `sin Job ID` si es `No publicado` o falta |
| encaje | Calculada | — | `encaje · cobertura`; `—` si está excluida |
| antiguedad | Calculada | — | 08/EVAL-ANTIGUEDAD con la fecha de hoy: `N d` desde la más antigua entre `fecha_publicacion` y `primera_deteccion`; `≥ N d` si solo hay `primera_deteccion`; `—` si no tiene fecha y se detectó hoy; `· antigua` desde el umbral de 08/EVAL-ACUERDOS (20 días por defecto) |
| alertas | Calculada | — | Si está excluida: `Excluida: …` con `condiciones_detalle` separado por `;`. Si no, unidos con ` · `: `Insuficiente: …` y `Académica: …` con los núcleos de esa categoría en `nucleos`, separados por `;`, y `Pendiente: …` con los pendientes de `condiciones_detalle` que no sean Sueldo, Duración, Relación ni Horario, en minúsculas. `—` si no hay nada (08/EVAL-INFORME) |
| url_oficial | Calculada | — | La de `vacantes`. Se repite porque el conector solo devuelve el texto de la columna `vacante`, no su liga |

- **Una fila por vacante evaluada de la tabla,** incluidas las excluidas, en el orden de la tabla. No tiene ID propio: cada fila es la pareja `busqueda_id` + `vacante_id`. Las vacantes no evaluadas no tienen fila, y la línea «N sin relación…» no se guarda.
- **Columnas calculadas en la hoja:** cada una es una sola fórmula en su encabezado (fila 1), la de su `formula` en REG-ESQUEMA. Devuelve el encabezado y el valor de todas las filas (`MAP` con búsqueda por ID), con rangos abiertos que incluyen las filas nuevas. En D:I no se escribe: están protegidas con advertencia. Un ID inexistente muestra `#N/A`.
- **Umbral de «antigua»:** el 20 de la fórmula de `antiguedad` es el valor por defecto de 08/EVAL-ACUERDOS. Si el titular lo cambia, se cambia en la fórmula del bloque y en la celda G1 de la hoja. La herramienta del modo local lo lee de la fórmula del bloque.
- **Al editar una fórmula:** dentro de `MAP`, `REGEXREPLACE` sobre una lista devuelve solo el primer elemento; por eso `alertas` une primero con `TEXTJOIN` y quita la categoría con `SUBSTITUTE`. La herramienta del modo local repite la lógica de cada fórmula (REG-LOCAL), así que un cambio de fórmula se hace también en `herramientas/registros.py` y en su prueba.
- **Vista, no autoridad:** si una aclaración actualiza la fila de `evaluaciones` (08/EVAL-REGISTRO), la tabla lo refleja. Cuando una búsqueda posterior hace una evaluación nueva, esta aparece en las filas de esa búsqueda, y las filas anteriores siguen mostrando la evaluación que se entregó en su momento.
- **Antigüedad:** cambia cada día, con la fecha de hoy en la zona horaria de 04, que es la de la hoja. Las fechas relativas («hace 3 días») no se guardan, así que aquí no aparecen.

### Relaciones

- `vacantes.empresa_id` → catálogo de 06.
- `vacantes.ultima_observacion_id` → `observaciones`.
- `observaciones.vacante_id` → `vacantes`; `observaciones.busqueda_id` → `busquedas`.
- `habilidades_vacante.observacion_id` → `observaciones`; su `vacante_id` coincide con el de la observación.
- `documentos.vacante_id` → `vacantes`, cuando aplica.
- `evaluaciones.vacante_id` → `vacantes`; `evaluaciones.observacion_id` → `observaciones`, de la misma vacante.
- `informes.busqueda_id` → `busquedas`; `informes.vacante_id` → `vacantes`; `informes.evaluacion_id` → `evaluaciones`, de la misma vacante.
- `vacantes.duplicado_de` → `vacantes`.
- **Identidad de una vacante:** ver REG-IDENTIDAD.

## REG-IDENTIDAD — Una fila por requisición

**Con Job ID:** la identidad es `empresa_id` + `job_id`, siempre. Antes de crear una fila, buscar esa pareja en `vacantes`.

- Si la misma requisición aparece en varias URL (portal, plataforma de reclutamiento, agregador), es una sola vacante con varias observaciones.
- Si el título es igual pero el Job ID es distinto, son vacantes separadas.
- Los Job IDs se comparan literalmente. Si solo difiere el formato (`R12345` frente a `R-12345`), es un posible duplicado y no se fusiona automáticamente.

**Sin Job ID:** la identidad provisional es `empresa_id` + `url_oficial`.

- Si la URL oficial es la misma, es la misma vacante.
- Si coinciden título y ubicación pero la URL es otra, es un posible duplicado. Las filas siguen separadas hasta tener prueba: que aparezca el Job ID o que la fuente oficial redirija de una a otra.
- Si después aparece el Job ID, se llena en la misma fila.

**Posibles duplicados sin prueba:** se anotan en `no_revisado_pendientes` de la búsqueda que los detectó.

**Fusión de duplicados confirmados:**

1. La fila con el ID más antiguo queda como canónica.
2. Las observaciones, habilidades, evaluaciones y documentos de la otra pasan al `vacante_id` de la canónica.
3. En la canónica, `primera_deteccion` toma la fecha más antigua y `ultima_observacion_id` se recalcula.
4. La fila absorbida no se borra, para que su ID no se reutilice: `duplicado_de` lleva el ID de la canónica y `ultima_observacion_id` queda vacía.
5. El motivo de la fusión se anota en `comparacion_anterior` de la búsqueda que la detectó.

Los análisis ignoran las filas con `duplicado_de`.

**Fuentes que cambian:**

- `vacantes` conserva los últimos valores observados de `titulo`, `url_oficial`, `ubicacion_literal` y `modalidad_literal`. Si una observación ve un cambio, su `motivo` lo anota como «antes → ahora».
- `job_id` no cambia, salvo que pase de `No publicado` a un valor.
- Las habilidades se registran en el primer análisis de la descripción. Al volver a analizarla, se comparan las extraídas con las ya registradas de esa vacante: si difieren, se registra el conjunto nuevo con la observación actual; si no, no se duplican filas. El conjunto vigente de habilidades de una vacante es el de su última observación analizada.

**Versiones:** no se borran filas, salvo los datos sintéticos. El historial de Sheets, o git en modo local, cubre las ediciones.

## REG-ESQUEMA — Bloque del esquema

El esquema completo en la forma que lee una herramienta: pestañas, columnas, listas cerradas, validaciones y fórmulas de `informes`. Es el primer bloque ```` ```json ```` de esta sección, y de él salen la hoja (REG-VALIDACION) y el archivo local (REG-LOCAL). Dice lo mismo que las tablas de REG-CAMPOS: al cambiar una columna se cambian los dos, según REG-DECISIONES («Encabezados»).

```json
{
  "hoja": {"nombre": "ChambaKit_Registros", "configuracion_regional": "en_US", "filas": 1000},
  "pestanas": [
    {
      "nombre": "vacantes",
      "columnas": [
        {"nombre": "vacante_id", "tipo": "id", "patron": "VAC-\\d{4,}", "oblig": "si"},
        {"nombre": "empresa_id", "tipo": "lista", "valores_de": "06/CAT-EMPRESAS", "oblig": "si"},
        {"nombre": "job_id", "tipo": "texto", "oblig": "si_existe"},
        {"nombre": "titulo", "tipo": "texto", "oblig": "si"},
        {"nombre": "url_oficial", "tipo": "url", "oblig": "si_existe"},
        {"nombre": "ubicacion_literal", "tipo": "multivalor", "oblig": "si_existe"},
        {"nombre": "modalidad_literal", "tipo": "texto", "oblig": "si_existe"},
        {"nombre": "region_relacionada", "tipo": "lista", "valores": ["Dentro", "Incluye", "Fuera", "Indeterminada"], "oblig": "si"},
        {"nombre": "fecha_publicacion", "tipo": "fecha", "oblig": "si_existe"},
        {"nombre": "primera_deteccion", "tipo": "fecha", "oblig": "si"},
        {"nombre": "ultima_observacion_id", "tipo": "ref", "patron": "OBS-\\d{4,}", "en": "observaciones", "misma_vacante": true, "oblig": "si", "vacia_con": "duplicado_de"},
        {"nombre": "duplicado_de", "tipo": "ref", "patron": "VAC-\\d{4,}", "en": "vacantes", "distinta_de": "vacante_id", "oblig": "no"}
      ],
      "prueba": {"vacante_id": "PRUEBA-VAC-0001", "empresa_id": "EMP-PRUEBA", "job_id": "000123", "titulo": "Puesto de prueba", "url_oficial": "https://example.com/empleo/000123", "ubicacion_literal": "Ciudad de prueba", "modalidad_literal": "No publicado", "region_relacionada": "Indeterminada", "fecha_publicacion": "2026-01-05", "primera_deteccion": "2026-01-10", "ultima_observacion_id": "PRUEBA-OBS-0001"}
    },
    {
      "nombre": "observaciones",
      "columnas": [
        {"nombre": "observacion_id", "tipo": "id", "patron": "OBS-\\d{4,}", "oblig": "si"},
        {"nombre": "vacante_id", "tipo": "ref", "patron": "VAC-\\d{4,}", "en": "vacantes", "oblig": "si"},
        {"nombre": "busqueda_id", "tipo": "ref", "patron": "BUS-\\d{4,}", "en": "busquedas", "oblig": "si"},
        {"nombre": "fecha_verificacion", "tipo": "fecha", "hora": true, "oblig": "si"},
        {"nombre": "estado_vigencia", "tipo": "lista", "valores": ["Confirmada abierta", "No verificable", "Cerrada"], "oblig": "si"},
        {"nombre": "motivo", "tipo": "texto", "oblig": "si"},
        {"nombre": "url_fuente", "tipo": "url", "oblig": "si_existe"},
        {"nombre": "tipo_fuente", "tipo": "lista", "valores": ["Oficial", "Agregador", "Buscador", "Aportada por el titular"], "oblig": "si"}
      ],
      "prueba": {"observacion_id": "PRUEBA-OBS-0001", "vacante_id": "PRUEBA-VAC-0001", "busqueda_id": "PRUEBA-BUS-0001", "fecha_verificacion": "2026-01-10", "estado_vigencia": "Confirmada abierta", "motivo": "En listado oficial; detalle no consultado", "url_fuente": "https://example.com/empleo/000123", "tipo_fuente": "Oficial"}
    },
    {
      "nombre": "habilidades_vacante",
      "columnas": [
        {"nombre": "habilidad_observacion_id", "tipo": "id", "patron": "HV-\\d{5,}", "oblig": "si"},
        {"nombre": "vacante_id", "tipo": "ref", "patron": "VAC-\\d{4,}", "en": "vacantes", "oblig": "si"},
        {"nombre": "observacion_id", "tipo": "ref", "patron": "OBS-\\d{4,}", "en": "observaciones", "misma_vacante": true, "oblig": "si"},
        {"nombre": "habilidad_literal", "tipo": "texto", "oblig": "si"},
        {"nombre": "habilidad_normalizada", "tipo": "texto", "oblig": "no"},
        {"nombre": "tipo_requisito", "tipo": "lista", "valores": ["Obligatorio", "Deseable", "En funciones", "Ambiguo"], "oblig": "si"}
      ],
      "prueba": {"habilidad_observacion_id": "PRUEBA-HV-00001", "vacante_id": "PRUEBA-VAC-0001", "observacion_id": "PRUEBA-OBS-0001", "habilidad_literal": "Experience with Python", "habilidad_normalizada": "Python", "tipo_requisito": "Obligatorio"}
    },
    {
      "nombre": "documentos",
      "columnas": [
        {"nombre": "documento_id", "tipo": "id", "patron": "DOC-\\d{4,}", "oblig": "si"},
        {"nombre": "vacante_id", "tipo": "ref", "patron": "VAC-\\d{4,}", "en": "vacantes", "oblig": "si_existe"},
        {"nombre": "fecha_generacion", "tipo": "fecha", "oblig": "si"},
        {"nombre": "version_perfil", "tipo": "patron", "patron": "\\d+\\.\\d+", "oblig": "si"},
        {"nombre": "version_cv_base", "tipo": "patron", "patron": "\\d+\\.\\d+", "oblig": "si"},
        {"nombre": "idioma", "tipo": "lista", "valores": ["ES", "EN"], "oblig": "si"},
        {"nombre": "formato", "tipo": "lista", "valores": ["PDF", "DOCX", "ODT", "TXT", "MD", "Formulario"], "oblig": "si"},
        {"nombre": "archivo", "tipo": "texto", "oblig": "si"},
        {"nombre": "revision_visual", "tipo": "lista", "valores": ["Satisfactoria", "Con fallas", "No realizada", "No aplica"], "oblig": "si"},
        {"nombre": "texto_extraible", "tipo": "lista", "valores": ["Satisfactoria", "Con fallas", "No realizada", "No aplica"], "oblig": "si"},
        {"nombre": "notas", "tipo": "texto", "oblig": "no"}
      ],
      "prueba": {"documento_id": "PRUEBA-DOC-0001", "vacante_id": "PRUEBA-VAC-0001", "fecha_generacion": "2026-01-10", "version_perfil": "1.10", "version_cv_base": "1.0", "idioma": "ES", "formato": "PDF", "archivo": "CV_prueba.pdf", "revision_visual": "No realizada", "texto_extraible": "No realizada", "notas": "Prueba"}
    },
    {
      "nombre": "busquedas",
      "columnas": [
        {"nombre": "busqueda_id", "tipo": "id", "patron": "BUS-\\d{4,}", "oblig": "si"},
        {"nombre": "fecha_hora", "tipo": "fecha", "hora": true, "oblig": "si"},
        {"nombre": "solicitud_alcance", "tipo": "texto", "oblig": "si"},
        {"nombre": "recursos_versiones", "tipo": "multivalor", "oblig": "si"},
        {"nombre": "fuentes_consultas_filtros", "tipo": "multivalor", "oblig": "si"},
        {"nombre": "cobertura_limitaciones", "tipo": "texto", "oblig": "si"},
        {"nombre": "no_revisado_pendientes", "tipo": "texto", "oblig": "si"},
        {"nombre": "comparacion_anterior", "tipo": "texto", "oblig": "si"},
        {"nombre": "canal", "tipo": "lista", "valores": ["Code", "Web"], "oblig": "si"}
      ],
      "prueba": {"busqueda_id": "PRUEBA-BUS-0001", "fecha_hora": "2026-01-10 09:30", "solicitud_alcance": "Prueba de la hoja", "recursos_versiones": "11 v1.0", "fuentes_consultas_filtros": "Sin consultas", "cobertura_limitaciones": "Sin listado", "no_revisado_pendientes": "Ninguno", "comparacion_anterior": "Sin búsqueda comparable", "canal": "Code"}
    },
    {
      "nombre": "evaluaciones",
      "columnas": [
        {"nombre": "evaluacion_id", "tipo": "id", "patron": "EVA-\\d{4,}", "oblig": "si"},
        {"nombre": "vacante_id", "tipo": "ref", "patron": "VAC-\\d{4,}", "en": "vacantes", "oblig": "si"},
        {"nombre": "observacion_id", "tipo": "ref", "patron": "OBS-\\d{4,}", "en": "observaciones", "misma_vacante": true, "oblig": "si"},
        {"nombre": "fecha_evaluacion", "tipo": "fecha", "oblig": "si"},
        {"nombre": "version_perfil", "tipo": "patron", "patron": "\\d+\\.\\d+", "oblig": "si"},
        {"nombre": "version_evaluacion", "tipo": "patron", "patron": "\\d+\\.\\d+", "oblig": "si"},
        {"nombre": "condiciones", "tipo": "lista", "valores": ["Sin exclusiones", "Excluida"], "oblig": "si"},
        {"nombre": "condiciones_detalle", "tipo": "multivalor", "oblig": "si"},
        {"nombre": "encaje", "tipo": "lista", "valores": ["★★★★★", "★★★★☆", "★★★☆☆", "★★☆☆☆", "★☆☆☆☆", "☆☆☆☆☆"], "oblig": "si_existe"},
        {"nombre": "cobertura", "tipo": "patron", "patron": "\\d+/\\d+(, \\d+ solo académicos?)?", "oblig": "si_existe"},
        {"nombre": "nucleos", "tipo": "multivalor", "oblig": "si_existe"}
      ],
      "prueba": {"evaluacion_id": "PRUEBA-EVA-0001", "vacante_id": "PRUEBA-VAC-0001", "observacion_id": "PRUEBA-OBS-0001", "fecha_evaluacion": "2026-01-10", "version_perfil": "1.0", "version_evaluacion": "1.0", "condiciones": "Sin exclusiones", "condiciones_detalle": "Sueldo | Remoto", "encaje": "★★★☆☆", "cobertura": "3/4, 1 solo académico", "nucleos": "Núcleo A: Directa | Núcleo B: Insuficiente | Núcleo C: Académica/formativa"}
    },
    {
      "nombre": "informes",
      "columnas": [
        {"nombre": "busqueda_id", "tipo": "ref", "patron": "BUS-\\d{4,}", "en": "busquedas", "oblig": "si"},
        {"nombre": "vacante_id", "tipo": "ref", "patron": "VAC-\\d{4,}", "en": "vacantes", "unica_con": "busqueda_id", "oblig": "si"},
        {"nombre": "evaluacion_id", "tipo": "ref", "patron": "EVA-\\d{4,}", "en": "evaluaciones", "misma_vacante": true, "oblig": "si"},
        {"nombre": "empresa", "tipo": "calculada", "formula": "={\"empresa\";MAP(B2:B,LAMBDA(v,IF(v=\"\",,SUBSTITUTE(XLOOKUP(v,vacantes!A2:A,vacantes!B2:B),\"EMP-\",\"\"))))}"},
        {"nombre": "vacante", "tipo": "calculada", "formula": "={\"vacante\";MAP(B2:B,LAMBDA(v,IF(v=\"\",,LET(j,XLOOKUP(v,vacantes!A2:A,vacantes!C2:C),t,XLOOKUP(v,vacantes!A2:A,vacantes!D2:D),u,XLOOKUP(v,vacantes!A2:A,vacantes!E2:E),HYPERLINK(u,IF(OR(j=\"\",j=\"No publicado\"),\"sin Job ID\",j)&\" — \"&t)))))}"},
        {"nombre": "encaje", "tipo": "calculada", "formula": "={\"encaje\";MAP(C2:C,LAMBDA(e,IF(e=\"\",,LET(c,XLOOKUP(e,evaluaciones!A2:A,evaluaciones!G2:G),s,XLOOKUP(e,evaluaciones!A2:A,evaluaciones!I2:I),k,XLOOKUP(e,evaluaciones!A2:A,evaluaciones!J2:J),IF(c=\"Excluida\",\"—\",s&IF(k=\"\",\"\",\" · \"&k))))))}"},
        {"nombre": "antiguedad", "tipo": "calculada", "formula": "={\"antiguedad\";MAP(B2:B,LAMBDA(v,IF(v=\"\",,LET(fp,XLOOKUP(v,vacantes!A2:A,vacantes!I2:I),pd,DATEVALUE(XLOOKUP(v,vacantes!A2:A,vacantes!J2:J)),h,TODAY(),n,IF(fp=\"\",h-pd,h-MIN(DATEVALUE(fp),pd)),IF(AND(fp=\"\",n<=0),\"—\",IF(fp=\"\",\"≥ \",\"\")&n&\" d\"&IF(n>=20,\" · antigua\",\"\"))))))}"},
        {"nombre": "alertas", "tipo": "calculada", "formula": "={\"alertas\";MAP(C2:C,LAMBDA(e,IF(e=\"\",,LET(c,XLOOKUP(e,evaluaciones!A2:A,evaluaciones!G2:G),d,XLOOKUP(e,evaluaciones!A2:A,evaluaciones!H2:H),n,XLOOKUP(e,evaluaciones!A2:A,evaluaciones!K2:K),IF(c=\"Excluida\",\"Excluida: \"&SUBSTITUTE(d,\" | \",\"; \"),LET(ns,SPLIT(n&\"\",\" | \",FALSE),ins,IFERROR(SUBSTITUTE(TEXTJOIN(\"; \",TRUE,FILTER(ns,REGEXMATCH(ns,\": Insuficiente$\"))),\": Insuficiente\",\"\"),\"\"),aca,IFERROR(SUBSTITUTE(TEXTJOIN(\"; \",TRUE,FILTER(ns,REGEXMATCH(ns,\": Académica/formativa$\"))),\": Académica/formativa\",\"\"),\"\"),ps,SPLIT(d&\"\",\" | \",FALSE),pen,IFERROR(LOWER(TEXTJOIN(\", \",TRUE,FILTER(ps,NOT(REGEXMATCH(ps,\"^(Sueldo|Duración|Relación|Horario|Ninguno)$\"))))),\"\"),r,TEXTJOIN(\" · \",TRUE,IF(ins=\"\",\"\",\"Insuficiente: \"&ins),IF(aca=\"\",\"\",\"Académica: \"&aca),IF(pen=\"\",\"\",\"Pendiente: \"&pen)),IF(r=\"\",\"—\",r)))))))}"},
        {"nombre": "url_oficial", "tipo": "calculada", "formula": "={\"url_oficial\";MAP(B2:B,LAMBDA(v,IF(v=\"\",,XLOOKUP(v,vacantes!A2:A,vacantes!E2:E))))}"}
      ],
      "prueba": {"busqueda_id": "PRUEBA-BUS-0001", "vacante_id": "PRUEBA-VAC-0001", "evaluacion_id": "PRUEBA-EVA-0001"}
    }
  ]
}
```

**Campos del bloque:**

| Campo | Qué lleva |
| --- | --- |
| `hoja.nombre` | El nombre del archivo en Drive; en modo local, el del archivo, con `.xlsx` |
| `hoja.configuracion_regional` | La configuración regional de la hoja. Es un requisito técnico, no la región del titular: las fórmulas del bloque separan sus argumentos con comas, y con una configuración de coma decimal, como `es_ES`, el conector las rechaza. Como las celdas de datos son texto, no cambia lo que se ve |
| `hoja.filas` | Las filas con que nace cada pestaña, contando el encabezado (REG-VALIDACION, «Crecimiento») |
| `pestanas` | Las pestañas, en su orden en la hoja |
| `pestanas[].columnas` | Las columnas de la pestaña, en orden: la primera es la A |
| `columnas[].nombre` | El encabezado, en la fila 1 |
| `columnas[].tipo` | `id`, `ref`, `texto`, `multivalor`, `fecha`, `url`, `patron`, `lista` o `calculada`. Su validación en la hoja está en REG-VALIDACION |
| `columnas[].oblig` | `si`, `si_existe` o `no` (REG-CONVENCIONES, «Obligatoriedad»). Las calculadas no lo llevan. Lo comprueba la herramienta del modo local; la hoja no lo usa |
| `columnas[].vacia_con` | Con `oblig` `si`: la columna puede quedar vacía cuando la nombrada tiene valor, como `ultima_observacion_id` en una fila absorbida (REG-IDENTIDAD) |
| `columnas[].patron` | En `id`, `ref` y `patron`: la expresión regular que cumple el valor completo. En `id` y `ref` se admite además `PRUEBA-` delante |
| `columnas[].hora` | En `fecha`: `true` si admite la hora `HH:MM` |
| `columnas[].valores` | En `lista`: los valores aceptados |
| `columnas[].valores_de` | En `lista`, en lugar de `valores`: de dónde salen. `06/CAT-EMPRESAS` son los IDs del catálogo de 06 |
| `columnas[].en` | En `ref`: la pestaña donde el ID debe existir, en su columna A |
| `columnas[].misma_vacante` | En `ref`: `true` si la fila citada tiene el mismo `vacante_id` que esta fila |
| `columnas[].unica_con` | En `ref`: la pareja de esta columna con la nombrada no se repite en la pestaña |
| `columnas[].distinta_de` | En `ref`: no puede ser igual a la columna nombrada de la misma fila |
| `columnas[].formula` | En `calculada`: la fórmula de su encabezado, que devuelve el encabezado y los valores de todas las filas |
| `pestanas[].prueba` | Una fila de datos sintéticos válidos para comprobar la hoja (REG-VALIDACION, «Comprobación»). En `informes`, solo las columnas que se escriben |

## REG-VALIDACION — Creación y validación de la hoja

### Creación

Con los conectores de Google Drive y Google Sheets, en este orden. Cada paso es una llamada, salvo donde se indica:

1. **Archivo:** con Drive, una hoja de cálculo nueva con el `nombre` del bloque. Nace con una pestaña de `sheetId` 0.
2. **Configuración regional y zona horaria:** la `configuracion_regional` del bloque y la `zona_horaria` de 04, en una llamada propia y antes de cualquier validación. El conector lee las fórmulas con la configuración vigente al empezar cada llamada: en la misma llamada que las validaciones, las rechazaría.
3. **Pestañas:** la pestaña 0 toma el nombre de la primera del bloque y se agregan las demás en orden, cada una con `filas` filas. En todas, la fila 1 queda fija.
4. **Encabezados:** los `nombre` de cada pestaña en su fila 1. En `informes`, solo A1:C1; las fórmulas van en el paso 8.
5. **Formato de texto:** en cada columna que no es calculada, de la fila 2 al final, antes de escribir cualquier dato.
6. **Validaciones:** las de la tabla de abajo, cada una de la fila 2 al final de su columna.
7. **Protección:** las columnas calculadas, desde la fila 1, protegidas solo con advertencia.
8. **Fórmulas:** la `formula` de cada columna calculada, en su celda de la fila 1.

Los pasos 3 a 7 pueden ir en una sola llamada.

**Validación por tipo.** `X` es la letra de la columna; la fórmula se escribe para la fila 2 y la hoja la ajusta en las demás. `{patron}` es el de la columna.

| Tipo | Regla | Fórmula o condición | Rechaza |
| --- | --- | --- | --- |
| `id` | Patrón y único | `=AND(REGEXMATCH(X2,"^(PRUEBA-)?{patron}$"),COUNTIF($X$2:$X,X2)=1)` | Sí |
| `ref` | Patrón y existe en la columna A de `en` | `=AND(REGEXMATCH(X2,"^(PRUEBA-)?{patron}$"),COUNTIF(INDIRECT("{en}!A2:A"),X2)>0)` | No |
| `fecha` | Patrón y fecha real | `=AND(REGEXMATCH(X2,"^\d{4}-\d{2}-\d{2}$"),ISNUMBER(DATEVALUE(X2)))` | Sí |
| `fecha` con `hora` | Patrón, fecha real y hora válida | `=AND(REGEXMATCH(X2,"^\d{4}-\d{2}-\d{2}( \d{2}:\d{2})?$"),ISNUMBER(DATEVALUE(LEFT(X2,10))),OR(LEN(X2)=10,ISNUMBER(TIMEVALUE(RIGHT(X2,5)))))` | Sí |
| `url` | Empieza con `http://` o `https://` y no tiene espacios | `=REGEXMATCH(X2,"^https?://\S+$")` | Sí |
| `patron` | Patrón | `=REGEXMATCH(X2,"^{patron}$")` | Sí |
| `lista` | Uno de `valores`, con desplegable | Condición de lista (`ONE_OF_LIST`) | Sí |
| `texto`, `multivalor` y `calculada` | Ninguna | — | — |

- **Variantes de `ref`:** cada modificador cambia o agrega una condición dentro del `AND`:
  - `misma_vacante`: el `COUNTIF` pasa a `COUNTIFS(INDIRECT("{en}!A2:A"),X2,INDIRECT("{en}!V2:V"),W2)>0`, donde `V` es la letra de `vacante_id` en `en` y `W`, la de `vacante_id` en esta pestaña.
  - `unica_con`: se agrega `COUNTIFS($U$2:$U,U2,$X$2:$X,X2)=1`, donde `U` es la letra de la columna nombrada.
  - `distinta_de`: se agrega `X2<>D2`, donde `D` es la letra de la columna nombrada.
  - Si `en` es la misma pestaña, el rango es `$A$2:$A`, sin `INDIRECT`.
- **`INDIRECT`:** una validación no puede citar otra pestaña directamente; por eso las referencias a otras pestañas lo usan.
- **`valores_de: 06/CAT-EMPRESAS`:** los IDs de la tabla CAT-EMPRESAS de 06. Si el catálogo está vacío, la columna queda sin validación hasta la primera empresa. Al agregar una empresa a 06, la lista se vuelve a aplicar con todos los IDs.
- **URL:** la validación de URL propia de Sheets no pasa por el conector, así que se usa la fórmula.
- **Rigor:** las listas, los IDs propios, las fechas, las URL y los patrones rechazan la entrada manual inválida. Las referencias solo marcan la celda, para que el orden en que se escriben o pegan las filas no bloquee la captura. Ninguna detiene al conector (REG-HOJA).

### Comprobación

Al crear la hoja, y cada vez que cambie su estructura, se comprueba con las filas `prueba` del bloque:

1. **Filas de prueba:** la `prueba` de cada pestaña va en su fila 2, en este orden: `busquedas`, `vacantes`, `observaciones`, `habilidades_vacante`, `documentos`, `evaluaciones` e `informes` (en esta, solo A:C).
2. **Fórmulas de validación:** en cada pestaña, en la columna que sigue a la última del esquema, fila 2, una fórmula temporal `={…}` con las fórmulas de validación de esa fila, sin su `=` y separadas por comas, solo de las columnas validadas con fórmula que tienen valor en la prueba. Todas deben dar `TRUE`.
3. **Lectura:** cada pestaña completa, de A1 a la columna de la fórmula temporal:
   - Los encabezados, en el orden del bloque.
   - Los valores de prueba, tal como se escribieron: `000123` y `1.10` no pierden ceros y las fechas siguen como texto.
   - En `informes`, D2:I2: `PRUEBA`, `000123 — Puesto de prueba`, `★★★☆☆ · 3/4, 1 solo académico`, `N d · antigua` (N, los días desde el 2026-01-05 hasta hoy en la zona horaria de 04), `Insuficiente: Núcleo B · Académica: Núcleo C · Pendiente: remoto` y `https://example.com/empleo/000123`.
4. **Reglas:** la configuración regional y la zona horaria de la hoja, la regla de validación de cada columna en la fila 2 (con sus valores en las listas y `strict` según «Rechaza»; `empresa_id` no tiene regla si 06 no tiene empresas), la fila 1 fija en cada pestaña y la protección de las columnas calculadas.
5. **Borrado:** los valores de la fila 2 de cada pestaña y la fórmula temporal; en `informes`, solo A:C y la fórmula temporal, porque D:I son las fórmulas. Después, cada pestaña muestra solo su encabezado.

`EMP-PRUEBA` no está en la lista de `empresa_id`, así que esa celda queda marcada mientras dura la prueba. Si algo no cuadra, se corrige en la hoja y se repite la comprobación.

### Crecimiento

Cada pestaña nace con `filas` filas. Cuando una escritura no cabe, se insertan filas **dentro** del rango validado: antes de la última fila, heredando de la anterior. Así la validación y el formato de texto se extienden solos. No se insertan justo debajo del encabezado, porque heredarían su formato y quedarían sin validación.

## REG-LOCAL — Archivo local (modo local)

El archivo `ChambaKit_Registros.xlsx` (el `nombre` del bloque) está en la raíz de la copia. Se lee y se escribe solo con `herramientas/registros.py`, con el Python del entorno virtual de la copia, que tiene `openpyxl`:

```sh
.venv/bin/python -I herramientas/registros.py <orden> …
```

En Windows, el Python es `.venv\Scripts\python.exe`. `--help` da las órdenes y la forma de su entrada, que va por stdin o en un archivo del directorio temporal de la sesión, nunca de la copia.

- **Creación:** `crear`, desde el bloque, en el paso 8 de `/configurar`. Lleva las pestañas y columnas del bloque, salvo las calculadas de `informes`, que no se guardan. No necesita la comprobación con filas `prueba` de REG-VALIDACION: la validación está en la herramienta, y sus pruebas automáticas la cubren.
- **Escritura:** `agregar` y `actualizar` comprueban cada fila que escriben contra el bloque: lo mismo que valida la hoja, más la obligatoriedad, y las referencias rechazan en lugar de solo marcar. Si una fila no cumple, no escriben ninguna y dicen qué corregir. Solo comprueban las filas que escriben: un cambio no vuelve a comprobar las filas que citan a la cambiada. Las referencias se resuelven contra lo ya registrado más lo de la misma llamada, así que una búsqueda se registra en dos llamadas (07/BUS-REGISTRO): `agregar` con todas sus filas nuevas, de todas las pestañas, y `actualizar` con los cambios a las filas ya registradas.
- **Lectura:** `leer` da una pestaña completa o las filas de unos IDs. `informe` da la tabla resumen de una búsqueda: sus filas de `informes` con las columnas calculadas, con la lógica de las fórmulas del bloque y la fecha de hoy en la zona horaria de 04. `exportar` da todas las pestañas a la vez, fila por fila y con el rango de la hoja donde van, para el cambio a la hoja (REG-HOJA); los valores que la hoja interpretaría ya llevan su `'` delante.
- **Encabezados:** la herramienta los compara con el bloque en cada uso y se detiene si no coinciden (REG-DECISIONES, «Encabezados»).
- **Historial y respaldo:** git. El archivo se versiona en la copia, así que no se ignora. Al cerrar una sesión que lo modificó, Claude le ofrece al titular un commit con él y, si la copia tiene remoto privado, el push.
- **Edición a mano:** el titular puede abrir el archivo en una hoja de cálculo para consultarlo. Las filas se escriben con la herramienta, que es la que las comprueba.

## REG-DECISIONES — Decisiones del esquema

- **Autoridades:** el perfil (02) manda sobre la trayectoria; las preferencias (04), sobre las condiciones; las fichas (06), sobre la configuración por empresa.
- **Historia de comprobaciones:** `observaciones` conserva todas las comprobaciones sucesivas. `vacantes` muestra el estado vigente a través de la última observación, sin crear otra autoridad contradictoria.
- **Dimensiones separadas:** vigencia, compatibilidad y postulación nunca van en una misma columna.
- **Ubicación y fechas:** ubicación literal y relación regional van separadas, igual que las fechas de publicación, detección y verificación.
- **Evidencia:** la evidencia fechada es la propia observación: fecha, URL, tipo de fuente y un `motivo` que cita el texto breve pertinente. No se guardan archivos ni copias de descripciones; la frase exacta de cada requisito queda en `habilidad_literal`. Así se cumple la regla de 07 de conservar evidencia fechada, y 07 precisa la evidencia mínima por estado. Se conservan los Job IDs.
- **Valores:** no inventar valores para llenar columnas. Una celda vacía es dato no registrado, no cero, cierre ni ausencia de habilidad.
- **Sin duplicar datos:** ninguna columna repite datos de otra pestaña, salvo tres atajos con regla de mantenimiento: `vacantes.primera_deteccion`, `vacantes.ultima_observacion_id` y `habilidades_vacante.vacante_id`. `informes` no copia valores: guarda IDs y calcula el resto.
- **Datos sintéticos de prueba:** marcarlos como tales y borrarlos después.
- **Ámbito:** cada pestaña abarca todas las empresas; no crear registros por empresa.
- **Encabezados:** no se cambian sin acordarlo aquí. Un cambio se hace en REG-CAMPOS, en el bloque de REG-ESQUEMA y en la hoja o el archivo local; la hoja se comprueba según REG-VALIDACION.
- **Postulaciones:** no se registran y no hay pestaña de seguimiento. Para postular, el titular pide el CV en el formato que exija la vacante (09) y postula por su cuenta, manualmente. El documento queda en `documentos`. Claude no envía candidaturas ni contacta a terceros.

## REG-PENDIENTES

Dudas del titular sobre el esquema, con `REG-P##` y su tratamiento. Al resolverse, salen de la tabla; si cambian una columna, se aplican según REG-DECISIONES («Encabezados»).

| ID | Pendiente | Tratamiento |
| --- | --- | --- |
