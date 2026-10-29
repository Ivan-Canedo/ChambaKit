# ChambaKit

Plantilla de instrucciones, módulos y herramientas para que un agente de IA apoye la búsqueda laboral de una persona: perfil, CV, búsqueda, evaluación de vacantes y tendencias.

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
Dónde se usa ChambaKit: Code (un agente con terminal sobre la copia, sea Claude Code, Antigravity u otro, en el equipo del titular o en la nube) o Web (un proyecto de claude.ai). Los separa si se llega a los portales y a los scripts, no qué agente se usa ni dónde corre. Solo Code hace búsquedas y escribe los registros; Web consulta y hace comprobaciones puntuales.
_Avoid_: modo, entorno, Local, canal Nube

**Code local**:
El canal Code en el equipo del titular, sobre su carpeta de la copia.
_Avoid_: modo local

**Code en la nube**:
El canal Code en una sesión de Claude Code en la nube (claude.ai/code o la pestaña Code de la app), sobre un clon nuevo del repositorio privado de la copia. Solo llega a los portales que estén en la lista de dominios del entorno.
_Avoid_: canal Nube, Claude Code web, remoto

**Entorno de la nube**:
La configuración en claude.ai/code con la que arranca cada sesión de Code en la nube: la lista de dominios y el script de instalación. Vive en la cuenta del titular, no en la copia.
_Avoid_: entorno, sandbox, VM

**Agente**:
El asistente de IA que trabaja con el titular. En el canal Code puede ser cualquiera con terminal; en el canal Web, solo Claude.
_Avoid_: Claude, cuando se habla del canal Code

## Registros

**Archivo de registros**:
El archivo de la copia donde viven las búsquedas, vacantes, observaciones, evaluaciones y documentos del titular. Es la única fuente de verdad, y solo lo escribe el canal Code.
_Avoid_: modo local, hoja de registros, base de datos

**Instantánea**:
La copia en texto del archivo de registros que lee el canal Web. Se regenera completa desde el archivo y nunca se edita a mano.
_Avoid_: export, réplica, snapshot, hoja

**Nota para Code**:
Lo que deja un chat del canal Web cuando algo debe cambiar en un módulo o en los registros, para que el canal Code lo aplique en la copia.
_Avoid_: pendiente, parche

## Búsqueda

**Plataforma de reclutamiento**:
El sistema que aloja el portal de empleo de una empresa, como Workday, Eightfold o SmartRecruiters.
_Avoid_: ATS, portal

**Adaptador**:
La parte del script de búsqueda que sabe leer una plataforma de reclutamiento; cada empresa que la usa solo aporta su configuración.
_Avoid_: adaptador por empresa, scraper

**Búsqueda**:
Recorrer el listado de vacantes de una o varias empresas en sus portales, filtrarlas, evaluarlas y registrarlas. Solo se hace en el canal Code.
_Avoid_: comprobación, consulta

**Comprobación puntual**:
Leer el anuncio oficial de una vacante, o de unas pocas que el titular nombra, sin recorrer ningún listado. Se hace en cualquier canal; desde Web, lo que se quiera conservar va en una nota para Code.
_Avoid_: búsqueda, verificación
