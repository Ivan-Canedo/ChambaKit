---
status: superseded by ADR 0006
---

# Dos lugares para los registros: hoja de Google o archivo local

Los registros viven en una hoja de Google que el agente crea con el conector. Si el titular no puede o no quiere conectar Google, la copia trabaja en modo local: los registros van a un archivo `.xlsx` dentro de la copia y todo se hace desde el canal Code. Antes de elegirlo, el agente advierte que en modo local el canal Web no funciona, porque un proyecto de claude.ai no puede leer ni escribir ese archivo.

## Consequences

- Los módulos que leen o escriben registros (00, 07, 08 y 11) describen los dos lugares, y el canal Code necesita una herramienta para escribir y leer el archivo local.
- El archivo se versiona en la copia: en modo local, git es el único respaldo e historial.
- Las fórmulas de la pestaña de informes no se calculan si nadie abre el archivo, así que en modo local la tabla resumen la calcula el script.
- El cambio solo va en un sentido: si el titular conecta Google después, el agente pasa los registros a la hoja, compara los conteos y retira el archivo local.
