# Los registros viven solo en el archivo de la copia y el canal Web lee una instantánea

Los registros viven en un único lugar, el archivo de registros de la copia (`ChambaKit_Registros.xlsx`), que solo escribe el canal Code con `herramientas/registros.py`. Las filas que salen de `buscar.py` pasan al archivo sin que el agente las genere una por una. El canal Web ya no busca ni escribe: lee una instantánea en Markdown que la herramienta regenera completa desde el archivo y que llega al proyecto de claude.ai, junto con los módulos, por la integración de GitHub con el repositorio privado de la copia. Web sí hace comprobaciones puntuales: lee el anuncio de una vacante que el titular nombra o pega, para evaluarla o adaptar el CV. Lo que se quiera conservar, como la observación, la evaluación o los requisitos, lo deja en una nota para Code.

Se retira la hoja de Google: escribirla con el conector de Sheets obligaba al modelo a generar cada celda y releer filas para comprobar. En una búsqueda de 14 empresas (~1,000 filas, ~750 mil tokens), eso fue más de la mitad del consumo. La búsqueda desde Web tampoco conseguía todas las vacantes, ni siquiera en las empresas con canal «Web y Code».

## Considered Options

- **Mantener la hoja como segundo lugar o como exportación opcional:** repetía en dos sitios la lógica de las fórmulas de `informes` y seguía dependiendo del conector que no escala, para un beneficio que la instantánea ya cubre.
- **SQLite en lugar del xlsx:** sería igual de binario en git, el titular no podría abrirlo, y la herramienta y sus pruebas ya existen para el xlsx. Se reabre solo si la lectura o la exportación se vuelven lentas.
- **Seguir pasando las filas al modelo y solo cambiar el destino:** no resolvía el consumo, que está en generar las filas, no en la herramienta que las recibe.

## Consequences

- Reemplaza al ADR 0003. También levanta la limitación del ADR 0005: sin la hoja, cualquier agente con terminal trabaja la copia completa en el canal Code. El canal Web sigue siendo de claude.ai.
- El canal Web necesita que la copia esté en un repositorio privado de GitHub. Sin GitHub, el titular puede subir la instantánea a mano o quedarse sin canal Web; con un repositorio público, no se ofrece el canal Web.
- Los datos llegan a Web después de exportar, hacer commit y push, y un Sync manual en claude.ai que solo el titular puede hacer.
- Las tendencias (10) se analizan solo en Code.
- Sale la columna `canal` de `busquedas`, que el ADR 0005 había conservado: nada filtra ya por ella, y `fuentes_consultas_filtros` dice cómo se leyó cada fuente. Las copias existentes la pierden en la migración.
- Las copias que ya usan la hoja necesitan una migración al archivo, con comparación de conteos.
