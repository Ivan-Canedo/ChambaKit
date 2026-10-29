# 11 — Esquema de registros

**Versión:** 1.6 — 2026-10-28 — En Code en la nube, los cambios se integran en `main` al cerrar, y un choque en el archivo de registros se resuelve reimportando (REG-LOCAL, «Historial y respaldo»).
**Estado:** esquema de la plantilla. El paso 8 de `/configurar` (Registros) crea el archivo de registros desde el bloque de REG-ESQUEMA.

## Responsabilidad

Definir campos, relaciones, autoridades y versionado de los datos de búsquedas, vacantes, observaciones, habilidades, evaluaciones, informes y documentos, y cómo se crea y se usa el archivo de registros que los guarda.

## REG-LUGAR — Dónde viven los registros

**En un solo lugar:** el archivo de registros, `ChambaKit_Registros.xlsx` en la raíz de la copia, con una pestaña por tabla y el esquema de REG-ESQUEMA. Lo crea el paso 8 de `/configurar` y solo se escribe desde el canal Code, con su herramienta (REG-LOCAL). No hay otro lugar ni cambio de lugar.

**Canal Web:** no lee el archivo, sino la instantánea (REG-INSTANTANEA), que la herramienta regenera con cada escritura.

## REG-CONVENCIONES — Reglas comunes

**Tipos:**

- **ID:** prefijo y número consecutivo (tabla de abajo).
- **Texto.** Cuando la columna dice «literal», se copia tal cual de la fuente, sin traducir ni normalizar.
- **Fecha:** texto ISO `AAAA-MM-DD`; donde se indica, se admite la hora: `AAAA-MM-DD HH:MM`. Se guarda como texto porque un valor de fecha no puede tener hora opcional: mostraría un 00:00 falso o escondería una hora real. Se ordena bien alfabéticamente y la herramienta comprueba que sea una fecha real.
- **URL:** empieza con `http://` o `https://` y no tiene espacios.
- **Lista cerrada:** solo admite sus valores.
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

**Fechas y zona horaria:** en la zona horaria de 04 (`zona_horaria` del bloque de PREF-UBICACION). La hora solo se registra si se conoce: en claude.ai no hay garantía de conocerla y no se infiere. Las comprobaciones del mismo día se ordenan por ID.

**Nulos:** una celda vacía significa «no registrado». Hay dos valores explícitos:

- `No publicado`: se comprobó que la fuente no da el dato. Solo en `job_id`, `ubicacion_literal` y `modalidad_literal`.
- `Ninguno`: no hay nada que reportar. Solo en `busquedas` y en `evaluaciones.condiciones_detalle`.

**Formato de texto:** todas las celdas de datos se escriben como texto. Así `1.10` no se convierte en 1.1, un Job ID numérico no pierde ceros y las fechas no cambian de forma. Ninguna columna lleva números ni fórmulas, y las calculadas de `informes` no se guardan.

**Ubicaciones múltiples:** una fila por requisición, no por sede. `ubicacion_literal` las anota en el orden de la fuente y `region_relacionada` resume el conjunto.

## REG-CAMPOS — Pestañas y columnas

| Pestaña | Unidad | Columnas |
| --- | --- | --- |
| `vacantes` | Una requisición identificada | vacante_id, empresa_id, job_id, titulo, url_oficial, ubicacion_literal, modalidad_literal, region_relacionada, fecha_publicacion, primera_deteccion, ultima_observacion_id, duplicado_de |
| `observaciones` | Comprobación fechada de una vacante | observacion_id, vacante_id, busqueda_id, fecha_verificacion, estado_vigencia, motivo, url_fuente, tipo_fuente |
| `habilidades_vacante` | Habilidad o requisito en una descripción observada | habilidad_observacion_id, vacante_id, observacion_id, habilidad_literal, habilidad_normalizada, tipo_requisito |
| `documentos` | Un archivo generado | documento_id, vacante_id, fecha_generacion, version_perfil, version_cv_base, idioma, formato, archivo, revision_visual, texto_extraible, notas |
| `busquedas` | Ejecución de una búsqueda o comprobación | busqueda_id, fecha_hora, solicitud_alcance, recursos_versiones, fuentes_consultas_filtros, cobertura_limitaciones, no_revisado_pendientes, comparacion_anterior |
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

**Empresa:** para registrar una vacante, su empresa necesita un EMP-ID en 06, aunque solo esté como «explorada». La herramienta lee el catálogo de 06, así que el ID vale desde que se agrega ahí.

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

### `informes`

La tabla resumen de cada búsqueda (08/EVAL-INFORME), para consultarla sin rehacerla. El agente escribe solo los IDs. Las demás columnas no se guardan: la herramienta las calcula desde `vacantes` y `evaluaciones` cada vez que da la tabla (`informe`) o regenera la instantánea (REG-LOCAL).

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
| url_oficial | Calculada | — | La de `vacantes`, aparte, porque `informe` da `vacante` como texto, sin su liga |

- **Una fila por vacante evaluada de la tabla,** incluidas las excluidas, en el orden de la tabla. No tiene ID propio: cada fila es la pareja `busqueda_id` + `vacante_id`. Las vacantes no evaluadas no tienen fila, y la línea «N sin relación…» no se guarda.
- **Referencias que faltan:** si la vacante o la evaluación de una fila no existe, sus columnas calculadas dicen `#N/A`.
- **Umbral de «antigua»:** la herramienta lo lee de la línea «Marca «antigua»» de 08/EVAL-ACUERDOS, donde el titular lo cambia; sin esa línea, usa 20 días.
- **Un solo cálculo:** la lógica de estas columnas vive solo en `herramientas/registros.py`. Un cambio de estas reglas se hace en la herramienta, en su prueba y en esta tabla.
- **Vista, no autoridad:** si una aclaración actualiza la fila de `evaluaciones` (08/EVAL-REGISTRO), la tabla lo refleja. Cuando una búsqueda posterior hace una evaluación nueva, esta aparece en las filas de esa búsqueda, y las filas anteriores siguen mostrando la evaluación que se entregó en su momento.
- **Antigüedad:** cambia cada día, con la fecha de hoy en la zona horaria de 04. Las fechas relativas («hace 3 días») no se guardan, así que aquí no aparecen.

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

**Versiones:** no se borran filas, salvo los datos sintéticos. git cubre las ediciones (REG-LOCAL, «Historial y respaldo»).

## REG-ESQUEMA — Bloque del esquema

El esquema completo en la forma que lee una herramienta: pestañas, columnas, listas cerradas y validaciones. Es el primer bloque ```` ```json ```` de esta sección, y de él salen el archivo de registros y las comprobaciones de su herramienta (REG-LOCAL). Dice lo mismo que las tablas de REG-CAMPOS: al cambiar una columna se cambian los dos, según REG-DECISIONES («Encabezados»).

```json
{
  "archivo": {"nombre": "ChambaKit_Registros"},
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
      ]
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
      ]
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
      ]
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
      ]
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
        {"nombre": "comparacion_anterior", "tipo": "texto", "oblig": "si"}
      ]
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
      ]
    },
    {
      "nombre": "informes",
      "columnas": [
        {"nombre": "busqueda_id", "tipo": "ref", "patron": "BUS-\\d{4,}", "en": "busquedas", "oblig": "si"},
        {"nombre": "vacante_id", "tipo": "ref", "patron": "VAC-\\d{4,}", "en": "vacantes", "unica_con": "busqueda_id", "oblig": "si"},
        {"nombre": "evaluacion_id", "tipo": "ref", "patron": "EVA-\\d{4,}", "en": "evaluaciones", "misma_vacante": true, "oblig": "si"},
        {"nombre": "empresa", "tipo": "calculada"},
        {"nombre": "vacante", "tipo": "calculada"},
        {"nombre": "encaje", "tipo": "calculada"},
        {"nombre": "antiguedad", "tipo": "calculada"},
        {"nombre": "alertas", "tipo": "calculada"},
        {"nombre": "url_oficial", "tipo": "calculada"}
      ]
    }
  ]
}
```

**Campos del bloque:**

| Campo | Qué lleva |
| --- | --- |
| `archivo.nombre` | El nombre del archivo de registros, sin `.xlsx` |
| `pestanas` | Las pestañas, en su orden en el archivo |
| `pestanas[].columnas` | Las columnas de la pestaña, en orden: la primera es la A |
| `columnas[].nombre` | El encabezado, en la fila 1 |
| `columnas[].tipo` | `id`, `ref`, `texto`, `multivalor`, `fecha`, `url`, `patron`, `lista` o `calculada` (REG-CONVENCIONES, «Tipos»). Una `calculada` no se guarda: la calcula la herramienta (REG-CAMPOS, `informes`) |
| `columnas[].oblig` | `si`, `si_existe` o `no` (REG-CONVENCIONES, «Obligatoriedad»). Las calculadas no lo llevan |
| `columnas[].vacia_con` | Con `oblig` `si`: la columna puede quedar vacía cuando la nombrada tiene valor, como `ultima_observacion_id` en una fila absorbida (REG-IDENTIDAD) |
| `columnas[].patron` | En `id`, `ref` y `patron`: la expresión regular que cumple el valor completo. En `id` y `ref` se admite además `PRUEBA-` delante |
| `columnas[].hora` | En `fecha`: `true` si admite la hora `HH:MM` |
| `columnas[].valores` | En `lista`: los valores aceptados |
| `columnas[].valores_de` | En `lista`, en lugar de `valores`: de dónde salen. `06/CAT-EMPRESAS` son los IDs del catálogo de 06 |
| `columnas[].en` | En `ref`: la pestaña donde el ID debe existir, en su columna A |
| `columnas[].misma_vacante` | En `ref`: `true` si la fila citada tiene el mismo `vacante_id` que esta fila |
| `columnas[].unica_con` | En `ref`: la pareja de esta columna con la nombrada no se repite en la pestaña |
| `columnas[].distinta_de` | En `ref`: no puede ser igual a la columna nombrada de la misma fila |

## REG-LOCAL — El archivo y su herramienta

El archivo `ChambaKit_Registros.xlsx` (el `nombre` del bloque) está en la raíz de la copia. Se lee y se escribe solo con `herramientas/registros.py`, con el Python del entorno virtual de la copia, que tiene `openpyxl`:

```sh
.venv/bin/python -I herramientas/registros.py <orden> …
```

En Windows, el Python es `.venv\Scripts\python.exe`. `--help` da las órdenes y la forma de su entrada, que va por stdin o en un archivo del directorio temporal de la sesión, nunca de la copia.

- **Creación:** `crear`, desde el bloque, en el paso 8 de `/configurar`. Lleva las pestañas y columnas del bloque, salvo las calculadas de `informes`, que no se guardan. La validación está en la herramienta, y sus pruebas automáticas la cubren.
- **Escritura:** tres órdenes, que comprueban cada fila que escriben contra el bloque: tipos, listas, obligatoriedad, IDs únicos y referencias. Si una fila no cumple, no escriben ninguna y dicen todos los errores. Solo comprueban las filas que escriben: un cambio no vuelve a comprobar las filas que citan a la cambiada. Las referencias se resuelven contra lo ya registrado más lo de la misma llamada.
  - `importar` registra una búsqueda desde la salida JSON de `buscar.py` y un archivo de decisiones (07/BUS-REGISTRO), sin que el agente genere sus filas. Escribe la fila de `busquedas`, con la cobertura y la comparación con la última búsqueda comparable, las vacantes nuevas y una observación por vacante listada. En las ya registradas, que identifica por REG-IDENTIDAD, actualiza los campos que cambiaron y `ultima_observacion_id`. No escribe nada si queda una línea «revisar» sin decisión o un `[FALLO]` sin declarar. Devuelve el `busqueda_id` y una lista compacta de las vacantes (ID, título y departamento).
  - `agregar` escribe filas nuevas de varias pestañas a la vez: en una búsqueda, los requisitos, las evaluaciones y `informes`, que piden juicio.
  - `actualizar` cambia columnas de filas ya registradas, por su ID.
- **Migración:** `migrar` pasa a esta versión una hoja de Google descargada como `.xlsx` (Archivo → Descargar → Microsoft Excel) o el archivo de registros de una copia 1.x, sin pasar las filas por el agente (ADR 0006).
  - **Entrada:** lee los valores de cada pestaña por el nombre de sus columnas. Ignora las calculadas de `informes` y quita las que el esquema ya no tiene, como `canal` de `busquedas`. Se detiene si falta una pestaña o columna del bloque o sobra una que no conoce.
  - **Comprobación:** cada fila, con las mismas reglas que `agregar`. Con un solo error no escribe nada y dice todos, con pestaña, fila de la hoja y columna.
  - **Correcciones:** `--correcciones` recibe un JSON `{pestaña: {ID o "fila N": {columna: texto}}}`, que se aplica antes de comprobar. Así solo las filas con error pasan por el agente, que le propone al titular cada corrección. En `informes`, que no tiene ID propio, o con un ID repetido, la fila se nombra por su número.
  - **Salida:** el archivo completo y, por pestaña, cuántas filas tenía la entrada y cuántas tiene el archivo escrito, para que el titular compare. También dice las columnas quitadas, cuántas filas corrigió y las pestañas de la entrada que no son del esquema.
  - **Sin sobrescribir:** no reemplaza un archivo de registros que ya tenga filas, salvo cuando la entrada es ese mismo archivo, de una versión anterior. Solo lee la entrada: la hoja de Drive queda intacta, y el titular decide si la borra.
- **Instantánea:** las órdenes de escritura y `migrar` la regeneran después de escribir (REG-INSTANTANEA); si rechazan la entrada, no la tocan. `instantanea` la regenera a pedido, por ejemplo si alguien la borró o la editó.
- **Lectura:** `leer` da una pestaña completa o las filas de unos IDs. `informe` da la tabla resumen de una búsqueda: sus filas de `informes` con las columnas calculadas de REG-CAMPOS, a la fecha de hoy en la zona horaria de 04 y con el umbral de «antigua» de 08/EVAL-ACUERDOS.
- **Encabezados:** la herramienta los compara con el bloque en cada uso y se detiene si no coinciden (REG-DECISIONES, «Encabezados»).
- **Historial y respaldo:** git. El archivo se versiona en la copia, así que no se ignora. Al cerrar una sesión que lo modificó, el agente le ofrece al titular un commit con él y, si la copia tiene remoto privado, el push.
  - **Code en la nube:** la sesión trabaja en un clon nuevo, en una rama propia que Code local y el canal Web no leen. Al cerrar una sesión que cambió módulos, registros o CV de `muestras_cv/`, el agente integra en `main`, con permiso del titular para cada paso: commit, `git fetch origin main`, `git rebase origin/main` y `git push origin HEAD:main`. Si `main` no avanzó desde que abrió la sesión, el rebase no cambia nada. Si el push se rechaza porque `main` avanzó otra vez, se repiten el fetch y el rebase.
  - **La rama de la sesión no se conserva:** no se sube. Si ya está en el remoto, el agente la borra después del push a `main` (`git push origin --delete <rama>`), con permiso.
  - **Choque en el archivo de registros:** pasa si otra sesión registró en paralelo. El archivo es binario, así que no se fusiona a mano. En cada commit que choque, el agente toma el archivo y la instantánea del `main` nuevo (`git checkout origin/main -- ChambaKit_Registros.xlsx instantanea/`), los agrega y sigue el rebase (`git rebase --continue`); si el commit queda vacío, porque solo traía registros, lo salta (`git rebase --skip`). Al terminar el rebase, rehace una sola vez sobre ese archivo las escrituras de la sesión: `importar` con la misma salida JSON y el mismo archivo de decisiones, que siguen en el directorio temporal de la sesión, y `agregar` y `actualizar` con los IDs que devuelva `importar`, porque pueden cambiar. La herramienta regenera la instantánea completa al escribir. Con eso hace un commit nuevo y el push a `main`.
- **Edición a mano:** el titular puede abrir el archivo en una hoja de cálculo para consultarlo. Las filas se escriben con la herramienta, que es la que las comprueba.

## REG-INSTANTANEA — Instantánea para el canal Web

La copia en Markdown del archivo de registros que lee el canal Web: la carpeta `instantanea/` de la copia, con dos vistas. Es una vista, no una autoridad: manda el archivo.

- **`informes.md`:** las últimas 10 búsquedas, la más reciente primero. Cada una lleva su fila de `busquedas` (alcance, cobertura, pendientes y comparación) y su tabla resumen con el formato de 08/EVAL-INFORME, con las columnas calculadas de `informes`.
- **`vacantes.md`:** una sección por cada vacante con evaluación cuya última observación no es `Cerrada`, salvo las filas absorbidas por una fusión (`duplicado_de`, REG-IDENTIDAD). El encabezado lleva el `VAC-` ID, el Job ID, el `empresa_id` y el título, para encontrarla aunque solo llegue un fragmento. Debajo van sus campos de `vacantes` y su antigüedad, su última observación, su última evaluación registrada y los requisitos de la observación evaluada. Los requisitos van agrupados por frase literal, con sus términos normalizados y su tipo, así que «Python or R» sigue siendo una alternativa.
- **Qué no trae:** las vacantes sin evaluación, el historial de observaciones y `documentos`.
- **Fecha:** el encabezado de cada vista lleva la fecha y hora de exportación, en la zona horaria de 04. La antigüedad está calculada a esa fecha, no a la de la lectura.
- **Cuándo se regenera:** completa, cada vez que la herramienta escribe en el archivo (REG-LOCAL), y a pedido con `instantanea`. Se arma antes de guardar el archivo: si no se puede, como cuando falta la zona horaria de 04, la herramienta tampoco escribe las filas.
- **Nunca se edita a mano:** la siguiente escritura la reemplaza completa. Para corregir un dato, se corrige el archivo con la herramienta.
- **Tamaño:** si pasa de 300 KB, la herramienta lo avisa en stderr sin fallar, para recortarla antes de que el canal Web deje de leerla completa.
- **Formato:** pasa markdownlint; los textos de los registros van escapados y las URL como autoliga.
- **En git:** se versiona en la copia junto con el archivo, en el mismo commit. La plantilla no trae la carpeta: la crea la primera escritura en una copia.

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
- **Encabezados:** no se cambian sin acordarlo aquí. Un cambio se hace en REG-CAMPOS, en el bloque de REG-ESQUEMA y en el archivo de registros.
- **Postulaciones:** no se registran y no hay pestaña de seguimiento. Para postular, el titular pide el CV en el formato que exija la vacante (09) y postula por su cuenta, manualmente. El documento queda en `documentos`. El agente no envía candidaturas ni contacta a terceros.

## REG-PENDIENTES

Dudas del titular sobre el esquema, con `REG-P##` y su tratamiento. Al resolverse, salen de la tabla; si cambian una columna, se aplican según REG-DECISIONES («Encabezados»).

| ID | Pendiente | Tratamiento |
| --- | --- | --- |
