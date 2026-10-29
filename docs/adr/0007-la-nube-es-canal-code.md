# Claude Code en la nube es el canal Code, y el canal Web se conserva

Una sesión de Claude Code en la nube (claude.ai/code o la pestaña Code de la app) es el canal Code: llega a los portales y corre los scripts, que es lo que define a ese canal (ADR 0005). Lo que cambia es el entorno: un clon nuevo del repositorio privado de la copia en cada sesión, sin `.venv`, con una lista de dominios permitidos y un script de instalación que viven en la cuenta del titular. Esas diferencias se atienden en las herramientas y en reglas puntuales de **Code en la nube**, no con reglas por canal.

El canal Web se conserva por ahora. La nube cubre lo que hace Web, también desde el teléfono, pero tiene fricción que Web no tiene: cada empresa nueva fuera de la lista obliga a editar el entorno, y Workable bloquea las IP de la nube. Retirar Web (instantánea, notas para Code, Sync) se decide después de que un titular use la nube un tiempo.

## Considered Options

- **Un tercer canal, «Nube»:** obligaba a redefinir «Canal» y a duplicar en 00, 07 y 11 las reglas que hoy valen para Code, el mismo costo que el ADR 0005 descartó para otros agentes.
- **Retirar ya el canal Web:** difícil de revertir y sin uso real de la nube que lo respalde.

## Consequences

- Las búsquedas y los registros hechos en la nube siguen las reglas de Code sin cambios.
- `buscar.py` distingue un host bloqueado por la lista de dominios y el bloqueo de Workable a la nube, y dice qué hacer en cada caso.
- Lo que necesita la sesión (LibreOffice, poppler, Carlito, `markdownlint-cli2` y el `.venv`) lo instala un hook SessionStart condicionado a `CLAUDE_CODE_REMOTE=true`, que viaja con la copia y con `/actualizar`. El script de instalación del entorno queda vacío, así que el titular solo configura la red, con nivel Custom por defecto: Full deja salir los datos de la sesión a cualquier dominio.
- Al cerrar una sesión en la nube, los cambios se integran en `main` con permiso del titular; la rama de la sesión no se conserva.
