# Otros agentes en modo local, con el canal Code redefinido y skills por puntero

Una copia se puede usar con un agente distinto de Claude, como Antigravity con Gemini, solo en modo local. El canal Code pasa a significar «un agente con terminal sobre la copia», sea Claude Code u otro; el canal Web sigue siendo un proyecto de claude.ai. Los módulos, `AGENTS.md` y las skills hablan de «el agente», y «Claude» queda solo en lo que de verdad es Claude: el canal Web, el proyecto de claude.ai, los conectores de Google y el paso 9 de `/configurar`. El texto completo de cada skill sigue en `.claude/skills/`, la única carpeta de donde Claude Code carga skills, y `.agents/skills/` lleva un puntero por skill, con el mismo `name` y `description`, que remite a ella.

Se limita al modo local porque la hoja de registros depende de los conectores de Google de claude.ai, que no existen para otros agentes, y el canal Web es de claude.ai.

## Considered Options

- **Un canal nuevo para otros agentes:** obligaba a migrar la columna `canal` de 11 y a duplicar las reglas de BUS-CANALES, cuando lo que separa a los canales es si se llega a los portales, no qué agente se usa.
- **Renombrar el canal Code** (por ejemplo, a «Local»): «Local» choca con **Modo local**, y el cambio de nombre tocaba los registros de cada copia sin ganar nada.
- **Symlink de `.agents/skills/` a `.claude/skills/`:** Git para Windows lo descarga como un archivo de texto.
- **Dos copias completas de cada skill:** cada cambio se editaría dos veces y se desincronizarían en silencio.
- **Una lista de dominios permitidos para el sandbox del agente:** los portales cambian con cada ficha de 06, y no hay un archivo versionable con los permisos de Antigravity. En su lugar, el agente diagnostica la falta de red y le dice al titular cómo dársela.

## Consequences

- La lista cerrada de `canal` (`Code` / `Web`) no cambia: las búsquedas de cualquier agente se registran como `Code`.
- Una prueba automática comprueba que cada skill tenga su puntero con el mismo `name` y `description`.
- `/configurar` decide en cada uso si el agente es Claude Code; no guarda qué agente usa el titular, que puede cambiarlo.
- El trabajo del mantenedor sigue dependiendo de Claude Code.
