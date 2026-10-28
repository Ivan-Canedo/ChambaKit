# 01 — Mapa y estado del proyecto

**Versión:** 1.5 — 2026-10-27 — El inventario describe un solo lugar de registros, el archivo de la copia.

## ESTADO — Punto de continuidad

**Versión de la plantilla:** 1.1, de <https://github.com/Ivan-Canedo/ChambaKit> — la de ChambaKit de la que salió esta copia o a la que se actualizó por última vez. En la copia, solo `/actualizar` la cambia.

**Estados:** «Sin llenar» espera el paso de `/configurar` que nombra su fila; «Configurado» ya lo pasó.

| Módulo | Versión | Estado | Siguiente paso sugerido |
| --- | --- | --- | --- |
| 00 Instrucciones | 1.4 | Sin llenar | `/configurar`, paso 8 (Registros): crea el archivo de registros |
| 02 Perfil maestro | 1.0 | Sin llenar | `/configurar`, paso 3 (Perfil maestro): extrae la trayectoria del CV actual y entrevista lo que falte |
| 03 CV base | 1.0 | Sin llenar | `/configurar`, paso 6 (CV base): redacta el CV en español e inglés desde 02 |
| 04 Preferencias | 1.0 | Sin llenar | `/configurar`, paso 4 (Preferencias): región, modalidad, sueldo y exclusiones |
| 05 Habilidades y roles | 1.0 | Sin llenar | `/configurar`, paso 5 (Habilidades y roles): matriz de evidencias y familias de roles desde 02 y 04 |
| 06 Empresas | 1.2 | Sin llenar | `/configurar`, paso 7 (Empresas): fichas de las empresas objetivo |
| 07 Método de búsqueda | 1.3 | Sin llenar | `/configurar`, paso 7 (Empresas): queda listo con la región de 04 y las fichas de 06 |
| 08 Evaluación | 1.3 | Sin llenar | `/configurar`, paso 5 (Habilidades y roles): queda listo con las condiciones de 04 y las familias de 05 |
| 09 Generación de CV | 1.2 | Sin llenar | `/configurar`, paso 6 (CV base): color del CV |
| 10 Tendencias | 1.1 | Sin llenar | `/configurar`, paso 8 (Registros): queda listo cuando existen los registros |
| 11 Esquema de registros | 1.3 | Sin llenar | `/configurar`, paso 8 (Registros): crea los registros desde este esquema |

**Orden sugerido:**

- Mientras alguna fila diga «Sin llenar», el orden lo pone `/configurar`.
- Después, 03 y 09 avanzan según se necesiten.
- Método (07) y ficha de cada empresa (06) antes de buscar en ella.
- Evaluación (08) antes de adaptar CV a vacantes.
- Tendencias (10) cuando haya muestras comparables.

La numeración no impone orden.

**Búsquedas:** viven en los registros (pestaña `busquedas` y las relacionadas). Este mapa no las registra, y una búsqueda no obliga a editar ningún módulo (07/BUS-REGISTRO).

## INVENTARIO — Qué hay en el proyecto

| Archivo | Contenido | Autoridad |
| --- | --- | --- |
| 00_INSTRUCCIONES_PROYECTO.md | Texto para el campo «Instrucciones»; no hace falta subirlo como archivo | Reglas generales y protocolos |
| 01_MAPA_DEL_PROYECTO.md | Este mapa y el estado | Estado de los módulos |
| 02_PERFIL_MAESTRO.md | Trayectoria completa, fuentes F/U y pendientes | **Trayectoria y hechos** |
| 03_CV_BASE.md | CV-ES, CV-EN, opcionales y trazabilidad | Selección editorial base |
| 04_PREFERENCIAS_LABORALES.md | Rutas, tipos de puesto excluidos, región (con su bloque de configuración), modalidad, sueldo, contratación, horario | **Condiciones deseadas** |
| 05_MAPA_HABILIDADES_Y_ROLES.md | Evidencias HAB, familias ROL y vocabulario | Relaciones habilidad–rol |
| 06_EMPRESAS_OBJETIVO.md | Catálogo, configuración por plataforma y fichas EMP-ID con su bloque de configuración | Configuración por empresa |
| 07_METODO_DE_BUSQUEDA.md | Acceso, pasos, vigencia, fechas, cobertura, comparación y registro | Método |
| 08_EVALUACION_DE_VACANTES.md | Rúbrica, condiciones, antigüedad, flujo, informe y registro de evaluaciones | Método |
| 09_GENERACION_DE_CV.md | Flujo, CV-SINTESIS, controles, plantilla y color del CV | Procedimiento y diseño de CV |
| 10_ANALISIS_DE_TENDENCIAS.md | Reglas de tendencias | Método |
| 11_ESQUEMAS_DE_REGISTROS.md | Esquema de los registros, con su bloque (REG-ESQUEMA), y cómo se crea y se usa el archivo de registros | Esquema de datos |
| Archivo de registros: `ChambaKit_Registros.xlsx` (00, «Registros») | Pestañas vacantes, observaciones, habilidades_vacante, documentos, busquedas, evaluaciones e informes. Vive en la copia y solo lo escribe el canal Code; el proyecto no lo recibe, sino su instantánea | **Datos operativos** |
| `instantanea/`: `informes.md` y `vacantes.md` | Copia en Markdown de los registros para el canal Web: las últimas 10 búsquedas con su tabla resumen y las vacantes evaluadas no cerradas. La regenera la herramienta de 11/REG-LOCAL con cada escritura; la plantilla no la trae | Vista, nunca se edita a mano (11/REG-INSTANTANEA) |

## OPERACIONES — Qué consultar

Además de las instrucciones y este mapa:

| Operación | Recursos |
| --- | --- |
| Actualizar trayectoria | 02 y fuentes disponibles |
| Ajustar objetivos o condiciones | 04 y 02 |
| Preparar el CV base | 03, 02, 04 y 09/CV-PLANTILLA |
| Relacionar habilidades y roles | 05, 02 y 04 |
| Desarrollar una empresa | 06/EMP-ID, 07 y 04 |
| Buscar y comparar vacantes | 07, 08, 04, 05, 06, 11 y los registros (vacantes, observaciones, busquedas, evaluaciones) |
| Descubrir empresas | 07, 02, 04, 05 y 06; explorar no la convierte en objetivo |
| Evaluar una vacante | 08, 02, 04, 05, la descripción fechada y los registros (habilidades_vacante, evaluaciones) |
| Adaptar o exportar un CV | 09, 02, 03, la evaluación, la vacante y los registros (documentos) |
| Analizar tendencias | 10, 05, 11 y los registros; declarar muestras y cobertura |

## FUERA DEL PROYECTO — Carpeta local

No están en el conocimiento del proyecto. Si una sesión los necesita, hay que adjuntarlos.

- **Documentos fuente de 02** (CV anteriores, el PDF de LinkedIn, constancias): se citan como fuentes F##; citarlos por nombre no da acceso a su contenido.
- **`muestras_cv/`:** CV generados, con su fuente Markdown y sus notas de trabajo (09/CV-MUESTRAS).
- **`AGENTS.md` y `CLAUDE.md`:** instrucciones para el agente que trabaja esta carpeta en el canal Code, el único lugar donde se editan los módulos. `CLAUDE.md` solo remite a `AGENTS.md`.
- **`.claude/skills/configurar/`:** la skill `/configurar`, que configura la copia paso a paso según la tabla ESTADO.
- **`.claude/skills/actualizar/` y `CAMBIOS.md`:** la skill `/actualizar`, que lleva a la copia los cambios de una versión más nueva de la plantilla sin tocar sus datos, y la lista de lo que trae cada versión. Se invoca a mano: nada avisa al abrir la copia.
- **`.agents/skills/`:** un puntero por skill, con su mismo nombre y descripción, que remite a la skill completa de `.claude/skills/`. Existen para que otros agentes, que leen esa carpeta y no `.claude/skills/` (Antigravity, Gemini CLI), encuentren `/configurar` y `/actualizar`; las skills se editan en `.claude/skills/` y el puntero solo cambia si cambia su nombre o su descripción.
- **`.markdownlint-cli2.jsonc`:** reglas de formato Markdown que se revisan en Code tras editar (AGENTS.md).
- **`herramientas/buscar.py`:** script de búsqueda del canal Code (07/BUS-ACCESO-CODE); no se sube al proyecto.
- **`herramientas/generar_cv.py`:** generador y comprobador de CV del canal Code (09/CV-HERRAMIENTAS); no se sube al proyecto.
- **`herramientas/registros.py` y `.venv/`:** la herramienta del archivo de registros y el entorno virtual de Python con que corre (11/REG-LOCAL); no se suben al proyecto.
- **`README.md`, `LICENSE`, `CONTRIBUTING.md`, `CONTEXT.md`, `docs/`, `herramientas/auditar_terminos.py` y `herramientas/pruebas/`:** presentación y licencia de la plantilla, y material de quien la mantiene; el titular no los necesita.
