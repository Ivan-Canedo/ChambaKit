# ChambaKit

Plantilla de instrucciones, módulos y herramientas para que Claude apoye la búsqueda laboral de una persona: perfil, CV, búsqueda, evaluación de vacantes y tendencias.

## Personas y repositorios

**Titular**:
La persona que busca trabajo y usa su copia de ChambaKit con sus propios datos.
_Avoid_: usuario, candidato

**Mantenedor**:
Quien desarrolla y publica la plantilla.
_Avoid_: usuario, autor

**Plantilla**:
El repositorio público de ChambaKit, sin datos de ningún titular.
_Avoid_: template, repo base

**Copia**:
El repositorio privado de un titular, creado desde la plantilla y llenado con sus datos.
_Avoid_: fork, clon

**Versión de la plantilla**:
Una publicación numerada de la plantilla (1.0, 1.1…). Cada copia anota de cuál salió o a cuál se actualizó por última vez.
_Avoid_: release, versión del módulo

**Actualización**:
Llevar a una copia los cambios de una versión más nueva de la plantilla, conservando lo que escribió el titular.
_Avoid_: migración, sincronización, merge

## Uso

**Canal**:
Dónde se usa ChambaKit: Code (Claude Code sobre la copia) o Web (un proyecto de claude.ai).
_Avoid_: modo, entorno

**Hoja de registros**:
La hoja de Google donde viven las búsquedas, vacantes, observaciones, evaluaciones y documentos del titular.
_Avoid_: base de datos, spreadsheet

**Modo local**:
La forma de usar ChambaKit sin conectar Google: los registros viven en un archivo de la copia y solo funciona el canal Code.
_Avoid_: modo offline, sin conexión

## Búsqueda

**Plataforma de reclutamiento**:
El sistema que aloja el portal de empleo de una empresa, como Workday, Eightfold o SmartRecruiters.
_Avoid_: ATS, portal

**Adaptador**:
La parte del script de búsqueda que sabe leer una plataforma de reclutamiento; cada empresa que la usa solo aporta su configuración.
_Avoid_: adaptador por empresa, scraper
