# 08 — Evaluación de vacantes

**Versión:** 1.2 — 2026-10-27 — La herramienta de registros toma el umbral de «antigua» de EVAL-ACUERDOS; EVAL-INFORME y EVAL-REGISTRO ya no hablan de la hoja.
**Estado:** método de la plantilla. Las condiciones salen de 04 y las familias de 05; queda listo con el paso 5 de `/configurar` (Habilidades y roles).
**Evaluaciones vigentes desde:** 1.0. Sube a la versión nueva solo si el cambio altera la clasificación de requisitos, las categorías, el nivel, la cobertura o las condiciones. Un cambio de 04 no lo sube: lo cubre la regla de EVAL-REGISTRO.

## EVAL-ALCANCE — Responsabilidad

Comparar los requisitos y condiciones de una vacante con la trayectoria y las preferencias, distinguiendo evidencia, experiencia transferible, brechas e incógnitas. La evaluación sirve para que el titular decida si postula y alimenta la adaptación del CV (09). El titular postula manualmente.

## EVAL-REGLAS — Reglas generales

- **Insumos:** la descripción y la evidencia fechadas de la vacante, el maestro (02), las preferencias (04) y el mapa de habilidades (05).
- **Dimensiones separadas:** vigencia, antigüedad, encaje profesional, condiciones y estado de postulación se evalúan por separado. Ninguna modifica a otra.
- **Habilidad ausente del CV:** no es carencia confirmada. Buscarla en el maestro y preguntar si es determinante (EVAL-PREGUNTAS).
- **Requisitos y contexto:** distinguir requisito obligatorio de deseable, y contexto laboral de académico o introductorio.
- **Nivel:** no inferir seniority, dominio ni credenciales por títulos, antigüedad o empresas.
- **Justificación:** explicar correspondencias y límites con referencias concretas al perfil.
- **Puntuación:** el nivel de encaje no es probabilidad de contratación.
- **Perfil intacto:** no alterar el perfil para que coincida con un anuncio.

## EVAL-ACUERDOS — Valores por defecto y decisiones del titular

**Valor por defecto (ajustable):**

- **Marca «antigua»:** a partir de 20 días publicada (EVAL-ANTIGUEDAD). Señala las vacantes abiertas hace tiempo para que el titular lo considere al decidir; no excluye. La herramienta de registros lee el número de esta línea para `informe` y la instantánea (11/REG-CAMPOS, `informes`): si el titular lo cambia, se cambia aquí, en cifras, y sin esta línea vale 20.

**Decisiones del titular:** si el titular cambia un valor por defecto, el cambio se anota aquí, con ID `EVAL-U##` y fecha, y se aplica en la sección que lo usa. Sus condiciones no se anotan aquí: su autoridad es 04 (EVAL-CONDICIONES).

| ID | Fecha | Decisión |
| --- | --- | --- |

## EVAL-FLUJO — Secuencia de trabajo

1. **Búsqueda (07):** al terminar, evaluar cada vacante relacionada con alguna familia ROL de 05. Si la relación es dudosa, se evalúa. Las demás se cuentan en una línea y no se evalúan; si el titular pide alguna, se evalúa.
2. **Por vacante, en este orden:** condiciones (EVAL-CONDICIONES). Si 04 excluye tipos de puesto, se empieza por «Tipo de puesto», que se ve en el título o en el anuncio: si no cumple, se registra `Excluida` sin extraer requisitos (07). Si la vacante no quedó excluida, clasificación de requisitos (EVAL-REQUISITOS) y encaje (EVAL-ENCAJE). Reutilizar una evaluación guardada cuando aplique (EVAL-REGISTRO).
3. **Entregar solo la tabla resumen** (EVAL-INFORME). Sin preguntas ni detalle.
4. **Cuando el titular pregunta por una vacante:** si hace falta, preguntarle lo que pueda cambiar el resultado (EVAL-PREGUNTAS); después, entregar el detalle.
5. **Si le interesa:** generar el CV (09) a partir del detalle.
6. **Registrar** cada evaluación en la pestaña `evaluaciones` (EVAL-REGISTRO), y la tabla resumen en `informes` (EVAL-INFORME).

No se gastan preguntas ni detalle en vacantes que el titular no pidió.

## EVAL-REQUISITOS — Extracción y tipo

Cada requisito se registra en `habilidades_vacante` (11) con su `tipo_requisito`, que anota lo que dice el anuncio. Clasificación:

| Situación en el anuncio | Tipo |
| --- | --- |
| Secciones separadas («Minimum/Required» y «Preferred/Nice to have») | El de su sección |
| Una sola lista con título que expresa necesidad («Qualifications», «Requirements», «What you'll need», «Must have») sin sección de preferidos | Obligatorio |
| Requisito matizado dentro de una lista obligatoria («ideally», «a plus», «preferably», «bonus», «is valued», «is preferred», «highly desirable») | Deseable, solo ese requisito |
| Aparece solo en responsabilidades o en la descripción del puesto | En funciones |
| Alternativas («Python, R or SQL»; «Bachelor's degree in X, Y or a related field») | Una fila por opción, con el tipo de la lista; se cubren si se cubre cualquiera |
| Ejemplos («such as Python or R»; «or similar»; «and other») | Una fila por herramienta nombrada, como alternativas. «Or similar» u «other» admiten evidencia equivalente |
| Requisitos juntos («SQL and Python») | Una fila por requisito; se evalúan aparte |
| Título neutro, que no expresa necesidad («Skills», «About you»), que mezcla requisitos matizados y no matizados, o redacción que no permite decidir | Ambiguo |

**Peso en la evaluación:**

| Tipo | Cuenta en la cobertura | Puede ser núcleo |
| --- | --- | --- |
| Obligatorio | Sí | Sí |
| Ambiguo | Sí, como obligatorio; el detalle lo marca «(amb.)» | Sí |
| En funciones | No | Sí; los núcleos suelen salir de las responsabilidades |
| Deseable | No | No; solo informe y CV |

Las preguntas sobre ambigüedades del anuncio no se le hacen al titular, porque solo la empresa puede aclararlas (EVAL-PREGUNTAS B).

## EVAL-ENCAJE — Categorías y nivel

### Categoría de cada requisito

Son las categorías de 09/CV-FLUJO, cada una con su localizador de 02 y el límite que importe:

| Categoría | Cuándo | Relación de 05 |
| --- | --- | --- |
| **Directa** | Evidencia laboral (EXP y PRY de 02) de lo mismo que se pide | Coincidencia exacta, variante o especialización |
| **Transferible** | Evidencia laboral de una capacidad útil para lo que se pide, ejercida en otra función | Transferencia propuesta |
| **Académica/formativa** | La evidencia viene solo de EDU, ACA o FOR | Cualquiera, en contexto académico |
| **Insuficiente** | 02 no la respalda. Motivo: **límite documentado** (p. ej., un curso introductorio frente a «experiencia profesional en X») o **no documentado** | Interés o aprendizaje |

- **Contexto de la evidencia:** la categoría depende de lo que pide el requisito. Si pide un título, el título de EDU cuenta como evidencia directa; si pide experiencia en X y X solo aparece en la tesis, es académica.
- **Varias evidencias:** se toma la más fuerte (directa > transferible > académica/formativa) y la otra se anota en el límite.
- **Años de experiencia:** se calculan con las fechas de 02 y solo en el contexto que pida el anuncio. Pasar del límite superior de un rango («2–5 years») no es una brecha.

### Núcleos

Son las dos o tres necesidades centrales del puesto, las mismas que identifica 09/CV-SINTESIS paso 1. Se eligen entre requisitos obligatorios, ambiguos y en funciones, nunca entre deseables. Cada núcleo recibe la categoría de su mejor evidencia. El detalle los muestra, para que el titular pueda corregir la elección.

### Nivel y cobertura

Se presentan como **estrellas · cobertura**, p. ej. **★★★☆☆ · 4/4, 1 solo académico**.

**Nivel**, según los núcleos:

| Estrellas | Regla |
| --- | --- |
| ★★★★★ | Todos los núcleos con evidencia directa y todos los obligatorios cubiertos |
| ★★★★☆ | Todos los núcleos con evidencia directa, con algún obligatorio insuficiente |
| ★★★☆☆ | Todos los núcleos con evidencia laboral (directa o transferible) y al menos uno solo transferible |
| ★★☆☆☆ | Algún núcleo solo con evidencia académica o formativa, sin núcleos insuficientes |
| ★☆☆☆☆ | Algún núcleo insuficiente, pero otros con evidencia |
| ☆☆☆☆☆ | Todos los núcleos insuficientes |

Siempre se muestran las cinco posiciones, con estrellas y no con un número, para que no se confunda la dirección de la escala. Hay más de tres niveles porque es común que una vacante tenga algún obligatorio insuficiente, y los núcleos con evidencia directa pesan más que cubrir todos los obligatorios.

**Cobertura:** `X/Y`, donde Y es el número de requisitos obligatorios y ambiguos (un grupo de alternativas cuenta como uno) y X, los cubiertos con cualquier categoría salvo insuficiente. Si alguno se cubre solo con evidencia académica o formativa, se agrega `, N solo académico` (o `académicos`).

No hay puntaje sumado ni ponderaciones: los pesos serían arbitrarios, un anuncio con muchos requisitos menores diluiría el resultado y un número aislado no dice qué falta.

## EVAL-CONDICIONES — Condiciones excluyentes

Las condiciones vienen de 04, tal como el titular las declaró: un criterio de 04 que sea preferencia o que siga pendiente no excluye (04/PREF-USO). Cada condición se marca **Cumple**, **No cumple** o **Pendiente**:

| Condición (04) | No cumple si… | Cumple si… | Pendiente si… |
| --- | --- | --- | --- |
| Modalidad (PREF-MODALIDAD), solo si 04 no acepta alguna | Solo ofrece modalidades que 04 no acepta | Ofrece alguna modalidad que 04 acepta | No publica la modalidad |
| Ubicación presencial o híbrida (PREF-UBICACION, PREF-MODALIDAD) | Ninguna sede está en la región de 04, exige más días presenciales que el máximo de 04, o exige reubicarse y 04 no lo acepta | Alguna sede está en la región de 04, con una asistencia dentro del máximo | La ubicación es demasiado general, no se publica o nombra una división de 04 sin nombrar una localidad aceptada |
| Remoto (PREF-UBICACION) | El alcance del remoto de 04 no cubre el país de la vacante, o la vacante se restringe a países o regiones que excluyen trabajar desde la residencia del titular (02 §2) | Está dentro del alcance y permite trabajar desde su residencia | Dice solo «Remote», sin país ni restricción |
| Sueldo (PREF-COMPENSACION) | El máximo publicado, llevado a la base de 04, es menor al mínimo | El mínimo publicado, llevado a la base de 04, alcanza el mínimo; se anota aparte si supera el objetivo | No se publica, el rango incluye el mínimo, no se puede llevar a la base de 04 sin suponer nada o no está claro qué incluye |
| Duración (PREF-CONTRATACION) | Es una duración que 04 no acepta | Es una duración que 04 acepta | No se aclara; «full-time» describe la jornada, no la duración |
| Relación (PREF-CONTRATACION) | Es una relación o un intermediario que 04 no acepta | Es una relación aceptada, directa o con un intermediario aceptado | No se aclara |
| Horario (PREF-JORNADA) | Exige días, guardias o turnos que 04 no acepta, o en remoto una jornada fuera de su ventana | El horario está dentro de lo que acepta 04 | No se menciona |
| Viajes (PREF-DISPONIBILIDAD), solo si 04 les pone un límite | Exige viajes por encima del límite | No exige viajes o están dentro del límite | Menciona viajes sin frecuencia ni duración |
| Tipo de puesto (PREF-TIPOS), solo si 04 excluye alguno | Es de un tipo excluido, por el título o el anuncio | Ni el título ni el anuncio lo indican | — |

- **Tipo de puesto:** se reconoce con los términos que 04 anota para cada tipo; manda esa lista. Estas señales sirven para llenarla en prácticas y puestos para recién egresados: intern, internship, practicante, becario, pasante, trainee, new grad, new college grad, NCG o recién egresado en el título o el anuncio, y el requisito de estar inscrito como estudiante o de haber egresado hace poco.
- **Viajes sin límite en 04:** no son condición; solo se anotan si el anuncio los menciona.
- **Montos:** se comparan según 04/PREF-COMPENSACION («Cómo comparar»).
- **Resultado:**
  - **Excluida:** alguna condición no cumple. La evaluación se detiene y no se calcula el encaje, salvo que el titular lo pida.
  - **Sin exclusiones:** se continúa y se listan los pendientes. Un pendiente no impide postular: el titular lo aclara en el proceso.

## EVAL-ANTIGUEDAD — Tiempo publicada

Dimensión aparte: no modifica el encaje ni las condiciones. Se calcula al armar la tabla, con la fecha de ese día y la fecha más antigua conocida de la vacante:

| Dato disponible | Se muestra |
| --- | --- |
| `fecha_publicacion` | `N d`, contando desde la más antigua entre `fecha_publicacion` y `primera_deteccion` |
| Solo fecha relativa de la fuente («hace 3 días») | `~N d (relativa)`. No se guarda, porque 11 no admite fechas relativas. Si `primera_deteccion` es más antigua, manda esta |
| Solo `primera_deteccion` anterior al día de hoy | `≥ N d` |
| Nada | `—` |

- **Marca «antigua»:** a partir del umbral de EVAL-ACUERDOS, 20 días por defecto. Es una señal y no excluye la vacante.
- **Republicaciones:** la fecha publicada puede ser de una republicación. Con el tiempo, `primera_deteccion` corrige esto. La fecha confiable de cada empresa se define en su ficha de 06 y en 07.

## EVAL-PREGUNTAS — Preguntas prioritarias

**A. Para el titular.** Solo cuando pregunta por una vacante y antes de entregar el detalle:

- Se pregunta por hechos que no están en 02, solo si la respuesta puede cambiar el nivel, la cobertura o el conteo de requisitos «solo académicos». Si no cambiaría nada, no se pregunta.
- Todas las preguntas van en un solo bloque, ordenadas por impacto.
- Las respuestas valen para el resto de la sesión y se juntan, con fecha, como **propuestas para 02**. No se recalculan otras vacantes salvo que el titular las pida.

**B. Para aclarar en el proceso:** las hace el titular, nunca el agente. Incluyen las condiciones pendientes y los requisitos ambiguos que sean núcleo o estén marcados como insuficientes. Van en el detalle.

## EVAL-INFORME — Tabla resumen y detalle

### Tabla resumen

Es lo que se entrega tras una búsqueda. Se ordena por estrellas y, con empate, la vacante más nueva va primero. Las excluidas van al final, con su motivo:

| Vacante | Encaje | Antigüedad | Alertas |
| --- | --- | --- | --- |
| [Job ID — título](URL) | ★★★☆☆ · 4/4, 1 solo académico | 18 d | — |
| [Job ID — título](URL) | ★☆☆☆☆ · 10/12, 2 solo académicos | 12 d | Insuficiente: núcleo A · Académica: núcleo B |
| [Job ID — título](URL) | ★★★☆☆ · 8/10 | 19 d | Pendiente: remoto |
| [Job ID — título](URL) | — | 25 d · antigua | **Excluida:** duración «6-month contract» |

**Alertas:** solo lo que puede pesar en la decisión de postular.

- **Sin exclusiones:** los núcleos `Insuficiente` y luego los `Académica/formativa`, con el nombre guardado en `nucleos` y separados por `;`. Después, los pendientes que no sean sueldo, duración, relación ni horario (como modalidad, ubicación, remoto o viajes), porque esos cuatro casi nunca se publican y quedan pendientes en casi todas. Si no hay nada, `—`.
- **Excluida:** el motivo, con la condición y el texto literal.
- Los núcleos directos y transferibles, y los cuatro pendientes habituales, se ven en el detalle.

Debajo de la tabla, una línea: «N sin relación con las familias de 05: no evaluadas».

**Registro en `informes` (11):** al final del registro de la búsqueda (07/BUS-REGISTRO), una fila por vacante de la tabla, en su orden, con `busqueda_id`, `vacante_id` y la `evaluacion_id` que se muestra. Encaje, antigüedad y alertas no se guardan: los calcula la herramienta de 11/REG-LOCAL, con el mismo formato de esta tabla. La línea de no evaluadas no se guarda.

**Consultarla después,** la tabla no se rehace:

- **En Code:** `informe` de la herramienta de 11/REG-LOCAL da la tabla de una búsqueda ya calculada, y `leer` las filas del detalle de una vacante: la de `vacantes`, la de su `ultima_observacion_id`, la evaluación que muestra la tabla y sus requisitos en `habilidades_vacante`, cuyo conjunto vigente es el de la última observación analizada (11/REG-IDENTIDAD).
- **En Web:** la instantánea (11/REG-INSTANTANEA) trae la tabla de las últimas búsquedas en `informes.md` y el detalle de cada vacante evaluada no cerrada en `vacantes.md`, con su antigüedad a la fecha de exportación.
- **Límite:** el texto del anuncio no se guarda (11/REG-DECISIONES), así que el detalle sale de los requisitos registrados.

### Detalle

Se entrega solo cuando el titular pregunta por una vacante y, si hacía falta, después de resolver las preguntas A:

1. **Encabezado:** empresa, Job ID, título, enlace, ubicación literal (con el lugar de la región de 04 que le corresponde, si aplica), modalidad literal, fecha de publicación, antigüedad y familia de 05.
2. **Encaje** y **condiciones**, en dos líneas: el encaje como en la tabla; las condiciones completas, `Sin exclusiones · pendientes: …` con todos los pendientes, o `Excluida: …`.
3. **Núcleos:** núcleo, categoría, evidencia y límite.
4. **Requisitos:** tabla completa con requisito literal, tipo, categoría, evidencia y límite.
5. **Para el CV (09):** núcleos y evidencias a destacar, y qué presentar solo como formación. Es la entrada de CV-SINTESIS paso 1; la tabla de requisitos sirve como base de CV-TRAZA.
6. **Para aclarar en el proceso** (EVAL-PREGUNTAS B).

Requisitos en el idioma del anuncio; lo demás en español.

## EVAL-REGISTRO — Pestaña `evaluaciones`

El esquema está en 11. Sirve para no volver a evaluar una vacante que reaparece en otra búsqueda.

- **Una fila por evaluación,** incluidas las excluidas. No se registran las vacantes no evaluadas por no tener relación con las familias de 05.
- **Reutilización:** una vacante que reaparece usa su última evaluación si la observación evaluada sigue teniendo el conjunto vigente de habilidades (11/REG-IDENTIDAD) y si `version_perfil` y `version_evaluacion` son iguales o posteriores a «Evaluaciones vigentes desde» de 02 y de 08, respectivamente. Las versiones se comparan número por número (1.10 es posterior a 1.9). Si 04 cambió después de `fecha_evaluacion`, se reevalúan las condiciones. Si algo cambió, se agrega una fila nueva.
- **Aclaraciones:** si las preguntas A cambian el resultado, se actualiza la misma fila; git conserva la versión anterior (11/REG-LOCAL, «Historial y respaldo»).
- **Núcleos:** el detalle de una vacante evaluada antes usa los núcleos guardados en `nucleos`, para no contradecir las estrellas guardadas.
- **No se guardan** las categorías por requisito (el detalle las regenera con `habilidades_vacante` y 02), la familia ROL, la antigüedad (se calcula) ni notas.

## EVAL-PENDIENTES

Dudas del titular sobre el método, como si la escala distingue bien sus vacantes, con `EVAL-P##` y su tratamiento. Al resolverse, salen de la tabla; si cambian un valor por defecto, se anotan en EVAL-ACUERDOS.

| ID | Pendiente | Tratamiento |
| --- | --- | --- |
