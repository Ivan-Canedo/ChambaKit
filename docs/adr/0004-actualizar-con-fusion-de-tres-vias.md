# Las actualizaciones fusionan cada archivo en tres vías desde etiquetas de la plantilla

Cada versión de la plantilla se publica como una etiqueta de git (`v1.0`, `v1.1`…), y la copia anota en 01 la URL de la plantilla y su versión. `/actualizar` trae la etiqueta nueva y fusiona cada archivo con `git merge-file`, con la versión anotada como base. El agente solo resuelve los conflictos, y le pregunta al titular cuando tocan sus datos. Se descartó que el agente reescribiera a mano en cada módulo los cambios de la plantilla: los datos y el método conviven en los mismos archivos, y reescribirlos a mano arriesga pisar datos sin que se note.

Esto no contradice ADR 0002: lo que no sirve es un `git merge` entre repositorios, porque la copia no comparte historial con la plantilla. La fusión archivo por archivo solo necesita la base, y esa base es la etiqueta anotada.

## Consequences

Cada publicación de la plantilla necesita su etiqueta. Si una copia pierde la URL o la versión de 01, ya no se puede actualizar sin reconstruirlas a mano. Los cambios que no son solo texto (columnas nuevas en los registros, datos que hay que preguntarle al titular) los describe el mantenedor en `CAMBIOS.md`, porque la fusión no los ve.
