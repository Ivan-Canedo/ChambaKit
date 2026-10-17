# 03 — CV base

**Versión:** 1.0 — 2026-10-17 — Plantilla inicial.
**Estado:** esqueleto de la plantilla. El paso 6 de `/configurar` (CV base) redacta el CV desde 02 y reemplaza CV-ES y CV-EN.
**Fuente de trayectoria:** `02_PERFIL_MAESTRO.md`, versión «pendiente».

## CV-USO — Responsabilidad

Es una selección editorial del maestro. No sustituye el inventario completo de trayectoria ni es una adaptación a una vacante.

CV-ES y CV-EN tienen contenido equivalente y el formato literal que lee `herramientas/generar_cv.py` (09/CV-HERRAMIENTAS): `###` por sección, negritas y viñetas. Todo lo que va dentro de esas dos secciones sale en el CV, así que las notas van fuera de ellas. Los identificadores `[CV-E##]` van al final de la línea o viñeta que respaldan, remiten a CV-TRAZABILIDAD y el script los retira. La longitud de este archivo no representa páginas del CV exportado.

Mientras CV-ES y CV-EN sean el esqueleto de la plantilla, solo muestran el formato y permiten comprobar la instalación generando un CV de prueba: no son datos de nadie. El paso 6 de `/configurar` borra este párrafo al redactar el CV.

## CV-DECISIONES — Acuerdos del titular

Acuerdos editoriales del titular sobre la base (enfoque, orden, qué incluir u omitir), con ID `CV-U##` y fecha. Un acuerdo que reemplaza a otro lo dice.

| ID | Fecha | Decisión |
| --- | --- | --- |

**Acuerdos por defecto** (el titular puede cambiarlos; el cambio se anota en la tabla):

- **Enfoque:** «pendiente». Lo acuerda el paso 6 con el titular, a partir de sus familias de roles (05).
- **Estructura:** encabezado, perfil profesional, experiencia profesional, habilidades, educación e idiomas. Formación complementaria, proyectos o publicaciones van en secciones propias si aportan. Varias funciones en un mismo empleo van dentro de ese empleo, no como empleos distintos.
- **Cargo y título:** el cargo contractual va tal cual en la experiencia, y el título descriptivo en el encabezado, por separado.
- **Fechas:** mes y año en los empleos; solo el año en los estudios.

## CV-REGLAS — Fidelidad del contenido

- Separar experiencia laboral, académica, formación, desarrollo en curso e intereses. Lo aprendido en cursos o estudios no es experiencia profesional, y una formación antigua no se presenta como experiencia actual.
- Ni el cargo ni el título llevan un seniority que el titular no tenga. Aspirar a un nivel no permite agregarlo al cargo actual.
- El contacto es el que 02 registra como vigente y confirmado por el titular; no se toma de un CV anterior.
- **Términos:** las plataformas de reclutamiento permiten buscar términos dentro de los CV ([Greenhouse — Search resumes for keywords](https://support.greenhouse.io/hc/en-us/articles/115004600186-Search-resumes-for-keywords), consultado el 2026-10-11). Se nombran las tecnologías pertinentes junto con la actividad realizada, sin acumular términos. No se prometen resultados en esas plataformas ni en lecturas por IA.
- No atribuir la autoría de herramientas recibidas ni el mérito del trabajo de otros. Distinguir lo que el titular diagnosticó, propuso o hizo de lo que implementó otro equipo.
- Una cifra dice solo lo que mide: no convertir volumen (líneas de código, tickets, horas) en impacto, una correlación en causa ni un proyecto en pruebas en un despliegue. No inventar ahorros, cobertura ni adopción. Una cifra que se presta a malas lecturas se omite del CV y se conserva en 02.
- Usar descripciones funcionales generales, sin nombres internos ni información que el empleador no haya autorizado divulgar.
- Lo que el titular declaró confidencial en 02 no se nombra ni se insinúa: solo se usa la formulación que acordó.
- Las condiciones de 04 (sueldo, contratación, horario) no van en el CV público.
- Al cambiar un hecho o su alcance, actualizar ambos idiomas. Revisar los datos de actualidad antes de una candidatura (02, regla 10).

## CV-ES — Borrador en español

### Encabezado

**Nombre Apellido**  
**Título descriptivo del perfil**  
Ciudad, País · <nombre@example.com> · +00 000 000 0000

### Perfil profesional

Síntesis general de tres o cuatro frases: especialidad, capacidades respaldadas y aportaciones que explican el perfil.

### Experiencia profesional

**Empresa — Cargo contractual**  
Ciudad, País · Mes de AAAA–actualidad

- Responsabilidad principal: actividad, objeto técnico y resultado respaldado.
- Aportación concreta, con el alcance que registra el perfil maestro.
  - Ejemplo subordinado a la viñeta anterior.

**Empresa anterior — Cargo contractual**  
Ciudad, País · Mes de AAAA–mes de AAAA

- Responsabilidad o aportación pertinente.

### Habilidades

- **Grupo de habilidades:** herramientas y prácticas, con su contexto.
- **Otro grupo:** herramientas y prácticas, con su contexto.

### Educación

**Título del grado** — Institución, AAAA.

### Idiomas

**Español:** nivel o uso.  
**Inglés:** nivel o uso.

## CV-EN — English draft

### Header

**First Last**  
**Descriptive profile title**  
City, Country · <name@example.com> · +00 000 000 0000

### Professional summary

General summary in three or four sentences: specialty, supported capabilities, and contributions that explain the profile.

### Professional experience

**Company — Contractual job title**  
City, Country · Month YYYY–present

- Main responsibility: activity, technical object, and supported result.
- Specific contribution, within the scope recorded in the master profile.
  - Example subordinate to the previous bullet.

**Previous company — Contractual job title**  
City, Country · Month YYYY–Month YYYY

- Relevant responsibility or contribution.

### Skills

- **Skill group:** tools and practices, with their context.
- **Another group:** tools and practices, with their context.

### Education

**Degree title** — Institution, YYYY.

### Languages

**Spanish:** level or use.  
**English:** level or use.

## CV-OPCIONALES — Ampliaciones y límites

Hechos de 02 que no entraron en la base pero pueden servir en una adaptación: versiones ampliadas de un bloque, en ES y EN con su `[CV-E##]`, y contenidos sin seleccionar, cada uno con su localizador de 02 y su límite. No se duplican en el CV de envío. Las traducciones de grados y formación son descriptivas, no denominaciones oficiales. Omitir algo no equivale a declarar falta de experiencia.

«pendiente»

## CV-TRAZABILIDAD — Correspondencia con el maestro

Cada `[CV-E##]` de CV-ES y CV-EN tiene una fila: los hechos que selecciona, su localizador en 02 (sección o ID, y fuentes F y U) y el límite que la redacción respeta.

| ID | Hechos seleccionados | Localizador en 02 / límite |
| --- | --- | --- |

## CV-PENDIENTES

Lo que falta decidir o revisar sobre la base, con ID `CV-P##`. Al resolverse, sale de la tabla y pasa a una línea de resueltos, con su fecha.

| ID | Pendiente | Tratamiento |
| --- | --- | --- |
