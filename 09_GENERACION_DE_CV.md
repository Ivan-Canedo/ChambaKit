# 09 — Generación de CV

**Versión:** 1.1 — 2026-10-18 — El canal Web necesita Claude; el archivo se genera en el canal Code con cualquier agente.
**Estado:** método de la plantilla, con el diseño por defecto. El color del CV es un dato del titular (CV-PLANTILLA).

## CV-ALCANCE — Responsabilidad

Adaptar el contenido a una vacante y producir el formato solicitado que se pueda generar y comprobar en la sesión. Este módulo define el procedimiento y la presentación; no guarda otra copia de la trayectoria. El contenido parte de `03_CV_BASE.md`, cuya síntesis general ya sigue CV-SINTESIS, y de `02_PERFIL_MAESTRO.md`. El exportador es `herramientas/generar_cv.py` (CV-HERRAMIENTAS).

## CV-ACUERDOS — Reglas y decisiones del titular

**Reglas:**

- **Formato de entrega:** se decide para cada vacante, según la convocatoria; ni PDF ni DOCX es el habitual.
- **Fidelidad:** seleccionar y redactar sin inventar, y distinguir experiencia laboral, académica, formación, intereses y trabajo en curso (00, reglas 1 y 2; 03/CV-REGLAS).
- **Base y adaptación:** la base de 03 conserva el orden acordado con el titular. Una adaptación puede proponer otra selección u otro orden, explicando el cambio, sin modificar la base.
- **CV en uso:** los CV que el titular va a usar se guardan en `muestras_cv/`, con su fuente Markdown y sus notas de trabajo (CV-MUESTRAS), y se registran en `documentos` solo si los va a usar.

**Decisiones del titular:** cada valor ajustable de CV-PLANTILLA que el titular cambie se anota aquí, con ID `GEN-U##` y fecha. El color no se anota: su única autoridad es el bloque de configuración de CV-PLANTILLA.

| ID | Fecha | Decisión |
| --- | --- | --- |

## CV-ENTRADAS — Recursos y datos mínimos

**Recursos (registrar las versiones usadas):**

- **02:** autoridad de hechos, fuentes y límites.
- **03:** CV-ES, CV-EN, CV-OPCIONALES y CV-TRAZABILIDAD.
- **Descripción de la vacante:** empresa, título, Job ID si existe, ubicación literal, requisitos y fuente con fecha. Si el titular pega el texto, marcarlo como aportado por él; no inventar URL ni verificación oficial.
- **Evaluación (08):** el detalle de la vacante (EVAL-INFORME): núcleos, requisitos con tipo, categoría, evidencia y límite, y el apartado «Para el CV». Si la vacante no tiene detalle, hacerlo con 08 antes de adaptar; no inventar un nivel ni categorías para poder adaptar.
- **04:** solo para revisar condiciones; no pasa al CV.
- **Registros, pestaña `documentos` (11):** para registrar el documento generado.

**Antes de redactar:** precisar idioma, formatos aceptados, límite de páginas o tamaño y propósito. Resolver primero lo que indiquen la convocatoria y el encargo, y preguntar solo lo que falte.

**Si falta información:**

- **Descripción de la vacante:** pedirla. Un borrador por familia de puesto se identifica como tal.
- **Dato personal determinante:** consultar 02; si no está, preguntar o dejar la afirmación fuera.
- **Dato pendiente:** no significa falta de capacidad.

## CV-FLUJO — Adaptación

1. **Delimitar el encargo:** vacante, evidencia, idioma, formato y restricciones. La vigencia es otra dimensión: redactar a partir de un anuncio no prueba que siga abierto.
2. **Relacionar requisitos con hechos:** partir del detalle de 08, después de comprobar que su evaluación sigue vigente (08/EVAL-REGISTRO); si no, rehacerla. Sus núcleos son las necesidades centrales de CV-SINTESIS paso 1, y su tabla de requisitos (tipo, categoría, localizador de 02 y límite) es la base de CV-TRAZA. Los tipos de requisito y las categorías de evidencia son los de 08.
3. **Seleccionar el contenido:** priorizar lo pertinente y revisar CV-OPCIONALES y 02 antes de descartar algo. Proponer los cambios de énfasis y orden respecto de la base. Omitir por espacio no niega la experiencia.
4. **Redactar:** escribir primero la experiencia y al final la síntesis (CV-SINTESIS). Cada frase indica actividad, objeto técnico y contribución o resultado respaldado. Los términos de la vacante se usan solo si describen hechos reales. Un resultado cualitativo basta; no inventar métricas. Separar el cargo contractual del título descriptivo, sin agregar seniority.
5. **Revisar fidelidad:** contrastar con las fuentes y explicar los cambios relevantes. Los hechos nuevos se proponen para 02 con fuente y fecha; no se sobrescribe al adaptar.
6. **Presentar y exportar:** escribir el CV adaptado en Markdown con el formato de 03 y generar PDF y DOCX con CV-PLANTILLA (CV-HERRAMIENTAS). Si excede la extensión de CV-PLANTILLA, compactar como indica ahí y repetir. No prometer formatos que no se puedan generar en el canal.
7. **Comprobar y entregar:** aplicar CV-CONTROLES al archivo exacto y entregar con una nota breve de cambios y limitaciones. Si el titular lo va a usar, guardarlo en `muestras_cv/` y registrarlo en `documentos` (CV-ACUERDOS).

Se puede trabajar el contenido aunque falten presentación o contacto; un borrador incompleto se identifica como borrador.

## CV-SINTESIS — Perfil profesional por vacante

**Regla:** redactar el perfil profesional para cada vacante, a partir de su descripción y de la evidencia seleccionada. La síntesis de la base es un punto de partida: no copiarla ni limitarse a insertar palabras clave. Sin vacante, identificarla como síntesis general.

**Elaboración:**

1. Identificar las dos o tres necesidades centrales del puesto y los hechos de 02 que mejor las respaldan. No atribuir habilidades por cercanía de términos, interés de aprendizaje o título de la vacante.
2. Escribir la experiencia primero y después la síntesis: especialidad pertinente, capacidades respaldadas y aportaciones que expliquen el encaje. Cambiar énfasis u orden solo cuando la vacante lo justifique; adaptar no exige cambios cosméticos.
3. Dar espacio en proporción a la pertinencia y la profundidad de la evidencia. Que un dato sea verdadero o una tecnología sea reciente no le da protagonismo; los detalles de actividades van en experiencia o habilidades.
4. Usar lenguaje técnico directo. Evitar adjetivos promocionales, acumulación de tecnologías, frecuencias que no aporten y fórmulas genéricas. No inflar verbos: «revisó» no autoriza «definió», «diseñó» ni «lideró».
5. Pauta: un párrafo de tres o cuatro frases breves, ajustado al contenido. No sacrificar matices necesarios por un conteo de palabras.

**Revisión de cada frase (en notas de trabajo, fuera del CV):**

- **Pertinencia:** qué necesidad del puesto responde o, en una síntesis general, qué eje profesional presenta.
- **Evidencia:** localizador de 02 o CV-E## que la sustenta, con contexto y estado en curso cuando aplique.
- **Proporción:** el énfasis corresponde a la profundidad real. No presentar aprendizaje o una actividad acotada como especialidad.
- **Precisión:** cada verbo, calificativo y término tiene función clara, sin exagerar.
- **Economía:** sin repeticiones ni detalles secundarios; se lee de corrido y concuerda con el resto del CV.

## CV-TRAZA — Notas de trabajo de cada adaptación

**Qué conservar, fuera del CV público:**

- **Vacante:** identidad, y procedencia y fecha de la descripción.
- **Versiones:** de 02, 03 y este módulo, más la evaluación y las evidencias consultadas.
- **Documento:** idioma, formato, versión y fecha.
- **Correspondencia:** cada afirmación con su CV-E## o localizador de 02, y los límites relevantes.
- **Cambios:** respecto de la base, omisiones relevantes y preguntas pendientes.

| Requisito de la vacante | Hecho y localizador | Contexto y límite | Tratamiento en el CV |
| --- | --- | --- | --- |

**Límites:**

- Fuentes internas, IDs editoriales, notas y preguntas nunca van en el documento de candidatura.
- Citar un documento ausente no acredita haberlo consultado.

## CV-CONTROLES — Antes de entregar

**Contenido:**

- Aplicar CV-SINTESIS al párrafo inicial y guardar la revisión en notas de trabajo.
- Toda afirmación tiene respaldo. Nombres, periodos, grados, cargo y contribuciones conservan su alcance. Revisar los datos de actualidad según la fecha de su fuente.
- Un documento listo para envío necesita el contacto actual confirmado en 02; no tomarlo de un CV anterior.
- Respetar los límites de 03/CV-REGLAS y los que 02 anota en cada hecho, incluida la información que el titular declaró confidencial.
- Revisar la divulgación externa: sin nombres internos no autorizados.
- Si hay dos idiomas, comparar hechos, fechas y límites. Las traducciones de grados no son denominaciones oficiales.
- Retirar marcadores, notas internas y afirmaciones sin resolver.

**Presentación y archivo:**

- Comprobar que el archivo existe y abre, su formato real y los requisitos de la convocatoria.
- Revisar visualmente todas las páginas: cortes, desbordes, legibilidad, saltos, espacios y consistencia. No comprimir hasta volverlo ilegible.
- Revisar el texto extraíble y su orden: nombre, contacto, encabezados, experiencia, fechas, tecnologías y caracteres especiales. Compararlo con el contenido aprobado. El script lo hace palabra por palabra y avisa («revisar») si un compuesto con guion queda partido al final de una línea: `pdftotext` lo une sin guion («state-of-theart») y una plataforma de reclutamiento podría hacer lo mismo al leer el CV.
- Evitar palabras solas al final de un párrafo cuando se busca ganar espacio; no es una falla.
- DOCX: convertirlo de nuevo a PDF y comparar páginas y texto. Sus viñetas se guardan como el carácter de viñeta de Word (fuente Symbol), que se extrae como un carácter privado; no es una falla.
- En entregas para formularios, revisar límites de caracteres y legibilidad al copiar.
- Distinguir comprobación satisfactoria, fallo detectado y comprobación no realizada. Si una herramienta impide revisar algo, decirlo.
- Repetir los controles afectados si cambia el contenido o la exportación.

Estos controles verifican fidelidad y presentación; no garantizan cómo lo lea una plataforma de reclutamiento, la selección ni la contratación.

## CV-ENTREGA

Entregar el borrador o los archivos que efectivamente existan, con idioma, formato y versión, y una nota breve de lo adaptado, los pendientes y los controles hechos o no disponibles. Generar un CV no autoriza postular, enviar mensajes ni subir documentos a una empresa.

## CV-HERRAMIENTAS — Generación y comprobación por canal

| Canal | Generación | Comprobación | Estado |
| --- | --- | --- | --- |
| **Code** | LibreOffice sin interfaz: FODT → PDF y FODT → DOCX | `pdftotext` (texto y orden), `pdftoppm` (vistas PNG para revisar), `pdfinfo` (páginas, tamaño) y `pdffonts` (fuentes incrustadas), de poppler | **Probado en Linux.** El paso 6 de `/configurar` instala LibreOffice, poppler y la fuente Carlito |
| **Web** (proyecto en claude.ai; necesita Claude) | No comprobado | No comprobado | El contenido se puede adaptar en la web y el archivo se genera en Code |

No hacen falta pandoc, python-docx ni reportlab.

**Script `herramientas/generar_cv.py`** (local, no se sube al proyecto):

```text
python3 -I herramientas/generar_cv.py ENTRADA.md --idioma es|en --salida RUTA/NOMBRE
```

- **Entrada:** `03_CV_BASE.md` (toma CV-ES o CV-EN) o un CV adaptado con el mismo formato: `###` por sección, `**negritas**`, viñetas con `-` seguido de un espacio y subviñetas con dos espacios de sangría. Los marcadores `[CV-E##]` se retiran solos, así que la fuente adaptada puede conservarlos para la traza. Los correos y URL van entre `<>` (Markdown estándar); el script quita los picos.
- **Secciones con formato propio:** el script reconoce dos por su nombre exacto.
  - **«Encabezado» o «Header»:** la primera línea solo en negritas es el nombre; la segunda, el título descriptivo; las demás, el contacto. La sección no imprime su título.
  - **«Experiencia profesional» o «Professional experience»:** una línea solo en negritas es un puesto, y la línea que la sigue, su lugar y periodo.
- **Color:** sale del bloque de configuración de CV-PLANTILLA. Si este módulo no lo tiene o el color no es `#RRGGBB`, el script se detiene con un mensaje y no genera nada.
- **Salida:** FODT, PDF, DOCX, vista PNG por página y TXT extraído.
- **Informe:** páginas, palabras, fuentes incrustadas, coincidencia palabra por palabra del texto extraído con el contenido y avisos de compuestos partidos. Si el texto no coincide, termina con error.
- **Nombre del archivo:** `CV_<Nombre>_<Apellido>_<ES|EN>_<Empresa>_<JobID>_<fecha>_v<NN>`; para la base, `CV_<Nombre>_<Apellido>_<ES|EN>_base_<fecha>_v<NN>`.

## CV-PLANTILLA — Presentación

Todo el diseño es un valor por defecto de la plantilla, y el titular puede cambiarlo. El script lo aplica; no hay que maquetar a mano. Lo marcado «ajustable» se cambia sin tocar código: el color, en su bloque; la letra y los márgenes, con opciones del script. Lo demás, como el tamaño de página o la tipografía, se cambia editando `herramientas/generar_cv.py` en la copia. Cada cambio, salvo el del color, se anota en CV-ACUERDOS.

**Color de acento (dato del titular, ajustable):** va solo en los títulos de sección y en la línea fina bajo el contacto. El de la plantilla es un gris azulado oscuro, `#3B4A5A`. El paso 6 de `/configurar` le pregunta al titular qué color quiere y lo escribe en el bloque de abajo, que es lo que lee el script; para cambiarlo después basta editar el bloque y volver a generar. Se recomienda un tono oscuro, con un contraste de al menos 4.5:1 sobre blanco, para que se lea bien y en escala de grises no se pierda información; si el elegido no lo alcanza, se le avisa al titular y él decide.

```json
{
  "color_acento": "#3B4A5A"
}
```

- **Página:** carta y una columna. Márgenes de 1.4 cm arriba y abajo y 1.7 cm a los lados (ajustables con `--margen`).
- **Sin** tablas, cuadros de texto, encabezado ni pie de página, columnas, iconos, fotos ni barras de habilidad: dificultan la extracción (ver la evidencia de abajo). El contacto va en el cuerpo, bajo el nombre.
- **Tipografía:** Carlito, con las mismas métricas que Calibri, así que el DOCX abierto en Word conserva los saltos. Texto de 10.5 pt (ajustable con `--tam`), con interlineado del 113 %; el resto se escala con él: nombre de 19.5 pt en negrita; título descriptivo de 11.5 pt en negrita gris; contacto, ubicación y fechas de 10 pt en gris.
- **Texto:** #1A1A1A y gris #4D4D4D.
- **Jerarquía:** por tamaño, negritas y espacio. Las viñetas son listas reales («•» y «–» para el ejemplo subordinado).
- **Estructura:** la de 03 (CV-DECISIONES).
- **Tono:** el de 03, técnico y directo, sin adjetivos promocionales. La plantilla no cambia la redacción.
- **Formatos (ajustable):** PDF para enviar y DOCX como editable; el FODT es intermedio. El formato de envío se decide por vacante (CV-ACUERDOS).
- **Extensión (ajustable):** una página por candidatura; la base de 03 puede ocupar más. Dos páginas son aceptables si una obliga a quitar evidencia pertinente. Para compactar: primero se acortan o unen los bloques opcionales (proyectos, formación), después se quitan los detalles secundarios de las viñetas; ajustar las líneas que terminan con una o dos palabras ahorra espacio sin quitar hechos.

**Evidencia sobre color y diseño, consultada el 2026-10-11.** No se encontró evidencia sólida de un color ganador para CV. Atraer la mirada, facilitar la lectura, mejorar una valoración simulada y conseguir entrevistas son resultados distintos. El color se usa por identidad y legibilidad, sin prometer efectos en la contratación. Fuentes:

- [Greenhouse, *Unsuccessful resume parse*](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse): las columnas, gráficos, imágenes y el contacto en encabezados o cuadros de texto dificultan la extracción. No menciona el color tipográfico.
- [Maier et al., 2013](https://link.springer.com/article/10.1007/s11031-012-9326-1), solo el resumen: el rojo fue desfavorable en situaciones específicas de percepción. No evalúa acentos en CV.
- [Popham et al., 2017](https://journals.sagepub.com/doi/10.1177/1541931213601792), resumen: la preferencia declarada por un diseño textual no produjo un efecto fiable en la selección simulada.
- [TheLadders, 2012](https://www.bu.edu/com/files/2018/10/TheLadders-EyeTracking-StudyC2.pdf): versiones reescritas y organizadas se valoraron como más fáciles de leer. No aísla el color.
- [Huntr](https://huntr.co/research/best-resume-format): la diferencia entre paletas con y sin acento no persistió dentro de la misma persona. Es un estudio observacional comercial.

## CV-MUESTRAS — Carpeta local `muestras_cv/`

Fuera del proyecto web. markdownlint no la revisa, porque sus fuentes llevan el formato literal del script.

- **Base:** PDF y DOCX de 03 en cada idioma, con el nombre de CV-HERRAMIENTAS. Son una referencia visual, no un CV de envío.
- **CV en uso:** PDF, DOCX, fuente Markdown (`_fuente.md`) y notas de trabajo (`NOTAS_CV_…md`, con el detalle de 08, CV-SINTESIS, CV-TRAZA y CV-CONTROLES) de cada candidatura (CV-ACUERDOS).

## CV-PENDIENTES

Sin pendientes al empezar. Lo que quede por decidir o comprobar sobre la generación de CV se anota aquí, con fecha.
