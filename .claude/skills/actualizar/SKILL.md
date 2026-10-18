---
name: actualizar
description: Lleva a la copia los cambios de una versión más nueva de la plantilla de ChambaKit, sin tocar los datos del titular.
disable-model-invocation: true
---

# Actualizar una copia de ChambaKit

Lleva a la copia del titular los cambios de una versión más nueva de la plantilla. Cada versión publicada es una etiqueta `vX.Y` del repositorio de la plantilla, y 01 («Versión de la plantilla») anota de cuál salió la copia y la URL de la plantilla. La copia no comparte historial con la plantilla, así que la actualización fusiona archivo por archivo, en tres vías (ADR 0004):

- **Base:** la etiqueta de la versión que anota 01.
- **Copia:** el archivo como está en esta carpeta, con los datos del titular.
- **Nueva:** la etiqueta de la versión destino.

`git merge-file` hace la fusión; tú resuelves solo los conflictos. Lo que la fusión no ve (columnas nuevas en los registros, datos que hay que preguntarle al titular) lo describe `CAMBIOS.md`, y lo haces en el paso 5.

En los comandos, `<base>` y `<nueva>` son las etiquetas (`v1.0`, `v1.1`), `<url>` es la de 01 y `<directorio temporal>` es una carpeta nueva en el directorio temporal de la sesión, no en la copia.

## Paso 1: Condiciones

Revisa todo antes de cambiar nada. Si algo falla, detente y dile al titular qué pasa y qué hacer:

1. **Plantilla:** si `git config --local --get chambakit.mantenedor` da `true`, esta carpeta es la plantilla y no se actualiza: dile al mantenedor que pruebe en un clon temporal (`CONTRIBUTING.md`, «Probar como titular»).
2. **Repositorio:** `git rev-parse --is-inside-work-tree` debe dar `true`. Si no, la copia salió del ZIP sin `git init`: explícale que la actualización necesita un repositorio y que lo cree con `git init` y un primer commit con todo (README, «Con el ZIP»).
3. **Sin cambios pendientes:** `git status --porcelain` debe salir vacío, para que la actualización quede en un solo commit y se pueda deshacer. Si no, pídele que haga commit de sus cambios o de sus archivos nuevos, o que los descarte.
4. **01:** la línea **Versión de la plantilla** debe tener la versión y la URL. Si falta alguna, no se puede elegir la base: pregúntale de qué versión y de qué URL salió su copia (la URL pública es la de su página de GitHub, «generated from …»). Sin esos dos datos, detente.
5. **Copia privada:** haz la revisión del paso 1 de `/configurar` (`.claude/skills/configurar/SKILL.md`), porque la actualización edita módulos (AGENTS.md, «Copia privada»).

## Paso 2: Versión destino

1. Lista las versiones publicadas: `git ls-remote --tags --refs <url> 'v*'`. Ordénalas por número, no como texto (`v1.10` va después de `v1.9`).
2. El destino es la más reciente. Si el titular pidió otra, debe estar en la lista y ser más nueva que la base.
3. Si la base ya es la más reciente, díselo y termina.
4. Dile al titular de qué versión a cuál va a pasar, y que al final le propones un solo commit que puede revisar antes.

## Paso 3: Traer las versiones

Trae las dos etiquetas sin agregar un remoto:

```sh
git fetch --no-tags <url> tag <base> tag <nueva>
```

Lista los archivos que la plantilla cambió entre las dos, con cada renombre como un borrado y un agregado:

```sh
git diff --name-status --no-renames <base> <nueva>
```

Cada línea es `M` (modificado), `A` (agregado), `D` (borrado) o, rara vez, `T` (cambió de tipo, como un archivo que pasa a ser enlace). Los archivos que no aparecen se quedan como están en la copia.

## Paso 4: Fusionar

1. **Esta skill primero:** fusiona las líneas de `.claude/skills/actualizar/` como dice «Cada archivo». Si alguna cambió, vuelve a leer este `SKILL.md` y sigue con su versión nueva, desde este punto.
2. **Los demás:** fusiona cada línea restante de la lista.
3. **Resumen:** lleva, por archivo, qué pasó: fusión limpia, conflictos resueltos (y cómo), agregado, borrado o decidido con el titular. El paso termina cuando cada línea de la lista tiene su entrada.

### Cada archivo

| Línea | En la copia | Qué haces |
| --- | --- | --- |
| `M` | Existe | Fusión en tres vías (abajo). |
| `M` | No existe (el titular lo borró) | Pregúntale si lo recupera en la versión nueva o lo deja borrado. |
| `A` | No existe | Agrégalo: `git show <nueva>:<archivo> > <archivo>`, creando su carpeta si falta. |
| `A` | Existe, igual a la nueva | Nada. |
| `A` | Existe, distinto | Pregúntale, mostrando los dos. |
| `D` | Igual a la base | `git rm -q <archivo>`. |
| `D` | Distinto de la base (el titular lo modificó) | Pregúntale si lo borra o lo conserva. |
| `D` | No existe | Nada. |
| `T` | Cualquiera | Pregúntale, mostrando la base y la nueva. |

Un archivo es igual a la base cuando `git hash-object <archivo>` da lo mismo que `git rev-parse <base>:<archivo>`. Si `git ls-tree <nueva> <archivo>` da modo `100755`, deja el archivo ejecutable (`chmod +x`).

**Fusión en tres vías:**

```sh
git show <base>:<archivo> > <directorio temporal>/base
git show <nueva>:<archivo> > <directorio temporal>/nueva
git merge-file -L copia -L <base> -L <nueva> <archivo> <directorio temporal>/base <directorio temporal>/nueva
```

Escribe el resultado en el archivo de la copia. La salida `0` es una fusión limpia; de `1` a `127`, la cantidad de conflictos, marcados en el archivo entre `<<<<<<< copia` y `>>>>>>> <nueva>`; `255` es un error y el archivo no cambió. Un archivo binario no se fusiona: si es igual a la base, reemplázalo por el de la nueva; si no, pregúntale.

### Conflictos

Resuelve cada conflicto en su lugar y deja el archivo sin marcas:

- **Solo texto de la plantilla** (instrucciones, estructura, código que el titular no tocó): toma el de la nueva.
- **Un dato del titular** (lo que escribió al llenar un módulo, una ficha de 06, un adaptador suyo en `herramientas/buscar.py`): consérvalo, acomodado a la estructura nueva.
- **Versiones y ESTADO:** la línea de versión de un módulo (`**Versión:**`; en 00, `Versión`) conserva la de la copia, y el cierre la actualiza. En la tabla ESTADO de 01, la fila de un módulo «Configurado» conserva su estado y su siguiente paso de la copia, y una fila «Sin llenar» toma la de la nueva; la columna Versión la pone el cierre.
- **Si no está claro** de quién es el texto o cómo acomodarlo: pregúntale, mostrando las tres versiones (base, copia y nueva).

## Paso 5: Acciones de CAMBIOS.md

`CAMBIOS.md`, ya en su versión nueva, tiene una sección `## vX.Y — fecha` por versión. Haz las de cada versión posterior a la base, hasta la destino, de la más vieja a la más nueva. Cada sección trae:

- **Qué cambió:** léeselo al titular en pocas líneas.
- **En la copia:** una lista numerada de acciones. Haz las **automáticas** y, en las **con el titular**, pregúntale o entrevístalo como diga la acción. Si una acción toca un módulo «Configurado», su fila de ESTADO toma el paso que la acción dice retomar.

El paso termina cuando cada acción de esas versiones está hecha o el titular decidió posponerla; las pospuestas van al resumen.

## Paso 6: Cierre

1. **Formato:** corre `markdownlint-cli2` sobre cada `.md` que cambió y deja cero advertencias (AGENTS.md, «Formato Markdown»).
2. **Pruebas:** si cambió algún archivo de `herramientas/`, corre las pruebas con el Python de `.venv/` si existe (en Windows, `.venv\Scripts\python.exe`) o, si no, con `python3`:

   ```sh
   .venv/bin/python -I -B -m unittest discover -s herramientas/pruebas
   ```

   Las que necesitan LibreOffice, poppler u `openpyxl` se saltan si faltan; un salto no es una falla. Si alguna falla, muéstrale la salida al titular antes de proponer el commit.
3. **Módulos:** cada módulo (00–11) que cambió, por la fusión o por una acción, sube de versión desde la que tiene en el último commit (`git show HEAD:<módulo>`), no desde la de la plantilla: versión, fecha de hoy y la línea de cambio «Actualizado a la plantilla vX.Y». Su fila de ESTADO toma esa versión. En 01, **Versión de la plantilla** pasa a la destino, sin la `v`.
4. **Resumen:** muéstrale el resumen del paso 4, con las acciones del paso 5 y lo pospuesto.
5. **Canal Web:** si 00 («Registros») tiene la URL de la hoja, recuérdale reemplazar en su proyecto web cada módulo que cambió; si cambió 00, se vuelve a pegar en «Instrucciones».
6. **Commit:** propónle un solo commit, «Actualiza a la plantilla vX.Y», con todos los archivos de la actualización (los agregados también: `git add` de cada uno). Hazlo solo con su permiso. Si prefiere deshacer todo, `git restore --staged --worktree .` revierte los archivos que ya existían y borra los agregados que ya pasaron por `git add`; los demás agregados, que están en el resumen, se borran a mano.
