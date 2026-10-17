# Adaptadores por plataforma de reclutamiento, sin catálogo de empresas

La plantilla no trae empresas. El script de búsqueda conserva un adaptador por plataforma de reclutamiento (Workday, Eightfold, SmartRecruiters, Workable, Avature, Oracle Recruiting Cloud), y cada empresa del titular solo aporta su configuración: la URL de su portal y la región. Un catálogo de empresas habría revelado los objetivos de una persona y quedado atado a una región; el conocimiento de una plataforma no es un dato personal y le ahorra al titular construir el acceso desde cero.

**Avature quedó fuera (2026-10-16):** su adaptador no funcionó con los portales de otras empresas, porque cada portal de Avature define sus propios campos y filtros, y un adaptador que no sirve para otras empresas no entra en la plantilla. Una empresa en Avature se atiende con un adaptador construido en la copia, como un sitio propio.

## Considered Options

- **Conservar un catálogo de empresas de ejemplo:** descartado por privacidad y porque solo sirve a quien busca en esa región.
- **Borrar todos los adaptadores:** descartado; cada titular repetiría el trabajo de descubrir cómo leer plataformas muy comunes.
- **Adaptadores de sitio propio:** los escritos para el sitio de una sola empresa no se reutilizan y no entran en la plantilla. El titular que los necesite los construye en su copia.
