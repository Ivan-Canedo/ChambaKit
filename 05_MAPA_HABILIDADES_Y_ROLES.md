# 05 — Mapa de habilidades y roles

**Versión:** 1.0 — 2026-10-17 — Plantilla inicial.
**Estado:** plantilla sin llenar. El paso 5 de `/configurar` (Habilidades y roles) construye la matriz de evidencias y las familias de roles desde 02 y 04.

## HAB-USO — Responsabilidad

Relaciona habilidades, sinónimos, especialidades y familias de puestos para descubrir y comparar oportunidades. Organiza relaciones con la trayectoria, pero no redefine el inventario del maestro (02 §10) ni acredita compatibilidad con una vacante por su título.

Las familias son agrupaciones descriptivas propuestas, construidas solo con fuentes internas (02 y 04). No son denominaciones verificadas en el mercado.

## HAB-REGLAS — Interpretación

- Distinguir coincidencia exacta, sinónimo, transferencia propuesta e interés de aprendizaje.
- La experiencia académica o formativa en una técnica no es ejercicio profesional de ella, y un repaso o un curso introductorio no es dominio laboral.
- No derivar la profesión del catálogo de empresas. Los términos propios de una empresa van en su ficha de 06; el método común no depende de ninguna.
- Separar las habilidades pedidas en anuncios de las que posee el titular.
- Reservar «brecha» para una diferencia sustentada frente a un requisito concreto; un dato no documentado es pendiente.
- Una aspiración de nivel (04) no acredita seniority ni se aplica a todas las rutas. No asignar niveles por años, autonomía o nombres de herramientas.
- Una relación técnica favorable no demuestra que se cumplan las condiciones de 04.

## HAB-CRITERIOS — Dirección acordada

Las rutas profesionales y sus criterios están en `04_PREFERENCIAS_LABORALES.md` (PREF-FUNCIONES) y aquí no se repiten. Esta sección cita por su `PREF-U##` cada criterio de 04 que cambia las familias, como qué tan cerca de su experiencia debe estar un cambio de carrera, y anota cómo se aplica a ellas.

«pendiente»

## HAB-RELACIONES — Tipos de relación

| Relación | Uso | Límite |
| --- | --- | --- |
| Coincidencia exacta | Mismo término y aplicación compatible | El nombre de un lenguaje o herramienta no acredita cualquier especialidad que lo use |
| Variante o sinónimo contextual | Otra forma de nombrar el mismo concepto en el contexto documentado | Una sigla puede significar otra cosa en otra fuente: usar la expansión de cada anuncio |
| Especialización | Concepto específico dentro de uno amplio | No se extiende al concepto amplio completo ni a sus otras especialidades |
| Transferencia propuesta | Capacidad útil en otra función, sin haberla ejercido | Nunca es coincidencia exacta |
| Interés o aprendizaje | Ruta deseada o actualización en curso | No es una competencia nueva |

Una habilidad puede tener relaciones distintas según el requisito.

## HAB-EVIDENCIAS — Núcleos con respaldo en el maestro

Cada núcleo `HAB-##` agrupa habilidades que la trayectoria muestra juntas. El contexto es el de 02 (laboral, académico, formativo o independiente) y no se sube: lo académico no pasa a laboral. Los localizadores remiten a `02_PERFIL_MAESTRO.md` (EXP, PRY, EDU, ACA, FOR, IND o una sección, como §10) y no son nuevas verificaciones de las fuentes originales. El límite copia o resume el de 02, sin suavizarlo.

| ID | Núcleo | Contexto y evidencia | Límite |
| --- | --- | --- | --- |
| «pendiente» | | | |

Las habilidades de 02 que no forman un núcleo, como un antecedente formativo aislado, se anotan en una línea bajo la tabla, con su localizador.

## HAB-ROLES — Familias de roles

Una o más familias `ROL-##` por cada ruta de 04/PREF-FUNCIONES: la función de la ruta y, si las evidencias lo justifican, funciones vecinas por transferencia. La cercanía describe el respaldo de las actividades, no la probabilidad de contratación ni el nivel de entrada. Las familias deciden qué vacantes se evalúan (08/EVAL-FLUJO).

| ID | Familia | Ruta de 04, base y relación | Qué revisar al concretarla |
| --- | --- | --- | --- |
| «pendiente» | | | |

No agregar familias fuera de las rutas de 04 solo porque el maestro tenga habilidades relacionadas.

## HAB-VOCABULARIO — Base interna

Términos del perfil que los anuncios pueden escribir de otra forma: siglas, variantes, traducciones, y también términos parecidos que no son sinónimos.

| Término en el perfil | Relación | Precaución |
| --- | --- | --- |
| «pendiente» | | |

Los títulos en inglés, las traducciones de familias y las equivalencias entre empresas se verifican con fuentes externas primarias, registrando término literal, significado, fuente, fecha y relación. Es una consulta terminológica, no una búsqueda de empleo. Una coincidencia en un anuncio no demuestra uso universal ni demanda. Lo que falte verificar queda como `HAB-P##`.

## HAB-APLICACION — Uso por otros módulos

1. **Explorar una función:** relacionar sus actividades con HAB-EVIDENCIAS y HAB-ROLES, conservando el vínculo al maestro y sus límites.
2. **Analizar un anuncio:** separar el requisito literal, la habilidad normalizada, la relación propuesta y la evidencia personal. Si falta información, dejarla pendiente.
3. **Condiciones y evaluación:** las condiciones se revisan en 04 y la evaluación en 08. Este mapa no puntúa ni descarta.
4. **Registros:** la pestaña `habilidades_vacante` de los registros (ver 11) guarda la demanda observada sin IDs HAB. La relación con la evidencia personal se hace en la evaluación (08); las familias ROL sirven para filtrar en la búsqueda (07).

## HAB-PENDIENTES

Lo que falta verificar o precisar, con `HAB-P##` y su tratamiento. Al resolverse, sale de la tabla y pasa a una línea de resueltos.

| ID | Pendiente | Tratamiento |
| --- | --- | --- |

## HAB-FUENTES

| ID | Fuente | Alcance |
| --- | --- | --- |
| HAB-C01 | `02_PERFIL_MAESTRO.md`, versión «pendiente» | Trayectoria y límites, con los localizadores de HAB-EVIDENCIAS |
| HAB-C02 | `04_PREFERENCIAS_LABORALES.md`, versión «pendiente» | Rutas (PREF-FUNCIONES) |

Las declaraciones del titular al revisar este mapa se agregan a la tabla como `HAB-U##`, con fecha. Si cambian una ruta o una condición, van a 04 como `PREF-U##`.
